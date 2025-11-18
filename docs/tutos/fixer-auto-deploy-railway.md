# 🔧 Fixer le Déploiement Automatique Railway

## 🔍 Problème

Le déploiement automatique depuis GitHub ne fonctionne pas. Il faut lancer `railway up` manuellement.

## ✅ Solutions

### 1. Vérifier la Connexion GitHub

1. Va sur [railway.app](https://railway.app) → Ton projet
2. **Settings** → **Source**
3. Vérifie que :
   - ✅ Le repo GitHub est bien connecté
   - ✅ La branche surveillée est `main` (ou la bonne branche)
   - ✅ Le statut est "Connected"

**Si pas connecté** :
1. Clique sur **"Connect GitHub"**
2. Autorise Railway à accéder au repo
3. Sélectionne la branche `main`

---

### 2. Vérifier les Webhooks GitHub

1. Va sur GitHub → Ton repo → **Settings** → **Webhooks**
2. Vérifie qu'il y a un webhook Railway :
   - URL : `https://api.railway.app/v1/webhooks/github`
   - Événements : `push` activé
   - Statut : ✅ Active (verte)

**Si pas de webhook** :
- Railway devrait le créer automatiquement lors de la connexion
- Si absent, reconnecte le repo dans Railway

---

### 3. Vérifier la Branche

Railway surveille seulement la branche configurée (généralement `main`).

**Vérifie** :
- Railway → Settings → Source → Branch = `main`
- Tes pushes sont bien sur `main` (pas sur une autre branche)

---

### 4. Forcer la Reconnexion

Si rien ne fonctionne :

1. Railway → Settings → Source
2. **Disconnect** le repo
3. **Connect GitHub** à nouveau
4. Sélectionne le repo et la branche `main`
5. Railway va recréer le webhook automatiquement

---

### 5. Tester le Déploiement Auto

1. Fais un petit changement (ex: commentaire dans un fichier)
2. Commit + Push sur `main`
3. Va sur Railway → Deployments
4. Tu devrais voir un nouveau déploiement démarrer automatiquement

---

## 🆘 Si ça ne fonctionne toujours pas

### Option A : Déploiement Manuel (Temporaire)

Utilise `railway up` pour déployer manuellement :
```bash
railway up
```

**Avantages** :
- ✅ Fonctionne immédiatement
- ✅ Déploie depuis code local

**Inconvénients** :
- ❌ Pas automatique
- ❌ Rebuild complet à chaque fois

### Option B : Vérifier les Logs Railway

1. Railway → Deployments
2. Regarde les logs du dernier déploiement
3. Cherche des erreurs de connexion GitHub

### Option C : Contacter le Support Railway

Si rien ne fonctionne :
- Railway Dashboard → Support
- Ou [discord.gg/railway](https://discord.gg/railway)

---

## 📋 Checklist de Vérification

- [ ] Repo GitHub connecté dans Railway
- [ ] Branche `main` configurée
- [ ] Webhook GitHub présent et actif
- [ ] Push effectué sur `main` (pas autre branche)
- [ ] Test : petit changement + push → déploiement auto

---

## 💡 Bonnes Pratiques

1. **Toujours push sur `main`** pour déclencher le déploiement auto
2. **Vérifier Railway Dashboard** après chaque push pour confirmer le déploiement
3. **Utiliser `railway up`** seulement pour tester du code local avant push

---

*Dernière mise à jour : 2025-11-18*

