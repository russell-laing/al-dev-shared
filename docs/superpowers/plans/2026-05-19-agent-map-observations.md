# Agent Map Observations: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement all actionable suggestions from the Observations section of `docs/al-dev-agent-map.md`: trim a stale tool grant, fix stale reviewer-team references, clarify dual-caller inputs, add I/O documentation to undocumented agents, fix commit-learn-verifier frontmatter, and split al-dev-commit-agent into two phase-specific agents.

**Architecture:** Pure documentation/YAML changes — no AL source code, no logic changes. The largest structural change is splitting `al-dev-commit-agent.md` into `al-dev-commit-agent-analysis.md` (model: sonnet) and `al-dev-commit-agent-execute.md` (model: haiku), then wiring the `/al-dev-commit` skill to dispatch the correct agent per phase. All other changes are text edits and I/O table additions.

**Tech Stack:** Markdown, YAML frontmatter, shell verification (`grep`, `wc -l`, `ls -la`)

---

## File Map

| Action | File |
|--------|------|
| Modify | `profile-al-dev-shared/agents/al-dev-explore.md` |
| Modify | `profile-al-dev-shared/agents/al-dev-security-reviewer.md` |
| Modify | `profile-al-dev-shared/agents/al-dev-performance-reviewer.md` |
| Modify | `profile-al-dev-shared/agents/al-dev-code-review.md` |
| Modify | `profile-al-dev-shared/agents/al-dev-expert-reviewer.md` |
| Modify | `profile-al-dev-shared/agents/al-dev-developer.md` |
| Modify | `profile-al-dev-shared/agents/al-dev-solution-architect.md` |
| Modify | `profile-al-dev-shared/agents/al-dev-release-notes-agent.md` |
| Modify | `profile-al-dev-shared/agents/al-dev-support-agent.md` |
| Modify | `profile-al-dev-shared/agents/commit-learn-verifier.md` |
| Modify | `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` |
| Create | `profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md` |
| Create | `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md` |
| Delete | `profile-al-dev-shared/agents/al-dev-commit-agent.md` |
| Modify | `docs/al-dev-agent-map.md` |

---

## Task 1: Structural fixes — trim tool grant and team-size references

Four small edits across four agent files. These are all about removing stale/wrong information with no behaviour change.

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-explore.md` (line 8)
- Modify: `profile-al-dev-shared/agents/al-dev-security-reviewer.md` (line 23)
- Modify: `profile-al-dev-shared/agents/al-dev-performance-reviewer.md` (line 121)
- Modify: `profile-al-dev-shared/agents/al-dev-code-review.md` (lines 3–8, 27)

- [ ] **Step 1: Remove Bash from al-dev-explore tools list**

In `profile-al-dev-shared/agents/al-dev-explore.md`, change line 8 from:
```yaml
tools: ["Read", "Glob", "Grep", "Bash"]
```
to:
```yaml
tools: ["Read", "Glob", "Grep"]
```

Rationale: the agent body contains no shell commands. Removing Bash enforces least-privilege and aligns the frontmatter with actual usage.

- [ ] **Step 2: Fix 4-reviewer team reference in al-dev-security-reviewer**

In `profile-al-dev-shared/agents/al-dev-security-reviewer.md`, change the Spawn Context paragraph:

Old text (line 23):
```
You are spawned as part of a 4-reviewer team (security, AL expert, performance, test coverage) to review implemented code in parallel. After independent review, you'll debate findings with other reviewers before the lead synthesizes results.
```

New text:
```
You are spawned as part of a 3-reviewer team (security, AL expert, performance) to review implemented code in parallel. After independent review, you'll debate findings with other reviewers before the lead synthesizes results.
```

- [ ] **Step 3: Remove stale test-coverage reference in al-dev-performance-reviewer**

In `profile-al-dev-shared/agents/al-dev-performance-reviewer.md`, change the last line of the file (line 121):

Old text:
```
- "This optimization might conflict with Test Coverage Reviewer's mocking requirement - propose compromise"
```

New text:
```
- "This optimization might conflict with AL Expert Reviewer's pattern requirement — propose compromise"
```

- [ ] **Step 4: Fix stale 4-specialist reference in al-dev-code-review**

In `profile-al-dev-shared/agents/al-dev-code-review.md`, make two changes:

**Change 1 — frontmatter description (lines 3–8):**

Old:
```yaml
description: >-
  General code review specialist — finds bugs, logic errors, and security
  issues with high signal-to-noise ratio. Use standalone or as part of
  the 4-specialist parallel review team alongside al-dev-security-reviewer,
  al-dev-expert-reviewer, al-dev-performance-reviewer, and
  al-dev-test-coverage-reviewer.
