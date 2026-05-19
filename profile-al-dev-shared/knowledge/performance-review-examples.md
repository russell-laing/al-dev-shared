# Performance Review Code Examples

Referenced by: `al-dev-performance-reviewer` agent

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

**Good:**
```al
rec.FindSet();
repeat
  // Load all data first, then process in memory
  // or use a JOIN/FILTER to reduce database calls
until rec.Next() = 0;
```

### Inefficient FINDSET Usage

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
