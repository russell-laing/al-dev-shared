# Session Analyst Shared Report Format

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a shared report format template in `al-dev-shared` so both harness-specific `al-dev-session-analyst` agents produce consistent, interchangeable findings reports — without merging the agents themselves.

**Architecture:** Add a single knowledge doc to `al-dev-shared` that defines the canonical report structure. Both harness analysts (Claude Code in `claude-configs` and Copilot CLI in `copilot-configs`) reference it. After this plan completes, two separate handover plans update each harness profile in their own repos. The agents remain harness-specific (as per the 2026-05-11 design spec); only the output format is shared.

**Tech Stack:** Markdown knowledge docs, `git`, `grep`, `wc`

---

## Background

The `al-dev-session-analyst` agent exists in two harness-specific copies:
- `claude-configs/profile-claude-al-dev/agents/al-dev-session-analyst.md` — JSONL-based, per-session skill attribution
- `copilot-configs/profile-copilot-al-dev/agents/al-dev-session-analyst.md` — SQL-based, cross-session aggregate patterns

These cannot be merged (forbidden harness tokens; different data sources). But their output format diverges independently. A shared format template anchors both outputs without violating the harness-agnostic constraint.

**Also in scope for the handover plans (not this repo):**
- Path bug fix in `claude-configs/profile-claude-al-dev/skills/al-dev-review/SKILL.md:27`
  — change `PROJECT_HASH=$(pwd | tr '/' '-')` → `PROJECT_HASH=$(pwd | tr '/_' '--')`
  — this is independent of the shared format work but should be shipped first as a direct commit to `claude-configs`.

---

## File Map

| File | Change | Responsibility |
|---|---|---|
| `profile-al-dev-shared/knowledge/session-analysis-report-format.md` | **Create** | Canonical report structure for both harness analysts |

---

### Task 1: Create the shared report format knowledge doc

**Files:**
- Create: `profile-al-dev-shared/knowledge/session-analysis-report-format.md`

- [ ] **Step 1: Verify the file does not already exist**

```bash
ls profile-al-dev-shared/knowledge/session-analysis-report-format.md 2>/dev/null && echo "EXISTS" || echo "NOT FOUND"
```

Expected: `NOT FOUND`

- [ ] **Step 2: Create the knowledge doc**

Create `profile-al-dev-shared/knowledge/session-analysis-report-format.md` with this exact content:

```markdown
# Session Analysis Report Format

Canonical output format for `al-dev-session-analyst` agents across all harnesses.
Both Claude Code (JSONL-based) and Copilot CLI (SQL-based) analysts produce reports
conforming to this structure so findings are consistent and interchangeable.

---

## Required Sections

Reports must include sections in this order:

1. Report header
2. Executive summary
3. Findings (HIGH → MEDIUM → LOW)
4. Recommendations by File / Target
5. What Went Well _(optional)_
6. Next Steps _(optional)_

---

## 1. Report Header

```markdown
# Session Review — {YYYY-MM-DD}

**Analysed:** {session identifier or repository name}
**Data source:** {e.g. "Claude Code JSONL transcript" | "Copilot CLI session_store (SQL)"}
**Scope:** {one sentence describing what was analysed and how many sessions}
```

---

## 2. Executive Summary

```markdown
## Executive Summary

**Skills invoked / Sessions analysed:** {harness-specific summary line}
**Issues detected:** {N} HIGH, {N} MEDIUM, {N} LOW
**Session outcome:** {one sentence}
```

---

## 3. Findings

Each finding must follow this structure exactly:

```markdown
### [HIGH|MEDIUM|LOW] {Short descriptive title}

**Severity:** {LEVEL} — {one sentence explaining why this severity}

**Pattern:** {Description of the friction pattern observed.}

**Evidence:**
```
{1–3 lines of supporting evidence — quoted messages, error output, or counts}
```

**Root cause:** {Why this happened — specific instruction gap, missing step, or logic error.}

**Impact:** {What the user experienced as a result.}

**Recommended fix:** {Specific actionable improvement — name the exact section or file to change, and describe the change.}

---
```

### Severity Definitions

| Severity | Meaning |
|---|---|
| **HIGH** | Workflow was blocked, user had to restart, or explicit rejection requiring full rework |
| **MEDIUM** | Extra turns required but workflow completed |
| **LOW** | Minor improvement opportunity, no disruption |

---

## 4. Recommendations by File / Target

```markdown
## Recommendations by File

| File | Issue | Priority |
|---|---|---|
| `path/to/file.md` | Short title of issue | HIGH / MEDIUM / LOW |
```

---

## 5. What Went Well (optional)

Brief bulleted list of workflow phases that succeeded without friction. Include at least one
entry if findings were found — shows the report is balanced, not a pure defect list.

---

## Zero-Finding Report

If no issues are found, the full report collapses to:

```markdown
# Session Review — {YYYY-MM-DD}

**Analysed:** {session identifier or repository name}
**Data source:** {data source}

## Summary

No significant friction detected in this session.
```
```

- [ ] **Step 3: Verify the file was created and is non-empty**

```bash
wc -l profile-al-dev-shared/knowledge/session-analysis-report-format.md
```

Expected: at least 90 lines

- [ ] **Step 4: Check for any placeholder text that should not remain**

```bash
grep -n "TODO\|TBD\|\[date\]\|YYYY-MM-DD" profile-al-dev-shared/knowledge/session-analysis-report-format.md
```

Expected: no matches (all `{YYYY-MM-DD}` template markers are inside code blocks, which is correct)

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/knowledge/session-analysis-report-format.md
git commit -m "📝 docs(session-analyst): add shared report format template

Canonical output structure for al-dev-session-analyst across both
harnesses. Claude Code (JSONL-based) and Copilot CLI (SQL-based)
analysts reference this to produce consistent, interchangeable reports.

Agents remain harness-specific per 2026-05-11 design; only the format
is shared."
```

---

## Handover Plans (to be created after this plan completes)

Once Task 1 is committed, create two separate handover plan files and execute them in their respective repos:

### Handover A — claude-configs

**Repo:** `/Users/russelllaing/claude-configs`
**Plan file:** `docs/superpowers/plans/2026-05-15-session-analyst-format-adoption.md`

Tasks:
1. **Path hotfix** (first, standalone commit): In `profile-claude-al-dev/skills/al-dev-review/SKILL.md:27`, change `PROJECT_HASH=$(pwd | tr '/' '-')` → `PROJECT_HASH=$(pwd | tr '/_' '--')`
2. **Format adoption**: Update `profile-claude-al-dev/agents/al-dev-session-analyst.md` — add a reference to the shared format at the top of Step 5 (Write Findings Report):
   > "Follow the canonical report format in `profile-al-dev-shared/knowledge/session-analysis-report-format.md`. The structure below must conform to that template."
3. Commit both changes.

### Handover B — copilot-configs

**Repo:** `/Users/russelllaing/copilot-configs`
**Plan file:** `docs/superpowers/plans/2026-05-15-session-analyst-format-adoption.md`

Tasks:
1. **Format adoption**: Update `profile-copilot-al-dev/agents/al-dev-session-analyst.md` — add a reference to the shared format at the top of the Output Format section:
   > "Follow the canonical report format in `profile-al-dev-shared/knowledge/session-analysis-report-format.md`. The structure below must conform to that template."
2. Commit.
