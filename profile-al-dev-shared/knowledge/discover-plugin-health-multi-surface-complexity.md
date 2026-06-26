# Discover-Plugin-Health Multi-Surface Complexity Analysis

## Current State

`discover-plugin-health` handles 3 modes: plugin-only, tooling-only, both. Within phases 1–3 (file-list building, context aggregation, parallel dispatch), multi-surface branching occurs at:

- **Phase 1:** Different glob patterns per surface + conditional `--since` scoping
- **Phase 2:** Surface-specific map parsing (plugin vs tooling maps have different depths)
- **Phase 3:** Surface-specific lens exclusions (tooling excludes `surface-placement`; plugin excludes `maintainer-handoff`)

## Proposed Future Refactoring (deferred)

Extract a `discover-single-surface` sub-skill to encapsulate phases 1–3 for one surface, then have a dispatcher invoke it once per surface, collecting results for phases 4–6 (findings assembly).

**Current plan:** Keep `discover-plugin-health` as-is (phases 1–5) and defer multi-surface optimization to a future session. This allows the phase-split improvements to be designed and evaluated separately.

**Rationale:** Multi-surface decomposition is architecturally orthogonal to the phase-split question. Addressing it now would couple two distinct design decisions.
