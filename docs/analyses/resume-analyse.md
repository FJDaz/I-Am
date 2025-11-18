# Résumé de l'Analyse - État des Lieux RAG

## ✅ Ce que j'ai TROUVÉ et IMPLÉMENTÉ

### 1. Données structurées créées
- ✅ `data/rpe_contacts.json` : Liste complète des 5 RPE avec contacts
- ✅ `data/lieux_importants.json` : Espace Dewailly avec adresse
- ✅ Fonction `load_structured_data()` : Chargement au démarrage

### 2. Injection dans le prompt
- ✅ Heuristique détection RPE (ligne 563) : Injecte liste RPE si question pertinente
- ✅ Heuristique détection lieux (ligne 571) : Injecte adresse si mention d'un lieu
- ✅ Prompt système mis à jour : Mentionne données structurées

### 3. Heuristiques existantes identifiées
- ✅ Recherche hybride BM25 (1.0) + Cosine (0.6)
- ✅ Stemmer français (Snowball)
- ✅ Boost lexical (lexique)
- ✅ Bonus monétaire (currency)
- ✅ Détection d'intention
- ✅ Extraction snippet utilisateur

---

## ⚠️ PROBLÈMES d'Heuristiques Identifiés

### 1. Détection RPE (ligne 563)
**Problème** : Liste de termes en dur, fragile
```python
any(term in question_text for term in ["rpe", "relais", "crèche", ...])
```
- Risque faux positifs/négatifs
- Pas de normalisation
- Non extensible

**Impact** : Peut injecter données RPE pour questions non pertinentes

### 2. Détection lieux (ligne 571)
**Problème** : "où" et "adresse" trop génériques
```python
any(term in question_text for term in ["espace dewailly", "dewailly", "adresse", "où", "localisation"])
```
- "où" → faux positifs
- Pas de vérification que le lieu est mentionné

**Impact** : Injection inutile pour questions génériques

---

## ❌ Ce qui MANQUE (à faire par toi)

### Test 2 : Tableaux tarifs en dur
- ❌ Extraction automatique tableaux depuis segments
- ❌ Détection questions tarifaires
- ❌ Formatage tableau HTML

### Test 3 : Sources établissements/contacts
- ❌ Recherche élargie pages contacts
- ❌ Question suivi "Quel est votre secteur ?"
- ❌ Mapping secteur → contact

### Test 4 : Recherche hors site
- ❌ Base connaissances génériques
- ❌ Détection info manquante
- ❌ Recherche complémentaire externe

### Test 6 : Mapping secteur→RPE
- ⚠️ Données RPE disponibles mais pas de fonction mapping
- ❌ Génération question suivi contextuelle
- ❌ Utilisation dans `follow_up_question`

### Test 7 : Recherche PDFs
- ❌ Indexation PDFs `data/raw/`
- ❌ Recherche "tarif été", "ALSH été"

### Test 8 : Multi-terminologie
- ⚠️ Lexique existe mais incomplet
- ❌ Synonymes : "activités" = "CLSH" = "centres de loisirs"
- ❌ Recherche cross-rubriques

### Test 9 & 10 : Mapping questions→dispositifs
- ❌ "difficultés scolaires" → DRE
- ❌ "allergie", "trouble santé" → PAI

---

## 🔧 Améliorations Heuristiques Nécessaires

### Pour chaque heuristique ajoutée :
1. **Remplacer détection RPE** : Utiliser lexique + intention au lieu de liste en dur
2. **Améliorer détection lieux** : Combinaison (mention_lieu AND question_géographique)
3. **Ajouter vérification pertinence** : Score avant injection
4. **Gérer contradictions** : Priorité données structurées vs RAG ?

---

## 📋 Fichiers Créés

1. `ANALYSE_HEURISTIQUES.md` : Analyse complète de toutes les heuristiques
2. `AMELIORATIONS_RAG.md` : Plan d'amélioration par test
3. `data/rpe_contacts.json` : Données RPE structurées
4. `data/lieux_importants.json` : Données lieux

---

## 🎯 Prochaines Étapes

1. **Toi** : Implémenter les manquants (Tests 2, 3, 4, 6, 7, 8, 9, 10)
2. **Moi** : Améliorer heuristiques existantes (RPE, lieux) si tu veux
3. **Ensemble** : Tester et ajuster selon résultats

---

## ⚡ Points d'Attention

- **Chaque heuristique ajoutée** doit être documentée et testée
- **Faux positifs** : Risque d'injecter données non pertinentes
- **Faux négatifs** : Risque de rater des cas pertinents
- **Performance** : Vérifier impact sur temps de réponse

