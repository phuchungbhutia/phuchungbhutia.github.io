import os
import re
import sys
from datetime import datetime

POSTS_DIR = os.path.join("content", "posts")
TIMEZONE_OFFSET = "+05:30"

def normalize_date(raw_val: str, filename: str) -> str:
    cleaned = raw_val.strip().strip("\"'").strip()
    match = re.search(r"(\d{4}-\d{2}-\d{2})(?:[T\s](\d{2}:\d{2}:\d{2}))?", cleaned)
    if match:
        d = match.group(1)
        t = match.group(2) if match.group(2) else "10:00:00"
        return f'"{d}T{t}{TIMEZONE_OFFSET}"'
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%B %d, %Y", "%b %d, %Y"):
        try:
            dt = datetime.strptime(cleaned, fmt)
            return f'"{dt.strftime("%Y-%m-%d")}T10:00:00{TIMEZONE_OFFSET}"'
        except ValueError:
            pass
    fn_match = re.match(r"^(\d{4}-\d{2}-\d{2})", filename)
    if fn_match:
        return f'"{fn_match.group(1)}T10:00:00{TIMEZONE_OFFSET}"'
    today = datetime.now().strftime("%Y-%m-%d")
    return f'"{today}T10:00:00{TIMEZONE_OFFSET}"'

def clean_taxonomy_line(line: str) -> str:
    m = re.match(r"^(categories|tags):\s*(?:\[(.*?)\]|(.*))?$", line, flags=re.IGNORECASE)
    if not m:
        return line
    key = m.group(1).lower()
    raw_vals = m.group(2) if m.group(2) is not None else m.group(3)
    if not raw_vals:
        return f"{key}: []"
    items = [x.strip().strip("\"'").strip() for x in raw_vals.split(",") if x.strip()]
    cleaned = []
    seen = set()
    for item in items:
        norm = item.replace("&", "and").strip()
        lowered = norm.lower()
        if lowered and lowered not in seen:
            seen.add(lowered)
            cleaned.append(f'"{norm}"')
    return f"{key}: [{', '.join(cleaned)}]"

def sanitize_front_matter(fm_text: str, filename: str) -> str:
    lines = fm_text.splitlines()
    new_lines = []
    has_date = False
    for line in lines:
        stripped = line.strip()
        if re.match(r"^render_with_liquid:", stripped, re.IGNORECASE):
            continue
        if re.match(r"^date:", stripped, re.IGNORECASE):
            raw_date = stripped.split(":", 1)[1]
            new_lines.append(f"date: {normalize_date(raw_date, filename)}")
            has_date = True
            continue
        if re.match(r"^(categories|tags):", stripped, re.IGNORECASE):
            new_lines.append(clean_taxonomy_line(stripped))
            continue
        if re.match(r"^title:", stripped, re.IGNORECASE):
            val = stripped.split(":", 1)[1].strip()
            if not ((val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'"))):
                val_escaped = val.replace('"', '\\"')
                new_lines.append(f'title: "{val_escaped}"')
                continue
        if re.match(r"^(description|summary):", stripped, re.IGNORECASE):
            key, val = stripped.split(":", 1)
            val_clean = val.strip().strip("\"'").replace('"', "'")
            new_lines.append(f'{key}: "{val_clean}"')
            continue
        new_lines.append(line)
    if not has_date:
        new_lines.insert(0, f"date: {normalize_date('', filename)}")
    return "\n".join(new_lines)

def process_file(filepath: str) -> bool:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    cleaned_content = re.sub(r"^[ \t]*\{%[ \t]*(?:raw|endraw)[ \t]*%\}[\r\t ]*\n?", "", content, flags=re.MULTILINE)
    fm_match = re.match(r"^(---\s*\n)(.*?\n)(---\s*\n?)(.*)$", cleaned_content, flags=re.DOTALL)
    if not fm_match:
        return False
    prefix, front_matter, suffix, body = fm_match.groups()
    filename = os.path.basename(filepath)
    new_fm = sanitize_front_matter(front_matter, filename)
    final_output = f"{prefix}{new_fm}\n{suffix}{body}"
    if final_output != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(final_output)
        return True
    return False

def main():
    target_dir = POSTS_DIR
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    if not os.path.isdir(target_dir):
        print(f"Error: Directory not found -> {target_dir}")
        sys.exit(1)
    total = 0
    updated = 0
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith((".md", ".markdown")):
                total += 1
                full_path = os.path.join(root, file)
                if process_file(full_path):
                    print(f"[FIXED] {file}")
                    updated += 1
    print(f"\nCompleted: {total} files inspected, {updated} files updated.")

if __name__ == "__main__":
    main()
