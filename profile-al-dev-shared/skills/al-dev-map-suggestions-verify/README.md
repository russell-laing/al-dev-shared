# al-dev-map-suggestions-verify User Guide

Verify architectural change suggestions from documentation maps using parallel
remote agent teams. Reduces session token burn from 1-1.5 hours to 40-50 minutes
through async verification and checkpoint/resume workflow.

## Quick Start

Initialize a verification run against both skill and agent map Observations:

```bash
/al-dev-map-suggestions-verify
```text

Expected output:

```text
Extracted 5 suggestions from map Observations
  - 2 trim suggestions (unused artifacts)
  - 1 merge suggestion (overlapping skills)
  - 1 split suggestion (artifact > 250 lines)
  - 1 align suggestion (contract mismatch)

For 1-2 suggestions: inline verification (immediate, ~3 min)
For 3+ suggestions: remote team dispatch (return now, verify later)

Dispatched 5 suggestions to verification team.
Run `/al-dev-map-suggestions-verify --resume` when ready to collect results.
```text

## Resume & Collect Results

After team completes verification (5-10 min), collect results and generate plan:

```bash
/al-dev-map-suggestions-verify --resume
```text

The skill reads `.dev/progress.md` checkpoint, polls team completion, aggregates
duck records, and invokes `superpowers:writing-plans` to generate the
implementation plan.

Expected behavior:

- Waits up to 10 minutes for team completion
- Displays verdict summary: ACCEPT (approved), DEFER (needs review),
  REJECT (not recommended)
- Generates `YYYY-MM-DD-al-dev-plan-map-plan.md` with step-by-step implementation
  guidance

## Command Reference

### `/al-dev-map-suggestions-verify`

Initialize extraction and dispatch phases.

**Flags:**

- `--surface {skills|agents|both}` — Which maps to audit (default: `both`)
- `--filter {all|trim|merge|split|inline|align|connect|promote}` — Filter
  (default: `all`)

**Examples:**

```bash
# Verify all suggestions from both maps
/al-dev-map-suggestions-verify

# Verify only skill-related trim suggestions
/al-dev-map-suggestions-verify --surface skills --filter trim

# Verify agent-related split and merge suggestions
/al-dev-map-suggestions-verify --surface agents --filter split,merge
```text

### `/al-dev-map-suggestions-verify --resume`

Resume from checkpoint and collect verification results.

**When to use:**

- After initial `/al-dev-map-suggestions-verify` dispatch returns
- When remote team verification completes (5-10 minutes later)
- If Phase 3 times out, can re-run to poll longer

**Flags:**

None; uses `.dev/progress.md` checkpoint to locate active run.

## How It Works

### Phase 1: Extract Suggestions (1-2 min)

Parses `docs/al-dev-skills-map.md` and `docs/al-dev-agent-map.md` Observations
sections. Builds suggestion queue with:

- Suggestion ID (unique identifier)
- Suggestion type (trim/merge/split/inline/align/connect/promote)
- Target files (artifacts to verify)
- Proposed changes (description)

### Phase 2: Dispatch or Inline Verify (~5 min)

**Path A (1-2 suggestions):** Inline verification

Synchronously verifies each suggestion:

1. Check file accessibility (U1 check)
2. Verify artifacts unchanged (U2 check)
3. Validate references (U3 check)
4. Run type-specific checks (trim-specific, merge-specific, etc.)
5. Write duck record (success or error)

**Path B (3+ suggestions):** Background team dispatch

Dispatches a parallel background agent team (one agent per suggestion), per the
pattern in `../../knowledge/background-agent-dispatch.md`. Each agent
independently:

1. Reads target files from repo
2. Runs all universal and type-specific checks
3. Writes duck record to shared directory
4. Updates manifest status

Returns immediately; user can continue working while team verifies in background.

### Phase 3: Collect & Plan Generation (30-40 min)

Invoked via `--resume` flag:

1. Reads checkpoint from `.dev/progress.md`
2. Polls manifest for team completion (10-minute timeout)
3. Reads all duck records from run directory
4. Aggregates by verdict: ACCEPT / DEFER / REJECT
5. Invokes `superpowers:writing-plans` with duck evidence
6. Generates step-by-step implementation plan

## Artifact Locations

### Input Files

- `docs/al-dev-skills-map.md` — Skill inventory with Observations section
- `docs/al-dev-agent-map.md` — Agent inventory with Observations section

### Checkpoint & State

- `.dev/progress.md` — Active run state (run_id, manifest path, phase, status)

### Run Artifacts

- `.dev/al-dev-map-suggestions-verify-runs/<run-id>/suggestion-queue.json` — Extracted
  suggestions list
- `.dev/al-dev-map-suggestions-verify-runs/<run-id>/manifest.json` — Status tracking across
  verification
- `.dev/al-dev-map-suggestions-verify-runs/<run-id>/duck-records/*.json` — Individual duck
  verification records

### Generated Output

- `.dev/YYYY-MM-DD-al-dev-plan-map-plan.md` — Implementation plan (generated
  by writing-plans)

## Success Criteria

A successful run demonstrates:

1. **Extraction succeeds** — Suggestions extracted from map Observations
2. **Verification completes** — All suggestions verified (or partial if timeout)
3. **Verdicts assigned** — Each duck record has verdict: ACCEPT / DEFER / REJECT
4. **Plan generated** — Implementation plan created with concrete action items
5. **No harness leaks** — Plan uses generic vocabulary (no harness-specific terms)

Example success summary output:

```text
Verification Results:
  ACCEPT: 3    (approved for implementation)
  DEFER:  1    (requires architect review)
  REJECT: 1    (not recommended)

Generated plan: .dev/2026-05-31-al-dev-plan-map-plan.md
Next step: Review plan and begin implementation
```text
