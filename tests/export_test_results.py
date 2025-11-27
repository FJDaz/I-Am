"""
Exporte les résultats des tests RAG dans un fichier Markdown lisible
"""
import requests
import json
from typing import Dict

# Configuration
SERVER_URL = "https://localhost:8711/rag-assistant"

# Supprimer les warnings SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Questions de test
TEST_QUESTIONS = [
    {
        "question": "Comment inscrire mon enfant à la crèche ?",
        "category": "Inscription crèche"
    },
    {
        "question": "Quels sont les tarifs de la cantine scolaire ?",
        "category": "Tarifs cantine"
    },
    {
        "question": "Horaires accueil périscolaire",
        "category": "Horaires périscolaire"
    },
    {
        "question": "Je veux inscrire mon enfant à une crèche",
        "category": "Variation inscription"
    },
    {
        "question": "Inscriptions aux crèches amiénoises",
        "category": "Variation pluriel"
    },
    {
        "question": "Comment faire garder mon enfant le mercredi ?",
        "category": "Garde mercredi"
    },
    {
        "question": "Tarif centre de loisirs vacances été",
        "category": "Tarifs ALSH"
    },
    {
        "question": "Quel est le prix pour les activités pendant les vacances ?",
        "category": "Synonymes"
    },
    {
        "question": "DRE dispositif réussite éducative",
        "category": "Terme technique"
    },
    {
        "question": "PAI projet accueil individualisé",
        "category": "Acronyme"
    }
]

def get_full_response(test_case: Dict) -> Dict:
    """Récupère la réponse complète du serveur."""
    question = test_case["question"]
    payload = {
        "question": question,
        "rag_results": [],
        "normalized_question": question.lower(),
        "conversation": []
    }

    try:
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

def generate_markdown(results: list) -> str:
    """Génère le contenu Markdown."""
    md = """# Résultats des Tests RAG - Amiens Enfance

## Configuration
- **Stemmer** : Français (Snowball)
- **Poids BM25** : 1.0
- **Poids Cosine Similarity** : 0.6
- **Date** : Tests automatisés

---

"""
    
    for i, (test_case, result) in enumerate(results, 1):
        if "error" in result:
            md += f"""## Test {i} : {test_case['question']}

**Catégorie** : {test_case['category']}

❌ **ERREUR** : {result['error']}

---

"""
            continue
        
        alignment = result.get('alignment', {})
        sources = result.get('sources', [])
        
        md += f"""## Test {i} : {test_case['question']}

**Catégorie** : {test_case['category']}

### Réponse

{result.get('answer_text', result.get('answer_html', 'N/A'))}

### Alignement RAG

- **Statut** : `{alignment.get('status', 'N/A')}`
- **Label** : {alignment.get('label', 'N/A')}
- **Résumé** : {alignment.get('summary', 'N/A')}

"""
        
        if sources:
            md += f"""### Sources ({len(sources)})

"""
            for j, source in enumerate(sources, 1):
                title = source.get('title', 'Sans titre')
                url = source.get('url', '')
                confidence = source.get('confidence', 'N/A')
                md += f"{j}. **{title}**"
                if url:
                    md += f" - [{url}]({url})"
                md += f" (confiance: {confidence})\n"
            md += "\n"
        
        follow_up = result.get('follow_up_question')
        if follow_up:
            md += f"""### Question de suivi suggérée

> {follow_up}

"""
        
        md += "---\n\n"
    
    # Statistiques
    successful = [r for r in results if "error" not in r[1]]
    md += f"""## Statistiques

- **Tests réussis** : {len(successful)}/{len(results)}
- **Tests échoués** : {len(results) - len(successful)}/{len(results)}

"""
    
    return md

def main():
    print("Récupération des réponses complètes...")
    results = []
    
    for i, test_case in enumerate(TEST_QUESTIONS, 1):
        print(f"[{i}/{len(TEST_QUESTIONS)}] {test_case['question'][:60]}...")
        result = get_full_response(test_case)
        results.append((test_case, result))
    
    print("\nGénération du Markdown...")
    markdown = generate_markdown(results)
    
    output_file = "test_results_rag.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"✅ Fichier généré : {output_file}")

if __name__ == "__main__":
    main()

