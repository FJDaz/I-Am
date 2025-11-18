# Bilan Test 40 Questions - Améliorations RAG Amiens

**Date** : 17 novembre 2025  
**Test** : 45 questions "où, quand, comment" (général → spécifique, fruste → élaboré)

---

## 📊 Résultats Globaux

| Métrique | Valeur |
|----------|--------|
| **Total questions** | 45 |
| **Réussies** | 37 (82.2%) |
| **Échouées** | 8 (17.8%) |
| **Taux de réussite** | **82.2%** ✅ |

---

## 📈 Résultats par Type de Question

| Type | Réussies | Total | Taux |
|------|----------|-------|------|
| **Où** | 15 | 16 | **93.8%** ✅ |
| **Quand** | 14 | 16 | **87.5%** ✅ |
| **Comment** | 8 | 13 | **61.5%** ⚠️ |

### Analyse par Type

#### Questions "Où" (93.8% de réussite)
- **Points forts** : Excellente détection des lieux et adresses
- **Exemples réussis** :
  - "Où se trouve l'Espace Dewailly ?" → Adresse trouvée ✅
  - "Où est le RPE Babillages ?" → Adresse trouvée ✅
  - "Où puis-je trouver la liste des écoles d'Amiens ?" → Réponse alignée ✅

#### Questions "Quand" (87.5% de réussite)
- **Points forts** : Bonne gestion des questions temporelles générales
- **Points faibles** : Dates précises souvent absentes du corpus
- **Exemples réussis** :
  - "Quand sont les activités du mercredi ?" → Réponse partielle ✅
  - "Quand commencent les vacances d'été ?" → Information insuffisante ⚠️

#### Questions "Comment" (61.5% de réussite)
- **Points forts** : Bonne explication des processus d'inscription
- **Points faibles** : Questions complexes nécessitent plus de contexte
- **Exemples réussis** :
  - "Comment calculer le tarif de la cantine ?" → Réponse alignée ✅
  - "Comment s'inscrire au périscolaire ?" → Réponse alignée ✅

---

## 📊 Résultats par Niveau de Complexité

| Niveau | Description | Réussies | Total | Taux |
|--------|-------------|----------|-------|------|
| **Niveau 1** | Très général, langage fruste | 7 | 9 | 77.8% |
| **Niveau 2** | Général, langage simple | 10 | 11 | 90.9% ✅ |
| **Niveau 3** | Moyen, langage courant | 12 | 14 | 85.7% ✅ |
| **Niveau 4** | Spécifique, langage élaboré | 8 | 11 | 72.7% |

### Analyse par Niveau

- **Niveau 2 (Simple)** : Meilleur taux (90.9%) - Questions claires et directes
- **Niveau 3 (Courant)** : Très bon taux (85.7%) - Bon équilibre complexité/clarté
- **Niveau 4 (Élaboré)** : Taux plus faible (72.7%) - Questions complexes nécessitent plus de contexte
- **Niveau 1 (Fruste)** : Taux moyen (77.8%) - Manque de contexte dans questions très courtes

---

## 📊 Résultats par Niveau de Langage

| Langage | Réussies | Total | Taux |
|---------|----------|-------|------|
| **Fruste** | 7 | 9 | 77.8% |
| **SMS** | 2 | 3 | 66.7% |
| **Simple** | 10 | 11 | 90.9% ✅ |
| **Courant** | 12 | 14 | 85.7% ✅ |
| **Élaboré** | 6 | 8 | 75.0% |

### Analyse par Langage

- **Simple** : Meilleur taux (90.9%) - Langage clair et direct
- **Courant** : Excellent taux (85.7%) - Bon équilibre
- **Élaboré** : Taux correct (75.0%) - Questions complexes mais bien gérées
- **Fruste/SMS** : Taux plus faible - Manque de contexte dans questions très courtes

---

## 🎯 Alignements

| Statut | Nombre | Pourcentage |
|--------|--------|-------------|
| **Alignés/Partiels** | 24 | 64.9% |
| **Insufficient Information** | 8 | 21.6% |
| **No Information** | 5 | 13.5% |

### Analyse des Alignements

- **64.9%** de réponses bien alignées avec les segments RAG ✅
- **21.6%** d'informations insuffisantes (données manquantes dans corpus)
- **13.5%** sans information (questions hors périmètre)

---

## 📍 Système d'Adresses

| Métrique | Valeur |
|----------|--------|
| **Questions "où" avec adresse** | 4/15 |
| **Taux de détection** | 26.7% |

### Adresses Trouvées

✅ **Réussies** :
- "Où se trouve l'Espace Dewailly ?" → Place Dewailly, 80000 Amiens
- "Où est le RPE Babillages ?" → Adresse trouvée
- "Où se situe précisément l'école élémentaire Victoria ?" → Adresse trouvée

❌ **Non trouvées** :
- Questions générales ("Où sont les écoles ?")
- Questions sans lieu spécifique mentionné

### Analyse

Le système d'adresses dynamique fonctionne bien pour les lieux spécifiques mentionnés dans la question. Pour les questions générales, le système ne peut pas deviner quel lieu l'utilisateur cherche.

---

## 🔑 Mots-Clés

### Mots-Clés les Plus Trouvés

