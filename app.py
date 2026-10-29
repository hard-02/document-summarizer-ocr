"""Multilingual Document Summarizer — Streamlit demo.

Run with:
    streamlit run app.py

Supported inputs:
  * Documents (.txt / .pdf / .docx) -> abstractive summary
  * Images (.png / .jpg)             -> OCR -> summary
  * Pasted text                      -> abstractive summary

Languages: English, Hindi.

Set SUMMARY_PROVIDER=gemini + GEMINI_API_KEY (env var or Streamlit secrets) to
use the Gemini API backend, or leave it unset for the fine-tuned local models.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import streamlit as st

# Streamlit Cloud: expose secrets as env vars BEFORE importing src modules,
# because src/config.py reads them at import time.
try:
    _secrets = st.secrets
    for _key in ("SUMMARY_PROVIDER", "GEMINI_API_KEY", "GEMINI_MODEL"):
        try:
            _val = _secrets[_key]
        except Exception:
            continue
        if _val and not os.environ.get(_key):
            os.environ[_key] = str(_val)
except Exception:  # no secrets.toml present locally
    pass

from src.config import (  # noqa: E402
    GEMINI_API_KEY,
    LANGUAGES,
    SUMMARIZATION_MODELS,
    SUMMARY_PROVIDER,
)
from src.ocr import image_to_text_any  # noqa: E402
from src.summarizer import summarize  # noqa: E402
from src.text_extraction import extract_text  # noqa: E402

st.set_page_config(page_title="Document Summarizer", page_icon="📄", layout="wide")

if SUMMARY_PROVIDER == "gemini" and not GEMINI_API_KEY:
    st.error(
        "Gemini is selected but no API key was found. "
        "Add `GEMINI_API_KEY` in Streamlit Cloud → Manage app → Settings → Secrets, then reboot."
    )

LANG_LABELS = {name: code for code, name in LANGUAGES.items()}


@st.cache_resource(show_spinner=False)
def _warm_model(language: str):
    """Pre-load the local model (no-op for the Gemini backend)."""
    if SUMMARY_PROVIDER == "local":
        from src.summarizer import _load_pipeline  # noqa: PLC0415

        _load_pipeline(language)
    return True


def render_summary(text: str, language: str, min_length: int, max_length: int) -> None:
    if not text or not text.strip():
        st.warning("No text found to summarize.")
        return
    if len(text.strip()) < 40:
        st.info("Text is very short — the summary may just echo it back.")

    try:
        with st.spinner("Loading model…"):
            _warm_model(language)
        with st.spinner("Summarizing…"):
            summary = summarize(text, language, max_length=max_length, min_length=min_length)
        st.subheader("Summary")
        st.write(summary)
        st.download_button(
            "Download summary (.txt)",
            data=summary.encode("utf-8"),
            file_name="summary.txt",
            mime="text/plain",
        )
    except Exception as exc:  # noqa: BLE001
        st.error(f"Summarization failed: {exc}")


st.sidebar.title("Controls")
mode = st.sidebar.radio("Input type", ["📄 Document", "🖼️ Image", "✍️ Text"])
language_label = st.sidebar.selectbox("Summary language", list(LANG_LABELS), index=0)
language = LANG_LABELS[language_label]

st.sidebar.markdown("---")
st.sidebar.markdown("**Summary length**")
cfg = SUMMARIZATION_MODELS[language]
max_length = st.sidebar.slider(
    "Max words", min_value=20, max_value=cfg["max_target_tokens"], value=cfg["gen_kwargs"]["max_length"]
)
min_length = st.sidebar.slider(
    "Min words", min_value=5, max_value=max_length, value=min(cfg["gen_kwargs"]["min_length"], max_length)
)

st.sidebar.markdown("---")
if SUMMARY_PROVIDER == "gemini":
    st.sidebar.caption("Backend: **Gemini API** (text + vision OCR). No local models.")
else:
    st.sidebar.caption("Backend: **local fine-tuned models** (BART / IndicBART) + EasyOCR.")

st.title("📄 Multilingual Document Summarizer")
st.markdown(
    "Upload a document or image, or paste text, and get an abstractive summary in English or Hindi."
)

if mode == "📄 Document":
    uploaded = st.file_uploader("Upload a document", type=["txt", "pdf", "docx"], help=".txt, .pdf, or .docx")
    if uploaded is not None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / uploaded.name
            path.write_bytes(uploaded.getvalue())
            try:
                text = extract_text(path)
            except Exception as exc:  # noqa: BLE001
                st.error(f"Could not read the document: {exc}")
                st.stop()

        st.markdown(f"**Extracted {len(text):,} characters**")
        with st.expander("Show extracted text", expanded=False):
            st.text_area("Document text", text, height=250, label_visibility="collapsed")

        if st.button("Summarize document", type="primary"):
            render_summary(text, language, min_length, max_length)

elif mode == "🖼️ Image":
    uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], help="PNG / JPG / JPEG")
    if uploaded is not None:
        image_bytes = uploaded.getvalue()
        st.image(image_bytes, caption=uploaded.name, use_container_width=True)

        if st.button("Extract text & summarize", type="primary"):
            with st.spinner("Extracting text from image…"):
                try:
                    ocr_text = image_to_text_any(image_bytes=image_bytes, mime_type=uploaded.type or "image/png")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"OCR failed: {exc}")
                    st.stop()

            st.markdown(f"**Extracted {len(ocr_text):,} characters**")
            with st.expander("Show extracted text", expanded=False):
                st.text_area("OCR text", ocr_text, height=250, label_visibility="collapsed")

            render_summary(ocr_text, language, min_length, max_length)

else:
    pasted = st.text_area("Paste text to summarize", height=260, placeholder="Paste text here…")
    if st.button("Summarize text", type="primary"):
        render_summary(pasted, language, min_length, max_length)
