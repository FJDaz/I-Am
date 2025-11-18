# Skill : Gestion Automatique du Résumé de Contexte

## 🎯 Objectif

Automatiser la gestion du fichier `RESUME_CONTEXTE.md` :
- **Si le fichier n'existe pas** : Le créer avec une structure de base
- **Sinon** : Le mettre à jour à chaque interaction avec les nouvelles informations

## 📋 Principe

À chaque interaction/session :
1. Vérifier si `tests/docs/RESUME_CONTEXTE.md` existe
2. Si non : Créer le fichier avec structure de base
3. Si oui : Mettre à jour avec :
   - Nouvelles tâches complétées
   - Nouvelles données ajoutées
   - Nouveaux modules créés
   - Nouvelles statistiques

## 🔧 Implémentation

### Structure du Fichier

```markdown
# Résumé de Contexte - Améliorations RAG Amiens

## 📋 Contexte Général
[Description du projet]

## ✅ Ce Qui A Été Fait
[Liste des réalisations]

## ⏳ Ce Qui Reste À Faire
[Liste des TODOs]

## 📊 État des Données
[Tableau des données]

## 🎯 Impact sur les Tests
[Tableau des tests]

## 🔧 Modules Créés
[Liste des modules]

## 📝 Fichiers de Documentation
[Liste des docs]
```

### Fonctions à Implémenter

```python
def check_resume_contexte_exists() -> bool:
    """Vérifie si RESUME_CONTEXTE.md existe."""
    pass

def create_resume_contexte() -> None:
    """Crée RESUME_CONTEXTE.md avec structure de base."""
    pass

def update_resume_contexte(updates: dict) -> None:
    """Met à jour RESUME_CONTEXTE.md avec nouvelles infos."""
    # updates = {
    #     "completed_tasks": [...],
    #     "new_data": {...},
    #     "new_modules": [...],
    #     "test_results": {...}
    # }
    pass

def get_current_state() -> dict:
    """Lit l'état actuel de RESUME_CONTEXTE.md."""
    pass
```

## 📝 Exemple d'Utilisation

```python
# Au début d'une session
if not check_resume_contexte_exists():
    create_resume_contexte()

# Après chaque action importante
updates = {
    "completed_tasks": ["Compléter adresses écoles"],
    "new_data": {
        "ecoles": {"adresses_completes": 204, "total": 255}
    },
    "new_modules": ["complete_school_addresses.py"]
}
update_resume_contexte(updates)
```

## 🎯 Avantages

1. **Traçabilité** : Historique automatique des améliorations
2. **Cohérence** : Toujours à jour
3. **Documentation** : Auto-générée
4. **Onboarding** : Nouveau développeur comprend rapidement l'état

## ⚠️ Points d'Attention

1. **Format** : Respecter la structure markdown
2. **Merge** : Gérer les conflits si plusieurs sessions
3. **Backup** : Sauvegarder avant modifications importantes
4. **Validation** : Vérifier que les mises à jour sont valides

## 🔄 Workflow Recommandé

1. **Début de session** : Vérifier/créer RESUME_CONTEXTE.md
2. **Pendant session** : Noter les actions importantes
3. **Fin de session** : Mettre à jour RESUME_CONTEXTE.md avec toutes les actions
4. **Commit** : Inclure RESUME_CONTEXTE.md dans le commit

## 📌 Notes

- Ce skill peut être intégré dans un script de session
- Peut être appelé automatiquement après chaque action majeure
- Peut générer aussi un BILAN_SESSION.md à la fin de chaque session

