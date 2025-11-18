# 🚀 Utiliser l'Extension Chrome avec Railway

## 📋 Prérequis

1. ✅ Serveur Railway déployé et fonctionnel
2. ✅ Extension Chrome installée localement
3. ✅ URL Railway obtenue

---

## 🔧 Étape 1 : Obtenir l'URL Railway

1. Va sur [railway.app](https://railway.app) → Ton projet
2. **Settings** → **Networking**
3. **Generate Domain** (ou utilise le domaine par défaut)
4. **Copie l'URL** : `https://ton-projet.up.railway.app`

**Exemple** : `https://i-am-production.up.railway.app`

---

## 🔧 Étape 2 : Mettre à Jour l'Extension

### Option A : Détection Automatique (Recommandé)

L'extension a déjà une détection automatique dans `content.js` (lignes 12-14) :

```javascript
const ASSISTANT_ENDPOINT = window.location.hostname === 'localhost'
  ? "http://localhost:8711/rag-assistant"
  : "https://i-am-production.up.railway.app/rag-assistant";
```

**Si ton URL Railway est différente**, modifie la ligne 14 :

```javascript
const ASSISTANT_ENDPOINT = window.location.hostname === 'localhost'
  ? "http://localhost:8711/rag-assistant"
  : "https://TON-URL-RAILWAY.up.railway.app/rag-assistant";
```

### Option B : Forcer l'URL Railway

Si tu veux toujours utiliser Railway (même en local), remplace par :

```javascript
const ASSISTANT_ENDPOINT = "https://TON-URL-RAILWAY.up.railway.app/rag-assistant";
```

---

## 🔧 Étape 3 : Vérifier CORS sur Railway

L'extension doit pouvoir appeler Railway depuis `https://www.amiens.fr`.

**Vérifie dans `rag_assistant_server.py`** (lignes ~970-980) :

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8711",
        "https://localhost:8711",
        "https://www.amiens.fr",  # ✅ Doit être présent
        os.environ.get("ALLOWED_ORIGIN", ""),  # Variable d'env optionnelle
    ],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"]
)
```

**Si besoin, ajoute une variable d'environnement sur Railway** :
- Key: `ALLOWED_ORIGIN`
- Value: `https://www.amiens.fr`

---

## 🔧 Étape 4 : Recharger l'Extension

1. Va sur `chrome://extensions/`
2. Trouve l'extension "Amiens Assistant" (ou le nom que tu lui as donné)
3. Clique sur **🔄 Recharger** (icône de rafraîchissement)
4. **OU** désactive puis réactive l'extension

---

## 🧪 Étape 5 : Tester

1. Va sur **https://www.amiens.fr**
2. Clique sur le bouton de l'assistant (coin inférieur droit)
3. Pose une question test : **"Quels sont les tarifs de la cantine ?"**
4. Vérifie que la réponse arrive

### ✅ Si ça fonctionne :
- Tu verras la réponse de l'assistant
- Les logs Railway montreront la requête

### ❌ Si ça ne fonctionne pas :

#### Erreur CORS :
```
Access to fetch at 'https://...' from origin 'https://www.amiens.fr' has been blocked by CORS policy
```
**Solution** : Vérifie que `https://www.amiens.fr` est dans `allow_origins` sur Railway

#### Erreur 502/500 :
```
Assistant cloud inaccessible après 3 tentatives
```
**Solution** : 
- Vérifie les logs Railway (Deployments → View Logs)
- Vérifie que `ANTHROPIC_API_KEY` est bien définie
- Vérifie que le serveur est bien démarré

#### Erreur réseau :
```
Failed to fetch
```
**Solution** :
- Vérifie que l'URL Railway est correcte
- Vérifie que le serveur Railway est actif (pas en veille)
- Teste l'URL directement : `https://TON-URL-RAILWAY.up.railway.app/rag-assistant` (doit retourner 405 Method Not Allowed, pas 404)

---

## 🔍 Debug : Vérifier la Configuration

### 1. Vérifier l'URL utilisée

Dans la console Chrome (F12) sur amiens.fr, tape :
```javascript
// L'extension expose ASSISTANT_ENDPOINT dans le scope global si besoin
// Sinon, regarde les requêtes réseau dans l'onglet Network
```

### 2. Tester l'endpoint directement

```bash
curl -X POST https://TON-URL-RAILWAY.up.railway.app/rag-assistant \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}'
```

**Résultat attendu** :
- ✅ `405 Method Not Allowed` ou erreur de payload = endpoint accessible
- ❌ `404 Not Found` = URL incorrecte
- ❌ Timeout = serveur en veille ou inaccessible

### 3. Vérifier les logs Railway

1. Railway → Ton projet → **Deployments**
2. Clique sur le dernier déploiement
3. **View Logs**
4. Tu devrais voir les requêtes arriver

---

## 📝 Checklist Rapide

- [ ] URL Railway obtenue et copiée
- [ ] `content.js` mis à jour avec la bonne URL
- [ ] Extension rechargée dans Chrome
- [ ] CORS configuré (`https://www.amiens.fr` dans `allow_origins`)
- [ ] Test effectué sur amiens.fr
- [ ] Réponse reçue ✅

---

## 🎯 Configuration Actuelle

D'après le code, l'extension utilise actuellement :
- **Local** : `http://localhost:8711/rag-assistant` (si sur localhost)
- **Production** : `https://i-am-production.up.railway.app/rag-assistant` (si sur amiens.fr)

**Vérifie que cette URL correspond à ton déploiement Railway !**

---

## 🆘 Problèmes Fréquents

### Le serveur Railway est en veille
- **Symptôme** : Premier appel prend 1-2 secondes
- **Solution** : Normal pour le plan gratuit, le serveur se réveille automatiquement

### L'extension ne se charge pas
- **Vérifie** : `chrome://extensions/` → Extension activée ?
- **Vérifie** : Le manifest.json est valide ?
- **Vérifie** : Les permissions sont accordées ?

### Les requêtes ne partent pas
- **Vérifie** : Console Chrome (F12) → Onglet Network
- **Vérifie** : Les requêtes vers Railway apparaissent ?
- **Vérifie** : Erreurs CORS ou réseau ?

---

*Dernière mise à jour : 2025-11-18*

