---
title: "Building an Autonomous Mobile & Desktop Document Processing AI Agent with OpenClaw"
date: "2026-08-04"
categories: ["AI & Automation", "Open Source", "Linux"]
tags: ["OpenClaw", "Termux", "Linux Mint", "Android", "Ollama", "Telegram Bot", "ImageMagick", "OCR"]
---

Setting up a self-hosted AI agent that does more than just chat opens up incredible automation possibilities. By combining an open-source agentic framework with lightweight system utilities, you can turn a low-power phone or a modest desktop into a 24/7 personal document processing hub.

This guide walks through configuring **OpenClaw** (formerly known as Clawdbot) across Android Termux and Linux Mint, setting up messaging channel integrations, running local LLMs, and defining custom Markdown skills to automatically clean, compress, and OCR scanned office documents.

---

## What is OpenClaw?

OpenClaw is an open-source, self-hosted AI agent framework designed to execute actions directly on your local hardware. Unlike standard conversational interfaces, OpenClaw operates via a messaging gateway—such as Telegram, WhatsApp, or Discord—allowing you to send tasks from your phone and have your home hardware or phone environment process them in real time.

### Core Architecture & Features
* **Gateway Process:** A background daemon (built on Node.js) that handles platform connections, session states, and tool loops.
* **Persistent Memory:** Uses structured files like `memory.md` to store context, preferences, and long-term rules.
* **Skills Ecosystem:** Plug-and-play modules that grant the agent authority to interface with GitHub, Google Calendar, command-line interfaces, and local document utilities.
* **Privacy-First Operations:** Can route tasks entirely through local LLM runners like Ollama or low-cost cloud APIs like Gemini 2.0/2.5 Flash.

---

## Environment Setup: Android Termux & Linux Mint

### 1. Android Setup (via Termux)
Running OpenClaw directly on Android enables hardware interaction (like camera and storage) and creates a portable, low-power server.

#### Base Installation
```bash
# Update and install dependencies (F-Droid Termux build recommended)
pkg update && pkg install nodejs-lts python git proot-distro

# Install OpenClaw globally
npm install -g openclaw@latest

```

#### Stabilizing the Mobile Node

* **Wake Lock:** Enable Termux's persistent background service to prevent Android app hibernation (`termux-wake-lock`).
* **Hardware Controls:** Install the **Termux:API** Android app and bridge it inside Termux:
```bash
pkg install termux-api

```


* **Graphics / PRoot (Optional for GUI Apps like OpenClaw Game):**
```bash
pkg install proot-distro
proot-distro install ubuntu
proot-distro login ubuntu

```



---

### 2. Linux Mint Setup & Optimization

Linux Mint provides a stable Linux environment for running background gateway daemons and local model inference.

#### Installing Node.js 22 & Build Tools

```bash
# Install NodeSource repository for Node.js 22
curl -fsSL [https://deb.nodesource.com/setup_22.x](https://deb.nodesource.com/setup_22.x) | sudo -E bash -

# Install dependencies and global package managers
sudo apt install -y nodejs build-essential python3 imagemagick ghostscript tesseract-ocr
sudo npm install -g pnpm
sudo pnpm add -g openclaw@latest

```

#### Optimizing Low-Resource Systems (4GB RAM)

If running on hardware with limited RAM:

1. **Desktop Overhead:** Use lightweight desktop environments like XFCE or MATE.
2. **Node.js RAM Cap:** Constrain Node.js memory usage when initializing the daemon:
```bash
node --max-old-space-size=1024 $(which openclaw) gateway

```


3. **Headless Chat:** Avoid keeping the web UI open in a browser; interact exclusively via Telegram or WhatsApp.

---

## Connecting Messaging Channels & AI Models

### 1. Linking Telegram Bot

1. Open Telegram and search for `@BotFather`.
2. Send `/newbot`, name your bot, and save the generated **API Token**.
3. Run the onboarding wizard in your terminal:
```bash
openclaw onboard

```


4. Select **Telegram**, paste your token, start a chat with your bot on Telegram, and approve the pairing code displayed in the terminal.

### 2. Model Selection: Local vs. Cloud

| Requirement | Recommended Model | Setup |
| --- | --- | --- |
| **Free Cloud Tier / Speed** | Gemini 2.5 Flash | Select Google Antigravity / API Key during onboarding |
| **High Reasoning / Code** | Claude 3.5 / 4.5 Sonnet | Set Anthropic API Key in `~/.openclaw/openclaw.json` |
| **Local Privacy (Low RAM)** | Qwen 2.5 Coder 1.5B | Run via Ollama (`ollama pull qwen2.5-coder:1.5b`) |
| **Local Privacy (Medium VRAM)** | Qwen 2.5 Coder 7B | Run via Ollama (`ollama pull qwen2.5-coder:7b`) |

