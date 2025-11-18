# Solution Erreur SSL - Extension Chrome

## 🔴 Problème Identifié

L'erreur `ERR_CERT_AUTHORITY_INVALID` vient du fait que :
1. L'extension essaie d'accéder à `https://localhost:8711`
2. Le serveur utilise un certificat SSL auto-signé
3. Chrome bloque les certificats auto-signés depuis les extensions

## ✅ Corrections Appliquées

### 1. Changement de l'endpoint dans content.js

**Fichier** : `chrome-extension-v2/content.js`

```javascript
// ❌ Avant (causait l'erreur)
const ASSISTANT_ENDPOINT = "https://localhost:8711/rag-assistant";

// ✅ Après (corrigé)
const ASSISTANT_ENDPOINT = "http://localhost:8711/rag-assistant";
```

### 2. Manifest.json déjà correct

Les permissions incluent déjà HTTP :
```json
"host_permissions": [
  "http://localhost:8711/*",
  "https://localhost:8711/*"
]
```

## 🔧 Action Requise : Relancer le Serveur en HTTP

Le serveur tourne actuellement en **HTTPS** (avec certificats SSL). Pour que l'extension fonctionne, il faut le relancer en **HTTP**.

### Option 1 : Relancer sans SSL (Recommandé)

1. **Arrêter le serveur actuel** :
   ```bash
   # Trouver le processus
   lsof -i :8711
   # Tuer le processus (remplacer PID)
   kill <PID>
   ```

2. **Relancer en HTTP** :
   ```bash
   cd "I Amiens"
   python3 rag_assistant_server.py
   ```
   
   Le serveur détectera automatiquement l'absence de certificats et lancera en HTTP.

### Option 2 : Supprimer temporairement les certificats

```bash
cd "I Amiens"
mv localhost-key.pem localhost-key.pem.bak
mv localhost-cert.pem localhost-cert.pem.bak
python3 rag_assistant_server.py
```

### Option 3 : Utiliser HTTPS avec certificat valide (Complexe)

Si vous voulez absolument HTTPS :
1. Générer un certificat valide pour localhost
2. L'ajouter aux certificats de confiance de Chrome
3. Configurer le serveur pour l'utiliser

**Mais pour le développement local, HTTP est plus simple.**

## 🧪 Vérification

Après avoir relancé le serveur en HTTP :

1. **Vérifier que le serveur répond en HTTP** :
   ```bash
   curl http://localhost:8711/rag-assistant -X POST \
     -H "Content-Type: application/json" \
     -d '{"question":"test"}'
   ```

2. **Recharger l'extension** :
   - Aller sur `chrome://extensions`
   - Cliquer "Recharger" pour l'extension

3. **Tester sur amiens.fr** :
   - Aller sur `https://www.amiens.fr`
   - Cliquer sur "Assistant Enfance Amiens"
   - Poser une question

## 📝 Résumé

- ✅ Extension corrigée : utilise maintenant `http://` au lieu de `https://`
- ⏳ Action requise : Relancer le serveur en HTTP (sans SSL)
- ✅ Manifest.json : Permissions HTTP déjà présentes

Une fois le serveur relancé en HTTP, l'extension devrait fonctionner sans erreur SSL.

