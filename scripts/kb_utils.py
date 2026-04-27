#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
NOTES_DIR = ROOT / "notes"
CONCEPTS_DIR = ROOT / "concepts"
INDEXES_DIR = ROOT / "indexes"
OUTPUTS_DIR = ROOT / "outputs"
META_QUESTIONS_DIR = ROOT / "meta_questions"
QUESTIONS_DIR = ROOT / "questions"
SYSTEMS_DIR = ROOT / "systems"
VARIABLES_DIR = ROOT / "variables"

CANONICAL_PAPER_TYPES = {
    "research_article",
    "review",
    "perspective",
    "methods_resource",
    "unknown",
}
LEGACY_RESEARCH_PAPER_TYPES = {
    "computational",
    "experimental",
    "mixed",
    "preprint",
    "theory",
}
LEGACY_METHOD_PAPER_TYPES = {
    "method",
    "methods",
    "methods-resource",
}
LEGACY_UNKNOWN_PAPER_TYPES = {
    "conference abstract",
    "duplicate-record",
    "needs-manual-review",
}
PLACEHOLDER_VALUES = {
    "duplicate-record",
    "needs-manual-review",
}
REVIEW_TITLE_PATTERN = re.compile(r"\b(review|reviews|reviewing|overview|survey|primer)\b")
PERSPECTIVE_TITLE_PATTERN = re.compile(r"\b(perspective|viewpoint|commentary|opinion)\b")
REVIEW_BODY_PATTERN = re.compile(
    r"\b(this review|this is a review|in this review|here we review|we review|review discusses|review article)\b"
)
PERSPECTIVE_BODY_PATTERN = re.compile(
    r"\b(this perspective|in this perspective|this commentary|this viewpoint|this opinion)\b"
)
METHOD_RESOURCE_PATTERN = re.compile(
    r"\b(method|methods|methodology|protocol|resource|platform|pipeline|tool|toolbox|software|workflow)\b"
)
DUPLICATE_PATTERN = re.compile(r"\bduplicate(?:[- ]record)?\b")
RESEARCH_SIGNAL_PATTERN = re.compile(
    r"\b(here,? we|in this work|in this study|we investigate|we measure|we show|we present|we find|"
    r"we reveal|we observe|we report|we quantify|our results|using [a-z])\b"
)

REQUIRED_FRONTMATTER_FIELDS = [
    "note_key",
    "title",
    "authors",
    "year",
    "journal",
    "doi",
    "source_pdf",
    "source_text",
    "paper_type",
    "include_in_synthesis",
    "domain",
    "system_type",
    "methods",
    "variables",
    "concepts",
    "confidence",
]

REQUIRED_NOTE_SECTIONS = [
    "Citation",
    "Core Question",
    "System",
    "Methods",
    "Key Variables",
    "Main Findings",
    "Quantitative Results",
    "Mechanism / Interpretation",
    "Evidence Map",
    "Limitations",
    "Concepts",
    "Confidence",
    "Open Questions",
]

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass
class MarkdownRecord:
    path: Path
    frontmatter: dict[str, Any]
    title: str
    sections: dict[str, str]
    body: str


def strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_scalar(value: str) -> Any:
    value = strip_quotes(value.strip())
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    end_index: int | None = None
    frontmatter_lines: list[str] = []
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break
        frontmatter_lines.append(lines[index])

    if end_index is None:
        return {}, text

    data: dict[str, Any] = {}
    index = 0
    while index < len(frontmatter_lines):
        line = frontmatter_lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if line.startswith(" "):
            raise ValueError(f"Invalid frontmatter indentation near: {line!r}")
        if ":" not in line:
            raise ValueError(f"Invalid frontmatter line: {line!r}")

        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()

        if raw_value:
            data[key] = parse_scalar(raw_value)
            index += 1
            continue

        items: list[Any] = []
        index += 1
        while index < len(frontmatter_lines):
            next_line = frontmatter_lines[index]
            if not next_line.strip():
                index += 1
                continue
            if not next_line.startswith("  - "):
                break
            items.append(parse_scalar(next_line[4:]))
            index += 1
        data[key] = items

    body = "\n".join(lines[end_index + 1 :]).lstrip("\n")
    return data, body


def parse_sections(body: str) -> tuple[str, dict[str, str]]:
    title = ""
    sections: dict[str, str] = {}
    current_heading: str | None = None
    buffer: list[str] = []

    for line in body.splitlines():
        if line.startswith("# "):
            if not title:
                title = line[2:].strip()
                continue
        if line.startswith("## "):
            if current_heading is not None:
                sections[current_heading] = "\n".join(buffer).strip()
            current_heading = line[3:].strip()
            buffer = []
            continue
        if current_heading is not None:
            buffer.append(line)

    if current_heading is not None:
        sections[current_heading] = "\n".join(buffer).strip()

    return title, sections


def read_markdown_record(path: Path) -> MarkdownRecord:
    raw_text = path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(raw_text)
    title, sections = parse_sections(body)
    return MarkdownRecord(
        path=path,
        frontmatter=frontmatter,
        title=title,
        sections=sections,
        body=body,
    )


def ensure_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def load_note_records() -> list[MarkdownRecord]:
    if not NOTES_DIR.exists():
        return []
    return [read_markdown_record(path) for path in sorted(NOTES_DIR.glob("*.md"))]


