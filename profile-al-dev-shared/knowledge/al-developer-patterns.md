# AL Developer Patterns and Conventions

Referenced by: `developer-tdd` and `developer-traditional` agents

## Standard AL Patterns

### RecordRef Operations

Pattern for operations on record references with error handling. Use RecordRef for dynamic table access when the table isn't known at compile time. Always validate the table ID before operations.

```al
procedure ReadFieldDynamically(TableId: Integer; RecordId: RecordId; FieldNo: Integer): Text
var
    RecRef: RecordRef;
    FieldRef: FieldRef;
begin
    RecRef.Open(TableId);
    if not RecRef.Get(RecordId) then
        exit('');

    FieldRef := RecRef.Field(FieldNo);
    exit(FieldRef.Value);
end;
```

Key operations:

- `RecRef.Open(TableID)` — open a table by ID
- `RecRef.Get(RecordID)` — retrieve a specific record
- `RecRef.FindSet()` — iterate through filtered records
- `RecRef.Field(FieldNo)` — access a field dynamically
- Always wrap in `if RecRef.Get()` guards — RecordRef operations fail silently otherwise

### Query Performance Best Practices

When writing queries, use filters to reduce record set scope; use `SetLoadFields` when you only need a subset of fields to limit column reads.

**SetLoadFields Pattern:** Specify only the fields you need before calling FindSet when the procedure reads a small subset of the record. Omitting SetLoadFields loads ALL columns from the table, which is expensive with large tables.

```al
procedure GetOrderAmountsByCustomer(CustomerId: Code[20]) Total: Decimal
var
    SalesHeader: Record "Sales Header";
begin
    SalesHeader.SetLoadFields("Amount", "Amount Including VAT");
    SalesHeader.SetRange("Sell-to Customer No.", CustomerId);
    
    if SalesHeader.FindSet() then
        repeat
            Total += SalesHeader."Amount Including VAT";
        until SalesHeader.Next() = 0;
end;

procedure GetOrderAmountsByCustomerBad(CustomerId: Code[20]) Total: Decimal
var
    SalesHeader: Record "Sales Header";
begin
    // WITHOUT SetLoadFields: All ~40 columns are loaded from the table
    // This is slow even if we only need two fields
    SalesHeader.SetRange("Sell-to Customer No.", CustomerId);
    
    if SalesHeader.FindSet() then
        repeat
            Total += SalesHeader."Amount Including VAT";
        until SalesHeader.Next() = 0;
end;
```

**Why it matters:** `SetLoadFields` limits the query to specified fields; without it, SQL reads entire rows. For tables with BLOBs, memos, or many columns, this difference is dramatic. Skip it when you will read most or all fields anyway.

**Avoid FINDSET in loops:** Never call FindSet inside a loop — collect IDs first, then process:

```al
procedure ProcessCustomers(FromDate: Date; ToDate: Date)
var
    Customer: Record Customer;
    CustomerIds: List of [Code[20]];
    CustomerId: Code[20];
begin
    // GOOD: One scan, one loop over results
    Customer.SetLoadFields("No.");
    Customer.SetFilter("Last Sales Date", '>=' + Format(FromDate));
    if Customer.FindSet() then
        repeat
            CustomerIds.Add(Customer."No.");
        until Customer.Next() = 0;
    
    // Now process in batches
    foreach CustomerId in CustomerIds do
        ProcessCustomerBatch(CustomerId, FromDate, ToDate);
end;
```

### Record Modification Patterns

**Single-record updates:** Call `LockTable` before `Get` when you need pessimistic locking for a read-modify-write cycle. Then call `Modify` with `true` to allow triggers/validations.

```al
procedure SetCreditLimit(CustomerId: Code[20]; NewLimit: Decimal)
var
    Customer: Record Customer;
begin
    Customer.LockTable();
    Customer.Get(CustomerId);
    Customer."Credit Limit" := NewLimit;
    Customer.Modify(true); // true = run OnModify triggers
end;
```

**Why:** Without `LockTable`, another user can modify the record between your Get and Modify, causing lost updates or stale data. Use it only when that concurrency protection is required, because it holds a database lock until the transaction ends.

**Batch updates:** Use `ModifyAll` for multiple records matching a filter — it's optimized for bulk operations.

