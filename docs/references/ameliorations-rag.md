# Améliorations RAG - Analyse par Test

## Test 1 : Inscription crèche - Liste des RPE

### Problème
La réponse mentionne "les cinq RPE" mais ne liste pas les noms, secteurs et contacts.

### Solution
**Ajouter en dur dans le prompt** la liste complète des RPE avec leurs informations :
- Babillages
- Germaine Dulac  
- RPE itinérant
- Chemin des Plantes
- Pigeon Vole

**Action** : Créer un fichier `data/rpe_contacts.json` et l'injecter dans le prompt quand la question concerne les RPE.

---

## Test 2 : Tarifs cantine - Tableau en dur

### Problème
La réponse mentionne les catégories mais ne présente pas le tableau complet des tarifs.

### Solution
**Extraire et formater le tableau des tarifs** depuis les segments RAG et l'inclure directement dans la réponse.

**Action** : 
1. Détecter les questions sur tarifs
2. Extraire les tableaux/chiffres des segments
3. Formater en tableau Markdown/HTML dans la réponse

---

## Test 3 : Horaires périscolaire - Sources manquantes

### Problème
Pas de liste des établissements avec contacts dans la réponse finale.

### Solution
**Recherche élargie** pour trouver :
- Liste des écoles avec contacts
- Coordonnées des services périscolaires
- Question de suivi : "Quel est votre secteur ?" pour orienter vers le bon contact

**Action** : Améliorer la recherche sémantique pour inclure les pages de contacts/établissements.

---

## Test 4 : Renseignements animatrices RPE - Recherche hors site

### Problème
Infos génériques (ex: livret de famille pour inscription) absentes du site mais disponibles ailleurs.

### Solution
**Politique dataset élargie** :
- Recherche thématique hors contraintes strictes du RAG site
- Intégrer des connaissances génériques législatives/administratives
- Exemple : "livret de famille requis" même si pas sur le site

**Action** : Créer un module de recherche complémentaire pour infos génériques (base de connaissances législative).

---

## Test 5 : Espace Dewailly - Adresse manquante

### Problème
Les nouveaux arrivants ne savent pas où se trouve l'Espace Dewailly.

### Solution
**Recherche d'adresse automatique** :
- Si mention d'un lieu sans adresse dans les segments
- Rechercher l'adresse complète (géolocalisation, site officiel)
- Ajouter dans la réponse : "L'Espace Dewailly se trouve au [adresse]"

**Action** : Module de recherche d'adresses/complément d'infos géographiques.

---

## Test 6 : Question de suivi secteur + RPE

### Problème
Question de suivi générique, pas de recherche du bon RPE selon secteur.

### Solution
**Question de suivi intelligente** :
- "Quel est votre secteur d'habitation ?"
- Recherche automatique du RPE correspondant au secteur
- Mapping secteur → RPE

**Action** : Créer un mapping secteur/RPE et l'utiliser pour les questions de suivi.

---

## Test 7 : Tarifs ALSH été - Recherche approfondie

### Problème
Tarifs cachés quelque part, pas trouvés par la recherche actuelle.

### Solution
**Recherche élargie** :
- Chercher dans tous les segments liés aux centres de loisirs
- Rechercher "tarif été", "vacances été", "ALSH été"
- Vérifier les PDFs dans `data/raw/`

**Action** : Améliorer l'indexation des PDFs et la recherche dans les documents non structurés.

---

## Test 8 : Activités vacances - Terminologie

### Problème
"Activités pendant les vacances" ne matche pas bien avec "CLSH" ou "centres de loisirs".

### Solution
**Recherche multi-terminologie** :
- Chercher "CLSH" + "centres de loisirs" + "activités"
- Rechercher dans rubrique "Sports" 
- Recherche "un été à amiens" dans tout le site
- Expansion de requête avec synonymes

**Action** : 
1. Améliorer le lexique avec synonymes (activités = CLSH = centres de loisirs)
2. Recherche cross-rubriques (sports + enfance)

---

## Test 9 : DRE - Question inversée

### Problème
Personne ne demande "qu'est-ce que DRE" directement. Il faut identifier les questions qui mènent à ce champ.

### Solution
**Recherche inverse** :
- Identifier les questions utilisateur qui devraient mener à DRE
- Exemples : "mon enfant a des difficultés scolaires", "aide pour réussite éducative"
- Améliorer la détection d'intention pour ces cas

**Action** : 
1. Créer un mapping questions → dispositifs (DRE, PAI, etc.)
2. Améliorer la détection d'intention pour les besoins éducatifs

---

## Test 10 : PAI - Même problème

### Solution identique au Test 9
- Mapping questions → PAI
- Détection : "trouble de santé", "allergie", "aménagement scolaire"

---

## Implémentation Prioritaire

### Phase 1 : Données en dur
1. ✅ Liste RPE (Test 1)
2. ✅ Tableau tarifs (Test 2)
3. ✅ Mapping secteur/RPE (Test 6)

### Phase 2 : Recherche améliorée
4. ✅ Recherche contacts/établissements (Test 3)
5. ✅ Recherche adresses (Test 5)
6. ✅ Recherche multi-terminologie (Test 8)

### Phase 3 : Recherche hors site
7. ⏳ Base connaissances génériques (Test 4)
8. ⏳ Recherche approfondie PDFs (Test 7)

### Phase 4 : Détection intelligente
9. ⏳ Mapping questions → dispositifs (Test 9, 10)

