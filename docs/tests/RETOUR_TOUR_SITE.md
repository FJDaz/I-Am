# Retour sur le Tour du Site - Analyse des Commentaires

## ✅ Points Clarifiés

### 1. Tarifs ALSH été - Pas de distinction
**Ton commentaire** : "y a pas de distinction, je le sais. Les centres sont fixes les fonctionnaires sont toujours sur leur centre"

**Impact** :
- ✅ Pas besoin de chercher tarifs spécifiques été vs autres périodes
- ✅ Les tarifs sont les mêmes toute l'année pour chaque centre
- ✅ Le PDF `LISTE+ALSH+ETE+2025.pdf` liste juste les centres ouverts en été, pas de tarifs différents

**Action** : Vérifier si le PDF est traité, sinon l'ajouter au corpus.

---

### 2. Tableau tarifs cantine - PDF trouvé
**Ton commentaire** : PDF ajouté `syn+tarif+2024+2025+pour+contrat (1).pdf`

**Action immédiate** :
1. ✅ Vérifier si PDF est dans `data/raw/`
2. ✅ Traiter avec `extract_pdfs.py` si pas déjà fait
3. ✅ Extraire tableau structuré pour injection dans réponses

**URL page** : `https://www.amiens.fr/Vivre-a-Amiens/Enfance/a-table/Les-tarifs`

---

### 3. Carte interactive écoles - API non ouverte
**Ton commentaire** : "je n'ai pas vu que les données soient ouvertes donc trick OSM ou trick G MAP si nécessaire"

**Solutions identifiées** :
1. **Overpass API OSM** (requête fournie) :
   ```
   [out:json];
   area["name"="Amiens"]->.a;
   node["amenity"="school"](area.a);
   out;
   ```
   - ✅ Récupère toutes les écoles d'Amiens
   - ✅ Données : nom, coordonnées, adresse
   - ⚠️ Manque : téléphone, contacts, secteur administratif

2. **Fichier JS OSM** : Tu mentionnes `/data/raw/js OSM` → à examiner

3. **Carte interactive** : `https://geo.amiens-metropole.com/adws/app/523da8c6-5dbc-11ec-9790-3dc5639e7001/index.html`
   - Données non ouvertes mais peut-être extractibles depuis le JS

**Stratégie** :
- Combiner OSM (adresses, coordonnées) + scraping site (contacts, secteurs)
- Sauvegarder dans base RAG structurée

---

### 4. Coordonnées périscolaires - Endpoint mystérieux
**Ton commentaire** : `proxy="/autocomplete/get-datas/(node)/3169"` donne école > horaires. "Comment récupérer ça, mystère ?"

**Analyse** :
- Endpoint interne de l'application
- Probablement appelé en AJAX depuis la page
- Nécessite reverse engineering du JS ou interception réseau

**Solutions** :
1. **Intercepter requêtes réseau** (DevTools) pour voir format exact
2. **Scraper le JS** de la page pour trouver l'API
3. **Fallback OSM** : Récupérer écoles via OSM, puis chercher horaires sur site par école

**URL page** : `https://www.amiens.fr/Vivre-a-Amiens/Enfance/Avant-Apres-l-ecole`

---

### 5. Adresses - Stratégie claire
**Ton commentaire** : "on prend l'adresse sur le site si c'est là, sinon, on cherche sur l'API libre dès qu'un lieu remonte, on save dans database RAG"

**Implémentation proposée** :
```python
def get_address_for_lieu(lieu_nom: str, segments: List[RagSegment]) -> Optional[str]:
    # 1. Chercher dans segments RAG d'abord
    for seg in segments:
        if lieu_nom.lower() in (seg.content or "").lower():
            # Extraire adresse (regex numéro + rue)
            address = extract_address_from_text(seg.content)
            if address:
                return address
    
    # 2. Si pas trouvé, chercher sur OSM
    address = fetch_address_from_osm(lieu_nom + " Amiens")
    if address:
        # Sauvegarder dans database RAG pour prochaines fois
        save_to_rag_database(lieu_nom, address)
        return address
    
    return None
```

**Base de données RAG** : Créer `data/lieux_cache.json` pour stocker adresses récupérées.

