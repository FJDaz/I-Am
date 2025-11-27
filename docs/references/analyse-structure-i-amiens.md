# 🔍 Analyse : Application Méthode Backend/ML/docs à I-Amiens

**Date :** 21 novembre 2025  
**Question :** Est-ce que la méthode de rangement Backend/ML/docs peut s'appliquer à I-Amiens ?

---

## ✅ RÉPONSE : **OUI, mais avec adaptations**

I-Amiens peut bénéficier de la même méthode d'organisation que bergsonAndFriends, mais avec quelques adaptations pour sa structure spécifique.

---

## 📊 Structure Actuelle I-Amiens

### Fichiers Racine

**Backend (Serveur) :**
- `rag_assistant_server.py` - Serveur FastAPI principal (1330 lignes)
- `main.py` - Point d'entrée alternatif ?
- `Procfile` - Configuration Railway
- `railway.json` - Configuration Railway
- `requirements.txt` - Dépendances Python
- `runtime.txt` - Version Python

**Frontend (Extension Chrome) :**
- `chrome-extension-v2/` - Extension Chrome (version active)
- `chrome-extension/` - Ancienne version ?
- `assistant-overlay.html` - Overlay HTML

**Préparation Données RAG (ML) :**
- `build_corpus_segments.py` - Construction corpus segments
- `embed_corpus.py` - Génération embeddings
- `extract_pdfs.py` - Extraction PDFs
- `data/` - Données (corpus, embeddings, metadata)
- `download_amiens_enfance/` - Données scrappées

**Outils (Tools) :**
- `tools/` - Scripts utilitaires (address_fetcher, extract_tarif_tables, etc.)

**Tests :**
- `tests/` - Scripts de test
- `test_*.py` - Tests racine

**Documentation :**
- `docs/` - ✅ **Déjà organisé selon méthode BAF** (tutos, notes, references, analyses, tests, supports)

---

## 🎯 Structure Proposée

### Application de la Méthode

```
I-Amiens/
├── Backend/                    # Serveur API + Frontend
│   ├── rag_assistant_server.py # Serveur FastAPI principal
│   ├── main.py                 # Point d'entrée
│   ├── Procfile                # Configuration Railway
│   ├── railway.json            # Config Railway
│   ├── requirements.txt        # Dépendances
│   ├── runtime.txt             # Version Python
│   ├── chrome-extension-v2/    # Extension Chrome (frontend)
│   ├── chrome-extension/       # Ancienne version (si utilisée)
│   └── assistant-overlay.html  # Overlay HTML
│
├── ML/                         # Préparation données RAG
│   ├── data/                   # Données RAG (corpus, embeddings, metadata)
│   │   ├── corpus_segments.json
│   │   ├── corpus_embeddings.npy
│   │   ├── corpus_metadata.json
│   │   ├── rpe_contacts.json
│   │   ├── tarifs_2024_2025.json
│   │   ├── ecoles_amiens.json
│   │   └── raw/                # PDFs sources
│   ├── download_amiens_enfance/ # Données scrappées
│   ├── build_corpus_segments.py # Construction corpus
│   ├── embed_corpus.py         # Génération embeddings
│   ├── extract_pdfs.py         # Extraction PDFs
│   └── chunks_*.json           # Chunks intermédiaires
│
├── tools/                      # Scripts utilitaires (peut rester racine)
│   ├── address_fetcher.py
│   ├── extract_tarif_tables.py
│   ├── fetch_osm_schools.py
│   ├── complete_school_addresses.py
│   ├── curate_segments.py
│   ├── rebuild_corpus.py
│   ├── resume_contexte_manager.py
│   └── [autres tools]
│
├── tests/                      # Scripts de test (peut rester racine)
│   ├── test_40_questions_complet.py
│   ├── test_integration.py
│   ├── eval_rag.py
│   └── [autres tests]
│
└── docs/                       # ✅ Déjà organisé (méthode BAF)
    ├── tutos/
    ├── notes/
    ├── references/
    ├── analyses/
    ├── tests/
    └── supports/
```

---

## 🔄 Différences avec bergsonAndFriends

### 1. **Pas de Fine-tuning de Modèle**

**bergsonAndFriends :**
- ML/ contient prompts, fine-tuning datasets
- Modèles locaux (Qwen 14B, Mistral 7B + LoRA)

**I-Amiens :**
- Utilise Claude (API externe Anthropic)
- ML/ contient préparation données RAG (embeddings, corpus)
- Pas de fine-tuning de modèle

