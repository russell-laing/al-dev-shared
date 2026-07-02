# AL Dev Agent Map

**Last updated:** 2026-07-02

<!-- BEGIN GENERATED: agent-coverage -->
**Coverage:** 32 active agents in `profile-al-dev-shared/agents/` (count derived from disk at generation time).
<!-- END GENERATED: agent-coverage -->

> **Generated sections** are refreshed by `scripts/generate_map_doc_sections.py`. Do not hand-edit inside `<!-- BEGIN/END GENERATED -->` markers. The Coverage count above is generator-owned — never edit or copy it by hand.

## Layer 1: Agent Catalog

<!-- BEGIN GENERATED: agent-catalog-table -->
| Agent | Model | Tools | Spawned by |
|-------|-------|-------|------------|
| al-pattern-reviewer | sonnet | Read | `/review-develop` |
| bc-support-researcher | sonnet | MCP: bc-code-intelligence, MCP: microsoft-docs | `/support-reply` |
| change-analyzer | haiku | Read | (none found) |
| codebase-explorer | sonnet | Bash, Read, Glob, Grep, Write | (none found) |
| commit-analyzer | haiku | Bash, Read | `/commit-preflight` |
| commit-executor | haiku | Bash, Read | `/commit-execute` |
| commit-group-drafter | haiku | (none) | `/commit-preflight` |
| commit-hook-classifier | haiku | Read | `/commit-execute` |
| commit-hook-fixer | sonnet | Read, Write, Bash | `/commit-execute` |
| commit-lint-fixer | haiku | Bash, Read | `/commit-execute` |
| corruption-recover | sonnet | Write, Bash | `/commit-recover` |
| developer-tdd | sonnet | Read, Write, Bash | `/develop-orchestrate` |
| developer-traditional | sonnet | Read, Write, Bash | `/develop-orchestrate`, `/fix` |
| diagnostics-classifier | haiku | Read | (none found) |
| diagnostics-decision | haiku | Read | (none found) |
| diagnostics-resolver | sonnet | Read, Edit, Bash | `/lint` |
| docs-writer | sonnet | Read, Write, Edit, Bash | `/document`, `/document-format` |
| ecosystem-researcher | sonnet | MCP: bc-code-intelligence, MCP: microsoft-docs | `/bc-research` |
| evidence-gatherer | sonnet | Read, Write, Bash, MCP: bc-code-intelligence | (none found) |
| findings-synthesizer | haiku | Read | (none found) |
| general-code-reviewer | sonnet | Read | (none found) |
| interview | sonnet | Read, USER_GATE | `/interview` |
| performance-reviewer | sonnet | Read | `/review-develop` |
| question-gatherer | sonnet | Write | (none found) |
| release-notes-writer | sonnet | Read, Write, Bash | `/release-notes` |
| repo-researcher | sonnet | Read, Glob, Grep, MCP: al-mcp-server, MCP: bc-code-intelligence | `/bc-research` |
| script-engineer | sonnet | Read, Write, Bash | (none found) |
| security-reviewer | sonnet | Read | `/review-develop` |
| solution-architect | opus | Read, Write, Glob, Grep | `/fix`, `/plan` |
| spec-writer | sonnet | Read, Write | (none found) |
| support-reply-drafter | sonnet | Read, Write, Bash | `/support-reply` |
| ticket-context-writer | haiku | Bash, Write | `/ticket` |
<!-- END GENERATED: agent-catalog-table -->

---

## Layer 2: Per-Agent Profiles

> **Maintainer note:** The per-agent profile blocks below are hand-authored and
> live outside the `<!-- BEGIN/END GENERATED -->` markers.
> `scripts/generate_map_doc_sections.py` refreshes only the coverage count and the
> catalog table above — it does **not** update these blocks. When an agent is
> renamed, added, or removed, hand-edit the matching `### <agent-name>` block here
> in the same change.

### general-code-reviewer

**Description:** General code review specialist — finds bugs, logic errors, and security issues with high signal-to-noise ratio. Available for standalone use; not integrated into /develop-orchestrate (which uses specialist reviewers for security, patterns, and performance).
**Model:** sonnet
**Tools:** Read
**Spawned by:** (none found in skill files)

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| Files to review | **Yes** | Via spawn prompt — file paths or diff scope |
| Spawn prompt | **Yes** | Task context: scope, other active reviewers, any open questions |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| Code Review Findings | Text report returned to calling skill; structured as Critical / High / Medium / Low |

