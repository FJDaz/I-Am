# Guide : Variables d'Environnement (.env)

## 📋 Vue d'ensemble

Les variables d'environnement permettent de stocker des informations sensibles (clés API, mots de passe) ou des configurations sans les coder en dur dans le code.

---

## 🐍 Python

### 1. Installation de `python-dotenv`

```bash
pip install python-dotenv
```

### 2. Créer le fichier `.env`

À la racine de votre projet (ou dans le dossier `Backend/`) :

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-xxx-votre-cle-ici
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
PORT=8000
DEBUG=true
API_BASE_URL=http://localhost:8000
```

**⚠️ Important :** Ajoutez `.env` à votre `.gitignore` pour ne pas commiter les secrets !

```bash
# .gitignore
.env
*.env
```

### 3. Charger les variables dans le code

```python
import os
from dotenv import load_dotenv

# Charger le fichier .env (cherche automatiquement à la racine)
load_dotenv()

# Récupérer une variable
api_key = os.environ.get("ANTHROPIC_API_KEY")

# Avec valeur par défaut
port = os.environ.get("PORT", "8000")  # "8000" si PORT n'existe pas

# Vérifier si une variable existe (obligatoire)
if not api_key:
    raise SystemExit("ANTHROPIC_API_KEY non défini. Ajoute la clé dans .env")

# Utiliser la variable
print(f"API Key: {api_key}")
```

### 4. Exemple complet (comme dans votre projet)

```python
from dotenv import load_dotenv
import os

load_dotenv()

# Variable obligatoire
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
if not anthropic_key:
    raise SystemExit("ANTHROPIC_API_KEY non défini. Ajoute la clé dans .env")

