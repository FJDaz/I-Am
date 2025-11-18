# Analyse des Heuristiques du Système RAG

## 🔍 État des Lieux - Ce qui EXISTE

### 1. Heuristiques de Recherche Sémantique

#### ✅ Recherche hybride BM25 + Cosine Similarity
- **Localisation** : `semantic_search()` ligne 663
- **Poids actuels** :
  - BM25 : `score * 1.0` (ligne 639)
  - Cosine : `score * 0.6` (ligne 666)
- **Paramètres** :
  - `top_k = 5` par défaut
  - `min_score = 0.2` pour cosine
  - `top_k * 4` candidats récupérés avant ranking final
- **Stemmer français** : Snowball (ligne 637)
- **Impact** : Bonne couverture, mais peut manquer des résultats si terminologie différente

#### ✅ Boost lexical (lexique)
- **Localisation** : `apply_lexicon_bonus()` ligne 472
- **Fonctionnement** :
  - Match termes usager → termes admin
  - Bonus de score selon poids du lexique
  - Normalisation des termes avant matching
- **Fichier** : `chrome-extension-v2/data/lexique_enfance.json`
- **Impact** : Améliore la correspondance terminologie usager/admin

#### ✅ Détection d'intention
- **Localisation** : `detect_user_intention()` ligne 529
- **Fonctionnement** :
  - Keywords matching sur intentions prédéfinies
  - Retourne label + poids
- **Limite** : Liste fixe d'intentions, pas de détection contextuelle avancée

### 2. Heuristiques de Scoring

#### ✅ Bonus monétaire (currency)
- **Localisation** : `apply_currency_bonus()` ligne 418
- **Fonctionnement** :
  - Détecte keywords monétaires ("tarif", "prix", "€", "garderie")
  - Boost segments contenant ces termes
  - Bonus : `CURRENCY_BONUS = 0.15`
- **Impact** : Priorise les segments tarifaires pour questions monétaires

#### ✅ Extraction snippet utilisateur
- **Localisation** : `extract_user_snippet()` ligne 500
- **Fonctionnement** :
  - Détecte tableaux/listes dans la question
  - Heuristiques : `|`, `\t`, `€`, `•`, `-`, `*`
  - Minimum 2 chiffres requis
  - Max 40 lignes, 1200 caractères
- **Impact** : Permet d'utiliser données fournies par l'utilisateur

### 3. Heuristiques d'Injection de Données Structurées (NOUVEAU)

#### ⚠️ Détection RPE (ligne 563)
```python
if rpe_data and any(term in question_text for term in ["rpe", "relais", "crèche", "inscription", "inscrire", "babillages", "germaine", "pigeon", "chemin des plantes"]):
```
- **Problème** : Liste de termes en dur, pas extensible
- **Impact** : Peut rater des variations ("relais petite enfance", "inscription en crèche municipale")
- **Amélioration nécessaire** : Utiliser le lexique ou détection sémantique

#### ⚠️ Détection lieux (ligne 571)
```python
if lieux_data and any(term in question_text for term in ["espace dewailly", "dewailly", "adresse", "où", "localisation"]):
```
- **Problème** : "où" et "adresse" sont trop génériques → risque de faux positifs
- **Impact** : Peut injecter données lieux pour des questions non pertinentes
- **Amélioration nécessaire** : Détection plus précise (combinaison lieu + question géographique)

### 4. Heuristiques de Requête (RAW_QUERY_HINTS)

#### ✅ Hints de requête (ligne 354)
- **Fonctionnement** : Mapping terme → suggestions de recherche
- **Exemples** :
  - "tarifs" → ["Synthese tarif 2024 2025", "tarifs centre de loisirs"]
  - "inscription" → ["inscriptions scolaires", "mairie de secteur"]
- **Limite** : Pas utilisé actuellement dans le code (à vérifier)

---

## ❌ Ce qui MANQUE (selon les tests)

### Test 1 : Liste RPE en dur
- **Status** : ✅ Fichier créé (`data/rpe_contacts.json`)
- **Status** : ⚠️ Injection ajoutée mais heuristique fragile
- **Manque** : 
  - Vérification que la liste est bien formatée dans la réponse
  - Gestion des cas où plusieurs RPE sont pertinents

### Test 2 : Tableau tarifs en dur
- **Status** : ❌ Pas implémenté
- **Manque** :
  - Extraction automatique de tableaux depuis segments RAG
  - Détection de questions tarifaires
  - Formatage tableau HTML/Markdown

### Test 3 : Sources établissements/contacts
- **Status** : ❌ Pas implémenté
- **Manque** :
  - Recherche élargie pour pages contacts
  - Question de suivi intelligente "Quel est votre secteur ?"
  - Mapping secteur → contact

### Test 4 : Recherche hors site (infos génériques)
- **Status** : ❌ Pas implémenté
- **Manque** :
  - Module de base de connaissances génériques
  - Détection quand info manque sur site
  - Recherche complémentaire externe

