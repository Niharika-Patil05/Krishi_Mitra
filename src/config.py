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
TOP_K = 5
SCORE_THRESHOLD = 0.75  # starting value; tuned in Milestone 6 using eval

# --- Languages (UI label -> Sarvam code). To be verified against docs in M3/M4.
LANGUAGES = {"मराठी": "mr-IN", "हिंदी": "hi-IN", "English": "en-IN"}
DEFAULT_LANGUAGE = "मराठी"

# --- LLM / speech: model IDs are filled in after checking official docs ------
LLM_TIMEOUT_S = 20
LLM_TEMPERATURE = 0.2

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
