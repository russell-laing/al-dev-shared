# Performance Anti-Patterns Prompt Content

Paste this block into the spawn prompt for the performance analysis agent (Step 2 of /al-dev-perf):

```text
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
P8 (MEDIUM baseline) — Full Table Scan: FindSet() with no prior
  SetRange() or SetFilter() on a table likely to be large
  (Sales Header/Line, Item, Customer, Vendor, any Ledger Entry
  table, or any table whose name is a common plural noun).
  Escalate to HIGH if the codeunit is Entry Point or Batch Processor.
  Do NOT flag FindSet on small config/setup tables.

For EACH finding report:
PATTERN: [P1–P8 ID]
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
  immediately discarded
```

---

## Severity Classification

Severity levels indicate the urgency of remediation and the likely user-visible impact. Use these definitions when escalating a baseline pattern or adjudicating ambiguous cases.

### Critical

The pattern causes O(N) or O(N²) database round-trips that scale with business data volume. Even a small dataset will degrade noticeably; large datasets can cause timeouts or lock contention. Remediation must happen before the code ships.

**Examples:**
- P1: Inner `FindSet` inside outer `FindSet` loop — 1 000 customers × 1 000 ledger entries = 1 M DB calls per batch run.
- P3 inside a Batch Processor codeunit that processes all open Sales Orders — CalcFields on each line multiplies DB calls by line count.

### High

The pattern adds measurable overhead per record but does not cause exponential scaling. Performance degrades proportionally to data volume and becomes user-visible above moderate table sizes (>10 000 rows). Remediation is required before release.

**Examples:**
- P2: `Customer.Get(No)` with no `SetLoadFields` when only `Name` and `Credit Limit` are read — fetches all 80+ Customer fields per call.
- P3 outside a loop but called from a function invoked per-line in a report — same CalcFields overhead, lower urgency than CRITICAL because it is not nested.
- P8 escalated: unfiltered `FindSet` on Item Ledger Entry inside an Entry Point codeunit.

### Medium

The pattern is wasteful or stylistically incorrect but has limited runtime impact at typical data volumes. Flag and recommend a fix, but do not block release on this finding alone.

**Examples:**
- P4: `FindSet(true)` with no write operations — unnecessary write lock acquired, slight overhead, risk of blocking other sessions.
- P5: Setup table `Get()` inside a loop of 50 records — adds 50 redundant DB calls; noticeable only at high call frequencies.
- P8 baseline: unfiltered `FindSet` on a large table inside a non-batch helper — wasteful but low observed frequency.

### Low

The pattern is an inefficiency or code-style issue with negligible runtime cost. Report it for completeness; remediation is optional.

**Examples:**
- P6: `SetRange` covering full PK then `FindFirst` — functionally identical to `Get()`; minor clarity and micro-performance improvement available.
- P7: `Count()` immediately before `FindSet()` on the same variable — two table scans where one suffices; impact is minimal unless table is very large.

---

## Exclusion Rules — When NOT to Flag

These rules prevent false positives that waste developer review time. Apply each rule before reporting a finding.

### Loop-body DB call exclusions (P1, P3, P5)

Do NOT flag a DB call inside a loop when:
- The call uses the same key on every iteration and the result is expected to vary due to concurrent writes (intentional re-read pattern).
- The inner table is a small lookup table guaranteed to be cached by the platform (e.g., Currency, Unit of Measure, Language). Indicator: table has fewer than 200 rows in a typical BC installation and no user-editable volume data.
- The call is inside a `TransactionModel::AutoCommit` or `Commit()` block where re-reading is required by design to see committed state.

### SetLoadFields exclusions (P2)

Do NOT flag missing `SetLoadFields` when:
- The procedure subsequently accesses 3 or more distinct fields from the record. The cost of the additional round-trip to read missing fields outweighs the savings.
- The record is fetched via `Get()` on a table with 10 or fewer fields total — field projection overhead exceeds the benefit.
- The record is immediately passed by reference (var) to another procedure that may access any field. You cannot statically determine the field set.

### FindSet(true) exclusions (P4)

Do NOT flag `FindSet(true)` when:
- Any of `Modify()`, `Delete()`, or `Rename()` is called anywhere in the loop body, including inside nested procedure calls that are visible in the same file.
- The code comment explicitly states a write lock is required for concurrency control.

### Full Table Scan exclusions (P8)

Do NOT flag an unfiltered `FindSet` when:
- The table is a setup, config, or enumeration table (recognisable by name: anything ending in Setup, Template, Type, Group, Code, or having fewer than 1 000 expected rows).
- The codeunit is a one-time migration or upgrade codeunit (contains `OnUpgradePerCompany` or `OnInstallPerCompany` subscribers).
- A comment above the FindSet explicitly documents why a full scan is required (e.g., reindexing, data correction).

---

## Trade-Off Guidance — Performance vs. Maintainability

Not every performance anti-pattern should be fixed the same way. The right fix depends on context: how hot is the code path, how often is it called, and how much complexity does the optimisation add? Use these guidelines to calibrate your FIX recommendation.

### When to prioritise a clean fix over the fastest fix

A full rewrite to eliminate N+1 queries can introduce bugs, especially when the inner query carries filtering side-effects. If the loop is called fewer than 100 times per batch and the table has fewer than 500 rows, a `SetLoadFields` addition (P2) or a Setup cache variable (P5) is the right trade-off — it removes measurable overhead without restructuring logic.

Example trade-off: `CalcFields` inside a loop (P3) on a report that runs nightly over 200 invoices. The correct fix is `SetAutoCalcFields` on the record before the loop, not restructuring the report dataset. Adding `SetAutoCalcFields` is a one-line change with zero maintainability cost.

### When the performance fix changes business logic risk

Replacing `FindFirst` (P6) with `Get()` changes error-handling behaviour: `Get()` returns `false` on missing records while `FindFirst` combined with a conditional may swallow the miss silently. Always note this in the FIX block when the patterns differ in error behaviour.

### Batch Processor vs. UI code paths

Apply stricter thresholds for batch processors and job queue codeunits. A P8 finding (full table scan) that costs 200 ms in a UI action is LOW impact; the same scan inside a job that runs every 5 minutes becomes HIGH impact due to accumulated load. Escalate severity by one level for any pattern found inside a codeunit with `IsJobQueueEntry` logic or `OnRun` trigger serving as a job entry point.

### Caching as a trade-off

For P5 (Setup table in loop), the standard fix is to read the setup record once before the loop into a local variable. This is always safe when the loop does not `Commit()` mid-run. If the loop contains explicit `Commit()` calls, a cached variable may read stale setup data — in that case, flag the pattern but note the caching risk in the FIX block rather than recommending the cache blindly.

### Complexity budget

If fixing a pattern requires adding a temporary table, a new procedure, or more than 15 lines of new code, note the complexity cost explicitly in the IMPACT field. A LOW-severity finding (P6 or P7) never justifies a refactor that adds 30 lines. Recommend the simple fix or mark it as "acceptable at current data volume" with a note to revisit if volume grows.
