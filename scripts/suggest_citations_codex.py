#!/usr/bin/env python3

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Iterable

from kb_utils import (
    OUTPUTS_DIR,
    ROOT,
    ensure_list,
    load_concept_records,
    load_library_note_records,
    parse_sections,
    read_markdown_record,
)
from run_codex_step import build_command


PROMPT_TEMPLATE = ROOT / "prompts" / "suggest_citations.md"
DEFAULT_OUTPUT_DIR = OUTPUTS_DIR / "citation_suggestions"
SEARCH_LAYER_DIRS = {
    "notes": ROOT / "notes",
    "concepts": ROOT / "concepts",
    "systems": ROOT / "systems",
    "theory": ROOT / "theory",
}
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "was",
    "were",
    "with",
}
SECTION_WEIGHTS = {
    "citation": 1.0,
    "core question": 1.5,
    "system": 1.2,
    "methods": 1.4,
    "key variables": 2.3,
    "main findings": 2.8,
    "quantitative results": 2.8,
    "mechanism / interpretation": 1.6,
    "evidence map": 2.0,
    "limitations": 1.5,
    "concepts": 2.0,
    "confidence": 0.5,
    "open questions": 1.0,
    "definition": 1.8,
    "how measured": 1.6,
    "evidence across papers": 1.8,
    "quantitative summary": 1.8,
    "conflicts / discrepancies": 1.5,
    "related concepts": 1.0,
    "source papers": 1.8,
    "variables": 2.0,
    "interaction structure": 1.8,
    "evidence": 1.7,
    "interpretation": 1.3,
    "competing models (if any)": 1.2,
}
LAYER_WEIGHTS = {
    "notes": 1.4,
    "concepts": 0.9,
    "systems": 0.8,
    "theory": 0.8,
}
MAX_NOTE_RESULTS = 8
MAX_CONTEXT_RESULTS = 4
TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*")
WHITESPACE_PATTERN = re.compile(r"\s+")


@dataclass
class SearchRecord:
    layer: str
    path: Path
    title: str
    label: str
    body: str
    frontmatter: dict[str, object]
    sections: dict[str, str]
    weighted_tokens: Counter[str]
    searchable_sections: list[tuple[str, str]]


@dataclass
class SearchHit:
    record: SearchRecord
    score: float
    matched_terms: list[str]
    snippet_lines: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Suggest citations for a scientific paragraph using local KB retrieval plus `codex exec`."
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        type=Path,
        help="Optional path to a text or markdown file containing the paragraph.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for generated markdown reports.",
    )
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--model")
    parser.add_argument("--profile")
    parser.add_argument("--top-notes", type=int, default=MAX_NOTE_RESULTS)
    parser.add_argument("--top-context", type=int, default=MAX_CONTEXT_RESULTS)
    parser.add_argument("--dry-run", action="store_true", help="Render retrieval and prompt, but skip `codex exec`.")
    return parser.parse_args()


def normalize_whitespace(text: str) -> str:
    return WHITESPACE_PATTERN.sub(" ", text).strip()


def read_paragraph(input_path: Path | None) -> tuple[str, str]:
    if input_path is not None:
        text = input_path.read_text(encoding="utf-8")
        paragraph = normalize_whitespace(text)
        if not paragraph:
            raise ValueError(f"No text found in {input_path}")
        return paragraph, input_path.stem

    if sys.stdin.isatty():
        raise ValueError("Provide a paragraph via a file path or stdin.")

    paragraph = normalize_whitespace(sys.stdin.read())
    if not paragraph:
        raise ValueError("No text found on stdin.")
    return paragraph, "stdin"


def tokenize(text: str) -> list[str]:
    return [token for token in TOKEN_PATTERN.findall(text.lower()) if token]


def filter_query_tokens(tokens: Iterable[str]) -> list[str]:
    filtered: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        if token in STOPWORDS:
            continue
        if len(token) <= 2 and not any(char.isdigit() for char in token):
            continue
        if token in seen:
            continue
        seen.add(token)
        filtered.append(token)
    return filtered


