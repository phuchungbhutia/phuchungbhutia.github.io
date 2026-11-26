---
title: "Troubleshooting Python PDF Booklet Generation on Linux and Dual-Boot NTFS Drives"
date: "2026-11-26"
categories: ["Development", "Python"]
tags: ["python", "pymupdf", "linux", "troubleshooting", "pdf", "2026"]
description: "A detailed troubleshooting runbook covering PEP 668 environment blocks, NTFS permission errors, interpreter mismatches, and PyMuPDF 1.28+ DocumentWriter API migrations."
---

# Troubleshooting Python PDF Booklet Generation on Linux and Dual-Boot NTFS Drives

Building a zero-dependency Python CLI tool to render Markdown into A5 pages and impose them onto A4 landscape saddle-stitch booklets looks straightforward on paper. Run that project across a dual-boot Linux and Windows setup on a shared NTFS data drive, and you hit four distinct environment and API roadblocks back to back.

Here is the complete technical breakdown of every error encountered while getting `md2booklet` running on Manjaro Linux, why each failure happened under the hood, and the full production-ready codebase that resolves all of them.

## Error 1: `zsh: command not found: pip` and PEP 668 Environment Locks

Running `pip install -r requirements.txt` inside a fresh Arch or Manjaro terminal immediately fails because `pip` is omitted from minimal base Python installations. Even when `python-pip` is present, modern Linux distributions enforce **PEP 668** (`externally-managed-environment`), blocking global `pip install` calls so third-party wheels do not overwrite system packages managed by `pacman`.

### The Fix

You have two clean paths depending on whether you want system-wide availability or project isolation:

1. **System packages via `pacman` (Zero virtual environment overhead):**
   ```bash
   sudo pacman -S python-pymupdf python-markdown
   ```

2. **Project-local virtual environment (venv):**
   ```bash
   sudo pacman -S python-pip
   python -m venv .venv
   ./.venv/bin/pip install pymupdf markdown
   ```

## Error 2: `zsh: permission denied` on Shared NTFS Partitions

Storing code repositories on a shared Windows NTFS partition (such as `/mnt/Data/Projects/md2booklet`) introduces two subtle filesystem traps:

* **No POSIX execute bits:** Standard `ntfs-3g` or `fuseblk` mounts often strip executable (+x) flags or map directory permissions awkwardly, causing direct execution (`./script.py`) or local binary shims to throw `permission denied`.
* **Symlink restrictions:** Depending on mount flags, creating a Python venv directly on an NTFS volume can fail when Python attempts to symlink `/usr/bin/python` into `.venv/bin/python`.

### The Fix

First, confirm your partition is mounted read-write (`rw`) and not locked read-only by Windows Fast Startup:

```bash
mount | grep /mnt/Data
```

Look for `(rw,...)` in the output. If it shows `(ro,...)`, boot into Windows and disable Fast Startup, or remount manually (`sudo mount -o remount,rw /mnt/Data`).

Second, always invoke scripts through the explicit interpreter binary rather than relying on shebang execution on NTFS, or house your virtual environment inside your native Linux home directory (`~/.venvs/`):

```bash
python -m venv ~/.venvs/md2booklet
~/.venvs/md2booklet/bin/pip install pymupdf markdown
~/.venvs/md2booklet/bin/python -m src.main input/sample.md
```

## Error 3: `ModuleNotFoundError: No module named 'fitz'` After Installing via `pacman`

Installing `python-pymupdf` via `pacman` places the library inside `/usr/lib/python3.x/site-packages/`. If you run `python -m src.main` immediately afterward and still get `ModuleNotFoundError`, your shell is resolving `python` to a different interpreter—such as an active `.venv`, Conda environment, or `pyenv` shim.

### The Fix

Check which binary your shell is actually executing:

```bash
which python
```

If `which python` points to `/mnt/Data/Projects/md2booklet/.venv/bin/python` instead of `/usr/bin/python`, either call the system binary directly or install the packages explicitly into that active environment's `pip`:

```bash
# Option A: Use the system Python where pacman installed PyMuPDF
/usr/bin/python -m src.main input/sample.md

# Option B: Install directly into the active virtual environment
./.venv/bin/python -m pip install pymupdf markdown
```

## Error 4: `TypeError: in method 'fz_draw_story', argument 2 of type 'mupdf::FzDevice const &'`

Once `pymupdf` (1.28.x) loads, older snippets using `story.draw(page)` crash with a C++ binding `TypeError` inside `fz_draw_story`.

### Root Cause

In recent releases of PyMuPDF, `Story.draw()` no longer accepts a `fitz.Page` object directly. Instead, Story layouts must write into a `mupdf::FzDevice` managed by `pymupdf.DocumentWriter`. Additionally, `import fitz` now triggers a deprecation warning in favor of `import pymupdf`.

