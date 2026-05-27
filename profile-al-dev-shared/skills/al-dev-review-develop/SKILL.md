---
name: al-dev-review-develop
description: >-
  Orchestrate multi-reviewer code review, compilation verification, and code-review
  output for implemented AL solutions. Consumes Phase 4 output from /al-dev-develop
  (completed developer work) and focuses exclusively on post-implementation quality gates
  and review synthesis.
argument-hint: ""
---

# Review-Develop Skill

Post-implementation review orchestration for /al-dev-develop Phase 5–10.

Dispatched by /al-dev-develop after Phase 4 (developer dispatch and implementation completion).

## Prerequisites

Phase 4 handoff artifact must exist:
`.dev/*-al-dev-develop-phase4-handoff.md` (or latest from /al-dev-develop Phase 4 output).

## Phase 5–10 Summary

- **Phase 5:** Prepare review entry + compile discipline
- **Phase 6–7:** Dispatch 3-specialist review panel (security, AL expert, performance) in parallel
- **Phase 8:** Compile verification (up to 5 fix cycles in autonomous mode)
- **Phase 8.5:** Pre-review staging
- **Phase 9:** Write code-review artifact
- **Phase 10:** Present review findings to user

## Review Panel

Three specialist agents (haiku):
- **al-dev-security-reviewer** — permission/auth/data exposure
- **al-dev-expert-reviewer** — AL conventions/BC patterns
- **al-dev-performance-reviewer** — N+1/SetLoadFields/efficiency

## Outputs

`.dev/$(date +%Y-%m-%d)-al-dev-develop-code-review.md` — Synthesized review findings from all three reviewers

## Implementation Notes

This skill contains the full implementation of Phases 5–10 from the parent /al-dev-develop skill. Copy verbatim from parent skill during refactoring, with these adaptations:

1. Adjust description to reflect post-implementation focus
2. Remove Phase 0–4 content entirely
3. Update prerequisites to reference Phase 4 handoff artifact
4. Keep compilation discipline, review panel, and code review write unchanged
5. Update input references to use Phase 4 handoff instead of full plan context
