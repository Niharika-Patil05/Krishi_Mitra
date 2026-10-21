"""Krishi Mitra - Streamlit UI. All logic lives in src/; this file only draws and wires."""
import html
import logging
import re
import time

import streamlit as st

from src import config, pipeline, speech
from src.config import EXAMPLES

logging.basicConfig(level=logging.INFO)
st.set_page_config(page_title="कृषी मित्र — Krishi Mitra", page_icon="🌱", layout="centered")
st.markdown(f"<style>{(config.ROOT / 'assets' / 'style.css').read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True)

CROPS = {"सर्व पिके / All": None, "ऊस / Sugarcane": "sugarcane", "द्राक्ष / Grapes": "grapes",
         "हळद / Turmeric": "turmeric", "सरकारी योजना / Schemes": "scheme"}


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


def answer_html(text: str) -> str:
    """Escape the LLM text, turn '* ' lines into a list and [n] markers into small citation chips."""
    lines, items, out = html.escape(text).splitlines(), [], []

    def flush():
        if items:
            out.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
            items.clear()

    for ln in lines:
        m = re.match(r"^\s*[*\-•]\s+(.*)", ln)
        if m:
            items.append(m.group(1))
        elif ln.strip():
            flush()
            out.append(f"<p>{ln.strip()}</p>")
    flush()
    body = "".join(out)
    return re.sub(r"\[(\d+(?:\s*,\s*\d+)*)\]", lambda m: f'<span class="cite">{m.group(1)}</span>', body)


def show_result(r: dict) -> None:
    if "error" in r:
        st.error(r["error"])
        return
    if r.get("transcript"):
        st.markdown(f'<p class="heard">तुम्ही म्हणालात: <b>{html.escape(r["transcript"])}</b></p>', unsafe_allow_html=True)
    cls = "answer notfound" if r["not_found"] else "answer"
    st.markdown(f'<div class="{cls}">{answer_html(r["answer"])}</div>', unsafe_allow_html=True)
    if r.get("audio"):
        st.audio(r["audio"], format="audio/wav")
    note = "जतन केलेले उत्तर (ऑफलाइन)" if r.get("cached") else f"{r['total']:.1f} से. · {r['provider']}"
    st.markdown(f'<p class="meta">{note}</p>', unsafe_allow_html=True)
    if r["sources"] and not r["not_found"]:
        with st.expander(f"स्रोत / Sources ({len(r['sources'])})"):
            for i, s in enumerate(r["sources"], 1):
                link = f' · <a href="{s["url"]}" target="_blank">PDF</a>' if s["url"].startswith("http") else ""
                st.markdown(
                    f'<div class="src"><span class="n">{i}</span><span class="t">{html.escape(s["title"])}</span>'
                    f'<div class="p">{html.escape(s["publisher"])} · पान {s["page"]}{link}</div>'
                    f'<blockquote>{html.escape(s["text"][:280])}…</blockquote></div>', unsafe_allow_html=True)


# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("**सेटिंग्ज / Settings**")
    lang_label = st.selectbox("उत्तराची भाषा / Answer language", list(config.LANGUAGES))
    crop_label = st.selectbox("पीक / Crop", list(CROPS))
    with st.expander("माहिती आणि मर्यादा / About"):
        st.markdown(
            "- उत्तरे फक्त ICAR, कृषी विद्यापीठे आणि सरकारी दस्तऐवजांतून येतात.\n"
            "- माहिती स्रोतांत नसेल तर अॅप तसे सांगते; अंदाज लावत नाही.\n"
            "- तुमचा आवाज लिप्यंतरणासाठी Sarvam AI कडे जातो; हे अॅप काहीही साठवत नाही.\n"
            "- बोली भाषा किंवा गोंगाटामुळे आवाज ओळखण्यात चुका होऊ शकतात.\n"
            "- कृषी अधिकारी किंवा KVK चा सल्ला याला पर्याय नाही.\n\n"
            f"किसान कॉल सेंटर: **{config.KCC_NUMBER}**")
lang, crop = config.LANGUAGES[lang_label], CROPS[crop_label]

# ---------------- Main ----------------
st.markdown(
    '<div class="masthead"><p class="kicker">ICAR · MPKV · PM-KISAN स्रोतांवर आधारित</p>'
    "<h1>कृषी मित्र</h1>"
    '<p class="sub">ऊस, द्राक्ष आणि हळद यांबद्दल प्रश्न विचारा. उत्तर मराठीत, पान क्रमांकासह स्रोत दाखवून.</p>'
    '<hr class="rule"></div>', unsafe_allow_html=True)

st.session_state.setdefault("q", "")


def pick_example() -> None:
    """Pill clicked: copy the example into the box and run it (then clear the pill)."""
    if st.session_state.ex:
        st.session_state.q = st.session_state.ex
        st.session_state.go = True
    st.session_state.ex = None


tab_type, tab_speak = st.tabs(["लिहा / Type", "बोला / Speak"])
with tab_type:
    st.text_area("प्रश्न", key="q", height=96, label_visibility="collapsed",
                 placeholder="उदा. हळदीवरील कंदकुज रोग कसा टाळावा?")
with tab_speak:
    audio = st.audio_input("प्रश्न बोला", label_visibility="collapsed")
    st.caption("रेकॉर्ड थांबवल्यावर खालील बटण दाबा.")

clicked = st.button("उत्तर मिळवा", type="primary")
st.markdown('<p class="label">उदाहरणे / TRY ASKING</p>', unsafe_allow_html=True)
st.pills("उदाहरणे", EXAMPLES, key="ex", on_change=pick_example, label_visibility="collapsed")

if clicked or st.session_state.pop("go", False):
    run_query(st.session_state.q, audio.getvalue() if audio else None, lang, crop)

if "result" in st.session_state:
    show_result(st.session_state.result)
