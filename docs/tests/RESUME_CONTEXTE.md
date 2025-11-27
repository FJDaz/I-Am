# Résumé de Contexte - Améliorations RAG Amiens

## 📋 Contexte Général

Travail sur l'amélioration du système RAG pour répondre aux 10 tests identifiés. L'objectif est d'enrichir les sources de données et d'améliorer les heuristiques pour fournir des réponses plus précises et complètes.

---

## ✅ Ce Qui A Été Fait

### 1. Extraction Tableaux Tarifs ✅
- **Module créé** : `tools/extract_tarif_tables.py`
- **Fichier généré** : `data/tarifs_2024_2025.json`
- **Résultat** : 5 tableaux extraits (2 cantine, 3 autres)
- **Intégration** : ✅ Injecté dans `build_prompt()` quand question tarifaire
- **Status** : Fonctionnel mais format HTML peut être amélioré

### 2. Récupération Écoles OSM ✅
- **Module créé** : `tools/fetch_osm_schools.py`
- **Fichier généré** : `data/ecoles_amiens.json`
- **Résultat** : 255 écoles avec coordonnées + secteurs approximatifs
- **Intégration** : ✅ Injecté dans `build_prompt()` quand question écoles
- **Status** : Fonctionnel mais adresses partielles, contacts manquants

### 3. Système Adresses Dynamique ✅
- **Module créé** : `tools/address_fetcher.py`
- **Fichier cache** : `data/lieux_cache.json` (auto-créé)
- **Stratégie** : Site → OSM Nominatim → Google Maps (fallback non implémenté)
- **Test** : ✅ Fonctionne (Espace Dewailly trouvé)
- **Status** : Module créé mais **PAS ENCORE INTÉGRÉ** dans `build_prompt()`

### 4. Amélioration Heuristiques ✅
- **RPE** : ✅ Utilise maintenant `match_lexicon_entries()` au lieu de liste en dur
- **Lieux** : ✅ Détection plus précise (lieu mentionné ET question géographique)
- **Tarifs** : ✅ Détection élargie avec plus de termes
- **Écoles** : ✅ Nouvelle détection ajoutée

### 5. Vérification API Carte ⚠️
- **Module créé** : `tools/check_carte_api.py`
- **Problème** : Erreur SSL (certificat)
- **Status** : Script créé mais non fonctionnel (problème SSL)

### 6. Chargement Données Structurées ✅
- **Intégration** : ✅ `load_structured_data()` charge maintenant :
  - RPE (`rpe_contacts.json`)
  - Lieux (`lieux_importants.json`)
  - Tarifs (`tarifs_2024_2025.json`) ← **NOUVEAU**
  - Écoles (`ecoles_amiens.json`) ← **NOUVEAU**

---

## ⏳ Ce Qui Reste À Faire (TODO List)

### ✅ Complété
- [x] Vérifier si API carte interactive est accessible
- [x] Extraire tableaux tarifs depuis PDF syn+tarif
- [x] Implémenter requête OSM Overpass pour récupérer écoles Amiens
- [x] Créer système adresses dynamique (Site → OSM → Google Maps) avec cache
- [x] Améliorer heuristiques RPE (utiliser lexique au lieu de liste en dur)

### ⏳ En Attente

#### Priorité 1 : Intégration Système Adresses ✅
- [x] **Intégrer `address_fetcher.py` dans `build_prompt()`** ✅ COMPLÉTÉ
  - Quand un lieu est mentionné mais pas d'adresse dans segments RAG
  - Appeler `get_address_for_lieu()` automatiquement
  - Injecter l'adresse dans les données structurées
  - **Améliorations ajoutées** :
    - Détection automatique des lieux mentionnés (pas seulement "Espace Dewailly")
    - Recherche d'adresse dans segments RAG en premier
    - Fallback automatique vers OSM via `address_fetcher`
    - Injection dans données structurées du prompt

#### Priorité 2 : Amélioration Extraction Tableaux ✅
- [x] **Améliorer parsing tableaux tarifs** ✅ COMPLÉTÉ
  - Colonnes parfois mélangées dans HTML
  - Utiliser `camelot` ou améliorer `pdfplumber` parsing
  - Format plus propre pour injection
  - **Améliorations ajoutées** :
    - Fonction `split_mixed_cell()` pour séparer valeurs mélangées
    - Correction automatique nombres séparés par espaces ("2 4,77 €" → "24,77 €")
    - Stratégies d'extraction multiples (pdfplumber)
    - Post-traitement pour améliorer structure des tableaux
    - Formatage HTML amélioré avec normalisation colonnes

