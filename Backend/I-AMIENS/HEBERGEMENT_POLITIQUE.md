# 📍 Hébergement de la Politique de Confidentialité

## Options d'Hébergement

Pour soumettre l'extension au Chrome Web Store, vous devez fournir une **URL publique** où la politique de confidentialité est accessible.

### Option 1 : GitHub Pages (Recommandé - Gratuit)

1. **Créer un dépôt GitHub** (si pas déjà fait)
2. **Créer un fichier `privacy-policy.html`** à la racine du dépôt
3. **Activer GitHub Pages** :
   - Settings → Pages
   - Source : `main` branch
   - Folder : `/ (root)`
4. **URL obtenue** : `https://votre-username.github.io/votre-repo/privacy-policy.html`

**Exemple** : `https://fjdaz.github.io/i-amiens/privacy-policy.html`

### Option 2 : Site Web Personnel

Si vous avez déjà un site web (ex: fjdaz.com), vous pouvez :
- Téléverser `PRIVACY_POLICY.html` sur votre serveur
- URL : `https://votre-site.com/i-amiens/privacy-policy.html`

### Option 3 : Netlify / Vercel (Gratuit)

1. Créer un compte sur Netlify ou Vercel
2. Créer un nouveau site
3. Téléverser le fichier `PRIVACY_POLICY.html`
4. Obtenir l'URL : `https://votre-site.netlify.app/privacy-policy.html`

### Option 4 : Railway (Même hébergeur que le backend)

Si vous avez déjà Railway, vous pouvez créer un service statique :
1. Créer un nouveau service sur Railway
2. Déployer le fichier HTML
3. Obtenir l'URL Railway

## Fichiers Créés

Deux versions de la politique sont disponibles :

1. **`PRIVACY_POLICY.md`** - Version Markdown (pour GitHub)
2. **`PRIVACY_POLICY.html`** - Version HTML (prête pour hébergement web)

## Instructions Rapides (GitHub Pages)

```bash
# 1. Créer un dépôt GitHub (si nécessaire)
# 2. Copier le fichier HTML
cp PRIVACY_POLICY.html privacy-policy.html

# 3. Commiter et pousser
git add privacy-policy.html
git commit -m "Add privacy policy for Chrome Web Store"
git push origin main

# 4. Activer GitHub Pages dans les settings du dépôt
# 5. URL sera : https://username.github.io/repo-name/privacy-policy.html
```

## Vérification

Avant de soumettre, vérifiez que :
- ✅ L'URL est accessible publiquement
- ✅ La page s'affiche correctement
- ✅ Le contenu est lisible et complet
- ✅ L'URL est en HTTPS (requis)

## Exemple d'URL à Fournir

```
https://votre-username.github.io/i-amiens/privacy-policy.html
```

ou

```
https://votre-site.com/i-amiens/privacy-policy.html
```



