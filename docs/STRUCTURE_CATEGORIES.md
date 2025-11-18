# 📚 Structure Catégorisée de la Documentation

## 🎯 Catégories Proposées

```
docs/
├── tutos/              # Guides pas à pas, tutoriels
├── notes/              # Notes rapides, TODO, réflexions
├── references/         # Explications techniques, concepts
├── guides/             # Guides pratiques, procédures
├── analyses/           # Analyses détaillées, bilans
├── tests/              # Documentation des tests
│   └── archives/       # Archives automatiques
└── supports/           # Support technique (extension, etc.)
```

## 📋 Détail des Catégories

### `tutos/` - Tutoriels et Guides Pas à Pas
**Contenu** : Guides étape par étape pour accomplir une tâche

**Exemples** :
- `DEPLOIEMENT_MVP.md` → `tutos/deploiement-mvp.md`
- `DEPLOIEMENT_OVH.md` → `tutos/deploiement-ovh.md`
- Guides d'installation, configuration, etc.

**Convention** : Noms en minuscules avec tirets (`deploiement-mvp.md`)

---

### `notes/` - Notes Rapides et Réflexions
**Contenu** : Notes temporaires, TODO, réflexions, points à retenir

**Exemples** :
- `NOTE_DEMAIN_CRASH_SERVEUR.md` → `notes/crash-serveur.md`
- Notes de réunion, points d'attention, TODO
- Notes de debug rapides

**Convention** : Noms courts, descriptifs (`crash-serveur.md`, `todo-api.md`)

---

### `references/` - Références Techniques
**Contenu** : Explications de concepts, architecture, fonctionnement

**Exemples** :
- `EXPLICATION_SEGMENTS_RAG.md` → `references/segments-rag.md`
- `EXPLICATION_ALIGNEMENT.md` → `references/alignement-rag.md`
- `OPTIMISATION_LATENCE.md` → `references/optimisation-latence.md`
- Concepts techniques, architecture système

**Convention** : Noms descriptifs (`segments-rag.md`, `architecture-systeme.md`)

---

### `guides/` - Guides Pratiques
**Contenu** : Guides pratiques, procédures, bonnes pratiques

**Exemples** :
- `GUIDE_DEPANNAGE.md` → `guides/depannage-extension.md`
- Guides d'utilisation, procédures opérationnelles
- Checklists, workflows

**Convention** : Noms descriptifs (`depannage-extension.md`, `workflow-deploiement.md`)

---

### `analyses/` - Analyses et Bilans
**Contenu** : Analyses détaillées, bilans, résultats d'études

**Exemples** :
- `BILAN_TEST_40_QUESTIONS.md` → `analyses/bilan-test-40-questions.md`
- `ANALYSE_CRASH_FRONTEND.md` → `analyses/crash-frontend.md`
- `ANALYSE_ERREUR_502.md` → `analyses/erreur-502.md`
- `ANALYSE_HEURISTIQUES.md` → `analyses/heuristiques-rag.md`
- Bilans de session, analyses de performance

**Convention** : Noms descriptifs avec préfixe si besoin (`bilan-xxx.md`, `analyse-xxx.md`)

---

### `tests/` - Documentation des Tests
**Contenu** : Documentation spécifique aux tests, résultats, méthodologie

**Exemples** :
- `README_TEST_HISTORIQUE.md` → `tests/README.md` (ou garder dans tests/)
- `test_results_rag.md` → `tests/resultats-rag.md`
- `rag_eval_summary.md` → `tests/evaluation-rag.md`
- Méthodologie de test, résultats détaillés

**Convention** : Garder la structure actuelle, mais organiser par type

---

### `supports/` - Support Technique
**Contenu** : Documentation de support, fixes, troubleshooting

**Exemples** :
- `FIX_SSL_ERROR.md` → `supports/fix-ssl.md`
- `FIX_500_ERROR.md` → `supports/fix-500.md`
- `FIX_FOLLOWUP_QUESTIONS.md` → `supports/fix-followup.md`
- `STATUS.md` → `supports/status-extension.md`
- Solutions de problèmes, fixes rapides

**Convention** : Noms courts avec préfixe `fix-` ou descriptif (`fix-ssl.md`)

---

## 🔄 Migration Proposée

### Fichiers à Déplacer

#### `docs/` → `docs/tutos/`
- `DEPLOIEMENT_MVP.md` → `tutos/deploiement-mvp.md`
- `DEPLOIEMENT_OVH.md` → `tutos/deploiement-ovh.md`

#### `docs/` → `docs/notes/`
- `NOTE_DEMAIN_CRASH_SERVEUR.md` → `notes/crash-serveur.md`

