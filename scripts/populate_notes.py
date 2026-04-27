#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXTRACTED_DIR = ROOT / "raw" / "extracted"
NOTES_DIR = ROOT / "notes"
TEMPLATE_PATH = ROOT / "templates" / "paper_note_template.md"
TEXT_SENTINEL = "----- EXTRACTED TEXT -----"
HEADING_NAMES = {
    "abstract",
    "background",
    "conclusion",
    "conclusions",
    "discussion",
    "experimental methods",
    "experimental section",
    "introduction",
    "keywords",
    "materials and methods",
    "methods",
    "references",
    "results",
    "results and discussion",
    "significance",
}
BAD_SENTENCE_FRAGMENTS = (
    "doi.org",
    "downloaded via",
    "department of",
    "article recommendations",
    "supporting information",
    "read online",
    "all rights are reserved",
    "please cite this article",
    "contents lists available",
    "published:",
    "received:",
    "accepted:",
    "editor:",
    "metrics & more",
    "sharingguidelines",
)
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "by",
    "during",
    "between",
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
    "our",
    "throughout",
    "upon",
    "that",
    "the",
    "their",
    "this",
    "to",
    "via",
    "using",
    "we",
    "with",
}
CONCEPT_NOUNS = {
    "alignment",
    "analysis",
    "analyses",
    "cholesterol",
    "chromatin",
    "cycle",
    "dimension",
    "dimensions",
    "domains",
    "fiber",
    "fractality",
    "fractal",
    "genome",
    "imaging",
    "membrane",
    "membranes",
    "microscopy",
    "multilayer",
    "multilayers",
    "organization",
    "ordering",
    "phase",
    "phases",
    "process",
    "processes",
    "rafts",
    "reflectivity",
    "simulations",
    "spectrum",
    "transition",
}
MONTHS = {
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
}
GENERIC_PHRASES = {
    "image based",
    "main findings",
    "materials methods",
    "our results",
    "results discussion",
    "this study",
}
BAD_CONCEPT_STARTS = {
    "addition",
    "article",
    "find",
    "many",
    "obtain",
    "plot",
    "reported",
    "show",
    "shows",
    "suggests",
}
UNIT_PATTERN = re.compile(
    r"(?i)(?:"
    r"≈|±|%"
    r"|(?<![A-Za-z])(?:nm|um|mm|cm|mM|uM|nM|pM|kDa|Da|kb|Mb|Gb|Mbp|bp|ms|min|h|hr|hrs|day|days|week|weeks|month|months|year|years|Pa|kPa|MPa|GPa|mV|Hz|kHz|MHz|GHz|fps|fold)(?![A-Za-z])"
    r"|Å|μm|µm|μM|µM|°C"
    r")"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Populate paper notes from extracted text files in raw/extracted."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite notes even if they already contain non-template content.",
    )
    return parser.parse_args()


def collapse_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def unique_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_items: list[str] = []
    for item in items:
        normalized = collapse_spaces(item).lower()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique_items.append(collapse_spaces(item))
    return unique_items


def parse_extracted_file(path: Path) -> tuple[dict[str, object], str]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    header, separator, body = raw.partition(TEXT_SENTINEL)
    metadata: dict[str, object] = {
        "source_pdf": "",
        "backend": "",
        "status": "",
        "warnings": [],
    }

    if separator:
        capture_warnings = False
        for line in header.splitlines():
            if line.startswith("Source PDF: "):
                metadata["source_pdf"] = line.removeprefix("Source PDF: ").strip()
                capture_warnings = False
            elif line.startswith("Extraction backend: "):
                metadata["backend"] = line.removeprefix("Extraction backend: ").strip()
                capture_warnings = False
            elif line.startswith("Extraction status: "):
                metadata["status"] = line.removeprefix("Extraction status: ").strip()
                capture_warnings = False
            elif line == "Warnings:":
                capture_warnings = True
            elif capture_warnings and line.startswith("- "):
                warning = line[2:].strip()
                if warning and warning.lower() != "none":
                    metadata["warnings"].append(warning)
    else:
        body = raw

    text = body.replace("\r\n", "\n").replace("\r", "\n").strip()
    if len(text) < 500:
        metadata["warnings"].append(
            "Extracted text is very short; the extraction may be incomplete."
        )
    if not text:
        metadata["warnings"].append("Extracted text body is empty.")

    metadata["warnings"] = unique_preserve_order(list(metadata["warnings"]))
    return metadata, text


def filename_hints(stem: str) -> dict[str, str]:
    parts = stem.split("_")
    year = parts[-1] if parts and re.fullmatch(r"(19|20)\d{2}", parts[-1]) else ""
    journal_parts = parts[1:-1] if year and len(parts) > 2 else parts[1:]
    return {
        "author_hint": parts[0].replace("-", " ") if parts else "",
        "year": year,
        "journal": " ".join(part.replace("-", " ") for part in journal_parts),
        "fallback_title": stem.replace("_", " "),
    }


def existing_note_title(note_path: Path) -> str:
    if not note_path.exists():
        return ""

    for line in note_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def plausible_title_line(line: str) -> bool:
    stripped = collapse_spaces(line.strip(" -"))
    if not stripped:
        return False
    if len(stripped) < 15 or len(stripped) > 220:
        return False
    lowered = stripped.lower()
    banned_fragments = (
        "abstract",
        "introduction",
        "keywords",
        "supplementary",
        "references",
        "doi",
        "@",
        "http",
        "received",
        "accepted",
        "published",
        "downloaded via",
    )
    if any(fragment in lowered for fragment in banned_fragments):
        return False
    if sum(character.isalpha() for character in stripped) < 10:
        return False
    return True


