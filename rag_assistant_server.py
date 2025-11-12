import json
import os
import re
import unicodedata
import string
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

try:
  from anthropic import Anthropic
except ImportError as exc:
  raise SystemExit("Install anthropic package: pip install anthropic fastapi uvicorn") from exc

ASSISTANT_SYSTEM_PROMPT = """
Tu es l'assistant officiel "Amiens Enfance".
Analyse chaque question en tenant compte :
- des segments RAG numérotés (#1, #2, …) et de leur résumé,
- du mémo de conversation (ce qui a déjà été répondu).

Style :
- Réponse HTML très courte : intro ≤ 3 phrases, puis <h3>Synthèse</h3> (1 phrase) et <h3>Ouverture</h3> (1 phrase). Évite listes et répétitions inutiles.
- Si une information a déjà été fournie, mentionne “déjà indiqué (#n)” ou renvoie au mémo plutôt que la détailler à nouveau.
- Cite au moins une source cliquable si disponible.
- Dans `alignment.summary`, indique clairement les segments exploités (ex. "Segments #1, #3").

Ne mentionne rien en dehors des segments.

Réponse obligatoire (JSON strict) :
{
  "answer_html": "...",
  "answer_text": "...",
  "follow_up_question": "...",
  "alignment": {"status": "...", "label": "...", "summary": "Segments #1, #3"},
  "sources": [{"title": "...", "url": "...", "confidence": "..."}]
}
"""

load_dotenv()
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
if not anthropic_key:
  raise SystemExit("ANTHROPIC_API_KEY non défini. Ajoute la clé dans .env")

client = Anthropic(api_key=anthropic_key)

EMBED_MODEL_NAME = os.environ.get("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDINGS_PATH = Path(
  os.environ.get("EMBEDDINGS_PATH", Path(__file__).resolve().parent / "data" / "corpus_embeddings.npy")
)
METADATA_PATH = Path(
  os.environ.get("METADATA_PATH", Path(__file__).resolve().parent / "data" / "corpus_metadata.json")
)
LEXICON_PATH = Path(
  os.environ.get(
    "LEXICON_PATH",
    Path(__file__).resolve().parent / "chrome-extension-v2" / "data" / "lexique_enfance.json"
  )
)
corpus_embeddings = None
corpus_metadata = None
embed_model = None
lexicon_entries: List[Dict[str, Any]] = []
whoosh_index = None
whoosh_dir: Optional[Path] = None
try:
  from sentence_transformers import SentenceTransformer
except ImportError:
  SentenceTransformer = None
  print("⚠️ sentence-transformers non installé ; la recherche sémantique sera désactivée.")

try:
  from whoosh import scoring
  from whoosh.analysis import StemmingAnalyzer
  from whoosh.fields import ID, TEXT, Schema
  from whoosh.index import create_in, open_dir
  from whoosh.qparser import MultifieldParser, OrGroup
except ImportError:
  scoring = None
  StemmingAnalyzer = None
  Schema = None
  create_in = None
  open_dir = None
  MultifieldParser = None


class RagSegment(BaseModel):
  label: Optional[str] = None
  url: Optional[str] = None
  score: Optional[float] = None
  excerpt: Optional[str] = None
  content: Optional[str] = None
  custom_id: Optional[str] = None


class ConversationTurn(BaseModel):
  role: str
  content: str


class AssistantRequest(BaseModel):
  question: str
  normalized_question: Optional[str] = None
  rag_results: List[RagSegment]
  conversation: List[ConversationTurn] = []
  instructions: Optional[str] = None
  intent_label: Optional[str] = None
  intent_weight: Optional[float] = None


class AlignmentPayload(BaseModel):
  status: str
  label: str
  summary: str


class AssistantResponse(BaseModel):
  answer_html: str
  answer_text: Optional[str] = None
  follow_up_question: Optional[str] = None
  alignment: AlignmentPayload
  sources: List[Dict[str, Any]] = []


