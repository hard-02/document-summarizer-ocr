"""Central configuration for the document summarizer + OCR app.

This file is intentionally dependency-light (stdlib only) so it can be
imported quickly by the Streamlit app before the heavy ML libraries load.
"""
from __future__ import annotations

import os
from pathlib import Path

# Project root = parent of the `src/` directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Directory where fine-tuned checkpoints live (git-ignored). Drop a folder
# here and the app will prefer it over the public Hugging Face checkpoint.
MODELS_DIR = Path(os.environ.get("MODELS_DIR", PROJECT_ROOT / "models"))


def resolve_device() -> str:
    """Return 'cuda' when a GPU is available, otherwise 'cpu'."""
    if os.environ.get("FORCE_CPU") == "1":
        return "cpu"
    try:
        import torch  # noqa: PLC0415 (deferred import)

        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


# ---------------------------------------------------------------------------
# Summarization models
# ---------------------------------------------------------------------------
# Keys are the language codes used by the app UI.
#   * model_id: public Hugging Face checkpoint used when no fine-tuned local
#     checkpoint is found in `MODELS_DIR / local_dir`.
#   * local_dir: sub-folder under `models/` that holds your fine-tuned weights
#     (e.g. from the Kaggle notebooks).
#   * lang_code: mBART-style language code used to force the decoder start
#     token (Indic models only).
SUMMARIZATION_MODELS = {
    "en": {
        "model_id": "facebook/bart-large-cnn",
        "local_dir": "english",
        "tokenizer_kwargs": {},
        "max_input_tokens": 1024,
        "max_target_tokens": 180,
        "gen_kwargs": {
            "num_beams": 4,
            "length_penalty": 2.0,
            "no_repeat_ngram_size": 3,
            "early_stopping": True,
            "min_length": 40,
            "max_length": 180,
        },
    },
    "hi": {
        "model_id": "ai4bharat/IndicBARTSS",
        "local_dir": "hindi",
        "lang_code": "hi_IN",
        "tokenizer_kwargs": {"do_lower_case": False, "use_fast": False},
        "max_input_tokens": 512,
        "max_target_tokens": 128,
        "gen_kwargs": {
            "num_beams": 4,
            "length_penalty": 1.0,
            "no_repeat_ngram_size": 3,
            "early_stopping": True,
            "min_length": 20,
            "max_length": 128,
        },
    },
    "mr": {
        "model_id": "ai4bharat/IndicBARTSS",
        "local_dir": "marathi",
        "lang_code": "mr_IN",
        "tokenizer_kwargs": {"do_lower_case": False, "use_fast": False},
        "max_input_tokens": 512,
        "max_target_tokens": 128,
        "gen_kwargs": {
            "num_beams": 4,
            "length_penalty": 1.0,
            "no_repeat_ngram_size": 3,
            "early_stopping": True,
            "min_length": 20,
            "max_length": 128,
        },
    },
}

# ---------------------------------------------------------------------------
# OCR (EasyOCR)
# ---------------------------------------------------------------------------
# EasyOCR language codes: 'en' English, 'hi' Hindi, 'mr' Marathi.
# The reader is built once and reused across requests.
OCR_LANGUAGES = ["en", "hi", "mr"]
