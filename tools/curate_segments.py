#!/usr/bin/env python3
"""
Curate the RAG corpus by surfacing the best segments for each user concern
defined in `chrome-extension-v2/data/lexique_enfance.json`.

Outputs:
  - data/curated_segments.json : mapping concern -> top segments with scores
  - data/curated_segments.md   : human-readable summary table
"""

from __future__ import annotations

import json
import math
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
LEXICON_PATH = ROOT / "chrome-extension-v2" / "data" / "lexique_enfance.json"
METADATA_PATH = ROOT / "data" / "corpus_metadata.json"
OUTPUT_JSON = ROOT / "data" / "curated_segments.json"
OUTPUT_MD = ROOT / "data" / "curated_segments.md"


def _strip_accents(text: str) -> str:
  normalized = unicodedata.normalize("NFKD", text)
  return "".join(char for char in normalized if not unicodedata.combining(char))


def normalize(text: str) -> str:
  if not text:
    return ""
  translation_table = str.maketrans(
    {"0": "o", "1": "i", "2": "z", "3": "e", "4": "a", "5": "s", "6": "g", "7": "t", "8": "b", "9": "g"}
  )
  lowered = _strip_accents(text.lower()).translate(translation_table)
  cleaned = []
  last_char = ""
  repeat_count = 0
  for char in lowered:
    if char.isalnum() or char.isspace():
      if char == last_char:
        repeat_count += 1
        if repeat_count >= 3:
          continue
      else:
        repeat_count = 1
        last_char = char
      cleaned.append(char)
    else:
      cleaned.append(" ")
      last_char = ""
      repeat_count = 0
  return " ".join("".join(cleaned).split())


def load_lexicon() -> List[Dict]:
  with LEXICON_PATH.open(encoding="utf-8") as f:
    data = json.load(f)
  return data.get("lexique_enfance", [])


def load_corpus() -> List[Dict]:
  with METADATA_PATH.open(encoding="utf-8") as f:
    return json.load(f)


def score_segment(normalized_text: str, admin_terms: List[str], weight: float) -> float:
  if not normalized_text or not admin_terms:
    return 0.0
  hits = 0
  for term in admin_terms:
    norm_term = normalize(term)
    if not norm_term:
      continue
    if norm_term in normalized_text:
      hits += 1
    else:
      # partial match: check tokens intersection
      term_tokens = set(norm_term.split())
      text_tokens = set(normalized_text.split())
      if term_tokens and term_tokens.issubset(text_tokens):
        hits += 0.5
  if not hits:
    return 0.0
  density = hits / max(len(admin_terms), 1)
  length_penalty = math.log(1 + len(normalized_text) / 800)
  return weight * hits * density / max(length_penalty, 0.6)


def curate(top_n: int = 5) -> Tuple[Dict[str, List[Dict]], List[str]]:
  lexicon = load_lexicon()
  corpus = load_corpus()
  normalized_corpus = [
    {
      "id": idx,
      "label": item.get("label") or item.get("source") or f"segment_{idx}",
      "url": item.get("url"),
      "content": item.get("content") or "",
      "norm_content": normalize(
        " ".join(
          str(item.get(field, ""))
          for field in ("content", "label", "source", "section")
        )
      ),
    }
    for idx, item in enumerate(corpus)
  ]

  curated: Dict[str, List[Dict]] = {}
  markdown_lines: List[str] = [
    "# Curated Segments par préoccupation\n",
  ]

  for entry in lexicon:
    concern = entry.get("terme_usager")
    admin_terms = entry.get("terme_admin") or []
    weight = float(entry.get("poids", 0.0))
    if not concern or not admin_terms:
      continue
    scores = []
    for segment in normalized_corpus:
      score = score_segment(segment["norm_content"], admin_terms, weight)
      if score <= 0:
        continue
      scores.append(
        {
          "segment_id": segment["id"],
          "label": segment["label"],
          "url": segment["url"],
          "score": round(score, 3),
          "preview": segment["content"][:280].replace("\n", " "),
        }
      )
    scores.sort(key=lambda item: item["score"], reverse=True)
    curated_list = scores[:top_n]
    curated[concern] = curated_list
    markdown_lines.append(f"## {concern}\n")
    markdown_lines.append("| Segment | Score | URL | Aperçu |")
    markdown_lines.append("| --- | --- | --- | --- |")
    for item in curated_list:
      preview = item["preview"].replace("|", " ")
      markdown_lines.append(
        f"| {item['label']} | {item['score']} | {item['url'] or ''} | {preview} |"
      )
    markdown_lines.append("")

  return curated, markdown_lines


def main() -> None:
  curated, markdown_lines = curate()
  OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
  with OUTPUT_JSON.open("w", encoding="utf-8") as f:
    json.dump(curated, f, ensure_ascii=False, indent=2)
  with OUTPUT_MD.open("w", encoding="utf-8") as f:
    f.write("\n".join(markdown_lines))

  from collections import Counter
  summary_lines = ["# Top segments les plus faibles (score < 0.3)\n", "| Préoccupation | Segment | Score |", "| --- | --- | --- |"]
  for concern, items in curated.items():
    for item in items:
      if item["score"] < 0.3:
        summary_lines.append(f"| {concern} | {item['label']} | {item['score']} |")
  summary_path = ROOT / "data" / "curated_segments_low_scores.md"
  with summary_path.open("w", encoding="utf-8") as f:
    f.write("\n".join(summary_lines))

  print(f"✅ Curated segments JSON → {OUTPUT_JSON}")
  print(f"✅ Curated segments Markdown → {OUTPUT_MD}")


if __name__ == "__main__":
  main()

