#!/usr/bin/env python3
"""
Split the Rijndael AES proposal PDF into 15 top-level section PDFs using PyMuPDF clips.
Run from repo root or any cwd; paths are absolute below.
"""

from __future__ import annotations

import sys
from pathlib import Path

import fitz  # PyMuPDF

BASE = Path(__file__).resolve().parent
SRC_PDF = BASE / "AES.pdf"
OUT_ROOT = BASE / "aes"

SECTIONS: list[tuple[int, str, str]] = [
    (1, "1. Introduction", "1_Introduction"),
    (2, "2. Mathematical preliminaries", "2_Mathematical_Preliminaries"),
    (3, "3. Design rationale", "3_Design_Rationale"),
    (4, "4. Specification", "4_Specification"),
    (5, "5. Implementation aspects", "5_Implementation_Aspects"),
    (6, "6. Performance figures", "6_Performance_Figures"),
    (7, "7. Motivation for design choices", "7_Motivation_For_Design_Choices"),
    (8, "8. Strength against known attacks", "8_Strength_Against_Known_Attacks"),
    (9, "9. Expected strength", "9_Expected_Strength"),
    (10, "10. Security goals", "10_Security_Goals"),
    (11, "11. Advantages and limitations", "11_Advantages_And_Limitations"),
    (12, "12. Extensions", "12_Extensions"),
    (13, "13. Other functionality", "13_Other_Functionality"),
    (14, "14. Suitability for ATM, HDTV, B-ISDN, voice and satellite", "14_Suitability_ATM_HDTV_BISDN"),
    (15, "15. Acknowledgements", "15_Acknowledgements"),
]

END_AFTER_15 = "16. References"


def _find_phrase_rect(page: fitz.Page, phrase: str) -> fitz.Rect | None:
    hits = page.search_for(phrase)
    return hits[0] if hits else None


def _collect_starts(doc: fitz.Document) -> list[tuple[int, fitz.Rect, str]]:
    """Return (0-based page index, rect of title, phrase) for each section body start (PDF page >= 4)."""
    out: list[tuple[int, fitz.Rect, str]] = []
    for _n, phrase, _slug in SECTIONS:
        found = None
        for pno in range(3, doc.page_count):  # skip TOC pages 1–3
            r = _find_phrase_rect(doc.load_page(pno), phrase)
            if r:
                found = (pno, r, phrase)
                break
        if not found:
            raise RuntimeError(f"Could not locate section title: {phrase!r}")
        out.append(found)
    return out


def _end_after_section_15(doc: fitz.Document) -> tuple[int, fitz.Rect]:
    for pno in range(3, doc.page_count):
        r = _find_phrase_rect(doc.load_page(pno), END_AFTER_15)
        if r:
            return pno, r
    raise RuntimeError(f"Could not locate {END_AFTER_15!r}")


def _build_page_clips(
    doc: fitz.Document,
    sp: int,
    sy0: float,
    ep: int,
    ey0: float,
) -> list[tuple[int, fitz.Rect]]:
    """Inclusive page range [sp, ep] with vertical clips: section starts at sy0 on sp, ends before ey0 on ep."""
    clips: list[tuple[int, fitz.Rect]] = []
    if sp > ep:
        raise ValueError("invalid range")
    if sp == ep:
        page = doc.load_page(sp)
        r = page.rect
        clip = fitz.Rect(r.x0, sy0, r.x1, ey0)
        return [(sp, clip)]

    # First page: sy0 -> bottom
    p0 = doc.load_page(sp)
    r0 = p0.rect
    clips.append((sp, fitz.Rect(r0.x0, sy0, r0.x1, r0.y1)))
    for mid in range(sp + 1, ep):
        pm = doc.load_page(mid)
        rm = pm.rect
        clips.append((mid, rm))
    # Last page: top -> ey0
    pe = doc.load_page(ep)
    re = pe.rect
    clips.append((ep, fitz.Rect(re.x0, re.y0, re.x1, ey0)))
    return clips


def _write_section_pdf(doc: fitz.Document, clips: list[tuple[int, fitz.Rect]], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    out = fitz.open()
    try:
        for pno, clip in clips:
            src_page = doc.load_page(pno)
            w, h = clip.width, clip.height
            new_page = out.new_page(width=w, height=h)
            new_page.show_pdf_page(new_page.rect, doc, pno, clip=clip)
        out.save(dest, deflate=True)
    finally:
        out.close()


def main() -> int:
    if not SRC_PDF.is_file():
        print(f"Missing source PDF: {SRC_PDF}", file=sys.stderr)
        return 1
    doc = fitz.open(SRC_PDF)
    try:
        starts = _collect_starts(doc)
        end_p, end_r = _end_after_section_15(doc)
        for i, ((_num, _phrase, slug), (sp, srect, _ph)) in enumerate(zip(SECTIONS, starts, strict=True)):
            if i < len(starts) - 1:
                ep, erect = starts[i + 1][0], starts[i + 1][1]
                ey0 = erect.y0
            else:
                ep, ey0 = end_p, end_r.y0
            clips = _build_page_clips(doc, sp, srect.y0, ep, ey0)
            out_dir = OUT_ROOT / slug
            out_pdf = out_dir / f"Sec{SECTIONS[i][0]}_AES.pdf"
            _write_section_pdf(doc, clips, out_pdf)
            print(f"Wrote {out_pdf} ({len(clips)} page(s))")
    finally:
        doc.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
