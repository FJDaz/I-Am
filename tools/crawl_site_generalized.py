#!/usr/bin/env python3
"""
Crawler généralisé pour tout le site amiens.fr
Utilise toutes les stratégies de découverte documentées

Usage:
    python crawl_site_generalized.py [--section SECTION] [--all]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Set, Optional

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.discover_urls import URLDiscoverer, fetch_page
from tools.rebuild_corpus import parse_page, Segment, slugify

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "ML" / "data" / "site_sections.json"
OUTPUT_PATH = ROOT / "ML" / "data" / "corpus_metadata_generalized.json"


def load_sections_config() -> Dict:
    """Charge la configuration des sections"""
    if not CONFIG_PATH.exists():
        print(f"❌ Fichier de configuration non trouvé: {CONFIG_PATH}")
        sys.exit(1)
    
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def crawl_section(section_config: Dict, discoverer: URLDiscoverer,
                  max_pages: int = 200) -> List[Segment]:
    """
    Crawl une section complète du site en utilisant toutes les stratégies
    
    Args:
        section_config: Configuration de la section
        discoverer: Instance de URLDiscoverer
        max_pages: Nombre maximum de pages à crawler
    
    Returns:
        Liste de segments extraits
    """
    base_url = section_config["base_url"]
    pattern = section_config.get("pattern")
    categories = section_config.get("categories", [])
    section_name = section_config.get("name", "unknown")
    
    print(f"\n{'='*60}")
    print(f"🔍 Crawling section: {section_name}")
    print(f"   URL: {base_url}")
    print(f"   Pattern: {pattern}")
    print(f"   Catégories: {', '.join(categories)}")
    print(f"{'='*60}\n")
    
    all_segments: List[Segment] = []
    to_visit: List[str] = [base_url]
    visited: Set[str] = set()
    
    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        
        if url in visited:
            continue
        
        visited.add(url)
        print(f"📄 [{len(visited)}/{max_pages}] {url}")
        
        try:
            # Parser la page et extraire les segments
            segments = parse_page(url, categories[0] if categories else section_name.lower())
            all_segments.extend(segments)
            print(f"   ✅ {len(segments)} segments extraits")
            
            # Découvrir de nouvelles URLs avec toutes les stratégies
            soup = fetch_page(url)
            
            # Stratégie 1: Push-blocks (H2 → URLs)
            push_urls = discoverer.discover_push_blocks(soup, url)
            if push_urls:
                print(f"   🔗 Push-blocks: {len(push_urls)} URLs découvertes")
                for new_url in push_urls:
                    if new_url not in visited and new_url not in to_visit:
                        to_visit.append(new_url)
            
            # Stratégie 2: Liens internes
            internal_urls = discoverer.discover_internal_links(soup, url, pattern)
            if internal_urls:
                print(f"   🔗 Liens internes: {len(internal_urls)} URLs découvertes")
                for new_url in internal_urls:
                    if new_url not in visited and new_url not in to_visit:
                        to_visit.append(new_url)
            
            # Stratégie 3: Navigation
            nav_urls = discoverer.discover_from_navigation(soup, url)
            if nav_urls:
                print(f"   🔗 Navigation: {len(nav_urls)} URLs découvertes")
                for new_url in nav_urls:
                    if new_url not in visited and new_url not in to_visit:
                        to_visit.append(new_url)
        
        except Exception as e:
            print(f"   ⚠️ Erreur: {e}")
            continue
    
    print(f"\n✅ Section {section_name}: {len(all_segments)} segments au total")
    return all_segments


def crawl_all_sections(config: Dict, section_name: Optional[str] = None) -> List[Segment]:
    """
    Crawl toutes les sections ou une section spécifique
    
    Args:
        config: Configuration complète
        section_name: Nom de la section à crawler (None = toutes)
    
    Returns:
        Liste de tous les segments
    """
    settings = config.get("settings", {})
    discoverer = URLDiscoverer(
        delay=settings.get("delay_between_requests", 1.0),
        respect_robots=settings.get("respect_robots_txt", True)
    )
    
    all_segments: List[Segment] = []
    
    # Stratégie 0: Sitemap (si activé)
    if settings.get("use_sitemap", True):
        print("🗺️  Découverte via sitemap.xml...")
        sitemap_urls = discoverer.discover_from_sitemap()
        print(f"✅ {len(sitemap_urls)} URLs découvertes via sitemap")
    
    # Filtrer les sections
    sections = config.get("sections", [])
    if section_name:
        sections = [s for s in sections if s.get("name") == section_name]
        if not sections:
            print(f"❌ Section '{section_name}' non trouvée")
            return []
    
    # Filtrer les sections activées
    sections = [s for s in sections if s.get("enabled", True)]
    
    # Trier par priorité
    sections.sort(key=lambda x: x.get("priority", 999))
    
    # Crawler chaque section
    for section in sections:
        max_pages = settings.get("max_pages_per_section", 200)
        segments = crawl_section(section, discoverer, max_pages)
        all_segments.extend(segments)
    
    return all_segments


def save_corpus(segments: List[Segment], output_path: Path):
    """Sauvegarde le corpus au format JSON"""
    corpus = [
        {
            "label": segment.label,
            "url": segment.url,
            "category": segment.category,
            "content": segment.content,
        }
        for segment in segments
    ]
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Corpus sauvegardé: {output_path}")
    print(f"   {len(corpus)} segments au total")


def main():
    parser = argparse.ArgumentParser(
        description="Crawler généralisé pour amiens.fr"
    )
    parser.add_argument(
        "--section",
        type=str,
        help="Nom de la section à crawler (ex: 'Enfance')"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Crawler toutes les sections activées"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(OUTPUT_PATH),
        help="Chemin du fichier de sortie"
    )
    
    args = parser.parse_args()
    
    # Charger la configuration
    config = load_sections_config()
    
    # Déterminer les sections à crawler
    if args.all:
        section_name = None
    elif args.section:
        section_name = args.section
    else:
        # Par défaut: seulement les sections activées
        section_name = None
    
    # Crawler
    print("🚀 Démarrage du crawl généralisé\n")
    segments = crawl_all_sections(config, section_name)
    
    # Sauvegarder
    output_path = Path(args.output)
    save_corpus(segments, output_path)
    
    print(f"\n✅ Crawl terminé: {len(segments)} segments extraits")


if __name__ == "__main__":
    main()

