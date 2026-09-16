---

title: "Static Sites on GitHub Pages: Hugo, Jekyll, VitePress, Docusaurus, MkDocs – Install, Themes, Debug, Deploy"
date: "2026-09-16"
categories: ["Web Development", "DevOps"]
tags: ["github-pages", "hugo", "jekyll", "vitepress", "docusaurus", "mkdocs", "papermod", "terminal-theme", "static-site", "howto", "2026"]
description: "Step-by-step guide to building and deploying static sites on GitHub Pages with Hugo, Jekyll, VitePress, Docusaurus, and MkDocs."

---

# Static Sites on GitHub Pages: Hugo, Jekyll, VitePress, Docusaurus, and MkDocs

GitHub Pages provides free, dependable hosting for static sites directly from GitHub repositories. By pairing GitHub Pages with a modern static site generator (SSG), you can build fast, secure, and easily maintainable websites—whether you need a technical blog, personal portfolio, or enterprise documentation site.

This guide details five static site generators across different ecosystems:

* **Hugo:** A Go-based static engine built for blogs and personal portals.
* **Jekyll:** The original Ruby-based generator natively supported by GitHub Pages.
* **VitePress:** A Vue 3-powered documentation and blogging tool.
* **Docusaurus:** A React-based platform designed for project documentation and versioning.
* **MkDocs:** A Python-based Markdown compiler featuring the Material theme.

---

## 1. Core Concepts of GitHub Pages

GitHub Pages hosts static assets (HTML, CSS, JavaScript, images, and media) served directly from a repository.

### Site Types

* **User or Organization Site:** Hosted at `[https://username.github.io](https://username.github.io)`. This setup requires the repository to be named strictly as `username.github.io`. Only one user or organization site is permitted per account.
* **Project Site:** Hosted at `[https://username.github.io/project-name](https://username.github.io/project-name)`. These can be created from any standard repository by enabling Pages under **Settings → Pages**.

### Deployment Models

* **Deploy from a Branch:** GitHub serves pre-built assets from a designated branch (typically `main` or `gh-pages`) from either the root `/` or the `/docs` directory.
* **GitHub Actions:** GitHub executes an automated CI/CD pipeline on push, builds the project from source, and deploys the resulting artifact directly to GitHub Pages. This is the recommended approach for Hugo, VitePress, Docusaurus, and modern MkDocs sites.

---

## 2. Hugo: Go-Based Static Site Generator

Hugo compiles thousands of pages in milliseconds, requires zero external runtime dependencies, and features production-ready themes such as PaperMod and Terminal.

### 2.1 Installation

Install Hugo on Debian, Ubuntu, or Linux Mint:

```bash
# Install the Hugo Extended package (required for SCSS processing)
sudo apt update
sudo apt install -y hugo

# Verify installation
hugo version

```

### 2.2 Site Scaffolding

Initialize a new Hugo project and set up a Git repository:

```bash
hugo new site my-blog
cd my-blog
git init

```

The base configuration is managed through `hugo.toml`:

```toml
baseURL = 'https://yourusername.github.io/'
languageCode = 'en-us'
title = 'My Technical Blog'
theme = 'PaperMod'

```

### 2.3 Adding Themes

#### Theme 1: PaperMod

PaperMod is a streamlined, responsive, and performance-focused theme:

```bash
# Add as a Git submodule from the project root
git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
git submodule update --init --recursive

```

Configure `hugo.toml`:

```toml
baseURL = 'https://yourusername.github.io/'
languageCode = 'en-us'
title = 'My Technical Blog'
theme = 'PaperMod'

[params]
  description = "A blog on systems, Linux, and performance engineering"
  author = "Your Name"
  ShowReadingTime = true
  ShowShareButtons = false

[menu]
  [[menu.main]]
    name = "Home"
    url = "/"
    weight = 1
  [[menu.main]]
    name = "Posts"
    url = "/posts/"
    weight = 2

```

#### Theme 2: Terminal

Terminal provides a clean, retro CLI aesthetic ideal for code-heavy technical notes:

```bash
git submodule add https://github.com/panr/hugo-theme-terminal.git themes/terminal

```

Update `hugo.toml`:

```toml
theme = 'terminal'

[params]
  themeColor = 'green'
  showTerminalEmulator = true

```

### 2.4 Local Development and Content Authoring

Generate a new blog post:

```bash
hugo new posts/first-post.md

```

