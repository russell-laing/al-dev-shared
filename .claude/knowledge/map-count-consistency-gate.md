# Map Count-Consistency Gate

Three-way count check run after `generate-map-doc-sections.py` succeeds in
`/sync-map-documentation-write` Phase 1. All three values must agree before
anything is committed.

## Gate Command

```bash
REPO=$(git rev-parse --show-toplevel)
DISK_AGENTS=$(find "$REPO/profile-al-dev-shared/agents" -maxdepth 1 -name "*.md" | wc -l | tr -d ' ')
COVERAGE_COUNT=$(grep -o '[0-9][0-9]* active agents' "$REPO/docs/agent_map.md" | grep -o '[0-9]*')
CATALOG_ROWS=$(awk '/BEGIN GENERATED: agent-catalog-table/,/END GENERATED: agent-catalog-table/' \
  "$REPO/docs/agent_map.md" | grep -Ec '^\| [a-z]')
echo "disk=${DISK_AGENTS} coverage=${COVERAGE_COUNT} catalog=${CATALOG_ROWS}"
```

The three values compared are:

- **active files on disk** — `*.md` count under `profile-al-dev-shared/agents/`
- **generated Coverage count** — the `N active agents` figure in `agent_map.md`
- **generated catalog rows** — data rows (lowercase kebab-case agent names)
  matching `^\| [a-z]` inside the `BEGIN/END GENERATED: agent-catalog-table`
  block, excluding the capitalized header row and the `|---` separator row.
  An earlier version of this pattern (`^| al-dev`) assumed every agent name
  shared an `al-dev` prefix; once agents were renamed away from that prefix,
  the pattern silently matched zero rows and the gate failed on every run.

## On Mismatch — Stop and Report

If the three values differ, **stop before Phase 3 (commit)** and report:

```text
Agent count mismatch after regeneration (disk=X coverage=Y catalog=Z).
The maps would commit stale counts. Investigate before committing.
```

## Bounded Recovery

Choose the recovery path by the mismatch cause:

- **Single stale generated value (known false positive)** — exactly one of the
  catalog table or the `Coverage` line lags the just-written docs map by one
  regeneration. Refresh the affected generated section from the docs map and
  re-run this count check once.
- **Any other case** — the mismatch persists after that refresh, more than one
  value disagrees, or the run state is no longer trustworthy. Abandon the old
  run with `/sync-map-documentation --force` and start fresh rather than
  committing mixed-state artifacts.

Once the count check passes — either it agreed on the first run, or the
single-stale-value refresh above brought it into agreement — proceed with the
remaining regenerations.
