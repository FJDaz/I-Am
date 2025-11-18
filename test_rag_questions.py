"""
Script de test pour le serveur RAG avec 5 questions diverses
"""
import requests
import json

# Configuration
SERVER_URL = "https://localhost:8711/rag-assistant"

# Questions de test - variées sur l'enfance à Amiens
QUESTIONS = [
    "Comment inscrire mon enfant à la crèche ?",
    "Combien coûte la cantine scolaire à Amiens ?",
    "Quels sont les horaires de l'accueil périscolaire ?",
    "Comment faire garder mon enfant le mercredi ?",
    "Quel est le tarif pour le centre de loisirs pendant les vacances d'été ?"
]

def test_question(question: str) -> dict:
    """Envoie une question au serveur RAG et retourne la réponse."""
    payload = {
        "question": question,
        "rag_results": [],
        "conversation": []
    }

    try:
        # Désactiver la vérification SSL pour localhost
        response = requests.post(
            SERVER_URL,
            json=payload,
            verify=False,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    print("=" * 80)
    print("TEST DU SERVEUR RAG - 5 QUESTIONS SUR L'ENFANCE À AMIENS")
    print("=" * 80)
    print()

    for i, question in enumerate(QUESTIONS, 1):
        print(f"\n{'=' * 80}")
        print(f"QUESTION {i}: {question}")
        print(f"{'=' * 80}")

        result = test_question(question)

        if "error" in result:
            print(f"\n❌ ERREUR: {result['error']}\n")
            continue

        # Afficher la réponse
        print(f"\n📝 RÉPONSE:")
        print(f"{result.get('answer_text', 'N/A')}")

        # Afficher l'alignement
        alignment = result.get('alignment', {})
        print(f"\n🎯 ALIGNEMENT:")
        print(f"   Status: {alignment.get('status', 'N/A')}")
        print(f"   Label: {alignment.get('label', 'N/A')}")
        print(f"   Summary: {alignment.get('summary', 'N/A')}")

        # Afficher les sources
        sources = result.get('sources', [])
        if sources:
            print(f"\n📚 SOURCES ({len(sources)}):")
            for source in sources[:3]:  # Max 3 sources
                print(f"   - {source.get('title', 'N/A')} (confiance: {source.get('confidence', 'N/A')})")

        # Afficher la question de suivi
        follow_up = result.get('follow_up_question')
        if follow_up:
            print(f"\n💬 QUESTION DE SUIVI:")
            print(f"   {follow_up}")

        print()

    print("\n" + "=" * 80)
    print("FIN DES TESTS")
    print("=" * 80)

if __name__ == "__main__":
    # Supprimer les warnings SSL
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    main()