#### `docs/` → `docs/references/`
- `OPTIMISATION_LATENCE.md` → `references/optimisation-latence.md`
- `EXPLICATION_SEGMENTS_RAG.md` → `references/segments-rag.md`
- `EXPLICATION_ALIGNEMENT.md` → `references/alignement-rag.md`
- `archive_docs_manager.md` → `references/archive-docs-manager.md`
- `resume_contexte_manager.md` → `references/resume-contexte-manager.md`
- `fetch_phone_numbers.md` → `references/fetch-phone-numbers.md`

#### `docs/tests/` → `docs/analyses/`
- `BILAN_*.md` → `analyses/bilan-*.md`
- `ANALYSE_*.md` → `analyses/analyse-*.md`
- `RESUME_ANALYSE.md` → `analyses/resume-analyse.md`
- `RESULTATS_IMPLÉMENTATION.md` → `analyses/resultats-implementation.md`

#### `docs/tests/` → `docs/references/`
- `PISTES_OUVERTURES_RAG.md` → `references/pistes-ouvertures-rag.md`
- `AMELIORATIONS_RAG.md` → `references/ameliorations-rag.md`
- `CLARIFICATIONS.md` → `references/clarifications.md`
- `PROMPT_ACTION.md` → `references/prompt-action.md`

#### `docs/tests/` → `docs/tests/` (garder mais réorganiser)
- `README_TEST_HISTORIQUE.md` → `tests/README.md`
- `test_results_rag.md` → `tests/resultats-rag.md`
- `rag_eval_summary.md` → `tests/evaluation-rag.md`
- `RESUME_CONTEXTE.md` → `tests/resume-contexte.md` (ou `references/` ?)

#### `docs/supports/` → `docs/supports/` (garder mais renommer)
- `FIX_*.md` → `supports/fix-*.md`
- `GUIDE_DEPANNAGE.md` → `supports/guide-depannage.md`
- `STATUS.md` → `supports/status-extension.md`

---

## 📝 Conventions de Nommage

### Format Recommandé
- **Tutos** : `deploiement-mvp.md`, `installation-extension.md`
- **Notes** : `crash-serveur.md`, `todo-api.md`, `reflexion-ux.md`
- **Références** : `segments-rag.md`, `architecture-systeme.md`
- **Guides** : `depannage-extension.md`, `workflow-deploiement.md`
- **Analyses** : `bilan-test-40-questions.md`, `analyse-crash-frontend.md`
- **Tests** : `resultats-rag.md`, `evaluation-rag.md`
- **Supports** : `fix-ssl.md`, `fix-500.md`, `status-extension.md`

### Règles
1. **Minuscules** avec tirets (`-`) pour séparer les mots
2. **Descriptif** : le nom doit indiquer clairement le contenu
3. **Court** : maximum 50 caractères
4. **Pas d'accents** : utiliser des caractères ASCII
5. **Préfixes** : `fix-`, `bilan-`, `analyse-` pour clarifier le type

---

## 🎯 Structure Finale Proposée

```
docs/
├── tutos/
│   ├── deploiement-mvp.md
│   └── deploiement-ovh.md
├── notes/
│   └── crash-serveur.md
├── references/
│   ├── segments-rag.md
│   ├── alignement-rag.md
│   ├── optimisation-latence.md
│   ├── archive-docs-manager.md
│   ├── resume-contexte-manager.md
│   ├── fetch-phone-numbers.md
│   ├── pistes-ouvertures-rag.md
│   ├── ameliorations-rag.md
│   └── clarifications.md
├── guides/
│   └── (à créer selon besoins)
├── analyses/
│   ├── bilan-test-40-questions.md
│   ├── bilan-implementation.md
│   ├── bilan-session.md
│   ├── analyse-crash-frontend.md
│   ├── analyse-erreur-502.md
│   ├── analyse-heuristiques.md
│   ├── analyse-dossiers.md
│   ├── resultats-implementation.md
│   └── resume-analyse.md
├── tests/
│   ├── README.md
│   ├── resume-contexte.md
│   ├── resultats-rag.md
│   ├── evaluation-rag.md
│   └── archives/
├── supports/
│   ├── guide-depannage.md
│   ├── fix-ssl.md
│   ├── fix-500.md
│   ├── fix-followup.md
│   ├── solution-ssl.md
│   ├── status-extension.md
│   └── README_FIX.md
└── README.md
```

---

## ✅ Avantages de cette Structure

1. **Clarté** : Chaque catégorie a un rôle précis
2. **Recherche** : Plus facile de trouver un document
3. **Évolutivité** : Facile d'ajouter de nouvelles catégories
4. **Maintenance** : Organisation logique pour l'archivage
5. **Onboarding** : Nouveaux contributeurs comprennent rapidement

---

## 🔄 Prochaines Étapes

1. **Valider** cette structure avec l'équipe
2. **Créer** les dossiers manquants
3. **Migrer** les fichiers existants
4. **Mettre à jour** les références dans le code
5. **Documenter** dans `docs/README.md`

