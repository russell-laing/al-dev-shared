# AL Dev Agent Map

**Last updated:** 2026-05-29 (19 agents; synced models to haiku after Remodel implementation; corrected tools and spawner references)

## Layer 1: Agent Catalog

| Agent | Model | Tools | Spawned by |
|-------|-------|-------|------------|
| al-dev-code-review | haiku | Read | (none found) |
| al-dev-commit-agent-analysis | haiku | Bash, Read | /al-dev-commit (analysis phase) |
| al-dev-commit-agent-execute | sonnet | Bash, Read | /al-dev-commit (execution phase) |
| al-dev-commit-message-drafter | haiku | (none) | /al-dev-commit (message-drafting phase) |
| al-dev-commit-recover-verifier | haiku | Bash, Read, Write | /commit-recover |
| al-dev-developer | sonnet | Read, Write, Edit, Glob, Grep, Bash | /al-dev-develop, /al-dev-fix |
| al-dev-diagnostics-fixer | haiku | Read, Edit, Glob, Grep, Bash | /al-dev-lint |
| al-dev-docs-writer | sonnet | Read, Write, Glob, Grep | (not spawned — skill mentions but doesn't dispatch) |
| al-dev-expert-reviewer | haiku | Read, Grep | /al-dev-develop, /al-dev-review-develop |
| al-dev-explore | haiku | Read, Glob, Grep, Write | (none found — skill uses built-in Explore type) |
| al-dev-interview | haiku | Read, Write, USER_GATE | /al-dev-interview |
| al-dev-performance-reviewer | haiku | Read, Grep | /al-dev-develop, /al-dev-review-develop |
| al-dev-release-notes-writer | sonnet | Bash, Write, Read, mcp:al-mcp-server, mcp:bc-code-intelligence | /al-dev-release-notes |
| al-dev-script-engineer | sonnet | Read, Write, Edit, Glob, Grep, Bash | (none found) |
| al-dev-security-reviewer | haiku | Read, Grep | /al-dev-develop, /al-dev-review-develop |
| al-dev-solution-architect | opus | Read, Write, Glob, Grep, mcp:bc-code-intelligence, mcp:microsoft-docs, mcp:al-mcp-server | /al-dev-plan, /al-dev-fix |
| al-dev-support-reply-drafter | haiku | Write | /al-dev-ticket (support mode: reply phase) |
| al-dev-support-researcher | sonnet | Read, mcp:al-mcp-server, mcp:microsoft-docs, mcp:bc-code-intelligence | /al-dev-ticket (support mode: research phase) |
| al-dev-ticket-agent | haiku | Bash, Write | /al-dev-ticket (all modes) |

---

## Layer 2: Per-Agent Profiles

### al-dev-code-review

**Description:** General code review specialist — finds bugs, logic errors, and security issues with high signal-to-noise ratio.
**Model:** haiku
**Tools:** Read
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

**Description:** Git commit manifest analyzer. Reads staged diffs and builds per-file manifests. Read-only — never modifies files. Split from message-drafting phase (al-dev-commit-message-drafter handles message composition).
**Model:** haiku
**Tools:** Bash, Read
**Spawned by:** /al-dev-commit (Phase 1 — analysis phase)

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `PROJECT_CONTEXT` and `FD_TICKET` from /al-dev-commit |
| Staged git index | **Yes** | Read via `git diff --cached` commands |

**Outputs:**

| Output | Description |
|--------|-------------|
| `MANIFESTS` block | Per-file change summary (object IDs, added/removed fields and procedures) |
| `WARNINGS` block | Validation issues and advisory notices |

---

### al-dev-commit-message-drafter

**Description:** Git commit message drafter. Consumes manifests from al-dev-commit-agent-analysis and drafts commit messages with context-aware description. Enables independent iteration on message quality.
**Model:** haiku
**Tools:** (none)
**Spawned by:** /al-dev-commit (Phase 2 — message-drafting phase)

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `MANIFESTS` and `PROPOSED_GROUPS` from analysis phase |
| Project context | No | `.dev/project-context.md` for domain knowledge |

**Outputs:**

| Output | Description |
|--------|-------------|
| `PROPOSED_GROUPS` block | Atomic commit group proposals with rationale |
| `DELETIONS` block | Staged deletions for the user audit gate |
| `WARNINGS` block | Validation issues and advisory notices |

---

### al-dev-commit-agent-execute

**Description:** Git commit execution agent. Runs lint, validates OOXML integrity, and executes git commits from an approved plan. Never writes or edits source files directly. Upgraded to sonnet for multi-phase orchestration and error recovery.
**Model:** sonnet (upgraded from haiku for complex error handling)
**Tools:** Bash, Read
**Spawned by:** /al-dev-commit (Phase 3 — execution phase)

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
| `.dev/session-log.md` | Append entry per file |

---

### al-dev-diagnostics-fixer

**Description:** Resolve AL lint warnings and compile errors surfaced by al-compile.
**Model:** haiku
**Tools:** Read, Edit, Glob, Grep, Bash
**Spawned by:** /al-dev-lint

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `.dev/compile-errors.log` | Yes | Output from `al-compile` |
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
**Tools:** Read, Write, Glob, Grep
**Spawned by:** (not dispatched — /al-dev-document skill mentions "docs-writer" in prose but contains no Agent() spawn call)

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| Latest `*-requirements.md` | **Yes** | What was needed |
| Latest `*-solution-plan.md` | **Yes** | Architecture |
| AL source files | **Yes** | Actual implementation |
| `AUDIENCE` parameter | **Yes** | Target audience (technical, functional, user, executive) |
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
**Model:** haiku
**Tools:** Read, Grep
**Spawned by:** /al-dev-develop, /al-dev-review-develop

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| AL files to review | **Yes** | Via spawn prompt — list of file paths to read |
| Spawn prompt | **Yes** | Task context: what was implemented, any open questions |

**Outputs:**

| Output | Description |
|--------|-------------|
| AL Expert Review Findings | Text report returned to /al-dev-develop; structured as Critical / High / Minor Issues |

---

### al-dev-explore

**Description:** Fast codebase exploration — finds files by pattern, searches for symbols, answers structural questions about code organization.
**Model:** haiku
**Tools:** Read, Glob, Grep, Write
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
| `.dev/$(date +%Y-%m-%d)-al-dev-explore.md` | Persistent findings file |

---

### al-dev-interview

**Description:** Interview the user to extract complete BC/AL implementation details through structured questioning.
**Model:** haiku
**Tools:** Read, Write, USER_GATE
**Spawned by:** /al-dev-interview

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| File path argument | No | Existing spec to refine (e.g., `.dev/*-al-dev-interview-requirements.md`) |
| Fresh start | No | If no file specified, creates new `.dev/*-al-dev-interview-requirements.md` |

**Outputs:**

| Output | Description |
|--------|-------------|
| `.dev/$(date +%Y-%m-%d)-al-dev-interview-requirements.md` | **Primary** (new interview) — Complete spec with decisions |
| Updated input file | **Primary** (refining) — Enhanced with interview findings |
| `.dev/session-log.md` | Append entry with summary |

---

### al-dev-performance-reviewer

**Description:** Review AL code for performance issues, inefficient queries, N+1 patterns, and resource consumption.
**Model:** haiku
**Tools:** Read, Grep
**Spawned by:** /al-dev-develop, /al-dev-review-develop

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| AL files to review | **Yes** | Via spawn prompt — list of file paths to read |
| Spawn prompt | **Yes** | Task context: what was implemented |

**Outputs:**

| Output | Description |
|--------|-------------|
| Performance Review Findings | Text report returned to /al-dev-develop; structured as Critical / High / Medium / Low |

---

### al-dev-release-notes-writer

**Description:** Run git diff analysis between two hashes, research AL object context, and write .dev/release-notes-\<version\>.md.
**Model:** sonnet
**Tools:** Bash, Write, Read, mcp:al-mcp-server, mcp:bc-code-intelligence
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
**Model:** haiku
**Tools:** Read, Grep
**Spawned by:** /al-dev-develop, /al-dev-review-develop

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

### al-dev-support-researcher

**Description:** Research a BC support query using AL symbols, MS Docs, and BC Code History. Produces internal technical findings. Uses systematic, curated sources only (no web search/fetch).
**Model:** sonnet
**Tools:** Read, mcp:al-mcp-server, mcp:microsoft-docs, mcp:bc-code-intelligence
**Spawned by:** /al-dev-ticket (support mode: research phase)

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `QUERY_TYPE` | **Yes** | `ticket`, `file`, or `freetext` — in dispatch prompt |
| `QUERY_CONTEXT` | **Yes** | The customer's question or symptom |
| `TICKET_FILE` | No | Path to ticket context file from `/al-dev-ticket`, or `NONE` |

**Outputs:**

| Output | Description |
|--------|-------------|
| Return block | Structured internal findings: root cause, evidence (AL symbols, MS Docs, BC history), workarounds, recommended resolution |

---

### al-dev-support-reply-drafter

**Description:** Draft a customer-facing reply from internal BC support research findings. Pairs with al-dev-support-researcher. Applies evidence requirements and tone constraints.
**Model:** haiku
**Tools:** Write
**Spawned by:** /al-dev-ticket (support mode: reply phase)

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `QUERY_TYPE` | **Yes** | `ticket`, `file`, or `freetext` — in dispatch prompt |
| `QUERY_CONTEXT` | **Yes** | Original customer question or symptom |
| `TICKET_FILE` | No | Path to ticket context file, or `NONE` |
| `RESEARCHER_FINDINGS` | **Yes** | Full structured output block from al-dev-support-researcher |

**Outputs:**

| Output | Description |
|--------|-------------|
| `.dev/<date>-support-<slug>.md` | **Primary** — Internal findings + draft customer reply |
| Return block | `FILE`, `QUERY_TYPE`, `BC_VERSION_SCOPE`, `SOURCES`, `SUMMARY` |

---

### al-dev-ticket-agent

**Description:** Fetch a Freshdesk ticket via API, write .dev/\$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md, download attachments, and detect inline images in HTML body. Follows canonical invocation pattern in knowledge/ticket-agent-invocation-pattern.md.
**Model:** haiku
**Tools:** Bash, Write
**Spawned by:** /al-dev-ticket (all modes: fetch, support, quick)

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `TICKET_ID` | **Yes** | Freshdesk ticket number (in dispatch prompt) |
| `FRESHDESK_API_KEY` | **Yes** | API key (from global settings via environment) |
| `FRESHDESK_DOMAIN` | **Yes** | Freshdesk subdomain (from global settings via environment) |

**Outputs:**

| Output | Description |
|--------|-------------|
| `.dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md` | **Primary** — structured ticket brief with inline image list |
| `.dev/attachments/` | Attached files (downloaded with ticket context) |
| Return block | `TICKET_CONTEXT_WRITTEN`, `TICKET_ID`, `STATUS`, `PRIORITY`, `COMMENTS_COUNT`, `ATTACHMENTS`, `INLINE_IMAGES_COUNT` |

---

### al-dev-commit-recover-verifier

**Description:** Recover corrupted AL files flagged in `.dev/commit-integrity.log` using fallback strategies and learned patterns.
**Model:** haiku
**Tools:** Bash, Read, Write
**Spawned by:** /commit-recover

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `REPO` | **Yes** | Project root directory |
| `CORRUPTION_LOG` | **Yes** | Path to `.dev/commit-integrity.log` with flagged files |
| `auto_fix` | No | If true, apply auto-fixes; if false, report findings only |

**Outputs:**

| Output | Description |
|--------|-------------|
| Fixed AL files | Recovered via fallback strategies (git restore, regex reconstruction, schema rebuild) |
| `.dev/$(date +%Y-%m-%d)-al-dev-commit-recover-report.md` | Recovery report with per-file strategy and status |

---

## Observations

> Generated by /analyze-agent-design on 2026-05-27; updated by /review-agent-map on 2026-05-29.

### Agents used by only one skill (single-purpose specialists)

- **al-dev-commit-agent-analysis** — used only by /al-dev-commit (Phase 1: analysis)
- **al-dev-commit-agent-execute** — used only by /al-dev-commit (Phase 3: execution)
- **al-dev-commit-message-drafter** — used only by /al-dev-commit (Phase 2: message composition)
- **al-dev-commit-recover-verifier** — used only by /commit-recover
- **al-dev-diagnostics-fixer** — used only by /al-dev-lint
- **al-dev-docs-writer** — used only by /al-dev-document (prose reference; no formal Agent() spawn call found)
- **al-dev-interview** — used only by /al-dev-interview
- **al-dev-release-notes-writer** — used only by /al-dev-release-notes
- **al-dev-support-reply-drafter** — used only by /al-dev-ticket (support mode: reply phase)
- **al-dev-support-researcher** — used only by /al-dev-ticket (support mode: research phase)

### Agents used by the review panel (shared across develop + review-develop)

- **al-dev-expert-reviewer** — used by /al-dev-develop, /al-dev-review-develop
- **al-dev-performance-reviewer** — used by /al-dev-develop, /al-dev-review-develop
- **al-dev-security-reviewer** — used by /al-dev-develop, /al-dev-review-develop

### Agents with no documented callers (standalone or special dispatch)

- **al-dev-code-review** — no skill spawns it; available for direct standalone use via Agent tool
- **al-dev-explore** — no skill spawns it; the `/al-dev-explore` skill dispatches the built-in `Explore` agent type instead
- **al-dev-script-engineer** — no skill spawns it; available for direct use via Agent tool

### Agents used by multiple skills (shared)

- **al-dev-developer** — used by /al-dev-develop, /al-dev-fix
- **al-dev-solution-architect** — used by /al-dev-plan, /al-dev-fix
- **al-dev-ticket-agent** — used by /al-dev-ticket (all three modes)

### Open quality suggestions

**Align: Clarify al-dev-developer TDD activation path**
Observation: Agent Inputs table documents `.dev/*-al-dev-test-test-plan.md` as required input "from /al-dev-develop," but the /al-dev-develop skill contains no logic to create test plans. Agent body (CRITICAL line 38) gates TDD workflow on test-plan file presence, but no spawning skill documented as providing this file. This breaks the TDD path.
Suggestion: Update Inputs table row for test-plan: mark as "Optional: User-supplied via /al-dev-test or created by test-engineer agent" OR clarify which skill creates test plans. If TDD is not actively used, remove the test-plan input and the CRITICAL gate from the agent body.
Trade-off: Documentation-only change; prevents confusion about TDD activation contract between skill and agent.

**Align: al-dev-review-develop is a stub skill**
Observation: /al-dev-review-develop describes Phases 5–10 of the develop workflow but its SKILL.md body is a stub (61 lines; no actual phase instructions). The three reviewer agents (expert, security, performance) are documented as its callers, but the skill contains no spawn calls. Map is pre-emptively accurate; skill body needs implementation to match documented contract.
Suggestion: Implement /al-dev-review-develop by copying Phases 5–10 from /al-dev-develop per the skill's own notes. Until then, /al-dev-develop is the only active spawner of the review panel.
Trade-off: Skill body is incomplete; review panel spawning works through /al-dev-develop only.

### Previously implemented improvements

**✅ Restored al-dev-commit-recover-verifier agent** (2026-05-29)
Agent file was empty; now restored with proper YAML frontmatter (haiku, Bash/Read/Write) and full recovery system prompt.

**✅ Remodelled 9 sonnet agents to haiku** (2026-05-27)
Downgraded: code-review, commit-agent-analysis, commit-message-drafter, diagnostics-fixer, expert-reviewer, interview, performance-reviewer, security-reviewer, support-reply-drafter. ~60% cost reduction for single-task agents.

**✅ Trimmed al-dev-support-reply-drafter tools** (2026-05-27)
Removed unused `Read` from tools list. Agent receives all input via dispatch block; no file reads needed.

**✅ Trimmed al-dev-commit-message-drafter tools** (2026-05-27)
Removed unused `Read` from tools list. Agent analyzes manifests from dispatch prompt without file I/O.

**✅ Upgraded al-dev-commit-agent-execute** (2026-05-22)
Model changed from haiku → sonnet for multi-phase orchestration (lint + validation + commit + retry) with error recovery.

**✅ Split al-dev-commit into three sequential agents** (2026-05-22)
- al-dev-commit-agent-analysis (manifest extraction, read-only)
- al-dev-commit-message-drafter (editorial, message composition)
- al-dev-commit-agent-execute (operational, commit execution)
Enabled independent iteration and audit gates between phases.

**✅ Trimmed al-dev-support-researcher tools** (2026-05-22)
Removed WebSearch and WebFetch; restricted to AL Symbols, MS Docs, BC Code History only.

### Inline candidates detected on 2026-05-29

None detected. All single-purpose agents have documented Inputs/Outputs sections and body length >10 lines; they do not meet the 2+ signal threshold for inlining.
