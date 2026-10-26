"""Multilingual Document & Image Summarizer — Streamlit demo.

Run with:
    streamlit run app.py

Supported inputs:
  * Documents  (.txt / .pdf / .docx) -> abstractive summary
  * Images     (.png / .jpg / .jpeg) -> EasyOCR text extraction -> summary

Languages: English, Hindi, Marathi.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from src.config import SUMMARIZATION_MODELS
from src.ocr import image_to_text
from src.summarizer import summarize
from src.text_extraction import extract_text

st.set_page_config(page_title="Doc & Image Summarizer", page_icon="📄", layout="wide")

LANG_OPTIONS = {
    "English": "en",
    "Hindi (हिन्दी)": "hi",
    "Marathi (मराठी)": "mr",
}


@st.cache_resource(show_spinner=False)
def _warm_model(language: str):
    """Trigger a cached model load; returns a sentinel so Streamlit caches it."""
    from src.summarizer import _load_pipeline  # noqa: PLC0415

    _load_pipeline(language)
    return True


def render_summary(text: str, language: str, min_length: int, max_length: int) -> None:
    """Show the summary (loading the model on first call) with sensible errors."""
    if not text or not text.strip():
        st.warning("No text found to summarize.")
        return

    if len(text.strip()) < 40:
        st.info("Text is very short — the summary may just echo it back.")

    try:
        with st.spinner("Loading model (first run downloads weights)…"):
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
    except Exception as exc:  # noqa: BLE001 (show a friendly error to the user)
        st.error(f"Summarization failed: {exc}")


# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------
st.sidebar.title("Controls")
mode = st.sidebar.radio("Input type", ["📄 Document", "🖼️ Image"])
language_label = st.sidebar.selectbox("Summary language", list(LANG_OPTIONS), index=0)
language = LANG_OPTIONS[language_label]

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
st.sidebar.caption(
    "Models: BART-large-CNN (English) · IndicBART (Hindi/Marathi) · EasyOCR (en+hi+mr). "
    "Fine-tune your own weights with the notebooks in `notebooks/`."
)

st.title("📄 Multilingual Document & Image Summarizer")
st.markdown(
    "Upload a document or an image, pick a language, and get an abstractive "
    "summary. Images are first run through OCR (English + Hindi + Marathi)."
)

# ---------------------------------------------------------------------------
# Document mode
# ---------------------------------------------------------------------------
if mode == "📄 Document":
    uploaded = st.file_uploader(
        "Upload a document", type=["txt", "pdf", "docx"], help=".txt, .pdf, or .docx"
    )
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

# ---------------------------------------------------------------------------
# Image mode
# ---------------------------------------------------------------------------
else:
    uploaded = st.file_uploader(
        "Upload an image", type=["png", "jpg", "jpeg"], help="PNG / JPG / JPEG"
    )
    if uploaded is not None:
        from PIL import Image  # noqa: PLC0415

        image = Image.open(uploaded)
        st.image(image, caption=uploaded.name, use_container_width=True)

        if st.button("Extract text & summarize", type="primary"):
            with st.spinner("Running OCR (first run downloads EasyOCR models)…"):
                try:
                    ocr_text = image_to_text(image)
                except Exception as exc:  # noqa: BLE001
                    st.error(f"OCR failed: {exc}")
                    st.stop()

            st.markdown(f"**OCR extracted {len(ocr_text):,} characters**")
            with st.expander("Show OCR text", expanded=False):
                st.text_area("OCR text", ocr_text, height=250, label_visibility="collapsed")

            render_summary(ocr_text, language, min_length, max_length)
