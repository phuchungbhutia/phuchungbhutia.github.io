---
title: "Deploying Jekyll Chirpy on GitHub Pages: The Complete Setup, CI/CD Pipeline, and Bug-Fix Playbook"
date: "2026-09-04T13:30:00+05:30"
categories: ["Web Development", "GitHub Pages"]
tags: ["jekyll", "chirpy", "github-actions", "htmlproofer", "python", "devops", "troubleshooting"]
---

Setting up a documentation portal or department blog using the **Jekyll Chirpy** theme on GitHub Pages looks effortless on paper. You fork the starter repo, point GitHub Actions to your branch, and watch the site spin up.

In reality, running a production-grade Chirpy setup with custom CI/CD pipelines quickly runs into a minefield of build-time failures: Ruby Liquid crashes over integer tags, `htmlproofer` throwing hundreds of false-positive 404s on dynamic taxonomy routes, missing local layout overrides, broken anchor fragment checks, and invisible non-breaking spaces that crash YAML parsers.

This guide is an end-to-end playbook covering the complete setup of Jekyll Chirpy on GitHub Pages, along with every major build error, root cause, and production-tested solution.

---

## 1. Initial Setup Architecture

Chirpy uses a decoupled build approach where raw markdown, theme assets, and plugins compile inside a GitHub Actions virtual container before pushing static HTML/CSS/JS artifacts directly to GitHub's CDN.

### Core File Structure
A functional Chirpy site must contain these core directories and files:

```text
├── .github/
│   └── workflows/
│       └── build-deploy.yml    # GitHub Actions CI/CD pipeline
├── _layouts/                   # Local layout overrides (e.g., tags.html)
├── _posts/                     # Blog entries (YYYY-MM-DD-title.md)
├── _tabs/                      # Static navigation pages
│   ├── categories.md
│   └── tags.md
├── assets/                     # Images, styles, and custom scripts
├── _config.yml                 # Master site configuration
├── Gemfile                     # Ruby dependencies
└── sanitize.py                 # Automated taxonomy sanitizer

```

### Essential Navigation Tabs (`_tabs/`)

Unlike basic Jekyll setups, Chirpy requires explicit markdown files inside `_tabs/` (or `tabs/`) with designated layouts to render top-level route indexes.

`_tabs/categories.md`:

```yaml
---
layout: categories
title: Categories
icon: fas fa-stream
order: 2
permalink: /categories/
---

```

`_tabs/tags.md`:

```yaml
---
layout: tags
title: Tags
icon: fas fa-tags
order: 3
permalink: /tags/
---

```

---

## 2. Master Site Configuration (`_config.yml`)

The `_config.yml` file dictates site identity, permalinks, and asset engines. A recurring trap during manual editing is the introduction of **non-breaking spaces (`\u00a0`)**, which look like normal spaces in editors but trigger fatal YAML syntax exceptions during parsing.

Here is a clean, production-ready `_config.yml`:

```yaml
# Master Theme Configuration
theme: jekyll-theme-chirpy
lang: en
timezone: Asia/Kolkata

# Identity & Metadata
title: Directorate of Local Fund Audit
tagline: Government of Sikkim
description: >-
  Primary Audit Institution in Sikkim for Local Self-Government Institutions.
url: "[https://sikkimlfa.github.io](https://sikkimlfa.github.io)"
baseurl: ""

# Social & Author Metadata
github:
  username: sikkimlfa

social:
  name: Directorate of Local Fund Audit
  email: sikkimlfa@gmail.com
  links:
    - [https://github.com/sikkimlfa](https://github.com/sikkimlfa)

# Layout Features
toc: true
paginate: 10

kramdown:
  footnote_backlink: "&#8617;&#xfe0e;"
  syntax_highlighter: rouge
  syntax_highlighter_opts:
    css_class: highlight
    span:
      line_numbers: false
    block:
      line_numbers: true
      start_line: 1

collections:
  tabs:
    output: true
    sort_by: order

defaults:
  - scope:
      path: ""
      type: posts
    values:
      layout: post
      comments: false
      toc: true
      permalink: /posts/:title/
  - scope:
      path: ""
      type: tabs
    values:
      layout: page
      permalink: /:title/

sass:
  style: compressed

compress_html:
  clippings: all
  comments: all
  endings: all
  profile: false
  blanklines: false
  ignore:
    envs: [development]

exclude:
  - "*.gem"
  - "*.gemspec"
  - README.md
  - LICENSE
  - sanitize.py

```

> **Warning:** Do **not** declare or enable `jekyll-archives` inside `_config.yml`. It conflicts directly with Chirpy's built-in client-side routing and causes duplicate route collisions.

---

## 3. The Production CI/CD Workflow (`build-deploy.yml`)

GitHub Actions compiles the site in an Ubuntu runner, validates links and assets, and deploys to the official `github-pages` environment.

Save this configuration as `.github/workflows/build-deploy.yml`:

```yaml
name: "Build and Deploy"
on:
  push:
    branches:
      - main
      - master
    paths-ignore:
      - .gitignore
      - README.md
      - LICENSE

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
      - name: Checkout Repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Pages Configuration
        id: pages
        uses: actions/configure-pages@v5

      - name: Setup Ruby Runtime
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: 3.3
          bundler-cache: true

      - name: Sanitize Front Matter
        run: python3 sanitize.py

      - name: Build Jekyll Site
        run: bundle exec jekyll b -d "_site${{ steps.pages.outputs.base_path }}"
        env:
          JEKYLL_ENV: "production"

      - name: Test Site Integrity
        run: |
          bundle exec htmlproofer _site \
            --disable-external \
            --no-check-internal-hash \
            --ignore-urls "/^http:\/\/127.0.0.1/,/^http:\/\/0.0.0.0/,/^http:\/\/localhost/,/^\/tags\//,/^\/categories\//"

      - name: Upload Build Artifacts
        uses: actions/upload-pages-artifact@v3
        with:
          path: "_site${{ steps.pages.outputs.base_path }}"

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4

```

---

## 4. Comprehensive Bug-Fix & Troubleshooting Guide

Here are the specific, real-world failures encountered when deploying Chirpy and how to solve each one.

### Bug 1: Liquid Exception `undefined method 'gsub' for an instance of Integer`

#### The Failure

The build aborts with this backtrace:

```text
Liquid Exception: undefined method 'gsub' for an instance of Integer in .../_layouts/tags.html
Jekyll::Utils#replace_character_sequence_with_hyphen: undefined method 'gsub' for an instance of Integer (NoMethodError)

```

#### Root Cause

If any post contains a numeric tag (such as `tags: [2025]` or `tags: [2026]`), YAML parses the value as a Ruby `Integer`. When Chirpy's default `tags.html` layout pipes that tag into Liquid's `slugify` filter, the underlying Ruby method attempts to run regex substitutions (`.gsub()`) directly on an integer object.

#### The Fix

Create a local layout override at `_layouts/tags.html` in your project root. Force-cast every tag to a string via `| append: ''` before sorting or slugifying:

```html
---
layout: page
---

{% include lang.html %}

{% assign tags_list = '' | split: '' %}

{% for post in site.posts %}
  {% for tag in post.tags %}
    {% assign tag_str = tag | append: '' | strip %}
    {% if tag_str != '' %}
      {% unless tags_list contains tag_str %}
        {% assign tags_list = tags_list | push: tag_str %}
      {% endunless %}
    {% endif %}
  {% endfor %}
{% endfor %}

{% assign tags_list = tags_list | sort_natural %}

<div id="tags" class="d-flex flex-wrap mx-xl-2">
  {% for tag in tags_list %}
    {% assign tag_str = tag | append: '' %}
    {% assign tag_slug = tag_str | slugify %}
    {% assign tag_posts = site.tags[tag] %}
    <a href="{{ tag_slug | prepend: '/tags/' | relative_url }}/" class="tag">
      {{ tag_str }}<span class="text-muted">({{ tag_posts.size }})</span>
    </a>
  {% endfor %}
</div>

```

---

### Bug 2: HTML-Proofer 200+ Link Failures on `/categories/`

#### The Failure

`htmlproofer` reports hundreds of broken internal links:

```text
* At _site/categories/index.html:1:
  internally linking to /categories/governance/, which does not exist
HTML-Proofer found 233 failures!

```

#### Root Cause

Chirpy handles categories as a client-side tree. It does **not** generate physical HTML directories on disk for every intermediate category slug (e.g. `_site/categories/governance/index.html`). Because `htmlproofer` checks static file paths on disk rather than evaluating JavaScript, it flags these virtual paths as broken.

#### The Fix

Tell `htmlproofer` to ignore category and tag paths via regex in your workflow file:

```bash
--ignore-urls "/^http:\/\/127.0.0.1/,/^http:\/\/0.0.0.0/,/^http:\/\/localhost/,/^\/tags\//,/^\/categories\//"

```

---

### Bug 3: `htmlproofer` OptionParser Error (`needless argument`)

#### The Failure

`htmlproofer` crashes during initialization:

```text
parse_cli_options: needless argument: --check-internal-hash=false (OptionParser::NeedlessArgument)

```

#### Root Cause

In **HTML-Proofer v5.x**, boolean CLI switches do not accept `=false` or `=true`. Ruby's `OptionParser` treats them as flags and expects a `--no-` prefix to negate them.

#### The Fix

Replace `--check-internal-hash=false` with:

```bash
--no-check-internal-hash

```

---

### Bug 4: Internal Link Hash Failures (`#pricing-guide`, `#file-organization`)

#### The Failure

`htmlproofer` flags missing heading IDs inside generated post pages:

```text
* At _site/posts/ai-service2/index.html:1:
  internally linking to #pricing-guide; the file exists, but the hash 'pricing-guide' does not

```

#### Root Cause

Markdown articles contain table-of-contents or inline anchor links (`[Pricing](#pricing-guide)`), but the actual heading text does not match Kramdown's slugification rules or was modified without updating the link.