def guess_title(text: str, fallback: str) -> tuple[str, str]:
    lines = [collapse_spaces(line) for line in text.splitlines() if line.strip()]
    candidates: list[tuple[float, str]] = []

    for index, line in enumerate(lines[:20]):
        if not plausible_title_line(line):
            continue

        parts = [line]
        for next_line in lines[index + 1 : min(len(lines), index + 4)]:
            if plausible_author_block(clean_author_text(next_line)):
                break
            if looks_like_heading(next_line):
                break
            lowered = next_line.lower()
            if any(
                fragment in lowered
                for fragment in (
                    "cite this",
                    "department",
                    "university",
                    "institute",
                    "center for",
                    "centre for",
                    "current applied physics",
                    "biophysical journal",
                )
            ):
                break
            if not plausible_title_line(next_line):
                break
            combined = collapse_spaces(" ".join(parts + [next_line]))
            if len(combined) > 220:
                break
            parts.append(next_line)

        title = collapse_spaces(" ".join(parts))
        words = title.split()
        score = 0.0
        if 5 <= len(words) <= 20:
            score += 4.0
        if 40 <= len(title) <= 180:
            score += 3.0
        if not title.endswith("."):
            score += 1.0
        if title.count(",") > 2:
            score -= 2.0
        if any(character.isdigit() for character in title):
            score -= 1.0
        score -= index * 0.2
        candidates.append((score, title))

    if candidates:
        score, title = max(candidates, key=lambda item: item[0])
        if score >= 4:
            return title, "text"

    return fallback, "filename"


def clean_author_text(text: str) -> str:
    cleaned = text.replace(" and ", ", ")
    cleaned = re.sub(r"(?<=\w)[*§†‡]+", "", cleaned)
    cleaned = re.sub(r",\s*[*§†‡]+", ",", cleaned)
    cleaned = re.sub(r"[*§†‡]", "", cleaned)
    cleaned = re.sub(r",\s*\d+\b", ",", cleaned)
    cleaned = re.sub(r"(?<=\D)\d+(?=\b)", "", cleaned)
    cleaned = re.sub(r"\b\d+\b", "", cleaned)
    cleaned = re.sub(r"\s+,", ",", cleaned)
    cleaned = re.sub(r",\s*,+", ", ", cleaned)
    return collapse_spaces(cleaned.strip(" ,;"))


def plausible_author_block(text: str) -> bool:
    if len(text) < 8 or len(text) > 240:
        return False
    lowered = text.lower()
    banned_fragments = (
        "abstract",
        "introduction",
        "department",
        "university",
        "institute",
        "center for",
        "centre for",
        "correspondence",
        "editor",
        "published",
        "accepted",
        "received",
        "biophysical journal",
    )
    if any(fragment in lowered for fragment in banned_fragments):
        return False
    separators = text.count(",") + lowered.count(" and ") + lowered.count(" & ")
    capitalized_words = sum(word[:1].isupper() for word in text.split())
    return separators >= 1 and capitalized_words >= 2


def looks_like_affiliation_line(line: str) -> bool:
    lowered = line.lower()
    return any(
        fragment in lowered
        for fragment in (
            "department",
            "university",
            "institute",
            "center for",
            "centre for",
            "school of",
            "college of",
            "correspondence",
            "e-mail",
            "email",
        )
    ) or bool(re.match(r"^\d+[A-Za-z]", line))


def find_title_span(lines: list[str], title: str) -> tuple[int | None, int | None]:
    normalized_title = collapse_spaces(title)
    for start in range(min(len(lines), 20)):
        combined = ""
        for end in range(start, min(len(lines), start + 4)):
            combined = collapse_spaces(f"{combined} {lines[end]}")
            if combined == normalized_title:
                return start, end + 1
    return None, None


def guess_authors(text: str, title: str) -> tuple[str, str]:
    lines = [collapse_spaces(line) for line in text.splitlines() if line.strip()]
    _title_start, title_end = find_title_span(lines, title)
    start_index = title_end if title_end is not None else 0
    search_lines = lines[start_index : min(len(lines), start_index + 12)]
    author_lines: list[str] = []

    for line in search_lines:
        lowered = line.lower()
        if any(
            fragment in lowered
            for fragment in (
                "cite this",
                "abstract",
                "significance",
                "keywords",
                "current applied physics",
                "biophysical journal",
                "read online",
            )
        ):
            break
        if looks_like_heading(line) or looks_like_affiliation_line(line):
            break

        cleaned_line = clean_author_text(line)
        if not plausible_author_block(cleaned_line):
            if author_lines:
                break
            continue

        author_lines.append(line)
        if len(author_lines) >= 2:
            break

    candidate = clean_author_text(" ".join(author_lines))
    if plausible_author_block(candidate):
        return candidate, "text"
    return "", "missing"


def extract_doi(text: str) -> str:
    match = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", text, flags=re.IGNORECASE)
    return match.group(0) if match else ""


