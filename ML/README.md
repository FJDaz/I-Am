# 🤖 ML - Préparation des Données RAG

**Dossier :** `ML/`  
**Contenu :** Fichiers liés à la préparation et au traitement des données RAG

---

## 📁 Structure

```
ML/
├── data/                       # Données RAG (corpus, embeddings, metadata)
│   ├── corpus_segments.json   # Corpus segments (utilisé par Backend)
│   ├── corpus_embeddings.npy  # Embeddings NumPy (utilisé par Backend)
│   ├── corpus_metadata.json   # Metadata corpus (utilisé par Backend)
│   ├── rpe_contacts.json      # Contacts RPE
│   ├── lieux_importants.json  # Lieux importants
│   ├── tarifs_2024_2025.json  # Tableaux tarifs
│   ├── ecoles_amiens.json     # Écoles Amiens
│   └── raw/                   # PDFs sources
│       ├── COUPON+INSCRIPTION*.pdf
│       ├── LISTE+ALSH+ETE+2025.pdf
│       └── menus/
│
├── download_amiens_enfance/   # Données scrappées (HTML/TXT)
│   └── [374 fichiers HTML/TXT scrappés du site]
│
├── build_corpus_segments.py   # Construction corpus segments
├── embed_corpus.py            # Génération embeddings
├── extract_pdfs.py            # Extraction PDFs
└── chunks_*.json              # Chunks intermédiaires
```

---

## 📋 Contenu par Catégorie

### Données RAG (`data/`)

**Fichiers utilisés par le Backend :**

- **`corpus_segments.json`** - Corpus segments RAG
  - Format : JSON avec segments numérotés
  - Utilisé par : Backend RAG System (Whoosh + embeddings)

- **`corpus_embeddings.npy`** - Embeddings NumPy
  - Format : NumPy array (numpy.ndarray)
  - Modèle : `sentence-transformers/all-MiniLM-L6-v2`
  - Généré par : `embed_corpus.py`

- **`corpus_metadata.json`** - Metadata corpus
  - Format : JSON avec métadonnées (label, url, etc.)
  - Utilisé avec : `corpus_embeddings.npy`

**Données structurées :**

- **`rpe_contacts.json`** - Contacts RPE (Relais Petite Enfance)
- **`lieux_importants.json`** - Lieux importants (écoles, structures)
- **`tarifs_2024_2025.json`** - Tableaux tarifs (crèches, centres de loisirs)
- **`ecoles_amiens.json`** - Écoles Amiens (adresses, contacts)

**Sources brutes :**

- **`raw/`** - PDFs sources
  - Documents d'inscription
  - Menus
  - Tarifs et synoptiques

### Données Scrappées (`download_amiens_enfance/`)

**Contenu :** 374 fichiers HTML/TXT scrappés du site "Vivre à Amiens - Enfance"
- Pages HTML complètes
- Extractions texte (.txt)
- Utilisé pour construire le corpus RAG

### Scripts de Préparation

- **`build_corpus_segments.py`** - Construction corpus segments
  - Lit les données scrappées
  - Découpe en segments
  - Génère `corpus_segments.json`

- **`embed_corpus.py`** - Génération embeddings
  - Lit `corpus_segments.json`
  - Génère embeddings avec sentence-transformers
  - Exporte `corpus_embeddings.npy` et `corpus_metadata.json`

- **`extract_pdfs.py`** - Extraction PDFs
  - Lit les PDFs dans `data/raw/`
  - Extrait le texte
  - Génère fichiers structurés

### Chunks Intermédiaires (`chunks/`)

**Fichiers intermédiaires de traitement :**
- `chunks/chunks_enfance.json` - Chunks bruts
- `chunks/chunks_enfance_clean.json` - Chunks nettoyés
- `chunks/chunks_enfance_min.json` - Chunks minimisés
- `chunks/chunks_enfance_final.json` - Chunks finaux
- `chunks/chunks_enfance.jsonl` - Format JSONL

**Pourquoi dans ML/ ?** Ces fichiers sont des **données intermédiaires** de préparation du corpus RAG. Ils font partie du workflow ML (extraction → chunks → corpus → embeddings) et sont stockés dans `ML/chunks/` car ils ne sont pas utilisés directement par le Backend (qui utilise `data/corpus_segments.json`).

### Scripts de Préparation (`scripts/`)

**Scripts de scraping et audit :**
- `scripts/# crawler_respectueux.py` - Crawler respectueux (commenté)
- `scripts/# audit_dynamiques.py` - Audit dynamique (commenté)
- `scripts/# mvp_chunks_cursor.py` - MVP chunks (commenté)
- `scripts/audit_enfance_online.py` - Audit en ligne des pages Enfance
- `scripts/Audit_Scrap_enfance.py` - Audit et scraping dynamique
- `scripts/update_chunks_from_download.py` - Mise à jour chunks depuis download

**Note :** Les fichiers avec `#` au début sont commentés/ignorés mais conservés pour référence.

---

## 🛠️ Usage

### Construire le Corpus

```bash
cd ML
python build_corpus_segments.py
```

**Résultat :** Génère `data/corpus_segments.json`

### Générer les Embeddings

```bash
cd ML
python embed_corpus.py
```

**Résultat :** 
- Génère `data/corpus_embeddings.npy`
- Génère `data/corpus_metadata.json`

### Extraire les PDFs

```bash
cd ML
python extract_pdfs.py
```

**Résultat :** Extrait texte des PDFs dans `data/raw/`

---

## 🔄 Workflow ML

```
1. Scraper site Amiens Enfance
   ↓
2. Extraire PDFs (extract_pdfs.py)
   ↓
3. Construire corpus segments (build_corpus_segments.py)
   ↓
4. Générer embeddings (embed_corpus.py)
   ↓
5. Intégrer dans Backend (Backend/rag_assistant_server.py)
```

---

## 📝 Notes

### Différence avec bergsonAndFriends

**bergsonAndFriends :**
- ML/ contient fine-tuning de modèles (LoRA, adapters)
- Prompts système pour les modèles

**I-Amiens :**
- ML/ contient préparation données RAG (pas de fine-tuning)
- Pas de prompts système (utilise Claude API externe)
- Focus sur corpus, embeddings, données structurées

### Utilisation par le Backend

Les fichiers dans `ML/data/` sont utilisés par :
- **Backend/rag_assistant_server.py** - Charge embeddings, metadata, données structurées
- **Backend/chrome-extension-v2/** - Charge `corpus_segments.json` localement

---

## 🔗 Liens

- **Backend :** `../Backend/`
- **Documentation :** `../docs/`
- **RAG System :** `../docs/references/segments-rag.md`
- **Stack technique :** `../docs/references/STACK_TECHNIQUE_I_AMIENS.md`

