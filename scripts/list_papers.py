#!/usr/bin/env python3

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PAPERS_DIR = ROOT / "raw" / "papers"


def main() -> None:
    if not PAPERS_DIR.exists():
        print("raw/papers does not exist")
        return

    pdfs = sorted(
        path for path in PAPERS_DIR.iterdir() if path.is_file() and path.suffix.lower() == ".pdf"
    )

    if not pdfs:
        print("No PDFs found in raw/papers")
        return

    for pdf in pdfs:
        print(pdf.relative_to(ROOT))


if __name__ == "__main__":
    main()