CURRENCY_KEYWORDS = (
  "tarif",
  "tarifs",
  "prix",
  "€",
  "garderie",
  "coute",
  "coûte",
  "cout",
  "coût",
  "combien",
  "facturation",
  "facture",
  "montant",
  "payer",
)
CURRENCY_BONUS = 2.5

INTENTION_KEYWORDS = {
  "action": {
    "weight": 1.0,
    "keywords": (
      "payer",
      "ouvrir",
      "fermer",
      "où",
      "quand",
      "contact",
      "téléphone",
      "telephone",
      "appeler",
      "adresse",
      "horaire",
      "heures",
      "mail",
      "email",
    ),
  },
  "planification": {
    "weight": 0.8,
    "keywords": (
      "inscription",
      "inscrire",
      "période",
      "periode",
      "calendrier",
      "date limite",
      "deadline",
      "réserver",
      "reserver",
      "pré-inscription",
      "pre-inscription",
      "préinscription",
      "preinscription",
      "planning",
    ),
  },
  "compréhension": {
    "weight": 0.5,
    "keywords": (
      "explication",
      "expliquer",
      "comment",
      "procédure",
      "procedure",
      "fonctionne",
      "fonctionnement",
      "dossier",
      "conditions",
      "documents",
    ),
  },
  "organisation": {
    "weight": 0.3,
    "keywords": (
      "plusieurs",
      "cumul",
      "coordination",
      "répartition",
      "repartition",
      "combien de temps",
      "temps de garde",
      "planning multiple",
      "alternance",
    ),
  },
  "anticipation": {
    "weight": 0.1,
    "keywords": (
      "si jamais",
      "au cas où",
      "au cas ou",
      "futur",
      "prévoir",
      "prevoir",
      "anticiper",
      "risque",
      "éventuel",
      "eventuel",
      "prévision",
      "prevision",
      "projection",
    ),
  },
}


def _strip_accents(text: str) -> str:
  normalized = unicodedata.normalize("NFKD", text)
  return "".join(char for char in normalized if not unicodedata.combining(char))


def _normalize(text: Optional[str]) -> str:
  if not text:
    return ""
  stripped = _strip_accents(text.lower())
  translation_table = str.maketrans(
    {
      "0": "o",
      "1": "i",
      "2": "z",
      "3": "e",
      "4": "a",
      "5": "s",
      "6": "g",
      "7": "t",
      "8": "b",
      "9": "g",
    }
  )
  replaced = stripped.translate(translation_table)
  cleaned_chars = []
  last_char = ""
  repeat_count = 0
  for char in replaced:
    if char in string.ascii_lowercase or char.isdigit() or char.isspace():
      if char == last_char:
        repeat_count += 1
        if repeat_count >= 3:
          continue
      else:
        repeat_count = 1
        last_char = char
      cleaned_chars.append(char)
    else:
      cleaned_chars.append(" ")
      last_char = ""
      repeat_count = 0
  cleaned = "".join(cleaned_chars)
  cleaned = " ".join(cleaned.split())
  return cleaned


def load_lexicon():
  global lexicon_entries
  if not LEXICON_PATH.exists():
    print(f"ℹ️ Lexique non trouvé ({LEXICON_PATH}); aucun boost lexical appliqué.")
    lexicon_entries = []
    return
  try:
    with LEXICON_PATH.open(encoding="utf-8") as f:
      data = json.load(f)
    raw_entries = data.get("lexique_enfance", [])
    prepared: List[Dict[str, Any]] = []
    for entry in raw_entries:
      ter_usager = entry.get("terme_usager")
      if not ter_usager:
        continue
      normalized_usager = _normalize(ter_usager)
      admin_terms = entry.get("terme_admin") or []
      normalized_admin = [_normalize(term) for term in admin_terms if term]
      prepared.append(
        {
          "terme_usager": ter_usager,
          "terme_admin": admin_terms,
          "poids": float(entry.get("poids", 0.0)),
          "_normalized_usager": normalized_usager,
          "_normalized_admin": [term for term in normalized_admin if term],
        }
      )
    lexicon_entries = prepared
    print(f"✅ Lexique chargé ({len(lexicon_entries)} entrées).")
  except Exception as exc:
    print(f"⚠️ Impossible de charger le lexique: {exc}")
    lexicon_entries = []


