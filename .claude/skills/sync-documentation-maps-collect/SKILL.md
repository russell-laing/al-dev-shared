---
name: sync-documentation-maps-collect
description: >-
  Collect results from /sync-documentation-maps audit teams. Reads audit
  artifacts, presents discrepancy findings, asks which maps to update, and
  dispatches remote update teams. Second step of the async sync workflow.
argument-hint: "--team-ids <skill-id>,<agent-id> [--wait]"
---

# Sync Documentation Maps — Collect

Second step of the three-skill async sync workflow. Reads audit artifacts
written by the remote audit teams, presents findings to the user, and
conditionally spawns remote update teams.

**Three-skill workflow:**

1. `/sync-documentation-maps` — dispatch audit teams (~5 min, then exit)
2. `/sync-documentation-maps-collect --team-ids <ids>` — collect results,
   spawn updates (this skill)
3. `/sync-documentation-maps-finalize --team-ids <ids>` — write maps, commit

**Working directory assumption:** All relative paths are resolved from
`/Users/russelllaing/al-dev-shared`. Use absolute paths in Bash commands.

---

## Phase 0 — Parse Arguments

Read the arguments supplied by the user.

Split `--team-ids` on comma to extract exactly two values:

- `SKILL_TEAM_ID` — first value
- `AGENT_TEAM_ID` — second value

Set `WAIT_MODE=false` (default). If `--wait` is present, set `WAIT_MODE=true`.

Error and stop if `--team-ids` is absent or produces fewer than two values.
Print a clear usage hint:

```text
Usage: /sync-documentation-maps-collect --team-ids <skill-id>,<agent-id> [--wait]
```

---

## Phase 1 — Load Checkpoint

Read the checkpoint written by `/sync-documentation-maps`:

```bash
cat /Users/russelllaing/al-dev-shared/.dev/sync-documentation-maps-checkpoint.json
```

Extract the following fields:

| Field | Variable |
|---|---|
| `run_id` | `RUN_ID` |
| `result_dir` | `RUN_DIR` |
| `auto_update` | `AUTO_UPDATE` |
| `skip_commit` | `SKIP_COMMIT` |

Error and stop if the checkpoint file is absent. Advise the user to run
`/sync-documentation-maps` first to generate it.

---

## Phase 2 — Optionally Poll Teams

If `WAIT_MODE=true`:

Poll both `SKILL_TEAM_ID` and `AGENT_TEAM_ID` using `TaskGet` until each
reports `completed` or `failed`. Log status after each check. Do not wait
more than 30 minutes total; if the timeout is reached, advise the user to
retry later and stop.

If `WAIT_MODE=false`:

Skip polling and proceed immediately to Phase 3. The audit artifacts may or
may not be present yet; Phase 3 handles the absent-file case.

---

## Phase 3 — Read Audit Artifacts

Verify artifact presence:

```bash
ls -la "${RUN_DIR}/audit/skill-audit.json" 2>/dev/null
ls -la "${RUN_DIR}/audit/agent-audit.json" 2>/dev/null
```

For each present file, read and parse the JSON. Extract:

- `surface` — which surface was audited
- `discrepancies` — array of discrepancy objects
- `summary` — human-readable summary string

For each absent file, note it as "pending" — the audit team has not yet
written its result.

If **both** files are absent, advise the user that audits are still running
and suggest re-running with `--wait` or waiting a few minutes:

```text
Audit results not yet available. Re-run with --wait to block until complete,
or wait for the teams to finish and then re-run this collect step.
```

Stop if both files are absent.

---

## Phase 4 — Present Findings

For each surface with a completed audit result, display:

```text
Skills Map Audit — <summary>
  • <discrepancy type>: <detail>
  • <discrepancy type>: <detail>

Agent Map Audit — <summary>
  • <discrepancy type>: <detail>
```

For any surface still pending, display:

```text
Skills Map Audit — pending (team still running)
```

