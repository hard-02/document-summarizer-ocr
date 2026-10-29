"""OCR wrapper.

Local mode uses EasyOCR (English + Hindi). The Gemini backend uses vision OCR
(see ``src.llm_api.extract_text_with_gemini``), so EasyOCR is not required for
the deployed demo — its import is deferred until a local OCR call is made.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

try:
    from .config import OCR_LANGUAGES
except ImportError:  # defensive: an older config without OCR settings
    OCR_LANGUAGES = ["en", "hi"]


@lru_cache(maxsize=1)
def get_reader(gpu: bool = False) -> Any:
    """Build (and cache) a single EasyOCR reader."""
    import easyocr  # noqa: PLC0415

    return easyocr.Reader(OCR_LANGUAGES, gpu=gpu)


def image_to_text(image: Any, gpu: bool = False) -> str:
    """Extract text from a PIL image or numpy array using EasyOCR."""
    import numpy as np  # noqa: PLC0415

    reader = get_reader(gpu)
    if hasattr(image, "convert"):  # PIL.Image
        image = np.array(image.convert("RGB"))

    arr = np.asarray(image)
    if arr.ndim == 3 and arr.shape[2] == 3:
        arr = arr[:, :, ::-1]  # EasyOCR expects BGR

    results = reader.readtext(arr, detail=0, paragraph=True)
    return "\n".join(line for line in results if line and line.strip())


def image_to_text_any(
    image: Any = None,
    image_bytes: bytes | None = None,
    mime_type: str = "image/png",
    gpu: bool = False,
) -> str:
    """Route OCR to Gemini vision (cloud) or EasyOCR (local).

    Callers can pass ``image_bytes`` in either mode; in local mode the bytes are
    converted to a PIL image automatically.
    """
    from .config import SUMMARY_PROVIDER  # noqa: PLC0415

    if SUMMARY_PROVIDER == "gemini":
        from .llm_api import extract_text_with_gemini  # noqa: PLC0415

        if image_bytes is None:
            import io  # noqa: PLC0415

            buf = io.BytesIO()
            image.save(buf, format="PNG")
            image_bytes = buf.getvalue()
        return extract_text_with_gemini(image_bytes, mime_type)

    if image is None and image_bytes is not None:
        import io  # noqa: PLC0415

        from PIL import Image  # noqa: PLC0415

        image = Image.open(io.BytesIO(image_bytes))
    return image_to_text(image, gpu=gpu)