```

New:
```yaml
description: >-
  General code review specialist — finds bugs, logic errors, and security
  issues with high signal-to-noise ratio. Use standalone or as part of
  the 3-specialist parallel review team alongside al-dev-security-reviewer,
  al-dev-expert-reviewer, and al-dev-performance-reviewer.
```

**Change 2 — Spawn Context body (line 27):**

Old:
```
You may be spawned as part of a 4-reviewer team (security, expert patterns, performance, test coverage) or independently for standalone reviews. When part of a team, focus on general code quality — leave specialised concerns to other reviewers.
```

New:
```
You may be spawned as part of a 3-reviewer team (security, expert patterns, performance) or independently for standalone reviews. When part of a team, focus on general code quality — leave specialised concerns to other reviewers.
```

- [ ] **Step 5: Verify no stale references remain**

```bash
grep -rn "4-reviewer\|4-specialist\|test coverage\|Test Coverage\|al-dev-test-coverage-reviewer" \
  profile-al-dev-shared/agents/
```

Expected: no output (all stale references removed).

```bash
grep -n "tools:" profile-al-dev-shared/agents/al-dev-explore.md
```

Expected: `8:tools: ["Read", "Glob", "Grep"]`

- [ ] **Step 6: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-explore.md \
        profile-al-dev-shared/agents/al-dev-security-reviewer.md \
        profile-al-dev-shared/agents/al-dev-performance-reviewer.md \
        profile-al-dev-shared/agents/al-dev-code-review.md
git commit -m "$(cat <<'EOF'
♻️ refactor(agents): trim stale tool grants and fix reviewer team-size references

WHY: al-dev-explore declared Bash but its body uses no shell commands;
three reviewer agents referenced a non-existent al-dev-test-coverage-reviewer,
distorting their debate posture.

CHANGED COMPONENTS
- al-dev-explore.md [m] — remove Bash from tools list
- al-dev-security-reviewer.md [m] — 4-reviewer → 3-reviewer team
- al-dev-performance-reviewer.md [m] — remove Test Coverage Reviewer reference
- al-dev-code-review.md [m] — 4-specialist → 3-specialist; remove al-dev-test-coverage-reviewer
EOF
)"
```

---

## Task 2: Add I/O tables to reviewer agents

Four reviewer agents (security, performance, expert, code-review) have structured review processes but no formal Inputs/Outputs tables. Add them immediately after the `## Role` section in each file, before the `---` separator.

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-security-reviewer.md`
- Modify: `profile-al-dev-shared/agents/al-dev-performance-reviewer.md`
- Modify: `profile-al-dev-shared/agents/al-dev-expert-reviewer.md`
- Modify: `profile-al-dev-shared/agents/al-dev-code-review.md`

- [ ] **Step 1: Add I/O table to al-dev-security-reviewer**

In `profile-al-dev-shared/agents/al-dev-security-reviewer.md`, insert after the line:
```
Review AL code for security vulnerabilities, permission issues, and data exposure risks.
```
And before the `---` separator that follows it:

```markdown

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| AL files to review | **Yes** | Via spawn prompt — list of file paths to read |
| Spawn prompt | **Yes** | Task context: what was implemented, any open questions |

## Outputs

| Output | Description |
|--------|-------------|
| Security Review Findings | Text report returned to /al-dev-develop; structured as Critical / High / Medium / Low |
```

- [ ] **Step 2: Add I/O table to al-dev-performance-reviewer**

In `profile-al-dev-shared/agents/al-dev-performance-reviewer.md`, insert after the line:
```
Review AL code for performance issues, inefficient queries, and resource consumption problems.
```
And before the `---` separator that follows it:

```markdown

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| AL files to review | **Yes** | Via spawn prompt — list of file paths to read |
| Spawn prompt | **Yes** | Task context: what was implemented |

## Outputs

| Output | Description |
|--------|-------------|
| Performance Review Findings | Text report returned to /al-dev-develop; structured as Critical / High / Optimization Opportunities |
```

- [ ] **Step 3: Add I/O table to al-dev-expert-reviewer**

In `profile-al-dev-shared/agents/al-dev-expert-reviewer.md`, insert after the line:
```
Review AL code for adherence to AL/BC best practices, naming conventions, and design patterns.
```
And before the `---` separator that follows it:

```markdown

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| AL files to review | **Yes** | Via spawn prompt — list of file paths to read |
| Spawn prompt | **Yes** | Task context: what was implemented, any open questions |

