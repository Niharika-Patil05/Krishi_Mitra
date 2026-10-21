"""Krishi Mitra - Streamlit UI. All logic lives in src/; this file only draws and wires.

All visible text comes from src/ui_text.py, so the whole page follows the chosen answer language.
"""
import html
import logging
import re
import time

import streamlit as st

from src import config, pipeline, speech
from src.ui_text import CROP_KEYS, DEFAULT_CODE, EXAMPLES, TEXT

logging.basicConfig(level=logging.INFO)
st.set_page_config(page_title="Krishi Mitra", page_icon="🌱", layout="centered", initial_sidebar_state="collapsed")
st.markdown(f"<style>{(config.ROOT / 'assets' / 'style.css').read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True)

# The language widget lives further down, but its value is already in session_state when the
# script reruns, so we can pick the interface language before drawing anything.
lang = config.LANGUAGES.get(st.session_state.get("lang"), DEFAULT_CODE)
T = TEXT[lang]


@st.cache_resource(show_spinner=False)
def get_retriever():
    """Load embedding model + FAISS index once per server process (not per click)."""
    from src.retriever import Retriever
    return Retriever()


def run_query(question: str, audio_bytes: bytes | None, crop: str | None) -> None:
    """Do STT (if voice), run the pipeline, fall back to cache on failure; store in session."""
    result, transcript, t0 = None, None, time.perf_counter()
    try:
        if not question.strip() and audio_bytes:
            with st.spinner(T["listening"]):
                # "unknown" = auto-detect, so a farmer may speak Marathi/Hindi/English freely
                question = transcript = speech.stt(audio_bytes, "unknown")
        if not question.strip():
            st.session_state.result = {"error": T["err_empty"]}
            return
        with st.spinner(T["searching"]):
            result = pipeline.ask(question, lang, get_retriever(), crop)
    except FileNotFoundError:
        st.session_state.result = {"error": T["err_index"]}
        return
    except Exception as e:  # never show a stack trace to the user
        logging.exception("query failed: %s", e)
        result = pipeline.cached_answer(question, lang)
        if result is None:
            st.session_state.result = {"error": f"{T['err_busy']} {T['kcc']}: {config.KCC_NUMBER}"}
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
        st.markdown(f'<p class="heard">{T["heard"]}: <b>{html.escape(r["transcript"])}</b></p>', unsafe_allow_html=True)
    cls = "answer notfound" if r["not_found"] else "answer"
    st.markdown(f'<div class="{cls}">{answer_html(r["answer"])}</div>', unsafe_allow_html=True)
    if r.get("audio"):
        st.audio(r["audio"], format="audio/wav")
    note = T["cached"] if r.get("cached") else f"{r['total']:.1f} {T['sec']} · {r['provider']}"
    st.markdown(f'<p class="meta">{note}</p>', unsafe_allow_html=True)
    if r["sources"] and not r["not_found"]:
        with st.expander(f"{T['sources']} ({len(r['sources'])})"):
            for i, s in enumerate(r["sources"], 1):
                link = f' · <a href="{s["url"]}" target="_blank">PDF</a>' if s["url"].startswith("http") else ""
                st.markdown(
                    f'<div class="src"><span class="n">{i}</span><span class="t">{html.escape(s["title"])}</span>'
                    f'<div class="p">{html.escape(s["publisher"])} · {T["page"]} {s["page"]}{link}</div>'
                    f'<blockquote>{html.escape(s["text"][:280])}…</blockquote></div>', unsafe_allow_html=True)


def rerun_with_new_settings() -> None:
    """Language/crop changed: answer the question already on screen again with the new settings.

    If that question is one of the example chips, swap in the same example in the new language.
    """
    r = st.session_state.get("result")
    if not r or "error" in r or not r.get("question"):
        return
    q, new_lang = r["question"], config.LANGUAGES[st.session_state.lang]
    for questions in EXAMPLES.values():
        if q in questions:
            q = EXAMPLES[new_lang][questions.index(q)]
            break
    st.session_state.q = q
    st.session_state.go = True


def pick_example() -> None:
    """Pill clicked: copy the example into the box and run it (then clear the pill)."""
    if st.session_state.ex:
        st.session_state.q = st.session_state.ex
        st.session_state.go = True
    st.session_state.ex = None


# ---------------- Header + settings popover ----------------
head, gear = st.columns([7, 1], vertical_alignment="top")
with head:
    st.markdown(
        f'<div class="masthead"><p class="kicker">{T["kicker"]}</p><h1>{T["title"]}</h1>'
        f'<p class="sub">{T["sub"]}</p><hr class="rule"></div>', unsafe_allow_html=True)
with gear:
    # Widgets inside a popover still run every time, so lang/crop are always available below.
    with st.popover("", icon=":material/settings:", help=T["settings"]):
        st.markdown(f"**{T['settings']}**")
        st.selectbox(T["answer_lang"], list(config.LANGUAGES), key="lang", on_change=rerun_with_new_settings)
        crop_key = st.selectbox(T["crop"], CROP_KEYS, key="crop", format_func=lambda k: T["crops"][k],
                                on_change=rerun_with_new_settings)
        crop = None if crop_key == "all" else crop_key
        points = "\n".join(f"- {p}" for p in T["about_points"])
        st.markdown(f"---\n**{T['about']}**\n\n{points}\n\n{T['kcc']}: **{config.KCC_NUMBER}**")

# ---------------- Question input ----------------
st.session_state.setdefault("q", "")
tab_type, tab_speak = st.tabs([T["tab_type"], T["tab_speak"]])
with tab_type:
    st.text_area(T["tab_type"], key="q", height=96, label_visibility="collapsed", placeholder=T["placeholder"])
with tab_speak:
    audio = st.audio_input(T["speak_label"], label_visibility="collapsed")
    st.caption(T["speak_hint"])

clicked = st.button(T["ask"], type="primary")
st.markdown(f'<p class="label">{T["try"].upper()}</p>', unsafe_allow_html=True)
st.pills(T["try"], EXAMPLES[lang], key="ex", on_change=pick_example, label_visibility="collapsed")

if clicked or st.session_state.pop("go", False):
    run_query(st.session_state.q, audio.getvalue() if audio else None, crop)

if "result" in st.session_state:
    show_result(st.session_state.result)
