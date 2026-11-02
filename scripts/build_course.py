#!/usr/bin/env python3
"""Compile a XeLaTeX course, run structural preflight, and render every page.

No external network access, no bundled proprietary fonts. Preview requires
PyMuPDF and Pillow. The PDF remains available if optional preview is missing.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLES = ROOT / "templates"


def preflight_pdf(path: Path, preview: Path | None, dpi: int) -> dict:
    try:
        import fitz  # type: ignore
    except ImportError:
        print("[WARN] PyMuPDF unavailable: cannot check page dimensions or render previews.")
        return {"file": str(path), "structural_check": "skipped"}

    doc = fitz.open(path)
    if len(doc) == 0:
        raise RuntimeError("The generated PDF has zero pages")
    page_w, page_h = doc[0].rect.width, doc[0].rect.height
    if abs(page_w - 595.276) > 2 or abs(page_h - 841.89) > 2:
        raise RuntimeError("PDF is not A4 portrait. Visual design contract violated.")

    offpage_spans = []
    empty_pages = []
    for index, pg in enumerate(doc):
        if not pg.get_text().strip():
            empty_pages.append(index + 1)
        page_rect = pg.rect
        for block in pg.get_text("dict").get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    x0, y0, x1, y1 = span["bbox"]
                    if x0 < -0.5 or y0 < -0.5 or x1 > page_rect.width + .5 or y1 > page_rect.height + .5:
                        offpage_spans.append({"page": index + 1, "text": span["text"][:60],
                                              "bbox": [round(v, 1) for v in (x0, y0, x1, y1)]})

    metrics = {"file": str(path), "pages": len(doc), "size": "A4 portrait",
               "empty_pages": empty_pages, "off_page_text_spans": offpage_spans}
    if preview:
        try:
            from PIL import Image, ImageOps, ImageDraw, ImageFont
        except ImportError:
            print("[WARN] Pillow unavailable: full-page preview generation skipped.")
            doc.close()
            return metrics
        pages = preview / "pages"
        pages.mkdir(parents=True, exist_ok=True)
        small_images = []
        thumb_w = 370
        for n, pg in enumerate(doc, 1):
            pix = pg.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False)
            frame = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            frame.save(pages / f"page-{n:03d}.png", optimize=True)
            th = frame.copy()
            th.thumbnail((thumb_w, 525))
            small_images.append(th)
        ncol = 3
        gap = 22
        title_h = 24
        nrow = (len(small_images) + ncol - 1) // ncol
        canvas = Image.new("RGB", (ncol * (thumb_w + gap) + gap, nrow * (525 + title_h + gap) + gap), "#e9eef0")
        drawer = ImageDraw.Draw(canvas)
        for idx, th in enumerate(small_images):
            c, r = idx % ncol, idx // ncol
            x = gap + c * (thumb_w + gap)
            y = gap + r * (525 + title_h + gap)
            canvas.paste(th, (x + (thumb_w - th.width) // 2, y))
            drawer.text((x + 6, y + 526), f"Page {idx + 1}", fill="#193B54")
        canvas.save(preview / "contact-sheet.png", optimize=True)
        metrics["preview_dir"] = str(preview)
        metrics["all_pages_rendered"] = len(small_images)
    doc.close()
    return metrics


def main() -> int:
    p = argparse.ArgumentParser(description="Build a polished, verified first-principles course PDF")
    p.add_argument("source", type=Path, help="XeLaTeX lesson .tex file")
    p.add_argument("--out", type=Path, required=True, help="Final PDF path")
    p.add_argument("--preview", type=Path, help="Render all pages and contact-sheet.png")
    p.add_argument("--dpi", type=int, default=130, help="Preview resolution; default=130")
    p.add_argument("--strict", action="store_true", help="Treat any overfull/missing character warning as an error")
    args = p.parse_args()

    source = args.source.expanduser().resolve()
    dest = args.out.expanduser().resolve()
    preview = args.preview.expanduser().resolve() if args.preview else None
    if not source.is_file():
        p.error(f"Source file not found: {source}")
    if shutil.which("latexmk") is None or shutil.which("xelatex") is None:
        p.error("Required latexmk and xelatex not found. Install texlive-xetex, latexmk, ctex and Noto CJK fonts.")
    if not (STYLES / "course-style.sty").exists():
        p.error(f"Missing style file: {STYLES / 'course-style.sty'}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if preview:
        preview.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="first-principles-") as tmp:
        tmpdir = Path(tmp)
        env = os.environ.copy()
        env["TEXINPUTS"] = f"{STYLES}{os.pathsep}" + env.get("TEXINPUTS", "")
        cmd = ["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error",
               "-file-line-error", f"-outdir={tmpdir}", str(source)]
        print("[BUILD]", " ".join(cmd), flush=True)
        run = subprocess.run(cmd, cwd=source.parent, env=env, text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        log_path = tmpdir / f"{source.stem}.log"
        log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else run.stdout
        if run.returncode != 0:
            print(run.stdout[-11000:], file=sys.stderr)
            raise SystemExit(f"LaTeX failed (code {run.returncode}); inspect the log above.")
        pdf = tmpdir / f"{source.stem}.pdf"
        if not pdf.is_file() or pdf.stat().st_size < 1000:
            raise SystemExit("LaTeX finished without producing a valid PDF")
        shutil.copyfile(pdf, dest)

        counts = {
            "overfull_hbox": len(re.findall(r"Overfull \\hbox", log)),
            "overfull_vbox": len(re.findall(r"Overfull \\vbox", log)),
            "undefined_references": len(re.findall(r"(undefined references|Reference .* undefined)", log, re.IGNORECASE)),
            "missing_glyphs": len(re.findall(r"Missing character:", log)),
        }
        qa = preflight_pdf(dest, preview, args.dpi)
        qa["latex_warnings"] = counts
        qa["bytes"] = dest.stat().st_size
        report = (preview / "qa-report.json") if preview else dest.with_suffix(".qa.json")
        report.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[DONE] {dest} ({qa.get('pages', '?')} pages, {qa['bytes']} bytes)")
        print(f"[QA] warning counts={counts}; empty_pages={qa.get('empty_pages', [])}; off_page_text={len(qa.get('off_page_text_spans', []))}")
        print(f"[QA] report={report}")
        if qa.get('empty_pages') or qa.get('off_page_text_spans'):
            print("[WARN] Structural anomalies detected. Inspect rendered pages before delivery.")
        if args.strict and (any(counts.values()) or qa.get('off_page_text_spans') or qa.get('empty_pages')):
            raise SystemExit("Strict mode failed; fix log/structural warnings before delivery")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
