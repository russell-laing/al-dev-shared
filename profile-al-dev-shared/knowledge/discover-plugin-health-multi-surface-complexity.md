# Discover-Plugin-Health Multi-Surface Complexity Analysis

## Current State

`discover-plugin-health` handles 3 modes: plugin-only, tooling-only, both. Within phases 1–3 (file-list building, context aggregation, parallel dispatch), multi-surface branching occurs at:

- **Phase 1:** Different glob patterns per surface + conditional `--since` scoping
- **Phase 2:** Surface-specific map parsing (plugin vs tooling maps have different depths)
- **Phase 3:** Surface-specific lens exclusions (tooling excludes `surface-placement`; plugin excludes `maintainer-handoff`)

## Companion Surface Registration

The multi-surface expansion is no longer deferred. Companion package surfaces are
registered through the canonical companion surface contract, and per-surface dispatch
must preserve legacy `both` behavior while allowing `companions` and per-package IDs.
