# 🧹 Nettoyage Fichiers Racine - I-Amiens

**Date :** 21 novembre 2025  
**Objectif :** Organiser les fichiers restés en vrac à la racine après création Backend/ML/docs

---

## ✅ Fichiers Organisés

### Scripts de Préparation Données → `ML/scripts/`

- **`# crawler_respectueux.py`** → `ML/scripts/# crawler_respectueux.py`
  - Crawler respectueux robots.txt
  - Commenté (fichier avec `#` au début)

- **`# audit_dynamiques.py`** → `ML/scripts/# audit_dynamiques.py`
  - Audit dynamique avec Playwright
  - Commenté

- **`# mvp_chunks_cursor.py`** → `ML/scripts/# mvp_chunks_cursor.py`
  - MVP chunks (version ancienne)
  - Commenté

- **`Audit_Scrap_enfance.py`** → `ML/scripts/Audit_Scrap_enfance.py`
  - Audit et scraping dynamique avec Playwright
  - Active JS, clique sur "voir +", récupère PDFs

- **`audit_enfance_online.py`** → `ML/scripts/audit_enfance_online.py`
  - Audit en ligne des pages Enfance
  - Détecte structures cachées (tables, blocs masqués)

- **`update_chunks_from_download.py`** → `ML/scripts/update_chunks_from_download.py`
  - Mise à jour chunks depuis download_amiens_enfance

### Chunks Intermédiaires → `ML/chunks/`

- **`chunks_enfance.json`** → `ML/chunks/chunks_enfance.json`
- **`chunks_enfance_clean.json`** → `ML/chunks/chunks_enfance_clean.json`
- **`chunks_enfance_min.json`** → `ML/chunks/chunks_enfance_min.json`
- **`chunks_enfance_final.json`** → `ML/chunks/chunks_enfance_final.json`
- **`chunks_enfance.jsonl`** → `ML/chunks/chunks_enfance.jsonl`
- **`chunks_enfance_clean.jsonl`** → `ML/chunks/chunks_enfance_clean.jsonl`

**Pourquoi dans ML/ ?** Les chunks sont des **données intermédiaires** de préparation du corpus RAG. Ils font partie du workflow ML :
1. Scraper site → `download_amiens_enfance/`
2. Extraire chunks → `chunks/chunks_enfance.json`
3. Nettoyer chunks → `chunks/chunks_enfance_clean.json`
4. Construire corpus → `data/corpus_segments.json`
5. Générer embeddings → `data/corpus_embeddings.npy`

Ils ne sont **pas utilisés directement par le Backend** (qui utilise `data/corpus_segments.json`), donc ils restent dans ML/.

### Tests Racine → `tests/`

- **`test_rag_questions.py`** → `tests/test_rag_questions.py`
- **`test_rag_series.py`** → `tests/test_rag_series.py`
- **`test_stemmer_search.py`** → `tests/test_stemmer_search.py`
- **`export_test_results.py`** → `tests/export_test_results.py`

### Scripts Utilitaires → `tools/`

- **`list_models.py`** → `tools/list_models.py`
- **`from bs4 import BeautifulSoup.py`** → `tools/` (fichier mal nommé)
- **`import gradio as gr.py`** → `tools/` (fichier mal nommé)

### Docs et Scripts Serveur → `docs/` et `Backend/`

- **`DEPLOIEMENT_MVP.md`** → `docs/tutos/deploiement-mvp.md`
- **`RELOAD_SERVER.sh`** → `Backend/RELOAD_SERVER.sh`
- **`start_server_http.sh`** → `Backend/start_server_http.sh`

### Certificats SSL → `Backend/`

- **`localhost-cert.pem.bak`** → `Backend/localhost-cert.pem.bak`
- **`localhost-key.pem.bak`** → `Backend/localhost-key.pem.bak`

---

## 📁 Structure Finale ML/

```
ML/
├── data/                       # Données RAG finales (utilisées par Backend)
│   ├── corpus_segments.json
│   ├── corpus_embeddings.npy
│   ├── corpus_metadata.json
│   └── [données structurées]
│
├── chunks/                     # ✅ NOUVEAU - Chunks intermédiaires
│   ├── chunks_enfance.json
│   ├── chunks_enfance_clean.json
│   ├── chunks_enfance_min.json
│   ├── chunks_enfance_final.json
│   └── chunks_enfance*.jsonl
│
├── scripts/                    # ✅ NOUVEAU - Scripts de préparation
│   ├── # crawler_respectueux.py    # Commenté
│   ├── # audit_dynamiques.py       # Commenté
│   ├── # mvp_chunks_cursor.py      # Commenté
│   ├── audit_enfance_online.py
│   ├── Audit_Scrap_enfance.py
│   └── update_chunks_from_download.py
│
├── download_amiens_enfance/    # Données scrappées
├── build_corpus_segments.py    # Scripts principaux
├── embed_corpus.py
└── extract_pdfs.py
```

---

## ✅ Fichiers Restants à la Racine (Normaux)

Ces fichiers restent à la racine car c'est leur place normale :

- **`.git/`**, **`.gitignore`** - Git (convention)
- **`.venv/`**, **`.netlify/`**, **`.claude/`** - Config système (convention)
- **`.env`** - Variables d'environnement (convention)
- **`Backend/`**, **`ML/`**, **`docs/`**, **`tools/`**, **`tests/`** - Dossiers projet
- **`README.md`** - Documentation principale
- **`logs/`**, **`flagged/`**, **`skills/`**, **`Journals/`** - Autres dossiers projet
- **`I Amiens Logo.ai`**, **`I Amiens.code-workspace`** - Fichiers de config projet

---

## 🎯 Pourquoi les Chunks sont dans ML/

**Question :** Pourquoi les chunks sont-ils dans ML/ et pas dans Backend/ ?

**Réponse :**

1. **Workflow ML** : Les chunks sont des **données intermédiaires** de préparation du corpus RAG, pas des données finales utilisées par le Backend.

2. **Workflow complet** :
   ```
   Scraper → download_amiens_enfance/
     ↓
   Extraire chunks → chunks/chunks_enfance.json
     ↓
   Nettoyer chunks → chunks/chunks_enfance_clean.json
     ↓
   Construire corpus → data/corpus_segments.json  ← Utilisé par Backend
     ↓
   Générer embeddings → data/corpus_embeddings.npy  ← Utilisé par Backend
   ```

3. **Séparation Backend/ML** :
   - **Backend/** = Code qui tourne (serveur, frontend)
   - **ML/** = Préparation données (scraping, chunks, corpus, embeddings)
   - Les chunks sont **intermédiaires**, donc dans ML/, pas dans Backend/

4. **Organisation** : Les chunks sont maintenant dans `ML/chunks/` pour éviter le désordre dans `ML/` racine.

---

**Organisation terminée le :** 21 novembre 2025

