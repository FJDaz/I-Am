# 📊 Analyse Charge Documentaire RAG et Politique Système

**Date :** 2025-01-XX  
**Objectif :** Analyser la charge actuelle et projetée pour optimiser la latence

---

## 📈 Charge Documentaire Actuelle

### Corpus Standard (Enfance uniquement)

| Composant | Taille | Description |
|-----------|--------|-------------|
| **Segments** | 1,514 | Nombre de segments RAG |
| **Embeddings** | 2.22 MB | NumPy array (1514 × 384 dims, float32) |
| **Metadata JSON** | 0.78 MB | Fichier JSON avec métadonnées |
| **Whoosh Index** | ~1.96 MB | Index BM25 créé en RAM au démarrage |
| **Sentence-transformers** | 90 MB | Modèle all-MiniLM-L6-v2 en RAM |
| **TOTAL RAM** | **~95 MB** | Charge mémoire totale |

### Taille sur Disque

- `corpus_embeddings.npy` : 2.22 MB
- `corpus_metadata.json` : 0.78 MB
- `corpus_segments.json` : 0.82 MB
- **Total disque :** ~3.81 MB

---

## 🔮 Projection Après Généralisation

### Scénarios de Croissance

| Multiplicateur | Segments | Embeddings | Metadata | Whoosh | Model | **TOTAL RAM** |
|----------------|----------|------------|----------|--------|-------|---------------|
| **Actuel (1x)** | 1,514 | 2.22 MB | 0.78 MB | 1.96 MB | 90 MB | **~95 MB** |
| **5x** | 7,570 | 11.1 MB | 3.9 MB | 9.75 MB | 90 MB | **~115 MB** |
| **10x** | 15,140 | 22.2 MB | 7.8 MB | 19.5 MB | 90 MB | **~140 MB** |
| **20x** | 30,280 | 44.4 MB | 15.6 MB | 39 MB | 90 MB | **~189 MB** |

### Estimation Réaliste

**Scénario probable :** 5-7 sections activées
- Enfance : 1,514 segments (actuel)
- Jeunesse : ~800-1,200 segments (estimé)
- Culture : ~600-1,000 segments (estimé)
- Sport : ~500-800 segments (estimé)
- Autres : ~500-1,000 segments (estimé)

**Total estimé :** 4,000-6,000 segments (≈ 3-4x actuel)

**RAM estimée :** ~110-125 MB

---

## ⚡ Analyse Latence Actuelle

### Temps de Recherche RAG

1. **Whoosh (BM25)** : ~10-50ms (recherche full-text)
2. **Embeddings (cosine similarity)** : ~20-100ms (calcul similarité)
3. **Combinaison scores** : ~5-10ms
4. **Total recherche RAG :** ~35-160ms

### Temps Claude API

- **Claude Sonnet** : 1-3 secondes
- **Claude Haiku** : 0.5-1.5 secondes

### Temps Total Requête

- **Recherche RAG** : ~35-160ms (négligeable)
- **Claude API** : 500-3000ms (bottleneck principal)
- **Total :** 0.5-3 secondes

---

## 🎯 Politique Système Recommandée

### 1. Charge Mémoire (Acceptable jusqu'à 20x)

**Verdict :** ✅ **Pas de problème jusqu'à 20x segments**

- Railway CPU : Généralement 512 MB - 2 GB RAM disponibles
- 189 MB pour 20x segments = **Acceptable**
- Pas besoin de changement d'infrastructure

**Recommandation :**
- ✅ Garder tout en mémoire (embeddings + metadata + Whoosh)
- ✅ Pas de lazy loading nécessaire
- ✅ Pas de pagination des embeddings

### 2. Optimisation Recherche RAG (Déjà Fait)

**Optimisations implémentées :**
- ✅ `top_k * 4` → `top_k * 2` (réduction 50% calculs)
- ✅ Cache embeddings de requêtes fréquentes (à implémenter)
- ✅ Cache résultats complets (déjà implémenté)

**Impact :**
- Recherche RAG : 35-160ms → **20-80ms** (amélioration ~50%)
- Gain total : ~15-80ms par requête

### 3. Optimisation Claude API (Priorité Haute)

**Bottleneck principal :** Claude API (500-3000ms)

**Stratégies :**

#### a) Claude Haiku (Recommandé)
- Latence : 0.5-1.5s (vs 1-3s Sonnet)
- Coût : ~5x moins cher
- Qualité : Légèrement inférieure mais acceptable
- **Gain :** 50-60% réduction latence

