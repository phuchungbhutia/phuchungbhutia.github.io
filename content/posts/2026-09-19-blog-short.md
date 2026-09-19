---
title: "A Reliable Prompt for Publication-Ready Markdown"
date: "2026-09-19"
categories: ["Writing", "Markdown"]
tags: ["markdown", "prompt-engineering", "content-workflows", "yaml", "technical-writing"]
description: "A practical guide to designing a structured prompt that produces consistent, publication-ready Markdown."
---

# A Reliable Prompt for Publication-Ready Markdown

A well-designed Markdown prompt does more than ask for an article. It defines the document structure, metadata format, writing style, formatting rules, source requirements, and final-output boundaries.

```prompt
Write publication-ready Markdown. Return ONLY raw Markdown, no code fences.
Inputs: [Topic], [Audience], [Depth], [Date], [Keywords], [Takeaway], [Notes].

- YAML: Line 1 MUST be `---`. Close with `---`. NEVER use `#` in YAML. Quote ALL values; no unquoted `*` or `&`. Exact format:
---
title: "X"
date: "YYYY-MM-DD"
categories: ["A", "B"]
tags: ["x"]
description: "One sentence."
---
- Structure: One H1 after closing `---`. Logical H2/H3. Ban "Intro/Conclusion".
- Style: Authoritative. Ban AI buzzwords (delve, tapestry). Use "and", not "&".
- Format: Max one blank line between blocks. No trailing spaces. Bullets `-`, aligned tables.
- Math/Code: `$inline$`, `$$display$$`. Escape `$` for currency. Code fences need language tags.
- Links: Strip ALL tracking params (utm_*, ref, source) and redirect wrappers (url?q=). Never invent URLs.
- Refs: End `## References`: source name on one line, clean raw URL on next. No markdown links.
- End with one newline.

```
The prompt examined here is designed to produce consistent blog posts from a small set of inputs:

- `[Topic]`
- `[Audience]`
- `[Depth]`
- `[Date]`
- `[Keywords]`
- `[Takeaway]`
- `[Notes]`

Its main strength is that it combines editorial instructions with machine-checkable formatting rules. That makes it useful for blogs, documentation systems, newsletters, knowledge bases, and automated publishing workflows.

## What the Prompt Controls

The prompt controls five important parts of the writing process:

| Area | Instruction | Purpose |
|---|---|---|
| Output format | Return only raw Markdown | Prevents explanations, wrappers, and code fences around the document |
| Metadata | Use YAML front matter | Makes the document suitable for static-site generators and content-management systems |
| Structure | Use one H1 and logical H2/H3 headings | Creates a predictable document hierarchy |
| Style | Use an authoritative tone and avoid selected expressions | Improves consistency and reduces unwanted wording |
| References | End with a source name and raw URL | Provides a simple, readable citation format |

This is more reliable than a short instruction such as “write a blog post in Markdown” because the expected output is explicitly defined.

## Why Raw Markdown Matters

The instruction to return only raw Markdown prevents a common failure: placing the article inside a fenced code block.

For example, an unsuitable response may begin like this:

```markdown
# Sample Article

Article content
```

That presentation displays the Markdown as code instead of allowing a Markdown renderer to interpret it. A raw Markdown response should begin directly with the document metadata or heading.

The prompt therefore establishes a clear boundary:

> The response itself must be the finished document, not an explanation of how to create the document.

This is especially important when the output will be copied into a `.md` file, committed to a repository, or sent directly to a publishing system.

## Designing the YAML Front Matter

The prompt requires YAML front matter to appear at the beginning of the document:

```yaml
---
title: "X"
date: "YYYY-MM-DD"
categories: ["A", "B"]
tags: ["x"]
description: "One sentence."
---
```

The opening `---` identifies the beginning of the metadata block, and the closing `---` separates metadata from the article body. Many static-site generators use this pattern to read page properties before rendering the Markdown.

### Required Fields

Each field has a specific role:

- `title` gives the article its public heading and page title.
- `date` records the publication or content date.
- `categories` groups the article into broad subject areas.
- `tags` identifies narrower topics and searchable terms.
- `description` provides a short summary for indexes, previews, or search metadata.

The prompt limits categories to two values. This encourages broad, meaningful classification instead of creating a long list of overlapping categories.

### Why Quote Every Value

The instruction to quote all values reduces ambiguity in YAML. Dates, special characters, punctuation, and strings beginning with reserved characters can otherwise be interpreted according to YAML rules rather than as plain text.

For example:

```yaml
title: "Internal Controls in Municipal Accounting"
date: "2026-09-19"
categories: ["Auditing", "Public Finance"]
tags: ["internal-controls", "municipal-accounting"]
description: "A practical guide to documenting internal controls in municipal accounting."
```

Quoted values also make the format easier to validate programmatically.

### Why Avoid `#` in YAML