---

### change-analyzer

**Description:** Analyze code changes to extract change type, scope, and user-facing impact. Produces structured change analysis for release-notes-writer.
**Model:** haiku
**Tools:** Read
**Spawned by:** (none found)

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| Commit message | **Yes** | Description of the change |
| Git diff | **Yes** | Unified format diff showing what changed |
| Prior version context | No | Version reference for impact assessment |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| Change analysis block | Structured YAML with change_type, scope, impact, priority, summary, breaking flag |

---

### commit-analyzer

**Description:** Git commit analyzer agent. Reads staged diffs and builds per-file manifests with object IDs and change signatures. Dispatched by commit-preflight (analysis phase). Read-only — never modifies files.
**Model:** haiku
**Tools:** Bash, Read
**Spawned by:** /commit-preflight

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| Dispatch prompt | **Yes** | `PROJECT_CONTEXT` and `FD_TICKET` from /commit-preflight |
| Staged git index | **Yes** | Read via `git diff --cached` commands |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| `MANIFESTS` block | Per-file change summary (object IDs, added/removed fields and procedures) |
| `WARNINGS` block | Validation issues and advisory notices |

---

### commit-group-drafter

**Description:** Git commit group drafter. Consumes manifests from commit-analyzer and drafts commit messages with context-aware description. Enables independent iteration on message quality.
**Model:** haiku
**Tools:** (none)
**Spawned by:** /commit-preflight

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| Dispatch prompt | **Yes** | `MANIFESTS`, `PROJECT_CONTEXT`, `FD_TICKET` from /commit-preflight |
| Project context | No | `.dev/project-context.md` for domain knowledge |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| `PROPOSED_GROUPS` block | Atomic commit group proposals with rationale |
| `DELETIONS` block | Staged deletions for the user audit gate |
| `WARNINGS` block | Validation issues and advisory notices |

---

### commit-executor

**Description:** Git commit execution agent. Executes git commits from an approved plan, handling hook failures and retry logic. Dispatched by commit-execute (execute phase) after commit-lint-fixer and commit-ooxml-validator complete. Never writes or edits source files directly — all fixes go through Bash.
**Model:** haiku
**Tools:** Bash, Read
**Spawned by:** /commit-execute

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| Dispatch prompt | **Yes** | `APPROVED_PLAN` — approved groups and messages from analysis phase |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| `COMMITS` block | SHA and message for each committed group |
| `SKIPPED` | Number of skipped groups |
| `HOOK_FAILURES` | Raw hook output for any failed groups (or `NONE`) |
| `STRIPPED_ATTRIBUTIONS` | Removed AI attribution lines (or `NONE`) |

---

### commit-lint-fixer

**Description:** Pre-flight lint and trailing-whitespace fixer for staged commit files. Runs Python lint (ruff), trailing whitespace fixes on text files, and line-count corruption detection. Returns LINT_FIXES. Dispatched sequentially by commit-execute (preflight) before OOXML validation. Applies fixes via Bash only; never uses Write or Edit on source files.
**Model:** haiku
**Tools:** Bash, Read
**Spawned by:** /commit-execute

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| Dispatch prompt | **Yes** | `APPROVED_PLAN` — approved groups from analysis phase (GROUP_N structured blocks with `files:` and `message:` fields) |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| `LINT_FIXES` | Files re-staged after lint fixes (or `NONE`) |

---

### commit-hook-classifier

**Description:** Classify pre-commit hook failures by recoverability. Reads hook failure logs and assigns each failure to fixable, transient, or non-fixable using the Failure Classification table in knowledge/commit-hook-recovery-patterns.md. Dispatched by commit-execute before commit-hook-fixer.
**Model:** haiku
**Tools:** Read
**Spawned by:** /commit-execute

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| `.dev/hook-failures.json` | **Yes** | Hook execution output (hook name, exit code, stderr/stdout). Read from file; fall back to the `HOOK_FAILURES` block in the dispatch prompt if missing. |
| `.dev/commits.json` | No | Commit details that triggered the hooks; used for context only |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| `HOOK_CLASSIFICATIONS` block | Per-failure classification: recoverability, root cause, recommended fix |