#### Priorité 3 : Compléter Données Écoles ✅
- [x] **Récupérer adresses complètes via Nominatim** ✅ COMPLÉTÉ
  - Parcourir les 255 écoles
  - Compléter adresses manquantes
  - Sauvegarder dans `ecoles_amiens.json`
  - **Script créé** : `tools/complete_school_addresses.py`
    - Reverse geocoding via Nominatim (coordonnées → adresse)
    - Rate limiting respecté (1 req/s)
    - Support test avec limite d'écoles
  - **Résultats** : 204/229 adresses complétées (89% de réussite)
    - 25 écoles sans adresse (coordonnées peut-être imprécises ou hors Amiens)

#### Priorité 4 : Endpoint Périscolaire (POC)
- [ ] **Investiguer endpoint autocomplete**
  - Analyser JS page "Avant-Après l'école"
  - Intercepter requêtes réseau (DevTools)
  - Reverse engineer si possible
  - **Note** : POC si commande

#### Priorité 5 : Améliorations Complémentaires
- [ ] **Mapping secteur → RPE**
  - Fonction pour déterminer RPE selon secteur utilisateur
  - Utiliser dans `follow_up_question`
- [ ] **Tester serveur avec nouvelles données intégrées**
  - Vérifier chargement au démarrage
  - Tester injection conditionnelle

#### ✅ Résolu - Crash Serveur
- [x] **Corriger crash serveur après 2-3 requêtes** ✅ COMPLÉTÉ
  - **Problème identifié** : Historique conversation trop volumineux (60 tours avec contenu complet)
  - **Solution appliquée** :
    - Limitation historique à 12 tours côté extension
    - Truncation contenu à 500 caractères par tour
    - Gestion d'erreurs améliorée dans `rag_assistant_endpoint()`
    - Timeout Claude API réduit (60s → 30s)
  - **Status** : Serveur stable maintenant

---

## 📊 État des Données

| Donnée | Fichier | Éléments | Intégration | Status |
|--------|---------|----------|--------------|--------|
| RPE | `data/rpe_contacts.json` | 5 RPE | ✅ | OK |
| Lieux | `data/lieux_importants.json` | 1 lieu | ✅ | OK |
| Tarifs | `data/tarifs_2024_2025.json` | 5 tableaux | ✅ | ⚠️ Format à améliorer |
| Écoles | `data/ecoles_amiens.json` | 255 écoles | ✅ | ✅ 204/255 adresses complétées (80%) |
| Cache adresses | `data/lieux_cache.json` | Auto | ✅ | ✅ Intégré |

---

## 🎯 Impact sur les Tests

| Test | Status | Action Restante |
|------|--------|-----------------|
| Test 1 (Liste RPE) | ✅ Résolu | Aucune |
| Test 2 (Tableaux tarifs) | ⚠️ Partiel | Améliorer format HTML |
| Test 3 (Liste écoles) | ⚠️ Partiel | Adresses complétées (80%), téléphones/emails à ajouter |
| Test 5 (Adresses) | ✅ Résolu | Intégration `address_fetcher` complétée |
| Test 6 (Mapping secteur→RPE) | ❌ Non fait | Créer fonction mapping |
| Test 7 (Tarifs ALSH été) | ✅ Résolu | Aucune |
| Test 8 (Activités vacances) | ❌ Non fait | Améliorer lexique |
| Test 9 & 10 (DRE, PAI) | ❌ Non fait | Mapping questions→dispositifs |

---

## 🔧 Modules Créés

1. ✅ `tools/extract_tarif_tables.py` - Extraction tableaux PDF (amélioré)
2. ✅ `tools/fetch_osm_schools.py` - Récupération écoles OSM
3. ✅ `tools/address_fetcher.py` - Système adresses dynamique
4. ✅ `tools/complete_school_addresses.py` - Complétion adresses écoles
5. ✅ `tools/resume_contexte_manager.py` - Gestion automatique RESUME_CONTEXTE.md
6. ✅ `tools/archive_old_docs.py` - Archivage automatique documentation
7. ⚠️ `tools/check_carte_api.py` - Vérification API (problème SSL)
8. ✅ `tests/test_integration.py` - Script de test d'intégration

---

## 📝 Fichiers de Documentation

### Documentation Technique
- ✅ `docs/references/methode-meta-skills.md` - Méthode méta pour créer des skills
- ✅ `docs/references/prompt-generateur-skills.md` - Prompt pour générer des skills
- ✅ `docs/references/segments-rag.md` - Explication des segments RAG
- ✅ `docs/references/optimisation-latence.md` - Optimisations de performance

### Guides et Tutos
- ✅ `docs/tutos/deploiement-mvp.md` - Guide déploiement Railway
- ✅ `docs/tutos/utiliser-extension-railway.md` - Guide utilisation extension avec Railway
- ✅ `docs/tutos/fixer-auto-deploy-railway.md` - Fix déploiement automatique
- ✅ `docs/tutos/retirer-secret-git.md` - Retirer secrets de Git
- ✅ `docs/tutos/securite-url-github.md` - Sécurité URL GitHub

