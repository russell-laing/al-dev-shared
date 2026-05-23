# Knowledge Quality Audit Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Address 8 HIGH severity issues and 8 MEDIUM/LOW severity issues identified in the knowledge-quality audit to improve agent guidance completeness and actionability.

**Architecture:** Three-phase implementation — CRITICAL fixes first (code review patterns, ticket invocation, performance decision frameworks), then HIGH fixes (RTM examples, verification patterns), then MEDIUM fixes (TDD workflow, commit conventions, script engineering). Each file gets focused content additions with concrete examples agents can execute.

**Tech Stack:** Knowledge files (Markdown), AL code examples, decision frameworks, audit validator

---

## File Structure

**Files to modify (8 total):**
- `profile-al-dev-shared/knowledge/code-review-patterns.md` — Add AL naming-violation code examples
- `profile-al-dev-shared/knowledge/ticket-agent-invocation-pattern.md` — Add ticket-type mapping and invocation parameters
- `profile-al-dev-shared/knowledge/perf-anti-patterns-prompt.md` — Expand 5 decision sections with frameworks
- `profile-al-dev-shared/knowledge/documentation-rtm-guide.md` — Add 3 audience-specific RTM examples
- `profile-al-dev-shared/knowledge/verification-and-planning.md` — Add checkpoint template and architect debate example
- `profile-al-dev-shared/knowledge/tdd-workflow.md` — Expand procedural sections with real examples
- `profile-al-dev-shared/knowledge/commit-conventions.md` — Clarify project-type declaration
- `profile-al-dev-shared/knowledge/script-engineer-conventions.md` — Add protocol integration example

---

## CRITICAL Priority (🔴) — Fix Before Next Release

### Task 1: Add AL Code Examples to code-review-patterns.md

**Files:**
- Modify: `profile-al-dev-shared/knowledge/code-review-patterns.md`
- Reference: Expert reviewer agent relies on this for naming antipattern detection

**Current state:** File exists but "Naming Convention Violations" section lacks concrete code examples

**What needs adding:** 5-10 AL code examples showing BEFORE/AFTER pairs for common naming antipatterns

- [ ] **Step 1: Read the current file to understand structure**

```bash
head -80 /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/code-review-patterns.md
```

- [ ] **Step 2: Locate the "Naming Convention Violations" section**

Find the section that describes naming violations (where examples should be added)

- [ ] **Step 3: Add BEFORE/AFTER code example block for variables**

Insert after naming violations intro:

```markdown
#### Example 1: Variable Naming — Avoid Abbreviations

**BEFORE (Poor):**
```al
procedure CalculateQty(DocLine: Record "Sales Line"; var Qty: Decimal)
begin
    var tmpRec: Record "Item Ledger Entry";
    var idx: Integer;
    var mxLines: Integer;
    
    mxLines := DocLine.Count();
    Qty := 0;
    
    if (DocLine.FindSet()) then
        repeat
            idx += 1;
            Qty += DocLine.Quantity;
        until DocLine.Next() = 0;
end;
```

**AFTER (Good):**
```al
procedure CalculateOrderQuantity(DocumentLine: Record "Sales Line"; var TotalQuantity: Decimal)
begin
    var temporaryInventoryRecord: Record "Item Ledger Entry";
    var lineIndex: Integer;
    var maximumLineCount: Integer;
    
    maximumLineCount := DocumentLine.Count();
    TotalQuantity := 0;
    
    if (DocumentLine.FindSet()) then
        repeat
            lineIndex += 1;
            TotalQuantity += DocumentLine.Quantity;
        until DocumentLine.Next() = 0;
end;
```

**What improved:** Variable names spell out intent (`tmpRec` → `temporaryInventoryRecord`, `idx` → `lineIndex`), parameter names are descriptive (`Qty` → `TotalQuantity`), procedure name matches the operation it performs.
```

- [ ] **Step 4: Add BEFORE/AFTER code example for procedure naming**

Insert after variable naming example:

```markdown
#### Example 2: Procedure Naming — Reflect Intent, Not Implementation

**BEFORE (Poor):**
```al
procedure Proc1(var Rec: Record Item; Amt: Decimal)
begin
    Rec."Unit Cost" := Amt;
    Rec.Validate();
end;

procedure DoIt(ItemNo: Code[20])
begin
    Clear(ItemNo);
end;
```

**AFTER (Good):**
```al
procedure UpdateItemUnitCost(var Item: Record Item; NewUnitCost: Decimal)
begin
    Item."Unit Cost" := NewUnitCost;
    Item.Validate();
end;

procedure ClearItemInventoryCache(ItemNumber: Code[20])
begin
    Clear(ItemNumber);
end;
```

**What improved:** Procedure names describe the action (`Proc1` → `UpdateItemUnitCost`, `DoIt` → `ClearItemInventoryCache`), making the intent clear to reviewers and reducing cognitive load.
```

- [ ] **Step 5: Add BEFORE/AFTER code example for object/field naming**

Insert after procedure naming example:

```markdown
#### Example 3: Object and Field Naming — Use Full Words in Public Interfaces

**BEFORE (Poor):**
```al
table 50000 "Ord Header"
{
    fields
    {
        field(1; "Ord No"; Code[20]) { }
        field(2; "Cust No"; Code[20]) { }
        field(3; "Amt Due"; Decimal) { }
        field(4; "Shp Dt"; Date) { }
        field(5; "Stat"; Option) { }
    }
}
```

**AFTER (Good):**
```al
table 50000 "Sales Order Header"
{
    fields
    {
        field(1; "Order Number"; Code[20]) { }
        field(2; "Customer Number"; Code[20]) { }
        field(3; "Amount Due"; Decimal) { }
        field(4; "Shipment Date"; Date) { }
        field(5; "Status"; Option) { }
    }
}
```

**What improved:** Field names are unambiguous (`Ord No` → `Order Number`, `Amt Due` → `Amount Due`, `Shp Dt` → `Shipment Date`). No abbreviations in public table definitions.
```

