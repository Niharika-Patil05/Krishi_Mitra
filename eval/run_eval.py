"""Evaluation: retrieval hit@k, refusal accuracy, per-stage latency; plus demo-cache builder.

  python -m eval.run_eval --no-llm   # retrieval only on the raw question (no API keys needed)
  python -m eval.run_eval            # full pipeline incl. rewrite + answer (needs keys)
  python -m eval.run_eval --cache    # regenerate demo_cache.json from config.EXAMPLES
"""
import argparse
import json
import re
import time
from collections import defaultdict

import pandas as pd

from src import config, llm, pipeline
from src.retriever import Retriever

RESULTS = config.ROOT / "eval" / "results.csv"


def lang_code(question: str) -> str:
    """Devanagari -> Marathi, else English (good enough for our test questions)."""
    return "mr-IN" if re.search(r"[ऀ-ॿ]", question) else "en-IN"


def evaluate(no_llm: bool) -> pd.DataFrame:
    retriever = Retriever()
    rows = []
    for q in pd.read_csv(config.ROOT / "eval" / "questions.csv").itertuples():
        lang, t = lang_code(q.question), defaultdict(float)
        in_scope = q.expected_source != "NONE"
        if no_llm:
            t0 = time.perf_counter()
            hits = retriever.search(q.question, k=config.TOP_K)
            t["retrieve"] = time.perf_counter() - t0
            refused = not hits or hits[0]["score"] < config.SCORE_THRESHOLD
            answer = ""
        else:
            res = pipeline.ask(q.question, lang, retriever, with_audio=False)
            hits, t = res["sources"], res["timings"]
            answer = res["answer"]
            # refusal = threshold refusal OR the LLM itself said "not found" (mentions the KCC number)
            refused = res["not_found"] or config.KCC_NUMBER in answer
        files = [h["file"] for h in hits]
        rows.append({
            "question": q.question, "lang": q.lang, "crop": q.crop, "expected": q.expected_source,
            "top1_file": files[0] if files else "", "top1_score": hits[0]["score"] if hits else 0.0,
            "hit@1": in_scope and files[:1] == [q.expected_source],
            "hit@5": in_scope and q.expected_source in files[:5],
            "refused": refused, "answer": answer, **{f"t_{k}": v for k, v in t.items()},
        })
    return pd.DataFrame(rows)


def summarise(df: pd.DataFrame) -> None:
    ins, oos = df[df.expected != "NONE"], df[df.expected == "NONE"]
    print("\n| Metric | Value |\n|---|---|")
    print(f"| Questions (in-scope / out-of-scope) | {len(ins)} / {len(oos)} |")
    print(f"| Retrieval hit@1 | {ins['hit@1'].mean():.0%} |")
    print(f"| Retrieval hit@5 | {ins['hit@5'].mean():.0%} |")
    print(f"| Refusal accuracy (out-of-scope) | {oos.refused.mean():.0%} |")
    print(f"| Wrongly refused (in-scope) | {ins.refused.mean():.0%} |")
    for col in [c for c in df.columns if c.startswith("t_")]:
        print(f"| Avg latency {col[2:]} (s) | {df[col].mean():.2f} |")
    print("\nThreshold sweep on top-1 score (pick one that refuses out-of-scope, keeps in-scope):")
    print("| threshold | in-scope kept | out-of-scope refused |\n|---|---|---|")
    for th in sorted(set(round(x, 2) for x in df.top1_score.quantile([i / 10 for i in range(11)]))):
        print(f"| {th:.2f} | {(ins.top1_score >= th).mean():.0%} | {(oos.top1_score < th).mean():.0%} |")


def build_cache() -> None:
    """Pre-compute answers for the example questions (run when APIs work, before the demo)."""
    retriever, cache = Retriever(), []
    for q in config.EXAMPLES:
        lang = lang_code(q)
        res = pipeline.ask(q, lang, retriever, with_audio=False)
        cache.append({"question": q, "lang": lang, "answer": res["answer"], "sources": res["sources"]})
        print(f"cached ({res['provider']}): {q}")
    config.DEMO_CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-llm", action="store_true")
    ap.add_argument("--cache", action="store_true")
    args = ap.parse_args()
    if args.cache:
        build_cache()
    else:
        df = evaluate(args.no_llm)
        df.to_csv(RESULTS, index=False)
        summarise(df)
        print(f"\nSaved {RESULTS}")
