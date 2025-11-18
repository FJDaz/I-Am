# Prompt d'Action - Améliorations RAG Amiens

## 🎯 Objectif
Améliorer le système RAG pour répondre aux 10 tests en enrichissant les sources et améliorant les heuristiques.

## 📋 Contexte Clé

### Sources Identifiées

1. **PDF tarifs complet** : `syn+tarif+2024+2025+pour+contrat (1).pdf`
   - ✅ Contient TOUS les tarifs (ALSH, cantine, périscolaire)
   - ⚠️ Gros travail RAG : extraction tableaux structurés
   - Déjà dans corpus mais besoin extraction fine

2. **PDF liste ALSH été** : `LISTE+ALSH+ETE+2025.pdf`
   - Liste centres ouverts + adresses
   - Déjà traité dans corpus

3. **Carte interactive écoles** : `https://geo.amiens-metropole.com/adws/app/523da8c6-5dbc-11ec-9790-3dc5639e7001/index.html`
   - ⚠️ À VÉRIFIER : API peut-être accessible (pas confirmé fermée)
   - Contient secteurs + données écoles
   - Fichier JS fourni mais utilité incertaine

4. **Endpoint autocomplete** : `proxy="/autocomplete/get-datas/(node)/3169"`
   - Donne école > horaires périscolaires
   - POC si commande

### Stratégies Validées

- **Adresses** : Site → OSM → Google Maps (fallback)
- **Écoles** : OSM (Overpass) + scraping site pour contacts
- **Tarifs** : Extraction tableaux depuis PDF
- **Cache** : Sauvegarder toutes adresses dans `data/lieux_cache.json`

---

## ✅ Todo List

### Phase 1 : Extraction Tableaux Tarifs (URGENT - Test 2)
- [ ] Vérifier contenu PDF tarifs dans corpus
- [ ] Créer `tools/extract_tarif_tables.py`
- [ ] Extraire tous tableaux (pdfplumber/camelot)
- [ ] Formater en JSON structuré
- [ ] Créer `data/tarifs_2024_2025.json`
- [ ] Injecter dans prompt quand question tarifaire

### Phase 2 : Vérifier API Carte (IMPORTANT - Test 3)
- [ ] Tester accès API carte (requêtes réseau)
- [ ] Analyser fichier JS fourni (vide actuellement)
- [ ] Si accessible : scraper données écoles + secteurs
- [ ] Si fermée : passer à OSM

### Phase 3 : OSM pour Écoles (IMPORTANT - Test 3)
- [ ] Implémenter requête Overpass fournie
- [ ] Récupérer écoles avec adresses/coordonnées
- [ ] Combiner avec données site (contacts si possible)
- [ ] Créer `data/ecoles_amiens.json`
- [ ] Mapping secteur → écoles

### Phase 4 : Système Adresses Dynamique (Test 5)
- [ ] Créer `tools/address_fetcher.py`
- [ ] Implémenter : Site → OSM → Google Maps
- [ ] Créer `data/lieux_cache.json`
- [ ] Intégrer dans `build_prompt()` pour injection auto

### Phase 5 : Endpoint Périscolaire (Test 3 - POC)
- [ ] Analyser JS page "Avant-Après l'école"
- [ ] Intercepter requêtes réseau (DevTools)
- [ ] Reverse engineer endpoint si possible
- [ ] Implémenter scraper (POC)

### Phase 6 : Amélioration Heuristiques
- [ ] Remplacer détection RPE par lexique
- [ ] Améliorer détection lieux (plus précise)
- [ ] Ajouter vérification pertinence avant injection

---

## 🚀 Commencer par

1. **Vérifier API carte** (rapide, débloque Test 3)
2. **Extraire tableaux tarifs** (impact fort Test 2)
3. **Implémenter OSM** (débloque Test 3, 5)
