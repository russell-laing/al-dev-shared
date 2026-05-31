# Sync Documentation Maps with Agent Teams — Design Spec

**Date:** 2026-05-31  
**Status:** Approved for implementation  
**Author:** Brainstorming collaboration  

## Executive Summary

**Problem:** `/sync-documentation-maps` orchestrates two expensive operations (`/review-skill-map` and `/review-agent-map`) in sequence. Each review operation reads 60+ files, performs complex comparisons, and updates documentation maps. On a large plugin surface, this consumes 1–2 hours of session tokens and blocks other work.

**Solution:** Dispatch audit and update operations to remote agent teams that execute in parallel outside the main session, but keep durable workflow state and result artifacts under repo-owned `.dev/` paths. Main session becomes a lightweight coordinator:
1. Audit phase (15–30 min): spawn remote audit teams for skills and agents
2. Async execution: audits run in parallel remotely
3. Presentation phase (5–10 min): fetch findings, present to user
4. Update phase (conditional, 15–30 min): spawn remote update teams based on user choice

**Expected outcome:**
- Session token burn: 1–2 hours → 30–60 minutes (50% reduction)
- Wall-clock time: 1–2 hours → 30–45 minutes (with async work)
- Same skill interface and workflow; user gets results faster

---

## Problem Statement

### Current Architecture

Today's `/sync-documentation-maps` coordinates two sequential review operations:

```
User: /sync-documentation-maps
  ↓
sync-documentation-maps (in-session)
  ├─ Phase 1: Dispatch /review-skill-map --no-update (in-session)
  │   └─ Reads 60+ skill files, parses plugin map, compares → 30–45 min
  ├─ Wait for completion
  ├─ Phase 2: Dispatch /review-agent-map --no-update (in-session)
  │   └─ Reads 40+ agent files, parses agent map, compares → 30–45 min
  ├─ Wait for completion
  ├─ Phase 3: Present findings to user, ask which maps to update
  └─ Phase 4: Conditional — dispatch /review-skill-map or /review-agent-map with updates (in-session)
      └─ Another 30–45 min if user selects updates
  ↓
Total: 1–2+ hours of session tokens burned
```

**Bottleneck:** Audits run sequentially (Phase 1, then Phase 2), preventing parallelization. If user selects both maps for update, Phase 4 runs additional expensive operations sequentially.

### Current Constraints

- Skill audit cost: ~45 minutes per run (reading 60+ files, diffing maps)
- Agent audit cost: ~45 minutes per run (reading 40+ agent files, diffing maps)
- Update operations: same cost as audits (re-read, re-compare, write)
- Sequential phases: no parallelization possible in-session

### Workflow Impact

Typical daily workflow:
1. Make changes to skills/agents
2. Run `/sync-documentation-maps` to verify and update maps (1–2+ hours)
3. Run `/analyze-skill-design` and `/analyze-agent-design` (additional time)
4. Can't do other work in same session (tokens exhausted)

---

## Solution: Remote Audit & Update Teams

### High-Level Architecture

Distribute expensive audit and update operations to remote agent teams:

```
User: /sync-documentation-maps
  ↓
sync-documentation-maps (in-session, lightweight coordinator)
  ├─ Phase 1: Spawn audit teams for skills and agents in parallel (5–10 min)
  └─ Exit; return team IDs, user is freed
  ↓
[Remote Audit Teams, async execution (~10–15 min wall time)]
  ├─ Skill audit team: read skill files, parse maps, produce audit report artifact
  └─ Agent audit team: read agent files, parse maps, produce audit report artifact
  ↓
User: /sync-documentation-maps-collect --team-ids <skill-id>,<agent-id>  [runs when ready]
  ↓
sync-documentation-maps-collect (in-session)
  ├─ Fetch audit results from remote teams (~5 min)
  ├─ Present findings to user, ask which maps to update (5 min)
  └─ [If user selects updates] Spawn update teams (5–10 min)
  ↓
[Remote Update Teams, async execution (~10–15 min wall time, optional)]
  ├─ Skill update team (if selected): read skill files, update map, write updated-map artifact
  └─ Agent update team (if selected): read agent files, update map, write updated-map artifact
  ↓
User: /sync-documentation-maps-finalize --team-ids <ids>  [optional, if updates spawned]
  ↓
sync-documentation-maps-finalize (in-session)
  ├─ Fetch updated maps from remote teams, write to disk (~5 min)
  ├─ Refresh dependency graph (~5 min)
  └─ Commit changes
  ↓
Total session time: ~20–30 min (vs. 1–2+ hours)
```

**Key wins:**
- Skill and agent audits run in parallel (not sequentially)
- Main session freed after ~10 minutes instead of locked for 1–2 hours
- Update operations (if needed) run async, collected in a follow-up session
- Same workflow and output

---

## Detailed Design

### Phase 1: Dispatch Audit Teams (In-Session, 5–10 min)

**Inputs:**
- No required arguments; optional flags: `--all` (skip user questions), `--skip-commit`

**Steps:**

1. **Determine audit scope**
   - Default: audit both skills and agents maps
   - Scope is always "audit only" (no updates) in Phase 1

