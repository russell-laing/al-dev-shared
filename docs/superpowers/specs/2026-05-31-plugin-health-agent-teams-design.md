# Plugin-Health Agent Teams Parallelization — Design Spec

**Date:** 2026-05-31  
**Status:** Approved for implementation  
**Author:** Brainstorming collaboration  

## Executive Summary

**Problem:** `/plugin-health` consumes 5+ hours of session tokens daily, making it impossible to do substantive work in the same session. The skill dispatches 15+ design and quality lenses sequentially in batched waves, burning tokens linearly.

**Solution:** Distribute lens execution to a remote agent team that runs in parallel across multiple Claude contexts, but keep durable workflow state and lens results under repo-owned `.dev/` artifacts. Main session moves to a lightweight dispatch-and-resume model:
1. Dispatch phase (30-45 min): build work queue, spawn remote team, return immediately
2. Async execution (5-15 min wall time): lenses run in parallel remotely
3. Collection phase (15-20 min): fetch results, write dossier, report findings

**Expected outcome:**
- Session token burn: 5+ hours → ~1 hour (80-90% reduction)
- Wall-clock time: 5+ hours → ~1 hour (with async work happening in background)
- Same skill interface and workflow; user immediately freed to do other work

---

## Problem Statement

### Current Architecture

Today's `/plugin-health` runs a full health sweep in a single session:

```
User: /plugin-health --surface both --dimension all
  ↓
plugin-health (in-session)
  ├─ Phase 1: Build file lists, pre-dispatch aggregation (~5 min)
  ├─ Phase 3a: Dispatch lenses in sequential waves (~4+ hours)
  │   ├─ Wave 1: Dispatch agents 1–3 (parallel within wave)
  │   ├─ Wait for completion
  │   ├─ Wave 2: Dispatch agents 4–6
  │   ├─ Wait for completion
  │   └─ ... (8+ waves total)
  └─ Phase 4: Assemble findings, write dossier (~10 min)
  ↓
User gets report, session is exhausted (5+ hours burned)
```

**Bottleneck:** Lenses are dispatched in sequential waves to fit within per-wave token budgets. Each wave completes before the next begins, preventing parallelization.

### Current Constraints

- Session token limit: ~500k tokens per 5-hour window
- Per-lens cost: ~5000 tokens (varies by scope)
- Lenses per wave: ~3 (limited by token budget)
- Total lenses: ~15–20 across both surfaces and dimensions
- Sequential waves = ~4–5 hours total

### Workflow Impact

Current workflow:
1. Day N, Session 1: `/plugin-health` (5+ hours, consumes entire session)
2. Day N, Session 2 (next day): Review findings, run `/superpowers:subagent-driven-development` to implement top 5 actions

The daily health check effectively blocks any other development work in Session 1.

---

## Solution: Remote Agent Team Dispatch

### High-Level Architecture

Move lens execution outside the main session by spawning a remote agent team:

```
User: /plugin-health --surface both --dimension all
  ↓
plugin-health (in-session, lightweight)
  ├─ Phase 1: Build file lists, pre-dispatch aggregation (~5 min)
  ├─ Phase 2: Build work queue, spawn remote agent team, return team ID (~40 min total)
  └─ Exit immediately; user is free
  ↓
[Remote Agent Team, async execution (~5–15 min wall time)]
  ├─ Team receives work queue
  ├─ Spawns up to N parallel lens agents
  ├─ Each lens executes independently → writes result artifacts into the repo-owned run contract
  └─ Team completes when all lenses finish or timeout
  ↓
User: /plugin-health --resume  [runs when ready]
  ↓
plugin-health (resume/collect path, in-session, lightweight)
  ├─ Fetch results from remote team (~10 min)
  ├─ Aggregate findings, write dossier (~10 min)
  └─ Report results
  ↓
User gets report; main session still has token budget remaining
```

**Key wins:**
- Main session freed after ~45 minutes (instead of locked for 5+ hours)
- Lenses run in parallel in remote contexts (wall-clock time: 5–15 min for all lenses)
- User can do other work while lenses execute, or wait for results
- Same public entry point; collection happens through `/plugin-health --resume`

