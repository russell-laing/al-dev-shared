# AL Dev Agent Map

**Last updated:** 2026-05-19

## Layer 1: Agent Catalog

| Agent | Model | Tools | Spawned by |
|-------|-------|-------|------------|
| al-dev-code-review | sonnet | Read, Glob, Grep | (none found) |
| al-dev-commit-agent-analysis | sonnet | Bash, Read, Glob | /al-dev-commit |
| al-dev-commit-agent-execute | haiku | Bash, Read, Glob | /al-dev-commit |
| al-dev-developer | sonnet | Read, Write, Edit, Glob, Grep, Bash | /al-dev-develop, /al-dev-fix |
| al-dev-diagnostics-fixer | sonnet | Read, Edit, Glob, Grep, Bash | /al-dev-lint, /al-dev-develop |
| al-dev-docs-writer | sonnet | Read, Write, Glob, Grep, Bash | /al-dev-document |
| al-dev-expert-reviewer | sonnet | Read, Grep, Glob | /al-dev-develop |
| al-dev-explore | sonnet | Read, Glob, Grep | (none found — skill uses built-in Explore type) |
| al-dev-interview | sonnet | Read, Write, AskUserQuestion | /al-dev-interview |
| al-dev-performance-reviewer | sonnet | Read, Grep, Glob | /al-dev-develop |
| al-dev-release-notes-agent | sonnet | Bash, Write, Read, Glob, mcp:al-mcp-server, mcp:bc-code-intelligence-mcp | /al-dev-release-notes |
| al-dev-script-engineer | sonnet | Read, Write, Edit, Glob, Grep, Bash | (none found) |
| al-dev-security-reviewer | sonnet | Read, Grep, Glob | /al-dev-develop |
| al-dev-solution-architect | opus | Read, Write, Glob, Grep, mcp:bc-code-intelligence, mcp:microsoft-docs, mcp:al-mcp-server | /al-dev-plan, /al-dev-fix |
| al-dev-support-agent | sonnet | WebSearch, WebFetch, Bash, Write, Read, mcp:al-mcp-server, mcp:microsoft-docs | /al-dev-support |
| al-dev-ticket-agent | haiku | Bash, Write | /al-dev-ticket, /al-dev-support |
| commit-learn-verifier | sonnet | Bash, Read, Write | /commit-learn |

---

## Layer 2: Per-Agent Profiles

### al-dev-code-review

**Description:** General code review specialist — finds bugs, logic errors, and security issues with high signal-to-noise ratio.
**Model:** sonnet
**Tools:** Read, Glob, Grep
**Spawned by:** (none found in skill files)

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| Files to review | **Yes** | Via spawn prompt — file paths or diff scope |
| Spawn prompt | **Yes** | Task context: scope, other active reviewers, any open questions |

**Outputs:**

| Output | Description |
|--------|-------------|
| Code Review Findings | Text report returned to calling skill; structured as Critical / High / Medium / Low |

---

### al-dev-commit-agent-analysis

**Description:** Git commit analysis agent. Reads staged diffs, builds per-file manifests, proposes commit groups, and drafts commit messages. Read-only — never modifies files.
**Model:** sonnet
**Tools:** Bash, Read, Glob
**Spawned by:** /al-dev-commit (Step 6 — analysis phase)

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `PROJECT_CONTEXT` and `FD_TICKET` from /al-dev-commit |
| Staged git index | **Yes** | Read via `git diff --cached` commands |

**Outputs:**

| Output | Description |
|--------|-------------|
| `MANIFESTS` block | Per-file change summary (object IDs, added/removed fields and procedures) |
| `PROPOSED_GROUPS` block | Atomic commit group proposals with draft messages |
| `DELETIONS` block | Staged deletions for the user audit gate |
| `WARNINGS` block | Validation issues and advisory notices |

---

### al-dev-commit-agent-execute

**Description:** Git commit execution agent. Runs lint, validates OOXML integrity, and executes git commits from an approved plan. Never writes or edits source files directly.
**Model:** haiku
**Tools:** Bash, Read, Glob
**Spawned by:** /al-dev-commit (Step 10 — execute phase)

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `APPROVED_PLAN` — approved groups and messages from analysis phase |

**Outputs:**

| Output | Description |
|--------|-------------|
| `COMMITS` block | SHA and message for each committed group |
| `SKIPPED` | Number of skipped groups |
| `LINT_FIXES` | Files re-staged after lint (or `NONE`) |
| `HOOK_FAILURES` | Raw hook output for any failed groups (or `NONE`) |
| `STRIPPED_ATTRIBUTIONS` | Removed AI attribution lines (or `NONE`) |