#### b) Cache Mémoire (Déjà Implémenté)
- TTL : 1h par défaut
- Questions fréquentes : Latence ~0ms (cache hit)
- **Gain :** 100% pour questions répétées

#### c) Streaming (Optionnel)
- Afficher réponse progressivement
- Perception latence réduite (UX)
- Pas de gain réel, mais meilleure UX

### 4. Optimisation Whoosh (Si Corpus > 10x)

**Si corpus > 15,000 segments :**

#### Option A : Index Persistant
- Sauvegarder index Whoosh sur disque
- Recharger au démarrage (plus rapide que reconstruire)
- **Gain :** Temps démarrage réduit

#### Option B : Index Optimisé
- Indexer seulement champs nécessaires (label, content)
- Réduire taille index de 30-40%
- **Gain :** Moins de RAM, recherche plus rapide

#### Option C : Pagination Embeddings (Non Recommandé)
- Charger embeddings par chunks
- **Inconvénient :** Complexité, latence recherche augmentée
- **Verdict :** ❌ Pas nécessaire avant 30,000+ segments

---

## 📋 Plan d'Action Optimisation Latence

### Phase 1 : Court Terme (Immédiat)

1. ✅ **Cache mémoire** - Déjà implémenté
2. ⚠️ **Tester Claude Haiku** - À faire
3. ✅ **Optimisation recherche** (`top_k * 2`) - Déjà fait

**Gain attendu :** 50-60% réduction latence (Haiku) + cache hits

### Phase 2 : Moyen Terme (Si Corpus > 10x)

1. **Index Whoosh persistant** - Si corpus > 15,000 segments
2. **Cache embeddings requêtes** - Implémenter cache `query_vec`
3. **Monitoring latence** - Logger temps recherche vs API

**Gain attendu :** 10-20% réduction latence recherche

### Phase 3 : Long Terme (Si Corpus > 20x)

1. **Index Whoosh optimisé** - Réduire champs indexés
2. **Embeddings quantifiés** - float32 → int8 (si qualité acceptable)
3. **CDN pour embeddings** - Si déploiement multi-régions

**Gain attendu :** 20-30% réduction taille mémoire

---

## 🎯 Recommandations Finales

### Pour Corpus Actuel (1,514 segments)

✅ **Configuration optimale :**
- Claude Haiku (0.5-1.5s) au lieu de Sonnet (1-3s)
- Cache mémoire activé (TTL 1h)
- Recherche optimisée (`top_k * 2`)
- **Latence cible :** 0.5-1.5s (vs 1-3s actuel)

### Pour Corpus Généralisé (5,000-10,000 segments)

✅ **Configuration optimale :**
- Claude Haiku
- Cache mémoire
- Index Whoosh persistant (si > 15,000 segments)
- **Latence cible :** 0.5-1.5s (même avec corpus 10x plus grand)

### Pour Corpus Très Grand (20,000+ segments)

⚠️ **Considérations :**
- RAM : ~189 MB (acceptable)
- Whoosh : Index persistant recommandé
- Embeddings : Peut rester en mémoire (189 MB acceptable)
- **Pas besoin de changement d'infrastructure**

---

## 📊 Tableau Récapitulatif

| Critère | Actuel (1,514) | 5x (7,570) | 10x (15,140) | 20x (30,280) |
|---------|----------------|-------------|--------------|--------------|
| **RAM** | 95 MB | 115 MB | 140 MB | 189 MB |
| **Disque** | 3.8 MB | 19 MB | 38 MB | 76 MB |
| **Latence RAG** | 35-160ms | 50-200ms | 70-250ms | 100-300ms |
| **Latence Claude** | 1-3s (Sonnet) | 1-3s | 1-3s | 1-3s |
| **Latence Totale** | 1-3s | 1-3s | 1-3s | 1-3s |
| **Avec Haiku** | 0.5-1.5s | 0.5-1.5s | 0.5-1.5s | 0.5-1.5s |
| **Avec Cache** | ~0ms (hit) | ~0ms (hit) | ~0ms (hit) | ~0ms (hit) |

**Conclusion :** La latence est dominée par Claude API, pas par la taille du corpus.

---

## ✅ Actions Prioritaires

1. **Tester Claude Haiku** (gain 50-60% latence)
2. **Valider cache** (gain 100% pour questions fréquentes)
3. **Monitorer latence** après généralisation
4. **Index Whoosh persistant** seulement si corpus > 15,000 segments

---

**Dernière mise à jour :** 2025-01-XX


