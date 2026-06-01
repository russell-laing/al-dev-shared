# Maintainer Tooling Naming Convention

**Last updated:** 2026-05-29

This document defines how maintainer tools and their outputs are named. The
`naming-convention-lens` agent flags drift against it on every `/plugin-health`
run; `scripts/tests/test_naming_convention.py` enforces the **lens-agent** rule
mechanically. Keep this doc and those two checkers in sync.

## Tools

### Lens agents — ENFORCED

Pattern: `{dimension}-{object}-lens-{aspect}`

- `dimension` ∈ `design` | `quality`
- `object` ∈ `agent` | `skill`
- `aspect` — a short kebab-case noun for the specific lens (e.g. `tool-hygiene`,
  `bloat`, `name-fit`)

Examples: `design-agent-lens-tool-hygiene`, `quality-skill-lens-bloat`.

**Exception:** `naming-convention-lens` is a cross-object lens (it judges both
agents and skills) and intentionally omits the `{dimension}` and `{object}`
words. It is the only allowed deviation from the pattern.

### Maintainer skills — ADVISORY

Pattern: `{verb}-{object}-{aspect}`

- `verb` ∈ `review` | `analyze` | `audit` | `plan` | `sync` | …
- `object` ∈ `skill` | `agent` | `knowledge` | `map` | `plugin`

Examples: `audit-quality`, `review-agent-map`, `al-dev-map-suggestions-verify`.

This rule is advisory: pre-existing skills that predate the convention
(`projection-sync`, `align-harness-repos`) are grandfathered. New skills SHOULD
conform; the `naming-convention-lens` flags non-conforming names as Low-severity
suggestions rather than hard failures.

## Outputs

### Living docs — overwritten in place, no date

Pattern: `al-dev-{object}-{kind}.md`

Examples: `al-dev-plugin-map.md`, `al-dev-agent-map.md`, `al-dev-skill-quality.md`,
`al-dev-agent-quality.md`, `al-dev-knowledge-quality.md`, `al-dev-plugin-graph.md`.

### Point-in-time artifacts — dated

Pattern: `{dir}/YYYY-MM-DD-{surface}-{kind}.md`

- `surface` ∈ `plugin` (the distributed `profile-al-dev-shared/` surface)
  | `tooling` (the maintainer `.claude/` surface)

Examples: `docs/health/2026-05-29-plugin-health.md`,
`docs/health/2026-05-29-tooling-health.md`.

## Harness neutrality

Every output named above must use generic vocabulary (no harness-specific
tokens such as tool names or settings paths). The maintainer tooling itself may
remain harness-specific, but its produced documents must not.
