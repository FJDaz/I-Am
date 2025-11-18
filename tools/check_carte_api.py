#!/usr/bin/env python3
"""
Vérifie si l'API de la carte interactive est accessible.
"""
import requests
import json
from pathlib import Path
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CARTE_URL = "https://geo.amiens-metropole.com/adws/app/523da8c6-5dbc-11ec-9790-3dc5639e7001/index.html"

def check_carte_api():
    """Vérifie l'accessibilité de l'API carte."""
    print("🔍 Vérification API carte interactive...\n")
    
    # 1. Tester la page principale
    print("1. Test page principale...")
    try:
        response = requests.get(CARTE_URL, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Page accessible")
            
            # Chercher endpoints dans le HTML
            html = response.text
            if "api" in html.lower() or "endpoint" in html.lower():
                print("   ⚠️ Mentions 'api' ou 'endpoint' trouvées dans le HTML")
            if ".json" in html or "application/json" in html:
                print("   ⚠️ Références JSON trouvées")
        else:
            print(f"   ❌ Page non accessible (status {response.status_code})")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 2. Tester endpoints possibles
    print("\n2. Test endpoints possibles...")
    endpoints = [
        "/api/data",
        "/api/ecoles",
        "/data.json",
        "/ecoles.json",
        "/adws/api/data",
    ]
    
    base_url = "https://geo.amiens-metropole.com"
    for endpoint in endpoints:
        try:
            url = base_url + endpoint
            response = requests.get(url, timeout=5, verify=False)
            if response.status_code == 200:
                print(f"   ✅ {endpoint} accessible")
                try:
                    data = response.json()
                    print(f"      JSON valide, {len(data)} éléments")
                except:
                    print(f"      Contenu: {response.text[:100]}...")
            elif response.status_code == 404:
                pass  # Endpoint n'existe pas, normal
        except:
            pass
    
    # 3. Analyser JS de la page
    print("\n3. Analyse JS de la page...")
    try:
        response = requests.get(CARTE_URL, timeout=10)
        html = response.text
        
        # Chercher scripts JS
        import re
        js_urls = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', html)
        if js_urls:
            print(f"   📜 {len(js_urls)} scripts JS trouvés")
            for js_url in js_urls[:3]:  # Limiter à 3
                if not js_url.startswith('http'):
                    js_url = "https://geo.amiens-metropole.com" + js_url
                print(f"      - {js_url}")
        
        # Chercher appels API dans le HTML
        api_calls = re.findall(r'(fetch|axios|\.get|\.post)\(["\']([^"\']+)["\']', html)
        if api_calls:
            print(f"   🔌 {len(api_calls)} appels API potentiels trouvés")
            for method, url in api_calls[:5]:
                print(f"      - {method}: {url}")
    except Exception as e:
        print(f"   ❌ Erreur analyse: {e}")
    
    print("\n✅ Vérification terminée")

if __name__ == "__main__":
    check_carte_api()

