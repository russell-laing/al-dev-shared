# /al-dev-fix Detailed Examples

This document provides detailed walkthroughs of two common fix scenarios.

## Example 1: Trivial Fix

```text
User: "/fix Customer validation allows negative credit limits"

You (analysis):
"Trivial - missing validation check in Customer table extension"

You (to developer):
"Add validation in CustomerExt OnValidate trigger for Credit Limit field.
 Error if value < 0."

Developer: [Implements]

You (to user):
"Fix complete → CustomerExt.Table.al

 Added validation: Credit Limit cannot be negative
 Compilation: ✅ Success

 Ready to test?"
```

**Time: 3-4 minutes**

## Example 2: Non-Trivial Fix

```text
User: "/fix Sales posting fails when credit limit is exactly 0"

You (analysis):
"Non-trivial - need to understand posting flow and where check happens"

You (spawn architect):
"Analyze why posting fails when credit limit is exactly 0"

Architect:
"Root cause: CreditValidator uses > instead of >= for comparison.
 Fix: Change comparison logic in ValidateCredit method.
 Risk: Ensure 0 is treated as 'no limit' if that's business rule."

You (review):
"Approach makes sense. Clarify: is 0 'no limit' or 'zero limit'?
 [Ask user or check existing code patterns]"

[User clarifies or you determine from code]

You (to developer):
"Fix comparison in CreditValidator.Codeunit.al ValidateCredit method.
 Change > to >= and document that 0 means [no limit/zero limit]."

Developer: [Implements]

You (to user):
"Fix complete → CreditValidator.Codeunit.al

 Root cause: Comparison logic excluded exactly 0
 Fix: Changed > to >= in ValidateCredit method
 Documented: 0 is treated as [no limit/zero limit]

 Compilation: ✅ Success
 Risk: Watch for edge cases where 0 limit is set intentionally

 Ready to test?"
```

**Time: 12-15 minutes**
