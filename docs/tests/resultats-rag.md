# Résultats des Tests RAG - Amiens Enfance

## Configuration
- **Stemmer** : Français (Snowball)
- **Poids BM25** : 1.0
- **Poids Cosine Similarity** : 0.6
- **Date** : Tests automatisés

---

## Test 1 : Comment inscrire mon enfant à la crèche ?

**Catégorie** : Inscription crèche

### Réponse

D'après les informations disponibles, les Relais Petite Enfance (RPE) à Amiens soutiennent les parents dans leur fonction d'employeur et accompagnent les assistants maternels. Vous pouvez contacter l'un des cinq RPE selon votre secteur d'habitation pour obtenir des renseignements sur l'inscription en crèche. 

Synthèse
Les RPE sont des points d'information pour les parents cherchant des solutions de garde d'enfants. 

Ouverture
Vous pouvez contacter directement le RPE de votre secteur par téléphone ou prendre rendez-vous pour des informations personnalisées.

### Alignement RAG

- **Statut** : `aligned`
- **Label** : aligned
- **Résumé** : Segments #2

### Sources (1)

1. **LES RELAIS PETITE ENFANCE - Amiens Métropole** - [https://www.amiens.fr/vivre-a-amiens/enfance/les-relais-petite-enfance](https://www.amiens.fr/vivre-a-amiens/enfance/les-relais-petite-enfance) (confiance: high)

### Question de suivi suggérée

> Quels sont les différents secteurs couverts par les RPE à Amiens ?

---

## Test 2 : Quels sont les tarifs de la cantine scolaire ?

**Catégorie** : Tarifs cantine

### Réponse

D'après les informations disponibles, les tarifs de la restauration scolaire à Amiens sont établis selon le quotient familial, avec 5 catégories allant de 0-391€ à 1341€ et plus. Les tarifs varient selon le nombre de jours par semaine (de 1 à 4 jours).

Synthèse
Les tarifs de cantine scolaire à Amiens fonctionnent par abonnement hebdomadaire avec des prix différenciés selon le quotient familial et le niveau scolaire (maternelle/élémentaire).

Ouverture
Pour connaître le tarif exact correspondant à votre situation, vous pouvez consulter le document complet des tarifs 2024-2025.

### Alignement RAG

- **Statut** : `aligned`
- **Label** : aligned
- **Résumé** : Segments #1, #2

### Sources (1)

1. **Synthese-tarif-2024-2025** - [https://www.amiens.fr/synthese-tarif-2024-2025](https://www.amiens.fr/synthese-tarif-2024-2025) (confiance: high)

### Question de suivi suggérée

> Quelles sont les modalités d'inscription à la cantine scolaire ?

---

## Test 3 : Horaires accueil périscolaire

**Catégorie** : Horaires périscolaire

### Réponse

D'après les informations disponibles, les études surveillées sont organisées tous les jours scolaires, pendant 1 heure après la fin des cours. Les horaires précis dépendent des horaires de classe spécifiques à chaque école.

Synthèse
L'accueil périscolaire en études surveillées s'adapte aux horaires de chaque établissement scolaire.

Ouverture
Pour connaître les horaires exacts de votre école, je vous invite à contacter directement l'établissement concerné.

### Alignement RAG

- **Statut** : `partial`
- **Label** : Informations partielles
- **Résumé** : Segments #1, #2, #3, #4, #5 - Les segments indiquent que les études surveillées ont lieu 1h après la fin des cours selon les horaires de chaque école, mais ne précisent pas les horaires exacts de l'accueil périscolaire complet.

### Sources (1)

1. **Les études surveillées** - [https://www.amiens.fr/vivre-a-amiens/enfance/a-l-ecole/les-etudes-surveillees](https://www.amiens.fr/vivre-a-amiens/enfance/a-l-ecole/les-etudes-surveillees) (confiance: high)

### Question de suivi suggérée

> Souhaitez-vous des informations sur les modalités d'inscription aux études surveillées ?

---

## Test 4 : Je veux inscrire mon enfant à une crèche

**Catégorie** : Variation inscription

### Réponse

Pour inscrire votre enfant en crèche à Amiens, vous pouvez contacter les Relais Petite Enfance (RPE). Ces relais soutiennent les parents dans leur fonction d'employeur et peuvent vous orienter dans vos démarches d'inscription en crèche. Les RPE d'Amiens Métropole disposent de cinq animatrices réparties sur différents secteurs de la ville pour vous accompagner. Vous pouvez contacter le RPE de votre secteur (Babillages, Germaine Dulac, RPE itinérant, Chemin des Plantes ou Pigeon Vole) pour obtenir des informations personnalisées.

### Alignement RAG

- **Statut** : `aligned`
- **Label** : aligned
- **Résumé** : Segments #1, #2, #3, #4, #5

### Sources (1)

1. **LES RELAIS PETITE ENFANCE - Amiens Métropole** - [https://www.amiens.fr/vivre-a-amiens/enfance/les-relais-petite-enfance](https://www.amiens.fr/vivre-a-amiens/enfance/les-relais-petite-enfance) (confiance: high)

### Question de suivi suggérée

> Dans quel quartier d'Amiens habitez-vous pour que je puisse vous indiquer le RPE le plus proche ?

---

## Test 5 : Inscriptions aux crèches amiénoises

**Catégorie** : Variation pluriel

### Réponse

Pour inscrire votre enfant dans une crèche à Amiens, vous devez passer par l'Accueil Petite Enfance situé à l'espace Dewailly. Une éducatrice de jeunes enfants vous accompagnera personnellement pour trouver la solution la plus adaptée à votre situation et procédera aux pré-inscriptions pour les crèches municipales. Les rendez-vous sont obligatoires pour les inscriptions en crèche municipale à Amiens. L'Accueil Petite Enfance vous informe également sur tous les autres modes d'accueil disponibles dans la ville.

### Alignement RAG

- **Statut** : `fully_aligned`
- **Label** : Réponse complètement alignée
- **Résumé** : Segment #4 utilisé pour fournir les informations sur l'Accueil Petite Enfance, le processus d'inscription et la prise de rendez-vous.

### Sources (1)

1. **Faire garder son enfant - Amiens Métropole** - [https://www.amiens.fr/vivre-a-amiens/enfance/faire-garder-son-enfant](https://www.amiens.fr/vivre-a-amiens/enfance/faire-garder-son-enfant) (confiance: high)

### Question de suivi suggérée

> Quels documents sont nécessaires pour l'inscription en crèche à Amiens ?

---

## Test 6 : Comment faire garder mon enfant le mercredi ?

**Catégorie** : Garde mercredi

### Réponse

Pour faire garder votre enfant le mercredi à Amiens, vous pouvez vous adresser aux Relais Petite Enfance (RPE). Ces services vous accompagnent dans la recherche et l'emploi d'un assistant maternel agréé ou d'une garde d'enfant à domicile.

Synthèse
Les RPE sont votre point de contact principal pour trouver une solution de garde adaptée à vos besoins du mercredi.

Ouverture
Avez-vous besoin de connaître les coordonnées précises des RPE d'Amiens?

### Alignement RAG

- **Statut** : `aligned`
- **Label** : aligned
- **Résumé** : Segments #1, #2, #3, #4, #5

### Sources (1)

1. **Faire garder son enfant** - [https://www.amiens.fr/vivre-a-amiens/enfance/faire-garder-son-enfant](https://www.amiens.fr/vivre-a-amiens/enfance/faire-garder-son-enfant) (confiance: high)

### Question de suivi suggérée

> Quels sont les horaires d'ouverture des Relais Petite Enfance à Amiens?

---

## Test 7 : Tarif centre de loisirs vacances été

**Catégorie** : Tarifs ALSH

### Réponse

D'après les informations disponibles, je ne trouve pas de tarifs spécifiques pour les centres de loisirs pendant les vacances d'été. Les segments mentionnent uniquement les tarifs pour l'accueil du mercredi et les petites vacances scolaires, mais pas explicitement pour l'été.

Synthèse
Les informations sur les tarifs des centres de loisirs pour les vacances d'été ne sont pas présentes dans les segments fournis.

Ouverture
Je vous invite à contacter directement le service Enfance de la ville d'Amiens pour obtenir les tarifs spécifiques aux vacances d'été.

### Alignement RAG

- **Statut** : `incomplete`
- **Label** : Informations partielles
- **Résumé** : Segments #1, #2, #3, #4, #5 mentionnent les centres de loisirs et certains tarifs, mais aucun ne précise les tarifs spécifiques pour les vacances d'été

### Sources (2)

1. **Synthèse des tarifs 2024-2025** - [https://www.amiens.fr/synthese-tarif-2024-2025](https://www.amiens.fr/synthese-tarif-2024-2025) (confiance: medium)
2. **Centres de loisirs - Liste des structures** - [https://www.amiens.fr/vivre-a-amiens/enfance/centres-de-loisirs/liste-des-structures](https://www.amiens.fr/vivre-a-amiens/enfance/centres-de-loisirs/liste-des-structures) (confiance: low)

### Question de suivi suggérée

> Comment puis-je inscrire mon enfant aux centres de loisirs pour les vacances d'été à Amiens ?

---

## Test 8 : Quel est le prix pour les activités pendant les vacances ?

**Catégorie** : Synonymes

### Réponse

D'après les informations disponibles, je ne peux pas vous indiquer les tarifs précis des activités pendant les vacances. Les segments mentionnent uniquement que la ville d'Amiens propose d'accueillir les enfants durant les mercredis et les petites vacances scolaires dans des accueils de loisirs maternels et primaires.

Synthèse
Les informations sur les prix des activités pendant les vacances ne sont pas présentes dans les segments fournis.

Ouverture
Pour connaître les tarifs, je vous invite à consulter directement le site officiel de la ville d'Amiens ou à contacter le service enfance.

### Alignement RAG

- **Statut** : `missing_information`
- **Label** : Information non disponible
- **Résumé** : Segments #1, #2, #3, #4, #5 mentionnent l'existence d'accueils de loisirs pendant les vacances mais ne contiennent aucune information sur les tarifs.

### Sources (1)

1. **Liste des structures - Centres de loisirs** - [https://www.amiens.fr/vivre-a-amiens/enfance/centres-de-loisirs/liste-des-structures](https://www.amiens.fr/vivre-a-amiens/enfance/centres-de-loisirs/liste-des-structures) (confiance: high)

### Question de suivi suggérée

> Quels sont les horaires d'ouverture des centres de loisirs pendant les vacances ?

---

## Test 9 : DRE dispositif réussite éducative

**Catégorie** : Terme technique

### Réponse

Le Dispositif de Réussite Éducative (DRE) est un programme destiné aux enfants et jeunes de 2 à 16 ans (et leurs familles) qui habitent dans les territoires prioritaires de la politique de la ville ou sont scolarisés en établissement REP+. Il s'adresse spécifiquement aux jeunes présentant des signes de fragilité dans leur parcours éducatif, que ce soit dans les domaines éducatifs, scolaires, socio-culturels ou de santé. 

Synthèse
Le DRE d'Amiens est piloté par la Caisse des Écoles de la Ville et propose des parcours personnalisés pour accompagner les enfants en difficulté. 

Ouverture
Le parcours personnalisé de Réussite Éducative est construit comme une co-construction s'appuyant sur différents outils adaptés aux besoins de l'enfant.

### Alignement RAG

- **Statut** : `aligned`
- **Label** : aligned
- **Résumé** : Segments #1, #2, #3, #4, #5

### Sources (1)

1. **Le Dispositif de Réussite Éducative (DRE)** - [https://www.amiens.fr/vivre-a-amiens/enfance/a-l-ecole/le-dispositif-de-reussite-educative-dre](https://www.amiens.fr/vivre-a-amiens/enfance/a-l-ecole/le-dispositif-de-reussite-educative-dre) (confiance: high)

### Question de suivi suggérée

> Comment peut-on inscrire un enfant au Dispositif de Réussite Éducative à Amiens ?

---

## Test 10 : PAI projet accueil individualisé

**Catégorie** : Acronyme

### Réponse

Le Projet d'Accueil Individualisé (PAI) est un dispositif mis en place pour les élèves ayant des troubles de santé nécessitant des aménagements spécifiques pendant leur scolarité. Il s'agit d'un document écrit établi par le médecin scolaire à partir des informations médicales fournies par la famille. 

Synthèse
Le PAI permet d'organiser les aménagements nécessaires (traitement médical, régime alimentaire ou protocole d'urgence) dans tous les lieux fréquentés par l'élève durant sa scolarité. 

Ouverture
Ce dispositif assure la continuité de la scolarité de l'enfant tout en garantissant sa sécurité et sa prise en charge médicale adaptée.

### Alignement RAG

- **Statut** : `aligned`
- **Label** : Aligned
- **Résumé** : Segments #1, #2, #3, #4, #5

### Sources (1)

1. **Projet d'Accueil Individualisé - Amiens Métropole** - [https://www.amiens.fr/vivre-a-amiens/enfance/a-l-ecole/projet-d-accueil-individualise](https://www.amiens.fr/vivre-a-amiens/enfance/a-l-ecole/projet-d-accueil-individualise) (confiance: high)

### Question de suivi suggérée

> Comment faire une demande de PAI pour mon enfant à Amiens ?

---

## Statistiques

- **Tests réussis** : 10/10
- **Tests échoués** : 0/10