RAW_QUERY_HINTS = {
  "tarifs": [
    "Synthese tarif 2024 2025",
    "tarifs centre de loisirs",
    "grille tarifaire amiens",
  ],
  "centre de loisirs": [
    "Synthese tarif 2024 2025",
    "tarifs accueil de loisirs",
  ],
  "inscription": [
    "inscriptions scolaires",
    "inscription scolaire",
    "mairie de secteur",
    "pièces justificatives",
  ],
  "inscrire": [
    "inscriptions scolaires",
    "mairie de secteur",
    "pièces justificatives",
  ],
  "s inscrire": [
    "inscriptions scolaires",
    "mairie de secteur",
    "pièces justificatives",
  ],
  "inscription scolaire": [
    "inscriptions scolaires",
    "mairie de secteur",
    "pièces justificatives",
  ],
  "documents": [
    "pièces justificatives",
    "dossier inscription",
  ],
  "justificatif": [
    "pièces justificatives",
    "dossier inscription",
  ],
  "périscolaire": [
    "accueil périscolaire",
    "inscription périscolaire",
  ],
}

QUERY_HINTS = { _normalize(key): value for key, value in RAW_QUERY_HINTS.items() }


def match_lexicon_entries(
  question: Optional[str],
  normalized_question: Optional[str] = None
) -> List[Dict[str, Any]]:
  if not lexicon_entries:
    return []
  text = _normalize(normalized_question) or _normalize(question)
  if not text:
    return []
  matches: List[Dict[str, Any]] = []
  for entry in lexicon_entries:
    key = entry.get("_normalized_usager")
    if key and key in text:
      matches.append(entry)
  return matches


def expand_query_with_lexicon(question: str, matches: List[Dict[str, Any]]) -> str:
  if not question or not matches:
    return question
  extra_terms: List[str] = []
  for entry in matches:
    for admin_term in entry.get("terme_admin", []):
      if admin_term and admin_term not in extra_terms:
        extra_terms.append(admin_term)
    normalized_usager = entry.get("_normalized_usager")
    if normalized_usager:
      hints = QUERY_HINTS.get(normalized_usager, [])
      for hint in hints:
        if hint and hint not in extra_terms:
          extra_terms.append(hint)
  if not extra_terms:
    return question
  return f"{question} " + " ".join(extra_terms)


def question_mentions_currency(question: Optional[str], normalized_question: Optional[str] = None) -> bool:
  text = _normalize(normalized_question) or _normalize(question)
  return any(keyword in text for keyword in CURRENCY_KEYWORDS)


def segment_contains_currency_data(segment: RagSegment) -> bool:
  text_parts = [
    segment.content or "",
    segment.excerpt or "",
    getattr(segment, "summary", "") or ""  # front peut envoyer des champs supplémentaires
  ]
  text = "\n".join(part for part in text_parts if part)
  if not text:
    return False
  if "€" in text:
    return True
  lowered = text.lower()
  if "tarif" in lowered or "prix" in lowered:
    return True
  digit_count = sum(ch.isdigit() for ch in text)
  return digit_count >= 4


def apply_currency_bonus(question: Optional[str], normalized_question: Optional[str], segments: List[RagSegment]) -> None:
  if not segments:
    return
  if not question_mentions_currency(question, normalized_question):
    return
  for segment in segments:
    if segment_contains_currency_data(segment):
      base_score = segment.score or 0.0
      segment.score = base_score + CURRENCY_BONUS


