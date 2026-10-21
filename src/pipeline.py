"""The whole question -> answer flow in one function, plus the demo-cache fallback."""
import difflib
import json
import logging
import time

from src import config, llm, prompts, speech
from src.retriever import Retriever

log = logging.getLogger("krishi.pipeline")


def ask(question: str, lang_code: str, retriever: Retriever, crop: str | None = None,
        with_audio: bool = True) -> dict:
    """Run the RAG pipeline. Raises RuntimeError if the LLM is unreachable (app then tries the cache).

    Returns: answer, sources (hits), audio (WAV bytes or None), provider, not_found, timings (s).
    """
    t = {}
    clock = time.perf_counter

    # 1. Rewrite to English: e5 retrieval works best with an English query over English PDFs
    t0 = clock()
    english_query, p_rewrite = llm.rewrite_to_english(question)
    t["rewrite"] = clock() - t0

    # 2. Retrieve (crop filter always keeps "scheme" documents)
    t0 = clock()
    hits = retriever.search(english_query, k=config.TOP_K, crop_filter=crop)
    t["retrieve"] = clock() - t0
    base = {"english_query": english_query, "sources": hits, "audio": None,
            "provider": p_rewrite, "cached": False, "timings": t}

    # 3. Refuse without calling the LLM when nothing relevant was found
    if not hits or hits[0]["score"] < config.SCORE_THRESHOLD:
        return {**base, "answer": prompts.NOT_FOUND[lang_code], "not_found": True}

    # 4. Grounded answer
    t0 = clock()
    answer, provider = llm.generate_answer(question, hits, lang_code)
    t["answer"] = clock() - t0

    # 5. Speech is a bonus: if it fails the text answer must still show
    audio = None
    t0 = clock()
    try:
        if with_audio:
            audio = speech.tts(prompts.strip_citations(answer), lang_code)
    except Exception as e:
        log.warning("TTS failed: %s", e)
    t["tts"] = clock() - t0
    return {**base, "answer": answer, "audio": audio, "provider": provider, "not_found": False}


def _normalise(s: str) -> str:
    return " ".join(s.lower().replace("?", " ").replace("।", " ").split())


def cached_answer(question: str, lang_code: str, cutoff: float = 0.85) -> dict | None:
    """Demo safety net: find a pre-computed answer for an (almost) identical question."""
    try:
        with open(config.DEMO_CACHE_PATH, encoding="utf-8") as f:
            cache = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    entries = {_normalise(e["question"]): e for e in cache if e["lang"] == lang_code}
    match = difflib.get_close_matches(_normalise(question), list(entries), n=1, cutoff=cutoff)
    if not match:
        return None
    e = entries[match[0]]
    return {"answer": e["answer"], "sources": e["sources"], "audio": None, "provider": "cache",
            "cached": True, "not_found": False, "english_query": "", "timings": {}}
