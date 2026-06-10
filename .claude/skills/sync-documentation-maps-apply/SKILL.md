---
name: sync-documentation-maps-apply
description: >-
  Applies validated update artifacts to docs/. Third step of the async sync
  flow. Validates update-agent artifacts, reads updated map content from
  the run directory, and writes both documentation maps to docs/. Each surface
  is validated independently — an invalid or missing artifact for one map does
  not block writing the other. Run
  /sync-documentation-maps-write next to regenerate diagrams and commit.
argument-hint: "--team-ids <id>[,<id>] [--skip-commit]"
workflow:
  stage: map-sync
  invoked-by: user
  repeatable: false
  inputs:
    - .dev/sync-documentation-maps-checkpoint.json
    - .dev/sync-documentation-maps-runs/RUN_ID/updates/<surface>-map.md
  outputs:
    - docs/al-dev-skills-map.md
    - docs/al-dev-agent-map.md
  next: [sync-documentation-maps-write]
---

# Sync Documentation Maps — Apply (Validate & Write to docs/)

Third step of the async sync flow. Reads updated map artifacts written
by the background update agents, validates them, and writes the canonical docs/
maps to disk.

**Four-skill workflow:**

1. `/sync-documentation-maps` — dispatch audit teams (~5 min, then exit)
2. `/sync-documentation-maps-collect --team-ids <ids>` — collect results, spawn updates
3. `/sync-documentation-maps-apply --team-ids <ids>` — validate artifacts, write maps (this skill)
4. `/sync-documentation-maps-write` — regenerate diagrams, projections, and commit

**Working directory assumption:** All relative paths are resolved from
`/Users/russelllaing/al-dev-shared`. Use absolute paths in Bash commands.

---

## Phase 0 — Parse Arguments

Read the arguments supplied by the user.

Split `--team-ids` on comma to populate `UPDATE_TEAM_IDS` (one or two values).

Set `SKIP_COMMIT=false` (default). If `--skip-commit` is present, set
`SKIP_COMMIT=true`.

Error and stop if `--team-ids` is absent or produces zero values.
Print a clear usage hint:

```text
Usage: /sync-documentation-maps-apply --team-ids <id>[,<id>] [--skip-commit]
```

---

## Phase 1 — Load Checkpoint

Read the checkpoint written by `/sync-documentation-maps-collect`:

```bash
cat /Users/russelllaing/al-dev-shared/.dev/sync-documentation-maps-checkpoint.json
```

Use the read pattern in
`.claude/skills/sync-documentation-maps/checkpoint-patterns.md` while applying
the finalize-specific field requirements and phase gate below. If that reference
is unavailable, parse the JSON fields in the table below directly with `jq`.

Extract the following fields:

| Field | Variable |
| --- | --- |
| `run_id` | `RUN_ID` |
| `result_dir` | `RUN_DIR` |
| `update_choice` | `UPDATE_CHOICE` |
| `skip_commit` | `SKIP_COMMIT_FROM_CHECKPOINT` |

If the checkpoint file is absent, stop with:

```text
Checkpoint not found. Run /sync-documentation-maps and
/sync-documentation-maps-collect first to generate it.
```

If `phase` is not `"update"`, stop with:

```text
Checkpoint phase is "<phase>" — expected "update".
Re-run /sync-documentation-maps-collect to advance the workflow to the
update phase before running this step.
```

If `SKIP_COMMIT` was not set via `--skip-commit` on the command line, use
`SKIP_COMMIT_FROM_CHECKPOINT` as the effective value.

---

## Phase 2 — Confirm Update Agents Finished

The update agents run in the background and the harness notifies when they
finish; their IDs (`UPDATE_TEAM_IDS`) are informational handles, not pollable
with `TaskGet`. The authoritative completion signal is the update artifact each
agent writes to `${RUN_DIR}/updates/`, validated in Phase 3.

Proceed directly to Phase 3 — the artifact check below determines whether each
map can be written. If you arrive here before the harness has signalled both
agents complete, Phase 3 will report any still-absent artifact as invalid and
skip that surface.

---

