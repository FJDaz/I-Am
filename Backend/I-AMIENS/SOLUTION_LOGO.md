# 🔧 Solution Problème Logo - Capture d'Écran

## Diagnostic

Le logo `IAM_logo.png` existe bien dans `statics/img/IAM_logo.png` (128x128 pixels).

## Solutions Rapides

### Solution 1 : Recharger l'Extension

1. Ouvrir `chrome://extensions`
2. Trouver "I-Amiens"
3. Cliquer sur l'icône de rechargement (🔄)
4. Recharger la page `https://www.amiens.fr`

### Solution 2 : Vérifier la Console

1. Ouvrir `https://www.amiens.fr`
2. Appuyer sur `F12`
3. Aller dans l'onglet "Console"
4. Vérifier s'il y a des erreurs 404 pour le logo

### Solution 3 : Vérifier le Manifest

Le logo doit être déclaré dans `web_accessible_resources` :
```json
"web_accessible_resources": [
  {
    "resources": [
      "statics/img/IAM_logo.png"
    ],
    "matches": [
      "https://www.amiens.fr/*"
    ]
  }
]
```

## Pour la Capture d'Écran

### Option A : Prendre la capture sans le logo visible

Vous pouvez prendre la capture même si le logo ne s'affiche pas. Le texte "Assistant Enfance Amiens" sera visible.

### Option B : Ajouter le logo manuellement après

1. Prendre la capture de l'interface
2. Ouvrir dans un éditeur d'images (Photoshop, GIMP, Preview)
3. Ajouter le logo depuis `statics/img/IAM_logo.png`

### Option C : Utiliser un placeholder temporaire

Si vous voulez que le logo s'affiche pour la capture, vous pouvez temporairement modifier `content.js` ligne 552 :

**Remplacement temporaire** :
```javascript
// Avant
<img src="${chrome.runtime.getURL('statics/img/IAM_logo.png')}" alt="I Am Logo" class="assistant-logo">

// Après (temporaire pour capture)
<img src="data:image/png;base64,[BASE64_DU_LOGO]" alt="I Am Logo" class="assistant-logo">
```

**⚠️ Important** : Remettre le code original après la capture !

## Format de Capture Requis

- **Format** : PNG ou JPEG
- **Taille** : 1280x800 ou 640x400 pixels minimum
- **Contenu** : Interface de l'assistant visible sur amiens.fr

## Étapes pour Capture

1. Ouvrir `https://www.amiens.fr`
2. Cliquer sur le bouton "Assistant Enfance Amiens" (en bas à droite)
3. Prendre une capture de l'overlay ouvert
4. Montrer :
   - Le champ de saisie
   - Le bouton "Analyser"
   - L'interface complète

Même sans le logo visible, la capture sera acceptable pour le Chrome Web Store.



