from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import SAMPLE_PDF_PATH  # noqa: E402  (import after sys.path patch)


def load_pdf(pdf_path: Path | str) -> list[dict[str, Any]]:

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"[ingest] PDF not found at: {pdf_path}\n"
            "        Please run the following command first:\n"
            "            python scripts/create_sample_pdf.py"
        )

    pages: list[dict[str, Any]] = []

    try:
        doc: fitz.Document = fitz.open(str(pdf_path))
    except Exception as exc:  # fitz can raise various C-level exceptions
        raise RuntimeError(
            f"[ingest] PyMuPDF failed to open '{pdf_path.name}': {exc}"
        ) from exc

    with doc:
        total_pages: int = len(doc)
        print(
            f"[ingest] Opened '{pdf_path.name}'  "
            f"({total_pages} page{'s' if total_pages != 1 else ''} detected)"
        )

        for page_idx, page in enumerate(doc, start=1):
            raw_text: str = page.get_text("text")
            clean_text: str = _clean_text(raw_text)

            if not clean_text:
                print(f"[ingest]   Page {page_idx:>3}: SKIPPED  (empty after cleaning)")
                continue

            record: dict[str, Any] = {
                "page_number": page_idx,
                "text": clean_text,
                "char_count": len(clean_text),
                "source_file": pdf_path.stem,
                "source_path": str(pdf_path.resolve()),
            }
            pages.append(record)

            print(
                f"[ingest]   Page {page_idx:>3}: {len(clean_text):>6} chars extracted"
            )

    print(
        f"[ingest] Ingestion complete  "
        f"({len(pages)} page{'s' if len(pages) != 1 else ''} returned)\n"
    )
    return pages


def _clean_text(raw: str) -> str:

    lines = raw.splitlines()
    cleaned: list[str] = []
    previous_was_blank: bool = False

    for line in lines:
        stripped_line: str = line.strip()
        is_blank: bool = stripped_line == ""

        # Collapse consecutive blank lines into one
        if is_blank and previous_was_blank:
            continue

        cleaned.append(stripped_line)
        previous_was_blank = is_blank

    return "\n".join(cleaned).strip()


def _print_separator(char: str = "-", width: int = 62) -> None:
    print(char * width)


def _run_standalone_test() -> None:

    _print_separator("=")
    print("  GA4GH-RegBot PoC  |  Phase 1: Ingestion & Parsing")
    print("  Standalone verification test")
    _print_separator("=")
    print()

    pages = load_pdf(SAMPLE_PDF_PATH)

    if not pages:
        print("[ingest] ERROR: No pages were returned.  Check the PDF.")
        sys.exit(1)

    _print_separator("=")
    print("EXTRACTION RESULTS")
    _print_separator("=")

    total_chars: int = 0
    for p in pages:
        total_chars += p["char_count"]
        print()
        _print_separator()
        print(f"  Page         : {p['page_number']}")
        print(f"  Source file  : {p['source_file']}")
        print(f"  Char count   : {p['char_count']}")
        print(f"  Source path  : {p['source_path']}")
        _print_separator()
        print("  Text preview (first 400 chars):")
        print()

        # Indent the preview for readability
        preview: str = p["text"][:400]
        for preview_line in preview.splitlines():
            print(f"    {preview_line}")

        if p["char_count"] > 400:
            print("    [... truncated ...]")

    print()
    _print_separator("=")
    print("SUMMARY")
    _print_separator("=")
    print(f"  Total pages ingested : {len(pages)}")
    print(f"  Total characters     : {total_chars}")
    print(
        f"  Source file(s)       : {', '.join(sorted({p['source_file'] for p in pages}))}"
    )
    print()
    _print_separator("=")
    print("  Phase 1 COMPLETE  ✓")
    _print_separator("=")
    print()


if __name__ == "__main__":
    _run_standalone_test()
