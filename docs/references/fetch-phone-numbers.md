# Moyens de Récupérer des Numéros de Téléphone et Emails

## 📞 Sources Possibles (Téléphones et Emails)

### 1. OpenStreetMap (OSM) - Nominatim
**Avantages** :
- ✅ Gratuit, pas de clé API
- ✅ Données ouvertes
- ✅ Bonne couverture pour établissements publics

**Limitations** :
- ⚠️ Numéros de téléphone souvent absents dans OSM
- ⚠️ Données incomplètes pour écoles

**Méthode** :
```python
# Via Overpass API
query = """
[out:json];
area["name"="Amiens"]->.a;
node["amenity"="school"](area.a);
out;
"""
# Puis extraire :
# - tags["phone"] ou tags["contact:phone"]
# - tags["email"] ou tags["contact:email"]
```

**Taux de réussite estimé** :
- Téléphones : ~10-20% (faible)
- Emails : ~5-10% (très faible)

---

### 2. Scraping du Site Amiens.fr
**Avantages** :
- ✅ Source officielle
- ✅ Données à jour
- ✅ Numéros complets avec horaires

**Limitations** :
- ⚠️ Nécessite parsing HTML
- ⚠️ Structure peut changer
- ⚠️ Rate limiting à respecter

**Méthode** :
```python
# Scraper pages individuelles des écoles
# Exemple : https://www.amiens.fr/vivre-a-amiens/enfance/a-l-ecole
# Extraire patterns :
# - Téléphones : r'0[1-9]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{2}'
# - Emails : r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
```

**Taux de réussite estimé** :
- Téléphones : ~60-80% (moyen-élevé)
- Emails : ~40-60% (moyen)

---

### 3. API Carte Interactive Amiens
**URL** : `https://geo.amiens-metropole.com/adws/app/523da8c6-5dbc-11ec-9790-3dc5639e7001/`

**Avantages** :
- ✅ Source officielle
- ✅ Données complètes (adresses, téléphones, horaires)

**Limitations** :
- ⚠️ API non documentée
- ⚠️ Nécessite reverse engineering
- ⚠️ Problème SSL (voir `tools/check_carte_api.py`)

**Méthode** :
- Intercepter requêtes réseau (DevTools)
- Analyser endpoints API
- Extraire données JSON

**Taux de réussite estimé** : ~90% (si API accessible)

---

### 4. Google Places API
**Avantages** :
- ✅ Données complètes et à jour
- ✅ Téléphones souvent présents

**Limitations** :
- ❌ Nécessite clé API (payant après quota gratuit)
- ❌ Coût : ~$0.017 par requête

**Méthode** :
```python
# Via Google Places API
# place_id → place details → 
#   - phone_number
#   - website (puis scraper pour email)
```

**Taux de réussite estimé** :
- Téléphones : ~80-90% (élevé mais payant)
- Emails : ~30-50% (via website scraping)

---

### 5. Extraction depuis Corpus RAG
**Avantages** :
- ✅ Déjà disponible
- ✅ Pas de requête externe

**Limitations** :
- ⚠️ Données partielles
- ⚠️ Format variable

**Méthode** :
```python
# Chercher dans segments RAG avec regex
# Téléphones :
pattern_phone = r'0[1-9][\s\.-]?\d{2}[\s\.-]?\d{2}[\s\.-]?\d{2}[\s\.-]?\d{2}'
# Emails :
pattern_email = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
```

**Taux de réussite estimé** :
- Téléphones : ~30-40% (moyen)
- Emails : ~20-30% (faible-moyen)

---

## 🎯 Recommandation

**Stratégie en cascade** (comme pour les adresses) :

### Pour Téléphones :
1. **Corpus RAG** (gratuit, rapide)
2. **Scraping site Amiens.fr** (gratuit, fiable)
3. **OSM Overpass** (gratuit, faible taux)
4. **Google Places API** (payant, dernier recours)

### Pour Emails :
1. **Corpus RAG** (gratuit, rapide)
2. **Scraping site Amiens.fr** (gratuit, fiable)
3. **Patterns génériques** : `nom.ecole@amiens-metropole.com` (à tester)
4. **OSM Overpass** (gratuit, très faible taux)

---

## 📝 Exemple d'Implémentation

Voir `tools/fetch_contacts.py` (à créer) :
- Fonction `extract_phone_from_text()` : regex téléphones
- Fonction `extract_email_from_text()` : regex emails
- Fonction `fetch_contacts_from_osm()` : Overpass API (phone + email)
- Fonction `fetch_contacts_from_site()` : scraping Amiens.fr
- Fonction `get_contacts_for_school()` : cascade (phone + email)
- Fonction `generate_email_pattern()` : générer email probable si non trouvé

---

## ⚠️ Points d'Attention

1. **Format téléphone français** : `03 22 97 11 04` ou `0322971104`
2. **Format email** : Vérifier domaines officiels (`@amiens-metropole.com`, `@ac-amiens.fr`)
3. **Rate limiting** : Respecter les limites des APIs
4. **Données personnelles** : Vérifier RGPD si stockage
5. **Mise à jour** : Numéros et emails peuvent changer
6. **Emails génériques** : Certaines écoles peuvent avoir des emails génériques (ex: `ecole@amiens-metropole.com`)

