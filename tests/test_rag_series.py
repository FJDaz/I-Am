"""
Série de tests RAG pour évaluer les performances avec le nouveau stemmer français
et les poids rééquilibrés (BM25: 1.0, Cosine: 0.6)
"""
import requests
import json
import time
from typing import Dict, List

# Configuration
SERVER_URL = "https://localhost:8711/rag-assistant"

# Supprimer les warnings SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Questions de test variées
TEST_QUESTIONS = [
    # Tests basiques
    {
        "question": "Comment inscrire mon enfant à la crèche ?",
        "category": "Inscription crèche",
        "expected_keywords": ["crèche", "inscription", "inscrire"]
    },
    {
        "question": "Quels sont les tarifs de la cantine scolaire ?",
        "category": "Tarifs cantine",
        "expected_keywords": ["cantine", "tarif", "prix"]
    },
    {
        "question": "Horaires accueil périscolaire",
        "category": "Horaires périscolaire",
        "expected_keywords": ["périscolaire", "horaires", "accueil"]
    },
    # Tests avec variations linguistiques (stemmer français)
    {
        "question": "Je veux inscrire mon enfant à une crèche",
        "category": "Variation inscription",
        "expected_keywords": ["crèche", "inscription"]
    },
    {
        "question": "Inscriptions aux crèches amiénoises",
        "category": "Variation pluriel",
        "expected_keywords": ["crèche", "inscription"]
    },
    {
        "question": "Comment faire garder mon enfant le mercredi ?",
        "category": "Garde mercredi",
        "expected_keywords": ["garde", "mercredi", "enfant"]
    },
    # Tests sémantiques (cosine similarity)
    {
        "question": "Tarif centre de loisirs vacances été",
        "category": "Tarifs ALSH",
        "expected_keywords": ["centre", "loisirs", "vacances", "été", "tarif"]
    },
    {
        "question": "Quel est le prix pour les activités pendant les vacances ?",
        "category": "Synonymes",
        "expected_keywords": ["prix", "activités", "vacances"]
    },
    # Tests avec termes techniques
    {
        "question": "DRE dispositif réussite éducative",
        "category": "Terme technique",
        "expected_keywords": ["DRE", "réussite", "éducative"]
    },
    {
        "question": "PAI projet accueil individualisé",
        "category": "Acronyme",
        "expected_keywords": ["PAI", "accueil", "individualisé"]
    }
]

def test_question(test_case: Dict) -> Dict:
    """Teste une question et retourne les métriques."""
    question = test_case["question"]
    payload = {
        "question": question,
        "rag_results": [],
        "normalized_question": question.lower(),
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
        answer = result.get('answer_text', '')
        
        # Vérifier la présence des mots-clés attendus
        keywords_found = []
        keywords_missing = []
        for keyword in test_case.get('expected_keywords', []):
            if keyword.lower() in answer.lower() or any(
                keyword.lower() in str(source.get('title', '')).lower() 
                for source in sources
            ):
                keywords_found.append(keyword)
            else:
                keywords_missing.append(keyword)
        
        return {
            "success": True,
            "question": question,
            "category": test_case["category"],
            "elapsed_time": elapsed,
            "alignment_status": alignment.get('status', 'unknown'),
            "alignment_label": alignment.get('label', 'N/A'),
            "sources_count": len(sources),
            "keywords_found": keywords_found,
            "keywords_missing": keywords_missing,
            "has_answer": len(answer) > 50,
            "answer_preview": answer[:150] + "..." if len(answer) > 150 else answer,
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
            "error": str(e)
        }

def print_results(results: List[Dict]):
    """Affiche les résultats de manière formatée."""
    print("\n" + "=" * 100)
    print("RÉSULTATS DES TESTS RAG")
    print("=" * 100)
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    print(f"\n✅ Tests réussis: {len(successful)}/{len(results)}")
    print(f"❌ Tests échoués: {len(failed)}/{len(results)}")
    
    if failed:
        print("\n" + "-" * 100)
        print("TESTS ÉCHOUÉS:")
        print("-" * 100)
        for r in failed:
            print(f"\n❌ [{r['category']}] {r['question']}")
            print(f"   Erreur: {r.get('error', 'Unknown')}")
    
    if successful:
        print("\n" + "-" * 100)
        print("DÉTAILS DES TESTS RÉUSSIS:")
        print("-" * 100)
        
        for i, r in enumerate(successful, 1):
            print(f"\n{i}. [{r['category']}] {r['question']}")
            print(f"   ⏱️  Temps: {r['elapsed_time']:.2f}s")
            print(f"   🎯 Alignement: {r['alignment_status']} - {r['alignment_label']}")
            print(f"   📚 Sources: {r['sources_count']}")
            
            if r['keywords_found']:
                print(f"   ✅ Mots-clés trouvés: {', '.join(r['keywords_found'])}")
            if r['keywords_missing']:
                print(f"   ⚠️  Mots-clés manquants: {', '.join(r['keywords_missing'])}")
            
            if r['sources_preview']:
                print(f"   📖 Top sources:")
                for src in r['sources_preview']:
                    print(f"      - {src['title']} (conf: {src['confidence']})")
            
            if r['has_answer']:
                print(f"   💬 Réponse: {r['answer_preview']}")
    
    # Statistiques globales
    if successful:
        avg_time = sum(r['elapsed_time'] for r in successful) / len(successful)
        avg_sources = sum(r['sources_count'] for r in successful) / len(successful)
        good_alignment = sum(1 for r in successful if r['alignment_status'] in ['strong', 'moderate'])
        
        print("\n" + "=" * 100)
        print("STATISTIQUES GLOBALES:")
        print("=" * 100)
        print(f"⏱️  Temps moyen de réponse: {avg_time:.2f}s")
        print(f"📚 Nombre moyen de sources: {avg_sources:.1f}")
        print(f"🎯 Alignements satisfaisants: {good_alignment}/{len(successful)} ({good_alignment*100/len(successful):.0f}%)")
        print(f"✅ Taux de réussite: {len(successful)*100/len(results):.0f}%")

def main():
    print("=" * 100)
    print("SÉRIE DE TESTS RAG - ÉVALUATION DES PERFORMANCES")
    print("Stemmer français + Poids rééquilibrés (BM25: 1.0, Cosine: 0.6)")
    print("=" * 100)
    print(f"\n📋 {len(TEST_QUESTIONS)} questions à tester...\n")
    
    results = []
    for i, test_case in enumerate(TEST_QUESTIONS, 1):
        print(f"[{i}/{len(TEST_QUESTIONS)}] Test: {test_case['question'][:60]}...")
        result = test_question(test_case)
        results.append(result)
        time.sleep(0.5)  # Petite pause entre les tests
    
    print_results(results)
    
    print("\n" + "=" * 100)
    print("FIN DES TESTS")
    print("=" * 100)

if __name__ == "__main__":
    main()

