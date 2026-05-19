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
