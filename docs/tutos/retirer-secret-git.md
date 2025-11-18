# Retirer un Secret de l'Historique Git

## Problème

GitHub a détecté une clé API dans un commit précédent (`.env`). Même si le fichier est maintenant dans `.gitignore`, il reste dans l'historique.

## Solution 1 : Nettoyer l'Historique (Recommandé)

```bash
# Retirer .env de tous les commits
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

# Nettoyer les références
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (⚠️ réécrit l'historique)
git push --force-with-lease origin main
```

## Solution 2 : Autoriser Temporairement (Rapide)

Utiliser l'URL fournie par GitHub pour autoriser le push une fois :
```
https://github.com/FJDaz/I-Am/security/secret-scanning/unblock-secret/35e352fpDTw8zB9HFKhAn22UhBw
```

⚠️ **Important** : Après autorisation, nettoyer l'historique quand même pour sécurité.

## Solution 3 : Régénérer la Clé API

1. Aller sur https://console.anthropic.com/
2. Révoquer l'ancienne clé
3. Créer une nouvelle clé
4. Mettre à jour `.env` localement
5. Nettoyer l'historique (Solution 1)

## Prévention

✅ Toujours mettre `.env` dans `.gitignore` **avant** le premier commit
✅ Utiliser des variables d'environnement dans les services de déploiement
✅ Ne jamais commiter de secrets

## Vérification

```bash
# Vérifier que .env n'est plus dans l'historique
git log --oneline --all -- .env

# Devrait être vide
```

