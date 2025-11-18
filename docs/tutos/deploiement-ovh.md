# Déploiement sur OVH - Analyse de l'Offre Perso

## 🔍 Analyse de Votre Offre OVH Perso

### Spécifications Disponibles :
- ✅ **Espace disque** : 100 Go (largement suffisant)
- ✅ **Sites web** : 5 (1 site pour le serveur RAG)
- ✅ **Base de données** : 1 MySQL/MariaDB disponible
- ❌ **CDN** : Non (pas critique)
- ⚠️ **Ressources CPU/RAM** : Partagées, limitées

## ❌ Problème Principal

**L'offre OVH Perso n'est PAS adaptée pour déployer un serveur FastAPI/uvicorn.**

### Limitations :
1. **Pas de processus long** : L'offre Perso est conçue pour sites web statiques/PHP, pas pour applications Python qui tournent en continu
2. **Pas de SSH root** : Impossible d'installer des dépendances système (Python packages, etc.)
3. **Pas de gestion de processus** : Pas de systemd, supervisor, ou équivalent
4. **Limite de temps d'exécution** : Scripts PHP/Python limités à quelques secondes
5. **Pas de port personnalisé** : Pas d'accès direct au port 8711

## ✅ Solutions Alternatives

### Option 1 : VPS OVH (Recommandé)

**Offre nécessaire** : VPS Starter ou supérieur (~3-5€/mois)

**Avantages** :
- ✅ Contrôle total (SSH root)
- ✅ Processus long possible
- ✅ Installation Python/FastAPI
- ✅ Gestion de processus (systemd)
- ✅ Ports personnalisés

**Configuration minimale recommandée** :
- 1 vCore
- 2 GB RAM
- 20 GB SSD
- IPv4

**Déploiement** :
```bash
# Installation
sudo apt update
sudo apt install python3 python3-pip nginx

# Clone du projet
git clone [votre-repo]
cd "I Amiens"

# Installation dépendances
pip3 install -r requirements.txt

# Configuration systemd
sudo nano /etc/systemd/system/rag-assistant.service
```

**Fichier systemd** (`/etc/systemd/system/rag-assistant.service`) :
```ini
[Unit]
Description=RAG Assistant Amiens Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/rag-assistant
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /var/www/rag-assistant/rag_assistant_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Nginx reverse proxy** :
```nginx
server {
    listen 80;
    server_name rag-assistant.votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:8711;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Option 2 : Services Cloud Gratuits/Pas Chers

#### Railway.app
- ✅ **Gratuit** : 500h/mois
- ✅ **Déploiement automatique** depuis GitHub
- ✅ **Support Python/FastAPI** natif
- ✅ **Variables d'environnement** pour API keys
- ⚠️ **Limite** : Se met en veille après inactivité

**Configuration** :
1. Créer `Procfile` :
```
web: python rag_assistant_server.py
```

2. Créer `railway.json` :
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python rag_assistant_server.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### Render.com
- ✅ **Gratuit** : Service gratuit avec limitations
- ✅ **Support Python** natif
- ✅ **Auto-deploy** depuis GitHub
- ⚠️ **Limite** : Se met en veille après inactivité (15 min)

#### Fly.io
- ✅ **Gratuit** : 3 VMs gratuites
- ✅ **Déploiement global** (CDN intégré)
- ✅ **Support Docker** natif
- ✅ **Pas de veille** (si configuré)

**Configuration** :
1. Créer `Dockerfile` :
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8711
CMD ["python", "rag_assistant_server.py"]
```

2. Créer `fly.toml` :
```toml
app = "rag-assistant-amiens"
primary_region = "cdg"

[build]

[env]
  PORT = "8711"

[[services]]
  internal_port = 8711
  protocol = "tcp"
  [[services.ports]]
    port = 80
    handlers = ["http"]
  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

### Option 3 : Utiliser l'Offre Perso pour les Données Statiques

**Stratégie hybride** :
- ✅ **Offre Perso** : Héberger les fichiers statiques (embeddings, metadata, JSON)
- ✅ **Service externe** : Railway/Render pour le serveur FastAPI
- ✅ **CDN** : Utiliser Cloudflare (gratuit) pour accélérer

**Architecture** :
```
[Chrome Extension] 
    ↓
[Railway/Render - FastAPI Server]
    ↓
[OVH Perso - Fichiers statiques via HTTP]
```

## 📊 Comparaison des Solutions

| Solution | Coût/mois | Setup | Maintenance | Performance |
|----------|-----------|-------|-------------|-------------|
| **VPS OVH** | 3-5€ | ⚠️ Moyen | ⚠️ Moyen | ✅ Excellent |
| **Railway** | 0-5€ | ✅ Facile | ✅ Facile | ✅ Bon |
| **Render** | 0-7€ | ✅ Facile | ✅ Facile | ✅ Bon |
| **Fly.io** | 0€ | ⚠️ Moyen | ✅ Facile | ✅ Excellent |

## 🚀 Recommandation

**Pour un déploiement rapide et gratuit** : **Railway.app** ou **Render.com**

**Pour un déploiement professionnel** : **VPS OVH Starter** (~3€/mois)

**Pour un déploiement global optimisé** : **Fly.io** (gratuit, pas de veille)

## 📝 Fichiers Nécessaires pour Déploiement

### 1. `requirements.txt`
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
anthropic==0.18.1
pydantic==2.5.0
python-dotenv==1.0.0
numpy==1.24.3
sentence-transformers==2.2.2
whoosh==2.7.4
```

### 2. `.env.example`
```env
ANTHROPIC_API_KEY=your_key_here
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDINGS_PATH=data/corpus_embeddings.npy
METADATA_PATH=data/corpus_metadata.json
LEXICON_PATH=chrome-extension-v2/data/lexique_enfance.json
```

### 3. `Dockerfile` (pour Fly.io/Docker)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8711

# Run server
CMD ["python", "rag_assistant_server.py"]
```

### 4. `.dockerignore`
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
.git
.gitignore
*.md
tests/
chrome-extension-v2/
```

## ⚠️ Points d'Attention

1. **Variables d'environnement** : Ne jamais commiter `ANTHROPIC_API_KEY`
2. **Fichiers volumineux** : Les embeddings `.npy` peuvent être lourds (vérifier la taille)
3. **CORS** : Mettre à jour les origines autorisées dans `rag_assistant_server.py`
4. **HTTPS** : Utiliser un reverse proxy (Nginx) ou service avec HTTPS intégré
5. **Monitoring** : Configurer des logs et alertes

## 🔧 Modification Nécessaire pour Déploiement

**Dans `rag_assistant_server.py`**, ligne 972 :
```python
app.add_middleware(
  CORSMiddleware,
  allow_origins=[
    "http://localhost:8711",
    "https://localhost:8711",
    "https://www.amiens.fr",
    "https://rag-assistant.votre-domaine.com",  # Ajouter votre domaine
  ],
  allow_credentials=True,
  allow_methods=["POST"],
  allow_headers=["*"]
)
```

## 📈 Prochaines Étapes

1. **Choisir une solution** (Railway recommandé pour débuter)
2. **Créer les fichiers de déploiement** (requirements.txt, Dockerfile si nécessaire)
3. **Tester localement** avec les mêmes variables d'environnement
4. **Déployer** et tester
5. **Mettre à jour l'extension Chrome** avec la nouvelle URL