## Outputs

| Output | Description |
|--------|-------------|
| AL Best Practices Review Findings | Text report returned to /al-dev-develop; structured as Critical / High / Minor Issues |
```

- [ ] **Step 4: Add I/O table to al-dev-code-review**

In `profile-al-dev-shared/agents/al-dev-code-review.md`, insert after the line:
```
Review code changes and surface only genuine issues: bugs, security vulnerabilities, logic errors, and significant inefficiencies. Never comment on style, formatting, or trivial matters.
```
And before the `---` separator that follows it:

```markdown

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Files to review | **Yes** | Via spawn prompt — file paths or diff scope |
| Spawn prompt | **Yes** | Task context: scope, other active reviewers, any open questions |

## Outputs

| Output | Description |
|--------|-------------|
| Code Review Findings | Text report returned to calling skill; structured as Critical / High / Medium / Low |
```

- [ ] **Step 5: Verify tables were inserted**

```bash
for f in al-dev-security-reviewer al-dev-performance-reviewer al-dev-expert-reviewer al-dev-code-review; do
  count=$(grep -c "^## Inputs" "profile-al-dev-shared/agents/$f.md")
  echo "$f: $count Inputs sections"
done
```

Expected: each file reports `1 Inputs sections`.

- [ ] **Step 6: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-security-reviewer.md \
        profile-al-dev-shared/agents/al-dev-performance-reviewer.md \
        profile-al-dev-shared/agents/al-dev-expert-reviewer.md \
        profile-al-dev-shared/agents/al-dev-code-review.md
git commit -m "$(cat <<'EOF'
📝 docs(agents): add Inputs/Outputs tables to reviewer agents

WHY: The agent map flagged these four reviewer agents as having no I/O
documentation, making it impossible to understand what they consume and
produce without reading the full body.

CHANGED COMPONENTS
- al-dev-security-reviewer.md [m] — add Inputs/Outputs tables
- al-dev-performance-reviewer.md [m] — add Inputs/Outputs tables
- al-dev-expert-reviewer.md [m] — add Inputs/Outputs tables
- al-dev-code-review.md [m] — add Inputs/Outputs tables
EOF
)"
```

---

## Task 3: Dual-caller input alignment for developer and architect agents

Both agents serve two callers with different input conventions. The Inputs table incorrectly marks file-based inputs as unconditionally Required, which is only true for the `/al-dev-develop`/`/al-dev-plan` caller path. The `/al-dev-fix` caller passes an inline prompt instead.

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-developer.md` (lines 22–23)
- Modify: `profile-al-dev-shared/agents/al-dev-solution-architect.md` (lines 26–27)

- [ ] **Step 1: Update al-dev-developer Inputs table**

In `profile-al-dev-shared/agents/al-dev-developer.md`, replace the Inputs table:

Old:
```markdown
| Input | Required | Description |
|-------|----------|-------------|
| `.dev/*-al-dev-plan-solution-plan.md` | Yes | Implementation plan |
| `.dev/*-al-dev-test-test-plan.md` | Yes | Test specs from test-engineer |
| `.dev/project-context.md` | No | Project memory (saves exploration) |
| `.dev/*-al-dev-develop-code-review.md` | No | Review findings when iterating |
```

New:
```markdown
| Input | Required | Description |
|-------|----------|-------------|
| `.dev/*-al-dev-plan-solution-plan.md` | **Yes** (from /al-dev-develop) · Inline prompt (from /al-dev-fix) | Implementation plan |
| `.dev/*-al-dev-test-test-plan.md` | **Yes** (from /al-dev-develop) · Not used (from /al-dev-fix) | Test specs from test-engineer |
| `.dev/project-context.md` | No | Project memory (saves exploration) |
| `.dev/*-al-dev-develop-code-review.md` | No | Review findings when iterating |
```

- [ ] **Step 2: Update al-dev-solution-architect Inputs table**

In `profile-al-dev-shared/agents/al-dev-solution-architect.md`, replace the Inputs table:

Old:
```markdown
| Input | Required | Description |
|-------|----------|-------------|
| Dated requirements file | **Yes** | From /interview (glob pattern match) |
| `.dev/project-context.md` | No | Project memory (read FIRST if exists) |
| MCP tools | No | BC Intelligence, MS Docs, AL Dependency |
```

New:
```markdown
| Input | Required | Description |
|-------|----------|-------------|
| Dated requirements file | **Yes** (from /al-dev-plan) · Inline prompt (from /al-dev-fix) | From /interview (glob pattern match) — or inline analysis + fix approach when dispatched by /al-dev-fix |
| `.dev/project-context.md` | No | Project memory (read FIRST if exists) |
| MCP tools | No | BC Intelligence, MS Docs, AL Dependency |
```

- [ ] **Step 3: Verify updates**

```bash
grep -A4 "## Inputs" profile-al-dev-shared/agents/al-dev-developer.md | grep "Inline prompt"
grep -A4 "## Inputs" profile-al-dev-shared/agents/al-dev-solution-architect.md | grep "Inline prompt"
```

Expected: one match per file.

- [ ] **Step 4: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-developer.md \
        profile-al-dev-shared/agents/al-dev-solution-architect.md
git commit -m "$(cat <<'EOF'
📝 docs(agents): clarify dual-caller inputs for developer and architect agents

WHY: /al-dev-fix dispatches both agents with inline prompts, not file-based
inputs. The Required label only applies to the /al-dev-develop and
/al-dev-plan caller paths; the mismatch was misleading future callers.

CHANGED COMPONENTS
- al-dev-developer.md [m] — note inline-prompt path from /al-dev-fix
- al-dev-solution-architect.md [m] — note inline-prompt path from /al-dev-fix
EOF
)"
```

