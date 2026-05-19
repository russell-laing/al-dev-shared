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
Use batch operations instead of record-by-record processing. Load all data first, then process in-memory when possible.

### Unreferenced Variables
Remove unused variables. They clutter the code and indicate dead code paths.

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
Wrap in Error() function with user-friendly message text. Avoid exposing internal IDs or technical details.

### Handling Missing Information
If implementation requires clarification from the user, stop and ask. Document what information is missing and why it matters.

## AL Naming Conventions

- Object names must be ≤30 characters
- Use AL prefix convention (e.g., prefix `ARR` for array processing codeunits)
- Be descriptive: `PaymentProcessor` is better than `Proc`
