"""Gemini API backend (standard library only).

Provides:
  * ``summarize_with_gemini(text, language, ...)``  — text summarization
  * ``extract_text_with_gemini(image_bytes, mime_type)`` — vision OCR
"""
from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request

from .config import GEMINI_API_KEY, GEMINI_ENDPOINT, GEMINI_MODEL

_LANG_NAMES = {"en": "English", "hi": "Hindi"}


def _generate(parts: list[dict], max_tokens: int = 1024) -> str:
    """Send ``parts`` to the Gemini API and return the generated text."""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set")

    url = f"{GEMINI_ENDPOINT}/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.2,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:  # pragma: no cover - network dependent
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"Gemini API error {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:  # pragma: no cover - network dependent
        raise RuntimeError(f"Gemini API request failed: {exc.reason}") from exc

    try:
        parts_out = data["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError) as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Unexpected Gemini response: {json.dumps(data)[:300]}") from exc

    text = "".join(part.get("text", "") for part in parts_out).strip()
    if not text:
        raise RuntimeError("Gemini returned an empty response")
    return text


def summarize_with_gemini(
    text: str,
    language: str,
    max_length: int | None = None,
    min_length: int | None = None,
) -> str:
    """Summarize ``text`` using the Gemini API and return the summary string."""
    lang = _LANG_NAMES.get(language, "English")
    max_words = max_length or 120
    prompt = (
        f"Summarize the following text in {lang} in at most {max_words} words. "
        "Be concise and factual. Return only the summary, with no preamble or labels.\n\n"
        + text[:12000]
    )
    return _generate([{"text": prompt}], max_tokens=1024)


def extract_text_with_gemini(image_bytes: bytes, mime_type: str = "image/png") -> str:
    """OCR an image using Gemini's vision capability."""
    prompt = (
        "Extract all the text visible in this image. Return only the extracted text, "
        "preserving line breaks. Do not add commentary or labels."
    )
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return _generate(
        [
            {"text": prompt},
            {"inline_data": {"mime_type": mime_type, "data": encoded}},
        ],
        max_tokens=2048,
    )
