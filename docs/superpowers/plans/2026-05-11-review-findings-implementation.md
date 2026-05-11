# Review Findings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply all HIGH and MEDIUM action items from `.dev/2026-05-11-al-dev-review-findings.md` to `AGENTS.md` and `CLAUDE.md`, and apply the LOW item to the `al-dev-session-analyst` agent.

**Architecture:** Four new convention sections are appended to both `AGENTS.md` and `CLAUDE.md` (they mirror each other — both are project-instructions files for their respective harnesses). The session-analyst agent gets a supplemental instruction for subagent-heavy sessions.

**Tech Stack:** Markdown only — no code, no tests.

---

## File Map

| File | Action | Responsible for |
|---|---|---|
| `AGENTS.md` | Append 4 sections | Copilot CLI project conventions |
| `CLAUDE.md` | Append 4 sections | Claude Code project conventions (mirror) |
| `~/.copilot/installed-plugins/copilot-configs/copilot-al-dev/agents/al-dev-session-analyst.md` | Edit analysis step | Git-log supplement for subagent sessions |

---

### Task 1: Add Quality Review Conventions to AGENTS.md

**Files:**
- Modify: `AGENTS.md` (append after the Harness Mapping section)

- [ ] **Step 1: Append Quality Review Conventions section**

Add to the end of `AGENTS.md`:

```markdown

---

## Quality Review Conventions

**Iterative task reviews (per-task scope):**
When a quality reviewer finds a bug class in one task, it MUST add that class
to an explicit "watch list" carried into every subsequent task review in the
same session. Append to the review prompt:

  "Previously found in this session: [list bug classes]. Check all new bash
   command blocks for stdout capture; check all new JSON output paths for
   completeness."

This prevents the same class of bug being found twice across two sequential
review cycles.
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add AGENTS.md
git -C /Users/russelllaing/al-dev-shared commit -m "📝 Add Quality Review Conventions to AGENTS.md

Addresses Pattern 1 (HIGH) from 2026-05-11 session friction review.
Per-task reviewers now carry a running bug-class watch list forward."
```

---

### Task 2: Add Plan Self-Review Requirement to AGENTS.md

**Files:**
- Modify: `AGENTS.md` (append after Quality Review Conventions)

- [ ] **Step 1: Append Plan Self-Review Requirement section**

Add to the end of `AGENTS.md`:

```markdown

## Plan Self-Review Requirement

Before submitting any plan for execution, the plan author MUST perform a
self-consistency pass:

1. **Token audit:** If the plan prohibits harness-specific tokens in output
   files, scan all *plan-specified file content* for those same tokens. Any
   occurrence in a code block example counts as a violation of the plan's own
   rule and must be resolved (genericise the example or add an explicit
   exception with reasoning) before execution begins.

2. **Constraint propagation check:** For every "must not contain X" rule in
   a spec, verify that no task step directs an agent to write content that
   contains X.

Unresolved contradictions at plan-review time cost 3× more to fix during
execution than at authoring time.
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add AGENTS.md
git -C /Users/russelllaing/al-dev-shared commit -m "📝 Add Plan Self-Review Requirement to AGENTS.md

Addresses Pattern 2 (HIGH) from 2026-05-11 session friction review.
Token audit and constraint propagation check now required before execution."
```

---

### Task 3: Add Tiered Code Review Protocol to AGENTS.md

**Files:**
- Modify: `AGENTS.md` (append after Plan Self-Review Requirement)

- [ ] **Step 1: Append Tiered Code Review Protocol section**

Add to the end of `AGENTS.md`:

```markdown

## Tiered Code Review Protocol

Per-task reviews check task-scope correctness. A **mid-point integration
review** must be scheduled at the halfway task (e.g. after Task 4 of 7) to
review the whole module assembled so far — not just the latest additions.

Integration review checklist additions (beyond per-task scope):
- [ ] All regex patterns tested against the full token set, not just the
      tokens introduced in the current task
- [ ] Deduplication / set-membership logic verified end-to-end across all
      scan functions added to date
- [ ] CLI flag names consistent across all `argparse` definitions added so far
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add AGENTS.md
git -C /Users/russelllaing/al-dev-shared commit -m "📝 Add Tiered Code Review Protocol to AGENTS.md

Addresses Pattern 4 (HIGH) from 2026-05-11 session friction review.
Mid-point integration review now required at task N/2."
```

---

### Task 4: Add Known Environment Issues to AGENTS.md

**Files:**
- Modify: `AGENTS.md` (append after Tiered Code Review Protocol)

- [ ] **Step 1: Append Known Environment Issues section**

Add to the end of `AGENTS.md`:

````markdown

## Known Environment Issues

**Python 3.13 / libexpat conflict (macOS)**
`pytest` may fail with a libexpat dynamic-library conflict under Python 3.13
on macOS. Workaround: run tests inline:

```bash
python3.13 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('mod', 'path/to/script.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert mod.some_function() == expected_value, 'Test failed'
print('PASS')
"
```

Until the environment is repaired, use this pattern for all Python test
verification in al-dev-shared sessions.
````