---

### commit-hook-fixer

**Description:** Apply scripted recovery fixes for classified pre-commit hook failures. Reads the HOOK_CLASSIFICATIONS block from commit-hook-classifier, applies scripted bash fixes for Fixable failures, re-stages affected files, and returns recovery status. Never re-runs commits itself — returns next_step guidance so the caller re-dispatches the execute agent. Handles the error path in isolation; classification is handled by commit-hook-classifier.
**Model:** sonnet
**Tools:** Read, Write, Bash
**Spawned by:** /commit-execute

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| `.dev/hook-failures.json` | **Yes** | Hook execution output and error logs from the failed commit attempt (hook name, exit code, captured stderr/stdout) |
| `.dev/commits.json` | **Yes** | Commit details that triggered the hooks (group id, files, approved message) |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| `HOOK_FAILURES` block | Per-failure diagnosis, recovery status, and the next step for the caller |

---

### developer-tdd

**Description:** Implement AL code using test-driven development when a test plan exists.
**Model:** sonnet
**Tools:** Read, Write, Bash
**Spawned by:** /develop-orchestrate

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| `.dev/*-plan-solution-plan.md` | **Yes** | Implementation plan |
| `.dev/*-test-test-plan.md` | **Yes** | Test plan that drives the TDD cycle |
| `.dev/project-context.md` | No | Project memory and conventions |
| `.dev/*-develop-code-review.md` | No | Review findings when iterating |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| AL source files | Implemented code in `src/` |
| Test codeunits | Test code in `src/Tests/` |
| `.dev/$(date +%Y-%m-%d)-developer-tdd-log.md` | TDD log: one entry per RED-GREEN-REFACTOR cycle |
| `.dev/session-log.md` | Session log entry per file |

---

### developer-traditional

**Description:** Implement AL code following an implementation plan without test-driven development.
**Model:** sonnet
**Tools:** Read, Write, Bash
**Spawned by:** /develop-orchestrate, /fix

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| `.dev/*-plan-solution-plan.md` | **Yes** | Implementation plan |
| `.dev/project-context.md` | No | Project memory and conventions |
| `.dev/*-develop-code-review.md` | No | Review findings for iteration |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| AL source files | Implemented code in `src/` |
| `.dev/session-log.md` | Session log entry per file |

---

### diagnostics-resolver

**Description:** Resolve AL lint warnings and compile errors surfaced by al-compile. Groups issues by rule ID, applies auto-fixes for scripted rules, and escalates judgment-required rules to the caller. Dispatched by /lint skill.
**Model:** sonnet
**Tools:** Read, Edit, Bash
**Spawned by:** `/lint`

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| `.dev/compile-errors.log` | Yes | Output from `al-compile` |
| AL source files (flagged paths) | Yes | Files to fix |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| Fixed AL source files | In-place fixes applied |
| Dated lint report | `.dev/$(date +%Y-%m-%d)-diagnostics-resolver-lint-report.md` with fix summary |

---

### diagnostics-classifier

**Description:** Classify lint rule violations by remediation strategy. Decides whether each rule group requires human judgment or can be auto-fixed.
**Model:** sonnet
**Tools:** Read
**Spawned by:** (none found)

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| Lint rule groups | **Yes** | Rule violations grouped by rule ID from compile output |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| Classification block | JSON array with decision per rule group: judgment-required or direct-fix |

---

### diagnostics-decision

**Description:** Classify lint rules and determine fix reversibility. Receives a rule and code context; determines whether the fix is safe to apply automatically or requires manual judgment.
**Model:** haiku
**Tools:** Read
**Spawned by:** (none found)

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| Lint rule definition | **Yes** | Rule ID, message, severity |
| Code snippet | **Yes** | Code context where the rule fired |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| Decision block | Classification as safe-auto-fix or judgment-required with reasoning |

---

### docs-writer

**Description:** Generate and maintain AL project documentation — feature docs, API references, and setup guides.
**Model:** sonnet
**Tools:** Read, Write, Edit, Bash
**Spawned by:** /document

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| Latest `*-requirements.md` | **Yes** | What was needed |
| Latest `*-solution-plan.md` | **Yes** | Architecture |
| AL source files | **Yes** | Actual implementation |
| `AUDIENCE` parameter | **Yes** | Target audience (technical, functional, user, executive) |
| Latest `*-code-review.md` | No | Quality notes |
| Latest `*-test-plan.md` | No | Test coverage info |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| `docs/` or `wiki/` | **Primary** — Documentation files |
| `docs/Features/[name].md` | Feature documentation |
| `docs/API/[name].md` | API reference (if public procedures) |
| `CHANGELOG.md` | Updated changelog |
| `.dev/session-log.md` | Append entry with summary |

