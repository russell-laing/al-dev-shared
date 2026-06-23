# Health Filter Contract

Canonical source of truth for the repo-local self-healing workflow filter
contract.

## Public Command Contract

The public stages in scope use this vocabulary:

```text
[--surface plugin|tooling|both] [--dimension design|quality|naming|all]
```

That means the shared public flag vocabulary is
`--surface plugin|tooling|both` plus
`--dimension design|quality|naming|all`.

Defaults:

```text
--surface both
--dimension all
```

`--resume` is valid only for `/audit-plugin-health` and
`/discover-plugin-health`.

`/report-plugin-health` preserves and validates the filter metadata written by
`/discover-plugin-health`; it does not expose a public `--dimension` argument.

## Surface Mapping

- `plugin` -> `profile-al-dev-shared/`
- `tooling` -> `.claude/`
- `both` -> union of the two concrete surfaces

## Dimension Mapping

- `design` -> design lenses only
- `quality` -> quality lenses only
- `naming` -> naming-convention lens only
- `all` -> union of the three concrete dimensions

## Per-Dimension Lens Roster

Ground-truth counts for the missing-lens completeness check in
`discover-plugin-health` Phase 3. The `remaining_lenses` set must empty
to zero by the end of a successful sweep; this table is the baseline for
each dimension-scoped run.

| Dimension | LLM lens agents | Static lenses | Total expected |
|-----------|-----------------|---------------|----------------|
| design    | 10 per surface (11 total − 1 surface exclusion) | 1 (tool-hygiene) | 11 per surface |
| quality   | 8 | 2 (agent-structure, skill-structure) | 10 |
| naming    | 0 | 1 (naming-convention-lens) | 1 |
| all       | 18 per surface (19 total − 1 surface exclusion) | 4 | 22 per surface |

**Per-surface LLM exclusions (reduce 19 → 18):**

- `plugin` surface: `design-skill-lens-maintainer-handoff` excluded
- `tooling` surface: `design-skill-lens-surface-placement` excluded

**Static lenses** are run by `scripts/health_static_lenses.py` — they write
`.dev/<date>-plugin-health-lens-<name>.json` artifacts identical to LLM agent output
and are treated as completed lenses by the `remaining_lenses` check.

## Friction Source

`/ingest-plugin-friction` is a discover-stage source that is **not a lens**. Its
findings files are named `YYYY-MM-DD-<surface>-friction-findings.md`. The
`select_health_artifacts.py` selector regex intentionally does **not** match this
name (the `friction-findings` token fails the `(design|quality|naming)?-?(findings|health)`
grammar), so friction findings are consumed only via
`/report-plugin-health --findings <path>`, never by automatic selection.

Friction findings are grouped under pseudo-lens blocks whose heading names the
dimension in parentheses:

- `### Friction: Workflow (design) Findings` -> dimension `design`
- `### Friction: Instruction Quality (quality) Findings` -> dimension `quality`
- `### Friction: Naming (naming) Findings` -> dimension `naming`

When `/report-plugin-health` consumes a friction findings file, it maps each
friction block to the dimension named in its parenthetical suffix for
`dimensions:` validation and dossier grouping. No dedicated dossier section is
added; friction findings appear under the existing Design / Quality / Naming
headings.

### Recurrence

For prior-artifact lookup when the report processes a friction findings file
(path ends in `-friction-findings.md`), the prior-artifact selector MUST use
`--kind friction-findings` (not `--kind findings`), so recurrence comparison
stays within the friction family:

```bash
select_health_artifacts.py --directory docs/health --kind friction-findings --surface <surface> --offset 1
```

The `--kind friction-findings` mode is added by the companion selector
extension task. Until the report skill is updated to invoke this mode, all
friction findings will appear as new on every run (recurrence counts will be
unsound). This is a known v1 limitation.

## Findings Metadata

`/discover-plugin-health` findings files should carry provenance metadata near
the top of the file:

```yaml
---
surface: tooling
dimensions:
  - quality
source_contract: .claude/knowledge/health-filter-contract.md
resume_mode: false
---
```

The `surface` value is singular because each findings file is written for one
surface. `dimensions` records the concrete dimensions requested for that run.

## Dossier Metadata

`/report-plugin-health` must preserve upstream provenance and validate that the
dossier sections match the findings metadata.

If a standard section is outside the requested dimensions, keep the section
heading and write `_Not requested in this run._` rather than `_No issues
found._`.

## Plan Provenance

`/plan-plugin-findings` must write the accepted-filter provenance into the plan
header:

```yaml
health_filters:
  surfaces:
    - tooling
  dimensions:
    - quality
```

Apply filters in this order:

1. surface
2. dimension
3. object-type routing (`--skills` or `--agents`)
4. finding-type routing

## Legacy Compatibility

Legacy five-column ledger rows remain readable:

```text
| Object | Issue | Disposition | Date | Evidence / note |
```

They map to:

- `surface = unknown`
- `dimension = unknown`

until migration or manual cleanup fills in the concrete values.

## Resume Contract

`--resume` reuses the stored concrete filter set from the interrupted discovery
run.

- Matching `--surface` and `--dimension` values -> resume is allowed
- Mismatched values -> stop and ask for a fresh non-resume run
- Report, disposition, and planning stages never accept `--resume`

## Migration Provenance

The ledger migration key is:

```text
(object, finding, date)
```

Migration is best-effort, not fully deterministic.

Inference precedence:

1. explicit migration override map
2. matching findings metadata or findings-section context on disk
3. matching dossier section context on disk

If provenance cannot be proven from live artifacts, write `unknown` for the
unresolved field and list the row in the migration audit report for manual
cleanup.
