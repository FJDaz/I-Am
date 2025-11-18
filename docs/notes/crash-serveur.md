# ⚠️ NOTE POUR DEMAIN - Crash Serveur

## 🔴 Problème Identifié

Le serveur crash après **2 ou 3 requêtes** successives.

**Hypothèse** : Problème lié à la gestion de l'**historique de conversation**.

## 🔍 À Investiguer

1. **Gestion de l'historique** :
   - Vérifier comment `conversation` est géré dans `rag_assistant_endpoint()`
   - Vérifier la limite de `conversation[-12:]` 
   - Vérifier la taille des messages dans l'historique

2. **Mémoire** :
   - Vérifier si l'historique s'accumule et cause un problème de mémoire
   - Vérifier les limites de tokens dans les appels API Claude

3. **Erreurs non capturées** :
   - Vérifier les logs du serveur pour voir l'erreur exacte
   - Vérifier si toutes les exceptions sont bien capturées dans le try/except

## 📝 Actions à Faire

1. **Ajouter des logs détaillés** pour identifier où ça crash
2. **Limiter la taille de l'historique** plus strictement
3. **Vérifier la gestion des erreurs** dans `call_model()` et `rag_assistant_endpoint()`
4. **Tester avec plusieurs requêtes successives** pour reproduire le crash

## 🔧 Fichiers à Vérifier

- `rag_assistant_server.py` :
  - Fonction `rag_assistant_endpoint()` (gestion conversation)
  - Fonction `call_model()` (gestion erreurs API)
  - Limite de tokens dans les appels Claude

## 📅 Date

Créé le : 17 novembre 2025

