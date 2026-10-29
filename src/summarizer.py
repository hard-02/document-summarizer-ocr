"""Language-aware abstractive summarization.

Two backends are supported, selected by ``SUMMARY_PROVIDER``:

* ``local``  - fine-tuned BART (English) / IndicBART (Hindi) checkpoints.
* ``gemini`` - the Google Gemini API (no PyTorch required).

For the local backend, a fine-tuned checkpoint in ``models/<lang>`` is used
when present, otherwise the public Hugging Face checkpoint.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from .config import MODELS_DIR, SUMMARIZATION_MODELS, resolve_device


def _decoder_start_id(tokenizer: Any, lang_code: str) -> int | None:
    """Resolve the forced decoder-start token id for Indic (mBART-style) models."""
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


def _decode_clean(tokenizer: Any, output_ids: list[int]) -> str:
    """Decode generated ids, stripping special AND added control tokens."""
    skip = set(tokenizer.all_special_ids)
    for tok, tok_id in getattr(tokenizer, "added_tokens_encoder", {}).items():
        if tok.startswith("<"):
            skip.add(tok_id)

    keep = [i for i in output_ids if i not in skip]
    return tokenizer.decode(keep, skip_special_tokens=True).strip()


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
    return tokenizer, model


def _indic_inputs(tokenizer: Any, model: Any, text: str, lang_code: str, max_input_tokens: int):
    """Tokenize input for IndicBART using its required ``"<text> </s> <2xx>"`` format."""
    lang_tok = f"<2{lang_code[:2]}>"
    formatted = f"{text} </s> {lang_tok}"
    return tokenizer(
        formatted,
        add_special_tokens=False,
        max_length=max_input_tokens,
        truncation=True,
        return_tensors="pt",
    ).to(model.device)


def summarize(
    text: str,
    language: str,
    max_length: int | None = None,
    min_length: int | None = None,
) -> str:
    """Summarize ``text`` in the given language and return the summary string."""
    from .config import SUMMARY_PROVIDER  # noqa: PLC0415

    if SUMMARY_PROVIDER == "gemini":
        from .llm_api import summarize_with_gemini  # noqa: PLC0415

        return summarize_with_gemini(text, language, max_length=max_length, min_length=min_length)

    import torch  # noqa: PLC0415

    cfg = SUMMARIZATION_MODELS[language]
    tokenizer, model = _load_pipeline(language)

    gen_kwargs = dict(cfg["gen_kwargs"])
    if max_length is not None:
        gen_kwargs["max_length"] = max_length
    if min_length is not None:
        gen_kwargs["min_length"] = min_length
    gen_kwargs.setdefault("min_length", min(gen_kwargs.get("max_length", 64), 20))

    lang_code = cfg.get("lang_code")
    if lang_code:
        inputs = _indic_inputs(tokenizer, model, text, lang_code, cfg["max_input_tokens"])
        start_id = _decoder_start_id(tokenizer, lang_code)
        if start_id is not None:
            gen_kwargs["decoder_start_token_id"] = start_id
        for name, tok_name in (("pad_token_id", "<pad>"), ("bos_token_id", "<s>"), ("eos_token_id", "</s>")):
            gen_kwargs[name] = tokenizer.convert_tokens_to_ids(tok_name)
    else:
        inputs = tokenizer(
            text,
            max_length=cfg["max_input_tokens"],
            truncation=True,
            return_tensors="pt",
        ).to(model.device)

    with torch.no_grad():
        output_ids = model.generate(**inputs, **gen_kwargs)

    return _decode_clean(tokenizer, output_ids[0].tolist()).strip()
