# AL Dev Agent Map

**Last updated:** 2026-06-01 (22 agents; analysis refreshed with 5 new suggestions)

## Layer 1: Agent Catalog

<!-- BEGIN GENERATED: agent-catalog-table -->
| Agent | Model | Tools | Spawned by |
|-------|-------|-------|------------|
| al-dev-code-review | haiku | Read | (none found) |
| al-dev-commit-agent-analysis | haiku | Bash, Read | `/al-dev-commit` |
| al-dev-commit-agent-execute | haiku | Bash, Read | `/al-dev-commit` |
| al-dev-commit-hook-fixer | sonnet | Read, Write, Bash | `/al-dev-commit` |
| al-dev-commit-lint-fixer | haiku | Bash, Read | `/al-dev-commit` |
| al-dev-commit-message-drafter | sonnet | (none) | `/al-dev-commit` |
| al-dev-commit-ooxml-validator | haiku | Bash | `/al-dev-commit` |
| al-dev-commit-recover-fixer | sonnet | Write | `/commit-recover` |
| al-dev-developer-tdd | sonnet | Read, Write, Bash | `/al-dev-develop`, `/al-dev-fix` |
| al-dev-developer-traditional | sonnet | Read, Write, Bash | `/al-dev-develop`, `/al-dev-fix`, `/al-dev-review-develop` |
| al-dev-diagnostics-fixer | sonnet | Read, Edit | `/al-dev-lint` |
| al-dev-docs-writer | sonnet | Read, Write | (none found) |
| al-dev-expert-reviewer | sonnet | Read | `/al-dev-review-develop` |
| al-dev-explore | haiku | Read, Glob, Grep, Write | (none found) |
| al-dev-interview | sonnet | Read, Write, USER_GATE | `/al-dev-interview` |
| al-dev-performance-reviewer | sonnet | Read | `/al-dev-review-develop` |
| al-dev-release-notes-writer | sonnet | Bash, Write, Read | `/al-dev-release-notes` |
| al-dev-script-engineer | sonnet | Read, Write, Bash | (none found) |
| al-dev-security-reviewer | sonnet | Read | `/al-dev-review-develop` |
| al-dev-solution-architect | opus | Read, Write, Glob, Grep | `/al-dev-fix`, `/al-dev-plan` |
| al-dev-support-reply-drafter | sonnet | Write | `/al-dev-support-reply` |
| al-dev-support-researcher | sonnet | (none) | `/al-dev-support-reply` |
| al-dev-ticket-agent | haiku | Bash, Write | `/al-dev-ticket` |
<!-- END GENERATED: agent-catalog-table -->

---

## Layer 2: Per-Agent Profiles

### al-dev-code-review

**Description:** General code review specialist — finds bugs, logic errors, and security issues with high signal-to-noise ratio. Available for standalone use; not integrated into /al-dev-develop (which uses specialist reviewers for security, patterns, and performance).
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

**Description:** Git commit analyzer agent. Reads staged diffs and builds per-file manifests with object IDs and change signatures. Dispatched by al-dev-commit (analysis phase). Read-only — never modifies files.
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
**Model:** sonnet
**Tools:** (none)
**Spawned by:** /al-dev-commit (Phase 2 — message-drafting phase)

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `MANIFESTS`, `PROJECT_CONTEXT`, `FD_TICKET` from /al-dev-commit |
| Project context | No | `.dev/project-context.md` for domain knowledge |

**Outputs:**

| Output | Description |
|--------|-------------|
| `PROPOSED_GROUPS` block | Atomic commit group proposals with rationale |
| `DELETIONS` block | Staged deletions for the user audit gate |
| `WARNINGS` block | Validation issues and advisory notices |

---

### al-dev-commit-agent-execute

**Description:** Git commit execution agent. Executes git commits from an approved plan, handling hook failures and retry logic. Dispatched by al-dev-commit (execute phase) after al-dev-commit-lint-fixer and al-dev-commit-ooxml-validator complete. Never writes or edits source files directly — all fixes go through Bash.
**Model:** haiku
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
| `HOOK_FAILURES` | Raw hook output for any failed groups (or `NONE`) |
| `STRIPPED_ATTRIBUTIONS` | Removed AI attribution lines (or `NONE`) |