## Phase 3 — Read and Validate Update Artifacts

Check for each expected artifact based on `UPDATE_CHOICE`:

- `UPDATE_CHOICE=skills` or `UPDATE_CHOICE=both` → check
  `"${RUN_DIR}/updates/skills-map.md"`
- `UPDATE_CHOICE=agents` or `UPDATE_CHOICE=both` → check
  `"${RUN_DIR}/updates/agent-map.md"`

For each expected artifact, run:

```bash
ls -la "${RUN_DIR}/updates/skills-map.md"
wc -l "${RUN_DIR}/updates/skills-map.md"
```

(substitute `agent-map.md` for the agent surface).

For the **agent** artifact, also run the count-consistency check — catalog
rows must match the active agent files on disk:

```bash
DISK_AGENTS=$(ls /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/*.md | wc -l | tr -d ' ')
CATALOG_ROWS=$(awk '/BEGIN GENERATED: agent-catalog-table/,/END GENERATED: agent-catalog-table/' \
  "${RUN_DIR}/updates/agent-map.md" | grep -c '^| al-dev')
echo "disk=${DISK_AGENTS} catalog=${CATALOG_ROWS}"
```

The `grep -c '^| al-dev'` count assumes each catalog row begins with `| al-dev`
(one space after the pipe) — the format the agent-map catalog generator emits.
This pattern is whitespace- and prefix-sensitive: if the generator changes the
row prefix or spacing, update it here and in `/sync-documentation-maps-write`
Phase 1, which uses the same pattern.

Apply these validation rules for each artifact:

| Condition | Action |
| --- | --- |
| File absent | Report and skip that surface |
| File empty (0 lines) | Report invalid and skip that surface |
| Missing `# AL Dev` header | Report invalid and skip that surface |
| Agent artifact: `CATALOG_ROWS` ≠ `DISK_AGENTS` | Report invalid and skip that surface — the audit/update pass missed or duplicated catalog entries |
| Passes all checks | Read content and proceed |

If **all expected artifacts** are missing or invalid, stop with:

```text
No valid update artifacts found. Update teams may still be running.
Re-run this step once the teams have completed, or run with --wait
in the collect step next time.
```

---

## Phase 4 — Write Updated Maps to Disk

For each valid artifact, copy it to the canonical docs/ path:

```bash
# Skills map:
cp "${RUN_DIR}/updates/skills-map.md" \
   /Users/russelllaing/al-dev-shared/docs/al-dev-skills-map.md
wc -l /Users/russelllaing/al-dev-shared/docs/al-dev-skills-map.md

# Agent map:
cp "${RUN_DIR}/updates/agent-map.md" \
   /Users/russelllaing/al-dev-shared/docs/al-dev-agent-map.md
wc -l /Users/russelllaing/al-dev-shared/docs/al-dev-agent-map.md
```

Verify minimum line counts:

- Skills map: must be ≥100 lines
- Agent map: must be ≥50 lines

If a written file is below its minimum, report a warning and continue.
Do not revert — partial content is better than the stale previous version.

Update the checkpoint `status` to `"awaiting-write"` so `/sync-documentation-maps-write`
knows the maps are ready:

```bash
CHECKPOINT_FILE="/Users/russelllaing/al-dev-shared/.dev/sync-documentation-maps-checkpoint.json"
jq '.status = "awaiting-write"' \
    "$CHECKPOINT_FILE" \
    > /tmp/sdm-checkpoint-tmp.json && \
    mv /tmp/sdm-checkpoint-tmp.json "$CHECKPOINT_FILE"
```

---

Maps written to `docs/`. Run `/sync-documentation-maps-write` to regenerate
diagrams, projections, and commit.

---

## Arguments

**`--team-ids <id>[,<id>]`** (required)
The update team IDs returned by `/sync-documentation-maps-collect`,
comma-separated. One ID if only one surface was updated; two IDs if both.

**`--skip-commit`** (optional)
Passed through to `/sync-documentation-maps-write`. Write maps to docs/ but
do not commit. Useful for review before committing.
Overrides the `skip_commit` value from the checkpoint if explicitly supplied.
