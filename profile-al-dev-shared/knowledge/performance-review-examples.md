# Performance Review Examples

Used by: `performance-reviewer` agent

These are review examples for spotting common performance issues in AL/BC.
Treat them as illustrative patterns, not production-ready snippets to copy verbatim.

> **Foundation:** These examples illustrate patterns defined in `knowledge/perf-anti-patterns-prompt.md`. Read the taxonomy file first for severity levels, exclusion rules, and the complete pattern catalog. These examples are visual companions to the taxonomy.

## Common Performance Issues

### N+1 Query Pattern

**Bad:**
```al
rec.FindSet();
repeat
  subRec.Get(rec.Id);  // Query inside loop — executes for every record
  // Process subRec
until rec.Next() = 0;
```

**Good (Batch Load Pattern):**
```al
var
    OrderList: Record "Sales Header";
    LineList: Record "Sales Line";
    OrderLines: Dictionary of [Integer, List of [Record "Sales Line"]];
    LineKey: Integer;
begin
    // Load ALL related records in one query
    LineList.SetLoadFields("Document No.", "Line No.", "Document Type", Amount);
    LineList.FindSet();
    repeat
        if not OrderLines.ContainsKey(LineList."Line No.") then
            OrderLines.Add(LineList."Line No.", new List of [Record "Sales Line"]);
        OrderLines.Get(LineList."Line No.").Add(LineList);
    until LineList.Next() = 0;
    
    // Process in memory — no more database queries
    foreach LineKey in OrderLines.Keys do
        ProcessOrderLines(OrderLines.Get(LineKey));
end;
```

**Good (JOIN Pattern):**
```al
var
    OrderHeader: Record "Sales Header";
    OrderLine: Record "Sales Line";
begin
    // Use JOINs to avoid N+1 — one SQL query instead of 1 + N
    OrderLine.SetLoadFields("Amount", "Unit Price", Quantity);
    OrderLine.SetRange("Document Type", OrderHeader."Document Type"::"Order");
    if OrderLine.FindSet() then
        repeat
            // Line data is already loaded; no additional Get() needed
            ProcessOrderLine(OrderLine);
        until OrderLine.Next() = 0;
end;
```

### Inefficient FINDSET Usage

**Why it matters:** Missing the basic `if FindSet()` guard or relying on inefficient access patterns can turn routine scans into avoidable work on larger tables.

**Bad:**
```al
rec.SetCurrentKey(Name);
rec.SetRange(Name, SearchValue);
rec.FindSet();  // Default sort, slow on large tables
repeat
  // Process record
until rec.Next() = 0;
```

**Good:**
```al
rec.SetCurrentKey(Name);  // Set most efficient key
rec.SetRange(Name, SearchValue);
if rec.FindSet() then
  repeat
    // Process record
  until rec.Next() = 0;
```

### Missing Table Indexes

**Why it matters:** Queries that filter on non-key fields often degrade into full-table scans, which become disproportionately expensive as data volume grows.

**Bad:**
```al
// Table has frequent lookups on DateField, but no index
rec.SetRange(DateField, MinDate, MaxDate);
rec.FindSet();  // Slow full table scan
```

**Good:**
```al
// Add index on DateField in table definition
// Then queries on DateField use the index
table MyTable
{
  fields
  {
    field(1; Id; Integer) { }
    field(2; DateField; Date) { }
  }
  keys
  {
    key(Key1; Id) { Clustered = true; }
    key(Key2; DateField) { }  // Add this for performance
  }
}
```

### Blocking Operations in Triggers

**Why it matters:** Heavy work inside interactive triggers delays user actions and can amplify contention during busy periods.

**Bad:**
```al
trigger OnInsert()
begin
  // Heavy processing inside trigger
  ProcessAllRelatedRecords();  // Blocks user input
end;
```

**Good:**
```al
trigger OnInsert()
begin
  // Queue for background processing
  EnqueueJob(Rec);  // Returns immediately
end;
```

### Unnecessary Loops

**Why it matters:** Repeating expensive operations inside loop bounds adds avoidable database or compute cost on every iteration.

**Bad:**
```al
for i := 1 to Rec.Count() do  // Count() executes query each iteration
  // Process i
```

**Good:**
```al
count := Rec.Count();
for i := 1 to count do
  // Process i
```

### Missing SetLoadFields

**Bad (loads ALL columns):**
```al
var
    Customer: Record Customer;  // ~50+ fields in table
begin
    Customer.SetRange("Last Sales Date", CalcDate('-30D', Today()), Today());
    if Customer.FindSet() then
        repeat
            // Only need "No." and "Name"
            LogCustomer(Customer."No.", Customer.Name);
        until Customer.Next() = 0;
end;
```

**Good (loads only needed columns):**
```al
var
    Customer: Record Customer;
begin
    Customer.SetLoadFields("No.", Name);  // Only these columns from SQL
    Customer.SetRange("Last Sales Date", CalcDate('-30D', Today()), Today());
    if Customer.FindSet() then
        repeat
            LogCustomer(Customer."No.", Customer.Name);
        until Customer.Next() = 0;
end;
```

**Impact:** Without SetLoadFields, SQL reads all ~50 columns from the Customer table even though you only need 2. For tables with BLOBs or large memo fields, this adds measurable latency and memory pressure.