def normalize_heading(line: str) -> str:
    cleaned = re.sub(r"^[^A-Za-z0-9]+", "", line.strip())
    cleaned = collapse_spaces(cleaned).rstrip(":")
    if re.fullmatch(r"(?:[A-Za-z]\s+){3,}[A-Za-z]", cleaned):
        cleaned = cleaned.replace(" ", "")
    return cleaned.lower()


def looks_like_heading(line: str) -> bool:
    normalized = normalize_heading(line)
    if not normalized:
        return False
    if normalized in HEADING_NAMES:
        return True
    if re.fullmatch(r"\d+(\.\d+)*", normalized):
        return True
    if re.match(r"^\d+(\.\d+)*\s+[A-Z]", line):
        return True
    if line.isupper() and len(line.split()) <= 8:
        return True
    return False


def extract_section(text: str, headings: tuple[str, ...], max_chars: int = 1800) -> str:
    lines = text.splitlines()
    heading_set = {heading.lower() for heading in headings}
    collected: list[str] = []
    capture = False

    for line in lines:
        normalized = normalize_heading(line)
        if not capture:
            matched_heading = next(
                (
                    heading
                    for heading in heading_set
                    if normalized == heading or normalized.startswith(f"{heading}:")
                ),
                "",
            )
            if not matched_heading:
                continue

            capture = True
            tail = re.sub(
                rf"^[^A-Za-z0-9]*{re.escape(matched_heading)}[:\s-]*",
                "",
                line,
                count=1,
                flags=re.IGNORECASE,
            )
            tail = collapse_spaces(tail)
            if tail and normalize_heading(tail) != matched_heading:
                collected.append(tail)
            continue

        if collected and looks_like_heading(line):
            break

        stripped = collapse_spaces(line)
        if not stripped:
            if collected:
                break
            continue

        collected.append(stripped)
        if len(" ".join(collected)) >= max_chars:
            break

    return " ".join(collected).strip()


def summarize_fragment(text: str, max_sentences: int = 4, max_chars: int = 900) -> str:
    flat = collapse_spaces(text)
    if not flat:
        return ""

    pieces = re.split(r"(?<=[.!?])\s+", flat)
    kept: list[str] = []
    total_chars = 0
    for piece in pieces:
        sentence = piece.strip()
        if len(sentence) < 30:
            continue
        if total_chars + len(sentence) > max_chars and kept:
            break
        kept.append(sentence)
        total_chars += len(sentence) + 1
        if len(kept) >= max_sentences:
            break

    if kept:
        return " ".join(kept)

    return flat[:max_chars].rstrip()


def extract_summary(text: str) -> str:
    abstract = extract_section(text, ("abstract",), max_chars=1400)
    if abstract:
        summary = summarize_fragment(abstract)
        if summary:
            return summary

    paragraphs = [
        collapse_spaces(paragraph)
        for paragraph in re.split(r"\n\s*\n", text)
        if collapse_spaces(paragraph)
    ]
    for paragraph in paragraphs:
        if len(paragraph) < 120:
            continue
        summary = summarize_fragment(paragraph)
        if summary:
            return summary

    return ""


def clean_sentence(sentence: str) -> str:
    sentence = sentence.replace("\u0001", "")
    sentence = re.sub(r"([A-Za-z])-\s+([A-Za-z])", r"\1\2", sentence)
    return collapse_spaces(sentence)


def sentence_candidates(text: str) -> list[str]:
    flat = clean_sentence(text)
    if not flat:
        return []

    candidates: list[str] = []
    for piece in re.split(r"(?<=[.!?])\s+", flat):
        sentence = clean_sentence(piece)
        if len(sentence) < 35 or len(sentence) > 450:
            continue
        if sentence.endswith("-"):
            continue
        lowered = sentence.lower()
        if any(fragment in lowered for fragment in BAD_SENTENCE_FRAGMENTS):
            continue
        if sum(character.isalpha() for character in sentence) < 20:
            continue
        candidates.append(sentence)
    return candidates


def pick_sentences_from_sources(
    sources: list[str],
    keywords: tuple[str, ...],
    limit: int,
    *,
    require_number: bool = False,
    banned_fragments: tuple[str, ...] = (),
) -> list[str]:
    selected: list[str] = []
    seen: set[str] = set()

    for source in sources:
        if not source:
            continue
        for sentence in sentence_candidates(source):
            lowered = sentence.lower()
            if keywords and not any(keyword in lowered for keyword in keywords):
                continue
            if require_number and not re.search(r"\d", sentence):
                continue
            if any(fragment in lowered for fragment in banned_fragments):
                continue
            normalized = re.sub(r"\W+", " ", lowered).strip()
            if normalized in seen:
                continue
            seen.add(normalized)
            selected.append(sentence)
            if len(selected) >= limit:
                return selected

    return selected


def first_useful_sentence(text: str) -> str:
    sentences = sentence_candidates(text)
    return sentences[0] if sentences else ""


