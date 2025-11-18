#!/usr/bin/env python3
"""
Test avec 10 questions contenant "où, quand, comment" pour valider
les améliorations du système RAG, notamment le système d'adresses dynamique.
"""
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Any

# Configuration
SERVER_URL = "https://localhost:8711/rag-assistant"

# 10 questions de test avec "où, quand, comment"
TEST_QUESTIONS = [
    {
        "question": "Où se trouve l'Espace Dewailly ?",
        "category": "géographique",
        "expected_keywords": ["Espace Dewailly", "adresse"],
        "type": "où"
    },
    {
        "question": "Où puis-je inscrire mon enfant à la crèche ?",
        "category": "inscription",
        "expected_keywords": ["RPE", "relais", "adresse"],
        "type": "où"
    },
    {
        "question": "Quand sont les inscriptions pour la cantine ?",
        "category": "inscription",
        "expected_keywords": ["cantine", "inscription"],
        "type": "quand"
    },
    {
        "question": "Comment s'inscrire au périscolaire ?",
        "category": "inscription",
        "expected_keywords": ["périscolaire", "inscription"],
        "type": "comment"
    },
    {
        "question": "Où est située l'école élémentaire Victoria ?",
        "category": "géographique",
        "expected_keywords": ["école", "Victoria", "adresse"],
        "type": "où"
    },
    {
        "question": "Quand a lieu l'accueil du mercredi ?",
        "category": "horaires",
        "expected_keywords": ["mercredi", "accueil", "horaires"],
        "type": "quand"
    },
    {
        "question": "Comment calculer le tarif de la cantine ?",
        "category": "tarifs",
        "expected_keywords": ["tarif", "cantine", "quotient"],
        "type": "comment"
    },
    {
        "question": "Où trouver la liste des écoles d'Amiens ?",
        "category": "géographique",
        "expected_keywords": ["école", "liste"],
        "type": "où"
    },
    {
        "question": "Quand commencent les vacances d'été ?",
        "category": "calendrier",
        "expected_keywords": ["vacances", "été"],
        "type": "quand"
    },
    {
        "question": "Comment obtenir les tarifs pour l'ALSH ?",
        "category": "tarifs",
        "expected_keywords": ["tarif", "ALSH", "centre de loisirs"],
        "type": "comment"
    }
]