- [ ] **Step 6: Commit the changes**

```bash
cd /Users/russelllaing/al-dev-shared
git add profile-al-dev-shared/knowledge/code-review-patterns.md
git commit -m "docs(knowledge): add AL naming convention code examples to code-review-patterns.md

- Add variable naming BEFORE/AFTER example (avoid abbreviations)
- Add procedure naming BEFORE/AFTER example (reflect intent)
- Add table/field naming BEFORE/AFTER example (use full words)

Closes expert-reviewer agent guidance gap for naming violations.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 7: Verify file persistence and line count**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/code-review-patterns.md
git status profile-al-dev-shared/knowledge/code-review-patterns.md
```

Expected: File line count increases by ~60 lines; `git status` shows the file as modified.

---

### Task 2: Add Ticket-to-Files Mapping to ticket-agent-invocation-pattern.md

**Files:**
- Modify: `profile-al-dev-shared/knowledge/ticket-agent-invocation-pattern.md`
- Referenced by: al-dev-ticket-agent, al-dev-ticket, al-dev-support (3 workflow components)

**Current state:** File has empty "Related Files section"

**What needs adding:** Structured ticket type → affected files mapping and invocation pattern examples

- [ ] **Step 1: Read the current file**

```bash
cat /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/ticket-agent-invocation-pattern.md
```

- [ ] **Step 2: Locate the "Related Files section" placeholder**

Find where this section is (should be clearly marked)

- [ ] **Step 3: Add ticket-type mapping table**

Insert after "Related Files" header:

```markdown
### Ticket Type → Affected Files Mapping

| Ticket Type | Primary Files | Agent Spawn Context |
|-------------|--------------|-------------------|
| **Bug Report** | Codeunit, Table, Page (where bug occurs) | `ticket_type: "bug"`, `severity: "high|medium|low"` |
| **Feature Request** | New Codeunit/Table, Existing Page (UI integration point), Test coverage plan | `ticket_type: "feature"`, `priority: "p1|p2|p3"` |
| **Performance Issue** | Codeunit (query loops, batching), Table (indexing), Report (rendering) | `ticket_type: "perf"`, `metric: "response_time|memory|throughput"` |
| **Data Migration** | New Codeunit (migration logic), Source/Target Tables | `ticket_type: "data-migration"`, `cutover_date: "YYYY-MM-DD"` |
| **Integration** | New Codeunit (API/webhook handler), Existing Codeunit (caller), External API definition | `ticket_type: "integration"`, `system: "Salesforce|SAP|Custom"` |
| **Documentation** | Knowledge files, Help context strings, CLAUDE.md | `ticket_type: "docs"`, `audience: "admin|developer|end-user"` |
| **Compliance/Security** | Codeunit (access control), Table (audit fields), Permission Set | `ticket_type: "compliance"`, `standard: "GDPR|SOC2|HIPAA"` |

### When Ticket Analysis Routes to Multiple Files

If a ticket requires changes to 3+ files, the ticket agent should:

1. **Prioritize by logical dependency:** Core table changes before UI changes, data structures before business logic
2. **Document affected file groups:** Group related changes (e.g., "Data Layer: [tables]", "Business Logic: [codeunits]")
3. **Flag integration points:** Where one file's changes affect another (e.g., table field rename requires codeunit update)

**Example:** Feature ticket requesting "Add customer credit limit field and enforce it on sales orders"

Affected file mapping:
```
TABLES:
- Customer table (add Credit Limit field, validation)
- Sales Order Header (add Check Credit Before Release field)
- Sales Order Line (reference customer credit limit)

CODEUNITS:
- Sales-Post codeunit (add pre-post validation checking credit limit)
- Customer-Management codeunit (add credit limit recalculation on receipt)

PAGES:
- Customer Card (add Credit Limit field to FactBox)
- Sales Order (add warning if approaching credit limit)

TESTS:
- Add test_CustomerCreditLimitEnforcement.al
- Add test_SalesOrderCreditCheck.al
```
```

- [ ] **Step 4: Add invocation pattern parameter example**

Insert after ticket-to-files mapping:

```markdown
### Invocation Pattern: Agent Spawn Parameters

When the ticket skill spawns the ticket agent, it passes context in this structure:

```
{
  "ticket_id": "JIRA-1234",
  "ticket_type": "bug|feature|perf|data-migration|integration|docs|compliance",
  "title": "user-provided ticket title",
  "description": "user-provided full description",
  "priority": "p1|p2|p3",              // Only for feature/bug
  "severity": "critical|high|medium|low",  // Only for bug/compliance
  "affected_systems": ["Customer", "Sales Order", "Reports"],
  "context_files": ["path/to/al/file.al", "docs/knowledge/related-doc.md"]
}
```

**Example invocation for bug ticket:**

```json
{
  "ticket_id": "BUG-567",
  "ticket_type": "bug",
  "title": "Sales Order total calculation incorrect when multiple discounts applied",
  "description": "When a sales order has both header discount and line discounts...",
  "severity": "high",
  "affected_systems": ["Sales Order", "Calculation Engine"],
  "context_files": ["SalesOrder.Codeunit.al", "DiscountCalculation.Codeunit.al"]
}
```

The ticket agent uses this to route analysis to the correct files and assessment framework (bug analysis vs. feature feasibility).
```

- [ ] **Step 5: Verify structure and commit**

```bash
cd /Users/russelllaing/al-dev-shared
git add profile-al-dev-shared/knowledge/ticket-agent-invocation-pattern.md
git commit -m "docs(knowledge): add ticket-type mapping and invocation patterns

- Add table mapping ticket types to affected files and spawn context
- Document multi-file priority order and integration point flagging
- Add invocation parameter structure with bug example

Supports ticket agent, ticket skill, and support workflow components.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 6: Verify file persistence**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/ticket-agent-invocation-pattern.md
git status profile-al-dev-shared/knowledge/ticket-agent-invocation-pattern.md
```