def apply_lexicon_bonus(
  segments: List[RagSegment],
  matches: List[Dict[str, Any]],
) -> None:
  if not segments or not matches:
    return
  for segment in segments:
    content_parts = [
      segment.content or "",
      segment.excerpt or "",
      getattr(segment, "label", "") or "",
      getattr(segment, "source", "") or "",
    ]
    normalized_content = _normalize(" ".join(part for part in content_parts if part))
    if not normalized_content:
      continue
    bonus = 0.0
    for entry in matches:
      weight = float(entry.get("poids", 0.0))
      if weight <= 0:
        continue
      normalized_admin_terms = entry.get("_normalized_admin", [])
      if any(term and term in normalized_content for term in normalized_admin_terms):
        bonus += weight
    if bonus:
      segment.score = (segment.score or 0.0) + bonus


def extract_user_snippet(question: Optional[str]) -> Optional[str]:
  if not question:
    return None
  lines = [line for line in question.splitlines() if line.strip()]
  if len(lines) < 2:
    return None
  content = "\n".join(lines)
  has_table_layout = any(("|" in line or "\t" in line) for line in lines)
  has_bullet_list = any(line.strip().startswith(("•", "-", "*", "●", "▪")) for line in lines)
  has_currency_symbol = "€" in content
  digit_count = sum(ch.isdigit() for ch in content)
  if (has_table_layout or has_currency_symbol or has_bullet_list) and digit_count >= 2:
    snippet = "\n".join(lines[:40])
    return snippet[:1200]
  return None


def compute_segment_refs(segments: List[RagSegment]) -> List[Tuple[str, RagSegment]]:
  refs: List[Tuple[str, RagSegment]] = []
  numeric_index = 1
  for segment in segments:
    if segment.custom_id:
      refs.append((segment.custom_id, segment))
    else:
      refs.append((str(numeric_index), segment))
      numeric_index += 1
  return refs


def detect_user_intention(question: Optional[str], normalized_question: Optional[str] = None) -> Tuple[str, float]:
  text = _normalize(normalized_question) or _normalize(question)
  if not text:
    return "inconnue", 0.0

  best_label = "inconnue"
  best_weight = 0.0

  for label, data in INTENTION_KEYWORDS.items():
    keywords = data.get("keywords", ())
    weight = float(data.get("weight", 0.0))
    if any(keyword in text for keyword in keywords):
      if weight > best_weight:
        best_label = label
        best_weight = weight

  return best_label, best_weight


def build_prompt(payload: AssistantRequest) -> str:
  lines = []
  lines.append(f"Question utilisateur: {payload.question}\n")
  if payload.normalized_question:
    lines.append(f"Question normalisée: {payload.normalized_question}\n")
  if payload.intent_label:
    weight_display = f"{payload.intent_weight:.2f}" if payload.intent_weight is not None else "n/a"
    lines.append(f"Intention détectée: {payload.intent_label} (poids {weight_display})\n")

  if payload.conversation:
    lines.append("Historique:\n")
    for turn in payload.conversation[-6:]:
      role = "Utilisateur" if turn.role == "user" else "Assistant"
      lines.append(f"- {role}: {turn.content}\n")

  lines.append("\nSegments RAG (références #n) :\n")
  if not payload.rag_results:
    lines.append("Aucun extrait disponible.\n")
  else:
    segment_refs = compute_segment_refs(payload.rag_results)
    for ref, seg in segment_refs:
      snippet = (seg.excerpt or seg.content or "").replace("\n", " ")
      snippet = snippet[:200]
      lines.append(
        f"#{ref}: {seg.label or getattr(seg, 'source', None) or 'Segment'} — {snippet}"
        + (f" (url: {seg.url})" if seg.url else "")
      )
    if any(seg.custom_id == "U" for seg in payload.rag_results):
      lines.append(
        "\nNote: Le segment #U provient directement d'une contribution utilisateur. "
        "Tu peux t'appuyer sur le segment #U fourni par l'utilisateur pour tes calculs ou vérifications.\n"
      )
  lines.append("\nDétails RAG (tronqués) :\n")
  for ref, seg in compute_segment_refs(payload.rag_results or []):
    lines.append(f"[#{ref}] {seg.label or getattr(seg, 'source', None) or 'Segment'}\n")
    if seg.url:
      lines.append(f"URL: {seg.url}\n")
    if seg.score is not None:
      lines.append(f"Score: {seg.score:.2f}\n")
    excerpt = (seg.excerpt or "").strip()
    if excerpt:
      lines.append(f"Extrait court: {excerpt[:400]}\n")
    content = (seg.content or "").strip()
    if content:
      lines.append(f"Contenu tronqué: {content[:800]}\n")
    lines.append("---\n")

  lines.append("\nConsigne complémentaire:\n")
  lines.append(payload.instructions or "")
  return "".join(lines)


