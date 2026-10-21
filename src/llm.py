"""LLM calls: Sarvam first, Groq as fallback. Also query rewrite and answer generation."""
import logging

from src import config, prompts

log = logging.getLogger("krishi.llm")


def _sarvam(messages: list[dict]) -> str:
    from sarvamai import SarvamAI
    key = config.get_secret("SARVAM_API_KEY")
    if not key:
        raise RuntimeError("SARVAM_API_KEY not set")
    resp = SarvamAI(api_subscription_key=key).chat.completions(
        model=config.SARVAM_LLM_MODEL,
        messages=messages,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.LLM_MAX_TOKENS,
        reasoning_effort=None,  # thinking tokens would eat the budget and add latency
        request_options={"timeout_in_seconds": config.LLM_TIMEOUT_S},
    )
    return resp.choices[0].message.content or ""


def _groq(messages: list[dict]) -> str:
    from groq import Groq
    key = config.get_secret("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY not set")
    resp = Groq(api_key=key, timeout=config.LLM_TIMEOUT_S).chat.completions.create(
        model=config.GROQ_LLM_MODEL,
        messages=messages,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.LLM_MAX_TOKENS,
    )
    return resp.choices[0].message.content or ""


def chat(messages: list[dict]) -> tuple[str, str]:
    """Return (text, provider). Tries Sarvam, then Groq; raises if both fail."""
    errors = []
    for name, fn in (("sarvam", _sarvam), ("groq", _groq)):
        try:
            text = fn(messages).strip()
            if not text:
                raise RuntimeError("empty response")
            log.info("LLM answered via %s", name)
            return text, name
        except Exception as e:  # network, auth, timeout, empty -> try next provider
            log.warning("LLM provider %s failed: %s", name, e)
            errors.append(f"{name}: {e}")
    raise RuntimeError("All LLM providers failed: " + " | ".join(errors))


def rewrite_to_english(question: str) -> tuple[str, str]:
    """Turn the farmer's question into an English search query. Returns (query, provider).

    If the LLM is down we search with the original text: e5 is multilingual, so
    retrieval still works (just a bit less accurately).
    """
    try:
        text, provider = chat(prompts.rewrite_messages(question))
        return text.strip().strip('"\'').splitlines()[0], provider
    except RuntimeError:
        return question, "none"


def generate_answer(question: str, hits: list[dict], lang_code: str) -> tuple[str, str]:
    """Grounded answer in the requested language. Returns (answer, provider)."""
    return chat(prompts.answer_messages(question, hits, lang_code))


if __name__ == "__main__":
    # CLI test: python -m src.llm "हळदीची लागवड कधी करावी?"
    import sys
    from src.retriever import Retriever
    logging.basicConfig(level=logging.INFO)
    q = " ".join(sys.argv[1:]) or "हळदीवरील कंदकुज रोगासाठी काय उपाय करावा?"
    en, p1 = rewrite_to_english(q)
    print(f"Rewrite ({p1}): {en}")
    hits = Retriever().search(en, k=config.TOP_K)
    ans, p2 = generate_answer(q, hits, "mr-IN")
    print(f"\nAnswer ({p2}):\n{ans}")
