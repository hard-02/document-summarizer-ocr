# Deployment Guide

A shareable, clickable link for your professor. Pick whichever is easiest.

---

## Option A — Hugging Face Spaces (easiest, free)

Deploys the **Streamlit** demo with no Docker knowledge.

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space).
2. SDK: **Streamlit**. Space name: e.g. `doc-summarizer`.
3. Upload these files (or link your GitHub repo):
   - `app.py`
   - `requirements.txt`
   - `src/` (the whole folder)
4. Click **Create Space**. It builds and gives you a public URL like
   `https://huggingface.co/spaces/<you>/doc-summarizer`.

> The models download on first request inside the Space (~1–2 GB) — the first
> summarize may take a few minutes, then it's cached.

---

## Option B — Docker (the FastAPI web app, any cloud)

Build and run locally first to verify:

```bash
docker build -t doc-summarizer .
docker run -p 8000:8000 doc-summarizer
# open http://localhost:8000
```

Then deploy the image to any container host:

| Host | What to do |
|------|-----------|
| [Render](https://render.com) | New Web Service → point at the repo, Dockerfile auto-detected |
| [Railway](https://railway.app) | New Project → Deploy from GitHub repo |
| [Fly.io](https://fly.io) | `fly launch` → deploys the Dockerfile |
| AWS/GCP/Azure | Push the image to a registry and run it as a container |

The `Dockerfile` serves the **FastAPI + frontend** app on port `8000`.

---

## Option C — Streamlit Community Cloud (free, GitHub-based)

1. Push this repo to GitHub (already done).
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. **New app** → pick the repo, branch `main`, main file path `app.py`.
4. Deploy. It builds from `requirements.txt` and runs `app.py`.

---

## Notes for all options

- The app auto-uses `models/<lang>/` if you add fine-tuned weights; otherwise it
  downloads the public checkpoints.
- First request triggers model downloads (BART, IndicBART, EasyOCR). Subsequent
  requests are fast.
- For the OCR (image) path, ensure the host has enough memory (~2 GB free) since
  EasyOCR loads detection + recognition models into RAM.