### The Fix

Route Story rendering through `pymupdf.DocumentWriter` backed by an `io.BytesIO` buffer. Once `writer.close()` flushes the pages to memory, reopen the stream with `pymupdf.open()` to stamp page footers and run the saddle-stitch imposition pass.

## Complete Production Code (`src/main.py`)

Below is the full, updated source code for `src/main.py`. It strips optional YAML front matter, renders Markdown directly to 1:1 A5 portrait pages via `DocumentWriter`, stamps centered footer page numbers on every page after the cover, and imposes the pages onto A4 landscape sheets in saddle-stitch order.

```python
import io
import re
import sys
import math
import argparse
import logging
from pathlib import Path
import markdown
import pymupdf

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("md2booklet")


def strip_front_matter(md_text: str) -> str:
    """Removes YAML front matter block (--- ... ---) if present at the top of the file."""
    return re.sub(r"\A---\s*\n.*?\n---\s*\n", "", md_text, flags=re.DOTALL)


def render_markdown_to_a5(md_path: Path, font_family: str, font_size: float) -> bytes:
    """Renders Markdown directly to A5 portrait pages in memory using PyMuPDF DocumentWriter."""
    raw_md = md_path.read_text(encoding="utf-8")
    clean_md = strip_front_matter(raw_md)

    html_body = markdown.markdown(
        clean_md,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
    )

    css = f"""
    body {{
        font-family: "{font_family}", sans-serif;
        font-size: {font_size}pt;
        line-height: 1.35;
        color: #111111;
    }}
    h1 {{
        font-size: {font_size * 1.6:.1f}pt;
        margin-top: 0;
        margin-bottom: 8pt;
        border-bottom: 1pt solid #cccccc;
        padding-bottom: 4pt;
    }}
    h2 {{
        font-size: {font_size * 1.3:.1f}pt;
        margin-top: 12pt;
        margin-bottom: 6pt;
    }}
    h3 {{
        font-size: {font_size * 1.1:.1f}pt;
        margin-top: 10pt;
        margin-bottom: 4pt;
    }}
    p {{
        margin-top: 0;
        margin-bottom: 8pt;
    }}
    ul, ol {{
        margin-top: 0;
        margin-bottom: 8pt;
        padding-left: 16pt;
    }}
    li {{
        margin-bottom: 3pt;
    }}
    blockquote {{
        margin: 8pt 0;
        padding: 4pt 10pt;
        border-left: 2.5pt solid #888888;
        color: #333333;
        background-color: #f9f9f9;
    }}
    pre, code {{
        font-family: monospace;
        font-size: {font_size * 0.85:.1f}pt;
        background-color: #f4f4f4;
    }}
    pre {{
        padding: 6pt;
        border: 0.5pt solid #dddddd;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 8pt 0;
        font-size: {font_size * 0.9:.1f}pt;
    }}
    th, td {{
        border: 0.5pt solid #bbbbbb;
        padding: 4pt 6pt;
        text-align: left;
    }}
    th {{
        background-color: #eeeeee;
        font-weight: bold;
    }}
    """

    full_html = (
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>{css}</style></head><body>{html_body}</body></html>"
    )

    # A5 portrait in points (148mm x 210mm)
    a5_rect = pymupdf.paper_rect("a5")
    mm = 72.0 / 25.4
    # Margins: Left=16mm (binding gutter), Top=14mm, Right=12mm, Bottom=14mm
    content_rect = pymupdf.Rect(
        16 * mm,
        14 * mm,
        a5_rect.width - (12 * mm),
        a5_rect.height - (14 * mm),
    )

    story = pymupdf.Story(html=full_html)
    buf = io.BytesIO()
    writer = pymupdf.DocumentWriter(buf)

    more = True
    while more:
        dev = writer.begin_page(a5_rect)
        more, _ = story.place(content_rect)
        story.draw(dev)
        writer.end_page()

    writer.close()

    # Reopen generated A5 stream to stamp page numbers (skipping cover page 1)
    out_doc = pymupdf.open(stream=buf.getvalue(), filetype="pdf")
    for page_num, page in enumerate(out_doc, start=1):
        if page_num > 1:
            footer_rect = pymupdf.Rect(
                0,
                a5_rect.height - (10 * mm),
                a5_rect.width,
                a5_rect.height - (4 * mm),
            )
            page.insert_textbox(
                footer_rect,
                str(page_num),
                fontsize=8,
                fontname="helv",
                color=(0.35, 0.35, 0.35),
                align=pymupdf.TEXT_ALIGN_CENTER,
            )

    pdf_bytes = out_doc.tobytes()
    out_doc.close()
    return pdf_bytes


def impose_to_a4_booklet(a5_pdf_bytes: bytes, output_path: Path) -> int:
    """Imposes A5 pages side-by-side onto A4 landscape sheets in saddle-stitch order."""
    src_doc = pymupdf.open(stream=a5_pdf_bytes, filetype="pdf")
    total_pages = len(src_doc)
    padded_total = math.ceil(total_pages / 4) * 4

    # A4 landscape in points (297mm x 210mm)
    a4_rect = pymupdf.paper_rect("a4-l")
    half_w = a4_rect.width / 2.0
    full_h = a4_rect.height

    left_slot = pymupdf.Rect(0, 0, half_w, full_h)
    right_slot = pymupdf.Rect(half_w, 0, a4_rect.width, full_h)

    booklet_doc = pymupdf.open()

    for sheet in range(padded_total // 4):
        # Front of physical sheet: [Last - 2*sheet, First + 2*sheet]
        front_left = padded_total - 1 - (2 * sheet)
        front_right = 2 * sheet

        # Back of physical sheet: [First + 2*sheet + 1, Last - 2*sheet - 1]
        back_left = 2 * sheet + 1
        back_right = padded_total - 2 - (2 * sheet)

        for left_idx, right_idx in [
            (front_left, front_right),
            (back_left, back_right),
        ]:
            sheet_page = booklet_doc.new_page(width=a4_rect.width, height=full_h)

            if left_idx < total_pages:
                sheet_page.show_pdf_page(left_slot, src_doc, left_idx)
            if right_idx < total_pages:
                sheet_page.show_pdf_page(right_slot, src_doc, right_idx)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    booklet_doc.save(str(output_path), garbage=4, deflate=True)
    sheet_count = padded_total // 4
    booklet_doc.close()
    src_doc.close()
    return sheet_count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Markdown to an A4 saddle-stitch PDF booklet."
    )
    parser.add_argument("input_md", help="Path to input .md file")
    parser.add_argument(
        "-f",
        "--font",
        default="sans-serif",
        help="Font family (default: sans-serif)",
    )
    parser.add_argument(
        "-s",
        "--size",
        type=float,
        default=10.0,
        help="Body font size in pt (default: 10.0)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Custom output PDF path (default: output/<name>_booklet.pdf)",
    )
    args = parser.parse_args()

    md_path = Path(args.input_md)
    if not md_path.is_file():
        log.error("File '%s' not found.", md_path)
        sys.exit(1)

    out_path = (
        Path(args.output)
        if args.output
        else Path("output") / f"{md_path.stem}_booklet.pdf"
    )

    log.info(
        "[1/2] Rendering '%s' to A5 pages (%s, %.1fpt)...",
        md_path.name,
        args.font,
        args.size,
    )
    a5_bytes = render_markdown_to_a5(md_path, args.font, args.size)

    log.info("[2/2] Imposing pages onto A4 landscape booklet...")
    sheets = impose_to_a4_booklet(a5_bytes, out_path)

    log.info("Done! Saved to: %s (%d A4 sheets)", out_path, sheets)
    log.info("Print tip: Enable Two-Sided printing and select 'Flip on Short Edge'.")


if __name__ == "__main__":
    main()
```

