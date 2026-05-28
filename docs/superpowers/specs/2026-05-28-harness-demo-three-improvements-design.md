# Design: Two Durable Improvements from Harness Engineering Demo

**Date:** 2026-05-28
**Goal:** Adapt the strongest reusable planning patterns from `coleam00/harness-engineering-demo`
to strengthen `profile-al-dev-shared`
**Scope:** Solution plan pattern references, constrained acceptance criteria, deferred invocation
safety follow-up
**Effort:** ~60 minutes total
**Source inspiration:** https://github.com/coleam00/harness-engineering-demo

---

## Background

Review of `coleam00/harness-engineering-demo` surfaced three useful ideas:

1. A frontmatter gate to prevent accidental auto-trigger of side-effect skills
2. A pattern-reference field in implementation planning
3. Acceptance criteria written as verifiable conditions rather than prose

Only the latter two are ready to adopt directly in `profile-al-dev-shared`. The invocation-safety
idea addresses a real risk, but the demo's mechanism is harness-specific and does not currently
fit this repo's shared authored surface without a separate boundary-aware mechanism design.

This design therefore keeps the two durable planning improvements and defers the invocation-safety
mechanism to a follow-up spec.

---

## Existing Coverage Reviewed

- `docs/superpowers/plans/2026-05-28-artifact-contract-validator-and-skill-template.md` — adds
  a structural validator and skill scaffold template. Does not address plan content quality.
- `docs/superpowers/plans/2026-05-28-shared-artifact-contracts-and-gates.md` — adds artifact
  contract matrix and final-gate wording. Does not constrain plan-level acceptance-criteria
  format.
- `docs/superpowers/plans/2026-05-28-profile-al-dev-shared-hybrid-improvements.md` — adds
  compile gate to `al-dev-commit`, investigation tightening, intent-preflight. Does not add
  pattern anchors inside solution plans.
- `docs/superpowers/plans/2026-05-28-harness-coverage-model.md` — coverage table only; does not
  change runtime behaviour.

---

## Problem Statement

Two active planning gaps remain after today's work, plus one deferred safety concern:

1. **Solution plans lack a concrete pattern anchor.** When the solution architect writes an
   implementation task, it describes what to build but does not point the developer agent at the
   best existing analogue to mirror. Developer agents must infer patterns from scratch, which
   increases variance.

2. **Acceptance criteria are not constrained enough to review or partially gate.** The current
   solution plan template does not define an Acceptance Criteria section with a limited, checkable
   structure. This makes self-verification and commit-gate review inconsistent.

3. **Accidental auto-trigger risk remains a real concern, but its mechanism is deferred.** Shared
   authored skills should remain harness-neutral unless the repo defines and validates an explicit
   exception. That mechanism is not part of this design.

---

## Deferred Follow-Up: Invocation Safety Mechanism

The auto-trigger concern is valid, especially for skills that dispatch developers, modify git
state, or write durable outputs. However, this design does **not** add a harness-specific
frontmatter field such as `disable-model-invocation` to shared skill files.

Any future invocation-safety mechanism must first answer:

- Where the control lives without weakening shared/harness boundaries
- Which runtime or projection layer enforces it
- How the behavior is validated in this repo rather than assumed from an external demo

This follow-up should be designed separately from the plan-quality changes below.

---

## Change A: Pattern Reference per Object in Solution Plans

### Problem

The solution plan's Object Design section names objects and describes their purpose but does not
tell the developer agent what existing code pattern is the best analogue to follow.

### Addition to `knowledge/solution-plan-template.md`

Each object entry in the Object Design section gains a required `Pattern reference:` line:

```markdown
**Codeunits:**
- Object ID 52xxx: "SalesPostingGuard"
  Purpose: Validate posting date on sales order release
  Key Methods: `ValidatePostingDate(SalesHeader: Record "Sales Header")`
  Pattern reference: `src/Codeunit/CustomerCreditCheck.Codeunit.al:L45` — best analogue for
    validation-on-release flow (subscriber + guard codeunit split)
```

When no analogue exists:

```markdown
  Pattern reference: none — establishing new posting-guard pattern
```

The `none` declaration is explicit, not optional. It prevents silent omission from passing
unnoticed during review.

### Addition to `agents/al-dev-solution-architect.md`

The Research phase gains an explicit sub-step:

