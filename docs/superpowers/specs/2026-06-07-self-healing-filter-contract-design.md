# Self-Healing Filter Contract Design

## Purpose

Standardize surface and dimension filtering across the self-healing workflow
from health discovery through implementation-plan generation.

The public workflow stages in scope are:

1. `/plugin-health-audit`
2. `/record-health-dispositions`
3. `/plan-health-findings`

The internal `/plugin-health-discover` and `/plugin-health-report` stages must
preserve the same filter provenance because they produce the artifacts consumed
downstream.

This design does not extend filtering into plan execution or post-change
validation.

## Public Command Contract

Every public stage in scope accepts:

```text
[--surface plugin|tooling|both] [--dimension design|quality|naming|all]
```

The defaults are:

```text
--surface both
--dimension all
```

`/plugin-health-audit` additionally accepts `--resume`. The flag remains
specific to audit discovery because it continues interrupted lens dispatch.
Disposition and planning stages do not accept `--resume`.

Invalid values fail before any artifact is read or written.

## Canonical Definition

The implementation must add:

```text
.claude/knowledge/health-filter-contract.md
```

This repo-local maintainer knowledge file is the canonical operational source
of truth for health-filter semantics. It must define:

- valid surface and dimension values;
- default values and union semantics;
- surface-to-directory mappings;
- the explicit dimension-to-lens mapping;
- downstream filter ordering;
- findings, dossier, ledger, and plan metadata representation;
- legacy `unknown` behavior;
- audit-only `--resume` semantics and mismatch handling.

The active self-healing skills must reference this file instead of maintaining
independent copies of the filter definitions. A skill may summarize the values
in its argument-parsing section, but the canonical file controls whenever
wording or behavior differs.

The generated maintainer guide must include a concise summary of the canonical
contract and link to the source file. The guide remains a generated
documentation surface, not a second source of truth.

## Filter Semantics

### Surface

- `plugin` selects `profile-al-dev-shared/`.
- `tooling` selects the repo-local maintainer tooling surface.
- `both` is the union of `plugin` and `tooling`.

Artifacts remain separated by surface. A request for one surface must never
substitute an artifact from another surface.

### Dimension

- `design` selects design-lens findings.
- `quality` selects quality-lens findings.
- `naming` selects naming-convention findings.
- `all` is the union of `design`, `quality`, and `naming`.

`all` is a command filter, not an individual finding dimension. Stored findings
and disposition rows use exactly one concrete dimension.

### Filter Ordering

Downstream filters apply in this order:

1. surface
2. dimension
3. existing object-type routing (`--skills` or `--agents`)
4. existing finding-type routing such as `trim`, `merge`, or `connect`

This order prevents a later filter from drawing findings from a surface or
dimension excluded by the caller.

## Workflow

### Audit

`/plugin-health-audit` parses the public filters and passes them, plus optional
`--resume`, to `/plugin-health-discover`.

Discovery builds only the requested surface file lists and dispatches only the
lenses belonging to the requested dimensions. The dimension-to-lens mapping
must be explicit rather than inferred from agent-name substrings at runtime.

### Report

`/plugin-health-report` preserves the selected surface and dimension metadata.
It writes only findings matching the discovery request. A narrow report may
retain the standard dossier headings, but excluded dimensions must be clearly
marked as not requested rather than reported as having no issues.

### Disposition

`/record-health-dispositions` selects the latest dossier independently for each
requested surface, then filters its findings by dimension before presenting
the decision gate.

Ledger matching uses:

```text
surface + dimension + object + issue essence
```

This prevents similarly worded findings from different surfaces or dimensions
from suppressing one another.

### Planning

`/plan-health-findings` filters accepted disposition rows by surface and
dimension before applying its existing object-type and finding-type routes.
The generated plan records the active surface and dimension filters in its
header.

If a requested filter produces no accepted findings, planning stops cleanly
without creating a plan.

## Artifact Contract

### Findings And Dossiers

Findings and health dossiers remain one file per surface:

```text
docs/health/YYYY-MM-DD-<surface>-findings.md
docs/health/YYYY-MM-DD-<surface>-health.md
```

Each file records machine-readable filter provenance near its header:

```yaml
---
surface: plugin
dimensions:
  - design
  - quality
---
```

The `dimensions` list contains the concrete dimensions included in that run.
An `all` request is stored as all three concrete values.

Existing artifact selectors continue to select by filename surface. Consumers
use the metadata to validate dimension compatibility.

