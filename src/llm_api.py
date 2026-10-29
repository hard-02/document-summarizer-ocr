"""Gemini API summarization backend (standard library only).

No SDK dependency: calls the Gemini REST endpoint with ``urllib`` so the
deployed demo can run without PyTorch or Transformers.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from .config import GEMINI_API_KEY, GEMINI_ENDPOINT, GEMINI_MODEL

_LANG_NAMES = {"en": "English", "hi": "Hindi"}


def summarize_with_gemini(
    text: str,
    language: str,
    max_length: int | None = None,
    min_length: int | None = None,
) -> str:
    """Summarize ``text`` using the Gemini API and return the summary string."""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set")

    lang = _LANG_NAMES.get(language, "English")
    max_words = max_length or 120
    prompt = (
        f"Summarize the following text in {lang} in at most {max_words} words. "
        "Be concise and factual. Return only the summary, with no preamble or labels.\n\n"
        + text[:12000]
    )

    url = f"{GEMINI_ENDPOINT}/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 1024,
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
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:  # pragma: no cover - network dependent
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"Gemini API error {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:  # pragma: no cover - network dependent
        raise RuntimeError(f"Gemini API request failed: {exc.reason}") from exc

    try:
        parts = data["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError) as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Unexpected Gemini response: {json.dumps(data)[:300]}") from exc

    summary = "".join(part.get("text", "") for part in parts).strip()
    if not summary:
        raise RuntimeError("Gemini returned an empty summary")
    return summary
