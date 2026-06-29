# Solution Architect Research Patterns

Reference for `solution-architect`. Evidence hierarchy and MCP tool
selection for the research phase.

## Evidence hierarchy (strict — do not skip a higher tier when available)

**AL LSP** (semantic correctness, preferred when the harness exposes it for
definitions, references, document symbols, hover/type information, and
rename/refactor impact checks) → **AL MCP** (base app / package symbols) →
**text search** (scoped pattern matching, weakest — label it `text search`).

Record each symbol claim with `file:line` and a one-sentence reason it is the
best match.

## MCP tools available

| Tool | When to use |
|------|-------------|
| `al_get_object_definition` | Extending base tables (see existing fields, avoid conflicts) |
| `al_find_references` | Subscribing to events (find available events) |
| `al_search_objects` | Unsure what base object to use (find related objects) |
| `ask_bc_expert` | Architecture questions, pattern selection |
| `find_bc_knowledge` | Best practices, performance/security concerns |
| `microsoft_docs_search` | Official syntax, breaking changes, API references |

## Complexity routing

- **SIMPLE:** skip research; use project context only.
- **MEDIUM:** use available AL semantic evidence + BC Code Intelligence.
- **COMPLEX:** use all semantic, knowledge, and documentation tools; comprehensive research.