If **both** surfaces have zero discrepancies, report:

```text
Both documentation maps are accurate. No updates needed.
```

Update the checkpoint `status` to `"complete"` and stop.

---

## Phase 5 — Ask User What to Update

If `AUTO_UPDATE=true` (passed through from `/sync-documentation-maps --all`),
set `UPDATE_CHOICE=both` and skip the prompt.

Otherwise, use `AskUserQuestion` to ask:

```text
Which documentation map would you like to update?

[1] Skills map only (docs/al-dev-skills-map.md)
[2] Agent map only (docs/al-dev-agent-map.md)
[3] Both maps
[4] Neither (skip updates)
```

Map the response to `UPDATE_CHOICE`: `skills`, `agents`, `both`, or `neither`.

If `UPDATE_CHOICE=neither`, update the checkpoint `status` to `"skipped"` and stop.

---

## Phase 6 — Spawn Update Teams via RemoteTrigger

Based on `UPDATE_CHOICE`, dispatch one or both update agents. Both dispatches
must run in parallel — do not wait for one before starting the other.

**Skills update** (if `UPDATE_CHOICE` is `skills` or `both`):

Dispatch agent `.claude/agents/sync-documentation-maps-skill-update.md` with
a prompt that includes `RUN_ID` and `RUN_DIR`. Capture the returned ID as
`SKILL_UPDATE_TEAM_ID`.

**Agents update** (if `UPDATE_CHOICE` is `agents` or `both`):

Dispatch agent `.claude/agents/sync-documentation-maps-agent-update.md` with
a prompt that includes `RUN_ID` and `RUN_DIR`. Capture the returned ID as
`AGENT_UPDATE_TEAM_ID`.

For surfaces not selected, set the corresponding variable to `null`.

---

## Phase 7 — Write Updated Checkpoint

Merge the new update team IDs into the existing checkpoint fields and write
the updated checkpoint:

```bash
# Update .dev/sync-documentation-maps-checkpoint.json
# Update ${RUN_DIR}/manifest.json
```

New fields to add or update:

| Field | Value |
|---|---|
| `phase` | `"update"` |
| `status` | `"dispatched"` |
| `update_choice` | `UPDATE_CHOICE` |
| `skill_update_team_id` | `SKILL_UPDATE_TEAM_ID` or `null` |
| `agent_update_team_id` | `AGENT_UPDATE_TEAM_ID` or `null` |

**Merge strategy:** Read the existing checkpoint JSON, add or update only the five
fields listed above (skill_update_team_id, agent_update_team_id, update_choice,
phase, status), and write the result back. Preserve all pre-existing fields
(e.g., `run_id`, `auto_update`, `skip_commit`, `result_dir`). Recommended
approach: use `jq` to update individual keys without re-serializing the whole
object, or read-mutate-write via script.

Verify both files were written:

```bash
ls -la /Users/russelllaing/al-dev-shared/.dev/sync-documentation-maps-checkpoint.json
ls -la "${RUN_DIR}/manifest.json"
```

---

## Phase 8 — Return to User

Print a summary and exit. Build the finalize command using only the non-null
update team IDs:

```text
Update teams dispatched.

  Run ID:              RUN_ID
  Skills update ID:    SKILL_UPDATE_TEAM_ID   (or "not selected")
  Agents update ID:    AGENT_UPDATE_TEAM_ID   (or "not selected")
  Run directory:       RUN_DIR

Next step (finalize when teams complete):
  /sync-documentation-maps-finalize --team-ids <non-null-ids>
```

Exit. Do not wait for update team completion.

---

## Arguments

**`--team-ids <skill-id>,<agent-id>`** (required)
The audit team IDs returned by `/sync-documentation-maps`, comma-separated.

**`--wait`** (optional)
Poll both audit teams until they complete before reading artifacts.
Default: read whatever artifacts are present and report pending for any absent.
