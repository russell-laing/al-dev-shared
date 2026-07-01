# Solution Plan Template

Canonical authoring template for the solution plan written by
`solution-architect` and passed to downstream review/approval flows.

```markdown
## Solution Plan: [Feature Name]

### Overview
[1-2 paragraphs: what we're building, why this approach]

### BC SaaS Data-Access Constraints

Business Central SaaS does **not** support direct SQL queries or database access. All data validation, querying, and manipulation must use AL constructs:

- **SetFilter** — Filter records by field conditions
- **Query objects** — Define and execute structured data queries
- **AL logic** — Inline validation and data transformation

#### Red Flags (SQL Hazards)

- ❌ "Query the database directly" → Use AL Query object instead
- ❌ "Run SQL to validate..." → Use SetFilter + FINDSET/FIND instead
- ❌ "Stored procedures" → Not available in SaaS; use AL codeunits

#### Pattern

When the plan says "validate data," ask: "In SaaS or on-prem?" If SaaS, require AL-based validation in the spec.

See `bash-safe-patterns.md` for SQL-safety patterns in plan task descriptions.

### Architecture

#### Component Design

[Describe the major components (codeunits, tables, pages) and how they
interact. One entry per AL object or logical grouping that carries a
distinct responsibility.]

#### Data Flow

[Describe the primary data path: from user action through the AL event
chain to persistence or output. Include field-level notes for critical
data paths.]

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
Validate: [exact shell command confirming this task is done — e.g., `rg -n "procedure ValidatePostingDate" src/` or `jq -r '.version' .dev/output.json`]

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
- `Validate:` is required. Use an exact shell command when the task can be machine-checked; use `Validate: [manual] — [description]` only when the validation cannot be automated.
- Tasks here are the architect's logical implementation units. They inform
  (but do not replace) the detailed execution and review flow performed by
  `plan`, `plan-final-review`, and downstream implementation
  workflows.

### Acceptance Criteria

Use numbered criteria in one of four allowed forms:

**Structural check** — file or symbol existence:
1. `src/Codeunit/SalesPostingGuard.Codeunit.al` exists and contains `procedure ValidatePostingDate`
2. `src/PageExtension/SalesOrderExt.PageExt.al` contains reference to `SalesPostingGuard.ValidatePostingDate`

**Gate check** — tool exit code or existing skill gate used during downstream
implementation or review:
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
