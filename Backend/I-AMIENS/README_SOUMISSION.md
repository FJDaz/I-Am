# 🚀 Guide de Soumission - I-Amiens

## ✅ État Actuel

Le dossier `chrome-extension-v2` contient **tous les fichiers nécessaires** pour soumettre l'extension au Chrome Web Store :

### Fichiers Présents ✅
- ✅ `manifest.json` - Mis à jour avec le nom "I-Amiens" et les icônes
- ✅ `content.js` - Script principal (52 KB)
- ✅ `data/corpus_segments.json` - Corpus de données
- ✅ `data/lexique_enfance.json` - Lexique
- ✅ `data/questions_usager.json` - Questions usager
- ✅ `statics/img/IAM_logo.png` - Logo/icône
- ✅ `diagnostic.js` - Outil de diagnostic (optionnel)

## ⚠️ Point Important : Permissions Localhost

**Le manifest.json contient actuellement :**
```json
"host_permissions": [
  "http://localhost:8711/*",
  "https://localhost:8711/*"
]
```

**⚠️ ATTENTION** : Le Chrome Web Store peut **rejeter** les extensions avec des permissions localhost pour les extensions publiques.

### Solutions

#### Option 1 : Retirer les permissions localhost (Recommandé pour production)
Si l'extension doit fonctionner uniquement avec le backend de production, retirer ces lignes du manifest.json.

#### Option 2 : Garder pour développement
Si vous avez besoin de localhost pour le développement, créez deux versions :
- Version développement : avec localhost
- Version production : sans localhost (pour le store)

**Note** : Le `content.js` détecte automatiquement si on est sur localhost ou en production, donc retirer les permissions du manifest ne cassera pas la détection automatique.

## 📦 Créer le Package de Soumission

### Méthode 1 : Script automatique
```bash
cd chrome-extension-v2
./prepare_submission.sh
```

Le script va :
- Vérifier tous les fichiers requis
- Créer un ZIP prêt pour soumission
- Afficher un résumé

### Méthode 2 : Manuel
```bash
cd chrome-extension-v2
zip -r ../I-Amiens-extension.zip . \
    -x "*.md" \
    -x "*.sh" \
    -x ".DS_Store" \
    -x "*.log"
```

## 📋 Checklist Avant Soumission

### Fichiers ✅
- [x] Tous les fichiers requis sont présents
- [x] Le manifest.json est valide
- [x] Le nom est "I-Amiens" partout

### À Vérifier 🔍
- [ ] **Vérifier les dimensions de `IAM_logo.png`** (doit être 128x128 pour le store)
- [ ] **Décider des permissions localhost** (voir ci-dessus)
- [ ] Tester l'extension en mode chargé (chrome://extensions)
- [ ] Vérifier que le backend de production est accessible

### À Préparer 📸
- [ ] **Captures d'écran** (minimum 1, recommandé 3-5)
  - Format: PNG ou JPEG
  - Taille: 1280x800 ou 640x400
  - Montrer l'interface de l'assistant en action
- [ ] **Politique de confidentialité**
  - Créer une page web expliquant quelles données sont collectées
  - URL à fournir dans le formulaire de soumission

### Informations pour le Store 📝
- [x] Nom: **I-Amiens**
- [ ] Description courte (132 caractères max)
- [ ] Description détaillée
- [ ] Catégorie: Productivité / Outils
- [ ] Mots-clés (optionnel)

## 🌐 Processus de Soumission

1. **Créer un compte développeur**
   - Aller sur https://chrome.google.com/webstore/devconsole
   - Payer les frais uniques de $5 (si pas déjà fait)

2. **Téléverser le package**
   - Cliquer sur "Ajouter un nouvel élément"
   - Téléverser le fichier ZIP

3. **Remplir le formulaire**
   - Informations de base (nom, description)
   - Captures d'écran
   - URL de la politique de confidentialité
   - Catégories et mots-clés

4. **Révision**
   - Google peut prendre 1-3 jours
   - Répondre rapidement aux questions si demandées

## 📚 Documentation

- **CHECKLIST_SOUMISSION.md** - Checklist détaillée complète
- **prepare_submission.sh** - Script pour créer le package ZIP
- **diagnostic.js** - Outil pour vérifier l'extension

## 🔗 Liens Utiles

- [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
- [Documentation Chrome Web Store](https://developer.chrome.com/docs/webstore/publish)
- [Politiques du Chrome Web Store](https://developer.chrome.com/docs/webstore/program-policies)
- [Guide Manifest V3](https://developer.chrome.com/docs/extensions/mv3/intro/)

