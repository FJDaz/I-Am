# 📐 Document Cadre - Stratégie Système I-Amiens

**Date :** 2025-01-XX  
**Version :** 1.0  
**Objectif :** Cadre de référence pour la généralisation d'I-Amiens à tout le site amiens.fr

---

## 🎯 Vision Stratégique

### Contexte Villes Moyennes

**Enjeux :**
- 24% d'illectronisme dans les pôles urbains < 50k habitants
- 17% jugent Internet "trop compliqué" (vs 11% en Île-de-France)
- Fracture numérique élevée, notamment chez les seniors (60%+)

**Opportunité :**
- Les mères 30-45 ans sont des **"prescriptrices numériques"** naturelles
- Effet de contagion familiale : cibler 17% de la population (mères actives) → toucher 40% par prescription
- 89% de satisfaction sur la rubrique Enfance (preuve de concept)

### Objectif I-Amiens Généralisé

**Phase 1 (MVP) :** Généraliser à tout amiens.fr en conservant la qualité Enfance
- Cibler les besoins essentiels : démarches administratives, info pratique locale
- S'adapter à chaque profil d'usager (personas)
- Rester simple pour publics peu technophiles

**Phase 2 (Évolution) :** Inclusion numérique par prescription familiale
- Mère active → Grand-mère (67%) → Amie senior
- Réduction de la charge des services d'accueil physique

---

## 🏗️ Architecture Actuelle

### Stack Technique

**Backend :**
- **Langage :** Python 3.9+
- **Framework :** FastAPI
- **Serveur :** Uvicorn (ASGI)
- **Déploiement :** Railway (PaaS, CPU, pas de GPU)

**RAG System :**
- **Recherche lexicale :** Whoosh (BM25F, stemmer français)
- **Recherche sémantique :** NumPy embeddings (sentence-transformers/all-MiniLM-L6-v2)
- **Recherche hybride :** Combinaison Whoosh + embeddings (top_k * 2)

**IA/LLM :**
- **Modèle :** Claude API (Anthropic)
  - Par défaut : Claude 3.7 Sonnet (qualité)
  - Option : Claude 3.5 Haiku (rapidité, configurable via `CLAUDE_MODEL`)
- **Usage :** Génération réponses avec contexte RAG

**Frontend :**
- **Extension Chrome :** Manifest V3
- **Technologies :** JavaScript vanilla, Content Scripts, Overlay HTML

### Flux Complet Actuel

```
Utilisateur (Chrome)
    ↓
Extension Chrome (content.js)
    ├── Recherche locale (corpus_segments.json)
    └── Appel Backend
        ↓
Backend FastAPI (rag_assistant_server.py)
    ├── Cache mémoire (vérification)
    ├── RAG System
    │   ├── Whoosh (BM25F, top_k * 2)
    │   └── Embeddings (cosine similarity, top_k * 2)
    ├── Données structurées (RPE, tarifs, écoles, lieux)
    └── Claude API
        ↓
Réponse enrichie (HTML + sources + follow_up_question)
    ↓
Extension Chrome (affichage)
```

### Charge Documentaire Actuelle

| Composant | Taille | Description |
|-----------|--------|-------------|
| **Segments RAG** | 1,514 | Corpus Enfance uniquement |
| **Embeddings** | 2.22 MB | NumPy array (1514 × 384 dims, float32) |
| **Metadata JSON** | 0.78 MB | Métadonnées segments |
| **Whoosh Index** | ~1.96 MB | Index BM25 créé en RAM au démarrage |
| **Sentence-transformers** | 90 MB | Modèle all-MiniLM-L6-v2 en RAM |
| **TOTAL RAM** | **~95 MB** | Charge mémoire totale |

**Projection généralisation (5-7 sections) :** ~110-125 MB RAM (acceptable)

### Optimisations Récentes

1. **Cache mémoire** (`Backend/cache.py`)
   - TTL : 1h par défaut
   - Questions fréquentes : latence ~0ms (cache hit)
   - Hash de questions normalisées

2. **Support Claude Haiku**
   - Variable d'environnement `CLAUDE_MODEL`
   - Gain latence : 50-60% (0.5-1.5s vs 1-3s Sonnet)

3. **Optimisation recherche RAG**
   - `top_k * 4` → `top_k * 2` (Whoosh et embeddings)
   - Réduction latence recherche : ~50%

4. **Détection corpus généralisé**
   - Détection automatique `corpus_metadata_generalized.json`
   - Fallback sur corpus standard si absent

---

## 👥 Personas et Stratégie de Prescription

### Personas Principaux (10)

