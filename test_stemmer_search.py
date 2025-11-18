#!/usr/bin/env python3
"""
Script de test pour vérifier que le stemmer français fonctionne correctement
avec des requêtes comme "inscrire" qui devraient matcher "inscription"
"""

import json
import tempfile
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from whoosh import scoring
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import ID, TEXT, Schema
from whoosh.index import create_in
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.lang.snowball.french import FrenchStemmer

# Chemins
BASE_DIR = Path(__file__).resolve().parent
EMBEDDINGS_PATH = BASE_DIR / "data" / "corpus_embeddings.npy"
METADATA_PATH = BASE_DIR / "data" / "corpus_metadata.json"

print("🔄 Chargement des données...")
corpus_embeddings = np.load(EMBEDDINGS_PATH)
with METADATA_PATH.open(encoding="utf-8") as f:
    corpus_metadata = json.load(f)

embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

print(f"✅ {len(corpus_metadata)} segments chargés")

# Construction de l'index Whoosh avec stemmer français
print("🔄 Construction de l'index Whoosh avec stemmer français...")
schema = Schema(
    id=ID(stored=True, unique=True),
    label=TEXT(stored=True),
    content=TEXT(analyzer=StemmingAnalyzer(minsize=2, stemfn=FrenchStemmer().stem), stored=False),
)

whoosh_dir = Path(tempfile.mkdtemp(prefix="test_whoosh_"))
ix = create_in(whoosh_dir, schema)
writer = ix.writer()

for idx, meta in enumerate(corpus_metadata):
    doc_id = str(idx)
    label = meta.get("label") or meta.get("source") or ""
    content = " ".join(
        str(meta.get(field, "")) for field in ("content", "label", "source", "section")
    )
    writer.add_document(id=doc_id, label=label, content=content)

writer.commit()
print(f"✅ Index Whoosh construit")

# Fonction de recherche hybride
def search_hybrid(question: str, top_k: int = 5):
    results = {}
    weights = {}

    # 1. Recherche BM25 avec stemmer français
    parser = MultifieldParser(["label", "content"], schema=ix.schema, group=OrGroup)
    query = parser.parse(question)

    with ix.searcher(weighting=scoring.BM25F(B=0.75, K1=1.6)) as searcher:
        hits = searcher.search(query, limit=top_k * 4)
        print(f"\n📊 BM25 (stemmer français) a trouvé {len(hits)} résultats pour '{question}':")
        for hit in hits[:5]:
            doc_id = hit["id"]
            score = float(hit.score or 0.0)
            meta = corpus_metadata[int(doc_id)]
            results[doc_id] = meta
            weights[doc_id] = score * 1.0  # Poids BM25 = 1.0
            print(f"  - [{score:.3f}] {meta.get('label', 'Sans titre')[:80]}")

    # 2. Recherche sémantique (embeddings)
    query_vec = embed_model.encode([question], normalize_embeddings=True)[0]
    scores = corpus_embeddings @ query_vec
    best_idx = np.argsort(-scores)[: top_k * 4]

    print(f"\n📊 Recherche sémantique (cosine) pour '{question}':")
    for idx in best_idx[:5]:
        score = float(scores[idx])
        if score < 0.2:
            continue
        doc_id = str(idx)
        meta = corpus_metadata[idx]
        if doc_id not in results:
            results[doc_id] = meta
        weights[doc_id] = weights.get(doc_id, 0.0) + (score * 0.6)  # Poids cosine = 0.6
        print(f"  - [{score:.3f}] {meta.get('label', 'Sans titre')[:80]}")

    # 3. Combinaison et classement final
    ranked = sorted(weights.items(), key=lambda item: item[1], reverse=True)[:top_k]

    print(f"\n🎯 TOP {top_k} RÉSULTATS COMBINÉS:")
    for rank, (doc_id, combined_score) in enumerate(ranked, 1):
        meta = results[doc_id]
        label = meta.get('label', 'Sans titre')
        content_preview = meta.get('content', '')[:150].replace('\n', ' ')
        print(f"\n{rank}. Score: {combined_score:.3f}")
        print(f"   Titre: {label}")
        print(f"   Extrait: {content_preview}...")

    return ranked, results

# Tests
print("\n" + "="*80)
print("TEST 1: Requête 'inscrire' (devrait trouver des docs sur 'inscription')")
print("="*80)
search_hybrid("inscrire", top_k=5)

print("\n" + "="*80)
print("TEST 2: Requête 'comment inscrire mon enfant' (plus contextuel)")
print("="*80)
search_hybrid("comment inscrire mon enfant", top_k=5)

print("\n" + "="*80)
print("TEST 3: Requête 'inscription scolaire' (contrôle - devrait bien fonctionner)")
print("="*80)
search_hybrid("inscription scolaire", top_k=5)

print("\n✅ Tests terminés!")