---

### 6. Section "Un été à Amiens"
**Ton commentaire** : "Regarde là si tu trouves une piste"

**À explorer** :
- Rubrique Sports + Enfance
- Activités vacances été
- Tarifs activités été

**Action** : Scraper cette section pour voir si données utiles.

---

## 🎯 Plan d'Action Priorisé

### Phase 1 : Traiter PDFs existants (URGENT)
1. ✅ Vérifier `LISTE+ALSH+ETE+2025.pdf` dans corpus
2. ✅ Traiter `syn+tarif+2024+2025+pour+contrat (1).pdf` si pas fait
3. ✅ Extraire tableau tarifs structuré

### Phase 2 : API OSM pour écoles (IMPORTANT)
1. ✅ Implémenter requête Overpass fournie
2. ✅ Récupérer écoles avec adresses/coordonnées
3. ✅ Combiner avec données site (contacts, secteurs) si possible
4. ✅ Créer `data/ecoles_amiens.json` structuré

### Phase 3 : Endpoint autocomplete périscolaire (À INVESTIGUER)
1. ⏳ Analyser JS de la page "Avant-Après l'école"
2. ⏳ Intercepter requêtes réseau pour comprendre format
3. ⏳ Implémenter scraper si possible
4. ⏳ Fallback : OSM + recherche manuelle par école

### Phase 4 : Système adresses dynamique
1. ⏳ Implémenter `get_address_for_lieu()` avec cache
2. ⏳ Créer `data/lieux_cache.json`
3. ⏳ Intégrer dans `build_prompt()` pour injection automatique

### Phase 5 : Section "Un été à Amiens"
1. ⏳ Explorer section Sports + Enfance
2. ⏳ Scraper activités été si pertinentes

---

## 🔧 Implémentations Techniques Nécessaires

### 1. Module OSM
```python
# tools/fetch_osm_data.py
import requests

def fetch_schools_from_osm(city="Amiens"):
    """Récupère écoles via Overpass API."""
    query = f"""
    [out:json];
    area["name"="{city}"]->.a;
    node["amenity"="school"](area.a);
    out;
    """
    # Appel API Overpass
    # Parse JSON
    # Retourne liste écoles avec nom, lat, lon, adresse
```

### 2. Module extraction tableaux
```python
# tools/extract_tables.py
def extract_tarif_table_from_pdf(pdf_path):
    """Extrait tableau tarifs depuis PDF."""
    # Utiliser pdfplumber ou camelot
    # Parser tableau
    # Retourner structure JSON/HTML
```

### 3. Module cache adresses
```python
# tools/address_cache.py
def get_cached_address(lieu_nom):
    """Récupère adresse depuis cache ou OSM."""
    # Vérifier cache
    # Si absent, OSM
    # Sauvegarder cache
```

---

## ❓ Questions à Résoudre

1. **Endpoint autocomplete** : Comment récupérer les données ?
   - Option A : Reverse engineer le JS
   - Option B : Intercepter requêtes réseau
   - Option C : Fallback OSM + scraping manuel

2. **Fichier JS OSM** : Que contient `/data/raw/js OSM` ?
   - À examiner pour voir si données extractibles

3. **Section "Un été à Amiens"** : Où exactement ?
   - URL précise à trouver
   - Contenu à analyser

---

## 📊 État des Sources

| Source | Status | Action |
|--------|--------|--------|
| PDF tarifs cantine | ✅ Trouvé | Traiter si pas fait |
| PDF ALSH été | ✅ Trouvé | Vérifier traitement |
| Carte écoles | ⚠️ API fermée | OSM + scraping |
| Endpoint périscolaire | ❓ Mystère | Investiguer |
| Adresses lieux | ✅ Stratégie claire | Implémenter OSM + cache |
| Section été | ❓ À explorer | Scraper |

---

## 🚀 Prochaines Étapes Immédiates

1. **Vérifier PDFs** : Sont-ils dans le corpus ?
2. **Implémenter OSM** : Module pour récupérer écoles
3. **Investiger endpoint** : Analyser JS/requêtes réseau
4. **Créer cache adresses** : Système de sauvegarde

