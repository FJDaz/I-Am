# Fix Erreur SSL - ERR_CERT_AUTHORITY_INVALID

## 🔴 Problème

L'extension Chrome essaie d'accéder à `https://localhost:8711` mais le certificat SSL n'est pas valide (auto-signé), ce qui cause l'erreur :
```
Failed to load resource: net::ERR_CERT_AUTHORITY_INVALID
TypeError: Failed to fetch
```

## ✅ Solution Appliquée

**Changement de l'endpoint de `https://` à `http://`** dans `content.js` :

```javascript
// Avant
const ASSISTANT_ENDPOINT = "https://localhost:8711/rag-assistant";

// Après
const ASSISTANT_ENDPOINT = "http://localhost:8711/rag-assistant";
```

## 🔧 Vérifications

### 1. Vérifier que le serveur accepte HTTP

Le serveur doit être lancé **sans SSL** pour accepter les requêtes HTTP :

```bash
# Vérifier comment le serveur tourne
lsof -i :8711

# Si lancé avec SSL, relancer sans SSL :
python3 rag_assistant_server.py
```

### 2. Vérifier les permissions dans manifest.json

Le manifest doit inclure les permissions HTTP ET HTTPS :

```json
"host_permissions": [
  "http://localhost:8711/*",
  "https://localhost:8711/*"
]
```

### 3. Recharger l'extension

1. Aller sur `chrome://extensions`
2. Cliquer sur "Recharger" pour l'extension
3. Recharger la page `https://www.amiens.fr`

## 🧪 Test

Après correction, tester dans la console :

```javascript
fetch('http://localhost:8711/rag-assistant', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({question: 'test'})
})
.then(r => r.json())
.then(console.log)
.catch(console.error)
```

## ⚠️ Alternative : Utiliser HTTPS avec certificat valide

Si vous voulez absolument utiliser HTTPS :

1. Générer un certificat valide pour localhost
2. L'ajouter aux certificats de confiance de Chrome
3. Configurer le serveur pour utiliser ce certificat

Mais pour le développement local, **HTTP est plus simple et suffisant**.

## 📝 Notes

- Les extensions Chrome sont strictes sur les certificats SSL
- Les certificats auto-signés ne sont pas acceptés par défaut
- HTTP sur localhost est sécurisé pour le développement local
- En production, utiliser HTTPS avec certificat valide