---

### ecosystem-researcher

**Description:** Research official Microsoft and curated ecosystem guidance for BC/AL questions. Produces structured findings for research synthesis.
**Model:** sonnet
**Tools:** MCP: bc-code-intelligence, MCP: microsoft-docs
**Spawned by:** /research

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| RESEARCH_QUESTION | **Yes** | Research question or hypothesis |
| RESEARCH_SCOPE | **Yes** | Product area, API, workflow, or comparison target |
| VERSION_SCOPE | No | BC or service version focus if known |
| LOCAL_FINDINGS | No | Repo-grounded findings to validate or contrast |
| ADJACENT_SERVICES | No | Specific Microsoft surfaces (Power Platform, Power BI, Excel, Azure, Graph) |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| Findings block | Structured research findings from official sources |

---

### evidence-gatherer

**Description:** Search multiple sources for evidence relevant to a query. Returns raw findings per source across documentation, code samples, and support resources.
**Model:** sonnet
**Tools:** Read, Write, Bash
**Spawned by:** (none found)

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| Search query | **Yes** | The evidence topic to search |
| Source identifiers | **Yes** | Which 3 sources to query (documentation, code samples, support resources) |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| Evidence findings | Per-source findings block with raw results from each source |

---

### findings-synthesizer

**Description:** Synthesize evidence from multiple sources into a unified findings report. Combines results from parallel evidence-gathering operations.
**Model:** haiku
**Tools:** Read
**Spawned by:** (none found)

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| Evidence list | **Yes** | Structured evidence from multiple sources (BC Code Intelligence, Git history, Markdown docs) |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| Unified findings | Synthesized report combining evidence from all sources |

---

### al-pattern-reviewer

**Description:** Review AL code for adherence to naming conventions, AL patterns, and BC design patterns.
**Model:** sonnet
**Tools:** Read
**Spawned by:** /review-develop

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| AL files to review | **Yes** | Via spawn prompt — list of file paths to read |
| Spawn prompt | **Yes** | Task context: what was implemented, any open questions |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| AL Expert Review Findings | Text report returned to /develop-orchestrate; structured as Critical / High / Minor Issues |

---

### explore

**Description:** Fast codebase exploration — finds files by pattern, searches for symbols, answers structural questions about code organization.
**Model:** sonnet
**Tools:** Read, Glob, Grep, Write
**Spawned by:** /explore, /investigate, /perf

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| Question or search task | **Yes** | What to understand about the codebase (via spawn prompt) |
| Scope | No | Directory or file patterns to focus on |
| Context | No | Previous findings to build upon |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| Findings | List of relevant files, code snippets, or relationships |
| Summary | Concise explanation of codebase structure for the query |
| Suggestions | Recommendations for next steps |
| `.dev/$(date +%Y-%m-%d)-explore-findings.md` | Persistent findings file written by the `/explore` skill |

---

### interview

**Description:** Interview the user to extract complete BC/AL implementation details through structured questioning.
**Model:** sonnet
**Tools:** Read, Write, USER_GATE
**Spawned by:** /interview

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| File path argument | No | Existing spec to refine (e.g., `.dev/*-interview-requirements.md`) |
| Fresh start | No | If no file specified, creates new `.dev/*-interview-requirements.md` |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| `.dev/$(date +%Y-%m-%d)-interview-requirements.md` | **Primary** (new interview) — Complete spec with decisions |
| Updated input file | **Primary** (refining) — Enhanced with interview findings |
| `.dev/session-log.md` | Append entry with summary |

---

### performance-reviewer

**Description:** Review AL code for performance issues, inefficient queries, N+1 patterns, and resource consumption.
**Model:** sonnet
**Tools:** Read
**Spawned by:** /review-develop

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| AL files to review | **Yes** | Via spawn prompt — list of file paths to read |
| Spawn prompt | **Yes** | Task context: what was implemented |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| Performance Review Findings | Text report returned to /develop-orchestrate; structured as Critical / High / Medium / Low |

