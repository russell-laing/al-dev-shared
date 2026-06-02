---
name: sync-documentation-maps
description: >-
  Use when plugin documentation maps are out of sync with the current codebase,
  or to verify accuracy after adding/removing skills or agents. Dispatches
  parallel remote audit teams via RemoteTrigger and exits — session freed after
  ~5 minutes. Collect results with /sync-documentation-maps-collect.
  Triggers: "sync documentation maps", "update maps", "are the maps accurate".
argument-hint: "[--all] [--skip-commit]"
---

# Sync Documentation Maps

Lightweight dispatch coordinator. Spawns parallel remote audit teams for skills
and agents via RemoteTrigger, writes a checkpoint with team IDs and artifact
paths, then exits — freeing the session after roughly 5 minutes. The audits
themselves already ran in parallel in the previous implementation; the
improvement here is session-freeing, not parallelism.

**Three-skill workflow:**

1. `/sync-documentation-maps` — dispatch audit teams (this skill, ~5 min)
2. `/sync-documentation-maps-collect --team-ids <ids>` — collect results, spawn updates
3. `/sync-documentation-maps-finalize --team-ids <ids>` — write maps, commit

---

## Phase 0 — Parse Arguments

Read the arguments supplied by the user:

AUTO_UPDATE=false
SKIP_COMMIT=false

- If `--all` is present, set `AUTO_UPDATE=true`.
- If `--skip-commit` is present, set `SKIP_COMMIT=true`.

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

## Phase 3 — Spawn Audit Teams via RemoteTrigger

Dispatch **both** tasks simultaneously (do not wait for one before starting the
other). Use RemoteTrigger to launch each audit as an independent remote agent.

- **Skills audit:** dispatch agent `.claude/agents/sync-documentation-maps-skill-audit.md`
  - Pass `RUN_ID` and `RUN_DIR` in the prompt so the agent writes its findings to
    `${RUN_DIR}/audit/skill-audit.json`
- **Agent audit:** dispatch agent `.claude/agents/sync-documentation-maps-agent-audit.md`
  - Pass `RUN_ID` and `RUN_DIR` in the prompt so the agent writes its findings to
    `${RUN_DIR}/audit/agent-audit.json`

Capture the returned task IDs as `SKILL_TEAM_ID` and `AGENT_TEAM_ID`.

**If RemoteTrigger fails** (schema error, task ID not returned, or no response
within 60 s):

1. Fall back to the Agent tool and dispatch both audits in-session:
   - Spawn `subagent_type: sync-documentation-maps-skill-audit` with `RUN_ID`
     and `RUN_DIR` in the prompt
   - Spawn `subagent_type: sync-documentation-maps-agent-audit` with the same
     context
   - Both agents write directly to `${RUN_DIR}/audit/`
2. Set `SKILL_TEAM_ID=in-session` and `AGENT_TEAM_ID=in-session` — pass these
   to `/sync-documentation-maps-collect --team-ids in-session,in-session`. The
   collect step reads artifacts directly from `${RUN_DIR}/audit/` (do **not**
   add `--wait`, which would attempt remote polling on the sentinel value).
   **Warning:** collect Phase 4 (update team dispatch) also uses RemoteTrigger —
   Option 1 defers but does not eliminate the dependency. If RemoteTrigger is
   persistently unavailable, use Option 3 instead.
3. Alternatively, use `/review-maps` which includes a built-in in-session mode
   gate and does not depend on RemoteTrigger at any phase.

---

## Phase 4 — Write Checkpoint

Write a checkpoint file so `/sync-documentation-maps-collect` can locate the
running teams and their artifact paths.

Write `.dev/sync-documentation-maps-checkpoint.json` with the following fields:

| Field | Value |
|---|---|
| `operation` | `"sync-documentation-maps"` |
| `run_id` | `RUN_ID` |
| `spawned_at` | `"${SPAWNED_AT}"` |
| `skill_audit_team_id` | `SKILL_TEAM_ID` |
| `agent_audit_team_id` | `AGENT_TEAM_ID` |
| `phase` | `"audit"` |
| `status` | `"dispatched"` |
| `auto_update` | `AUTO_UPDATE` (true/false) |
| `skip_commit` | `SKIP_COMMIT` (true/false) |
| `result_dir` | `RUN_DIR` |
| `manifest_path` | `${RUN_DIR}/manifest.json` |

Also write the identical JSON to `${RUN_DIR}/manifest.json`.

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

Next step (collect results when teams complete):
  /sync-documentation-maps-collect --team-ids SKILL_TEAM_ID,AGENT_TEAM_ID
```

Exit. Do not wait for team completion.

---

## Arguments

**`--all`** (optional)
Set `AUTO_UPDATE=true` — passed through to the collect and finalize steps so
that both maps are updated without prompting the user.

**`--skip-commit`** (optional)
Set `SKIP_COMMIT=true` — passed through to the finalize step so that map
changes are written but not committed (dry-run / review mode).
