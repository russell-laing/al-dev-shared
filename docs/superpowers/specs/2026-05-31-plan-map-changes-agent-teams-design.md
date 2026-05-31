# Plan Map Changes with Agent Teams — Design Spec

**Date:** 2026-05-31  
**Status:** Approved for implementation  
**Author:** Brainstorming collaboration  

## Executive Summary

**Problem:** `/plan-map-changes` rubber-ducks architectural suggestions from map Observations sections, then writes an implementation plan. For 5–10 suggestions, rubber-ducking is expensive: each suggestion requires reading affected files, grepping for callers, verifying claims. On a large plugin surface, rubber-ducking alone consumes 30–60 minutes, followed by another 30 minutes for plan writing. Total: 1–1.5 hours per planning session.

**Solution:** Dispatch rubber-ducking to remote agents that verify suggestions in parallel, but keep durable state and duck records under repo-owned `.dev/` artifacts. Main session becomes:
1. Extraction phase (5 min): parse map Observations, build suggestion queue
2. Async rubber-ducking (10–20 min wall time): remote agents verify all suggestions in parallel
3. Resume/plan phase (30 min): collect repo-owned duck records, invoke writing-plans skill

**Expected outcome:**
- Session token burn: 1–1.5 hours → 45 minutes (40% reduction)
- Wall-clock time: 1–1.5 hours → 45 minutes (with async verification)
- Same suggestion vocabulary and plan format
- Better parallelization of expensive verification work

---

## Problem Statement

### Current Architecture

Today's `/plan-map-changes` rubber-ducks suggestions sequentially:

```
User: /plan-map-changes
  ↓
plan-map-changes (in-session)
  ├─ Phase 1: Extract suggestions from map Observations (5 min)
  │   └─ Parse docs/al-dev-skills-map.md and docs/al-dev-agent-map.md
  │
  ├─ Phase 2: Rubber-duck each suggestion (30–60 min, sequential or parallel)
  │   ├─ For suggestion 1: read files, grep, verify claim, write duck record
  │   ├─ For suggestion 2: read files, grep, verify claim, write duck record
  │   ├─ For suggestion 3...
  │   └─ [With parallelization for 3+ suggestions: dispatch parallel agents]
  │       └─ But coordination overhead remains; still reads must complete before plan writing
  │
  ├─ Phase 3: Write implementation plan (30 min)
  │   └─ Invoke superpowers:writing-plans with duck records
  │
  └─ Return plan to user
  ↓
Total: 1–1.5 hours of session tokens burned
```

**Bottleneck:** Even with parallelization, rubber-ducking requires extensive file reading and grepping. For 5–10 suggestions across large files, this is expensive. The current parallel-agent approach (for 3+) helps but adds coordination overhead.

### Current Constraints

- Per-suggestion rubber-duck cost: ~5–10 minutes (read files, grep, verify)
- For ≤2 suggestions: sequential inline path (~10–20 min)
- For 3+ suggestions: dispatches parallel agents (~10–30 min depending on complexity)
- Plan writing: always sequential (~30 min)

### Workflow Impact

Typical planning workflow after design analysis:
1. Run `/analyze-skill-design` or `/analyze-agent-design` (produces suggestions in Observations)
2. Run `/plan-map-changes` to rubber-duck and write plan (1–1.5 hours)
3. Can't do other work in same session (tokens exhausted)

Many users batch architectural changes, so suggestions (5–10+) are common.

---

## Solution: Remote Rubber-Duck Teams

### High-Level Architecture

Dispatch rubber-ducking to remote agents, parallelize verification work outside main session, and persist all durable artifacts inside the repo:

```
User: /plan-map-changes
  ↓
plan-map-changes (in-session, lightweight coordinator)
  ├─ Phase 1: Extract suggestions, build verification queue (5 min)
  └─ Phase 2: Spawn remote rubber-duck team, write repo-local run state (5 min)
  ↓
[Remote Rubber-Duck Team, async execution (~10–20 min wall time)]
  ├─ Receive: suggestion queue (5–10 suggestions, each with files to read)
  ├─ Dispatch: one agent per suggestion (parallel)
  │   └─ Each agent: read files, run U1–U3 checks, run type-specific checks, write one duck record artifact
  └─ Aggregate: update repo-owned run manifest / duck record set
  ↓
User: /plan-map-changes --resume  [runs when ready]
  ↓
plan-map-changes (resume/collect path, in-session)
  ├─ Read repo-owned duck records for active run (~5 min)
  ├─ Invoke superpowers:writing-plans with aggregated records (~30 min)
  └─ Return plan
  ↓
Total session time: ~40–45 min (vs. 1–1.5 hours)
```

**Key wins:**
- All suggestions rubber-ducked in parallel (wall-clock: 10–20 min, not 30–60 min)
- Main session freed after ~10 min dispatch phase
- Plan writing happens once, after all verification is done (no re-reading)
- Same public entry point, same suggestion vocabulary, same plan format

---

## Detailed Design

### Phase 1: Extract & Queue (In-Session, 5 min)

**Inputs:**
- Optional: `--skills`, `--agents`, or both (default)
- Optional: suggestion type filter (`trim`, `merge`, `split`, etc.)

**Steps:**

1. **Read map Observations sections**
   - Read `docs/al-dev-skills-map.md` and/or `docs/al-dev-agent-map.md`
   - Extract all open items from `## Observations` (or skill-specific sections)
   - Skip items marked `← implemented` or `← completed`

2. **Build suggestion queue**
   ```json
   {
     "surface": "both",
     "type_filter": "all",
     "suggestions": [
       {
         "id": "1",
         "type": "trim",
         "subject": "al-dev-code-review",
         "proposed_change": "Remove unused 'Read' tool from al-dev-code-review agent",
         "map_line": 42,
         "target_file": "profile-al-dev-shared/agents/al-dev-code-review.md"
       },
       {
         "id": "2",
         "type": "merge",
         "subject": "al-dev-plan + al-dev-architect",
         "proposed_change": "Merge al-dev-architect into al-dev-plan",
         "map_line": 55,
         "target_files": ["profile-al-dev-shared/skills/al-dev-plan/SKILL.md", "profile-al-dev-shared/skills/al-dev-architect/SKILL.md"]
       },
       ...
     ]
   }
   ```

3. **Determine parallelization**
   - If 1–2 suggestions: offer sequential inline path (skip agent dispatch, do in Phase 2 inline)
   - If 3+ suggestions: proceed to Phase 2 (dispatch agent team)

4. **Checkpoint**
   ```json
   {
     "operation": "plan-map-changes",
     "run_id": "<timestamp-or-uuid>",
     "spawned_at": "2026-05-31T11:00:00Z",
     "suggestion_count": 7,
     "surface": "both",
     "phase": "extract",
     "status": "ready_for_dispatch",
     "type_filter": "all",
     "result_dir": ".dev/plan-map-changes-runs/<run-id>/",
     "queue_path": ".dev/plan-map-changes-runs/<run-id>/suggestion-queue.json",
     "manifest_path": ".dev/plan-map-changes-runs/<run-id>/manifest.json"
   }
   ```

5. **Write repo-owned run artifacts**
   - Create `.dev/plan-map-changes-runs/<run-id>/`
   - Write the full suggestion queue to `suggestion-queue.json`
   - Write initial manifest to `manifest.json`
   - Keep `.dev/progress.md` updated so resume can recover the active run without depending on runtime-owned storage

**Token budget:** ~5 minutes

---

### Phase 2: Dispatch Rubber-Duck Team (In-Session, 5 min)

**Steps:**

1. **Determine team composition**
   - For N suggestions: spawn agent team with N duck workers (or batch N/4)
   - Team receives: suggestion queue, context (map content, knowledge files)

2. **Spawn remote rubber-duck team**
   - Pass: suggestion queue, target file list, knowledge context, and the repo-owned run directory contract
   - Team will: assign one duck worker per suggestion, execute in parallel, and write duck records into the run directory contract
   - Return: team ID

