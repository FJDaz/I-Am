# 🚀 Guide : Généraliser I-Amiens à Tout le Site

**Objectif :** Utiliser toutes les stratégies de scraping pour crawler toutes les sections d'amiens.fr

---

## 📋 Résumé des Stratégies Disponibles

### ✅ Stratégies Implémentées

1. **Push-Blocks (H2 → URLs)** 
   - Extrait les H2 dans `.push-block__inner`
   - Convertit en slug et construit des URLs
   - **Fichier :** `tools/discover_urls.py` → `discover_push_blocks()`

2. **Liens Internes**
   - Suit tous les `<a href>` sur la page
   - Filtre par domaine et pattern
   - **Fichier :** `tools/discover_urls.py` → `discover_internal_links()`

3. **Navigation**
   - Extrait les liens des menus de navigation
   - **Fichier :** `tools/discover_urls.py` → `discover_from_navigation()`

4. **Sitemap.xml**
   - Parse le sitemap.xml du site
   - **Fichier :** `tools/discover_urls.py` → `discover_from_sitemap()`

5. **Scraping Dynamique (Playwright)**
   - Clique sur "voir +" et accordéons
   - Extrait le contenu caché
   - **Fichier :** `ML/scripts/crawl_dynamic.py` (généralisé depuis Audit_Scrap_enfance.py)

---

## 🎯 Utilisation Rapide

### Étape 1 : Configurer les Sections

Éditer `ML/data/site_sections.json` pour activer les sections souhaitées :

```json
{
  "sections": [
    {
      "name": "Enfance",
      "enabled": true,  // ← Activer cette section
      "priority": 1
    },
    {
      "name": "Jeunesse",
      "enabled": true,  // ← Activer cette section
      "priority": 2
    }
  ]
}
```

### Étape 2 : Lancer le Crawl

#### Option A : Crawler une section spécifique

```bash
cd "I Amiens"
python tools/crawl_site_generalized.py --section "Enfance"
```

#### Option B : Crawler toutes les sections activées

```bash
python tools/crawl_site_generalized.py --all
```

#### Option C : Scraping dynamique (Playwright)

```bash
python ML/scripts/crawl_dynamic.py
```

#### Option D : Tester la découverte d'URLs seulement

```bash
python tools/discover_urls.py
```

### Étape 3 : Régénérer les Embeddings

Après avoir crawlé de nouvelles sections, régénérer les embeddings :

```bash
# Avec corpus généralisé
python ML/embed_corpus.py --generalized

# Ou sans flag (détection automatique)
python ML/embed_corpus.py
```

---

## 📊 Exemple de Sortie

```
🚀 Démarrage du crawl généralisé

============================================================
🔍 Crawling section: Enfance
   URL: https://www.amiens.fr/Vivre-a-Amiens/Enfance
   Pattern: /Enfance
   Catégories: tarifs, centres_loisirs, inscriptions, menus, rpe
============================================================

📄 [1/200] https://www.amiens.fr/Vivre-a-Amiens/Enfance
   ✅ 3 segments extraits
   🔗 Push-blocks: 5 URLs découvertes
   🔗 Liens internes: 12 URLs découvertes
   🔗 Navigation: 8 URLs découvertes

📄 [2/200] https://www.amiens.fr/Vivre-a-Amiens/Enfance/Centres-de-loisirs
   ✅ 2 segments extraits
   ...

✅ Section Enfance: 45 segments au total

✅ Corpus sauvegardé: ML/data/corpus_metadata_generalized.json
   45 segments au total
```

---

## 🔧 Personnalisation

### Modifier les Paramètres

Éditer `ML/data/site_sections.json` → section `settings` :

```json
{
  "settings": {
    "max_pages_per_section": 200,      // Nombre max de pages par section
    "delay_between_requests": 1.0,     // Délai entre requêtes (secondes)
    "respect_robots_txt": true,        // Respecter robots.txt
    "use_sitemap": true,               // Utiliser sitemap.xml
    "use_dynamic_scraping": false      // Scraping Playwright (lent)
  }
}
```

### Ajouter une Nouvelle Section

Ajouter dans `ML/data/site_sections.json` :

```json
{
  "name": "Nouvelle Section",
  "base_url": "https://www.amiens.fr/Vivre-a-Amiens/Nouvelle-Section",
  "pattern": "/Nouvelle-Section",
  "categories": ["categorie1", "categorie2"],
  "enabled": true,
  "priority": 8
}
```

### Configurer Claude Haiku (plus rapide)

Dans `Backend/rag_assistant_server.py` ou via variable d'environnement :

```bash
# .env ou Railway
CLAUDE_MODEL=claude-3-5-haiku-20241022  # Plus rapide (0.5-1.5s)
# ou
CLAUDE_MODEL=claude-3-7-sonnet-20250219  # Meilleure qualité (1-3s)
```

---

## 🐛 Dépannage

### Erreur : "Fichier de configuration non trouvé"

```bash
# Vérifier que le fichier existe
ls ML/data/site_sections.json

# Si absent, créer depuis le template
cp ML/data/site_sections.json.example ML/data/site_sections.json
```

### Erreur : "Impossible de récupérer [URL]"

- Vérifier la connexion internet
- Vérifier que l'URL existe (ouvrir dans navigateur)
- Vérifier `robots.txt` (peut bloquer certaines URLs)

### Trop d'URLs découvertes

- Réduire `max_pages_per_section` dans `settings`
- Ajouter un filtre plus strict dans `pattern`

### Cache ne fonctionne pas

- Vérifier que `Backend/cache.py` existe
- Vérifier les logs : `[CACHE HIT]` devrait apparaître pour questions répétées
- Vérifier stats : `cache_stats()` dans le code

### Embeddings non trouvés

- Vérifier que `corpus_embeddings_generalized.npy` existe (si corpus généralisé)
- Sinon vérifier `corpus_embeddings.npy` (corpus standard)
- Régénérer : `python ML/embed_corpus.py --generalized`

---

## 📚 Documentation Complète

Pour plus de détails sur les stratégies, voir :
- `docs/references/strategies-scraping-generalisation.md`
- `docs/references/PLAN_ACTION_COMPLET.md`
- `docs/references/AUTOMATISABLE_VS_MANUEL.md`

---

## ✅ Checklist de Généralisation

- [x] Module `discover_urls.py` créé
- [x] Script `crawl_site_generalized.py` créé
- [x] Configuration `site_sections.json` créée
- [x] Scraping dynamique généralisé (`crawl_dynamic.py`)
- [x] Support corpus généralisé dans `embed_corpus.py`
- [x] Cache mémoire créé (`Backend/cache.py`)
- [x] Prompt système généralisé
- [x] Support Claude Haiku
- [x] Optimisations recherche RAG
- [ ] Tester sur section Enfance (régression)
- [ ] Tester sur section Jeunesse
- [ ] Généraliser `Audit_Scrap_enfance.py` pour scraping dynamique
- [ ] Documenter les nouvelles URLs découvertes
- [ ] Mettre à jour le corpus RAG avec nouvelles sections

---

## 🎯 Prochaines Étapes

1. **Tester le crawl sur Enfance** (vérifier régression)
2. **Activer section Jeunesse** dans `site_sections.json`
3. **Crawler et régénérer embeddings**
4. **Tester recherche RAG** sur questions multi-sections
5. **Tester Claude Haiku** vs Sonnet (décider)
6. **Déployer sur Railway**

---

**Dernière mise à jour :** 2025-01-XX
