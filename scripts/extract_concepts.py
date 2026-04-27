#!/usr/bin/env python3

from __future__ import annotations

from collections import defaultdict

from kb_utils import (
    OUTPUTS_DIR,
    ensure_list,
    load_concept_records,
    load_note_records,
    load_synthesis_note_records,
    relative_link,
    resolved_paper_type,
    slug_to_title,
    write_text_if_changed,
)

PLACEHOLDER_CONCEPTS = {"needs-manual-review"}


def note_link(report_path, record) -> str:
    return f"[{record.title}]({relative_link(report_path, record.path)})"


def concept_link(report_path, concept_slug: str, concept_record) -> str:
    if concept_record is None:
        return "-"
    title = str(concept_record.frontmatter.get("title") or concept_record.title or slug_to_title(concept_slug))
    return f"[{title}]({relative_link(report_path, concept_record.path)})"


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def main() -> None:
    records = [
        record
        for record in load_synthesis_note_records()
    ]
    scanned_notes = len(load_note_records())
    concept_records = load_concept_records()
    concept_lookup = {
        str(record.frontmatter.get("concept_id", "")).strip(): record
        for record in concept_records
    }

    grouped = defaultdict(list)
    for record in records:
        for concept in ensure_list(record.frontmatter.get("concepts")):
            if concept in PLACEHOLDER_CONCEPTS:
                continue
            grouped[concept].append(record)

    report_path = OUTPUTS_DIR / "concept_report.md"
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    missing_pages: list[str] = []
    for concept in sorted(grouped):
        concept_record = concept_lookup.get(concept)
        if concept_record is None:
            missing_pages.append(concept)
        paper_links = "<br>".join(note_link(report_path, record) for record in sorted(grouped[concept], key=lambda item: item.title.lower()))
        rows.append(
            [
                f"`{concept}`",
                str(len(grouped[concept])),
                concept_link(report_path, concept, concept_record),
                paper_links,
            ]
        )

    three_plus = [
        concept for concept in sorted(grouped)
        if len(grouped[concept]) >= 3
    ]
    three_plus_block = "\n".join(f"- `{concept}` ({len(grouped[concept])} papers)" for concept in three_plus) if three_plus else "- None."
    if three_plus:
        upgrade_candidates_block = "\n".join(
            f"- `{concept}` now meets the >=3-paper threshold and is a good candidate for a concept-page upgrade if synthesis value stays high."
            for concept in three_plus
        )
    else:
        upgrade_candidates_block = "- None. No concept tag currently spans 3 or more notes, so no concept met the stronger synthesis upgrade threshold in this update."

    missing_block = "\n".join(f"- `{concept}`" for concept in missing_pages) if missing_pages else "- None"
    report = "\n".join(
        [
            "# Concept Report",
            "",
            "Generated from note frontmatter concept tags, excluding notes with `include_in_synthesis: false`.",
            "",
            "## Summary",
            f"- Notes scanned: {scanned_notes}",
            f"- Notes included in synthesis: {len(records)}",
            f"- Notes excluded from synthesis: {scanned_notes - len(records)}",
            f"- Unique concept tags: {len(grouped)}",
            f"- Concept pages present: {len(concept_lookup)}",
            f"- Missing concept pages: {len(missing_pages)}",
            f"- Concepts with >=3 papers: {len(three_plus)}",
            "",
            "## Concept Coverage",
            render_table(["Concept Tag", "Paper Count", "Concept Page", "Papers"], rows),
            "",
            "## Concepts With >=3 Papers",
            three_plus_block,
            "",
            "## Concepts Meeting The Stronger Synthesis Upgrade Threshold",
            upgrade_candidates_block,
            "",
            "## Missing Concept Pages",
            missing_block,
        ]
    )
    write_text_if_changed(report_path, report)
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
