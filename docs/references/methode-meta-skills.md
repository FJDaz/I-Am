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
   - Peut être invoqué automatiquement par l'IA
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
[Comment l'IA peut l'invoquer]

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

*Dernière mise à jour : 2025-11-18*

