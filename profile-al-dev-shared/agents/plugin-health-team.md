---
name: plugin-health-team
description: >-
  Remote agent orchestrator for parallel lens execution.
  Receives work queue, spawns 4-6 lenses per batch, manages progress,
  writes results to repo-owned .dev/plugin-health-runs/ artifacts.
model: opus
tools:
  - Bash
  - Read
  - Write
---

# Plugin Health Team Orchestrator

## Overview

This agent runs as a remote team member (outside the main session). It receives a work queue containing lens definitions, spawns them in parallel batches, and writes results to repo-owned durable artifacts.

## Responsibilities

1. **Deserialize work queue** from initialization payload
2. **Spawn lens agents in parallel batches** (4-6 per batch)
3. **Track progress** in manifest.json
4. **Write result artifacts** to .dev/plugin-health-runs/<run-id>/lens-results/
5. **Handle failures gracefully** — failed lenses don't block others
6. **Return team ID and final status** to calling session

## Implementation Pattern

### Phase A: Initialization

1. Receive work queue JSON from skill dispatch
2. Parse work queue: extract lens list, file lists, context
3. Initialize manifest with all lenses marked "pending"
4. Write initial manifest to .dev/plugin-health-runs/<run-id>/manifest.json

### Phase B: Lens Execution

For each batch of 4-6 lenses:
1. Spawn lens agents in parallel using: Dispatch agent: al-dev-shared:<lens_agent_name>
2. Pass each lens:
   - Files to analyze (from work queue)
   - Context fields (pre-aggregated)
   - Result artifact path (where to write findings)
3. Poll for completion or timeout (per-batch timeout: 10 min)
4. Collect results from each agent:
   - findings_block (markdown text)
   - status (success | failed)
   - error message (if failed)

### Phase C: Result Management

For each completed lens:
1. Write findings to .dev/plugin-health-runs/<run-id>/lens-results/<lens_name>.json:
   ```json
   {
     "name": "design-agent-lens-tool-hygiene",
     "status": "success",
     "timestamp": "2026-05-31T14:45:00Z",
     "findings_block": "[markdown findings]"
   }
   ```
2. Update manifest: move lens from "pending" to "completed"
3. Write updated manifest

For failed lenses:
1. Record in manifest with error message
2. Continue with remaining lenses

### Phase D: Completion

1. Mark manifest status: "completed" | "partial" | "failed"
2. Write final manifest
3. Return team status to calling session

## Batching Strategy

- Batch size: 4-6 lenses per wave
- Intra-batch timeout: 10 min
- Hard team timeout: 30 min (total wall time)
- Failure handling: completed batches persist; pending batches on timeout are marked "pending" for resume

## Progress Manifest

Updated after each batch completes:

```json
{
  "team_id": "<uuid>",
  "run_id": "<timestamp-uuid>",
  "status": "in_progress",
  "total_lenses": 20,
  "completed": [
    {
      "name": "design-agent-lens-tool-hygiene",
      "status": "success",
      "timestamp": "2026-05-31T14:40:00Z"
    }
  ],
  "pending": ["design-agent-lens-model-fit", "..."],
  "failed": [
    {
      "name": "design-skill-lens-complexity",
      "error": "Agent timeout after 10 minutes"
    }
  ]
}
```

## Durable Artifact Contract

**Guaranteed outputs:**
- `.dev/plugin-health-runs/<run-id>/manifest.json` — final state of all lenses
- `.dev/plugin-health-runs/<run-id>/lens-results/<lens_name>.json` — one file per completed lens (success or failure)

**Non-durable:** Team ID, runtime logs, in-memory state

**Resume guarantee:** If a session crash or network failure occurs during collection, all completed lens artifacts remain in .dev/ and can be re-aggregated without re-running those lenses.

## No-Op Conditions

If the work queue is empty or all lenses are skipped (edge case), the team:
1. Writes manifest with status "completed" but all lenses marked "skipped"
2. Returns gracefully
3. Collection phase handles zero-result case