- [ ] **Step 2: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add AGENTS.md
git -C /Users/russelllaing/al-dev-shared commit -m "📝 Add Known Environment Issues to AGENTS.md

Addresses Pattern 3 (MEDIUM) from 2026-05-11 session friction review.
Documents Python 3.13 / libexpat workaround for all future sessions."
```

---

### Task 5: Mirror all 4 sections to CLAUDE.md

**Files:**
- Modify: `CLAUDE.md` (append all 4 sections after Commit Conventions)

CLAUDE.md is the Claude Code equivalent of AGENTS.md. Both must carry the same operational conventions.

- [ ] **Step 1: Append all 4 sections to CLAUDE.md in a single edit**

Add to the end of `CLAUDE.md`:

````markdown

---

## Quality Review Conventions

**Iterative task reviews (per-task scope):**
When a quality reviewer finds a bug class in one task, it MUST add that class
to an explicit "watch list" carried into every subsequent task review in the
same session. Append to the review prompt:

  "Previously found in this session: [list bug classes]. Check all new bash
   command blocks for stdout capture; check all new JSON output paths for
   completeness."

This prevents the same class of bug being found twice across two sequential
review cycles.

## Plan Self-Review Requirement

Before submitting any plan for execution, the plan author MUST perform a
self-consistency pass:

1. **Token audit:** If the plan prohibits harness-specific tokens in output
   files, scan all *plan-specified file content* for those same tokens. Any
   occurrence in a code block example counts as a violation of the plan's own
   rule and must be resolved (genericise the example or add an explicit
   exception with reasoning) before execution begins.

2. **Constraint propagation check:** For every "must not contain X" rule in
   a spec, verify that no task step directs an agent to write content that
   contains X.

Unresolved contradictions at plan-review time cost 3× more to fix during
execution than at authoring time.

## Tiered Code Review Protocol

Per-task reviews check task-scope correctness. A **mid-point integration
review** must be scheduled at the halfway task (e.g. after Task 4 of 7) to
review the whole module assembled so far — not just the latest additions.

Integration review checklist additions (beyond per-task scope):
- [ ] All regex patterns tested against the full token set, not just the
      tokens introduced in the current task
- [ ] Deduplication / set-membership logic verified end-to-end across all
      scan functions added to date
- [ ] CLI flag names consistent across all `argparse` definitions added so far

## Known Environment Issues

**Python 3.13 / libexpat conflict (macOS)**
`pytest` may fail with a libexpat dynamic-library conflict under Python 3.13
on macOS. Workaround: run tests inline:

```bash
python3.13 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('mod', 'path/to/script.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert mod.some_function() == expected_value, 'Test failed'
print('PASS')
"
```

Until the environment is repaired, use this pattern for all Python test
verification in al-dev-shared sessions.
````

- [ ] **Step 2: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add CLAUDE.md
git -C /Users/russelllaing/al-dev-shared commit -m "📝 Mirror review-findings conventions to CLAUDE.md

Adds Quality Review Conventions, Plan Self-Review Requirement,
Tiered Code Review Protocol, and Known Environment Issues — mirroring
the AGENTS.md additions from the 2026-05-11 session friction review."
```

---

### Task 6: Update al-dev-session-analyst with git-log supplement (LOW)

**Files:**
- Modify: `~/.copilot/installed-plugins/copilot-configs/copilot-al-dev/agents/al-dev-session-analyst.md`
  (and the source in the copilot-configs repo if applicable)

- [ ] **Step 1: Add git-log supplement instruction to File Churn Analysis section**

In the `### 3. File Churn Analysis` section, after the existing bullet points, add:

```markdown
- **For subagent-driven sessions:** session_store does not track subagent
  file writes. When a session's checkpoints indicate heavy subagent use,
  supplement FILE_CHURN with a git log count:
  ```bash
  git log --oneline --name-only --since="<session-start-date>" | grep -v "^[a-f0-9]" | sort | uniq -c | sort -rn | head -20
  ```
  Note the discrepancy between session_store edit counts and git commit
  counts in the report's File Churn table (`Inferred Cause` column).
```

- [ ] **Step 2: Verify the edit looks correct**

```bash
grep -A 10 "git log" ~/.copilot/installed-plugins/copilot-configs/copilot-al-dev/agents/al-dev-session-analyst.md
```

Expected: the new git log block appears after the FILE_CHURN bullet points.

- [ ] **Step 3: Commit (in copilot-configs repo)**

```bash
git -C $(dirname $(dirname ~/.copilot/installed-plugins/copilot-configs/copilot-al-dev/agents/al-dev-session-analyst.md))/../.. add copilot-al-dev/agents/al-dev-session-analyst.md
git -C ... commit -m "📝 Add git-log supplement to session analyst for subagent sessions

Addresses Pattern 5 (LOW) from 2026-05-11 session friction review.
FILE_CHURN from session_store is supplemented with git log for sessions
where subagents write files outside session_store tracking."
```

> **Note:** Task 6 modifies a file in a separate repo (`copilot-configs`). Confirm the correct git root before committing.
