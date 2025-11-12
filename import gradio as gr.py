
# pip install gradio
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Tuple

import difflib
import huggingface_hub
import re

try:  # huggingface_hub>=0.21 n'expose plus HfFolder, ce stub restaure l'API attendue par gradio.
    from huggingface_hub import HfFolder  # type: ignore
except ImportError:
    class HfFolder:  # minimal backport utilisé par gradio.oauth
        _token_path = Path.home() / ".huggingface" / "token"

        @classmethod
        def path_token(cls) -> str:
            return str(cls._token_path)

        @classmethod
        def save_token(cls, token: str) -> None:
            cls._token_path.parent.mkdir(parents=True, exist_ok=True)
            cls._token_path.write_text(token, encoding="utf-8")

        @classmethod
        def get_token(cls) -> str | None:
            try:
                return cls._token_path.read_text(encoding="utf-8").strip()
            except FileNotFoundError:
                return None

        @classmethod
        def delete_token(cls) -> None:
            try:
                cls._token_path.unlink()
            except FileNotFoundError:
                pass

    setattr(huggingface_hub, "HfFolder", HfFolder)

import gradio as gr

try:
    from cursor import Client

    CursorClientType = Client
except ImportError:
    CursorClientType = None  # type: ignore

CURSOR_CLIENT: CursorClientType | None = None
if CursorClientType is not None:
    api_key = os.getenv("CURSOR_API_KEY")
    if api_key:
        CURSOR_CLIENT = CursorClientType(api_key=api_key)

FALLBACK_DIR = Path("download_amiens_enfance")
NOISE_PATTERNS = (
    "votre navigateur est obsolète",
    "mettez à jour votre navigateur",
)


def _is_valid_section(section: str) -> bool:
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


def _load_fallback_segments() -> List[Tuple[str, int, str]]:
    segments: List[Tuple[str, int, str]] = []
    if not FALLBACK_DIR.exists():
        return segments

    for path in sorted(FALLBACK_DIR.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = path.read_text(encoding="utf-8", errors="ignore")

            raw_sections = re.split(r"\n{2,}", text)
            for index, section in enumerate(raw_sections, start=1):
                section = section.strip()
                if not section:
                    continue
                if not _is_valid_section(section):
                    continue
                segments.append((path.name, index, section))

    return segments


FALLBACK_SEGMENTS = _load_fallback_segments()


def _slugify(text: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9]+", "-", text)
    sanitized = sanitized.strip("-")
    return sanitized.lower()


def _guess_url_from_filename(filename: str) -> str | None:
    stem = Path(filename).stem
    if not stem:
        return None

    parts = stem.split("_")
    if not parts:
        return None

    slug_parts = [_slugify(part) for part in parts]
    if any(not part for part in slug_parts):
        return None

    slug = "/".join(slug_parts)
    return f"https://www.amiens.fr/{slug}"


def _score_snippet(question: str, content: str) -> float:
    question = question.lower()
    content_lower = content.lower()
    tokens = [token for token in question.split() if len(token) > 2]
    if not tokens:
        return 0.0

    counts = sum(content_lower.count(token) for token in tokens)
    match_ratio = difflib.SequenceMatcher(None, question, content_lower[:1000]).ratio()
    return counts + match_ratio


def _snippet_from_content(content: str, question: str, window: int = 320) -> str:
    content_lower = content.lower()
    question_lower = question.lower()
    idx = -1
    for token in question_lower.split():
        if len(token) < 3:
            continue
        idx = content_lower.find(token)
        if idx != -1:
            break

    if idx == -1:
        snippet = content[:window]
    else:
        start = max(idx - window // 2, 0)
        end = min(start + window, len(content))
        snippet = content[start:end]
    return snippet.strip()


def _normalize_snippet(snippet: str, max_chars: int = 400) -> str:
    collapsed = re.sub(r"\s+", " ", snippet).strip()
    if len(collapsed) <= max_chars:
        return collapsed

    truncated = collapsed[:max_chars].rsplit(" ", 1)[0]
    return truncated + "…"

def ask(question: str) -> Tuple[str, str]:
    if CURSOR_CLIENT:
        docs = CURSOR_CLIENT.search(question, top_k=3)
        answer = " ".join(doc["content"] for doc in docs)
        sources = ", ".join(doc.get("source", "inconnu") for doc in docs)
        return answer, sources

    if not FALLBACK_SEGMENTS:
        message = (
            "Aucune connexion Cursor disponible et aucun corpus local trouvé. "
            f"Ajoute des fichiers texte dans `{FALLBACK_DIR}` ou configure Cursor pour activer la recherche."
        )
        return (
            "Je ne peux pas encore répondre depuis Cursor. "
            "Ajoute des documents locaux ou configure le client RAG.",
            message,
        )

    scored_segments = [
        (filename, index, content, _score_snippet(question, content))
        for filename, index, content in FALLBACK_SEGMENTS
    ]
    ranked = [
        (filename, index, content, score)
        for filename, index, content, score in sorted(
            scored_segments, key=lambda item: item[2], reverse=True
        )
        if score > 0
    ][:3]

    if not ranked:
        message = (
            "Aucun extrait local ne correspond clairement à la question. "
            "Ajoute davantage de contenu structuré ou configure Cursor pour des résultats plus précis."
        )
        return (
            "Je n'ai pas trouvé de passage pertinent dans le corpus local.",
            message,
        )

    answer_parts = []
    links: List[str] = []
    for filename, index, content, _score in ranked:
        snippet = _normalize_snippet(_snippet_from_content(content, question))
        label = f"{filename} (section {index})"
        url = _guess_url_from_filename(filename)
        if url:
            answer_parts.append(f"{label}:\n{snippet}\n→ {url}")
            links.append(f"{label}: {url}")
        else:
            answer_parts.append(f"{label}:\n{snippet}")
            links.append(label)

    answer = "\n\n".join(answer_parts)
    link_summary = "\n".join(links)

    return answer, f"Sources locales:\n{link_summary}"

iface = gr.Interface(
    fn=ask,
    inputs="text",
    outputs=["text", "text"],
    title="Assistant Enfance Amiens",
    description=(
        "Pose une question sur la rubrique Enfance. "
        "Si Cursor est configuré (paquet + env CURSOR_API_KEY), le système répond avec les infos RAG."
    ),
)

iface.launch()
