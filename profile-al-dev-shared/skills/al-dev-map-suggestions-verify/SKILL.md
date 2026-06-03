---
name: al-dev-map-suggestions-verify
description: >-
  Verify and rubber-duck existing map suggestions before creating an implementation plan.
  Rubber-duck architectural suggestions from map Observations using parallel
  background agent teams, reducing token burn from 1-1.5 hours to 40-50 min
argument-hint: "[--resume] [--surface skills|agents|both] [--filter trim|merge|...]"
---

# Skill: /al-dev-map-suggestions-verify

Verify architectural change suggestions from `docs/al-dev-skills-map.md` and `docs/al-dev-agent-map.md`
Observations sections using parallel background agent teams. Reduces session token burn from 1-1.5 hours
to 40-50 minutes through async verification and multi-session checkpoint/resume workflow.

## Overview: Three Entry Points

**Entry 1: Initial dispatch** (`/al-dev-map-suggestions-verify` or `/al-dev-map-suggestions-verify --surface agents --filter trim`)

- Phase 1: Extract suggestions from map Observations
- Phase 2: Dispatch background team for 3+ suggestions, or inline verify 1-2
- Returns early; user freed to work while team verifies in background

**Entry 2: Resume after team completion** (`/al-dev-map-suggestions-verify --resume`)

- Phase 3: Collect & Plan generation
- Aggregate duck records into plan document
- Invoke superpowers:writing-plans to generate implementation plan

**Success metric:** 40-50 min total session token burn (Phase 1: ~5 min, Phase 2: ~5 min, Phase 3: ~30-40 min)
vs 1-1.5 hours for single-session sequential verification. Parallelization of 5-10 suggestions across
a background team avoids sequential tool use overhead.

## Reference Documents

- `../../knowledge/map-change-rubber-duck-checks.md` — Verification procedures (U1-U3 universal checks, type-specific checks)
- `./MANIFEST-SCHEMA.md` — JSON schemas for checkpoint and manifest files
- `./extract-suggestions.py` — Phase 1 extraction script

## Architecture: Three Phases

### Phase 1: Extract Suggestions

Parse map Observations sections and build suggestion queue. Determine parallelization path based on count:

- ≤2 suggestions → proceed to inline verification
- 3+ suggestions → proceed to background team dispatch

**Inputs:**

- `--surface skills|agents|both` (default: both)
- `--filter all|trim|merge|...` (default: all)
- Map files: `docs/al-dev-skills-map.md`, `docs/al-dev-agent-map.md`

**Outputs:**

- `.dev/al-dev-map-suggestions-verify-runs/<run-id>/suggestion-queue.json` — Suggestions to verify
- `.dev/al-dev-map-suggestions-verify-runs/<run-id>/manifest.json` — Manifest with status tracking

**Exit status:**

- 0 if suggestions found
- 1 if no suggestions in queue or extraction failed

**Checkpoint update (Phase 1 complete):**

After extraction completes, update `.dev/progress.md` with:

- `phase: extracting`
- `status: completed`
- `suggestion_count: <count>`
- `manifest_path: .dev/al-dev-map-suggestions-verify-runs/<run-id>/suggestion-queue.json`

### Phase 2: Dispatch or Inline Verify

## Path A: Inline verification (1-2 suggestions)

For each suggestion, synchronously:

1. Read target files specified in suggestion
2. Run universal checks (U1-U3): file accessibility, syntax, references
3. Run type-specific checks (trim/merge/split/inline/align/connect/promote)
4. Write duck record (success) or error record (failure) to `.dev/al-dev-map-suggestions-verify-runs/<run-id>/duck-records/`
5. Jump to Phase 3 collection

**Why inline for small batches:** Avoids 5-minute background team setup overhead for trivial batches.

## Path B: Background team dispatch (3+ suggestions)

> **Independence assumption:** The 3+ threshold assumes suggestions are mostly independent (targeting different files or output artifacts). For dependent suggestions that modify the same files (e.g., both updating the same skill), consider running inline verification even if count ≥3 to avoid parallel verification conflicts.

