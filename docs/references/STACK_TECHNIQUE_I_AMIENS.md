# 🛠️ Stack Technique - I-Amiens

**Date :** 19 novembre 2025  
**Projet :** Assistant RAG pour Amiens Enfance

---

## 📋 Stack Complète

### Backend

**Langage :** Python 3.9+  
**Framework :** FastAPI  
**Serveur :** Uvicorn (ASGI)

**Dépendances principales :**
- `fastapi>=0.104.1` - Framework web API
- `uvicorn[standard]>=0.24.0` - Serveur ASGI
- `anthropic>=0.18.1` - Client API Claude (Anthropic)
- `pydantic>=2.5.0` - Validation de données
- `numpy>=1.24.3` - Calculs numériques (embeddings)
- `whoosh>=2.7,<3` - Moteur de recherche full-text
- `pdfminer.six>=20220524` - Extraction PDF
- `xlrd>=2.0.1` - Lecture fichiers Excel
- `python-dotenv>=1.0.0` - Gestion variables d'environnement

### Frontend

**Extension Chrome :** Chrome Extension v2  
**Technologies :**
- JavaScript vanilla (pas de framework)
- Manifest V3 (Chrome Extension)
- Content Scripts
- Overlay HTML

**Fichiers clés :**
- `chrome-extension-v2/manifest.json` - Configuration extension
- `chrome-extension-v2/content.js` - Script injection
- `chrome-extension-v2/diagnostic.js` - Diagnostic
- `chrome-extension-v2/data/` - Données locales (corpus, lexique)

### RAG System

**Technologie :** Whoosh (full-text search) + NumPy (embeddings)

**Composants :**
- **Corpus segments** : `data/corpus_segments.json`
- **Embeddings** : `data/corpus_embeddings.npy` (NumPy array)
- **Metadata** : `data/corpus_metadata.json`
- **Whoosh index** : Recherche full-text

**Données structurées :**
- `data/rpe_contacts.json` - Contacts RPE
- `data/lieux_importants.json` - Lieux importants
- `data/tarifs_2024_2025.json` - Tableaux tarifs
- `data/ecoles_amiens.json` - Écoles Amiens
- `data/lieux_cache.json` - Cache adresses

### IA / LLM

**Modèle :** Claude (Anthropic)  
**API :** Anthropic API  
**Usage :** Génération réponses avec contexte RAG

---

## 🏗️ Architecture

### Flux Complet

```
Utilisateur (Chrome)
    ↓
Extension Chrome (content.js)
    ↓
Backend FastAPI (rag_assistant_server.py)
    ↓
RAG System (Whoosh + NumPy embeddings)
    ↓
Claude API (Anthropic)
    ↓
Réponse enrichie avec sources
```

### Composants

1. **Extension Chrome**
   - Injecte overlay sur pages Amiens.fr
   - Appelle backend FastAPI
   - Affiche réponses avec sources

2. **Backend FastAPI**
   - Endpoint `/rag_assistant` (POST)
   - Gère RAG lookup
   - Appelle Claude API
   - Retourne réponse HTML + sources

3. **RAG System**
   - Whoosh : Recherche full-text dans corpus
   - NumPy : Similarité sémantique (embeddings)
   - Extraction concepts
   - Formatage contexte

4. **Claude API**
   - Génération réponse avec contexte RAG
   - Format JSON strict
   - Questions de suivi (follow_up_question)

---

## 📦 Dépendances Détaillées

### Backend (Python)

```txt
fastapi>=0.104.1          # Framework web API REST
uvicorn[standard]>=0.24.0  # Serveur ASGI (avec standard pour performance)
anthropic>=0.18.1         # Client API Claude (Anthropic)
pydantic>=2.5.0          # Validation données (modèles)
python-dotenv>=1.0.0     # Variables d'environnement (.env)
numpy>=1.24.3            # Calculs numériques (embeddings)
whoosh>=2.7,<3           # Moteur recherche full-text
pdfminer.six>=20220524   # Extraction texte PDF
xlrd>=2.0.1              # Lecture fichiers Excel
```

### Frontend (Chrome Extension)

**Manifest V3 :**
- Content Scripts
- Background Service Worker (si nécessaire)
- Permissions : `activeTab`, `storage`

**Technologies :**
- JavaScript ES6+
- HTML/CSS (overlay)
- Chrome Extension APIs

---

## 🚀 Déploiement

### Backend

**Plateforme :** Railway (PaaS)  
**Fichiers de configuration :**
- `Procfile` : `web: python rag_assistant_server.py`
- `railway.json` : Configuration Railway
- `runtime.txt` : Version Python (si spécifiée)

**Variables d'environnement :**
- `ANTHROPIC_API_KEY` - Clé API Claude
- `PORT` - Port serveur (auto par Railway)

### Frontend

**Distribution :** Extension Chrome (fichiers locaux)  
**Installation :** Mode développeur Chrome

---

## 📊 Comparaison avec Bergson and Friends

| Composant | I-Amiens | Bergson and Friends |
|-----------|----------|---------------------|
| **Backend** | FastAPI (Python) | FastAPI (Python) |
| **Frontend** | Chrome Extension | HTML/JS vanilla |
| **IA** | Claude (Anthropic) | Qwen 14B + LoRA (HF/Modal) |
| **RAG** | Whoosh + NumPy | Custom (corpus segments) |
| **Déploiement** | Railway | Render + Modal/HF |
| **Modèle** | API externe (Claude) | Modèle local (Qwen) |

---

## 🔧 Outils et Scripts

### Scripts Python

- `rag_assistant_server.py` - Serveur FastAPI principal
- `tools/address_fetcher.py` - Système adresses dynamique
- `tools/extract_tarif_tables.py` - Extraction tableaux PDF
- `tools/fetch_osm_schools.py` - Récupération écoles OSM
- `tools/complete_school_addresses.py` - Complétion adresses
- `embed_corpus.py` - Génération embeddings
- `build_corpus_segments.py` - Construction corpus segments

### Tests

- `tests/test_40_questions_complet.py` - Tests 40 questions
- `tests/test_integration.py` - Tests intégration
- `tests/eval_rag.py` - Évaluation RAG

---

## 📝 Fichiers Clés

### Backend

- `rag_assistant_server.py` - Serveur FastAPI (1330 lignes)
- `requirements.txt` - Dépendances Python
- `Procfile` - Commande démarrage Railway
- `railway.json` - Configuration Railway

### Frontend

- `chrome-extension-v2/manifest.json` - Configuration extension
- `chrome-extension-v2/content.js` - Script injection
- `chrome-extension-v2/diagnostic.js` - Diagnostic

### Data

- `data/corpus_segments.json` - Corpus segments RAG
- `data/corpus_embeddings.npy` - Embeddings NumPy
- `data/corpus_metadata.json` - Metadata corpus
- `data/rpe_contacts.json` - Contacts RPE
- `data/tarifs_2024_2025.json` - Tarifs
- `data/ecoles_amiens.json` - Écoles

---

## 🎯 Résumé Ultra-Rapide

**Stack I-Amiens :**
- **Backend :** FastAPI (Python) sur Railway
- **Frontend :** Chrome Extension (JavaScript)
- **IA :** Claude API (Anthropic)
- **RAG :** Whoosh + NumPy embeddings
- **Déploiement :** Railway (PaaS)

**Différence principale avec BAF :**
- I-Amiens utilise Claude (API externe)
- BAF utilise Qwen 14B (modèle local fine-tuné)

---

**Dernière mise à jour :** 19 novembre 2025

