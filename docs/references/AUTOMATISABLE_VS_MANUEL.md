# 🤖 Ce qui peut être automatisé vs nécessite intervention manuelle

**Date :** 2025-01-XX  
**Contexte :** Plan de généralisation I-Amiens à tout le site

---

## ✅ Ce que je peux faire automatiquement (sans intervention)

### Phase 1 : Refactoriser les Modules de Découverte

✅ **Créer `tools/discover_urls.py`**
- Code complet avec classe `URLDiscoverer`
- Toutes les stratégies (push-blocks, liens internes, navigation, sitemap)
- Gestion robots.txt et délais

✅ **Modifier `tools/rebuild_corpus.py`**
- Importer `URLDiscoverer`
- Remplacer `discover_push_blocks()` par appel à `URLDiscoverer`
- Rendre `load_sources()` configurable

### Phase 2 : Configuration Multi-Sections

✅ **Créer `ML/data/site_sections.json`**
- Structure complète avec toutes les sections
- Enfance activée, autres désactivées par défaut
- Settings globaux configurés

✅ **Créer `tools/crawl_site_generalized.py`**
- Script complet de crawl généralisé
- Utilise toutes les stratégies de découverte
- Gère multi-sections automatiquement

### Phase 3 : Généraliser le Scraping Dynamique

✅ **Renommer et modifier `ML/scripts/Audit_Scrap_enfance.py` → `crawl_dynamic.py`**
- Généraliser BASE_URL (paramètre)
- Support multi-sections
- Sélecteurs généralisés

### Phase 4 : Régénération Embeddings

✅ **Modifier `ML/embed_corpus.py`**
- Adapter pour charger `corpus_metadata_generalized.json`
- Générer `corpus_embeddings_generalized.npy`

### Phase 5 : Adaptation Système RAG

✅ **Modifier `Backend/rag_assistant_server.py` - Chemins**
- Détection automatique corpus_generalized si existe
- Fallback sur corpus actuel

✅ **Modifier `Backend/rag_assistant_server.py` - Prompt système**
- Généraliser "Amiens Enfance" → "Amiens"
- Ou prompt dynamique selon section détectée

✅ **Créer structure lexiques multi-sections**
- Créer fichiers `lexique_jeunesse.json`, etc. (vides ou templates)
- Adapter `load_lexicon()` pour chargement conditionnel

✅ **Adapter `load_structured_data()`**
- Chargement conditionnel selon section
- Garder RPE/tarifs/écoles seulement si Enfance

### Phase 5 : Optimisation Performance

✅ **Créer `Backend/cache.py`**
- Module cache mémoire complet
- Dict Python avec TTL
- Fonctions get/set/clear

✅ **Intégrer cache dans `rag_assistant_endpoint()`**
- Vérifier cache avant recherche RAG
- Sauvegarder résultats dans cache

✅ **Optimiser recherche RAG**
- Réduire `top_k * 4` → `top_k * 2`
- Cache embeddings de requêtes fréquentes
- Optimiser schéma Whoosh

### Phase 6 : Documentation

✅ **Créer `docs/tutos/GUIDE_GENERALISATION_SITE.md`**
- Guide complet d'utilisation
- Exemples de configuration
- Dépannage

✅ **Mettre à jour `docs/references/strategies-scraping-generalisation.md`**
- Documenter toutes les stratégies
- Exemples d'utilisation

---

## ⚠️ Ce qui nécessite intervention manuelle

### Tests et Validation

❌ **Test de régression sur Enfance**
- Nécessite : Exécuter `crawl_site_generalized.py --section "Enfance"`
- Nécessite : Comparer résultats avec corpus actuel
- Nécessite : Validation que tout fonctionne

❌ **Test sur nouvelles sections**
- Nécessite : Activer section dans `site_sections.json`
- Nécessite : Crawler et vérifier qualité segments
- Nécessite : Tester recherche RAG sur questions

❌ **Test système RAG complet**
- Nécessite : Tester recherche hybride multi-sections
- Nécessite : Vérifier performance latence
- Nécessite : Validation qualité réponses

### Décisions et Configuration

❌ **Tester Claude Haiku vs Sonnet**
- Nécessite : Décision utilisateur (qualité vs rapidité)
- Nécessite : Tests comparatifs avec échantillon questions
- Nécessite : Validation que Haiku est acceptable

❌ **Activer sections dans `site_sections.json`**
- Nécessite : Décision utilisateur (quelles sections activer)
- Nécessite : Vérification que les URLs existent

❌ **Remplir lexiques multi-sections**
- Nécessite : Contenu spécifique par section
- Nécessite : Validation avec utilisateurs

### Déploiement

❌ **Déployer sur Railway**
- Nécessite : Credentials Railway
- Nécessite : Variables d'environnement
- Nécessite : Test en production

❌ **Régénérer embeddings en production**
- Nécessite : Upload nouveau corpus sur Railway
- Nécessite : Régénérer embeddings (peut être long)
- Nécessite : Redémarrer serveur

---

## 🚀 Plan d'Action Automatisable

### Ce que je peux faire maintenant (sans attendre)

1. ✅ Créer tous les fichiers de code (discover_urls.py, crawl_site_generalized.py, cache.py)
2. ✅ Créer fichiers de configuration (site_sections.json)
3. ✅ Modifier fichiers existants (rebuild_corpus.py, rag_assistant_server.py, embed_corpus.py)
4. ✅ Créer documentation complète
5. ✅ Généraliser scraping dynamique (crawl_dynamic.py)

### Ce qui nécessite votre validation après

1. ⚠️ Tester le crawl sur Enfance (vérifier régression)
2. ⚠️ Activer sections souhaitées dans `site_sections.json`
3. ⚠️ Tester Claude Haiku et décider
4. ⚠️ Valider qualité réponses multi-sections
5. ⚠️ Déployer sur Railway

---

## 💡 Recommandation

**Je peux lancer maintenant :**
- Tous les fichiers de code et configuration
- Toutes les modifications de code
- Toute la documentation

**Vous devrez ensuite :**
- Tester et valider
- Activer les sections souhaitées
- Décider Claude Haiku vs Sonnet
- Déployer sur Railway

**Souhaitez-vous que je commence par créer tous les fichiers automatiquement ?**

---

**Dernière mise à jour :** 2025-01-XX

