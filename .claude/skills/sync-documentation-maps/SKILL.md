---
name: sync-documentation-maps
description: >-
  Use when plugin documentation maps are out of sync with the current codebase,
  or to verify accuracy after adding/removing skills or agents. Dispatches
  parallel background audit agents and writes a checkpoint; the harness notifies
  on completion. Collect results with /sync-documentation-maps-collect.
  Triggers: "sync documentation maps", "update maps", "are the maps accurate".
argument-hint: "[--all] [--skip-commit] [--force]"
---

# Sync Documentation Maps

Lightweight dispatch coordinator. Spawns parallel background audit agents for
skills and agents, writes a checkpoint with their agent IDs and artifact paths,
then returns. The agents run in the background; the harness notifies on
completion (roughly 5 minutes), so the user is free to work meanwhile.

**Four-skill workflow:**

1. `/sync-documentation-maps` — dispatch audit teams (this skill, ~5 min)
2. `/sync-documentation-maps-collect --team-ids <ids>` — collect results, spawn updates
3. `/sync-documentation-maps-apply [RUN_ID]` — write maps to docs/
4. `/sync-documentation-maps-write` — regenerate diagrams/projections/graph, commit

---

## Phase 0 — Parse Arguments

Read the arguments supplied by the user:

AUTO_UPDATE=false
SKIP_COMMIT=false
FORCE=false

- If `--all` is present, set `AUTO_UPDATE=true`.
- If `--skip-commit` is present, set `SKIP_COMMIT=true`.
- If `--force` is present, set `FORCE=true`.

### Cadence guard — no dispatch over an uncollected run

Abandoned runs spawn audit agents whose results are never read (4 of 13
dispatches May 31 – Jun 4 were abandoned). Check the checkpoint before
dispatching:

```bash
cat /Users/russelllaing/al-dev-shared/.dev/sync-documentation-maps-checkpoint.json 2>/dev/null
```

If the checkpoint exists and its `status` is anything other than `"done"`,
a prior run is still in flight or uncollected. Unless `FORCE=true`, stop
with:

```text
Prior sync run <run_id> is incomplete (status: <status>).
Collect it first (/sync-documentation-maps-collect, then -apply, -write),
or re-run with --force to abandon it and start fresh.
```

With `FORCE=true`, note the abandoned `run_id` in the new run's progress
entry so the orphaned artifacts are traceable.

---

## Phase 1 — Generate Run Context

Create a timestamped run directory to hold all artifacts for this operation:

```bash
RUN_ID=$(date -u +%Y%m%dT%H%M%SZ)
SPAWNED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)
RUN_DIR="/Users/russelllaing/al-dev-shared/.dev/sync-documentation-maps-runs/${RUN_ID}"
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

## Phase 3 — Spawn Background Audit Agents

Dispatch **both** audit agents simultaneously (do not wait for one before
starting the other), using the canonical in-session background-dispatch pattern
in `.claude/skills/sync-documentation-maps/checkpoint-patterns.md`. Use the
`Agent` tool with `run_in_background: true` so the agents run in the background
and the harness notifies on completion:

Dispatch both audit agents with one template, varying only the three
parameters in the table below. Use the `Agent` tool with `run_in_background:
true`:

```text
Agent: <SUBAGENT_TYPE>
Prompt:
  Audit <TARGET_DESCRIPTION> against <MAP_FILE>.

  Inputs:
  - run_id: <RUN_ID>
  - result_dir: <RUN_DIR>

  Write audit findings to <result_dir>/audit/<OUTPUT_FILE> per the schema in
  your agent definition.
```

| Run | `<SUBAGENT_TYPE>` | `<TARGET_DESCRIPTION>` / `<MAP_FILE>` | `<OUTPUT_FILE>` |
|-----|-------------------|----------------------------------------|-----------------|
| Skills | `sync-documentation-maps-skill-audit` | `skills in profile-al-dev-shared/skills/` against `docs/al-dev-skills-map.md` | `skill-audit.json` |
| Agents | `sync-documentation-maps-agent-audit` | `agents in profile-al-dev-shared/agents/` against `docs/al-dev-agent-map.md` | `agent-audit.json` |

Capture the returned background agent IDs as `SKILL_TEAM_ID` and
`AGENT_TEAM_ID`. These are informational handles for the checkpoint — the
authoritative handoff is the audit JSON each agent writes to `${RUN_DIR}/audit/`,
which `/sync-documentation-maps-collect` reads directly. They are **not** polled
with `TaskGet`.

---

## Phase 4 — Write Checkpoint

Write a checkpoint file so `/sync-documentation-maps-collect` can locate the
running teams and their artifact paths.

Write the checkpoint with the following fields. Before writing, check whether
`.dev/sync-documentation-maps-checkpoint.json` already exists:

```bash
ls -la .dev/sync-documentation-maps-checkpoint.json 2>/dev/null
```

If it **exists**, read it with the Read tool first, then use the Edit tool to
replace the entire JSON block. If it **does not exist**, use the Write tool
directly. Apply the same read-first rule to `${RUN_DIR}/manifest.json`.

| Field | Value |
|---|---|
| `operation` | `"sync-documentation-maps"` |
| `run_id` | `RUN_ID` |
| `spawned_at` | `"${SPAWNED_AT}"` |
| `skill_audit_team_id` | `SKILL_TEAM_ID` |
| `agent_audit_team_id` | `AGENT_TEAM_ID` |
| `phase` | `"audit"` |
| `status` | `"audit"` |
| `auto_update` | `AUTO_UPDATE` (true/false) |
| `skip_commit` | `SKIP_COMMIT` (true/false) |
| `result_dir` | `RUN_DIR` |
| `manifest_path` | `${RUN_DIR}/manifest.json` |

Write the identical JSON to `${RUN_DIR}/manifest.json` (this is always new,
so Write is safe without a prior read).

Verify both files exist:

```bash
ls -la .dev/sync-documentation-maps-checkpoint.json
ls -la "${RUN_DIR}/manifest.json"
```

Append a progress entry to `.dev/progress.md`:

```bash
cat >> .dev/progress.md << 'EOF'
[2026-05-31] sync-documentation-maps (run ${RUN_ID}): Spawned skill-audit
  (${SKILL_TEAM_ID}) and agent-audit (${AGENT_TEAM_ID}) teams.
  Next: /sync-documentation-maps-collect --team-ids ${SKILL_TEAM_ID},${AGENT_TEAM_ID}
EOF
```

---

## Phase 5 — Return to User

Print a summary and exit:

```text
Audit teams dispatched.

  Run ID:            RUN_ID
  Skills team ID:    SKILL_TEAM_ID
  Agents team ID:    AGENT_TEAM_ID
  Run directory:     RUN_DIR
  Checkpoint:        .dev/sync-documentation-maps-checkpoint.json

Next step (collect results when the agents finish):
  /sync-documentation-maps-collect --team-ids SKILL_TEAM_ID,AGENT_TEAM_ID
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