Expected: File line count increases by ~50 lines.

---

### Task 3: Expand Decision Frameworks in perf-anti-patterns-prompt.md

**Files:**
- Modify: `profile-al-dev-shared/knowledge/perf-anti-patterns-prompt.md`
- Referenced by: al-dev-performance-reviewer, al-dev-perf skill

**Current state:** 5 sections each with 1-2 lines, lacking decision logic

**What needs adding:** Decision framework and one concrete example for each of the 5 sections

- [ ] **Step 1: Read the current file**

```bash
cat /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/perf-anti-patterns-prompt.md
```

- [ ] **Step 2: Find the 5 thin sections that need expansion:**
- When to prioritise clean fix over fastest fix
- When performance fix changes business logic risk
- Batch Processor vs. UI code paths
- Caching as trade-off
- Complexity budget

- [ ] **Step 3: Expand section 1 — "When to prioritise clean fix over fastest fix"**

Replace thin section with:

```markdown
## When to Prioritise Clean Fix Over Fastest Fix

**Decision Framework:**

Choose the *clean* (slower but maintainable) fix when:
- The code is in a hot path executed 100+ times per user session, AND code clarity won't impact future performance tuning
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
procedure GetCustomerSummary(var Customer: Record Customer): JsonObject
var
    SalesLines: Record "Sales Line";
    Summary: JsonObject;
    TotalAmount: Decimal;
begin
    TotalAmount := 0;
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
```

- [ ] **Step 4: Expand section 2 — "When performance fix changes business logic risk"**

Replace thin section with:

```markdown
## When Performance Fix Changes Business Logic Risk

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
    
    if SalesLines.FindSet() then
        repeat
            // No per-line validation; all checks done at header level
            SalesLines.Modify();
        until SalesLines.Next() = 0;
end;
```

**Decision:** The safe fix pre-validates once (header-level), then skips per-line checks. No business logic changes; same validations, better order.
```

- [ ] **Step 5: Expand section 3 — "Batch Processor vs. UI code paths"**

Replace thin section with:

```markdown
## Batch Processor vs. UI Code Paths — Different Trade-off Rules

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
            InventoryCache.Add(Item."No.", CalculateInventory(Item."No."));
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
```

- [ ] **Step 6: Expand section 4 — "Caching as trade-off"**

Replace thin section with:

```markdown
## Caching as Trade-off — When Cache Correctness Matters

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
```

- [ ] **Step 7: Expand section 5 — "Complexity budget"**

Replace thin section with:

```markdown
## Complexity Budget — When Code Gets Too Clever

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
```

- [ ] **Step 8: Commit the changes**

```bash
cd /Users/russelllaing/al-dev-shared
git add profile-al-dev-shared/knowledge/perf-anti-patterns-prompt.md
git commit -m "docs(knowledge): expand performance decision frameworks with concrete examples

- Expand 'Clean vs. Fast fix' with decision logic and query example
- Expand 'Business logic risk' with red flags and validation example
- Expand 'Batch vs. UI paths' with memory/latency trade-offs and examples
- Expand 'Caching trade-offs' with invalidation patterns and credit limit example
- Expand 'Complexity budget' with patterns table and unrolled loop example

Supports performance-reviewer agent and perf skill guidance.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 9: Verify file persistence**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/perf-anti-patterns-prompt.md
git status profile-al-dev-shared/knowledge/perf-anti-patterns-prompt.md
```

Expected: File line count increases by ~150 lines.

---

## HIGH Priority (🟡) — Fix This Week

### Task 4: Add Audience-Specific RTM Examples to documentation-rtm-guide.md

**Files:**
- Modify: `profile-al-dev-shared/knowledge/documentation-rtm-guide.md`
- Referenced by: al-dev-docs-writer agent

**Current state:** Examples section has 2 lines; audience perspective section has 2 lines

**What needs adding:** 3 concrete RTM table examples (functional user, technical admin, developer) + decision criteria for omitting RTM

- [ ] **Step 1: Read the current file**

```bash
cat /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/documentation-rtm-guide.md
```

- [ ] **Step 2: Find the "Examples" section and "User Perspective" section**

Locate both thin sections

- [ ] **Step 3: Add functional user RTM example**

Insert after examples header:

```markdown
### Example 1: Functional User RTM — "How to Process a Sales Order"

**Use case:** Documenting a feature from the business user's perspective. RTM maps user stories to instructions.

| User Requirement | Page Section | Step | Verification |
|------------------|-------------|------|--------------|
| "Create sales order for customer" | Sales Order Card | Enter header (customer, date) | Customer details auto-populate |
| "Add line items with quantity" | Sales Order Lines | Click Add Line, enter Item No., Quantity | System calculates line total |
| "System should verify customer credit" | Sales Order Card | Click Validate (before posting) | Credit warning appears if exceeded |
| "Apply discount if quantity threshold met" | Sales Order Lines | Quantity > 10 auto-applies 5% discount | Discount appears in Amount field |
| "Post order to create invoice" | Sales Order Card | Click Post | Order status changes to "Posted" |
| "Verify invoice in Accounts Receivable" | Posted Invoices | Search customer invoices | New invoice appears in list |

**RTM structure:** Each row is a user action (requirement) → UI location → steps → how to verify. Rows flow in business-logic order (create → validate → post → verify).

**Who uses this RTM?** Functional testers, business analysts, end users validating new features.
```

- [ ] **Step 4: Add technical admin RTM example**

Insert after functional user example:

```markdown
### Example 2: Technical Admin RTM — "Deploying the Sales Module Update"

