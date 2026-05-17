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

## Performance Anti-Patterns

### P1 — N+1 Query (CRITICAL)

```al
// BAD: Get() or FindFirst inside a FindSet loop
if Orders.FindSet() then repeat
    Item.Get(Orders."Item No.");  // N DB calls
until Orders.Next() = 0;
```

### P2 — Missing SetLoadFields (HIGH)

```al
// BAD: loads all fields when only one is needed
Customer.Get(CustNo);
Name := Customer.Name;

// GOOD:
Customer.SetLoadFields(Name);
Customer.Get(CustNo);
```

Only flag when fewer than ~3 fields are used from the retrieved
record. Do not flag when most fields are needed.

### P3 — CalcFields Inside Loop (HIGH)

```al
// BAD: DB hit per record — use CalcFields before the loop
// or filter with SetAutoCalcFields
if Item.FindSet() then repeat
    Item.CalcFields("Sales (LCY)");
until Item.Next() = 0;
```

Do not flag CalcFields on FlowFields when there is no loop —
that is required and correct.

### P4 — FindSet(true) on Read-Only Pass (MEDIUM)

```al
// BAD: write lock when loop body never calls Modify/Delete
if MyRec.FindSet(true) then repeat
    // reads only
until MyRec.Next() = 0;

// GOOD: FindSet() or FindSet(false)
```

Only flag when the loop body has no Modify(), Delete(), or
Rename() calls.

### P5 — Setup.Get() Per Loop Iteration (MEDIUM)

```al
// BAD: re-reads same setup record on every iteration
if Item.FindSet() then repeat
    JobsSetup.Get();
    InventorySetup.Get();
until Item.Next() = 0;

// GOOD: Get() once before the loop
```

### P6 — SetRange on PK + FindFirst Where Get() Suffices (LOW)

```al
// BAD:
MyRec.SetRange("Primary Key", KeyValue);
if MyRec.FindFirst() then ...

// GOOD: if MyRec.Get(KeyValue) then ...
```

Only flag when the SetRange covers the full primary key with
exact values (not ranges or filters).

### P7 — Redundant Count Pass (LOW)

```al
// BAD: two full table scans for the same data
RecCount := MyRec.Count();
if MyRec.FindSet() then repeat
until MyRec.Next() = 0;
```

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

   Anti-patterns to find:
   P1 (CRITICAL) — Get(), FindFirst(), or FindSet() called
     inside another FindSet loop body. The inner call's key
     varies per iteration (confirming N DB calls).
   P2 (HIGH) — Record retrieved with Get()/Find without
     SetLoadFields when fewer than 3 fields are subsequently
     used from that record.
   P3 (HIGH) — CalcFields() called inside any loop body.
     Exception: do NOT flag if the FlowField cannot be filtered
     with SetAutoCalcFields and there is no alternative.
   P4 (MEDIUM) — FindSet(true) used in a loop where no
     Modify(), Delete(), or Rename() is called in the loop body.
   P5 (MEDIUM) — Any Setup table Get() (JobsSetup, SalesSetup,
     InventorySetup, PurchasesPayablesSetup, etc.) called inside
     a loop body.
   P6 (LOW) — SetRange on all PK fields + FindFirst where
     Get() on the same key would work.
   P7 (LOW) — Count() called immediately before FindSet() on
     the same record variable.

   For EACH finding report:
   PATTERN: [P1–P7 ID]
   SEVERITY: CRITICAL | HIGH | MEDIUM | LOW
   FILE: [exact path]
   LINE: [line number]
   CODE: [3–5 lines of the problematic code]
   FIX: [3–5 lines of the corrected version]
   IMPACT: [estimated frequency — per record, per batch, etc.]

   Do NOT flag:
   - CalcFields outside loops
   - Get() inside loops where the key value is unchanged
     (same record fetched intentionally, e.g., re-read after Modify)
   - SetLoadFields when the procedure reads most fields anyway
   - FindSet(true) when the loop body calls Modify(), Delete(),
     or Rename()
   - SetRange + FindFirst when the SetRange does not cover the
     full primary key with exact (non-range) values
   - Count() before FindSet when the count value is used
     (stored, displayed, or drives control flow) rather than
     immediately discarded"
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

### 🔴 P1 — N+1 Query — `CreateJobV6.Codeunit.al:123`

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

**Estimated impact:** High — once per quote item in batch operations

[Repeat block for each finding, ordered by CRITICAL → LOW]

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