---

### al-dev-commit-lint-fixer

**Description:** Pre-flight lint and trailing-whitespace fixer for staged commit files. Runs Python lint (ruff), trailing whitespace fixes on text files, and line-count corruption detection. Returns LINT_FIXES. Dispatched sequentially by al-dev-commit (Step 9.5a) before OOXML validation. Applies fixes via Bash only; never uses Write or Edit on source files.
**Model:** haiku
**Tools:** Bash, Read
**Spawned by:** /al-dev-commit (Step 9.5a — lint pre-flight)

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `APPROVED_PLAN` — approved groups from analysis phase (GROUP_N structured blocks with `files:` and `message:` fields) |

**Outputs:**

| Output | Description |
|--------|-------------|
| `LINT_FIXES` | Files re-staged after lint fixes (or `NONE`) |

---

### al-dev-commit-ooxml-validator

**Description:** OOXML ZIP integrity validator for staged commit files. Validates .docx, .xlsx, .pptx, and .odt files using unzip integrity check. Returns OOXML_FAILURES. Dispatched sequentially by al-dev-commit (Step 9.5b) after lint preflight. Read-only: never modifies files.
**Model:** haiku
**Tools:** Bash
**Spawned by:** /al-dev-commit (Step 9.5b — OOXML validation)

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `APPROVED_PLAN` — approved groups from analysis phase (GROUP_N structured blocks with `files:` and `message:` fields) |

**Outputs:**

| Output | Description |
|--------|-------------|
| `OOXML_FAILURES` | OOXML files that failed ZIP validation with reason (or `NONE`) |

---

### al-dev-commit-hook-fixer

**Description:** Diagnose and recover from pre-commit hook failures. Analyzes hook error logs, identifies root causes, recommends fixes, and optionally reruns commits with corrections applied. Complements al-dev-commit-agent-execute by handling error recovery in isolation.
**Model:** sonnet
**Tools:** Read, Write, Bash
**Spawned by:** /al-dev-commit (Phase 4 — error recovery)

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `.dev/hook-failures.json` | **Yes** | Hook execution output and error logs from the failed commit attempt (hook name, exit code, captured stderr/stdout) |
| `.dev/commits.json` | **Yes** | Commit details that triggered the hooks (group id, files, approved message) |

**Outputs:**

| Output | Description |
|--------|-------------|
| `HOOK_FAILURES` block | Per-failure diagnosis, recovery status, and the next step for the caller |

---

### al-dev-developer-tdd

**Description:** Implement AL code using test-driven development when a test plan exists.
**Model:** sonnet
**Tools:** Read, Write, Bash
**Spawned by:** /al-dev-develop, /al-dev-fix

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `.dev/*-al-dev-plan-solution-plan.md` | **Yes** | Implementation plan |
| `.dev/*-al-dev-test-test-plan.md` | **Yes** | Test plan that drives the TDD cycle |
| `.dev/project-context.md` | No | Project memory and conventions |
| `.dev/*-al-dev-develop-code-review.md` | No | Review findings when iterating |

**Outputs:**

| Output | Description |
|--------|-------------|
| AL source files | Implemented code in `src/` |
| Test codeunits | Test code in `src/Tests/` |
| `.dev/$(date +%Y-%m-%d)-al-dev-developer-tdd-log.md` | TDD log: one entry per RED-GREEN-REFACTOR cycle |
| `.dev/session-log.md` | Session log entry per file |

---

### al-dev-developer-traditional

**Description:** Implement AL code following an implementation plan without test-driven development.
**Model:** sonnet
**Tools:** Read, Write, Bash
**Spawned by:** /al-dev-develop, /al-dev-fix, /al-dev-review-develop (autonomous mode)

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `.dev/*-al-dev-plan-solution-plan.md` | **Yes** | Implementation plan |
| `.dev/project-context.md` | No | Project memory and conventions |
| `.dev/*-al-dev-develop-code-review.md` | No | Review findings for iteration |

**Outputs:**

| Output | Description |
|--------|-------------|
| AL source files | Implemented code in `src/` |
| `.dev/session-log.md` | Session log entry per file |

