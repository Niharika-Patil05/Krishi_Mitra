"""Central settings: paths, model names, retrieval knobs, language codes, secrets.

Everything tunable lives here so the viva answer to "where do I change X?" is one file.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# --- Paths -----------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
INDEX_DIR = ROOT / "data" / "index"
SOURCES_CSV = ROOT / "data" / "sources.csv"
FAISS_PATH = INDEX_DIR / "faiss.index"
CHUNKS_PATH = INDEX_DIR / "chunks.jsonl"
DEMO_CACHE_PATH = ROOT / "demo_cache.json"

# --- Embeddings (runs locally; small enough for Streamlit Cloud) ------------
EMBED_MODEL = "intfloat/multilingual-e5-small"
QUERY_PREFIX = "query: "      # required by the e5 model card
PASSAGE_PREFIX = "passage: "  # required by the e5 model card

# --- Chunking ---------------------------------------------------------------
CHUNK_SIZE = 800      # characters
CHUNK_OVERLAP = 150   # characters
MIN_PAGE_CHARS = 50   # skip covers / blank pages

# --- Retrieval --------------------------------------------------------------
TOP_K = 8
SCORE_THRESHOLD = 0.84  # tuned on eval/questions.csv: keeps 100% of in-scope, refuses 80% of out-of-scope before any LLM call

# --- Languages (UI label -> Sarvam code; codes verified against docs.sarvam.ai)
LANGUAGES = {"मराठी": "mr-IN", "हिंदी": "hi-IN", "English": "en-IN"}
DEFAULT_LANGUAGE = "मराठी"

# --- LLM (model IDs verified against docs.sarvam.ai / console.groq.com/docs) --
SARVAM_LLM_MODEL = "sarvam-105b"          # V1 chat route; "sarvam-m" is deprecated
GROQ_LLM_MODEL = "llama-3.3-70b-versatile"
LLM_MAX_TOKENS = 1024                     # reasoning is off, so this is all answer
LLM_TIMEOUT_S = 20
LLM_TEMPERATURE = 0.2

# --- Speech (Sarvam; IDs verified against docs.sarvam.ai) --------------------
STT_MODEL = "saaras:v4"       # recommended model; default mode = plain transcription
TTS_MODEL = "bulbul:v3"       # stable; v4-flash is newer but speakers differ
TTS_SPEAKER = "shubh"         # documented default voice for v3
TTS_MAX_CHARS = 2000          # API limit is 2500 for v3; keep a safety margin
SPEECH_TIMEOUT_S = 30

KCC_NUMBER = "1800-180-1551"


def load_secrets() -> None:
    """Load .env for local runs. On Streamlit Cloud, keys come from st.secrets."""
    load_dotenv(ROOT / ".env")


def get_secret(name: str) -> str | None:
    """Return a key from st.secrets, falling back to env vars / .env."""
    try:
        import streamlit as st
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass  # streamlit missing or no secrets file: fall through to env
    load_secrets()
    return os.getenv(name)

# Shown as buttons in the UI; also used to pre-compute demo_cache.json
EXAMPLES = ["द्राक्षावरील भुरी रोगासाठी काय उपाय करावा?", "हळदीची लागवड कधी करावी?",
            "पीएम-किसान योजनेत किती रक्कम मिळते?", "हळदीवरील कंदकुज रोग कसा टाळावा?",
            "कोल्हापूर भागात ऊस लागवड कोणत्या महिन्यात करावी?", "What are the improved turmeric varieties?"]
