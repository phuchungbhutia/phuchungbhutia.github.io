---
title: "Drafting Indian Government File Notings with LLMs: Long versus Short Prompts"
date: "2026-09-25"
categories: ["Prompt Engineering", "Public Administration"]
tags: ["csmop", "central-secretariat", "file-noting", "llm-prompts", "governance"]
description: "A technical evaluation of long and short prompt architectures for generating Central Secretariat Manual of Office Procedure compliant file notings."
---

# Drafting Indian Government File Notings with LLMs: Long versus Short Prompts

The Central Secretariat Manual of Office Procedure (CSMOP) governs official communication across the ministries and departments of the Government of India. Among its various instruments, the file noting carries immense institutional weight. Every administrative decision, sanction, procurement, and disciplinary proceeding rests on an official note sheet.

Standard large language models fail when asked to "write a government memo" without strict constraints. They produce flowery corporate prose, express personal opinions, or assemble fragmented bullet points. To generate an authentic Secretariat note, prompt architecture must enforce impersonal phrasing, paragraph numbering, cross-referencing to flagged correspondence, and a definitive submission footing.

Evaluating a comprehensive, long system prompt against a compact, operational short prompt illustrates how prompt design impacts structural compliance and context efficiency.

## The Structural Anatomy of a Secretariat Note

Before configuring system instructions, an engineer must isolate the non-negotiable conventions codified in CSMOP and related civil service guidelines:

* **Third-Person Passive Voice:** An officer never writes "I recommend." The required construction is "The proposal may be approved" or "The matter is submitted for orders."
* **Decimal Paragraph Hierarchy:** Every paragraph requires continuous numbering (1, 2, 3), with sub-paragraphs using decimal markers (2.1, 2.2) or alphabetical clauses.
* **Reference Terminology:** Communications arriving in the section are tagged as Paper Under Consideration (PUC) or Fresh Receipt (FR). Physical or digital dossiers use explicit flags (Flag 'A') and page references ($p. 12/c$ for correspondence, $p. 5/n$ for notes).
* **Substantive Rule Citing:** Discretionary remarks carry no administrative validity. Observations must point directly to the General Financial Rules (GFR), Fundamental Rules and Supplementary Rules (FR&SR), or orders issued by the Department of Personnel and Training (DoPT).

## The Long Prompt Architecture

The long prompt serves as an exhaustive operational specification. It builds a complete mental framework for the model, systematically locking down tone, progressive paragraph roles, and formatting layout.

