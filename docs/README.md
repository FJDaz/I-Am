# 📚 Documentation du Projet Amiens Enfance

## Structure des Dossiers

```
docs/
├── tutos/             # Guides pas à pas, tutoriels
├── notes/             # Notes rapides, TODO, réflexions
├── references/        # Explications techniques, concepts
├── guides/            # Guides pratiques, procédures
├── analyses/          # Analyses détaillées, bilans
├── tests/             # Documentation des tests
│   └── archives/      # Archives automatiques
└── supports/         # Support technique (extension, etc.)
```

## 📁 Contenu par Catégorie

### `docs/tutos/`
Guides pas à pas :
- **deploiement-mvp.md** : Guide de déploiement MVP/POC sur Railway
- **deploiement-ovh.md** : Analyse et alternatives de déploiement OVH

### `docs/notes/`
Notes rapides et réflexions :
- **crash-serveur.md** : Notes sur les crashes serveur

### `docs/references/`
Explications techniques et concepts :
- **segments-rag.md** : Explication des segments RAG
- **alignement-rag.md** : Explication du système d'alignement
- **optimisation-latence.md** : Optimisations de performance
- **methode-meta-skills.md** : Méthode méta pour créer des skills (structure, principes, workflow)
- **prompt-generateur-skills.md** : Prompt complet pour générer automatiquement des skills
- **archive-docs-manager.md** : Skill d'archivage automatique
- **resume-contexte-manager.md** : Skill de gestion du contexte
- **fetch-phone-numbers.md** : Stratégies de récupération contacts
- **pistes-ouvertures-rag.md** : Stratégies pour les ouvertures
- **ameliorations-rag.md** : Améliorations du système RAG
- **clarifications.md** : Clarifications techniques
- **prompt-action.md** : Actions sur les prompts

### `docs/guides/`
Guides pratiques (à compléter selon besoins)

### `docs/analyses/`
Analyses détaillées et bilans :
- **bilan-test-40-questions.md** : Résultats des tests
- **bilan-implementation.md** : Bilan d'implémentation
- **bilan-session.md** : Bilan de session
- **analyse-crash-frontend.md** : Analyse des crashes frontend
- **analyse-erreur-502.md** : Analyse des erreurs 502
- **analyse-heuristiques.md** : Analyse des heuristiques
- **analyse-dossiers.md** : Analyse des dossiers
- **resultats-implementation.md** : Résultats d'implémentation
- **resume-analyse.md** : Résumé d'analyse

### `docs/tests/`
Documentation des tests :
- **README.md** : Documentation des tests
- **resume-contexte.md** : Résumé du contexte projet
- **resultats-rag.md** : Résultats des tests RAG
- **evaluation-rag.md** : Évaluation du système RAG
- **archives/** : Archives automatiques (après 1 jour)

### `docs/supports/`
Support technique pour l'extension Chrome :
- **guide-depannage.md** : Guide de dépannage
- **fix-ssl-error.md** : Fix erreurs SSL
- **fix-500-error.md** : Fix erreurs 500
- **fix-followup-questions.md** : Fix questions de suivi
- **solution-ssl.md** : Solution aux problèmes SSL
- **status-extension.md** : État actuel de l'extension
- **README_FIX.md** : Documentation des fixes

## 🔄 Archivage Automatique

Les documents de plus de 1 jour dans `docs/tests/` sont automatiquement déplacés vers `docs/tests/archives/` par le script `tools/archive_old_docs.py`.

## 📝 Conventions

- **Fichiers .md** : Documentation Markdown
- **Noms de fichiers** : En MAJUSCULES pour les documents importants, camelCase pour les autres
- **Dates** : Format `YYYY-MM-DD` dans les noms de fichiers archivés

