# 📸 Guide pour Captures d'Écran - Chrome Web Store

## Problème du Logo

Si le logo ne s'affiche pas dans l'extension en local, voici comment le résoudre et prendre des captures d'écran.

## 🔧 Vérification du Logo

### 1. Vérifier que l'extension est bien chargée
1. Ouvrir Chrome → `chrome://extensions`
2. Activer "Mode développeur"
3. Vérifier que l'extension I-Amiens est chargée
4. Si nécessaire, cliquer sur "Recharger" (icône circulaire)

### 2. Vérifier la console pour les erreurs
1. Ouvrir `https://www.amiens.fr` dans un nouvel onglet
2. Appuyer sur `F12` pour ouvrir les outils de développement
3. Aller dans l'onglet "Console"
4. Vérifier s'il y a des erreurs concernant le logo (404, chemin incorrect, etc.)

### 3. Solution si le logo ne s'affiche pas

**Option A : Utiliser une image de base64 inline (temporaire pour capture)**
- Le logo peut être encodé en base64 directement dans le HTML
- Ou utiliser une URL externe temporaire pour la capture

**Option B : Vérifier le chemin**
- Le logo doit être dans `statics/img/IAM_logo.png`
- Le manifest.json doit déclarer `statics/img/IAM_logo.png` dans `web_accessible_resources`

## 📸 Prendre des Captures d'Écran

### Captures Requises (Minimum 1, Recommandé 3-5)

1. **Capture principale** : Interface de l'assistant ouverte
   - Montrer le bouton "Assistant Enfance Amiens"
   - Montrer l'overlay avec le logo (si visible)
   - Montrer le champ de saisie

2. **Capture avec question/réponse** :
   - Une question posée (ex: "Quels sont les tarifs de la cantine ?")
   - La réponse affichée
   - Les sources/liens

3. **Capture du site amiens.fr** :
   - Montrer l'extension intégrée au site
   - Montrer que ça fonctionne sur amiens.fr

### Format des Captures

- **Format** : PNG ou JPEG
- **Taille recommandée** : 
  - 1280x800 pixels (petite promotion)
  - 920x680 pixels (grande promotion)
  - Minimum : 640x400 pixels

### Outils pour Captures

**macOS** :
- `Cmd + Shift + 4` : Capture de zone
- `Cmd + Shift + 3` : Capture d'écran complet
- Utiliser l'outil de capture macOS pour sélectionner la zone

**Chrome DevTools** :
1. `F12` → Outils de développement
2. `Cmd + Shift + P` (macOS) ou `Ctrl + Shift + P` (Windows)
3. Taper "screenshot"
4. Choisir "Capture node screenshot" ou "Capture full size screenshot"

## 🎨 Si le Logo Ne S'Affiche Pas

### Solution Temporaire pour Capture

Vous pouvez temporairement modifier `content.js` pour utiliser une URL externe ou un placeholder :

```javascript
// Option 1 : URL externe (si vous avez hébergé le logo)
<img src="https://votre-site.com/IAM_logo.png" alt="I Am Logo" class="assistant-logo">

// Option 2 : Placeholder temporaire
<img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiBmaWxsPSIjY2IwYjhmIi8+PHRleHQgeD0iNTA%2BJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTYiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI%2BSS1BPC90ZXh0Pjwvc3ZnPg%3D%3D" alt="I Am Logo" class="assistant-logo">
```

**⚠️ Important** : Remettre le chemin original après la capture !

## ✅ Checklist Avant Capture

- [ ] Extension chargée dans Chrome
- [ ] Site amiens.fr ouvert
- [ ] Assistant visible et fonctionnel
- [ ] Logo visible (ou placeholder si problème)
- [ ] Interface complète visible
- [ ] Pas d'erreurs dans la console

## 📝 Exemple de Captures

1. **Capture 1** : Bouton assistant en bas à droite sur amiens.fr
2. **Capture 2** : Overlay ouvert avec interface complète
3. **Capture 3** : Question posée et réponse affichée
4. **Capture 4** : Suggestions de suivi (si disponibles)

Une fois les captures prises, vous pouvez les utiliser dans le formulaire de soumission Chrome Web Store.



