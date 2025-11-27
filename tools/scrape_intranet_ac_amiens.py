#!/usr/bin/env python3
"""
Script pour scraper l'intranet ac-amiens.fr
Gère l'authentification et extrait le contenu de manière structurée
"""

import os
import time
import json
import re
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup


class IntranetScraper:
    """
    Scraper pour l'intranet ac-amiens.fr
    """
    
    def __init__(
        self,
        base_url: str = "https://intranet.ac-amiens.fr/",
        output_dir: str = "intranet_ac_amiens_data",
        delay: float = 2.0,
        username: Optional[str] = None,
        password: Optional[str] = None,
        session_cookies: Optional[Dict] = None
    ):
        self.base_url = base_url.rstrip("/")
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.username = username
        self.password = password
        self.session_cookies = session_cookies or {}
        
        # Créer le dossier de sortie
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialiser la session
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        # Charger les cookies de session si fournis
        if self.session_cookies:
            self.session.cookies.update(self.session_cookies)
        
        self.visited: Set[str] = set()
        self.pages_data: List[Dict] = []
    
    def authenticate(self) -> bool:
        """
        Tente de s'authentifier sur l'intranet
        Retourne True si l'authentification réussit
        """
        if not self.username or not self.password:
            print("⚠️ Pas de credentials fournis, tentative d'accès sans authentification")
            return False
        
        try:
            # D'abord, récupérer la page de login pour voir le formulaire
            login_url = urljoin(self.base_url, "/login")  # ou "/connexion", "/auth", etc.
            resp = self.session.get(login_url, timeout=15)
            
            if resp.status_code != 200:
                print(f"⚠️ Impossible d'accéder à la page de login: {resp.status_code}")
                return False
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Chercher le formulaire de connexion
            form = soup.find("form")
            if not form:
                print("⚠️ Aucun formulaire trouvé, peut-être déjà connecté ou structure différente")
                # Vérifier si on est déjà connecté
                if "déconnexion" in resp.text.lower() or "logout" in resp.text.lower():
                    print("✅ Semble déjà connecté")
                    return True
                return False
            
            # Extraire l'action du formulaire
            action = form.get("action", "")
            if not action.startswith("http"):
                action = urljoin(self.base_url, action)
            
            # Chercher les champs de formulaire
            username_field = form.find("input", {"type": "text"}) or form.find("input", {"name": re.compile(r"user|login|email", re.I)})
            password_field = form.find("input", {"type": "password"})
            
            if not username_field or not password_field:
                print("⚠️ Impossible de trouver les champs de formulaire")
                return False
            
            username_name = username_field.get("name", "username")
            password_name = password_field.get("name", "password")
            
            # Préparer les données du formulaire
            form_data = {
                username_name: self.username,
                password_name: self.password
            }
            
            # Chercher un token CSRF ou similaire
            csrf_token = form.find("input", {"name": re.compile(r"csrf|token|_token", re.I)})
            if csrf_token:
                form_data[csrf_token.get("name")] = csrf_token.get("value", "")
            
            # Soumettre le formulaire
            print(f"🔐 Tentative d'authentification...")
            time.sleep(self.delay)
            resp = self.session.post(action, data=form_data, timeout=15, allow_redirects=True)
            
            # Vérifier si l'authentification a réussi
            if resp.status_code == 200:
                # Vérifier les indicateurs de succès
                if "erreur" in resp.text.lower() or "incorrect" in resp.text.lower():
                    print("❌ Échec de l'authentification")
                    return False
                print("✅ Authentification réussie")
                return True
            else:
                print(f"⚠️ Réponse inattendue: {resp.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de l'authentification: {e}")
            return False
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Récupère une page et retourne un BeautifulSoup
        """
        if url in self.visited:
            return None
        
        try:
            print(f"📄 Récupération: {url}")
            resp = self.session.get(url, timeout=15, allow_redirects=True)
            
            if resp.status_code == 401:
                print(f"⚠️ Accès non autorisé (401) pour {url}")
                return None
            
            if resp.status_code == 403:
                print(f"⚠️ Accès interdit (403) pour {url}")
                return None
            
            if resp.status_code != 200:
                print(f"⚠️ Erreur HTTP {resp.status_code} pour {url}")
                return None
            
            # Vérifier si on est redirigé vers une page de login
            if "connexion" in resp.url.lower() or "login" in resp.url.lower():
                print(f"⚠️ Redirection vers la page de login pour {url}")
                return None
            
            self.visited.add(url)
            time.sleep(self.delay)
            
            return BeautifulSoup(resp.text, "html.parser")
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de {url}: {e}")
            return None
    
    def extract_content(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Extrait le contenu structuré d'une page
        """
        # Extraire le titre
        title = soup.find("title")
        title_text = title.get_text(strip=True) if title else ""
        
        # Extraire les H1, H2, H3
        headings = {
            "h1": [h.get_text(strip=True) for h in soup.find_all("h1")],
            "h2": [h.get_text(strip=True) for h in soup.find_all("h2")],
            "h3": [h.get_text(strip=True) for h in soup.find_all("h3")]
        }
        
        # Extraire le texte principal (sans scripts, styles, etc.)
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        main_content = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile(r"content|main|article", re.I))
        if main_content:
            text_content = main_content.get_text(separator="\n", strip=True)
        else:
            text_content = soup.get_text(separator="\n", strip=True)
        
        # Extraire les liens
        links = []
        for a in soup.find_all("a", href=True):
            href = a.get("href")
            if href:
                full_url = urljoin(url, href)
                links.append({
                    "text": a.get_text(strip=True),
                    "url": full_url,
                    "is_internal": urlparse(full_url).netloc == urlparse(self.base_url).netloc
                })
        
        # Extraire les images
        images = []
        for img in soup.find_all("img", src=True):
            src = img.get("src")
            if src:
                full_url = urljoin(url, src)
                images.append({
                    "alt": img.get("alt", ""),
                    "url": full_url
                })
        
        # Extraire les tableaux
        tables = []
        for table in soup.find_all("table"):
            rows = []
            for tr in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append(rows)
        
        return {
            "url": url,
            "title": title_text,
            "headings": headings,
            "text_content": text_content,
            "links": links,
            "images": images,
            "tables": tables,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def discover_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """
        Découvre les liens internes sur une page
        """
        links = []
        base_netloc = urlparse(self.base_url).netloc
        
        for a in soup.find_all("a", href=True):
            href = a.get("href")
            if not href:
                continue
            
            full_url = urljoin(current_url, href)
            parsed = urlparse(full_url)
            
            # Ne garder que les liens internes
            if parsed.netloc == base_netloc:
                # Nettoyer l'URL (enlever les fragments)
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.query:
                    clean_url += f"?{parsed.query}"
                
                if clean_url not in self.visited and clean_url not in links:
                    links.append(clean_url)
        
        return links
    
    def scrape(self, start_url: Optional[str] = None, max_pages: int = 100, depth: int = 3):
        """
        Scrape l'intranet en commençant par start_url
        """
        if start_url is None:
            start_url = self.base_url
        
        # Tenter l'authentification si nécessaire
        if self.username and self.password:
            if not self.authenticate():
                print("⚠️ Échec de l'authentification, continuation quand même...")
        
        # Queue de pages à visiter
        to_visit = [(start_url, 0)]  # (url, depth)
        
        while to_visit and len(self.pages_data) < max_pages:
            url, current_depth = to_visit.pop(0)
            
            if current_depth > depth:
                continue
            
            soup = self.fetch_page(url)
            if not soup:
                continue
            
            # Extraire le contenu
            page_data = self.extract_content(soup, url)
            self.pages_data.append(page_data)
            
            # Sauvegarder la page individuellement
            self._save_page(page_data)
            
            # Découvrir de nouveaux liens
            if current_depth < depth:
                new_links = self.discover_links(soup, url)
                for link in new_links:
                    if link not in [u for u, _ in to_visit]:
                        to_visit.append((link, current_depth + 1))
            
            print(f"✅ Page {len(self.pages_data)}/{max_pages} traitée: {url}")
        
        # Sauvegarder le résumé
        self._save_summary()
        print(f"\n✅ Scraping terminé: {len(self.pages_data)} pages extraites")
    
    def _save_page(self, page_data: Dict):
        """Sauvegarde une page individuelle"""
        # Créer un nom de fichier sûr
        url_path = urlparse(page_data["url"]).path.strip("/")
        if not url_path:
            url_path = "index"
        
        safe_name = re.sub(r'[^\w\-_/]', '_', url_path)
        if len(safe_name) > 200:
            safe_name = safe_name[:200]
        
        file_path = self.output_dir / f"{safe_name}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(page_data, f, ensure_ascii=False, indent=2)
        
        # Sauvegarder aussi le texte brut
        text_path = self.output_dir / f"{safe_name}.txt"
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(page_data["text_content"])
    
    def _save_summary(self):
        """Sauvegarde un résumé de toutes les pages"""
        summary = {
            "total_pages": len(self.pages_data),
            "base_url": self.base_url,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "pages": [
                {
                    "url": p["url"],
                    "title": p["title"],
                    "headings_count": {
                        "h1": len(p["headings"]["h1"]),
                        "h2": len(p["headings"]["h2"]),
                        "h3": len(p["headings"]["h3"])
                    },
                    "links_count": len(p["links"]),
                    "images_count": len(p["images"]),
                    "tables_count": len(p["tables"])
                }
                for p in self.pages_data
            ]
        }
        
        summary_path = self.output_dir / "summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)


def main():
    """
    Fonction principale
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Scraper pour l'intranet ac-amiens.fr")
    parser.add_argument("--url", default="https://intranet.ac-amiens.fr/", help="URL de départ")
    parser.add_argument("--output", default="intranet_ac_amiens_data", help="Dossier de sortie")
    parser.add_argument("--max-pages", type=int, default=100, help="Nombre maximum de pages à scraper")
    parser.add_argument("--depth", type=int, default=3, help="Profondeur de crawling")
    parser.add_argument("--delay", type=float, default=2.0, help="Délai entre les requêtes (secondes)")
    parser.add_argument("--username", help="Nom d'utilisateur pour l'authentification")
    parser.add_argument("--password", help="Mot de passe pour l'authentification")
    parser.add_argument("--cookies", help="Fichier JSON contenant les cookies de session")
    
    args = parser.parse_args()
    
    # Charger les cookies si fournis
    cookies = {}
    if args.cookies:
        with open(args.cookies, "r") as f:
            cookies = json.load(f)
    
    # Créer le scraper
    scraper = IntranetScraper(
        base_url=args.url,
        output_dir=args.output,
        delay=args.delay,
        username=args.username,
        password=args.password,
        session_cookies=cookies
    )
    
    # Lancer le scraping
    scraper.scrape(start_url=args.url, max_pages=args.max_pages, depth=args.depth)


if __name__ == "__main__":
    main()


