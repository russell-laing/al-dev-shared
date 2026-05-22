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

**Decision Framework:**

Choose the *clean* (slower but maintainable) fix when:
- The code runs fewer than 100 times per user session, so throughput gain is negligible
- The performance gain (fast fix) is < 5% vs. baseline, AND code complexity increases >30%
- The fast fix requires unsafe patterns (unchecked ARRAY operations, unsafe type casts, global state mutation) that create regression risk
- The code is in a shared library (codeunit/table) where maintainability affects other modules' performance debugging

Choose the *fast* fix when:
- User-facing latency is >2s and clean rewrite requires weeks
- The fix is isolated to one code path with no shared dependencies
- The performance gain (fast fix) is >20% improvement over clean approach

**Example:** Query returning 10,000 records for a FactBox display

SLOW BUT CLEAN FIX:
```al
procedure GetCustomerSummaryByDateRange(StartDate: Date; EndDate: Date): JsonObject
var
    Customer: Record Customer;
    SalesLines: Record "Sales Line";
    Summary: JsonObject;
    TotalAmount: Decimal;
begin
    TotalAmount := 0;
    Customer.SetFilter("Creation Date", '>=%1&<=%2', StartDate, EndDate);
    if Customer.FindSet() then
        repeat
            SalesLines.SetRange("Customer No.", Customer."No.");
            SalesLines.CalcSums(Amount);
            TotalAmount += SalesLines.Amount;
        until Customer.Next() = 0;
    
    Summary.Add('Total', TotalAmount);
    exit(Summary);
end;
```

FAST BUT RISKY FIX:
```al
procedure GetCustomerSummaryCached(var Customer: Record Customer): JsonObject
var
    CacheKey: Text;
begin
    CacheKey := 'CUST_' + Customer."No.";
    if Cache.Get(CacheKey) <> '' then
        exit(ParseCacheJson(Cache.Get(CacheKey)));
    // ... cache logic with inline SQL
end;
```

**Decision:** Use the clean fix. The 10,000-record load is a data-load problem (table design), not an algorithm problem. Solving it with cache masks the real issue and breaks when data changes.

### When the performance fix changes business logic risk

**Decision Framework:**

A performance fix introduces *business logic risk* when it:
- Changes which records are processed (filtering, batching boundaries)
- Modifies when validations run (early exit vs. full validation)
- Alters transaction scope (split one transaction into many, or vice versa)
- Removes intermediate steps that provide audit/compliance trail

**RED FLAGS — Ask for requirements review before implementing:**
- "Skip validation on bulk inserts for speed"
- "Cache customer balance instead of querying each time"
- "Process payments in batches instead of one-by-one"

These are NOT performance problems; they are requirements problems.

**Example: "Slow Sales Order validation"**

RISKY FIX (skips validation):
```al
procedure PostSalesOrderFast(var SalesHeader: Record "Sales Header")
begin
    SalesHeader.Validate := false;  // DANGEROUS: skips all field validations
    SalesHeader.Modify();
end;
```

SAFE FIX (validates earlier):
```al
procedure PostSalesOrderOptimized(var SalesHeader: Record "Sales Header")
var
    SalesLines: Record "Sales Line";
begin
    // Validate BEFORE loops, not during
    SalesHeader.ValidateCustomerCredit();
    SalesHeader.ValidateShippingAddress();
    
    SalesLines.SetRange("Document No.", SalesHeader."No.");
    if SalesLines.FindSet() then
        repeat
            // No per-line validation; all checks done at header level
            SalesLines.Modify();
        until SalesLines.Next() = 0;
end;
```

**Decision:** The safe fix pre-validates once (header-level), then skips per-line checks. No business logic changes; same validations, better order.

### Batch Processor vs. UI code paths — Different Trade-off Rules

**Batch Processing (Codeunit::RunBatch) Trade-offs:**
- Can sacrifice user-facing latency for throughput (10 seconds for 1M records is OK)
- Can use memory-intensive caching/indexing strategies
- Must prioritize **correctness** over speed (batch runs unattended; no way to retry fast)
- Best approach: Clean code + async architecture (fire and forget)

**UI Code Path Trade-offs:**
- Must keep response <500ms (user perception threshold)
- Memory constraints (UI thread must not block)
- Can sacrifice data completeness for responsiveness (show 100 records, not 10K)
- Best approach: Pagination, filtering, narrow result sets

**Example Decision:**

**Batch Processor — Recalculate Inventory:**
```al
procedure RecalculateAllInventory()  // Called from batch job
var
    Item: Record Item;
    InventoryCache: Dictionary of [Code[20], Decimal];
begin
    // Load all items into cache (OK for batch, uses memory freely)
    if Item.FindSet() then
        repeat
            // CalculateInventoryFromCache performs pure math, no DB calls — avoids N+1 pattern
            InventoryCache.Add(Item."No.", CalculateInventoryFromCache(Item."No."));
        until Item.Next() = 0;
    
    // Single pass through data
    UpdateInventoryLedger(InventoryCache);
end;
```

