# Solution Plan Template

```markdown
## Solution Plan: [Feature Name]

### Overview
[1-2 paragraphs: what we're building, why this approach]

### Object Design

**Tables / Table Extensions:**
- Object ID 50xxx: "[Name]"
  Purpose: [1 sentence]
  Fields: [list key fields with IDs and types]

**Pages / Page Extensions:**
- Object ID 51xxx: "[Name]"
  Purpose: [1 sentence]
  Modifications: [what's being added/changed]

**Codeunits:**
- Object ID 52xxx: "[Name]" (Interface: "[Interface Name]")
  Purpose: [1 sentence]
  Key Methods: [list with signatures]

**Enums** (if any):
- Object ID 53xxx: "[Name]"
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
