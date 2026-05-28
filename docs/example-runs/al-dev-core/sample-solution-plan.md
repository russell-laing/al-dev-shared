# Example Solution Plan

Goal: Add a posting-date validation to a sales-order extension.

Files:
- `src/Codeunit/SalesPostingGuard.Codeunit.al`
- `src/PageExtension/SalesOrderExt.PageExt.al`

Acceptance criteria:
- validation blocks posting dates before work date
- page surfaces the validation message consistently
