# Production Failure Recovery & Troubleshooting Matrix

This guide details common failure modes across the Hugo PaperMod static pipeline, GitHub Actions build runner, and YAML front matter parsers.

---

### Issue Index

1. [Duplicate Front Matter Keys](#1-duplicate-front-matter-keys)
2. [Empty Array Collision with Multiline Bullets](#2-empty-array-collision-with-multiline-bullets)
3. [Minifier JSON-LD Schema Crashes](#3-minifier-json-ld-schema-crashes)
4. [Unparsable Date Front Matter](#4-unparsable-date-front-matter)
5. [Submodule Missing in GitHub Actions](#5-submodule-missing-in-github-actions)
6. [Windows Line Ending Warnings (LF vs CRLF)](#6-windows-line-ending-warnings-lf-vs-crlf)

---

### 1. Duplicate Front Matter Keys

#### Symptoms
Hugo halts execution during site assembly:
```text
ERROR error building site: assemble: failed to create page from pageMetaSource /posts/...: mapping key "date" already defined

```

#### Root Cause

Two identical keys (typically `date:` or `title:`) exist in the front matter header block, causing standard YAML parsers to abort immediately.

#### Solution

Execute the automated sanitizer script to strip redundant keys:

```powershell
python sanitize.py content/posts

```

To resolve manually in the offending post:

```yaml
# INCORRECT
---
date: "2026-08-05T10:00:00+05:30"
title: "Sample Article"
date: "2026-08-05T10:00:00+05:30"
---

# CORRECT
---
title: "Sample Article"
date: "2026-08-05T10:00:00+05:30"
---

```

---

### 2. Empty Array Collision with Multiline Bullets

#### Symptoms

```text
ERROR error building site: assemble: failed to create page: value is not allowed in this context
  categories: []
>   - "Productivity"

```

#### Root Cause

`categories: []` terminates the array inline as an empty structure. The subsequent indented bullet items (`- ...`) conflict with the inline definition.

#### Solution

Convert taxonomy fields to valid bracketed lists:

```yaml
# INCORRECT
categories: []
  - "Productivity"
  - "Automation"

# CORRECT (Option A: Inline)
categories: ["Productivity", "Automation"]

# CORRECT (Option B: Block)
categories:
  - "Productivity"
  - "Automation"

```

---

### 3. Minifier JSON-LD Schema Crashes

#### Symptoms

```text
ERROR error building site: render: failed to process ".../index.html": expected comma character or an array or object ending

```

Or:

```text
template: _partials/templates/schema_json.html: can't evaluate field publisherType in type bool

```

#### Root Cause

1. Double quotes inside `summary` or `title` fields break Hugo's automatic JSON-LD metadata generation.
2. Setting `schema: false` in `hugo.yaml` causes a Go template type error because PaperMod expects `.Site.Params.schema` to be a dictionary, not a boolean.

#### Solution

Ensure `hugo.yaml` contains safe minifier flags and sets `publisherType`:

```yaml
minify:
  disableJSON: true
  minifyOutput: true

params:
  schema:
    publisherType: "Person"

```

---

### 4. Unparsable Date Front Matter

#### Symptoms

```text
ERROR the "date" front matter field is not a parsable date: see content/posts/...

```

#### Root Cause

Date string is empty, uses non-standard formatting (e.g., `August 4, 2026`), or lacks quotes around timestamps containing colons and offsets.

#### Solution

Format all timestamps using ISO-8601 strings:

```yaml
# INCORRECT
date: 2026-08-04 10:00:00
date: 

# CORRECT
date: "2026-08-04T10:00:00+05:30"

```

Run `python sanitize.py content/posts` to infer missing dates from post filenames (`YYYY-MM-DD-*.md`).

---

### 5. Submodule Missing in GitHub Actions

#### Symptoms

The CI build runs in seconds, but produces a blank page, missing CSS, or logs:

```text
error: theme "PaperMod" not found

```

#### Root Cause

The GitHub Actions checkout runner did not fetch Git submodules recursively.

#### Solution

Verify `.github/workflows/deploy.yml` sets `submodules: recursive`:

```yaml
- name: Checkout
  uses: actions/checkout@v4
  with:
    submodules: recursive
    fetch-depth: 0

```

---

### 6. Windows Line Ending Warnings (LF vs CRLF)

#### Symptoms

Git outputs hundreds of lines during commit:

```text
warning: in the working copy of '...', LF will be replaced by CRLF the next time Git touches it

```

#### Root Cause

Hugo generates static files (`public/`) using Unix line endings (`LF`), while Git on Windows flags conversions to DOS line endings (`CRLF`). Furthermore, the generated output directory `public/` should not be checked into source control.

#### Solution

1. Add `public/` and build artifacts to `.gitignore`:
```gitignore
public/
resources/
.hugo_build.lock

```


2. Remove tracked build artifacts from the Git cache:
```powershell
git rm -r --cached public

```


3. Set global line-ending normalization:
```powershell
git config --global core.autocrlf true
