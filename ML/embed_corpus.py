import json
import os
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent

# Chemins avec support corpus généralisé
CORPUS_GENERALIZED_PATH = BASE_DIR / "data" / "corpus_metadata_generalized.json"
CORPUS_SEGMENTS_PATH = BASE_DIR / "data" / "corpus_segments.json"
CORPUS_METADATA_PATH = BASE_DIR / "data" / "corpus_metadata.json"

EMBEDDINGS_GENERALIZED_PATH = BASE_DIR / "data" / "corpus_embeddings_generalized.npy"
EMBEDDINGS_PATH = BASE_DIR / "data" / "corpus_embeddings.npy"
METADATA_PATH = BASE_DIR / "data" / "corpus_metadata.json"
METADATA_GENERALIZED_PATH = BASE_DIR / "data" / "corpus_metadata_generalized.json"


def load_corpus(use_generalized: bool = True):
  """
  Charge le corpus depuis corpus_metadata_generalized.json si disponible,
  sinon fallback sur corpus_segments.json ou corpus_metadata.json
  
  Args:
    use_generalized: Si True, essaie de charger corpus généralisé en premier
  """
  # Essayer corpus généralisé en premier
  if use_generalized and CORPUS_GENERALIZED_PATH.exists():
    print(f"📂 Chargement corpus généralisé: {CORPUS_GENERALIZED_PATH}")
    with CORPUS_GENERALIZED_PATH.open(encoding="utf-8") as f:
      data = json.load(f)
    return data
  
  # Fallback sur corpus_segments.json
  if CORPUS_SEGMENTS_PATH.exists():
    print(f"📂 Chargement corpus segments: {CORPUS_SEGMENTS_PATH}")
    with CORPUS_SEGMENTS_PATH.open(encoding="utf-8") as f:
      data = json.load(f)
    return data
  
  # Fallback sur corpus_metadata.json
  if CORPUS_METADATA_PATH.exists():
    print(f"📂 Chargement corpus metadata: {CORPUS_METADATA_PATH}")
    with CORPUS_METADATA_PATH.open(encoding="utf-8") as f:
      data = json.load(f)
    return data
  
  raise SystemExit(f"Corpus introuvable. Cherché dans:\n- {CORPUS_GENERALIZED_PATH}\n- {CORPUS_SEGMENTS_PATH}\n- {CORPUS_METADATA_PATH}")


def save_embeddings(embeddings: np.ndarray, metadata, use_generalized: bool = True):
  """
  Sauvegarde les embeddings et métadonnées.
  Utilise les chemins généralisés si use_generalized=True et corpus généralisé détecté.
  """
  if use_generalized and CORPUS_GENERALIZED_PATH.exists():
    # Sauvegarder dans fichiers généralisés
    np.save(EMBEDDINGS_GENERALIZED_PATH, embeddings)
    with METADATA_GENERALIZED_PATH.open("w", encoding="utf-8") as f:
      json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"✅ Embeddings généralisés sauvegardés dans {EMBEDDINGS_GENERALIZED_PATH}")
    print(f"✅ Métadonnées généralisées sauvegardées dans {METADATA_GENERALIZED_PATH}")
  else:
    # Sauvegarder dans fichiers standards
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
  import argparse
  
  parser = argparse.ArgumentParser(description="Générer embeddings pour corpus RAG")
  parser.add_argument(
    "--generalized",
    action="store_true",
    help="Utiliser corpus généralisé (corpus_metadata_generalized.json)"
  )
  args = parser.parse_args()
  
  use_generalized = args.generalized or CORPUS_GENERALIZED_PATH.exists()
  
  corpus = load_corpus(use_generalized=use_generalized)
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
  save_embeddings(embeddings, metadata, use_generalized=use_generalized)


if __name__ == "__main__":
  main()

