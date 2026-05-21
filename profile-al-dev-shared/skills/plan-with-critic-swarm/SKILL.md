---
name: plan-with-critic-swarm
description: Generate plan with parallel critic swarm for defense-in-depth review
argument-hint: "<spec-file-or-description>"
---

# Plan with Critic Swarm

## Overview

Generate an implementation plan, then dispatch 6 parallel critic agents (security, testability, type-safety, rollback-safety, API-contracts, edge-cases) to independently red-team it. Synthesize findings into ranked recommendations, apply auto-fixes, and gate user approval.

## Steps

1. **Generate draft plan** using superpowers:writing-plans skill with the provided spec
2. **Dispatch 6 parallel critics** via Agent tool:
   - **Security Critic:** Check for auth/permission issues, data exposure, input validation
   - **Testability Critic:** Verify tests are concrete, cover happy path + edge cases, assertions are verifiable
   - **Type-Safety Critic:** Scan for missing var parameters, incorrect signatures, generic type mismatches (AL-specific)
   - **Rollback-Safety Critic:** Identify breaking schema changes, data migrations without backfill, hard-deletes
   - **API-Contract Critic:** Check method signatures are consistent, property names follow conventions, no breaking changes
   - **Edge-Cases Critic:** Find assumptions, off-by-one patterns, null-reference risks, boundary violations
3. **Synthesize findings:** Deduplicate, rank by severity, generate auto-fix patches where possible
4. **Apply auto-fixes:** Edit plan with high-confidence fixes (e.g., add missing var, correct anchor string)
5. **Generate critique report:** Write findings + recommendations to `.dev/plan-critique-YYYYMMDD.md`
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

## Dispatch Pattern

```
# Pseudo for reference (actual implementation uses Agent tool in skill body)
for each critic_type in [security, testability, type_safety, rollback_safety, api_contracts, edge_cases]:
  spawn Agent(critic_prompt, plan_content) -> findings_json
merge all findings -> ranked_list
apply auto_fixes(plan) -> updated_plan
ask user approval
```