### 2. **Frontend : Extension Chrome**

**bergsonAndFriends :**
- Frontend HTML/JS vanilla dans Backend/

**I-Amiens :**
- Extension Chrome dans `chrome-extension-v2/`
- Devrait aller dans Backend/ (c'est le frontend qui tourne)

### 3. **Structure `tools/` et `tests/`**

**bergsonAndFriends :**
- Scripts dispersés, certains dans Backend/, certains dans ML/

**I-Amiens :**
- Déjà organisés dans `tools/` et `tests/`
- Peuvent rester à la racine ou être déplacés dans Backend/ selon usage

---

## 📝 Plan d'Organisation

### Phase 1 : Créer Backend/ et ML/

```bash
cd "I Amiens"
mkdir -p Backend ML
```

### Phase 2 : Déplacer Backend

```bash
# Serveur
mv rag_assistant_server.py Backend/
mv main.py Backend/
mv Procfile Backend/
mv railway.json Backend/
mv requirements.txt Backend/
mv runtime.txt Backend/

# Frontend
mv chrome-extension-v2 Backend/
mv chrome-extension Backend/  # Si utilisé
mv assistant-overlay.html Backend/
```

### Phase 3 : Déplacer ML (Préparation Données)

```bash
# Scripts de préparation
mv build_corpus_segments.py ML/
mv embed_corpus.py ML/
mv extract_pdfs.py ML/

# Données
mv data/ ML/
mv download_amiens_enfance/ ML/

# Chunks intermédiaires
mv chunks_*.json ML/
mv chunks_*.jsonl ML/
```

### Phase 4 : Décider pour tools/ et tests/

**Option A : Garder à la racine** (si utilisé par Backend ET ML)
**Option B : Déplacer dans Backend/** (si principalement utilisés par le serveur)

---

## ✅ Avantages de l'Organisation

1. **Clarté** : Séparation claire entre serveur, préparation données, et documentation
2. **Cohérence** : Même structure que bergsonAndFriends
3. **Maintenance** : Plus facile de trouver les fichiers
4. **Déploiement** : Railway déploie seulement Backend/

---

## ⚠️ Adaptations Nécessaires

### 1. **Chemins dans rag_assistant_server.py**

Si `data/` est déplacé dans `ML/`, mettre à jour les chemins :
```python
# Avant
DATA_DIR = Path("data")

# Après
DATA_DIR = Path("../ML/data")
# Ou utiliser chemin absolu/projet
```

### 2. **Procfile Railway**

Si fichiers déplacés, mettre à jour :
```
# Avant
web: python rag_assistant_server.py

# Après
web: python Backend/rag_assistant_server.py
```

### 3. **Extension Chrome**

Vérifier les chemins dans `manifest.json` et `content.js` si déplacée.

---

## 🎯 Recommandation

### ✅ **OUI, appliquer la méthode avec adaptations**

**Organisation recommandée :**
1. ✅ **Backend/** : Serveur FastAPI + Extension Chrome
2. ✅ **ML/** : Préparation données RAG (embeddings, corpus)
3. ✅ **docs/** : Déjà organisé (garder tel quel)
4. ⚠️ **tools/** : Garder à la racine (utilisé par Backend ET ML)
5. ⚠️ **tests/** : Garder à la racine ou dans Backend/ selon usage

**Différence principale avec bergsonAndFriends :**
- ML/ contient préparation données RAG, pas fine-tuning de modèle
- Backend/ contient Extension Chrome, pas juste HTML

---

## 📋 Checklist d'Application

- [ ] Créer dossiers Backend/ et ML/
- [ ] Déplacer fichiers serveur dans Backend/
- [ ] Déplacer Extension Chrome dans Backend/
- [ ] Déplacer scripts préparation données dans ML/
- [ ] Déplacer data/ dans ML/
- [ ] Mettre à jour chemins dans rag_assistant_server.py
- [ ] Mettre à jour Procfile pour Railway
- [ ] Mettre à jour manifest.json Extension Chrome si nécessaire
- [ ] Créer Backend/README.md
- [ ] Créer ML/README.md
- [ ] Mettre à jour README.md principal

---

**Conclusion :** ✅ La méthode s'applique parfaitement à I-Amiens avec quelques adaptations pour sa structure spécifique (Extension Chrome, pas de fine-tuning, outils séparés).

---

**Dernière mise à jour :** 21 novembre 2025

