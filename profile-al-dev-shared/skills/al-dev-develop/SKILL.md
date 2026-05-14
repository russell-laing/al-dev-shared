---
name: al-dev-develop
description: >-
  Implement an AL/BC solution using parallel developers
  and 4-specialist review (security, AL expert, performance,
  test coverage). Use when implementing a planned feature,
  generating AL code, or building from a solution plan.
  Requires a solution plan. Prefer over ad-hoc
  implementation for anything beyond a trivial fix.
argument-hint: "[optional: specific module or scope override]"
---

# Develop Skill

Implement an AL/BC solution using parallel developers
and 4-specialist review. You do NOT write code yourself.

## Prerequisites

`.dev/*-al-dev-plan-solution-plan.md` must exist (from
/plan). If missing, tell the user to run /plan first
and stop.

## Phase 0: Check for Existing Progress

Per the Phase 0 Read Protocol in
`knowledge/workflow-resilience.md`.

---

## Phase 1: Read Context

If `$ARGUMENTS` is provided, treat it as a scope override
(e.g. "data-model-only", "UI layer", "integration module").
Apply that scope when partitioning work in Phase 2 — skip
modules outside the specified scope.

1. Read the latest solution plan:
   `$(ls .dev/*-al-dev-plan-solution-plan.md 2>/dev/null \
   | sort | tail -1)`
2. Read `.dev/project-context.md` if it exists
3. Identify:
   - Objects to create (tables, pages, codeunits, enums)
   - BC integration points
   - Validation rules
   - Testability requirements
   - Object ID ranges

## Phase 2: Partition Work

Analyze the plan and partition into independent modules.
Each module must own different files — no overlap.

Partition boundaries:
- Data model (tables, table extensions, enums)
- Business logic (codeunits, interfaces)
- UI (pages, page extensions)
- Integration (APIs, event subscribers)

**How many developers to spawn:**

| Objects | Developers |
| ------- | ---------- |
| 1-3     | 1          |
| 4-8     | 2-3        |
| 9+      | 3-4        |

For small solutions (1-3 objects), skip partitioning and
spawn a single developer.

## Phase 3: Spawn Developer Team

For each developer, include in the prompt:

```text
Implement [module name] from the latest solution plan
(.dev/*-al-dev-plan-solution-plan.md).

Your assigned objects:
- [Object list from partition]

Before writing code, use the AL Symbols MCP (`al-mcp-server`)
to verify base app objects you will extend or subscribe to:
- al_get_object_definition — confirm field names, IDs, and
  triggers on base tables you are extending
- al_search_object_members — locate the exact event signatures
  you plan to subscribe to
- al_find_references — check if similar extensions already
  exist in the project

Follow AL best practices:
- SetLoadFields for record retrieval
- Error handling with FieldCaption
- Dependency injection for testability
- Events for extensibility

Object IDs: [range from plan]
Naming prefix: [from plan or project-context.md]
Project patterns: [from project-context.md if available]

IMPORTANT: Do NOT run git commit. Your role is to implement
and verify compilation only. Commits are handled separately
by /al-dev-commit after user approval.
```

Spawn developers as **al-dev-developer** agents. If parallel,
spawn all at once.

## Phase 4: Verify on Completion

When all developers complete, verify before proceeding:

1. Check file ownership — confirm no two developers wrote
   the same file (if there's overlap, assign one owner to
   reconcile and re-implement)
2. Verify naming consistency across all objects
3. Check object ID usage — no duplicates, all in range
4. Answer any tactical questions left open (object ID
   assignment, naming clarification)
5. Escalate to user only for architectural changes or
   requirements ambiguity that block progress

Write `.dev/progress.md` per `knowledge/workflow-resilience.md`.

## Phase 5: Spawn Review Team

When all developers complete, spawn 4 reviewers in parallel
as a single batch:

**al-dev-security-reviewer:**
Review all implemented code for permission issues, data
exposure risks, authentication gaps.

**al-dev-expert-reviewer:**
Review for AL naming conventions, BC best practices
(SetLoadFields, FieldCaption), code organization, event
patterns.

**al-dev-performance-reviewer:**
Review for query efficiency, N+1 patterns, SetLoadFields
usage, loop efficiency, record variable scoping.

