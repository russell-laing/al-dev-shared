# Development Commands

Common commands for maintaining the shared plugin surface.

## Validation (All Harnesses)

```bash
# Validate that shared source has no harness-specific leakage
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared

# Validate agent structure (frontmatter, tools, model assignment)
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents

# Validate knowledge file quality
python3 scripts/validate-knowledge-quality.py --path profile-al-dev-shared/knowledge

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
- `python3 scripts/validate-lens-agents.py`
- a projections-current check (regenerates to a temp dir and diffs against
  `profile-al-dev-shared/generated/`)

Bypass with `git commit --no-verify` only when intentionally committing a
work-in-progress; the hook is fast local feedback, not a security control.

## Projection (Harness-Native Artifacts)

```bash
# Regenerate all harness projections after shared agent/policy changes
python3 scripts/generate-agent-projections.py
```

## Documentation Maps (Mermaid Diagrams)

The documentation maps (`docs/al-dev-skills-map.md`, `docs/al-dev-agent-map.md`, `docs/al-dev-plugin-graph.md`) contain auto-generated sections with Mermaid diagrams. These are regenerated from the shared plugin source:

```bash
# Regenerate all documentation map sections
# - Layer 1 lifecycle diagrams
# - Layer 2 per-skill drilldowns (with Phase<N> nodes)
# - Agent catalog and dependency graphs
python3 scripts/generate-map-doc-sections.py

# Regenerate plugin dependency graph separately
python3 scripts/generate-plugin-graph.py
```

**Do not hand-edit** sections between `<!-- BEGIN GENERATED: ... -->` and `<!-- END GENERATED: ... -->` markers; changes will be overwritten on the next regeneration. Use the skills-based interface (`/sync-documentation-maps`) for interactive updates.

## Plugin Health and Documentation

```bash
# Run the suggestions-only health sweep (writes per-surface dossiers; never auto-edits)
/plugin-health-audit --surface both
```

Dossiers are written to `docs/health/YYYY-MM-DD-<surface>-findings.md`.

## Updating Documentation Maps

When skills or agents change, synchronize the documentation:

```bash
# Primary workflow:
/sync-documentation-maps  # Audits and updates both maps (interactive or --all)
/analyze-skill-design     # Generate architecture improvement suggestions
/analyze-agent-design     # Generate agent design improvement suggestions
/audit-quality --type skill   # Audit skill quality (clarity, structure, bloat, drift)
/audit-quality --type agent   # Audit agent quality (clarity, structure, bloat, drift)
```

For audit-only (no updates):

```bash
/review-skill-map --no-update   # Verify skills map accuracy without modifying
/review-agent-map --no-update   # Verify agent map accuracy without modifying
```

These skills write findings to:

- `docs/al-dev-skills-map.md` — Skill inventory and relationships
- `docs/al-dev-agent-map.md` — Agent inventory and tool assignments
- `docs/al-dev-plugin-map.md` — Skill architecture improvement suggestions
- `docs/al-dev-skill-quality.md` — Skill clarity and structural issues
- `docs/al-dev-agent-quality.md` — Agent quality audit results
