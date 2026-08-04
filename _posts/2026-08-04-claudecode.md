---
title: "Mastering Claude Code: A Complete Guide to .md Configs, Skills, and Agents"
date: 2026-08-04
categories: [AI Tools, Developer Tools, Software Architecture]
tags: [claude-code, prompt-engineering, developer-experience, markdown, agentic-ai]
---

As AI-assisted software development moves from simple code completion to autonomous agentic workflows, organizing context becomes the single most critical factor for success. Anthropic’s **Claude Code** CLI leverages dedicated Markdown (`.md`) files to maintain project memory, define domain-specific skills, and orchestrate specialized subagents.

Without these context files, an AI agent operates blindly, drifting from project conventions, misinterpreting architectures, or rewriting existing codebase patterns. This guide provides a detailed breakdown of every required and optional `.md` file in the Claude Code ecosystem, along with production-ready templates for your project.

---

## 1. Core Memory Files

Core memory files sit directly in your project root or `.claude/` directory. They act as the agent's baseline instruction set, technical manual, and scratchpad across CLI sessions.

### `.claudecode.md`
This is the primary global rulebook for Claude Code within your repository. It dictates coding style, constraints, testing requirements, and architectural boundaries.

#### Template
```markdown
# Project Standards & Conventions

## Tech Stack & Language Guidelines
- **Primary Language:** TypeScript (strict mode enabled)
- **Framework:** Next.js (App Router)
- **Styling:** Tailwind CSS with Radix UI components

## Code Style & Formatting
- Prefer functional components and immutability.
- Use explicit type annotations; avoid using `any` under any circumstance.
- Run `pnpm lint` before submitting any code changes.

## Testing Standards
- All new API routes require corresponding integration tests under `__tests__/api/`.
- Run tests via `pnpm test`. Do not commit code with failing tests.

## Architecture Guidelines
- Place business logic in `lib/services/`, not directly in UI components or route handlers.
- Database access must strictly use Prisma ORM through `lib/db.ts`.

```

* **What to write:** Define non-negotiable standards. Be explicit about preferred libraries, prohibited practices, folder structures, and testing expectations.

---

### `.claudedoc.md`

While `.claudecode.md` handles coding *rules*, `.claudedoc.md` handles system *understanding*. It describes how the high-level architecture operates and how data flows through the application.

#### Template

```markdown
# Technical System Documentation

## System Overview
This repository contains the backend and web client for our automated customer support pipeline.

## Architecture & Data Flow
1. **Inbound Webhook:** User queries hit `/api/v1/webhooks/incoming`.
2. **Ingestion & Queue:** Messages are validated and pushed to Redis BullMQ.
3. **Processing Worker:** The background worker (`services/worker.ts`) fetches pending jobs and queries the LLM processing service.
4. **Storage:** Final responses and session logs are stored in PostgreSQL.

## Critical Dependencies & Services
- **Database:** PostgreSQL (Hosted on Supabase)
- **Queue System:** Redis
- **Authentication:** NextAuth.js with JWT session strategy

```

* **What to write:** Explain the "why" and "how" behind your system design. Include database relationships, third-party service connections, and asynchronous processing paths.

---

### `.claudenotes.md`

This file acts as a persistent working memory across sessions. It helps the agent remember active tasks, unblocked issues, and architectural decisions made in previous interactions.

#### Template

```markdown
# Session Memory & Active Notes

## Active Tasks
- [ ] Refactor `/api/v1/checkout` route to support dynamic multi-currency payments.
- [ ] Fix memory leak in background worker job consumer.

## Known Bugs & Issues
- **Issue:** Redis connection drops during high-concurrency spikes.
  - **Workaround:** Max retries set to 5 in `lib/redis.ts`.

## Recent Changes
- Updated Next.js to version 15.1.
- Migrated user authentication to strict server actions.

```

* **What to write:** Update this file regularly or ask Claude Code to update it at the end of a session. Record technical debt, unresolved bugs, and pending todo items.

---

## 2. Agent Skills (`SKILL.md`)

