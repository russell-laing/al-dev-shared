# Solution Architect Schema Mapping Decisions

Decision guide for mapping AL object fields to the 5-column schema table. Used by solution-architect during the Output Format step.

Document all external field/table references with existence verification in your solution plans:

| Field/Table | Source | Exists? | Evidence Source | Rationale | Risk |
|-------------|--------|---------|-----------------|-----------|------|
| G/L Register No. | G/L Entry | NO | AL MCP | Use "Entry No." (PK) instead | Low |
| Customer Type | Customer | YES | AL LSP | Link to code in AC_CUSTOMER_TYPE | Low |
| Document No. | Purch. Header | YES | text search | Primary document identifier; text-verified only | Medium |

**Format per mapping:**

- **[Field Name]** in [Source Table]: [YES/NO]
  - Evidence Source: [AL LSP / AL MCP / text search / unverified]
  - Evidence: [semantic operation, MCP query, or exact file:line]
  - Alternative: [If field doesn't exist, what should be used?]
  - Rationale: [Why this choice is correct]
  - Risk: [Low/Medium/High — data integrity implications]

> **Definition:** A symbol is *required* if the implementation plan's code
> templates or task steps explicitly reference it by name (procedure call,
> field access, or object instantiation).

If a required external symbol is `unverified`:

- **CRITICAL path field** (implementation cannot proceed without it): mark as `BLOCKED` in the Schema Mapping table and stop. Do not write implementation tasks — return the plan with a `BLOCKED` section listing the unverified fields and required resolution steps.
- **Optional field** (implementation can continue with an alternative): document the risk as a `HIGH` item in the Schema Mapping table and continue with a concrete alternative design.

**Why this section matters:**

- Developers verify field existence against AL symbols BEFORE writing code
- Prevents compile errors from field misreferences mid-implementation
- Documents design choices for future reference
- Speeds up schema review during code review phase
