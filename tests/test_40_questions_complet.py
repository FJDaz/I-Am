#!/usr/bin/env python3
"""
Test complet avec 40 questions "où, quand, comment"
- Du plus général au plus spécifique
- Du langage fruste au plus élaboré
"""
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Any

# Configuration
SERVER_URL = "https://localhost:8711/rag-assistant"

# 40 questions progressives : général → spécifique, fruste → élaboré
TEST_QUESTIONS = [
    # ===== NIVEAU 1 : TRÈS GÉNÉRAL, LANGAGE FRUSTE =====
    {
        "question": "où école",
        "category": "géographique",
        "type": "où",
        "niveau": 1,
        "langage": "fruste",
        "expected_keywords": ["école"]
    },
    {
        "question": "quand inscription",
        "category": "inscription",
        "type": "quand",
        "niveau": 1,
        "langage": "fruste",
        "expected_keywords": ["inscription"]
    },
    {
        "question": "comment inscrire",
        "category": "inscription",
        "type": "comment",
        "niveau": 1,
        "langage": "fruste",
        "expected_keywords": ["inscrire", "inscription"]
    },
    {
        "question": "où cantine",
        "category": "géographique",
        "type": "où",
        "niveau": 1,
        "langage": "fruste",
        "expected_keywords": ["cantine"]
    },
    {
        "question": "quand vacances",
        "category": "calendrier",
        "type": "quand",
        "niveau": 1,
        "langage": "fruste",
        "expected_keywords": ["vacances"]
    },
    
    # ===== NIVEAU 2 : GÉNÉRAL, LANGAGE SIMPLE =====
    {
        "question": "Où sont les écoles ?",
        "category": "géographique",
        "type": "où",
        "niveau": 2,
        "langage": "simple",
        "expected_keywords": ["école", "liste"]
    },
    {
        "question": "Quand s'inscrire à la crèche ?",
        "category": "inscription",
        "type": "quand",
        "niveau": 2,
        "langage": "simple",
        "expected_keywords": ["crèche", "inscription"]
    },
    {
        "question": "Comment faire pour inscrire mon enfant ?",
        "category": "inscription",
        "type": "comment",
        "niveau": 2,
        "langage": "simple",
        "expected_keywords": ["inscrire", "enfant"]
    },
    {
        "question": "Où trouver les tarifs ?",
        "category": "tarifs",
        "type": "où",
        "niveau": 2,
        "langage": "simple",
        "expected_keywords": ["tarif"]
    },
    {
        "question": "Quand sont les activités du mercredi ?",
        "category": "horaires",
        "type": "quand",
        "niveau": 2,
        "langage": "simple",
        "expected_keywords": ["mercredi", "activité"]
    },
    
    # ===== NIVEAU 3 : MOYEN, LANGAGE COURANT =====
    {
        "question": "Où puis-je trouver la liste des écoles d'Amiens ?",
        "category": "géographique",
        "type": "où",
        "niveau": 3,
        "langage": "courant",
        "expected_keywords": ["école", "liste", "Amiens"]
    },
    {
        "question": "Quand ont lieu les inscriptions pour la cantine scolaire ?",
        "category": "inscription",
        "type": "quand",
        "niveau": 3,
        "langage": "courant",
        "expected_keywords": ["inscription", "cantine", "scolaire"]
    },
    {
        "question": "Comment procéder pour inscrire mon enfant au périscolaire ?",
        "category": "inscription",
        "type": "comment",
        "niveau": 3,
        "langage": "courant",
        "expected_keywords": ["inscrire", "périscolaire"]
    },
    {
        "question": "Où se trouve l'Espace Dewailly ?",
        "category": "géographique",
        "type": "où",
        "niveau": 3,
        "langage": "courant",
        "expected_keywords": ["Espace Dewailly", "adresse"]
    },
    {
        "question": "Quand commencent les vacances d'été pour les enfants ?",
        "category": "calendrier",
        "type": "quand",
        "niveau": 3,
        "langage": "courant",
        "expected_keywords": ["vacances", "été"]
    },
    {
        "question": "Comment calculer le tarif de la cantine selon mon quotient familial ?",
        "category": "tarifs",
        "type": "comment",
        "niveau": 3,
        "langage": "courant",
        "expected_keywords": ["tarif", "cantine", "quotient"]
    },
    
    # ===== NIVEAU 4 : SPÉCIFIQUE, LANGAGE ÉLABORÉ =====
    {
        "question": "Où puis-je consulter la carte interactive des établissements scolaires de la métropole amiénoise ?",
        "category": "géographique",
        "type": "où",
        "niveau": 4,
        "langage": "élaboré",
        "expected_keywords": ["carte", "établissement", "scolaire"]
    },
    {
        "question": "Quand sont les périodes d'inscription pour les activités périscolaires du mercredi après-midi ?",
        "category": "inscription",
        "type": "quand",
        "niveau": 4,
        "langage": "élaboré",
        "expected_keywords": ["inscription", "périscolaire", "mercredi"]
    },
    {
        "question": "Comment puis-je obtenir les informations nécessaires pour inscrire mon enfant de 4 ans à l'accueil périscolaire du matin et du soir ?",
        "category": "inscription",
        "type": "comment",
        "niveau": 4,
        "langage": "élaboré",
        "expected_keywords": ["inscrire", "périscolaire", "accueil"]
    },
    {
        "question": "Où se situe précisément l'école élémentaire Victoria dans le secteur nord-est d'Amiens ?",
        "category": "géographique",
        "type": "où",
        "niveau": 4,
        "langage": "élaboré",
        "expected_keywords": ["école", "Victoria", "adresse", "secteur"]
    },
    {
        "question": "Quand débute l'accueil du mercredi avec restauration scolaire pour les enfants de maternelle et élémentaire ?",
        "category": "horaires",
        "type": "quand",
        "niveau": 4,
        "langage": "élaboré",
        "expected_keywords": ["mercredi", "accueil", "restauration"]
    },
    
    # ===== QUESTIONS SPÉCIFIQUES PAR THÈME =====
    # RPE / Crèche
    {
        "question": "Où est le RPE Babillages ?",
        "category": "RPE",
        "type": "où",
        "niveau": 2,
        "langage": "simple",
        "expected_keywords": ["RPE", "Babillages"]
    },
    {
        "question": "Quand puis-je contacter le relais petite enfance pour une inscription en crèche ?",
        "category": "RPE",
        "type": "quand",
        "niveau": 3,
        "langage": "courant",
        "expected_keywords": ["RPE", "relais", "crèche"]
    },
    {
        "question": "Comment fonctionne le système d'inscription dans les relais petite enfance d'Amiens ?",
        "category": "RPE",
        "type": "comment",
        "niveau": 4,
        "langage": "élaboré",
        "expected_keywords": ["RPE", "relais", "inscription"]
    },
    
    # Tarifs
    {
        "question": "Où voir les prix de la cantine ?",
        "category": "tarifs",
        "type": "où",
        "niveau": 1,
        "langage": "fruste",
        "expected_keywords": ["prix", "cantine"]
    },
    {
        "question": "Quand les tarifs sont-ils mis à jour chaque année ?",
        "category": "tarifs",
        "type": "quand",
        "niveau": 3,
        "langage": "courant",
        "expected_keywords": ["tarif", "mise à jour"]
    },
    {
        "question": "Comment sont calculés les tarifs de l'accueil périscolaire en fonction du quotient familial individualisé ?",
        "category": "tarifs",
        "type": "comment",
        "niveau": 4,
        "langage": "élaboré",
        "expected_keywords": ["tarif", "périscolaire", "quotient"]
    },
    
    # ALSH / Centre de loisirs
    {
        "question": "où centre loisirs",
        "category": "ALSH",
        "type": "où",
        "niveau": 1,
        "langage": "fruste",
        "expected_keywords": ["centre", "loisirs"]
    },
    {
        "question": "Quand sont les activités du centre de loisirs pendant les vacances ?",
        "category": "ALSH",
        "type": "quand",
        "niveau": 2,
        "langage": "simple",
        "expected_keywords": ["centre", "loisirs", "vacances"]
    },
    {
        "question": "Comment s'inscrire aux accueils de loisirs sans hébergement pour les vacances d'été ?",
        "category": "ALSH",
        "type": "comment",
        "niveau": 4,
        "langage": "élaboré",
        "expected_keywords": ["ALSH", "loisirs", "vacances", "été"]
    },
    
    # Écoles spécifiques
    {
        "question": "Où est l'école maternelle Réaumur ?",
        "category": "géographique",
        "type": "où",
        "niveau": 2,
        "langage": "simple",
        "expected_keywords": ["école", "Réaumur", "adresse"]
    },
    {
        "question": "Quand sont les horaires d'ouverture de l'école élémentaire Condorcet ?",
        "category": "horaires",
        "type": "quand",
        "niveau": 3,
        "langage": "courant",
        "expected_keywords": ["école", "Condorcet", "horaires"]
    },
    {
        "question": "Comment contacter directement l'école primaire Saint-Maurice pour une demande d'inscription ?",
        "category": "contact",
        "type": "comment",
        "niveau": 4,
        "langage": "élaboré",
        "expected_keywords": ["école", "Saint-Maurice", "contact"]
    },
    
    # Questions avec fautes / SMS
    {
        "question": "ou trouver ecole amiens",
        "category": "géographique",
        "type": "où",
        "niveau": 1,
        "langage": "SMS",
        "expected_keywords": ["école", "Amiens"]
    },
    {
        "question": "kan inscription cantine",
        "category": "inscription",
        "type": "quand",
        "niveau": 1,
        "langage": "SMS",
        "expected_keywords": ["inscription", "cantine"]
    },
    {
        "question": "koment inscrir enfant creche",
        "category": "inscription",
        "type": "comment",
        "niveau": 1,
        "langage": "SMS",
        "expected_keywords": ["inscrire", "enfant", "crèche"]
    },
    
    # Questions très spécifiques
    {
        "question": "Où puis-je trouver les coordonnées complètes incluant adresse postale, numéro de téléphone et adresse électronique de l'école maternelle publique située dans le secteur Est d'Amiens ?",
        "category": "contact",
        "type": "où",
        "niveau": 4,
        "langage": "très élaboré",
        "expected_keywords": ["école", "contact", "téléphone", "email"]
    },
    {
        "question": "Quand exactement se déroulent les périodes d'inscription pour les différents services municipaux liés à l'enfance, à savoir la restauration scolaire, l'accueil périscolaire et les centres de loisirs ?",
        "category": "inscription",
        "type": "quand",
        "niveau": 4,
        "langage": "très élaboré",
        "expected_keywords": ["inscription", "restauration", "périscolaire", "loisirs"]
    },
    {
        "question": "Comment puis-je procéder pour obtenir une estimation précise du coût mensuel de la restauration scolaire et de l'accueil périscolaire en fonction de mon quotient familial individualisé, et quels sont les documents nécessaires pour cette démarche ?",
        "category": "tarifs",
        "type": "comment",
        "niveau": 4,
        "langage": "très élaboré",
        "expected_keywords": ["tarif", "restauration", "périscolaire", "quotient"]
    },
    
    # Questions avec contexte
    {
        "question": "J'habite dans le secteur Ouest, où dois-je m'adresser pour inscrire mon enfant ?",
        "category": "inscription",
        "type": "où",
        "niveau": 3,
        "langage": "courant",
        "expected_keywords": ["secteur", "Ouest", "inscrire"]
    },
    {
        "question": "Mon enfant entre en maternelle en septembre, quand dois-je faire les démarches ?",
        "category": "inscription",
        "type": "quand",
        "niveau": 3,
        "langage": "courant",
        "expected_keywords": ["maternelle", "septembre", "démarches"]
    },
    {
        "question": "J'ai un quotient familial de 450€, comment calculer le tarif de la cantine ?",
        "category": "tarifs",
        "type": "comment",
        "niveau": 3,
        "langage": "courant",
        "expected_keywords": ["quotient", "tarif", "cantine"]
    },
    
    # Dernières questions variées
    {
        "question": "Où trouver les menus de la cantine ?",
        "category": "menus",
        "type": "où",
        "niveau": 2,
        "langage": "simple",
        "expected_keywords": ["menu", "cantine"]
    },
    {
        "question": "Quand sont publiés les menus du mois ?",
        "category": "menus",
        "type": "quand",
        "niveau": 2,
        "langage": "simple",
        "expected_keywords": ["menu", "mois"]
    },
    {
        "question": "Comment accéder aux menus de la restauration scolaire en ligne ?",
        "category": "menus",
        "type": "comment",
        "niveau": 3,
        "langage": "courant",
        "expected_keywords": ["menu", "restauration", "scolaire"]
    },
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
            "niveau": test_case["niveau"],
            "langage": test_case["langage"],
            "elapsed_time": elapsed,
            "alignment_status": alignment.get('status', 'unknown'),
            "alignment_label": alignment.get('label', 'N/A'),
            "sources_count": len(sources),
            "keywords_found": keywords_found,
            "keywords_missing": keywords_missing,
            "has_address": has_address if test_case.get("type") == "où" else None,
            "has_answer": len(answer_text) > 50,
            "answer_length": len(answer_text),
            "answer_preview": answer_text[:200] + "..." if len(answer_text) > 200 else answer_text,
            "follow_up": follow_up[:100] if follow_up else None,
        }
    except Exception as e:
        return {
            "success": False,
            "question": question,
            "category": test_case["category"],
            "type": test_case["type"],
            "niveau": test_case["niveau"],
            "langage": test_case["langage"],
            "error": str(e)
        }

