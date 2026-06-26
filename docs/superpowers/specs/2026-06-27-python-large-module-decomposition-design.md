# Python Large Module Decomposition Design

## Goal

Reduce the remaining oversized packaged Python modules into smaller, single-purpose package modules without changing their observable behavior, import contracts, or CLI entrypoints.

This design covers Step 3 from [docs/superpowers/plans/2026-06-26-python-scripts-package-foundation-handoff.md](/Users/russelllaing/al-dev-shared/.worktrees/python-scripts-large-module-decomposition/docs/superpowers/plans/2026-06-26-python-scripts-package-foundation-handoff.md).

## Current Context

The Step 2 package foundation and health-surface refactor already landed on `master`:

- packaged roots exist under `scripts/al_dev_tools/`
- top-level `scripts/*.py` health commands remain as compatibility wrappers
- tests still treat `scripts/tests/` as the regression surface

The main remaining Step 3 debt is concentrated in four large modules:

- `scripts/al_dev_tools/docs/map_doc_sections.py` — inventory discovery, reference extraction, marker replacement, health summarization, and multiple renderers in one file
- `scripts/al_dev_tools/docs/maintainer_guide_sections.py` — contract parsing, validation, gap analysis, topology helpers, and document rendering in one file
- `scripts/al_dev_tools/health/health_disposition_store.py` — event-store I/O, current-state materialization, markdown rendering, legacy compatibility, matching, findings parsing, and CLI behavior in one file
- `scripts/al_dev_tools/health/check_ledger_staleness.py` — row parsing, store loading, closure resolution, repo path lookup, git inspection, and CLI handling in one file

## Phase Split

### Phase 3A: Docs Decomposition

Phase 3A decomposes only the docs package pair:

- `scripts/al_dev_tools/docs/map_doc_sections.py`
- `scripts/al_dev_tools/docs/maintainer_guide_sections.py`

The split should create package-local modules grouped by responsibility:

- shared models and constants
- inventory or contract parsing
- graph, topology, or gap computation
- section rendering
- document orchestration

The existing filenames stay in place as compatibility facades that re-export the current public functions used by tests and calling scripts.

### Phase 3B: Health Decomposition

Phase 3B decomposes only the health package pair:

- `scripts/al_dev_tools/health/health_disposition_store.py`
- `scripts/al_dev_tools/health/check_ledger_staleness.py`

The split should create package-local modules grouped by responsibility:

- data models and normalization helpers
- event-store reading and appending
- current-state materialization and index building
- markdown rendering and legacy compatibility helpers
- findings parsing and ledger matching
- ledger parsing and closure resolution
- repo or git queries
- CLI entrypoints

The existing filenames stay in place as compatibility facades, and the top-level `scripts/*.py` wrappers remain unchanged unless a wrapper still carries non-trivial logic.

## Architecture

The decomposition should preserve the current external surface while narrowing internal files.

Each large module becomes a thin coordination layer or compatibility facade over smaller sibling modules in the same package. New modules should be named by responsibility rather than by technical layer, so the code that changes together stays together and tests can target one concern at a time.

`main(argv: list[str] | None = None) -> int` should exist only in CLI-facing modules. Library modules should expose pure or mostly pure functions that accept explicit inputs and return structured values instead of reading global state or exiting the process directly.

## Module Boundaries

### Docs Package

`map_doc_sections` should separate:

- inventory models and metadata parsing
- skill, agent, and knowledge reference extraction
- marker-span detection and marked-section replacement
- plugin-health summarization
- Mermaid or markdown renderers
- document update planning and application

`maintainer_guide_sections` should separate:

- workflow contract model definitions
- frontmatter parsing and contract loading
- contract validation
- producer, consumer, and artifact status analysis
- gap computation
- stage- or journey-specific rendering
- section assembly

### Health Package

`health_disposition_store` should separate:

- normalization helpers and shared keys
- JSONL shard path and event validation helpers
- event-store reading and append operations
- current-state materialization and index computation
- markdown view rendering
- Markdown-history compatibility helpers
- findings-file parsing and match logic
- CLI-only dispatch helpers

`check_ledger_staleness` should separate:

- ledger row model and parsing
- store-backed and file-backed row loading
- object-to-path resolution
- closure resolution and integrity warnings
- git-backed stale-open detection helpers
- staged-file checks
- CLI argument parsing and reporting

## Compatibility Rules

- Preserve the existing public imports used by `scripts/tests/` and current wrappers.
- Keep compatibility re-exports in the current module filenames before deleting or renaming callable symbols.
- Keep top-level `scripts/*.py` health commands as wrappers during Step 3.
- Do not mix broad I/O modernization or error-translation changes into this phase unless required to preserve behavior after a move.
- Do not change generated document or report formats unless a current test already proves the existing format.

## Error Handling

The decomposition should be behavior-preserving.

- If a split reveals a hidden coupling, move the coupled helpers together instead of forcing an artificial boundary.
- If a helper is used both by a renderer and a CLI path, keep it in a library module and keep exit-code translation at the CLI edge.
- If an existing test depends on a name imported from a large module, the facade module should continue to export that name.
- If a new module boundary would require changing external command behavior, defer that change to Step 4.

## Testing

Phase 3A validation should focus on docs behavior first:

```bash
python3 -m unittest scripts.tests.test_generate_map_doc_sections scripts.tests.test_generate_maintainer_guide scripts.tests.test_generate_plugin_graph
```

Phase 3B validation should focus on health behavior first:

```bash
python3 -m unittest scripts.tests.test_health_disposition_store scripts.tests.test_health_benchmark_adapter scripts.tests.test_health_disposition_store_match scripts.tests.test_check_ledger_staleness scripts.tests.test_select_health_artifacts scripts.tests.test_check_disposition_store_consistency scripts.tests.test_validate_health_loop_state scripts.tests.test_assemble_health_findings scripts.tests.test_split_multilens_findings scripts.tests.test_migrate_health_disposition_jsonl
```

The Step 3 anchor after both phases remains:

```bash
python3 -m unittest scripts.tests.test_generate_map_doc_sections scripts.tests.test_generate_maintainer_guide scripts.tests.test_generate_plugin_graph scripts.tests.test_health_disposition_store scripts.tests.test_health_benchmark_adapter
```

## Rollout

1. Decompose the docs package pair first while leaving current callable names in place.
2. Run the docs-focused regression suite and fix facade or import drift before moving on.
3. Decompose the health package pair second while leaving current callable names and wrappers in place.
4. Run the health-focused regression suite and then the combined Step 3 anchor.
5. Write the next rolling handoff for Step 4 I/O and error-handling standardization after Step 3 is stable.

## Non-Goals

- Do not remove compatibility wrappers in `scripts/*.py`.
- Do not change repo-wide Python tooling, formatter policy, or validator architecture in this phase.
- Do not merge docs and health decomposition into one commit sequence if that makes regressions harder to localize.
- Do not treat this phase as permission to rewrite behavior that belongs to Step 4 or Step 5.
