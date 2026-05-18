# AL Dev Agent Map

**Last updated:** 2026-05-18

## Layer 1: Agent Catalog

| Agent | Model | Tools | Spawned by |
|-------|-------|-------|------------|
| al-dev-code-review | sonnet | Read, Glob, Grep | (none found) |
| al-dev-commit-agent | haiku | Bash, Read, Glob | /al-dev-commit |
| al-dev-developer | sonnet | Read, Write, Edit, Glob, Grep, Bash | /al-dev-develop, /al-dev-fix |
| al-dev-diagnostics-fixer | sonnet | Read, Edit, Glob, Grep, Bash | /al-dev-lint, /al-dev-develop |
| al-dev-docs-writer | sonnet | Read, Write, Glob, Grep, Bash | /al-dev-document |
| al-dev-expert-reviewer | sonnet | Read, Grep, Glob | /al-dev-develop |
| al-dev-explore | sonnet | Read, Glob, Grep, Bash | (none found — skill uses built-in Explore type) |
| al-dev-interview | sonnet | Read, Write, AskUserQuestion | /al-dev-interview |
| al-dev-performance-reviewer | sonnet | Read, Grep, Glob | /al-dev-develop |
| al-dev-release-notes-agent | sonnet | Bash, Write, Read, Glob | /al-dev-release-notes |
| al-dev-script-engineer | sonnet | Read, Write, Edit, Glob, Grep, Bash | (none found) |
| al-dev-security-reviewer | sonnet | Read, Grep, Glob | /al-dev-develop |
| al-dev-solution-architect | opus | Read, Write, Glob, Grep, mcp:bc-code-intelligence, mcp:microsoft-docs, mcp:al-mcp-server | /al-dev-plan, /al-dev-fix |
| al-dev-support-agent | sonnet | WebSearch, WebFetch, Bash, Write, Read, mcp:al-mcp-server, mcp:microsoft-docs | /al-dev-support |
| al-dev-ticket-agent | haiku | Bash, Write | /al-dev-ticket, /al-dev-support |
| commit-learn-verifier | (not specified) | (not specified) | /commit-learn |

---

## Layer 2: Per-Agent Profiles

### al-dev-code-review

**Description:** General code review specialist — finds bugs, logic errors, and security issues with high signal-to-noise ratio.
**Model:** sonnet
**Tools:** Read, Glob, Grep
**Spawned by:** (none found in skill files)
**Inputs:** Not documented
**Outputs:** Not documented

---

### al-dev-commit-agent

**Description:** Git commit workflow agent.
**Model:** haiku
**Tools:** Bash, Read, Glob
**Spawned by:** /al-dev-commit
**Inputs:** Not documented
**Outputs:** Not documented

---

### al-dev-developer

**Description:** Implement AL code following an implementation plan.
**Model:** sonnet
**Tools:** Read, Write, Edit, Glob, Grep, Bash
**Spawned by:** /al-dev-develop, /al-dev-fix

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `.dev/*-al-dev-plan-solution-plan.md` | Yes | Implementation plan |
| `.dev/*-al-dev-test-test-plan.md` | Yes | Test specs from test-engineer |
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
**Inputs:** Not documented
**Outputs:** Not documented

---

### al-dev-explore

**Description:** Fast codebase exploration — finds files by pattern, searches for symbols, answers structural questions about how code is organized.
**Model:** sonnet
**Tools:** Read, Glob, Grep, Bash
**Spawned by:** (none found — the `/al-dev-explore` skill dispatches a built-in `Explore` subagent type, not this agent file directly)
**Inputs:** Not documented
**Outputs:** Not documented

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
**Inputs:** Not documented
**Outputs:** Not documented

---

### al-dev-release-notes-agent

**Description:** Run git diff analysis between two hashes, research AL object context, and write .dev/release-notes-\<version\>.md.
**Model:** sonnet
**Tools:** Bash, Write, Read, Glob
**Spawned by:** /al-dev-release-notes
**Inputs:** Not documented
**Outputs:** Not documented

---

### al-dev-script-engineer

**Description:** Write, validate, and run scripts for AL development and documentation workflows.
**Model:** sonnet
**Tools:** Read, Write, Edit, Glob, Grep, Bash
**Spawned by:** (none found in skill files)
**Inputs:** Not documented
**Outputs:** Not documented

---

### al-dev-security-reviewer