---

### al-dev-developer

**Description:** Implement AL code following an implementation plan.
**Model:** sonnet
**Tools:** Read, Write, Edit, Glob, Grep, Bash
**Spawned by:** /al-dev-develop, /al-dev-fix

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `.dev/*-al-dev-plan-solution-plan.md` | **Yes** (from /al-dev-develop) · Inline prompt (from /al-dev-fix) | Implementation plan |
| `.dev/*-al-dev-test-test-plan.md` | **Yes** (from /al-dev-develop) · Not used (from /al-dev-fix) | Test specs from test-engineer |
| `.dev/project-context.md` | No | Project memory (saves exploration) |
| `.dev/*-al-dev-develop-code-review.md` | No | Review findings when iterating |

**Outputs:**

| Output | Description |
|--------|-------------|
| AL source files | **Primary** — Implemented code in `src/` |
| Test codeunits | Test code in `src/Tests/` |
| `.dev/$(date +%Y-%m-%d)-al-dev-developer-tdd-log.md` | TDD log |
| `.dev/project-context.md` | Update with new objects |
| `.dev/session-log.md` | Append entry per file |

---

### al-dev-diagnostics-fixer

**Description:** Resolve AL lint warnings and compile errors surfaced by al-compile.
**Model:** sonnet
**Tools:** Read, Edit, Glob, Grep, Bash
**Spawned by:** /al-dev-lint, /al-dev-develop

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `.dev/compile-errors.log` | Yes | Output from `al-compile` |
| `knowledge/al-linting-rules.md` | Yes | Rule ID lookup reference |
| AL source files (flagged paths) | Yes | Files to fix |

**Outputs:**

| Output | Description |
|--------|-------------|
| Fixed AL source files | In-place fixes applied |
| Dated lint report | `.dev/$(date +%Y-%m-%d)-al-dev-lint-lint-report.md` with fix summary |

---

### al-dev-docs-writer

**Description:** Generate and maintain AL project documentation — feature docs, API references, and setup guides.
**Model:** sonnet
**Tools:** Read, Write, Glob, Grep, Bash
**Spawned by:** /al-dev-document

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| Latest `*-requirements.md` | **Yes** | What was needed |
| Latest `*-solution-plan.md` | **Yes** | Architecture |
| AL source files | **Yes** | Actual implementation |
| Latest `*-code-review.md` | No | Quality notes |
| Latest `*-test-plan.md` | No | Test coverage info |

**Outputs:**

| Output | Description |
|--------|-------------|
| `docs/` or `wiki/` | **Primary** — Documentation files |
| `docs/Features/[name].md` | Feature documentation |
| `docs/API/[name].md` | API reference (if public procedures) |
| `CHANGELOG.md` | Updated changelog |
| `.dev/session-log.md` | Append entry with summary |

---

### al-dev-expert-reviewer

**Description:** Review AL code for adherence to naming conventions, AL patterns, and BC design patterns.
**Model:** sonnet
**Tools:** Read, Grep, Glob
**Spawned by:** /al-dev-develop

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| AL files to review | **Yes** | Via spawn prompt — list of file paths to read |
| Spawn prompt | **Yes** | Task context: what was implemented, any open questions |

**Outputs:**

| Output | Description |
|--------|-------------|
| AL Best Practices Review Findings | Text report returned to /al-dev-develop; structured as Critical / High / Minor Issues |

---

### al-dev-explore

**Description:** Fast codebase exploration — finds files by pattern, searches for symbols, answers structural questions about how code is organized.
**Model:** sonnet
**Tools:** Read, Glob, Grep
**Spawned by:** (none found — the `/al-dev-explore` skill dispatches a built-in `Explore` subagent type, not this agent file directly)

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| Question or search task | **Yes** | What to understand about the codebase (via spawn prompt) |
| Scope | No | Directory or file patterns to focus on |
| Context | No | Previous findings to build upon |

**Outputs:**

| Output | Description |
|--------|-------------|
| Findings | List of relevant files, code snippets, or relationships |
| Summary | Concise explanation of codebase structure for the query |
| Suggestions | Recommendations for next steps |

---

### al-dev-interview

