# Clarifications des Améliorations

## 1. "Utiliser le lexique ou détection sémantique" - Comment ?

### Problème actuel (ligne 563)
```python
if rpe_data and any(term in question_text for term in ["rpe", "relais", "crèche", ...]):
```
Liste de termes en dur, fragile.

### Solution proposée
**Option A : Utiliser le lexique existant**
```python
# Au lieu de liste en dur, utiliser match_lexicon_entries()
lexicon_matches = match_lexicon_entries(payload.question, payload.normalized_question)
# Chercher si un match concerne "inscription" ou "crèche"
rpe_relevant = any(
    entry.get("terme_usager") in ["inscription", "inscrire", "crèche"] 
    for entry in lexicon_matches
)
if rpe_data and rpe_relevant:
    # injecter données RPE
```

**Option B : Détection sémantique (embeddings)**
```python
# Calculer similarité entre question et "inscription crèche RPE"
rpe_query = "inscription crèche relais petite enfance"
question_vec = embed_model.encode([payload.question])[0]
rpe_vec = embed_model.encode([rpe_query])[0]
similarity = np.dot(question_vec, rpe_vec)
if similarity > 0.6:  # seuil à ajuster
    # injecter données RPE
```

**Recommandation** : Option A (lexique) car plus simple et déjà en place.

---

## 2. "où" et "adresse" - Récolte automatique pour TOUT lieu

### Compréhension
- Si un lieu est cité dans la question OU dans les segments RAG
- ET que l'adresse n'est pas présente dans les segments
- ALORS récolter automatiquement l'adresse via OpenStreetMap/API

### Implémentation proposée
```python
def detect_mentioned_lieux(question: str, segments: List[RagSegment]) -> List[str]:
    """Détecte les lieux mentionnés dans question + segments."""
    lieux_mentions = []
    # Détecter dans question
    for lieu in lieux_data.get("lieux", []):
        if lieu["nom"].lower() in question.lower():
            lieux_mentions.append(lieu["nom"])
    # Détecter dans segments
    for seg in segments:
        for lieu in lieux_data.get("lieux", []):
            if lieu["nom"].lower() in (seg.content or "").lower():
                lieux_mentions.append(lieu["nom"])
    return list(set(lieux_mentions))

def check_address_present(lieu_nom: str, segments: List[RagSegment]) -> bool:
    """Vérifie si l'adresse est déjà dans les segments."""
    for seg in segments:
        if lieu_nom.lower() in (seg.content or "").lower():
            # Vérifier présence d'adresse (numéro + rue)
            if re.search(r'\d+.*(rue|avenue|boulevard|place)', seg.content, re.I):
                return True
    return False

def fetch_address_from_osm(lieu_nom: str) -> Optional[str]:
    """Récupère l'adresse via OpenStreetMap API."""
    # Utiliser Nominatim API
    import requests
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{lieu_nom} Amiens",
        "format": "json",
        "limit": 1
    }
    response = requests.get(url, params=params)
    if response.ok:
        data = response.json()
        if data:
            return data[0].get("display_name")
    return None
```

---

## 3. Tableaux tarifs - Quel est le problème ?

### Problème identifié
Les segments RAG contiennent les données tarifaires mais :
- Pas formatées en tableau
- Le modèle ne les présente pas clairement
- L'utilisateur doit chercher dans le texte

### Solution
**Extraire et formater automatiquement les tableaux depuis segments**

```python
def extract_tarif_table(segments: List[RagSegment]) -> Optional[str]:
    """Extrait un tableau de tarifs depuis les segments."""
    for seg in segments:
        content = seg.content or ""
        # Détecter structure tabulaire (lignes avec | ou tabulations)
        if "€" in content and ("tarif" in content.lower() or "prix" in content.lower()):
            # Parser le tableau
            lines = content.split("\n")
            table_rows = []
            for line in lines:
                if "€" in line or re.search(r'\d+', line):
                    # Extraire colonnes
                    parts = re.split(r'\s{2,}|\t|\|', line)
                    if len(parts) >= 2:
                        table_rows.append(parts)
            if table_rows:
                # Formater en HTML
                return format_table_html(table_rows)
    return None
```

**À faire** : Oui, c'est à implémenter.

---

## 4. Contacts - Carte interactive + OpenStreetMap

### Compréhension
- Utiliser carte interactive pour sélection secteur
- OpenStreetMap API pour mapping secteur → coordonnées
- Mapping coordonnées → RPE le plus proche

### Implémentation
```python
# 1. Carte interactive (frontend) : utilisateur clique sur secteur
# 2. Backend reçoit coordonnées ou nom secteur
# 3. Mapping secteur → RPE via données rpe_contacts.json
# 4. Retourner RPE correspondant

def get_rpe_for_secteur(secteur: str) -> Optional[Dict]:
    """Trouve le RPE correspondant à un secteur."""
    if not rpe_data:
        return None
    for rpe in rpe_data.get("rpe_list", []):
        if secteur.lower() in [s.lower() for s in rpe.get("secteurs", [])]:
            return rpe
    return None

def get_rpe_for_coordinates(lat: float, lon: float) -> Optional[Dict]:
    """Trouve le RPE le plus proche via coordonnées."""
    # Utiliser données RPE + calcul distance
    # Ou reverse geocoding OSM pour obtenir secteur
    pass
```

---

## 5. Base connaissances génériques - À narrowiser

### Compréhension
- Pas de recherche tous azimuts
- Recherche ciblée sur infos génériques législatives/administratives
- Exemple : "livret de famille requis pour inscription" (info générique, pas sur site)

### Approche proposée
1. **Détecter** quand info manque sur site (segments insuffisants)
2. **Identifier** le type d'info manquante (document, procédure, etc.)
3. **Chercher** dans base connaissances ciblée (pas Google général)
4. **Sources** : Service-public.fr, sites officiels administratifs

---

## 6. PDFs - Déjà convertis ?

### État actuel
- ✅ Script `extract_pdfs.py` existe
- ✅ Script `tools/ingest_menus.py` pour menus
- ❓ PDFs dans `data/raw/` : ont-ils été traités ?

### Vérification nécessaire
- Vérifier si PDFs sont dans `chunks_enfance_clean.json`
- Vérifier si PDFs sont dans `data/corpus_metadata.json`
- Si non, les traiter

---

## 7. Rassembler MD de tests

### Fichiers à rassembler
- `test_results_rag.md`
- `EXPLICATION_ALIGNEMENT.md`
- `AMELIORATIONS_RAG.md`
- `ANALYSE_HEURISTIQUES.md`
- `RESUME_ANALYSE.md`
- `ANALYSE_DOSSIERS.md`
- `CLARIFICATIONS.md` (ce fichier)

### Action : Créer dossier `tests/` et y déplacer

