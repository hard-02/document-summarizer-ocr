"""FastAPI backend for the Multilingual Document & Image Summarizer.

Serves:
  * a JSON API  (/api/*)
  * the static frontend (web/static/)

Run with:
    uvicorn web.server:app --reload
"""
from __future__ import annotations

import io
import sys
import tempfile
from pathlib import Path
from typing import Optional

# Make the repo root importable so we can reuse src/ modules.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.config import SUMMARIZATION_MODELS
from src.ocr import image_to_text
from src.summarizer import summarize
from src.text_extraction import extract_text

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Doc & Image Summarizer API", version="1.0.0")

# Allow local development from any origin (frontend is served same-origin anyway).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SummarizeTextRequest(BaseModel):
    text: str
    language: str = "en"
    max_length: Optional[int] = None
    min_length: Optional[int] = None


class SummaryResponse(BaseModel):
    language: str
    summary: str
    source_text: Optional[str] = None
    source_length: int


def _validate_language(language: str) -> str:
    language = (language or "en").strip().lower()
    if language not in SUMMARIZATION_MODELS:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")
    return language


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "languages": list(SUMMARIZATION_MODELS)}


@app.post("/api/summarize-text", response_model=SummaryResponse)
def summarize_text(req: SummarizeTextRequest) -> SummaryResponse:
    language = _validate_language(req.language)
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is empty")
    summary = summarize(text, language, req.max_length, req.min_length)
    return SummaryResponse(language=language, summary=summary, source_length=len(text))


@app.post("/api/summarize-document", response_model=SummaryResponse)
async def summarize_document(
    file: UploadFile = File(...),
    language: str = Form("en"),
    max_length: Optional[int] = Form(None),
    min_length: Optional[int] = Form(None),
) -> SummaryResponse:
    language = _validate_language(language)
    filename = file.filename or "document.txt"
    suffix = Path(filename).suffix.lower()
    data = await file.read()

    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(data)
            tmp_path = Path(tmp.name)
        text = extract_text(tmp_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)

    summary = summarize(text, language, max_length, min_length)
    return SummaryResponse(language=language, summary=summary, source_text=text, source_length=len(text))


@app.post("/api/ocr-summarize", response_model=SummaryResponse)
async def ocr_summarize(
    file: UploadFile = File(...),
    language: str = Form("en"),
    max_length: Optional[int] = Form(None),
    min_length: Optional[int] = Form(None),
) -> SummaryResponse:
    language = _validate_language(language)
    data = await file.read()

    try:
        from PIL import Image  # noqa: PLC0415

        image = Image.open(io.BytesIO(data))
        ocr_text = image_to_text(image)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"OCR failed: {exc}") from exc

    if not ocr_text.strip():
        raise HTTPException(status_code=422, detail="No text detected in the image")

    summary = summarize(ocr_text, language, max_length, min_length)
    return SummaryResponse(language=language, summary=summary, source_text=ocr_text, source_length=len(ocr_text))


# Serve the frontend last so /api/* routes take precedence.
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