2. **Spawn skill audit team**
   - Pass: list of all skill files, current skills map content
   - Team will: read files, parse map, identify discrepancies
   - Return: audit team ID

3. **Spawn agent audit team** (in parallel)
   - Pass: list of all agent files, current agent map content
   - Team will: read files, parse map, identify discrepancies
   - Return: audit team ID

4. **Write checkpoint**
   ```json
   {
     "operation": "sync-documentation-maps",
     "run_id": "<timestamp-or-uuid>",
     "spawned_at": "2026-05-31T10:30:00Z",
     "skill_audit_team_id": "<uuid>",
     "agent_audit_team_id": "<uuid>",
     "phase": "audit",
     "status": "dispatched",
     "result_dir": ".dev/sync-documentation-maps-runs/<run-id>/",
     "manifest_path": ".dev/sync-documentation-maps-runs/<run-id>/manifest.json"
   }
   ```

5. **Write repo-owned run artifacts**
   - Create `.dev/sync-documentation-maps-runs/<run-id>/`
   - Write audit inputs / work queue metadata to the run directory
   - Write initial manifest to `.dev/sync-documentation-maps-runs/<run-id>/manifest.json`
   - Keep `.dev/progress.md` aligned with the active run

5. **Return to user**
   - Print: `"Dispatched audits for skills and agents. Audits running in parallel."`
   - Print: `"Collect results when ready: /sync-documentation-maps-collect --team-ids <skill-id>,<agent-id>"`
   - Exit skill

**Token budget:** ~5–10 minutes

---

### Phase 2: Audit Execution (Remote, Async, 10–15 min Wall Time)

**Executed by remote audit teams**

**Skill Audit Team:**
1. Receive: skill file list, current `docs/al-dev-skills-map.md` content
2. For each skill file:
   - Read skill metadata (name, description, triggers)
   - Extract agent references
   - Compute phase count
3. Parse current skills map:
   - Extract inventory table
   - Extract layer 1 diagram
   - Extract observations
4. Compare files vs. map:
   - Check each skill in map exists as file (or vice versa)
   - Check descriptions match
   - Check agent references are accurate
   - Identify discrepancies
5. Write audit report to repo-owned run artifacts:
   ```json
   {
     "surface": "skills",
     "total_files": 62,
     "map_entries": 50,
     "discrepancies": [
       {
         "type": "file_not_in_map",
         "file": "profile-al-dev-shared/skills/foo/SKILL.md",
         "reason": "new skill added"
       },
       {
         "type": "agent_reference_mismatch",
         "skill": "al-dev-plan",
         "detail": "..."
       }
     ],
     "summary": "2 discrepancies found"
   }
   ```
   Path:
   - `.dev/sync-documentation-maps-runs/<run-id>/audit/skill-audit.json`

**Agent Audit Team:**
- Similar process for agents
- Read agent files, parse agent map, identify discrepancies
- Write to `.dev/sync-documentation-maps-runs/<run-id>/audit/agent-audit.json`

---

### Phase 2a: Presentation (In-Session, After Audits Complete)

**New skill: `/sync-documentation-maps-collect`**

**Inputs:**
- `--team-ids <skill-id>,<agent-id>` (required)
- `--wait` (optional): block until audits complete (default: fetch current results)

**Steps:**

1. **Read audit results from repo-owned run artifacts**
   - Read `.dev/sync-documentation-maps-runs/<run-id>/manifest.json`
   - If orchestration metadata exists, optionally poll team status
   - Read `.dev/sync-documentation-maps-runs/<run-id>/audit/skill-audit.json`
   - Read `.dev/sync-documentation-maps-runs/<run-id>/audit/agent-audit.json`

2. **Present findings**
   ```
   Skills Map Audit:
   - 2 discrepancies found
     • new-skill not in map (file exists, not in map)
     • al-dev-develop agent reference mismatch
   
   Agent Map Audit:
   - 1 discrepancy found
     • al-dev-code-review not in map
   ```

3. **Determine next step**
   - If no discrepancies: report "Both maps accurate" and exit
   - If discrepancies exist: proceed to Phase 3

**Token budget:** ~5–10 minutes

---

### Phase 3: User Choice (In-Session)

**Ask user via `AskUserQuestion`:**

```
Which documentation map would you like to update?

[1] Skills map only (docs/al-dev-skills-map.md)
[2] Agent map only (docs/al-dev-agent-map.md)
[3] Both maps
[4] Neither (skip updates)
```

If user selects [4], stop. Otherwise, proceed to Phase 4.

---

### Phase 4: Spawn Update Teams (Conditional, In-Session, 5–10 min)

**Only if user selected updates in Phase 3**

**Steps:**

1. **Build update queue** (based on user choice)
   - Skills update: list of all skill files, audit findings, current map content
   - Agent update: list of all agent files, audit findings, current map content

2. **Spawn update teams** (in parallel if both selected)
   - Skill update team (if selected):
     - Will: read discrepancies, update map (add/remove/correct entries)
     - Return: team ID
   - Agent update team (if selected):
     - Will: read discrepancies, update map
     - Return: team ID

