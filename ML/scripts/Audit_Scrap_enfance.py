"""
Audit et scraping dynamique pour la rubrique "Enfance" du site amiens.fr
- Active le rendu JS
- Clique sur les "voir +" et les accordéons
- Récupère les tables, contenus cachés et PDF
- Sauvegarde dans download_amiens_enfance
"""

import asyncio
import os
import re
from urllib.parse import urljoin, urldefrag, urlparse
from playwright.async_api import async_playwright

OUTPUT_DIR = "/Users/francois-jeandazin/Documents/En Cours/Crea/NUX/I Amiens/download_amiens_enfance"
BASE_URL = "https://www.amiens.fr/Vivre-a-Amiens/Enfance"

os.makedirs(OUTPUT_DIR, exist_ok=True)

visited = set()
MAX_PAGES = 150

def _clean_texts(texts):
    return [text.strip() for text in texts if text and text.strip()]


async def save_file(name, content):
    path = os.path.join(OUTPUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"💾 Saved: {path}")


async def extract_page_content(page, url):
    # Cliquer sur tous les "voir +" et accordéons
    await page.evaluate("""
        () => {
            document.querySelectorAll('button, a').forEach(el => {
                if(/voir|plus|détails/i.test(el.innerText)) el.click();
            });
        }
    """)

    await page.wait_for_timeout(800)  # laisse le temps au JS de charger le contenu
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
        if text and re.search(r"voir|plus|détails", text, re.I)
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
    await save_file(f"{slug}.txt", report_content)
    await save_file(f"{slug}.html", content)

    # Récupérer les liens internes pour crawler
    raw_links = await page.locator("a[href]").evaluate_all("els => els.map(el => el.href)")
    internal_links = []
    for link in raw_links:
        if not link:
            continue
        canonical_link, _ = urldefrag(link)
        if canonical_link.startswith(BASE_URL) and canonical_link not in visited and canonical_link not in internal_links:
            internal_links.append(canonical_link)
    return internal_links

async def crawl(url, page):
    canonical_url, _ = urldefrag(url)
    if canonical_url in visited:
        return
    visited.add(canonical_url)
    if len(visited) > MAX_PAGES:
        return
    try:
        await page.goto(canonical_url, timeout=20000)
        new_links = await extract_page_content(page, canonical_url)
        for link in new_links:
            await crawl(link, page)
    except Exception as e:
        print(f"⚠️ {url}: {e}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await crawl(BASE_URL, page)
        await browser.close()
    print("✅ Audit dynamique terminé.")

if __name__ == "__main__":
    asyncio.run(main())
