# Pistes pour Ouvertures Basées sur le RAG

## 🎯 Objectif

Faire en sorte que les questions d'ouverture (follow-up) soient des questions dont les réponses **figurent dans le RAG**, pour éviter les questions sans réponse.

## 🔍 Problème Actuel

Le modèle génère des ouvertures sans vérifier si la réponse existe dans le RAG, ce qui peut mener à :
- Questions sur des sujets non couverts
- Frustration utilisateur (pas de réponse)
- Perte de confiance

## 💡 Pistes de Solution

### Piste 1 : Prompt Injection avec Contraintes RAG (RECOMMANDÉ)

**Principe** : Modifier le prompt système pour demander explicitement des ouvertures basées sur le contenu disponible.

**Avantages** :
- Simple à implémenter
- Pas de changement d'architecture
- Le modèle peut analyser les segments RAG

**Implémentation** :
```
Dans ASSISTANT_SYSTEM_PROMPT, ajouter :

"Ouverture" : question de suivi formulée COMME UN UTILISATEUR la poserait.
IMPORTANT : La question d'ouverture DOIT porter sur un sujet dont la réponse 
est disponible dans les segments RAG fournis (#1, #2, #3) ou dans les données 
structurées.

Exemples d'ouvertures valides (réponse dans RAG) :
- "Quel est mon quotient familial ?" (si segments contiennent info tarifs)
- "Où se trouve l'Espace Dewailly ?" (si segments contiennent info lieux)
- "Comment s'inscrire au périscolaire ?" (si segments contiennent info inscription)

À ÉVITER : Questions sur des sujets absents des segments RAG.
```

### Piste 2 : Post-Processing avec Vérification RAG

**Principe** : Après génération de l'ouverture, vérifier qu'elle a une réponse dans le RAG.

**Avantages** :
- Garantit que la réponse existe
- Peut suggérer une alternative si pas de réponse

**Implémentation** :
```python
def validate_followup_has_rag_answer(followup_question: str, rag_results: List[RagSegment]) -> bool:
    """Vérifie si la question d'ouverture a une réponse dans le RAG."""
    if not followup_question or not rag_results:
        return False
    
    # Recherche rapide dans les segments RAG
    question_tokens = tokenize(followup_question)
    for segment in rag_results:
        content = (segment.content or "").lower()
        # Vérifier si les mots-clés de la question sont dans le segment
        matches = sum(1 for token in question_tokens if token in content)
        if matches >= len(question_tokens) * 0.5:  # Au moins 50% des mots
            return True
    return False

# Dans rag_assistant_endpoint, après normalisation :
if normalized_followup:
    if not validate_followup_has_rag_answer(normalized_followup, rag_results):
        # Générer une alternative ou supprimer l'ouverture
        normalized_followup = generate_alternative_followup(rag_results)
```

### Piste 3 : Génération Multiple + Sélection

**Principe** : Demander au modèle de générer plusieurs ouvertures, puis choisir celle avec le meilleur score RAG.

**Avantages** :
- Plusieurs options à choisir
- Meilleure qualité garantie

**Inconvénients** :
- Plus coûteux (plusieurs générations)
- Plus complexe

**Implémentation** :
```
Dans le prompt, demander :
"follow_up_questions": [
  "question 1",
  "question 2", 
  "question 3"
]

Puis scorer chaque question avec le RAG et choisir la meilleure.
```

### Piste 4 : Extraction de Questions depuis Segments RAG

**Principe** : Analyser les segments RAG pour extraire des questions implicites.

**Avantages** :
- Questions garanties d'avoir une réponse
- Basées sur le contenu réel

**Implémentation** :
```python
def extract_followup_from_rag(rag_results: List[RagSegment]) -> Optional[str]:
    """Extrait une question d'ouverture depuis les segments RAG."""
    # Analyser les segments pour trouver des informations partielles
    # Générer une question sur ce qui n'a pas été complètement couvert
    
    # Exemple : Si segment parle de tarifs mais pas de quotient familial
    # → Question : "Quel est mon quotient familial ?"
    
    # Exemple : Si segment parle d'inscription mais pas de documents
    # → Question : "Quels documents sont nécessaires ?"
```

### Piste 5 : Template de Questions Basées sur Données Structurées

