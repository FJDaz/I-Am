#!/usr/bin/env python3
"""
Ingest locally downloaded menu files (PDF, XLS/XLSX) into the RAG corpus.

Steps:
  - Convert each PDF page to text via pdfminer.
  - Convert each Excel sheet to a Markdown-like table.
  - Append the generated segments to `data/corpus_metadata.json`
    under dedicated categories (`menus_pdf`, `menus_table`, ...).
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from pdfminer.high_level import extract_text
from pdfminer.pdfpage import PDFPage
import xlrd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "menus"
OUTPUT_PATH = ROOT / "data" / "corpus_metadata.json"


@dataclass
class Segment:
  label: str
  url: str
  category: str
  content: str


def clean_text(text: str) -> str:
  """Normalize whitespace while keeping bullet points readable."""
  text = text.replace("\u00a0", " ")
  text = re.sub(r"[ \t]+", " ", text)
  text = re.sub(r"\n{3,}", "\n\n", text)
  return text.strip()


def pdf_page_count(path: Path) -> int:
  with path.open("rb") as fh:
    return sum(1 for _ in PDFPage.get_pages(fh))


def pdf_to_segments(path: Path, base_label: str, base_url: str) -> Iterable[Segment]:
  page_total = pdf_page_count(path)
  for idx in range(page_total):
    page_text = clean_text(extract_text(str(path), page_numbers=[idx]))
    if not page_text:
      continue
    yield Segment(
        label=f"{base_label}-page-{idx + 1}",
        url=f"{base_url}#page={idx + 1}",
        category="menus_pdf",
        content=page_text,
    )


def xl_cell_to_str(value, datemode) -> str:
  """Convert xlrd cell content to human-readable string."""
  if isinstance(value, float):
    if math.isfinite(value) and float(int(value)) == value:
      return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")
  return str(value)


def xls_to_segments(path: Path, base_label: str, base_url: str) -> Iterable[Segment]:
  book = xlrd.open_workbook(path, formatting_info=False)
  for sheet_index, sheet in enumerate(book.sheets(), start=1):
    rows: List[str] = []
    for row_idx in range(sheet.nrows):
      cells = [
          xl_cell_to_str(sheet.cell_value(row_idx, col_idx), book.datemode).strip()
          for col_idx in range(sheet.ncols)
      ]
      if any(cell for cell in cells):
        rows.append(" | ".join(cells))
    if not rows:
      continue
    content = f"# {sheet.name}\n" + "\n".join(rows)
    yield Segment(
        label=f"{base_label}-sheet-{sheet_index}",
        url=f"{base_url}#sheet={sheet_index}",
        category="menus_table",
        content=clean_text(content),
    )


def load_existing_corpus() -> List[dict]:
  if OUTPUT_PATH.exists():
    with OUTPUT_PATH.open(encoding="utf-8") as fh:
      return json.load(fh)
  return []


def filter_outdated_segments(corpus: List[dict]) -> List[dict]:
  """Remove previously ingested menu segments to avoid duplication."""
  return [
      item
      for item in corpus
      if not item.get("category", "").startswith("menus_")
  ]


def main() -> None:
  if not RAW_DIR.exists():
    raise SystemExit(f"Missing raw menus directory: {RAW_DIR}")

  corpus = filter_outdated_segments(load_existing_corpus())
  new_segments: List[Segment] = []

  for path in sorted(RAW_DIR.glob("*")):
    if path.name.lower().endswith(".pdf"):
      base_label = path.stem.replace(" ", "-").lower()
      base_url = f"file://{path.relative_to(ROOT)}"
      new_segments.extend(pdf_to_segments(path, base_label, base_url))
    elif path.suffix.lower() in {".xls", ".xlsx"}:
      base_label = path.stem.replace(" ", "-").lower()
      base_url = f"file://{path.relative_to(ROOT)}"
      new_segments.extend(xls_to_segments(path, base_label, base_url))

  corpus.extend(
      {
          "label": segment.label,
          "url": segment.url,
          "category": segment.category,
          "content": segment.content,
      }
      for segment in new_segments
  )

  OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
  with OUTPUT_PATH.open("w", encoding="utf-8") as fh:
    json.dump(corpus, fh, ensure_ascii=False, indent=2)

  print(f"✅ Ajouté {len(new_segments)} segments menus → {OUTPUT_PATH}")


if __name__ == "__main__":
  main()