def guess_journal_year(text: str, hints: dict[str, str]) -> tuple[str, str, dict[str, str]]:
    lines = [collapse_spaces(line) for line in text.splitlines() if line.strip()]

    def plausible_journal_name(name: str) -> bool:
        cleaned = collapse_spaces(name).strip(" ,;")
        lowered = cleaned.lower()
        if not cleaned or len(cleaned) < 6 or len(cleaned.split()) > 6:
            return False
        if lowered.split()[0] in MONTHS:
            return False
        if any(
            fragment in lowered
            for fragment in (
                "submitted",
                "accepted",
                "received",
                "available online",
                "article history",
                "keywords",
                "correspondence",
                "editor",
            )
        ):
            return False
        return True

    for line in lines[:80]:
        cleaned = re.sub(r"^Cite This:\s*", "", line, flags=re.IGNORECASE)
        match = re.search(
            r"(?P<journal>[A-Z][A-Za-z.&/ \-]+?)\s+(?P<year>(19|20)\d{2})(?:[,;)]|$)",
            cleaned,
        )
        if match and plausible_journal_name(match.group("journal")):
            return (
                collapse_spaces(match.group("journal")).strip(" ,;"),
                match.group("year"),
                {"journal": "text", "year": "text"},
            )

        match = re.search(
            r",\s*(?P<journal>[A-Z][A-Za-z.&/ \-]+?)\s*\((?P<year>(19|20)\d{2})\)",
            cleaned,
        )
        if match and plausible_journal_name(match.group("journal")):
            return (
                collapse_spaces(match.group("journal")).strip(" ,;"),
                match.group("year"),
                {"journal": "text", "year": "text"},
            )

        match = re.search(
            r"(?P<journal>[A-Z][A-Za-z.&/ \-]+?)\s+\d+[^A-Za-z]+.*?\b(?P<year>(19|20)\d{2})\b",
            cleaned,
        )
        if match and plausible_journal_name(match.group("journal")):
            return (
                collapse_spaces(match.group("journal")).strip(" ,;"),
                match.group("year"),
                {"journal": "text", "year": "text"},
            )

    sources = {"journal": "missing", "year": "missing"}
    journal = ""
    year = ""
    if hints["journal"]:
        journal = hints["journal"]
        sources["journal"] = "filename"
    if hints["year"]:
        year = hints["year"]
        sources["year"] = "filename"
    return journal, year, sources


def extract_core_question(summary: str, text: str) -> list[str]:
    abstract = extract_section(text, ("abstract",), max_chars=1800)
    introduction = extract_section(text, ("introduction", "background", "significance"), max_chars=1800)
    gap_lines = pick_sentences_from_sources(
        [abstract, summary, introduction],
        keywords=(
            "however",
            "remain",
            "remains",
            "unclear",
            "unknown",
            "not been revealed",
            "not been elucidated",
            "little is known",
            "key factor",
            "physical origin",
        ),
        limit=1,
        banned_fragments=("figure",),
    )
    aim_lines = pick_sentences_from_sources(
        [abstract, summary, introduction],
        keywords=(
            "in this study",
            "here, we",
            "here we",
            "we investigate",
            "we compare",
            "we examine",
            "we ask",
            "we test",
        ),
        limit=1,
        banned_fragments=("figure",),
    )
    lines = unique_preserve_order(gap_lines + aim_lines)
    if lines:
        return lines[:2]

    fallback = first_useful_sentence(summary)
    return [fallback] if fallback else []


def extract_main_findings(summary: str, text: str) -> list[str]:
    abstract = extract_section(text, ("abstract",), max_chars=1800)
    results = extract_section(text, ("results and discussion", "results", "discussion", "conclusions", "conclusion"))
    return pick_sentences_from_sources(
        [abstract, summary, results, text[:6000]],
        keywords=(
            "we find",
            "we found",
            "we show",
            "we demonstrated",
            "we demonstrate",
            "we observed",
            "we observe",
            "our results",
            "our data",
            "suggest",
            "indicate",
            "reveal",
            "revealed",
            "showed",
        ),
        limit=4,
        banned_fragments=("figure",),
    )


def extract_methods_overview(summary: str, text: str) -> list[str]:
    abstract = extract_section(text, ("abstract",), max_chars=1800)
    methods = extract_section(
        text,
        ("materials and methods", "methods", "experimental methods", "experimental section"),
        max_chars=2200,
    )
    return pick_sentences_from_sources(
        [abstract, summary, methods, text[:6000]],
        keywords=(
            "using",
            "by using",
            "we used",
            "we utilize",
            "we utilized",
            "we apply",
            "we applied",
            "combining",
            "combined",
            "imaging",
            "microscopy",
            "simulation",
            "simulations",
            "reflectivity",
            "spectroscopy",
            "analysis",
            "analyses",
            "measured",
            "measurements",
            "prepared",
            "collected",
        ),
        limit=4,
        banned_fragments=("figure",),
    )


def has_quantitative_signal(sentence: str) -> bool:
    if not re.search(r"(?<![A-Za-z])\d+(?:\.\d+)?", sentence):
        return False
    if re.search(r"\b\d+(?:\.\d+)?\s*m\b", sentence):
        return True
    if UNIT_PATTERN.search(sentence):
        return True
    if re.search(r"[≈±]", sentence):
        return True
    return False


