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
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

try:
  from anthropic import Anthropic
except ImportError as exc:
  raise SystemExit("Install anthropic package: pip install anthropic fastapi uvicorn") from exc

# Import système adresses dynamique
try:
  from tools.address_fetcher import get_address_for_lieu, extract_address_from_text
except ImportError:
  # Fallback si le module n'est pas disponible
  def get_address_for_lieu(*args, **kwargs):
    return None
  def extract_address_from_text(*args, **kwargs):
    return None

# Modèle Claude : support Haiku (plus rapide) ou Sonnet (meilleure qualité)
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-3-7-sonnet-20250219")
# Options: "claude-3-7-sonnet-20250219" (qualité) ou "claude-3-5-haiku-20241022" (rapidité)

ASSISTANT_SYSTEM_PROMPT = """
Tu es l'assistant officiel "Amiens".
Analyse chaque question en tenant compte :
- des segments RAG numérotés (#1, #2, …) et de leur résumé (les numéros sont pour ton usage interne uniquement),
- du mémo de conversation (ce qui a déjà été répondu),
- des données structurées fournies (listes RPE, lieux, etc.) si présentes.

IMPORTANT : Ne mentionne JAMAIS les numéros de segments (#1, #2, #3) dans tes réponses à l'utilisateur. Utilise plutôt les titres ou sources des segments.

Style :
- Réponse HTML très courte : intro ≤ 3 phrases, puis <h3>Synthèse</h3> (1 phrase). Évite listes et répétitions inutiles.
- NE PAS inclure de section "Ouverture" dans le HTML : les questions de suivi sont gérées séparément via follow_up_question.
- Si une information a déjà été fournie, renvoie au mémo plutôt que la détailler à nouveau. 
- ⚠️ INTERDICTION ABSOLUE : NE JAMAIS mentionner les numéros de segments (#1, #2, #3, segments #1, etc.) dans tes réponses à l'utilisateur (answer_html). Utilise uniquement les titres ou sources des segments.
- Cite au moins une source cliquable si disponible.
- Dans `alignment.summary`, indique clairement les segments exploités - mais ces numéros ne doivent JAMAIS apparaître dans answer_html.
- Si une question géographique ("où", "adresse", "localisation") ne trouve pas d'adresse dans les segments, redirige vers la carte géographique d'Amiens Métropole : https://geo.amiens-metropole.com/adws/app/523da8c6-5dbc-11ec-9790-3dc5639e7001/index.html
- Si des données structurées sont fournies (section "DONNÉES STRUCTURÉES"), tu DOIS les inclure dans ta réponse de manière claire et structurée.

IMPORTANT - Format des "follow_up_question" (ouvertures) :
Les questions de suivi doivent être formulées COMME UN UTILISATEUR les poserait, pas comme l'assistant.
- ❌ MAUVAIS : "Souhaitez-vous connaître votre quotient familial ?"
- ❌ MAUVAIS : "Pouvez-vous me préciser le nombre de jours ?"
- ❌ MAUVAIS : "Je quel est votre quotient familial pour que je puisse vous indiquer le tarif exact ?"
- ✅ BON : "Quel est mon quotient familial ?"
- ✅ BON : "Combien de jours par semaine ?"
- ✅ BON : "Où se trouve cette école ?"

Règles pour les ouvertures :
- Question courte et directe (max 10 mots)
- Formulation à la première personne (je/mon/mes/mon enfant)
- Pas de formules de politesse ("Souhaitez-vous", "Pouvez-vous", "Je souhaite")
- Pas de préfixe "Je " en début de phrase
- Utilise "mon/mes" au lieu de "votre/vos" quand pertinent

CRITÈRE ESSENTIEL - Ouvertures basées sur RAG :
La question d'ouverture DOIT porter sur un sujet dont la réponse est disponible dans :
- Les segments RAG fournis (référencés en interne par #1, #2, #3, etc.)
- Les données structurées fournies (tarifs, lieux, RPE, écoles)

Analyse les segments RAG pour identifier :
- Informations partielles qui méritent un approfondissement
- Sujets connexes mentionnés mais non détaillés
- Données structurées disponibles (tarifs → quotient familial, lieux → adresse, etc.)

Exemples d'ouvertures valides (réponse dans RAG) :
- Si segments parlent de tarifs → "Quel est mon quotient familial ?"
- Si segments parlent de lieux → "Où se trouve [lieu mentionné] ?"
- Si segments parlent d'inscription → "Quels documents sont nécessaires ?"
- Si segments parlent de RPE → "Quel est le contact de mon RPE ?"

À ÉVITER : Questions sur des sujets absents des segments RAG ou données structurées.

Ne mentionne rien en dehors des segments ET des données structurées fournies.

Réponse obligatoire (JSON strict) :
{
  "answer_html": "...",
  "answer_text": "...",
  "follow_up_question": "...",
  "alignment": {"status": "...", "label": "...", "summary": "..."},
  "sources": [{"title": "...", "url": "...", "confidence": "..."}]
}
"""

