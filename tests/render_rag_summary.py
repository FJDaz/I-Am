#!/usr/bin/env python3
"""
Construit une synthèse lisible à partir du benchmark CSV :
- génère un CSV "flat" sans retours chariot pour inspection rapide
- produit un résumé Markdown avec verdict court par question
"""

from __future__ import annotations

import csv
import argparse
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "tests" / "rag_eval_results.csv"
DEFAULT_FLAT_OUTPUT = ROOT / "tests" / "rag_eval_results_flat.csv"
DEFAULT_MD_OUTPUT = ROOT / "tests" / "rag_eval_summary.md"


def flatten(text: str) -> str:
  if not text:
    return ""
  return " ".join(line.strip() for line in text.splitlines() if line.strip())


def first_segment_label(segment_field: str) -> str:
  if not segment_field:
    return ""
  return segment_field.split(";")[0].strip()


def derive_diagnostic(row: Dict[str, str]) -> str:
  status = (row.get("alignment_status") or "").lower()
  answer = (row.get("answer_text") or "").lower()
  segments = (row.get("top_segments") or "").lower()

  if status == "aligned":
    if "tarif" in segments or "€" in answer:
      return "OK – grille tarifaire identifiée"
    return "OK – réponse alignée"

  if "partial" in status:
    if "qfi" in answer:
      return "Attention – réponse partielle orientée QFI"
    return "Attention – couverture partielle"

  if "insufficient" in status or "missing" in status or status in {"no_information", "not_found"}:
    if "qfi" in answer:
      return "À compléter – renvoie vers calcul QFI"
    return "À compléter – ressources insuffisantes"

  if status.startswith("error"):
    return f"Erreur backend ({row.get('alignment_status')})"

  return "Diagnostique à vérifier"


def generate_flat_csv(rows: Iterable[Dict[str, str]], output_path: Path) -> None:
  fieldnames = [
    "question_id",
    "variant_label",
    "intent",
    "question",
    "alignment_status",
    "alignment_summary",
    "top_segments",
    "sources",
    "answer_text",
    "answer_html",
    "diagnostic",
  ]
  with output_path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
      writer.writerow({key: row.get(key, "") for key in fieldnames})


def generate_markdown(
  rows: Iterable[Dict[str, str]],
  output_path: Path,
  status_counts: Dict[str, int],
) -> None:
  with output_path.open("w", encoding="utf-8") as f:
    total = sum(status_counts.values())
    f.write(f"# Synthèse benchmark RAG ({total} questions)\n\n")

    f.write("## Répartition des statuts\n\n")
    for status, count in sorted(status_counts.items(), key=lambda item: item[0]):
      f.write(f"- `{status}` : **{count}**\n")
    f.write("\n")

    f.write("## Détails par question\n\n")
    f.write("| Question | Variante | Statut | Diagnostic | Segment principal |\n")
    f.write("| --- | --- | --- | --- | --- |\n")

    for row in rows:
      question = row.get("question", "")
      variant = row.get("variant_label", "")
      status = row.get("alignment_status", "")
      diagnostic = row.get("diagnostic", "")
      top_segment = first_segment_label(row.get("top_segments", ""))
      question_short = question if len(question) <= 80 else f"{question[:77]}…"
      f.write(
        f"| {question_short} | {variant} | `{status}` | {diagnostic} | {top_segment} |\n"
      )


def main() -> None:
  parser = argparse.ArgumentParser(description="Génère des synthèses à partir du benchmark RAG.")
  parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="CSV d'entrée (benchmark).")
  parser.add_argument("--flat-output", type=Path, default=DEFAULT_FLAT_OUTPUT, help="CSV sortie sans retours à la ligne.")
  parser.add_argument("--md-output", type=Path, default=DEFAULT_MD_OUTPUT, help="Résumé Markdown.")
  args = parser.parse_args()

  with args.input.open(encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

  status_counts = Counter(row.get("alignment_status", "unknown") for row in rows)

  for row in rows:
    row["answer_text"] = flatten(row.get("answer_text", ""))
    row["answer_html"] = flatten(row.get("answer_html", ""))
    row["alignment_summary"] = flatten(row.get("alignment_summary", ""))
    row["diagnostic"] = derive_diagnostic(row)

  generate_flat_csv(rows, args.flat_output)
  generate_markdown(rows, args.md_output, status_counts)

  print(f"✅ CSV synthétique → {args.flat_output}")
  print(f"✅ Résumé Markdown → {args.md_output}")


if __name__ == "__main__":
  main()

