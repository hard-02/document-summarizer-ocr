# Multilingual Document Summarizer (English & Hindi)

Abstractive summarization of long documents in **English** and **Hindi**, with a
Streamlit demo, a FastAPI web app, and an optional **Gemini API** backend for
free deployment.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Demo](https://img.shields.io/badge/Demo-Streamlit-ff4b4b)

## ✨ Features

| Capability | Implementation |
|-----------|----------------|
| Document summarization | Abstractive summarization (BART / IndicBART) |
| Languages | English (`en`) and Hindi (`hi`) |
| Input formats | `.txt`, `.pdf`, `.docx`, pasted text |
| Two frontends | **Web app** (FastAPI + HTML/CSS/JS) and **Streamlit** |
| Optional API backend | Google **Gemini** (no PyTorch, fast, free-tier friendly) |
| Train your own model | Kaggle notebooks **and** a local `scripts/train.py` |

## 🧠 Architecture

```
 Document (.txt/.pdf/.docx) ──► text extraction ──► Summarizer ──► Summary
                                                    │
                        local: BART (en) / IndicBART (hi)
                        or:    Gemini API (no torch)
```

The app first checks `models/<lang>/` for a fine-tuned checkpoint. If none is
present, it falls back to the public checkpoint — or to Gemini when
`SUMMARY_PROVIDER=gemini`.

## 🗂️ Repository structure

```
document-summarizer-ocr/
├── app.py                        # Streamlit demo
├── web/                          # FastAPI backend + static frontend
│   ├── server.py
│   └── static/                   # index.html · styles.css · app.js
├── src/
│   ├── config.py                 # model registry + provider config
│   ├── text_extraction.py        # .txt / .pdf / .docx readers
│   ├── summarizer.py             # local models + Gemini routing
│   └── llm_api.py                # Gemini REST client (stdlib only)
├── scripts/train.py              # local fine-tuning (en / hi)
├── notebooks/                    # Kaggle fine-tuning notebooks
│   ├── 01_finetune_english_bart.ipynb
│   └── 02_finetune_indicbart_hindi.ipynb
├── models/                       # (git-ignored) fine-tuned weights
├── requirements.txt              # local-model stack
├── requirements-api.txt          # lightweight Gemini stack
├── Dockerfile.api                # slim image for the Gemini demo
└── docs/
    ├── SETUP.md
    ├── DEPLOY.md
    ├── DEPLOY_RENDER.md
    └── architecture.svg
```

## 🚀 Quickstart

### Local models (default)

```bash
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py            # or: uvicorn web.server:app --reload
```

### Gemini API backend (no torch)

```bash
pip install -r requirements-api.txt
export SUMMARY_PROVIDER=gemini
export GEMINI_API_KEY=your_key
uvicorn web.server:app --reload     # http://127.0.0.1:8000
```

## 🎓 Fine-tune

- **Kaggle:** `notebooks/01_finetune_english_bart.ipynb` (BART, CNN/DailyMail)
  and `notebooks/02_finetune_indicbart_hindi.ipynb` (IndicBART, XL-Sum Hindi).
- **Locally:**
  ```bash
  pip install -r requirements.txt -r requirements-train.txt
  python scripts/train.py --language en --epochs 2
  python scripts/train.py --language hi --epochs 2
  ```

Drop the output folders into `models/english/` and `models/hindi/`.

## 📊 Results

| Language | Model | ROUGE-1 | ROUGE-2 | ROUGE-L | ROUGE-Lsum |
|----------|-------|---------|---------|---------|------------|
| English | BART-base, fine-tuned on CNN/DailyMail (2,000 examples, 2 epochs, Kaggle T4) | 40.65 | 19.10 | 28.30 | 37.59 |
| Hindi | IndicBART, fine-tuned on XL-Sum (2,000 examples, 2 epochs) | 60.42 | 25.90 | 60.36 | 60.26 |

**English** is a solid BART fine-tune. **Hindi** works but is *verbose* (it fills
the 128-token cap, so ROUGE-1 is inflated by long output) — treat these as
"strong for a small fine-tune", not SOTA.

## ☁️ Deploy

- **Gemini demo on Render (free):** see [docs/DEPLOY_RENDER.md](docs/DEPLOY_RENDER.md).
- **Hugging Face static page:** the existing Space is a static landing page.
- **Docker:** `Dockerfile` (local models) or `Dockerfile.api` (Gemini).

## 🗂️ Datasets & models

- **English** — [CNN/DailyMail](https://huggingface.co/datasets/abisee/cnn_dailymail) → [BART](https://huggingface.co/facebook/bart-base)
- **Hindi** — [XL-Sum](https://huggingface.co/datasets/csebuetnlp/xlsum) → [IndicBART](https://huggingface.co/ai4bharat/IndicBARTSS)
- **Optional** — [Gemini API](https://aistudio.google.com/apikey) (`gemini-3.5-flash`)

## 📚 References

- Lewis et al., *BART: Denoising Sequence-to-Sequence Pre-training* (2019)
- Dabre et al., *IndicBART: A Pre-trained Model for Indic Natural Language Generation* (2022)
- Hasan et al., *XL-Sum: Large-Scale Multilingual Abstractive Summarization* (2021)

## 📄 License

[MIT](LICENSE) © 2026 Hardik Pathak