---

### question-gatherer

**Description:** Ask clarifying questions to understand requirements. Applies clarification techniques (probing, rephrasing, examples) and writes collected answers to handoff artifact.
**Model:** sonnet
**Tools:** Write
**Spawned by:** (none found)

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| Requirements topic | **Yes** | Context or topic to interview about |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| `.dev/YYYY-MM-DD-interview-answers.md` | Q&A pairs and clarifications collected from the interview |

---

### release-notes-writer

**Description:** Run git diff analysis between two hashes, research AL object context, and write .dev/release-notes-\<version\>.md.
**Model:** sonnet
**Tools:** Read, Write, Bash
**Spawned by:** /release-notes

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| `START_HASH` | **Yes** | Earlier commit (exclusive lower bound) |
| `END_HASH` | **Yes** | Later commit (inclusive upper bound) |
| `RELEASE_TYPE` | **Yes** | `uat` or `prod` |
| `VERSION` | No | Label (e.g. `v2.1.0`); short hash used if omitted |
| `PROJECT_CONTEXT` | No | Content of `.dev/project-context.md` if it exists |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| `.dev/$(date +%Y-%m-%d)-release-notes-<VERSION or short-hash>.md` | **Primary** — formatted release notes file |
| Return block | `RELEASE_NOTES_WRITTEN`, `VERSION`, `CHANGES`, `SUMMARY`, `EXCLUDED`, `DIAGRAMS`, `AMBIGUOUS` |

---

### repo-researcher

**Description:** Research repository structure, local implementation patterns, and extension seams for BC/AL questions. Produces structured findings for research synthesis.
**Model:** sonnet
**Tools:** Read, Glob, Grep, MCP: al-mcp-server, MCP: bc-code-intelligence
**Spawned by:** /research

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| RESEARCH_QUESTION | **Yes** | Research question or hypothesis |
| RESEARCH_SCOPE | **Yes** | Target feature area, file set, object names, or comparison goal |
| CONTEXT_PATHS | No | Starting files, folders, or documents to inspect first |
| VERSION_SCOPE | No | BC version focus if the caller already knows it matters |
| PRIOR_FINDINGS | No | Findings from other research lanes to check against the repo |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| Findings block | Repo-verified implementation findings and patterns |

---

### script-engineer

**Description:** Write, validate, and run scripts for AL development and documentation workflows.
**Model:** sonnet
**Tools:** Read, Write, Bash
**Spawned by:** (none found)

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| User request | **Yes** | Script goal and AL project context (via spawn prompt) |
| `.dev/02-solution-plan.md` | No | If implementing a planned script |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| Python script file(s) | In `scripts/` following toolkit conventions (Python default) |
| Governance tokens | Inline in documentation or `.dev/` files |

---

### spec-writer

**Description:** Synthesize interview answers into a requirements specification. Produces a refined, structured spec from collected Q&A.
**Model:** sonnet
**Tools:** Read, Write
**Spawned by:** (none found)

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| `.dev/YYYY-MM-DD-interview-answers.md` | **Yes** | Collected Q&A from question-gatherer |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| Refined specification | Functional requirements, non-functional requirements, constraints, use cases |

---

### security-reviewer

**Description:** Review AL code for security vulnerabilities, permission issues, and data exposure risks.
**Model:** sonnet
**Tools:** Read
**Spawned by:** /review-develop

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| AL files to review | **Yes** | Via spawn prompt — list of file paths to read |
| Spawn prompt | **Yes** | Task context: what was implemented, any open questions |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| Security Review Findings | Text report returned to /develop-orchestrate; structured as Critical / High / Medium / Low |

---

### solution-architect

**Description:** Design BC-integrated solutions and create detailed implementation plans.
**Model:** opus
**Tools:** Read, Write, Glob, Grep
**Spawned by:** /fix, /plan

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| Dated requirements file | **Yes** (from /plan) · Inline prompt (from /fix) | From /interview (glob pattern match) — or inline analysis + fix approach when dispatched by /fix |
| `.dev/project-context.md` | No | Project memory (read FIRST if exists) |
| MCP tools | No | BC Intelligence, MS Docs, AL Dependency |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| Dated solution plan file | **Primary** — Architecture + implementation plan |
| `.dev/project-context.md` | Update with new patterns/objects learned |
| `.dev/session-log.md` | Append entry with summary of work done |

