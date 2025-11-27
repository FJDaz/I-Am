# 🚀 I-AMIENS - Version Production

## 📋 Description

Cette version de l'extension **I-AMIENS** est configurée pour la **production** et la soumission au Chrome Web Store.

## ✅ Différences avec chrome-extension-v2

### Permissions
- ❌ **Retiré** : Permissions `localhost:8711` (non acceptées par le Chrome Web Store)
- ✅ **Ajouté** : Permission `https://i-am-production.up.railway.app/*` (backend Railway)

### Endpoint
- ❌ **Retiré** : Détection automatique localhost/production
- ✅ **Forcé** : Utilise uniquement `https://i-am-production.up.railway.app/rag-assistant`

### Usage
- **chrome-extension-v2** : Pour développement et tests locaux
- **I-AMIENS** : Pour production et soumission au Chrome Web Store

## 📦 Structure

```
I-AMIENS/
├── manifest.json          # Permissions Railway uniquement
├── content.js             # Endpoint Railway forcé
├── data/                   # Données locales
│   ├── corpus_segments.json
│   ├── lexique_enfance.json
│   └── questions_usager.json
├── statics/
│   └── img/
│       └── IAM_logo.png
└── README.md              # Ce fichier
```

## 🔧 Configuration

### manifest.json
```json
{
  "name": "I-Amiens",
  "host_permissions": [
    "https://i-am-production.up.railway.app/*"
  ]
}
```

### content.js
```javascript
const ASSISTANT_ENDPOINT = "https://i-am-production.up.railway.app/rag-assistant";
```

## 📝 Préparation pour Soumission

1. **Vérifier les fichiers** :
   ```bash
   cd I-AMIENS
   ls -la
   ```

2. **Créer le package ZIP** :
   ```bash
   zip -r ../I-Amiens-extension.zip . \
       -x "*.md" \
       -x "*.sh" \
       -x ".DS_Store"
   ```

3. **Tester l'extension** :
   - Ouvrir Chrome → `chrome://extensions`
   - Activer "Mode développeur"
   - Cliquer "Charger l'extension non empaquetée"
   - Sélectionner le dossier `I-AMIENS`
   - Tester sur `https://www.amiens.fr`

## ⚠️ Points Importants

- ✅ Pas de permissions localhost (conforme Chrome Web Store)
- ✅ Endpoint Railway uniquement (production)
- ✅ Tous les fichiers requis présents
- ✅ Nom "I-Amiens" dans le manifest

## 📚 Documentation Complète

Voir `CHECKLIST_SOUMISSION.md` dans le dossier parent pour la checklist complète de soumission.



