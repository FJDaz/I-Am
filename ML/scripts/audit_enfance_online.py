"""
Audit en ligne des pages de la rubrique Enfance.

Le script explore récursivement les pages `amiens.fr` dont l'URL
contient `/Vivre-a-Amiens/Enfance`, en respectant `robots.txt`.
Pour chaque page, il détecte quelques structures susceptibles de
cacher du contenu à un crawl basique (tables, blocs masqués, etc.).

Utilisation rapide :
    python3 audit_enfance_online.py

Options :
    --max-pages N    Limite le nombre de pages visitées (par défaut 200)
    --delay SECS     Délai entre requêtes (par défaut 1.0 seconde)
    --export PATH    Chemin d'export JSON (par défaut stdout)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.robotparser
from collections import deque
from pathlib import Path
from typing import Dict, Iterable, List, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.amiens.fr"
START_PATH = "/Vivre-a-Amiens/Enfance"
USER_AGENT = "AmiensCrawlerAudit/0.1 (+mailto:contact@example.com)"


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit en ligne de la rubrique Enfance (amiens.fr)")
    parser.add_argument("--max-pages", type=int, default=200, help="Nombre maximum de pages à visiter")
    parser.add_argument("--delay", type=float, default=1.0, help="Délai (en secondes) entre requêtes")
    parser.add_argument("--export", type=Path, default=None, help="Chemin du fichier JSON de sortie")
    return parser.parse_args(argv)


def load_robots(user_agent: str) -> urllib.robotparser.RobotFileParser:
    robots = urllib.robotparser.RobotFileParser()
    robots.set_url(urljoin(BASE_URL, "/robots.txt"))
    robots.read()
    if not robots.can_fetch(user_agent, urljoin(BASE_URL, START_PATH)):
        raise SystemExit("Accès refusé par robots.txt pour le point d'entrée.")
    return robots


def should_visit(url: str, robots: urllib.robotparser.RobotFileParser, user_agent: str) -> bool:
    parsed = urlparse(url)
    if parsed.netloc and parsed.netloc != urlparse(BASE_URL).netloc:
        return False
    if "/Vivre-a-Amiens/Enfance" not in parsed.path:
        return False
    if not robots.can_fetch(user_agent, url):
        return False
    return True


def fetch(session: requests.Session, url: str) -> requests.Response | None:
    try:
        response = session.get(url, timeout=20)
        response.raise_for_status()
        return response
    except requests.RequestException as exc:
        print(f"[WARN] Requête échouée ({url}): {exc}", file=sys.stderr)
        return None


def analyze_html(html: str) -> Dict[str, bool | int]:
    soup = BeautifulSoup(html, "html.parser")

    hidden_selectors = (
        '[style*="display:none"]',
        '[style*="visibility:hidden"]',
        ".collapse",
        ".accordion",
        ".hidden",
    )
    hidden_count = sum(len(soup.select(selector)) for selector in hidden_selectors)

    metrics: Dict[str, bool | int] = {
        "has_tables": bool(soup.find_all("table")),
        "has_scripts": bool(soup.find_all("script")),
        "has_iframes": bool(soup.find_all("iframe")),
        "has_details": bool(soup.find_all("details")),
        "has_lazy_images": bool(
            soup.find_all("img", attrs={"loading": "lazy"})
            or soup.find_all(lambda tag: tag.name == "img" and any(attr.startswith("data-") for attr in tag.attrs))
        ),
        "hidden_candidate_count": hidden_count,
        "has_data_attrs": any(
            any(attr.startswith("data-") for attr in tag.attrs)
            for tag in soup.find_all(True)
        ),
        "contains_voir_plus": "voir +" in soup.get_text(separator=" ").lower(),
    }
    return metrics


def extract_links(soup: BeautifulSoup, current_url: str) -> List[str]:
    links = []
    for tag in soup.find_all("a", href=True):
        href = urljoin(current_url, tag["href"])
        links.append(href.split("#", 1)[0])
    return links


def audit_enfance(max_pages: int, delay: float) -> List[Dict[str, object]]:
    robots = load_robots(USER_AGENT)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    queue: deque[str] = deque([urljoin(BASE_URL, START_PATH)])
    visited: Set[str] = set()
    results: List[Dict[str, object]] = []

    while queue and len(visited) < max_pages:
        url = queue.popleft()
        if url in visited or not should_visit(url, robots, USER_AGENT):
            continue

        response = fetch(session, url)
        if response is None:
            visited.add(url)
            continue

        if "application/pdf" in response.headers.get("Content-Type", "") or url.lower().endswith(".pdf"):
            results.append(
                {
                    "url": url,
                    "type": "pdf",
                    "note": "Ignoré pour l'audit HTML",
                }
            )
            visited.add(url)
            time.sleep(delay)
            continue

        html = response.text
        metrics = analyze_html(html)
        metrics.update({"url": url, "type": "html"})
        results.append(metrics)

        soup = BeautifulSoup(html, "html.parser")
        for link in extract_links(soup, url):
            if link not in visited and should_visit(link, robots, USER_AGENT):
                queue.append(link)

        visited.add(url)
        time.sleep(delay)

    return results


def main(argv: Iterable[str]) -> int:
    args = parse_args(argv)
    results = audit_enfance(args.max_pages, args.delay)

    if args.export:
        with args.export.open("w", encoding="utf-8") as fp:
            json.dump(results, fp, ensure_ascii=False, indent=2)
        print(f"✅ Audit terminé. Résultats enregistrés dans {args.export}")
    else:
        json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

