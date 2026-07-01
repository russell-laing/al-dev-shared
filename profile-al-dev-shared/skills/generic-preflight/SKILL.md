---
name: generic-preflight
description: >-
  Parameterized preflight context gathering. Accepts a `context-type` argument
  (plan | review) and writes the corresponding context artifact.
argument-hint: "[--context-type plan|review]"
---

# Generic Preflight

Parameterized context gathering for multi-context workflows. Invoked by skills that need standardized resume-checking and artifact writing without duplication.

## Supported context types

- **plan** → writes `.dev/plan-context.md`
- **review** → writes `.dev/review-context.md`

## Phase 0: Resume check

Check `.dev/progress.md` for prior incomplete work:

- If exists: offer resume or restart options
- If absent: proceed to Phase 1

## Phase 1: Gather context

Based on `context-type`:

- **plan**: Read the latest plan artifact and prepare edit context
- **review**: Read the latest code changes and prepare review context

Write appropriate context file.

## Phase 2: Report

Return the context artifact path to the calling skill.
