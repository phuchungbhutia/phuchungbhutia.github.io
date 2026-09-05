---
title: "Modernizing My Engineering Hub: Migrating from Jekyll Chirpy to Hugo PaperMod"
date: "2026-09-05T20:55:00+05:30"
categories: ["Web Development", "DevOps"]
tags: ["hugo", "github-pages", "ci-cd", "automation", "2026"]
description: "A comprehensive post-mortem detailing the architectural migration of my personal engineering hub from Jekyll to Hugo PaperMod, featuring an automated YAML pre-processor, dynamic GitHub API integration, and in-page Fuse.js search."

---
Maintaining a personal engineering garden should ideally demand zero cognitive overhead once the publishing pipeline is established. Over time, my setup running Jekyll Chirpy on GitHub Pages began accumulating operational drag: Bundler gem conflicts, brittle Liquid templating crashes triggered by nested code blocks, and sluggish CI build times that routinely hovered around a minute.

I took the opportunity to overhaul the platform entirely. The site now runs on **Hugo Extended** with a tailored **PaperMod** foundation, supported by an automated front matter sanitization engine and dynamic client-side interfaces. Here is the breakdown of the problems encountered, the architectural decisions made, and the specific code implemented across the stack.

---

## Architectural Comparison: Why Jekyll Chirpy Was Retired

The core motivation was eliminating runtime fragility and improving build performance. Chirpy is a capable theme, but its dependency tree and strict taxonomy rules created recurring maintenance bottlenecks.

| Architectural Dimension | Legacy Implementation (Jekyll Chirpy) | Modernized Stack (Hugo PaperMod) |
| --- | --- | --- |
| **Engine Runtime** | Ruby 3.x, Bundler, RubyGems | Standalone Go binary (Hugo Extended) |
| **Average CI Build Latency** | 45 to 75 seconds | 400 to 700 milliseconds |
| **Template Syntax Parsing** | Liquid Engine (conflicts with code fences) | Native Goldmark Markdown |
| **Search Architecture** | Pre-indexed Lunr.js bundle | Dynamic in-page Fuse.js JSON evaluation |
| **Taxonomy Limits** | Enforced 2-tier category hierarchy | Arbitrary tag and category depth |
| **Front Matter Handling** | Aborts on loose/unquoted YAML keys | Pre-processed via automated AST script |

---

## Step 1: Cleansing the Workspace and Git Backups

Before rewriting the publishing pipeline, the previous site state had to be cleanly archived and isolated.

First, the existing Jekyll repository was tagged and pushed to a persistent tracking branch:

```powershell
# Archive legacy state
git checkout -b legacy-jekyll-chirpy
git push origin legacy-jekyll-chirpy
git checkout main

```

Next, all legacy dependencies, build outputs, and bundler locks were removed to leave only clean Markdown posts and media assets:

```powershell
# Purge Ruby artifacts, Jekyll configs, and layouts
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue _site, .jekyll-cache, _layouts, _includes, _tabs, _plugins
Remove-Item -Force -ErrorAction SilentlyContinue Gemfile, Gemfile.lock, _config.yml

# Initialize clean Hugo structure and submodule
hugo new site . --force
git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod

```

---

## Step 2: Debugging the Production Build Failures

Moving decades worth of legacy front matter into Hugo's native Go parser immediately exposed several formatting incompatibilities.

### 1. The Duplicate Key Collision

Hugo halts site rendering when YAML keys repeat within a single post header:

```text
ERROR assemble: failed to create page from pageMetaSource /posts/2026-08-05-ocr2md:
mapping key "date" already defined

```

* **Root Cause:** Earlier Jekyll formatting tools had injected a top-level `date:` line without stripping the existing date attribute further down in the front matter.

### 2. Conflicting Empty Array and Multiline List Syntax

Several migrated posts contained colliding YAML structures:

```text
ERROR assemble: [4:3] value is not allowed in this context
  categories: []
>   - "Productivity"

```

* **Root Cause:** Chirpy’s scaffolding occasionally emitted empty inline brackets (`categories: []`) immediately preceding multiline bullet entries. In standard YAML, an inline structure cannot be simultaneously followed by block-level items.

### 3. Schema.org Minification Failures

Compiling with `hugo --minify` caused execution breaks:

```text
execute of template failed: template: _partials/templates/schema_json.html:
can't evaluate field publisherType in type bool

```

* **Root Cause:** Attempting to suppress Schema JSON-LD via `schema: false` violates PaperMod’s template contract, which expects `.Site.Params.schema` to evaluate as an object rather than a boolean. Furthermore, unescaped quotation marks in article summaries broke JSON minification passes.

---

## Step 3: Engineering the Pre-Build Sanitizer (`sanitize.py`)

Rather than manually editing hundreds of legacy posts, I wrote an automated pre-processing script (`sanitize.py`) that executes in the GitHub Actions runner prior to compiling.