**Use case:** Documenting a system administration task. RTM maps deployment requirements to configuration steps.

| Admin Requirement | Configuration Area | Procedure | Verification Command |
|------------------|-------------------|-----------|---------------------|
| "Apply hotfix to codeunit 50000" | Code Deployments | Import .al file via DevOps | `al-compile --output errors.log` returns no errors |
| "Update customer credit limit validation" | Table 18 extensions | Modify validation rule in Customer table | Run test suite: `pytest tests/customer-validation/` |
| "Enable credit limit enforcement on sales order posting" | Permission Set assignments | Add "Post Sales Order" permission to all Sales roles | User can post order without "Access Denied" |
| "Configure audit logging for order amendments" | Audit Trail setup | Enable field-change logging on Sales Header | Changes appear in Audit Log within 5 minutes |
| "Validate integration with external billing system" | Integration endpoints | Test webhook endpoint with mock payload | Webhook returns HTTP 200 OK; order appears in billing system |

**RTM structure:** Each row is an admin task → config location → how to perform it → how to verify it works. Rows follow deployment sequence (code → config → permissions → testing).

**Who uses this RTM?** System administrators, DevOps engineers, deployment teams.
```

- [ ] **Step 5: Add developer RTM example**

Insert after technical admin example:

```markdown
### Example 3: Developer RTM — "Implementing Customer Credit Limit Enforcement"

**Use case:** Documenting a code feature. RTM maps functional requirements to code modules and tests.

| Functional Requirement | Code Module | Implementation | Test Coverage |
|-------|---|---|---|
| "Customer credit limit is set and stored" | Table 18 (Customer) | Add field "Credit Limit" (Decimal, min 0) | `test_CustomerCreditLimitField_CanBeSet()` |
| "Credit limit cannot be negative" | Table 18 validation | Add validation: `if "Credit Limit" < 0 then Error(...)` | `test_CustomerCreditLimitField_RejectsNegative()` |
| "Sales order cannot post if customer exceeds credit" | Codeunit 80 (Sales-Post) | Add pre-post check in OnBeforePostSalesHeader | `test_SalesOrder_BlockedWhenCreditExceeded()` |
| "Sales order warning if approaching limit (90%)" | Page 42 (Sales Order) | Add FactBox field binding to credit usage % | `test_SalesOrderPage_WarningAppearsAt90Percent()` |
| "Credit limit overrides for emergency orders" | Table 109 (Sales Order Header) | Add field "Override Credit Check" (boolean) | `test_SalesOrder_AllowsOverride_WhenFlagSet()` |
| "Audit log tracks credit overrides" | Codeunit 50001 (Audit Handler) | Log credit override to audit table | `test_AuditLog_RecordsCreditOverride()` |

**RTM structure:** Each row is a requirement → code location → how implemented → corresponding test. Rows follow data-flow order (store → validate → use → display).

**Who uses this RTM?** Developers writing code, code reviewers verifying coverage, QA testers writing test plans.
```

- [ ] **Step 6: Add omit decision criteria**

Insert after the three examples:

```markdown
### When to Omit RTM Table

