"""Generate editor-style code screenshots for Appendix A of the report."""

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path(__file__).resolve().parent / "code_screenshots"
OUT_DIR.mkdir(exist_ok=True)

FONT_PATH = "/System/Library/Fonts/Menlo.ttc"
FONT_SIZE = 15
LINE_HEIGHT = 22
PAD = 18
GUTTER = 52

BG = (30, 34, 42)
TITLE_BG = (44, 49, 58)
BORDER = (58, 64, 74)
FG = (220, 223, 228)
COMMENT = (106, 153, 85)
STRING = (206, 145, 120)
KEYWORD = (86, 156, 214)
NUMBER = (181, 206, 168)
FUNC = (220, 220, 170)
LINENO = (110, 118, 129)

KEYWORDS = {
    "def", "class", "return", "if", "else", "elif", "for", "while", "in", "import",
    "from", "as", "with", "try", "except", "finally", "raise", "pass", "continue",
    "break", "and", "or", "not", "is", "None", "True", "False", "lambda", "yield",
    "assert", "async", "await", "global", "nonlocal",
}

TOKEN_RE = re.compile(
    r'(""".*?"""|\'\'\'.*?\'\'\'|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')'  # strings
    r"|(#[^\n]*)"                                                          # comments
    r"|(\b\d+(?:\.\d+)?\b)"                                                # numbers
    r"|([A-Za-z_]\w*)"                                                     # words
    r"|(\s+)"                                                              # whitespace
    r"|(.)"                                                                # anything
)


def colorize(line: str):
    """Return a list of (text, color) segments for a line of Python."""
    out = []
    for m in TOKEN_RE.finditer(line):
        string, comment, number, word, space, other = m.groups()
        if string is not None:
            out.append((string, STRING))
        elif comment is not None:
            out.append((comment, COMMENT))
        elif number is not None:
            out.append((number, NUMBER))
        elif word is not None:
            if word in KEYWORDS:
                out.append((word, KEYWORD))
            elif line[m.end():m.end() + 1] == "(":
                out.append((word, FUNC))
            else:
                out.append((word, FG))
        else:
            out.append((space if space is not None else other, FG))
    return out


def render(code: str, filename: str, out_path: Path) -> None:
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    lines = code.rstrip("\n").split("\n")

    probe = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(probe)
    char_w = d.textlength("M", font=font)
    body_w = int(max(d.textlength(ln, font=font) for ln in lines) + GUTTER + PAD * 2)
    width = max(body_w, 620)
    title_h = 34
    height = title_h + PAD + len(lines) * LINE_HEIGHT + PAD

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    # Title bar
    draw.rectangle([0, 0, width, title_h], fill=TITLE_BG)
    draw.line([0, title_h, width, title_h], fill=BORDER, width=1)
    for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = 18 + i * 18
        draw.ellipse([cx - 5, title_h // 2 - 5, cx + 5, title_h // 2 + 5], fill=col)
    small = ImageFont.truetype(FONT_PATH, 12)
    draw.text((84, title_h // 2 - 7), filename, font=small, fill=(170, 176, 186))

    # Code
    y = title_h + PAD
    for idx, line in enumerate(lines, 1):
        draw.text((PAD, y), f"{idx:>3}", font=font, fill=LINENO)
        x = PAD + GUTTER
        for text, color in colorize(line):
            draw.text((x, y), text, font=font, fill=color)
            x += d.textlength(text, font=font)
        y += LINE_HEIGHT

    # Border
    draw.rectangle([0, 0, width - 1, height - 1], outline=BORDER, width=1)
    img.save(out_path, "PNG")
    print("wrote", out_path.name, f"{width}x{height}")


SNIPPETS = {
    "01_summarizer": ("src/summarizer.py", '''def summarize(text, language, max_length=None, min_length=None):
    from .config import SUMMARY_PROVIDER
    if SUMMARY_PROVIDER == "gemini":
        from .llm_api import summarize_with_gemini
        return summarize_with_gemini(text, language, max_length=max_length,
                                     min_length=min_length)
    import torch
    cfg = SUMMARIZATION_MODELS[language]
    tokenizer, model = _load_pipeline(language)
    gen_kwargs = dict(cfg["gen_kwargs"])
    lang_code = cfg.get("lang_code")
    if lang_code:
        inputs = _indic_inputs(tokenizer, model, text, lang_code,
                               cfg["max_input_tokens"])
    else:
        inputs = tokenizer(text, max_length=cfg["max_input_tokens"],
                           truncation=True, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output_ids = model.generate(**inputs, **gen_kwargs)
    return _decode_clean(tokenizer, output_ids[0].tolist()).strip()'''),
    "02_ocr": ("src/ocr.py", '''def image_to_text_any(image=None, image_bytes=None,
                      mime_type="image/png", gpu=False):
    """Route OCR to Gemini vision (cloud) or EasyOCR (local)."""
    from .config import SUMMARY_PROVIDER
    if SUMMARY_PROVIDER == "gemini":
        from .llm_api import extract_text_with_gemini
        if image_bytes is None:
            import io
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            image_bytes = buf.getvalue()
        return extract_text_with_gemini(image_bytes, mime_type)
    if image is None and image_bytes is not None:
        import io
        from PIL import Image
        image = Image.open(io.BytesIO(image_bytes))
    return image_to_text(image, gpu=gpu)'''),
    "03_api": ("web/server.py", '''@app.post("/api/ocr-summarize", response_model=SummaryResponse)
async def ocr_summarize(
    file: UploadFile = File(...),
    language: str = Form("en"),
    max_length: Optional[int] = Form(None),
    min_length: Optional[int] = Form(None),
) -> SummaryResponse:
    language = _validate_language(language)
    data = await file.read()
    try:
        ocr_text = image_to_text_any(image_bytes=data,
                                     mime_type=file.content_type or "image/png")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"OCR failed: {exc}")
    if not ocr_text.strip():
        raise HTTPException(status_code=422, detail="No text detected")
    summary = summarize(ocr_text, language, max_length, min_length)
    return SummaryResponse(language=language, summary=summary,
                           source_text=ocr_text,
                           source_length=len(ocr_text))'''),
    "04_gemini": ("src/llm_api.py", '''def extract_text_with_gemini(image_bytes: bytes,
                             mime_type: str = "image/png") -> str:
    """OCR an image using Gemini's vision capability."""
    prompt = ("Extract all the text visible in this image. "
              "Return only the extracted text, preserving line breaks.")
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return _generate(
        [
            {"text": prompt},
            {"inline_data": {"mime_type": mime_type, "data": encoded}},
        ],
        max_tokens=2048,
    )'''),
}

for name, (filename, code) in SNIPPETS.items():
    render(code, filename, OUT_DIR / f"{name}.png")

print("done")
