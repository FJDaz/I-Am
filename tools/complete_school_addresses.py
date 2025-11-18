#!/usr/bin/env python3
"""
Complète les adresses des écoles via Nominatim (reverse geocoding).
Utilise les coordonnées pour récupérer les adresses complètes.
"""
import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "ecoles_amiens.json"
OUTPUT_PATH = ROOT / "data" / "ecoles_amiens.json"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
# Rate limiting : 1 requête par seconde (politesse Nominatim)
DELAY_BETWEEN_REQUESTS = 1.1

def fetch_address_from_coordinates(lat: float, lon: float) -> Optional[str]:
    """Récupère l'adresse via reverse geocoding (coordonnées → adresse)."""
    try:
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "addressdetails": 1,
            "zoom": 18  # Niveau de détail élevé
        }
        headers = {
            "User-Agent": "Amiens-RAG-Assistant/1.0 (contact: amiens-rag@example.com)"
        }
        
        response = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=10)
        if response.ok:
            data = response.json()
            address = data.get("address", {})
            
            # Construire adresse complète
            address_parts = []
            if address.get("house_number"):
                address_parts.append(address["house_number"])
            if address.get("road"):
                address_parts.append(address["road"])
            
            if address_parts:
                # Ajouter code postal et ville si disponibles
                postcode = address.get("postcode", "")
                city = address.get("city") or address.get("town") or address.get("village", "Amiens")
                full_address = " ".join(address_parts)
                if postcode:
                    full_address += f", {postcode} {city}"
                elif city != "Amiens":
                    full_address += f", {city}"
                return full_address
            elif data.get("display_name"):
                # Fallback sur display_name
                return data["display_name"]
    except Exception as e:
        print(f"   ⚠️ Erreur pour ({lat}, {lon}): {e}")
    
    return None

def complete_addresses(input_path: Path, output_path: Path, max_schools: Optional[int] = None):
    """Complète les adresses manquantes des écoles."""
    print(f"📄 Chargement depuis {input_path.name}...")
    
    if not input_path.exists():
        print(f"❌ Fichier introuvable: {input_path}")
        return
    
    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    schools = data.get("ecoles", [])
    total = len(schools)
    
    # Filtrer les écoles sans adresse
    schools_to_complete = [
        s for s in schools 
        if not s.get("adresse") and s.get("coordonnees")
    ]
    
    print(f"📊 {total} école(s) au total")
    print(f"🔍 {len(schools_to_complete)} école(s) sans adresse à compléter")
    
    if max_schools:
        schools_to_complete = schools_to_complete[:max_schools]
        print(f"⚠️ Limitation à {max_schools} école(s) pour ce test")
    
    if not schools_to_complete:
        print("✅ Toutes les écoles ont déjà une adresse !")
        return
    
    # Compléter les adresses
    completed = 0
    failed = 0
    
    for i, school in enumerate(schools_to_complete, 1):
        nom = school.get("nom", "Sans nom")
        coords = school.get("coordonnees", {})
        lat = coords.get("lat")
        lon = coords.get("lon")
        
        if not lat or not lon:
            print(f"   [{i}/{len(schools_to_complete)}] ⚠️ {nom}: Pas de coordonnées")
            failed += 1
            continue
        
        print(f"   [{i}/{len(schools_to_complete)}] 🔍 {nom}...", end=" ", flush=True)
        
        address = fetch_address_from_coordinates(lat, lon)
        
        if address:
            # Trouver l'école dans la liste complète et mettre à jour
            for s in schools:
                if s.get("osm_id") == school.get("osm_id"):
                    s["adresse"] = address
                    break
            print(f"✅ {address}")
            completed += 1
        else:
            print("❌ Non trouvée")
            failed += 1
        
        # Rate limiting : attendre entre les requêtes
        if i < len(schools_to_complete):
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Sauvegarder
    print(f"\n💾 Sauvegarde...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Résultats:")
    print(f"   - Adresses complétées: {completed}")
    print(f"   - Échecs: {failed}")
    print(f"   - Total traité: {len(schools_to_complete)}")
    print(f"   - Fichier sauvegardé: {output_path}")

def main():
    import sys
    
    # Option pour limiter le nombre d'écoles (utile pour tester)
    max_schools = None
    if len(sys.argv) > 1:
        try:
            max_schools = int(sys.argv[1])
        except ValueError:
            print("⚠️ Usage: python complete_school_addresses.py [max_schools]")
            print("   Exemple: python complete_school_addresses.py 10  (pour tester avec 10 écoles)")
    
    complete_addresses(INPUT_PATH, OUTPUT_PATH, max_schools)

if __name__ == "__main__":
    main()

