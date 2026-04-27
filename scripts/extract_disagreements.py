#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any

import yaml

from kb_utils import (
    CONCEPTS_DIR,
    META_QUESTIONS_DIR,
    OUTPUTS_DIR,
    QUESTIONS_DIR,
    SYSTEMS_DIR,
    VARIABLES_DIR,
    MarkdownRecord,
    load_layer_records,
    relative_link,
    slug_to_title,
    write_text_if_changed,
)

PLACEHOLDER_TOKENS = {"", "(none)", "none", "tbd", "todo", "n/a", "na", "-", "--"}

LAYER_ORDER = ["meta_questions", "questions", "systems", "concepts", "variables"]
LAYER_DIRS = {
    "meta_questions": META_QUESTIONS_DIR,
    "questions": QUESTIONS_DIR,
    "systems": SYSTEMS_DIR,
    "concepts": CONCEPTS_DIR,
    "variables": VARIABLES_DIR,
}

DISAGREEMENT_SECTIONS = {
    "meta_questions": "Differences",
    "questions": "Competing Models",
    "systems": "Competing Models (if any)",
    "concepts": "Conflicts / Discrepancies",
    "variables": "Conflicts / Ambiguities",
}

# Layers where the disagreement section is expected by KB convention.
# Systems use "(if any)" so absence is allowed.
SECTION_REQUIRED_BY_CONVENTION = {"meta_questions", "questions", "concepts", "variables"}

LAYER_DEFAULT_ABSTRACTION = {
    "meta_questions": "theoretical",
    "systems": "mechanistic",
    "concepts": "theoretical",
    "variables": "methodological",
}

ABSTRACTION_KEYWORDS = [
    ("methodological", re.compile(r"\b(measure|measurement|assay|method|threshold|calibration|protocol|readout|descriptor|metric)\b", re.IGNORECASE)),
    ("empirical", re.compile(r"\b(observe|observed|report|reported|finding|findings|correlation|trend|data)\b", re.IGNORECASE)),
    ("theoretical", re.compile(r"\b(model|theory|framework|principle|formalism|hypothesis)\b", re.IGNORECASE)),
    ("normative", re.compile(r"\b(should|must|ought|best practice|recommend|preferred)\b", re.IGNORECASE)),
]

BULLET_PATTERN = re.compile(r"^\s*[-*]\s+")
LABEL_SPLIT_PATTERN = re.compile(r"\s+[-—:]\s+")


@dataclass
class Extraction:
    qid: str
    layer: str
    page_path: Path
    question: str
    subfield: str
    abstraction: str
    positions: list[dict[str, str]]
    source_sections: list[str]
    extraction_context: dict[str, str] = field(default_factory=dict)


@dataclass
class LayerResult:
    extracted: list[Extraction] = field(default_factory=list)
    skipped_empty: list[Path] = field(default_factory=list)
    skipped_missing_section: list[Path] = field(default_factory=list)


