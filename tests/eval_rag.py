#!/usr/bin/env python3
"""
Évalue la pertinence du backend RAG Amiens en lançant une série de questions
usagers (formulations standard + variantes SMS / fautes) et en collectant
les scores renvoyés.

Usage :
  python tests/eval_rag.py --endpoint https://localhost:8711/rag-assistant \
      --output results/rag_eval.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_PATH = ROOT / "chrome-extension-v2" / "data" / "questions_usager.json"
DEFAULT_OUTPUT = ROOT / "tests" / "rag_eval_results.csv"


@dataclass
class QuestionEntry:
  id: str
  intent: str
  text: str
  variant_label: str


def load_questions(path: Path) -> List[QuestionEntry]:
  with path.open(encoding="utf-8") as f:
    data = json.load(f)
  entries: List[QuestionEntry] = []
  for item in data.get("questions", []):
    base_id = item.get("id")
    intent = item.get("intent", "inconnue")
    canonical = item.get("canonical")
    sms = item.get("sms")
    variants = item.get("variants", [])

    if canonical:
      entries.append(
        QuestionEntry(
          id=f"{base_id}:canonical",
          intent=intent,
          text=canonical,
          variant_label="canonical",
        )
      )
    if sms:
      entries.append(
        QuestionEntry(
          id=f"{base_id}:sms",
          intent=intent,
          text=sms,
          variant_label="sms",
        )
      )
    for idx, variant in enumerate(variants):
      if not variant:
        continue
      entries.append(
        QuestionEntry(
          id=f"{base_id}:var{idx+1}",
          intent=intent,
          text=variant,
          variant_label=f"variant_{idx+1}",
        )
      )
  return entries


def call_backend(
  endpoint: str,
  question: str,
  ranked_segments: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
  payload = {
    "question": question,
    "normalized_question": question.lower(),
    "rag_results": ranked_segments or [],
    "conversation": [],
  }
  response = requests.post(endpoint, json=payload, timeout=30)
  response.raise_for_status()
  return response.json()


def extract_top_segments(result: Dict[str, Any]) -> List[Dict[str, Any]]:
  segments: List[Dict[str, Any]] = result.get("alignment", {}).get("segments", [])
  if segments:
    return segments
  return result.get("rag_segments", [])


def analyse_response(result: Dict[str, Any]) -> Dict[str, Any]:
  alignment = result.get("alignment", {})
  sources = result.get("sources", [])
  top_segments = extract_top_segments(result)

  def segment_labels(segments: Iterable[Dict[str, Any]]) -> List[str]:
    labels: List[str] = []
    for segment in segments:
      label = segment.get("label") or segment.get("source")
      if label:
        labels.append(label)
    return labels

  answer_html = result.get("answer_html")
  answer_text = result.get("answer_text")
  return {
    "answer_html": answer_html if isinstance(answer_html, str) else "",
    "answer_text": answer_text if isinstance(answer_text, str) else "",
    "alignment_status": alignment.get("status"),
    "alignment_summary": alignment.get("summary"),
    "sources": "; ".join(src.get("title") or src.get("url", "") for src in sources),
    "top_segments": "; ".join(segment_labels(top_segments)),
  }


def main(argv: Optional[List[str]] = None) -> int:
  parser = argparse.ArgumentParser(description="Benchmark du backend RAG Amiens.")
  parser.add_argument("--endpoint", default="https://localhost:8711/rag-assistant", help="URL de l'endpoint FastAPI.")
  parser.add_argument("--questions", type=Path, default=QUESTIONS_PATH, help="Chemin du JSON de questions.")
  parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Fichier CSV de sortie.")
  parser.add_argument("--insecure", action="store_true", help="Désactive la vérification TLS (utile pour certif auto-signé).")
  args = parser.parse_args(argv)

  questions = load_questions(args.questions)
  if not questions:
    print("⚠️ Aucune question trouvée.", file=sys.stderr)
    return 1

  if args.insecure:
    requests.packages.urllib3.disable_warnings()  # type: ignore[attr-defined]
    verify = False
  else:
    verify = True

  args.output.parent.mkdir(parents=True, exist_ok=True)

  with args.output.open("w", encoding="utf-8", newline="") as f:
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
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for entry in questions:
      try:
        raw_question = entry.text
        payload = {
          "question": raw_question,
          "normalized_question": raw_question.lower(),
          "rag_results": [],
          "conversation": [],
        }
        response = requests.post(args.endpoint, json=payload, timeout=30, verify=verify)
        response.raise_for_status()
        result = response.json()
        summary = analyse_response(result)
      except Exception as exc:  # pylint: disable=broad-except
        summary = {
          "alignment_status": f"error: {exc}",
          "alignment_summary": "",
          "top_segments": "",
          "sources": "",
          "answer_text": "",
        }

      writer.writerow(
        {
          "question_id": entry.id,
          "variant_label": entry.variant_label,
          "intent": entry.intent,
          "question": entry.text,
          **summary,
        }
      )

  print(f"✅ Benchmark terminé. Résultats dans {args.output}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