Edit `content/posts/first-post.md`:

```markdown
---
title: "First Post"
date: 2026-09-16T10:00:00+05:30
draft: false
tags: ["hugo", "linux"]
---

## Welcome

This is my first post deployed using Hugo and PaperMod.

```

Launch the local development server with draft rendering enabled:

```bash
hugo server -D

```

Preview the site at `http://localhost:1313`.

### 2.5 Production Build and GitHub Actions Deployment

Compiling the site locally produces static output in the `public/` directory:

```bash
hugo --minify

```

To automate builds and deployments on push, create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Hugo Site to GitHub Pages

on:
  push:
    branches: ["main"]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true
          fetch-depth: 0

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: "latest"
          extended: true

      - name: Build Hugo Assets
        run: hugo --minify

      - name: Upload Artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./public

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to Pages
        id: deployment
        uses: actions/deploy-pages@v4

```

In your GitHub repository, navigate to **Settings → Pages**, set the **Source** to **GitHub Actions**, and push your code to trigger the workflow.

---

## 3. Jekyll: Native GitHub Pages Engine

Jekyll is supported natively by GitHub Pages, allowing direct source-to-site rendering without requiring custom CI/CD pipelines.

### 3.1 Minimal Native Jekyll Configuration

Create a repository with the following minimal structure:

```text
├── _config.yml
└── index.md

```

`_config.yml`:

```yaml
title: "My Jekyll Site"
description: "A minimal Jekyll site on GitHub Pages"
theme: minima

```

`index.md`:

```markdown
---
layout: home
title: "Home"
---

## System Overview

This site is rendered natively using GitHub Pages' built-in Jekyll engine.

```

Push to GitHub, navigate to **Settings → Pages**, and select **Deploy from a branch** (`main` / `/ (root)`).

### 3.2 Local Environment Setup

To test and preview changes locally before pushing:

```bash
# Install Ruby and build tools
sudo apt install -y ruby ruby-dev build-essential

# Configure bundler directory
gem install bundler --user-install
bundle config path --local vendor/bundle

```

Create a `Gemfile`:

```ruby
source "https://rubygems.org"

gem "github-pages", group: :jekyll_plugins
gem "minima"
gem "jekyll-remote-theme"

```

Install gems and start the local server:

```bash
bundle install
bundle exec jekyll serve

```

Preview the site at `http://localhost:4000`.

### 3.3 Theme Customization and Remote Themes

To use community themes outside GitHub's pre-installed list, use `jekyll-remote-theme` in `_config.yml`:

```yaml
remote_theme: "mmistakes/minimal-mistakes-jekyll"
plugins:
  - jekyll-remote-theme

```

### 3.4 The Role of `.nojekyll`

When deploying pre-built HTML from other SSGs (such as Hugo, VitePress, Docusaurus, or MkDocs), add an empty `.nojekyll` file to the root of your deployment branch.

> **Important:** GitHub Pages treats directories beginning with an underscore (such as `_assets/`, `_app/`, or `_static/`) as private Jekyll system paths and ignores them by default. Adding a `.nojekyll` file disables this behavior, ensuring all assets are served correctly.

---

## 4. VitePress: Vue 3-Powered Documentation and Portals

VitePress pairs the performance of Vite with Vue 3 to deliver fast, documentation-focused static sites.

### 4.1 Project Initialization

Initialize a new Node.js project:

```bash
mkdir my-vitepress-site
cd my-vitepress-site
npm init -y
npm install -D vitepress vue

```

Create the documentation source tree:

```bash
mkdir -p docs/.vitepress docs/guide

```

Create `docs/.vitepress/config.js`:

```javascript
export default {
  title: 'My VitePress Portal',
  description: 'Fast, Vue-powered static documentation',
  base: '/my-vitepress-site/', // Set to '/' if deploying to a root user site
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/guide/getting-started' }
    ],
    sidebar: {
      '/guide/': [
        {
          text: 'Introduction',
          items: [
            { text: 'Getting Started', link: '/guide/getting-started' }
          ]
        }
      ]
    }
  }
}

```

Create `docs/index.md`:

```markdown
# Welcome to VitePress

A fast documentation engine built on Vite and Vue 3.

```

Create `docs/guide/getting-started.md`:

```markdown
# Getting Started

This guide explains how to configure and deploy your VitePress site.

```

Update the `scripts` section in `package.json`:

```json
{
  "scripts": {
    "docs:dev": "vitepress dev docs",
    "docs:build": "vitepress build docs",
    "docs:preview": "vitepress preview docs"
  }
}

```

### 4.2 Local Development

Run the development server:

```bash
npm run docs:dev

```

Preview the site locally at `http://localhost:5173`.

### 4.3 GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy VitePress to GitHub Pages

on:
  push:
    branches: ["main"]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci
      - run: npm run docs:build

      - name: Upload Pages Artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/.vitepress/dist

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

## 5. Docusaurus: React-Based Documentation Framework

Docusaurus is designed for complex documentation projects requiring API references, documentation versioning, internationalization, and React component integration.

### 5.1 Project Scaffolding

Generate a new Docusaurus site using the classic template:

```bash
npx create-docusaurus@latest my-website classic
cd my-website

```

Key directories include:

* `docs/`: Markdown files for documentation.
* `blog/`: Blog entries and metadata.
* `src/pages/`: Custom React page templates.
* `docusaurus.config.js`: Site settings and navigation.

Configure `docusaurus.config.js`:

```javascript
module.exports = {
  title: 'Engineering Docs',
  tagline: 'Technical documentation and system architecture notes',
  url: 'https://yourusername.github.io',
  baseUrl: '/my-website/', // Set to '/' for root username.github.io sites
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'yourusername',
  projectName: 'my-website',
  trailingSlash: false,
  themeConfig: {
    navbar: {
      title: 'Docs Home',
      items: [
        { type: 'doc', docId: 'intro', position: 'left', label: 'Manual' },
        { to: '/blog', label: 'Releases', position: 'left' }
      ]
    }
  }
};

```

### 5.2 Local Execution

Start the local development server:

```bash
npm run start

```

Access the dashboard at `http://localhost:3000`.

### 5.3 Automated GitHub Actions Deployment

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Docusaurus to GitHub Pages

on:
  push:
    branches: ["main"]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci
      - run: npm run build

      - name: Upload Pages Artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./build

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

## 6. MkDocs: Python-Based Markdown Documentation

MkDocs compiles standard Markdown files into clean, responsive documentation using configuration defined in a single YAML file.

### 6.1 Installation and Scaffolding

```bash
# Install Python tools
sudo apt install -y python3 python3-pip

# Install MkDocs and the Material theme
pip3 install --user mkdocs mkdocs-material

```

Create a new project structure:

```bash
mkdocs new my-docs
cd my-docs

```

Configure `mkdocs.yml`:

```yaml
site_name: System Documentation
site_url: https://yourusername.github.io/my-docs/

theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.instant
    - content.code.copy

nav:
  - Overview: index.md
  - Architecture: architecture.md

```

Create `docs/index.md`:

```markdown
# Overview

Welcome to the internal system architecture and deployment reference manual.

```

Create `docs/architecture.md`:

```markdown
# Architecture

Detailed system diagrams, network graphs, and deployment strategies.

```

### 6.2 Local Preview

Run the development server with live reloading:

```bash
mkdocs serve

```

Preview the documentation at `http://localhost:8000`.

### 6.3 Deployment Options

#### Option A: Direct CLI Deployment

MkDocs includes a built-in command to compile and push your site directly to the `gh-pages` branch:

```bash
mkdocs gh-deploy

```

#### Option B: GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy MkDocs to GitHub Pages

on:
  push:
    branches: ["main"]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.x"

      - run: pip install mkdocs mkdocs-material
      - run: mkdocs build

      - name: Upload Pages Artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./site

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

## 7. Comparative Assessment

| Tool | Ecosystem | Strengths | Best Used For |
| --- | --- | --- | --- |
| **Hugo** | Go | Sub-second builds, zero external dependencies, robust blog themes (PaperMod, Terminal). | Personal sites, high-volume blogs, portfolios. |
| **Jekyll** | Ruby | Built-in GitHub Pages support, simple setup, broad legacy theme support. | Simple personal sites, small blogs. |
| **VitePress** | Vue 3 | Fast development server, modern tooling, lightweight build output. | Software library docs, modern technical blogs. |
| **Docusaurus** | React | Native docs versioning, i18n support, custom React components, integrated search. | Complex API documentation, multi-version open-source projects. |
| **MkDocs** | Python | Standard Markdown files, simple single-file configuration, feature-rich Material theme. | Internal engineering runbooks, quick setup guides. |