> For each object in the Object Design, locate the best existing analogue in the project using
> the strongest available evidence source: `AL LSP` when exposed by the active harness or adapter,
> otherwise `AL MCP`, otherwise scoped `text search`. Record the file path and line number as the
> `Pattern reference`. If no useful analogue exists, record `none` with a one-line rationale.

This change does not require exact proof of an identical structural pattern. It requires the
strongest available evidence for the best analogue the developer should inspect first.

### Files Changed

- `profile-al-dev-shared/knowledge/solution-plan-template.md`
- `profile-al-dev-shared/agents/al-dev-solution-architect.md`

---

## Change B: Constrained Acceptance Criteria

### Problem

The current solution plan template does not define an Acceptance Criteria section with a limited
format. Prose criteria such as "validation works correctly" are difficult to review consistently
and only partially usable by the existing `al-dev-commit` gate.

### Addition to `knowledge/solution-plan-template.md`

Add a new `Acceptance Criteria` section to the solution plan template. Each criterion must be
numbered and use one of four forms:

**Structural check** — file or symbol existence:

```text
1. `src/Codeunit/SalesPostingGuard.Codeunit.al` exists and contains `procedure ValidatePostingDate`
2. `src/PageExtension/SalesOrderExt.PageExt.al` contains `SalesPostingGuard.ValidatePostingDate`
```

**Gate check** — tool exit code or existing skill gate:

```text
3. `al-compile` exits 0 with no new errors in `.dev/compile-errors.log`
```

**Pattern check** — a required or forbidden pattern in changed code:

```text
4. No `Error(StrSubstNo(` appears in new or modified files
```

**Manual check** — user or tester validation that cannot be machine-checked yet:

```text
5. [manual] Posting is blocked when order date is before work date
```

Unlabelled prose criteria are not permitted.

### Addition to `agents/al-dev-solution-architect.md`

The Write output step gains:

> Add a numbered `Acceptance Criteria` section to the solution plan. Each criterion must use one
> of the allowed forms: structural, gate, pattern, or `[manual]`. Do not write free-form prose
> criteria.

### Addition to `skills/al-dev-commit/SKILL.md`

The pre-commit checklist step gains a bounded cross-reference:

> Read the acceptance criteria from the solution plan when one exists. Verify directly checkable
> structural, gate, and pattern criteria before proceeding. Surface any `[manual]` criteria as
> pending manual validation; do not treat them as automatic blockers.

This is intentionally narrower than full programmatic enforcement. It improves review and partial
gating now without claiming a dedicated validator contract that does not yet exist.

### Files Changed

- `profile-al-dev-shared/knowledge/solution-plan-template.md`
- `profile-al-dev-shared/agents/al-dev-solution-architect.md`
- `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`

---

## Combined Scope Summary

| Change | Files touched | Risk |
|---|---|---|
| A — Pattern reference | `solution-plan-template.md` + `al-dev-solution-architect.md` | Low — additive planning guidance |
| B — Constrained acceptance criteria | `solution-plan-template.md` + `al-dev-solution-architect.md` + `al-dev-commit/SKILL.md` | Low — additive format + bounded gate wording |
| Deferred follow-up — invocation safety | No shared-surface runtime changes in this spec | None in this spec |

**Note:** Change A and Change B both modify the same two shared files. The implementation plan
should combine them into one task per file rather than editing each file in separate tasks.

This design intentionally avoids projection or runtime changes for invocation safety. Any future
mechanism must be specified separately and validated against this repo's boundary rules.

---

## Acceptance Criteria for This Design

1. The spec contains no instruction to add `disable-model-invocation` to shared skill files.
2. The spec contains a deferred follow-up section for invocation safety.
3. `knowledge/solution-plan-template.md` is specified to include `Pattern reference:` in each
   Object Design block.
4. Pattern references allow `AL LSP`, `AL MCP`, or scoped `text search` evidence, and permit
   `none` plus rationale when no analogue exists.
5. `knowledge/solution-plan-template.md` is specified to gain a new `Acceptance Criteria` section.
6. The Acceptance Criteria format is limited to numbered structural, gate, pattern, or
   `[manual]` criteria.
7. `agents/al-dev-solution-architect.md` is specified to require the pattern-reference lookup and
   the constrained criteria format.
8. `skills/al-dev-commit/SKILL.md` is specified to verify only directly checkable criteria and to
   surface `[manual]` items without treating them as automatic blockers.
9. `python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents` exits 0 after
   the agent wording changes.
10. `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared` exits 0 after all
    shared-surface changes.