**Description:** Interview the user to extract complete BC/AL implementation details through structured questioning.
**Model:** sonnet
**Tools:** Read, Write, AskUserQuestion
**Spawned by:** /al-dev-interview

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| File path argument | No | Existing spec to refine (e.g., `.dev/*-al-dev-interview-requirements.md`) |
| Fresh start | No | If no file specified, creates new `.dev/*-al-dev-interview-notes.md` |

**Outputs:**

| Output | Description |
|--------|-------------|
| `.dev/$(date +%Y-%m-%d)-al-dev-interview-notes.md` | **Primary** (new interview) — Complete spec with decisions |
| Updated input file | **Primary** (refining) — Enhanced with interview findings |
| `.dev/session-log.md` | Append entry with summary |

---

### al-dev-performance-reviewer

**Description:** Review AL code for performance issues, inefficient queries, N+1 patterns, and resource consumption.
**Model:** sonnet
**Tools:** Read, Grep, Glob
**Spawned by:** /al-dev-develop

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| AL files to review | **Yes** | Via spawn prompt — list of file paths to read |
| Spawn prompt | **Yes** | Task context: what was implemented |

**Outputs:**

| Output | Description |
|--------|-------------|
| Performance Review Findings | Text report returned to /al-dev-develop; structured as Critical / High / Optimization Opportunities |

---

### al-dev-release-notes-agent

**Description:** Run git diff analysis between two hashes, research AL object context, and write .dev/release-notes-\<version\>.md.
**Model:** sonnet
**Tools:** Bash, Write, Read, Glob, mcp:al-mcp-server, mcp:bc-code-intelligence-mcp
**Spawned by:** /al-dev-release-notes

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `START_HASH` | **Yes** | Earlier commit (exclusive lower bound) |
| `END_HASH` | **Yes** | Later commit (inclusive upper bound) |
| `RELEASE_TYPE` | **Yes** | `uat` or `prod` |
| `VERSION` | No | Label (e.g. `v2.1.0`); short hash used if omitted |
| `PROJECT_CONTEXT` | No | Content of `.dev/project-context.md` if it exists |

**Outputs:**

| Output | Description |
|--------|-------------|
| `.dev/$(date +%Y-%m-%d)-al-dev-release-notes-<VERSION>.md` | **Primary** — formatted release notes file |
| Return block | `RELEASE_NOTES_WRITTEN`, `VERSION`, `CHANGES`, `SUMMARY`, `EXCLUDED`, `DIAGRAMS`, `AMBIGUOUS` |

---

### al-dev-script-engineer

**Description:** Write, validate, and run scripts for AL development and documentation workflows.
**Model:** sonnet
**Tools:** Read, Write, Edit, Glob, Grep, Bash
**Spawned by:** (none found in skill files)

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| User request | **Yes** | Script goal and AL project context (via spawn prompt) |
| `.dev/02-solution-plan.md` | No | If implementing a planned script |

**Outputs:**

| Output | Description |
|--------|-------------|
| Python script file(s) | In `scripts/` following toolkit conventions (Python default) |
| Governance tokens | Inline in documentation or `.dev/` files |

---

### al-dev-security-reviewer

**Description:** Review AL code for security vulnerabilities, permission issues, and data exposure risks.
**Model:** sonnet
**Tools:** Read, Grep, Glob
**Spawned by:** /al-dev-develop

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| AL files to review | **Yes** | Via spawn prompt — list of file paths to read |
| Spawn prompt | **Yes** | Task context: what was implemented, any open questions |

**Outputs:**

| Output | Description |
|--------|-------------|
| Security Review Findings | Text report returned to /al-dev-develop; structured as Critical / High / Medium / Low |

---

### al-dev-solution-architect

**Description:** Design BC-integrated solutions and create detailed implementation plans.
**Model:** opus
**Tools:** Read, Write, Glob, Grep, mcp:bc-code-intelligence, mcp:microsoft-docs, mcp:al-mcp-server
**Spawned by:** /al-dev-plan, /al-dev-fix

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| Dated requirements file | **Yes** (from /al-dev-plan) · Inline prompt (from /al-dev-fix) | From /interview (glob pattern match) — or inline analysis + fix approach when dispatched by /al-dev-fix |
| `.dev/project-context.md` | No | Project memory (read FIRST if exists) |
| MCP tools | No | BC Intelligence, MS Docs, AL Dependency |

**Outputs:**