---

### al-dev-diagnostics-fixer

**Description:** Resolve AL lint warnings and compile errors surfaced by al-compile.
**Model:** sonnet
**Tools:** Read, Edit
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
**Tools:** Read, Write
**Spawned by:** (none found)

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
**Model:** sonnet
**Tools:** Read
**Spawned by:** /al-dev-review-develop

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
| `.dev/$(date +%Y-%m-%d)-al-dev-explore-findings.md` | Persistent findings file written by the `/al-dev-explore` skill |

---

### al-dev-interview

**Description:** Interview the user to extract complete BC/AL implementation details through structured questioning.
**Model:** sonnet
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
**Model:** sonnet
**Tools:** Read
**Spawned by:** /al-dev-review-develop

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
**Tools:** Bash, Write, Read
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
| `.dev/$(date +%Y-%m-%d)-al-dev-release-notes-<VERSION or short-hash>.md` | **Primary** — formatted release notes file |
| Return block | `RELEASE_NOTES_WRITTEN`, `VERSION`, `CHANGES`, `SUMMARY`, `EXCLUDED`, `DIAGRAMS`, `AMBIGUOUS` |

---

### al-dev-script-engineer

**Description:** Write, validate, and run scripts for AL development and documentation workflows.
**Model:** sonnet
**Tools:** Read, Write, Bash
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
**Tools:** Read
**Spawned by:** /al-dev-review-develop

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
**Tools:** Read, Write, Glob, Grep
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
**Tools:** (none)
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
**Model:** sonnet
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
**Spawned by:** /al-dev-ticket (fetch + attachment-download phases in `--mode=context-only` and `--mode=full`)

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

### al-dev-commit-recover-fixer

**Description:** Recover corrupted AL files flagged in `.dev/commit-integrity.log` using fallback strategies and learned patterns.
**Model:** sonnet
**Tools:** Write
**Spawned by:** /commit-recover

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `REPO` | No | Inferred from working directory; not passed explicitly by /commit-recover |
| `CORRUPTION_LOG` | **Yes** | Path to `.dev/commit-integrity.log` with flagged files |
| `auto_fix` | No | If true, apply auto-fixes; if false, report findings only |

**Outputs:**

| Output | Description |
|--------|-------------|
| Fixed AL files | Recovered via fallback strategies (git restore, regex reconstruction, schema rebuild) |
| `.dev/$(date +%Y-%m-%d)-al-dev-commit-recover-report.md` | Recovery report with per-file strategy and status |

---

## Observations

> Generated by /analyze-agent-design on 2026-06-01.
> Run /review-agent-map first if the agent list has changed since this was written.

### Agents used by only one skill

- **al-dev-commit-agent-analysis** — used only by /al-dev-commit (Phase 1: analysis)
- **al-dev-commit-agent-execute** — used only by /al-dev-commit (Phase 3: execution)
- **al-dev-commit-lint-fixer** — used only by /al-dev-commit (Step 9.5a: lint pre-flight)
- **al-dev-commit-message-drafter** — used only by /al-dev-commit (Phase 2: message composition)
- **al-dev-commit-ooxml-validator** — used only by /al-dev-commit (Step 9.5b: OOXML validation)
- **al-dev-commit-recover-fixer** — used only by /commit-recover
- **al-dev-diagnostics-fixer** — used only by /al-dev-lint
- **al-dev-docs-writer** — used only by /al-dev-document (Step 2 — dispatched as docs-writer specialist)
- **al-dev-expert-reviewer** — used only by /al-dev-review-develop
- **al-dev-interview** — used only by /al-dev-interview
- **al-dev-performance-reviewer** — used only by /al-dev-review-develop
- **al-dev-release-notes-writer** — used only by /al-dev-release-notes
- **al-dev-security-reviewer** — used only by /al-dev-review-develop
- **al-dev-support-reply-drafter** — used only by /al-dev-ticket (support mode: reply phase)
- **al-dev-support-researcher** — used only by /al-dev-ticket (support mode: research phase)

### Agents with no inputs/outputs documentation

None — all 22 agents have documented Inputs and Outputs tables.