---

## Task 4: I/O tables for release-notes-agent and support-agent

Both agents have detailed step-by-step bodies that imply their inputs and outputs clearly, but lack formal tables at the top.

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-release-notes-agent.md`
- Modify: `profile-al-dev-shared/agents/al-dev-support-agent.md`

- [ ] **Step 1: Verify al-dev-release-notes-agent MCP fix (ebd0144)**

The Observations note that ebd0144 claimed to add MCP tools to the frontmatter. Confirm:

```bash
head -12 profile-al-dev-shared/agents/al-dev-release-notes-agent.md
```

Expected: both `mcp__plugin_profile-claude-al-dev_al-mcp-server` and
`mcp__plugin_profile-claude-al-dev_bc-code-intelligence-mcp` are in the tools list.

If they are present, the suggestion is resolved. Continue to Step 2.
If they are absent, add them to the tools array before continuing.

- [ ] **Step 2: Add Inputs/Outputs tables to al-dev-release-notes-agent**

In `profile-al-dev-shared/agents/al-dev-release-notes-agent.md`, insert after the opening paragraph (after `All inputs are provided in the dispatch prompt:` bullet list) and before `---\n\n## Phase: extract-changes`, add:

```markdown

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `START_HASH` | **Yes** | Earlier commit (exclusive lower bound) |
| `END_HASH` | **Yes** | Later commit (inclusive upper bound) |
| `RELEASE_TYPE` | **Yes** | `uat` or `prod` |
| `VERSION` | No | Label (e.g. `v2.1.0`); short hash used if omitted |
| `PROJECT_CONTEXT` | No | Content of `.dev/project-context.md` if it exists |

## Outputs

| Output | Description |
|--------|-------------|
| `.dev/$(date +%Y-%m-%d)-al-dev-release-notes-<VERSION>.md` | **Primary** — formatted release notes file |
| Return block | `RELEASE_NOTES_WRITTEN`, `VERSION`, `CHANGES`, `SUMMARY`, `EXCLUDED`, `DIAGRAMS`, `AMBIGUOUS` |

```

- [ ] **Step 3: Add Inputs/Outputs tables to al-dev-support-agent**

In `profile-al-dev-shared/agents/al-dev-support-agent.md`, insert after the opening paragraph (after `Dispatched by \`/al-dev-support\`.`) and before `## Step 1 — Parse Prompt and Classify Query`:

```markdown

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `QUERY_TYPE` | **Yes** | `ticket`, `file`, or `freetext` — in dispatch prompt |
| `QUERY_CONTEXT` | **Yes** | The customer's question or symptom |
| `TICKET_FILE` | No | Path to ticket context file from `/al-dev-ticket`, or `NONE` |

## Outputs

| Output | Description |
|--------|-------------|
| `.dev/<date>-support-<slug>.md` | **Primary** — Internal findings + draft customer reply |
| Return block | `FILE`, `QUERY_TYPE`, `BC_VERSION_SCOPE`, `SOURCES`, `SUMMARY` |

```

