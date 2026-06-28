# Maintainer Tooling Naming Convention

**Last updated:** 2026-05-29

This document defines how maintainer tools and their outputs are named. The
`naming-convention-lens` agent flags drift against it on every `/audit-plugin-health`
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

**Dimension boundary:** semantic name/body drift (a name that implies one verb
or scope while the body does another) is a **quality** concern checked by the
`quality-agent-lens-name-fit` and `quality-skill-lens-name-fit` lenses;
pattern/convention conformance against this document is the **naming** dimension
checked by `naming-convention-lens`. These two concerns must stay in separate
lenses — do not merge name-fit checks into the naming-convention lens.

**Split decision gate:** the single cross-object `naming-convention-lens` is
acceptable only while one shared rule set covers both objects. If future policy
adds materially different agent vs skill naming rules, replace the singleton with
object-specific naming lenses rather than growing the singleton.

### Maintainer skills — ADVISORY

Pattern: `{verb}-{object}-{aspect}`

- `verb` is one of `review`, `analyze`, `audit`, `plan`, `sync`, …
- `object` is one of `skill`, `agent`, `knowledge`, `map`, `plugin`

Examples: `audit-plugin-health`, `review-agent-map`, `verify-map-suggestions`.

This rule is advisory: existing names that deviate are grandfathered — see
[Grandfathered exceptions](#grandfathered-exceptions). New skills SHOULD
conform; the `naming-convention-lens` flags non-conforming names as Low-severity
suggestions rather than hard failures.

The repo-local `regenerate_agent_projections` skill is currently grandfathered
until the compat surface is retired.

The repo-local maintainer command `/plan-plugin-findings` is the current name
for the workflow that used to be wired to `/verify-map-suggestions`.

### Python maintainer tooling files — ADVISORY

Pattern: `snake_case.py`, with a verb-first stem that states the file's primary
behavior.

Top-level CLI entrypoints under `scripts/` SHOULD also use `snake_case.py` so
the import path, test naming, and direct file invocation all align.

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

- `regenerate_agent_projections`