3. **Update checkpoint**
   ```json
   {
     "operation": "plan-map-changes",
     "run_id": "<timestamp-or-uuid>",
     "phase": "rubber_duck",
     "team_id": "<uuid>",
     "suggestion_count": 7,
     "status": "dispatched",
     "result_dir": ".dev/plan-map-changes-runs/<run-id>/",
     "manifest_path": ".dev/plan-map-changes-runs/<run-id>/manifest.json"
   }
   ```

4. **Return to user**
   - Print: `"Dispatched rubber-duck verification for 7 suggestions."`
   - Print: `"Re-run /plan-map-changes --resume when you want to collect results and write the plan."`
   - Exit skill

**Token budget:** ~5 minutes

---

### Phase 2a: Rubber-Duck Execution (Remote, Async, 10–20 min Wall Time)

**Executed by remote rubber-duck team**

**Each duck worker agent:**

1. **Receive one suggestion**
   - Type (trim, merge, split, etc.)
   - Target files to read
   - Proposed change description

2. **Read and analyze target files**
   - Read full content of all files mentioned in suggestion
   - For agents: read agent.md file completely
   - For skills: read SKILL.md file completely
   - Build symbol/reference index (functions, agents, etc.)

3. **Run universal checks** (U1–U3)
   - U1: File accessibility and basic syntax
   - U2: Artifact presence (does X exist in the file?)
   - U3: Reference validity (is X actually used/referenced elsewhere?)

4. **Run type-specific checks**
   - Reference: `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`
   - For **Trim**: verify tool is unused, no downstream deps
   - For **Merge**: verify both skills/agents exist, identify overlaps, check callers
   - For **Split**: verify target has separable concerns, check handoff gaps
   - For **Inline**: verify target used by only one caller, check call sites
   - For **Align**: verify input/output contract mismatch, check callers
   - (Similar checks for skill-type suggestions)

5. **Write duck record**
   ```json
   {
     "suggestion_id": "1",
     "type": "trim",
     "subject": "al-dev-code-review",
     "claim": "Remove unused 'Read' tool",
     "state": "Confirmed: Read tool is declared in frontmatter but not used in body",
     "side_effects": [
       "al-dev-expert-reviewer invokes al-dev-code-review; verify it doesn't pass file reading to this agent"
     ],
     "scope_gap": "None",
     "verdict": "proceed",
     "evidence": {
       "file_read": "profile-al-dev-shared/agents/al-dev-code-review.md",
       "tool_usage_check": "Read not found in body; grep for 'Read' returned no matches",
       "caller_check": "5 callers found; all pass LSP results, not file reads"
     }
   }
   ```

6. **Return record to repo-owned run artifacts**
   - Write to: `.dev/plan-map-changes-runs/<run-id>/duck-records/<suggestion_id>.json`
   - Update: `.dev/plan-map-changes-runs/<run-id>/manifest.json`
   - Mark in manifest: suggestion 1 complete, with status, timestamp, and record path

---

### Phase 3: Collect & Plan via `/plan-map-changes --resume` (In-Session, 35–45 min)

**Inputs:**
- `--resume` (required for this path)
- Active repo-local checkpoint and run directory
- Optional internal wait behavior if implementation chooses to poll before reading artifacts

**Steps:**

1. **Locate and validate repo-owned run state**
   - Read `.dev/progress.md`
   - Read `.dev/plan-map-changes-runs/<run-id>/manifest.json`
   - Extract active team ID, suggestion queue, completed records, and any failures
   - If no active run exists, report: `"No resumable /plan-map-changes run found. Start a new run with /plan-map-changes."`

2. **Verify collection integrity**
   - Check: every queued suggestion has either a duck record path or an explicit failed/pending status in the manifest
   - If any missing: report which and offer to re-run missing suggestions or proceed with partial

3. **Review duck records for skips**
   - Any verdict = `skip`? Note reasons; these suggestions will be excluded from plan

4. **Build plan context**
   - Aggregate all duck records from `.dev/plan-map-changes-runs/<run-id>/duck-records/`
   - Extract verified file paths, scopes, side-effects
   - Correct any flag/name mismatches found during rubber-ducking
   - Order suggestions: additive changes first, structural changes last

