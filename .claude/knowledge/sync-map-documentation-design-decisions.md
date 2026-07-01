# Design Decisions: Async Dispatch in sync-map-documentation

## Overview

This document records the design rationale for splitting the documentation map sync workflow into four independent phases, each with checkpoint isolation.

## Decision: Four-Phase Checkpoint Isolation

**Split boundary:** Audit phase isolated, compare isolated, update isolated, regen isolated.

**Rationale:**

- Each stage can be re-run independently if prior stages succeed.
- Failures in early stages (e.g., audit) do not require re-running later stages (e.g., write).
- Checkpoints provide resume capability for long-running workflows.
- Skill surface area remains testable in isolation.

## Related Skills

- `/sync-map-documentation` — dispatcher, writes initial checkpoint
- `/sync-map-documentation-collect` — collects audit results, spawns update agents
- `/sync-map-documentation-apply` — applies updates to maps
- `/sync-map-documentation-write` — regenerates diagrams and commits

See `./sync-map-update-shared.md` for shared procedure documentation.