### Potential shared agents

- **al-dev-developer-tdd** — used by /al-dev-develop and /al-dev-fix when a test plan exists
- **al-dev-developer-traditional** — used by /al-dev-develop, /al-dev-fix, and /al-dev-review-develop (autonomous compile-fix loops)
- **al-dev-solution-architect** — used by /al-dev-plan, /al-dev-fix
- **al-dev-ticket-agent** — used by /al-dev-ticket (all three modes)

### Audit Sync: 3 Discrepancies Resolved (2026-06-01)

Based on agent audit from `20260601T002200Z`, the map has been synchronized with ground-truth agent file declarations:

**Archived agents removed (2 agents) — resolved:**

- `plan-map-changes-duck-worker`: Removed from Layer 1 Catalog and Layer 2 profile. Agent is archived at `profile-al-dev-shared/archived/agents/plan-map-changes-duck-worker.md`. (Skill renamed to `al-dev-map-suggestions-verify`.)
- `plugin-health-team`: Removed from Layer 1 Catalog and Layer 2 profile. Agent is archived at `profile-al-dev-shared/archived/agents/plugin-health-team.md`.

**Caller mismatch (1 agent) — resolved:**

- `al-dev-docs-writer`: Spawned by field updated to `(none found)`. The al-dev-document skill invokes this agent via a prose alias ("docs-writer teammate") rather than a qualified `al-dev-shared:` name, so no invocation is detected by grep. The agent remains active; only the map field has been corrected to reflect the grep-derived value.

### Audit Sync: 20 Discrepancies Resolved (2026-06-01)

Based on agent audit from `20260531T222851Z`, the map has been synchronized with ground-truth agent file declarations:

**Tools drift (13 agents) — resolved:**
All 13 agents with undeclared tools have been updated to reflect their actual tool declarations in agent files. Removed inferred tools that are not in agent frontmatter (Edit, Glob, Grep, MCP: * tools) to ensure map accuracy aligns with implementation.

**Model drift (2 agents) — resolved:**

- `al-dev-interview`: Updated from haiku → sonnet (agent file specifies sonnet)
- `al-dev-commit-recover-fixer`: Updated from haiku → sonnet (agent file specifies sonnet)

**Archived agents (5 agents) — noted:**
Archived test engineer agents are missing the `name` field in YAML frontmatter. These agents are not active in the current system and are archived; their files are in `profile-al-dev-shared/archived/agents/`. No action required for the active agent map.

### Quality suggestions

**Remodel: al-dev-commit-recover-fixer**
Observation: Agent performs recovery strategy selection across three fallback methods (git restore, regex reconstruction, schema rebuild), per-file verdict documentation, and recovery report authoring; currently assigned haiku.
Suggestion: Change model to sonnet — task requires multi-step judgment (strategy selection per file, evidence documentation, report synthesis), not simple mechanical execution.
Trade-off: Slightly higher cost per recovery run; justified because wrong strategy selection or incomplete recovery reports are the most likely failure modes.

**Remodel: al-dev-interview** <- highest leverage
Observation: Agent conducts 40+ structured questions with adaptive follow-up, handles requirement conflicts, and synthesizes a complete spec with REQ/ACC tokens and risk assessments; currently assigned haiku.
Suggestion: Change model to sonnet — sustained adaptive reasoning and spec synthesis go well beyond single-step retrieval.
Trade-off: Higher cost per interview run; justified because missed requirements or poorly resolved conflicts create 3x rework downstream in /al-dev-plan.

**Align: al-dev-commit-agent-execute**
Observation: Agent's Outputs table documents `STRIPPED_ATTRIBUTIONS`; the caller skill (/al-dev-commit Step 11 summary display) only reads COMMITS, SKIPPED, and HOOK_FAILURES — STRIPPED_ATTRIBUTIONS is never consumed.
Suggestion: Remove STRIPPED_ATTRIBUTIONS from the Outputs table if attribution stripping is automatic and silent, or update /al-dev-commit Step 11 to display it if attribution stripping should be surfaced to the user.
Trade-off: Documentation-only change; prevents future caller confusion about which outputs are actually consumed.

