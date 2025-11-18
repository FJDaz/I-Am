#!/usr/bin/env python3
"""
Gestionnaire automatique du fichier RESUME_CONTEXTE.md
- Si n'existe pas : crée le fichier
- Sinon : met à jour avec nouvelles informations
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
RESUME_PATH = ROOT / "docs" / "tests" / "RESUME_CONTEXTE.md"

TEMPLATE = """# Résumé de Contexte - Améliorations RAG Amiens

## 📋 Contexte Général

Travail sur l'amélioration du système RAG pour répondre aux 10 tests identifiés. L'objectif est d'enrichir les sources de données et d'améliorer les heuristiques pour fournir des réponses plus précises et complètes.

---

## ✅ Ce Qui A Été Fait

### 1. Extraction Tableaux Tarifs ✅
- **Module créé** : `tools/extract_tarif_tables.py`
- **Fichier généré** : `data/tarifs_2024_2025.json`
- **Résultat** : 5 tableaux extraits (2 cantine, 3 autres)
- **Intégration** : ✅ Injecté dans `build_prompt()` quand question tarifaire
- **Status** : Fonctionnel mais format HTML peut être amélioré

### 2. Récupération Écoles OSM ✅
- **Module créé** : `tools/fetch_osm_schools.py`
- **Fichier généré** : `data/ecoles_amiens.json`
- **Résultat** : 255 écoles avec coordonnées + secteurs approximatifs
- **Intégration** : ✅ Injecté dans `build_prompt()` quand question écoles
- **Status** : Fonctionnel mais adresses partielles, contacts manquants

### 3. Système Adresses Dynamique ✅
- **Module créé** : `tools/address_fetcher.py`
- **Fichier cache** : `data/lieux_cache.json` (auto-créé)
- **Stratégie** : Site → OSM Nominatim → Google Maps (fallback non implémenté)
- **Test** : ✅ Fonctionne (Espace Dewailly trouvé)
- **Status** : ✅ Intégré dans `build_prompt()`

### 4. Amélioration Heuristiques ✅
- **RPE** : ✅ Utilise maintenant `match_lexicon_entries()` au lieu de liste en dur
- **Lieux** : ✅ Détection plus précise (lieu mentionné ET question géographique)
- **Tarifs** : ✅ Détection élargie avec plus de termes
- **Écoles** : ✅ Nouvelle détection ajoutée

### 5. Vérification API Carte ⚠️
- **Module créé** : `tools/check_carte_api.py`
- **Problème** : Erreur SSL (certificat)
- **Status** : Script créé mais non fonctionnel (problème SSL)

### 6. Chargement Données Structurées ✅
- **Intégration** : ✅ `load_structured_data()` charge maintenant :
  - RPE (`rpe_contacts.json`)
  - Lieux (`lieux_importants.json`)
  - Tarifs (`tarifs_2024_2025.json`)
  - Écoles (`ecoles_amiens.json`)

---

## ⏳ Ce Qui Reste À Faire (TODO List)

### ✅ Complété
- [x] Vérifier si API carte interactive est accessible
- [x] Extraire tableaux tarifs depuis PDF syn+tarif
- [x] Implémenter requête OSM Overpass pour récupérer écoles Amiens
- [x] Créer système adresses dynamique (Site → OSM → Google Maps) avec cache
- [x] Améliorer heuristiques RPE (utiliser lexique au lieu de liste en dur)

### ⏳ En Attente

#### Priorité 4 : Endpoint Périscolaire (POC)
- [ ] **Investiguer endpoint autocomplete**
  - Analyser JS page "Avant-Après l'école"
  - Intercepter requêtes réseau (DevTools)
  - Reverse engineer si possible
  - **Note** : POC si commande

#### Priorité 5 : Améliorations Complémentaires
- [ ] **Mapping secteur → RPE**
  - Fonction pour déterminer RPE selon secteur utilisateur
  - Utiliser dans `follow_up_question`
- [ ] **Récupérer téléphones et emails des écoles**
  - Scraping site Amiens.fr
  - OSM Overpass (faible taux)
  - Patterns génériques pour emails

---

## 📊 État des Données

| Donnée | Fichier | Éléments | Intégration | Status |
|--------|---------|----------|--------------|--------|
| RPE | `data/rpe_contacts.json` | 5 RPE | ✅ | OK |
| Lieux | `data/lieux_importants.json` | 1 lieu | ✅ | OK |
| Tarifs | `data/tarifs_2024_2025.json` | 5 tableaux | ✅ | ⚠️ Format à améliorer |
| Écoles | `data/ecoles_amiens.json` | 255 écoles | ✅ | ⚠️ Adresses incomplètes |
| Cache adresses | `data/lieux_cache.json` | Auto | ✅ | ✅ Intégré |

---

## 🎯 Impact sur les Tests

