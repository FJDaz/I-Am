# Gitignore des Fichiers de Données

## Problème

GitHub rejette les pushs contenant des fichiers volumineux ou sensibles. Les fichiers suivants doivent être ignorés :

## Fichiers à Ignorer

### Fichiers Volumineux
- `data/*.npy` : Embeddings (2.2MB+)
- `data/raw/**/*` : Fichiers bruts (PDFs, XLS, etc.)
- `*.xls`, `*.xlsx` : Fichiers Excel

### Fichiers Sensibles
- `*.pem` : Certificats SSL
- `.env`, `.env.local` : Variables d'environnement
- Tous fichiers contenant des clés API

## Solution

Les fichiers sont maintenant dans `.gitignore`. Si ils étaient déjà trackés :

```bash
# Retirer du cache git (sans supprimer localement)
git rm --cached data/*.npy
git rm --cached data/raw/**/*

# Commit
git add .gitignore
git commit -m "Ignore data files"
```

## Pour le Déploiement

Les fichiers de données doivent être :
1. **Générés localement** avant déploiement
2. **Téléchargés** depuis un stockage séparé (S3, etc.)
3. **Créés** par le script de déploiement

Pour Railway, ajouter dans les variables d'environnement ou utiliser un volume persistant.