1. **Mère active 30-45 ans** ⭐ (PIVOT - priorité 1)
2. **Grand-mère 65+** (prescrite par la mère)
3. **Étudiant 18-25 ans**
4. **Actif 40-60 ans** (propriétaire, professionnel)
5. **Public économique** (entreprises, commerçants)
6. **Touriste/visiteur**
7. **Adolescent 12-17 ans**
8. **Femme aidante 45-60 ans**
9. **Bénévole associatif**
10. **Jeune actif sans voiture**

### Chaînes de Prescription Principales

**Chaîne principale (la plus stratégique) :**
```
Mère active → Grand-mère (67%) → Amie senior
    ↓
    → Père (23%) → Collègues
    ↓  
    → Ado (8%) → Amis étudiants
```

**Points clés :**
- **La mère active est le pivot** - son expérience conditionne toute la chaîne
- **La grand-mère est la clé de l'inclusion senior** - via prescription familiale
- **L'étudiant est le prescripteur "ascendant"** - montre son autonomie à ses parents

### Priorisation Personas (Phase MVP)

**Phase 1 (MVP) :**
1. **Mère active 30-45 ans** ✅ (déjà couvert - Enfance)
2. **Actif 40-60 ans** (démarches administratives : carte identité, permis, taxes)

**Phase 2 :**
3. **Étudiant 18-25 ans** (logement, transports, culture)
4. **Seniors** (via prescription familiale, pas directe)

**Phase 3 :**
5. Autres personas selon besoins identifiés

### Détection de Personas (À Implémenter)

**Matrice de scoring :**
- **Termes forts (+3 pts)** : Vocabulaire très spécifique (ex: "PMI", "CROUS", "ABF")
- **Termes moyens (+2 pts)** : Vocabulaire contextuel (ex: "inscription", "enfant")
- **Termes faibles (+1 pt)** : Vocabulaire générique (ex: "horaires", "tarif")
- **Plages horaires** : Coefficients selon persona (ex: 20h-22h → Mère active ×1.8)

**Résolution des conflits :**
- Hiérarchie : Femme aidante > Bénévole > Étudiant > Mère active > Grand-mère > ...
- Règles contextuelles : "ma mère" → Femme aidante, "association" → Bénévole

**Seuils de confiance :**
- **Forte (≥8 pts)** : Persona détecté avec certitude
- **Moyenne (5-7 pts)** : Persona probable
- **Faible (≤4 pts)** : Persona par défaut (Mère active ou Actif selon heure)

---

## 🌐 Plateformes et Sources de Données

### Sites à Scraper

1. **amiens.fr** (site principal)
   - Rubriques : Enfance, Jeunesse, Culture, Sport, Urbanisme, etc.
   - Stratégies : Push-blocks, liens internes, navigation, sitemap, scraping dynamique

2. **Portail citoyen** (portail-citoyen.amiens.fr)
   - Publik (structure standardisée)
   - Services : Enfance, stationnement, associations, habitation, solidarités

3. **Portail démarches** (demarches.amiens.fr)
   - Eau, assainissement, téléservices métropole
   - Formulaires dynamiques (peut nécessiter Playwright)

4. **Mes démarches** (amiens.fr)
   - Stationnement, paiement, emploi, démarches seniors

5. **L'Heure Civique** (amiens.lheurecivique.fr)
   - Plateforme solidarité de proximité
   - Scraping externe

6. **Zoo d'Amiens** (zoo-amiens.fr)
   - Infos pratiques, billetterie

### APIs Disponibles

1. **Amienscope API** (open data)
   - Événements culturels, sportifs, festifs
   - Documentation : https://doc.amienscope.fr

2. **GTFS/GTFS-RT** (transports Ametis)
   - Horaires bus/tram temps réel
   - Données : https://transport.data.gouv.fr/datasets/ametis

3. **Services administratifs**
   - Pas d'API publique documentée
   - Accès via interfaces web standard

### Stratégies de Scraping

**Déjà implémentées :**
1. **Push-blocks (H2 → URLs)** - Extraction H2 dans `.push-block__inner`
2. **Liens internes** - Suivi `<a href>` sur pages
3. **Scraping dynamique (Playwright)** - Contenu caché, accordéons, "voir +"

**À généraliser :**
4. **Navigation** - Extraction liens menus
5. **Sitemap.xml** - Parse sitemap pour découverte URLs
6. **Multi-domaines** - Adaptation `URLDiscoverer` pour portails multiples

---

## 🔧 Architecture Cible (Généralisation)

### Modules à Créer/Adapter

#### 1. Détection de Personas

**Fichier :** `Backend/persona_detector.py`

