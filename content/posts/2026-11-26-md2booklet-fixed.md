---
title: "Fixing PDF-Extracted Markdown Tables, Indentation, and A5 Saddle-Stitch Booklets in Python"
description: "A complete Python pipeline to clean PDF-extracted Markdown, format justified paragraphs, repair broken tables, and impose A5 pages onto A4 saddle-stitch booklets."
date: 2026-11-26 12:00:00 +0000
categories: [Python, PDF Processing, Automation]
tags: [pymupdf, markdown, pdf-to-markdown, booklet-imposition, cli-tools]
---

# Fixing PDF-Extracted Markdown Tables, Indentation, and A5 Saddle-Stitch Booklets in Python

Converting dense government rules, schedules, and financial compendiums from PDF into clean Markdown frequently breaks down. Raw text extraction leaves behind page folios, flattened clauses, and fragmented tables. This guide provides a self-contained Python pipeline that cleans raw dumps, formats justified paragraphs, repairs tables, and imposes A5 pages onto A4 landscape sheets for duplex printing.

## Why PDF-to-Markdown Dumps Break Booklet Rendering

When regulatory documents or schedules are converted from PDF to Markdown, four structural problems commonly appear.

* **Embedded page numbers:** Standalone folios, hyphenated page markers, or numbers glued directly to adjacent words remain inside the text stream and clash with new booklet page numbers.
* **Stacked lines and missing indentation:** Rules, sub-clauses, chapters, and appendices get merged into single long blocks. Plain leading spaces in Markdown collapse in HTML unless styled with explicit CSS margins.
* **Broken Markdown tables:** Multi-line table cells wrap across lines without pipe delimiters, mid-table separator rows appear inside bodies, or the first line of a row lacks leading pipes.
* **A5 column clipping:** A standard A5 page leaves roughly 120mm of printable width after binding. Wide schedule tables overflow unless fixed table layouts and word-wrapping are set in CSS.

## Architecture of the Solution

The script splits processing into three clear stages.

* **Text and Table Sanitizer:** Strips old page markers, un-stacks chapters and sub-clauses, wraps sub-clauses in styled HTML containers, and reconstructs multi-line or pipe-incomplete rows into valid Markdown tables.
* **A5 Story Renderer:** Converts cleaned Markdown to HTML, applies justified paragraphs with first-line indents, fits tables to A5 width via `pymupdf.Story`, and stamps sequential page numbers on page 2 onward.
* **A4 Saddle-Stitch Imposer:** Pads the A5 page count to a multiple of four and places page pairs onto A4 landscape sheets so printing two-sided with short-edge flipping produces a foldable booklet.

## Complete Python Pipeline

The complete script is provided below.

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
    """Removes YAML front matter block if present at the top of the file."""
    return re.sub(r"\A---\s*\n.*?\n---\s*\n", "", md_text, flags=re.DOTALL)


def _clean_ws(s: str) -> str:
    """Collapses repeated whitespace into a single space."""
    return re.sub(r"\s+", " ", s).strip()


