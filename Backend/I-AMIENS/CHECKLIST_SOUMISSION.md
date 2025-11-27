# 📋 Checklist de Soumission - I-Amiens (Chrome Web Store)

## ✅ Éléments Requis dans l'Extension

### 1. Fichiers de Base
- [x] `manifest.json` - Manifest V3 (✅ présent)
- [x] `content.js` - Script principal (✅ présent)
- [x] `data/corpus_segments.json` - Données corpus (✅ présent)
- [x] `data/lexique_enfance.json` - Lexique (✅ présent)
- [x] `data/questions_usager.json` - Questions (✅ présent)
- [x] `statics/img/IAM_logo.png` - Logo (✅ présent)

### 2. Manifest.json
- [x] `manifest_version: 3` (✅ conforme)
- [x] `name: "I-Amiens"` (✅ mis à jour)
- [x] `description` - Description claire (✅ présent)
- [x] `version` - Numéro de version (✅ 0.2.0)
- [x] `icons` - Icônes 16x16, 48x48, 128x128 (✅ ajouté)

### 3. Icônes
- [ ] **Vérifier que `IAM_logo.png` est en 128x128 pixels** (requis pour le store)
- [ ] Si nécessaire, créer des versions 16x16 et 48x48 ou redimensionner

### 4. Permissions
- ⚠️ **ATTENTION**: Les permissions `localhost:8711` dans `host_permissions` peuvent poser problème
  - Le Chrome Web Store n'accepte généralement pas les permissions localhost pour les extensions publiques
  - **Solution**: Retirer ces permissions si l'extension doit fonctionner uniquement avec le backend en production
  - Si besoin de localhost pour développement, utiliser une version séparée

## 📦 Préparation du Package ZIP

### Structure du ZIP
```
I-Amiens-extension.zip
├── manifest.json
├── content.js
├── diagnostic.js (optionnel)
├── data/
│   ├── corpus_segments.json
│   ├── lexique_enfance.json
│   └── questions_usager.json
└── statics/
    └── img/
        └── IAM_logo.png
```

### Commandes pour créer le ZIP
```bash
cd chrome-extension-v2
zip -r ../I-Amiens-extension.zip . -x "*.md" -x "*.sh" -x ".DS_Store"
```

## 🌐 Informations pour le Chrome Web Store

### 1. Informations de Base
- **Nom**: I-Amiens
- **Description courte** (132 caractères max):
  ```
  Assistant intelligent pour la rubrique enfance du site amiens.fr. Réponses basées sur RAG et IA.
  ```
- **Description détaillée**:
  ```
  I-Amiens est un assistant intelligent qui aide les utilisateurs à trouver des informations sur les services enfance de la ville d'Amiens.
  
  Fonctionnalités:
  - Recherche locale dans le corpus de données Amiens Enfance
  - Réponses générées par IA (Claude) basées sur les données officielles
  - Interface intuitive intégrée au site amiens.fr
  - Suggestions de questions de suivi
  
  L'extension fonctionne uniquement sur le site amiens.fr et nécessite un backend accessible.
  ```

### 2. Catégorie
- **Catégorie principale**: Productivité
- **Catégorie secondaire**: Outils

### 3. Captures d'écran
- [ ] **Minimum 1 capture d'écran** (recommandé: 3-5)
- [ ] Format: PNG ou JPEG
- [ ] Taille recommandée: 1280x800 ou 640x400
- [ ] Montrer:
  - L'interface de l'assistant sur amiens.fr
  - Une question posée et la réponse
  - Les suggestions de suivi

### 4. Icône du Store
- [ ] Icône 128x128 pixels (utiliser `IAM_logo.png` si aux bonnes dimensions)
- [ ] Format: PNG avec transparence

### 5. Images Promotionnelles (optionnel mais recommandé)
- [ ] **Petite promotion** (440x280) - optionnel
- [ ] **Grande promotion** (920x680) - optionnel
- [ ] **Marque** (112x112) - optionnel

## ⚠️ Points d'Attention

### 1. Permissions Localhost
**PROBLÈME**: Le manifest contient:
```json
"host_permissions": [
  "http://localhost:8711/*",
  "https://localhost:8711/*"
]
```

**SOLUTION**: 
- Pour une extension publique, retirer ces permissions
- L'extension doit utiliser uniquement l'endpoint de production:
  ```javascript
  const ASSISTANT_ENDPOINT = "https://i-am-production.up.railway.app/rag-assistant";
  ```
- Créer une version séparée pour le développement local si nécessaire

### 2. Backend Accessible
- Vérifier que le backend Railway est accessible publiquement
- Tester l'endpoint: `https://i-am-production.up.railway.app/rag-assistant`
- S'assurer que CORS est configuré correctement

### 3. Politique de Confidentialité
- [ ] Créer une page de politique de confidentialité
- [ ] Expliquer quelles données sont collectées (si aucune, le préciser)
- [ ] URL à fournir dans le formulaire de soumission

### 4. Code Source
- Le code doit être lisible (pas minifié/obfusqué)
- ✅ Le code actuel est lisible

## 📝 Étapes de Soumission

1. **Créer un compte développeur Chrome Web Store**
   - Aller sur https://chrome.google.com/webstore/devconsole
   - Payer les frais uniques de $5 (si pas déjà fait)

2. **Préparer le package**
   - Créer le ZIP avec tous les fichiers nécessaires
   - Vérifier que le ZIP ne contient pas de fichiers inutiles

3. **Remplir le formulaire**
   - Téléverser le ZIP
   - Remplir les informations (nom, description, catégories)
   - Ajouter les captures d'écran
   - Fournir l'URL de la politique de confidentialité
   - Indiquer les permissions utilisées

4. **Révision**
   - Google peut prendre 1-3 jours pour réviser
   - Répondre rapidement aux questions si demandées

## 🔍 Vérifications Finales

- [ ] Tous les fichiers sont présents dans le ZIP
- [ ] Le manifest.json est valide (tester avec `chrome://extensions`)
- [ ] L'extension fonctionne en mode chargé (pas depuis le store)
- [ ] Les permissions sont minimales et justifiées
- [ ] Le backend de production est accessible
- [ ] Les captures d'écran sont prêtes
- [ ] La politique de confidentialité est disponible
- [ ] Le nom "I-Amiens" est utilisé partout (manifest, descriptions)

## 📚 Ressources

- [Documentation Chrome Web Store](https://developer.chrome.com/docs/webstore/publish)
- [Politiques du Chrome Web Store](https://developer.chrome.com/docs/webstore/program-policies)
- [Guide Manifest V3](https://developer.chrome.com/docs/extensions/mv3/intro/)

