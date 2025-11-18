#!/usr/bin/env python3
"""
Script simple pour vérifier l'état du test des 40 questions
À exécuter dans l'IDE pour voir la progression
"""
import json
from pathlib import Path
from datetime import datetime

LOG_FILE = Path(__file__).parent / "test_40_questions_output.log"
RESULTS_FILE = Path(__file__).parent / "test_results_40_questions.json"
CSV_FILE = Path(__file__).parent / "test_results_40_questions.csv"

print("=" * 80)
print("📊 ÉTAT DU TEST 40 QUESTIONS")
print("=" * 80)
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Vérifier si le test tourne
if LOG_FILE.exists():
    with LOG_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Compter les questions traitées
    import re
    last_question = 0
    for line in lines:
        match = re.search(r'\[(\d+)/45\]', line)
        if match:
            last_question = max(last_question, int(match.group(1)))
    
    # Vérifier si terminé
    is_completed = "FIN DES TESTS" in "".join(lines[-20:])
    
    print(f"📈 PROGRESSION: {last_question}/45 ({last_question*100/45:.1f}%)")
    print(f"🔄 Statut: {'✅ TERMINÉ' if is_completed else '🔄 EN COURS'}")
    print()
    
    # Dernières lignes du log
    print("📝 DERNIÈRES LIGNES DU LOG:")
    print("-" * 80)
    for line in lines[-5:]:
        if line.strip():
            print(f"   {line.strip()[:75]}")
    print()
else:
    print("⏳ Test pas encore démarré ou log introuvable")
    print()

# Vérifier les résultats
if RESULTS_FILE.exists():
    print("✅ FICHIER DE RÉSULTATS TROUVÉ")
    print("-" * 80)
    
    with RESULTS_FILE.open("r", encoding="utf-8") as f:
        results = json.load(f)
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    print(f"📊 Total: {len(results)} questions")
    print(f"   ✅ Réussies: {len(successful)} ({len(successful)*100/len(results):.1f}%)")
    print(f"   ❌ Échouées: {len(failed)}")
    print()
    
    # Stats par type
    où_tests = [r for r in successful if r.get("type") == "où"]
    quand_tests = [r for r in successful if r.get("type") == "quand"]
    comment_tests = [r for r in successful if r.get("type") == "comment"]
    
    print("📊 PAR TYPE:")
    print(f"   Où: {len(où_tests)}/{len([r for r in results if r.get('type') == 'où'])}")
    print(f"   Quand: {len(quand_tests)}/{len([r for r in results if r.get('type') == 'quand'])}")
    print(f"   Comment: {len(comment_tests)}/{len([r for r in results if r.get('type') == 'comment'])}")
    print()
    
    # Adresses
    où_with_address = [r for r in où_tests if r.get("has_address")]
    print(f"📍 Adresses trouvées: {len(où_with_address)}/{len(où_tests)}")
    print()
    
    # Alignements
    aligned = [r for r in successful if r.get("alignment_status") in ["aligned", "partial"]]
    print(f"🎯 Alignements: {len(aligned)}/{len(successful)} ({len(aligned)*100/max(len(successful),1):.1f}%)")
    print()
    
    print(f"💾 Fichiers disponibles:")
    print(f"   - {RESULTS_FILE.name}")
    if CSV_FILE.exists():
        print(f"   - {CSV_FILE.name}")
else:
    print("⏳ Résultats pas encore disponibles")
    print()

print("=" * 80)
print("💡 Pour relancer le monitoring: python3 tests/check_test_status.py")
print("=" * 80)

