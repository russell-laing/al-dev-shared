---
name: generic-preflight
description: >-
  Parameterized preflight skill for plan and review phases. Handles resume
  logic, context gathering, and state checkpointing for both /plan and
  /review-develop flows via context-type argument.
argument-hint: "[context-type: planning|review]"
---

# Generic Preflight Skill

Shared Phase 0 resume-check + context-gathering logic for the planning and
review preflight flows — invoked as `/generic-preflight --context-type planning`
or `/generic-preflight --context-type review`. Reduces duplication by
parameterizing the context type.

## Phase 0: Resume Check & Initialization

Check `.dev/<context-type>-preflight-checkpoint.md` for resume capability.

If exists, read checkpoint and present resume option:

```text
Resume previous work on [context]? Run:
  /generic-preflight --resume --context-type <type>

```

If not exists, proceed to Phase 1 (context gathering).

## Phase 1: Gather Planning Context (context-type: planning)

For `context-type: planning`, collect:

1. Spec file (if exists in `.dev/spec-*.md`)
2. Prior plan artifacts (if any)
3. Current branch state (`git log`, `git diff`)
4. Test status (if applicable)

Write to `.dev/planning-preflight-context.md`.

## Phase 2: Gather Review Context (context-type: review)

For `context-type: review`, collect:

1. Current branch state (`git log`, `git diff`)
2. Test results (run test suite if applicable)
3. Linter status (if applicable)
4. Code review checkpoint (prior findings if any)

Write to `.dev/review-preflight-context.md`.

## Phase 3: Emit Preflight Checkpoint

Write `.dev/<context-type>-preflight-checkpoint.md` with:

- Timestamp
- Context file path
- Ready/blocked status
- Next command (downstream skill to invoke)

## Implementation Notes

This skill is invoked by:

- `/plan` (context-type: planning)
- `/review-develop` (context-type: review)

Each caller receives the context in their expected output file. The skill handles
both paths via the `context-type` argument.