- [ ] **Step 4: Verify**

```bash
grep -c "^## Inputs" \
  profile-al-dev-shared/agents/al-dev-release-notes-agent.md \
  profile-al-dev-shared/agents/al-dev-support-agent.md
```

Expected: each file reports `1`.

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-release-notes-agent.md \
        profile-al-dev-shared/agents/al-dev-support-agent.md
git commit -m "$(cat <<'EOF'
📝 docs(agents): add Inputs/Outputs tables to release-notes and support agents

WHY: Both agents had detailed step-by-step bodies but no formal I/O tables,
making caller contracts invisible to the agent map review.

CHANGED COMPONENTS
- al-dev-release-notes-agent.md [m] — add Inputs/Outputs tables
- al-dev-support-agent.md [m] — add Inputs/Outputs tables
EOF
)"
```

---

## Task 5: Fix commit-learn-verifier frontmatter and add Outputs table

The agent file has no `model` or `tools` in its frontmatter. The agent map catalog shows `(not specified)` for both. The body uses Bash (git commands, sed, validation), Read (for file inspection), and Write (to update learnings.md on success).

**Files:**
- Modify: `profile-al-dev-shared/agents/commit-learn-verifier.md`

- [ ] **Step 1: Add model and tools to frontmatter**

In `profile-al-dev-shared/agents/commit-learn-verifier.md`, replace the frontmatter:

Old:
```yaml
---
description: Analyze file corruption incidents, propose and execute recovery strategies with fallback methods
---
```

New:
```yaml
---
description: Analyze file corruption incidents, propose and execute recovery strategies with fallback methods
model: sonnet
tools: ["Bash", "Read", "Write"]
---
```

Rationale: sonnet for the reasoning-heavy hypothesis formation; Bash for git/shell recovery commands; Read for file inspection; Write for updating learnings.md.

- [ ] **Step 2: Add Outputs table after the Input section**

In `profile-al-dev-shared/agents/commit-learn-verifier.md`, after the `## Input` section (after the last bullet in the input list) and before `## Analysis Process`, insert:

```markdown

## Outputs

| Output | Description |
|--------|-------------|
| Analysis report (text) | Root cause hypothesis, pattern match result, fallback strategy, recovery result |
| Updated `learnings.md` | Recovery outcome recorded (success or failure); new guardrails if applicable |
```

- [ ] **Step 3: Verify**

```bash
head -6 profile-al-dev-shared/agents/commit-learn-verifier.md
grep -c "^## Outputs" profile-al-dev-shared/agents/commit-learn-verifier.md
```

Expected: frontmatter shows `model: sonnet` and `tools:`; Outputs count is `1`.

- [ ] **Step 4: Commit**

```bash
git add profile-al-dev-shared/agents/commit-learn-verifier.md
git commit -m "$(cat <<'EOF'
📝 docs(agents): add model, tools and Outputs table to commit-learn-verifier

WHY: The agent had no frontmatter model or tools, leaving the harness to
infer defaults; outputs were implied by the body format but never formally
declared.

CHANGED COMPONENTS
- commit-learn-verifier.md [m] — add model/tools frontmatter, add Outputs table
EOF
)"
```

---

## Task 6: Create al-dev-commit-agent-analysis.md

Extract the read-only analysis phase from `al-dev-commit-agent.md` into a dedicated sonnet agent. The analysis phase runs Steps 1–7 of the current file.

**Files:**
- Create: `profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md`

- [ ] **Step 1: Create the new file**

Create `profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md` with the following content:

The file has three parts:
1. **New frontmatter + header + I/O tables** (write this exactly):

```markdown
---
description: >-
  Git commit analysis agent. Reads staged diffs, builds per-file manifests,
  proposes commit groups, and drafts commit messages. Dispatched by
  al-dev-commit (analysis phase). Read-only — never modifies files.
model: sonnet
tools: ["Bash", "Read", "Glob"]
---

# Agent: al-dev-commit-agent (Analysis Phase)

Read-only analysis phase of the commit workflow. Dispatched by
`/al-dev-commit` with phase-specific instructions.

**Do not modify any files in this phase.**

All inputs arrive in the dispatch prompt:

- `PROJECT_CONTEXT` — scopes, object ID prefix, naming patterns
- `FD_TICKET` — Freshdesk ticket number or empty

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `PROJECT_CONTEXT` and `FD_TICKET` from /al-dev-commit |
| Staged git index | **Yes** | Read via `git diff --cached` commands |

## Outputs

| Output | Description |
|--------|-------------|
| `MANIFESTS` block | Per-file change summary (object IDs, added/removed fields and procedures) |
| `PROPOSED_GROUPS` block | Atomic commit group proposals with draft messages |
| `DELETIONS` block | Staged deletions for the user audit gate |
| `WARNINGS` block | Validation issues and advisory notices |

---

```