The current artifact for a surface represents the most recent audit contract
for that surface. A later narrow run supersedes an earlier broad run on the same
date. A downstream request that is broader than the current artifact stops for
that surface and instructs the user to rerun the audit with the broader
dimension filter. It must not treat dimensions absent from the metadata as
having no findings.

### Disposition Ledger

The disposition table gains `Surface` and `Dimension` columns:

```text
| Surface | Dimension | Object | Finding | Disposition | Date | Evidence / note |
```

New rows always store one concrete surface and one concrete dimension. They
never store `both` or `all`.

### Generated Plans

Every generated health-findings plan includes:

```yaml
health_filters:
  surfaces:
    - plugin
  dimensions:
    - quality
    - naming
```

The lists contain concrete selected values. This metadata records planning
provenance; it does not cause plan execution to reapply the filters.

## Legacy Compatibility

Existing findings and dossiers without metadata remain readable:

- infer surface from the artifact filename;
- infer finding dimension from its dossier section;
- treat `Design suggestions` as `design`;
- treat `Quality findings` as `quality`;
- treat `Naming violations` as `naming`.

Implementation performs a one-time deterministic schema migration of the
existing table when the first new-format row is written:

- add the `Surface` and `Dimension` columns to the header and separator;
- infer values from matching historical dossiers where unambiguous;
- store `unknown` for a value that cannot be inferred safely;
- preserve the original object, finding, disposition, date, evidence, and row
  order.

An ambiguous legacy row:

- with `Dimension=unknown` is included only for an `all` dimension request;
- with `Surface=unknown` is included only for a `both` surface request;
- is not included in a narrow surface or dimension request;
- is reported to the user as requiring explicit ledger migration.

The `unknown` sentinel is valid only for migrated legacy rows. New rows must
always use concrete values.

## Resume Contract

`--resume` continues only an interrupted audit discovery.

Resume artifacts must record the original concrete surfaces and dimensions.
On resume:

1. load the interrupted run metadata;
2. compare it with any explicitly supplied filters;
3. reuse the stored filters when the caller supplies only `--resume`;
4. fail on a filter mismatch rather than mixing lens outputs;
5. dispatch only incomplete lenses within the stored filter set.

If every selected lens is already complete, discovery skips dispatch and
assembles the findings from disk.

## Error Handling

- A missing artifact for one requested surface is reported and that surface is
  skipped.
- Processing stops if no requested surface has a usable artifact.
- A dossier whose metadata excludes the requested dimension is skipped with a
  precise rerun instruction.
- A narrow disposition request with no findings leaves the ledger unchanged.
- A narrow planning request with no accepted rows creates no plan.
- Resume metadata mismatches fail before lens outputs are assembled.
- Ambiguous legacy rows are reported rather than silently classified.

## Documentation

Update the active skill contracts and generated maintainer documentation so
examples use the standardized parameters:

```text
/plugin-health-audit --surface both --dimension all
/record-health-dispositions --surface plugin --dimension naming
/plan-health-findings --surface tooling --dimension quality
```

The documentation must explain that `--resume` is audit-only.
It must point maintainers to
`.claude/knowledge/health-filter-contract.md` for the complete definitions.

## Testing

Automated coverage must verify:

- default `both` and `all` behavior at every public stage;
- each individual dimension;
- both individual surfaces and their union;
- discovery dispatches only lenses in the selected dimensions;
- report metadata and excluded-dimension wording;
- disposition filtering before the decision gate;
- ledger matching includes surface and dimension;
- planning filter order;
- generated plan provenance;
- canonical contract coverage for every required definition;
- active skills reference the canonical contract;
- generated maintainer documentation links to the canonical contract;
- legacy dossier section inference;
- unambiguous legacy ledger inference;
- ambiguous legacy rows are excluded from narrow requests;
- zero-result downstream requests do not modify artifacts;
- resume reuses stored filters;
- resume rejects surface or dimension mismatches.

Run the applicable repository validators after implementation, including the
maintainer-guide generator tests and Markdown checks.

## Acceptance Criteria

1. The three public stages expose the same surface and dimension vocabulary and
   defaults.
2. A narrow audit can remain narrow through disposition and plan generation.
3. Every new finding and disposition has explicit concrete surface and
   dimension provenance.
4. Historical artifacts remain consumable without unsafe guesses.
5. `--resume` cannot combine outputs from different filter sets.
6. Surface and dimension semantics are memorialized in the canonical repo-local
   health-filter contract and are not independently redefined by workflow
   skills.
7. No source implementation is changed by this design-spec commit.
