# Plugin-Health Parallelization Guide

> **Status: Aspirational design document.** The `/plugin-health` command described here
> does not exist as an active skill. The current implementation uses three separate skills:
> `/plugin-health-audit` (full synchronous sweep), `/plugin-health-discover` (lenses only),
> and `/plugin-health-report` (ranking only). This document records the intended
> async/resumable architecture for reference if those skills are later unified.

## What Changed

**Before:** `/plugin-health` consumed 5+ hours of session tokens, blocking other work.

**After:** Dispatch phase (~45 min) spawns a remote team that executes lenses in parallel while you work. Collection phase (~20 min) fetches results when ready.

## User Workflow

### Normal Case (No Session Interruption)

```bash
# Session 1: Dispatch
/plugin-health --surface both --dimension all

# Output: "Dispatched team <id>. Re-run /plugin-health --resume when ready."
# You are now free to do other work for ~5-15 minutes while lenses execute

# Session 1: Collect (when ready, typically 10-20 minutes later)
/plugin-health --resume

# Output: Findings file and dossier written to docs/health/
```

### Resume Case (Session Ended Before Collection)

```bash
# Session 1: Dispatch
/plugin-health --surface both --dimension all

# Session 1 ends (or you switch contexts)

# Session 2 (later): Resume collection
/plugin-health --resume

# Output: Collects results from prior dispatch and writes files
```

### Partial Results (Some Lenses Timed Out)

```bash
# Session 1: Dispatch
/plugin-health --surface both --dimension all

# Session 1: Collection (at time X)
/plugin-health --resume
# Output: "PARTIAL — 18 of 20 lenses completed. Run /plugin-health --resume to finish."

# Session 2 (when ready): Complete remaining lenses
/plugin-health --resume
# Output: "Dispatching remaining 2 lenses..."
# (Dispatch phase runs again with only pending lenses)

# Session 2 (later): Collect final results
/plugin-health --resume
# Output: All 20 lenses complete, dossier written
```

## Architecture (For Developers)

### Dispatch Phase

1. Parse arguments (`--surface`, `--dimension`, `--resume`)
2. Build file lists for agents and skills
3. Aggregate context (tool inventory, model assignments, etc.)
4. Determine which lenses to run
5. Build work queue JSON
6. Write to `.dev/plugin-health-runs/<run-id>/`
7. Save checkpoint to `.dev/plugin-health-team-checkpoint.json`
8. Spawn remote agent team with work queue
9. Return immediately

**Token cost:** ~45 min

### Async Execution (Remote)

Runs outside main session in parallel batches:

1. Receive work queue
2. Spawn 4-6 lenses per batch
3. Each lens analyzes files independently
4. Write findings to `.dev/plugin-health-runs/<run-id>/lens-results/<lens_name>.json`
5. Update manifest with progress
6. On completion or timeout, mark status

**Wall-clock time:** 5-15 min (running in background)

### Collection Phase

1. Read checkpoint to locate prior run
2. Read manifest to see which lenses completed
3. Aggregate all lens findings from `.dev/plugin-health-runs/`
4. Write findings markdown file to `docs/health/YYYY-MM-DD-<surface>-findings.md`
5. Write dossier with ranked suggestions to `docs/health/YYYY-MM-DD-<surface>-health.md`
6. Update checkpoint with "collected" status

**Token cost:** ~20 min

### Durable Artifacts

All artifacts under `.dev/plugin-health-runs/` persist across session boundaries:

```text
.dev/plugin-health-runs/
  <run-id>/
    work-queue.json              # Input to remote team
    manifest.json                # Progress tracking (updated by team)
    lens-results/
      design-agent-lens-tool-hygiene.json
      design-agent-lens-model-fit.json
      ...                        # One file per lens (success or failure)
.dev/plugin-health-team-checkpoint.json  # Checkpoint for resume
```

## Recovery Procedures

### "No resumable run found" Error

**Cause:** No checkpoint exists (first time, or old checkpoint was cleared)

**Fix:** Start new dispatch with `/plugin-health --surface X --dimension Y`

### "Collection failed: Manifest not found"

**Cause:** Run directory was deleted or moved

**Fix:** Manually find the run ID in prior checkpoint or check `.dev/plugin-health-runs/` directory. If artifacts are lost, start a new dispatch.

### "Partial completion after timeout"

**Cause:** Remote team hit 30-minute hard timeout; some lenses didn't complete

**Status:** Dossier reports "PARTIAL — X of Y lenses completed"

**Fix:** Run `/plugin-health --resume` to dispatch remaining lenses and merge results

### Manual Inspection

To check dispatch/collection state at any time:

```bash
# View active checkpoint
cat .dev/plugin-health-team-checkpoint.json

# View lens progress
cat .dev/plugin-health-runs/<run-id>/manifest.json

# View a specific lens result
cat .dev/plugin-health-runs/<run-id>/lens-results/<lens_name>.json

# View findings and dossier
cat docs/health/YYYY-MM-DD-<surface>-findings.md
cat docs/health/YYYY-MM-DD-<surface>-health.md
```

## Performance Metrics

### Token Savings

| Phase | Old System | New System |
|-------|-----------|-----------|
| Dispatch | 0 (inline) | ~45 min |
| Lens execution | ~4-5 hours | ~5-15 min (remote) |
| Collection | 0 (inline) | ~20 min |
| **Total tokens** | **5+ hours** | **~1 hour** |
| **Savings** | — | **80-90%** |

### Wall-Clock Time

| Metric | Old | New |
|--------|-----|-----|
| User waits for results | 5+ hours | ~45 min + async |
| Time to be freed | N/A (locked) | 45 minutes |
| Time to resume work | N/A | Immediately after dispatch |

## Testing

New system produces identical findings to old system:

```bash
# Verify: findings blocks are identical (modulo timestamps)
diff <(old-system findings) <(new-system findings)
# Expected: minimal diff (timestamps only)
```

## Troubleshooting

### Lenses fail with "Agent not found"

Check that all lens agent definitions exist in `profile-al-dev-shared/agents/`. Remote team cannot spawn lenses without agent definitions.

### Work queue is empty

**Cause:** File discovery found no agents or skills

**Fix:** Verify agents and skills exist in expected directories:

- `profile-al-dev-shared/agents/*.md`
- `profile-al-dev-shared/skills/*/SKILL.md`
- `.claude/agents/*.md`
- `.claude/skills/*/SKILL.md`

### Findings are empty or truncated

**Cause:** Lens agent returned malformed findings_block

**Fix:** Check manifest for lens status. If "failed", error message is included. If "success" with empty findings, lens agent may need debugging.
