import os
import re

posts_dir = "_posts"

if os.path.exists(posts_dir):
    for root, _, files in os.walk(posts_dir):
        for file in files:
            if file.endswith((".md", ".markdown")):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract front matter block only (between opening and closing '---')
                front_matter_match = re.match(r"^(---\s*\n.*?\n---)(\s*\n.*)$", content, flags=re.DOTALL)
                if not front_matter_match:
                    continue

                front_matter, body = front_matter_match.group(1), front_matter_match.group(2)

                # 1. Clean inline arrays: categories: [A, B, C] or tags: [2025, Audit]
                def clean_taxonomies(match):
                    key = match.group(1)
                    raw_vals = match.group(2)
                    items = [x.strip().strip("\"'").strip() for x in raw_vals.split(",") if x.strip()]

                    cleaned = []
                    seen = set()
                    for item in items:
                        normalized = item.replace("&", "and").strip()
                        lowered = normalized.lower()
                        if lowered and lowered not in seen:
                            seen.add(lowered)
                            cleaned.append(f'"{lowered}"')

                    # Chirpy caps categories to maximum depth of 2
                    if key == "categories" and len(cleaned) > 2:
                        cleaned = cleaned[:2]

                    sep = ", "
                    joined = sep.join(cleaned)
                    return f"{key}: [{joined}]"

                # 2. Quote numeric YAML bullet list items inside front matter: - 2025 -> - "2025"
                def clean_bullet_items(match):
                    indent = match.group(1)
                    val = match.group(2).strip().strip("\"'").strip()
                    if val.isdigit():
                        return f'{indent}- "{val}"'
                    return match.group(0)

                new_front_matter = re.sub(r"^(categories|tags):\s*\[(.*?)\]", clean_taxonomies, front_matter, flags=re.MULTILINE)
                new_front_matter = re.sub(r"^(\s*)-\s+(.*)$", clean_bullet_items, new_front_matter, flags=re.MULTILINE)

                new_content = new_front_matter + body

                if new_content != content:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)

print("Taxonomies sanitized successfully.")
