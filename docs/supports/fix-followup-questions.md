# Fix Questions de Suivi (Follow-up) - Format Utilisateur

## 🔴 Problème

Les questions de suivi générées par le modèle étaient formulées comme des questions d'assistant :
- ❌ "Je quel est votre quotient familial pour que je puisse vous indiquer le tarif exact qui s'applique à votre situation ?"
- ❌ "Souhaitez-vous connaître votre quotient familial ?"
- ❌ "Pouvez-vous me préciser le nombre de jours ?"

Alors qu'elles devraient être formulées comme des questions utilisateur directes :
- ✅ "Quel est mon quotient familial ?"
- ✅ "Combien de jours par semaine ?"
- ✅ "Où se trouve cette école ?"

## ✅ Solution Implémentée

### 1. Prompt Injection

**Fichier** : `rag_assistant_server.py` - `ASSISTANT_SYSTEM_PROMPT`

Ajout d'instructions explicites dans le prompt système :
```
IMPORTANT - Format des "follow_up_question" (ouvertures) :
Les questions de suivi doivent être formulées COMME UN UTILISATEUR les poserait, pas comme l'assistant.

Règles pour les ouvertures :
- Question courte et directe (max 10 mots)
- Formulation à la première personne (je/mon/mes/mon enfant)
- Pas de formules de politesse ("Souhaitez-vous", "Pouvez-vous", "Je souhaite")
- Pas de préfixe "Je " en début de phrase
- Utilise "mon/mes" au lieu de "votre/vos" quand pertinent
```

Avec des exemples concrets de ce qu'il faut faire et ne pas faire.

### 2. Post-Processing

**Fichier** : `rag_assistant_server.py` - `normalize_followup_question()`

Fonction de normalisation qui :
1. **Enlève les préfixes** : "Je ", "Souhaitez-vous", "Pouvez-vous", etc.
2. **Remplace les pronoms** : "votre/vos" → "mon/mes" quand pertinent
3. **Simplifie les phrases** : Enlève "pour que je puisse", "afin de", etc.
4. **Assure le format** : Ajoute "?" si manquant, limite à 80 caractères

**Transformations appliquées** :
- `"Je quel est votre quotient familial..."` → `"Quel est mon quotient familial ?"`
- `"Souhaitez-vous connaître..."` → `"Connaître mon quotient familial ?"`
- `"Pouvez-vous me préciser..."` → `"Préciser le nombre de jours ?"`

### 3. Application

La fonction est appliquée sur `follow_up_question` avant de retourner la réponse :
```python
raw_followup = result.get("follow_up_question")
normalized_followup = normalize_followup_question(raw_followup)
```

## 🧪 Tests

Exemples de transformations :
- Input: `"Je quel est votre quotient familial pour que je puisse vous indiquer le tarif exact ?"`
- Output: `"Quel est mon quotient familial ?"`

- Input: `"Souhaitez-vous connaître votre quotient familial ?"`
- Output: `"Connaître mon quotient familial ?"`

## 📝 Fichiers Modifiés

- `rag_assistant_server.py` :
  - `ASSISTANT_SYSTEM_PROMPT` : Ajout instructions sur les ouvertures
  - `normalize_followup_question()` : Nouvelle fonction de post-processing
  - `rag_assistant_endpoint()` : Application de la normalisation

## 🚀 Action Requise

**Relancer le serveur** pour appliquer les changements :
```bash
lsof -ti :8711 | xargs kill
python3 rag_assistant_server.py
```

## ✅ Résultat Attendu

Les questions de suivi seront maintenant :
- Formulées comme des questions utilisateur directes
- Courtes et simples
- À la première personne
- Sans formules de politesse