---

### support-researcher

**Description:** Research a BC support query using AL symbols, MS Docs, and BC Code History. Produces internal technical findings. Uses systematic, curated sources only (no web search/fetch).
**Model:** sonnet
**Tools:** MCP: bc-code-intelligence, MCP: microsoft-docs
**Spawned by:** /support-reply

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| `QUERY_TYPE` | **Yes** | `ticket`, `file`, or `freetext` — in dispatch prompt |
| `QUERY_CONTEXT` | **Yes** | The customer's question or symptom |
| `TICKET_FILE` | No | Path to ticket context file from `/ticket`, or `NONE` |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| Return block | Structured internal findings: root cause, evidence (AL symbols, MS Docs, BC history), workarounds, recommended resolution |

---

### support-reply-drafter

**Description:** Draft a customer-facing reply from internal BC support research findings. Pairs with support-researcher. Applies evidence requirements and tone constraints.
**Model:** sonnet
**Tools:** Write
**Spawned by:** /support-reply

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| `QUERY_TYPE` | **Yes** | `ticket`, `file`, or `freetext` — in dispatch prompt |
| `QUERY_CONTEXT` | **Yes** | Original customer question or symptom |
| `TICKET_FILE` | No | Path to ticket context file, or `NONE` |
| `RESEARCHER_FINDINGS` | **Yes** | Full structured output block from support-researcher |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| `.dev/<date>-support-<slug>.md` | **Primary** — Internal findings + draft customer reply |
| Return block | `FILE`, `QUERY_TYPE`, `BC_VERSION_SCOPE`, `SOURCES`, `SUMMARY` |

---

### ticket-context-writer

**Description:** Fetch a Freshdesk ticket via API, write .dev/\$(date +%Y-%m-%d)-ticket-ticket-context.md, download attachments, and detect inline images in HTML body. Follows canonical invocation pattern in knowledge/ticket-agent-invocation-pattern.md.
**Model:** haiku
**Tools:** Bash, Write
**Spawned by:** /ticket

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| `TICKET_ID` | **Yes** | Freshdesk ticket number (in dispatch prompt) |
| `FRESHDESK_API_KEY` | **Yes** | API key (from global settings via environment) |
| `FRESHDESK_DOMAIN` | **Yes** | Freshdesk subdomain (from global settings via environment) |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| `.dev/$(date +%Y-%m-%d)-ticket-ticket-context.md` | **Primary** — structured ticket brief with inline image list |
| `.dev/attachments/` | Attached files (downloaded with ticket context) |
| Return block | `TICKET_CONTEXT_WRITTEN`, `TICKET_ID`, `STATUS`, `PRIORITY`, `COMMENTS_COUNT`, `ATTACHMENTS`, `INLINE_IMAGES_COUNT` |

---

### corruption-recover

**Description:** Recover corrupted AL files flagged in `.dev/commit-integrity.log` using fallback strategies and learned patterns.
**Model:** sonnet
**Tools:** Write, Bash
**Spawned by:** /commit-recover

**Inputs:**

| Input | Required | Description |
| ------- | ---------- | ------------- |
| `REPO` | No | Inferred from working directory; not passed explicitly by /commit-recover |
| `CORRUPTION_LOG` | **Yes** | Path to `.dev/commit-integrity.log` with flagged files |
| `auto_fix` | No | If true, apply auto-fixes; if false, report findings only |

**Outputs:**

| Output | Description |
| -------- | ------------- |
| Fixed AL files | Recovered via fallback strategies (git restore, regex reconstruction, schema rebuild) |
| `.dev/$(date +%Y-%m-%d)-plugin-recover-report.md` | Recovery report with per-file strategy and status |

---

## Observations

> **Findings live in the health dossier, not in this map.** This map is
> documentation only — it describes the current agent roster. To find
> improvement suggestions (Trim, Remodel, Split, Inline, Align), run
> `/audit-plugin-health` and read the ranked dossier in `docs/health/`, then
> `/map-suggestions-verify` to turn accepted findings into a plan.
>
> History: in-map suggestions through 2026-06-01 were retired when findings
> converged on the health dossier (2026-06-02).