# Variable optionnelle avec valeur par défaut
embed_model = os.environ.get("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
port = int(os.environ.get("PORT", "8000"))  # Convertir en int

# Utilisation
client = Anthropic(api_key=anthropic_key)
```

### 5. Spécifier un chemin personnalisé

```python
from dotenv import load_dotenv
from pathlib import Path

# Charger depuis un chemin spécifique
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Ou depuis la racine du projet
project_root = Path(__file__).parent.parent
load_dotenv(dotenv_path=project_root / ".env")
```

---

## 🟨 JavaScript / Node.js

### 1. Installation de `dotenv`

```bash
npm install dotenv
# ou
yarn add dotenv
```

### 2. Créer le fichier `.env`

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-xxx-votre-cle-ici
API_BASE_URL=http://localhost:8000
PORT=3000
NODE_ENV=development
```

### 3. Charger les variables dans le code

```javascript
// Au début du fichier (avant toute autre import)
require('dotenv').config();

// Récupérer une variable
const apiKey = process.env.ANTHROPIC_API_KEY;

// Avec valeur par défaut
const port = process.env.PORT || 3000;

// Vérifier si une variable existe
if (!apiKey) {
    console.error("ANTHROPIC_API_KEY non défini dans .env");
    process.exit(1);
}

// Utiliser la variable
console.log(`API Key: ${apiKey}`);
```

### 4. Avec ES6 modules (import/export)

```javascript
// config.js
import dotenv from 'dotenv';
dotenv.config();

export const API_KEY = process.env.ANTHROPIC_API_KEY;
export const PORT = process.env.PORT || 3000;
export const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

// Vérification
if (!API_KEY) {
    throw new Error("ANTHROPIC_API_KEY non défini dans .env");
}
```

### 5. Dans un fichier séparé

```javascript
// config.js
require('dotenv').config();

module.exports = {
    apiKey: process.env.ANTHROPIC_API_KEY,
    port: process.env.PORT || 3000,
    apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:8000',
    nodeEnv: process.env.NODE_ENV || 'development'
};

// app.js
const config = require('./config');
console.log(config.apiKey);
```

---

## 🌐 Extension Chrome (JavaScript dans le navigateur)

**⚠️ Limitation :** Les extensions Chrome ne peuvent pas charger directement un fichier `.env` pour des raisons de sécurité.

### Solution 1 : Utiliser `chrome.storage` (recommandé)

```javascript
// background.js ou content.js
// Stocker les variables dans chrome.storage.local

chrome.storage.local.get(['ANTHROPIC_API_KEY'], (result) => {
    const apiKey = result.ANTHROPIC_API_KEY;
    if (!apiKey) {
        console.error("API Key non configurée");
        return;
    }
    // Utiliser apiKey
});
```

### Solution 2 : Variables dans le code (non recommandé pour secrets)

```javascript
// config.js (à ne PAS commiter si contient des secrets)
const CONFIG = {
    API_BASE_URL: window.location.hostname === 'localhost'
        ? "http://localhost:8711"
        : "https://i-am-production.up.railway.app",
    // Ne pas mettre de clés API ici !
};

// Utilisation
const endpoint = `${CONFIG.API_BASE_URL}/rag-assistant`;
```

### Solution 3 : Variables d'environnement au build (si vous utilisez un bundler)

```javascript
// webpack.config.js ou vite.config.js
const API_KEY = process.env.ANTHROPIC_API_KEY;

module.exports = {
    // ...
    plugins: [
        new webpack.DefinePlugin({
            'process.env.API_KEY': JSON.stringify(API_KEY)
        })
    ]
};
```

---

## 📝 Bonnes Pratiques

### 1. Créer un fichier `.env.example`

```bash
# .env.example (à commiter)
ANTHROPIC_API_KEY=sk-ant-xxx-remplacer-par-votre-cle
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
PORT=8000
DEBUG=false
API_BASE_URL=http://localhost:8000
```

### 2. Ajouter à `.gitignore`

```bash
# .gitignore
.env
*.env
!.env.example
```

### 3. Documentation dans le README

```markdown
## Configuration

1. Copier `.env.example` vers `.env`
2. Remplir les variables avec vos valeurs
3. Ne jamais commiter le fichier `.env`
```

### 4. Validation des variables au démarrage

```python
# Python
required_vars = ["ANTHROPIC_API_KEY", "PORT"]
missing = [var for var in required_vars if not os.environ.get(var)]
if missing:
    raise SystemExit(f"Variables manquantes dans .env: {', '.join(missing)}")
```

```javascript
// JavaScript
const requiredVars = ['ANTHROPIC_API_KEY', 'PORT'];
const missing = requiredVars.filter(varName => !process.env[varName]);
if (missing.length > 0) {
    console.error(`Variables manquantes dans .env: ${missing.join(', ')}`);
    process.exit(1);
}
```

---

## 🔒 Sécurité

### ✅ À FAIRE
- ✅ Utiliser `.env` pour les secrets
- ✅ Ajouter `.env` à `.gitignore`
- ✅ Créer un `.env.example` sans secrets
- ✅ Valider les variables au démarrage
- ✅ Utiliser des valeurs par défaut pour les variables optionnelles

### ❌ À ÉVITER
- ❌ Commiter le fichier `.env`
- ❌ Coder en dur les clés API dans le code
- ❌ Partager les fichiers `.env` par email/chat
- ❌ Utiliser `.env` en production (utiliser les variables d'environnement du système)

---

## 🚀 Déploiement (Production)

### Railway / Heroku / Vercel

Configurez les variables dans le dashboard de la plateforme :

```bash
# Dans Railway/Heroku/Vercel dashboard
ANTHROPIC_API_KEY=sk-ant-xxx
PORT=8000
NODE_ENV=production
```

### Docker

```dockerfile
# Dockerfile
ENV ANTHROPIC_API_KEY=sk-ant-xxx
ENV PORT=8000
```

Ou via `docker-compose.yml` :

```yaml
services:
  app:
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - PORT=8000
    env_file:
      - .env
```

---

## 📚 Exemples Réels de Votre Projet

### Python (rag_assistant_server.py)

```python
from dotenv import load_dotenv
import os

load_dotenv()

# Variable obligatoire
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
if not anthropic_key:
    raise SystemExit("ANTHROPIC_API_KEY non défini. Ajoute la clé dans .env")

# Variable optionnelle avec défaut
EMBED_MODEL_NAME = os.environ.get("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
```

### JavaScript (content.js)

```javascript
// Détection automatique selon l'environnement
const ASSISTANT_ENDPOINT = window.location.hostname === 'localhost'
    ? "http://localhost:8711/rag-assistant"
    : "https://i-am-production.up.railway.app/rag-assistant";
```

---

## 🔗 Références

- [python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
- [dotenv (Node.js) Documentation](https://github.com/motdotla/dotenv)
- [12-Factor App - Config](https://12factor.net/config)

