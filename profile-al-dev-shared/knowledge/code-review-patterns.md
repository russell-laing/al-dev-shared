# Code Review Patterns and Severity

Referenced by: `al-dev-code-review` and `al-dev-expert-reviewer` agents

## Common AL Issues

### Naming Convention Violations

**Pattern:** Object names must be ≤30 characters; use AL prefix conventions.

Bad:
- `VeryLongDescriptiveNameThatExceedsTheCharacterLimit` (too long)
- `veryLongName` (lowercase; AL prefers PascalCase)

Good:
- `PaymentProcessor` (≤30 chars, descriptive)
- `ARRAnalyzer` (prefix convention for array processing)

#### Examples in AL Code

##### BAD: Violates character limit (>30 chars) and post-fix naming

```al
codeunit 50100 "LongNameViolationCodeunitPostFix" { }
table 50101 "PurchaseOrderApprovalDataTable" { }
```

##### GOOD: Follows 30-char limit and pre-fix convention

```al
codeunit 50100 "PurchaseApprovalProcessor" { }
table 50101 "PurchaseApprovalData" { }
```

##### Detection during review

- Count characters in object names: if > 30, flag it
- Check naming order: pre-fix (category first, e.g., "Purchase Approval")
  vs post-fix (category last, bad)
- Abbreviations: OK: "PO" for Purchase Order;
  NOT OK: "PAPD" for Purchase Approval Processing Details

##### Variable Naming — Avoid Abbreviations

BEFORE (Poor):
```al
procedure CalculateQty(DocLine: Record "Sales Line"; var Qty: Decimal)
var
    tmpRec: Record "Item Ledger Entry";
    idx: Integer;
    mxLines: Integer;
begin
    mxLines := DocLine.Count();
    Qty := 0;
    
    if (DocLine.FindSet()) then
        repeat
            idx += 1;
            Qty += DocLine.Quantity;
        until DocLine.Next() = 0;
end;
```

AFTER (Good):
```al
procedure CalculateOrderQuantity(DocumentLine: Record "Sales Line"; var TotalQuantity: Decimal)
var
    TemporaryInventoryRecord: Record "Item Ledger Entry";
    LineIndex: Integer;
    MaximumLineCount: Integer;
begin
    MaximumLineCount := DocumentLine.Count();
    TotalQuantity := 0;
    
    if (DocumentLine.FindSet()) then
        repeat
            LineIndex += 1;
            TotalQuantity += DocumentLine.Quantity;
        until DocumentLine.Next() = 0;
end;
```

What improved: Variable names spell out intent (`tmpRec` → `TemporaryInventoryRecord`, `idx` → `LineIndex`). Parameter names are descriptive (`Qty` → `TotalQuantity`).

##### Procedure Naming — Reflect Intent, Not Implementation

BEFORE (Poor):
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

AFTER (Good):
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

What improved: Procedure names describe the action (`Proc1` → `UpdateItemUnitCost`, `DoIt` → `ClearItemInventoryCache`). Intent is clear to reviewers without reading the body.

##### Table and Field Naming — Use Full Words in Public Interfaces

BEFORE (Poor):
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

AFTER (Good):
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

What improved: Field names are unambiguous and full-word (`Ord No` → `Order Number`, `Cust No` → `Customer Number`). No abbreviations in public table definitions.

### Event Subscriber Mismatches

**Pattern:** Procedure signature must match event signature exactly (var parameters, order, types).

Bad:
```al
// Event: OnBeforeInsert(var Rec: Record; var IsHandled: Boolean)
// Subscriber signature mismatch:
local procedure OnRecordInsert(rec: Record)  // Missing IsHandled parameter
begin
  // Process
end;
```

Good:
```al
local procedure OnRecordInsert(var rec: Record; var isHandled: Boolean)
begin
  // Process
  isHandled := true;
end;
```

### Missing Error Handling

**Pattern:** All external operations should have error handling.

Bad:
```al
procedure CallExternalAPI(url: Text): Text
begin
  response := HttpClient.Get(url);  // No error check
  exit(response.Content);
end;
```

Good:
```al
procedure CallExternalAPI(url: Text): Text
begin
  if not HttpClient.Get(url, response) then
    Error('API call failed: %1', HttpClient.GetLastErrorMessage());
  exit(response.Content);
end;
```

### Incorrect AL Patterns

**Pattern:** Using deprecated or non-idiomatic AL patterns.

Bad:
```al
// Using StrSubstNo instead of label format
Error(StrSubstNo('Invalid value: %1', fieldValue));
```

Good:
```al
// Using label with parameters
Error(InvalidValueErr, fieldValue);

// In label definition:
// InvalidValueErr = 'Invalid value: %1';
```

## Severity Classification

### Critical
- Security vulnerabilities (data exposure, injection attacks)
- Data loss risks (unhandled exceptions in deletes, overwrites)
- Compilation failures
- Breaks existing functionality

**Action:** Block merge; fix before proceeding.

### High
- Performance bottlenecks (N+1 queries, missing indexes)
- Missing error handling in critical paths
- Incorrect AL patterns that violate best practices
- Incorrect event subscriber signatures

**Action:** Request changes; document why blocking.

### Medium
- Code style violations (naming, formatting)
- Naming inconsistencies (e.g., `UserID` vs `UserId`)
- Documentation gaps in public functions
- Potential maintainability issues

**Action:** Request changes; allow override if justified.

### Low
- Formatting and whitespace
- Comment clarity
- Optimization opportunities that don't block performance
- Code organization suggestions

**Action:** Suggest; don't block.

## Review Checklist

Before approving code:
- [ ] No critical issues
- [ ] High issues addressed (or documented)
- [ ] Naming conventions followed
- [ ] Error handling present
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] Tests pass (if applicable)
