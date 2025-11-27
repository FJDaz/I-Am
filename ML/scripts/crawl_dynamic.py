"""
Scraping dynamique généralisé pour toutes les sections du site amiens.fr
- Active le rendu JS avec Playwright
- Clique sur les "voir +" et les accordéons
- Récupère les tables, contenus cachés et PDF
- Généralise Audit_Scrap_enfance.py pour toutes les sections
"""

import asyncio
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urldefrag, urlparse
from playwright.async_api import async_playwright

# Chemins relatifs au projet
ROOT = Path(__file__).resolve().parents[2]
SECTIONS_CONFIG = ROOT / "ML" / "data" / "site_sections.json"
OUTPUT_BASE_DIR = ROOT / "ML" / "download_amiens_enfance"

visited = set()
MAX_PAGES = 150


def load_sections_config() -> Dict:
    """Charge la configuration des sections"""
    if not SECTIONS_CONFIG.exists():
        print(f"⚠️ Configuration non trouvée: {SECTIONS_CONFIG}")
        return {"sections": []}
    
    with SECTIONS_CONFIG.open(encoding="utf-8") as f:
        return json.load(f)


def _clean_texts(texts):
    return [text.strip() for text in texts if text and text.strip()]


async def save_file(name: str, content: str, output_dir: Path):
    """Sauvegarde un fichier dans le répertoire de sortie"""
    path = output_dir / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(content)
    print(f"💾 Saved: {path}")


async def extract_page_content(page, url: str, base_url: str, output_dir: Path):
    """
    Extrait le contenu d'une page avec scraping dynamique
    
    Args:
        page: Page Playwright
        url: URL de la page
        base_url: URL de base pour filtrer les liens
        output_dir: Répertoire de sortie
    """
    # Cliquer sur tous les "voir +" et accordéons
    await page.evaluate("""
        () => {
            // Cliquer sur boutons "voir +", "détails", etc.
            document.querySelectorAll('button, a, [role="button"]').forEach(el => {
                const text = el.innerText?.toLowerCase() || '';
                if(/voir|plus|détails|afficher|développer/i.test(text)) {
                    el.click();
                }
            });
            
            // Ouvrir tous les accordéons fermés
            document.querySelectorAll('[aria-expanded="false"]').forEach(el => {
                el.click();
            });
        }
    """)

    await page.wait_for_timeout(1000)  # Laisse le temps au JS de charger le contenu
    await page.wait_for_load_state("networkidle")

    # Récupérer HTML
    content = await page.content()

    # Extraire tables, display:none, aria-hidden, PDF links
    tables = _clean_texts(await page.locator("table").all_inner_texts())
    display_none = _clean_texts(await page.locator("[style*='display:none']").all_inner_texts())
    aria_hidden = _clean_texts(await page.locator("[aria-hidden='true']").all_inner_texts())

    button_texts = await page.locator("a, button").all_inner_texts()
    voir_plus_texts = [
        text.strip()
        for text in button_texts
        if text and re.search(r"voir|plus|détails|afficher", text, re.I)
    ]

    pdf_hrefs = await page.locator("a[href$='.pdf']").evaluate_all("els => els.map(el => el.getAttribute('href'))")
    pdf_links = [urljoin(url, href) for href in pdf_hrefs if href]

    # Sauvegarde du résultat
    canonical_url, fragment = urldefrag(url)
    parsed = urlparse(canonical_url)
    slug = parsed.path.strip("/") or "index"
    slug = slug.replace("/", "_")
    if fragment:
        slug = f"{slug}__{fragment}"
    slug = slug.replace("#", "_").replace("?", "_")

    report_content = f"""
URL: {url}

Tables: {tables}
Display:none: {display_none}
Aria-hidden: {aria_hidden}
Voir+: {voir_plus_texts}
PDFs: {pdf_links}
"""
    await save_file(f"{slug}.txt", report_content, output_dir)
    await save_file(f"{slug}.html", content, output_dir)

    # Récupérer les liens internes pour crawler
    raw_links = await page.locator("a[href]").evaluate_all("els => els.map(el => el.href)")
    internal_links = []
    for link in raw_links:
        if not link:
            continue
        canonical_link, _ = urldefrag(link)
        if canonical_link.startswith(base_url) and canonical_link not in visited and canonical_link not in internal_links:
            internal_links.append(canonical_link)
    return internal_links


async def crawl_section(url: str, base_url: str, page, output_dir: Path):
    """
    Crawl récursif d'une section
    
    Args:
        url: URL à crawler
        base_url: URL de base pour filtrer les liens
        page: Page Playwright
        output_dir: Répertoire de sortie
    """
    canonical_url, _ = urldefrag(url)
    if canonical_url in visited:
        return
    visited.add(canonical_url)
    if len(visited) > MAX_PAGES:
        return
    try:
        await page.goto(canonical_url, timeout=20000)
        new_links = await extract_page_content(page, canonical_url, base_url, output_dir)
        for link in new_links:
            await crawl_section(link, base_url, page, output_dir)
    except Exception as e:
        print(f"⚠️ {url}: {e}")


async def crawl_all_sections():
    """Crawl toutes les sections activées depuis la configuration"""
    config = load_sections_config()
    sections = [s for s in config.get("sections", []) if s.get("enabled", False)]
    
    if not sections:
        print("⚠️ Aucune section activée dans site_sections.json")
        return
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        for section in sections:
            section_name = section.get("name", "unknown")
            base_url = section.get("base_url")
            pattern = section.get("pattern", "")
            
            print(f"\n{'='*60}")
            print(f"🔍 Crawling dynamique section: {section_name}")
            print(f"   URL: {base_url}")
            print(f"{'='*60}\n")
            
            # Réinitialiser visited pour chaque section
            visited.clear()
            
            # Créer répertoire de sortie pour cette section
            output_dir = OUTPUT_BASE_DIR / section_name.lower().replace(" ", "_")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Crawler la section
            await crawl_section(base_url, base_url, page, output_dir)
            
            print(f"\n✅ Section {section_name}: {len(visited)} pages crawlé")
        
        await browser.close()
    
    print("\n✅ Audit dynamique terminé.")


async def main():
    """Point d'entrée principal"""
    await crawl_all_sections()


if __name__ == "__main__":
    asyncio.run(main())