Skills are modular, repeatable workflows that teach Claude Code how to execute specialized operations like performing database migrations, writing end-to-end tests, or auditing security.

* **File Location:** `.claude/skills/[skill-name]/SKILL.md`

### Template

```markdown
---
name: database-migration
description: Guidelines and verification steps for running and creating Prisma database migrations safely.
---

# Skill: Database Migration Workflow

## Pre-requisites
- Ensure local PostgreSQL instance is running via Docker (`docker-compose up -d`).

## Step-by-Step Instructions
1. Modify schema in `prisma/schema.prisma`.
2. Generate migration script using `pnpm prisma migrate dev --create-only --name <descriptive_name>`.
3. Inspect generated SQL inside `prisma/migrations/` for destructive operations (`DROP COLUMN`, `TRUNCATE`).
4. Apply migration using `pnpm prisma migrate dev`.
5. Run `pnpm prisma generate` to refresh client types.

## Constraints
- **NEVER** run `prisma migrate reset` in non-development environments.
- Always check that field additions are either optional or provide a default value.

```

* **What to write:** Use the YAML frontmatter (`name` and `description`) carefully—Claude Code reads the `description` to automatically pick and execute the skill when relevant.

---

## 3. Custom Subagents (`[agent-name].md`)

Subagents are isolated Claude instances constrained to specific tool sets, roles, and boundaries. You can assign them narrow responsibilities such as code review, security auditing, or documentation generation.

* **File Location:** `.claude/agents/[agent-name].md`

### Template

```markdown
---
name: security-auditor
description: Delegate to this agent to scan new code changes or pull requests for security vulnerabilities, exposed secrets, or OWASP top 10 risks.
tools: ["read_file", "search_files", "list_dir"]
model: sonnet
permissionMode: acceptEdits
---

# Role: Security Auditor

You are a senior Application Security Engineer. Your job is to analyze code changes for potential vulnerabilities before deployment.

## Audit Checklist
- Check for unvalidated inputs in API endpoints (SQL Injection, XSS).
- Search for hardcoded credentials, API keys, or JWT secrets.
- Validate that authentication wrappers are applied to sensitive routes.
- Ensure sensitive data is not being written to application logs.

## Output Requirements
Provide a structured security report identifying:
1. Risk severity (Critical, High, Medium, Low)
2. Affected file and line number
3. Remediation code snippet

```

* **What to write:** Restrict tool usage in the frontmatter (e.g., limit read/write permissions where appropriate). Explicitly define the subagent's role, checklist, and required output format.

---

## 4. Universal Brief (`AGENTS.md`)

If your project utilizes multiple AI execution environments (such as Claude Code, Cursor, or Windsurf), use a top-level `AGENTS.md` file in your root folder as a single source of truth across all tools.

* **File Location:** `AGENTS.md`

### Template

```markdown
# Universal Agent Directives

## Workspace Conventions
- Workspace package manager is strictly `pnpm`. Do not run `npm` or `yarn`.
- Commit messages must follow Conventional Commits (e.g., `feat:`, `fix:`, `docs:`).

## Core Rules
1. Never commit API keys or `.env` files to git.
2. Keep methods small and modular—aim for under 30 lines per function.
3. Write clean, self-documenting code over excessive inline comments.

```

---

## Summary of File Paths

| File | Purpose | Scope |
| --- | --- | --- |
| `.claudecode.md` | Global project rules, style guidelines, and tech stack | Project-wide |
| `.claudedoc.md` | Architectural documentation and data flows | Project-wide |
| `.claudenotes.md` | Active task tracking, bugs, and session memory | Session-to-Session |
| `.claude/skills/[name]/SKILL.md` | Specialized, step-by-step procedure guides | Modular Workflow |
| `.claude/agents/[name].md` | Custom subagent roles and tool permissions | Delegated Tasks |
| `AGENTS.md` | Cross-tool AI instructions (Claude Code, Cursor, etc.) | Universal |

Configuring these Markdown files ensures consistent, predictable, and production-grade output from Claude Code across your entire team.

```

```