1. Build team context JSON with all suggestions
2. Dispatch one background duck worker agent per suggestion in parallel, following
   the canonical pattern in `../../knowledge/background-agent-dispatch.md`
3. Update `.dev/progress.md` checkpoint with run state (run_id, phase=2, status=dispatched)
4. Return to user with message: "Dispatched X suggestions to verification team. Run `/al-dev-map-suggestions-verify --resume` when ready."

**Why background dispatch for large batches:** Each suggestion takes 5-10 minutes to verify (reading files, running checks, writing records).
Parallel background agents avoid sequential tool use overhead (each tool context switch costs ~30 seconds).

### Phase 3: Collect & Plan Generation

Invoked via `/al-dev-map-suggestions-verify --resume`. Validates multi-session state and aggregates results.

1. Read `.dev/progress.md` for active al-dev-map-suggestions-verify state (run_id, manifest path)
2. Validate manifest exists and is readable
3. Poll manifest until all suggestions completed or timeout (10 min default)
4. For incomplete suggestions: ask user (wait / proceed partial / abort)
5. For failed suggestions: ask user (retry / skip / abort)
6. Aggregate all duck records into single verification summary
7. Invoke superpowers:writing-plans with aggregated duck records as context
8. Writing-plans generates implementation plan with duck evidence attached
9. Update `.dev/progress.md` to mark run complete, clear entry on exit

**Outputs:**

- `.dev/YYYY-MM-DD-al-dev-plan-plan.md` — Implementation plan (generated by writing-plans)
- Duck records aggregated into plan preamble/context section

## Implementation Guide

### Phase 1: Extract Suggestions (Standalone Script)

Call `extract-suggestions.py` to parse map Observations and build the suggestion queue:

```bash
python3 profile-al-dev-shared/skills/al-dev-map-suggestions-verify/extract-suggestions.py \
  --surface both \
  --filter all \
  --output .dev/al-dev-map-suggestions-verify-runs/<run-id>/suggestion-queue.json
```

**Script behavior:**

- Accepts: `--surface {skills|agents|both}`, `--filter {all|trim|merge|split|inline|align|connect|promote}`, `--output <path>`
- Returns exit code 0 if suggestions found, 1 if empty
- Writes JSON: `{"suggestion_count": N, "suggestions": [...]}`
- Each suggestion has: `id`, `type`, `subject`, `proposed_change`, `target_files`

**Schema reference:** See `./MANIFEST-SCHEMA.md` for full suggestion object structure.

### Phase 2: Route Verification

**Logic:**

- If ≤2 suggestions: Run inline verification (call `validate-suggestions.py`), jump to Phase 3
- If 3+ suggestions: Dispatch a background duck worker team, return to user, wait for `--resume`

**Inline verification call:**

```bash
python3 profile-al-dev-shared/skills/al-dev-map-suggestions-verify/validate-suggestions.py \
  --suggestion-queue .dev/al-dev-map-suggestions-verify-runs/<run-id>/suggestion-queue.json \
  --output .dev/al-dev-map-suggestions-verify-runs/<run-id>/duck-records/ \
  --manifest .dev/al-dev-map-suggestions-verify-runs/<run-id>/manifest.json
```

**Script behavior:**

- Reads suggestion queue from Phase 1
- Runs U1-U3 universal checks (file accessibility, artifact presence, references)
- Runs type-specific checks (trim, merge, split, inline, align, connect, promote)
- Writes duck records (success verdicts: ACCEPT/REJECT/DEFER, or error records) to output directory
- Returns exit code 0 if all checks passed, 1 if failures

**Background team dispatch call** (for 3+ suggestions):

See `../../knowledge/background-agent-dispatch.md` for the canonical parallel
background-dispatch pattern (run directory, file handoff, artifact-presence gate).

High-level steps:

1. Write team context JSON to `.dev/al-dev-map-suggestions-verify-runs/<run-id>/team-context.json`
2. Dispatch one background duck worker agent per suggestion, in parallel
3. Each agent reads suggestion, runs checks, writes duck record
4. Update `.dev/progress.md` checkpoint with manifest path
5. Return to user: "Dispatched N suggestions. Run `/al-dev-map-suggestions-verify --resume` when ready."

### Phase 3: Resume & Collect

Entry point: `/al-dev-map-suggestions-verify --resume`

**Manifest polling logic:**

1. Read `.dev/progress.md` for `run_id` and `manifest_path`
2. Poll manifest every 10 seconds until all suggestions complete or timeout (10 min default)
3. On timeout: ask user (wait longer / proceed partial / abort)
4. On failures: ask user (skip / retry / abort)

**Duck record aggregation:**

1. Read all `.json` files from `.dev/al-dev-map-suggestions-verify-runs/<run-id>/duck-records/`
2. Filter by verdict: ACCEPT / DEFER / REJECT
3. Format duck records as markdown context

**Plan generation:**

Invoke `superpowers:writing-plans` with aggregated duck records and context:

- ACCEPT records: recommended implementations
- DEFER records: requires architect review
- REJECT records: rationale for rejection

**Checkpoint cleanup:**

1. Update `.dev/progress.md`: phase=completed, status=completed
2. Remove al-dev-map-suggestions-verify section from `.dev/progress.md`
3. Return success (plan document written by writing-plans)

**Full script details:**

See `validate-suggestions.py` for the complete implementation of U1-U3 checks and type-specific verification functions.

## Validation & Error Handling

**Pre-execution validation:**

1. Verify map files exist: `docs/al-dev-skills-map.md`, `docs/al-dev-agent-map.md`
2. Verify extract-suggestions.py is executable
3. Verify `.dev/` directory writable

**Phase 1 errors:** No suggestions found → return 1 (normal exit)

**Phase 2 errors:**

- Inline verification U1/U2/U3 failure → write error record, proceed to Phase 3
- Background dispatch failure → ask user (inline instead / abort)

**Phase 3 errors:**

- Progress.md missing → display recovery steps
- Manifest missing/corrupted → ask user to locate manually
- Duck records incomplete after timeout → ask user (wait / partial / abort)

## Testing & Validation

See `./tests/test-extract.py` for Phase 1 extraction unit tests.
See `./validate-plan-changes.py` for manifest schema validation.
See `./tests/scenarios.yaml` for trigger regression tests.

## Notes on Token Efficiency

**Phase execution time:**

- Phase 1 (extraction): ~5 min
- Phase 2 (dispatch/inline): ~5 min (immediate return)
- Phase 3 (team verification + plan): ~30-40 min

**Total workflow:** 40-50 min vs 1-1.5 hours sequential

## Troubleshooting

### Skill not triggering

**Symptom:** `/al-dev-map-suggestions-verify` command not recognized or fails to start.

**Verification:**

1. Confirm skill is registered in harness settings for `al-dev-shared`
2. Restart the harness session or reload settings
3. Verify skill file exists: `profile-al-dev-shared/skills/al-dev-map-suggestions-verify/SKILL.md`

**Solution:** Run `/sync-documentation-maps` to refresh skill registration, then retry.

### Extraction produces empty queue

**Symptom:** "No suggestions found in map Observations" — extraction exits with status 1.

**Root causes:**

- Map files have no Observations sections
- Observations sections are empty or malformed
- Filter is too restrictive (no suggestions match)

**Solution:**

1. Verify maps exist: `ls docs/al-dev-skills-map.md docs/al-dev-agent-map.md`
2. Check Observations are populated: `grep -A 5 "## Observations" docs/al-dev-*-map.md`
3. Try `--filter all` to remove filtering: `/al-dev-map-suggestions-verify --filter all`
4. If still empty, run `/analyze-skill-design` or `/analyze-agent-design` first to generate suggestions

### Team dispatch fails

**Symptom:** Background dispatch error during Phase 2, or "Failed to spawn duck team".

**Root causes:**