def extract_quantitative_anchors(summary: str, text: str) -> list[str]:
    abstract = extract_section(text, ("abstract",), max_chars=1800)
    results = extract_section(text, ("results and discussion", "results", "discussion", "conclusions", "conclusion"))
    selected: list[str] = []
    seen: set[str] = set()

    for source in [abstract, summary, results, text[:8000]]:
        if not source:
            continue
        for sentence in sentence_candidates(source):
            lowered = sentence.lower()
            if "figure" in lowered or re.search(r"\bfig(?:ure)?\.?\s*\d", lowered):
                continue
            if sentence.startswith("("):
                continue
            if any(
                fragment in lowered
                for fragment in ("article ", " abstract ", "center for", "department of", "university")
            ):
                continue
            if any(fragment in lowered for fragment in ("histogram", "grayscale", "schematic", "scale bars", "plot")):
                continue
            if not has_quantitative_signal(sentence):
                continue
            normalized = re.sub(r"\W+", " ", lowered).strip()
            if normalized in seen:
                continue
            seen.add(normalized)
            selected.append(sentence)
            if len(selected) >= 4:
                return selected

    return selected


def extract_related_concepts(
    note_title: str,
    summary: str,
    main_findings: list[str],
    methods_overview: list[str],
) -> list[str]:
    title_lower = note_title.lower()
    corpus = " ".join(
        part
        for part in [note_title, summary, " ".join(main_findings[:2]), " ".join(methods_overview[:2])]
        if part
    ).lower()
    corpus = re.sub(r"(?<=\w)[’']s\b", "", corpus)
    tokens = re.findall(r"[a-z][a-z'-]*", corpus)
    counts: Counter[str] = Counter()

    for size in (2, 3, 4):
        for index in range(len(tokens) - size + 1):
            phrase_tokens = tokens[index : index + size]
            if phrase_tokens[0] in STOPWORDS or phrase_tokens[-1] in STOPWORDS:
                continue
            if any(token == "s" or len(token) == 1 for token in phrase_tokens):
                continue
            if sum(token not in STOPWORDS for token in phrase_tokens) < 2:
                continue
            if sum(token in STOPWORDS for token in phrase_tokens) > 1:
                continue
            phrase = " ".join(phrase_tokens)
            if phrase in GENERIC_PHRASES:
                continue
            if phrase_tokens[-1] not in CONCEPT_NOUNS:
                continue
            if phrase_tokens[0] in BAD_CONCEPT_STARTS:
                continue
            counts[phrase] += 1

    chosen: list[str] = []
    for phrase, _count in sorted(
        counts.items(),
        key=lambda item: (
            item[1] + (3 if item[0] in title_lower else 0),
            len(item[0].split()),
            len(item[0]),
        ),
        reverse=True,
    ):
        if _count < 2 and phrase not in title_lower:
            continue
        if any(phrase in existing or existing in phrase for existing in chosen):
            continue
        chosen.append(phrase)
        if len(chosen) >= 5:
            break

    return chosen


def replace_section(template: str, heading: str, body: str) -> str:
    pattern = re.compile(rf"(^## {re.escape(heading)}\n)(.*?)(?=^## |\Z)", flags=re.MULTILINE | re.DOTALL)
    match = pattern.search(template)
    if not match:
        return template

    replacement = f"{match.group(1)}{body.rstrip()}\n\n"
    return template[: match.start()] + replacement + template[match.end() :]


def note_has_meaningful_content(text: str) -> bool:
    placeholder_lines = {
        "## Citation",
        "## Core Question",
        "## System",
        "## Methods",
        "## Key Variables",
        "## Main Findings",
        "## Quantitative Results",
        "## Mechanism / Interpretation",
        "## Evidence Map",
        "## Limitations",
        "## Concepts",
        "## Confidence",
        "## Open Questions",
    }

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "---":
            continue
        if stripped.startswith("# "):
            continue
        if re.match(r"^[A-Za-z0-9_]+:\s*", stripped):
            continue
        if stripped in placeholder_lines:
            continue
        if stripped.startswith("- {{") or stripped.startswith("- "):
            placeholder_content = stripped.startswith("- {{") or stripped in {
                "- 1-3 bullets only.",
                "- What is actually being studied in this paper.",
                "- Only methods used in this paper.",
                "- Keep this to 3-6 bullets.",
                "- Use normalized concept tags only, for example `x-ray-reflectivity`.",
                "- high / medium / low",
            }
            if placeholder_content:
                continue
        return True
    return False


def render_bullets(items: list[str], *, fallback: str = "") -> str:
    items = unique_preserve_order(items)
    if items:
        return "\n".join(f"- {item}" for item in items)
    return fallback


def estimate_confidence(
    text: str,
    metadata: dict[str, object],
    title_source: str,
    authors: str,
    journal: str,
    year: str,
    core_question: list[str],
    main_findings: list[str],
    methods_overview: list[str],
    quantitative_anchors: list[str],
    extraction_warnings: list[str],
) -> str:
    score = 0
    status = str(metadata.get("status") or "").lower()

    if status == "ok":
        score += 2
    elif status == "warning":
        score += 1

    if len(text) >= 5000:
        score += 2
    elif len(text) >= 1500:
        score += 1

    if title_source == "text":
        score += 1
    if authors:
        score += 1
    if journal:
        score += 1
    if year:
        score += 1
    if core_question:
        score += 1
    if len(main_findings) >= 2:
        score += 1
    if methods_overview:
        score += 1
    if quantitative_anchors:
        score += 1

    if extraction_warnings:
        score -= 1
    if any("empty" in warning.lower() or "short" in warning.lower() for warning in extraction_warnings):
        score -= 2
    if any("filename" in warning.lower() for warning in extraction_warnings):
        score -= 1

    if score >= 8:
        return "high"
    if score >= 4:
        return "medium"
    return "low"


