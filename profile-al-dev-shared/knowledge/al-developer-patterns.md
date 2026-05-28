# AL Developer Patterns and Conventions

Referenced by: `al-dev-developer` agent

## Standard AL Patterns

### RecordRef Operations
Pattern for operations on record references with error handling. Use RecordRef for dynamic table access when the table isn't known at compile time. Always validate the table ID before operations.

```al
procedure ReadFieldDynamically(TableId: Integer; RecordId: RecordId; FieldNo: Integer): Text
var
    RecRef: RecordRef;
    FieldRef: FieldRef;
begin
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
When writing queries, use filters to reduce record set scope; always use `SetLoadFields` to limit column reads.

**SetLoadFields Pattern:** Specify only the fields you need before calling FindSet. Omitting SetLoadFields loads ALL columns from the table, which is expensive with large tables.

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

**Why it matters:** `SetLoadFields` limits the query to specified fields; without it, SQL reads entire rows. For tables with BLOBs, memos, or many columns, this difference is dramatic.

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

**Single-record updates:** Always call `LockTable` before `Get` to prevent concurrent modifications. Then call `Modify` with `true` to allow triggers/validations.

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

**Why:** Without `LockTable`, another user can modify the record between your Get and Modify, causing lost updates or stale data. LockTable holds a database lock until the transaction ends.

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

Event subscribers must match the event's exact signature (including `var` parameters). Use the AL symbols MCP to verify the procedure signature before writing a subscriber.

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

**How to verify:** Use `al_search_objects` and `al_get_object_definition` MCPs to inspect the publishing procedure, OR search the base app source for the event name and signature.

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

## Bash Command Conventions

AL projects frequently have directories with spaces in their names (e.g., `SRC/Table Extension/`). Backslash-escaped whitespace in bash commands (`SRC/Table\ Extension/file.al`) triggers permission prompts. Follow these rules when constructing bash commands.

### Rule 1: Single file — use the Read tool, not bash grep

When inspecting a known specific file, use the Read tool. This avoids path construction entirely and is faster.

```text
✅ Read "SRC/Table Extension/SalesLine.TableExt.al"
❌ Bash: grep -E '...' SRC/Table\ Extension/SalesLine.TableExt.al
```

### Rule 2: Multi-file search — use recursive patterns with `.`

Use `--include` glob patterns with `.` as the root. `grep` and `find` traverse directories transparently, so no spaced path ever appears in the command.

```bash
# ✅ Safe — no explicit path, grep recurses from .
grep -rn --include="*.al" -E '^\s*(field|procedure|table)' .

# ✅ Safe — find recurses without explicit directory names
find . -name "*.al" -exec grep -l "95010\|95008" {} \;

# ❌ Avoid — backslash-escaped space triggers prompts
grep -E '...' SRC/Table\ Extension/SalesLine.TableExt.al
```

### Rule 3: When an explicit path is unavoidable — double-quote it

If you must reference a file by path directly, always wrap in double quotes.

```bash
# ✅ Quoted — no prompt
grep -E '...' "SRC/Table Extension/SalesLine.TableExt.al"

# ❌ Backslash-escaped — triggers prompt
grep -E '...' SRC/Table\ Extension/SalesLine.TableExt.al
```
