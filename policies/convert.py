"""Convert policy PDFs into page-aware Markdown for later retrieval.

Usage:
    python policies/convert.py
    python policies/convert.py --input-dir policies/pdf --output-dir policies/md

The converter preserves page boundaries so retrieved chunks can cite source
pages later in the support-ticket co-pilot.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


DEFAULT_INPUT_DIR = Path(__file__).parent / "pdf"
DEFAULT_OUTPUT_DIR = Path(__file__).parent / "md"


def policy_name(pdf_path: Path) -> str:
    """Return a stable, human-readable policy name from a PDF filename."""
    name = re.sub(r"[_-]+", " ", pdf_path.stem)
    name = re.sub(r"\bvaletax\b", "", name, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", name).strip().title()


def clean_text(text: str) -> str:
    """Normalize extracted text while retaining meaningful paragraph breaks."""
    text = text.replace("\u00a0", " ").replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    cleaned: list[str] = []
    blank_pending = False
    for line in lines:
        if not line:
            blank_pending = True
            continue
        if blank_pending and cleaned:
            cleaned.append("")
        cleaned.append(line)
        blank_pending = False
    return "\n".join(cleaned).strip()


def extract_pages(pdf_path: Path) -> list[str]:
    """Extract PDF text page-by-page using Poppler's pdftotext utility."""
    if shutil.which("pdftotext") is None:
        raise RuntimeError(
            "pdftotext is required but was not found. Install Poppler "
            "(for example, the poppler-utils package) and try again."
        )
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [clean_text(page) for page in result.stdout.split("\f") if clean_text(page)]


def to_markdown(pdf_path: Path, pages: list[str]) -> str:
    """Build page-aware Markdown from extracted PDF pages."""
    name = policy_name(pdf_path)
    sections = [
        f"# {name}",
        "",
        f"> Source: {pdf_path.name}",
        "> Extraction: `pdftotext -layout`",
        "",
        "This file was generated from the source PDF. Page headings are preserved "
        "to support retrieval citations.",
        "",
    ]
    for page_number, page_text in enumerate(pages, start=1):
        sections.extend([f"## Page {page_number}", "", page_text, ""])
    return "\n".join(sections).rstrip() + "\n"


def convert_directory(input_dir: Path, output_dir: Path) -> list[Path]:
    """Convert every PDF in input_dir and return generated Markdown paths."""
    pdf_files = sorted(input_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {input_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    for pdf_path in pdf_files:
        pages = extract_pages(pdf_path)
        output_path = output_dir / f"{pdf_path.stem}.md"
        output_path.write_text(to_markdown(pdf_path, pages), encoding="utf-8")
        generated.append(output_path)
        print(f"Converted {pdf_path} ({len(pages)} pages) -> {output_path}")
    return generated


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    convert_directory(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
