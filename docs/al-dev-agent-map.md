# AL Dev Agent Map

**Last updated:** 2026-06-15

<!-- BEGIN GENERATED: agent-coverage -->
**Coverage:** 24 active agents in `profile-al-dev-shared/agents/` (count derived from disk at generation time).
<!-- END GENERATED: agent-coverage -->

> **Generated sections** are refreshed by `scripts/generate-map-doc-sections.py`. Do not hand-edit inside `<!-- BEGIN/END GENERATED -->` markers. The Coverage count above is generator-owned — never edit or copy it by hand.

## Layer 1: Agent Catalog

<!-- BEGIN GENERATED: agent-catalog-table -->
| Agent | Model | Tools | Spawned by |
|-------|-------|-------|------------|
| al-dev-al-pattern-reviewer | haiku | Read | `/al-dev-review-develop` |
| al-dev-commit-analyzer | haiku | Bash, Read | `/al-dev-commit-preflight` |
| al-dev-commit-executor | haiku | Bash, Read | `/al-dev-commit-execute` |
| al-dev-commit-group-drafter | sonnet | (none) | `/al-dev-commit-preflight` |
| al-dev-commit-hook-classifier | haiku | Read | `/al-dev-commit-execute` |
| al-dev-commit-hook-fixer | sonnet | Read, Write, Bash | `/al-dev-commit-execute` |
| al-dev-commit-lint-fixer | haiku | Bash, Read | `/al-dev-commit-execute` |
| al-dev-commit-ooxml-validator | haiku | Bash | `/al-dev-commit-execute` |
| al-dev-commit-recover-fixer | sonnet | Write, Bash | `/commit-recover` |
| al-dev-developer-tdd | sonnet | Read, Write, Bash | `/al-dev-develop-orchestrate` |
| al-dev-developer-traditional | sonnet | Read, Write, Bash | `/al-dev-develop-orchestrate`, `/al-dev-fix` |
| al-dev-diagnostics-resolver | sonnet | Read, Edit, Bash | `/al-dev-lint` |
| al-dev-docs-writer | sonnet | Read, Write | (none found) |
| al-dev-explore | haiku | Read, Glob, Grep, Write | (none found) |
| al-dev-general-code-reviewer | haiku | Read | (none found) |
| al-dev-interview | sonnet | Read, Write, USER_GATE | `/al-dev-interview` |
| al-dev-performance-reviewer | sonnet | Read | `/al-dev-review-develop` |
| al-dev-release-notes-writer | sonnet | Bash, Write, Read, MCP: al-mcp-server | `/al-dev-release-notes` |
| al-dev-script-engineer | sonnet | Read, Write, Bash | (none found) |
| al-dev-security-reviewer | sonnet | Read | `/al-dev-review-develop` |
| al-dev-solution-architect | opus | Read, Write, Glob, Grep | `/al-dev-fix`, `/al-dev-plan` |
| al-dev-support-reply-drafter | sonnet | Write | `/al-dev-support-reply` |
| al-dev-support-researcher | sonnet | MCP: bc-code-intelligence, MCP: microsoft-docs | `/al-dev-support-reply` |
| al-dev-ticket-context-writer | haiku | Bash, Write | `/al-dev-ticket` |
<!-- END GENERATED: agent-catalog-table -->

---

## Layer 2: Per-Agent Profiles

### al-dev-general-code-reviewer

**Description:** General code review specialist — finds bugs, logic errors, and security issues with high signal-to-noise ratio. Available for standalone use; not integrated into /al-dev-develop-orchestrate (which uses specialist reviewers for security, patterns, and performance).
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

### al-dev-commit-analyzer

**Description:** Git commit analyzer agent. Reads staged diffs and builds per-file manifests with object IDs and change signatures. Dispatched by al-dev-commit-preflight (analysis phase). Read-only — never modifies files.
**Model:** haiku
**Tools:** Bash, Read
**Spawned by:** /al-dev-commit-preflight

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `PROJECT_CONTEXT` and `FD_TICKET` from /al-dev-commit-preflight |
| Staged git index | **Yes** | Read via `git diff --cached` commands |

**Outputs:**

| Output | Description |
|--------|-------------|
| `MANIFESTS` block | Per-file change summary (object IDs, added/removed fields and procedures) |
| `WARNINGS` block | Validation issues and advisory notices |

---

### al-dev-commit-group-drafter

**Description:** Git commit group drafter. Consumes manifests from al-dev-commit-analyzer and drafts commit messages with context-aware description. Enables independent iteration on message quality.
**Model:** sonnet
**Tools:** (none)
**Spawned by:** /al-dev-commit-preflight

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `MANIFESTS`, `PROJECT_CONTEXT`, `FD_TICKET` from /al-dev-commit-preflight |
| Project context | No | `.dev/project-context.md` for domain knowledge |

**Outputs:**

| Output | Description |
|--------|-------------|
| `PROPOSED_GROUPS` block | Atomic commit group proposals with rationale |
| `DELETIONS` block | Staged deletions for the user audit gate |
| `WARNINGS` block | Validation issues and advisory notices |

---

### al-dev-commit-executor

**Description:** Git commit execution agent. Executes git commits from an approved plan, handling hook failures and retry logic. Dispatched by al-dev-commit-execute (execute phase) after al-dev-commit-lint-fixer and al-dev-commit-ooxml-validator complete. Never writes or edits source files directly — all fixes go through Bash.
**Model:** haiku
**Tools:** Bash, Read
**Spawned by:** /al-dev-commit-execute

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

