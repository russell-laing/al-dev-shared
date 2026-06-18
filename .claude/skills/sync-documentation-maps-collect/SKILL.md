---
name: sync-documentation-maps-collect
description: >-
  Collect results from /sync-documentation-maps audit agents. Reads audit
  artifacts, presents discrepancy findings, asks which maps to update (skipped when `--all`/auto-update is set), and
  dispatches background update agents. Supports Resume/Restart when a prior
  collect state exists (decision table in
  `.claude/skills/sync-documentation-maps/collect-resume-patterns.md`);
  `--wait` polls for both audit artifacts for up to 30
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

## Phase-proof requirement

This skill follows `../../knowledge/phase-proof-contract.md`: before reporting
any phase complete, advancing to the next phase, or updating
`.dev/health-loop-state.md`, emit a phase-proof block (observed command output
or file-existence check) binding to that phase's deliverable. A restated
intention is not proof.

## Phase 1 — Load & Resume

**Parse arguments.** Split `--team-ids` on comma to extract exactly two
values: `SKILL_TEAM_ID` (first) and `AGENT_TEAM_ID` (second). Set
`WAIT_MODE=false` by default; if `--wait` is present, set `WAIT_MODE=true`.

Error and stop if `--team-ids` is absent or produces fewer than two values.
Print the usage hint:

```text
Usage: /sync-documentation-maps-collect --team-ids <skill-id>,<agent-id> [--wait]
```

**Load checkpoint.** Read `.dev/sync-documentation-maps-checkpoint.json` and
extract `run_id` → `RUN_ID`, `result_dir` → `RUN_DIR`, `auto_update` →
`AUTO_UPDATE`, `skip_commit` → `SKIP_COMMIT`. Full field contract:
`.claude/skills/sync-documentation-maps/checkpoint-patterns.md`.

**Resume / restart.** Check `status` in the checkpoint and act per the table
below.

| Checkpoint `status` | Action |
| --- | --- |
| unset or `"audit"` | Proceed normally with fresh Phase 1 |
| `"dispatched"` / `"complete"` / `"skipped"` | USER\_GATE: Resume / Restart / Cancel (see `collect-resume-patterns.md`) |
| file absent | Stop — advise running `/sync-documentation-maps` first |

---

## Phase 2 — Poll & Read

Run the poll-then-read state machine in
`.claude/skills/sync-documentation-maps/collect-polling-patterns.md`, passing
`WAIT_MODE` and `RUN_DIR`. It polls on artifact presence when `WAIT_MODE=true`
(30-minute cap), reads and parses each present `*-audit.json` into `surface`,
`discrepancies`, and `summary`, records an absent surface as `pending` (and a surface still pending on a same-`RUN_ID` re-run as `stalled` — consequence: stop and recommend restarting from `/sync-documentation-maps`; see `collect-polling-patterns.md` §Absence handling), and stops with the
"Audit results not yet available" message when both artifacts are absent. If both artifacts are still absent on a same-`RUN_ID` re-run, this is a stalled run — stop and recommend restarting from `/sync-documentation-maps`.

---

## Phase 3 — Prep Results

Merge the parsed findings from both surfaces into a single working set. For
each surface, compute `name = discrepancy.skill ?? discrepancy.agent`, then
stable-sort by `name` and discrepancy `type`. Deduplicate on `(name, type)` and
keep the first item from that stable ordering so duplicate reports collapse
deterministically.

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

## Delegated scope pack

Mutating delegation in this skill follows `../../knowledge/delegated-scope-pack.md`:
ship a scope pack (allowed paths, do-not-touch list, expected outputs) in the
dispatch prompt, and run the post-task `git status --short` diff sanity check
before accepting the result. Reject and re-dispatch on any out-of-scope change.

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
