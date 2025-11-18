# Explication : Qu'est-ce qu'un Segment RAG ?

## 🎯 Définition Simple

Un **segment RAG** est un **extrait de texte** extrait du corpus de documents (site web, PDFs, etc.) qui est **pertinent** pour répondre à la question de l'utilisateur.

## 📚 Analogie

Imagine que vous avez une **bibliothèque** avec des milliers de livres sur "Amiens Enfance". Quand quelqu'un vous pose une question, vous ne lisez pas tous les livres. Vous :
1. **Cherchez** dans l'index les pages pertinentes
2. **Extrayez** les passages qui parlent du sujet
3. **Utilisez** ces passages pour répondre

Les **segments RAG** sont ces passages extraits.

## 🔍 Comment ça fonctionne ?

### 1. **Indexation du Corpus**
- Tous les documents du site Amiens.fr sont **indexés** (découpés en petits morceaux)
- Chaque morceau devient un **segment** avec :
  - Un **contenu** (le texte)
  - Un **titre/label** (d'où vient le texte)
  - Une **URL** (lien vers la source)
  - Des **métadonnées** (type de document, date, etc.)

### 2. **Recherche Sémantique**
Quand l'utilisateur pose une question :
- Le système **cherche** dans l'index les segments les plus pertinents
- Utilise la **similarité sémantique** (comprend le sens, pas juste les mots)
- Retourne les **top 5 segments** les plus pertinents

### 3. **Utilisation dans la Réponse**
Les segments sont :
- **Numérotés** (#1, #2, #3, etc.)
- **Inclus dans le prompt** envoyé à Claude
- **Utilisés par Claude** pour construire la réponse
- **Cités** dans les sources de la réponse

## 📊 Structure d'un Segment

```python
RagSegment(
  label="Tarifs cantine 2024-2025",      # Titre du document
  url="https://www.amiens.fr/tarifs",     # Lien vers la source
  score=0.85,                             # Score de pertinence (0-1)
  excerpt="Les tarifs de la cantine...",  # Extrait court (400 caractères)
  content="Contenu complet du segment..." # Contenu complet
)
```

## 🎯 Exemple Concret

**Question utilisateur** : "Quels sont les tarifs de la cantine ?"

**Segments RAG trouvés** :
- **#1** : "Tarifs cantine 2024-2025" (score: 0.92)
  - Extrait : "Les tarifs de la cantine varient selon le quotient familial..."
  - URL : https://www.amiens.fr/tarifs-cantine
  
- **#2** : "Inscription cantine" (score: 0.78)
  - Extrait : "Pour inscrire votre enfant à la cantine..."
  - URL : https://www.amiens.fr/inscription-cantine

- **#3** : "Horaires cantine" (score: 0.65)
  - Extrait : "La cantine est ouverte de 11h30 à 13h30..."
  - URL : https://www.amiens.fr/horaires-cantine

**Claude utilise ces segments** pour construire sa réponse en citant les sources.

## 🔧 Pourquoi des Segments ?

### Avantages :
1. **Précision** : Répond uniquement avec le contenu pertinent
2. **Traçabilité** : Chaque réponse peut citer ses sources
3. **Efficacité** : Pas besoin de lire tout le corpus
4. **Mise à jour** : Si un document change, les segments sont mis à jour

### Limitations :
1. **Dépend du corpus** : Si l'info n'est pas dans les documents, pas de réponse
2. **Qualité de l'indexation** : Si les segments sont mal découpés, moins bonnes réponses
3. **Score de pertinence** : Parfois des segments peu pertinents sont inclus

## 📝 Dans le Code

### Où sont créés les segments ?
- **Recherche sémantique** : `semantic_search()` trouve les segments pertinents
- **Recherche lexicale** : `whoosh_index` (recherche par mots-clés)
- **Combinaison** : Les deux méthodes sont combinées pour meilleur résultat

### Comment sont utilisés ?
1. **Recherche** : `semantic_search(question, lexicon_matches, top_k=5)`
2. **Scoring** : Chaque segment a un score de pertinence
3. **Tri** : Segments triés par score décroissant
4. **Injection** : Inclus dans le prompt envoyé à Claude
5. **Citation** : Sources citées dans la réponse finale

## 🎯 En Résumé

**Segments RAG = Extraits pertinents du corpus pour répondre à la question**

- **Entrée** : Question utilisateur
- **Traitement** : Recherche dans l'index → Extraction segments pertinents
- **Sortie** : Top 5 segments avec scores, utilisés par Claude pour répondre

C'est le **cœur du système RAG** : au lieu de tout lire, on extrait juste ce qui est pertinent !

