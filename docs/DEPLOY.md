# Deployment Guide

Three ways to share the project.

---

## Option A — Gemini demo on Render (free, interactive)

The lightweight FastAPI app in **Gemini mode** — no PyTorch, no OCR.

1. Get a free Gemini key at <https://aistudio.google.com/apikey>.
2. [render.com](https://render.com) → **New → Web Service** → connect this repo.
3. Set:
   - **Build**: Docker
   - **Dockerfile path**: `Dockerfile.api`
   - **Env vars**: `SUMMARY_PROVIDER=gemini`, `GEMINI_API_KEY=<key>`
4. Deploy and wait for the build (~2–4 min).

Full details: [DEPLOY_RENDER.md](DEPLOY_RENDER.md).

---

## Option B — Hugging Face static page (free)

Hugging Face's free tier only allows *Static* Spaces. The Space
`hardikpathak/doc-summarizer` hosts a static project landing page (screenshot +
results + GitHub link). It is informational, not interactive.

---

## Option C — Docker (local models)

```bash
docker build -t doc-summarizer .
docker run -p 8000:8000 doc-summarizer
```

This image includes PyTorch + the local models (~2 GB). Use `Dockerfile.api`
for the slim Gemini build instead.

---

## Notes

- Keep the Gemini key **server-side** (environment variable), never in the
  frontend.
- Render's free tier sleeps after inactivity; the first request may take
  ~30–60 s.