**Principe** : Utiliser les données structurées pour générer des questions pertinentes.

**Avantages** :
- Questions garanties d'avoir une réponse
- Basées sur données fiables

**Implémentation** :
```python
def generate_followup_from_structured_data(
    question: str,
    rag_results: List[RagSegment],
    structured_data: Dict
) -> Optional[str]:
    """Génère une question d'ouverture basée sur données structurées."""
    
    # Si question sur tarifs → suggérer question quotient familial
    if "tarif" in question.lower():
        return "Quel est mon quotient familial ?"
    
    # Si question sur écoles → suggérer question secteur
    if "école" in question.lower():
        return "Dans quel secteur se trouve cette école ?"
    
    # Si question sur RPE → suggérer question contact
    if "rpe" in question.lower() or "relais" in question.lower():
        return "Quel est le contact de mon RPE ?"
```

## 🎯 Recommandation : Approche Hybride

**Combinaison Piste 1 + Piste 2** :

1. **Prompt Injection** (Piste 1) :
   - Modifier `ASSISTANT_SYSTEM_PROMPT` pour demander des ouvertures basées sur RAG
   - Le modèle génère déjà des ouvertures pertinentes

2. **Post-Processing Validation** (Piste 2) :
   - Vérifier que l'ouverture générée a une réponse dans le RAG
   - Si non, générer une alternative depuis les segments RAG

3. **Fallback Template** (Piste 5) :
   - Si validation échoue, utiliser des templates basés sur données structurées

## 📝 Implémentation Suggérée

### Étape 1 : Améliorer le Prompt

```python
ASSISTANT_SYSTEM_PROMPT = """
...
"Ouverture" : question de suivi formulée COMME UN UTILISATEUR la poserait.
CRITÈRE IMPORTANT : La question d'ouverture DOIT porter sur un sujet dont 
la réponse est disponible dans les segments RAG (#1, #2, #3) ou dans les 
données structurées fournies.

Analyse les segments RAG pour identifier :
- Informations partielles qui méritent un approfondissement
- Sujets connexes mentionnés mais non détaillés
- Données structurées disponibles (tarifs, lieux, RPE, écoles)

Exemples d'ouvertures valides :
- Si segments parlent de tarifs → "Quel est mon quotient familial ?"
- Si segments parlent de lieux → "Où se trouve [lieu mentionné] ?"
- Si segments parlent d'inscription → "Quels documents sont nécessaires ?"

À ÉVITER : Questions sur des sujets absents des segments RAG.
"""
```

### Étape 2 : Ajouter Validation

```python
def validate_and_fix_followup(
    followup: Optional[str],
    rag_results: List[RagSegment],
    structured_data: Dict
) -> Optional[str]:
    """Valide et corrige la question d'ouverture."""
    if not followup:
        return None
    
    # Vérifier si la question a une réponse dans le RAG
    if has_rag_answer(followup, rag_results):
        return followup
    
    # Sinon, générer une alternative depuis les segments
    return generate_alternative_from_rag(rag_results, structured_data)
```

### Étape 3 : Génération Alternative

```python
def generate_alternative_from_rag(
    rag_results: List[RagSegment],
    structured_data: Dict
) -> Optional[str]:
    """Génère une question d'ouverture alternative depuis le RAG."""
    
    # Analyser les segments pour trouver des sujets partiels
    topics = extract_partial_topics(rag_results)
    
    # Mapper vers questions pertinentes
    if "tarif" in topics and "quotient" not in topics:
        return "Quel est mon quotient familial ?"
    
    if "lieu" in topics:
        return "Où se trouve ce lieu ?"
    
    # Fallback : question générique basée sur données structurées
    if structured_data.get("tarifs"):
        return "Quels sont les tarifs détaillés ?"
    
    return None
```

## 🧪 Test

Créer un test qui vérifie que les ouvertures générées ont bien une réponse dans le RAG :
- Tester avec différentes questions
- Vérifier que les ouvertures sont pertinentes
- Vérifier que les réponses existent dans le RAG

## 📊 Métriques de Succès

- **Taux d'ouvertures avec réponse RAG** : > 90%
- **Pertinence des ouvertures** : Questions logiques de suivi
- **Satisfaction utilisateur** : Les ouvertures mènent à des réponses utiles

