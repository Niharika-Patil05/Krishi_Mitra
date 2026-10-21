"""Krishi Mitra - Streamlit UI. All logic lives in src/; this file only draws and wires."""
import logging
import time

import streamlit as st

from src import config, pipeline, speech
from src.config import EXAMPLES

logging.basicConfig(level=logging.INFO)
st.set_page_config(page_title="कृषी मित्र — Krishi Mitra", page_icon="🌾")

CROPS = {"सर्व / All": None, "ऊस Sugarcane": "sugarcane", "द्राक्ष Grapes": "grapes",
         "हळद Turmeric": "turmeric", "योजना Schemes": "scheme"}


@st.cache_resource(show_spinner="माहिती भांडार लोड होत आहे...")
def get_retriever():
    """Load embedding model + FAISS index once per server process (not per click)."""
    from src.retriever import Retriever
    return Retriever()


def run_query(question: str, audio_bytes: bytes | None, lang: str, crop: str | None) -> None:
    """Do STT (if voice), run the pipeline, fall back to cache on failure; store in session."""
    result, transcript, t0 = None, None, time.perf_counter()
    try:
        if not question.strip() and audio_bytes:
            with st.spinner("आवाज ऐकत आहे..."):
                # "unknown" = auto-detect, so a farmer may speak Marathi/Hindi/English freely
                question = transcript = speech.stt(audio_bytes, "unknown")
        if not question.strip():
            st.session_state.result = {"error": "कृपया प्रश्न लिहा किंवा बोला. / Please type or speak a question."}
            return
        with st.spinner("उत्तर शोधत आहे..."):
            result = pipeline.ask(question, lang, get_retriever(), crop)
    except FileNotFoundError:
        st.session_state.result = {"error": "Index not found. Run `python -m src.ingest` first."}
        return
    except Exception as e:  # never show a stack trace to the user
        logging.exception("query failed: %s", e)
        result = pipeline.cached_answer(question, lang)
        if result is None:
            st.session_state.result = {
                "error": f"सेवा सध्या उपलब्ध नाही, कृपया थोड्या वेळाने प्रयत्न करा. "
                         f"/ Service busy, please retry. Kisan Call Centre: {config.KCC_NUMBER}"}
            return
    result.update(question=question, transcript=transcript, total=time.perf_counter() - t0)
    st.session_state.result = result


def show_result(r: dict) -> None:
    if "error" in r:
        st.error(r["error"])
        return
    if r.get("transcript"):
        st.info(f"🎤 {r['transcript']}")
    if r["not_found"]:
        st.warning(r["answer"])
    else:
        st.markdown(r["answer"])
    if r.get("cached"):
        st.caption("🗂️ cached answer (offline demo mode)")
    if r.get("audio"):
        st.audio(r["audio"], format="audio/wav")
    parts = [f"⏱ {r['total']:.1f}s", f"LLM: {r['provider']}"]
    st.caption(" · ".join(parts))
    if r["sources"]:
        with st.expander("स्रोत / Sources"):
            for i, s in enumerate(r["sources"], 1):
                st.markdown(f"**[{i}] {s['title']}** — {s['publisher']}, page {s['page']}"
                            + (f" · [link]({s['url']})" if s["url"].startswith("http") else ""))
                st.caption(s["text"][:300] + "…")


# ---------------- Sidebar ----------------
with st.sidebar:
    lang_label = st.selectbox("उत्तराची भाषा / Answer language", list(config.LANGUAGES))
    crop_label = st.selectbox("पीक / Crop", list(CROPS))
    with st.expander("About & Limitations"):
        st.markdown(
            "- Answers come only from ICAR / government / university documents.\n"
            "- If the answer is not in them, the app says so — it does not guess.\n"
            "- Your voice is sent to Sarvam AI for transcription; nothing is stored by this app.\n"
            "- Speech recognition may struggle with strong dialects or noise.\n"
            "- Not a replacement for your agriculture officer or KVK. "
            f"Kisan Call Centre: {config.KCC_NUMBER}")
lang, crop = config.LANGUAGES[lang_label], CROPS[crop_label]

# ---------------- Main ----------------
st.title("🌾 कृषी मित्र — Krishi Mitra")
st.write("ऊस, द्राक्ष आणि हळद पिकांसाठी विश्वासार्ह सरकारी/ICAR स्रोतांवर आधारित मराठी आवाज-सल्लागार.")

st.session_state.setdefault("q", "")


def use_example(text: str) -> None:
    st.session_state.q = text
    st.session_state.go = True


st.caption("उदाहरणे / Examples")
for i, ex in enumerate(EXAMPLES):
    st.button(ex, key=f"ex{i}", on_click=use_example, args=(ex,), width="stretch")

st.text_input("तुमचा प्रश्न लिहा / Type your question", key="q")
audio = st.audio_input("किंवा बोला / Or speak")
clicked = st.button("विचारा / Ask", type="primary")

if clicked or st.session_state.pop("go", False):
    run_query(st.session_state.q, audio.getvalue() if audio else None, lang, crop)

if "result" in st.session_state:
    show_result(st.session_state.result)
