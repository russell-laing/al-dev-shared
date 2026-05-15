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
