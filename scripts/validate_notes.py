#!/usr/bin/env python3

from __future__ import annotations

import sys

from kb_utils import (
    CANONICAL_PAPER_TYPES,
    REQUIRED_FRONTMATTER_FIELDS,
    REQUIRED_NOTE_SECTIONS,
    ROOT,
    ensure_list,
    is_normalized_slug,
    load_note_records,
    normalized_note_tags,
    resolved_include_in_synthesis,
    resolved_paper_type,
)


ALLOWED_CONFIDENCE = {"high", "medium", "low"}


def main() -> int:
    records = load_note_records()
    if not records:
        print("No note files found in notes/")
        return 0

    errors: list[str] = []
    warnings: list[str] = []

    for record in records:
        relpath = record.path.relative_to(ROOT)
        fm = record.frontmatter

        for field in REQUIRED_FRONTMATTER_FIELDS:
            if field not in fm:
                errors.append(f"{relpath}: missing frontmatter field `{field}`")
                continue
            value = fm[field]
            if isinstance(value, list):
                if not ensure_list(value):
                    errors.append(f"{relpath}: frontmatter field `{field}` is empty")
            elif str(value).strip() == "":
                errors.append(f"{relpath}: frontmatter field `{field}` is empty")

        note_key = str(fm.get("note_key", "")).strip()
        if note_key and note_key != record.path.stem:
            errors.append(f"{relpath}: note_key `{note_key}` does not match filename stem `{record.path.stem}`")

        title = str(fm.get("title", "")).strip()
        if title and record.title and title != record.title:
            errors.append(f"{relpath}: frontmatter title does not match `#` heading")

        section_order = list(record.sections.keys())
        for section in REQUIRED_NOTE_SECTIONS:
            if section not in record.sections:
                errors.append(f"{relpath}: missing section `## {section}`")
            elif not record.sections[section].strip():
                errors.append(f"{relpath}: section `## {section}` is empty")

        if section_order[: len(REQUIRED_NOTE_SECTIONS)] != REQUIRED_NOTE_SECTIONS:
            warnings.append(f"{relpath}: section order differs from KB convention")

        confidence = str(fm.get("confidence", "")).strip().lower()
        if confidence and confidence not in ALLOWED_CONFIDENCE:
            errors.append(f"{relpath}: invalid confidence `{confidence}`")

        paper_type = str(fm.get("paper_type", "")).strip()
        if paper_type and paper_type not in CANONICAL_PAPER_TYPES:
            errors.append(f"{relpath}: invalid paper_type `{paper_type}`")

        include_in_synthesis = fm.get("include_in_synthesis")
        if not isinstance(include_in_synthesis, bool):
            errors.append(f"{relpath}: `include_in_synthesis` must be `true` or `false`")

        for concept in ensure_list(fm.get("concepts")):
            if not is_normalized_slug(concept):
                errors.append(f"{relpath}: concept tag `{concept}` is not normalized kebab-case")

        for method in ensure_list(fm.get("methods")):
            if method != method.lower():
                warnings.append(f"{relpath}: method `{method}` is not normalized lower-case")

        for variable in ensure_list(fm.get("variables")):
            if not variable:
                errors.append(f"{relpath}: empty variable entry in frontmatter")

        if "Confidence" in record.sections:
            confidence_section = record.sections["Confidence"].strip().lower()
            if confidence and confidence not in confidence_section:
                warnings.append(f"{relpath}: `## Confidence` section does not mirror frontmatter confidence")

        tags = ensure_list(fm.get("tags"))
        if "paper" not in tags:
            errors.append(f"{relpath}: note tags must include `paper`")
        if resolved_paper_type(record) == "review" and "review" not in tags:
            errors.append(f"{relpath}: review notes must include tag `review`")
        if resolved_paper_type(record) != "review" and "review" in tags:
            errors.append(f"{relpath}: non-review note should not carry tag `review`")

        if paper_type and paper_type != resolved_paper_type(record):
            warnings.append(
                f"{relpath}: paper_type `{paper_type}` does not match resolver result `{resolved_paper_type(record)}`"
            )
        if isinstance(include_in_synthesis, bool) and include_in_synthesis != resolved_include_in_synthesis(record):
            warnings.append(
                f"{relpath}: include_in_synthesis `{include_in_synthesis}` differs from default resolver result `{resolved_include_in_synthesis(record)}`"
            )
        if tags != normalized_note_tags(record):
            warnings.append(f"{relpath}: note tags differ from normalized tag set {normalized_note_tags(record)}")

    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"- {error}")

    if warnings:
        print("Validation warnings:")
        for warning in warnings:
            print(f"- {warning}")

    if not errors and not warnings:
        print(f"Validated {len(records)} notes with no issues.")
    elif not errors:
        print(f"Validated {len(records)} notes with warnings.")
    else:
        print(f"Validated {len(records)} notes with errors.")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
