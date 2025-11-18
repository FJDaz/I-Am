# Fix Erreur 500 - Serveur

## 🔴 Problème

Erreur 500 (Internal Server Error) après les modifications d'indentation.

## ✅ Correction Appliquée

**Problème** : Erreur d'indentation dans la création de `RagSegment` pour la contribution utilisateur.

**Fichier** : `rag_assistant_server.py` ligne 985

**Correction** :
```python
# ❌ Avant (mauvaise indentation)
RagSegment(
  label="Contribution utilisateur",
score=max_score + CURRENCY_BONUS,  # ← Pas aligné
...

# ✅ Après (corrigé)
RagSegment(
  label="Contribution utilisateur",
  score=max_score + CURRENCY_BONUS,  # ← Aligné
  ...
)
```

## 🔧 Action Requise

**Le serveur doit être relancé** pour appliquer les corrections :

```bash
# Option 1 : Script automatique
./RELOAD_SERVER.sh

# Option 2 : Manuel
lsof -ti :8711 | xargs kill
python3 rag_assistant_server.py
```

## 🧪 Vérification

Après relance, tester :
```bash
curl http://localhost:8711/rag-assistant -X POST \
  -H "Content-Type: application/json" \
  -d '{"question":"test","rag_results":[],"conversation":[]}'
```

Devrait retourner une réponse JSON valide (pas d'erreur 500).

## ✅ Status

- ✅ Syntaxe Python corrigée
- ✅ Indentation corrigée
- ⏳ Serveur à relancer pour appliquer les changements