def load_embeddings():
  global corpus_embeddings, corpus_metadata, embed_model, whoosh_index, whoosh_dir
  if SentenceTransformer is None:
    return
  try:
    corpus_embeddings = np.load(EMBEDDINGS_PATH)
    with METADATA_PATH.open(encoding="utf-8") as f:
      corpus_metadata = json.load(f)
    embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    print(f"✅ Embeddings chargés ({corpus_embeddings.shape[0]} segments).")

    if Schema and StemmingAnalyzer:
      schema = Schema(
        id=ID(stored=True, unique=True),
        label=TEXT(stored=True),
        content=TEXT(analyzer=StemmingAnalyzer(minsize=2), stored=False),
      )
      whoosh_dir = Path(tempfile.mkdtemp(prefix="amiens_whoosh_"))
      ix = create_in(whoosh_dir, schema)
      writer = ix.writer()
      for idx, meta in enumerate(corpus_metadata):
        doc_id = str(idx)
        label = meta.get("label") or meta.get("source") or ""
        content = " ".join(
          str(meta.get(field, "")) for field in ("content", "label", "source", "section")
        )
        writer.add_document(id=doc_id, label=label, content=content)
      writer.commit()
      whoosh_index = ix
      print(f"✅ Index Whoosh construit ({len(corpus_metadata)} documents).")
    else:
      whoosh_index = None
      print("⚠️ Whoosh indisponible : installation requise pour BM25 local.")
  except Exception as exc:
    print(f"⚠️ Impossible de charger les embeddings: {exc}")
    corpus_embeddings = None
    corpus_metadata = None
    embed_model = None
    whoosh_index = None


def semantic_search(
  question: str,
  matches: Optional[List[Dict[str, Any]]] = None,
  top_k: int = 5,
  min_score: float = 0.2
) -> List[Tuple[float, Dict[str, Any]]]:
  results: Dict[str, Dict[str, Any]] = {}
  weights: Dict[str, float] = {}
  lexicon_terms: List[str] = []
  if matches:
    for entry in matches:
      lexicon_terms.extend(entry.get("_normalized_admin", []))
  normalized_terms = [term for term in lexicon_terms if term]

  if whoosh_index:
    parser = MultifieldParser(["label", "content"], schema=whoosh_index.schema, group=OrGroup)
    query = parser.parse(question)
    with whoosh_index.searcher(weighting=scoring.BM25F(B=0.75, K1=1.6)) as searcher:
      hits = searcher.search(query, limit=top_k * 4)
      for hit in hits:
        doc_id = hit["id"]
        score = float(hit.score or 0.0)
        meta = corpus_metadata[int(doc_id)]
        results[doc_id] = {
          "label": meta.get("label"),
          "url": meta.get("url"),
          "section": meta.get("section"),
          "source": meta.get("source"),
          "content": meta.get("content"),
        }
        bm25_weight = score * 1.2
        if normalized_terms:
          normalized_content = _normalize(meta.get("content") or "")
          term_hits = sum(1 for term in normalized_terms if term and term in normalized_content)
          if term_hits:
            bm25_weight += term_hits * 2.5
        weights[doc_id] = weights.get(doc_id, 0.0) + bm25_weight

  if corpus_embeddings is not None and embed_model is not None:
    query_vec = embed_model.encode([question], normalize_embeddings=True)[0]
    scores = corpus_embeddings @ query_vec
    best_idx = np.argsort(-scores)[: top_k * 4]
    for idx in best_idx:
      score = float(scores[idx])
      if score < min_score:
        continue
      doc_id = str(idx)
      meta = corpus_metadata[idx]
      if doc_id not in results:
        results[doc_id] = {
          "label": meta.get("label"),
          "url": meta.get("url"),
          "section": meta.get("section"),
          "source": meta.get("source"),
          "content": meta.get("content"),
        }
      cosine_weight = score * 0.4
      weights[doc_id] = weights.get(doc_id, 0.0) + cosine_weight

  ranked = sorted(weights.items(), key=lambda item: item[1], reverse=True)[:top_k]
  combined_results: List[Tuple[float, Dict[str, Any]]] = []
  for doc_id, score in ranked:
    meta = results.get(doc_id)
    if not meta:
      continue
    combined_results.append((score, {**meta, "score": score}))
  return combined_results


