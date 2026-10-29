# Deploy the lightweight demo (Gemini API backend)

Deploys the FastAPI web app in **Gemini mode** — no PyTorch, no OCR, no model
downloads. Build is fast and fits Render's free tier.

## 1. Get a Gemini API key

1. Open <https://aistudio.google.com/apikey>
2. Create an API key (free tier is fine) and copy it.

## 2. Deploy on Render (free)

1. Create a free account at <https://render.com>.
2. **New → Web Service** → connect this GitHub repository.
3. Settings:
   - **Build**: Docker
   - **Dockerfile path**: `Dockerfile.api`
   - **Region**: closest to you (e.g. Singapore for India)
4. **Environment variables**:
   - `SUMMARY_PROVIDER` = `gemini`
   - `GEMINI_API_KEY` = your key
   - `GEMINI_MODEL` = `gemini-3.5-flash` (default)
5. **Create Web Service** and wait for the build (~2–4 min).

Render gives you a URL like `https://doc-summarizer.onrender.com`.

> Note: Render's free tier spins down after inactivity, so the first request
> after a break may take ~30–60 s to wake up.

## 3. Run locally

```bash
pip install -r requirements-api.txt
SUMMARY_PROVIDER=gemini GEMINI_API_KEY=your_key \
  uvicorn web.server:app --port 8000
```

Open <http://127.0.0.1:8000>.

## 4. Switch back to local models

```bash
pip install -r requirements.txt
# leave SUMMARY_PROVIDER unset (defaults to "local")
uvicorn web.server:app --port 8000
```

## Notes

- The API key must stay **server-side**. Never put it in the HTML/JS.
- Gemini costs are negligible for this project (a few hundred summaries
  costs well under $0.10; the free tier may cover it entirely).
- Supported languages in the demo: **English** and **Hindi**.
