"""Language-aware abstractive summarization.

Loads one (tokenizer, model) pair per language on first use and caches it.
Prefers a local fine-tuned checkpoint in ``models/<lang>`` when present,
otherwise falls back to the public Hugging Face checkpoint from ``config``.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from .config import MODELS_DIR, SUMMARIZATION_MODELS, resolve_device


def _decoder_start_id(tokenizer: Any, lang_code: str) -> int | None:
    """Resolve the forced decoder-start token id for Indic (mBART-style) models.

    Handles both tokenizer conventions:
      * mBART50-style ``tokenizer.lang_code_to_id["hi_IN"]``
      * IndicBART-style added tokens like ``<2hi>``
    """
    if not lang_code:
        return None

    lang_to_id = getattr(tokenizer, "lang_code_to_id", None) or {}
    if lang_code in lang_to_id:
        return int(lang_to_id[lang_code])

    tok = f"<2{lang_code[:2]}>"
    token_id = tokenizer.convert_tokens_to_ids(tok)
    if token_id != getattr(tokenizer, "unk_token_id", None):
        return int(token_id)

    return getattr(tokenizer, "bos_token_id", None)


@lru_cache(maxsize=None)
def _load_pipeline(language: str) -> tuple[Any, Any]:
    """Load and cache (tokenizer, model) for a language."""
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer  # noqa: PLC0415

    cfg = SUMMARIZATION_MODELS[language]
    local_dir = MODELS_DIR / cfg["local_dir"]
    model_id = str(local_dir) if local_dir.is_dir() else cfg["model_id"]

    tokenizer = AutoTokenizer.from_pretrained(model_id, **cfg["tokenizer_kwargs"])
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id).to(resolve_device())
    model.eval()

    # Pin the decoder language for Indic models so generations are in the
    # right script even when training/inference used a local checkpoint.
    start_id = _decoder_start_id(tokenizer, cfg.get("lang_code", ""))
    if start_id is not None:
        model.config.forced_bos_token_id = start_id

    return tokenizer, model


def summarize(
    text: str,
    language: str,
    max_length: int | None = None,
    min_length: int | None = None,
) -> str:
    """Summarize ``text`` in the given language and return the summary string."""
    import torch  # noqa: PLC0415

    cfg = SUMMARIZATION_MODELS[language]
    tokenizer, model = _load_pipeline(language)

    inputs = tokenizer(
        text,
        max_length=cfg["max_input_tokens"],
        truncation=True,
        return_tensors="pt",
    ).to(model.device)

    gen_kwargs = dict(cfg["gen_kwargs"])
    if max_length is not None:
        gen_kwargs["max_length"] = max_length
    if min_length is not None:
        gen_kwargs["min_length"] = min_length
    gen_kwargs.setdefault("min_length", min(gen_kwargs.get("max_length", 64), 20))

    with torch.no_grad():
        output_ids = model.generate(**inputs, **gen_kwargs)

    summary = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return summary.strip()
