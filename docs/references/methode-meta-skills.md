# Méthode Méta : Structure des Skills

## 📋 Analyse de la Structure Actuelle

### Pattern Observé

Les skills dans ce projet suivent un pattern cohérent :

1. **Documentation** (`docs/references/[nom-skill].md`)
   - Spécification détaillée du skill
   - Exemples d'utilisation
   - Workflow recommandé

2. **Implémentation** (`tools/[nom_skill].py`)
   - Script Python autonome
   - Fonctions réutilisables
   - Interface CLI

3. **Intégration**
   - Peut être appelé manuellement
   - Peut être invoqué automatiquement par **Cursor** (l'IA)
   - Résultat visible et traçable

---

## 🏗️ Structure Standard d'un Skill

### 1. Documentation Markdown (`docs/references/[nom-skill].md`)

```markdown
# Skill : [Nom du Skill]

## 🎯 Objectif

[Description claire et concise de ce que fait le skill]

## 📋 Principe

[Explication du fonctionnement, logique, stratégie]

## 🔧 Implémentation

### Structure du Fichier/Données
[Si applicable : structure des fichiers manipulés]

### Fonctions à Implémenter
[Signature des fonctions principales]

## 📝 Exemple d'Utilisation

### Manuel
[Comment l'exécuter manuellement]

### Automatique (Skill)
[Comment **Cursor** peut l'invoquer automatiquement]

## 🎯 Avantages

[Liste des bénéfices]

## ⚠️ Points d'Attention

[Limitations, précautions, edge cases]

## 🔄 Workflow Recommandé

[Étapes recommandées pour utiliser le skill]

## 📌 Notes

[Informations complémentaires]
```

### 2. Script Python (`tools/[nom_skill].py`)

```python
#!/usr/bin/env python3
"""
[Description courte du script]
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configuration
ROOT = Path(__file__).resolve().parents[1]
[Autres constantes]

def fonction_principale(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """
    [Description de la fonction principale]
    
    Args:
        param1: [Description]
        param2: [Description]
    
    Returns:
        [Description du retour]
    """
    # Implémentation
    pass

def fonction_utilitaire() -> bool:
    """[Description]"""
    pass

if __name__ == "__main__":
    import sys
    # Interface CLI
    # Exemple : fonction_principale(sys.argv[1] if len(sys.argv) > 1 else None)
```

---

## 🎯 Caractéristiques d'un Bon Skill

### ✅ Doit avoir :

1. **Objectif clair et unique**
   - Un skill = une responsabilité
   - Facile à comprendre en 30 secondes

2. **Documentation complète**
   - Spécification détaillée
   - Exemples concrets
   - Cas d'usage

3. **Implémentation autonome**
   - Script exécutable seul
   - Pas de dépendances cachées
   - Gestion d'erreurs

4. **Interface simple**
   - CLI simple (arguments optionnels)
   - Retour structuré (JSON, dict, etc.)
   - Messages clairs

5. **Traçabilité**
   - Logs informatifs
   - Résultats visibles
   - Peut être vérifié manuellement

### ❌ Ne doit pas avoir :

1. **Objectifs multiples**
   - Un skill ne doit pas faire 10 choses différentes

2. **Dépendances implicites**
   - Toutes les dépendances doivent être explicites

3. **Effets de bord cachés**
   - Tous les changements doivent être documentés

4. **Configuration hardcodée**
   - Utiliser des constantes en haut du fichier

---

## 🔄 Workflow de Création d'un Skill

### Étape 1 : Identification du Besoin
- [ ] Problème récurrent identifié
- [ ] Action répétitive à automatiser
- [ ] Tâche complexe à documenter

### Étape 2 : Spécification
- [ ] Écrire la documentation (`docs/references/[nom].md`)
- [ ] Définir l'objectif clairement
- [ ] Lister les fonctions nécessaires
- [ ] Prévoir les cas d'usage

### Étape 3 : Implémentation
- [ ] Créer le script Python (`tools/[nom].py`)
- [ ] Implémenter les fonctions
- [ ] Ajouter gestion d'erreurs
- [ ] Tester manuellement

### Étape 4 : Intégration
- [ ] Vérifier que le script est exécutable
- [ ] Documenter l'invocation automatique
- [ ] Ajouter au README si nécessaire

### Étape 5 : Validation
- [ ] Tester tous les cas d'usage
- [ ] Vérifier les edge cases
- [ ] Mettre à jour la documentation si besoin

---

## 📊 Exemples de Skills Existants

### 1. `resume-contexte-manager`
- **Objectif** : Gérer automatiquement `RESUME_CONTEXTE.md`
- **Pattern** : Vérification → Création/Mise à jour
- **Fichiers** : `docs/references/resume-contexte-manager.md` + `tools/resume_contexte_manager.py`

### 2. `archive-docs-manager`
- **Objectif** : Archiver automatiquement les docs anciennes
- **Pattern** : Détection → Archivage → Renommage
- **Fichiers** : `docs/references/archive-docs-manager.md` + `tools/archive_old_docs.py`

### 3. `fetch-phone-numbers` (documentation seulement)
- **Objectif** : Documenter les stratégies de récupération de contacts
- **Pattern** : Cascade de sources (RAG → Site → OSM → Google)
- **Fichiers** : `docs/references/fetch-phone-numbers.md` (pas encore d'implémentation)

---

## 🎓 Principes Méta

### 1. **Séparation des Préoccupations**
- Documentation = Spécification
- Implémentation = Code
- Intégration = Workflow

### 2. **Réutilisabilité**
- Fonctions modulaires
- Paramètres configurables
- Pas de hardcoding

### 3. **Traçabilité**
- Logs clairs
- Résultats vérifiables
- Historique des actions

### 4. **Simplicité**
- Interface simple
- Documentation claire
- Exemples concrets

### 5. **Robustesse**
- Gestion d'erreurs
- Validation des entrées
- Fallbacks si nécessaire

---

## 🚀 Utilisation de cette Méthode

Cette méthode méta peut être utilisée pour :
1. **Créer de nouveaux skills** : Suivre le pattern documenté
2. **Auditer les skills existants** : Vérifier la conformité
3. **Refactorer des skills** : Améliorer selon les principes
4. **Documenter des workflows** : Standardiser les processus

---
## 📋 Fonctionnement Résumé de Contexte Systématique

### Principe

Le **résumé de contexte** est un skill automatique qui maintient un fichier de synthèse du projet à jour. **Cursor** (l'IA intégrée) l'invoque systématiquement à chaque interaction importante.

### Workflow Automatique

**Important** : C'est **Cursor** qui effectue ces mises à jour automatiquement, pas un autre système.

1. **Vérification** : Au début de chaque session/interaction
   - **Cursor** vérifie si `docs/tests/RESUME_CONTEXTE.md` existe
   - Si non : **Cursor** crée le fichier avec structure de base

2. **Mise à jour** : Après chaque action importante
   - **Cursor** ajoute les nouvelles tâches complétées
   - **Cursor** met à jour les statistiques
   - **Cursor** documente les nouveaux modules créés
   - **Cursor** enregistre les résultats de tests

3. **Structure du fichier** :
   ```markdown
   # Résumé de Contexte - [Nom du Projet]
   
   ## 📋 Contexte Général
   [Description du projet et objectifs]
   
   ## ✅ Ce Qui A Été Fait
   [Liste des réalisations avec statut]
   
   ## ⏳ Ce Qui Reste À Faire
   [TODOs et priorités]
   
   ## 📊 État des Données
   [Tableau des données et fichiers]
   
   ## 🎯 Impact sur les Tests
   [Résultats et métriques]
   
   ## 🔧 Modules Créés
   [Liste des modules/scripts]
   
   ## 📝 Fichiers de Documentation
   [Liste des docs créées]
   ```

### Implémentation

**Fichier** : `tools/resume_contexte_manager.py`

**Fonctions principales** :
- `check_resume_contexte_exists()` → Vérifie l'existence
- `create_resume_contexte()` → Crée le fichier initial
- `update_resume_contexte(updates)` → Met à jour avec nouvelles infos
- `get_current_state()` → Lit l'état actuel

**Invocation automatique par Cursor** :
- **Cursor** invoque ce skill après chaque action majeure
- Format : `update_resume_contexte({"completed_tasks": [...], "new_data": {...}})`
- **Cursor** détecte automatiquement quand une mise à jour est nécessaire

---

## 🏗️ Architecture de Documentation Systématique

### Structure Catégorisée

La documentation suit une architecture standardisée avec catégories claires :

```
docs/
├── tutos/              # Guides pas à pas, tutoriels
├── notes/              # Notes rapides, TODO, réflexions
├── references/         # Explications techniques, concepts
├── guides/             # Guides pratiques, procédures
├── analyses/           # Analyses détaillées, bilans
├── tests/              # Documentation des tests
│   └── archives/       # Archives automatiques
└── supports/           # Support technique
```

### Catégories et Usage

#### `tutos/` - Tutoriels
- **Contenu** : Guides étape par étape
- **Exemples** : `deploiement-mvp.md`, `installation-extension.md`
- **Convention** : Noms en minuscules avec tirets

#### `notes/` - Notes Rapides
- **Contenu** : TODO, réflexions, points à retenir
- **Exemples** : `crash-serveur.md`, `todo-api.md`
- **Convention** : Noms courts et descriptifs

#### `references/` - Références Techniques
- **Contenu** : Concepts, architecture, fonctionnement
- **Exemples** : `segments-rag.md`, `architecture-systeme.md`
- **Convention** : Noms descriptifs, techniques

#### `guides/` - Guides Pratiques
- **Contenu** : Procédures, bonnes pratiques, workflows
- **Exemples** : `depannage-extension.md`, `workflow-deploiement.md`
- **Convention** : Noms descriptifs, actionnables

#### `analyses/` - Analyses et Bilans
- **Contenu** : Analyses détaillées, bilans, résultats
- **Exemples** : `bilan-test-40-questions.md`, `analyse-crash-frontend.md`
- **Convention** : Préfixe `bilan-` ou `analyse-`

#### `tests/` - Documentation des Tests
- **Contenu** : Tests, résultats, méthodologie
- **Exemples** : `resultats-rag.md`, `evaluation-rag.md`
- **Convention** : Garder structure actuelle

#### `supports/` - Support Technique
- **Contenu** : Fixes, troubleshooting, solutions
- **Exemples** : `fix-ssl.md`, `fix-500.md`
- **Convention** : Préfixe `fix-` pour corrections

### Archivage Automatique

**Skill** : `archive-docs-manager`

**Fonctionnement** :
- **Cursor** détecte les fichiers `.md` de plus de N jours (défaut: 1 jour)
- **Cursor** déplace dans `docs/tests/archives/` (ou catégorie appropriée)
- **Cursor** renomme avec date : `YYYY-MM-DD_nom.md`
- **Cursor** met à jour le titre dans le fichier

**Invocation** :
- Automatique : **Cursor** invoque après archivage de docs
- Manuel : `python tools/archive_old_docs.py [jours]`

### Conventions de Nommage

1. **Minuscules** avec tirets (`-`) pour séparer les mots
2. **Descriptif** : Le nom indique clairement le contenu
3. **Court** : Maximum 50 caractères
4. **Pas d'accents** : Utiliser ASCII
5. **Préfixes** : `fix-`, `bilan-`, `analyse-` pour clarifier

### README Principal

Chaque projet doit avoir un `docs/README.md` qui :
- Décrit la structure des dossiers
- Liste le contenu par catégorie
- Explique les conventions
- Référence les skills disponibles

### Structure des Données

**Règle d'organisation des fichiers de données** :

```
data/
├── RAG/                 # Fichiers RAG (corpus, glossaires)
│   ├── corpus_*.md
│   ├── glossaire_*.md
│   └── ...
└── raw/                 # Fichiers bruts classés par extension
    ├── txt/             # Fichiers .txt
    │   ├── 01_esthetique_transcendantale.txt
    │   ├── 02_analytique_des_concepts.txt
    │   └── ...
    ├── pdf/             # Fichiers .pdf
    │   └── ...
    └── doc/              # Fichiers .doc, .docx
        └── ...
```

**Règles de classement** :
- **Fichiers RAG** → `data/RAG/`
  - Corpus RAG (corpus_*.md, Corpus *.md)
  - Glossaires conversationnels (glossaire_*.md, Glossaire *.md)
  - Tous les fichiers .md utilisés pour le RAG
  
- **Fichiers bruts** → `data/raw/[extension]/`
  - Fichiers .txt → `data/raw/txt/`
  - Fichiers .pdf → `data/raw/pdf/`
  - Fichiers .doc, .docx → `data/raw/doc/`
  - Autres formats → `data/raw/[extension]/`

**Invocation automatique par Cursor** :
- **Cursor** détecte les fichiers RAG en vrac (dans `RAG/` ou à la racine)
- **Cursor** déplace vers `data/RAG/`
- **Cursor** détecte les fichiers bruts (.txt, .pdf, .doc) en vrac
- **Cursor** déplace vers `data/raw/[extension]/` selon l'extension

---

## 🔄 Intégration Skills + Documentation

### Workflow Complet

1. **Action importante** → **Cursor** détecte
2. **Cursor** invoque le skill approprié
3. **Skill exécuté** → Résultat documenté
4. **Résumé contexte** → **Cursor** met à jour automatiquement
5. **Documentation** → **Cursor** crée/met à jour dans catégorie appropriée
6. **Archivage** → **Cursor** archive automatiquement après N jours

### Exemple Concret

```
Action : Création d'un nouveau module
  ↓
Cursor détecte l'action importante
  ↓
Cursor invoque : resume-contexte-manager
  ↓
Cursor exécute : update_resume_contexte({
  "new_modules": ["tools/fetch_contacts.py"],
  "completed_tasks": ["Récupération téléphones écoles"]
})
  ↓
Cursor crée : docs/references/fetch-phone-numbers.md
  ↓
Cursor met à jour : RESUME_CONTEXTE.md automatiquement
```

**Note** : Toutes ces actions sont effectuées automatiquement par **Cursor**, sans intervention manuelle.

---

*Dernière mise à jour : 2025-11-18*