def slugify_tag(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower())
    slug = slug.strip("-")
    return slug or "needs-manual-review"


def split_authors(authors: str) -> list[str]:
    if not authors:
        return []
    parts = [collapse_spaces(part) for part in re.split(r",\s*", authors) if collapse_spaces(part)]
    return unique_preserve_order(parts)


def infer_methods(note_title: str, summary: str, text: str, methods_overview: list[str]) -> list[str]:
    haystack = " ".join([note_title, summary, text, " ".join(methods_overview)]).lower()
    method_map = [
        ("spinning disk confocal microscopy", "spinning-disk confocal microscopy"),
        ("confocal microscopy", "confocal microscopy"),
        ("fluorescence microscopy", "fluorescence microscopy"),
        ("synchrotron x-ray reflectivity", "synchrotron x-ray reflectivity"),
        ("x-ray reflectivity", "x-ray reflectivity"),
        ("x-ray scattering", "x-ray scattering"),
        ("molecular dynamics", "all-atom molecular dynamics"),
        ("mass-scaling", "mass-scaling analysis"),
        ("box-counting", "box-counting analysis"),
        ("lacunarity", "lacunarity analysis"),
        ("multifractal", "multifractal analysis"),
        ("electron density", "electron density reconstruction"),
    ]

    methods: list[str] = []
    for keyword, normalized in method_map:
        if keyword in haystack:
            methods.append(normalized)
    return unique_preserve_order(methods)


def infer_variables(note_title: str, summary: str, text: str) -> list[str]:
    haystack = " ".join([note_title, summary, text]).lower()
    variable_map = [
        ("cholesterol", "cholesterol mol%"),
        ("lamellar spacing", "lamellar spacing [D]"),
        ("intermembrane distance", "intermembrane distance [D]"),
        ("domain area", "domain area [A]"),
        ("water layer thickness", "water layer thickness [d_w]"),
        ("hydrogen bonds per water molecule", "hydrogen bonds per water molecule [n_HB]"),
        ("surface range", "surface range [s_c]"),
        ("fwhm", "x-ray peak FWHM"),
        ("electron density", "electron density profile [rho(z)]"),
        ("mass-scaling dimension", "mass-scaling dimension"),
        ("box-counting dimension", "box-counting dimension"),
        ("lacunarity", "lacunarity"),
        ("multifractal spectrum", "multifractal spectrum width [W_T]"),
    ]

    variables: list[str] = []
    for keyword, normalized in variable_map:
        if keyword in haystack:
            variables.append(normalized)
    return unique_preserve_order(variables)


def infer_domain(note_title: str, summary: str, text: str) -> str:
    haystack = " ".join([note_title, summary, text]).lower()
    if any(keyword in haystack for keyword in ("membrane", "lipid", "cholesterol", "bilayer", "multilayer", "raft")):
        return "membrane biophysics"
    if any(keyword in haystack for keyword in ("genome", "chromatin", "nucleus", "nuclei", "cell cycle", "hela")):
        return "genome biophysics"
    return "needs-manual-review"


def infer_system_type(note_title: str, summary: str, text: str) -> str:
    haystack = " ".join([note_title, summary, text]).lower()
    if "phase-separated" in haystack and "multilayer" in haystack:
        return "phase-separated lipid multilayer"
    if "supported" in haystack and "multilayer" in haystack:
        return "supported lipid multilayer"
    if "multilayer" in haystack:
        return "lipid multilayer"
    if ("nucleus" in haystack or "nuclei" in haystack) and "live" in haystack:
        return "live-cell nuclei"
    return "needs-manual-review"


def infer_paper_type(note_title: str, summary: str, text: str, methods: list[str]) -> str:
    haystack = " ".join([note_title, summary, text]).lower()
    has_experiment = any(
        method in methods
        for method in (
            "fluorescence microscopy",
            "confocal microscopy",
            "spinning-disk confocal microscopy",
            "x-ray reflectivity",
            "synchrotron x-ray reflectivity",
            "x-ray scattering",
        )
    )
    has_computation = "all-atom molecular dynamics" in methods
    has_analysis = any(
        method in methods
        for method in (
            "mass-scaling analysis",
            "box-counting analysis",
            "lacunarity analysis",
            "multifractal analysis",
        )
    )

    if any(keyword in haystack for keyword in (" perspective", " viewpoint", " commentary", " opinion")):
        return "perspective"
    if any(keyword in haystack for keyword in ("this review", "in this review", "we review", "review article")):
        return "review"
    if any(keyword in haystack for keyword in (" protocol", "resource", "platform", "pipeline", "toolbox", "software")):
        return "methods_resource"
    if has_experiment or has_computation or has_analysis:
        return "research_article"
    return "unknown"


def infer_include_in_synthesis(paper_type: str) -> bool:
    return paper_type not in {"review", "perspective"}


def extract_system_summary(summary: str, text: str, system_type: str) -> list[str]:
    sources = [summary, extract_section(text, ("materials and methods", "methods", "experimental"), max_chars=900), text[:1200]]
    system_sentences = pick_sentences_from_sources(
        sources,
        keywords=("multilayer", "bilayer", "membrane", "cells", "nucleus", "nuclei", "dataset", "material"),
        limit=1,
    )
    if system_sentences:
        return system_sentences
    if system_type != "needs-manual-review":
        return [system_type]
    return ["Manual review required."]