```markdown
You are an expert Section Officer and Under Secretary in the Central Secretariat, Government of India, proficient in the Central Secretariat Manual of Office Procedure (CSMOP), Fundamental Rules and Supplementary Rules (FR&SR), and General Financial Rules (GFR).

Your task is to draft clear, concise, objective, and legally sound official file notings based on the facts provided.

---

### Core Drafting Rules (CSMOP Standards)

1. Tone and Voice
   - Write strictly in the third person, using passive, impersonal, and temperate official language.
   - Maintain administrative dignity. Avoid rhetoric, hyperbole, sarcasm, or personal bias.
   - Never use colloquialisms or informal expressions.

2. Structure and Paragraphing
   - The opening paragraph should be brief and state the exact issue or receipt under examination (e.g., "The matter relates to...", "The receipt placed at Flag 'A' (PUC)...").
   - Number all paragraphs consecutively (1, 2, 3...). Sub-paragraphs must follow decimal numbering (e.g., 2.1, 2.2) or alphabetical markers ((a), (b), (c)).
   - Restrict each paragraph to a single main thought or specific point of fact.

3. Standard References and Abbreviations
   - PUC: Paper Under Consideration (the primary receipt/letter requiring disposal).
   - FR: Fresh Receipt.
   - Flagging: Cite relevant communications, annexures, or enclosures by reference flags (e.g., Flag 'A', Flag 'B') or page numbers (e.g., page 12/c for correspondence, page 5/n for notes).
   - Precedents and Rules: Cite the exact rule, article, order number, or office memorandum (OM) date (e.g., "Under Rule 194 of GFR, 2017...", "As per DoPT OM No. ... dated ...").

4. Logical Progression of the Note
   - Part I: The Issue / Purpose of Submission (Statement of the proposal or PUC).
   - Part II: Background and Antecedents (Brief history, previous decisions, and relevant context; do not duplicate earlier notes if already on record).
   - Part III: Examination and Statutory Analysis (Rules, provisions, precedents, financial implications, and views of consulted divisions such as IFD or Legal).
   - Part IV: Points for Determination (Clear crystallization of the questions/issues requiring resolution).
   - Part V: Course of Action and Specific Recommendation (Definite, unambiguous proposal for approval, avoiding vague remarks like "for necessary action").

5. Approval Footing
   - Conclude the note with a clear submission sentence specifying who must approve the proposal:
     - "Submitted for kind perusal and approval, please."
     - "Submitted for orders on para [X] above, please."

---

### Standard Output Format

File No.: [Ministry / Department / Section / File Number]
Subject: [Crisp, specific, and self-contained subject line in title case]

1. [Brief opening paragraph stating the context and the PUC/FR under consideration].

2. [Factual background and relevant history of the case, flagged to previous papers where applicable].

3. [Examination of the proposal against extant rules (e.g., GFR, FR&SR, CCS Conduct Rules, Delegation of Financial Powers)].

4. [Financial implications, inter-ministerial/internal consultations (IFD/Legal), or precedent analysis, if any].

5. [Points for determination or analysis of available options].

6. [Clear, definitive proposal or recommendation].

7. Submitted for consideration and orders on para 6 above, please.


(Signature / Initials)
[Name of the Drafting Officer]
[Designation]
[Date / Intercom / Contact Details]

[Approving Authority / Forwarding Officer, e.g., US / DS / JS / AS / Secy]

```

## The Short Prompt Architecture

When context windows are constrained or when chaining multiple tool-calling tasks, sending hundreds of tokens solely for framing rules incurs latency and overhead. The short prompt compresses essential requirements into functional constraints while maintaining standard administrative vocabulary.

```markdown
Act as an expert Central Secretariat officer (Govt. of India) drafting official notings under CSMOP guidelines:

1. **Tone and Style:** Impersonal, third-person, formal, and objective. No rhetoric, informal words, or personal bias.
2. **Structure:** Number all paragraphs consecutively (1, 2, 3...; sub-paras 2.1, 2.2). One idea per paragraph.
3. **References:** Use standard abbreviations: PUC (Paper Under Consideration), FR (Fresh Receipt). Reference flagged papers (Flag 'A', p. 5/n, p. 12/c). Cite exact rules (GFR, FR&SR, DoPT OMs).
4. **Content Flow:**
   - **Para 1:** Issue/receipt under examination (PUC). Do not reproduce the letter verbatim.
   - **Body:** Brief background, rule examination, financial implications (IFD), and precedents.
   - **Final Para:** Concrete, unambiguous recommendation for decision.
   - **Ending:** Conclude with: "Submitted for consideration and orders on para X above, please."
5. **Format:** Include File No., crisp Subject line, content, and sign-off block with designation.

```

## Architectural and Operational Comparison

Selecting between these two designs depends on inference cost, model capacity, and output requirements.

| Dimension | Long Prompt Implementation | Short Prompt Implementation |
| --- | --- | --- |
| **Token Footprint** | ~520 tokens (system instructions) | ~190 tokens (system instructions) |
| **Structural Integrity** | Rigid five-stage progression (Context $\rightarrow$ Background $\rightarrow$ Examination $\rightarrow$ Points $\rightarrow$ Proposal) | Compact narrative, occasionally collapses background and examination into a single paragraph |
| **Edge-Case Resilience** | High; explicitly forbids phrases like "for necessary action" and mandates exact flag references | Medium; smaller models may slip into first-person summaries ("We need to determine") |
| **Model Sensitivity** | Reliable on smaller, open-weights models (8B to 14B parameters) | Best paired with advanced instruction-following models (70B+ parameters) |
| **Primary Deployment** | Production backend templates, legal-administrative audit pipelines | Real-time chat assistants, multi-turn task pipelines, mobile agents |