def stringify_value(value: object) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def weighted_terms(text: str, weight: float) -> Counter[str]:
    counter: Counter[str] = Counter()
    for token in tokenize(text):
        counter[token] += weight
    return counter


def build_note_record(record) -> SearchRecord:
    frontmatter = record.frontmatter
    weighted = Counter()
    weighted.update(weighted_terms(record.title, 4.5))
    for field, field_weight in (
        ("note_key", 4.0),
        ("journal", 1.4),
        ("domain", 1.8),
        ("system_type", 1.7),
    ):
        value = str(frontmatter.get(field, "")).strip()
        if value:
            weighted.update(weighted_terms(value, field_weight))
    for field in ("methods", "variables", "concepts", "authors"):
        values = ensure_list(frontmatter.get(field))
        if values:
            weighted.update(weighted_terms(" ".join(values), 2.6))

    searchable_sections: list[tuple[str, str]] = []
    for name, text in record.sections.items():
        searchable_sections.append((name, text))
        section_weight = SECTION_WEIGHTS.get(name.lower(), 1.1)
        weighted.update(weighted_terms(text, section_weight))

    return SearchRecord(
        layer="notes",
        path=record.path,
        title=record.title or str(frontmatter.get("title") or record.path.stem),
        label=str(frontmatter.get("note_key") or record.path.stem),
        body=record.body,
        frontmatter=frontmatter,
        sections=record.sections,
        weighted_tokens=weighted,
        searchable_sections=searchable_sections,
    )


def load_markdown_records(layer: str, root: Path) -> list[SearchRecord]:
    records: list[SearchRecord] = []
    for path in sorted(root.rglob("*.md")):
        if path.name == "README.md":
            continue
        record = read_markdown_record(path)
        weighted = Counter()
        weighted.update(weighted_terms(record.title or path.stem, 3.8))
        for key, value in record.frontmatter.items():
            weighted.update(weighted_terms(stringify_value(value), 1.8))

        searchable_sections: list[tuple[str, str]] = []
        for name, text in record.sections.items():
            searchable_sections.append((name, text))
            section_weight = SECTION_WEIGHTS.get(name.lower(), 1.3)
            weighted.update(weighted_terms(text, section_weight))

        body_title, body_sections = parse_sections(record.body)
        if not searchable_sections and body_sections:
            for name, text in body_sections.items():
                searchable_sections.append((name, text))
                weighted.update(weighted_terms(text, SECTION_WEIGHTS.get(name.lower(), 1.3)))
        if not searchable_sections and record.body:
            searchable_sections.append(("Body", record.body))
            weighted.update(weighted_terms(record.body, 1.1))

        label = str(record.frontmatter.get("concept_id") or body_title or record.title or path.stem)
        records.append(
            SearchRecord(
                layer=layer,
                path=path,
                title=record.title or body_title or path.stem,
                label=label,
                body=record.body,
                frontmatter=record.frontmatter,
                sections=record.sections if record.sections else body_sections,
                weighted_tokens=weighted,
                searchable_sections=searchable_sections,
            )
        )
    return records


def load_search_records() -> list[SearchRecord]:
    records: list[SearchRecord] = [build_note_record(record) for record in load_library_note_records()]
    records.extend(load_concept_records_for_search())
    records.extend(load_markdown_records("systems", SEARCH_LAYER_DIRS["systems"]))
    records.extend(load_markdown_records("theory", SEARCH_LAYER_DIRS["theory"]))
    return records