- Background-agent dispatch unavailable in this session
- `.dev/` directory not writable
- Team context JSON too large (>5MB)

**Solution:**

1. Verify `.dev/` writable: `touch .dev/test-write && rm .dev/test-write`
2. Check `.dev/progress.md` is created: `cat .dev/progress.md`
3. If background dispatch is unavailable, fall back to inline: manually run duck checks on 1-2 suggestions
4. For large batches, split into smaller runs: `/al-dev-map-suggestions-verify --surface skills --filter trim` then separate agent run

### Inline verification hangs

**Symptom:** Inline verification (1-2 suggestions) appears stuck or takes >5 minutes.

**Root causes:**

- Large file reads (artifact > 1MB)
- Grep timeout during reference checking (slow filesystem)
- Regex engine backtracking on complex patterns

**Solution:**

1. Check file sizes: `wc -l profile-al-dev-shared/skills/**/*.md | sort -n | tail -10`
2. Check disk health: `df -h` and `du -sh .dev/`
3. Increase timeout in validate-suggestions.py: change `timeout=15` to `timeout=30` in grep calls
4. If stuck, interrupt (Ctrl+C) and retry specific suggestion: `/al-dev-map-suggestions-verify --filter trim --surface skills`

### Resume can't find run

**Symptom:** "No active al-dev-map-suggestions-verify run found in .dev/progress.md" when running `--resume`.

**Root causes:**

- `.dev/progress.md` was deleted or overwritten
- Run completed and checkpoint was cleared
- Wrong directory (not at repo root)

**Solution:**

1. Verify working directory: `pwd` should show `al-dev-shared` at path end
2. Check if run completed: `ls .dev/al-dev-map-suggestions-verify-runs/` — if directory empty, run already completed
3. Look for orphaned runs: `find .dev -name 'manifest.json' | head -5`
4. Restart workflow: `/al-dev-map-suggestions-verify --surface both --filter all` to begin new run

### Duck records missing after collection

**Symptom:** "No duck records found in run directory" or "Manifest is empty" after team returns.

**Root causes:**

- Background agents failed silently (no duck-records/*.json files created)
- Run directory permissions restrict read access
- Team context JSON corrupted during dispatch

**Solution:**

1. Verify directory exists: `ls -la .dev/al-dev-map-suggestions-verify-runs/<run-id>/duck-records/`
2. Check manifest status: `cat .dev/al-dev-map-suggestions-verify-runs/<run-id>/manifest.json | grep -E 'status|suggestions'`
3. Check for failed suggestions: look for `"status": "failed"` in manifest
4. If all failed, check worker agent logs (if available) or re-dispatch with smaller batch

### Manifest timeout

**Symptom:** "Verification timed out" after 10 minutes of polling; team hasn't completed.

**Root causes:**

- Background team processing slower than expected (5-10 min verification per suggestion)
- Heavy local file I/O or many concurrent agents
- Background agent crash (no visible error message)

**Solution:**

1. Choose "Wait longer" option when prompted (adds 5 more minutes)
2. Check manifest status manually: `cat .dev/al-dev-map-suggestions-verify-runs/<run-id>/manifest.json`
3. If suggestions still pending after 20 minutes total, choose "Proceed with completed" and manually retry failed ones
4. For large batches (8+ suggestions), split into two runs to reduce team coordination overhead

### Plan generation failed

**Symptom:** "Failed to generate implementation plan" or "writing-plans skill invocation error" during Phase 3.

**Root causes:**

- `superpowers:writing-plans` not available or failed
- Duck record context format incompatible with writing-plans input schema
- Disk space exhausted when writing plan output

**Solution:**

1. Verify writing-plans skill exists: `/writing-plans --help` (test command)
2. Check duck records format: `cat .dev/al-dev-map-suggestions-verify-runs/<run-id>/duck-records/*.json | head -20`
3. Verify disk space: `df -h .dev`
4. Try manual plan generation: copy duck records context and invoke writing-plans separately
5. If writing-plans unavailable, ask user to review duck records manually and create plan document
