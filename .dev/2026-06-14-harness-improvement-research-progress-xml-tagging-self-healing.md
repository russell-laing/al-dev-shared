# Harness Improvement Research Progress

## Scope

- Research question: assess whether XML tagging should be added to the self-healing tooling in `al-dev-shared` to improve prompt and handoff structure.
- In scope: repo-local self-healing tooling, especially prompt boundaries, loop-state handoffs, checkpoint semantics, and machine-readable orchestration cues.
- Compared ecosystems: current `al-dev-shared` repo-local contracts versus current first-party LLM prompting guidance.
- Recency window: current vendor documentation accessed on 2026-06-14.
- Exclusions: shared-profile projection edits, broad harness audits, and non-self-healing maintainer tooling.

## Completed Phases

- Phase 1: live baseline established.
- Phase 2: external source plan completed.
- Phase 3: evidence gathered.
- Phase 4: repository comparison completed.
- Phase 5: briefing written.

## Current State

Research is complete. The live repo already contains explicit structure for
self-healing orchestration: `.dev/health-loop-state.md` has a documented YAML
schema, `.dev/progress.md` is an authoritative resume checkpoint, and `.claude`
workflow metadata uses a documented frontmatter schema. The final briefing
concludes that XML tags are useful as prompt delimiters but are not the best
primary improvement for current self-healing correctness.

## Next Step

No further research action pending. Recommended downstream action: none.

## Temp And Baseline Paths

- `HARNESS_RESEARCH_TMP`: `/var/folders/v7/j_7c4s7558qgrrm4grpz4b4c0000gn/T/harness-research.eOmYA0`
- baseline: `/var/folders/v7/j_7c4s7558qgrrm4grpz4b4c0000gn/T/harness-research.eOmYA0/protected-before.txt`
- baseline: `/var/folders/v7/j_7c4s7558qgrrm4grpz4b4c0000gn/T/harness-research.eOmYA0/index-before.txt`
- baseline: `/var/folders/v7/j_7c4s7558qgrrm4grpz4b4c0000gn/T/harness-research.eOmYA0/status-before.txt`

## Open Questions

- None.