def call_model(prompt: str) -> Dict[str, Any]:
  response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=900,
    temperature=0.2,
    system=ASSISTANT_SYSTEM_PROMPT,
    messages=[{"role": "user", "content": prompt}],
  )

  if not response.content:
    raise HTTPException(status_code=502, detail="Réponse vide du modèle")

  text = "".join(part.text for part in response.content if hasattr(part, "text"))
  clean = text.strip()
  if clean.startswith("```"):
    lines = clean.splitlines()
    # retire la première ligne (``` or ```json) et la dernière ligne ```
    clean = "\n".join(lines[1:-1]).strip()
  try:
    return json.loads(clean)
  except json.JSONDecodeError:
    # tente d'extraire un bloc ```json ... ```
    code_blocks = re.findall(r"```(?:json)?\s*(.*?)```", clean, flags=re.DOTALL | re.IGNORECASE)
    for block in code_blocks:
      try:
        return json.loads(block.strip())
      except json.JSONDecodeError:
        continue
    # tente la première portion entre { ... }
    json_start = clean.find("{")
    json_end = clean.rfind("}")
    if json_start != -1 and json_end != -1 and json_end > json_start:
      snippet = clean[json_start : json_end + 1]
      try:
        return json.loads(snippet)
      except json.JSONDecodeError:
        pass
  try:
    data = json.loads(clean)
    return data
  except Exception as exc:
    print("\n=== Réponse brute du modèle (JSON attendu) ===")
    print(text)
    print("=== Fin de la réponse brute ===\n")
    raise HTTPException(status_code=502, detail=f"JSON invalide: {exc}") from exc


app = FastAPI(title="RAG Assistant Amiens V2", version="0.2.0")
load_embeddings()
load_lexicon()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:8711", "https://localhost:8711", "https://www.amiens.fr"],
  allow_credentials=True,
  allow_methods=["POST"],
  allow_headers=["*"]
)


