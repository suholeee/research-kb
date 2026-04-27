#!/usr/bin/env python3

from __future__ import annotations

from collections import Counter

from kb_utils import (
    INDEXES_DIR,
    ensure_list,
    load_concept_records,
    load_note_records,
    resolved_include_in_synthesis,
    resolved_paper_type,
)


def print_counter(title: str, counter: Counter[str]) -> None:
    print(title)
    if not counter:
        print("  (none)")
        return
    for key, count in counter.most_common():
        print(f"  {key}: {count}")


def main() -> None:
    notes = load_note_records()
    concepts = load_concept_records()
    index_files = [path for path in INDEXES_DIR.glob("*.md") if path.name != "README.md"]

    year_counter = Counter(str(note.frontmatter.get("year", "")) for note in notes)
    paper_type_counter = Counter(resolved_paper_type(note) for note in notes)
    synthesis_counter = Counter("true" if resolved_include_in_synthesis(note) else "false" for note in notes)
    domain_counter = Counter(str(note.frontmatter.get("domain", "")) for note in notes)
    confidence_counter = Counter(str(note.frontmatter.get("confidence", "")) for note in notes)
    method_counter = Counter(
        method
        for note in notes
        for method in ensure_list(note.frontmatter.get("methods"))
    )
    concept_counter = Counter(
        concept
        for note in notes
        for concept in ensure_list(note.frontmatter.get("concepts"))
    )

    print(f"Notes: {len(notes)}")
    print(f"Concept pages: {len(concepts)}")
    print(f"Index files: {len(index_files)}")
    print()
    print_counter("Years", year_counter)
    print()
    print_counter("Paper Types", paper_type_counter)
    print()
    print_counter("Include In Synthesis", synthesis_counter)
    print()
    print_counter("Domains", domain_counter)
    print()
    print_counter("Confidence", confidence_counter)
    print()
    print_counter("Methods", method_counter)
    print()
    print_counter("Concept Tags", concept_counter)
    print()

    unknown_notes = sorted(
        note.path.name
        for note in notes
        if resolved_paper_type(note) == "unknown"
    )
    print("Unknown Paper Types")
    if unknown_notes:
        for name in unknown_notes:
            print(f"  {name}")
    else:
        print("  (none)")


if __name__ == "__main__":
    main()
