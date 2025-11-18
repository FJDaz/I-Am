# Analyse Crash Frontend vs Backend

## 🔍 Problème Identifié

Le test backend fonctionne (10 requêtes OK), mais l'extension Chrome crash après 2-3 requêtes.

## 📊 Différences Clés

### Backend Test
- ✅ Historique limité à ce qui est envoyé (10 tours max dans le test)
- ✅ Pas de segments RAG volumineux
- ✅ Pas de `instructions` (PROMPT_INJECTION)
- ✅ Payload JSON simple et contrôlé

### Extension Chrome
- ⚠️ **Historique peut aller jusqu'à 60 tours** (`history.length > 60`)
- ⚠️ **Envoie TOUT l'historique** : `conversation: history` (ligne 1512)
- ⚠️ **Envoie segments RAG** : `rag_results: ragPayload` (peut être volumineux)
- ⚠️ **Envoie PROMPT_INJECTION** : `instructions: PROMPT_INJECTION` (long texte)
- ⚠️ **Historique contient du HTML** : même si `stripHtml()` est utilisé, peut rester du contenu volumineux

## 🎯 Hypothèses du Crash

### Hypothèse 1 : Taille du Payload JSON
L'extension envoie un payload JSON énorme :
- 60 tours d'historique × ~100-200 tokens = 6000-12000 tokens
- Segments RAG (3 segments × ~200 tokens) = 600 tokens
- PROMPT_INJECTION = ~500 tokens
- **Total estimé : 7000-13000 tokens dans le payload**

Même si le serveur ne prend que `conversation[-12:]`, il doit d'abord :
1. **Parser tout le JSON** (peut être lent/coûteux)
2. **Charger en mémoire** tout l'historique
3. **Extraire les 12 derniers tours**

### Hypothèse 2 : Accumulation Mémoire
- L'historique s'accumule dans `history` (jusqu'à 60 tours)
- Chaque tour contient du contenu HTML nettoyé mais peut être long
- Le serveur reçoit tout, même s'il ne prend que 12 tours
- **Mémoire saturée** après quelques requêtes

### Hypothèse 3 : Parsing JSON Lent
- JSON.stringify() d'un historique de 60 tours peut être lent
- Le serveur doit parser un JSON énorme
- **Timeout ou crash** si le parsing prend trop de temps

## 🔧 Solutions Proposées

### Solution 1 : Limiter l'historique côté Extension (RECOMMANDÉ)
```javascript
// Dans callAssistant(), avant d'envoyer :
const limitedHistory = history.slice(-12); // Limiter à 12 tours comme le serveur

const body = {
  question,
  normalized_question: normalizedQuestion,
  rag_results: ragPayload,
  conversation: limitedHistory, // ← Limiter ici
  instructions: PROMPT_INJECTION,
  intent_label: intentLabel,
  intent_weight: intentWeight,
};
```

### Solution 2 : Nettoyer l'historique plus agressivement
```javascript
function pushHistory(role, content) {
  const cleaned = stripHtml(content);
  if (!cleaned) return;
  
  // Limiter la taille du contenu
  const maxLength = 500; // Limiter à 500 caractères
  const truncated = cleaned.length > maxLength 
    ? cleaned.substring(0, maxLength) + "..." 
    : cleaned;
  
  history.push({ role, content: truncated });
  if (history.length > 12) { // Limiter à 12 au lieu de 60
    history = history.slice(-12);
  }
}
```

### Solution 3 : Ne pas envoyer PROMPT_INJECTION
Le serveur a déjà son propre prompt système. L'extension n'a pas besoin d'envoyer `instructions`.

## 🧪 Test à Faire

Créer un test qui simule exactement ce que l'extension envoie :
- Historique de 60 tours
- Segments RAG volumineux
- PROMPT_INJECTION
- Vérifier la taille du payload JSON

## 📝 Action Immédiate

**Modifier `content.js` ligne 1512** pour limiter l'historique avant l'envoi :
```javascript
conversation: history.slice(-12), // Limiter à 12 tours
```

