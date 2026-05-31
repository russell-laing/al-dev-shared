---
name: sync-documentation-maps-finalize
description: >-
  Finalize sync-documentation-maps updates. Reads updated map artifacts from
  remote update teams, writes them to docs/, refreshes the dependency graph,
  and commits. Final step of the async sync-documentation-maps workflow.
argument-hint: "--team-ids <ids> [--skip-commit]"
---

# Sync Documentation Maps — Finalize

Third and final step of the three-skill async sync workflow. Reads updated map
artifacts written by the remote update teams, validates them, writes the
canonical docs/ maps, refreshes the dependency graph, and commits.

**Three-skill workflow:**

1. `/sync-documentation-maps` — dispatch audit teams (~5 min, then exit)
2. `/sync-documentation-maps-collect --team-ids <ids>` — collect results, spawn updates
3. `/sync-documentation-maps-finalize --team-ids <ids>` — write maps, commit (this skill)

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
Usage: /sync-documentation-maps-finalize --team-ids <id>[,<id>] [--skip-commit]
```

---

## Phase 1 — Load Checkpoint

Read the checkpoint written by `/sync-documentation-maps-collect`:

```bash
cat /Users/russelllaing/al-dev-shared/.dev/sync-documentation-maps-checkpoint.json
```

Extract the following fields:

| Field | Variable |
|---|---|
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
update phase before running finalize.
```

If `SKIP_COMMIT` was not set via `--skip-commit` on the command line, use
`SKIP_COMMIT_FROM_CHECKPOINT` as the effective value.

---

## Phase 2 — Check Update Team Status

Call `TaskGet` for each ID in `UPDATE_TEAM_IDS`. For each team, report:

- `completed` — ready to read artifacts
- `running` — still in progress; artifact may be partial
- `failed` — team reported failure; artifact may be absent

Print a status table:

```text
Update team status:
  <team-id-1>: completed
  <team-id-2>: running
```

Note: Phase 3 artifact validation is the authoritative gate. Continue
regardless of reported status — the artifact check determines whether
the map can be written.

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

Apply these validation rules for each artifact:

| Condition | Action |
|---|---|
| File absent | Report and skip that surface |
| File empty (0 lines) | Report invalid and skip that surface |
| Missing `# AL Dev` header | Report invalid and skip that surface |
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

---

## Phase 5 — Refresh Dependency Graph

Run the dependency graph generator:

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/generate-agent-projections.py
```

Capture the exit code. If non-zero, report:

```text
Dependency graph refresh failed (exit <code>). Continuing — maps have been
written; graph will be refreshed on the next run.
```

Continue regardless of exit code.

---

## Phase 6 — Present Summary

Print a summary of all work completed:

```text
Sync finalized.

  Run ID: RUN_ID

  Updated files:
    docs/al-dev-skills-map.md       — <N> lines  (or "skipped")
    docs/al-dev-agent-map.md        — <N> lines  (or "skipped")

  Dependency graph: refreshed  (or "refresh failed — see above")
```

---

## Phase 7 — Commit

If `SKIP_COMMIT=true`, print a dry-run message and stop:

```text
--skip-commit set. Skipping commit. Files written to docs/ are ready for
manual review and commit.
```

Otherwise, stage and commit:

```bash
git -C /Users/russelllaing/al-dev-shared status
git -C /Users/russelllaing/al-dev-shared add \
    docs/al-dev-skills-map.md \
    docs/al-dev-agent-map.md
git -C /Users/russelllaing/al-dev-shared add \
    profile-al-dev-shared/generated/ 2>/dev/null || true
git -C /Users/russelllaing/al-dev-shared diff --cached --stat
git -C /Users/russelllaing/al-dev-shared commit \
    -m "docs: sync documentation maps with current codebase"
git -C /Users/russelllaing/al-dev-shared log --oneline -n 1
```

If the commit exits non-zero, report the error and advise the user to inspect
`git status` and commit manually.

---

## Phase 8 — Update Checkpoint

Set `phase` to `"complete"` and `status` to `"done"` in both checkpoint files:

```bash
# Update .dev/sync-documentation-maps-checkpoint.json
# Update ${RUN_DIR}/manifest.json
```

Use `jq` to update only the two fields; preserve all pre-existing fields:

```bash
jq '.phase = "complete" | .status = "done"' \
    /Users/russelllaing/al-dev-shared/.dev/sync-documentation-maps-checkpoint.json \
    > /tmp/sdm-checkpoint-tmp.json && \
    mv /tmp/sdm-checkpoint-tmp.json \
       /Users/russelllaing/al-dev-shared/.dev/sync-documentation-maps-checkpoint.json

jq '.phase = "complete" | .status = "done"' \
    "${RUN_DIR}/manifest.json" \
    > /tmp/sdm-manifest-tmp.json && \
    mv /tmp/sdm-manifest-tmp.json "${RUN_DIR}/manifest.json"
```

Append a completion record to `.dev/progress.md`:

```text
[2026-05-31] sync-documentation-maps-finalize complete — RUN_ID maps written
and committed.
```

(Use the actual current date and RUN_ID value.)

Print a final confirmation:

```text
sync-documentation-maps workflow complete. Run ID: RUN_ID
```

---

## Arguments

**`--team-ids <id>[,<id>]`** (required)
The update team IDs returned by `/sync-documentation-maps-collect`,
comma-separated. One ID if only one surface was updated; two IDs if both.

**`--skip-commit`** (optional)
Write maps to docs/ but do not commit. Useful for review before committing.
Overrides the `skip_commit` value from the checkpoint if explicitly supplied.
