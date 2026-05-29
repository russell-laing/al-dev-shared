# Solution Plan Template

```markdown
## Solution Plan: [Feature Name]

### Overview
[1-2 paragraphs: what we're building, why this approach]

### Object Design

**Tables / Table Extensions:**
- Object ID 50xxx: "[Name]"
  Purpose: [1 sentence]
  Pattern reference: [file:line or "none — rationale"]
  Fields: [list key fields with IDs and types]

**Pages / Page Extensions:**
- Object ID 51xxx: "[Name]"
  Purpose: [1 sentence]
  Pattern reference: [file:line or "none — rationale"]
  Modifications: [what's being added/changed]

**Codeunits:**
- Object ID 52xxx: "[Name]" (Interface: "[Interface Name]")
  Purpose: [1 sentence]
  Pattern reference: [file:line or "none — rationale"]
  Key Methods: [list with signatures]

**Enums** (if any):
- Object ID 53xxx: "[Name]"
  Pattern reference: [file:line or "none — rationale"]
  Values: [list]

### BC Base App Integration
- Extends Table: [Base Table Name] (ID: [Base ID])
- Subscribes to Events: [Event names]
- Calls Base App: [Procedures/APIs used]

### Data Validation Rules
[List all validation rules with triggers]

### Testability Design
[How dependency injection/interfaces enable testing]

### Implementation Notes
[Object ID assignments, naming conventions, special
considerations]

### Implementation Tasks

**Task 1: [name]**
Files: [files to create or modify]
Gotcha: [one project-specific pitfall — e.g., "object names must be ≤30 chars; verify before creating" or "var parameters from AL MCP must be verified before use in subscribers"]
Validate: [exact shell command confirming this task is done — e.g., `grep -rn "procedure ValidatePostingDate" src/` or `grep -c "error AL" .dev/compile-errors.log | grep -q "^0$"`]

**Task 2: [name]**
Files: ...
Gotcha: ...
Validate: ...

**Task N: [name]**
Files: ...
Gotcha: ...
Validate: ...

---

#### Gotcha and Validate Rules

- `Gotcha:` is required. Write `Gotcha: none — [rationale]` rather than omitting it.
- `Validate:` is required. Write `Validate: [manual] — [description]` rather than omitting it.
- Tasks here are the architect's logical implementation units. They inform (but do not replace) the detailed sub-task checklist produced by `writing-plans`.

### Acceptance Criteria

Use numbered criteria in one of four allowed forms:

**Structural check** — file or symbol existence:
1. `src/Codeunit/SalesPostingGuard.Codeunit.al` exists and contains `procedure ValidatePostingDate`
2. `src/PageExtension/SalesOrderExt.PageExt.al` contains reference to `SalesPostingGuard.ValidatePostingDate`

**Gate check** — tool exit code or existing skill gate:
3. `al-compile` exits 0 with no new errors in `.dev/compile-errors.log`

**Pattern check** — a required or forbidden pattern in changed code:
4. No `Error(StrSubstNo(` appears in new or modified files

**Manual check** — user or tester validation that cannot be machine-checked:
5. [manual] Posting is blocked when order date is before work date

Unlabelled prose criteria are not permitted. Each criterion must be numbered and use one of the four forms above.

### Winning Approach Rationale
Based on [Architect X]'s [approach], incorporating [Y]
from [Architect Z].

Chosen because:
- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

Trade-offs accepted:
- [Limitation 1]: Acceptable because [reason]
- [Limitation 2]: Mitigated by [strategy]
```
