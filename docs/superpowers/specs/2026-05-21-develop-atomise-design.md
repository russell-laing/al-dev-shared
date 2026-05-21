# Design Spec: Atomise /al-dev-develop

**Status:** Draft — run /plan-map-changes after approving this design to generate the implementation plan
**Date:** 2026-05-21
**Source:** docs/al-dev-plugin-map.md — Architectural suggestions > Atomise

---

## Problem Statement

/al-dev-develop spans ~14 phases with two separable concern groups. Splitting enables the review
pipeline to run independently (e.g., post-hoc code review, iterative review gates). The plugin map
suggests extracting "Phases 5–6" but rubber-ducking found the real extract is Phases 5–10 with
autonomous-mode phase 4.5 also moving to the review half.

## Phase Inventory and Split

| Phase | Name | Belongs to |
|-------|------|-----------|
| 0 | Check for Existing Progress | /al-dev-develop |
| 0.5 | Context Preservation Checkpoint | /al-dev-develop |
| 1 | Read Context | /al-dev-develop |
| 1.5 | Signature Verification (--autonomous only) | /al-dev-develop |
| 2 | Partition Work | /al-dev-develop |
| 3 | Spawn Developer Team | /al-dev-develop |
| 4 | Verify on Completion | /al-dev-develop |
| 4.5 | Static Validation (--autonomous only) | /al-dev-review-develop |
| 5 | Spawn Review Team | /al-dev-review-develop |
| 6 | Synthesise Review Findings | /al-dev-review-develop |
| 7 | Manage Review Iteration | /al-dev-review-develop |
| 8 | Compilation & Error Handling | /al-dev-review-develop |
| 9 | Validate and Write Code Review | /al-dev-review-develop |
| 10 | Present to User for Approval | /al-dev-review-develop |

## Handoff Contract

After Phase 4 completes, /al-dev-develop writes:
`.dev/$(date +%Y-%m-%d)-al-dev-develop-implementation-complete.md`

Content:

```markdown
# Implementation Complete — Handoff for Review

## Summary
- Developers spawned: [N]
- Files implemented: [list]
- Object IDs used: [ranges]

## Context
- Solution plan: [path from ls glob]
- Project context: .dev/project-context.md (if exists)
- Compilation: not yet run (review half runs compile in Phase 8)

## Autonomous (if --autonomous flag was used)
- Verified signatures: .dev/*-al-dev-autonomous-signatures.md
- Static validation: Phase 4.5 will run as first step of /al-dev-review-develop
```

/al-dev-review-develop starts by reading the latest handoff marker to establish context.

## Autonomous Mode Split

| Phase | --autonomous trigger | Location |
|-------|---------------------|----------|
| 1.5 | Signature Verification (--autonomous only) | /al-dev-develop |
| 4.5 | Static Validation (--autonomous only) | /al-dev-review-develop (first step) |

Both skills gate their autonomous phases on the `--autonomous` flag passed at invocation.
Users run `/al-dev-develop --autonomous` then `/al-dev-review-develop --autonomous`.

## Validator Relocation

`profile-al-dev-shared/skills/al-dev-develop/validate-code-review.py` is referenced in Phase 9.
When Phase 9 moves to /al-dev-review-develop:

1. Copy validator to `profile-al-dev-shared/skills/al-dev-review-develop/validate-code-review.py`
2. Update the VALIDATOR path in Phase 9 to use the new skill directory
3. Keep original in `skills/al-dev-develop/` for now (remove in a follow-up once stable)

## New Skill Interfaces

`/al-dev-develop [--autonomous] [scope]`
- Phases 0–4 only
- Final phase 4 message: "Implementation complete → run /al-dev-review-develop to run review pipeline."

`/al-dev-review-develop [--autonomous]`
- Reads latest `*-al-dev-develop-implementation-complete.md`
- Phases 4.5 (if --autonomous) through 10
- Produces code-review.md as today

## Files to Change (when this design is approved)

- Modify `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` — truncate at Phase 4, add handoff write
- Create `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md` — Phases 4.5–10
- Create `profile-al-dev-shared/skills/al-dev-review-develop/validate-code-review.py` — copy from al-dev-develop
- Update `docs/al-dev-plugin-map.md` — add /al-dev-review-develop in Layer 1 and Layer 2

## Risk: User Workflow Change

Current: `/al-dev-develop` is a complete end-to-end command.
After: users run two commands sequentially.

Mitigation: Phase 4 final message must explicitly name the next command. Consider adding a
`/al-dev-review-develop` shortcut that checks for an unreviewed handoff marker and auto-invokes.
