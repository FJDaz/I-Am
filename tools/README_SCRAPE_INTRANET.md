# Scraper Intranet AC Amiens

Script pour scraper le contenu de l'intranet `https://intranet.ac-amiens.fr/`

## Installation

Les dépendances nécessaires :
```bash
pip install requests beautifulsoup4
```

## Utilisation

### 1. Scraping basique (sans authentification)

Si l'intranet est accessible sans authentification :
```bash
python tools/scrape_intranet_ac_amiens.py --url https://intranet.ac-amiens.fr/ --max-pages 50
```

### 2. Scraping avec authentification

Si l'intranet nécessite une authentification :
```bash
python tools/scrape_intranet_ac_amiens.py \
  --url https://intranet.ac-amiens.fr/ \
  --username votre_username \
  --password votre_password \
  --max-pages 100 \
  --depth 3
```

### 3. Utilisation avec cookies de session

Si vous avez déjà une session active, vous pouvez exporter vos cookies depuis votre navigateur et les utiliser :

1. Exporter les cookies depuis votre navigateur (extension comme "Cookie-Editor" ou DevTools)
2. Sauvegarder dans un fichier JSON :
```json
{
  "session_id": "valeur",
  "csrf_token": "valeur",
  ...
}
```

3. Utiliser le script :
```bash
python tools/scrape_intranet_ac_amiens.py \
  --url https://intranet.ac-amiens.fr/ \
  --cookies cookies.json \
  --max-pages 100
```

## Options disponibles

- `--url` : URL de départ (défaut: https://intranet.ac-amiens.fr/)
- `--output` : Dossier de sortie (défaut: intranet_ac_amiens_data)
- `--max-pages` : Nombre maximum de pages à scraper (défaut: 100)
- `--depth` : Profondeur de crawling (défaut: 3)
- `--delay` : Délai entre les requêtes en secondes (défaut: 2.0)
- `--username` : Nom d'utilisateur pour l'authentification
- `--password` : Mot de passe pour l'authentification
- `--cookies` : Fichier JSON contenant les cookies de session

## Structure des données extraites

Le script crée un dossier avec :
- `summary.json` : Résumé de toutes les pages scrapées
- `*.json` : Fichiers JSON individuels pour chaque page avec :
  - URL, titre, headings (H1, H2, H3)
  - Contenu texte
  - Liens (internes et externes)
  - Images
  - Tableaux
- `*.txt` : Fichiers texte bruts pour chaque page

## Notes importantes

⚠️ **Respect des conditions d'utilisation** :
- Vérifiez que vous avez l'autorisation de scraper l'intranet
- Respectez les délais entre les requêtes (défaut: 2 secondes)
- Ne surchargez pas le serveur avec trop de requêtes simultanées

⚠️ **Authentification** :
- Le script tente automatiquement de détecter et remplir le formulaire de connexion
- Si la structure du formulaire est différente, vous devrez peut-être modifier le code
- Les cookies de session sont une alternative plus fiable si vous avez déjà une session active

## Exemple de sortie

```
📄 Récupération: https://intranet.ac-amiens.fr/
✅ Page 1/100 traitée: https://intranet.ac-amiens.fr/
📄 Récupération: https://intranet.ac-amiens.fr/page1
✅ Page 2/100 traitée: https://intranet.ac-amiens.fr/page1
...
✅ Scraping terminé: 50 pages extraites
```


