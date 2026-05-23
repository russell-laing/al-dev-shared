# Session Analysis Report Format

Canonical output format for `al-dev-session-analyst` agents across all harnesses.
Claude Code (JSONL-based), Copilot CLI (SQL-based), and Codex
(session-transcript/tool-trace-based) analysts produce reports conforming to
this structure so findings are consistent and interchangeable.

---

## Report Shapes

Use one of these two valid report shapes:

1. Standard report — required when one or more findings are present
2. Zero-finding collapsed report — allowed only when no issues are found

### Standard Report Sections

Standard reports must include sections in this order:

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
**Data source:** {e.g. "Claude Code JSONL transcript" | "Copilot CLI session_store (SQL)" | "Codex session transcript / tool trace"}
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

Brief bulleted list of workflow phases that succeeded without friction.
Include this section only when there is at least one concrete success worth recording.

---

## 6. Next Steps (optional)

Brief bulleted list of follow-up actions, investigation ideas, or workflow improvements.
Include only when there is a clear next action after the review.

---

## Zero-Finding Report

If no issues are found, use this collapsed format instead of the standard
section order above:

```markdown
# Session Review — {YYYY-MM-DD}

**Analysed:** {session identifier or repository name}
**Data source:** {e.g. "Claude Code JSONL transcript" | "Copilot CLI session_store (SQL)" | "Codex session transcript / tool trace"}

## Summary

No significant friction detected in this session.
```