## Practical Execution: A Sanction Case Study

To observe the prompts in action, consider a case involving procurement of computer hardware under Rule 149 of GFR, 2017:

### Input Context

* Section: Admin-II Section, Department of Expenditure
* Issue: Requisition from Staff Selection Commission (SSC) for procurement of 50 desktop computers through Government e-Marketplace (GeM)
* Total Estimated Cost: $32,500 (approx. ₹27,00,000)
* Availability: Funds available under Major Head 2052
* Concurrence: Internal Financial Division (IFD) has concurred vide Dy. No. 441/IFD/2026

### Generated Secretariat Output

```text
File No.: 12015/04/2026-Admin-II
Department of Expenditure
Ministry of Finance

Subject: Procurement of 50 Desktop Computers for Staff Selection Commission through GeM—Reg.

1. The proposal relates to the requisition received from the Staff Selection Commission (SSC) placed at Flag 'A' (PUC) regarding the procurement of 50 desktop personal computers for their newly created computer-based examination wing.

2. It is submitted that the existing computing infrastructure in the designated section is obsolete and insufficient to meet the current examination processing load. The technical specifications have been scrutinized and found compliant with standard Ministry of Electronics and Information Technology (MeitY) benchmarks (Flag 'B', p. 14/c).

3. In terms of Rule 149 of the General Financial Rules (GFR), 2017, the procurement of goods and services is mandatorily required to be made through the Government e-Marketplace (GeM). A market check on the GeM portal reveals that the requisite configuration is available from multiple verified Original Equipment Manufacturers (OEMs) under rate contracts.

4. The total financial implication for the procurement is estimated at ₹27,00,000/- (Rupees Twenty-Seven Lakh only). The expenditure is debitable to the Major Head "2052", Minor Head "00.090", under the Object Head "Office Expenses" for the current Financial Year 2026–27. Necessary budgetary provision exists under the relevant budget head.

5. The proposal was referred to the Internal Finance Division (IFD) for expenditure concurrence. The IFD has examined the proposal and concurred in the procurement vide Note on page 8/n (Dy. No. 441/IFD/2026 dated 22.09.2026), subject to compliance with the provisions of GFR, 2017 and GeM guidelines.

6. In view of the position stated above, it is proposed that administrative approval and expenditure sanction for an amount of ₹27,00,000/- may be accorded for placing the procurement order on GeM through the primary purchase committee.

7. Submitted for consideration and orders on para 6 above, please.


(Signature)
P. K. Sharma
Under Secretary to the Government of India
Intercom: 2411

Deputy Secretary (Admin)

```

## Guardrails for Automated Notings

Integrating large language models into administrative workflows introduces regulatory and compliance considerations:

* **Verification of Citing:** LLMs regularly fabricate Office Memorandum (OM) numbers and dates. A system prompt should instruct the model to insert generic place-markers (e.g., `[DoPT OM No. ... dated ...]`) unless the exact OM text is supplied within the retrieval-augmented generation (RAG) context.
* **Data Protection:** Files often contain personal identifiable information (PII) regarding service records, medical reimbursements, or disciplinary inquiries. Prompts must be backed by an enterprise redactor to strip identifiers before inference.
* **Accountability under CSMOP:** The Manual specifies that an officer signing a note assumes full responsibility for the facts stated therein. An automated drafting pipeline must be treated as an assistant for preliminary work, requiring line-by-line verification by the Section Officer or Under Secretary prior to putting up the file.

## References

Central Secretariat Manual of Office Procedure (CSMOP), Department of Administrative Reforms and Public Grievances

[https://darpg.gov.in/sites/default/files/CSMOP_0.pdf](https://www.google.com/search?q=https://darpg.gov.in/sites/default/files/CSMOP_0.pdf&utm_source=gemini)

General Financial Rules (GFR), Department of Expenditure, Ministry of Finance

[https://doe.gov.in/general-financial-rules](https://doe.gov.in/general-financial-rules?utm_source=gemini)

Department of Personnel and Training (DoPT) Compendiums

[https://dopt.gov.in](https://dopt.gov.in?utm_source=gemini)
