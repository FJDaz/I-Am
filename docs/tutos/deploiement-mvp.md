# 🚀 Déploiement MVP/POC - Guide Rapide (15 minutes)

## Objectif
Déployer rapidement le serveur RAG pour que les utilisatrices puissent tester l'extension Chrome.

## ✅ Solution : Railway.app (Gratuit, Simple, Rapide)

### Pourquoi Railway ?
- ✅ **Gratuit** : 500h/mois (largement suffisant pour un POC)
- ✅ **Déploiement en 5 minutes** depuis GitHub
- ✅ **HTTPS automatique** (pas de config SSL)
- ✅ **Variables d'environnement** faciles
- ⚠️ **Mise en veille** après 5 min d'inactivité (réveil en 1-2s)

## 📋 Étapes de Déploiement

### 1. Préparer le Repository (2 min)

**Fichiers déjà créés** :
- ✅ `Procfile` : Indique comment lancer le serveur
- ✅ `runtime.txt` : Version Python
- ✅ `requirements.txt` : Dépendances

**Vérifier que `requirements.txt` contient** :
```
fastapi
uvicorn[standard]
anthropic
pydantic
python-dotenv
numpy
whoosh
pdfminer.six
xlrd
```

**Note** : `sentence-transformers` a été retiré pour alléger l'image Docker (de ~5 Go à ~200 Mo). La recherche utilise Whoosh (BM25) uniquement.

### 2. Créer un Compte Railway (2 min)

1. Aller sur https://railway.app/
2. Cliquer sur **"Login"** → **"Login with GitHub"**
3. Autoriser Railway à accéder à votre GitHub

### 3. Déployer le Projet (5 min)

1. Dans Railway, cliquer sur **"New Project"**
2. Sélectionner **"Deploy from GitHub repo"**
3. Choisir votre repository (celui contenant le projet "I Amiens")
4. Railway détecte automatiquement Python et le `Procfile`

### 4. Configurer les Variables d'Environnement (3 min)

**⚠️ IMPORTANT** : Le build réussit mais le déploiement crash sans cette étape !

Dans Railway → Votre projet → **Variables** (onglet en haut) :

1. Cliquer sur **"+ New Variable"**
2. Ajouter :
   - **Key** : `ANTHROPIC_API_KEY`
   - **Value** : `sk-ant-...` (ta clé Anthropic)
3. Cliquer sur **"Add"**

**Variables optionnelles** :
- `PORT=8711` (Railway définit automatiquement `PORT`, mais on peut le garder)
- `ALLOWED_ORIGIN=https://www.amiens.fr` (si besoin de restreindre CORS)

**Note** : Après avoir ajouté `ANTHROPIC_API_KEY`, Railway redéploie automatiquement.

### 5. Obtenir l'URL du Serveur (1 min)

1. Dans Railway → Votre projet → **Settings** → **Networking**
2. Cliquer sur **"Generate Domain"** (ou utiliser le domaine par défaut)
3. **Copier l'URL** : `https://votre-projet.up.railway.app`

### 6. Mettre à Jour l'Extension Chrome (2 min)

**Modifier `chrome-extension-v2/content.js`** :

```javascript
// Remplacer la ligne avec ASSISTANT_ENDPOINT
const ASSISTANT_ENDPOINT = "https://votre-projet.up.railway.app/rag-assistant";
```

**Ou mieux, détection automatique** :
```javascript
// Détection automatique : production si pas localhost
const ASSISTANT_ENDPOINT = window.location.hostname === 'localhost' 
  ? "http://localhost:8711/rag-assistant"
  : "https://votre-projet.up.railway.app/rag-assistant";
```

### 7. Tester (1 min)

1. Recharger l'extension Chrome
2. Aller sur https://www.amiens.fr
3. Cliquer sur l'icône de l'assistant
4. Poser une question test : "Quels sont les tarifs de la cantine ?"

## 🎯 Résultat Attendu

- ✅ Serveur accessible 24/7 (avec réveil automatique)
- ✅ HTTPS automatique
- ✅ Extension fonctionnelle pour toutes les utilisatrices
- ✅ Pas de configuration serveur complexe

## ⚠️ Limitations MVP

1. **Mise en veille** : Premier appel après inactivité = 1-2s de latence (réveil)
2. **Gratuit** : 500h/mois = ~20 jours continus (largement suffisant pour POC)
3. **Pas de domaine personnalisé** : URL `*.up.railway.app` (gratuit)

## 🔄 Mise à Jour du Code

**Pour mettre à jour le serveur** :
1. Push sur GitHub
2. Railway redéploie automatiquement (1-2 min)

**Pour mettre à jour l'extension** :
1. Modifier `content.js`
2. Recharger l'extension dans Chrome (chrome://extensions → Recharger)

## 📊 Monitoring

Dans Railway → Votre projet → **Metrics** :
- Voir les logs en temps réel
- Voir l'utilisation CPU/RAM
- Voir les requêtes HTTP

## 🆘 Troubleshooting

### Le serveur ne démarre pas / "Deploy crashed"
- **Erreur** : `ANTHROPIC_API_KEY non défini`
- **Solution** : Ajouter la variable dans Railway → **Variables** → **+ New Variable**
  - Key: `ANTHROPIC_API_KEY`
  - Value: `sk-ant-...` (ta clé Anthropic)
- Vérifier les logs dans Railway → **Deployments** → **View Logs**

### Erreur CORS dans l'extension
- Vérifier que `ALLOWED_ORIGIN` contient `https://www.amiens.fr`
- Vérifier l'URL dans `content.js`

### Le serveur se met en veille
- Normal pour le plan gratuit
- Premier appel = 1-2s de latence (réveil automatique)
- Pour éviter : utiliser Fly.io (gratuit, pas de veille)

## 🚀 Alternative : Render.com (Similaire)

Si Railway ne fonctionne pas :

1. Aller sur https://render.com/
2. **New** → **Web Service**
3. Connecter GitHub repo
4. Configurer :
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `python rag_assistant_server.py`
   - **Environment Variables** : Même que Railway

## 📝 Checklist Déploiement

- [ ] Repository GitHub prêt (avec `Procfile`, `runtime.txt`, `requirements.txt`)
- [ ] Compte Railway créé
- [ ] Projet déployé sur Railway
- [ ] Variables d'environnement configurées
- [ ] URL du serveur copiée
- [ ] Extension Chrome mise à jour avec la nouvelle URL
- [ ] Test effectué sur amiens.fr
- [ ] Extension partagée avec les utilisatrices

## 🎉 C'est Prêt !

Une fois déployé, partagez simplement :
1. **L'extension Chrome** (fichier `.crx` ou instructions d'installation)
2. **L'URL du serveur** (déjà intégrée dans l'extension)

Les utilisatrices peuvent tester directement sur amiens.fr ! 🚀