In YAML, the `#` character introduces a comment when used in the appropriate context. The prompt therefore bans `#` in YAML values to avoid accidental comments or malformed metadata.

For example, an unquoted value such as the following can create parsing problems:

```yaml
description: Audit # checklist
```

The text after `#` may be treated as a comment. Quoting the complete value is safer:

```yaml
description: "Audit # checklist"
```

The prompt goes further by banning `#` entirely in YAML, which creates a stricter and simpler validation rule.

## Building the Heading Structure

The prompt requires one H1 immediately after the closing YAML delimiter:

```markdown
# Article Title
```

The H1 serves as the document’s primary heading. Subsequent sections should use H2 headings, with H3 headings reserved for subsections.

A suitable hierarchy looks like this:

```markdown
# Main Article Title

## First Major Section

### Supporting Detail

## Second Major Section
```

This structure improves readability and helps tools interpret the document outline.

### Why One H1 Is Useful

Multiple H1 headings can make the document hierarchy unclear. A single H1 establishes one central subject, while H2 and H3 headings organize the supporting discussion.

For example, an article about audit documentation could use:

```markdown
# How to Prepare an Audit Requisition

## Identify the Audit Objective

## Organize Supporting Records

### Financial Statements

### Registers and Vouchers

## Review the Requisition Before Issue
```

The hierarchy reflects the relationship between the article, its major steps, and its supporting details.

### Avoiding “Intro” and “Conclusion” Headings

The prompt bans headings named “Intro” and “Conclusion.” This encourages headings that communicate the actual subject matter.

Instead of:

```markdown
## Introduction
```

use:

```markdown
## Why Audit Documentation Matters
```

Instead of:

```markdown
## Conclusion
```

use:

```markdown
## Practical Takeaways
```

Specific headings are more useful to readers scanning the article and more informative when displayed in a table of contents.

## Controlling Editorial Style

The style rules are deliberately short:

- Use an authoritative tone.
- Avoid selected AI-related buzzwords.
- Use “and” instead of “&”.

These rules establish a professional baseline without prescribing every sentence.

### Authoritative Does Not Mean Complicated

An authoritative article should be confident, precise, and evidence-based. It should not rely on unnecessarily complex language.

Weak wording:

> It might perhaps be considered that maintaining records could possibly help improve audit work.

Stronger wording:

> Complete records improve audit verification and reduce avoidable follow-up.

The second sentence is direct and makes a clear claim.

### Avoiding Generic Buzzwords

Words such as “delve” and “tapestry” can make technical writing sound formulaic or ornamental. Replacing them with plain verbs usually improves clarity.

| Avoid | Prefer |
|---|---|
| Delve into the issue | Examine the issue |
| A tapestry of controls | A system of controls |
| Leverage the process | Use the process |
| Unlock insights | Identify findings |
| Transformative solution | Practical solution |

The goal is not to ban creativity. It is to prevent vague language from replacing specific explanations.

### Using “And” Instead of “&”

The ampersand is appropriate in some official names, branding, citations, and technical notation. However, using “and” in ordinary prose creates a consistent editorial style.

Preferred:

> Accounting and audit procedures should be documented together.

