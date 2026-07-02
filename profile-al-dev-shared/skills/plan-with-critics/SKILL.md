---
name: plan-with-critics
description: >-
  Generate an implementation plan from a spec, then red-team it with six
  critics covering security, testability, type-safety, rollback safety, API
  contracts, and edge cases before user approval.
argument-hint: "<spec-file-or-description>"
---

# Plan with Critic Swarm

## Overview

Generate an implementation plan, then dispatch 6 parallel critic agents (security, testability, type-safety, rollback-safety, API-contracts, edge-cases) to independently red-team it. Synthesize findings into ranked recommendations, apply auto-fixes, and gate user approval.

**Note:** This skill always generates a fresh plan from the provided spec (Step 1).
If you already have a plan file, provide it as the spec input — the skill will treat
it as the starting specification rather than generating a competing plan.

## Steps

See ../../knowledge/critic-dispatch-template.md for the standard 6-critic batch pattern and deduplication rules.

Expected outputs from critics:

- Ranked list of approaches (N approaches, each scored 1-5)
- Pros/cons per approach (3-4 bullets each)
- Winner recommendation with justification

1. **Generate draft plan** using superpowers:writing-plans skill with the provided spec
See `../../knowledge/critic-dispatch-template.md` for the pattern documentation
(parallel dispatch + dedup + synthesize). The following implementation uses the
6-critic variant.
2. **Dispatch 6 parallel critics** via Agent tool:
   - **Security Critic:** Check for auth/permission issues, data exposure, input validation
   - **Testability Critic:** Verify tests are concrete, cover happy path + edge cases, assertions are verifiable
   - **Type-Safety Critic:** Scan for missing var parameters, incorrect signatures, generic type mismatches (AL-specific)
   - **Rollback-Safety Critic:** Identify breaking schema changes, data migrations without backfill, hard-deletes
   - **API-Contract Critic:** Check method signatures are consistent, property names follow conventions, no breaking changes
   - **Edge-Cases Critic:** Find assumptions, off-by-one patterns, null-reference risks, boundary violations
3. **Synthesize findings:** Deduplicate, rank by severity, generate auto-fix patches where possible
4. **Apply auto-fixes:** Edit plan with high-confidence fixes (e.g., add missing var, correct anchor string)
5. **Generate critique report:** Write findings + recommendations to `.dev/plan-critique-YYYY-MM-DD.md` (replace `YYYY-MM-DD` with the current date in ISO form, e.g. `2026-06-24`)
6. **Gate approval:** Present synthesized findings and ask user to approve plan before passing to executing-plans

## Example Workflow

Spec: "Add a new Table with fields linked to Customer"

Critics find:

- ❌ **Type-Safety:** Procedure modifying table has no `var` param in event subscriber
- ❌ **Rollback-Safety:** New schema field is NOT NULL, no backfill strategy for existing rows
- ⚠️ **API-Contract:** Field name uses suffix (BadgerCertExpires) instead of prefix (exp_BadgerCert)
- ✅ **Tests:** Plan includes test for new field validation

Auto-fixes applied: var parameter added, field renamed
Findings written: Rollback strategy must be addressed before execution
Approval gate: User reviews findings, approves plan with noted constraints