2. **Phase: analysis body**: copy the content of `al-dev-commit-agent.md` from the line `## Phase: analysis` through to the end of `### Step 7 — Return analysis output` (the closing ` ``` ` block of the PROPOSED_GROUPS output). This is the content between `---\n\n## Phase: analysis` and the `---\n\n## Phase: execute` boundary in the source file.

Run this to extract and verify the boundary:
```bash
grep -n "## Phase:" profile-al-dev-shared/agents/al-dev-commit-agent.md
```
Expected output: two lines showing the line numbers of `## Phase: analysis` and `## Phase: execute`.

- [ ] **Step 2: Verify the file was created correctly**

```bash
ls -la profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md
wc -l profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md
grep -c "^## Phase:" profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md
```

Expected: file exists and is non-empty; `grep` output is `1` (only the analysis phase, not execute).

```bash
grep "model:" profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md
```

Expected: `model: sonnet`

- [ ] **Step 3: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md
git commit -m "$(cat <<'EOF'
✨ feat(agents): extract al-dev-commit-agent-analysis from commit agent

WHY: Split the unified commit agent into phase-specific agents to enforce
the read-only contract structurally and enable model right-sizing (sonnet
for semantic analysis, haiku for mechanical execution).

CHANGED COMPONENTS
- al-dev-commit-agent-analysis.md [+] — analysis phase with model: sonnet
EOF
)"
```

---

## Task 7: Create al-dev-commit-agent-execute.md

Extract the write-heavy execute phase from `al-dev-commit-agent.md` into a dedicated haiku agent.

**Files:**
- Create: `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md`

- [ ] **Step 1: Create the new file**

Create `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md` with the following content:

**New frontmatter + header + I/O tables** (write this exactly):

```markdown
---
description: >-
  Git commit execution agent. Runs lint, validates OOXML integrity, and
  executes git commits from an approved plan. Dispatched by al-dev-commit
  (execute phase). Never writes or edits source files directly — all fixes
  go through Bash.
model: haiku
tools: ["Bash", "Read", "Glob"]
---

# Agent: al-dev-commit-agent (Execute Phase)

Execute phase of the commit workflow. Dispatched by `/al-dev-commit`
with an approved commit plan after user confirmation.

All inputs arrive in the dispatch prompt:

- `APPROVED_PLAN` — the full approved group + message list from the analysis phase

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `APPROVED_PLAN` — approved groups and messages from the analysis phase |

## Outputs

| Output | Description |
|--------|-------------|
| `COMMITS` block | SHA and message for each committed group |
| `SKIPPED` | Number of skipped groups |
| `LINT_FIXES` | Files re-staged after lint (or `NONE`) |
| `HOOK_FAILURES` | Raw hook output for any failed groups (or `NONE`) |
| `STRIPPED_ATTRIBUTIONS` | Removed AI attribution lines (or `NONE`) |

> ⚠️ **CRITICAL: Never use Write or Edit on staged source files.**
>
> All fixes must go through Bash (ruff, perl).
> Reading file content into context then writing it back WILL
> collapse newlines and corrupt the file. If a fix cannot be
> made via Bash, record it as HOOK_FAILURE and stop.

---

```

Then append the **Phase: execute body**: copy the content of `al-dev-commit-agent.md` from `## Phase: execute` through to the end of the file (the closing ` ``` ` block of the Step 3 return format).

Run to find the start line:
```bash
grep -n "## Phase: execute" profile-al-dev-shared/agents/al-dev-commit-agent.md
```

- [ ] **Step 2: Verify the file was created correctly**

```bash
ls -la profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
wc -l profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
grep -c "^## Phase:" profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
```

Expected: file exists and is non-empty; `grep` output is `1` (only execute phase).

```bash
grep "model:" profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
```

Expected: `model: haiku`

- [ ] **Step 3: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
git commit -m "$(cat <<'EOF'
✨ feat(agents): extract al-dev-commit-agent-execute from commit agent

WHY: Mechanical bash execution does not require sonnet-level reasoning.
Haiku reduces cost and latency for the execution phase while the structural
split enforces the no-file-write constraint.

