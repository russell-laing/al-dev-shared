---
name: al-dev-perf
description: Analyze AL codeunits for performance anti-patterns.
argument-hint: "[codeunit name, file path, or 'scan all']"
---

# Skill: /al-dev-perf

Static performance analysis — surfaces AL anti-patterns before
they reach production.

---

## When to Use

| Situation | Use |
| --- | --- |
| A process is noticeably slow in BC | ✅ |
| Implementing a codeunit with large data sets | ✅ |
| Code review flagged performance concerns | ✅ |
| Before a performance-critical feature ships | ✅ |
| General style review (no perf concern) | ❌ |

---

## Implementation

### Step 1 — Determine Scope

From user args:

- **Specific file path**: analyse that file directly
- **Codeunit name**: find via Glob then analyse

```bash
find src/ -iname "*.codeunit.al" 2>/dev/null
```

- **"scan all"** or no args: find all codeunit files in `src/`

Load `.dev/project-context.md` to prioritise objects noted as
high-volume or batch-processing.

### Step 1.5 — Identify Entry-Point Metadata

For each codeunit found in Step 1, use the AL Symbols MCP
(`al-mcp-server`) to classify it before spawning the analysis agent:

- `al_get_object_summary` — check for OnRun() and codeunit type
- `al_search_object_members` — detect event subscriber attributes

| Indicator | Classification | Severity modifier |
| --- | --- | --- |
| Has `OnRun()` | Entry Point | +1 level |
| Has `[EventSubscriber]` attribute | Hot Path | +1 level |
| Name contains Batch/Process/Import/Post/Transfer/Run | Batch Processor | +1 level |
| None of the above | Utility | none |

If al-mcp-server is unavailable or returns no result for a codeunit,
default to Utility (no modifier). Do not block the analysis.

Produce a classification summary to pass into Step 2:

```
Codeunit classifications:
- CreateJobV6.Codeunit.al → Entry Point (has OnRun)
- BatchPostSales.Codeunit.al → Batch Processor (name heuristic)
- StringHelper.Codeunit.al → Utility
```

---

### Step 2 — Spawn Performance Analysis Agent

> Pattern: `knowledge/explore-subagent-pattern.md` — Steps A–D.
> Performance-specific prompt content is below.

```text
Spawn an explore agent:
  purpose: Perf scan: [scope description]
  prompt: [performance analysis prompt]
  output: performance findings with file:line references

Prompt:
  "Scan these AL codeunit files for performance anti-patterns.
   Read each file fully, then report ALL findings.

   Files to analyse: [file paths from Step 1]

   Codeunit classifications (from AL Symbols pre-research):
   [paste the classification summary from Step 1.5]

   Severity escalation rule: For any P1–P8 finding in a codeunit
   classified as Entry Point, Hot Path, or Batch Processor — escalate
   its severity by one level (LOW→MEDIUM, MEDIUM→HIGH, HIGH→CRITICAL).
   Reflect this in the SEVERITY field and explain it in the IMPACT field.

   Anti-patterns to find and 'Do NOT flag' exclusions: See `knowledge/perf-anti-patterns-prompt.md`. Paste the full content of that file here before dispatching.

   For EACH finding report:
   PATTERN: [P1–P8 ID]
   SEVERITY: CRITICAL | HIGH | MEDIUM | LOW
   FILE: [exact path]
   LINE: [line number]
   CODE: [3–5 lines of the problematic code]
   FIX: [3–5 lines of the corrected version]
   IMPACT: [estimated frequency — per record, per batch, etc.]"
```

---

### Step 3 — Write Analysis Report

Write `.dev/$(date +%Y-%m-%d)-al-dev-perf-perf-analysis.md`:

```markdown
# Performance Analysis — [scope] — [date]

## Summary

| Severity | Count |
| --- | --- |
| 🔴 CRITICAL | N |
| 🟠 HIGH | N |
| 🟡 MEDIUM | N |
| 🟢 LOW | N |

**Total findings:** N across X files

## Findings

### 🔴 CreateJobV6.Codeunit.al — ⚡ Entry Point

#### 🔴 P1 — N+1 Query — line 123

~~~al
// Current (BAD):
if V6QuoteItem.FindSet() then repeat
    Item.Get(V6QuoteItem."Item No.");  // N DB calls
until V6QuoteItem.Next() = 0;
~~~

**Fix:**

~~~al
// Pre-load all Items with SetLoadFields before the loop,
// or cache in a temporary record keyed on Item No.
~~~

**Estimated impact:** CRITICAL (escalated from HIGH) — Entry Point called by Job Queue; P1 hit on every quote item in batch processing

[Repeat per codeunit; within each codeunit, repeat per finding ordered by CRITICAL → LOW]

### 🟢 StringHelper.Codeunit.al — 🗃 Utility

#### 🟢 P6 — SetRange + FindFirst — line 44

[finding details...]

**Estimated impact:** LOW — Utility procedure; low call frequency

## Recommended Fix Order

1. [CRITICAL findings — fix immediately]
2. [HIGH findings — fix before next release]
3. [MEDIUM findings — fix when touching the file]
4. [LOW findings — optional, low risk]

## Next Steps

[If CRITICAL or HIGH findings:]
Design fixes with: `/al-dev-plan fix performance issues in [scope]`

[If only LOW findings:]
No critical issues. Low findings documented for reference.
```

---

### Step 4 — Present to User

```text
Performance analysis complete → perf-analysis.md

Findings: N total
  🔴 Critical: N  (N+1 queries in hot paths)
  🟠 High: N      (missing SetLoadFields)
  🟡 Medium: N    (FindSet(true) write-lock misuse)
  🟢 Low: N       (minor optimisations)

Top priority: [most critical finding in one line]

[If CRITICAL/HIGH:]
Ready to plan fixes? /al-dev-plan fix performance issues in [scope]

[If LOW only:]
No critical issues found. Findings in perf-analysis.md.
```

---

## Notes

- SetLoadFields is only worth flagging when fewer than ~3 fields
  are used — do not flag comprehensive record reads
- FindSet(true) is only a problem when the loop body has no
  Modify/Delete/Rename
- CalcFields on FlowFields is required — only flag when it is
  inside a loop with many iterations
- For very large codebases, scope to specific codeunits first;
  use "scan all" only for smaller extensions
- AL Symbols lookup (Step 1.5) enriches severity by context; if symbols
  are unavailable the skill falls back to equal-weight analysis
- The +1 severity escalation applies once per finding — a LOW finding
  in a Batch Processor becomes MEDIUM, not CRITICAL
- P8 (full table scan) is most useful on tables > ~1000 rows; do not
  flag config or setup tables
