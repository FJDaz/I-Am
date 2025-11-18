#!/usr/bin/env python3
"""
Script de simulation pour tester l'hypothèse du crash serveur lié à l'historique.
Simule plusieurs requêtes successives avec historique qui s'accumule.
"""

import requests
import json
import time
import sys
from typing import List, Dict, Any

SERVER_URL = "http://localhost:8711/rag-assistant"

def count_tokens_approx(text: str) -> int:
    """Estimation approximative du nombre de tokens (1 token ≈ 4 caractères)"""
    return len(text) // 4

def estimate_prompt_size(conversation_history: List[Dict], question: str, rag_segments: int = 0) -> int:
    """
    Estime la taille du prompt final qui sera envoyé à Claude.
    Prend en compte:
    - L'historique de conversation (limité à 12 tours dans le code)
    - La question actuelle
    - Les segments RAG
    - Le prompt système
    - Les données structurées potentielles
    """
    # Prompt système (~500 tokens)
    system_tokens = 500
    
    # Historique limité à 12 tours (conversation[-12:])
    limited_history = conversation_history[-12:] if len(conversation_history) > 12 else conversation_history
    history_tokens = sum(count_tokens_approx(json.dumps(turn, ensure_ascii=False)) 
                        for turn in limited_history)
    
    # Question actuelle
    question_tokens = count_tokens_approx(question)
    
    # Segments RAG (estimation: ~200 tokens par segment)
    rag_tokens = rag_segments * 200
    
    # Données structurées potentielles (estimation: ~300 tokens)
    structured_tokens = 300
    
    # Total estimé
    total = system_tokens + history_tokens + question_tokens + rag_tokens + structured_tokens
    
    return total

