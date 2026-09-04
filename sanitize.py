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

def format_clean_list(key: str, items: list) -> str:
    cleaned = []
    seen = set()
    for item in items:
        val = item.strip().strip("\"'").replace("&", "and").strip()
        lowered = val.lower()
        if lowered and lowered not in seen:
            seen.add(lowered)
            cleaned.append(f'"{val}"')
    return f"{key}: [{', '.join(cleaned)}]"

def sanitize_front_matter(fm_text: str, filename: str) -> str:
    lines = fm_text.splitlines()
    new_lines = []
    seen_keys = set()
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Drop legacy Jekyll/Liquid keys
        if re.match(r"^render_with_liquid:", stripped, re.IGNORECASE):
            i += 1
            continue

        # Handle Date (deduplicate)
        if re.match(r"^date:", stripped, re.IGNORECASE):
            if "date" in seen_keys:
                i += 1
                continue
            seen_keys.add("date")
            raw_date = stripped.split(":", 1)[1]
            new_lines.append(f"date: {normalize_date(raw_date, filename)}")
            i += 1
            continue

        # Handle Taxonomies (deduplicate)
        tax_match = re.match(r"^(categories|tags):\s*(.*)$", stripped, re.IGNORECASE)
        if tax_match:
            key = tax_match.group(1).lower()
            if key in seen_keys:
                # Skip duplicate and its indented items
                j = i + 1
                while j < len(lines) and re.match(r"^\s*-\s*(.+)$", lines[j]):
                    j += 1
                i = j
                continue
            seen_keys.add(key)
            rest = tax_match.group(2).strip()
            collected_items = []

            if rest and rest not in ("[]", ""):
                cleaned_rest = rest.strip("[]")
                inline_parts = [x.strip() for x in cleaned_rest.split(",") if x.strip()]
                collected_items.extend(inline_parts)

            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                bullet_match = re.match(r"^\s*-\s*(.+)$", next_line)
                if bullet_match:
                    collected_items.append(bullet_match.group(1).strip())
                    j += 1
                else:
                    break

            new_lines.append(format_clean_list(key, collected_items))
            i = j
            continue

        # Handle Title (deduplicate)
        if re.match(r"^title:", stripped, re.IGNORECASE):
            if "title" in seen_keys:
                i += 1
                continue
            seen_keys.add("title")
            val = stripped.split(":", 1)[1].strip()
            if not ((val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'"))):
                val_escaped = val.replace('"', '\\"')
                new_lines.append(f'title: "{val_escaped}"')
            else:
                new_lines.append(f'title: {val}')
            i += 1
            continue

        # Handle Description / Summary (deduplicate)
        desc_match = re.match(r"^(description|summary):", stripped, re.IGNORECASE)
        if desc_match:
            d_key = desc_match.group(1).lower()
            if d_key in seen_keys:
                i += 1
                continue
            seen_keys.add(d_key)
            key_name, val = stripped.split(":", 1)
            val_clean = val.strip().strip("\"'").replace('"', "'")
            new_lines.append(f'{key_name}: "{val_clean}"')
            i += 1
            continue

        new_lines.append(line)
        i += 1

    if "date" not in seen_keys:
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
                fp = os.path.join(root, file)
                if process_file(fp):
                    print(f"[FIXED] {file}")
                    updated += 1

    print(f"\nScan completed: {total} files checked, {updated} updated.")

if __name__ == "__main__":
    main()