**Omit RTM if:**
- Documentation is <500 words (RTM adds overhead for small docs)
- Feature is a bug fix or internal refactor with no new requirements (RTM is for requirements tracing, not code refactoring)
- Feature is a simple config change with 1-2 steps (too granular for RTM; use numbered list instead)
- Audience is developers only, code-level traceability is in comments/tests (don't duplicate)

**Include RTM if:**
- Feature is new and spans 3+ modules (track req → code → test mappings)
- Documentation is for multiple audiences (functional users + admins + developers; RTM tailors to each)
- Compliance/audit trail required (RTM documents what was implemented, who verified, where the evidence is)
- Stakeholder sign-off needed (RTM is the deliverable artifact)
```

- [ ] **Step 7: Commit the changes**

```bash
cd /Users/russelllaing/al-dev-shared
git add profile-al-dev-shared/knowledge/documentation-rtm-guide.md
git commit -m "docs(knowledge): add RTM examples for functional user, admin, and developer

- Add functional user RTM example (sales order processing workflow)
- Add technical admin RTM example (deployment and configuration)
- Add developer RTM example (credit limit enforcement feature)
- Add decision criteria for when to omit RTM

Supports docs-writer agent guidance on audience-specific documentation.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 8: Verify file persistence**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/documentation-rtm-guide.md
git status profile-al-dev-shared/knowledge/documentation-rtm-guide.md
```

Expected: File line count increases by ~80 lines.

---

### Task 5: Add Actionable Examples to verification-and-planning.md

**Files:**
- Modify: `profile-al-dev-shared/knowledge/verification-and-planning.md`
- Status: Currently orphaned (not referenced by any active agent yet)

**Current state:** File describes concepts but lacks concrete examples

**What needs adding:** Verification checkpoint template, architect debate transcript example, caching strategy example

- [ ] **Step 1: Read the current file**

```bash
cat /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/verification-and-planning.md
```

- [ ] **Step 2: Locate sections needing examples:**
- Verification Pattern section
- The Three Architect Outputs section
- Example: Architect Debate on Caching Strategy section

- [ ] **Step 3: Add verification checkpoint template**

Insert after "Verification Pattern" header:

```markdown
### Verification Checkpoint Template

Every multi-phase skill should use this checkpoint structure after each phase:

**File:** `.dev/progress.md`

```markdown
# Skill Execution Progress

## Phase 0: Requirements Analysis
- [x] Read ticket/spec
- [x] Identified 3 affected modules (Table, Codeunit, Page)
- [x] Risk assessment complete (medium complexity, 1 data model change)

**Output:** Requirements context file saved to `.dev/requirements.md`

**Resume capability:** Can restart from Phase 1 with requirements cached

---

## Phase 1: Design & Planning
- [ ] Architect debate completed
- [ ] Design decision: Use event-based architecture (vs. procedure override)
- [ ] Plan written to `.dev/2026-05-22-solution-plan.md`

**Next:** Phase 2 (Implementation) can proceed with design from Phase 1

---

## Phase 2: Implementation
- [ ] Code changes: Table 18 (+5 fields), Codeunit 50000 (new procedure), Page 42 (new FactBox)
- [ ] Tests written: 8 test procedures
- [ ] Code review: Waiting for approval

**Status:** Paused pending review

---

## Phase 3: Verification
- [ ] Local test run: 8/8 tests passing
- [ ] Compile check: 0 errors
- [ ] Integration test: Feature end-to-end verified

**Result:** Ready for commit
```

This structure lets agents:
1. Resume at any phase (check `.dev/progress.md` at start)
2. Know what was output from prior phases (references to `.dev/*.md` files)
3. Checkpoint after each phase (prevents context loss in long sessions)
```

- [ ] **Step 4: Add architect debate transcript example**

Insert after "The Three Architect Outputs" section:

```markdown
### Example: Architect Debate on Caching Strategy

**Problem Statement:** Sales order posting takes 2.5 seconds for 100+ lines due to repeated customer balance lookups.

**Three Design Proposals:**

**Proposal 1: Query Optimization (Solo Architect)**
```
Approach: Index customer ledger by customer number, add early-exit in query loop.

Pros: 
- Simplest change: 5 lines of code, no new tables/fields
- Balance remains real-time (no stale cache risk)
- No performance variation (consistent <500ms)

Cons:
- Won't scale beyond 500 lines (index hit still O(n) lookups)
- Ignores root cause (repeated balance calculation inside line loop)

Risk: Medium (low code change, but incomplete solution)
```

**Proposal 2: In-Memory Cache (Conservative)**
```
Approach: Load customer balance into Dictionary on order entry, reuse throughout posting.

Pros:
- Significant speed gain (90% reduction: 2.5s → 0.25s)
- Clear cache invalidation (disposed when order posting done)
- Backward compatible

Cons:
- Requires new Dictionary variable, increases function size
- Breaks if balance changes mid-posting (rare, but possible in integration scenarios)

Risk: Low (well-understood pattern, clear scope)
```

**Proposal 3: Database View + Materialized Cache (Aggressive)**
```
Approach: Create materialized view of customer balance, refresh every 1 hour via batch job, query view instead of ledger.

Pros:
- Fastest performance (0.05s lookup in view)
- Scales to 1000s of lines
- Works across all modules (not just sales posting)

Cons:
- High complexity: new view, new batch job, new sync logic
- Cache can be 1 hour stale (balance might be wrong for recent transactions)
- Requires new monitoring (batch failure alerts)

Risk: High (complex implementation, stale-data risk, cross-module dependencies)
```

**Debate:**
- **Conservative advocate:** "Proposal 2 (in-memory) hits the sweet spot. We're optimizing a single operation (order posting), not the whole system. Materialized view is overengineering."
- **Aggressive advocate:** "Proposal 2 fails if balance changes mid-posting. We should use Proposal 3 — the view is the right abstraction, and we can invest in refresh logic now."
- **Solo architect:** "Actually, let's try Proposal 1 first (query optimization). If it meets the 500ms target, we avoid cache complexity entirely."

**Decision:** Proposal 2 (in-memory cache)

Rationale: Proposal 1 insufficient (doesn't scale), Proposal 3 over-scoped (introduces stale-data risk and cross-module dependencies). Proposal 2 is minimal, isolated, and provides the needed performance (0.25s << 2.5s). Revisit if posting expands beyond 500 lines.

**Implementation task:** Add `customerBalanceCache: Dictionary` to posting procedure, load once, query from cache for all line lookups, clear on exit.

**Verification:** Measure posting time for 100-line order; confirm < 0.5s.
```

This example shows:
1. Three distinct proposals (not a solo choice)
2. Clear trade-off analysis (perf vs. complexity vs. risk)
3. Debate logic (why each proposal was chosen or rejected)
4. Final decision with reasoning
5. Linked to implementation task and verification step
```

- [ ] **Step 5: Add caching strategy example under a separate section**

Insert as a new subsection after the debate example:

```markdown
### Example: Architect Debate Output — Caching Strategy Decision Document

After the debate resolves, the architect creates a one-page decision document:

```markdown
# Caching Strategy for Sales Order Posting

## Decision: In-Memory Customer Balance Cache

### Context
Sales order posting (100+ lines) takes 2.5s due to repeated ledger lookups.

### Rejected Alternatives
- Query optimization alone (Proposal 1): insufficient scaling past 500 lines
- Materialized view (Proposal 3): over-scoped, introduces stale-data risk

### Implementation
```al
procedure PostSalesOrder(var SalesHeader: Record "Sales Header")
var
    customerBalanceCache: Dictionary of [Code[20], Decimal];
begin
    // Load balance once
    LoadCustomerBalances(SalesHeader, customerBalanceCache);
    
    // Query cache for all line lookups (no repeated ledger queries)
    ProcessSalesLines(SalesHeader, customerBalanceCache);
    
    // Clear cache on exit (order-scoped, not persistent)
    customerBalanceCache.Clear();
end;
```

### Test Coverage
- test_PostSalesOrder_UsesCache() — verify cache loaded once
- test_PostSalesOrder_Performance() — confirm < 0.5s for 100-line order

### Risk Mitigation
- Cache is order-scoped (cleared on function exit)
- Falls back to ledger query if cache miss (defensible)
- Only used in posting; doesn't affect balance queries in UI

### Rollback Plan
If cache causes test failure: Remove customerBalanceCache variable, revert to uncached ledger queries (recovers original 2.5s behavior).
```

This output:
- States the decision clearly
- Documents why alternatives were rejected
- Shows the code implementation
- Lists verification steps
- Includes risk mitigation and rollback path

All future work references this decision document, so developers don't re-litigate the choice.
```

- [ ] **Step 6: Commit the changes**

```bash
cd /Users/russelllaing/al-dev-shared
git add profile-al-dev-shared/knowledge/verification-and-planning.md
git commit -m "docs(knowledge): add verification checkpoints and architect debate examples

- Add verification checkpoint template for multi-phase skills
- Add architect debate transcript example (caching strategy)
- Add caching strategy decision document example with implementation

Provides concrete patterns for verification-and-planning knowledge.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 7: Verify file persistence**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/verification-and-planning.md
git status profile-al-dev-shared/knowledge/verification-and-planning.md
```

Expected: File line count increases by ~120 lines.

---

## MEDIUM Priority (🟢) — Fix This Month

### Task 6: Expand Procedural Sections in tdd-workflow.md

**Files:**
- Modify: `profile-al-dev-shared/knowledge/tdd-workflow.md`

**Current state:** 5 procedural sections each with 2 lines, lacking concrete examples

**What needs adding:** Real examples from app.json auto-detection, CI/CD integration patterns

- [ ] **Step 1: Read the current file**

```bash
cat /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/tdd-workflow.md
```

- [ ] **Step 2: Locate the 5 thin sections:**
- Auto-Detection
- File Output Options
- Failures-Only Filter
- CI/CD Integration
- Example Workflows

- [ ] **Step 3: Expand "Auto-Detection" section**

Replace thin section with:

```markdown
## Auto-Detection: Detecting Test Framework from app.json

TDD workflow auto-detects the test framework by reading the project's `app.json`:

**AL Test Framework (Built-in):**
```json
{
  "name": "MyApp",
  "version": "1.0.0.0",
  "publisher": "CompanyName",
  "appDependencies": [],
  "test": "tests/"
}
```

If `app.json` has a `"test"` field pointing to a directory, the workflow assumes AL's built-in test framework. Tests run via:
```bash
al-compile --output test-results.xml
```

**External Test Framework (pytest, jest, etc.):**
```json
{
  "name": "MyIntegration",
  "version": "1.0.0.0",
  "testFramework": "pytest"
}
```

If `app.json` has `"testFramework"`, the workflow runs:
```bash
pytest tests/ --junitxml=test-results.xml
```

**Detection Logic:**
1. Check if `app.json` contains `"test"` field → use AL test framework
2. Check if `app.json` contains `"testFramework"` field → use specified framework
3. If neither, fallback: check for `pytest.ini` or `jest.config.js` in project root
4. If no test config found, error out: "No test framework detected"

**Result:** Workflow automatically runs the right command without user input.
```

- [ ] **Step 4: Expand "File Output Options" section**

Replace thin section with:

```markdown
## File Output Options: Where Test Results Are Written

TDD workflow writes test output to `.dev/` directory with timestamp:

**AL Test Framework Output:**
```
.dev/
  ├── 2026-05-22-tdd-test-results.xml    # JUnit XML (parsed by CI/CD)
  ├── 2026-05-22-tdd-test-summary.txt    # Human-readable summary
  └── 2026-05-22-tdd-coverage.json       # Code coverage report (if enabled)
```

**Example test-summary.txt:**
```
Test Results Summary
====================
Run Time: 2026-05-22 14:32:45

Total Tests: 24
Passed: 22
Failed: 2
Skipped: 0

FAILED TESTS:
- test_CustomerCreditLimit_RejectsNegative (Assertion: Credit Limit should be >= 0)
- test_SalesOrder_BlocksPosting_WhenCreditExceeded (Timeout: query took >5s)

Duration: 2.3 seconds
```

**External Test Framework Output (pytest example):**
```
.dev/
  ├── 2026-05-22-tdd-pytest-results.xml  # JUnit XML
  ├── 2026-05-22-tdd-pytest-report.html  # HTML report (for viewing)
  └── 2026-05-22-tdd-coverage.txt        # Text coverage report
```

**Output file naming convention:**
`{DATE}-tdd-{FRAMEWORK}-{OUTPUT_TYPE}.{EXT}`

Example: `2026-05-22-tdd-pytest-results.xml`, `2026-05-22-tdd-pytest-coverage.txt`

This allows multiple test runs to coexist in `.dev/` without overwriting.
```

- [ ] **Step 5: Expand "Failures-Only Filter" section**

Replace thin section with:

```markdown
## Failures-Only Filter: Focus on Failing Tests

After the first full test run, TDD workflow can filter to only failing tests:

**Full Run (all tests):**
```bash
al-compile --output .dev/2026-05-22-tdd-test-results.xml
# Output: 24 tests in 2.3 seconds
```

**Failures-Only Run (after failure):**
```bash
# Workflow extracts failed test names from prior run
# Runs only those tests:

al-compile --test-class=test_CustomerCreditLimit_RejectsNegative \
           --test-class=test_SalesOrder_BlocksPosting_WhenCreditExceeded \
           --output .dev/2026-05-22-tdd-test-results-filtered.xml
# Output: 2 tests in 0.3 seconds (10× faster feedback loop)
```

**When to use failures-only:**
- After fixing one test, quickly verify it passes (run just that test)
- During active development of a feature (don't wait for full suite)
- Debugging a specific test (run it in isolation)

**When to use full run:**
- Before commit (ensure no regressions)
- After major refactor (re-verify all tests)
- In CI/CD (always full run to catch integration issues)

**Workflow Heuristic:**
- First invocation: full run (establish baseline)
- If failures found: run failures-only for dev cycle
- Before commit: switch back to full run
```

- [ ] **Step 6: Expand "CI/CD Integration" section**

Replace thin section with:

```markdown
## CI/CD Integration: Test Results Feed the Pipeline

TDD workflow writes test results in JUnit XML format, which CI/CD systems understand natively:

**GitHub Actions Integration:**
```yaml
name: AL Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run AL Tests
        run: al-compile --output test-results.xml
      - name: Publish Test Results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: test-results.xml
```

CI/CD automatically parses the `.xml` file and shows test results in the PR:
```
✅ 22 passed, ❌ 2 failed out of 24 tests
```

**Azure Pipelines Integration:**
```yaml
steps:
  - script: al-compile --output $(Build.ArtifactStagingDirectory)/test-results.xml
    displayName: "Run Tests"
  
  - task: PublishTestResults@2
    inputs:
      testResultsFiles: '$(Build.ArtifactStagingDirectory)/test-results.xml'
      testResultsFormat: 'JUnit'
```

**Result:** CI/CD sees test failures and blocks merge until tests pass.

**Key requirement:** Test framework must output JUnit XML (standard format). AL test framework produces this by default.
```

- [ ] **Step 7: Expand "Example Workflows" section**

Replace thin section with:

```markdown
## Example Workflows: Common TDD Scenarios

### Scenario 1: New Feature (Red-Green-Refactor Cycle)

```
1. Write test (RED)
   al-compile --test-class=test_NewFeature_XYZ
   Output: FAIL — function not defined

2. Write minimal code (GREEN)
   Add function stub to codeunit

3. Run test
   al-compile --test-class=test_NewFeature_XYZ
   Output: PASS

4. Refactor (optional)
   Improve code clarity
   Run full test suite to verify no regression
   al-compile --output test-results.xml

5. Commit
   git add tests/ src/
   git commit -m "feat: add new feature with tests"
```

### Scenario 2: Bug Fix with Test

```
1. Reproduce bug in test
   test_BugFix_BugNameReproducesIssue() — expects correct behavior
   Run: FAIL — bug causes wrong result

2. Debug and fix the bug
   Locate issue in codeunit, apply fix

3. Run failures-only
   al-compile --test-class=test_BugFix_BugNameReproducesIssue
   Output: PASS

4. Run full suite
   al-compile --output test-results.xml
   Confirm no regression: 24/24 PASS

5. Commit
   git add src/ tests/
   git commit -m "fix: resolve bug in X module

   Fixes issue where [description]. Added regression test.
   "
```

### Scenario 3: Refactor with Safety Net

```
1. Add tests for current behavior (no code change yet)
   test_Refactor_PreservesExistingBehavior() — just documents what already works
   Run: PASS (tests the current code)

2. Refactor code (logic unchanged, structure improved)
   Reorganize procedures, improve variable names
   Do NOT change logic

3. Run full test suite
   al-compile --output test-results.xml
   Expected: All prior tests still pass (24/24 PASS)

4. Commit
   git add src/
   git commit -m "refactor: reorganize module X for clarity

   No logic changes. All existing tests pass.
   "
```

Each workflow shows the test commands and expected outputs, so developers know what "done" looks like.
```

- [ ] **Step 8: Commit the changes**

```bash
cd /Users/russelllaing/al-dev-shared
git add profile-al-dev-shared/knowledge/tdd-workflow.md
git commit -m "docs(knowledge): expand TDD procedural sections with real examples

- Expand Auto-Detection with app.json detection logic
- Expand File Output Options with .dev/ naming convention
- Expand Failures-Only Filter with usage heuristics
- Expand CI/CD Integration with GitHub Actions and Azure Pipelines examples
- Expand Example Workflows with Red-Green-Refactor, Bug Fix, and Refactor scenarios

Supports TDD workflow guidance with concrete patterns.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 9: Verify file persistence**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/tdd-workflow.md
git status profile-al-dev-shared/knowledge/tdd-workflow.md
```

Expected: File line count increases by ~120 lines.

---

### Task 7: Clarify project-type Declaration in commit-conventions.md

**Files:**
- Modify: `profile-al-dev-shared/knowledge/commit-conventions.md`

**Current state:** Section on project-type declaration has 2 lines with minimal explanation

**What needs adding:** Clear documentation of project-type values (al|vault|tool) and rationale

- [ ] **Step 1: Read the current file and find the project-type section**

```bash
cat /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/commit-conventions.md | grep -A 5 "project-type"
```

- [ ] **Step 2: Expand the project-type section**

Replace thin section with:

```markdown
## project-type Declaration

Every CLAUDE.md must declare the `project-type` field in the header section. This field tells Claude Code how to categorize the project and what workflows apply.

**Valid project-type values:**

| Type | Meaning | Example Projects | Tools & Patterns |
|------|---------|------------------|------------------|
| `al` | Business Central / Dynamics 365 AL application | Sales, Finance, HR modules | AL compiler, BC symbols, test framework |
| `vault` | Knowledge/documentation vault (no code compilation) | al-dev-shared (this repo), onboarding docs, playbooks | Markdown validators, knowledge organization |
| `tool` | CLI tool, script, or utility (Python, Bash, JS) | Deployment automation, validator scripts, build tools | Package managers, test runners, CI/CD hooks |

**Examples:**

AL Project:
```yaml
project-type: al
```

Knowledge Vault:
```yaml
project-type: vault
```

Python Tool:
```yaml
project-type: tool
```

**Why this matters:**
- Determines which skills and agents are active
- Informs compile/test commands (AL projects run `al-compile`, tool projects run `pytest` or npm)
- Shapes documentation requirements (AL projects need RTM mapping, vault projects need knowledge audit)

**Detection (if not specified):**
1. Check for `app.json` → project-type: `al`
2. Check for `package.json` or `pyproject.toml` → project-type: `tool`
3. Check for `knowledge/` or `docs/` directory → project-type: `vault`
4. If unclear, ask the user
```

- [ ] **Step 3: Commit the changes**

```bash
cd /Users/russelllaing/al-dev-shared
git add profile-al-dev-shared/knowledge/commit-conventions.md
git commit -m "docs(knowledge): clarify project-type declaration with examples

- Document al|vault|tool values and their meanings
- Add example table with detection logic
- Explain why project-type matters for skills and workflows

Supports commit convention guidance.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 4: Verify file persistence**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/commit-conventions.md
git status profile-al-dev-shared/knowledge/commit-conventions.md
```

Expected: File line count increases by ~25 lines.

---

### Task 8: Add Protocol Integration Example to script-engineer-conventions.md

**Files:**
- Modify: `profile-al-dev-shared/knowledge/script-engineer-conventions.md`

**Current state:** "Protocol-Based Integration" section has 1 line

**What needs adding:** 2-3 paragraphs with protocol integration pattern example

- [ ] **Step 1: Read the current file**

```bash
cat /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/script-engineer-conventions.md
```

- [ ] **Step 2: Find the "Protocol-Based Integration" section**

Locate the section header

- [ ] **Step 3: Expand with protocol integration pattern**

Replace the 1-line section with:

```markdown
## Protocol-Based Integration: Script Communication Patterns

Scripts often need to communicate results to parent processes (Claude Code harness, CI/CD, Slack, etc.). Use **structured protocol output** instead of free-form logging.

**Protocol patterns:**

**Pattern 1: Exit Code + Stdout JSON**
```bash
#!/bin/bash
# Script performs some task and outputs structured result

result_json=$(cat <<EOF
{
  "status": "success",
  "task": "deploy-app",
  "version": "1.0.5",
  "duration_seconds": 42,
  "artifacts": [
    "dist/app-1.0.5.tar.gz",
    "dist/app-1.0.5.sha256"
  ]
}
EOF
)

echo "$result_json"
exit 0  # 0 = success; non-zero = failure
```

Parent process parses JSON from stdout, checks exit code:
```bash
output=$(./deploy.sh)
if [ $? -eq 0 ]; then
    version=$(echo "$output" | jq -r '.version')
    echo "Deployment succeeded: $version"
else
    echo "Deployment failed"
    exit 1
fi
```

**Pattern 2: Structured Log Lines (Newline-Delimited JSON)**
```bash
#!/bin/bash
# Script emits progress as it runs; each line is parseable JSON

log_event() {
    local phase=$1
    local status=$2
    local message=$3
    echo "{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"phase\": \"$phase\", \"status\": \"$status\", \"message\": \"$message\"}"
}

log_event "setup" "in_progress" "Installing dependencies..."
pip install -r requirements.txt
log_event "setup" "completed" "Dependencies installed"

log_event "test" "in_progress" "Running tests..."
pytest tests/
log_event "test" "completed" "Tests passed (24/24)"
```

Parent process (Claude Code monitor) reads each line, parses JSON, updates UI:
```
✓ Setup completed: Dependencies installed
✓ Test completed: Tests passed (24/24)
```

**Pattern 3: File-Based Result Checkpoint**
```bash
#!/bin/bash
# Long-running script writes progress to .dev/progress.json periodically

progress_file=".dev/progress.json"

update_progress() {
    local phase=$1
    local percent=$2
    cat > "$progress_file" <<EOF
{
  "phase": "$phase",
  "percent_complete": $percent,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "in_progress"
}
EOF
}

update_progress "compilation" 25
./compile-all.sh
update_progress "linking" 50
./link-all.sh
update_progress "packaging" 75
./package-app.sh
update_progress "completed" 100

cat > "$progress_file" <<EOF
{
  "phase": "completed",
  "percent_complete": 100,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "success",
  "output": "app-1.0.5.tar.gz"
}
EOF
```

Claude Code harness polls `.dev/progress.json` and shows progress bar; on completion, reads the `output` field.

**When to use each pattern:**

- **Exit Code + JSON:** Simple scripts, one-shot operations, CI/CD integration
- **Log Lines (NDJSON):** Long-running scripts, multiple discrete steps, monitoring/UI feedback
- **File Checkpoint:** Very long operations (>10 minutes), risk of process interruption, need to resume

All three patterns follow the rule: **Make your output machine-parseable, not human-readable.** Humans read JSON fine; machines struggle with prose.
```

- [ ] **Step 4: Commit the changes**

```bash
cd /Users/russelllaing/al-dev-shared
git add profile-al-dev-shared/knowledge/script-engineer-conventions.md
git commit -m "docs(knowledge): add protocol integration patterns to script conventions

- Add Exit Code + Stdout JSON pattern with example
- Add Structured Log Lines (NDJSON) pattern for long-running scripts
- Add File-Based Result Checkpoint pattern for resumable operations
- Explain when to use each pattern

Supports script engineer guidance on structured communication protocols.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 5: Verify file persistence**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/script-engineer-conventions.md
git status profile-al-dev-shared/knowledge/script-engineer-conventions.md
```

Expected: File line count increases by ~90 lines.

---

## Completion Checklist

After all tasks are complete:

- [ ] All 8 files modified (code-review-patterns, ticket-invocation, perf-anti-patterns, documentation-rtm, verification-and-planning, tdd-workflow, commit-conventions, script-engineer-conventions)
- [ ] All commits created with proper formatting and co-author trailer
- [ ] No forbidden patterns in changes (TODO, TBD, [dates], YYYY-MM-DD, harness tokens)
- [ ] Line counts verified for each file (increases as expected, no dropped lines)
- [ ] git status shows all expected file changes

- [ ] **Final verification step: Run audit validator again**

```bash
cd /Users/russelllaing/al-dev-shared
python3 scripts/validate-knowledge-quality.py --path profile-al-dev-shared/knowledge
```

Expected output: HIGH severity issue count should drop from 8 to 0 (or 1-2 if false positives remain).

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-22-knowledge-quality-fixes.md`. 

**Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration with quality checkpoints

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints for review

Which approach would you prefer?