---

## 8. Configuration Best Practices and Troubleshooting

### 8.1 Base URLs and Path Routing

Incorrectly configured asset paths are the most common cause of missing styles or broken links on GitHub Pages.

* **User Sites (`username.github.io`):** Serve from the root path (`/`). Set your base path to `'/'` or `[https://username.github.io/](https://username.github.io/)`.
* **Project Sites (`username.github.io/project-name`):** Require the repository sub-path in your asset configuration:
* **Hugo:** `baseURL = '[https://username.github.io/project-name/](https://username.github.io/project-name/)'`
* **VitePress:** `base: '/project-name/'`
* **Docusaurus:** `baseUrl: '/project-name/'`
* **MkDocs:** `site_url: [https://username.github.io/project-name/](https://username.github.io/project-name/)`



### 8.2 Resolving Build and Deployment Issues

#### Missing Styles and Broken Links

Verify that your `base` or `baseURL` configuration includes the repository path on project sites. For non-Jekyll generators, confirm that `.nojekyll` is present if you are deploying from a pre-built branch.

#### Hugo Theme Submodules Missing in CI

Ensure your checkout action has submodules enabled:

```yaml
- uses: actions/checkout@v4
  with:
    submodules: true
    fetch-depth: 0

```

#### Docusaurus Fails on Broken Links

By default, Docusaurus fails builds when broken links are detected. To temporarily downgrade these errors to warnings while debugging, update `docusaurus.config.js`:

```javascript
onBrokenLinks: 'warn'

```

#### Node Version Mismatches

Always pin specific Node.js or Python runtime versions in your GitHub Actions workflows to match your local development environment:

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 20

```

---

## 9. Automated Bootstrap Script: Hugo and PaperMod

Save the following script as `new-hugo-blog.sh` to scaffold a complete Hugo site configured with PaperMod:

```bash
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <site-name>"
  exit 1
fi

SITE_NAME="$1"
TARGET_DIR="$HOME/projects/$SITE_NAME"

mkdir -p "$HOME/projects"

if [[ -d "$TARGET_DIR" ]]; then
  echo "Error: Directory '$TARGET_DIR' already exists."
  exit 1
fi

# Scaffolding
hugo new site "$TARGET_DIR"
cd "$TARGET_DIR"

git init
git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
git submodule update --init --recursive

cat > hugo.toml <<EOF
baseURL = 'https://yourusername.github.io/'
languageCode = 'en-us'
title = 'Engineering and Systems Log'
theme = 'PaperMod'

[params]
  description = "Technical notes on infrastructure, Linux, and performance"
  author = "Your Name"
  ShowReadingTime = true

[menu]
  [[menu.main]]
    name = "Home"
    url = "/"
    weight = 1
  [[menu.main]]
    name = "Posts"
    url = "/posts/"
    weight = 2
EOF

mkdir -p content/posts
cat > content/posts/welcome.md <<EOF
---
title: "System Initialization"
date: 2026-09-16T10:00:00+05:30
draft: false
tags: ["infrastructure", "notes"]
---

Welcome to the technical deployment log.
EOF

echo "=== Hugo site '$SITE_NAME' successfully initialized at $TARGET_DIR ==="
echo "To preview your site, run:"
echo "  cd $TARGET_DIR"
echo "  hugo server -D"

```

Make the script executable and run it:

```bash
chmod +x new-hugo-blog.sh
./new-hugo-blog.sh system-portal

```

---

## References

1. [GitHub Pages Official Documentation](https://docs.github.com/en/pages)
2. [Hugo Documentation and Architecture Guide](https://gohugo.io/documentation/)
3. [Hugo PaperMod Theme Repository and Instructions](https://github.com/adityatelange/hugo-PaperMod)
4. [Jekyll Documentation and GitHub Pages Integration](https://jekyllrb.com/docs/)
5. [VitePress Documentation](https://vitepress.dev/)
6. [Docusaurus Documentation](https://docusaurus.io/docs)
7. [MkDocs User Guide](https://www.mkdocs.org/)
8. [Material for MkDocs Documentation](https://squidfunk.github.io/mkdocs-material/)
9. [GitHub Actions Documentation: Deploying to Pages](https://www.google.com/search?q=https://docs.github.com/en/pages/getting-started-with-github-pages/using-github-actions-to-publish-your-site)