### Documentation Tests (ancienne structure)
- ✅ `tests/docs/PROMPT_ACTION.md` - Plan d'action initial
- ✅ `tests/docs/RETOUR_TOUR_SITE.md` - Analyse commentaires utilisateur
- ✅ `tests/docs/RESULTATS_IMPLÉMENTATION.md` - Résultats détaillés
- ✅ `tests/docs/BILAN_IMPLÉMENTATION.md` - Bilan complet
- ✅ `tests/docs/RESUME_CONTEXTE.md` - Ce document

---

## 🚀 Prochaines Actions Immédiates

1. ✅ **Intégrer `address_fetcher` dans `build_prompt()`** - COMPLÉTÉ
   - Appel automatique quand lieu mentionné sans adresse
   - Injection dans données structurées

2. **Tester le serveur avec nouvelles données**
   - Vérifier chargement au démarrage
   - Tester injection conditionnelle

3. **Améliorer format tableaux**
   - Parser plus fin des colonnes
   - HTML plus propre

---



## 🔄 Dernières Mises à Jour

**2025-11-18** :
- ✅ **Optimisation déploiement Railway** :
  - Retrait `sentence-transformers` et `torch` de `requirements.txt` (allègement Docker : 5 Go → 200 Mo)
  - Build Railway réussi (103 secondes, vs timeout avant)
  - Recherche sémantique désactivée (Whoosh BM25 seul, suffisant pour MVP)
  - Code adapté pour fonctionner sans embeddings (gestion gracieuse)
- ✅ **Extension Chrome améliorée** :
  - Logo IAM ajouté dans le header (`statics/img/IAM_logo.png`)
  - CSS h1 amélioré (font-size 1.7rem, couleur cue, Open Sans ExtraBold)
  - Font-weight optimisé (seul header h1 et submit button en bold)
  - Import Google Fonts ajouté pour Open Sans weight 800
- ✅ **Méthode méta skills créée** :
  - `docs/references/methode-meta-skills.md` : Structure complète des skills
  - `docs/references/prompt-generateur-skills.md` : Prompt pour générer des skills
  - Section ajoutée : Fonctionnement résumé contexte systématique + architecture documentation
  - Précision : **Cursor** (l'IA) invoque automatiquement les skills
- ✅ **Architecture documentation** :
  - Structure `docs/` créée dans bergsonAndFriends (même architecture que I Amiens)
  - 23 fichiers .md classés dans bergsonAndFriends (notes, tutos, supports, references)
  - README mis à jour dans les deux projets
- ✅ **Documentation déploiement** :
  - `docs/tutos/utiliser-extension-railway.md` : Guide utilisation extension avec Railway
  - `docs/tutos/fixer-auto-deploy-railway.md` : Guide fix déploiement automatique

**2025-11-17 23:30** :
- ✅ Prompt injection + post-processing pour questions de suivi (follow-up)
  - Instructions ajoutées dans `ASSISTANT_SYSTEM_PROMPT` pour générer questions utilisateur
  - Fonction `normalize_followup_question()` créée pour post-processing
  - Transformations : "Je quel est votre..." → "Quel est mon quotient familial ?"
- ✅ **Crash serveur résolu** :
  - Problème : Historique conversation trop volumineux (60 tours → 12 tours)
  - Solution : Limitation historique côté extension + truncation contenu
  - Serveur stable maintenant

## ⚠️ Points d'Attention

1. **Google Maps** : Non implémenté (nécessite clé API)
2. **API carte** : Problème SSL non résolu
3. **Endpoint périscolaire** : Mystère, nécessite investigation manuelle
4. **Format tableaux** : Peut être amélioré pour meilleure lisibilité
5. ✅ **Crash Serveur** : RÉSOLU
   - **Problème** : Historique conversation trop volumineux
   - **Solution** : Limitation historique (12 tours) + truncation contenu (500 chars)
   - **Status** : Serveur stable
6. **Déploiement Railway** : ✅ Fonctionnel
   - Build réussi (103 secondes)
   - Image Docker allégée (200 Mo vs 5 Go)
   - Recherche Whoosh uniquement (suffisant pour MVP)

---

## 📌 Notes Importantes

- **PDF tarifs** : Contient TOUS les tarifs (ALSH, cantine, périscolaire) - source majeure
- **OSM** : Fonctionne bien pour écoles, alternative à API carte
- **Cache adresses** : Système prêt mais pas encore utilisé automatiquement
- **Heuristiques** : Améliorées mais peuvent encore être affinées

