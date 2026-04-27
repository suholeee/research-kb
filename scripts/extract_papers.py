#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Callable

from detect_changes import (
    DEFAULT_MANIFEST,
    FileSnapshot,
    load_manifest,
    sha256_file,
    snapshot_from_manifest,
)


ROOT = Path(__file__).resolve().parent.parent
PAPERS_DIR = ROOT / "raw" / "papers"
EXTRACTED_DIR = ROOT / "raw" / "extracted"
TEXT_SENTINEL = "----- EXTRACTED TEXT -----"


Extractor = Callable[[Path], tuple[str, list[str]]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract text from PDFs in raw/papers into raw/extracted."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="State manifest used to skip unchanged PDFs. Defaults to .kb_state.json.",
    )
    parser.add_argument(
        "--pdf",
        action="append",
        default=[],
        help="Specific PDF path to extract. May be passed multiple times.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-extract all selected PDFs even if the manifest says they are unchanged.",
    )
    return parser.parse_args()


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
    text = text.replace("\u00a0", " ")
    text = "\n".join(line.rstrip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_with_pymupdf(pdf_path: Path) -> tuple[str, list[str]]:
    import fitz

    warnings: list[str] = []
    parts: list[str] = []
    document = fitz.open(pdf_path)
    try:
        for page_index, page in enumerate(document, start=1):
            try:
                page_text = normalize_text(page.get_text("text"))
            except Exception as exc:  # pragma: no cover - backend specific
                warnings.append(f"Page {page_index}: {exc}")
                continue

            if page_text:
                parts.append(page_text)
            else:
                warnings.append(f"Page {page_index}: no text extracted")
    finally:
        document.close()

    return "\n\n".join(parts).strip(), warnings


def extract_with_pypdf(pdf_path: Path) -> tuple[str, list[str]]:
    try:
        from pypdf import PdfReader
    except ImportError:  # pragma: no cover - fallback import
        from PyPDF2 import PdfReader

    warnings: list[str] = []
    parts: list[str] = []
    reader = PdfReader(str(pdf_path))

    for page_index, page in enumerate(reader.pages, start=1):
        try:
            page_text = normalize_text(page.extract_text() or "")
        except Exception as exc:  # pragma: no cover - backend specific
            warnings.append(f"Page {page_index}: {exc}")
            continue

        if page_text:
            parts.append(page_text)
        else:
            warnings.append(f"Page {page_index}: no text extracted")

    return "\n\n".join(parts).strip(), warnings


def select_extractor() -> tuple[str, Extractor | None, list[str]]:
    try:
        import fitz  # noqa: F401

        return "pymupdf", extract_with_pymupdf, []
    except ImportError:
        pass

    try:
        import pypdf  # noqa: F401

        return "pypdf", extract_with_pypdf, []
    except ImportError:
        pass

    try:
        import PyPDF2  # noqa: F401

        return "PyPDF2", extract_with_pypdf, []
    except ImportError:
        pass

    return (
        "unavailable",
        None,
        [
            "No supported PDF parser is installed. Install `pypdf` or `pymupdf` to extract text.",
        ],
    )


def write_extracted_file(
    pdf_path: Path,
    output_path: Path,
    backend_name: str,
    text: str,
    warnings: list[str],
    status: str,
) -> None:
    lines = [
        f"Source PDF: {pdf_path.relative_to(ROOT)}",
        f"Extraction backend: {backend_name}",
        f"Extraction status: {status}",
        "Warnings:",
    ]

    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- None")

    lines.extend(["", TEXT_SENTINEL, ""])
    if text:
        lines.append(text)

    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def resolve_pdf_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    return path


def selected_pdf_paths(requested_pdfs: list[str]) -> list[Path]:
    if requested_pdfs:
        paths = [resolve_pdf_path(value) for value in requested_pdfs]
        papers_dir = PAPERS_DIR.resolve()
        return sorted(
            path
            for path in paths
            if path.is_file() and path.suffix.lower() == ".pdf" and path.resolve().parent == papers_dir
        )
    return sorted(path for path in PAPERS_DIR.iterdir() if path.is_file() and path.suffix.lower() == ".pdf")


def pdf_needs_extraction(
    pdf_path: Path,
    output_path: Path,
    previous_snapshot: dict[str, FileSnapshot],
    *,
    force: bool,
    requested_pdfs: bool,
) -> bool:
    if force:
        return True
    if requested_pdfs:
        return True
    if not output_path.exists():
        return True

    relpath = pdf_path.relative_to(ROOT).as_posix()
    previous = previous_snapshot.get(relpath)
    if previous is None:
        return True

    return previous.sha256 != sha256_file(pdf_path)


def remove_deleted_pdf_outputs(previous_snapshot: dict[str, FileSnapshot], current_pdf_paths: list[Path]) -> None:
    current_pdf_stems = {path.stem for path in current_pdf_paths}
    previous_pdf_stems = {
        Path(relpath).stem
        for relpath, snapshot in previous_snapshot.items()
        if snapshot.layer == "raw_papers"
    }
    deleted_pdf_stems = sorted(previous_pdf_stems - current_pdf_stems)

    for stem in deleted_pdf_stems:
        output_path = EXTRACTED_DIR / f"{stem}.txt"
        if not output_path.exists():
            continue
        output_path.unlink()
        print(f"Removed {output_path.relative_to(ROOT)} [source PDF deleted]")


def main() -> None:
    args = parse_args()

    if not PAPERS_DIR.exists():
        print("raw/papers does not exist")
        return

    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    previous_snapshot = snapshot_from_manifest(load_manifest(args.manifest))
    current_pdf_paths = sorted(path for path in PAPERS_DIR.iterdir() if path.is_file() and path.suffix.lower() == ".pdf")
    remove_deleted_pdf_outputs(previous_snapshot, current_pdf_paths)

    pdf_paths = selected_pdf_paths(args.pdf)
    if not pdf_paths:
        print("No matching PDFs found in raw/papers")
        return

    backend_name, extractor, backend_warnings = select_extractor()

    for pdf_path in pdf_paths:
        output_path = EXTRACTED_DIR / f"{pdf_path.stem}.txt"
        if not pdf_needs_extraction(
            pdf_path,
            output_path,
            previous_snapshot,
            force=args.force,
            requested_pdfs=bool(args.pdf),
        ):
            print(f"Skipped {output_path.relative_to(ROOT)} [unchanged]")
            continue

        warnings = list(backend_warnings)
        text = ""
        status = "warning" if warnings else "ok"

        if extractor is not None:
            try:
                text, extraction_warnings = extractor(pdf_path)
                warnings.extend(extraction_warnings)
            except Exception as exc:  # pragma: no cover - backend specific
                warnings.append(f"Fatal extraction error: {exc}")
                status = "error"
            else:
                if warnings and status == "ok":
                    status = "warning"

        text = normalize_text(text)
        if not text:
            warnings.append("No extracted text was produced. The PDF may be image-only or parser output was empty.")
            status = "warning" if status == "ok" else status
        elif len(text) < 500:
            warnings.append("Extracted text is very short. Review the PDF manually before trusting the note.")
            status = "warning" if status == "ok" else status

        deduped_warnings = list(dict.fromkeys(warnings))
        write_extracted_file(pdf_path, output_path, backend_name, text, deduped_warnings, status)
        print(f"Wrote {output_path.relative_to(ROOT)} [{status}]")


if __name__ == "__main__":
    main()
