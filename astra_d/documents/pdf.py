"""PDF text extraction with OCR fallback and content-hash caching."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler\Release-26.02.0-0\poppler-26.02.0\Library\bin"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

CACHE_DIRNAME = "pdf_cache"


def _data_dir() -> Path:
    override = os.environ.get("ASTRA_D_DATA_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "data"


def _cache_dir() -> Path:
    path = _data_dir() / CACHE_DIRNAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def file_hash(file_path: str) -> str:
    """Return a sha256 hash of the file's contents (not its path)."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _cache_path(hash_value: str) -> Path:
    return _cache_dir() / f"{hash_value}.txt"


def read_pdf(file_path: str, use_cache: bool = True) -> str:
    """
    Extract text from PDF.

    Tries normal text extraction first, then OCR fallback.
    Results are cached by file content hash so unchanged files
    never trigger OCR twice.
    """
    hash_value = file_hash(file_path)
    cache_file = _cache_path(hash_value)

    if use_cache and cache_file.exists():
        print("Using cached extracted text (no OCR/extraction re-run).")
        return cache_file.read_text(encoding="utf-8")

    text = ""

    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if text.strip():
            print("Using PDF text extraction")
            cache_file.write_text(text.strip(), encoding="utf-8")
            return text.strip()

    except Exception as e:
        print(f"PDF extraction failed: {e}")

    print("No text found. Running OCR...")

    images = convert_from_path(file_path, poppler_path=POPPLER_PATH)

    ocr_text = ""
    for i, image in enumerate(images, start=1):
        print(f"OCR page {i}/{len(images)}")
        page_text = pytesseract.image_to_string(image)
        if page_text:
            ocr_text += page_text + "\n"

    ocr_text = ocr_text.strip()
    cache_file.write_text(ocr_text, encoding="utf-8")
    return ocr_text