def clean_pdf_dump_text(text: str) -> str:
    """
    Cleans raw PDF-extracted text:
    - Strips old inline and standalone page numbers
    - Un-stacks rules, sub-clauses, chapters, appendices, and department headings
    - Indents sub-clauses cleanly using HTML divs so PyMuPDF Story renders indents
    - Reconstructs Markdown tables even when the first line of a row lacks pipes
    """
    text = re.sub(r"(?m)^\s*-?\s*\d{1,3}\s*-?\s*$", "", text)
    text = re.sub(r"(?:^|\s)-\s*\d{1,3}\s*-(?=\s|$|[.,;:])", " ", text)
    text = re.sub(r"(?<=[.;:])\s*-\s*\d{1,3}\s*-", "", text)
    text = re.sub(r"\b\d{1,3}(?=(?:Department|Chapter|Appendix|settlement)\b)", "", text)

    text = re.sub(r"\s+(?=(?:Chapter\s+[IVXLC]+|Appendix\s+\d+)\b)", "\n\n", text)
    text = re.sub(r"(?<!^)(?<!\n)\s+(?=\d{1,3}\s+[A-Z][A-Z0-9\s/&(),.-]{4,}(?=\s+(?:\([a-z]\)|[A-Z][a-z]+|\|)))", "\n\n### ", text)
    text = re.sub(r"(?<!^)(?<!\n)\s+(?=\d{1,3}\.\s+[A-Z][A-Za-z0-9\s,'\"()/-]{2,70}\s*(?::\s*-|:-|:))", "\n\n", text)
    text = re.sub(r"(?<=[.;:])\s+(?=\((?:\d+|[a-z]{1,2}|i{1,3}|iv|v|vi{0,3})\)\s+)", "\n", text)

    lines = text.splitlines()
    out_lines: list[str] = []
    table_buffer: list[str] = []
    pending_row_prefix: str = ""

    def flush_table() -> None:
        nonlocal table_buffer, pending_row_prefix
        if pending_row_prefix:
            if table_buffer:
                table_buffer.append(pending_row_prefix)
            else:
                out_lines.append(pending_row_prefix)
            pending_row_prefix = ""

        if not table_buffer:
            return

        parsed_rows: list[list[str]] = []
        for raw in table_buffer:
            s = raw.strip()
            if re.fullmatch(r"\|?[\s\-:|]+\|?", s) and "-" in s:
                continue

            if "|" in s:
                inner = s.strip("|")
                cells = [_clean_ws(c) for c in inner.split("|")]
            elif "\t" in s:
                cells = [_clean_ws(c) for c in s.split("\t")]
            elif re.search(r"\s{3,}", s):
                cells = [_clean_ws(c) for c in re.split(r"\s{3,}", s)]
            else:
                if parsed_rows:
                    last_row = parsed_rows[-1]
                    idx = len(last_row) - 1
                    while idx > 0 and not last_row[idx]:
                        idx -= 1
                    last_row[idx] = _clean_ws(f"{last_row[idx]} {s}")
                continue

            target_cols = len(parsed_rows[0]) if parsed_rows else max(2, len(cells))
            if len(cells) < target_cols:
                cells.extend([""] * (target_cols - len(cells)))
            elif len(cells) > target_cols and parsed_rows:
                head = cells[: target_cols - 1]
                tail = " ".join(c for c in cells[target_cols - 1 :] if c)
                cells = head + [tail]

            parsed_rows.append(cells)

        non_empty_cols = {c_idx for row in parsed_rows for c_idx, val in enumerate(row) if val}

        if len(parsed_rows) >= 2 and len(non_empty_cols) >= 2:
            col_count = len(parsed_rows[0])
            first_cell = parsed_rows[0][0]
            if re.match(r"^(\([a-z0-9]+\)|\d+\.)", first_cell):
                default_headers = [f"Col {i + 1}" for i in range(col_count)]
                if col_count == 4:
                    default_headers = ["Nature of Power / Item", "Authority", "Extent", "Conditions / Remarks"]
                elif col_count == 3:
                    default_headers = ["Sl. No.", "Description", "Retention / Details"]
                parsed_rows.insert(0, default_headers)

            out_lines.append("")
            out_lines.append("| " + " | ".join(parsed_rows[0]) + " |")
            out_lines.append("| " + " | ".join(["---"] * col_count) + " |")
            for row in parsed_rows[1:]:
                out_lines.append("| " + " | ".join(row) + " |")
            out_lines.append("")
        else:
            for row in parsed_rows:
                joined = " — ".join(c for c in row if c)
                if joined:
                    out_lines.append(joined)

        table_buffer = []

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            flush_table()
            if out_lines and out_lines[-1] != "":
                out_lines.append("")
            continue

        next_stripped = lines[idx + 1].strip() if idx + 1 < len(lines) else ""
        next_has_pipes = "|" in next_stripped

        if re.match(r"^(Chapter\s+[IVXLC]+|Appendix\s+\d+)\b", stripped, re.IGNORECASE):
            flush_table()
            out_lines.append("")
            out_lines.append(f"## {stripped}")
            out_lines.append("")
            continue

        if stripped.startswith("### "):
            flush_table()
            out_lines.append("")
            out_lines.append(stripped)
            out_lines.append("")
            continue

        is_table_line = "|" in stripped or "\t" in stripped or bool(re.search(r"\s{3,}", stripped))

        if is_table_line:
            if pending_row_prefix:
                merged = f"{pending_row_prefix} {stripped.lstrip('|').strip()}"
                if not merged.endswith("|"):
                    merged += " |"
                merged = "| " + merged.lstrip("|").strip()
                table_buffer.append(merged)
                pending_row_prefix = ""
            else:
                table_buffer.append(stripped)
            continue

        if next_has_pipes and not re.match(r"^(\d{1,3}\.\s+[A-Z]|Chapter|Appendix)", stripped):
            if pending_row_prefix:
                table_buffer.append(pending_row_prefix)
            pending_row_prefix = stripped
            continue

        if table_buffer and not re.match(r"^(\d{1,3}\.\s+[A-Z]|###\s+)", stripped):
            table_buffer.append(stripped)
            continue

        flush_table()

        if re.match(r"^\((?:i{1,3}|iv|v|vi{0,3})\)\s+", stripped):
            out_lines.append(f'<div class="subclause-2">{stripped}</div>')
        elif re.match(r"^\((?:\d+|[a-z]{1,2})\)\s+", stripped):
            out_lines.append(f'<div class="subclause-1">{stripped}</div>')
        else:
            out_lines.append(stripped)

    flush_table()

    cleaned = "\n".join(out_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def render_markdown_to_a5(md_path: Path, font_family: str, font_size: float) -> bytes:
    """Renders Markdown directly to A5 portrait pages in memory using PyMuPDF DocumentWriter."""
    raw_md = md_path.read_text(encoding="utf-8")
    no_front_matter = strip_front_matter(raw_md)
    clean_md = clean_pdf_dump_text(no_front_matter)

    html_body = markdown.markdown(clean_md, extensions=["tables", "fenced_code", "sane_lists"])

    css = f"""
    body {{ font-family: "{font_family}", sans-serif; font-size: {font_size}pt; line-height: 1.38; color: #111111; }}
    h1 {{ font-size: {font_size * 1.5:.1f}pt; margin-top: 0; margin-bottom: 8pt; border-bottom: 1pt solid #cccccc; padding-bottom: 4pt; }}
    h2 {{ font-size: {font_size * 1.25:.1f}pt; margin-top: 12pt; margin-bottom: 6pt; page-break-after: avoid; }}
    h3 {{ font-size: {font_size * 1.08:.1f}pt; margin-top: 10pt; margin-bottom: 4pt; page-break-after: avoid; }}
    p {{ margin-top: 0; margin-bottom: 6pt; text-align: justify; text-indent: 18pt; }}
    h1 + p, h2 + p, h3 + p, table + p {{ text-indent: 0; }}
    .subclause-1 {{ margin-left: 14pt; text-indent: 12pt; margin-bottom: 4pt; text-align: justify; }}
    .subclause-2 {{ margin-left: 28pt; text-indent: 12pt; margin-bottom: 3pt; text-align: justify; }}
    ul, ol {{ margin-top: 0; margin-bottom: 6pt; padding-left: 16pt; }}
    li {{ margin-bottom: 3pt; }}
    blockquote {{ margin: 8pt 0; padding: 4pt 10pt; border-left: 2.5pt solid #888888; color: #333333; background-color: #f9f9f9; }}
    pre, code {{ font-family: monospace; font-size: {font_size * 0.85:.1f}pt; background-color: #f4f4f4; }}
    pre {{ padding: 6pt; border: 0.5pt solid #dddddd; }}
    table {{ width: 100%; table-layout: fixed; border-collapse: collapse; margin: 8pt 0; font-size: {font_size * 0.78:.1f}pt; }}
    th, td {{ border: 0.5pt solid #bbbbbb; padding: 3pt 4pt; text-align: left; vertical-align: top; word-wrap: break-word; overflow-wrap: break-word; }}
    th {{ background-color: #eeeeee; font-weight: bold; }}
    tr {{ break-inside: avoid; }}
    """

    full_html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{html_body}</body></html>"

    a5_rect = pymupdf.paper_rect("a5")
    mm = 72.0 / 25.4
    content_rect = pymupdf.Rect(16 * mm, 14 * mm, a5_rect.width - (12 * mm), a5_rect.height - (14 * mm))

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

    out_doc = pymupdf.open(stream=buf.getvalue(), filetype="pdf")
    for page_num, page in enumerate(out_doc, start=1):
        if page_num > 1:
            footer_rect = pymupdf.Rect(0, a5_rect.height - (10 * mm), a5_rect.width, a5_rect.height - (4 * mm))
            page.insert_textbox(footer_rect, str(page_num), fontsize=8, fontname="helv", color=(0.35, 0.35, 0.35), align=pymupdf.TEXT_ALIGN_CENTER)

    pdf_bytes = out_doc.tobytes()
    out_doc.close()
    return pdf_bytes


def impose_to_a4_booklet(a5_pdf_bytes: bytes, output_path: Path) -> int:
    """Imposes A5 pages side-by-side onto A4 landscape sheets in saddle-stitch order."""
    src_doc = pymupdf.open(stream=a5_pdf_bytes, filetype="pdf")
    total_pages = len(src_doc)
    padded_total = math.ceil(total_pages / 4) * 4

    a4_rect = pymupdf.paper_rect("a4-l")
    half_w = a4_rect.width / 2.0
    full_h = a4_rect.height

    left_slot = pymupdf.Rect(0, 0, half_w, full_h)
    right_slot = pymupdf.Rect(half_w, 0, a4_rect.width, full_h)

    booklet_doc = pymupdf.open()

    for sheet in range(padded_total // 4):
        front_left = padded_total - 1 - (2 * sheet)
        front_right = 2 * sheet
        back_left = 2 * sheet + 1
        back_right = padded_total - 2 - (2 * sheet)

        for left_idx, right_idx in [(front_left, front_right), (back_left, back_right)]:
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
    parser = argparse.ArgumentParser(description="Clean PDF-extracted Markdown and convert to an A4 saddle-stitch PDF booklet.")
    parser.add_argument("input_md", help="Path to input .md file")
    parser.add_argument("-f", "--font", default="sans-serif", help="Font family (default: sans-serif)")
    parser.add_argument("-s", "--size", type=float, default=10.0, help="Body font size in pt (default: 10.0)")
    parser.add_argument("-o", "--output", help="Custom output PDF path (default: output/<name>_booklet.pdf)")
    parser.add_argument("--save-cleaned", help="Optional path to save the cleaned Markdown intermediate file")
    args = parser.parse_args()

    md_path = Path(args.input_md)
    if not md_path.is_file():
        log.error("File '%s' not found.", md_path)
        sys.exit(1)

    if args.save_cleaned:
        cleaned_preview = clean_pdf_dump_text(strip_front_matter(md_path.read_text(encoding="utf-8")))
        Path(args.save_cleaned).write_text(cleaned_preview, encoding="utf-8")
        log.info("Saved cleaned Markdown to: %s", args.save_cleaned)

    out_path = Path(args.output) if args.output else Path("output") / f"{md_path.stem}_booklet.pdf"

    log.info("[1/2] Cleaning and rendering '%s' to A5 pages (%s, %.1fpt)...", md_path.name, args.font, args.size)
    a5_bytes = render_markdown_to_a5(md_path, args.font, args.size)

    log.info("[2/2] Imposing pages onto A4 landscape booklet...")
    sheets = impose_to_a4_booklet(a5_bytes, out_path)

    log.info("Done! Saved to: %s (%d A4 sheets)", out_path, sheets)
    log.info("Print tip: Enable Two-Sided printing and select 'Flip on Short Edge'.")


if __name__ == "__main__":
    main()
```

## Running and Verifying Your Output

Follow these steps to process your documents.

* **Inspect the cleaned Markdown first:**
  ```bash
  python md2booklet.py rules_dump.md --save-cleaned cleaned_rules.md -s 9.5
  ```

* **Generate the A4 saddle-stitch booklet:**
  ```bash
  python md2booklet.py rules_dump.md -f "DejaVu Sans" -s 9.5 -o output/rules_a4_booklet.pdf
  ```

> **Note:** Enable two-sided printing and select "Flip on Short Edge" so the A4 landscape sheets fold cleanly into an A5 booklet.

## Summary

* Raw PDF text extraction often embeds page folios and breaks table structures.
* The provided Python pipeline sanitizes text, reconstructs tables, and applies precise CSS indentation.
* PyMuPDF renders the cleaned Markdown to A5 pages and imposes them onto A4 sheets for saddle-stitch binding.

## References

* [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
* [Python-Markdown Documentation](https://python-markdown.github.io/)