#### Configuring Ollama in OpenClaw

Edit `~/.openclaw/openclaw.json`:

```json
{
  "agents": {
    "default": "doc-wizard",
    "providers": {
      "ollama": {
        "baseUrl": "[http://127.0.0.1:11434](http://127.0.0.1:11434)",
        "apiKey": "ollama"
      }
    }
  }
}

```

---

## Complete Project Structure & System Templates

To transform your bot into a document processing engine, use this structured Markdown layout. These files define the project workspace (`CLAUDE.md`), the AI personality/rules (`AGENTS.md`), and the command pipeline execution (`SKILL.md`).

### Workspace Hierarchy

```text
~/.openclaw/
├── openclaw.json
├── agents/
│   └── doc-wizard/
│       └── AGENTS.md
└── skills/
    └── paper-pro/
        └── SKILL.md
~/document-workspace/
└── CLAUDE.md

```

---

### Template 1: `CLAUDE.md` (Workspace Context)

**Path:** `~/document-workspace/CLAUDE.md`

```markdown
# Project: Office Document Automator
Context: Professional document cleanup, compression, and PDF merging.

## Tech Stack
- OS: Linux Mint / Android Termux
- Core Tools: ImageMagick (magick), Ghostscript (gs), Tesseract (tesseract)

## Required Commands
- Clean: magick [input] -colorspace gray -deskew 40% -trim [output]
- Merge: gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook -o [final.pdf] [inputs]
- OCR: tesseract [input] [output_prefix]

## Standards
- Max file size: 1.0MB per image.
- Output format: Compressed PDF.
- Quality: Lossless text preservation.

```

---

### Template 2: `AGENTS.md` (Agent Identity & Rules)

**Path:** `~/.openclaw/agents/doc-wizard/AGENTS.md`

```markdown
# Agent: Document-Wizard
Role: Autonomous Office Automation Orchestrator.

## Identity & Tone
- Name: Wizard
- Style: Spartan, informative, and technical.
- Address user as: Phuchung.

## Operational Rules
1. Shadow Removal: Mandatory for all incoming document photos.
2. Deskewing: Auto-align any text tilted > 5 degrees.
3. Batch Processing: Combine all images in a single session into one PDF.
4. Compression: Ensure final PDF uses /ebook or /screen settings.

## Prohibited Actions
- Do not upload files to cloud storage without explicit confirmation.
- Do not delete original files until the PDF is successfully verified.

```

---

### Template 3: `SKILL.md` (Execution Pipeline)

**Path:** `~/.openclaw/skills/paper-pro/SKILL.md`

```markdown
---
name: paper-pro
description: Professional document cleaning, margin optimization, and PDF merging.
version: 1.0.0
---

# Skill: Paper-Pro

## Instructions
1. Detect document edges and trim black borders.
2. Apply adaptive thresholding to remove shadows and smudges.
3. Add 5% white margins to the optimized image.
4. Compress the image to under 1MB using 85% JPEG quality.
5. If multiple images exist, merge into a single PDF using Ghostscript.

## Tool Requirements
- ImageMagick
- Ghostscript
- Tesseract (optional for OCR)

## Triggers
- "Clean these photos"
- "Make a PDF from these images"
- "Remove shadows and compress"

```

---

## How the Document Pipeline Works

1. **Upload:** You drop 5 document photos into your Telegram or WhatsApp chat.
2. **Orchestration:** The agent receives the files, reads `AGENTS.md` and `SKILL.md`, and plans the CLI execution sequence.
3. **Image Cleanup (ImageMagick):** Shadows are removed via gray thresholding, text lines are deskewed, and borders are trimmed.
4. **PDF Merging (Ghostscript):** Images are compiled into a multi-page PDF using the `/ebook` optimization profile (150 DPI), keeping overall file size under 1MB without sacrificing text legibility.
5. **OCR (Tesseract):** Text is extracted into an accompanying text file if requested.
6. **Delivery:** The agent posts the final `.pdf` and optional plain text back to your mobile chat.

---

## Managing and Maintaining the Gateway

```bash
# Start background daemon
openclaw gateway --install-daemon

# Check running daemon status
openclaw status

# Restart daemon after editing configuration or skills
openclaw gateway restart

# Run diagnostic check for broken dependencies
openclaw doctor

```

```

```