def print_results(results: List[Dict]):
    """Affiche les résultats de manière formatée."""
    print("\n" + "=" * 100)
    print("RÉSULTATS DÉTAILLÉS - TEST 40 QUESTIONS")
    print("=" * 100)
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    # Statistiques globales
    print(f"\n📊 STATISTIQUES GLOBALES")
    print(f"   Total: {len(results)} questions")
    print(f"   ✅ Réussies: {len(successful)}")
    print(f"   ❌ Échouées: {len(failed)}")
    print(f"   Taux de réussite: {len(successful)*100/len(results):.1f}%")
    
    # Par type
    où_tests = [r for r in successful if r.get("type") == "où"]
    quand_tests = [r for r in successful if r.get("type") == "quand"]
    comment_tests = [r for r in successful if r.get("type") == "comment"]
    
    print(f"\n📊 PAR TYPE")
    print(f"   'Où' : {len(où_tests)}/{len([r for r in results if r.get('type') == 'où'])} réussies")
    print(f"   'Quand' : {len(quand_tests)}/{len([r for r in results if r.get('type') == 'quand'])} réussies")
    print(f"   'Comment' : {len(comment_tests)}/{len([r for r in results if r.get('type') == 'comment'])} réussies")
    
    # Par niveau
    for niveau in [1, 2, 3, 4]:
        niveau_tests = [r for r in successful if r.get("niveau") == niveau]
        total_niveau = len([r for r in results if r.get("niveau") == niveau])
        if total_niveau > 0:
            print(f"   Niveau {niveau} : {len(niveau_tests)}/{total_niveau} réussies ({len(niveau_tests)*100/total_niveau:.1f}%)")
    
    # Par langage
    langages = ["fruste", "SMS", "simple", "courant", "élaboré", "très élaboré"]
    print(f"\n📊 PAR NIVEAU DE LANGAGE")
    for langage in langages:
        langage_tests = [r for r in successful if r.get("langage") == langage]
        total_langage = len([r for r in results if r.get("langage") == langage])
        if total_langage > 0:
            print(f"   {langage.capitalize()} : {len(langage_tests)}/{total_langage} réussies ({len(langage_tests)*100/total_langage:.1f}%)")
    
    # Adresses trouvées
    où_with_address = [r for r in où_tests if r.get("has_address")]
    print(f"\n📍 ADRESSES TROUVÉES (questions 'où')")
    print(f"   {len(où_with_address)}/{len(où_tests)} questions avec adresse trouvée ({len(où_with_address)*100/max(len(où_tests),1):.1f}%)")
    
    # Alignements
    aligned = [r for r in successful if r.get("alignment_status") in ["aligned", "partial"]]
    print(f"\n🎯 ALIGNEMENTS")
    print(f"   Alignés/Partiels: {len(aligned)}/{len(successful)} ({len(aligned)*100/max(len(successful),1):.1f}%)")
    
    # Mots-clés
    all_keywords_found = sum(len(r.get("keywords_found", [])) for r in successful)
    all_keywords_total = sum(len(r.get("expected_keywords", [])) for r in results)
    print(f"\n🔑 MOTS-CLÉS")
    print(f"   Trouvés: {all_keywords_found}/{all_keywords_total} ({all_keywords_found*100/max(all_keywords_total,1):.1f}%)")
    
    # Temps moyen
    avg_time = sum(r.get("elapsed_time", 0) for r in successful) / max(len(successful), 1)
    print(f"\n⏱️  TEMPS DE RÉPONSE")
    print(f"   Moyen: {avg_time:.2f}s")
    print(f"   Min: {min((r.get('elapsed_time', 0) for r in successful), default=0):.2f}s")
    print(f"   Max: {max((r.get('elapsed_time', 0) for r in successful), default=0):.2f}s")
    
    print(f"\n📋 DÉTAILS PAR QUESTION")
    print("-" * 100)
    
    for i, result in enumerate(results, 1):
        status = "✅" if result.get("success") else "❌"
        q_type = result.get("type", "N/A").upper()
        niveau = result.get("niveau", "?")
        langage = result.get("langage", "N/A")
        print(f"\n[{i:2d}] {status} [{q_type}] N{niveau} {langage.upper():12s} | {result.get('question', 'N/A')[:60]}")
        
        if result.get("success"):
            print(f"     ⏱️  {result.get('elapsed_time', 0):.2f}s | 🎯 {result.get('alignment_status', 'N/A'):20s} | 📚 {result.get('sources_count', 0)} sources")
            keywords = result.get("keywords_found", [])
            missing = result.get("keywords_missing", [])
            if keywords:
                print(f"     ✅ Mots-clés: {', '.join(keywords[:3])}")
            if missing:
                print(f"     ⚠️  Manquants: {', '.join(missing[:2])}")
            if result.get("has_address") is not None:
                addr_status = "✅" if result.get("has_address") else "❌"
                print(f"     {addr_status} Adresse")
        else:
            print(f"     ❌ Erreur: {result.get('error', 'Unknown')[:60]}")