| Output | Description |
|--------|-------------|
| Dated solution plan file | **Primary** — Architecture + implementation plan |
| `.dev/project-context.md` | Update with new patterns/objects learned |
| `.dev/session-log.md` | Append entry with summary of work done |

---

### al-dev-support-agent

**Description:** Research a BC support query using AL symbols, MS Docs, and BC Code History.
**Model:** sonnet
**Tools:** WebSearch, WebFetch, Bash, Write, Read, mcp:al-mcp-server, mcp:microsoft-docs
**Spawned by:** /al-dev-support

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `QUERY_TYPE` | **Yes** | `ticket`, `file`, or `freetext` — in dispatch prompt |
| `QUERY_CONTEXT` | **Yes** | The customer's question or symptom |
| `TICKET_FILE` | No | Path to ticket context file from `/al-dev-ticket`, or `NONE` |

**Outputs:**

| Output | Description |
|--------|-------------|
| `.dev/<date>-support-<slug>.md` | **Primary** — Internal findings + draft customer reply |
| Return block | `FILE`, `QUERY_TYPE`, `BC_VERSION_SCOPE`, `SOURCES`, `SUMMARY` |

---

### al-dev-ticket-agent

**Description:** Fetch a Freshdesk ticket via API, write .dev/\$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md, and optionally download attachments.
**Model:** haiku
**Tools:** Bash, Write
**Spawned by:** /al-dev-ticket, /al-dev-support

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `TICKET_ID` | **Yes** | Freshdesk ticket number — in dispatch prompt |
| `FRESHDESK_API_KEY` | **Yes** | API key — from environment |
| `FRESHDESK_DOMAIN` | **Yes** | Freshdesk subdomain — from environment |

**Outputs:**

| Output | Description |
|--------|-------------|
| `.dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md` | **Primary** — structured ticket brief |
| Return block | `TICKET_LOADED`, `TITLE`, `STATUS`, `SUMMARY`, `ATTACHMENTS`, `FILE` |

---

### commit-learn-verifier

**Description:** Analyze file corruption incidents, propose and execute recovery strategies with fallback methods.
**Model:** sonnet
**Tools:** Bash, Read, Write
**Spawned by:** /commit-learn

**Inputs:**

- **File path:** the corrupted file
- **Baseline/current line count:** what changed
- **Git history:** last 3–5 commits showing what edits were made
- **Learnings.md:** current known patterns and strategies
- **Incident log entry:** timestamp, error type (CORRUPTION/SYNTAX_ERROR)

**Outputs:**

| Output | Description |
|--------|-------------|
| Analysis report (text) | Root cause hypothesis, pattern match result, fallback strategy, recovery result |
| Updated `learnings.md` | Recovery outcome recorded (success or failure) with new guardrails if applicable |

---

## Observations

> Run /review-agent-map first if the agent list has changed before running /analyze-agent-design.

Populated by /analyze-agent-design.

### Agents used by only one skill

- **al-dev-commit-agent-analysis** — used only by /al-dev-commit
- **al-dev-commit-agent-execute** — used only by /al-dev-commit
- **al-dev-docs-writer** — used only by /al-dev-document
- **al-dev-expert-reviewer** — used only by /al-dev-develop
- **al-dev-interview** — used only by /al-dev-interview
- **al-dev-performance-reviewer** — used only by /al-dev-develop
- **al-dev-release-notes-agent** — used only by /al-dev-release-notes
- **al-dev-security-reviewer** — used only by /al-dev-develop
- **al-dev-support-agent** — used only by /al-dev-support
- **commit-learn-verifier** — used only by /commit-learn

### Agents with no callers (standalone only)

- **al-dev-code-review** — no skill spawns it; available for direct use alongside the 3-reviewer team
- **al-dev-explore** — no skill spawns it; the `/al-dev-explore` skill dispatches the built-in `Explore` agent type instead
- **al-dev-script-engineer** — no skill spawns it; available for direct use

### Potential shared agents

- **al-dev-developer** — used by /al-dev-develop, /al-dev-fix
- **al-dev-diagnostics-fixer** — used by /al-dev-lint, /al-dev-develop
- **al-dev-solution-architect** — used by /al-dev-plan, /al-dev-fix
- **al-dev-ticket-agent** — used by /al-dev-ticket, /al-dev-support

### Inline candidates

> Detected by /review-agent-map on 2026-05-19.

None detected. No agent scores 2+ inline signals (single caller + minimal body < 10 lines + no I/O docs). All agents have I/O documentation; none have a body under 10 lines post-frontmatter.