3. **Write checkpoint**
   ```json
   {
     "operation": "sync-documentation-maps",
     "run_id": "<timestamp-or-uuid>",
     "phase": "update",
     "skill_update_team_id": "<uuid>" or null,
     "agent_update_team_id": "<uuid>" or null,
     "status": "dispatched",
     "result_dir": ".dev/sync-documentation-maps-runs/<run-id>/",
     "manifest_path": ".dev/sync-documentation-maps-runs/<run-id>/manifest.json"
   }
   ```

4. **Return to user**
   - Print: `"Dispatched updates for selected maps. Updates running in parallel."`
   - Print: `"Finalize updates: /sync-documentation-maps-finalize --team-ids <ids>"`
   - Exit skill

**Token budget:** ~5–10 minutes

---

### Phase 5: Finalization (In-Session, 10–15 min)

**New skill: `/sync-documentation-maps-finalize`**

**Inputs:**
- `--team-ids <ids>` (required): team IDs from update phase
- `--skip-commit` (optional): dry-run mode

**Steps:**

1. **Read updated maps from repo-owned run artifacts**
   - Read `.dev/sync-documentation-maps-runs/<run-id>/manifest.json`
   - If orchestration metadata exists, optionally wait for completion
   - Read `.dev/sync-documentation-maps-runs/<run-id>/updates/skills-map.md` when present
   - Read `.dev/sync-documentation-maps-runs/<run-id>/updates/agent-map.md` when present
   - Verify content integrity

2. **Write updated maps to disk**
   - `docs/al-dev-skills-map.md` (if skills team provided results)
   - `docs/al-dev-agent-map.md` (if agent team provided results)

3. **Refresh dependency graph**
   ```bash
   python3 scripts/generate-agent-projections.py
   ```

4. **Present summary**
   - Show files modified: skills map, agent map, graph
   - Show git diff summary

5. **Commit** (unless `--skip-commit`)
   - Commit message: "docs: sync documentation maps with current codebase"

**Token budget:** ~10–15 minutes

---

## Resume Behavior

**Scenario: Audit teams dispatched, user checks results next day**

```bash
/sync-documentation-maps-collect --team-ids <skill-id>,<agent-id>
```

**Scenario: Update teams spawned, user finalizes next day**

```bash
/sync-documentation-maps-finalize --team-ids <skill-id>,<agent-id>
```

Checkpoint files persist across sessions, allowing multi-session workflows.

---

## Error Handling

### Audit Failure

- If one audit team fails (e.g., agent audit crashes): return partial results, report which audit failed
- User can re-run `/sync-documentation-maps` to retry failed audit

### Update Failure

- If update team fails after collection (e.g., unable to write map): collection phase detects and reports
- User can retry `/sync-documentation-maps-finalize` to re-attempt finalization

### Partial Completion

- If audits complete but user doesn't proceed with updates: no harm; checkpoint persists
- If updates complete but user doesn't finalize: update artifacts remain under `.dev/sync-documentation-maps-runs/<run-id>/`; can finalize later

---

## Testing & Verification

### Performance Validation

| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| Audit phase (tokens) | 45 min (skills) + 45 min (agents) = 90 min sequential | ~10 min + async execution | 80+ min saved |
| Update phase (tokens) | 45 min + 45 min = 90 min sequential | ~10 min + async execution | 80+ min saved |
| Total session time | 1–2+ hours | 30–60 min | 50% reduction |
| Wall-clock time | 1–2+ hours | 30–45 min total | 50% reduction |

### Correctness Validation

**Test 1: Audit equivalence**
- Run current `/sync-documentation-maps --skip-commit` on live codebase
- Run new system (audit teams + collection) with same scope
- Diff audit reports: should be equivalent

**Test 2: Update equivalence**
- Current: `/sync-documentation-maps` with user selecting both maps
- New: dispatch audits, user selects both maps, finalize updates
- Diff updated map files: should be equivalent

**Test 3: Partial updates**
- User selects skills map only → verify agent map unchanged
- User selects agent map only → verify skills map unchanged

---

## Implementation Notes

### Coordination

The three sub-skills (dispatch, collect, finalize) communicate via repo-owned artifacts:
- Checkpoint file: `.dev/sync-documentation-maps-checkpoint.json`
- Run directory: `.dev/sync-documentation-maps-runs/<run-id>/`
- Manifest: `.dev/sync-documentation-maps-runs/<run-id>/manifest.json`
- Audit result files and update result files stored under the run directory
- Team IDs remain orchestration metadata only, not the primary durable source of truth

### Backward Compatibility

- Current `/sync-documentation-maps` interface unchanged
- Optional new workflow: `/sync-documentation-maps --all` dispatches and auto-collects (all-in-one, if user prefers)

---

## Success Criteria

✅ Skill and agent audits run in parallel (not sequential)  
✅ Session token burn reduced from 1–2 hours to 30–60 min  
✅ User freed after 5–10 min dispatch phase  
✅ Audit results identical to current system  
✅ Updated maps identical to current system  
✅ Multi-session workflow supported (dispatch → later collect/finalize)  
✅ Same skill interface and workflow expectations maintained