---

## Detailed Design

### Phase 1: Dispatch (In-Session, 30–45 min)

**Inputs:**
- Arguments: `--surface` (plugin | tooling | both), `--dimension` (design | quality | all), optional `--resume`

**Steps:**

1. **Parse arguments and validate**
   - Validate surface/dimension combinations
   - If `--resume` flag, check for prior checkpoint file (see Resume Behavior)

2. **Build file lists** (same as current Phase 1)
   ```bash
   find profile-al-dev-shared/agents -name "*.md"
   find profile-al-dev-shared/skills -name "SKILL.md"
   find .claude/agents -name "*.md"
   find .claude/skills -name "SKILL.md"
   ```

3. **Pre-dispatch aggregation** (same as current Phase 2)
   - Parse `docs/al-dev-agent-map.md`: extract tool inventory, model assignments, caller map
   - Parse `docs/al-dev-plugin-map.md`: extract layer 1 diagram, phase counts, handoff chains
   - Compute derived mappings: agent usage counts, single-use agents, no-agent skills

4. **Determine lens scope**
   - Build lens list based on `--dimension` and `--surface` flags
   - Example: `--dimension design --surface plugin` → only design lenses for plugin surface

5. **Resume detection** (if `--resume` flag)
   - Check for checkpoint file: `.dev/plugin-health-team-checkpoint.json`
   - Extract: prior team ID, run ID, list of completed lenses, result directory
   - Compute: remaining lenses = all lenses − completed lenses
   - Log: "Resuming team <id>: X lenses already completed, Y remaining"

6. **Build work queue**
   ```json
   {
     "surface": "both",
     "dimension": "all",
     "agent_files": ["agent1.md", "agent2.md", ...],
     "skill_files": ["skill1/SKILL.md", "skill2/SKILL.md", ...],
     "context": {
       "tool_inventory": {...},
       "model_assignments": {...},
       "caller_map": {...},
       "agent_usage_counts": {...},
       "phase_counts": {...},
       "handoff_chains": {...},
       "preplanning_skills": [...],
       "layer1_diagram_content": "..."
     },
     "lenses": [
       {
         "name": "design-agent-lens-tool-hygiene",
         "files": ["agent1.md", "agent2.md", ...],
         "context_fields": ["tool_inventory"]
       },
       {
         "name": "design-skill-lens-complexity",
         "files": ["skill1/SKILL.md", "skill2/SKILL.md", ...],
         "context_fields": ["phase_counts", "no_agent_skills"]
       },
       ...
     ]
   }
   ```

7. **Spawn remote agent team**
   - Invoke managed agent with team mode enabled
   - Pass work queue as initialization payload plus the repo-owned artifact contract
   - Receive: team ID (globally unique)
   - Write checkpoint file: `.dev/plugin-health-team-checkpoint.json`
   ```json
   {
     "run_id": "<timestamp-or-uuid>",
     "team_id": "<uuid>",
     "surface": "both",
     "dimension": "all",
     "spawned_at": "2026-05-31T14:30:00Z",
     "completed_lenses": [],
     "status": "dispatched",
     "result_dir": ".dev/plugin-health-runs/<run-id>/",
     "manifest_path": ".dev/plugin-health-runs/<run-id>/manifest.json"
   }
   ```

8. **Write repo-owned run artifacts**
   - Create `.dev/plugin-health-runs/<run-id>/`
   - Write work queue to `.dev/plugin-health-runs/<run-id>/work-queue.json`
   - Write manifest scaffold to `.dev/plugin-health-runs/<run-id>/manifest.json`
   - Keep `.dev/progress.md` aligned with the active run ID and current phase

9. **Return to user**
   - Print: `"Dispatched health sweep team <id>. Lenses running in background."`
   - Print: `"Re-run /plugin-health --resume when you want to collect results."`
   - Record the active team ID in the checkpoint so resume can recover it without a second public command
   - Exit skill

**Token budget:** ~30–45 minutes (mostly from aggregation context building)

---

### Phase 2: Lens Execution (Remote, Async, 5–15 min Wall Time)

**Executed by remote agent team (outside main session)**

