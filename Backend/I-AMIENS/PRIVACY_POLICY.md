# Politique de Confidentialité - I-Amiens

**Dernière mise à jour :** 22 novembre 2024

## Introduction

I-Amiens ("nous", "notre", "l'extension") est une extension Chrome qui fournit un assistant intelligent pour la rubrique enfance du site amiens.fr. Cette politique de confidentialité explique comment nous traitons les données lorsque vous utilisez notre extension.

## Collecte de Données

### Données Collectées

**I-Amiens ne collecte, ne stocke ni ne transmet aucune donnée personnelle identifiante.**

L'extension fonctionne de la manière suivante :

1. **Questions de l'utilisateur** : Lorsque vous posez une question via l'interface de l'extension, cette question est envoyée au serveur backend (hébergé sur Railway) pour obtenir une réponse. Cette question n'est pas stockée de manière persistante dans l'extension.

2. **Historique de conversation** : L'extension maintient un historique temporaire de la conversation en mémoire (limité à 12 échanges) uniquement pour améliorer le contexte des réponses. Cet historique :
   - N'est stocké que dans la mémoire du navigateur
   - Est effacé lorsque vous fermez l'onglet ou le navigateur
   - N'est jamais transmis à des tiers
   - N'est pas sauvegardé de manière persistante

3. **Données locales** : L'extension utilise des données locales embarquées (corpus de documents, lexique) pour améliorer les réponses. Ces données sont stockées localement dans l'extension et ne sont jamais transmises.

### Données NON Collectées

I-Amiens **ne collecte pas** :
- ❌ Informations d'identification personnelle (nom, adresse, email, etc.)
- ❌ Informations de santé
- ❌ Informations financières
- ❌ Informations d'authentification
- ❌ Communications personnelles
- ❌ Données de localisation (GPS, adresse IP)
- ❌ Historique de navigation web
- ❌ Activité utilisateur (clics, mouvements de souris, etc.)
- ❌ Contenu des pages web visitées

## Utilisation des Données

Les questions que vous posez sont utilisées **uniquement** pour :
- Générer des réponses pertinentes via le système RAG (Retrieval-Augmented Generation)
- Améliorer le contexte de la conversation en cours (historique temporaire)

## Stockage des Données

- **Extension** : Aucune donnée n'est stockée de manière persistante dans l'extension
- **Backend Railway** : Les questions peuvent être temporairement traitées par le serveur backend pour générer des réponses. Nous ne conservons pas ces données de manière permanente.

## Partage des Données

**I-Amiens ne vend, ne loue ni ne partage vos données avec des tiers.**

Les questions sont envoyées uniquement au serveur backend Railway pour obtenir des réponses, et ne sont pas utilisées à d'autres fins.

## Sécurité

Nous nous efforçons de protéger vos données en :
- Utilisant des connexions HTTPS sécurisées
- Ne stockant aucune donnée personnelle
- Limitant la collecte au strict minimum nécessaire au fonctionnement de l'extension

## Vos Droits

Comme nous ne collectons pas de données personnelles identifiables, il n'y a pas de données à supprimer ou à modifier. Si vous avez des questions ou des préoccupations, vous pouvez nous contacter.

## Modifications de cette Politique

Nous pouvons mettre à jour cette politique de confidentialité occasionnellement. La date de dernière mise à jour est indiquée en haut de ce document.

## Contact

Pour toute question concernant cette politique de confidentialité, vous pouvez nous contacter via le dépôt GitHub du projet ou le site web officiel.

## Conformité

Cette extension est conforme aux politiques du Chrome Web Store et respecte les réglementations en vigueur sur la protection des données.

---

**Note importante** : Cette extension fonctionne uniquement sur le site `https://www.amiens.fr` et nécessite un accès au backend Railway pour fonctionner. Aucune donnée n'est collectée en dehors de ce cadre.