@app.post("/rag-assistant", response_model=AssistantResponse)
def rag_assistant_endpoint(payload: AssistantRequest):
  lexicon_matches = match_lexicon_entries(payload.question, payload.normalized_question)
  expanded_question = expand_query_with_lexicon(payload.question or "", lexicon_matches)

  incoming_segments = payload.rag_results or []
  rag_results: List[RagSegment] = []
  for item in incoming_segments:
    if isinstance(item, RagSegment):
      rag_results.append(item)
    elif isinstance(item, dict):
      rag_results.append(RagSegment(**item))
    else:
      # fallback : tente conversion via dict
      if hasattr(RagSegment, "model_validate"):
        rag_results.append(RagSegment.model_validate(item))  # type: ignore[attr-defined]
      else:
        rag_results.append(RagSegment.parse_obj(item))

  if not rag_results:
    fallback_query = expanded_question or payload.question
    fallback_segments = semantic_search(fallback_query, lexicon_matches, top_k=5, min_score=0.25)
    for score, meta in fallback_segments:
      rag_results.append(
        RagSegment(
          label=meta.get("label") or meta.get("source"),
          url=meta.get("url"),
          score=score,
          excerpt=(meta.get("content") or "")[:400],
          content=meta.get("content"),
        )
      )

  user_snippet = extract_user_snippet(payload.question)
  if user_snippet and not any(seg.custom_id == "U" for seg in rag_results):
    max_score = max((seg.score or 0.0) for seg in rag_results) if rag_results else 0.0
    rag_results.insert(
      0,
      RagSegment(
        label="Contribution utilisateur",
        score=max_score + CURRENCY_BONUS,
        excerpt=user_snippet[:400],
        content=user_snippet,
        custom_id="U",
      )
    )

  apply_currency_bonus(payload.question, payload.normalized_question, rag_results)
  apply_lexicon_bonus(rag_results, lexicon_matches)

  try:
    debug_scores = sorted(
      (
        (
          float(seg.score) if seg.score is not None else 0.0,
          seg.label or getattr(seg, "source", None) or seg.custom_id or "Segment",
          seg.custom_id or "",
        )
        for seg in rag_results
      ),
      key=lambda entry: entry[0],
      reverse=True,
    )[:5]
    if lexicon_matches:
      matched_terms = [entry.get("terme_usager") for entry in lexicon_matches]
      print(f"[RAG DEBUG] Question: {payload.question!r} (lexique: {matched_terms}) → {debug_scores}")
    else:
      print(f"[RAG DEBUG] Question: {payload.question!r} → {debug_scores}")
  except Exception as exc:
    print(f"[RAG DEBUG] Impossible d'afficher les scores: {exc}")

  intent_label = payload.intent_label
  intent_weight = payload.intent_weight
  if intent_label is None or intent_weight is None:
    intent_label, intent_weight = detect_user_intention(payload.question, payload.normalized_question)

  conversation_raw = list(payload.conversation or [])
  conversation: List[ConversationTurn] = []
  for entry in conversation_raw:
    if isinstance(entry, ConversationTurn):
      conversation.append(entry)
    elif isinstance(entry, dict):
      role = entry.get("role", "assistant")
      content = entry.get("content", "")
      conversation.append(ConversationTurn(role=role, content=content))

  summary_entries: List[str] = []
  for ref, seg in compute_segment_refs(rag_results):
    snippet = (seg.excerpt or seg.content or "").replace("\n", " ")
    snippet = snippet[:160]
    summary_entries.append(f"#{ref}: {seg.label or getattr(seg, 'source', None) or 'Segment'} — {snippet}")
  if summary_entries:
    memo_text = " | ".join(summary_entries[:5])
    conversation.append(ConversationTurn(role="assistant", content=f"Mémo RAG actuel : {memo_text}"))

  enriched_payload = payload.model_copy()
  enriched_payload.rag_results = rag_results
  enriched_payload.conversation = conversation[-12:]
  enriched_payload.intent_label = intent_label
  enriched_payload.intent_weight = intent_weight

  prompt = build_prompt(enriched_payload)
  result = call_model(prompt)

  alignment = result.get("alignment") or {}
  response = AssistantResponse(
    answer_html=result.get("answer_html", "<p>(Réponse indisponible)</p>"),
    answer_text=result.get("answer_text"),
    follow_up_question=result.get("follow_up_question"),
    alignment=AlignmentPayload(
      status=alignment.get("status", "info"),
      label=alignment.get("label", "Analyse RAG"),
      summary=alignment.get("summary", "Alignement non précisée."),
    ),
    sources=result.get("sources", []),
  )
  return response


if __name__ == "__main__":
  uvicorn.run("rag_assistant_server:app", host="0.0.0.0", port=8711)