def normalize_paper_type(value: Any) -> str:
    normalized = str(value or "").strip().lower().replace("-", "_")
    if not normalized:
        return "unknown"
    if normalized in CANONICAL_PAPER_TYPES:
        return normalized
    if normalized in LEGACY_RESEARCH_PAPER_TYPES:
        return "research_article"
    if normalized in LEGACY_METHOD_PAPER_TYPES:
        return "methods_resource"
    if normalized in {"conference_abstract", "duplicate_record"}:
        return "unknown"
    if normalized in LEGACY_UNKNOWN_PAPER_TYPES:
        return "unknown"
    return "unknown"


def is_duplicate_tracking_note(record: MarkdownRecord) -> bool:
    explicit = str(record.frontmatter.get("paper_type", "")).strip().lower()
    if explicit == "duplicate-record":
        return True
    haystack = " ".join(
        [
            record.title,
            str(record.frontmatter.get("system_type", "")),
            record.sections.get("System", ""),
            record.sections.get("Main Findings", ""),
            record.sections.get("Limitations", ""),
            record.sections.get("Open Questions", ""),
        ]
    ).lower()
    return bool(DUPLICATE_PATTERN.search(haystack))


def resolved_paper_type(record: MarkdownRecord) -> str:
    explicit_raw = str(record.frontmatter.get("paper_type", "")).strip()
    explicit = normalize_paper_type(explicit_raw)
    title = record.title.lower()
    methods = [item.lower() for item in ensure_list(record.frontmatter.get("methods"))]
    core_question = record.sections.get("Core Question", "").lower()
    methods_text = record.sections.get("Methods", "").lower()
    main_findings = record.sections.get("Main Findings", "").lower()
    body = " ".join(
        [
            record.title,
            core_question,
            methods_text,
            main_findings,
            record.sections.get("Limitations", ""),
        ]
    ).lower()
    review_cues = bool(REVIEW_TITLE_PATTERN.search(title) or REVIEW_BODY_PATTERN.search(body))
    perspective_cues = bool(PERSPECTIVE_TITLE_PATTERN.search(title) or PERSPECTIVE_BODY_PATTERN.search(body))
    method_cues = bool(
        METHOD_RESOURCE_PATTERN.search(title)
        and any(token in title for token in ("method", "protocol", "resource", "platform", "pipeline", "tool", "software"))
    )
    non_placeholder_methods = [item for item in methods if item not in PLACEHOLDER_VALUES]
    findings_have_content = bool(main_findings and "manual review required" not in main_findings)
    research_cues = bool(
        RESEARCH_SIGNAL_PATTERN.search(body)
        or ("we " in core_question and findings_have_content)
        or (non_placeholder_methods and findings_have_content)
    )

    if perspective_cues:
        return "perspective"
    if review_cues:
        return "review"
    if explicit in {"review", "perspective"}:
        if research_cues:
            return "research_article"
        return explicit
    if explicit == "methods_resource":
        return "methods_resource"
    if explicit == "research_article":
        return "research_article"
    if method_cues and explicit == "unknown":
        return "methods_resource"
    if research_cues:
        return "research_article"
    return explicit


def resolved_include_in_synthesis(record: MarkdownRecord) -> bool:
    explicit = record.frontmatter.get("include_in_synthesis")
    if isinstance(explicit, bool):
        return explicit
    if isinstance(explicit, str):
        lowered = explicit.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
    if is_duplicate_tracking_note(record):
        return False
    return resolved_paper_type(record) not in {"review", "perspective"}


def normalized_note_tags(record: MarkdownRecord) -> list[str]:
    tags = ensure_list(record.frontmatter.get("tags"))
    normalized: list[str] = []
    for tag in tags:
        tag = tag.strip().lower()
        if tag and tag not in normalized:
            normalized.append(tag)
    if "paper" not in normalized:
        normalized.insert(0, "paper")
    if resolved_paper_type(record) == "review" and "review" not in normalized:
        normalized.append("review")
    if resolved_paper_type(record) != "review":
        normalized = [tag for tag in normalized if tag != "review"]
    return normalized


def load_library_note_records() -> list[MarkdownRecord]:
    return [
        record
        for record in load_note_records()
        if not is_duplicate_tracking_note(record)
    ]


def load_synthesis_note_records() -> list[MarkdownRecord]:
    return [
        record
        for record in load_note_records()
        if not is_duplicate_tracking_note(record) and resolved_include_in_synthesis(record)
    ]


def load_concept_records() -> list[MarkdownRecord]:
    if not CONCEPTS_DIR.exists():
        return []
    records: list[MarkdownRecord] = []
    for path in sorted(CONCEPTS_DIR.glob("*.md")):
        if path.name == "README.md":
            continue
        records.append(read_markdown_record(path))
    return records


def load_layer_records(layer_dir: Path) -> list[MarkdownRecord]:
    if not layer_dir.exists():
        return []
    records: list[MarkdownRecord] = []
    for path in sorted(layer_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        records.append(read_markdown_record(path))
    return records


def relative_link(from_path: Path, to_path: Path) -> str:
    return os.path.relpath(to_path, start=from_path.parent).replace(os.sep, "/")


def slug_to_title(slug: str) -> str:
    words = slug.replace("_", "-").split("-")
    if not words:
        return slug
    title_words: list[str] = []
    for word in words:
        if word == "x":
            title_words.append("X")
        else:
            title_words.append(word.capitalize())
    return " ".join(title_words)


def is_normalized_slug(value: str) -> bool:
    return bool(SLUG_PATTERN.fullmatch(value))


def write_text_if_changed(path: Path, text: str) -> None:
    existing = None
    if path.exists():
        existing = path.read_text(encoding="utf-8")
    normalized = text.rstrip() + "\n"
    if existing != normalized:
        path.write_text(normalized, encoding="utf-8")
