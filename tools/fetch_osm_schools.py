#!/usr/bin/env python3
"""
Récupère les écoles d'Amiens via Overpass API (OpenStreetMap).
"""
import json
import requests
from pathlib import Path
from typing import List, Dict, Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "data" / "ecoles_amiens.json"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def fetch_schools_from_osm(city: str = "Amiens") -> List[Dict[str, Any]]:
    """Récupère les écoles via Overpass API."""
    query = f"""
    [out:json][timeout:25];
    area["name"="{city}"]->.a;
    (
      node["amenity"="school"](area.a);
      way["amenity"="school"](area.a);
      relation["amenity"="school"](area.a);
    );
    out center;
    """
    
    print(f"🔍 Récupération écoles depuis OSM (ville: {city})...")
    
    try:
        response = requests.post(
            OVERPASS_URL,
            data={"data": query},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        schools = []
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            name = tags.get("name", "École sans nom")
            
            # Coordonnées
            if "lat" in element and "lon" in element:
                lat, lon = element["lat"], element["lon"]
            elif "center" in element:
                lat, lon = element["center"]["lat"], element["center"]["lon"]
            else:
                continue
            
            # Adresse
            address_parts = []
            if tags.get("addr:housenumber"):
                address_parts.append(tags["addr:housenumber"])
            if tags.get("addr:street"):
                address_parts.append(tags["addr:street"])
            address = " ".join(address_parts) if address_parts else None
            
            school = {
                "nom": name,
                "adresse": address or tags.get("addr:full"),
                "code_postal": tags.get("addr:postcode", "80000"),
                "ville": tags.get("addr:city", city),
                "coordonnees": {
                    "lat": lat,
                    "lon": lon
                },
                "type": tags.get("amenity", "school"),
                "niveau": tags.get("isced:level"),  # Niveau scolaire si disponible
                "osm_id": element.get("id"),
                "osm_type": element.get("type")
            }
            
            schools.append(school)
        
        print(f"✅ {len(schools)} école(s) trouvée(s)")
        return schools
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

def map_secteur_from_coordinates(lat: float, lon: float) -> str:
    """Détermine le secteur depuis les coordonnées (approximatif)."""
    # Amiens centre approximatif
    centre_lat, centre_lon = 49.8942, 2.2958
    
    # Calcul direction approximative
    delta_lat = lat - centre_lat
    delta_lon = lon - centre_lon
    
    if abs(delta_lat) < 0.01 and abs(delta_lon) < 0.01:
        return "Centre"
    elif delta_lat > 0:
        return "Sud" if abs(delta_lon) < 0.01 else ("Sud-Est" if delta_lon > 0 else "Sud-Ouest")
    else:
        return "Nord" if abs(delta_lon) < 0.01 else ("Nord-Est" if delta_lon > 0 else "Nord-Ouest")

def main():
    schools = fetch_schools_from_osm("Amiens")
    
    if not schools:
        print("⚠️ Aucune école récupérée")
        return
    
    # Ajouter secteur approximatif
    for school in schools:
        if school["coordonnees"]:
            school["secteur_approximatif"] = map_secteur_from_coordinates(
                school["coordonnees"]["lat"],
                school["coordonnees"]["lon"]
            )
    
    # Sauvegarder
    output_data = {
        "source": "OpenStreetMap Overpass API",
        "total": len(schools),
        "ecoles": schools
    }
    
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Données sauvegardées: {OUTPUT_PATH}")
    print(f"📊 {len(schools)} école(s) avec coordonnées")

if __name__ == "__main__":
    main()

