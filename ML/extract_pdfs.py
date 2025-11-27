"""
Script pour extraire le texte des PDFs dans data/raw et les ajouter à chunks_enfance_clean.json
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

try:
    import pdfplumber
except ImportError:
    raise SystemExit("❌ Installe pdfplumber: pip install pdfplumber")

ROOT = Path(__file__).parent
RAW_DIR = ROOT / "data" / "raw"
CHUNKS_PATH = ROOT / "chunks_enfance_clean.json"


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extrait le texte d'un PDF avec pdfplumber."""
    text_parts = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
    except Exception as e:
        print(f"⚠️  Erreur lors de l'extraction de {pdf_path.name}: {e}")
        return ""

    return "\n\n".join(text_parts)


def load_existing_chunks() -> List[dict]:
    """Charge les chunks existants."""
    if not CHUNKS_PATH.exists():
        return []
    return json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))


def save_chunks(chunks: List[dict]) -> None:
    """Sauvegarde les chunks."""
    chunks.sort(key=lambda item: item.get("source", ""))
    CHUNKS_PATH.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    if not RAW_DIR.exists():
        raise SystemExit(f"❌ Dossier introuvable: {RAW_DIR}")

    # Trouver tous les PDFs
    pdf_files = list(RAW_DIR.rglob("*.pdf"))
    if not pdf_files:
        print(f"⚠️  Aucun PDF trouvé dans {RAW_DIR}")
        return

    print(f"📄 {len(pdf_files)} PDF(s) trouvé(s)")

    # Charger chunks existants
    chunks = load_existing_chunks()
    existing_sources = {chunk.get("source") for chunk in chunks}

    # Extraire et ajouter les nouveaux PDFs
    added = 0
    for pdf_path in pdf_files:
        source_name = pdf_path.name

        if source_name in existing_sources:
            print(f"⏭️  Déjà indexé: {source_name}")
            continue

        print(f"📖 Extraction: {source_name}")
        text = extract_text_from_pdf(pdf_path)

        if not text or len(text.strip()) < 50:
            print(f"⚠️  Texte trop court ou vide: {source_name}")
            continue

        chunks.append({
            "source": source_name,
            "content": text,
            "category": "Enfance",
            "url": None,  # Les PDFs n'ont pas d'URL directe
        })
        added += 1
        print(f"✅ Ajouté: {source_name} ({len(text)} caractères)")

    if added > 0:
        save_chunks(chunks)
        print(f"\n✅ {added} nouveau(x) document(s) ajouté(s)")
        print(f"📊 Total: {len(chunks)} documents dans {CHUNKS_PATH}")
        print("\n🔄 Prochaines étapes:")
        print("   1. python build_corpus_segments.py")
        print("   2. python embed_corpus.py")
        print("   3. Redémarrer le serveur RAG")
    else:
        print("\n✅ Aucun nouveau document à ajouter")


if __name__ == "__main__":
    main()
