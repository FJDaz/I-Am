# 🎓 I-Amiens

**Projet :** Assistant RAG pour Amiens Enfance  
**Backend :** FastAPI (Python) sur Railway  
**Frontend :** Extension Chrome (Manifest V3)  
**IA :** Claude (Anthropic API)

---

## 📁 Structure du Projet

```
I-Amiens/
├── Backend/                    # Serveur API + Extension Chrome
│   ├── rag_assistant_server.py # Serveur FastAPI principal (1330 lignes)
│   ├── main.py                 # Point d'entrée alternatif
│   ├── chrome-extension-v2/    # Extension Chrome (frontend)
│   ├── chrome-extension/       # Ancienne version (legacy)
│   ├── assistant-overlay.html  # Overlay HTML
│   ├── Procfile                # Configuration Railway
│   ├── railway.json            # Config Railway
│   └── requirements.txt        # Dépendances Python
│
├── ML/                         # Préparation données RAG
│   ├── data/                   # Données RAG (corpus, embeddings, metadata)
│   │   ├── corpus_segments.json
│   │   ├── corpus_embeddings.npy
│   │   ├── corpus_metadata.json
│   │   ├── rpe_contacts.json
│   │   ├── lieux_importants.json
│   │   ├── tarifs_2024_2025.json
│   │   ├── ecoles_amiens.json
│   │   └── raw/                # PDFs sources
│   ├── download_amiens_enfance/ # Données scrappées (374 fichiers)
│   ├── build_corpus_segments.py # Construction corpus
│   ├── embed_corpus.py          # Génération embeddings
│   ├── extract_pdfs.py          # Extraction PDFs
│   └── chunks_*.json            # Chunks intermédiaires
│
├── tools/                       # Scripts utilitaires
│   ├── address_fetcher.py
│   ├── extract_tarif_tables.py
│   ├── fetch_osm_schools.py
│   ├── complete_school_addresses.py
│   ├── curate_segments.py
│   ├── rebuild_corpus.py
│   └── resume_contexte_manager.py
│
├── tests/                       # Scripts de test
│   ├── test_40_questions_complet.py
│   ├── test_integration.py
│   ├── eval_rag.py
│   └── [autres tests]
│
└── docs/                        # Documentation
    ├── tutos/                   # Guides pas à pas
    ├── notes/                   # Notes rapides
    ├── references/              # Références techniques
    ├── analyses/                # Analyses détaillées
    ├── tests/                   # Documentation des tests
    └── supports/                # Support technique
```

---

## 🚀 Quick Start

### Backend (Local)

1. **Installer dépendances** :
   ```bash
   cd Backend
   pip install -r requirements.txt
   ```

2. **Configurer variables d'environnement** :
   ```bash
   # Créer .env à la racine
   ANTHROPIC_API_KEY=your_key_here
   ```

3. **Lancer le serveur** :
   ```bash
   python Backend/rag_assistant_server.py
   ```

4. **Interface** : `http://localhost:8000`

### Extension Chrome

1. **Ouvrir Chrome** : `chrome://extensions/`
2. **Mode développeur** : Activer
3. **Charger l'extension** : Sélectionner `Backend/chrome-extension-v2/`
4. **Utiliser** : L'extension injecte l'assistant dans les pages

### Railway (Déploiement)

1. **Déployer** sur Railway
2. **Configurer** variables d'environnement dans Railway dashboard
3. **Railway** lance automatiquement via `Procfile`

---

## 📚 Documentation

- **README Backend :** `Backend/README.md`
- **README ML :** `ML/README.md`
- **Documentation complète :** `docs/README.md`
- **Stack technique :** `docs/references/STACK_TECHNIQUE_I_AMIENS.md`
- **Tutos :** `docs/tutos/`

---

## 🔧 Développement

### Préparer les Données RAG

1. **Extraire PDFs** : `python ML/extract_pdfs.py`
2. **Construire corpus** : `python ML/build_corpus_segments.py`
3. **Générer embeddings** : `python ML/embed_corpus.py`

### Tester le RAG

1. **Tests 40 questions** : `python tests/test_40_questions_complet.py`
2. **Tests intégration** : `python tests/test_integration.py`
3. **Évaluer RAG** : `python tests/eval_rag.py`

---

## 🎯 Architecture

```
Utilisateur (Chrome)
    ↓
Extension Chrome (chrome-extension-v2/content.js)
    ↓
Backend FastAPI (rag_assistant_server.py)
    ├── RAG System
    │   ├── Whoosh (full-text search)
    │   └── NumPy embeddings (sentence-transformers)
    │   └── ML/data/ (corpus, embeddings, metadata)
    ├── Claude API (Anthropic)
    └── Données structurées
        ├── RPE contacts
        ├── Lieux importants
        ├── Tarifs 2024-2025
        └── Écoles Amiens
```

---

## 📝 Endpoints API

- `GET /health` - Health check
- `POST /rag_assistant` - Requête RAG principale
- `GET /init` - Initialisation conversation

---

## 🔗 Références

- **Méthode d'organisation :** `docs/references/analyse-structure-i-amiens.md`
- **Segments RAG :** `docs/references/segments-rag.md`
- **Alignement RAG :** `docs/references/alignement-rag.md`

---

**Dernière mise à jour :** 21 novembre 2025
