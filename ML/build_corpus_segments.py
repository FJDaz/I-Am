from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable, List, Tuple

ROOT = Path(__file__).parent
CHUNKS_PATH = ROOT / "chunks_enfance_clean.json"
OUTPUT_EXTENSION_PATH = ROOT / "chrome-extension" / "data" / "corpus_segments.json"
OUTPUT_DATA_PATH = ROOT / "data" / "corpus_segments.json"

NOISE_PATTERNS = (
    "votre navigateur est obsolète",
    "mettez à jour votre navigateur",
)


def load_chunks() -> Iterable[Tuple[str, str]]:
    data = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
    for entry in data:
        source = entry.get("source") or "inconnu.txt"
        content = entry.get("content") or ""
        yield source, content


def slugify(component: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", component)
    slug = slug.strip("-")
    return slug.lower()


def guess_url(source: str) -> str | None:
    stem = Path(source).stem
    if not stem:
        return None
    parts = [part for part in stem.split("_") if part]
    if not parts:
        return None
    slug_parts = [slugify(part) for part in parts]
    if any(not part for part in slug_parts):
        return None
    return "https://www.amiens.fr/" + "/".join(slug_parts)


def is_valid_section(section: str) -> bool:
    lowered = section.lower()
    if any(pattern in lowered for pattern in NOISE_PATTERNS):
        return False

    words = re.findall(r"\b\w+\b", section)
    if len(words) < 15:
        return False

    unique_words = {word.lower() for word in words if len(word) > 2}
    if len(unique_words) < 5:
        return False

    alpha_ratio = sum(char.isalpha() for char in section) / max(len(section), 1)
    if alpha_ratio < 0.35:
        return False

    return True


def split_sections(content: str) -> List[str]:
    sections = []
    raw_sections = re.split(r"\n{2,}", content)
    for section in raw_sections:
        section = section.strip()
        if not section:
            continue
        if not is_valid_section(section):
            continue
        sections.append(section)
    return sections


def build_segments() -> List[dict]:
    segments: List[dict] = []
    for source, content in load_chunks():
        url = guess_url(source)
        sections = split_sections(content)
        for index, section in enumerate(sections, start=1):
            label = f"{source} (section {index})"
            segments.append(
                {
                    "label": label,
                    "source": source,
                    "section": index,
                    "content": section,
                    "url": url,
                }
            )
    return segments


def write_output(segments: List[dict]) -> None:
    text = json.dumps(segments, ensure_ascii=False, indent=2)
    OUTPUT_EXTENSION_PATH.write_text(text, encoding="utf-8")
    OUTPUT_DATA_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(f"Fichier introuvable : {CHUNKS_PATH}")

    segments = build_segments()
    write_output(segments)
    print(f"{len(segments)} segments écrits dans {OUTPUT_EXTENSION_PATH}")


if __name__ == "__main__":
    main()

