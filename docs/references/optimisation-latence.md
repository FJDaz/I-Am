# Optimisation de la Latence du Serveur Local

## 🔍 Analyse des Causes de Latence

### Causes identifiées :
1. **Pas de compression HTTP** (gzip/brotli)
2. **Timeout trop long** (60s pour Claude API)
3. **Pas de workers multiples** (uvicorn single-threaded)
4. **Chargements synchrones** au démarrage
5. **Pas de cache** pour requêtes répétées
6. **Pas de connexions keep-alive optimisées**

## 🚀 Solutions d'Optimisation

### 1. Compression HTTP (Gzip)

**Impact** : Réduction de 60-80% de la taille des réponses

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

**Ajouter dans `rag_assistant_server.py` après ligne 965** :
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 2. Réduire le Timeout Claude API

**Impact** : Évite les attentes inutiles, fail-fast

**Modifier ligne 921** :
```python
timeout=30.0,  # Au lieu de 60.0
```

### 3. Workers Multiples (Uvicorn)

**Impact** : Traitement parallèle de plusieurs requêtes

**Modifier les lignes 1296-1298** :
```python
if os.path.exists(ssl_keyfile) and os.path.exists(ssl_certfile):
    uvicorn.run(
        "rag_assistant_server:app",
        host="0.0.0.0",
        port=8711,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
        workers=2,  # 2 workers pour développement local
        loop="asyncio"
    )
else:
    uvicorn.run(
        "rag_assistant_server:app",
        host="0.0.0.0",
        port=8711,
        workers=2,
        loop="asyncio"
    )
```

**⚠️ Attention** : Les workers multiples nécessitent que les données (embeddings, metadata) soient partagées en mémoire ou rechargées par worker.

### 4. Cache Simple pour Requêtes Fréquentes

**Impact** : Réponses instantanées pour questions identiques

```python
from functools import lru_cache
from hashlib import md5
import json

# Cache simple en mémoire (max 100 entrées)
_request_cache = {}
CACHE_TTL = 300  # 5 minutes

def get_cache_key(payload: AssistantRequest) -> str:
    """Génère une clé de cache basée sur la question"""
    key_data = {
        "question": payload.question,
        "normalized": payload.normalized_question,
        "rag_count": len(payload.rag_results or [])
    }
    return md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()

# Dans rag_assistant_endpoint, avant le traitement :
cache_key = get_cache_key(payload)
if cache_key in _request_cache:
    cached_response, cached_time = _request_cache[cache_key]
    if time.time() - cached_time < CACHE_TTL:
        return cached_response
```

### 5. Chargement Asynchrone des Données

**Impact** : Démarrage plus rapide, chargement en arrière-plan

```python
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: charger en arrière-plan
    asyncio.create_task(load_data_async())
    yield
    # Shutdown: cleanup si nécessaire
    pass

app = FastAPI(
    title="RAG Assistant Amiens V2",
    version="0.2.0",
    lifespan=lifespan
)
```

### 6. Optimiser les Appels API Claude

**Impact** : Réduction du temps de réponse

- **Streaming** : Si possible, utiliser streaming pour afficher la réponse progressivement
- **Max tokens** : Limiter `max_tokens` pour éviter les réponses trop longues
- **Temperature** : Réduire si pas nécessaire (0.3 au lieu de 0.7)

### 7. Connexions Keep-Alive

**Impact** : Réutilisation des connexions HTTP

Uvicorn gère déjà les keep-alive par défaut, mais on peut optimiser :

```python
uvicorn.run(
    ...,
    timeout_keep_alive=30,  # Garder les connexions ouvertes 30s
    limit_concurrency=10,   # Limiter les connexions simultanées
)
```

## 📊 Configuration Recommandée (Développement Local)

### Configuration Minimale (Rapide à implémenter) :

1. **Compression Gzip** ✅ (1 ligne)
2. **Timeout réduit** ✅ (1 ligne)
3. **Workers = 1** (garder single-threaded pour éviter problèmes de partage mémoire)

### Configuration Optimale (Production) :

1. **Compression Gzip** ✅
2. **Timeout 30s** ✅
3. **Workers = 2-4** (selon CPU)
4. **Cache simple** ✅
5. **Keep-alive optimisé** ✅

## 🔧 Implémentation Rapide

**Fichier à modifier** : `rag_assistant_server.py`

**Lignes à ajouter/modifier** :

1. **Import Gzip** (après ligne 13) :
```python
from fastapi.middleware.gzip import GZipMiddleware
```

2. **Ajouter middleware** (après ligne 976) :
```python
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

3. **Réduire timeout** (ligne 921) :
```python
timeout=30.0,  # Au lieu de 60.0
```

4. **Optimiser uvicorn** (lignes 1296-1298) :
```python
uvicorn.run(
    "rag_assistant_server:app",
    host="0.0.0.0",
    port=8711,
    timeout_keep_alive=30,
    limit_concurrency=10
)
```

## 📈 Gains Attendus

- **Compression** : -60% taille réponses → -40% temps transfert
- **Timeout réduit** : -50% temps d'attente max
- **Keep-alive** : -20% overhead connexions
- **Total estimé** : **-30 à -50% latence perçue**

## ⚠️ Notes Importantes

1. **Workers multiples** : Nécessite que les embeddings/metadata soient thread-safe ou rechargés par worker
2. **Cache** : Peut masquer des mises à jour de données (TTL court recommandé)
3. **Compression** : Augmente légèrement l'usage CPU mais réduit la bande passante

## 🧪 Test de Performance

Pour mesurer l'amélioration :

```python
import time

@app.post("/rag-assistant", response_model=AssistantResponse)
def rag_assistant_endpoint(payload: AssistantRequest):
    start_time = time.time()
    try:
        # ... code existant ...
        response_time = time.time() - start_time
        print(f"[PERF] Temps de réponse: {response_time:.2f}s")
        return result
    except Exception as e:
        response_time = time.time() - start_time
        print(f"[PERF] Erreur après {response_time:.2f}s: {e}")
        raise
```