**Split: plugin-health-team**
Observation: System prompt describes two separable concerns — (1) lens batch orchestration (spawn 4-6 lenses, track progress, manage timeouts) and (2) result collection (read completed lens outputs, write manifest, write findings files).
Suggestion: Extract result collection into a new agent `plugin-health-result-collector`; have the orchestrator hand off a completion list and terminate; the collector reads and aggregates lens results independently.
Trade-off: One new agent file to maintain; each agent's scope becomes narrower — orchestration failures can be diagnosed separately from collection failures.

**Implemented: Remodel al-dev-code-review** (2026-06-01)
Agent model downgraded from sonnet to haiku. Justification: Single-file pattern-matching review task with no active callers requires only read + categorize capability — haiku is appropriately scoped and reduces cost without signal loss.

### Inline candidates

None detected. All single-purpose agents have documented Inputs/Outputs sections and body length >10 lines; they do not meet the 2+ signal threshold for inlining.

### Previously implemented improvements

**Confirmed implemented: Remodel al-dev-solution-architect** (2026-05-29)
Both /al-dev-plan and /al-dev-fix already conditionally pass `model: sonnet` for SIMPLE tier and omit the model parameter (defaulting to opus) for MEDIUM/COMPLEX. No spawning-skill change needed.

**Confirmed implemented: Split al-dev-commit-agent-execute** (2026-05-29; preflight further split 2026-05-31)
Pre-flight lint and OOXML validation extracted into two focused agents: `al-dev-commit-lint-fixer` (Step 9.5a — ruff, trailing whitespace, line-count corruption) and `al-dev-commit-ooxml-validator` (Step 9.5b — ZIP integrity). al-dev-commit-agent-execute handles only git commit invocation and hook retry logic.

**Confirmed implemented: Align al-dev-commit-recover-fixer** (2026-05-29)
Inputs table line 23 already reads: "Inferred from working directory; not passed explicitly by /commit-recover."

**Confirmed implemented: Align al-dev-ticket-agent** (2026-05-29)
Inputs table rows already document FRESHDESK_API_KEY and FRESHDESK_DOMAIN as "available as shell environment variable in agent bash context" with a Note block explaining the injection mechanism.

**Confirmed implemented: Align al-dev-developer TDD activation** (2026-05-29)
Inputs table already marks test-plan as Optional. Agent body correctly implements dual-path logic (TDD if file present, traditional if absent).

**Confirmed implemented: Align al-dev-review-develop stub** (2026-05-29)
al-dev-review-develop/SKILL.md is fully implemented with all Phases 5-10 including reviewer spawn calls in Phase 6-7. Not a stub.

**Restored al-dev-commit-recover-fixer agent** (2026-05-29)
Agent file was empty; now restored with proper YAML frontmatter (haiku, Bash/Read/Write) and full recovery system prompt.

**Remodelled sonnet agents to haiku** (2026-05-27)
Downgraded commit-agent-analysis, commit-message-drafter, interview, support-reply-drafter. Sonnet retained for diagnostics-fixer, expert-reviewer, performance-reviewer, security-reviewer (all require high technical judgment per model-fit re-verification on 2026-06-01).

**Trimmed al-dev-support-reply-drafter tools** (2026-05-27)
Removed unused `Read` from tools list. Agent receives all input via dispatch block; no file reads needed.

**Trimmed al-dev-commit-message-drafter tools** (2026-05-27)
Removed unused `Read` from tools list. Agent analyzes manifests from dispatch prompt without file I/O.

**Upgraded al-dev-commit-agent-execute** (2026-05-22)
Model changed from haiku to sonnet for multi-phase orchestration (lint + validation + commit + retry) with error recovery.

**Split al-dev-commit into three sequential agents** (2026-05-22)

- al-dev-commit-agent-analysis (manifest extraction, read-only)
- al-dev-commit-message-drafter (editorial, message composition)
- al-dev-commit-agent-execute (operational, commit execution)

Enabled independent iteration and audit gates between phases.

**Trimmed al-dev-support-researcher tools** (2026-05-22)
Removed WebSearch and WebFetch; restricted to AL Symbols, MS Docs, BC Code History only.