**Description:** Review AL code for security vulnerabilities, permission issues, and data exposure risks.
**Model:** sonnet
**Tools:** Read, Grep, Glob
**Spawned by:** /al-dev-develop
**Inputs:** Not documented
**Outputs:** Not documented

---

### al-dev-solution-architect

**Description:** Design BC-integrated solutions and create detailed implementation plans.
**Model:** opus
**Tools:** Read, Write, Glob, Grep, mcp:bc-code-intelligence, mcp:microsoft-docs, mcp:al-mcp-server
**Spawned by:** /al-dev-plan, /al-dev-fix

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| Dated requirements file | **Yes** | From /interview (glob pattern match) |
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
**Inputs:** Not documented
**Outputs:** Not documented

---

### al-dev-ticket-agent

**Description:** Fetch a Freshdesk ticket via API, write .dev/\$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md, and optionally download attachments.
**Model:** haiku
**Tools:** Bash, Write
**Spawned by:** /al-dev-ticket, /al-dev-support
**Inputs:** Not documented
**Outputs:** Not documented

---

### commit-learn-verifier

**Description:** Analyze file corruption incidents, propose and execute recovery strategies with fallback methods.
**Model:** Not specified in frontmatter
**Tools:** Not specified in frontmatter
**Spawned by:** /commit-learn

**Inputs:**

- **File path:** the corrupted file
- **Baseline/current line count:** what changed
- **Git history:** last 3–5 commits showing what edits were made
- **Learnings.md:** current known patterns and strategies
- **Incident log entry:** timestamp, error type (CORRUPTION/SYNTAX_ERROR)

**Outputs:** Not documented

---

## Observations

> Run /review-agent-map first if the agent list has changed before running
> /analyze-agent-design.

### Inline candidates

> Detected by /review-agent-map on 2026-05-18.

Note: No agent met the "minimal body" signal (< 10 lines after frontmatter) — the smallest body found was al-dev-explore at 33 lines. All candidates below scored on single caller + no I/O docs only. Inlining any of them would add 114–486 lines to the calling skill, so treat these as documentation gaps to fix (add Inputs/Outputs) rather than immediate inline targets.

**Inline: al-dev-commit-agent**
Signals: single caller (✓), minimal body (✗), no inputs/outputs docs (✓).
Spawned by: /al-dev-commit. Body: 486 lines.
Suggestion: Add Inputs/Outputs documentation to the agent file rather than inlining — body is too large to absorb.
Trade-off: Documentation fix is low-risk; inlining would bloat /al-dev-commit significantly.

**Inline: al-dev-expert-reviewer**
Signals: single caller (✓), minimal body (✗), no inputs/outputs docs (✓).
Spawned by: /al-dev-develop. Body: 127 lines.
Suggestion: Add Inputs/Outputs documentation to the agent file rather than inlining.
Trade-off: The three reviewer agents (expert, performance, security) share the same caller and could theoretically be merged into one, but that is a Split/Merge concern for /analyze-agent-design.

**Inline: al-dev-performance-reviewer**
Signals: single caller (✓), minimal body (✗), no inputs/outputs docs (✓).
Spawned by: /al-dev-develop. Body: 114 lines.
Suggestion: Add Inputs/Outputs documentation to the agent file rather than inlining.
Trade-off: Same as al-dev-expert-reviewer above.

**Inline: al-dev-release-notes-agent**
Signals: single caller (✓), minimal body (✗), no inputs/outputs docs (✓).
Spawned by: /al-dev-release-notes. Body: 225 lines.
Suggestion: Add Inputs/Outputs documentation to the agent file rather than inlining.
Trade-off: 225-line body is too large to absorb; document the contract instead.

**Inline: al-dev-security-reviewer**
Signals: single caller (✓), minimal body (✗), no inputs/outputs docs (✓).
Spawned by: /al-dev-develop. Body: 159 lines.
Suggestion: Add Inputs/Outputs documentation to the agent file rather than inlining.
Trade-off: Same as al-dev-expert-reviewer above.

**Inline: al-dev-support-agent**
Signals: single caller (✓), minimal body (✗), no inputs/outputs docs (✓).
Spawned by: /al-dev-support. Body: 175 lines.
Suggestion: Add Inputs/Outputs documentation to the agent file rather than inlining.
Trade-off: 175-line body is too large to absorb; document the contract instead.
