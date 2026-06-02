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

**Runtime assumption:** This workflow requires a harness/session that can
spawn and track remote update teams. If remote dispatch is unavailable, stop
and tell the user to rerun in a supported session; do not attempt a partial
inline update in this skill.

---

## Phase 1 — Load & Resume

**Parse arguments.** Split `--team-ids` on comma to extract exactly two
values: `SKILL_TEAM_ID` (first) and `AGENT_TEAM_ID` (second). Set
`WAIT_MODE=false` by default; if `--wait` is present, set `WAIT_MODE=true`.

Error and stop if `--team-ids` is absent or produces fewer than two values.
Print the usage hint:

```text
Usage: /sync-documentation-maps-collect --team-ids <skill-id>,<agent-id> [--wait]
```

**Load checkpoint.** Read the checkpoint written by `/sync-documentation-maps`:

```bash
cat /Users/russelllaing/al-dev-shared/.dev/sync-documentation-maps-checkpoint.json
```

Extract these fields:

| Field | Variable |
|---|---|
| `run_id` | `RUN_ID` |
| `result_dir` | `RUN_DIR` |
| `auto_update` | `AUTO_UPDATE` |
| `skip_commit` | `SKIP_COMMIT` |

Error and stop if the checkpoint file is absent. Advise the user to run
`/sync-documentation-maps` first to generate it.

**Resume / restart.** If the checkpoint `status` is already `"dispatched"`,
`"complete"`, or `"skipped"`, this collect step has already run. Use a
`USER_GATE` prompt to offer:

```text
A previous collect run reached status "<status>". How would you like to proceed?

[1] Resume — re-read artifacts and continue from where it left off
[2] Restart — re-run the full collect step from a clean state
[3] Cancel — stop without changes
```

On Resume, continue with the existing `update_choice` and team IDs already in
the checkpoint. On Restart, ignore prior update fields and proceed fresh. On
Cancel, stop. If `status` is unset or `"audit"`, proceed normally.

---

## Phase 2 — Poll & Read

**Poll (only if `WAIT_MODE=true`).** Poll both `SKILL_TEAM_ID` and
`AGENT_TEAM_ID` using `TaskGet` until each reports `completed` or `failed`.
Log status after each check. Do not wait more than 30 minutes total; if the
timeout is reached, advise the user to retry later and stop.

If `WAIT_MODE=false`, skip polling — the read step below handles any absent
artifacts.

**Read audit artifacts.** Verify presence of both audit results:

```bash
ls -la "${RUN_DIR}/audit/skill-audit.json" 2>/dev/null
ls -la "${RUN_DIR}/audit/agent-audit.json" 2>/dev/null
```

For each present file, read and parse the JSON. Extract:

- `surface` — which surface was audited
- `discrepancies` — array of discrepancy objects
- `summary` — human-readable summary string

For each absent file, note it as "pending" — that audit team has not yet
written its result.

If **both** files are absent, advise the user and stop:

```text
Audit results not yet available. Re-run with --wait to block until complete,
or wait for the teams to finish and then re-run this collect step.
```

---

## Phase 3 — Prep Results

Merge the parsed findings from both surfaces into a single working set. For
each surface, sort its `discrepancies` by object name and deduplicate by
`(object, type)` so the same finding reported twice is shown once.

Display the prepared findings. For each surface with a completed audit:

```text
Skills Map Audit — <summary>
  • <discrepancy type>: <detail>
  • <discrepancy type>: <detail>

Agent Map Audit — <summary>
  • <discrepancy type>: <detail>
```

For any surface still pending:

```text
Skills Map Audit — pending (team still running)
```

If **both** surfaces have completed with zero discrepancies, report and stop:

```text
Both documentation maps are accurate. No updates needed.
```

In that case, update the checkpoint `status` to `"complete"` and exit without
dispatching update teams.

---

## Phase 4 — User Gate & Dispatch

**Choose maps to update.** If `AUTO_UPDATE=true` (passed through from
`/sync-documentation-maps --all`), set `UPDATE_CHOICE=both` and skip the
prompt. Otherwise, use a `USER_GATE` prompt:

```text
Which documentation map would you like to update?

[1] Skills map only (docs/al-dev-skills-map.md)
[2] Agent map only (docs/al-dev-agent-map.md)
[3] Both maps
[4] Neither (skip updates)
```

Map the response to `UPDATE_CHOICE`: `skills`, `agents`, `both`, or `neither`.
If `UPDATE_CHOICE=neither`, update the checkpoint `status` to `"skipped"` and
stop.

**Dispatch update teams via RemoteTrigger.** Both dispatches run in parallel —
do not wait for one before starting the other.

If the harness cannot spawn remote update teams, stop with:

```text
Remote dispatch unavailable. Run this workflow in a session that supports
remote team spawning and task tracking.
```

- **Skills update** (if `UPDATE_CHOICE` is `skills` or `both`): dispatch agent
  `.claude/agents/sync-documentation-maps-skill-update.md` with a prompt that
  includes `RUN_ID` and `RUN_DIR`. Capture the returned ID as
  `SKILL_UPDATE_TEAM_ID`.
- **Agents update** (if `UPDATE_CHOICE` is `agents` or `both`): dispatch agent
  `.claude/agents/sync-documentation-maps-agent-update.md` with a prompt that
  includes `RUN_ID` and `RUN_DIR`. Capture the returned ID as
  `AGENT_UPDATE_TEAM_ID`.

For surfaces not selected, set the corresponding variable to `null`.

**Write updated checkpoint.** Merge the new update team IDs into the existing
checkpoint and `${RUN_DIR}/manifest.json`. Add or update only these fields:

| Field | Value |
|---|---|
| `phase` | `"update"` |
| `status` | `"dispatched"` |
| `update_choice` | `UPDATE_CHOICE` |
| `skill_update_team_id` | `SKILL_UPDATE_TEAM_ID` or `null` |
| `agent_update_team_id` | `AGENT_UPDATE_TEAM_ID` or `null` |

**Merge strategy:** Read the existing checkpoint JSON, update only the five
fields above, and write the result back. Preserve all pre-existing fields
(e.g., `run_id`, `auto_update`, `skip_commit`, `result_dir`). Use `jq` to
update individual keys, or read-mutate-write via script. Verify both files
were written:

```bash
ls -la /Users/russelllaing/al-dev-shared/.dev/sync-documentation-maps-checkpoint.json
ls -la "${RUN_DIR}/manifest.json"
```

**Return to user.** Print a summary and exit. Build the finalize command
using only the non-null update team IDs:

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
