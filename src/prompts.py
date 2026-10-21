"""All prompt templates and fixed messages in one place (easy to show in the viva)."""
import re

from src import config

# Language names used inside prompts (the LLM follows names better than codes).
LANG_NAMES = {
    "mr-IN": "Marathi (Devanagari script)",
    "hi-IN": "Hindi (Devanagari script)",
    "en-IN": "English",
}

REWRITE_SYSTEM = (
    "You convert a farmer's question (Marathi, Hindi or English) into one short English "
    "search query for a farming document database. Keep crop, pest, disease, chemical and "
    "scheme names. Output ONLY the English query, nothing else."
)

ANSWER_SYSTEM = """You are Krishi Mitra, a farm advisory assistant for farmers in Sangli and Kolhapur, Maharashtra.

Rules:
1. Answer ONLY from the numbered CONTEXT below. Never use outside knowledge.
2. If the context does not contain the answer, say so plainly and suggest calling Kisan Call Centre {kcc} or the local KVK. Do not guess.
3. Reply in {language}. Use simple, farmer-friendly words and short sentences. HARD LIMIT: 100 words, at most 5 short bullet points. Pick only the most useful points.
4. Put the source number right after each fact, like "... करावे [1]." Never write a separate list of sources at the end and never write "according to [1]".
5. Only if your answer contains a pesticide / fungicide / chemical dose: give the dose exactly as written in the context and end with this line: "{dose_note}". Otherwise do NOT add that line.
6. Never give medical, legal or financial guarantees."""

DOSE_NOTE = {
    "mr-IN": "वापरण्यापूर्वी स्थानिक कृषी अधिकारी / KVK यांचा सल्ला घ्या.",
    "hi-IN": "उपयोग से पहले स्थानीय कृषि अधिकारी / KVK से सलाह लें।",
    "en-IN": "Consult your local agriculture officer / KVK before use.",
}

# Shown when retrieval finds nothing relevant (no LLM call, so it cannot hallucinate).
NOT_FOUND = {
    "mr-IN": f"माफ करा, ही माहिती माझ्या उपलब्ध स्रोतांमध्ये सापडली नाही. कृपया किसान कॉल सेंटर ({config.KCC_NUMBER}) किंवा जवळच्या KVK शी संपर्क साधा.",
    "hi-IN": f"क्षमा करें, यह जानकारी मेरे उपलब्ध स्रोतों में नहीं मिली। कृपया किसान कॉल सेंटर ({config.KCC_NUMBER}) या नज़दीकी KVK से संपर्क करें।",
    "en-IN": f"Sorry, I could not find this in my trusted sources. Please contact Kisan Call Centre ({config.KCC_NUMBER}) or your local KVK.",
}


def rewrite_messages(question: str) -> list[dict]:
    return [{"role": "system", "content": REWRITE_SYSTEM},
            {"role": "user", "content": question}]


def format_context(hits: list[dict]) -> str:
    """Number each chunk so the model can cite it as [n]."""
    return "\n\n".join(
        f"[{i}] ({h['title']}, page {h['page']})\n{h['text']}" for i, h in enumerate(hits, 1)
    )


def answer_messages(question: str, hits: list[dict], lang_code: str) -> list[dict]:
    system = ANSWER_SYSTEM.format(
        kcc=config.KCC_NUMBER, language=LANG_NAMES[lang_code], dose_note=DOSE_NOTE[lang_code]
    )
    user = f"CONTEXT:\n{format_context(hits)}\n\nQUESTION: {question}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def strip_citations(text: str) -> str:
    """Remove [1], [2] markers so the text-to-speech does not read them aloud."""
    return re.sub(r"\s*\[\d+(?:\s*,\s*\d+)*\]", "", text).strip()


# A dose looks like "2 g/L", "१० ग्रॅम/लिटर", "0.5 ml/L", "1 kg/ha", "30 ppm", "1.5%" (Devanagari digits too).
_DOSE = re.compile(
    r"[\d०-९]\s*(?:ग्रॅम|ग्राम|मिली|किलो|लिटर|g|kg|ml|mL|l|L)\s*/\s*\S"          # 2 g/L, १० ग्रॅम/लिटर
    r"|[\d०-९]\s*ppm"                                                          # 30 ppm
    r"|(?:spray|फवार)\D{0,40}[\d०-९.]+\s*(?:%|टक्के)"                              # spray ... 0.5%
    r"|[\d०-९.]+\s*(?:%|टक्के)\s*\D{0,20}(?:spray|फवार|mixture|मिश्रण)", re.I)       # 1% Bordeaux mixture


def fix_dose_note(answer: str, lang_code: str) -> str:
    """Add the safety line only when the answer quotes a chemical dose; remove it otherwise.

    We enforce this in code because the LLM does not follow the 'only if a dose' rule reliably.
    """
    note = DOSE_NOTE[lang_code]
    body = "\n".join(l for l in answer.splitlines() if note not in l).rstrip()
    return f"{body}\n\n{note}" if _DOSE.search(body) else body