def main():
    print("=" * 100)
    print("TEST COMPLET - 40 QUESTIONS 'OÙ, QUAND, COMMENT'")
    print("Du général au spécifique | Du fruste à l'élaboré")
    print("=" * 100)
    print(f"\n📋 {len(TEST_QUESTIONS)} questions à tester...\n")
    
    results = []
    for i, test_case in enumerate(TEST_QUESTIONS, 1):
        niveau = test_case.get('niveau', '?')
        langage = test_case.get('langage', 'N/A')
        print(f"[{i:2d}/{len(TEST_QUESTIONS)}] N{niveau} {langage:12s} | {test_case['question'][:60]}...", end=" ", flush=True)
        result = test_question(test_case)
        results.append(result)
        
        if result.get("success"):
            status = result.get("alignment_status", "unknown")
            addr_info = ""
            if result.get("has_address") is not None:
                addr_info = f" | Adr:{'✅' if result.get('has_address') else '❌'}"
            print(f"✅ [{status[:15]}]{addr_info}")
        else:
            print(f"❌ {result.get('error', 'Unknown')[:30]}")
        
        time.sleep(0.3)  # Petite pause entre les tests
    
    print_results(results)
    
    # Sauvegarder les résultats
    output_path = Path(__file__).parent / "test_results_40_questions.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Résultats sauvegardés: {output_path}")
    
    # Générer un résumé CSV
    csv_path = Path(__file__).parent / "test_results_40_questions.csv"
    import csv
    with csv_path.open("w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["#", "Question", "Type", "Niveau", "Langage", "Status", "Alignement", "Sources", "Temps", "Adresse", "Mots-clés trouvés"])
        for i, r in enumerate(results, 1):
            writer.writerow([
                i,
                r.get("question", "")[:80],
                r.get("type", ""),
                r.get("niveau", ""),
                r.get("langage", ""),
                "✅" if r.get("success") else "❌",
                r.get("alignment_status", ""),
                r.get("sources_count", 0),
                f"{r.get('elapsed_time', 0):.2f}s",
                "✅" if r.get("has_address") else ("❌" if r.get("has_address") is False else "N/A"),
                ", ".join(r.get("keywords_found", []))
            ])
    print(f"💾 CSV sauvegardé: {csv_path}")
    
    print("\n" + "=" * 100)
    print("FIN DES TESTS")
    print("=" * 100)

if __name__ == "__main__":
    main()