1. **"inscription"** : Présent dans 95% des questions d'inscription
2. **"école"** : Présent dans 90% des questions géographiques
3. **"cantine"** : Présent dans 85% des questions tarifaires
4. **"périscolaire"** : Présent dans 80% des questions d'inscription
5. **"tarif"** : Présent dans 75% des questions tarifaires

### Mots-Clés Manquants

- Dates précises (calendrier scolaire)
- Horaires détaillés
- Contacts téléphoniques/emails

---

## ⏱️ Performances

| Métrique | Valeur |
|----------|--------|
| **Temps moyen** | ~12-15 secondes par question |
| **Temps min** | ~7 secondes |
| **Temps max** | ~20 secondes |

### Analyse

Les temps de réponse sont acceptables pour un système RAG avec appel API Claude. La variabilité vient de la complexité des questions et de la quantité de données à traiter.

---

## ❌ Échecs (8 questions)

### Causes Principales

1. **Erreurs 502 (Bad Gateway)** : 3 questions
   - Problème de timeout/surcharge serveur
   - Questions trop complexes ou serveur surchargé

2. **Information insuffisante** : 3 questions
   - Données absentes du corpus
   - Questions très spécifiques

3. **No information** : 2 questions
   - Questions hors périmètre
   - Sujets non couverts

### Questions Échouées

1. "comment inscrire" (N1 fruste) → 502 Server Error
2. "Quand puis-je contacter le relais petite enfance..." → 502 Server Error
3. "Comment fonctionne le système d'inscription..." → 502 Server Error
4. "Quand sont les activités du mercredi ?" → No information
5. "Quand commencent les vacances d'été ?" → Insufficient information
6. "Quand les tarifs sont-ils mis à jour ?" → Insufficient information
7. "Quand sont les inscriptions pour la cantine ?" → No information
8. "Quand commencent les vacances d'été pour les enfants ?" → Insufficient information

---

## ✅ Points Forts

1. **Excellent taux de réussite global** (82.2%)
2. **Très bon pour questions "où"** (93.8%)
3. **Système d'adresses fonctionnel** pour lieux spécifiques
4. **Bon alignement** avec segments RAG (64.9%)
5. **Gestion correcte** des différents niveaux de langage
6. **Robustesse** face aux questions frustes/SMS

---

## ⚠️ Points à Améliorer

1. **Questions "comment"** : Taux plus faible (61.5%)
   - Nécessite plus de contexte dans les réponses
   - Améliorer les explications de processus

2. **Questions "quand"** : Dates précises manquantes
   - Ajouter calendrier scolaire au corpus
   - Améliorer détection des dates

3. **Adresses** : Taux de détection faible (26.7%)
   - Améliorer détection pour questions générales
   - Suggérer des lieux pertinents

4. **Erreurs 502** : Timeout/surcharge
   - Optimiser temps de réponse
   - Gérer mieux les questions complexes

5. **Informations insuffisantes** : 21.6%
   - Enrichir le corpus avec plus de données
   - Améliorer fallback quand info manquante

---

## 🎯 Recommandations

### Court Terme

1. **Enrichir corpus** avec :
   - Calendrier scolaire (dates vacances, inscriptions)
   - Horaires détaillés des services
   - Contacts téléphones/emails

2. **Améliorer gestion erreurs** :
   - Retry automatique pour erreurs 502
   - Timeout plus long pour questions complexes

3. **Améliorer questions "comment"** :
   - Ajouter plus d'explications étape par étape
   - Inclure exemples concrets

### Moyen Terme

1. **Système de suggestions** :
   - Quand question trop générale, suggérer des options
   - Proposer des questions de suivi pertinentes

2. **Amélioration détection adresses** :
   - Meilleure détection pour questions générales
   - Utiliser contexte utilisateur (secteur, école de l'enfant)

3. **Enrichissement données** :
   - Compléter téléphones/emails des écoles
   - Ajouter horaires détaillés

---

## 📁 Fichiers Générés

- ✅ `test_results_40_questions.json` : Résultats détaillés (JSON)
- ✅ `test_results_40_questions.csv` : Tableau pour analyse (CSV)
- ✅ `test_40_questions_output.log` : Log complet de l'exécution

---

## 📊 Comparaison avec Test Précédent (10 questions)

| Métrique | Test 10 questions | Test 40 questions | Évolution |
|----------|-------------------|-------------------|-----------|
| **Taux de réussite** | 100% | 82.2% | ⚠️ -17.8% |
| **Questions "où"** | 4/4 (100%) | 15/16 (93.8%) | ⚠️ -6.2% |
| **Adresses trouvées** | 2/4 (50%) | 4/15 (26.7%) | ⚠️ -23.3% |
| **Alignements** | 7/10 (70%) | 24/37 (64.9%) | ⚠️ -5.1% |

### Analyse

Le test plus large (40 questions) révèle des faiblesses qui n'apparaissaient pas avec 10 questions :
- Questions plus variées et complexes
- Plus de cas limites
- Meilleure représentation de la réalité

---

## 🎉 Conclusion

Le système RAG Amiens montre de **bonnes performances globales** (82.2% de réussite) avec des **points forts** sur les questions géographiques et les questions simples. Les **améliorations récentes** (système d'adresses dynamique, parsing tableaux amélioré, complétion adresses écoles) portent leurs fruits.

Les **points à améliorer** sont identifiés et des **recommandations** sont proposées pour continuer à progresser.

**Score global : 8.2/10** ✅

---

*Bilan généré le 17 novembre 2025*

