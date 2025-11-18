# Tour du Site - Sources Disponibles et Manquantes

## ✅ Sources TROUVÉES dans le corpus

### 1. PDFs - Déjà indexés
- ✅ `COUPON+INSCRIPTION+3+SEMAINES+AOUT+2025.pdf` → dans corpus_metadata.json
- ✅ `COUPON+INSCRIPTION+4+SEMAINES+AOUT+2025.pdf` → dans corpus_metadata.json
- ✅ `COUPON+INSCRIPTION+JUILLET+2025.pdf` → dans corpus_metadata.json
- ✅ `LISTE+ALSH+ETE+2025.pdf` → à vérifier
- ✅ Menus (PDF/XLS) → traités par `tools/ingest_menus.py`

**Status** : PDFs sont convertis et indexés ✅

### 2. Informations générales écoles
- ✅ "78 écoles publiques" mentionnées
- ✅ "5 secteurs géographiques : Est – Ouest – Nord - Sud et Centre"
- ✅ Répartition : 32 maternelles, 30 élémentaires, 16 primaires
- ✅ "carte des écoles d'Amiens" mentionnée (mais pas de données détaillées)

**URL** : `https://www.amiens.fr/vivre-a-amiens/enfance/a-l-ecole`

### 3. Contacts RPE
- ✅ Liste complète des 5 RPE avec adresses, téléphones, emails
- ✅ Secteurs couverts par chaque RPE
- ✅ Disponible dans `data/rpe_contacts.json`

### 4. Tarifs cantine
- ✅ "Synthese-tarif-2024-2025" mentionnée
- ✅ "5 catégories selon quotient familial"
- ⚠️ Tableau détaillé : à vérifier dans segments

---

## ❌ Sources MANQUANTES (non trouvées dans corpus)

### 1. Liste détaillée des 78 écoles avec contacts
**Manque** :
- Noms des écoles
- Adresses des écoles
- Téléphones des écoles
- Secteur de chaque école
- Contacts services périscolaires par école
https://geo.amiens-metropole.com/adws/app/523da8c6-5dbc-11ec-9790-3dc5639e7001/index.html?context=vwYB
Tout se trouve sur la carte. Comment touchcer l'API ? j'ai trouvé ça mais je ne pense pas que cela t'aide beaucoup...
Repli stratégique : requête libre sur API OSM 
[out:json];
area["name"="Amiens"]->.a;
node["amenity"="school"](area.a);
out;

