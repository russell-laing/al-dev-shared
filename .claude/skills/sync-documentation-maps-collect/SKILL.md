---
name: sync-documentation-maps-collect
description: >-
  Collect results from /sync-documentation-maps audit agents. Reads audit
  artifacts, presents discrepancy findings, asks which maps to update, and
  dispatches background update agents. Supports Resume/Restart when a prior
  collect state exists; `--wait` polls for both audit artifacts for up to 30
  minutes before reading them. Second step of the async sync workflow.
argument-hint: "--team-ids <skill-id>,<agent-id> [--wait]"
workflow:
  stage: map-sync
  invoked-by: user
  repeatable: false
  inputs:
    - .dev/sync-documentation-maps-checkpoint.json
    - .dev/sync-documentation-maps-runs/RUN_ID/audit/<surface>-audit.json
  outputs:
    - .dev/sync-documentation-maps-runs/RUN_ID/updates/<surface>-map.md
  next: [sync-documentation-maps-apply]
---

# Sync Documentation Maps — Collect

Second step of the four-skill async sync workflow. Reads audit artifacts
written by the remote audit teams, presents findings to the user, and
conditionally spawns remote update teams.

**Four-skill workflow:**

1. `/sync-documentation-maps` — dispatch audit teams (~5 min, then exit)
2. `/sync-documentation-maps-collect --team-ids <ids>` — collect results,
   spawn updates (this skill)
3. `/sync-documentation-maps-apply --team-ids <ids>` — validate artifacts, write maps
4. `/sync-documentation-maps-write` — regenerate diagrams, projections, and commit

**Working directory assumption:** All relative paths are resolved from
`/Users/russelllaing/al-dev-shared`. Use absolute paths in Bash commands.

**Runtime assumption:** This workflow requires a harness/session that can
spawn background agents and read their artifact files. If background dispatch is
unavailable, stop and tell the user to rerun in a supported session; do not
attempt a partial inline update in this skill.

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

Extract fields `run_id`, `result_dir`, `auto_update`, `skip_commit` per the
field table below and the full contract in
`.claude/skills/sync-documentation-maps/checkpoint-patterns.md`.

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

**Poll (only if `WAIT_MODE=true`).** The audit agents run in the background and
write their results to `${RUN_DIR}/audit/`. Poll on **artifact presence** —
`ls "${RUN_DIR}/audit/skill-audit.json"` and `…/agent-audit.json` — until both
files exist or the timeout is reached. Log which files are present after each
check. Do not wait more than 30 minutes total; if the timeout is reached, advise
the user to retry later and stop. (Background-agent IDs are not pollable with
`TaskGet`; the artifact files are the authoritative completion signal.)

If `WAIT_MODE=false`, skip polling — the harness notifies when the background
agents finish, and the read step below handles any artifact still absent.

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

If `WAIT_MODE=false` and an expected audit artifact is not yet present, do **not**
block: record that surface as `pending` and report that the harness will notify on
completion; the user re-runs collect (or runs `--wait`) once notified.

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

**Dispatch updates, merge the checkpoint, and report.** Per `UPDATE_CHOICE`,
dispatch the selected update agents in parallel with `run_in_background: true`:
`sync-documentation-maps-skill-update` (if `skills`/`both`) and
`sync-documentation-maps-agent-update` (if `agents`/`both`), passing each
`run_id` and `result_dir`. Capture the returned background IDs, merge the
update fields (`skill_update_team_id`, `agent_update_team_id`,
`update_choice`, `status: "dispatched"`) into BOTH the root checkpoint and
`${RUN_DIR}/manifest.json` (read-first, then Edit), then print the
next-step summary pointing at `/sync-documentation-maps-apply`.

For the exact dispatch skeleton, prompt templates, and checkpoint-merge
field list, follow
`.claude/skills/sync-documentation-maps/collect-dispatch-patterns.md`.

Exit. Do not wait for update team completion.

---

## Arguments

**`--team-ids <skill-id>,<agent-id>`** (required)
The audit team IDs returned by `/sync-documentation-maps`, comma-separated.

**`--wait`** (optional)
Poll for both audit artifacts until they are present before reading them.
Default: read whatever artifacts are present and report pending for any absent.
