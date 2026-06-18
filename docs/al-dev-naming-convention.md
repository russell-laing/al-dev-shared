# Maintainer Tooling Naming Convention

**Last updated:** 2026-05-29

This document defines how maintainer tools and their outputs are named. The
`naming-convention-lens` agent flags drift against it on every `/plugin-health-audit`
run; `scripts/tests/test_naming_convention.py` enforces the **lens-agent** rule
mechanically. Keep this doc and those two checkers in sync.

## Tools

### Lens agents — ENFORCED

Pattern: `{dimension}-{object}-lens-{aspect}`

- `dimension` is one of `design` or `quality`
- `object` is one of `agent` or `skill`
- `aspect` — a short kebab-case noun for the specific lens (e.g. `tool-hygiene`,
  `bloat`, `name-fit`)

Examples: `design-agent-lens-tool-hygiene`, `quality-skill-lens-bloat`.

**Exception:** `naming-convention-lens` is a cross-object lens (it judges both
agents and skills) and intentionally omits the `{dimension}` and `{object}`
words. It is the only allowed deviation from the pattern.

### Maintainer skills — ADVISORY

Pattern: `{verb}-{object}-{aspect}`

- `verb` is one of `review`, `analyze`, `audit`, `plan`, `sync`, …
- `object` is one of `skill`, `agent`, `knowledge`, `map`, `plugin`

Examples: `plugin-health-audit`, `review-agent-map`, `verify-map-suggestions`.

This rule is advisory: existing names that deviate are grandfathered — see
[Grandfathered exceptions](#grandfathered-exceptions). New skills SHOULD
conform; the `naming-convention-lens` flags non-conforming names as Low-severity
suggestions rather than hard failures.

## Outputs

### Living docs — overwritten in place, no date

Pattern: `al-dev-{object}-{kind}.md`

Examples: `al-dev-skills-map.md`, `al-dev-agent-map.md`, `al-dev-knowledge-quality.md`,
`al-dev-plugin-graph.md`.

### Point-in-time artifacts — dated

Pattern: `{dir}/YYYY-MM-DD-{surface}-{kind}.md`

- `surface` is one of `plugin` (the distributed `profile-al-dev-shared/`
  surface) or `tooling` (the maintainer `.claude/` surface)

Examples: `docs/health/2026-05-29-plugin-health.md`,
`docs/health/2026-05-29-tooling-health.md`.

## Harness neutrality

Every output named above must use generic vocabulary (no harness-specific
tokens such as tool names or settings paths). The maintainer tooling itself may
remain harness-specific, but its produced documents must not.

## Grandfathered exceptions

These names predate or intentionally deviate from `{verb}-{object}-{aspect}` and
are accepted; lenses should not re-flag them:

- `plugin-health-audit`, `plugin-health-discover`, `plugin-health-report` —
  health-sweep entry-point and workflow-phase family; the `{object}-{aspect}-{verb}`
  ordering predates the `{verb}-{object}-{aspect}` convention and is kept for the
  family's recognisability.
- `projection-sync` — established verb-object name; regenerates harness projections from canonical source.
- `align-harness-repos` — validate-with-optional-fix workflow; name retained for recognisability.
- `al-dev-consolidate` — user-facing artifact-consolidation workflow.
- `sync-documentation-maps`, `-collect`, `-write` — workflow-phase family naming
  (the `-apply` member was renamed from `-wait` for clarity).
- `sync-documentation-maps-{agent|skill}-{audit|update}` — sync workflow agent
  family; named for the workflow they serve.
- `implement-health-plan`, `ingest-friction-log`, `plan-health-findings`,
  `record-health-dispositions`, `revise-health-plan` — health-loop phase family;
  each is named for the workflow stage it serves, and a rename has high blast
  radius across the loop (cross-references in sibling phase skills and the
  health-loop breadcrumb), so it is not recommended.