CHANGED COMPONENTS
- al-dev-commit-agent-execute.md [+] — execute phase with model: haiku
EOF
)"
```

---

## Task 8: Wire /al-dev-commit skill to new agents + delete old agent

Update the skill to dispatch `al-dev-commit-agent-analysis` in Step 6 and `al-dev-commit-agent-execute` in Step 10, then delete the now-obsolete unified agent file.

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` (lines 156, 311)
- Delete: `profile-al-dev-shared/agents/al-dev-commit-agent.md`

- [ ] **Step 1: Update Step 6 dispatch in the skill**

In `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`, change the agent reference in the Step 6 agent tool block:

Old:
```
  agent: al-dev-shared:al-dev-commit-agent
  description: "Commit analysis: analyse staged changes"
```

New:
```
  agent: al-dev-shared:al-dev-commit-agent-analysis
  description: "Commit analysis: analyse staged changes"
```

- [ ] **Step 2: Update Step 10 dispatch in the skill**

In the same file, change the agent reference in the Step 10 agent tool block:

Old:
```
  agent: al-dev-shared:al-dev-commit-agent
  description: "Commit execution: [N] commits"
```

New:
```
  agent: al-dev-shared:al-dev-commit-agent-execute
  description: "Commit execution: [N] commits"
```

- [ ] **Step 3: Verify both references are updated**

```bash
grep -n "al-dev-commit-agent" profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```

Expected: two lines — one showing `al-dev-commit-agent-analysis` and one showing `al-dev-commit-agent-execute`. No bare `al-dev-commit-agent` reference.

- [ ] **Step 4: Delete the obsolete unified agent file**

```bash
git rm profile-al-dev-shared/agents/al-dev-commit-agent.md
```

- [ ] **Step 5: Verify deletion**

```bash
ls profile-al-dev-shared/agents/al-dev-commit-agent.md 2>&1
```

Expected: `No such file or directory`

```bash
ls profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md \
   profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
```

Expected: both files exist.

- [ ] **Step 6: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-commit/SKILL.md
git commit -m "$(cat <<'EOF'
♻️ refactor(skills): wire al-dev-commit to phase-specific agent files

WHY: Complete the commit-agent split — skill now dispatches
al-dev-commit-agent-analysis (sonnet) for Step 6 and
al-dev-commit-agent-execute (haiku) for Step 10. Old unified agent removed.

CHANGED COMPONENTS
- SKILL.md [m] — update Step 6 and Step 10 agent dispatch references
- al-dev-commit-agent.md [-] — replaced by phase-specific agents
EOF
)"
```

---

## Task 9: Sync docs/al-dev-agent-map.md

Update the agent map to reflect all changes made in Tasks 1–8. This is a single comprehensive sync.

**Files:**
- Modify: `docs/al-dev-agent-map.md`

- [ ] **Step 1: Update Layer 1 catalog table**

Replace the `al-dev-commit-agent` row:
```
| al-dev-commit-agent | haiku | Bash, Read, Glob | /al-dev-commit |
```

With two rows:
```
| al-dev-commit-agent-analysis | sonnet | Bash, Read, Glob | /al-dev-commit |
| al-dev-commit-agent-execute | haiku | Bash, Read, Glob | /al-dev-commit |
```

Also update the `al-dev-explore` tools column from `Read, Glob, Grep, Bash` to `Read, Glob, Grep`.

- [ ] **Step 2: Replace al-dev-commit-agent per-agent profile**

Remove the `### al-dev-commit-agent` section (currently showing "Not documented" for inputs/outputs) and replace it with two new sections:

```markdown
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
```

- [ ] **Step 3: Update al-dev-explore profile**

In the `### al-dev-explore` section, update the Tools line from:
```
**Tools:** Read, Glob, Grep, Bash
```
to:
```
**Tools:** Read, Glob, Grep
```

Also update the "Not documented" inputs/outputs to reflect what the agent file already documents:

```markdown
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
```

- [ ] **Step 4: Update reviewer agent profiles with I/O tables**

For each of `al-dev-security-reviewer`, `al-dev-performance-reviewer`, `al-dev-expert-reviewer`, `al-dev-code-review`, replace the `**Inputs:** Not documented` / `**Outputs:** Not documented` lines with the tables added in Task 2. (Use the exact table content from Task 2 Steps 1–4.)

- [ ] **Step 5: Update release-notes, support, script-engineer, ticket-agent, and verifier profiles**

