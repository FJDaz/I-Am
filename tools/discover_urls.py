#!/usr/bin/env python3
"""
Module de découverte d'URLs pour amiens.fr
Généralise les stratégies de découverte à tout le site

Stratégies implémentées :
1. Découverte par push-blocks (H2 → URLs)
2. Découverte par liens internes
3. Découverte par navigation
4. Découverte par sitemap.xml
"""

from __future__ import annotations

import re
import time
from typing import List, Set, Optional
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup


def slugify(text: str) -> str:
    """Convertit un texte en slug (minuscules, tirets)"""
    slug = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug


class URLDiscoverer:
    """
    Découvre les URLs sur amiens.fr en utilisant plusieurs stratégies
    """
    
    def __init__(self, base_domain: str = "https://www.amiens.fr", 
                 respect_robots: bool = True,
                 delay: float = 1.0):
        self.base_domain = base_domain
        self.visited: Set[str] = set()
        self.respect_robots = respect_robots
        self.delay = delay
        self.robots_parser = None
        
        if respect_robots:
            self._load_robots()
    
    def _load_robots(self):
        """Charge et parse robots.txt"""
        try:
            robots_url = f"{self.base_domain}/robots.txt"
            self.robots_parser = RobotFileParser()
            self.robots_parser.set_url(robots_url)
            self.robots_parser.read()
        except Exception as e:
            print(f"⚠️ Impossible de charger robots.txt: {e}")
            self.robots_parser = None
    
    def _can_fetch(self, url: str) -> bool:
        """Vérifie si l'URL est autorisée par robots.txt"""
        if not self.respect_robots or not self.robots_parser:
            return True
        user_agent = "I-Amiens-Crawler/1.0"
        return self.robots_parser.can_fetch(user_agent, url)
    
    def _is_valid_url(self, url: str, check_exists: bool = True) -> bool:
        """Vérifie si l'URL est valide et existe"""
        if url in self.visited:
            return False
        
        if not self._can_fetch(url):
            return False
        
        if not check_exists:
            return True
        
        try:
            resp = requests.head(url, timeout=5, allow_redirects=True)
            if resp.status_code == 200:
                self.visited.add(url)
                time.sleep(self.delay)  # Respecter le délai
                return True
        except Exception:
            pass
        
        return False
    
    def discover_push_blocks(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Découvre les URLs via les push-blocks (H2 dans .push-block__inner)
        
        Stratégie : Le site utilise des blocs de navigation avec H2.
        Le texte du H2 peut être converti en slug pour construire une URL.
        
        Args:
            soup: BeautifulSoup de la page
            base_url: URL de base pour construire les URLs relatives
        
        Returns:
            Liste d'URLs découvertes
        """
        urls = []
        blocks = soup.select(".push-block__inner h2")
        
        for block in blocks:
            text = block.get_text(strip=True)
            if not text:
                continue
            
            # Slugifier le texte du H2
            slug = slugify(text)
            
            # Construire l'URL candidate
            candidate = f"{base_url.rstrip('/')}/{slug}"
            
            # Vérifier si l'URL est valide
            if self._is_valid_url(candidate):
                urls.append(candidate)
        
        return urls
    
    def discover_internal_links(self, soup: BeautifulSoup, 
                                current_url: str,
                                pattern: Optional[str] = None) -> List[str]:
        """
        Découvre les URLs via les liens internes (<a href>)
        
        Args:
            soup: BeautifulSoup de la page
            current_url: URL actuelle pour résoudre les liens relatifs
            pattern: Pattern optionnel pour filtrer les URLs (ex: "/Enfance")
        
        Returns:
            Liste d'URLs découvertes
        """
        urls = []
        
        for link in soup.select("a[href]"):
            href = link.get("href")
            if not href:
                continue
            
            # Résoudre l'URL absolue
            absolute_url = urljoin(current_url, href)
            parsed = urlparse(absolute_url)
            
            # Filtrer par domaine
            if parsed.netloc != urlparse(self.base_domain).netloc:
                continue
            
            # Filtrer par pattern si fourni
            if pattern and pattern not in absolute_url:
                continue
            
            # Normaliser l'URL (enlever fragments et query params)
            canonical = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            # Vérifier si l'URL est valide
            if self._is_valid_url(canonical, check_exists=False):
                urls.append(canonical)
        
        return urls
    
    def discover_from_navigation(self, soup: BeautifulSoup, 
                                 base_url: str) -> List[str]:
        """
        Découvre les URLs depuis les menus de navigation
        
        Args:
            soup: BeautifulSoup de la page
            base_url: URL de base
        
        Returns:
            Liste d'URLs découvertes
        """
        urls = []
        
        # Navigation principale (plusieurs sélecteurs possibles)
        nav_selectors = [
            "nav a[href]",
            ".navigation a[href]",
            ".menu a[href]",
            ".main-menu a[href]",
            "[role='navigation'] a[href]"
        ]
        
        for selector in nav_selectors:
            nav_links = soup.select(selector)
            for link in nav_links:
                href = link.get("href")
                if href:
                    absolute_url = urljoin(base_url, href)
                    if self._is_valid_url(absolute_url, check_exists=False):
                        urls.append(absolute_url)
        
        return urls
    
    def discover_from_sitemap(self) -> List[str]:
        """
        Découvre les URLs depuis le sitemap.xml
        
        Returns:
            Liste d'URLs découvertes
        """
        urls = []
        sitemap_url = f"{self.base_domain}/sitemap.xml"
        
        try:
            resp = requests.get(sitemap_url, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "xml")
                
                # Sitemap standard
                for loc in soup.find_all("loc"):
                    url = loc.text.strip()
                    if url.startswith(self.base_domain):
                        if self._is_valid_url(url, check_exists=False):
                            urls.append(url)
                
                # Sitemap index (sitemaps multiples)
                for sitemap in soup.find_all("sitemap"):
                    loc = sitemap.find("loc")
                    if loc:
                        sitemap_url = loc.text.strip()
                        # Récursivement parser le sous-sitemap
                        try:
                            sub_resp = requests.get(sitemap_url, timeout=10)
                            if sub_resp.status_code == 200:
                                sub_soup = BeautifulSoup(sub_resp.content, "xml")
                                for loc in sub_soup.find_all("loc"):
                                    url = loc.text.strip()
                                    if url.startswith(self.base_domain):
                                        if self._is_valid_url(url, check_exists=False):
                                            urls.append(url)
                        except Exception:
                            pass
        
        except Exception as e:
            print(f"⚠️ Erreur sitemap: {e}")
        
        return urls
    
    def discover_all(self, soup: BeautifulSoup, current_url: str,
                     pattern: Optional[str] = None) -> List[str]:
        """
        Combine toutes les stratégies de découverte
        
        Args:
            soup: BeautifulSoup de la page
            current_url: URL actuelle
            pattern: Pattern optionnel pour filtrer
        
        Returns:
            Liste d'URLs découvertes (dédupliquées)
        """
        all_urls = set()
        
        # Stratégie 1: Push-blocks
        push_urls = self.discover_push_blocks(soup, current_url)
        all_urls.update(push_urls)
        
        # Stratégie 2: Liens internes
        internal_urls = self.discover_internal_links(soup, current_url, pattern)
        all_urls.update(internal_urls)
        
        # Stratégie 3: Navigation
        nav_urls = self.discover_from_navigation(soup, current_url)
        all_urls.update(nav_urls)
        
        return list(all_urls)


def fetch_page(url: str) -> BeautifulSoup:
    """Récupère une page et retourne un BeautifulSoup"""
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.content, "html.parser")
    except Exception as e:
        raise RuntimeError(f"Impossible de récupérer {url}: {e}") from e


if __name__ == "__main__":
    # Test de la découverte
    discoverer = URLDiscoverer()
    
    # Test sur section Enfance
    test_url = "https://www.amiens.fr/Vivre-a-Amiens/Enfance"
    print(f"🔍 Test sur: {test_url}")
    
    soup = fetch_page(test_url)
    
    # Test push-blocks
    push_urls = discoverer.discover_push_blocks(soup, test_url)
    print(f"✅ Push-blocks: {len(push_urls)} URLs")
    for url in push_urls[:5]:  # Afficher les 5 premières
        print(f"   - {url}")
    
    # Test liens internes
    internal_urls = discoverer.discover_internal_links(soup, test_url, "/Enfance")
    print(f"\n✅ Liens internes: {len(internal_urls)} URLs")
    for url in internal_urls[:5]:
        print(f"   - {url}")
    
    # Test sitemap
    sitemap_urls = discoverer.discover_from_sitemap()
    print(f"\n✅ Sitemap: {len(sitemap_urls)} URLs")
    for url in sitemap_urls[:5]:
        print(f"   - {url}")