def extract_mechanism_interpretation(summary: str, text: str) -> list[str]:
    sources = [summary, extract_section(text, ("discussion", "results and discussion", "conclusion", "conclusions"), max_chars=1800)]
    mechanism = pick_sentences_from_sources(
        sources,
        keywords=("suggest", "indicate", "imply", "conclude", "because", "therefore", "mechanism", "interpre"),
        limit=3,
        banned_fragments=("previous work", "reported by", "et al", "literature"),
    )
    if mechanism:
        return mechanism
    return ["Manual review required."]


def render_bullet_section(items: list[str], fallback: str) -> str:
    items = unique_preserve_order(items)
    if items:
        return "\n".join(f"- {item}" for item in items)
    return f"- {fallback}"


def render_quantitative_results(quantitative_anchors: list[str]) -> str:
    anchors = unique_preserve_order(quantitative_anchors)
    if not anchors:
        return "\n".join(
            [
                "- Variable: needs-manual-review",
                "- Value: not extracted automatically",
                "- Units: needs-manual-review",
                "- Conditions: needs-manual-review",
                "- Interpretation (1 line max): normalize from PDF or extracted text during manual review",
            ]
        )

    blocks: list[str] = []
    for anchor in anchors:
        blocks.append(
            "\n".join(
                [
                    "- Variable: needs-manual-review",
                    f"- Value: {anchor}",
                    "- Units: needs-manual-review",
                    "- Conditions: needs-manual-review",
                    "- Interpretation (1 line max): extracted quantitative anchor; normalize during manual review",
                ]
            )
        )
    return "\n\n".join(blocks)


def render_frontmatter(
    note_key: str,
    note_title: str,
    authors: list[str],
    year: str,
    journal: str,
    doi: str,
    source_pdf: str,
    source_text: Path,
    paper_type: str,
    include_in_synthesis: bool,
    domain: str,
    system_type: str,
    methods: list[str],
    variables: list[str],
    concepts: list[str],
    confidence: str,
) -> str:
    def yaml_quote(value: str) -> str:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    tags = ["paper"]
    if paper_type == "review":
        tags.append("review")

    lines = [
        "---",
        "tags:",
    ]
    lines.extend(f"  - {tag}" for tag in tags)
    lines.extend(
        [
        f"note_key: {note_key}",
        f"title: {yaml_quote(note_title)}",
        "authors:",
        ]
    )
    if authors:
        lines.extend(f"  - {author}" for author in authors)
    else:
        lines.append("  - needs-manual-review")

    scalar_pairs = [
        ("year", yaml_quote(year or "needs-manual-review")),
        ("journal", yaml_quote(journal or "needs-manual-review")),
        ("doi", yaml_quote(doi or "needs-manual-review")),
        ("source_pdf", yaml_quote(source_pdf or "needs-manual-review")),
        ("source_text", yaml_quote(str(source_text.relative_to(ROOT)))),
        ("paper_type", yaml_quote(paper_type)),
        ("include_in_synthesis", "true" if include_in_synthesis else "false"),
        ("domain", yaml_quote(domain)),
        ("system_type", yaml_quote(system_type)),
    ]
    lines.extend(f"{key}: {value}" for key, value in scalar_pairs)

    for key, values in (
        ("methods", methods),
        ("variables", variables),
        ("concepts", concepts),
    ):
        lines.append(f"{key}:")
        if values:
            lines.extend(f"  - {yaml_quote(value)}" for value in values)
        else:
            lines.append(f"  - {yaml_quote('needs-manual-review')}")

    lines.append(f"confidence: {yaml_quote(confidence)}")
    lines.append("---")
    return "\n".join(lines)


