# audit_dynamiques.py
import requests
from bs4 import BeautifulSoup
import json

urls = [
    "https://www.amiens.fr/Vivre-a-Amiens/Enfance",
    "https://www.amiens.fr/Vivre-a-Amiens/Enfance/Faire-garder-son-enfant",
    "https://www.amiens.fr/Vivre-a-Amiens/Enfance/Centres-de-loisirs",
    "https://www.amiens.fr/Vivre-a-Amiens/Enfance/a-l-ecole",
    "https://www.amiens.fr/Vivre-a-Amiens/Enfance/a-table",
]

def check_dynamic(url):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        scripts = [s.get("src") for s in soup.find_all("script") if s.get("src")]
        onclicks = [tag.get("onclick") for tag in soup.find_all() if tag.get("onclick")]
        data_attrs = [a for a in soup.find_all(attrs={"data-toggle": True})]

        return {
            "url": url,
            "scripts_js": len(scripts),
            "onclicks": len(onclicks),
            "data_attrs": len(data_attrs),
            "suspect_phrases": any(
                phrase in soup.get_text().lower()
                for phrase in ["voir plus", "lire la suite", "en savoir plus"]
            ),
        }
    except Exception as e:
        return {"url": url, "error": str(e)}

results = [check_dynamic(u) for u in urls]

print(json.dumps(results, indent=2, ensure_ascii=False))
