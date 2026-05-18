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
| Script file(s) | In `scripts/` following toolkit conventions (Python default) |
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

> Generated by /analyze-agent-design on 2026-05-19.
> Observations implemented on 2026-05-19. Run /review-agent-map to regenerate.

### Agents used by only one skill

- **al-dev-commit-agent** — used only by /al-dev-commit
- **al-dev-docs-writer** — used only by /al-dev-document
- **al-dev-expert-reviewer** — used only by /al-dev-develop
- **al-dev-interview** — used only by /al-dev-interview
- **al-dev-performance-reviewer** — used only by /al-dev-develop
- **al-dev-release-notes-agent** — used only by /al-dev-release-notes
- **al-dev-security-reviewer** — used only by /al-dev-develop
- **al-dev-support-agent** — used only by /al-dev-support
- **commit-learn-verifier** — used only by /commit-learn

### Agents with no inputs/outputs documentation

- **al-dev-code-review** — general code review: bugs, logic errors, security issues
- **al-dev-commit-agent** — git staging analysis (analysis phase) and commit execution (execute phase)
- **al-dev-expert-reviewer** — AL naming conventions, AL/BC design patterns review
- **al-dev-explore** — codebase search and structural exploration (file patterns, symbols)
- **al-dev-performance-reviewer** — query performance, N+1 patterns, loop efficiency review
- **al-dev-release-notes-agent** — release notes from git diff between two hashes
- **al-dev-script-engineer** — Python/Bash script writing for AL development workflows
- **al-dev-security-reviewer** — AL permissions, data exposure, and authorization review
- **al-dev-support-agent** — BC support query research and draft customer reply
- **commit-learn-verifier** — file corruption analysis and recovery (outputs not documented)

### Potential shared agents

- **al-dev-developer** — used by /al-dev-develop, /al-dev-fix
- **al-dev-diagnostics-fixer** — used by /al-dev-lint, /al-dev-develop
- **al-dev-solution-architect** — used by /al-dev-plan, /al-dev-fix
- **al-dev-ticket-agent** — used by /al-dev-ticket, /al-dev-support

### Quality suggestions

**Split: al-dev-commit-agent** ← highest leverage
Observation: The agent description and system prompt explicitly describe two separable phases: `analysis` (read-only, semantic — reads diffs, builds manifests, proposes groups, drafts messages) and `execute` (write-heavy, mechanical — runs lint, validates OOXML, commits). The two phases have opposite safety profiles (analysis must never modify files; execute is the only write phase) and different reasoning demands (analysis requires code comprehension; execute is shell orchestration). The agent is already dispatched with phase-specific instructions, so the calling convention already treats them as separate agents.
Suggestion: Extract the two phases into `al-dev-commit-agent-analysis` (model: `sonnet` — for semantic commit message reasoning and group proposal) and `al-dev-commit-agent-execute` (model: `haiku` — for mechanical bash execution). Update `/al-dev-commit` to dispatch the appropriate agent per phase.
Trade-off: Two agent files to maintain instead of one; the read-only constraint becomes structural rather than documented. Enables model right-sizing: analysis gets Sonnet depth; execute gets Haiku speed and cost.

**Align: al-dev-developer**
Observation: The Inputs table marks `.dev/*-al-dev-plan-solution-plan.md` and `.dev/*-al-dev-test-test-plan.md` as **Required**. However, `/al-dev-fix` dispatches the developer with a fully inline prompt ("Fix [issue] in [file]… Issue: … Expected fix: …") — no solution-plan file is created or passed. The **Required** label is only true for the `/al-dev-develop` caller path. The mismatch means `/al-dev-fix`-dispatched developer instances are technically violating their own contract on every call.
Suggestion: Update the Inputs table to distinguish callers: mark the solution-plan input as "Required (from /al-dev-develop) | Inline prompt (from /al-dev-fix)". Alternatively, split the Required column into caller-specific rows.
Trade-off: Documentation-only change; clarifies that the agent can operate in two modes and prevents future callers from assuming a file must always be present.