**al-dev-test-coverage-reviewer:**
Review for testability (dependency injection present?),
interfaces for mocking, event extensibility, test scenario
coverage. Compare to the latest solution plan
(.dev/*-al-dev-plan-solution-plan.md) testability
requirements.

Each reviewer reads ALL implemented AL files.

Write `.dev/progress.md` per `knowledge/workflow-resilience.md`.

## Phase 6: Synthesise Review Findings

When all reviewers complete:

1. Read all four review outputs
2. Cross-reference overlapping findings — if Security
   and Performance both flag the same code, that finding
   is higher priority than one raised by a single reviewer
3. Where reviewers contradict each other (e.g. AL Expert
   recommends a pattern that Performance flags as slow),
   apply your own judgement to resolve the conflict using
   the criteria in Phase 7
4. Consolidate into a single categorised list before
   assigning fixes

## Phase 7: Manage Review Iteration

Categorize all findings:

**CRITICAL** (must fix before user sees code):
- Security vulnerabilities
- Data corruption risks
- Missing core functionality
- Broken testability (no dependency injection)

**HIGH** (should fix):
- Performance issues, missing SetLoadFields
- Poor error handling, pattern violations

**MINOR** (nice to have):
- Naming suggestions, code organization, comments

Decision:
- CRITICAL found: assign fixes to relevant developer(s),
  re-review after fixes, iterate until resolved
- Only HIGH/MINOR: document in code review, present to
  user for decision

Do NOT present to user until critical issues are resolved.

## Phase 8: Compile + Lint Pass

Follow `knowledge/compile-lint-procedure.md` in full.

Write lint report to:
`.dev/$(date +%Y-%m-%d)-al-dev-lint-lint-report.md`

Additional rules for this skill:

- If compilation errors remain after the developer fix pass,
  reassign to the responsible developer agent and iterate.
- If `al-compile` is unavailable, skip the diagnostics-fixer
  step and note "Compilation not verified" in the Phase 10
  review summary.
- Unresolved lint items from the lint report are surfaced at
  the Phase 10 user approval gate — no new gate here.
- If the diagnostics-fixer introduces a regression (new
  compile errors), spawn a new `al-dev-developer` agent with
  the regression details, re-run `al-compile`, then
  re-spawn diagnostics-fixer.

Write `.dev/progress.md` per `knowledge/workflow-resilience.md`.

## Phase 9: Validate and Write Code Review

YOU write the synthesis yourself. Write to:
`.dev/$(date +%Y-%m-%d)-al-dev-develop-code-review.md`

Use this structure:

```markdown
## Code Review: [Feature Name]

### Implementation Summary
[What was built: objects, key functionality]

### Review Process
4 specialized reviewers (security, AL expert, performance,
test coverage) completed parallel review.

### Critical Issues (All Resolved)
- Issue: [description]
  Fix: [what was changed]
  Verified by: [which reviewer re-checked]

### Issues for User Decision

**High Priority:**
1. [Issue description]
   - Severity: High
   - Impact: [what happens if not fixed]
   - Recommendation: [suggested fix]

**Minor Issues:**
1. [Issue description]
   - Recommendation: [optional improvement]

### Review Consensus
[Overall quality assessment]

### Recommendation
Code is ready for [testing/deployment] with [N]
high-priority issues to address.
```

After writing, run the validator:

```bash
VALIDATOR="$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-develop/validate-code-review.py"
PLAN=$(ls .dev/*-al-dev-plan-solution-plan.md \
  2>/dev/null | sort | tail -1)
REVIEW=$(ls .dev/*-al-dev-develop-code-review.md \
  2>/dev/null | sort | tail -1)
[ -f "$VALIDATOR" ] && [ -n "$PLAN" ] && \
  [ -n "$REVIEW" ] && python3 "$VALIDATOR" \
  "$REVIEW" "$PLAN" || echo \
  "Validator not found — skipping"
```

Fix any issues before presenting to the user.

## Phase 10: Present to User for Approval

```text
Implementation complete -> [list AL files created]

Review findings (4 specialist reviewers):
[N] critical issues found and fixed
[N] high-priority issues for your decision
[N] minor suggestions documented

Key implementations:
- [Object 1]: [1-sentence description]
- [Object 2]: [1-sentence description]
- [Object 3]: [1-sentence description]

Code review -> .dev/[date]-al-dev-develop-code-review.md
Lint report -> .dev/[date]-al-dev-lint-lint-report.md
  (N unresolved items, if any)
Compilation: [Success / Not verified]

Ready to proceed to testing?
```

USER_GATE — ask the user with options:
- Approve - Proceed to testing
- Review Issues - Show high-priority issues in detail
- Fix Issues First - Address high-priority issues now
- Refine - Adjust implementation
- Stop - Cancel development

After user approves, remind them: "Run `/al-dev-commit` to stage
and commit the implemented changes using the validated commit
workflow."