```al
procedure SetStatusForDueOrders()
var
    SalesHeader: Record "Sales Header";
begin
    SalesHeader.SetFilter("Due Date", '<' + Format(Today()));
    SalesHeader.SetRange(Status, SalesHeader.Status::Open);
    SalesHeader.ModifyAll(Status, SalesHeader.Status::Overdue, true); // true = run triggers
end;
```

**Commit() inside FindSet loops is dangerous:**

Calling `Commit()` while iterating a `FindSet()` result may reset the server
cursor state on some BC versions, causing records to be re-processed or skipped.
It also holds locks across the full loop duration.

```al
// ❌ BAD: Commit inside FindSet — cursor may reset
procedure ProcessPending(var Entry: Record "Email Retry Entry")
begin
    if Entry.FindSet() then
        repeat
            Commit();                // Dangerous: cursor may reset after commit
            RetryRecord(Entry);
        until Entry.Next() = 0;
end;

// ✅ GOOD: collect keys first, then iterate the collected set
procedure ProcessPending(var Entry: Record "Email Retry Entry")
var
    TempEntry: Record "Email Retry Entry" temporary;
begin
    if Entry.FindSet() then
        repeat
            TempEntry := Entry;
            TempEntry.Insert();
        until Entry.Next() = 0;

    if TempEntry.FindSet() then
        repeat
            Entry.Get(TempEntry."Entry No.");
            RetryRecord(Entry);
            Commit();              // Safe: iterating temp table, not live cursor
        until TempEntry.Next() = 0;
end;
```

### FilterGroup Usage

Use `FilterGroup` to separate user-visible filters (FilterGroup 0) from system filters (FilterGroup 2). This is essential in pages to prevent users from accidentally removing your required filters.

```al
procedure ApplySystemFilter(var Customer: Record Customer; MinCreditLimit: Decimal)
begin
    // FilterGroup(0) = user-visible filters (can be edited in UI)
    Customer.FilterGroup(0);
    Customer.SetFilter("Credit Limit", '>=' + Format(MinCreditLimit));
    
    // FilterGroup(2) = system filters (hidden from users, cannot be removed)
    Customer.FilterGroup(2);
    Customer.SetFilter(Blocked, '=%1', Customer.Blocked::" ");
end;
```

**Why it matters:** If you mix user and system filters in FilterGroup 0, users can accidentally delete your business logic filters. FilterGroup(2) is immutable in the UI.

---

## Common AL Mistakes to Avoid

### Event Subscriber Skeleton

Event subscribers must match the event's exact signature (including `var` parameters). Use the strongest available AL symbol evidence to verify the procedure signature before writing a subscriber.

```al
[EventSubscriber(ObjectType::Codeunit, Codeunit::"Sales-Post", 'OnAfterPostSalesDoc', '', false, false)]
local procedure OnAfterPostSalesDoc(var SalesHeader: Record "Sales Header"; var GenJnlPostLine: Codeunit "Gen. Jnl.-Post Line"; CommitIsSuppressed: Boolean)
begin
    // Your code here
end;
```

**Subscriber attributes:**

- `ObjectType` — Type of object publishing the event (Codeunit, Table, Page, etc.)
- `Object ID` — the object's name or ID
- `Event name` — the exact event procedure name
- `Element` — context (leave empty for codeunits)
- `SkipOnMissingLicense` — false for required behavior; true to skip silently if license missing
- `SkipOnMissingPermission` — same pattern for permission checks

**Critical:** The procedure signature must match EXACTLY, including parameter names and `var` modifiers. If the event has `var SalesHeader`, your subscriber must too.

**How to verify:** Prefer `AL semantic navigation` when available. Otherwise use `AL symbol MCP` to inspect the publishing procedure, or run scoped text search against the base app source for the event name and signature.

### Performance Anti-Pattern: N+1 Queries

**Problem:** Loading one record at a time inside a loop causes N database calls for N records — exponential slowdown.

```al
// ❌ BAD: N+1 queries — one Get() per customer
procedure ProcessCustomersWithOrders()
var
    SalesHeader: Record "Sales Header";
    Customer: Record Customer;
begin
    if SalesHeader.FindSet() then
        repeat
            Customer.Get(SalesHeader."Sell-to Customer No.");  // DB call per record!
            ProcessOrder(SalesHeader, Customer);
        until SalesHeader.Next() = 0;
end;

// ✅ GOOD: Load all customers once, process in-memory
procedure ProcessCustomersWithOrdersBetter()
var
    SalesHeader: Record "Sales Header";
    CustomerCache: Dictionary of [Code[20], Record Customer];
begin
    LoadCustomerCache(CustomerCache);  // Single filtered read
    if SalesHeader.FindSet() then
        repeat
            ProcessOrder(SalesHeader, CustomerCache.Get(SalesHeader."Sell-to Customer No."));
        until SalesHeader.Next() = 0;
end;
```