**Align: al-dev-solution-architect**
Observation: The Inputs table marks "Dated requirements file" as **Required** ("From /interview"). `/al-dev-fix` dispatches the architect with an inline analysis prompt containing only a root-cause hypothesis and fix approach — no requirements file is created or referenced. Same mismatch pattern as al-dev-developer: the **Required** label reflects `/al-dev-plan` usage, not `/al-dev-fix` usage.
Suggestion: Update the Inputs table to note "Required (from /al-dev-plan) | Inline prompt (from /al-dev-fix)". This makes the dual-caller contract explicit.
Trade-off: Documentation-only; prevents callers from assuming they must always produce a requirements file before dispatching the architect.

**Align: al-dev-security-reviewer**
Observation: The `## Spawn Context` section says "You are spawned as part of a 4-reviewer team (security, AL expert, performance, test coverage)." No `al-dev-test-coverage-reviewer` agent exists in the plugin. `/al-dev-develop` confirms a 3-specialist panel only. The stale reference causes the agent to expect a test-coverage opinion that is never provided, which may distort its debate posture.
Suggestion: Update the `## Spawn Context` section in `al-dev-security-reviewer.md` to read "3-reviewer team (security, AL expert, performance)." Apply the same fix to `al-dev-performance-reviewer.md` which references "Test Coverage Reviewer's mocking requirement" in its debate section.
Trade-off: Two-file documentation fix; removes misleading team context that shapes how the agent debates findings.

**Align: al-dev-release-notes-agent**
Observation: The `research-context` phase in the body calls `al-mcp-server` tools (`al_get_object_summary`, `al_get_object_definition`) and `bc-code-intelligence-mcp` (`ask_bc_expert`). These MCP servers are not declared in the frontmatter tools list `["Bash", "Write", "Read", "Glob"]`. The harness uses the tools list to grant tool access; undeclared MCP tools cannot be called at runtime.
Suggestion: Verify current frontmatter — commit `ebd0144` (2026-05-18) claimed to add MCP tools to this agent. If the fix landed, this suggestion is already resolved. If not, add `mcp__plugin_profile-claude-al-dev_al-mcp-server` and `mcp__plugin_profile-claude-al-dev_bc-code-intelligence-mcp`.
Trade-off: Adding MCP tools unlocks the AL object research phase. If the MCP phase is unreachable in practice, remove it from the body instead.

**Trim: al-dev-explore**
Observation: Tools list includes `Bash`; the system prompt body contains no Bash commands. The body explicitly scopes the agent to search tools only: "don't read entire files unless necessary," "don't perform code analysis or changes — only exploration." No shell invocations appear anywhere in the body.
Suggestion: Remove `Bash` from the tools list in the agent frontmatter.
Trade-off: Minimal — tool wasn't used; tighter least-privilege posture.

### Inline candidates

> Detected 2026-05-18. No agent met the minimal-body threshold (< 15 lines after frontmatter) — smallest body is al-dev-explore at 32 lines. Candidates below score on single-caller + no I/O docs only. Inlining any of them would add 113–485 lines to the calling skill; treat as documentation gaps rather than inline targets.

- **al-dev-commit-agent** — single caller /al-dev-commit; 485-line body; no I/O docs. Add Inputs/Outputs documentation.
- **al-dev-expert-reviewer** — single caller /al-dev-develop; 126-line body; no I/O docs. Add Inputs/Outputs documentation.
- **al-dev-performance-reviewer** — single caller /al-dev-develop; 113-line body; no I/O docs. Add Inputs/Outputs documentation.
- **al-dev-release-notes-agent** — single caller /al-dev-release-notes; 224-line body; no I/O docs. Add Inputs/Outputs documentation.
- **al-dev-security-reviewer** — single caller /al-dev-develop; 158-line body; no I/O docs. Add Inputs/Outputs documentation.
- **al-dev-support-agent** — single caller /al-dev-support; 174-line body; no I/O docs. Add Inputs/Outputs documentation.
