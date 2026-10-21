# कृषी मित्र — Krishi Mitra

Marathi voice farm-advisory assistant (RAG + speech) for farmers in Sangli/Kolhapur
(sugarcane, grapes, turmeric). Answers are grounded in ICAR / government / university
PDFs and always cite document and page. If the answer is not in the sources, the app
says so and points to Kisan Call Centre (1800-180-1551) or the local KVK.

> **Status:** Milestone 1 (skeleton). Full README is written in Milestone 7.

## Quick setup (local)

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                                  # then add your keys
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # optional, for streamlit
```

Later milestones add: `python -m src.ingest`, `streamlit run app.py`.

## Layout

See the build spec: `app.py`, `src/` (config, ingest, retriever, llm, speech, prompts,
pipeline), `data/` (raw PDFs, sources.csv, committed FAISS index), `eval/`, `docs/`.