5. **Invoke writing-plans skill**
   ```
   Invoke: superpowers:writing-plans
   Context:
     - All duck records (verified claims, evidence, verdicts)
     - Corrected scope and file paths
     - Ordering: additive first, structural last
     - Task pattern: verify with ls, diff, wc -l, grep
   ```

6. **Writing-plans returns plan**
   - Writes to: `docs/superpowers/plans/YYYY-MM-DD-plugin-map-<label>.md`
   - Includes: task ordering, verification steps, commit groups

7. **Return to user**
   - Present plan summary
   - Next step: `Use /superpowers:executing-plans to run the plan`

**Token budget:** ~35–45 minutes (mostly in writing-plans invocation)

---

## Resume Behavior

**Scenario: Duck team dispatched, user collects next day**

```bash
/plan-map-changes --resume
```

Checkpoint and run artifacts persist the active run; results are read from `.dev/plan-map-changes-runs/<run-id>/` and the plan is written on-demand.

**Scenario: Duck team partially complete**

- Collection detects missing records
- User can retry `/plan-map-changes --resume`
- Or: re-dispatch with `--resume` flag to complete missing suggestions

---

## Error Handling

### Duck Verification Failure

- If a duck agent fails (can't read file, symbol not found): returns partial record with error
- Collection detects and reports which suggestions failed verification
- User can proceed with verified suggestions, or re-run team to retry failed ones

### Plan Writing Failure

- If writing-plans skill fails: duck records already collected and validated
- User can manually retry `/plan-map-changes --resume` without re-doing verification

### Partial Completion

- If some suggestions don't have duck records when collection tries to fetch: report which are missing
- User can wait for completion or proceed with partial list

### Artifact Ownership Rule

- Remote agents may perform the verification work.
- Durable state, suggestion queues, manifests, and duck records must live under `.dev/plan-map-changes-runs/<run-id>/`.
- The lead session must be able to resume from repo-owned artifacts alone, even if runtime-managed team storage is unavailable later.

---

## Testing & Verification

### Performance Validation

| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| Rubber-duck phase (tokens) | 30–60 min | ~10–20 min async + 5 min coordination | 20–50 min saved |
| Plan writing (tokens) | 30 min | 30 min (same) | None |
| Total session time | 1–1.5 hours | 40–50 min | 40–50% reduction |

### Correctness Validation

**Test 1: Duck record equivalence**
- Extract 5 suggestions from map Observations
- Run current `/plan-map-changes` → capture all duck records
- Run new system (dispatch + collect) → capture all duck records
- Compare: records should be equivalent (claim, state, verdict)

**Test 2: Plan equivalence**
- Current: `/plan-map-changes` with manual duck records
- New: dispatch teams, collect, invoke writing-plans
- Diff generated plan files: should be equivalent

**Test 3: Partial verification**
- Dispatch duck team with 7 suggestions
- Allow 3 to complete, then collect
- Verify: 3 suggestions have duck records, 4 are pending
- User can retry or proceed with partial

---

## Implementation Notes

### Single Suggestion Edge Case

If user runs `/plan-map-changes` with only 1 suggestion:
- Phase 1 detects 1 suggestion
- Default to inline verification
- Only dispatch a remote team if implementation later proves a strong reason for that edge case

### Team Capacity

- Remote team manages up to N parallel duck workers (N = team size)
- Typical team: 4–6 workers per team
- For 10 suggestions: 2 waves of 5, completes in ~15 min wall-clock

---

## Success Criteria

✅ Rubber-ducking all suggestions runs in parallel (not sequential)  
✅ Session token burn reduced from 1–1.5 hours to 40–50 min  
✅ User freed after 10 min dispatch phase  
✅ Duck records identical to current system  
✅ Generated plan identical to current system  
✅ Multi-session workflow supported through `/plan-map-changes` plus repo-owned `.dev/` artifacts  
✅ Same public entry point, suggestion vocabulary, and plan format maintained