**Description:** Pre-flight lint and trailing-whitespace fixer for staged commit files. Runs Python lint (ruff), trailing whitespace fixes on text files, and line-count corruption detection. Returns LINT_FIXES. Dispatched sequentially by al-dev-commit-execute (preflight) before OOXML validation. Applies fixes via Bash only; never uses Write or Edit on source files.
**Model:** haiku
**Tools:** Bash, Read
**Spawned by:** /al-dev-commit-execute

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

**Description:** OOXML ZIP integrity validator for staged commit files. Validates .docx, .xlsx, .pptx, and .odt files using unzip integrity check. Returns OOXML_FAILURES. Dispatched sequentially by al-dev-commit-execute (validation) after lint preflight. Read-only: never modifies files.
**Model:** haiku
**Tools:** Bash
**Spawned by:** /al-dev-commit-execute

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `APPROVED_PLAN` — approved groups from analysis phase (GROUP_N structured blocks with `files:` and `message:` fields) |

**Outputs:**

| Output | Description |
|--------|-------------|
| `OOXML_FAILURES` | OOXML files that failed ZIP validation with reason (or `NONE`) |

---

### al-dev-commit-hook-classifier

**Description:** Classify pre-commit hook failures by recoverability. Reads hook failure logs and assigns each failure to fixable, transient, or non-fixable using the Failure Classification table in knowledge/commit-hook-recovery-patterns.md. Dispatched by al-dev-commit-execute before al-dev-commit-hook-fixer.
**Model:** haiku
**Tools:** Read
**Spawned by:** /al-dev-commit-execute

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `.dev/hook-failures.json` | **Yes** | Hook execution output (hook name, exit code, stderr/stdout). Read from file; fall back to the `HOOK_FAILURES` block in the dispatch prompt if missing. |
| `.dev/commits.json` | No | Commit details that triggered the hooks; used for context only |

**Outputs:**

| Output | Description |
|--------|-------------|
| `HOOK_CLASSIFICATIONS` block | Per-failure classification: recoverability, root cause, recommended fix |

---

### al-dev-commit-hook-fixer

**Description:** Apply scripted recovery fixes for classified pre-commit hook failures. Reads the HOOK_CLASSIFICATIONS block from al-dev-commit-hook-classifier, applies scripted bash fixes for Fixable failures, re-stages affected files, and returns recovery status. Never re-runs commits itself — returns next_step guidance so the caller re-dispatches the execute agent. Handles the error path in isolation; classification is handled by al-dev-commit-hook-classifier.
**Model:** sonnet
**Tools:** Read, Write, Bash
**Spawned by:** /al-dev-commit-execute

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
**Spawned by:** /al-dev-develop-orchestrate

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
**Spawned by:** /al-dev-develop-orchestrate, /al-dev-fix

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

### al-dev-diagnostics-resolver

**Description:** Resolve AL lint warnings and compile errors surfaced by al-compile. Groups issues by rule ID, applies auto-fixes for scripted rules, and escalates judgment-required rules to the caller. Dispatched by al-dev-lint skill.
**Model:** sonnet
**Tools:** Read, Edit, Bash
**Spawned by:** `/al-dev-lint`

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

### al-dev-al-pattern-reviewer

**Description:** Review AL code for adherence to naming conventions, AL patterns, and BC design patterns.
**Model:** haiku
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
| AL Expert Review Findings | Text report returned to /al-dev-develop-orchestrate; structured as Critical / High / Minor Issues |

---

### al-dev-explore

**Description:** Fast codebase exploration — finds files by pattern, searches for symbols, answers structural questions about code organization.
**Model:** haiku
**Tools:** Read, Glob, Grep, Write
**Spawned by:** (none found)

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
| Performance Review Findings | Text report returned to /al-dev-develop-orchestrate; structured as Critical / High / Medium / Low |

---

### al-dev-release-notes-writer

**Description:** Run git diff analysis between two hashes, research AL object context, and write .dev/release-notes-\<version\>.md.
**Model:** sonnet
**Tools:** Bash, Write, Read, MCP: al-mcp-server
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
**Spawned by:** (none found)

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
| Security Review Findings | Text report returned to /al-dev-develop-orchestrate; structured as Critical / High / Medium / Low |

---

### al-dev-solution-architect

**Description:** Design BC-integrated solutions and create detailed implementation plans.
**Model:** opus
**Tools:** Read, Write, Glob, Grep
**Spawned by:** /al-dev-fix, /al-dev-plan

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
**Tools:** MCP: bc-code-intelligence, MCP: microsoft-docs
**Spawned by:** /al-dev-support-reply (research phase)

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
**Spawned by:** /al-dev-support-reply (reply phase)

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

### al-dev-ticket-context-writer

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
**Tools:** Write, Bash
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

> **Findings live in the health dossier, not in this map.** This map is
> documentation only — it describes the current agent roster. To find
> improvement suggestions (Trim, Remodel, Split, Inline, Align), run
> `/plugin-health-audit` and read the ranked dossier in `docs/health/`, then
> `/al-dev-map-suggestions-verify` to turn accepted findings into a plan.
>
> History: in-map suggestions through 2026-06-01 were retired when findings
> converged on the health dossier (2026-06-02).
