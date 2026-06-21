---
name: sync-map-documentation-apply
description: >-
  Applies validated update artifacts to docs/. Third step of the async sync
  flow. Validates update-agent artifacts (including a mandatory agent-artifact
  catalog count check that confirms the generated agent-catalog rows match the
  live agent files), reads updated map content from
  the run directory, and writes both documentation maps to docs/. Each surface
  is validated independently — an invalid or missing artifact for one map does
  not block writing the other — except when both surfaces fail validation, in
  which case the skill halts without writing either map. Run
  /sync-map-documentation-write next to regenerate diagrams and commit.
argument-hint: "--team-ids <id>[,<id>] [--skip-commit]"
workflow:
  stage: map-sync
  invoked-by: user
  repeatable: false
  inputs:
    - .dev/sync-map-documentation-checkpoint.json
    - .dev/sync-map-documentation-runs/RUN_ID/updates/<surface>-map.md
  outputs:
    - docs/al-dev-skills-map.md
    - docs/al-dev-agent-map.md
  next: [sync-map-documentation-write]
---

# Sync Map Documentation — Apply (Validate & Write to docs/)

Third step of the async sync flow. Reads updated map artifacts written
by the background update agents, validates them, and writes the canonical docs/
maps to disk.

**Four-skill workflow:**

1. `/sync-map-documentation` — dispatch audit teams (~5 min, then exit)
2. `/sync-map-documentation-collect --team-ids <ids>` — collect results, spawn updates
3. `/sync-map-documentation-apply --team-ids <ids>` — validate artifacts, write maps (this skill)
4. `/sync-map-documentation-write` — regenerate diagrams, projections, and commit

**Working directory assumption:** All relative paths are resolved from
`/Users/russelllaing/al-dev-shared`. Use absolute paths in Bash commands.

---

## Phase-proof requirement

This skill follows `../../knowledge/phase-proof-contract.md`: before reporting
any phase complete, advancing to the next phase, or updating
`.dev/health-loop-state.md`, emit a phase-proof block (observed command output
or file-existence check) binding to that phase's deliverable. A restated
intention is not proof.

## Phase 0 — Parse Arguments

Read the arguments supplied by the user.

Split `--team-ids` on comma to populate `UPDATE_TEAM_IDS` (one or two values).

Set `SKIP_COMMIT=false` (default). If `--skip-commit` is present, set
`SKIP_COMMIT=true`.

Error and stop if any of the following are true: `--team-ids` is absent; it is
present but is an empty string; or splitting its value on comma yields zero
non-empty segments. Print a clear usage hint:

```text
Usage: /sync-map-documentation-apply --team-ids <id>[,<id>] [--skip-commit]
```

---

## Phase 1 — Load Checkpoint

Follow the read pattern in `.claude/skills/sync-map-documentation/checkpoint-patterns.md`.
Extract these fields:

| Field | Variable |
| --- | --- |
| `run_id` | `RUN_ID` |
| `result_dir` | `RUN_DIR` |
| `update_choice` | `UPDATE_CHOICE` |
| `skip_commit` | `SKIP_COMMIT_FROM_CHECKPOINT` |

Checkpoint absent → stop: "Checkpoint not found. Run /sync-map-documentation
and /sync-map-documentation-collect first to generate it."
`phase` ≠ `"update"` → stop: "Checkpoint phase is `<phase>` — expected
`update`. Re-run /sync-map-documentation-collect to advance the workflow."
If `SKIP_COMMIT` was not set via `--skip-commit`, use
`SKIP_COMMIT_FROM_CHECKPOINT`.

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

For each artifact gated by `UPDATE_CHOICE`:

1. Check presence with `ls -la "${RUN_DIR}/updates/<artifact>.md"`
2. Run the catalog count check from the **Apply-stage Artifact Validation** matrix
   in `.claude/skills/sync-map-documentation/checkpoint-patterns.md`. A
   `CATALOG_ROWS` ≠ `DISK_AGENTS` mismatch makes the agent artifact invalid — skip
   that surface.
3. Validate each present artifact per `checkpoint-patterns.md`

Artifact gates by `UPDATE_CHOICE`:

- `UPDATE_CHOICE=skills` or `UPDATE_CHOICE=both` → check
  `"${RUN_DIR}/updates/skills-map.md"`
- `UPDATE_CHOICE=agents` or `UPDATE_CHOICE=both` → check
  `"${RUN_DIR}/updates/agent-map.md"`

Apply the validation rules and all-surfaces-invalid stop rule from the
"Apply-stage artifact validation" section in `checkpoint-patterns.md`.

Each surface is validated independently — a valid artifact for one surface
is written to `docs/` even when the other surface's artifact is invalid.
When **both** surfaces fail validation, the skill halts without writing either map.

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

Update the checkpoint `status` to `"awaiting-write"` so `/sync-map-documentation-write`
knows the maps are ready:

```bash
CHECKPOINT_FILE="/Users/russelllaing/al-dev-shared/.dev/sync-map-documentation-checkpoint.json"
jq '.status = "awaiting-write"' \
    "$CHECKPOINT_FILE" \
    > /tmp/sdm-checkpoint-tmp.json && \
    mv /tmp/sdm-checkpoint-tmp.json "$CHECKPOINT_FILE"
```

---

Maps written to `docs/`. Run `/sync-map-documentation-write` to regenerate
diagrams, projections, and commit.

---

## Arguments

**`--team-ids <id>[,<id>]`** (required)
The update team IDs returned by `/sync-map-documentation-collect`,
comma-separated. One ID if only one surface was updated; two IDs if both.

**`--skip-commit`** (optional)
Passed through to `/sync-map-documentation-write`. Write maps to docs/ but
do not commit. Useful for review before committing.
Overrides the `skip_commit` value from the checkpoint if explicitly supplied.
