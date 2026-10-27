# Multilingual Document & Image Summarizer

Summarize **documents** (`.txt`, `.pdf`, `.docx`) and **images** (via OCR) in
**English, Hindi, and Marathi** — with a **web app**, a **Streamlit demo**, and
**Kaggle + local** fine-tuning. A complete NLP course project covering the full
ML lifecycle: data loading → fine-tuning a seq2seq model → ROUGE evaluation →
user-facing application.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Demo](https://img.shields.io/badge/Demo-Streamlit-ff4b4b)
![OCR](https://img.shields.io/badge/OCR-EasyOCR-orange)

## ✨ Features

| Capability | Implementation |
|-----------|----------------|
| Document summarization | Abstractive summarization (BART / IndicBART) |
| Image → text | EasyOCR (English + Hindi + Marathi) |
| Image → summary | OCR output fed into the summarizer |
| Regional languages | Hindi (`hi`), Marathi (`mr`) via [IndicBART sentence summarizer](https://huggingface.co/ai4bharat/MultiIndicSentenceSummarization) |
| Two frontends | **Web app** (FastAPI + HTML/CSS/JS) and **Streamlit** demo |
| Train your own model | Kaggle notebooks **and** a local `scripts/train.py` |

## 🧠 Architecture

![Architecture diagram](docs/architecture.svg)

## 📸 Screenshot

![App screenshot](docs/screenshot.png)

## 🗂️ Repository structure

```
document-summarizer-ocr/
├── app.py                        # Streamlit demo
├── web/                          # FastAPI backend + static frontend (the "website")
│   ├── server.py                 #   JSON API + serves the UI
│   ├── static/                   #   index.html · styles.css · app.js
│   └── requirements.txt
├── src/                          # shared inference core
│   ├── config.py                 #   model registry + device + paths
│   ├── text_extraction.py        #   .txt / .pdf / .docx readers
│   ├── ocr.py                    #   EasyOCR wrapper (en + hi + mr)
│   └── summarizer.py             #   language-aware summarization
├── scripts/
│   └── train.py                  # local fine-tuning (CLI, mirrors the notebooks)
├── notebooks/                    # Kaggle fine-tuning notebooks
│   ├── 01_finetune_english_bart.ipynb
│   └── 02_finetune_indicbart_hindi_marathi.ipynb
├── models/                       # (git-ignored) drop fine-tuned weights here
├── data/                         # (git-ignored) raw data
├── docs/
│   ├── architecture.svg
│   ├── SETUP.md
│   └── DEPLOY.md
├── requirements.txt              # app + inference deps
├── requirements-train.txt        # fine-tuning deps
├── Dockerfile                    # container for the web app
├── .dockerignore
└── LICENSE                       # MIT
```

## 🚀 Quickstart

### Option A — Web app (FastAPI + frontend)

```bash
python -m venv .venv
source .venv/bin/activate                 # Windows: .venv\Scripts\activate

pip install -r web/requirements.txt       # installs app deps + FastAPI/uvicorn

uvicorn web.server:app --reload           # then open http://127.0.0.1:8000
```

### Option B — Streamlit demo

```bash
pip install -r requirements.txt
streamlit run app.py                      # opens http://localhost:8501
```

> First run downloads the models (BART, IndicBART) and EasyOCR weights
> (~1–2 GB total) — subsequent runs are fast. Both frontends call the same
> `src/` modules, and both auto-use `models/<lang>/` if a fine-tuned checkpoint
> is present.

## 🎓 Fine-tune

### On Kaggle (free GPU)
1. [kaggle.com](https://www.kaggle.com) → **Create → New Notebook**, enable **GPU** + **Internet**.
2. Use `notebooks/01_finetune_english_bart.ipynb` (BART, CNN/DailyMail) or
   `notebooks/02_finetune_indicbart_hindi_marathi.ipynb` (IndicBART, XL-Sum).
3. Download the output folder and place it in `models/english/`, `models/hindi/`,
   or `models/marathi/`.

### Locally (your own GPU/CPU)
```bash
pip install -r requirements.txt -r requirements-train.txt

python scripts/train.py --language en --epochs 2 --batch-size 4
python scripts/train.py --language hi --epochs 2
python scripts/train.py --language mr --epochs 2
```

See `scripts/train.py --help` for all options (dataset/model overrides, FP16,
push-to-hub, etc.).

## 📤 GitHub

This repo is ready to push — see [docs/SETUP.md](docs/SETUP.md#3-publish-to-github)
for the exact commands.

## 🗂️ Datasets & models

- **English** — [CNN/DailyMail](https://huggingface.co/datasets/cnn_dailymail) → [BART](https://huggingface.co/facebook/bart-base)
- **Hindi / Marathi** (out-of-the-box) — [IndicBART sentence summarizer](https://huggingface.co/ai4bharat/MultiIndicSentenceSummarization) (fine-tuned on IndicSentenceSummarization)
- **Hindi / Marathi** (your own document-level model) — fine-tune [IndicBART](https://huggingface.co/ai4bharat/IndicBARTSS) on [XL-Sum](https://huggingface.co/datasets/csebuetnlp/xlsum) with the notebooks
- **OCR** — [EasyOCR](https://github.com/JaidedAI/EasyOCR)

## 📊 Results

| Language | Model | ROUGE-1 | ROUGE-2 | ROUGE-L | ROUGE-Lsum |
|----------|-------|---------|---------|---------|------------|
| English | BART-base, fine-tuned on CNN/DailyMail (2,000 examples, 2 epochs, Kaggle T4) | 40.65 | 19.10 | 28.30 | 37.59 |
| Hindi | IndicBART, fine-tuned on XL-Sum (2,000 examples, 2 epochs) | 60.42 | 25.90 | 60.36 | 60.26 |
| Marathi | IndicBART, fine-tuned on XL-Sum (2,000 examples, 2 epochs) | 45.76 | 16.44 | 45.65 | 45.65 |

**English** is a solid BART fine-tune (val loss 1.96). **Hindi (60.4)** and
**Marathi (45.8)** both work — the spot-check shows coherent, on-topic summaries.
Both Indic models are *verbose* (they fill the 128-token cap, so ROUGE-1 is
inflated by long/extractive output) because they were fine-tuned on only 2,000
examples × 2 epochs — treat these as "strong for a small fine-tune", not SOTA.
The earlier failed Marathi run (ROUGE-1 2.53, garbage) was from before the
IndicBART `<2xx>` format fix; the re-run above is the real result.

## 📚 References

- Lewis et al., *BART: Denoising Sequence-to-Sequence Pre-training* (2019)
- Dabre et al., *IndicBART: A Pre-trained Model for Indic Natural Language Generation* (2022)
- Hasan et al., *XL-Sum: Large-Scale Multilingual Abstractive Summarization* (2021)

## 📄 License

[MIT](LICENSE) © 2026 Hardik Pathak
