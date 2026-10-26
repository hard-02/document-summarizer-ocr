"""OCR wrapper around EasyOCR (English + Hindi + Marathi)."""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from .config import OCR_LANGUAGES


@lru_cache(maxsize=1)
def get_reader(gpu: bool = False) -> Any:
    """Build (and cache) a single EasyOCR reader.

    EasyOCR downloads its detection/recognition models on first use, so we
    keep exactly one reader per process.
    """
    import easyocr  # noqa: PLC0415

    return easyocr.Reader(OCR_LANGUAGES, gpu=gpu)


def image_to_text(image: Any, gpu: bool = False) -> str:
    """Extract text from a PIL image or numpy array.

    EasyOCR expects BGR (OpenCV-style) arrays; PIL images are converted
    automatically.
    """
    import numpy as np  # noqa: PLC0415

    reader = get_reader(gpu)

    if hasattr(image, "convert"):  # PIL.Image
        image = np.array(image.convert("RGB"))

    arr = np.asarray(image)
    # EasyOCR's readtext expects BGR; convert a 3-channel RGB array.
    if arr.ndim == 3 and arr.shape[2] == 3:
        arr = arr[:, :, ::-1]

    results = reader.readtext(arr, detail=0, paragraph=True)
    return "\n".join(line for line in results if line and line.strip())
