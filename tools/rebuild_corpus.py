#!/usr/bin/env python3
"""
Rebuild the RAG corpus from a curated set of Amiens Enfance URLs.
Handles pages with JS-driven navigation by discovering <div class="push-block__inner">
and rewriting slugs, captures collapsible sections, and extracts PDF links for menus.
Outputs a fresh data/corpus_metadata.json.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import html2text
from bs4 import BeautifulSoup

# Import URLDiscoverer pour découverte généralisée
try:
    from tools.discover_urls import URLDiscoverer, fetch_page as fetch_page_discover
except ImportError:
    # Fallback si discover_urls n'est pas disponible
    URLDiscoverer = None
    fetch_page_discover = None

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "data" / "corpus_metadata.json"
CONFIG_PATH = ROOT / "data" / "corpus_sources.json"

DEFAULT_SOURCES = [
  {"url": "https://www.amiens.fr/vivre-a-amiens/enfance/a-table/les-tarifs", "category": "tarifs"},
  {"url": "https://www.amiens.fr/Vivre-a-Amiens/Enfance/Centres-de-loisirs", "category": "centres_loisirs"},
  {"url": "https://www.amiens.fr/vivre-a-amiens/enfance/a-l-ecole/inscriptions-scolaires2", "category": "inscriptions"},
  {"url": "https://www.amiens.fr/Vivre-a-Amiens/Enfance/Centres-de-loisirs/Modalites-d-inscription", "category": "modalites"},
  {"url": "https://www.amiens.fr/Vivre-a-Amiens/Enfance/LES-RELAIS-PETITE-ENFANCE", "category": "rpe"},
  {"url": "https://www.amiens.fr/vivre-a-amiens/enfance/a-table/les-menus", "category": "menus"},
]

HTML2TEXT_CONVERTER = html2text.HTML2Text()
HTML2TEXT_CONVERTER.ignore_links = False
HTML2TEXT_CONVERTER.ignore_images = False


class CrawlError(RuntimeError):
  pass


def load_sources() -> List[Dict[str, str]]:
  if CONFIG_PATH.exists():
    with CONFIG_PATH.open(encoding="utf-8") as f:
      data = json.load(f)
    return data.get("sources", DEFAULT_SOURCES)
  return DEFAULT_SOURCES


def fetch_page(url: str) -> BeautifulSoup:
  import urllib.request

  try:
    with urllib.request.urlopen(url) as resp:
      html = resp.read()
  except Exception as exc:
    raise CrawlError(f"Unable to fetch {url}: {exc}") from exc
  return BeautifulSoup(html, "html.parser")


def slugify(text: str) -> str:
  slug = re.sub(r"[^\w\s-]", "", text.lower()).strip()
  slug = re.sub(r"[\s_]+", "-", slug)
  return slug


def discover_push_blocks(soup: BeautifulSoup, base_url: str, discoverer: Optional[URLDiscoverer] = None) -> List[str]:
  """
  Découvre les URLs via push-blocks (H2).
  Utilise URLDiscoverer si disponible, sinon fallback sur implémentation locale.
  """
  if discoverer is not None:
    return discoverer.discover_push_blocks(soup, base_url)
  
  # Fallback : implémentation locale (compatibilité)
  urls = []
  blocks = soup.select(".push-block__inner h2")
  for block in blocks:
    text = block.get_text(strip=True)
    if not text:
      continue
    slug = slugify(text)
    candidate = f"{base_url.rstrip('/')}/{slug}"
    urls.append(candidate)
  return urls


def extract_pdf_links(soup: BeautifulSoup) -> List[str]:
  pdf_links = []
  for tag in soup.select("a[href$='.pdf']"):
    href = tag.get("href")
    if href:
      if href.startswith("http"):
        pdf_links.append(href)
      else:
        pdf_links.append("https://www.amiens.fr" + href)
  return pdf_links


def html_to_markdown(html: str) -> str:
  return HTML2TEXT_CONVERTER.handle(html)


@dataclass
class Segment:
  url: str
  label: str
  category: str
  content: str


def parse_page(url: str, category: str) -> List[Segment]:
  soup = fetch_page(url)
  segments: List[Segment] = []
  main_content = soup.find("main") or soup
  for article in main_content.find_all(["article", "section", "div"], recursive=False):
    text = article.get_text(" ", strip=True)
    if not text:
      continue
    markdown = html_to_markdown(str(article))
    label = article.get("id") or article.get("class")
    if isinstance(label, list):
      label = "-".join(label)
    label = label or f"{category}-{len(segments)+1}"
    segments.append(Segment(url=url, label=str(label), category=category, content=markdown))
  if not segments:
    markdown = html_to_markdown(str(main_content))
    segments.append(Segment(url=url, label=category, category=category, content=markdown))
  for pdf_url in extract_pdf_links(soup):
    segments.append(Segment(url=pdf_url, label="pdf", category=f"{category}_pdf", content=pdf_url))
  return segments


def rebuild_corpus(use_discoverer: bool = True) -> List[Dict[str, str]]:
  """
  Rebuild corpus from sources.
  
  Args:
    use_discoverer: Si True, utilise URLDiscoverer pour découverte avancée
  """
  sources = load_sources()
  seen_urls = set()
  all_segments: List[Segment] = []
  
  # Initialiser URLDiscoverer si disponible
  discoverer = None
  if use_discoverer and URLDiscoverer is not None:
    discoverer = URLDiscoverer(respect_robots=True, delay=1.0)
  
  for source in sources:
    base_url = source["url"]
    category = source.get("category", "general")
    if base_url in seen_urls:
      continue
    seen_urls.add(base_url)
    try:
      segments = parse_page(base_url, category)
      all_segments.extend(segments)
    except CrawlError as exc:
      print(exc, file=sys.stderr)
      continue
    
    # Découvrir nouvelles URLs avec URLDiscoverer ou fallback
    soup = fetch_page(base_url)
    discovered_urls = discover_push_blocks(soup, base_url, discoverer)
    
    for discovered in discovered_urls:
      if discovered in seen_urls:
        continue
      seen_urls.add(discovered)
      try:
        segments = parse_page(discovered, category)
        all_segments.extend(segments)
      except CrawlError:
        continue

  corpus = [
    {
      "label": segment.label,
      "url": segment.url,
      "category": segment.category,
      "content": segment.content,
    }
    for segment in all_segments
  ]
  return corpus


def main() -> None:
  corpus = rebuild_corpus()
  OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
  with OUTPUT_PATH.open("w", encoding="utf-8") as f:
    json.dump(corpus, f, ensure_ascii=False, indent=2)
  print(f"✅ Nouveau corpus généré ({len(corpus)} segments) → {OUTPUT_PATH}")


if __name__ == "__main__":
  main()