```python
class PersonaDetector:
    def detect(self, question: str, hour: int, context: dict) -> Persona:
        # Matrice de scoring enrichie
        # Résolution des conflits
        # Retourne persona + score de confiance
```

**Intégration :**
- Appel avant recherche RAG
- Adaptation prompt système selon persona
- Filtrage/pondération segments RAG

#### 2. Prompts Adaptatifs

**Fichier :** `Backend/prompt_adapters.py`

```python
PROMPTS_BY_PERSONA = {
    "mere_active": "Réponse courte (2-3 phrases), vocabulaire concret...",
    "etudiant": "Réponse très brève (1-2 phrases), directe...",
    "senior": "Réponse guidée (4-6 phrases), proposer alternative téléphonique...",
    "actif_40_60": "Réponse structurée (3-5 phrases), étapes numérotées..."
}
```

**Usage :**
- Remplace ou complète `ASSISTANT_SYSTEM_PROMPT` selon persona détecté
- Adapte longueur, ton, structure

#### 3. Lexique Généralisé

**Fichier :** `ML/data/lexique_generalized.json`

**Structure :**
```json
{
  "rubriques": {
    "enfance": {...},
    "urbanisme": {
      "ABF": {"terme_admin": ["Architecte des Bâtiments de France"], "poids": 0.9},
      "permis": {"terme_admin": ["Autorisation d'urbanisme"], "poids": 0.8}
    },
    "transports": {...},
    "culture": {...}
  }
}
```

**Chargement :**
- Dynamique selon requête/persona
- Cache des lexiques chargés

#### 4. Données Structurées Multi-Rubriques

**Fichier :** `ML/data/{persona}_data.json`

**Exemples :**
- `enfance_data.json` : RPE, tarifs, écoles (existant)
- `urbanisme_data.json` : PLU, secteurs, ABF
- `transports_data.json` : Lignes, arrêts, horaires
- `culture_data.json` : Lieux, événements, programmation

**Chargement :**
- Conditionnel selon persona détecté
- Fallback si données absentes

#### 5. Enrichissement Temps Réel

**Fichier :** `Backend/data_enricher.py`

```python
class DataEnricher:
    def enrich_transport(self, query: str) -> dict:
        # API GTFS-RT (horaires temps réel)
    
    def enrich_events(self, query: str) -> dict:
        # API Amienscope (événements culturels)
    
    def enrich_air_quality(self, query: str) -> dict:
        # Open data qualité air
```

**Intégration :**
- Après recherche RAG
- Enrichit réponse avec données dynamiques
- Architecture hybride : RAG (statique) + Enrichissement (dynamique)

#### 6. Scraping Multi-Plateformes

**Fichier :** `tools/scrapers/` (nouveau dossier)

**Scrapers spécialisés :**
- `scraper_amiens_fr.py` - Site principal (existant)
- `scraper_portail_citoyen.py` - Publik (structure standardisée)
- `scraper_demarches.py` - Formulaires dynamiques (Playwright)
- `scraper_heure_civique.py` - Plateforme externe

**Orchestrateur :** `tools/crawl_multi_platforms.py`
- Charge configuration plateformes
- Appelle scraper approprié selon URL
- Agrège résultats

---

## 📊 Métriques et Succès

### Métriques Techniques

**Performance :**
- Latence recherche RAG : 35-160ms (actuel) → 20-80ms (optimisé)
- Latence Claude API : 1-3s (Sonnet) → 0.5-1.5s (Haiku)
- Cache hit rate : À mesurer (objectif >30% pour questions fréquentes)

**Charge :**
- RAM : ~95 MB (actuel) → ~110-125 MB (généralisé)
- Disque : ~3.8 MB (actuel) → ~15-20 MB (généralisé)

### Métriques Prescription (À Définir)

**Indicateurs :**
- Sessions multi-personas (même IP, différents profils)
- Partage de liens (tracking URLs partagées)
- Feedback utilisateur ("Qui vous a parlé de cet assistant ?")
- Adoption par tranche d'âge (mesure inclusion numérique)

**Objectifs :**
- 67% des grand-mères prescrites par leur fille (cible)
- Réduction illectronisme senior : -10% en 1 an (ambitieux)

### Métriques Qualité

**RAG :**
- Précision recherche : À mesurer (objectif >80%)
- Couverture corpus : % requêtes avec réponse RAG (objectif >70%)

**Réponses :**
- Satisfaction utilisateur : 89% (Enfance) → maintenir sur généralisé
- Taux de fallback humain : À mesurer (objectif <10%)

---

## 🚧 Points Bloquants et Évolutivité

### Points Bloquants Actuels

1. **Pas de détection de personas**
   - Blocage : Nécessite création module `persona_detector.py`
   - Impact : Pas d'adaptation prompts/lexique selon persona