def load_concept_records_for_search() -> list[SearchRecord]:
    records: list[SearchRecord] = []
    for record in load_concept_records():
        weighted = Counter()
        weighted.update(weighted_terms(record.title, 4.0))
        for key, value in record.frontmatter.items():
            weighted.update(weighted_terms(stringify_value(value), 1.8))

        searchable_sections: list[tuple[str, str]] = []
        for name, text in record.sections.items():
            searchable_sections.append((name, text))
            weighted.update(weighted_terms(text, SECTION_WEIGHTS.get(name.lower(), 1.5)))

        records.append(
            SearchRecord(
                layer="concepts",
                path=record.path,
                title=record.title,
                label=str(record.frontmatter.get("concept_id") or record.path.stem),
                body=record.body,
                frontmatter=record.frontmatter,
                sections=record.sections,
                weighted_tokens=weighted,
                searchable_sections=searchable_sections,
            )
        )
    return records


def build_idf(records: list[SearchRecord]) -> dict[str, float]:
    doc_freq: Counter[str] = Counter()
    total = len(records)
    for record in records:
        doc_freq.update(set(record.weighted_tokens))
    return {
        token: math.log((1 + total) / (1 + freq)) + 1.0
        for token, freq in doc_freq.items()
    }


def build_significant_phrases(paragraph: str) -> list[str]:
    tokens = filter_query_tokens(tokenize(paragraph))
    phrases: list[str] = []
    for size in (3, 2):
        for start in range(0, len(tokens) - size + 1):
            phrase_tokens = tokens[start : start + size]
            if all(token in STOPWORDS for token in phrase_tokens):
                continue
            phrase = " ".join(phrase_tokens)
            if len(phrase) < 10:
                continue
            if phrase not in phrases:
                phrases.append(phrase)
            if len(phrases) >= 8:
                return phrases
    return phrases


def sentence_candidates(text: str) -> list[str]:
    raw_lines = [line.strip() for line in text.splitlines() if line.strip()]
    candidates: list[str] = []
    for line in raw_lines:
        parts = re.split(r"(?<=[.!?])\s+", line)
        for part in parts:
            part = normalize_whitespace(part)
            if part:
                candidates.append(part)
    return candidates


def snippet_score(text: str, query_terms: list[str], phrases: list[str]) -> float:
    lower_text = text.lower()
    token_counts = Counter(tokenize(lower_text))
    score = 0.0
    for term in query_terms:
        if term in token_counts:
            score += min(token_counts[term], 3) * 1.0
    for phrase in phrases:
        if phrase in lower_text:
            score += 3.5
    return score


def trim_snippet(text: str, limit: int = 240) -> str:
    text = normalize_whitespace(text)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def select_snippets(record: SearchRecord, query_terms: list[str], phrases: list[str]) -> list[str]:
    candidates: list[tuple[float, str, str]] = []
    for section_name, section_text in record.searchable_sections:
        for sentence in sentence_candidates(section_text):
            score = snippet_score(sentence, query_terms, phrases)
            if score <= 0:
                continue
            candidates.append((score, section_name, sentence))
    candidates.sort(key=lambda item: (-item[0], len(item[2])))
    selected: list[str] = []
    seen: set[str] = set()
    for _, section_name, sentence in candidates:
        normalized = sentence.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        selected.append(f"{section_name}: {trim_snippet(sentence)}")
        if len(selected) >= 3:
            break
    return selected


def score_record(
    record: SearchRecord,
    query_terms: list[str],
    phrases: list[str],
    idf_lookup: dict[str, float],
) -> SearchHit | None:
    matched_terms = [term for term in query_terms if record.weighted_tokens.get(term, 0) > 0]
    if not matched_terms:
        return None

    score = 0.0
    for term in matched_terms:
        score += record.weighted_tokens[term] * idf_lookup.get(term, 1.0)

    lower_body = record.body.lower()
    for phrase in phrases:
        if phrase in lower_body:
            score += 5.0

    score *= LAYER_WEIGHTS.get(record.layer, 1.0)
    snippets = select_snippets(record, query_terms, phrases)
    if snippets:
        score += min(len(snippets), 3) * 0.8

    return SearchHit(
        record=record,
        score=score,
        matched_terms=matched_terms[:8],
        snippet_lines=snippets,
    )


