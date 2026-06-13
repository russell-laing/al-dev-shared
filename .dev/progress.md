research_question: Improve `.claude` self-healing loop correctness for orchestration, resume, handoff, and close-back behavior using current external harness evidence.
scope: `.claude` self-healing loop only; focus on loop-state, resume semantics, stale-state handling, compaction/handoff boundaries, and close-back invariants. Exclude lens redesign, broad plugin-health quality audits, and shared-profile edits.
completed_phases:
  - "Phase 1: live baseline established"
  - "Phase 2: external source plan completed"
  - "Phase 3: evidence gathered"
  - "Phase 4: repository comparison completed"
  - "Phase 5: briefing written and validated"
current_state: "Research complete. Briefing written and protected-surface before/after manifests match exactly."
next_step: "No further research action pending in this checkpoint. Recommended downstream action: run `review-improvement-reports` on `.dev/2026-06-13-harness-improvement-research-claude-self-healing-loop.md`."
HARNESS_RESEARCH_TMP: "/var/folders/v7/j_7c4s7558qgrrm4grpz4b4c0000gn/T/harness-research.Nl0gKf"
baseline_snapshot_paths:
  - "/var/folders/v7/j_7c4s7558qgrrm4grpz4b4c0000gn/T/harness-research.Nl0gKf/protected-before.txt"
  - "/var/folders/v7/j_7c4s7558qgrrm4grpz4b4c0000gn/T/harness-research.Nl0gKf/index-before.txt"
  - "/var/folders/v7/j_7c4s7558qgrrm4grpz4b4c0000gn/T/harness-research.Nl0gKf/status-before.txt"
open_questions:
  - "Whether any candidate pattern belongs in shared knowledge rather than remaining `.claude`-local."