2. **Lexique hardcodé Enfance**
   - Blocage : `lexique_enfance.json` spécifique
   - Impact : Extension nécessite création lexiques par rubrique

3. **Prompt système fixe**
   - Blocage : Pas d'adaptation selon persona
   - Impact : Réponses non optimisées pour chaque profil

4. **Données structurées spécifiques**
   - Blocage : RPE, tarifs, écoles hardcodés pour Enfance
   - Impact : Nouveaux personas nécessitent nouvelles données

### Évolutivité (Ajout Personas)

**✅ Possible sans refonte si :**

1. **Architecture modulaire :**
   - Lexique : `lexique_{rubrique}.json` (chargement dynamique)
   - Prompts : Dictionnaire `PROMPTS_BY_PERSONA` (ajout entrée)
   - Données : `{persona}_data.json` (chargement conditionnel)
   - Détection : Matrice extensible (ajout dans dict)

2. **Pas de refonte nécessaire :**
   - Ajout persona = ajout fichiers JSON + entrée dans matrices
   - Code reste inchangé (architecture extensible)

**❌ Blocages si architecture non modulaire :**
- Hardcoding dans code → refonte nécessaire
- Pas de système de détection → impossible d'adapter

### Recommandations Évolutivité

1. **Créer `persona_detector.py` dès maintenant**
   - Matrice extensible (dictionnaire Python)
   - Ajout persona = ajout entrée dans dict

2. **Structurer lexique par rubrique**
   - `lexique_generalized.json` avec structure hiérarchique
   - Chargement à la demande

3. **Système de prompts modulaire**
   - Dictionnaire `PROMPTS_BY_PERSONA`
   - Fallback sur prompt par défaut si persona inconnu

4. **Données structurées conditionnelles**
   - Chargement selon persona détecté
   - Pas de chargement si données absentes (graceful degradation)

---

## 🎯 Plan d'Action Stratégique

### Phase 1 : MVP Généralisation (Court Terme)

**Objectif :** Généraliser à tout amiens.fr avec 2 personas prioritaires

**Actions :**
1. ✅ Scraping généralisé (déjà fait : `crawl_site_generalized.py`)
2. ✅ Corpus généralisé (déjà fait : détection automatique)
3. ⚠️ **Créer `persona_detector.py`** (à faire)
4. ⚠️ **Adapter prompts selon persona** (à faire)
5. ⚠️ **Étendre lexique** (à faire)
6. ⚠️ **Tester sur Actif 40-60 ans** (démarches administratives)

**Livrables :**
- Module détection personas
- Prompts adaptatifs
- Lexique généralisé
- Corpus multi-rubriques

### Phase 2 : Inclusion Numérique (Moyen Terme)

**Objectif :** Maximiser prescription familiale (Mère → Grand-mère)

**Actions :**
1. Analytics prescription (sessions multi-personas)
2. Optimisation expérience grand-mère (via prescription)
3. Fallback humain pour seniors (contact téléphonique)
4. Formation agents d'accueil (usage assistant)

**Livrables :**
- Dashboard analytics prescription
- Module fallback humain
- Documentation agents

### Phase 3 : APIs et Temps Réel (Long Terme)

**Objectif :** Enrichir avec données dynamiques

**Actions :**
1. Intégration Amienscope API (événements)
2. Intégration GTFS-RT (transports temps réel)
3. Enrichissement qualité air, déchets
4. Architecture hybride RAG + Enrichissement

**Livrables :**
- Module `data_enricher.py`
- Intégration APIs externes
- Tests temps réel

---

## 📚 Références

### Documents Sources

- **Architecture actuelle :** `docs/references/STACK_TECHNIQUE_I_AMIENS.md`
- **Personas :** `docs/analyses/Contexte PERSONAS DS.txt`
- **Contexte villes moyennes :** `docs/analyses/Ressources Doc pour stratégie Sys.txt`
- **Plateformes :** `docs/notes/à part amiens.fr et amiens tourisme, quels sont le.md`
- **Charge RAG :** `docs/references/ANALYSE_CHARGE_RAG_POLITIQUE_SYSTEME.md`
- **Plan généralisation :** `docs/references/PLAN_ACTION_COMPLET.md`

### APIs et Ressources

- **Amienscope API :** https://doc.amienscope.fr
- **GTFS Ametis :** https://transport.data.gouv.fr/datasets/ametis
- **Portail citoyen :** https://portail-citoyen.amiens.fr
- **Portail démarches :** https://demarches.amiens.fr

---

**Dernière mise à jour :** 2025-01-XX  
**Version :** 1.0