def rank_hits(
    paragraph: str,
    records: list[SearchRecord],
    *,
    top_notes: int,
    top_context: int,
) -> tuple[list[SearchHit], list[SearchHit]]:
    query_terms = filter_query_tokens(tokenize(paragraph))
    if not query_terms:
        raise ValueError("Could not extract meaningful query terms from the paragraph.")
    phrases = build_significant_phrases(paragraph)
    idf_lookup = build_idf(records)

    note_hits: list[SearchHit] = []
    context_hits: list[SearchHit] = []
    for record in records:
        hit = score_record(record, query_terms, phrases, idf_lookup)
        if hit is None or hit.score <= 0:
            continue
        if record.layer == "notes":
            note_hits.append(hit)
        else:
            context_hits.append(hit)

    note_hits.sort(key=lambda item: (-item.score, item.record.label.lower()))
    context_hits.sort(key=lambda item: (-item.score, item.record.label.lower()))
    return trim_hits(note_hits, limit=top_notes, ratio=0.2, floor=90.0, min_results=2), trim_hits(
        context_hits,
        limit=top_context,
        ratio=0.18,
        floor=70.0,
        min_results=2,
    )


def trim_hits(
    hits: list[SearchHit],
    *,
    limit: int,
    ratio: float,
    floor: float,
    min_results: int,
) -> list[SearchHit]:
    if not hits:
        return []
    top_score = hits[0].score
    threshold = max(floor, top_score * ratio)
    selected: list[SearchHit] = []
    for hit in hits:
        if len(selected) >= limit:
            break
        if len(selected) < min_results or hit.score >= threshold:
            selected.append(hit)
            continue
        break
    return selected


def format_note_hit(hit: SearchHit) -> str:
    journal = str(hit.record.frontmatter.get("journal", "")).strip()
    year = str(hit.record.frontmatter.get("year", "")).strip()
    methods = ", ".join(ensure_list(hit.record.frontmatter.get("methods"))[:4]) or "n/a"
    concepts = ", ".join(ensure_list(hit.record.frontmatter.get("concepts"))[:6]) or "n/a"
    lines = [
        f"- Note key: {hit.record.label}",
        f"  Title: {hit.record.title}",
        f"  Path: {hit.record.path.relative_to(ROOT)}",
        f"  Journal/Year: {journal or 'n/a'} / {year or 'n/a'}",
        f"  Methods: {methods}",
        f"  Concepts: {concepts}",
        f"  Retrieval score: {hit.score:.2f}",
        f"  Matched terms: {', '.join(hit.matched_terms)}",
    ]
    if hit.snippet_lines:
        lines.append("  Supporting snippets:")
        for snippet in hit.snippet_lines:
            lines.append(f"  - {snippet}")
    return "\n".join(lines)


def format_context_hit(hit: SearchHit) -> str:
    lines = [
        f"- Layer: {hit.record.layer}",
        f"  Label: {hit.record.label}",
        f"  Title: {hit.record.title}",
        f"  Path: {hit.record.path.relative_to(ROOT)}",
        f"  Retrieval score: {hit.score:.2f}",
        f"  Matched terms: {', '.join(hit.matched_terms)}",
    ]
    if hit.snippet_lines:
        lines.append("  Relevant snippets:")
        for snippet in hit.snippet_lines:
            lines.append(f"  - {snippet}")
    return "\n".join(lines)


def build_retrieval_context(
    paragraph: str,
    note_hits: list[SearchHit],
    context_hits: list[SearchHit],
) -> str:
    query_terms = filter_query_tokens(tokenize(paragraph))
    phrase_lines = build_significant_phrases(paragraph)
    lines = [
        "Paragraph terms:",
        f"- Query tokens: {', '.join(query_terms[:20]) or 'n/a'}",
        f"- Significant phrases: {', '.join(phrase_lines) or 'n/a'}",
        "",
        "Primary note candidates:",
    ]
    if not note_hits:
        lines.append("- none")
    else:
        for hit in note_hits:
            lines.append(format_note_hit(hit))

    lines.extend(["", "Secondary framing context:"])
    if not context_hits:
        lines.append("- none")
    else:
        for hit in context_hits:
            lines.append(format_context_hit(hit))
    return "\n".join(lines)


