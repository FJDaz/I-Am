#!/usr/bin/env python3
"""
Système de récupération d'adresses : Site → OSM → Google Maps (fallback)
"""
import json
import re
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = ROOT / "data" / "lieux_cache.json"

# Charger cache
def load_cache() -> Dict[str, str]:
    """Charge le cache d'adresses."""
    if CACHE_PATH.exists():
        try:
            with CACHE_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache: Dict[str, str]):
    """Sauvegarde le cache."""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CACHE_PATH.open("w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def extract_address_from_text(text: str) -> Optional[str]:
    """Extrait une adresse depuis un texte (regex numéro + rue)."""
    if not text:
        return None
    
    # Pattern : numéro + rue/avenue/boulevard/place
    patterns = [
        r'\d+\s+(?:rue|avenue|boulevard|place|allée|chemin|impasse|route)\s+[^,\n]{5,50}',
        r'\d+\s+[A-Z][^,\n]{10,50}(?:rue|avenue|boulevard|place)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            address = match.group(0).strip()
            # Nettoyer
            address = re.sub(r'\s+', ' ', address)
            if len(address) > 10:  # Adresse valide
                return address
    
    return None

def fetch_address_from_osm(lieu_nom: str, city: str = "Amiens") -> Optional[str]:
    """Récupère l'adresse via Nominatim (OSM)."""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": f"{lieu_nom} {city}",
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }
        headers = {
            "User-Agent": "Amiens-RAG-Assistant/1.0"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.ok:
            data = response.json()
            if data:
                result = data[0]
                # Construire adresse complète
                address_parts = []
                if result.get("address", {}).get("house_number"):
                    address_parts.append(result["address"]["house_number"])
                if result.get("address", {}).get("road"):
                    address_parts.append(result["address"]["road"])
                if address_parts:
                    address = " ".join(address_parts) + f", {city}"
                    return address
                elif result.get("display_name"):
                    return result["display_name"]
    except Exception as e:
        print(f"⚠️ Erreur OSM: {e}")
    
    return None

def fetch_address_from_google_maps(lieu_nom: str, city: str = "Amiens") -> Optional[str]:
    """Récupère l'adresse via Google Maps API (fallback)."""
    # Note: Nécessite une clé API Google Maps
    # Pour l'instant, retourne None (à implémenter si nécessaire)
    return None

def get_address_for_lieu(
    lieu_nom: str,
    segments_rag: Optional[List[Any]] = None,
    city: str = "Amiens"
) -> Optional[str]:
    """
    Récupère l'adresse d'un lieu : Site → OSM → Google Maps.
    Sauvegarde dans cache pour réutilisation.
    """
    cache = load_cache()
    
    # Vérifier cache d'abord
    if lieu_nom.lower() in cache:
        return cache[lieu_nom.lower()]
    
    # 1. Chercher dans segments RAG
    if segments_rag:
        for seg in segments_rag:
            content = getattr(seg, "content", "") or getattr(seg, "excerpt", "") or ""
            if lieu_nom.lower() in content.lower():
                address = extract_address_from_text(content)
                if address:
                    cache[lieu_nom.lower()] = address
                    save_cache(cache)
                    return address
    
    # 2. Si pas trouvé, chercher sur OSM
    address = fetch_address_from_osm(lieu_nom, city)
    if address:
        cache[lieu_nom.lower()] = address
        save_cache(cache)
        return address
    
    # 3. Fallback Google Maps (si implémenté)
    address = fetch_address_from_google_maps(lieu_nom, city)
    if address:
        cache[lieu_nom.lower()] = address
        save_cache(cache)
        return address
    
    return None

if __name__ == "__main__":
    # Test
    test_lieux = ["Espace Dewailly", "RPE Babillages"]
    for lieu in test_lieux:
        print(f"\n🔍 Recherche adresse: {lieu}")
        address = get_address_for_lieu(lieu)
        if address:
            print(f"   ✅ {address}")
        else:
            print(f"   ❌ Non trouvée")

