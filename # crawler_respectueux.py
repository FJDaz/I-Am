# crawler_respectueux.py
import time, requests, urllib.robotparser, os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE = "https://www.amiens.fr"
START = "https://www.amiens.fr/Vivre-a-Amiens/Enfance"  # point d'entrée choisi
USER_AGENT = "MyAmiensPOC/0.1 (+mailto:ton.email@exemple.com)"
DELAY = 1.0  # seconde entre requêtes

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})

# check robots
rp = urllib.robotparser.RobotFileParser()
rp.set_url(urljoin(BASE, "/robots.txt"))
rp.read()
if not rp.can_fetch(USER_AGENT, START):
    raise SystemExit("robots.txt interdit l'accès à cette URL pour ce user-agent. Demande l'autorisation.")

to_visit = [START]
visited = set()
output_dir = "download_amiens_enfance"
os.makedirs(output_dir, exist_ok=True)

while to_visit:
    url = to_visit.pop(0)
    if url in visited: 
        continue
    parsed = urlparse(url)
    if parsed.netloc != urlparse(BASE).netloc:
        continue  # rester dans le domaine amiens.fr
    if not rp.can_fetch(USER_AGENT, url):
        print("robots.txt refuse:", url)
        continue

    try:
        resp = session.get(url, timeout=15)
    except Exception as e:
        print("Erreur request:", e)
        time.sleep(2)
        continue

    code = resp.status_code
    if code == 429:
        print("429 rate limit, backoff")
        time.sleep(10)
        to_visit.append(url)
        continue
    if code >= 400:
        print("Erreur HTTP", code, url)
        continue

    # détection simple de protection
    if "captcha" in resp.text.lower() or "access denied" in resp.text.lower():
        print("Probable blocage / captcha sur", url)
        continue

    # si PDF (Content-Type ou url)
    ctype = resp.headers.get("Content-Type","")
    if "application/pdf" in ctype or url.lower().endswith(".pdf"):
        fname = os.path.join(output_dir, os.path.basename(parsed.path) or "file.pdf")
        with open(fname, "wb") as f:
            f.write(resp.content)
        print("PDF saved:", fname)
        visited.add(url)
        time.sleep(DELAY)
        continue

    soup = BeautifulSoup(resp.text, "html.parser")
    # sauvegarde texte simple
    txt = soup.get_text(separator="\n")
    safe_name = parsed.path.strip("/").replace("/", "_") or "index"
    with open(os.path.join(output_dir, safe_name + ".txt"), "w", encoding="utf-8") as f:
        f.write(txt)

    visited.add(url)
    # collecte liens internes pour périmètre Enfance seulement (filtre par "/Enfance")
    for a in soup.find_all("a", href=True):
        href = urljoin(BASE, a["href"])
        if href.startswith(BASE) and "/Enfance" in href and href not in visited:
            to_visit.append(href)

    time.sleep(DELAY)
print("Terminé. Pages:", len(visited))
