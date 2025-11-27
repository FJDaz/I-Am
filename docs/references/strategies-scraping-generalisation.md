# 🕷️ Stratégies de Scraping et Généralisation à Tout le Site

**Date :** 2025-01-XX  
**Objectif :** Documenter toutes les stratégies employées pour récupérer les informations cachées et proposer un plan pour généraliser I-Amiens à tout le site amiens.fr

---

## 📋 Table des Matières

1. [Stratégies Actuelles](#stratégies-actuelles)
2. [Architecture de Découverte](#architecture-de-découverte)
3. [Plan de Généralisation](#plan-de-généralisation)
4. [Implémentation](#implémentation)

---

## 🎯 Stratégies Actuelles

### 1. **Découverte par Push-Blocks (H2 → URLs)**

**Fichier :** `tools/rebuild_corpus.py`  
**Fonction :** `discover_push_blocks()`

**Principe :**
- Le site amiens.fr utilise des blocs de navigation avec la classe `.push-block__inner`
- Chaque bloc contient un `<h2>` qui représente une section
- Le texte du H2 peut être converti en slug pour construire une URL

**Code actuel :**
```python
def discover_push_blocks(soup: BeautifulSoup, base_url: str) -> List[str]:
    urls = []
    blocks = soup.select(".push-block__inner h2")
    for block in blocks:
        text = block.get_text(strip=True)
        if not text:
            continue
        slug = slugify(text)  # Convertit en slug (minuscules, tirets)
        candidate = f"{base_url.rstrip('/')}/{slug}"
        urls.append(candidate)
    return urls
```

**Exemple :**
- H2 : "Modalités d'inscription"
- Slug : `modalites-d-inscription`
- URL construite : `https://www.amiens.fr/vivre-a-amiens/enfance/centres-de-loisirs/modalites-d-inscription`

**Limitations actuelles :**
- ❌ Fonctionne seulement pour la section Enfance
- ❌ Ne gère pas les variations de casse dans les URLs
- ❌ Ne vérifie pas si l'URL existe avant de l'ajouter

---

### 2. **Scraping Dynamique avec Playwright**

**Fichier :** `ML/scripts/Audit_Scrap_enfance.py`

**Stratégies :**

#### a) **Clics automatiques sur éléments interactifs**
```python
# Cliquer sur tous les "voir +" et accordéons
await page.evaluate("""
    () => {
        document.querySelectorAll('button, a').forEach(el => {
            if(/voir|plus|détails/i.test(el.innerText)) el.click();
        });
    }
""")
```

#### b) **Extraction de contenu caché**
- Tables avec `display:none`
- Éléments `aria-hidden="true"`
- Contenu dans accordéons fermés

#### c) **Découverte récursive de liens**
- Suit tous les liens internes
- Limite à 150 pages par défaut
- Filtre par domaine (`BASE_URL`)

**Avantages :**
- ✅ Récupère le contenu généré par JavaScript
- ✅ Découvre les pages cachées dans les accordéons
- ✅ Extrait les PDFs automatiquement

**Limitations :**
- ❌ Lent (nécessite un navigateur)
- ❌ Limité à la section Enfance (`BASE_URL = "https://www.amiens.fr/Vivre-a-Amiens/Enfance"`)

---

### 3. **Extraction de PDFs**

**Fichier :** `tools/rebuild_corpus.py`  
**Fonction :** `extract_pdf_links()`

**Principe :**
```python
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
```

**Utilisation :**
- Les PDFs sont indexés comme segments séparés
- Catégorie : `{category}_pdf`
- Contenu : URL du PDF (peut être enrichi avec extraction texte)

---

### 4. **Crawling Respectueux (robots.txt)**

**Fichier :** `ML/scripts/# crawler_respectueux.py`

**Principe :**
- Vérifie `robots.txt` avant chaque requête
- Respecte les délais entre requêtes (1 seconde)
- Filtre par section (`/Enfance`)

**Code :**
```python
rp = urllib.robotparser.RobotFileParser()
rp.set_url(urljoin(BASE, "/robots.txt"))
rp.read()
if not rp.can_fetch(USER_AGENT, url):
    continue
```

---

## 🏗️ Architecture de Découverte

### Stratégies Multi-Niveaux

```
┌─────────────────────────────────────────────────┐
│  Niveau 1 : URLs Directes (Sources Configurées) │
│  - URLs dans corpus_sources.json                │
│  - URLs par défaut (DEFAULT_SOURCES)            │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  Niveau 2 : Découverte Push-Blocks (H2)        │
│  - Extraire H2 de .push-block__inner           │
│  - Slugifier et construire URLs                │
│  - Vérifier existence (HEAD request)            │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  Niveau 3 : Suivi Liens Internes               │
│  - Extraire tous les <a href>                  │
│  - Filtrer par domaine amiens.fr               │
│  - Filtrer par pattern (optionnel)             │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  Niveau 4 : Scraping Dynamique (Playwright)    │
│  - Cliquer sur éléments interactifs            │
│  - Extraire contenu caché (display:none)      │
│  - Découvrir nouvelles URLs après interaction  │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Plan de Généralisation

### Phase 1 : Généraliser les Stratégies de Découverte

#### 1.1. **Fonction de Découverte Universelle**

**Créer :** `tools/discover_urls.py`

```python
"""
Module de découverte d'URLs pour amiens.fr
Généralise les stratégies de découverte à tout le site
"""

from typing import List, Set, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

class URLDiscoverer:
    def __init__(self, base_domain: str = "https://www.amiens.fr"):
        self.base_domain = base_domain
        self.visited: Set[str] = set()
    
    def discover_push_blocks(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Découvre les URLs via les push-blocks (H2)"""
        urls = []
        blocks = soup.select(".push-block__inner h2")
        for block in blocks:
            text = block.get_text(strip=True)
            if not text:
                continue
            slug = slugify(text)
            candidate = f"{base_url.rstrip('/')}/{slug}"
            if self._is_valid_url(candidate):
                urls.append(candidate)
        return urls
    
    def discover_internal_links(self, soup: BeautifulSoup, 
                                current_url: str,
                                pattern: Optional[str] = None) -> List[str]:
        """Découvre les URLs via les liens internes"""
        urls = []
        for link in soup.select("a[href]"):
            href = link.get("href")
            if not href:
                continue
            absolute_url = urljoin(current_url, href)
            parsed = urlparse(absolute_url)
            
            # Filtrer par domaine
            if parsed.netloc != urlparse(self.base_domain).netloc:
                continue
            
            # Filtrer par pattern si fourni
            if pattern and pattern not in absolute_url:
                continue
            
            # Enlever fragments et query params pour normaliser
            canonical = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if canonical not in self.visited:
                urls.append(canonical)
        
        return urls
    
    def discover_from_navigation(self, soup: BeautifulSoup, 
                                 base_url: str) -> List[str]:
        """Découvre les URLs depuis les menus de navigation"""
        urls = []
        
        # Navigation principale
        nav_links = soup.select("nav a[href], .navigation a[href]")
        for link in nav_links:
            href = link.get("href")
            if href:
                absolute_url = urljoin(base_url, href)
                if self._is_valid_url(absolute_url):
                    urls.append(absolute_url)
        
        return urls
    
    def discover_from_sitemap(self) -> List[str]:
        """Découvre les URLs depuis le sitemap.xml"""
        urls = []
        sitemap_url = f"{self.base_domain}/sitemap.xml"
        try:
            resp = requests.get(sitemap_url, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "xml")
                for loc in soup.find_all("loc"):
                    url = loc.text.strip()
                    if url.startswith(self.base_domain):
                        urls.append(url)
        except Exception as e:
            print(f"⚠️ Erreur sitemap: {e}")
        
        return urls
    
    def _is_valid_url(self, url: str) -> bool:
        """Vérifie si l'URL existe (HEAD request)"""
        if url in self.visited:
            return False
        try:
            resp = requests.head(url, timeout=5, allow_redirects=True)
            if resp.status_code == 200:
                self.visited.add(url)
                return True
        except:
            pass
        return False
```

---

#### 1.2. **Configuration par Section**

**Créer :** `ML/data/site_sections.json`

```json
{
  "sections": [
    {
      "name": "Enfance",
      "base_url": "https://www.amiens.fr/Vivre-a-Amiens/Enfance",
      "pattern": "/Enfance",
      "categories": ["tarifs", "centres_loisirs", "inscriptions", "menus", "rpe"]
    },
    {
      "name": "Jeunesse",
      "base_url": "https://www.amiens.fr/Vivre-a-Amiens/Jeunesse",
      "pattern": "/Jeunesse",
      "categories": ["activites", "inscriptions", "tarifs"]
    },
    {
      "name": "Culture",
      "base_url": "https://www.amiens.fr/Vivre-a-Amiens/Culture",
      "pattern": "/Culture",
      "categories": ["evenements", "lieux", "reservations"]
    },
    {
      "name": "Sport",
      "base_url": "https://www.amiens.fr/Vivre-a-Amiens/Sport",
      "pattern": "/Sport",
      "categories": ["equipements", "inscriptions", "tarifs"]
    }
  ]
}
```

---

### Phase 2 : Crawler Multi-Section

#### 2.1. **Crawler Généralisé**

**Créer :** `tools/crawl_site.py`

```python
#!/usr/bin/env python3
"""
Crawler généralisé pour tout le site amiens.fr
Utilise toutes les stratégies de découverte
"""

import json
from pathlib import Path
from typing import List, Dict
from discover_urls import URLDiscoverer
from rebuild_corpus import parse_page, Segment

def crawl_section(section_config: Dict, discoverer: URLDiscoverer) -> List[Segment]:
    """Crawl une section complète du site"""
    base_url = section_config["base_url"]
    pattern = section_config.get("pattern")
    categories = section_config.get("categories", [])
    
    all_segments = []
    to_visit = [base_url]
    visited = set()
    
    while to_visit:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)
        
        try:
            # Parser la page
            segments = parse_page(url, categories[0] if categories else "general")
            all_segments.extend(segments)
            
            # Découvrir de nouvelles URLs
            soup = fetch_page(url)
            
            # Stratégie 1: Push-blocks
            push_urls = discoverer.discover_push_blocks(soup, url)
            for new_url in push_urls:
                if new_url not in visited:
                    to_visit.append(new_url)
            
            # Stratégie 2: Liens internes
            internal_urls = discoverer.discover_internal_links(soup, url, pattern)
            for new_url in internal_urls:
                if new_url not in visited:
                    to_visit.append(new_url)
            
            # Stratégie 3: Navigation
            nav_urls = discoverer.discover_from_navigation(soup, url)
            for new_url in nav_urls:
                if new_url not in visited:
                    to_visit.append(new_url)
        
        except Exception as e:
            print(f"⚠️ Erreur sur {url}: {e}")
            continue
    
    return all_segments

def crawl_all_sections(config_path: str) -> List[Segment]:
    """Crawl toutes les sections configurées"""
    with open(config_path) as f:
        config = json.load(f)
    
    discoverer = URLDiscoverer()
    all_segments = []
    
    # Stratégie 0: Sitemap
    sitemap_urls = discoverer.discover_from_sitemap()
    print(f"✅ {len(sitemap_urls)} URLs découvertes via sitemap")
    
    for section in config["sections"]:
        print(f"\n🔍 Crawling section: {section['name']}")
        segments = crawl_section(section, discoverer)
        all_segments.extend(segments)
        print(f"✅ {len(segments)} segments trouvés")
    
    return all_segments
```

---

### Phase 3 : Scraping Dynamique Généralisé

#### 3.1. **Playwright Multi-Section**

**Modifier :** `ML/scripts/Audit_Scrap_enfance.py` → `ML/scripts/crawl_dynamic.py`

```python
"""
Scraping dynamique généralisé avec Playwright
Généralise à toutes les sections du site
"""

async def crawl_section_dynamic(section_config: Dict, page):
    """Crawl dynamique d'une section"""
    base_url = section_config["base_url"]
    pattern = section_config.get("pattern")
    
    visited = set()
    to_visit = [base_url]
    
    while to_visit and len(visited) < MAX_PAGES:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)
        
        try:
            await page.goto(url, timeout=20000)
            
            # Cliquer sur éléments interactifs
            await page.evaluate("""
                () => {
                    // Cliquer sur "voir +", accordéons, etc.
                    document.querySelectorAll('button, a, [role="button"]').forEach(el => {
                        const text = el.innerText?.toLowerCase() || '';
                        if(/voir|plus|détails|afficher|développer/i.test(text)) {
                            el.click();
                        }
                    });
                    
                    // Ouvrir tous les accordéons
                    document.querySelectorAll('[aria-expanded="false"]').forEach(el => {
                        el.click();
                    });
                }
            """)
            
            await page.wait_for_timeout(1000)
            await page.wait_for_load_state("networkidle")
            
            # Extraire contenu
            content = await page.content()
            await save_file(f"{slugify(url)}.html", content)
            
            # Découvrir nouveaux liens
            new_links = await page.locator("a[href]").evaluate_all(
                "els => els.map(el => el.href)"
            )
            
            for link in new_links:
                if link and pattern in link and link not in visited:
                    to_visit.append(link)
        
        except Exception as e:
            print(f"⚠️ {url}: {e}")
```

---

## 🔧 Implémentation

### Étape 1 : Créer les Modules de Découverte

```bash
cd "I Amiens"
mkdir -p tools/discovery
touch tools/discovery/__init__.py
touch tools/discovery/url_discoverer.py
touch tools/discovery/section_crawler.py
```

### Étape 2 : Généraliser `rebuild_corpus.py`

**Modifier :** `tools/rebuild_corpus.py`

- Ajouter support multi-sections
- Utiliser `URLDiscoverer` pour toutes les stratégies
- Charger configuration depuis `site_sections.json`

### Étape 3 : Créer Script de Crawl Complet

**Créer :** `tools/crawl_full_site.py`

```python
#!/usr/bin/env python3
"""
Crawl complet du site amiens.fr
Combine toutes les stratégies de découverte
"""

from discovery.url_discoverer import URLDiscoverer
from discovery.section_crawler import crawl_all_sections
from rebuild_corpus import rebuild_corpus

def main():
    # 1. Crawl statique (BeautifulSoup)
    print("🔍 Phase 1: Crawl statique...")
    corpus_static = rebuild_corpus()  # Modifié pour multi-sections
    
    # 2. Crawl dynamique (Playwright) - optionnel
    print("\n🔍 Phase 2: Crawl dynamique...")
    # corpus_dynamic = crawl_dynamic_all_sections()
    
    # 3. Fusion et déduplication
    print("\n✅ Fusion des corpus...")
    # corpus_final = merge_corpus(corpus_static, corpus_dynamic)
    
    print(f"✅ Corpus final: {len(corpus_final)} segments")

if __name__ == "__main__":
    main()
```

---

## 📊 Stratégies Résumées

| Stratégie | Fichier Actuel | Généralisation | Priorité |
|-----------|----------------|-----------------|----------|
| **Push-Blocks (H2)** | `rebuild_corpus.py` | ✅ `discover_urls.py` | Haute |
| **Liens Internes** | `Audit_Scrap_enfance.py` | ✅ `discover_urls.py` | Haute |
| **Scraping Dynamique** | `Audit_Scrap_enfance.py` | ✅ `crawl_dynamic.py` | Moyenne |
| **Sitemap** | ❌ Non implémenté | ✅ `discover_urls.py` | Basse |
| **Navigation** | ❌ Non implémenté | ✅ `discover_urls.py` | Basse |
| **PDFs** | `rebuild_corpus.py` | ✅ Déjà généralisé | Haute |

---

## 🎯 Checklist de Généralisation

- [ ] Créer `tools/discovery/url_discoverer.py`
- [ ] Créer `ML/data/site_sections.json`
- [ ] Modifier `tools/rebuild_corpus.py` pour multi-sections
- [ ] Créer `tools/crawl_full_site.py`
- [ ] Généraliser `ML/scripts/Audit_Scrap_enfance.py` → `crawl_dynamic.py`
- [ ] Tester sur section Enfance (régression)
- [ ] Tester sur section Jeunesse
- [ ] Tester sur section Culture
- [ ] Documenter les nouvelles URLs découvertes
- [ ] Mettre à jour `corpus_sources.json` avec nouvelles sections

---

## 📝 Notes Importantes

### Limitations à Garder en Tête

1. **Rate Limiting** : Respecter `robots.txt` et délais entre requêtes
2. **Contenu Dynamique** : Certaines pages nécessitent JavaScript (Playwright)
3. **URLs Variables** : Certaines URLs peuvent changer (versions, dates)
4. **Contenu Protégé** : Certaines pages peuvent nécessiter authentification

### Améliorations Futures

1. **Cache** : Mettre en cache les pages déjà crawlé
2. **Parallélisation** : Crawler plusieurs sections en parallèle
3. **Monitoring** : Logger les URLs découvertes vs visitées
4. **Validation** : Vérifier qualité du contenu extrait

---

**Dernière mise à jour :** 2025-01-XX