For `### al-dev-release-notes-agent`: replace Not documented with the I/O tables from Task 4 Step 2.

For `### al-dev-support-agent`: replace Not documented with the I/O tables from Task 4 Step 3.

For `### al-dev-script-engineer`: replace Not documented with:

```markdown
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
```

For `### al-dev-ticket-agent`: replace Not documented with:

```markdown
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
```

For `### commit-learn-verifier`: update Model and Tools (now specified), replace Not documented outputs with:

```markdown
**Model:** sonnet
**Tools:** Bash, Read, Write

**Outputs:**

| Output | Description |
|--------|-------------|
| Analysis report (text) | Root cause hypothesis, pattern match, fallback strategy, recovery result |
| Updated `learnings.md` | Recovery outcome recorded (success or failure) with new guardrails if applicable |
```

- [ ] **Step 6: Update Observations section**

Update the Observations section header date and mark resolved items:

Replace the header:
```
> Generated by /analyze-agent-design on 2026-05-19.
> Run /review-agent-map first if the agent list has changed since this was written.
```

With:
```
> Generated by /analyze-agent-design on 2026-05-19.
> Observations implemented on 2026-05-19. Run /review-agent-map to regenerate.
```

Also mark the "Align: al-dev-release-notes-agent" suggestion as resolved since ebd0144 already fixed the MCP frontmatter.

- [ ] **Step 7: Verify the map was updated**

```bash
grep -c "al-dev-commit-agent-analysis\|al-dev-commit-agent-execute" docs/al-dev-agent-map.md
```

Expected: at least 4 (catalog row + spawned-by + profile heading + description).

```bash
grep "al-dev-commit-agent |" docs/al-dev-agent-map.md
```

Expected: no output (old unified agent row removed from catalog).

```bash
grep "Not documented" docs/al-dev-agent-map.md
```

Expected: no output (all agents now have I/O documentation).

- [ ] **Step 8: Commit**

```bash
git add docs/al-dev-agent-map.md
git commit -m "$(cat <<'EOF'
📝 docs(agent-map): sync all Task 1–8 changes to agent map

WHY: Agent map was last updated 2026-05-19 before the split and alignment
changes; this commit brings it into sync with all implemented observations.

CHANGED COMPONENTS
- al-dev-agent-map.md [m] — split commit agent catalog/profiles, update
  all I/O tables, fix explore tools, mark observations implemented
EOF
)"
```

---

## Verification Checklist (post all tasks)

Run these checks after completing all tasks to confirm nothing was missed:

```bash
# 1. No stale reviewer team references
grep -rn "4-reviewer\|4-specialist\|test coverage\|Test Coverage\|al-dev-test-coverage-reviewer" \
  profile-al-dev-shared/agents/ && echo "FAIL" || echo "PASS"

# 2. Both new commit agents exist, old one deleted
ls profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md \
   profile-al-dev-shared/agents/al-dev-commit-agent-execute.md && echo "PASS"
ls profile-al-dev-shared/agents/al-dev-commit-agent.md 2>&1 | grep "No such" && echo "PASS"

# 3. Skill uses new agent names
grep "al-dev-commit-agent-analysis\|al-dev-commit-agent-execute" \
  profile-al-dev-shared/skills/al-dev-commit/SKILL.md | wc -l | grep -q "2" && echo "PASS"

# 4. No bare al-dev-commit-agent reference in skill
grep -v "analysis\|execute" profile-al-dev-shared/skills/al-dev-commit/SKILL.md | \
  grep "al-dev-commit-agent" && echo "FAIL" || echo "PASS"

# 5. All agent files have I/O documentation
for f in al-dev-security-reviewer al-dev-performance-reviewer al-dev-expert-reviewer \
         al-dev-code-review al-dev-release-notes-agent al-dev-support-agent \
         commit-learn-verifier; do
  count=$(grep -c "^## Inputs\|^## Outputs\|\*\*Inputs:\*\*\|\*\*Outputs:\*\*" \
    "profile-al-dev-shared/agents/$f.md" 2>/dev/null || echo 0)
  echo "$f: $count I/O markers"
done

# 6. al-dev-explore has no Bash in tools
grep "tools:" profile-al-dev-shared/agents/al-dev-explore.md | grep -v "Bash" && echo "PASS"

# 7. commit-learn-verifier has model and tools
grep "^model:\|^tools:" profile-al-dev-shared/agents/commit-learn-verifier.md
```