The script performs four critical sanitization routines:

* **Key Deduplication:** Retains only the first valid instance of `date:`, `title:`, and taxonomy mappings.
* **Date Normalization:** Converts legacy human-readable dates or unquoted strings to strict ISO-8601 timestamps (`"YYYY-MM-DDTHH:MM:SS+05:30"`), falling back to filename pattern matching (`YYYY-MM-DD-*.md`) if the date key is absent.
* **Taxonomy Flattening:** Merges inline definitions and broken indented bullet lists into clean single-line arrays (e.g., `categories: ["DevOps", "Automation"]`).
* **Liquid Stripping:** Strips leftover Jekyll tags (`{% raw %}`, `{% endraw %}`) from the post body so Goldmark compiles code fences cleanly.

```python
# Core logic snippet from sanitize.py
def sanitize_front_matter(fm_text: str, filename: str) -> str:
    lines = fm_text.splitlines()
    new_lines, seen_keys = [], set()
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Deduplicate and standardize ISO timestamps
        if re.match(r"^date:", stripped, re.IGNORECASE):
            if "date" in seen_keys:
                i += 1
                continue
            seen_keys.add("date")
            new_lines.append(f"date: {normalize_date(stripped.split(':', 1)[1], filename)}")
            i += 1
            continue

        # Convert broken bullet lists under categories/tags into valid arrays
        tax_match = re.match(r"^(categories|tags):\s*(.*)$", stripped, re.IGNORECASE)
        if tax_match:
            key = tax_match.group(1).lower()
            if key in seen_keys:
                i += 1
                continue
            seen_keys.add(key)
            collected = []
            j = i + 1
            while j < len(lines) and re.match(r"^\s*-\s*(.+)$", lines[j]):
                collected.append(re.match(r"^\s*-\s*(.+)$", lines[j]).group(1).strip())
                j += 1
            new_lines.append(format_clean_list(key, collected))
            i = j
            continue

        new_lines.append(line)
        i += 1

    return "\n".join(new_lines)

```

---

## Step 4: Custom Layout Overhauls

To make the site functional and responsive, several default PaperMod templates were overridden under `layouts/`.

### 1. Dynamic GitHub Repository Integration (`layouts/index.html`)

Rather than maintaining static project cards, the landing page uses the public GitHub REST API to fetch live repository metadata on client page load.

The custom layout:

* Renders the top 5 most recently active non-fork repositories in a clean table.
* Displays live star counts, fork counts, and primary language tags.
* Parses `homepage` or GitHub Pages attributes to generate direct deployment badges.
* Automatically places secondary repositories into an expandable `<details>` drawer.

### 2. In-Page Dynamic Search on `/posts/` (`layouts/posts/list.html`)

The standalone search page was purged entirely. Instead, the main `/posts/` section integrates Fuse.js directly above the post roll:

* **Default State:** Renders the 5 most recent articles alongside a collapsible drawer for older archives.
* **Active State:** As the reader types, the default archive hides instantly, and Fuse.js evaluates Hugo's pre-built `index.json` to stream search matches directly below the search bar without triggering page reloads.

### 3. Responsive Navigation Flex Bar (`layouts/partials/header.html`)

The main header layout was rewritten to enforce a strict two-column flex layout:

* **Left:** Site brand ("Phuchung Bhutia") and dark/light mode toggle.
* **Right:** Ordered navigation links (**Blogs**, **Categories**, **Tags**, **Archives**) accompanied by an inline SVG linking to the upstream GitHub repository, styled with proper margin gutters to eliminate line-wrapping bugs on desktop displays.

---

## Step 5: Continuous Integration Pipeline (`.github/workflows/deploy.yml`)

The deployment process runs via a single unified GitHub Actions workflow configured with Python and Hugo Extended:

```yaml
name: Deploy Hugo to Pages

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Source Code
        uses: actions/checkout@v4
        with:
          submodules: recursive
          fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Setup Hugo Extended
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: "latest"
          extended: true

      - name: Execute Pre-Build Sanitizer
        run: python sanitize.py content/posts

      - name: Compile Minified Site
        run: hugo --minify

      - name: Upload Deployment Artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./public

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Publish to GitHub Pages CDN
        id: deployment
        uses: actions/deploy-pages@v4

```

---

## Conclusion and Future Roadmap

Migrating from Chirpy to Hugo PaperMod reduced build and deployment latencies by nearly **98%** while eradicating the recurring syntax and dependency issues inherent to Ruby environments. With the automated AST sanitizer guarding the pre-build pipeline, posts can now be drafted in any standard Markdown editor without fear of crashing the remote runner.

**Next Milestones:**

* Expand the `sanitize.py` engine to validate internal image reference paths in `/static/assets/img/`.
* Implement automated OpenGraph social preview cards utilizing Hugo's native image-processing pipeline.
* Integrate continuous link-checking across all outbound references using headless CI validation steps.
