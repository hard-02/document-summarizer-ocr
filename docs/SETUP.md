# Setup Guide

Everything you need to run, train, and publish this project.

---

## 1. Run the app locally (two frontends)

The project ships two frontends that share the same `src/` inference core:

| Frontend | Command | URL |
|----------|---------|-----|
| **Web app** (FastAPI + HTML/CSS/JS) | `uvicorn web.server:app --reload` | `http://127.0.0.1:8000` |
| **Streamlit demo** | `streamlit run app.py` | `http://localhost:8501` |

### 1.1 Web app

```bash
cd document-summarizer-ocr

python -m venv .venv
source .venv/bin/activate              # macOS / Linux
# .venv\Scripts\activate               # Windows

pip install --upgrade pip
pip install -r web/requirements.txt    # installs app deps + FastAPI/uvicorn

uvicorn web.server:app --reload
```

Open `http://127.0.0.1:8000`. The UI has three tabs — **Document**, **Image**,
**Text** — with language + length controls and drag-and-drop upload.

### 1.2 Streamlit demo

```bash
pip install -r requirements.txt
streamlit run app.py
```

**First-run note:** both apps download BART, IndicBART, and EasyOCR weights on
first use (~1–2 GB). Pre-warm with:

```bash
python -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; \
  AutoTokenizer.from_pretrained('facebook/bart-large-cnn'); \
  AutoModelForSeq2SeqLM.from_pretrained('facebook/bart-large-cnn')"
```

---

## 2. Fine-tune

Two ways — **Kaggle** (free GPU) or **local** (`scripts/train.py`).

### 2.1 On Kaggle

1. Sign in to [kaggle.com](https://www.kaggle.com) → **Create → New Notebook**.
2. Sidebar: **Accelerator → GPU T4 x2**, **Internet → On**.
3. **File → Import Notebook** and upload from `notebooks/`.
4. **Run All**.

| Notebook | Model | Output folder | Place in |
|----------|-------|---------------|----------|
| `01_finetune_english_bart.ipynb` | BART | `bart-finetuned-cnn` | `models/english/` |
| `02_finetune_indicbart_hindi_marathi.ipynb` | IndicBART | `indicbart-finetuned-hindi` | `models/hindi/` |
| 〃 (set `LANG="marathi"`) | IndicBART | `indicbart-finetuned-marathi` | `models/marathi/` |

Download each folder from the Kaggle **Output** tab and place it under `models/`
as shown — the app/web UI auto-detect and use them.

### 2.2 Locally

```bash
pip install -r requirements.txt -r requirements-train.txt

python scripts/train.py --language en --epochs 2 --batch-size 4
python scripts/train.py --language hi --epochs 2
python scripts/train.py --language mr --epochs 2
```

Useful flags (`python scripts/train.py --help`):

- `--train-size N` / `--eval-size N` — sample size (default 2000 / 200).
- `--epochs`, `--batch-size`, `--lr` — training hyperparameters.
- `--fp16` / `--no-fp16` — mixed precision (defaults to auto).
- `--output-dir` — where to save; `--push-to-hub <repo>` — push to HF Hub.

Move the saved folder into `models/<lang>/` to use it in the apps.

> `models/` and `data/` are git-ignored — trained weights and raw data should
> not be committed.

---

## 3. Publish to GitHub

### 3.1 Initialize and commit
```bash
cd document-summarizer-ocr

git init
git add .
git status          # sanity check — you should NOT see models/*.bin etc.
git commit -m "Initial commit: multilingual document & image summarizer"
```

### 3.2 Create the remote repo
1. Go to [github.com/new](https://github.com/new).
2. Name it e.g. `document-summarizer-ocr`.
3. **Do not** initialize it with a README / .gitignore (you already have these).
4. Click **Create repository**, then copy the `https://…` URL.

### 3.3 Push
```bash
git remote add origin https://github.com/<your-username>/document-summarizer-ocr.git
git branch -M main
git push -u origin main
```

### 3.4 Polish for the professor
- Add a real screenshot of the running web app (drop `docs/screenshot.png` and
  reference it in `README.md`).
- Add a short **Results** section with your ROUGE scores (printed by the
  notebooks / `scripts/train.py`).
- The `LICENSE` (MIT) is already included.

---

## 4. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `streamlit: command not found` | Activate the venv first, or use `python -m streamlit run app.py`. |
| `uvicorn: command not found` | Use `python -m uvicorn web.server:app --reload`. |
| EasyOCR download hangs / fails | Check your network; EasyOCR pulls models from GitHub on first use. |
| `CUDA out of memory` | Lower `per_device_train_batch_size` to `2` and/or reduce `max_input_length` to `256`. |
| Indic summary in the wrong script | Ensure `LANG_CODE` matches the language and `forced_bos_token_id` was set (printed by the script). |
| `models/` weights not detected | Folder name must match `config.py` (`english`, `hindi`, `marathi`) and contain `config.json` + weights. |
| PDF text is empty | The PDF is likely a scanned image — use the **Image** tab (OCR) instead. |

---

## 5. Environment summary

| Where | What | Why |
|-------|------|-----|
| **Local** | Web app + Streamlit + `scripts/train.py` | Demo, screenshots, and training on your own GPU |
| **Kaggle** | GPU fine-tuning notebooks | Free GPU, easy to share with the professor |
| **GitHub** | Source + notebooks + docs | Version control + submission |
| **Hugging Face** (optional) | Host fine-tuned weights | Reuse without re-downloading |
