#!/usr/bin/env python3
"""Render original paper PDFs and crop the two main tables without redrawing them.

Requirements: Tectonic (for --compile), Poppler, pymupdf, Pillow.
Run from any directory; all default paths are relative to this project.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

import pymupdf
from PIL import Image


SITE = Path(__file__).resolve().parents[1]
WORKSPACE = SITE.parent
SOURCE = WORKSPACE / "CVPR2027__Arxiv_"
BUILD = WORKSPACE / "tmp" / "pdfs"
ASSETS = SITE / "assets"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_paper():
    staging = BUILD / "latex-source"
    shutil.copytree(SOURCE, staging, dirs_exist_ok=True)
    main = staging / "main.tex"
    text = main.read_text()
    # The source targets pdfLaTeX's OT1 Times fonts. Tectonic defaults to TU;
    # select OT1 in the temporary copy to avoid substituting Latin Modern.
    declaration = r"\documentclass[10pt,twocolumn,letterpaper]{article}"
    if text.count(declaration) != 1:
        raise RuntimeError("Document class changed; review the font compatibility wrapper.")
    main.write_text(text.replace(declaration, declaration + "\n" + r"\usepackage[OT1]{fontenc}"))
    subprocess.run([
        "tectonic", "--keep-logs", "--keep-intermediates",
        "--outdir", str(BUILD), "main.tex",
    ], cwd=staging, check=True)
    log = (BUILD / "main.log").read_text()
    if "LaTeX Font Warning" in log or "Missing character" in log:
        raise RuntimeError("Inspect font warnings before exporting the figures.")


def render(name, width=3200):
    pdf = ASSETS / "pdf" / f"{name}.pdf"
    png_base = ASSETS / "figures" / name
    subprocess.run([
        "pdftoppm", "-f", "1", "-singlefile", "-png",
        "-scale-to-x", str(width), "-scale-to-y", "-1",
        str(pdf), str(png_base),
    ], check=True, capture_output=True)
    image = png_base.with_suffix(".png")
    with Image.open(image) as img:
        dimensions = list(img.size)
    print(f"Rendered {name}: {dimensions[0]} × {dimensions[1]}")
    return {"pdf": str(pdf.relative_to(SITE)), "png": str(image.relative_to(SITE)),
            "pdf_sha256": digest(pdf), "png_sha256": digest(image), "pixels": dimensions}


def crop_table(document, aux, label, name, expected_number):
    match = re.search(r"\\newlabel\{" + re.escape(label) + r"\}\{\{(\d+)\}\{(\d+)\}", aux)
    if not match:
        raise RuntimeError(f"Missing cross-reference: {label}")
    number, page_number = map(int, match.groups())
    if number != expected_number:
        raise RuntimeError(f"Table numbering changed: {label} is now Table {number}.")
    page = document[page_number - 1]
    captions = [b for b in page.get_text("blocks") if b[4].startswith(f"Table {number}.")]
    if len(captions) != 1:
        raise RuntimeError(f"Cannot uniquely locate Table {number}'s caption.")
    caption = pymupdf.Rect(captions[0][:4])
    rules = sorted([
        d for d in page.get_drawings()
        if d["rect"].width > page.rect.width * .55
        and d["rect"].height < 1 and d["width"] > 0
        and d["rect"].y0 > caption.y1
    ], key=lambda d: d["rect"].y0)
    if not rules:
        raise RuntimeError(f"Cannot locate Table {number}'s top rule.")
    top = rules[0]
    bottom_candidates = [d for d in rules[1:]
                         if abs(d["width"] - top["width"]) < .04
                         and abs(d["rect"].width - top["rect"].width) < 1
                         and d["rect"].y0 > top["rect"].y0 + 20]
    if not bottom_candidates:
        raise RuntimeError(f"Cannot locate Table {number}'s bottom rule.")
    bottom = bottom_candidates[0]
    box = pymupdf.Rect(min(caption.x0, top["rect"].x0) - 3, caption.y0 - 3,
                       max(caption.x1, top["rect"].x1) + 3, bottom["rect"].y1 + 3)
    cropped = pymupdf.open()
    output_page = cropped.new_page(width=box.width, height=box.height)
    output_page.show_pdf_page(output_page.rect, document, page_number - 1, clip=box)
    cropped.set_metadata({"title": f"ReAccess — Table {number}",
                          "subject": captions[0][4].strip()})
    cropped.save(ASSETS / "pdf" / f"{name}.pdf", garbage=4, deflate=True)
    cropped.close()
    record = render(name)
    record.update({"source": "main.tex (compiled)", "table_source": f"table/{'main' if number == 2 else 'baseline'}.tex",
                   "latex_label": label, "table_number": number,
                   "paper_page": page_number, "crop_box_pdf_points": list(box),
                   "caption": captions[0][4].strip()})
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--compile", action="store_true", help="Compile a temporary copy with the original Times font encoding.")
    args = parser.parse_args()
    BUILD.mkdir(parents=True, exist_ok=True)
    (ASSETS / "pdf").mkdir(parents=True, exist_ok=True)
    (ASSETS / "figures").mkdir(parents=True, exist_ok=True)
    if args.compile:
        compile_paper()
    paper = BUILD / "main.pdf"
    aux_file = BUILD / "main.aux"
    if not paper.exists() or not aux_file.exists():
        raise SystemExit("Compile the manuscript first: run this script with --compile.")
    log = (BUILD / "main.log").read_text()
    if "LaTeX Font Warning" in log or "Missing character" in log:
        raise SystemExit("Font substitutions detected. Rerun with --compile before exporting.")
    shutil.copy2(paper, ASSETS / "pdf" / "reaccess-paper.pdf")
    records = {}
    for name in ["motivation", "framework", "visualization", "efficiency"]:
        source = SOURCE / "figure" / f"{name}.pdf"
        copied = ASSETS / "pdf" / f"{name}.pdf"
        shutil.copy2(source, copied)
        assert digest(source) == digest(copied)
        record = render(name, 2400 if name == "efficiency" else 3200)
        record.update({"source": f"figure/{name}.pdf", "source_sha256": digest(source), "original_pdf_unchanged": True})
        records[name] = record
    aux = aux_file.read_text()
    with pymupdf.open(paper) as document:
        records["table2"] = crop_table(document, aux, "tab:main_results", "table2", 2)
        records["table3"] = crop_table(document, aux, "tab:baseline_comparison", "table3", 3)
        pages = len(document)
    html_path = SITE / "index.html"
    html = html_path.read_text()
    for name, record in records.items():
        pattern = r'<img\b(?=[^>]*\bsrc="assets/figures/' + re.escape(name) + r'\.png")[^>]*>'
        def dimensions(match):
            tag = re.sub(r'\s(?:width|height)="[^"]*"', '', match.group())
            return tag[:-1] + f' width="{record["pixels"][0]}" height="{record["pixels"][1]}">'
        html, count = re.subn(pattern, dimensions, html)
        assert count == 1, f"Expected one image element for {name}, got {count}"
    html_path.write_text(html)
    provenance = {"source_project": "../CVPR2027__Arxiv_", "paper_pages": pages,
                  "paper_sha256": digest(paper),
                  "compilation": "Tectonic; OT1 font encoding added only to a temporary source copy to preserve pdfLaTeX Times fonts.",
                  "rendering": "Poppler pdftoppm; PDF figures copied unchanged; tables cropped from compiled paper without redrawing.",
                  "assets": records}
    (ASSETS / "provenance.json").write_text(json.dumps(provenance, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