**Où chercher** :
- Page "carte des écoles d'Amiens" (mentionnée mais pas de données
https://geo.amiens-metropole.com/adws/app/523da8c6-5dbc-11ec-9790-3dc5639e7001/index.html
- Pages individuelles par secteur
- Fichiers téléchargeables (PDF/Excel)

### 2. Tarifs ALSH été spécifiques
**Manque** :
- Tarifs centres de loisirs pour vacances d'été (vs mercredi/petites vacances)
- Distinction ALSH été vs autres périodes y a pas de distincition, je le sais. Les centres sont fixes les fonctionnaires sont toujours sur leur centre

**Où chercher** :
- `LISTE+ALSH+ETE+2025.pdf` (à vérifier contenu) tu l'as /Users/francois-jeandazin/Documents/En Cours/Crea/NUX/I Amiens/data/raw/LISTE+ALSH+ETE+2025.pdf et tu l'as traité déjà, non ?
- Page "Centres de loisirs" → section été dans pdf traités si traités, sinon à faire d'urgence
- Synthèse tarifs (vérifier si section été présente) idem

### 3. Tableau tarifs cantine formaté
**Manque** :
- Tableau structuré avec toutes les catégories QF là : https://www.amiens.fr/Vivre-a-Amiens/Enfance/a-table/Les-tarifs  PDF recap ajouté /Users/francois-jeandazin/Documents/En Cours/Crea/NUX/I Amiens/data/raw/syn+tarif+2024+2025+pour+contrat (1).pdf
- Tarifs par niveau (maternelle/élémentaire)
- Tarifs par nombre de jours

**Où chercher** :
- Document "Synthese-tarif-2024-2025" (PDF ?) ajouté /Users/francois-jeandazin/Documents/En Cours/Crea/NUX/I Amiens/data/raw/syn+tarif+2024+2025+pour+contrat (1).pdf
- Page tarifs restauration scolaire

### 4. Coordonnées services périscolaires
**Manque** :
- Contacts par école pour études surveillées
- Contacts accueil périscolaire matin/soir
- Horaires détaillés par établissement Trick API OSM

**Où chercher** :
- Pages individuelles écoles
- Section "Avant/Après l'école" https://www.amiens.fr/Vivre-a-Amiens/Enfance/Avant-Apres-l-ecole (pauvre) requêtes par proxy="/autocomplete/get-datas/(node)/3169" donne école > horaires Comment r"cupérer ça, mystère ?
- Fichiers contacts téléchargeables

### 5. Adresses complètes lieux
**Manque** :
- Adresse précise Espace Dewailly (si pas dans segments) Tric OSM
- Autres lieux d'accueil (si mentionnés sans adresse)

**Solution** : OpenStreetMap API (à implémenter)
onprend l'adresse sur le site si c'est là, sinon, on cherche sur l'API libre dès qu'un lmieu remonte, on save dazns database RAG

### 6. Informations génériques législatives
**Manque** :
- Documents requis pour inscriptions (livret de famille, etc.)

- Procédures administratives génériques
https://www.amiens.fr/Vivre-a-Amiens/Enfance/a-l-ecole/Inscriptions-scolaires2
**Solution** : Base connaissances externe ciblée (Service-public.fr, etc.) à implémenter

---

## 🔍 Pages à Explorer (non indexées ?)

### À vérifier sur le site :
1. **Carte interactive écoles** : `https://www.amiens.fr/vivre-a-amiens/enfance/a-l-ecole`
   - Peut contenir données JSON/API
   - Carte cliquable → données écoles je nai pas vu que les données soient ouvertes donc trick OSM pu trick G MAP si nécessaire

2. **Liste téléchargeable écoles** :
   - PDF/Excel avec liste complète voir plus haut https://www.amiens.fr/Vivre-a-Amiens/Enfance/Avant-Apres-l-ecole (pauvre) requêtes par proxy="/autocomplete/get-datas/(node)/3169" donne école > horaires Comment r"cupérer ça, mystère ?
   - Fichier "annuaire-ecoles-amiens.pdf" idem

3. **Page tarifs détaillée** :
   - `https://www.amiens.fr/synthese-tarif-2024-2025` voir plus haut PDf dans raw
   - Vérifier si tableau complet présent

4. **Pages par secteur** :
   - Écoles par secteur (Est, Ouest, Nord, Sud, Centre)
   Un secteur sur carte interactive : voir /Users/francois-jeandazin/Documents/En Cours/Crea/NUX/I Amiens/data/raw/js OSM
   - Contacts par secteur idem

5. **Section "Un été à Amiens"** :
   - Activités vacances été
   - Tarifs activités été
   - Rubrique Sports + Enfance
   Regharde là si tu trouves une piste

---

## 📋 Actions Recommandées

### Phase 1 : Vérifier PDFs existants
1. ✅ Vérifier contenu `LISTE+ALSH+ETE+2025.pdf` dans corpus
2. ✅ Vérifier si tableau tarifs dans segments existants

### Phase 2 : Explorer pages non indexées
1. Scraper carte interactive écoles (si données JSON)
2. Télécharger fichiers annuaires/listes
3. Explorer section "Un été à Amiens"

### Phase 3 : Compléter avec APIs externes
1. OpenStreetMap pour adresses manquantes
2. Base connaissances génériques (ciblée)

---

## 🎯 Priorités

1. **Urgent** : Liste écoles avec contacts (Test 3)
2. **Important** : Tarifs ALSH été (Test 7)
3. **Important** : Tableau tarifs cantine formaté (Test 2)
4. **Nice to have** : Adresses via OSM (Test 5)

