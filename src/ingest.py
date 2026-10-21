"""Offline ingestion: PDFs -> cleaned pages -> chunks -> embeddings -> FAISS index.

Run once on your laptop:  python -m src.ingest
The app never re-embeds at startup; it only loads the saved index.
"""
import json
import re
from collections import Counter

import faiss
import fitz  # pymupdf
import pandas as pd
from sentence_transformers import SentenceTransformer

from src import config


def clean(text: str) -> str:
    """Collapse whitespace but keep paragraph breaks (useful split points)."""
    text = text.replace("\xa0", " ")
    text = re.sub(r"[-]", "-", text)  # PDF bullet glyphs (e.g. ) -> "-"
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # single newlines are just PDF line wraps -> join them
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    return text.strip()


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Split on sentence boundaries into ~size-char chunks with ~overlap chars carried over."""
    # Split after . ? ! or Devanagari danda, or at paragraph breaks
    sentences = [s.strip() for s in re.split(r"(?<=[.?!।])\s+|\n\n", text) if s.strip()]
    chunks, current = [], ""
    for s in sentences:
        if current and len(current) + len(s) + 1 > size:
            chunks.append(current)
            # start next chunk with the tail of this one, cut at a word boundary
            tail = current[-overlap:]
            tail = tail[tail.find(" ") + 1:] if " " in tail else tail
            current = tail
        current = f"{current} {s}".strip()
        while len(current) > size * 1.5:  # a single huge "sentence" (tables, lists)
            chunks.append(current[:size])
            current = current[size - overlap:]
    if current.strip():
        chunks.append(current)
    return chunks


def extract_pages(pdf_path) -> list[tuple[int, str]]:
    """Return [(page_number starting at 1, cleaned_text)] skipping near-empty pages."""
    pages = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc, start=1):
            text = clean(page.get_text())
            if len(text) >= config.MIN_PAGE_CHARS:
                pages.append((i, text))
    return pages


def build() -> None:
    sources = pd.read_csv(config.SOURCES_CSV).fillna("")
    records, page_counts = [], Counter()
    for row in sources.itertuples():
        path = config.RAW_DIR / row.file
        if not path.exists():
            print(f"[skip] {row.file} not found in data/raw/")
            continue
        for page_no, text in extract_pages(path):
            page_counts[row.file] += 1
            for piece in chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP):
                records.append({
                    "id": len(records), "text": piece, "file": row.file,
                    "title": row.title, "publisher": row.publisher,
                    "url": row.url, "crop": row.crop, "page": page_no,
                })
    if not records:
        raise SystemExit("No chunks produced - put PDFs in data/raw/ first.")

    print(f"Embedding {len(records)} chunks with {config.EMBED_MODEL} ...")
    model = SentenceTransformer(config.EMBED_MODEL)
    vectors = model.encode(
        [config.PASSAGE_PREFIX + r["text"] for r in records],
        batch_size=32, normalize_embeddings=True, show_progress_bar=True,
    ).astype("float32")

    index = faiss.IndexFlatIP(vectors.shape[1])  # inner product == cosine (normalised)
    index.add(vectors)
    config.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(config.FAISS_PATH))
    with open(config.CHUNKS_PATH, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    chunk_counts = Counter(r["file"] for r in records)
    print(f"\nDocs: {len(page_counts)}  Pages: {sum(page_counts.values())}  Chunks: {len(records)}")
    for file in page_counts:
        print(f"  {file}: {page_counts[file]} pages, {chunk_counts[file]} chunks")


if __name__ == "__main__":
    build()