Use batch operations (`ModifyAll`, `DeleteAll`) or load-first-then-process instead of row-by-row DB calls inside loops.

### Unreferenced Variables

**Problem:** Unused variables indicate dead code, clutter the codeunit, and confuse readers about data flow.

```al
// ❌ BAD: Unused variables
procedure CalculateTotal(var SalesHeader: Record "Sales Header"): Decimal
var
    SalesLine: Record "Sales Line";
    Customer: Record Customer;  // Declared but never used
    CurrencyCode: Code[10];     // Declared but never used
begin
    SalesHeader.CalcFields(Amount);
    exit(SalesHeader.Amount);
end;

// ✅ GOOD: Only needed variables declared
procedure CalculateTotal(var SalesHeader: Record "Sales Header"): Decimal
begin
    SalesHeader.CalcFields(Amount);
    exit(SalesHeader.Amount);
end;
```

Remove unused variables during code review or refactoring. They should not appear in GREEN or REFACTOR phases.

### Missing Access = Internal on Extension-Private Codeunits

A codeunit without an `Access` modifier defaults to `Access = Public`,
meaning any other extension can call it directly — bypassing any page-level
authorization guard.

If a codeunit is only ever called from within this extension (not exposed as
a public API), declare it `Access = Internal`.

```al
// ❌ BAD: public by default — callable from any extension
codeunit 50504 "Email Retry Mgt."
{
    procedure RetryRecord(var Entry: Record "Email Retry Entry")
    begin
        // Auth guard is only on the calling page; bypassed here
    end;
}

// ✅ GOOD: restricted to this extension
codeunit 50504 "Email Retry Mgt."
{
    Access = Internal;
    procedure RetryRecord(var Entry: Record "Email Retry Entry")
    begin
        // Caller is always from this extension
    end;
}
```

**Decision rule:** If the codeunit is not documented as part of the
extension's public API and is not intended for external callers, always add
`Access = Internal`.

### Unsafe Singleton Setup Initialization (GetSafe Race)

The `if not Get() then Insert()` pattern is a concurrent-insert race.
Two sessions can both fail the `Get()` check simultaneously and both
call `Insert()` — one throws a duplicate-key error. This is especially
dangerous inside event subscriber context (which runs inside another
active transaction).

```al
// ❌ BAD: race condition — concurrent sessions both Insert()
procedure GetSetupSafe()
begin
    if not Get() then begin
        Init();
        Insert();
    end;
end;

// ✅ GOOD option A — insert-or-ignore
procedure GetSetupSafe()
begin
    if not Get() then begin
        Init();
        if not Insert() then
            Get();   // Another session already inserted — just read it
    end;
end;

// ✅ GOOD option B — pre-create in install, never insert at runtime
//   OnInstallAppPerCompany creates the record once.
//   GetSetupSafe() only reads; never inserts.
procedure GetSetupSafe()
begin
    if not Get() then
        Error(SetupRecordMissingErr);
end;
```

Prefer option B when the feature has an install codeunit — pre-creating the
record in `OnInstallAppPerCompany` is the cleanest and safest approach.

## Error Handling Rules

### String Substitution with Labels

Use `Error(label, args)` instead of `Error(StrSubstNo(...))` to satisfy AA0231.

Good:

```al
Error(SomeLabel, fieldValue);
```

Bad:

```al
Error(StrSubstNo(SomeLabel, fieldValue));
```

### User-Facing Errors

User-facing error messages should be clear, actionable, and avoid internal technical
details. The message should explain WHAT went wrong and HOW to fix it, not system
internals.

#### BAD: Internal error message

```al
if (PurchHeader.Status <> PurchHeader.Status::Open) then
    Error('Cannot update PurchHeader with Status=' + Format(PurchHeader.Status));
```

#### GOOD: User-friendly error message

```al
if (PurchHeader.Status <> PurchHeader.Status::Open) then
    Error('Purchase order must be Open to make changes. Status: %1',
        Format(PurchHeader.Status));
```