**UI Code Path — Show Customer Balance:**
```al
procedure GetCustomerBalance(CustomerNo: Code[20]): Decimal
begin
    // DO NOT load all items like batch does
    // Query only the customer balance, cache short-lived (1 min)
    exit(QueryCustomerBalance(CustomerNo));  // Query, not cache
end;
```

**Decision:** Batch uses memory-heavy caching; UI uses lightweight queries. Different rules for different contexts.

### Caching as trade-off — When Cache Correctness Matters

**When Caching Improves Performance:**
- Data is read-heavy (100+ reads per write)
- Query is expensive (10+ table joins, complex filtering)
- Update frequency is known and bounded (daily batch, weekly reconciliation)

**When Caching Creates Risk:**
- Cache invalidation is unclear (how to know cache is stale?)
- Data consistency is critical (customer balance, inventory, compliance audit)
- Multiple systems write the same data (integration scenarios)

**Invalidation Patterns:**
- **Time-based:** Cache expires after N minutes (OK for non-critical reads like "top 10 customers")
- **Event-based:** Cache clears when related data changes (OK for materialized views, requires event hook)
- **Manual:** Code explicitly clears cache on Save (OK for small caches, risky if forgotten)

**Example: Customer Credit Limit Cache**

WRONG (high invalidation cost):
```al
var CreditCache: Dictionary of [Code[20], Decimal];

procedure GetCustomerCreditLimit(CustomerNo: Code[20]): Decimal
begin
    if not CreditCache.ContainsKey(CustomerNo) then
        CreditCache.Add(CustomerNo, Customer."Credit Limit");
    exit(CreditCache.Get(CustomerNo));
end;

// When is this cache invalid? If customer credit is changed manually in table,
// cache stays stale. Dangerous for sales orders!
```

RIGHT (invalidation is clear):
```al
procedure GetCustomerCreditLimit(CustomerNo: Code[20]): Decimal
var
    Customer: Record Customer;
begin
    Customer.Get(CustomerNo);
    // Direct query; cache not worth it (customer changes infrequently)
    exit(Customer."Credit Limit");
end;
```

**Decision:** Skip the cache. Customer credit limit changes rarely; query cost is <1ms. Cache invalidation risk >> performance gain.

### Complexity budget — When Code Gets Too Clever

**Complexity warning signs:**
- Function exceeds 50 lines (split into procedures)
- More than 3 nested IF statements (extract to separate procedure)
- More than 2 data structures (Dictionary + Array + custom record) in one function
- Conditional logic using bitwise operations or unusual patterns

**Complexity vs. Performance Trade-off:**

| Code Pattern | Performance | Maintainability | Use When |
|-------------|-------------|-----------------|----------|
| Loop with early exit | Good | Good | Searching, filtering |
| Indexed lookup (Dictionary) | Excellent | Good | 100+ lookups |
| Bit flags (1 var stores 8 states) | Excellent | Poor | Extreme memory constraint |
| Separate procedures (DRY) | Slightly slower | Excellent | Default choice |
| Inline/unrolled loops | Excellent | Poor | Proven bottleneck with measurement |

**Example: Don't Trade Maintainability for Micro-optimizations**

OVER-COMPLEX (unrolled loop for 5% speed gain):
```al
procedure ProcessOrdersFast(var SalesHeaders: Record "Sales Header")
begin
    // Unrolled loop: processes 4 orders per iteration (too clever!)
    while SalesHeaders.FindSet() do begin
        ProcessOrder(SalesHeaders);
        SalesHeaders.Next();
        if SalesHeaders."No." <> '' then begin
            ProcessOrder(SalesHeaders);
            SalesHeaders.Next();
            if SalesHeaders."No." <> '' then begin
                ProcessOrder(SalesHeaders);
                SalesHeaders.Next();
                if SalesHeaders."No." <> '' then begin
                    ProcessOrder(SalesHeaders);
                    SalesHeaders.Next();
                end;
            end;
        end;
    end;
end;
```

SIMPLE AND SUFFICIENT (clear, 95% speed of over-complex version):
```al
procedure ProcessOrders(var SalesHeaders: Record "Sales Header")
begin
    if SalesHeaders.FindSet() then
        repeat
            ProcessOrder(SalesHeaders);
        until SalesHeaders.Next() = 0;
end;
```

**Decision:** Use the simple loop. 5% speed gain is not worth a 10x increase in maintenance cost. Keep complexity budget for proven bottlenecks.
