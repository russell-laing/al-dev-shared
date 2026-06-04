# Solution Architect Research Patterns

Reference for `al-dev-solution-architect`. Evidence hierarchy and MCP tool
selection for the research phase.

## Evidence hierarchy (strict — do not skip a higher tier when available)

**AL LSP** (semantic correctness, preferred when the harness exposes it) →
**AL MCP** (base app / package symbols) → **text search** (pattern matching,
weakest).

Record each symbol claim with `file:line` and a one-sentence reason it is the
best match.

## MCP tools available

| Tool | Use for |
|------|---------|
| AL Code Intelligence MCP | AL symbols, procedures, events, tables |
| Microsoft Docs MCP | Official BC and AL documentation |
| AL Dependency MCP | Cross-package dependency lookups |

## Complexity routing

SIMPLE → single analogue + minimal design; MEDIUM → 2–3 candidate patterns;
COMPLEX → full alternatives analysis before selecting.
