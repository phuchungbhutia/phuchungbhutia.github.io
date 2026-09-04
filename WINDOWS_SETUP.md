# Local Development & Tooling Runbook (Windows + VSCodium)

This document covers configuring a local environment for writing, validating, and testing static posts on Windows 11/10 using VSCodium.

---

### Prerequisites & Toolchain Installation

Open **PowerShell as Administrator** and install the core dependencies via the Windows Package Manager:

```powershell
# 1. Install Hugo Extended Edition
winget install Hugo.Hugo.Extended --source winget

# 2. Install Git
winget install Git.Git --source winget

# 3. Install Python 3.11+
winget install Python.Python.3.11 --source winget

# 4. Install VSCodium
winget install VSCodium.VSCodium --source winget

```

Close and restart your terminal session. Verify the installed binaries:

```powershell
hugo version      # Must indicate 'extended'
git --version
python --version

```

---

### Recommended VSCodium Extensions

Open VSCodium (`Ctrl + Shift + X`) and install the following extensions from the Open VSX Registry:

| Extension Name | Extension ID | Utility |
| --- | --- | --- |
| **Front Matter CMS** | `eliostruyf.vscode-front-matter` | Visual metadata dashboard and tagging helper |
| **Markdown All in One** | `yzhang.markdown-all-in-one` | Auto-formatting, keyboard shortcuts, TOC generator |
| **YAML** | `redhat.vscode-yaml` | YAML schema validation for front matter and configs |
| **GitLens (Community)** | `eamodio.gitlens` | Commit blame and Git history visualization |

---

### Environment Bootstrap

1. Clone your repository with Git submodules:
```powershell
git clone --recurse-submodules [https://github.com/phuchungbhutia/phuchungbhutia.github.io.git](https://github.com/phuchungbhutia/phuchungbhutia.github.io.git)
cd phuchungbhutia.github.io

```


2. Launch the folder inside VSCodium:
```powershell
codium .

```


3. Configure your Git user profile:
```powershell
git config user.name "Phuchung Bhutia"
git config user.email "your-email@domain.com"

```



---

### Daily Publishing Workflow

#### Step 1: Create a New Post

Create a new Markdown file inside `content/posts/` with the standard date prefix:
`content/posts/2026-09-04-system-audit-notes.md`

Add the standard front matter schema:

```yaml
---
title: "Modern Audit Automation and Public Accounting Architecture"
date: "2026-09-04T10:00:00+05:30"
categories: ["Audit and Compliance", "Public Finance"]
tags: ["automation", "reporting", "governance"]
summary: "Technical notes on reconciling public audit trails using automated parsers."
---

Article text starts here. Standard code blocks render without template collisions:

```python
def reconcile(ledger):
    return sum(entry['amount'] for entry in ledger)

```

```

#### Step 2: Validate Front Matter
Run the repository sanitizer to clean syntax, check tags, and verify dates:
```powershell
python sanitize.py content/posts

```

#### Step 3: Run Local Preview Server

Start the development server with draft rendering enabled:

```powershell
hugo server -D

```

Open `http://localhost:1313/` in your browser to verify changes with hot-reloading.

#### Step 4: Test Minification

Verify that the static minifier compiles cleanly without JSON errors:

```powershell
hugo --minify

```

#### Step 5: Push to Production

```powershell
git add content/posts/
git commit -m "content: add post on audit automation architecture"
git push origin main

```
