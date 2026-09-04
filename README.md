# Technical Journal & Digital Garden

[![Deploy Hugo to Pages](https://github.com/phuchungbhutia/phuchungbhutia.github.io/actions/workflows/deploy.yml/badge.svg)](https://github.com/phuchungbhutia/phuchungbhutia.github.io/actions/workflows/deploy.yml)
[![GitHub Pages](https://img.shields.io/badge/Live-phuchungbhutia.github.io-121013?style=flat&logo=github&logoColor=white)](https://phuchungbhutia.github.io/)
[![Hugo Engine](https://img.shields.io/badge/Hugo-v0.165.0%2B-FF4088?style=flat&logo=hugo&logoColor=white)](https://gohugo.io/)
[![Theme](https://img.shields.io/badge/Theme-PaperMod-blueviolet?style=flat)](https://github.com/adityatelange/hugo-PaperMod)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight, serverless engineering and governance notebook deployed to GitHub Pages via Hugo and an automated GitHub Actions CI/CD runner.

---

### Project Documentation

| Document | Description | Direct Link |
| :--- | :--- | :--- |
| **Windows Runbook** | Local setup for Windows 11/10, VSCodium, Winget dependencies, and authoring loop | [WINDOWS_SETUP.md](WINDOWS_SETUP.md) |
| **Troubleshooting Matrix** | Resolution steps for duplicate keys, YAML list syntax, date parsing, and schema crashes | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |

---

### System Architecture & Pipeline

```text
  [Local Workspace: Windows / VSCodium]
                  │
                  ▼  (git push origin main)
  [GitHub Actions Runner: ubuntu-latest]
                  │
                  ├─► 1. actions/checkout@v4 (submodules: recursive)
                  ├─► 2. actions/setup-python@v5 (Python 3.11)
                  ├─► 3. python sanitize.py (Deduplication, ISO Dates, Taxonomies)
                  ├─► 4. hugo --minify (HTML, CSS, JS, Search Index JSON)
                  │
                  ▼  (upload-pages-artifact@v3)
  [GitHub Pages Edge CDN] ──► Production Site (phuchungbhutia.github.io)

```

---

### Core Specifications

| Metric / Dimension | Implementation Detail | Operational Target |
| --- | --- | --- |
| **Static Engine** | Hugo Extended (Go native) | Build latency < 800ms |
| **Theme Base** | PaperMod (Git Submodule) | Zero custom layout hacking |
| **Taxonomies** | Categories & Tags | Native Hugo array parsing |
| **Search Engine** | Fuse.js (Client-side) | Static index JSON output |
| **Front Matter Sanity** | Custom Python AST parser (`sanitize.py`) | Automated CI/CD pre-build hook |
| **Asset Pipeline** | Standalone static image pass-through | `/static/assets/img/` |

---

### Directory Layout

```text
phuchungbhutia.github.io/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions deployment runner
├── assets/
│   └── css/
│       └── extended/
│           └── custom.css      # Dark mode overrides & custom variables
├── content/
│   ├── posts/                  # Markdown articles & technical writeups
│   ├── archives.md             # PaperMod timeline archive view stub
│   └── search.md               # Fuse.js client-side search stub
├── static/
│   └── assets/
│       └── img/                # Post images, hero assets, avatar
├── themes/
│   └── PaperMod/               # Upstream theme Git submodule
├── hugo.yaml                   # Core site configuration
├── sanitize.py                 # Build-time front-matter validation hook
├── TROUBLESHOOTING.md          # Diagnostic runbook for YAML & CI/CD errors
├── WINDOWS_SETUP.md            # Windows & VSCodium local environment guide
├── .gitignore                  # Git tracking exclusion list
└── README.md

```

---

### Rapid Local Commands

```bash
# Clone with submodule dependencies
git clone --recurse-submodules [https://github.com/phuchungbhutia/phuchungbhutia.github.io.git](https://github.com/phuchungbhutia/phuchungbhutia.github.io.git)

# Run sanitization pass locally (matches CI runner)
python sanitize.py content/posts

# Start local livereload server
hugo server -D

# Compile production-minified artifacts
hugo --minify
