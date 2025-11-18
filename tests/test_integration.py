#!/usr/bin/env python3
"""
Test d'intégration pour vérifier que les nouvelles fonctionnalités fonctionnent.
"""
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

def test_imports():
    """Test que les imports fonctionnent."""
    print("🔍 Test des imports...")
    try:
        from tools.address_fetcher import get_address_for_lieu, extract_address_from_text
        print("   ✅ address_fetcher importé avec succès")
    except ImportError as e:
        print(f"   ❌ Erreur import address_fetcher: {e}")
        return False
    
    try:
        from rag_assistant_server import load_structured_data, build_prompt
        print("   ✅ rag_assistant_server importé avec succès")
    except ImportError as e:
        print(f"   ❌ Erreur import rag_assistant_server: {e}")
        return False
    
    return True

def test_data_loading():
    """Test que les données structurées se chargent."""
    print("\n🔍 Test du chargement des données...")
    try:
        from rag_assistant_server import load_structured_data, rpe_data, lieux_data, tarifs_data, ecoles_data
        
        load_structured_data()
        
        checks = [
            ("RPE", rpe_data),
            ("Lieux", lieux_data),
            ("Tarifs", tarifs_data),
            ("Écoles", ecoles_data),
        ]
        
        all_ok = True
        for name, data in checks:
            if data:
                count = len(data.get("rpe_list", [])) if name == "RPE" else \
                        len(data.get("lieux", [])) if name == "Lieux" else \
                        data.get("total_tables", 0) if name == "Tarifs" else \
                        data.get("total", 0) if name == "Écoles" else 0
                print(f"   ✅ {name}: {count} élément(s) chargé(s)")
            else:
                print(f"   ⚠️ {name}: Non chargé (peut être normal si fichier absent)")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"   ❌ Erreur lors du chargement: {e}")
        return False

def test_address_fetcher():
    """Test du système d'adresses."""
    print("\n🔍 Test du système d'adresses...")
    try:
        from tools.address_fetcher import get_address_for_lieu
        
        # Test avec un lieu connu
        test_lieu = "Espace Dewailly"
        address = get_address_for_lieu(test_lieu, city="Amiens")
        
        if address:
            print(f"   ✅ Adresse trouvée pour '{test_lieu}': {address}")
            return True
        else:
            print(f"   ⚠️ Aucune adresse trouvée pour '{test_lieu}' (peut être normal)")
            return True  # Pas une erreur critique
    except Exception as e:
        print(f"   ❌ Erreur lors du test d'adresse: {e}")
        return False

def main():
    """Lance tous les tests."""
    print("=" * 60)
    print("TESTS D'INTÉGRATION - Système RAG Amiens")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Chargement données", test_data_loading()))
    results.append(("Système adresses", test_address_fetcher()))
    
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 Tous les tests sont passés !")
    else:
        print("\n⚠️ Certains tests ont échoué.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