### Test 5 : Adresse Espace Dewailly
- **Status** : ⚠️ Fichier créé mais heuristique fragile
- **Manque** :
  - Recherche automatique si adresse absente
  - Géolocalisation/API externe
  - Vérification présence dans segments avant injection

### Test 6 : Question suivi secteur + RPE
- **Status** : ⚠️ Données RPE disponibles mais pas de mapping secteur→RPE
- **Manque** :
  - Fonction de mapping secteur → RPE
  - Génération question de suivi contextuelle
  - Utilisation dans `follow_up_question`

### Test 7 : Tarifs ALSH été (recherche approfondie)
- **Status** : ❌ Pas implémenté
- **Manque** :
  - Recherche dans PDFs (`data/raw/`)
  - Indexation PDFs
  - Recherche "tarif été", "vacances été", "ALSH été"

### Test 8 : Multi-terminologie (activités = CLSH)
- **Status** : ⚠️ Lexique existe mais incomplet
- **Manque** :
  - Synonymes dans lexique : "activités" = "CLSH" = "centres de loisirs"
  - Recherche cross-rubriques (sports + enfance)
  - Expansion de requête automatique

### Test 9 & 10 : Mapping questions → dispositifs (DRE, PAI)
- **Status** : ❌ Pas implémenté
- **Manque** :
  - Mapping questions utilisateur → dispositifs
  - Détection : "difficultés scolaires" → DRE
  - Détection : "allergie", "trouble santé" → PAI

---

## ⚠️ Problèmes d'Heuristiques Identifiés

### 1. Heuristique d'injection RPE (ligne 563)
**Problème** :
- Liste de termes en dur, non extensible
- Pas de normalisation (accents, pluriels)
- Risque de faux positifs/négatifs

**Impact système** :
- Peut injecter données RPE pour questions non pertinentes
- Peut rater des questions pertinentes avec terminologie différente

**Amélioration nécessaire** :
```python
# Au lieu de :
any(term in question_text for term in ["rpe", "relais", ...])

# Utiliser :
- Lexique pour matching normalisé
- Détection d'intention "inscription_crèche"
- Score de pertinence avant injection
```

### 2. Heuristique détection lieux (ligne 571)
**Problème** :
- "où" et "adresse" trop génériques
- Pas de vérification que le lieu est mentionné

**Impact système** :
- Faux positifs : toute question avec "où" → injection lieux
- Pas de précision sur quel lieu

**Amélioration nécessaire** :
```python
# Détection plus précise :
- Combinaison : (mention_lieu AND question_géographique)
- Vérifier présence du lieu dans segments RAG
- Score de pertinence
```

### 3. Pas de gestion des cas limites
**Problèmes** :
- Que faire si données structurées + segments RAG se contredisent ?
- Priorité : données structurées ou RAG ?
- Comment gérer plusieurs lieux/RPE pertinents ?

---

## 📋 Plan d'Action - Ce qui reste à faire

### Phase 1 : Améliorer heuristiques existantes
1. ✅ Remplacer détection RPE par matching lexique + intention
2. ✅ Améliorer détection lieux (plus précise)
3. ✅ Ajouter vérification pertinence avant injection

### Phase 2 : Implémenter manquants critiques
4. ❌ Extraction tableaux tarifs (Test 2)
5. ❌ Recherche contacts/établissements (Test 3)
6. ❌ Mapping secteur→RPE + question suivi (Test 6)
7. ❌ Multi-terminologie dans lexique (Test 8)

### Phase 3 : Fonctionnalités avancées
8. ❌ Recherche PDFs (Test 7)
9. ❌ Mapping questions→dispositifs (Test 9, 10)
10. ❌ Base connaissances génériques (Test 4)

### Phase 4 : Robustesse
11. ❌ Gestion contradictions données structurées vs RAG
12. ❌ Tests unitaires pour chaque heuristique
13. ❌ Logging/monitoring des heuristiques

---

## 🔧 Modifications Système Nécessaires

### Pour chaque nouvelle heuristique :
1. **Documenter** : Quoi, pourquoi, quand
2. **Tester** : Cas limites, faux positifs/négatifs
3. **Paramétrer** : Seuils, poids ajustables
4. **Monitorer** : Logs, métriques d'efficacité

### Architecture proposée :
```
build_prompt()
  ├─ detect_context() → détermine quel contexte (RPE, tarifs, lieux, etc.)
  ├─ should_inject_structured_data() → vérifie pertinence
  ├─ format_structured_data() → formate pour prompt
  └─ inject_if_relevant() → injection conditionnelle
```

---

## 📊 Métriques à Suivre

Pour chaque heuristique, mesurer :
- **Précision** : % de cas où injection était pertinente
- **Rappel** : % de cas pertinents où injection a eu lieu
- **Impact** : Amélioration qualité réponse (score utilisateur)

---

## 🎯 Priorités Immédiates

1. **Améliorer heuristiques existantes** (RPE, lieux) - risque de faux positifs
2. **Implémenter Test 2** (tableaux tarifs) - impact fort utilisateur
3. **Implémenter Test 6** (mapping secteur→RPE) - améliore UX
4. **Implémenter Test 8** (multi-terminologie) - améliore couverture

