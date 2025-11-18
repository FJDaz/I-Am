# Guide de Dépannage - Extension Chrome

## 🔍 Diagnostic

Un script de diagnostic est disponible :
```bash
cd chrome-extension-v2
node diagnostic.js
```

## ✅ Vérifications de Base

### 1. Fichiers Présents
- ✅ `manifest.json`
- ✅ `content.js`
- ✅ `data/corpus_segments.json`
- ✅ `data/lexique_enfance.json`
- ✅ `data/questions_usager.json`

### 2. Serveur Backend
Le serveur doit tourner sur `https://localhost:8711/rag-assistant`

Vérifier :
```bash
curl -k https://localhost:8711/rag-assistant -X POST \
  -H "Content-Type: application/json" \
  -d '{"question":"test"}'
```

### 3. Installation Extension

1. Ouvrir Chrome → `chrome://extensions`
2. Activer "Mode développeur"
3. Cliquer "Charger l'extension non empaquetée"
4. Sélectionner le dossier `chrome-extension-v2`

## ⚠️ Problèmes Courants

### Extension ne s'affiche pas sur amiens.fr

**Cause** : L'extension ne se charge que sur `https://www.amiens.fr/*`

**Solution** :
- Vérifier que vous êtes bien sur `https://www.amiens.fr` (pas `http://`)
- Recharger la page (F5)
- Vérifier la console (F12) pour erreurs

### Erreur "Backend inaccessible"

**Cause** : Le serveur ne tourne pas ou n'est pas accessible

**Solution** :
1. Vérifier que le serveur tourne :
   ```bash
   lsof -i :8711
   ```

2. Démarrer le serveur si nécessaire :
   ```bash
   cd "I Amiens"
   python3 rag_assistant_server.py
   ```

3. Vérifier les permissions dans `manifest.json` :
   ```json
   "host_permissions": [
     "http://localhost:8711/*",
     "https://localhost:8711/*"
   ]
   ```

### Erreur "Impossible de charger le corpus local"

**Cause** : Fichiers JSON non accessibles

**Solution** :
1. Vérifier que les fichiers existent dans `data/`
2. Vérifier `web_accessible_resources` dans `manifest.json`
3. Recharger l'extension dans `chrome://extensions`

### Extension ne répond pas

**Cause** : Erreur JavaScript dans `content.js`

**Solution** :
1. Ouvrir la console (F12)
2. Vérifier les erreurs JavaScript
3. Vérifier l'onglet "Console" pour messages d'erreur
4. Vérifier l'onglet "Network" pour requêtes échouées

## 🔧 Corrections Appliquées

### Manifest.json
- ✅ Ajout de `questions_usager.json` dans `web_accessible_resources`

## 📊 Statistiques

Les statistiques de l'extension sont dans :
- `chrome-extension-v2/data/corpus_segments.json` : 1506 segments
- `chrome-extension-v2/data/lexique_enfance.json` : 36 entrées
- `chrome-extension-v2/data/questions_usager.json` : 17 questions

## 🧪 Test Manuel

1. Aller sur `https://www.amiens.fr`
2. Cliquer sur le bouton "Assistant Enfance Amiens" (en bas à droite)
3. Poser une question : "Où se trouve l'Espace Dewailly ?"
4. Vérifier que la réponse s'affiche

## 📝 Logs

Pour déboguer, ouvrir la console (F12) et vérifier :
- Messages d'erreur
- Requêtes réseau vers `localhost:8711`
- Erreurs de chargement de fichiers

## 🆘 Support

Si le problème persiste :
1. Exécuter `node diagnostic.js`
2. Noter les erreurs dans la console
3. Vérifier que le serveur répond correctement

