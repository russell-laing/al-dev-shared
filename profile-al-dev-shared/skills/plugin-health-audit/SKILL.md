---
name: plugin-health-audit
description: >-
  Suggestions-only health sweep of the al-dev-shared plugin surfaces (skills and agents).
  Generates findings and recommendations but never auto-fixes source files.
  Dispatches design and quality lenses, ranks findings, and writes dossiers to docs/health/.
  Parallelized via agent teams: dispatch phase spawns remote lenses, collection phase
  fetches results via --resume flag.
argument-hint: "[--surface plugin|tooling|both] [--dimension design|quality|all] [--resume]"
---

# Skill: /plugin-health-audit

Run a parallelized suggestions-only health sweep of the al-dev-shared plugin surfaces. The sweep
dispatches remote agent teams to analyze skills and agents against design and quality lenses,
collects results, and writes ranked findings to docs/health/. Supports resume workflow to collect
results in a separate session after dispatch. Never auto-edits source files.

## Overview: Dispatch-and-Resume Workflow

**Entry 1: Initial dispatch** (`/plugin-health-audit` or `/plugin-health-audit --surface agents --dimension design`)

- Phase 1: Parse arguments, build file lists and work queue, spawn remote agent team
- Returns immediately; user freed to work while team analyzes in background
- Writes checkpoint to `.dev/plugin-health-team-checkpoint.json`

**Entry 2: Resume collection** (`/plugin-health-audit --resume`)

- Phase 3: Fetch results from repo artifacts, aggregate findings, rank by severity, write dossiers
- Continues from the dispatch checkpoint created in Entry 1
- Writes final dossier to docs/health/

**Success metric:** Initial dispatch completes in ~10-15 min; remote team runs async;
collection (Phase 3) completes in ~10-15 min. Total session token cost: ~40-50 min
over two sessions vs. 5+ hours in single-session monolithic approach.

**Token-limit resilience:** If a remote sweep is truncated (lenses show `"pending"`
in the checkpoint), run `/plugin-health-audit --resume` to collect whatever completed.
For very large surfaces that repeatedly hit token limits, run separate sweeps:
`/plugin-health-audit --surface plugin` then `/plugin-health-audit --surface tooling`
— this halves the lens count per dispatch.

## Reference Documents

- `../../knowledge/plugin-health-lenses.md` — Lens definitions and scoring
- `./dispatch.py` — Phase 1 work queue building and checkpoint management
- `./collect.py` — Phase 3 result aggregation and dossier generation
- `./schemas.py` — Checkpoint and work queue data structures

## Phase 1: Dispatch (Lightweight, In-Session)

### Step 1: Detect resume flag

Resume mode allows collection to happen in a new session after dispatch completes:

```python
resume = "--resume" in arguments
if resume:
    # Skip to Phase 3 (collection)
    from dispatch import dispatch_work
    success, message = dispatch_work(surface, dimension, resume=True)
    if success:
        print(message)
    else:
        print(f"Error: {message}")
    return
```

### Step 2: Parse arguments

Validate surface and dimension arguments:

```python
from dispatch import validate_arguments
surface = arguments.get("--surface", "both")
dimension = arguments.get("--dimension", "all")

valid, error = validate_arguments(surface, dimension)
if not valid:
    print(f"Argument error: {error}")
    return
```

### Step 3: Build file lists and work queue

Delegate to dispatch.py to build work queues and spawn the remote team:

```python
from dispatch import dispatch_work
success, message = dispatch_work(surface, dimension, resume=False)
print(message)
if not success:
    print(f"Dispatch failed: {message}")
```

The skill now delegates to dispatch.py for all orchestration logic.

## Phase 3: Collection & Reporting (Resume Path)

### Step 1: Load checkpoint

Resume mode allows collection to happen in a new session after dispatch completes:

```python
from dispatch import load_checkpoint
from pathlib import Path

checkpoint_path = Path("/Users/russelllaing/al-dev-shared/.dev/plugin-health-team-checkpoint.json")
checkpoint = load_checkpoint(str(checkpoint_path))

if checkpoint is None:
    print("Error: No resumable plugin-health-audit run found. Start a new sweep with /plugin-health-audit.")
    return

print(f"Resuming team {checkpoint.team_id}: run_id={checkpoint.run_id}")
```

### Step 2: Poll for remote team completion (optional)

If implementation chooses to poll:

```python
# Poll remote team status or check manifest directly
manifest_path = checkpoint.manifest_path
manifest = json.load(open(manifest_path))

if manifest['status'] == 'in_progress':
    print("Remote team still executing. Check back in a few minutes.")
    print("Run /plugin-health-audit --resume again to collect when ready.")
    return
```

### Step 3: Aggregate findings and write output files

```python
from collect import collect_results

success = collect_results(checkpoint)
if success:
    print(f"Findings written to {checkpoint.findings_file}")
    print(f"Dossier written to {checkpoint.dossier_file}")
    
    if checkpoint.status == "partial":
        print("\nNote: Some lenses remain pending. Run /plugin-health-audit --resume to complete.")
    else:
        print("\nNext step: Use /superpowers:writing-plans to implement top recommendations.")
else:
    print("Error: Collection failed. Check logs above.")
```

This adds the full collection path that runs when user calls `/plugin-health-audit --resume`.
