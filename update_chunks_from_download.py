from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from bs4 import BeautifulSoup


ROOT = Path(__file__).parent
DOWNLOAD_DIR = ROOT / "download_amiens_enfance"
CHUNKS_PATH = ROOT / "chunks_enfance_clean.json"
DEFAULT_CATEGORY = "Enfance"


def _clean_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _strip_unwanted_nodes(soup: BeautifulSoup) -> None:
    for tag in soup(["script", "style", "noscript", "template"]):
        tag.decompose()
    for selector in ("header", "footer", "nav", "form", "aside"):
        for tag in soup.select(selector):
            tag.decompose()


def extract_main_text(html_path: Path) -> str | None:
    try:
        raw_html = html_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw_html = html_path.read_text(encoding="latin-1", errors="ignore")

    soup = BeautifulSoup(raw_html, "html.parser")
    _strip_unwanted_nodes(soup)

    main = soup.find("main")
    candidates: Iterable[BeautifulSoup] = (main,) if main else ()
    if not candidates:
        body = soup.find("body")
        candidates = (body,) if body else (soup,)

    for candidate in candidates:
        if candidate is None:
            continue
        text = candidate.get_text(separator="\n")
        cleaned = _clean_text(text)
        if len(cleaned.split()) >= 50:
            return cleaned

    return None


def load_chunks() -> list[dict]:
    if not CHUNKS_PATH.exists():
        return []
    return json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))


def persist_chunks(chunks: list[dict]) -> None:
    chunks.sort(key=lambda item: item.get("source", ""))
    CHUNKS_PATH.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    if not DOWNLOAD_DIR.exists():
        raise SystemExit(f"Dossier introuvable : {DOWNLOAD_DIR}")

    chunks = load_chunks()
    existing_sources = {entry.get("source") for entry in chunks}
    additions = 0

    for html_path in sorted(DOWNLOAD_DIR.glob("*.html")):
        source_name = html_path.name
        if source_name in existing_sources:
            continue

        text = extract_main_text(html_path)
        if not text:
            continue

        chunks.append(
            {
                "source": source_name,
                "content": text,
                "category": DEFAULT_CATEGORY,
            }
        )
        existing_sources.add(source_name)
        additions += 1

    persist_chunks(chunks)
    print(f"{additions} nouvelles entrées ajoutées dans {CHUNKS_PATH.name}")


if __name__ == "__main__":
    main()