**Steps:**

1. **Team receives work queue**
   - Deserialize work queue from initialization payload
   - Extract lens list, file lists, context

2. **Spawn lens agents in parallel batches**
   - Determine safe batch size (e.g., 4–6 lenses per batch) based on remote token budget
   - For each batch:
     ```
     Batch 1: [design-agent-lens-tool-hygiene, design-agent-lens-model-fit, design-agent-lens-scope-isolation]
     Batch 2: [design-agent-lens-caller-alignment, design-agent-lens-usage-patterns, design-skill-lens-complexity]
     Batch 3: ...
     ```

3. **Each lens agent executes independently**
   - Receive: files to analyze, relevant context fields
   - Run lens logic (same as current lens agents)
   - Return: findings block (or empty if no findings)
   - Write result artifact into `.dev/plugin-health-runs/<run-id>/lens-results/<lens_name>.json`

4. **Progress tracking**
   - Team maintains a progress manifest:
     ```json
     {
       "team_id": "<uuid>",
       "status": "in_progress",
       "total_lenses": 20,
       "completed": [
         {"name": "design-agent-lens-tool-hygiene", "status": "success", "timestamp": "..."},
         {"name": "design-agent-lens-model-fit", "status": "success", "timestamp": "..."}
       ],
       "pending": ["design-agent-lens-scope-isolation", ...],
       "failed": []
     }
     ```

5. **Completion condition**
   - All lenses complete, OR
   - Team timeout (hard limit, e.g., 30 min wall time), OR
   - Critical failure (team unrecoverable)
   - Mark team status: `success` | `partial` | `failed`

**Result Management:**
- Each lens writes findings to `.dev/plugin-health-runs/<run-id>/lens-results/<lens_name>.json`
- The team updates `.dev/plugin-health-runs/<run-id>/manifest.json`
- Durable resume state remains repo-owned even if runtime-managed team storage is unavailable later
- Team ID is still useful for orchestration, but it is not the primary durable source of truth

---

### Phase 3: Collection & Reporting via `/plugin-health --resume` (In-Session, 15–20 min)

**Inputs:**
- `--resume` (required for this path)
- Active checkpoint from the prior dispatch phase
- Optional internal wait behavior if the implementation chooses to poll before collecting

**Steps:**

1. **Locate and validate checkpoint**
   - Read `.dev/plugin-health-team-checkpoint.json`
   - Extract team ID, run ID, surface, dimension, spawned timestamp, result directory
   - If no active checkpoint exists, report: `"No resumable plugin-health run found. Start a new sweep with /plugin-health."`

2. **Fetch team status**
   - Query team status only if orchestration metadata is available
   - If team is still running, either poll briefly or collect partial results, depending on implementation choice
   - Resume must tolerate partial state and never require the user to call a second public command

3. **Read lens results from repo-owned run artifacts**
   - Read `.dev/plugin-health-runs/<run-id>/manifest.json`
   - For each completed lens in the manifest, read `.dev/plugin-health-runs/<run-id>/lens-results/<lens_name>.json`
   - Aggregate into in-memory findings structure
   ```python
   findings = {}
   for lens_result in remote_results:
       lens_name = lens_result['name']
       findings[lens_name] = lens_result['findings_block']
   ```

4. **Assemble findings file**
   - Write to: `docs/health/2026-05-31-<surface>-findings.md`
   - Structure:
     ```markdown
     # <Surface> Findings — 2026-05-31

     ## Raw lens output

     ### Design Agent Lens: Tool Hygiene
     [findings block]

     ---

     ### Design Agent Lens: Model Fit
     [findings block]

     ...

     ## Failed lenses
     - design-skill-lens-near-duplicates (timeout)

     ## Resume information
     - Total lenses in scope: 20
     - Completed: 18
     - Status: PARTIAL — call with `--resume` to complete missing lenses
     ```

5. **Rank findings and write dossier**
   - Run ranking logic (same as current plugin-health-report)
   - Extract top 5 suggestions
   - Write dossier to: `docs/health/2026-05-31-<surface>-health.md`
   - Refresh plugin dependency graph (plugin surface only)

