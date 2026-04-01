# Rijndael AES proposal — per-section PDFs and extractions

Source: `../AES.pdf` (AES Proposal: Rijndael, Daemen & Rijmen).

## Layout

Each top-level section (1–15) is in its own folder:

- `N_<ShortTitle>/SecN_AES.pdf` — clipped, self-contained PDF for that section only.
- `docling_extract.md` — Docling export with **formula enrichment** (LaTeX-style math where the pipeline detects equations). Embedded PDF text is used (`do_ocr=False` in Docling) for speed because this PDF has a good text layer.
- `OCR_supplement_600dpi.md` — Present for sections **2, 4, 7, and 8** (heavy math, matrices, figures). Built from **600 dpi** page renders + Tesseract OCR. Use alongside `docling_extract.md` when you need verbatim text from typeset matrix layouts.
- `pages_600dpi/` — PNG page images (600 dpi) for those OCR’d sections.

## Regenerate

From `docs/research/`:

```bash
.venv_aes/bin/python3 split_aes_sections.py
.venv_aes/bin/python3 extract_aes_docling_ocr.py
```

Re-run Docling/OCR from scratch:

```bash
FORCE=1 .venv_aes/bin/python3 extract_aes_docling_ocr.py
```

## Tooling venv

A local interpreter venv lives at `docs/research/.venv_aes` (Docling, PyMuPDF, Tesseract bindings). It is not part of the main `rdagent` package dependencies.
