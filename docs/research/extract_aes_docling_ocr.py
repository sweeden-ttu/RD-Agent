#!/usr/bin/env python3
"""
For each SecN_AES.pdf under docs/research/aes/*/:
  1) Docling -> docling_extract.md (embedded PDF text + formula enrichment; no full-page OCR).
  2) If math signal in native PDF text is not reflected in markdown, render 600 dpi PNGs
     and run Tesseract -> OCR_supplement_600dpi.md

The source Rijndael PDF has a good text layer; enabling Docling's do_ocr on every page is very slow
and redundant. Tesseract at 600 dpi is used only as a fallback for weak formula capture.

Usage:
  docs/research/.venv_aes/bin/python3 docs/research/extract_aes_docling_ocr.py
  FORCE=1 docs/research/.venv_aes/bin/python3 docs/research/extract_aes_docling_ocr.py
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import fitz
import pytesseract
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from PIL import Image

BASE = Path(__file__).resolve().parent
AES_ROOT = BASE / "aes"
DPI = 600
ZOOM = DPI / 72.0
TESSERACT = "/opt/homebrew/bin/tesseract"
FORCE = os.environ.get("FORCE", "").lower() in ("1", "true", "yes")

pytesseract.pytesseract.tesseract_cmd = TESSERACT

MATH_SIGNAL_RE = re.compile(
    r"⊕|⊗|GF\s*\(\s*2|m\(x\s*\)|xtime|polynomial|modulo|\^\s*\d|circulant|matrix",
    re.IGNORECASE,
)
LATEX_RE = re.compile(r"\$\$|\$[^\$\n]+\$|\\\(|\\\)|\\begin\{|\\\[|\\\]")


def _section_sort_key(d: Path) -> tuple[int, str]:
    pdfs = list(d.glob("Sec*_AES.pdf"))
    if not pdfs:
        return (999, d.name)
    m = re.search(r"Sec(\d+)_AES\.pdf", pdfs[0].name)
    n = int(m.group(1)) if m else 999
    return (n, d.name)


def _raw_pdf_text(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    try:
        return "\n".join(doc.load_page(i).get_text("text") for i in range(doc.page_count))
    finally:
        doc.close()


def _math_signal_count(text: str) -> int:
    return len(MATH_SIGNAL_RE.findall(text))


def _latexish_count(md: str) -> int:
    return len(LATEX_RE.findall(md)) + md.count("$$")


def _needs_ocr_supplement(raw: str, md: str, section_num: int) -> bool:
    """Heuristic OCR fallback; math-heavy sections always get 600 dpi OCR for matrix/figure text."""
    if section_num in (2, 4, 7, 8):
        return True
    sig = _math_signal_count(raw)
    lx = _latexish_count(md)
    if sig >= 6 and lx < 2:
        return True
    if raw.count("^") >= 12 and lx < 2:
        return True
    return False


def _render_pages_600dpi(pdf_path: Path, img_dir: Path) -> list[Path]:
    img_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    paths: list[Path] = []
    try:
        mat = fitz.Matrix(ZOOM, ZOOM)
        for i in range(doc.page_count):
            pix = doc.load_page(i).get_pixmap(matrix=mat, alpha=False)
            out = img_dir / f"page_{i+1:03d}_{DPI}dpi.png"
            pix.save(out.as_posix())
            paths.append(out)
    finally:
        doc.close()
    return paths


def _tesseract_pages(paths: list[Path]) -> str:
    parts: list[str] = []
    for p in paths:
        im = Image.open(p)
        txt = pytesseract.image_to_string(im, config="--oem 1 --psm 6")
        parts.append(f"## OCR page: {p.name}\n\n{txt.strip()}\n")
    return "\n".join(parts)


def main() -> int:
    if not AES_ROOT.is_dir():
        print(f"Missing {AES_ROOT}", file=sys.stderr)
        return 1

    opts = PdfPipelineOptions()
    opts.do_ocr = False
    opts.do_formula_enrichment = True

    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)},
    )

    section_dirs = sorted((p for p in AES_ROOT.iterdir() if p.is_dir()), key=_section_sort_key)
    for d in section_dirs:
        pdfs = list(d.glob("Sec*_AES.pdf"))
        if not pdfs:
            print(f"skip (no Sec*_AES.pdf): {d}")
            continue
        pdf_path = pdfs[0]
        m = re.search(r"Sec(\d+)_AES\.pdf", pdf_path.name)
        section_num = int(m.group(1)) if m else 0

        out_md = d / "docling_extract.md"
        if out_md.is_file() and not FORCE:
            print(f"skip docling (exists): {pdf_path.name}")
            md = out_md.read_text(encoding="utf-8")
        else:
            print(f"Docling: {pdf_path.name} ...")
            result = converter.convert(pdf_path.as_posix())
            md = result.document.export_to_markdown()
            out_md.write_text(md, encoding="utf-8")

        raw = _raw_pdf_text(pdf_path)
        ocr_out = d / "OCR_supplement_600dpi.md"
        if ocr_out.is_file() and not FORCE:
            print(f"  -> OCR supplement already present, skip")
            continue

        if _needs_ocr_supplement(raw, md, section_num):
            print(
                f"  -> OCR supplement (600 dpi); math_signal={_math_signal_count(raw)}, "
                f"latexish={_latexish_count(md)}"
            )
            img_dir = d / "pages_600dpi"
            paths = _render_pages_600dpi(pdf_path, img_dir)
            ocr_txt = _tesseract_pages(paths)
            ocr_out.write_text(ocr_txt, encoding="utf-8")
        else:
            print(
                f"  -> OCR skipped (math_signal={_math_signal_count(raw)}, latexish={_latexish_count(md)})"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