def render_note(
    template: str,
    note_title: str,
    extracted_path: Path,
    extracted_metadata: dict[str, object],
    authors: str,
    journal: str,
    year: str,
    doi: str,
    summary: str,
    text: str,
    core_question: list[str],
    main_findings: list[str],
    methods_overview: list[str],
    quantitative_anchors: list[str],
    related_concepts: list[str],
    extraction_warnings: list[str],
    extraction_confidence: str,
) -> str:
    del template

    authors_list = split_authors(authors)
    concepts = unique_preserve_order([slugify_tag(item) for item in related_concepts if item.strip()])
    methods = infer_methods(note_title, summary, text, methods_overview)
    variables = infer_variables(note_title, summary, text)
    domain = infer_domain(note_title, summary, text)
    system_type = infer_system_type(note_title, summary, text)
    paper_type = infer_paper_type(note_title, summary, text, methods)
    include_in_synthesis = infer_include_in_synthesis(paper_type)
    system_summary = extract_system_summary(summary, text, system_type)
    mechanism = extract_mechanism_interpretation(summary, text)

    open_questions: list[str] = []
    if extraction_warnings:
        open_questions.extend(f"Review target: {warning}" for warning in extraction_warnings[:3])
    if quantitative_anchors:
        open_questions.append("Normalize extracted quantitative anchors into structured `Quantitative Results` entries.")
    else:
        open_questions.append("Add paper-specific quantitative results after reviewing the PDF.")
    open_questions.append("Populate `Evidence Map` from figure captions or direct PDF review.")
    open_questions = unique_preserve_order(open_questions)

    frontmatter = render_frontmatter(
        note_key=extracted_path.stem,
        note_title=note_title,
        authors=authors_list,
        year=year,
        journal=journal,
        doi=doi,
        source_pdf=str(extracted_metadata.get("source_pdf") or ""),
        source_text=extracted_path,
        paper_type=paper_type,
        include_in_synthesis=include_in_synthesis,
        domain=domain,
        system_type=system_type,
        methods=methods,
        variables=variables,
        concepts=concepts,
        confidence=extraction_confidence,
    )

    citation_lines = []
    citation_lines.append(f"- Authors: {authors or 'needs-manual-review'}")
    citation_lines.append(f"- Year: {year or 'needs-manual-review'}")
    citation_lines.append(f"- Journal: {journal or 'needs-manual-review'}")
    citation_lines.append(f"- DOI: {doi or 'needs-manual-review'}")

    sections = [
        frontmatter,
        "",
        f"# {note_title}",
        "",
        "## Citation",
        "\n".join(citation_lines),
        "",
        "## Core Question",
        render_bullet_section(core_question, "Manual review required."),
        "",
        "## System",
        render_bullet_section(system_summary, "Manual review required."),
        "",
        "## Methods",
        render_bullet_section(methods_overview, "Manual review required."),
        "",
        "## Key Variables",
        render_bullet_section(variables, "needs-manual-review"),
        "",
        "## Main Findings",
        render_bullet_section(main_findings, "Manual review required."),
        "",
        "## Quantitative Results",
        render_quantitative_results(quantitative_anchors),
        "",
        "## Mechanism / Interpretation",
        render_bullet_section(mechanism, "Manual review required."),
        "",
        "## Evidence Map",
        "- Manual figure review required before downstream synthesis.",
        "",
        "## Limitations",
        "- Manual review required to separate paper limitations from extraction limitations.",
        "",
        "## Concepts",
        render_bullet_section(concepts, "needs-manual-review"),
        "",
        "## Confidence",
        f"- {extraction_confidence}",
        "",
        "## Open Questions",
        render_bullet_section(open_questions, "Manual review required."),
    ]
    return "\n".join(sections)


def main() -> None:
    args = parse_args()

    if not EXTRACTED_DIR.exists():
        print("raw/extracted does not exist. Run scripts/extract_papers.py first.")
        return

    if not TEMPLATE_PATH.exists():
        print("templates/paper_note_template.md does not exist")
        return

    extracted_paths = sorted(
        path
        for path in EXTRACTED_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}
    )
    if not extracted_paths:
        print("No extracted text files found in raw/extracted")
        return

    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    for extracted_path in extracted_paths:
        note_path = NOTES_DIR / f"{extracted_path.stem}.md"
        if note_path.exists() and not args.force:
            existing_text = note_path.read_text(encoding="utf-8", errors="replace")
            if note_has_meaningful_content(existing_text):
                print(f"Skipped {note_path.relative_to(ROOT)} (already contains content; use --force to overwrite)")
                continue

        extracted_metadata, text = parse_extracted_file(extracted_path)
        hints = filename_hints(extracted_path.stem)
        fallback_title = existing_note_title(note_path) or hints["fallback_title"]
        note_title, title_source = guess_title(text, fallback_title)
        authors, authors_source = guess_authors(text, note_title)
        journal, year, journal_year_sources = guess_journal_year(text, hints)

        doi = extract_doi(text)
        summary = extract_summary(text)
        core_question = extract_core_question(summary, text)
        main_findings = extract_main_findings(summary, text)
        methods_overview = extract_methods_overview(summary, text)
        quantitative_anchors = extract_quantitative_anchors(summary, text)
        related_concepts = extract_related_concepts(note_title, summary, main_findings, methods_overview)

        extraction_warnings = list(extracted_metadata.get("warnings", []))
        if title_source != "text":
            extraction_warnings.append("Title fell back to the extracted filename stem.")
        if authors_source != "text":
            extraction_warnings.append("Authors were not confidently extracted from the text.")
        if journal_year_sources["journal"] == "filename":
            extraction_warnings.append("Journal fell back to the extracted filename stem.")
        if journal_year_sources["year"] == "filename":
            extraction_warnings.append("Year fell back to the extracted filename stem.")
        if not quantitative_anchors:
            extraction_warnings.append("No quantitative anchors were confidently extracted.")
        extraction_warnings = unique_preserve_order(extraction_warnings)

        extraction_confidence = estimate_confidence(
            text=text,
            metadata=extracted_metadata,
            title_source=title_source,
            authors=authors,
            journal=journal,
            year=year,
            core_question=core_question,
            main_findings=main_findings,
            methods_overview=methods_overview,
            quantitative_anchors=quantitative_anchors,
            extraction_warnings=extraction_warnings,
        )

        note_text = render_note(
            template=template,
            note_title=note_title,
            extracted_path=extracted_path,
            extracted_metadata=extracted_metadata,
            authors=authors,
            journal=journal,
            year=year,
            doi=doi,
            summary=summary,
            text=text,
            core_question=core_question,
            main_findings=main_findings,
            methods_overview=methods_overview,
            quantitative_anchors=quantitative_anchors,
            related_concepts=related_concepts,
            extraction_warnings=extraction_warnings,
            extraction_confidence=extraction_confidence,
        )
        note_path.write_text(note_text.rstrip() + "\n", encoding="utf-8")
        print(f"Wrote {note_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
