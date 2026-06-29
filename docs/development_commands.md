# Development Commands

Common commands for maintaining the shared plugin surface.

## Validation (All Harnesses)

```bash
# Validate that shared source has no harness-specific leakage
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared

# Validate agent structure (frontmatter, tools, model assignment)
python3 scripts/validate_lens_agents.py --path profile-al-dev-shared/agents

# Validate knowledge file quality
python3 scripts/validate_knowledge_quality.py --path profile-al-dev-shared/knowledge

# Validate that skills honour the artifact-contract matrix
python3 scripts/validate_artifact_contracts.py
```

## Pre-commit Neutrality Gate

A checked-in hook at `.githooks/pre-commit` blocks any commit that fails
harness neutrality, lens-policy sync, or leaves generated projections stale.
Enable it once per clone:

```bash
git config core.hooksPath .githooks
```

The hook runs, in order:

- `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared`
- `python3 scripts/validate_lens_agents.py`
- a projections-current check (regenerates to a temp dir and diffs against
  `profile-al-dev-shared/generated/`)
- staged markdownlint for `profile-al-dev-shared/agents/**/*.md` and
  `profile-al-dev-shared/skills/**/*.md`
- a doc-map freshness warning when staged skill/agent changes omit the tracked
  documentation maps
- `python3 scripts/check_ledger_staleness.py --staged` (non-blocking warning on
  execution failure)
- `python3 scripts/validate_health_loop_state.py --staged`
- `python3 scripts/validate_maintainer_contracts.py`
- `python3 scripts/validate_artifact_leaks.py` to block staged scratch files and
  raw `docs/superpowers/plans|specs` markdown

Bypass with `git commit --no-verify` only when intentionally committing a
work-in-progress; the hook is fast local feedback, not a security control.

## Projection (Harness-Native Artifacts)

```bash
# Regenerate all harness projections after shared agent/policy changes
python3 scripts/generate_agent_projections.py
```

## Documentation Maps (Mermaid Diagrams)

The documentation maps (`docs/skills-map.md`, `docs/agent-map.md`, `docs/plugin-graph.md`) and maintainer guide pages (`docs/maintainer_tooling.md`, `docs/maintainer_tooling/*.md`) contain auto-generated sections with Mermaid diagrams. These are regenerated from the shared plugin source:

```bash
# Regenerate all documentation map sections
# - Layer 1 lifecycle diagrams
# - Layer 2 per-skill drilldowns (with Phase<N> nodes)
# - Agent catalog and dependency graphs
python3 scripts/generate_map_doc_sections.py

# Regenerate plugin dependency graph separately
python3 scripts/generate_plugin_graph.py

# Regenerate the maintainer guide's generated sections
# (summary overview, stage diagrams, run order, artifact roles, contract appendix)
# from the `workflow:` frontmatter blocks in .claude/skills/*/SKILL.md
python3 scripts/generate_maintainer_guide.py
```

**Do not hand-edit** sections between `<!-- BEGIN GENERATED: ... -->` and `<!-- END GENERATED: ... -->` markers; changes will be overwritten on the next regeneration. Use the skills-based interface (`/sync-map-documentation`) for interactive updates.
Local HTML exports such as `docs/maintainer_tooling.html` are preview-only artifacts, not maintained repo outputs; do not edit or commit them.

## Health Disposition Store

- Inspect current state (generated projection):
  `head -80 docs/health/dispositions.md`
- Inspect the latest history shard:
  `ls docs/health/dispositions_history/$(date +%Y)/` then `head -80 <shard>`
- Stamp legacy 5-column ledger rows with explicit surface/dimension/ID columns:
  `python3 scripts/migrate_health_disposition_columns.py --help`
- Run the closure-staleness check:
  `python3 scripts/check_ledger_staleness.py`
- Rebuild the generated current view from history shards (re-run after manual shard edits):
  `python3 scripts/migrate_health_disposition_store.py --rebuild-current-only`
- Migrate Markdown history shards into JSONL events and regenerate derived views:
  `python3 scripts/migrate_health_disposition_jsonl.py --root .`

## Plugin Health and Documentation

```bash
# Run the suggestions-only health sweep (writes per-surface dossiers; never auto-edits)
/audit-plugin-health --surface both --dimension all
/audit-plugin-health --surface both --dimension naming
/audit-plugin-health --surface tooling --dimension quality
/audit-plugin-health --surface plugin --dimension design --resume
```

Dossiers are written to `docs/health/YYYY-MM-DD-<surface>-health.md` (the
`-findings.md` file is the intermediate raw lens output the report ranks into the
dossier).

`--resume` is valid only for `/audit-plugin-health` and resumes the stored
filter set from an interrupted discovery run.

## Updating Documentation Maps

When skills or agents change, synchronize the documentation:

```bash
# Keep the maps accurate (maintained entry point):
/sync-map-documentation  # Async step 1: dispatch audits for both maps
/sync-map-documentation-collect --team-ids <skill-id>,<agent-id>  # Step 2: collect audits and stage updates
/sync-map-documentation-apply --team-ids <id>[,<id>]  # Step 3: validate and write map docs
/sync-map-documentation-write  # Step 4: regenerate downstream docs/projections and commit

# Find improvements (one entry, all dimensions → one dossier):
/audit-plugin-health --surface both --dimension all
/audit-plugin-health --surface plugin --dimension design
/audit-plugin-health --surface tooling --dimension quality
/audit-plugin-health --surface both --dimension naming
```

For audit-only map checks (no updates):

```bash
/sync-map-documentation --no-update   # Print the maintained async sequence without dispatching or modifying docs
```

These skills write to:

- `docs/skills-map.md` — Skill inventory and relationships (documentation only)
- `docs/agent-map.md` — Agent inventory and tool assignments (documentation only)
- `docs/health/YYYY-MM-DD-<surface>-health.md` — the ranked findings dossier (all design, quality, and naming findings)
