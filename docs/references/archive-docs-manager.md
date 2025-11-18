# Skill: Archive Docs Manager

## 📋 Description

Skill pour archiver automatiquement les fichiers de documentation de plus de 1 jour dans `docs/tests/archives/` et renommer avec la date de dernière modification.

## 🎯 Fonctionnalités

1. **Détection automatique** : Identifie les fichiers `.md` de plus de N jours (par défaut 1)
2. **Archivage** : Déplace les fichiers dans `docs/tests/archives/`
3. **Renommage** : Ajoute la date de dernière modification devant le nom (`YYYY-MM-DD_nom.md`)
4. **Mise à jour titre** : Met à jour le titre dans le fichier avec la date
5. **Exclusions** : Ne touche pas à `RESUME_CONTEXTE.md` et `README.md`

## 📁 Structure

```
docs/tests/
├── RESUME_CONTEXTE.md          (toujours conservé)
├── BILAN_TEST_40_QUESTIONS.md  (fichiers récents)
├── ...
└── archives/
    ├── 2025-11-15_AMELIORATIONS_RAG.md
    ├── 2025-11-14_BILAN_IMPLÉMENTATION.md
    └── ...
```

## 🚀 Utilisation

### Manuel

```bash
# Archiver les fichiers de plus de 1 jour (défaut)
python3 tools/archive_old_docs.py

# Archiver les fichiers de plus de 5 jours
python3 tools/archive_old_docs.py 5
```

### Automatique (Skill)

Quand l'utilisateur demande de faire le ménage dans les docs :
1. Exécuter `tools/archive_old_docs.py`
2. Afficher le résumé des fichiers archivés
3. Confirmer l'opération

## 📝 Exemple d'utilisation

**Input utilisateur** :
> "Fais un petit ménage dans les docs tests, ajoute un sous-dossier archives et mets tout ce qui a plus d'un jour dedans"

**Action** :
1. Créer `docs/tests/archives/` si n'existe pas
2. Exécuter `python3 tools/archive_old_docs.py` (défaut: 1 jour)
3. Afficher le résultat

## ⚙️ Paramètres

- `days` : Nombre de jours avant archivage (défaut: 1)
- `docs_dir` : Dossier de documentation (défaut: `docs/tests`)
- `exclude_files` : Fichiers à ne jamais archiver

## 🔄 Mise à jour des titres

Le script met automatiquement à jour le titre dans le fichier :
- **Avant** : `# BILAN IMPLÉMENTATION`
- **Après** : `# 2025-11-15 - BILAN IMPLÉMENTATION`

## 📊 Résultat

Le script affiche :
- Nombre de fichiers archivés
- Liste des fichiers déplacés
- Nombre de fichiers conservés