def test_question(test_case: Dict) -> Dict:
    """Teste une question et retourne les métriques."""
    question = test_case["question"]
    
    payload = {
        "question": question,
        "normalized_question": question.lower(),
        "rag_results": [],
        "conversation": []
    }

    start_time = time.time()
    try:
        response = requests.post(
            SERVER_URL,
            json=payload,
            verify=False,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        elapsed = time.time() - start_time
        
        # Analyser les résultats
        sources = result.get('sources', [])
        alignment = result.get('alignment', {})
        answer_html = result.get('answer_html', '')
        answer_text = result.get('answer_text', '')
        follow_up = result.get('follow_up_question', '')
        
        # Vérifier la présence des mots-clés attendus
        keywords_found = []
        keywords_missing = []
        full_text = (answer_html + " " + answer_text).lower()
        
        for keyword in test_case.get('expected_keywords', []):
            if keyword.lower() in full_text:
                keywords_found.append(keyword)
            else:
                keywords_missing.append(keyword)
        
        # Vérifier si une adresse a été trouvée (pour questions "où")
        has_address = False
        if test_case.get("type") == "où":
            # Chercher des patterns d'adresse dans la réponse
            import re
            address_patterns = [
                r'\d+\s+(?:rue|avenue|boulevard|place|allée|chemin)',
                r'\d{5}\s+[A-Z]',
                r'adresse[:\s]+[^<]+',
            ]
            for pattern in address_patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    has_address = True
                    break
        
        return {
            "success": True,
            "question": question,
            "category": test_case["category"],
            "type": test_case["type"],
            "elapsed_time": elapsed,
            "alignment_status": alignment.get('status', 'unknown'),
            "alignment_label": alignment.get('label', 'N/A'),
            "sources_count": len(sources),
            "keywords_found": keywords_found,
            "keywords_missing": keywords_missing,
            "has_address": has_address if test_case.get("type") == "où" else None,
            "has_answer": len(answer_text) > 50,
            "answer_preview": answer_text[:200] + "..." if len(answer_text) > 200 else answer_text,
            "follow_up": follow_up[:100] if follow_up else None,
            "sources_preview": [
                {
                    "title": s.get('title', 'N/A')[:60],
                    "confidence": s.get('confidence', 'N/A')
                }
                for s in sources[:3]
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "question": question,
            "category": test_case["category"],
            "type": test_case["type"],
            "error": str(e)
        }

def print_results(results: List[Dict]):
    """Affiche les résultats de manière formatée."""
    print("\n" + "=" * 100)
    print("RÉSULTATS DÉTAILLÉS")
    print("=" * 100)
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    # Statistiques par type
    où_tests = [r for r in successful if r.get("type") == "où"]
    quand_tests = [r for r in successful if r.get("type") == "quand"]
    comment_tests = [r for r in successful if r.get("type") == "comment"]
    
    print(f"\n📊 STATISTIQUES GLOBALES")
    print(f"   Total: {len(results)} questions")
    print(f"   ✅ Réussies: {len(successful)}")
    print(f"   ❌ Échouées: {len(failed)}")
    print(f"   Taux de réussite: {len(successful)*100/len(results):.0f}%")
    
    print(f"\n📊 PAR TYPE")
    print(f"   'Où' : {len(où_tests)}/{len([r for r in results if r.get('type') == 'où'])} réussies")
    print(f"   'Quand' : {len(quand_tests)}/{len([r for r in results if r.get('type') == 'quand'])} réussies")
    print(f"   'Comment' : {len(comment_tests)}/{len([r for r in results if r.get('type') == 'comment'])} réussies")
    
    # Adresses trouvées (pour questions "où")
    où_with_address = [r for r in où_tests if r.get("has_address")]
    print(f"\n📍 ADRESSES TROUVÉES (questions 'où')")
    print(f"   {len(où_with_address)}/{len(où_tests)} questions avec adresse trouvée")
    
    # Alignements
    aligned = [r for r in successful if r.get("alignment_status") in ["aligned", "partial"]]
    print(f"\n🎯 ALIGNEMENTS")
    print(f"   Alignés/Partiels: {len(aligned)}/{len(successful)} ({len(aligned)*100/max(len(successful),1):.0f}%)")
    
    # Mots-clés
    all_keywords_found = sum(len(r.get("keywords_found", [])) for r in successful)
    all_keywords_total = sum(len(r.get("expected_keywords", [])) for r in results)
    print(f"\n🔑 MOTS-CLÉS")
    print(f"   Trouvés: {all_keywords_found}/{all_keywords_total} ({all_keywords_found*100/max(all_keywords_total,1):.0f}%)")
    
    print(f"\n📋 DÉTAILS PAR QUESTION")
    print("-" * 100)
    
    for i, result in enumerate(results, 1):
        status = "✅" if result.get("success") else "❌"
        q_type = result.get("type", "N/A").upper()
        print(f"\n[{i}] {status} [{q_type}] {result.get('question', 'N/A')}")
        
        if result.get("success"):
            print(f"    ⏱️  Temps: {result.get('elapsed_time', 0):.2f}s")
            print(f"    🎯 Alignement: {result.get('alignment_status', 'N/A')} ({result.get('alignment_label', 'N/A')})")
            print(f"    📚 Sources: {result.get('sources_count', 0)}")
            
            keywords = result.get("keywords_found", [])
            missing = result.get("keywords_missing", [])
            if keywords:
                print(f"    ✅ Mots-clés trouvés: {', '.join(keywords)}")
            if missing:
                print(f"    ⚠️  Mots-clés manquants: {', '.join(missing)}")
            
            if result.get("has_address") is not None:
                addr_status = "✅" if result.get("has_address") else "❌"
                print(f"    {addr_status} Adresse: {'Trouvée' if result.get('has_address') else 'Non trouvée'}")
            
            if result.get("answer_preview"):
                print(f"    💬 Réponse: {result.get('answer_preview')[:150]}...")
        else:
            print(f"    ❌ Erreur: {result.get('error', 'Unknown')}")

def main():
    print("=" * 100)
    print("TESTS AVEC QUESTIONS 'OÙ, QUAND, COMMENT'")
    print("Validation des améliorations RAG (système d'adresses dynamique)")
    print("=" * 100)
    print(f"\n📋 {len(TEST_QUESTIONS)} questions à tester...\n")
    
    results = []
    for i, test_case in enumerate(TEST_QUESTIONS, 1):
        print(f"[{i}/{len(TEST_QUESTIONS)}] Test: {test_case['question'][:70]}...", end=" ", flush=True)
        result = test_question(test_case)
        results.append(result)
        
        if result.get("success"):
            status = result.get("alignment_status", "unknown")
            addr_info = ""
            if result.get("has_address") is not None:
                addr_info = f" | Adresse: {'✅' if result.get('has_address') else '❌'}"
            print(f"✅ [{status}]{addr_info}")
        else:
            print(f"❌ {result.get('error', 'Unknown')}")
        
        time.sleep(0.5)  # Petite pause entre les tests
    
    print_results(results)
    
    # Sauvegarder les résultats
    output_path = Path(__file__).parent / "test_results_ou_quand_comment.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Résultats sauvegardés: {output_path}")
    
    print("\n" + "=" * 100)
    print("FIN DES TESTS")
    print("=" * 100)

if __name__ == "__main__":
    main()