def is_placeholder_section(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    cleaned_lines = []
    for line in stripped.splitlines():
        bare = BULLET_PATTERN.sub("", line).strip().lower()
        if bare:
            cleaned_lines.append(bare)
    if not cleaned_lines:
        return True
    return all(line in PLACEHOLDER_TOKENS for line in cleaned_lines)


def parse_positions(section_text: str) -> list[dict[str, str]]:
    positions: list[dict[str, str]] = []
    current: list[str] | None = None
    for line in section_text.splitlines():
        if BULLET_PATTERN.match(line):
            if current is not None:
                positions.append(_finalize_position(current))
            current = [BULLET_PATTERN.sub("", line)]
        elif line.strip() and current is not None:
            current.append(line.strip())
    if current is not None:
        positions.append(_finalize_position(current))
    return [p for p in positions if p["summary"].strip()]


def _finalize_position(lines: list[str]) -> dict[str, str]:
    text = " ".join(part.strip() for part in lines if part.strip())
    match = LABEL_SPLIT_PATTERN.search(text)
    if match and match.start() <= 80:
        label = text[: match.start()].strip()
        summary = text[match.end():].strip()
    else:
        words = text.split()
        label = " ".join(words[:6])
        if len(words) > 6:
            label = label.rstrip(",.;:") + "..."
        summary = text
    return {"label": label, "summary": summary}


def infer_abstraction(layer: str, title: str, sections: dict[str, str]) -> str:
    if layer in LAYER_DEFAULT_ABSTRACTION:
        return LAYER_DEFAULT_ABSTRACTION[layer]
    haystack_parts = [title, sections.get("Core Question", ""), sections.get("Competing Models", "")]
    haystack = " ".join(haystack_parts).lower()
    for tag, pattern in ABSTRACTION_KEYWORDS:
        if pattern.search(haystack):
            return tag
    return "mechanistic"


def derive_subfield(record: MarkdownRecord, layer: str) -> str:
    if layer == "meta_questions":
        tags = record.frontmatter.get("tags")
        if isinstance(tags, list):
            filtered = [
                str(tag).strip()
                for tag in tags
                if str(tag).strip() and str(tag).strip().lower() != "meta-question"
            ]
            if filtered:
                return ",".join(filtered)
        return record.path.stem
    for key in ("domain", "cluster", "subfield"):
        value = record.frontmatter.get(key)
        if isinstance(value, list) and value:
            return str(value[0]).strip()
        if isinstance(value, str) and value.strip():
            return value.strip()
    return record.path.stem


def derive_question(layer: str, record: MarkdownRecord) -> str:
    title = record.title or slug_to_title(record.path.stem)
    if layer in {"meta_questions", "questions"}:
        return title
    if layer == "systems":
        return f"What are the competing models for {title}?"
    if layer == "concepts":
        return f"What disagreements remain about {title}?"
    if layer == "variables":
        return f"What ambiguities remain for {title}?"
    return title


def collect_extraction_context(layer: str, sections: dict[str, str]) -> dict[str, str]:
    context: dict[str, str] = {}
    if layer == "meta_questions":
        for name, key in (
            ("Systems Involved", "systems_involved"),
            ("Shared Structure", "shared_structure"),
            ("Unified Hypothesis", "unified_hypothesis"),
            ("Testable Predictions", "testable_predictions"),
        ):
            text = sections.get(name, "").strip()
            if text:
                context[key] = text
    elif layer == "questions":
        for name in ("Competing Models", "Supporting Evidence"):
            text = sections.get(name, "").strip()
            if text:
                context[name] = text
    elif layer == "systems":
        for name in ("Competing Models (if any)", "Interpretation"):
            text = sections.get(name, "").strip()
            if text:
                context[name] = text
    elif layer == "concepts":
        text = sections.get("Conflicts / Discrepancies", "").strip()
        if text:
            context["Conflicts / Discrepancies"] = text
    elif layer == "variables":
        text = sections.get("Conflicts / Ambiguities", "").strip()
        if text:
            context["Conflicts / Ambiguities"] = text
    return context


def collect_source_sections(layer: str, sections: dict[str, str]) -> list[str]:
    layer_section_lists = {
        "meta_questions": ["Differences"],
        "questions": ["Core Question", "Competing Models", "Supporting Evidence", "Missing Evidence", "Confidence"],
        "systems": ["Variables", "Interaction Structure", "Interpretation", "Competing Models (if any)"],
        "concepts": ["Definition", "Evidence Across Papers", "Conflicts / Discrepancies"],
        "variables": ["Definition", "Conflicts / Ambiguities"],
    }
    return [name for name in layer_section_lists.get(layer, []) if sections.get(name, "").strip()]


def build_layer_result(layer: str, qid_counter: list[int]) -> LayerResult:
    result = LayerResult()
    section_name = DISAGREEMENT_SECTIONS[layer]
    records = load_layer_records(LAYER_DIRS[layer])
    for record in records:
        if section_name not in record.sections:
            if layer in SECTION_REQUIRED_BY_CONVENTION:
                result.skipped_missing_section.append(record.path)
            continue
        section_text = record.sections.get(section_name, "")
        if is_placeholder_section(section_text):
            result.skipped_empty.append(record.path)
            continue
        positions = parse_positions(section_text)
        if not positions:
            result.skipped_empty.append(record.path)
            continue
        qid_counter[0] += 1
        extraction = Extraction(
            qid=f"Q{qid_counter[0]:03d}",
            layer=layer,
            page_path=record.path,
            question=derive_question(layer, record),
            subfield=derive_subfield(record, layer),
            abstraction=infer_abstraction(layer, record.title, record.sections),
            positions=positions,
            source_sections=collect_source_sections(layer, record.sections),
            extraction_context=collect_extraction_context(layer, record.sections),
        )
        result.extracted.append(extraction)
    return result


def extraction_to_yaml_entry(extraction: Extraction) -> dict[str, Any]:
    rel_path = extraction.page_path.relative_to(extraction.page_path.parents[1]).as_posix()
    entry: dict[str, Any] = {
        "id": extraction.qid,
        "question": extraction.question,
        "subfield": extraction.subfield,
        "abstraction": extraction.abstraction,
        "expert_notes": {
            "positions": [
                {"label": pos["label"], "summary": pos["summary"]}
                for pos in extraction.positions
            ],
            "crux": "",
            "common_flattening": "",
        },
        "extraction_context": extraction.extraction_context,
        "provenance": {
            "source_layer": extraction.layer,
            "source_page": rel_path,
            "source_sections": extraction.source_sections,
        },
    }
    return entry


def emit_yaml(extractions: list[Extraction]) -> str:
    documents = [extraction_to_yaml_entry(e) for e in extractions]
    text = yaml.safe_dump(
        documents,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
        width=100,
    )
    parsed = yaml.safe_load(text)
    if not isinstance(parsed, list) or len(parsed) != len(documents):
        raise RuntimeError("YAML round-trip parse failed: structure mismatch.")
    for original, reparsed in zip(documents, parsed):
        if original["id"] != reparsed["id"]:
            raise RuntimeError(f"YAML round-trip parse failed at {original['id']}.")
    return text


def render_report(layer_results: dict[str, LayerResult], report_path: Path) -> str:
    total_extracted = sum(len(r.extracted) for r in layer_results.values())
    total_skipped_empty = sum(len(r.skipped_empty) for r in layer_results.values())
    total_skipped_missing = sum(len(r.skipped_missing_section) for r in layer_results.values())

    lines: list[str] = []
    lines.append("# Disagreement Extraction Report")
    lines.append("")
    lines.append("Generated from meta_questions, questions, systems, concepts, and variables layers.")
    lines.append("Only populated disagreement-shaped sections are extracted; placeholders are skipped.")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Total extractions: {total_extracted}")
    lines.append(f"- Pages skipped due to empty/placeholder disagreement section: {total_skipped_empty}")
    lines.append(f"- Pages missing the conventional disagreement section: {total_skipped_missing}")
    lines.append("")
    lines.append("## Per-Layer Counts")
    lines.append("| Layer | Extracted | Skipped (empty) | Skipped (missing section) |")
    lines.append("| --- | --- | --- | --- |")
    for layer in LAYER_ORDER:
        r = layer_results[layer]
        lines.append(f"| `{layer}` | {len(r.extracted)} | {len(r.skipped_empty)} | {len(r.skipped_missing_section)} |")
    lines.append("")

    lines.append("## Abstraction Tag Distribution")
    abstraction_tags = ["empirical", "mechanistic", "theoretical", "methodological", "normative"]
    header = "| Layer | " + " | ".join(abstraction_tags) + " | total |"
    sep = "| --- |" + " --- |" * (len(abstraction_tags) + 1)
    lines.append(header)
    lines.append(sep)
    for layer in LAYER_ORDER:
        r = layer_results[layer]
        counts = {tag: 0 for tag in abstraction_tags}
        for e in r.extracted:
            counts[e.abstraction] = counts.get(e.abstraction, 0) + 1
        row = f"| `{layer}` | " + " | ".join(str(counts[tag]) for tag in abstraction_tags) + f" | {len(r.extracted)} |"
        lines.append(row)
    lines.append("")

    lines.append("## Extracted Questions")
    lines.append("| ID | Source Layer | Source Page | Position Count |")
    lines.append("| --- | --- | --- | --- |")
    for layer in LAYER_ORDER:
        for extraction in layer_results[layer].extracted:
            link = f"[{extraction.page_path.name}]({relative_link(report_path, extraction.page_path)})"
            lines.append(f"| {extraction.qid} | `{layer}` | {link} | {len(extraction.positions)} |")
    lines.append("")

    lines.append("## Pages With Empty Disagreement Sections (Populate Next)")
    any_empty = False
    for layer in LAYER_ORDER:
        empties = layer_results[layer].skipped_empty
        if not empties:
            continue
        any_empty = True
        lines.append(f"### `{layer}`")
        for path in empties:
            link = f"[{path.name}]({relative_link(report_path, path)})"
            lines.append(f"- {link}")
        lines.append("")
    if not any_empty:
        lines.append("- None.")
        lines.append("")

    lines.append("## Pages Missing Disagreement Section By KB Convention")
    any_missing = False
    for layer in LAYER_ORDER:
        if layer not in SECTION_REQUIRED_BY_CONVENTION:
            continue
        missing = layer_results[layer].skipped_missing_section
        if not missing:
            continue
        any_missing = True
        lines.append(f"### `{layer}` (expected section: `{DISAGREEMENT_SECTIONS[layer]}`)")
        for path in missing:
            link = f"[{path.name}]({relative_link(report_path, path)})"
            lines.append(f"- {link}")
        lines.append("")
    if not any_missing:
        lines.append("- None.")
        lines.append("")

    return "\n".join(lines)


def print_dry_run(layer_results: dict[str, LayerResult]) -> None:
    print("Disagreement extraction dry run")
    print("=" * 60)
    for layer in LAYER_ORDER:
        r = layer_results[layer]
        print(f"\n[{layer}]")
        print(f"  extracted: {len(r.extracted)}")
        print(f"  skipped (empty/placeholder): {len(r.skipped_empty)}")
        print(f"  skipped (missing section): {len(r.skipped_missing_section)}")
        if r.extracted:
            print(f"  candidate pages:")
            for e in r.extracted:
                print(f"    - {e.qid} {e.page_path.name} ({len(e.positions)} positions, abstraction={e.abstraction})")
        if r.skipped_empty:
            print(f"  empty/placeholder pages:")
            for p in r.skipped_empty:
                print(f"    - {p.name}")
        if r.skipped_missing_section:
            print(f"  missing-section pages:")
            for p in r.skipped_missing_section:
                print(f"    - {p.name}")
    print("\n" + "=" * 60)
    print("Sample extraction per layer (first non-empty):")
    for layer in LAYER_ORDER:
        r = layer_results[layer]
        if not r.extracted:
            continue
        sample = r.extracted[0]
        print(f"\n--- {layer}: {sample.qid} ---")
        entry = extraction_to_yaml_entry(sample)
        print(yaml.safe_dump([entry], sort_keys=False, default_flow_style=False, allow_unicode=True, width=100))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract populated disagreement sections from KB synthesis layers into an OpenQuestion-format YAML."
    )
    parser.add_argument("--dry-run", action="store_true", help="Report what would be extracted without writing files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    qid_counter = [0]
    layer_results: dict[str, LayerResult] = {}
    for layer in LAYER_ORDER:
        layer_results[layer] = build_layer_result(layer, qid_counter)

    if args.dry_run:
        print_dry_run(layer_results)
        return

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    yaml_path = OUTPUTS_DIR / "disagreement_questions.yaml"
    report_path = OUTPUTS_DIR / "disagreement_extraction_report.md"

    all_extractions: list[Extraction] = []
    for layer in LAYER_ORDER:
        all_extractions.extend(layer_results[layer].extracted)

    yaml_text = emit_yaml(all_extractions)
    report_text = render_report(layer_results, report_path)

    write_text_if_changed(yaml_path, yaml_text)
    write_text_if_changed(report_path, report_text)
    print(f"Wrote {yaml_path}")
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