6. **Update checkpoint**
   - Mark collection complete in `.dev/plugin-health-team-checkpoint.json`
   - Record: results collected at, findings file path, dossier file path

7. **Present results to user**
   - Print dossier summary
   - Highlight top 5 suggestions
   - Next step: `Use /superpowers:writing-plans to implement top 5 actions`

**Token budget:** ~15–20 minutes

---

### Resume Behavior

**Scenario: User's dispatch session ends before collection begins**

1. **In new session, user runs:**
   ```bash
   /plugin-health --resume
   ```

2. **Skill reads checkpoint:**
   - Finds prior team ID from `.dev/plugin-health-team-checkpoint.json`
   - Fetches results
   - Completes collection and dossier (same as normal flow)

**Scenario: Remote team work is interrupted (partial results)**

1. **Collection detects partial results:**
   - Remaining lenses marked `pending` in manifest
   - Dossier reports: "PARTIAL — X of Y lenses completed"

2. **User runs (in new session):**
   ```bash
   /plugin-health --resume
   ```

3. **Dispatch phase detects prior checkpoint:**
   - Extracts completed lens list
   - Builds new work queue with only `pending` lenses
   - Spawns new team (or extends prior team if still alive)
   - Returns new team ID

4. **Collection aggregates both results:**
   - Reads prior findings from `docs/health/` checkpoint
   - Merges new lens results from current team
   - Writes final dossier with all results

---

## Error Handling

### Lens Failure

**Single lens fails** (agent crashes, malformed output, timeout):
- Team marks lens status: `failed` with error message
- Other lenses continue (no cascade failure)
- Collection phase includes failed lens in findings:
  ```markdown
  ### Design Skill Lens: Handoff Gaps — FAILED
  Error: Agent timed out after 5 minutes. Check team logs for details.
  ```
- User can manually re-run via `--resume` in a fresh session

### Partial Completion

**Remote team timeout (some lenses incomplete after hard limit):**
- Team returns results for completed lenses only
- Marks remaining lenses as `pending` with reason (timeout)
- Collection reports: "12 of 15 lenses completed. Remaining lenses: [list]"
- User can call `/plugin-health --resume` to complete missing lenses

### Network / Collection Failure

**Result fetch fails** (network error, remote store unavailable):
- Collection phase retries with exponential backoff (3 attempts)
- If all retries fail:
  - Checkpoint persists with partial state
  - User can retry `/plugin-health --resume`
  - Repo-owned work artifacts remain under `.dev/plugin-health-runs/<run-id>/`; no re-dispatch needed for already completed lenses

### Duplicate Teams

**User accidentally spawns two teams** (e.g., runs `/plugin-health` twice instead of resuming):
- Each spawn creates a unique team ID
- Checkpoint file updated with latest team ID
- Prior team continues executing (no harm)
- Optional: expose internal diagnostics later, but do not add a second public collection command

### Success Criteria

| Scenario | Outcome | Next Step |
|----------|---------|-----------|
| All lenses complete | Findings file + dossier written, graph refreshed | Run `/superpowers:writing-plans` |
| Partial completion (some timeouts) | Findings aggregated from completed, report notes status | Run `/plugin-health --resume` to finish |
| No lenses complete | Report shows all lenses pending, no findings written | Check team status or run `/plugin-health --resume` |

---

## Testing & Verification

### Performance Validation

**Metric 1: Session token cost**
- **Before:** Single session, `plugin-health` consumes 5+ hours of tokens
- **After:** 
  - Dispatch phase: ~45 min tokens
  - Collection phase: ~20 min tokens
  - Total: ~1 hour tokens (vs. 5+ hours)
  - **Savings:** 80–90% reduction

**Measurement:**
```bash
# Current system (baseline)
time /plugin-health --surface both --dimension all
echo "Session tokens remaining: <check harness>"

# New system (target)
time /plugin-health --surface both --dimension all
echo "Session tokens after dispatch: <should be ~7/8 remaining>"
time /plugin-health --resume
echo "Session tokens after collection: <should be ~6/8 remaining>"
```

