# 🔧 Fix Erreur SSL - Extension Chrome

## ✅ Corrections Appliquées

1. **Endpoint changé en HTTP** dans `content.js` :
   - `https://localhost:8711` → `http://localhost:8711`

2. **Manifest.json** : Déjà correct (permissions HTTP présentes)

## 🚀 Action Requise

Le serveur tourne actuellement en **HTTPS**. Pour que l'extension fonctionne, il faut le relancer en **HTTP**.

### Méthode Rapide

```bash
cd "I Amiens"
./start_server_http.sh
```

Ce script va :
1. Arrêter le serveur actuel
2. Sauvegarder les certificats SSL
3. Relancer le serveur en HTTP

### Méthode Manuelle

1. **Arrêter le serveur** :
   ```bash
   lsof -ti :8711 | xargs kill
   ```

2. **Sauvegarder les certificats** :
   ```bash
   mv localhost-key.pem localhost-key.pem.bak
   mv localhost-cert.pem localhost-cert.pem.bak
   ```

3. **Relancer le serveur** :
   ```bash
   python3 rag_assistant_server.py
   ```

## 🧪 Test

Après relance en HTTP :

1. **Vérifier** :
   ```bash
   curl http://localhost:8711/rag-assistant -X POST \
     -H "Content-Type: application/json" \
     -d '{"question":"test"}'
   ```

2. **Recharger l'extension** dans `chrome://extensions`

3. **Tester** sur `https://www.amiens.fr`

## 📝 Notes

- HTTP sur localhost est sécurisé pour le développement
- Les certificats sont sauvegardés (peuvent être restaurés)
- En production, utiliser HTTPS avec certificat valide