def render_prompt(paragraph: str, retrieval_context: str) -> str:
    template = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "ROOT": str(ROOT),
        "PARAGRAPH": paragraph,
        "RETRIEVAL_CONTEXT": retrieval_context,
    }
    prompt = template
    for key, value in replacements.items():
        prompt = prompt.replace(f"{{{{{key}}}}}", value)
    return prompt


def run_codex_prompt(
    prompt_text: str,
    *,
    codex_bin: str,
    model: str | None,
    profile: str | None,
) -> tuple[str, str, str, int, list[str]]:
    if shutil.which(codex_bin) is None:
        raise RuntimeError(f"Could not find `{codex_bin}` on PATH.")

    with tempfile.NamedTemporaryFile(prefix="citation_suggestions_", suffix=".txt", delete=False) as handle:
        output_last_message = Path(handle.name)

    command = build_command(
        codex_bin=codex_bin,
        layer="notes",
        output_last_message=output_last_message,
        model=model,
        profile=profile,
    )
    completed = subprocess.run(
        command,
        input=prompt_text,
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    agent_message = output_last_message.read_text(encoding="utf-8").strip() if output_last_message.exists() else ""
    return agent_message, completed.stdout, completed.stderr, completed.returncode, command


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "paragraph"


def output_path(output_dir: Path, input_label: str, paragraph: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = slugify(input_label)
    excerpt = "-".join(filter_query_tokens(tokenize(paragraph))[:6])
    suffix = slugify(excerpt)[:60] if excerpt else "citation-suggestions"
    return output_dir / f"{timestamp}_{prefix}_{suffix}.md"


def ensure_report_heading(text: str) -> str:
    stripped = text.lstrip()
    if stripped.startswith("# Citation Suggestions"):
        return stripped.rstrip() + "\n"
    return "# Citation Suggestions\n\n" + stripped.rstrip() + "\n"


def print_summary(report_path: Path, note_hits: list[SearchHit], context_hits: list[SearchHit]) -> None:
    top_notes = ", ".join(hit.record.label for hit in note_hits[:3]) or "none"
    top_context = ", ".join(hit.record.label for hit in context_hits[:2]) or "none"
    print(f"Wrote {report_path.relative_to(ROOT)}")
    print(f"Top note hits: {top_notes}")
    print(f"Top context hits: {top_context}")


def main() -> int:
    args = parse_args()
    try:
        paragraph, input_label = read_paragraph(args.input_path)
        records = load_search_records()
        note_hits, context_hits = rank_hits(
            paragraph,
            records,
            top_notes=args.top_notes,
            top_context=args.top_context,
        )
        retrieval_context = build_retrieval_context(paragraph, note_hits, context_hits)
        prompt_text = render_prompt(paragraph, retrieval_context)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(prompt_text)
        return 0

    try:
        agent_message, stdout, stderr, returncode, command = run_codex_prompt(
            prompt_text,
            codex_bin=args.codex_bin,
            model=args.model,
            profile=args.profile,
        )
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if returncode != 0:
        print("`codex exec` failed.", file=sys.stderr)
        print(f"Command: {' '.join(command)}", file=sys.stderr)
        if stdout.strip():
            print(stdout.strip(), file=sys.stderr)
        if stderr.strip():
            print(stderr.strip(), file=sys.stderr)
        if agent_message:
            print(agent_message, file=sys.stderr)
        return returncode

    report_text = ensure_report_heading(agent_message or stdout)
    report_path = output_path(args.output_dir, input_label, paragraph)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_text, encoding="utf-8")
    print_summary(report_path, note_hits, context_hits)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