The prompt’s rule should be interpreted as a style preference rather than a command to alter official names or source titles.

## Handling Math and Code

The prompt provides separate rules for mathematical expressions and code.

### Inline and Display Mathematics

Inline mathematics should use a single pair of dollar signs:

```markdown
The control rate is calculated as $r = \frac{p}{n}$.
```

Display mathematics should use double dollar signs:

```markdown
$$
r = \frac{p}{n}
$$
```

The prompt also states that currency dollar signs must be escaped:

```markdown
The estimated cost is \$2,500.
```

This distinction prevents a currency amount from being interpreted as the beginning of a mathematical expression.

Support for mathematical syntax can vary between Markdown processors. If the publishing platform does not support mathematical rendering, the author should use plain text or the platform’s documented syntax.

### Language Tags for Code Fences

Code fences must include a language tag:

````markdown
```bash
echo "Backup completed"
```
````

A language tag helps readers identify the intended language and allows many renderers to apply syntax highlighting.

Examples include:

- `bash` for shell commands.
- `python` for Python code.
- `javascript` for JavaScript.
- `sql` for SQL statements.
- `json` for JSON data.
- `yaml` for YAML examples.

A code fence without a language tag is less informative:

````markdown
```
echo "Backup completed"
```
````

The stricter rule also makes the output easier to validate automatically.

## Making the Input Variables Useful

The input placeholders make the prompt reusable, but each variable should have a clear function.

| Input | What it should define |
|---|---|
| `[Topic]` | The central subject of the article |
| `[Audience]` | Readers’ knowledge level, role, and needs |
| `[Depth]` | Expected scope, detail, and technical complexity |
| `[Date]` | Metadata date and, where appropriate, time context |
| `[Keywords]` | Terms to use naturally in headings and body text |
| `[Takeaway]` | The practical result readers should remember |
| `[Notes]` | Facts, examples, constraints, or source material supplied by the author |

### Topic

The topic should be specific enough to support a focused article.

Less precise:

> Auditing

More precise:

> How municipal auditors can document verification of grant expenditure records

The second topic gives the writer a clear subject, scope, and professional context.

### Audience

Audience information affects vocabulary, examples, and explanation depth.

Examples include:

- Beginners learning Markdown.
- Technical writers maintaining documentation.
- Municipal accounting staff preparing audit records.
- Developers building a static-site publishing workflow.

An article for beginners should define terms. An article for experienced auditors can focus more quickly on procedures, evidence, and controls.

### Depth

Depth should describe the expected level of treatment rather than merely saying “long” or “short.”

Useful values include:

- Brief overview.
- Practical guide.
- Detailed technical explanation.
- Advanced reference article.

For example, a practical guide may include steps, checklists, and examples. An advanced reference article may include edge cases, validation rules, and implementation considerations.

### Date

The date should normally use the ISO format `YYYY-MM-DD`:

```yaml
date: "2026-09-19"
```

This format is unambiguous and sorts correctly in filenames, databases, and content systems.

### Keywords

Keywords should be used naturally. They should not be repeated mechanically or inserted where they weaken the sentence.

For an article about Markdown publishing, suitable keywords might include:

- Markdown front matter.
- YAML validation.
- static-site generator.
- content workflow.
- document structure.

Keywords are most useful when they reflect the article’s genuine subject rather than functioning as a separate block of repeated search terms.

### Takeaway

The takeaway defines the practical value of the article. It answers a central question:

> What should the reader be able to understand or do after reading this article?

For example:

> Readers should be able to use the prompt to generate consistent Markdown files that can be reviewed and published with minimal cleanup.

This statement keeps the article focused.

### Notes

Notes are useful for facts, examples, terminology, constraints, and organizational preferences. They should not be treated automatically as verified sources.

If the notes contain a legal requirement, technical specification, government procedure, or current statistic, the writer should verify the claim before presenting it as fact.

## Adding Sources Correctly

The prompt requires a final references section:

```markdown
## References

Source Name
https://example.org/source
```