The GOOD version:

- Names the action that failed ("Purchase order must be in Open status")
- Shows the current state ("Current status: X")
- Is readable without understanding internal field names

### Error('') Is Forbidden

Calling `Error('')` with an empty string (or no-argument form) produces a blank
error dialog. The user sees nothing useful and the failure is invisible.

**Rule:** Every `Error()` call must pass a non-empty Label as its first argument.
No exceptions.

```al
// ❌ BAD: silent failure
if not CanProceed then
    Error('');

// ✅ GOOD: named label
OperationNotAllowedErr: Label 'This operation is not allowed in the current state.';
...
if not CanProceed then
    Error(OperationNotAllowedErr);
```

For `TryFunction` return paths, do NOT call `Error('')` to propagate failure —
instead let the `TryFunction` return `false` naturally and let the caller handle it:

```al
// ❌ BAD in a TryFunction: swallows the real error with a blank one
[TryFunction]
procedure TrySend(): Boolean
begin
    if not Email.Send(Message) then
        Error('');   // blank; original Send error lost
end;

// ✅ GOOD in a TryFunction: let false propagate; caller checks the return value
[TryFunction]
procedure TrySend(): Boolean
begin
    if not Email.Send(Message) then
        exit(false);   // or just: Email.Send(Message);  (TryFunction traps it)
end;
```

### Handling Missing Information

When required data is not provided or cannot be computed, ask for
clarification explicitly instead of assuming defaults. Document the
assumption and what the user should provide.

#### Example: Requesting Missing Information

In a sales invoice workflow, if the customer's shipping address is
missing, provide a clear error asking for it:

```al
procedure ValidateShippingAddress(SalesHeader: Record "Sales Header") Result: Boolean
begin
    if SalesHeader."Ship-to Address" = '' then begin
        // Clear, specific request with next steps
        Error(
            'Shipping address required for Order %1.' +
            ' Go to Sales Orders, select this order,' +
            ' choose Actions > Edit Ship-To Address.',
            SalesHeader."No.");
    end;
    Result := true;
end;
```

The error message:

- Identifies what is missing (Shipping address)
- For which record (Order #X)
- How to provide it (exact menu path)

## AL Naming Conventions

- Object names must be ≤30 characters
- Use AL prefix convention (e.g., prefix `ARR` for array processing codeunits)
- Be descriptive: `PaymentProcessor` is better than `Proc`

---

## Shell Command Conventions

AL projects frequently have directories with spaces in their names (e.g., `SRC/Table Extension/`). In some harnesses, backslash-escaped whitespace in shell commands (`SRC/Table\ Extension/file.al`) can trigger avoidable permission prompts or brittle command parsing. Follow these rules when constructing shell commands.

### Rule 1: Single file — read the file directly

When inspecting a known specific file, read it directly with the active harness capability instead of building a shell search command. This avoids path construction entirely and is faster.

```text
✅ Read "SRC/Table Extension/SalesLine.TableExt.al"
❌ Shell: rg -n '...' SRC/Table\ Extension/SalesLine.TableExt.al
```

### Rule 2: Multi-file search — prefer recursive patterns with `.`

This pattern keeps the command portable across repos and avoids permission
prompts caused by explicit directory names with spaces.

Use recursive patterns with `.` as the root. `rg` or `grep` can traverse directories transparently, so no spaced path ever appears in the command.

```bash
# ✅ Preferred — no explicit path, rg recurses from .
rg -n '^\s*(field|procedure|table)' . --glob "*.al"

# ✅ Also safe — grep recurses from .
grep -rn --include="*.al" -E '^\s*(field|procedure|table)' .

# ❌ Avoid — explicit spaced path with backslash escaping is brittle
rg -n '...' SRC/Table\ Extension/SalesLine.TableExt.al
```

### Rule 3: When an explicit path is unavoidable — double-quote it

Quoting is the safe fallback when a command must target one concrete file and
cannot rely on recursive traversal from the current directory.

If you must reference a file by path directly, always wrap in double quotes.

```bash
# ✅ Quoted — no prompt
rg -n '...' "SRC/Table Extension/SalesLine.TableExt.al"

# ❌ Backslash-escaped — more brittle across harnesses
rg -n '...' SRC/Table\ Extension/SalesLine.TableExt.al
```