load_dotenv()
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
if not anthropic_key:
  raise SystemExit("ANTHROPIC_API_KEY non défini. Ajoute la clé dans .env")

client = Anthropic(api_key=anthropic_key)

EMBED_MODEL_NAME = os.environ.get("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Détection automatique corpus généralisé si existe
ML_DATA_DIR = Path(__file__).resolve().parent.parent / "ML" / "data"
EMBEDDINGS_GENERALIZED_PATH = ML_DATA_DIR / "corpus_embeddings_generalized.npy"
METADATA_GENERALIZED_PATH = ML_DATA_DIR / "corpus_metadata_generalized.json"
EMBEDDINGS_STANDARD_PATH = ML_DATA_DIR / "corpus_embeddings.npy"
METADATA_STANDARD_PATH = ML_DATA_DIR / "corpus_metadata.json"

# Utiliser corpus généralisé si disponible, sinon fallback sur standard
if EMBEDDINGS_GENERALIZED_PATH.exists() and METADATA_GENERALIZED_PATH.exists():
  EMBEDDINGS_PATH = os.environ.get("EMBEDDINGS_PATH", EMBEDDINGS_GENERALIZED_PATH)
  METADATA_PATH = os.environ.get("METADATA_PATH", METADATA_GENERALIZED_PATH)
  print("✅ Corpus généralisé détecté et utilisé")
else:
  EMBEDDINGS_PATH = Path(
    os.environ.get("EMBEDDINGS_PATH", EMBEDDINGS_STANDARD_PATH)
  )
  METADATA_PATH = Path(
    os.environ.get("METADATA_PATH", METADATA_STANDARD_PATH)
  )
  print("📂 Utilisation du corpus standard")
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
rpe_data: Optional[Dict[str, Any]] = None
lieux_data: Optional[Dict[str, Any]] = None
tarifs_data: Optional[Dict[str, Any]] = None
ecoles_data: Optional[Dict[str, Any]] = None
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
  from whoosh.lang.snowball.french import FrenchStemmer
except ImportError:
  scoring = None
  StemmingAnalyzer = None
  Schema = None
  create_in = None
  open_dir = None
  MultifieldParser = None
  FrenchStemmer = None

# Import cache (même répertoire)
try:
  from .cache import get_cache, cache_stats
except ImportError:
  try:
    from cache import get_cache, cache_stats
  except ImportError:
    # Fallback si cache.py n'est pas disponible
    def get_cache(*args, **kwargs):
      return None
    def cache_stats():
      return {"total_entries": 0, "active_entries": 0}


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


def load_structured_data():
  """Charge les données structurées (RPE, lieux, tarifs, écoles)."""
  global rpe_data, lieux_data, tarifs_data, ecoles_data
  data_dir = Path(__file__).resolve().parent.parent / "ML" / "data"
  
  # Charger données RPE
  rpe_path = data_dir / "rpe_contacts.json"
  if rpe_path.exists():
    try:
      with open(rpe_path, "r", encoding="utf-8") as f:
        rpe_data = json.load(f)
      print(f"✅ Données RPE chargées ({len(rpe_data.get('rpe_list', []))} RPE)")
    except Exception as e:
      print(f"⚠️ Impossible de charger les données RPE: {e}")
      rpe_data = None
  else:
    rpe_data = None
  
  # Charger données lieux
  lieux_path = data_dir / "lieux_importants.json"
  if lieux_path.exists():
    try:
      with open(lieux_path, "r", encoding="utf-8") as f:
        lieux_data = json.load(f)
      print(f"✅ Données lieux chargées ({len(lieux_data.get('lieux', []))} lieux)")
    except Exception as e:
      print(f"⚠️ Impossible de charger les données lieux: {e}")
      lieux_data = None
  else:
    lieux_data = None
  
  # Charger données tarifs
  tarifs_path = data_dir / "tarifs_2024_2025.json"
  if tarifs_path.exists():
    try:
      with open(tarifs_path, "r", encoding="utf-8") as f:
        tarifs_data = json.load(f)
      total = tarifs_data.get("total_tables", 0)
      print(f"✅ Données tarifs chargées ({total} tableaux)")
    except Exception as e:
      print(f"⚠️ Impossible de charger les données tarifs: {e}")
      tarifs_data = None
  else:
    tarifs_data = None
  
  # Charger données écoles
  ecoles_path = data_dir / "ecoles_amiens.json"
  if ecoles_path.exists():
    try:
      with open(ecoles_path, "r", encoding="utf-8") as f:
        ecoles_data = json.load(f)
      total = ecoles_data.get("total", 0)
      print(f"✅ Données écoles chargées ({total} écoles)")
    except Exception as e:
      print(f"⚠️ Impossible de charger les données écoles: {e}")
      ecoles_data = None
  else:
    ecoles_data = None


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

  # Injecter données structurées selon le contexte
  question_lower = (payload.question or "").lower()
  normalized_lower = (payload.normalized_question or "").lower()
  question_text = question_lower + " " + normalized_lower
  
  # Détection améliorée : utiliser lexique au lieu de liste en dur
  lexicon_matches = match_lexicon_entries(payload.question, payload.normalized_question)
  rpe_relevant = any(
    entry.get("terme_usager") in ["inscription", "inscrire", "crèche", "relais"] 
    for entry in lexicon_matches
  ) or any(term in question_text for term in ["rpe", "relais petite enfance"])
  
  # Données RPE si question concerne les RPE/crèche/inscription
  if rpe_data and rpe_relevant:
    lines.append("\n=== DONNÉES STRUCTURÉES : LISTE DES RPE ===\n")
    lines.append("Tu DOIS inclure cette liste complète dans ta réponse si la question concerne les RPE :\n")
    for rpe in rpe_data.get("rpe_list", []):
      lines.append(f"- {rpe['nom']} : Secteurs {', '.join(rpe['secteurs'][:3])}... | Adresse: {rpe['adresse']} | Tél: {rpe['telephone']} | Email: {rpe['email']}\n")
    lines.append("\n")
  
  # Données tarifs si question tarifaire
  if tarifs_data and any(term in question_text for term in ["tarif", "prix", "coût", "€", "cantine", "restauration", "périscolaire", "mercredi", "alsh"]):
    lines.append("\n=== DONNÉES STRUCTURÉES : TABLEAUX TARIFAIRES ===\n")
    lines.append("Tu DOIS inclure les tableaux tarifaires pertinents dans ta réponse :\n")
    tarifs_by_type = tarifs_data.get("tarifs_by_type", {})
    if "cantine" in tarifs_by_type and any(t in question_text for t in ["cantine", "restauration", "repas"]):
      for table_html in tarifs_by_type["cantine"][:2]:  # Max 2 tableaux
        lines.append(table_html + "\n")
    if "periscolaire" in tarifs_by_type and "périscolaire" in question_text:
      for table_html in tarifs_by_type["periscolaire"][:2]:
        lines.append(table_html + "\n")
    if "mercredi" in tarifs_by_type and "mercredi" in question_text:
      for table_html in tarifs_by_type["mercredi"][:1]:
        lines.append(table_html + "\n")
    lines.append("\n")
  
  # Données lieux : détection améliorée avec système adresses dynamique
  question_geographique = any(term in question_text for term in ["où", "adresse", "localisation", "se trouve", "situé", "localiser", "emplacement"])
  
  # Détection spéciale pour crèches
  is_creche_question = any(term in question_text for term in ["creche", "crèche", "crèches", "creches"]) and question_geographique
  
  # Détecter les lieux mentionnés dans la question
  lieux_mentionnes = []
  
  # 0. Si question sur crèches, ajouter "crèches" comme lieu à chercher
  if is_creche_question:
    lieux_mentionnes.append({
      "nom": "crèches",
      "adresse": None,
      "description": "Crèches municipales d'Amiens",
      "source": "detection_creche"
    })
  
  # 1. Chercher dans lieux_data
  if lieux_data:
    for lieu in lieux_data.get("lieux", []):
      lieu_nom_lower = lieu["nom"].lower()
      if lieu_nom_lower in question_text:
        lieux_mentionnes.append({
          "nom": lieu["nom"],
          "adresse": lieu.get("adresse"),
          "description": lieu.get("description", ""),
          "source": "lieux_data"
        })
  
  # 2. Chercher des patterns de noms de lieux (majuscules, noms propres)
  # Patterns pour détecter des noms de lieux potentiels
  lieu_patterns = [
    r"\b(?:espace|centre|salle|théâtre|médiathèque|bibliothèque|gymnase|stade|piscine|école|mairie|hôtel de ville)\s+[A-Z][a-zéèêàâôùûç]+(?:\s+[A-Z][a-zéèêàâôùûç]+)*",
    r"\b[A-Z][a-zéèêàâôùûç]+\s+(?:de|du|des|d')\s+[A-Z][a-zéèêàâôùûç]+",
  ]
  
  for pattern in lieu_patterns:
    matches = re.findall(pattern, payload.question or "", re.IGNORECASE)
    for match in matches:
      match_lower = match.lower()
      # Éviter les doublons et les mots trop courts
      if len(match) > 5 and not any(l["nom"].lower() == match_lower for l in lieux_mentionnes):
        lieux_mentionnes.append({
          "nom": match,
          "adresse": None,
          "description": "",
          "source": "detection"
        })
  
  # 3. Si question géographique et lieux détectés, chercher/adapter les adresses
  if question_geographique and lieux_mentionnes:
    lines.append("\n=== DONNÉES STRUCTURÉES : LIEUX ET ADRESSES ===\n")
    carte_geo_url = "https://geo.amiens-metropole.com/adws/app/523da8c6-5dbc-11ec-9790-3dc5639e7001/index.html"
    adresses_trouvees = False
    
    for lieu_info in lieux_mentionnes:
      lieu_nom = lieu_info["nom"]
      adresse = lieu_info.get("adresse")
      
      # Si pas d'adresse dans lieux_data, chercher dans segments RAG puis OSM
      if not adresse:
        # Vérifier d'abord dans les segments RAG
        adresse_trouvee = False
        if payload.rag_results:
          for seg in payload.rag_results:
            content = (seg.content or seg.excerpt or "").lower()
            if lieu_nom.lower() in content:
              extracted = extract_address_from_text(seg.content or seg.excerpt or "")
              if extracted:
                adresse = extracted
                adresse_trouvee = True
                break
        
        # Si toujours pas trouvé, utiliser address_fetcher (cherche dans RAG puis OSM)
        if not adresse_trouvee:
          fetched_address = get_address_for_lieu(
            lieu_nom,
            segments_rag=payload.rag_results,
            city="Amiens"
          )
          if fetched_address:
            adresse = fetched_address
      
      # Injecter dans le prompt
      if adresse:
        desc = f" - {lieu_info['description']}" if lieu_info.get("description") else ""
        lines.append(f"- {lieu_nom} : {adresse}{desc}\n")
        adresses_trouvees = True
      else:
        # Même sans adresse, mentionner le lieu si détecté
        desc = f" - {lieu_info['description']}" if lieu_info.get("description") else ""
        lines.append(f"- {lieu_nom}{desc} (adresse à rechercher)\n")
    
    # Si aucune adresse trouvée pour une question "où", rediriger vers la carte
    if not adresses_trouvees and question_geographique:
      if is_creche_question:
        lines.append(f"\n⚠️ IMPORTANT : Aucune adresse trouvée pour les crèches. Tu DOIS rediriger l'utilisateur vers la carte géographique d'Amiens Métropole.\n")
        lines.append(f"Format de réponse OBLIGATOIRE : 'Pour localiser les crèches et leurs adresses à Amiens, consultez la carte interactive d'Amiens Métropole : {carte_geo_url}'\n")
        lines.append("Tu dois inclure le lien cliquable dans ta réponse HTML.\n")
      else:
        lines.append(f"\n⚠️ IMPORTANT : Si aucune adresse n'est trouvée pour les lieux demandés, tu DOIS inclure un lien vers la carte géographique d'Amiens Métropole : {carte_geo_url}\n")
        lines.append("Format de réponse : 'Pour localiser [lieu] et son adresse, consultez la carte interactive : [lien vers la carte]'\n")
    lines.append("\n")
  
  # Données écoles si question sur écoles/établissements
  if ecoles_data and any(term in question_text for term in ["école", "établissement", "liste", "contact", "adresse école"]):
    lines.append("\n=== DONNÉES STRUCTURÉES : ÉCOLES D'AMIENS ===\n")
    lines.append(f"Total: {ecoles_data.get('total', 0)} écoles disponibles.\n")
    lines.append("Si la question demande une liste ou des contacts d'écoles, tu peux mentionner qu'il y a 78 écoles publiques réparties en 5 secteurs.\n")
    lines.append("Pour des informations détaillées par école, oriente vers la carte interactive ou les mairies de secteur.\n")
    lines.append("\n")

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
  try:
    # Charger les embeddings pré-calculés (même sans sentence-transformers)
    corpus_embeddings = np.load(EMBEDDINGS_PATH)
    with METADATA_PATH.open(encoding="utf-8") as f:
      corpus_metadata = json.load(f)
    print(f"✅ Embeddings chargés ({corpus_embeddings.shape[0]} segments).")
    
    # Charger le modèle seulement si sentence-transformers est disponible
    if SentenceTransformer is not None:
      embed_model = SentenceTransformer(EMBED_MODEL_NAME)
      print("✅ Modèle sentence-transformers chargé (recherche sémantique activée).")
    else:
      embed_model = None
      print("⚠️ sentence-transformers non disponible (recherche Whoosh uniquement).")

    if Schema and StemmingAnalyzer and FrenchStemmer:
      # Utilisation du stemmer français (Snowball) au lieu du Porter anglais
      schema = Schema(
        id=ID(stored=True, unique=True),
        label=TEXT(stored=True),
        content=TEXT(analyzer=StemmingAnalyzer(minsize=2, stemfn=FrenchStemmer().stem), stored=False),
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
      # Optimisation : réduire de top_k * 4 à top_k * 2 pour meilleure performance
      hits = searcher.search(query, limit=top_k * 2)
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
        # Rééquilibrage du poids BM25 (avec stemmer français maintenant)
        bm25_weight = score * 1.0
        if normalized_terms:
          normalized_content = _normalize(meta.get("content") or "")
          term_hits = sum(1 for term in normalized_terms if term and term in normalized_content)
          if term_hits:
            bm25_weight += term_hits * 2.5
        weights[doc_id] = weights.get(doc_id, 0.0) + bm25_weight

  if corpus_embeddings is not None and embed_model is not None:
    query_vec = embed_model.encode([question], normalize_embeddings=True)[0]
    scores = corpus_embeddings @ query_vec
    # Optimisation : réduire de top_k * 4 à top_k * 2 pour meilleure performance
    best_idx = np.argsort(-scores)[: top_k * 2]
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
      # Augmentation du poids sémantique (cosine similarity)
      cosine_weight = score * 0.6
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
  try:
    response = client.messages.create(
      model=CLAUDE_MODEL,
      max_tokens=900,
      temperature=0.2,
      system=ASSISTANT_SYSTEM_PROMPT,
      messages=[{"role": "user", "content": prompt}],
      timeout=30.0,  # Timeout de 30 secondes pour l'API Claude (optimisé)
    )
  except Exception as e:
    print(f"❌ Erreur API Claude: {e}")
    raise HTTPException(status_code=502, detail=f"Erreur API Claude: {str(e)}")

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
load_structured_data()

app.add_middleware(
  CORSMiddleware,
  allow_origins=[
    "http://localhost:8711",
    "https://localhost:8711",
    "https://www.amiens.fr",
    os.environ.get("ALLOWED_ORIGIN", ""),  # Pour déploiement (Railway/Render)
  ],
  allow_credentials=True,
  allow_methods=["POST"],
  allow_headers=["*"]
)

# Compression Gzip pour réduire la latence
app.add_middleware(GZipMiddleware, minimum_size=1000)


def has_rag_answer(question: str, rag_results: List[RagSegment]) -> bool:
  """
  Vérifie si une question a une réponse potentielle dans les segments RAG.
  """
  if not question or not rag_results:
    return False
  
  # Extraire les mots-clés de la question (enlever mots vides)
  stop_words = {"quel", "quelle", "quels", "quelles", "est", "sont", "mon", "ma", "mes", "le", "la", "les", "un", "une", "des", "de", "du", "à", "pour", "avec", "dans", "sur", "par", "où", "comment", "quand", "combien"}
  question_lower = question.lower()
  question_words = [w for w in re.findall(r'\b\w+\b', question_lower) if w not in stop_words and len(w) > 2]
  
  if not question_words:
    return False
  
  # Vérifier si au moins 50% des mots-clés sont présents dans les segments
  for segment in rag_results:
    content = (segment.content or segment.excerpt or "").lower()
    matches = sum(1 for word in question_words if word in content)
    if matches >= len(question_words) * 0.5:  # Au moins 50% des mots-clés
      return True
  
  return False


def generate_followup_from_structured_data(
  question: str,
  rag_results: List[RagSegment],
  structured_data: Dict[str, Any]
) -> Optional[str]:
  """
  Génère une question d'ouverture alternative basée sur les données structurées disponibles.
  """
  question_lower = question.lower()
  
  # Analyser le contenu des segments pour identifier les sujets
  rag_content = " ".join([(seg.content or seg.excerpt or "").lower() for seg in rag_results[:3]])
  
  # Mapping basé sur les données structurées disponibles
  if structured_data.get("tarifs_data") and ("tarif" in question_lower or "prix" in question_lower or "coût" in question_lower):
    if "quotient" not in rag_content:
      return "Quel est mon quotient familial ?"
  
  if structured_data.get("lieux_data") and ("où" in question_lower or "adresse" in question_lower or "localisation" in question_lower):
    # Chercher un lieu mentionné dans les segments
    for seg in rag_results[:3]:
      content = (seg.content or seg.excerpt or "").lower()
      if "espace" in content or "école" in content or "crèche" in content:
        return "Où se trouve ce lieu ?"
  
  if structured_data.get("rpe_data") and ("rpe" in question_lower or "relais" in question_lower):
    if "contact" not in rag_content and "téléphone" not in rag_content:
      return "Quel est le contact de mon RPE ?"
  
  if structured_data.get("ecoles_data") and ("école" in question_lower or "scolaire" in question_lower):
    if "secteur" not in rag_content:
      return "Dans quel secteur se trouve cette école ?"
  
  # Fallback générique basé sur données disponibles
  if structured_data.get("tarifs_data"):
    return "Quels sont les tarifs détaillés ?"
  
  if structured_data.get("rpe_data"):
    return "Quels sont les contacts des RPE ?"
  
  return None


def clean_segment_references(html_text: str) -> str:
  """
  Nettoie les références aux numéros de segments (#1, #2, segment #3, etc.) du HTML.
  Ces numéros sont pour usage interne uniquement et ne doivent jamais apparaître dans answer_html.
  """
  if not html_text:
    return html_text

  # Patterns à nettoyer
  patterns = [
    r'\bsegments?\s*#\d+(?:\s*,\s*#\d+)*',  # "segment #1", "segments #1, #2"
    r'\b#\d+(?:\s*,\s*#\d+)*',              # "#1", "#1, #2, #3"
    r'\(\s*segments?\s*#\d+(?:\s*,\s*#\d+)*\s*\)',  # "(segment #1)"
    r'\[\s*segments?\s*#\d+(?:\s*,\s*#\d+)*\s*\]',  # "[segment #1]"
  ]

  cleaned = html_text
  for pattern in patterns:
    cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

  # Nettoyer les espaces multiples et parenthèses vides résultantes
  cleaned = re.sub(r'\s+', ' ', cleaned)
  cleaned = re.sub(r'\(\s*\)', '', cleaned)
  cleaned = re.sub(r'\[\s*\]', '', cleaned)

  return cleaned.strip()


def normalize_followup_question(question: Optional[str]) -> Optional[str]:
  """
  Normalise une question de suivi pour qu'elle soit formulée comme un utilisateur la poserait.
  Transforme les questions d'assistant en questions utilisateur directes.
  """
  if not question:
    return None
  
  # Nettoyer la question
  q = question.strip()
  if not q:
    return None
  
  # Enlever les préfixes "Je " en début de phrase (plusieurs variantes)
  q = re.sub(r'^Je\s+', '', q, flags=re.IGNORECASE)
  q = re.sub(r'^je\s+', '', q, flags=re.IGNORECASE)
  
  # Enlever les formules de politesse courantes
  patterns_to_remove = [
    r'^Souhaitez-vous\s+',
    r'^Pouvez-vous\s+',
    r'^Pourriez-vous\s+',
    r'^Voulez-vous\s+',
    r'^Je souhaite\s+',
    r'^Je voudrais\s+',
    r'^Je veux\s+',
    r'^Je dois\s+',
    r'^Souhaitez-vous que je\s+',
    r'^Pouvez-vous me\s+',
    r'^Pourriez-vous me\s+',
  ]
  
  for pattern in patterns_to_remove:
    q = re.sub(pattern, '', q, flags=re.IGNORECASE)
  
  # Enlever "me " qui reste parfois après "Pouvez-vous me"
  q = re.sub(r'^me\s+', '', q, flags=re.IGNORECASE)
  
  # Enlever "Je " qui peut rester après d'autres transformations
  # Faire plusieurs passes pour être sûr
  for _ in range(3):  # Plusieurs passes pour gérer les cas complexes
    q = re.sub(r'^Je\s+', '', q, flags=re.IGNORECASE)
    q = re.sub(r'^je\s+', '', q, flags=re.IGNORECASE)
  
  # Capitaliser la première lettre
  if q:
    q = q[0].upper() + q[1:] if len(q) > 1 else q.upper()
  
  # Remplacer "votre/vos" par "mon/mes" quand pertinent
  # Mais seulement si c'est clairement une question utilisateur
  q = re.sub(r'\bvotre\s+quotient\s+familial\b', 'mon quotient familial', q, flags=re.IGNORECASE)
  q = re.sub(r'\bvotre\s+enfant\b', 'mon enfant', q, flags=re.IGNORECASE)
  q = re.sub(r'\bvotre\s+situation\b', 'ma situation', q, flags=re.IGNORECASE)
  q = re.sub(r'\bvotre\s+tarif\b', 'mon tarif', q, flags=re.IGNORECASE)
  q = re.sub(r'\bvos\s+enfants\b', 'mes enfants', q, flags=re.IGNORECASE)
  
  # Enlever les phrases trop longues ou explicatives
  # Si la question contient "pour que je puisse", "afin de", etc., simplifier
  q = re.sub(r'\s+pour\s+que\s+je\s+puisse[^?]*', '', q, flags=re.IGNORECASE)
  q = re.sub(r'\s+afin\s+de[^?]*', '', q, flags=re.IGNORECASE)
  q = re.sub(r'\s+qui\s+s\'applique\s+à[^?]*', '', q, flags=re.IGNORECASE)
  
  # S'assurer qu'il y a un point d'interrogation
  if not q.endswith('?'):
    # Si la phrase se termine par un point, le remplacer par ?
    if q.endswith('.'):
      q = q[:-1] + '?'
    else:
      q = q + '?'
  
  # Nettoyer les espaces multiples
  q = re.sub(r'\s+', ' ', q).strip()
  
  # Limiter la longueur (max 80 caractères pour une question courte)
  if len(q) > 80:
    # Prendre la première phrase jusqu'au point d'interrogation
    match = re.match(r'^([^?]+)\?', q)
    if match:
      q = match.group(1).strip() + '?'
    else:
      q = q[:77] + '...?'
  
  return q if q else None


@app.post("/rag-assistant", response_model=AssistantResponse)
def rag_assistant_endpoint(payload: AssistantRequest):
  try:
    # Vérifier le cache avant de faire la recherche RAG
    cache = get_cache(ttl=3600)  # TTL de 1h par défaut
    cache_key = payload.question or payload.normalized_question or ""
    
    if cache and cache_key:
      cached_result = cache.get(cache_key)
      if cached_result is not None:
        print(f"[CACHE HIT] Question: {cache_key[:50]}...")
        # IMPORTANT: Nettoyer les segments même dans les réponses en cache
        if "answer_html" in cached_result:
          cached_result["answer_html"] = clean_segment_references(cached_result["answer_html"])
        if "alignment" in cached_result and "summary" in cached_result["alignment"]:
          cached_result["alignment"]["summary"] = clean_segment_references(cached_result["alignment"]["summary"])
        return AssistantResponse(**cached_result)
    
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
    
    # Normaliser la question de suivi pour qu'elle soit formulée comme un utilisateur
    raw_followup = result.get("follow_up_question")
    normalized_followup = normalize_followup_question(raw_followup)
    
    # Validation : vérifier que l'ouverture a une réponse dans le RAG
    if normalized_followup:
      if not has_rag_answer(normalized_followup, rag_results):
        # Fallback : générer une alternative depuis données structurées
        structured_data = {
          "tarifs_data": tarifs_data,
          "rpe_data": rpe_data,
          "lieux_data": lieux_data,
          "ecoles_data": ecoles_data,
        }
        alternative_followup = generate_followup_from_structured_data(
          payload.question or "",
          rag_results,
          structured_data
        )
        if alternative_followup:
          normalized_followup = normalize_followup_question(alternative_followup)
        else:
          # Si pas d'alternative, supprimer l'ouverture plutôt que proposer une question sans réponse
          normalized_followup = None
    
    # Nettoyer les références aux segments (#1, #2, etc.) de la réponse HTML ET du summary
    raw_answer_html = result.get("answer_html", "<p>(Réponse indisponible)</p>")
    cleaned_answer_html = clean_segment_references(raw_answer_html)

    # IMPORTANT: Nettoyer aussi alignment.summary qui s'affiche dans le badge
    raw_summary = alignment.get("summary", "Alignement non précisée.")
    cleaned_summary = clean_segment_references(raw_summary)

    response = AssistantResponse(
      answer_html=cleaned_answer_html,
      answer_text=result.get("answer_text"),
      follow_up_question=normalized_followup,
      alignment=AlignmentPayload(
        status=alignment.get("status", "info"),
        label=alignment.get("label", "Analyse RAG"),
        summary=cleaned_summary,
      ),
      sources=result.get("sources", []),
    )
    
    # Sauvegarder dans le cache
    if cache and cache_key:
      try:
        # Convertir response en dict pour le cache
        cache_value = response.model_dump() if hasattr(response, "model_dump") else response.dict()
        cache.set(cache_key, cache_value, ttl=3600)  # TTL de 1h
      except Exception as e:
        print(f"⚠️ Erreur lors de la sauvegarde dans le cache: {e}")
    
    return response
  except HTTPException:
    # Re-raise les HTTPException (déjà gérées)
    raise
  except Exception as e:
    # Capturer toutes les autres erreurs pour éviter les crashes
    import traceback
    error_trace = traceback.format_exc()
    print(f"❌ Erreur dans rag_assistant_endpoint: {e}")
    print(f"Traceback: {error_trace}")
    raise HTTPException(
      status_code=500,
      detail=f"Erreur serveur: {str(e)}"
    )


if __name__ == "__main__":
  import os
  # Port depuis variable d'environnement (pour Railway/Render) ou 8711 par défaut
  port = int(os.environ.get("PORT", 8711))
  ssl_keyfile = "localhost-key.pem"
  ssl_certfile = "localhost-cert.pem"
  if os.path.exists(ssl_keyfile) and os.path.exists(ssl_certfile):
    uvicorn.run(
      "rag_assistant_server:app",
      host="0.0.0.0",
      port=port,
      ssl_keyfile=ssl_keyfile,
      ssl_certfile=ssl_certfile,
      timeout_keep_alive=30,
      limit_concurrency=10
    )
  else:
    uvicorn.run(
      "rag_assistant_server:app",
      host="0.0.0.0",
      port=port,
      timeout_keep_alive=30,
      limit_concurrency=10
    )