| Test | Status | Action Restante |
|------|--------|-----------------|
| Test 1 (Liste RPE) | ✅ Résolu | Aucune |
| Test 2 (Tableaux tarifs) | ⚠️ Partiel | Améliorer format HTML |
| Test 3 (Liste écoles) | ⚠️ Partiel | Compléter adresses, investiguer endpoint |
| Test 5 (Adresses) | ✅ Résolu | Intégration `address_fetcher` complétée |
| Test 6 (Mapping secteur→RPE) | ❌ Non fait | Créer fonction mapping |
| Test 7 (Tarifs ALSH été) | ✅ Résolu | Aucune |
| Test 8 (Activités vacances) | ❌ Non fait | Améliorer lexique |
| Test 9 & 10 (DRE, PAI) | ❌ Non fait | Mapping questions→dispositifs |

---

## 🔧 Modules Créés

1. ✅ `tools/extract_tarif_tables.py` - Extraction tableaux PDF
2. ✅ `tools/fetch_osm_schools.py` - Récupération écoles OSM
3. ✅ `tools/address_fetcher.py` - Système adresses dynamique
4. ⚠️ `tools/check_carte_api.py` - Vérification API (problème SSL)

---

## 📝 Fichiers de Documentation

- ✅ `docs/tests/PROMPT_ACTION.md` - Plan d'action initial
- ✅ `docs/tests/RETOUR_TOUR_SITE.md` - Analyse commentaires utilisateur
- ✅ `docs/tests/RESULTATS_IMPLÉMENTATION.md` - Résultats détaillés
- ✅ `docs/tests/BILAN_IMPLÉMENTATION.md` - Bilan complet
- ✅ `docs/tests/RESUME_CONTEXTE.md` - Ce document

---

## ⚠️ Points d'Attention

1. **Google Maps** : Non implémenté (nécessite clé API)
2. **API carte** : Problème SSL non résolu
3. **Endpoint périscolaire** : Mystère, nécessite investigation manuelle
4. **Format tableaux** : Peut être amélioré pour meilleure lisibilité

---

## 📌 Notes Importantes

- **PDF tarifs** : Contient TOUS les tarifs (ALSH, cantine, périscolaire) - source majeure
- **OSM** : Fonctionne bien pour écoles, alternative à API carte
- **Cache adresses** : Système prêt et intégré automatiquement
- **Heuristiques** : Améliorées mais peuvent encore être affinées

---

*Dernière mise à jour : {date}*
"""

def check_resume_contexte_exists() -> bool:
    """Vérifie si RESUME_CONTEXTE.md existe."""
    return RESUME_PATH.exists()

def create_resume_contexte() -> None:
    """Crée RESUME_CONTEXTE.md avec structure de base."""
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = TEMPLATE.format(date=date)
    
    RESUME_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESUME_PATH.open("w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ RESUME_CONTEXTE.md créé : {RESUME_PATH}")

def update_resume_contexte(updates: Dict[str, Any]) -> None:
    """Met à jour RESUME_CONTEXTE.md avec nouvelles informations."""
    if not RESUME_PATH.exists():
        create_resume_contexte()
        return
    
    # Lire le fichier actuel
    with RESUME_PATH.open("r", encoding="utf-8") as f:
        content = f.read()
    
    # Mettre à jour selon les updates
    # TODO: Implémenter logique de mise à jour intelligente
    # Pour l'instant, on ajoute juste une note de mise à jour
    
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Ajouter section de mise à jour si elle n'existe pas
    if "## 🔄 Dernières Mises à Jour" not in content:
        updates_section = f"\n\n## 🔄 Dernières Mises à Jour\n\n"
        updates_section += f"**{date}** :\n"
        if "completed_tasks" in updates:
            updates_section += f"- Tâches complétées : {', '.join(updates['completed_tasks'])}\n"
        if "new_modules" in updates:
            updates_section += f"- Nouveaux modules : {', '.join(updates['new_modules'])}\n"
        updates_section += "\n"
        
        # Insérer avant "⚠️ Points d'Attention"
        if "## ⚠️ Points d'Attention" in content:
            content = content.replace("## ⚠️ Points d'Attention", updates_section + "## ⚠️ Points d'Attention")
        else:
            content += updates_section
    
    # Mettre à jour la date en bas
    content = re.sub(r'\*Dernière mise à jour : .+\*', f'*Dernière mise à jour : {date}*', content)
    
    # Sauvegarder
    with RESUME_PATH.open("w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ RESUME_CONTEXTE.md mis à jour : {RESUME_PATH}")

def main():
    """Fonction principale pour tester."""
    if not check_resume_contexte_exists():
        print("📝 Création de RESUME_CONTEXTE.md...")
        create_resume_contexte()
    else:
        print("✅ RESUME_CONTEXTE.md existe déjà")
        print("📝 Test de mise à jour...")
        update_resume_contexte({
            "completed_tasks": ["Test de mise à jour"],
            "new_modules": ["resume_contexte_manager.py"]
        })

if __name__ == "__main__":
    main()