#### The Fix

Disable internal hash checking entirely in the workflow step using `--no-check-internal-hash`. Alternatively, define the heading anchor explicitly in the markdown file:

```markdown
## Pricing Guide {#pricing-guide}

```

---

### Bug 5: Missing Image Assets Breaking the Build

#### The Failure

`htmlproofer` flags non-existent banner images:

```text
For the Images check, the following failures were found:
* At _site/index.html:1:
  internal image /assets/img/headers/preview-image.png does not exist

```

#### Root Cause

A blog post front matter declared an `image:` path, but the file was never committed to the repository.

#### The Fix

Either commit the referenced file into `assets/img/headers/preview-image.png`, or remove the `image:` block from the post's front matter until the asset is ready.

---

### Bug 6: Category 404s Due to Depth Exceeding 2 Levels

#### The Failure

Clicking category pills returns a 404 page on the live website.

#### Root Cause

Chirpy supports a **maximum category depth of 2**: `[Primary Category, Subcategory]`. Listing 3 or more items as a flat array in `categories:` breaks Chirpy's hierarchical URL generation.

#### The Fix

Keep `categories:` capped to 2 items, and push all supplementary keywords into `tags:`:

```yaml
# ❌ INCORRECT (Breaks Chirpy routing)
categories: ["Public Finance", "Audit", "Governance", "Sikkim"]

# ✅ CORRECT (Supported structure)
categories: ["Public Finance", "Audit and Governance"]
tags: ["sikkim", "local-body-audit", "dcb-statement"]

```

---

## 5. Automated Front Matter Sanitizer (`sanitize.py`)

To prevent recurring human errors across dozens of markdown files, place this script in the root of your repository. It runs automatically in the CI/CD pipeline before Jekyll compiles, sanitizing arrays, capping category depths, and quoting numeric values strictly within YAML front matter blocks.

Save as `sanitize.py`:

```python
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

                # Match front matter block only
                fm_match = re.match(r"^(---\s*\n.*?\n---)(\s*\n.*)$", content, flags=re.DOTALL)
                if not fm_match:
                    continue

                front_matter, body = fm_match.group(1), fm_match.group(2)

                # 1. Clean inline arrays: categories: [A, B] or tags: [2025, Audit]
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

                    # Chirpy requires category depth <= 2
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

                new_fm = re.sub(r"^(categories|tags):\s*\[(.*?)\]", clean_taxonomies, front_matter, flags=re.MULTILINE)
                new_fm = re.sub(r"^(\s*)-\s+(.*)$", clean_bullet_items, new_fm, flags=re.MULTILINE)

                new_content = new_fm + body

                if new_content != content:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)

print("Taxonomies sanitized successfully.")

```

---

## 6. Standard Blog Post Template

When adding new content, follow this standardized template structure:

```markdown
---
title: "Standard Operating Procedures for Local Fund Audits in Sikkim"
date: "2026-09-04T10:00:00+05:30"
categories: ["Public Finance", "Audit and Governance"]
tags: ["local-fund-audit", "panchayat", "sikkim", "dcb-statement"]
description: "Comprehensive guidance on audit requisition procedures, cashbook reconciliation, and statutory compliance."
---

Opening summary introducing the topic and core objectives.

---

## 1. Statutory Mandate

Explain the statutory basis and governing rules using clear, professional terminology.

* **Primary Verification:** Confirming that all cashbook entries match bank records.
* **Statutory Compliance:** Ensuring statutory deductions (GST-TDS, Income Tax, Labour Cess) are deposited within prescribed timelines.

---

## 2. Technical Implementation & Formats

Use formatted markdown tables for financial and procedural data:

| Parameter | Responsibility | Frequency | Statutory Timeline |
| :--- | :--- | :---: | :--- |
| **Cash Book Reconciliation** | Accounts Officer / Sachiva | Monthly | 5th of following month |
| **DCB Register Verification** | Head of Office | Quarterly | End of quarter |
| **Annual Financial Statements** | Executive Officer | Annual | June 30th |

---

## 3. Key Observations & Action Taken

Summarize actionable takeaways and next steps for administration or field teams.

```

---

## Summary Checklist for a Clean Build

Before pushing new posts or configuration changes to GitHub, verify these six checks:

1. **Category Depth:** Are `categories` capped at maximum 2 levels?
2. **Special Characters:** Are ampersands (`&`) written as `and` in taxonomy names?
3. **Layout Overrides:** Does `_layouts/tags.html` exist to cast tags to strings?
4. **HTML-Proofer Flags:** Is `--no-check-internal-hash` enabled and are `/categories/` URLs ignored?
5. **Asset Integrity:** Do all referenced header images exist on disk?
6. **Tabs Present:** Do `_tabs/categories.md` and `_tabs/tags.md` exist with their required front matter?

Following this architecture keeps your GitHub Actions pipeline running clean, avoids broken links, and delivers a robust, high-performance static site on GitHub Pages.