## One-Command Project Scaffold & Verification

To recreate the entire folder structure (`src/`, `input/`, `output/`, `requirements.txt`, and `src/__init__.py`) cleanly from scratch and run a verification build:

```bash
mkdir -p md2booklet/{src,input,output} && cd md2booklet
touch src/__init__.py

cat << 'EOF' > requirements.txt
pymupdf>=1.28.0
markdown>=3.7
EOF

cat << 'EOF' > input/sample.md
---
title: "Sample Booklet"
date: "2026-11-26"
---

# Saddle-Stitch Booklet Verification

This document tests direct **A5** rendering via `pymupdf.DocumentWriter` and saddle-stitch imposition onto **A4 landscape** sheets.

| Parameter | Value |
| :--- | :--- |
| Target Paper | A4 Landscape |
| Folded Page Size | A5 Portrait (1:1 scale) |
| Duplex Setting | **Flip on Short Edge** |
EOF
```

After saving `src/main.py` inside the `md2booklet/src/` directory, run the verification build using your active interpreter:

```bash
python -m src.main input/sample.md --font "Liberation Sans" --size 10
```

When printing the resulting `output/sample_booklet.pdf`, keep scaling at 100% (Actual Size) and select **Flip on Short Edge** in your duplex printer settings so the back sides align right-side up when folded.

## References

PyMuPDF Documentation
https://pymupdf.readthedocs.io/en/latest/

PEP 668 – Marking Python Base Environments as “Externally Managed”
https://peps.python.org/pep-0668/