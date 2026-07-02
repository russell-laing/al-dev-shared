---
name: sync-map-documentation
description: >-
  Use when plugin documentation maps are out of sync with the current codebase,
  or to verify accuracy after adding/removing skills or agents. Dispatches
  parallel background audit agents and writes a checkpoint. Collect results with
  /sync-map-documentation-collect using the checkpoint reference.
  Triggers: "sync documentation maps", "review maps", "update maps", "sync maps",
  "are the maps accurate", "check the maps".
argument-hint: "[--all] [--skip-commit] [--force] [--no-update]"
workflow:
  stage: map-sync
  invoked-by: both
  repeatable: true
  inputs:
    - docs/skills_map.md
    - docs/agent_map.md
  outputs:
    - .dev/sync-map-documentation-checkpoint.json
    - .dev/sync-map-documentation-runs/RUN_ID/audit/<surface>-audit.json
  next: [sync-map-documentation-collect]
---

# Sync Map Documentation

Lightweight dispatch coordinator. Dispatches parallel background audit agents for
skills and agents, writes a checkpoint with their agent IDs and artifact paths,
then returns. The agents run in the background; the harness notifies on
completion, so the user is free to work meanwhile.

**Four-skill workflow:**

1. `/sync-map-documentation` — dispatch audit teams (this skill)
2. `/sync-map-documentation-collect --team-ids <ids>` — collect results, spawn updates
3. `/sync-map-documentation-apply --team-ids <ids>` — validate artifacts, write maps
4. `/sync-map-documentation-write` — regenerate diagrams/projections/graph, commit

**Design note:** This skill orchestrates 4 async sub-skills (dispatcher, collect, apply, write) with checkpoint handoff between stages. See `.claude/knowledge/sync-map-documentation-design-decisions.md` for design rationale on phase isolation.

## Maintainer Contracts

Apply `../../knowledge/phase-proof-contract.md` at every phase boundary before
reporting completion or updating `.dev/health-loop-state.md`.

Apply `../../knowledge/dispatch-fallback-contract.md` before every agent
dispatch. Declare the preferred path, run preflight, fall back
deterministically, and log `preferred → outcome → fallback → reason`.

## Phase 0 — Parse Arguments

| Argument | Default | Behaviour |
| --- | --- | --- |
| `--all` | off | Auto-update both maps without prompting (passed to collect/finalize) |
| `--skip-commit` | off | Write map changes but do not commit (dry-run) |
| `--force` | off | Override the cadence guard and dispatch over an uncollected run |
| `--no-update` | off | Print the four-skill sequence and stop — no dispatch, no checkpoint |

Set booleans from the flags: `AUTO_UPDATE` ← `--all`; `SKIP_COMMIT` ←
`--skip-commit`; `FORCE` ← `--force`; `NO_UPDATE` ← `--no-update`. If
`NO_UPDATE=true`, print the four-skill workflow (sync → collect → apply → write)
sequence (steps 1–4 from the header) and stop without dispatching.

### Cadence guard — no dispatch over an uncollected run

Check the checkpoint before dispatching. This is a literal-string comparison on
the checkpoint `status` field (the `2>/dev/null` below silently collapses the
absent-file case, so handle it explicitly):

- file absent or unreadable → no prior run; proceed
- `status == "done"` → prior run finished; proceed
- any other value (e.g. `"audit"`, `"collect"`, `"apply"`, null) → a run is
  in progress; stop unless `FORCE=true`

A *present* checkpoint whose `status` is `null` or empty is treated as
in-progress (the blocking case above) — only an absent or unreadable file
counts as "no prior run" and proceeds. A null status typically means a run
wrote the checkpoint but had not yet recorded its stage.

```bash
cat /Users/russelllaing/al-dev-shared/.dev/sync-map-documentation-checkpoint.json 2>/dev/null
```

```text
Prior sync run <run_id> is incomplete (status: <status>).
Collect it first (/sync-map-documentation-collect, then -apply, -write),
or re-run with --force to abandon it and start fresh.
```

With `FORCE=true`, note the abandoned `run_id` in the new run's progress entry:
append a line to `.dev/progress.md` of the form
`abandoned <old RUN_ID>; superseded by <new RUN_ID>; reason: <prior status / why>`.
This note is recorded only in `.dev/progress.md`, not in the checkpoint JSON.

If `status` is `done` (or `FORCE=true` was passed), proceed to Phase 1.

---

## Phase 1 — Generate Run Context

Create a timestamped run directory to hold all artifacts for this operation:

```bash
RUN_ID=$(date -u +%Y%m%dT%H%M%SZ)
SPAWNED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)
RUN_DIR="/Users/russelllaing/al-dev-shared/.dev/sync-map-documentation-runs/${RUN_ID}"
mkdir -p "${RUN_DIR}/audit"
mkdir -p "${RUN_DIR}/updates"
ls -la "${RUN_DIR}/"
```

Record `RUN_ID` and `RUN_DIR` for use in all subsequent phases.

---

## Phase 2 — Build File Lists

Enumerate the current skills and agents (including archived surfaces) so the
audit teams have a complete inventory to compare against the maps:

```bash
ls profile-al-dev-shared/skills/
ls profile-al-dev-shared/archived/skills/ 2>/dev/null
ls profile-al-dev-shared/agents/
ls profile-al-dev-shared/archived/agents/ 2>/dev/null
```

---

## Phase 3 — Dispatch Audit Agents

### Phase 3.1 — Dispatch metadata agents (parallel)

Dispatch in parallel:

- `al-dev-shared:collect-agent-metadata` (writes `agent-metadata.json`)
- `al-dev-shared:sync-map-documentation-skill-metadata` (writes `skill-metadata.json`)

Pass `run_id` and `result_dir` to both. Wait for both to complete.

Verify `.claude/skills/sync-map-documentation/sync-map-documentation-dispatch-patterns.md`
exists before dispatching; if it is absent, stop and report the missing canonical
dispatch template rather than improvising agent IDs/parameters.

For the canonical dispatch template and surface parameterization table, follow
`.claude/skills/sync-map-documentation/sync-map-documentation-dispatch-patterns.md`.

Capture the returned agent IDs as `AGENT_METADATA_TEAM_ID` and `SKILL_METADATA_TEAM_ID`.

### Phase 3.2 — Dispatch discrepancy agents (parallel)

Dispatch in parallel after metadata agents complete:

- `al-dev-shared:sync-map-documentation-agent-compare` (reads `agent-metadata.json`,
  writes `agent-audit.json`)
- `al-dev-shared:sync-map-documentation-skill-compare` (reads `skill-metadata.json`,
  writes `skill-audit.json`)

Pass `run_id` and `result_dir` to both. Wait for both to complete.

Capture the returned agent IDs as `AGENT_DISCREPANCY_TEAM_ID` and `SKILL_DISCREPANCY_TEAM_ID`.
These are informational handles for the checkpoint — the authoritative handoff is the
audit JSON each agent writes to `${RUN_DIR}/audit/`, which `/sync-map-documentation-collect`
reads directly. They are **not** polled with `TaskGet`.

---

## Phase 4 — Write Checkpoint

Write these fields to `.dev/sync-map-documentation-checkpoint.json` (merge pattern in
`checkpoint-patterns.md`; root checkpoint may exist from a prior run) and identically to
`${RUN_DIR}/manifest.json` (always new — create directly with Write):

| Field | Value |
| --- | --- |
| `operation` | `"sync-map-documentation"` |
| `run_id` | `RUN_ID` |
| `spawned_at` | `"${SPAWNED_AT}"` |
| `skill_metadata_team_id` | `SKILL_METADATA_TEAM_ID` |
| `agent_metadata_team_id` | `AGENT_METADATA_TEAM_ID` |
| `skill_discrepancy_team_id` | `SKILL_DISCREPANCY_TEAM_ID` |
| `agent_discrepancy_team_id` | `AGENT_DISCREPANCY_TEAM_ID` |
| `phase` | `"audit"` |
| `status` | `"audit"` |
| `auto_update` | `AUTO_UPDATE` (true/false) |
| `skip_commit` | `SKIP_COMMIT` (true/false) |
| `result_dir` | `RUN_DIR` |
| `manifest_path` | `${RUN_DIR}/manifest.json` |

Verify both files exist:

```bash
ls -la .dev/sync-map-documentation-checkpoint.json && ls -la "${RUN_DIR}/manifest.json"
```

Append the dispatch progress entry to `.dev/progress.md`.

---

## Phase 5 — Return to User

Print a summary and exit:

```text
Audit teams dispatched.

  Run ID:                      RUN_ID
  Skill metadata team ID:      SKILL_METADATA_TEAM_ID
  Agent metadata team ID:      AGENT_METADATA_TEAM_ID
  Skill discrepancy team ID:   SKILL_DISCREPANCY_TEAM_ID
  Agent discrepancy team ID:   AGENT_DISCREPANCY_TEAM_ID
  Run directory:               RUN_DIR
  Checkpoint:                  .dev/sync-map-documentation-checkpoint.json

Next step (collect results when the agents finish):
  /sync-map-documentation-collect --team-ids SKILL_DISCREPANCY_TEAM_ID,AGENT_DISCREPANCY_TEAM_ID
```

Return without blocking. The audit agents run in the background; the harness
notifies on completion, at which point run the collect step above.

---

## Arguments

**`--all`** (optional)
Set `AUTO_UPDATE=true` — passed through to the collect and finalize steps so
that both maps are updated without prompting the user.

**`--skip-commit`** (optional)
Set `SKIP_COMMIT=true` — passed through to the finalize step so that map
changes are written but not committed (dry-run / review mode).

**`--force`** (optional)
Override the Phase 0 cadence guard and dispatch even when the prior run's
checkpoint status is not `done`. The guard is a literal-string check on the
checkpoint `status` field: an absent or unreadable checkpoint and `status ==
"done"` both proceed without `--force`; any other value (e.g. `"audit"`,
`"collect"`, `"apply"`, null) blocks dispatch unless `--force` is given.

**`--no-update`** (optional)
Print the maintained four-skill async sequence — `/sync-map-documentation` →
`/sync-map-documentation-collect` → `/sync-map-documentation-apply` →
`/sync-map-documentation-write` — and stop; no agents are dispatched
and no checkpoint is written. Use when you want to review the steps without starting
a sync run.
