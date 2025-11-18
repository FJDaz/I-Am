# Test Simulation Historique - Crash Serveur

## 🎯 Objectif

Simuler une conversation avec historique qui s'accumule pour :
1. **Évaluer l'hypothèse** : Le crash est-il lié à l'historique ?
2. **Identifier le seuil critique** : Combien de tours d'historique avant le crash ?
3. **Mesurer les limites** : Taille des tokens, temps de réponse, etc.

## 🚀 Utilisation

```bash
# Test avec 10 requêtes (par défaut)
python3 tests/test_historique_crash.py

# Test avec un nombre spécifique de requêtes
python3 tests/test_historique_crash.py 15
```

## 📊 Ce que le script mesure

1. **Historique total** : Nombre de tours accumulés
2. **Historique utilisé** : Nombre de tours réellement utilisés (limité à 12 dans le code)
3. **Tokens estimés** :
   - Tokens d'historique
   - Tokens du prompt final (système + historique + question + RAG)
4. **Temps de réponse** : Pour chaque requête
5. **Erreurs** : Type et moment où elles surviennent

## 🔍 Hypothèses testées

### Hypothèse 1 : Limite d'historique
- Le code limite à `conversation[-12:]` (12 tours)
- Mais l'historique total continue de s'accumuler
- **Test** : Vérifier si le crash survient même avec la limite

### Hypothèse 2 : Limite de tokens
- Claude a une limite de tokens d'entrée (200k pour Claude 3.7 Sonnet)
- Le prompt peut dépasser cette limite si l'historique est trop long
- **Test** : Estimer la taille du prompt et vérifier si on approche la limite

### Hypothèse 3 : Accumulation mémoire
- L'historique s'accumule dans la mémoire du serveur
- Peut causer un problème de mémoire après plusieurs requêtes
- **Test** : Vérifier si le crash survient après un certain nombre de requêtes

## 📈 Résultats attendus

Le script génère :
- **Affichage en temps réel** : Progression de la simulation
- **Résumé final** : Statistiques et seuil critique identifié
- **Fichier JSON** : `tests/test_historique_results.json` avec tous les détails

## 🎯 Interprétation des résultats

### Si crash après N requêtes :
- **Seuil critique identifié** : N tours d'historique
- **Tokens au moment du crash** : Taille du prompt qui cause le problème
- **Action** : Limiter l'historique à N-1 tours ou réduire la taille des messages

### Si pas de crash :
- L'hypothèse historique est **fausse**
- Le problème vient d'ailleurs (mémoire, autre erreur, etc.)
- **Action** : Investiguer d'autres causes

## 🔧 Améliorations possibles

- Ajouter mesure de mémoire réelle (psutil)
- Tester avec différentes tailles de réponses
- Tester avec différents types de questions
- Mesurer la taille réelle du prompt envoyé à Claude (si accessible)