The source name appears on one line, followed by the raw URL on the next line. This differs from ordinary Markdown links, which use the format `[Source Name](URL)`.

The references section should contain only sources that support claims made in the article. It should not be used to create an unrelated reading list.

### Source Quality

For technical Markdown and YAML guidance, primary specifications are preferable. The YAML specification documents the syntax and behavior of YAML constructs such as quoted scalars and comments. The CommonMark specification documents core Markdown behavior, including headings and fenced code blocks. [yaml](https://yaml.org/spec/1.2.1/)

For practical guidance, official documentation from the relevant software or publishing platform is generally preferable to an unattributed blog post.

### Reference Placement

References should appear at the end of the article, after all substantive sections:

```markdown
## References

YAML 1.2.2 Specification
https://yaml.org/spec/1.2.2/

CommonMark Specification
https://spec.commonmark.org/
```

The document should end with one newline after the final URL.

## Validation Before Publication

A prompt becomes more dependable when its output can be checked against explicit rules.

A simple review checklist can verify the following:

- The first line is exactly `---`.
- The YAML block closes with `---`.
- Every YAML value is quoted.
- No `#` appears in the YAML block.
- The `date` uses `YYYY-MM-DD`.
- The `categories` array contains no more than two values.
- Exactly one H1 appears after the YAML block.
- No heading is named “Intro” or “Conclusion”.
- Code fences have language tags.
- Currency dollar signs are escaped where necessary.
- The final section is `## References`.
- Each reference contains a source name and raw URL.
- The document ends with one newline.
- No explanatory text appears outside the Markdown document.

For automated workflows, these checks can be implemented with a Markdown parser, YAML parser, regular expressions, or a combination of validation tools. Parser-based validation is generally safer for structure, while regular expressions are useful for simple style checks.

## A Refined Reusable Template

The prompt can be organized into a reusable template like this:

```text
Write a publication-ready Markdown article using these inputs:

Topic: [Topic]
Audience: [Audience]
Depth: [Depth]
Date: [Date]
Keywords: [Keywords]
Takeaway: [Takeaway]
Notes: [Notes]

Return only raw Markdown. Do not wrap the response in a code fence or add commentary.

Use YAML front matter as the first block. The first line must be exactly:
---

Use this exact field structure:
title: "X"
date: "YYYY-MM-DD"
categories: ["A", "B"]
tags: ["x"]
description: "One sentence."

Close the YAML block with:
---

Follow the closing delimiter with exactly one H1. Use logical H2 and H3 headings. Do not use headings named "Intro" or "Conclusion".

Write in an authoritative, clear style. Avoid the words "delve" and "tapestry". Use "and" instead of "&" in ordinary prose.

Use Markdown bullets with "-". Align tables. Allow no trailing spaces and no more than one blank line between blocks.

Use $...$ for inline mathematics and $$...$$ for display mathematics. Escape currency dollar signs. Add a language tag to every code fence.

End with:
## References

List each source name on one line and its raw URL on the next line.

End the response with one newline.
```

This template separates the input data from the output rules. That makes it easier to reuse in a writing assistant, shell script, spreadsheet workflow, or document-processing system.

## Practical Takeaways

- Define the output format before asking for content.
- Use quoted YAML values when predictable metadata parsing matters.
- Require one clear heading hierarchy.
- State style preferences with concrete examples or banned patterns.
- Distinguish mathematical notation from currency.
- Require language identifiers for code blocks.
- Treat supplied notes as input material, not automatically verified evidence.
- Add references only for sources that support the article.
- Validate the generated Markdown before publishing it.

A strong Markdown prompt functions as a lightweight editorial specification. It does not replace human review, but it reduces formatting errors, clarifies expectations, and makes the final document easier to publish and maintain.

## References

YAML 1.2.2 Specification
[https://yaml.org/spec/1.2.2/](https://yaml.org/spec/1.2.2/)

CommonMark Specification
[https://spec.commonmark.org/](https://spec.commonmark.org/)
