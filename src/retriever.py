"""Load the saved FAISS index and search it. No embedding of documents happens here."""
import json

import faiss
from sentence_transformers import SentenceTransformer

from src import config


class Retriever:
    def __init__(self) -> None:
        self.model = SentenceTransformer(config.EMBED_MODEL)
        self.index = faiss.read_index(str(config.FAISS_PATH))
        with open(config.CHUNKS_PATH, encoding="utf-8") as f:
            self.chunks = [json.loads(line) for line in f]

    def search(self, query: str, k: int = config.TOP_K, crop_filter: str | None = None) -> list[dict]:
        """Return top-k chunks (each with a 'score') for an English query.

        crop_filter keeps only that crop plus "scheme" docs (schemes apply to everyone).
        FAISS has no metadata filter, so we over-fetch and filter in Python; the corpus is
        small (a few thousand chunks) so this is fast.
        """
        q = self.model.encode([config.QUERY_PREFIX + query], normalize_embeddings=True).astype("float32")
        fetch = len(self.chunks) if crop_filter else k
        scores, ids = self.index.search(q, fetch)
        hits = []
        for score, i in zip(scores[0], ids[0]):
            chunk = self.chunks[i]
            if crop_filter and chunk["crop"] not in (crop_filter, "scheme"):
                continue
            hits.append({**chunk, "score": float(score)})
            if len(hits) == k:
                break
        return hits


if __name__ == "__main__":
    # Quick manual test: python -m src.retriever
    r = Retriever()
    for q in ["How to control rhizome rot in turmeric?",
              "Which turmeric varieties are recommended for Maharashtra?",
              "What is the best time of planting turmeric?"]:
        print(f"\n=== {q}")
        for h in r.search(q, k=3):
            print(f"  {h['score']:.3f} | {h['file']} p.{h['page']} | {h['text'][:110]!r}")