def simulate_conversation(num_requests: int = 10) -> None:
    """
    Simule une conversation avec historique qui s'accumule.
    """
    print(f"🧪 Simulation de {num_requests} requêtes avec historique accumulé\n")
    print("=" * 80)
    
    conversation_history: List[Dict[str, str]] = []
    questions = [
        "Où se trouve l'Espace Dewailly ?",
        "Quels sont les tarifs de la cantine ?",
        "Comment s'inscrire au périscolaire ?",
        "Où sont les crèches à Amiens ?",
        "Quel est mon quotient familial ?",
        "Combien de jours par semaine pour le centre de loisirs ?",
        "Quels sont les horaires du périscolaire ?",
        "Où se trouve l'école élémentaire Victoria ?",
        "Comment calculer le tarif de la cantine ?",
        "Quand sont les inscriptions pour la cantine ?",
    ]
    
    results = []
    
    for i in range(min(num_requests, len(questions))):
        question = questions[i]
        print(f"\n📝 Requête #{i+1}/{num_requests}")
        print(f"   Question: {question}")
        
        # Préparer le payload avec historique
        payload = {
            "question": question,
            "rag_results": [],
            "conversation": conversation_history.copy(),
            "normalized_question": question.lower().strip(),
        }
        
        # Estimer la taille du prompt
        history_size = len(conversation_history)
        history_tokens = sum(count_tokens_approx(json.dumps(turn, ensure_ascii=False)) 
                            for turn in conversation_history)
        
        # Historique limité dans le code (conversation[-12:])
        limited_history_size = min(12, history_size)
        limited_history_tokens = sum(count_tokens_approx(json.dumps(turn, ensure_ascii=False)) 
                                    for turn in conversation_history[-12:])
        
        # Estimation taille prompt final envoyé à Claude
        estimated_prompt_tokens = estimate_prompt_size(conversation_history, question, rag_segments=3)
        
        print(f"   Historique total: {history_size} tours, ~{history_tokens} tokens")
        print(f"   Historique limité (utilisé): {limited_history_size} tours, ~{limited_history_tokens} tokens")
        print(f"   Estimation prompt final: ~{estimated_prompt_tokens} tokens")
        
        try:
            start_time = time.time()
            response = requests.post(
                SERVER_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer_text", "") or data.get("answer_html", "")
                answer_tokens = count_tokens_approx(answer)
                
                # Ajouter à l'historique
                conversation_history.append({
                    "role": "user",
                    "content": question
                })
                conversation_history.append({
                    "role": "assistant",
                    "content": answer[:500]  # Limiter pour éviter explosion
                })
                
                print(f"   ✅ Succès ({elapsed:.2f}s)")
                print(f"   Réponse: ~{answer_tokens} tokens")
                print(f"   Nouvelle taille historique: {len(conversation_history)} tours")
                
                results.append({
                    "request_num": i + 1,
                    "status": "success",
                    "elapsed": elapsed,
                    "history_size": history_size,
                    "history_tokens": history_tokens,
                    "limited_history_size": limited_history_size,
                    "limited_history_tokens": limited_history_tokens,
                    "estimated_prompt_tokens": estimated_prompt_tokens,
                    "answer_tokens": answer_tokens,
                })
                
            else:
                print(f"   ❌ Erreur HTTP {response.status_code}")
                print(f"   Réponse: {response.text[:200]}")
                
                results.append({
                    "request_num": i + 1,
                    "status": f"error_{response.status_code}",
                    "elapsed": elapsed,
                    "history_size": history_size,
                    "history_tokens": history_tokens,
                    "limited_history_size": limited_history_size,
                    "limited_history_tokens": limited_history_tokens,
                    "estimated_prompt_tokens": estimated_prompt_tokens,
                    "error": response.text[:200],
                })
                
                # Arrêter si erreur 500 (crash serveur)
                if response.status_code == 500:
                    print(f"\n🔴 CRASH DÉTECTÉ à la requête #{i+1}")
                    print(f"   Seuil critique: {history_size} tours dans l'historique")
                    print(f"   Tokens historiques: ~{history_tokens}")
                    break
                    
        except requests.exceptions.Timeout:
            print(f"   ⏱️ Timeout (>60s)")
            results.append({
                "request_num": i + 1,
                "status": "timeout",
                "history_size": history_size,
                "history_tokens": history_tokens,
                "limited_history_size": limited_history_size,
                "limited_history_tokens": limited_history_tokens,
                "estimated_prompt_tokens": estimated_prompt_tokens,
            })
            break
            
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Erreur de connexion (serveur crashé?)")
            results.append({
                "request_num": i + 1,
                "status": "connection_error",
                "history_size": history_size,
                "history_tokens": history_tokens,
                "limited_history_size": limited_history_size,
                "limited_history_tokens": limited_history_tokens,
                "estimated_prompt_tokens": estimated_prompt_tokens,
            })
            break
            
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append({
                "request_num": i + 1,
                "status": "exception",
                "error": str(e),
                "history_size": history_size,
                "history_tokens": history_tokens,
                "limited_history_size": limited_history_size,
                "limited_history_tokens": limited_history_tokens,
                "estimated_prompt_tokens": estimated_prompt_tokens,
            })
            break
        
        # Petite pause entre requêtes
        time.sleep(0.5)
    
    # Résumé
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DE LA SIMULATION\n")
    
    successful = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") != "success"]
    
    print(f"✅ Requêtes réussies: {len(successful)}/{len(results)}")
    print(f"❌ Requêtes échouées: {len(failed)}/{len(results)}")
    
    if successful:
        print(f"\n📈 Évolution de l'historique:")
        for r in successful:
            print(f"   Requête #{r['request_num']}: {r['history_size']} tours total "
                  f"({r.get('limited_history_size', 'N/A')} utilisés), "
                  f"~{r.get('estimated_prompt_tokens', 0)} tokens prompt, {r['elapsed']:.2f}s")
    
    if failed:
        print(f"\n🔴 Échecs:")
        for r in failed:
            print(f"   Requête #{r['request_num']}: {r['status']}")
            if r.get('history_size') is not None:
                print(f"      Historique au moment de l'échec: {r['history_size']} tours, "
                      f"~{r.get('history_tokens', 0)} tokens")
    
    # Identifier le seuil critique
    if failed:
        last_success = successful[-1] if successful else None
        first_failure = failed[0]
        
        if last_success:
            print(f"\n🎯 SEUIL CRITIQUE IDENTIFIÉ:")
            print(f"   Dernière requête réussie: #{last_success['request_num']}")
            print(f"   Historique: {last_success['history_size']} tours, "
                  f"~{last_success['history_tokens']} tokens")
            print(f"   Première requête échouée: #{first_failure['request_num']}")
            print(f"   Historique: {first_failure.get('history_size', 'N/A')} tours, "
                  f"~{first_failure.get('history_tokens', 0)} tokens")
            print(f"\n   💡 Le serveur semble crash au-delà de:")
            print(f"      - {last_success['history_size']} tours d'historique")
            print(f"      - ~{last_success['history_tokens']} tokens d'historique")
    
    # Sauvegarder les résultats
    output_file = "tests/test_historique_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Résultats sauvegardés dans: {output_file}")


if __name__ == "__main__":
    num_requests = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    print("🚀 Test de simulation d'historique conversation")
    print(f"   Serveur: {SERVER_URL}")
    print(f"   Nombre de requêtes: {num_requests}\n")
    
    # Vérifier que le serveur est accessible
    try:
        response = requests.get("http://localhost:8711", timeout=2)
    except:
        try:
            # Tester avec une requête simple
            test_payload = {
                "question": "test",
                "rag_results": [],
                "conversation": [],
            }
            response = requests.post(SERVER_URL, json=test_payload, timeout=5)
            if response.status_code != 200:
                print("⚠️  Le serveur répond mais avec une erreur. Continuons quand même...\n")
        except Exception as e:
            print(f"❌ Erreur: Le serveur n'est pas accessible: {e}")
            print("   Assurez-vous que le serveur tourne sur http://localhost:8711")
            sys.exit(1)
    
    simulate_conversation(num_requests)