**Metric 2: Wall-clock time**
- **Before:** 5+ hours (user waits)
- **After:** 
  - Dispatch: 30–45 min
  - Async execution: 5–15 min (background, user freed)
  - Collection: 15–20 min (user waits for report)
  - **Total perceived time:** 45 min until results (vs. 5+ hours)

### Correctness Validation

**Test 1: Full sweep equivalence**
- Run `/plugin-health --surface both --dimension all` on current system → capture findings
- Run new system (dispatch + collection) with same scope → capture findings
- Diff findings blocks: should be identical (modulo ordering/timestamps)
- Dossier ranking and suggestions should be unchanged

**Test 2: Partial scope**
- Run `/plugin-health --surface plugin --dimension design` (current) → findings A
- Run new system with same scope → findings B
- Verify A ≈ B

**Test 3: Resume behavior**
- Spawn dispatch, allow remote team to complete 50% of lenses
- Call `/plugin-health --resume` with partial results available
- Verify findings file written with partial results
- Call `/plugin-health --resume` to complete remaining lenses
- Call `/plugin-health --resume` again to finalize once the remaining results exist
- Verify final findings contain all lenses' results

### Regression Testing

**Test 4: Concurrent teams**
- Spawn team A with `--surface plugin --dimension design`
- Spawn team B with `--surface tooling --dimension quality` (overlapping file analysis)
- Verify both teams execute without interference
- Collect from each team independently
- Verify results are independent and correct

**Test 5: Failure resilience**
- Inject synthetic lens failure (mock agent that crashes)
- Spawn dispatch, allow team to execute
- Verify: failed lens marked as failed, other lenses complete
- Collection phase includes failed lens in report
- User can re-run failed lens via `--resume`

**Test 6: Resume collection path**
- Spawn dispatch and let the remote team complete
- Verify: dispatch returns and checkpoint records the active team
- User calls `/plugin-health --resume`
- Verify: resume fetches results and writes findings/dossier without requiring any other public command

---

## Implementation Notes

### Managed Agent Infrastructure

This design assumes Claude Code has support for **managed agent teams** (remote, parallel execution with shared result store). If not available:

**Fallback option:**
- Implement agent team as a distributed async pattern using Claude Batch API
- Dispatch batch job containing all lens agents
- Poll batch status endpoint until completion
- Fetch results from batch output store
- Collection phase remains the same

### Result Storage

**Requirement:** Durable artifacts must be repo-owned:
- `.dev/plugin-health-runs/<run-id>/work-queue.json`
- `.dev/plugin-health-runs/<run-id>/manifest.json`
- `.dev/plugin-health-runs/<run-id>/lens-results/<lens_name>.json`
- Retention: enough for next-session resume and manual inspection

**Options:**
1. Remote team writes directly into repo-owned `.dev/` paths
2. Remote team writes to temporary runtime storage, but the lead session or orchestrator mirrors each completed artifact into repo-owned `.dev/` paths immediately
3. Batch infrastructure may exist underneath, but it must not be the only durable artifact owner

### Backward Compatibility

**Current users of `/plugin-health`:**
- Skill signature unchanged (`--surface`, `--dimension`, `--resume`)
- Output format (findings file, dossier) unchanged
- Public entry point unchanged (`/plugin-health` starts and resumes the workflow)
- Only difference: user experience (45 min dispatch + async, then `/plugin-health --resume` to collect/report, vs. 5+ hour single session)
- Durable state moves to explicit repo-owned run artifacts under `.dev/plugin-health-runs/`

**Migration path:**
- Deploy new dispatch logic
- Existing `/plugin-health --resume` calls work without change (checkpoint detection)
- Old single-session approach still available (fallback) if agent team infrastructure unavailable

---

## Success Criteria

✅ Session token burn reduced from 5+ hours to ~1 hour per run  
✅ Wall-clock time for results: ~45 min to dispatch + async execution, vs. 5+ hour lock  
✅ User freed to do other work immediately after dispatch (45 min into session)  
✅ Findings and dossier output identical to current system  
✅ Resume behavior works seamlessly across session boundaries  
✅ Partial failures (lens crashes, timeouts) don't block entire sweep  
✅ Daily health sweep no longer blocks other development work in same session
