# Plan d'Action Complet : Généraliser I-Amiens à Tout le Site

**Date :** 2025-01-XX  
**Inclut :** Optimisations performance (Claude Haiku, cache, RAG)

---

## Phase 1 : Refactoriser les Modules de Découverte

✅ **Automatisable :**
- Créer `tools/discover_urls.py` avec classe `URLDiscoverer`
- Modifier `tools/rebuild_corpus.py` pour utiliser `URLDiscoverer`

---

## Phase 2 : Configuration Multi-Sections

✅ **Automatisable :**
- Créer `ML/data/site_sections.json`
- Créer `tools/crawl_site_generalized.py`

---

## Phase 3 : Généraliser le Scraping Dynamique

✅ **Automatisable :**
- Renommer `ML/scripts/Audit_Scrap_enfance.py` → `crawl_dynamic.py`
- Généraliser pour toutes sections

---

## Phase 4 : Régénération Embeddings et Index RAG

✅ **Automatisable :**
- Modifier `ML/embed_corpus.py` pour corpus généralisé
- Vérifier performance Whoosh (code de test)

⚠️ **Nécessite validation :**
- Tester performance avec corpus plus grand

---

## Phase 5 : Adaptation Système RAG

✅ **Automatisable :**
- Modifier prompt système (généraliser "Amiens Enfance")
- Adapter chemins embeddings (détection automatique)
- Créer structure lexiques multi-sections
- Adapter `load_structured_data()` (chargement conditionnel)

---

## Phase 6 : Optimisation Performance et Latence

✅ **Automatisable :**
- Créer `Backend/cache.py` (cache mémoire)
- Intégrer cache dans `rag_assistant_endpoint()`
- Optimiser recherche RAG (réduire top_k, cache embeddings)
- Ajouter support Claude Haiku (variable d'environnement)

⚠️ **Nécessite décision :**
- Tester Claude Haiku vs Sonnet et décider
- Valider que cache fonctionne correctement

---

## Phase 7 : Tests et Validation

❌ **Nécessite intervention manuelle :**
- Test régression Enfance
- Test nouvelles sections (Jeunesse, etc.)
- Test système RAG complet
- Validation qualité réponses

---

## Phase 8 : Documentation

✅ **Automatisable :**
- Créer `docs/tutos/GUIDE_GENERALISATION_SITE.md`
- Mettre à jour documentation stratégies

---

## 🚀 Ce que je peux lancer maintenant

### Fichiers à créer (100% automatique) :
1. ✅ `tools/discover_urls.py` - Module découverte URLs
2. ✅ `tools/crawl_site_generalized.py` - Crawler généralisé
3. ✅ `ML/data/site_sections.json` - Configuration sections
4. ✅ `Backend/cache.py` - Cache mémoire
5. ✅ `ML/scripts/crawl_dynamic.py` - Scraping dynamique généralisé
6. ✅ `docs/tutos/GUIDE_GENERALISATION_SITE.md` - Guide utilisateur

### Fichiers à modifier (100% automatique) :
1. ✅ `tools/rebuild_corpus.py` - Utiliser URLDiscoverer
2. ✅ `ML/embed_corpus.py` - Support corpus généralisé
3. ✅ `Backend/rag_assistant_server.py` - Prompt, chemins, cache, Haiku
4. ✅ Documentation existante

### Ce qui nécessite votre intervention :
1. ⚠️ Tester et valider (après création fichiers)
2. ⚠️ Activer sections souhaitées dans `site_sections.json`
3. ⚠️ Décider Claude Haiku vs Sonnet (après tests)
4. ⚠️ Déployer sur Railway

---

## 💡 Recommandation

**Je peux créer TOUS les fichiers de code maintenant** (environ 15-20 fichiers/modifications).

**Vous devrez ensuite :**
- Tester le crawl sur Enfance
- Activer les sections souhaitées
- Tester Claude Haiku
- Valider et déployer

**Souhaitez-vous que je commence maintenant ?**

---

**Dernière mise à jour :** 2025-01-XX

