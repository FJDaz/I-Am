import json
import os
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent
CORPUS_PATH = BASE_DIR / "data" / "corpus_segments.json"
EMBEDDINGS_PATH = BASE_DIR / "data" / "corpus_embeddings.npy"
METADATA_PATH = BASE_DIR / "data" / "corpus_metadata.json"


def load_corpus():
  if not CORPUS_PATH.exists():
    raise SystemExit(f"Corpus introuvable: {CORPUS_PATH}")
  with CORPUS_PATH.open(encoding="utf-8") as f:
    data = json.load(f)
  return data


def save_embeddings(embeddings: np.ndarray, metadata):
  np.save(EMBEDDINGS_PATH, embeddings)
  with METADATA_PATH.open("w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)
  print(f"✅ Embeddings sauvegardés dans {EMBEDDINGS_PATH}")
  print(f"✅ Métadonnées sauvegardées dans {METADATA_PATH}")


def build_metadata(corpus):
  metadata = []
  for entry in corpus:
    content = entry.get("content") or ""
    truncated = " ".join(content.split())[:1500]
    metadata.append(
      {
        "label": entry.get("label"),
        "source": entry.get("source"),
        "url": entry.get("url"),
        "section": entry.get("section"),
        "content": truncated,
      }
    )
  return metadata


def main():
  corpus = load_corpus()
  texts = [entry.get("content") or "" for entry in corpus]
  if not texts:
    raise SystemExit("Corpus vide, impossible de générer des embeddings.")

  model_name = os.environ.get("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
  print(f"🔄 Chargement du modèle d'embeddings {model_name}…")
  model = SentenceTransformer(model_name)

  print(f"🔄 Génération des embeddings pour {len(texts)} segments…")
  embeddings = model.encode(
    texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True
  )

  metadata = build_metadata(corpus)
  save_embeddings(embeddings, metadata)


if __name__ == "__main__":
  main()

