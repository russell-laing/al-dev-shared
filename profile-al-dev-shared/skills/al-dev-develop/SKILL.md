---
name: al-dev-develop
description: >-
  Implement an AL/BC solution using parallel developers
  and 3-specialist review (security, AL expert, performance).
  Use when implementing a planned feature,
  generating AL code, or building from a solution plan.
  Requires a solution plan. Pass --autonomous to activate
  signature verification, static validation, and a
  self-healing compile loop (replaces /al-dev-autonomous).
  Prefer over ad-hoc implementation for anything beyond a trivial fix.
argument-hint: "[--autonomous] [module or scope override]"
---

# Develop Skill

Implement an AL/BC solution using parallel developers
and 3-specialist review. You do NOT write code yourself.

## Prerequisites

`.dev/*-al-dev-plan-solution-plan.md` must exist (from
/plan). If missing, tell the user to run /plan first
and stop.

## Scope Expansion Gate

While executing this skill, BEFORE you (or any dispatched
developer agent) edit a file or change a line that is not
explicitly named in the approved plan, you MUST:

1. Stop — do not invoke the edit tool yet.
2. List the proposed out-of-scope change(s) as numbered items:

   ~~~text
   **Proposed out-of-scope changes:**
   1. [file:line] — [what would change and why]
   2. [file:line] — [what would change and why]
   ~~~

3. Present to the user with this exact prompt:
   "These changes are outside the approved plan. Approve, reject,
   or defer each. Reply with item numbers (e.g., '1 approve, 2
   defer')."
4. Wait for per-item decision before resuming.

**What counts as "out of scope":**

- New file not listed in the plan
- Edit to a procedure, field, or object not referenced in the
  plan, even if it is in a file the plan does name
- Fixing an "encountered" issue (lint warning, deprecated API,
  unrelated bug) that the plan did not call out

**What does NOT count as "out of scope":**

- Cosmetic adjustments inside an in-scope edit (whitespace,
  formatter output)
- Importing a dependency required to implement an in-scope change

This gate is passed verbatim into every developer agent dispatch
in Phase 3 so the rule propagates to subagents.

## Phase 0: Check for Existing Progress

Per the Phase 0 Read Protocol in
`knowledge/workflow-resilience.md`.

---

## Phase 1: Read Context

**Autonomous mode detection:**
Check `$ARGUMENTS` for `--autonomous`. If present:
- After Step 3 below, run Phase 1.5 (Signature Verification) before
  proceeding to Phase 2
- After Phase 4 (Verify on Completion), run Phase 4.5 (Static Validation)
  before spawning the review team
- In Phase 8, use the 5-attempt compile-verify loop instead of the
  single compile pass
- In Phase 9, use the extended code review template (includes autonomous
  verification results section)

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

## Phase 1.5: Signature Verification (--autonomous only)

Skip this phase if `--autonomous` is not in `$ARGUMENTS`.

Before dispatching any developer, verify every external procedure
signature via the AL symbols MCP.

For each external procedure identified in Phase 1, run the
appropriate MCP query:

```text
al_get_object_definition — for base objects being extended:
  confirms field names, IDs, and trigger signatures

al_search_object_members — for event signatures and methods:
  locates exact event publisher signatures with var parameters

al_find_references — to detect existing similar extensions:
  avoids duplicate subscriber registration
```

Verify for each procedure:

- Exact procedure name (case-sensitive)
- Parameter list: names, types, var vs value modifier
- Return type if applicable

Write verified signatures to:
`.dev/$(date +%Y-%m-%d)-al-dev-autonomous-signatures.md`

Use this format:

```markdown
## Verified Signatures

### [ObjectType] [ObjectName].[ProcedureName]
- Parameters: [ParamName: Type; var ParamName: Type]
- Return: [Type or void]
- Source: al_search_object_members / al_get_object_definition
- Verified: [ISO timestamp]

### NOT VERIFIED: [ProcedureName]
- Reason: [not found in MCP / ambiguous match]
- Risk: Developer must not guess this signature
```

If any procedure is NOT VERIFIED, include this block in the
developer spawn prompt:

```text
⚠️ Unverified signatures — do NOT guess these:
- [ProcedureName]: [reason not verified]
STOP and report back if you need to call this procedure.
```

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

SCOPE EXPANSION GATE: Before editing any file or line not
explicitly named in the plan, you MUST stop — do not invoke
the edit tool yet. Instead, list the
proposed change(s) as numbered items in this format:

  **Proposed out-of-scope changes:**
  1. [file:line] — [what would change and why]

Then present to the user: "These changes are outside the
approved plan. Approve, reject, or defer each. Reply with
item numbers (e.g., '1 approve, 2 defer')."

Wait for per-item decision before resuming. Do NOT silently
expand scope by fixing encountered lint warnings, deprecated
APIs, or unrelated issues not named in the plan.
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

## Phase 4.5: Static Validation (--autonomous only)

Skip this phase if `--autonomous` is not in `$ARGUMENTS`.

Run these checks on all newly created AL files before the
review team is spawned. Fix CRITICAL issues by dispatching
a developer before proceeding.

### Check 1: Object Name Length

```bash
grep -rn -E \
  '^(table|page|codeunit|report|enum|interface|xmlport|query|permissionset)\s+[0-9]+\s+' \
  --include="*.al" .
```

For each match, the object name is everything after the numeric
ID. Count its characters. Flag any name exceeding 30 characters
as a CRITICAL issue.

### Check 2: Compile Guard Logic

```bash
grep -rn '#if\|#else\|#endif' --include="*.al" .
```

For each `#if` directive, read the surrounding block. Verify:

- The condition matches the intended feature flag
- Every `#if` has a matching `#endif`
- The `#else` branch, if present, contains the correct fallback

Flag any inverted condition or unmatched directive as CRITICAL.

### Check 3: Label and Message Consistency

```bash
grep -rn "label\|Error(\|Message(\|FieldCaption" \
  --include="*.al" . | head -50
```

Cross-reference against the solution plan's feature descriptions.
Flag any label using different terminology than the plan as a HIGH issue.

### Static Validation Report

Write to:
`.dev/$(date +%Y-%m-%d)-al-dev-autonomous-static-validation.md`

```markdown
## Static Validation Results

### Object Name Lengths
| Object | Name | Length | Status |
| --- | --- | --- | --- |
| table 50100 | ABCSomeName | 11 | ✅ |

### Compile Guards
| File | Line | Directive | Status |
| --- | --- | --- | --- |

### Label Consistency
| File:Line | Label Text | Plan Term | Status |
| --- | --- | --- | --- |

### Summary
CRITICAL issues: N (must fix before review)
HIGH issues: N (flagged in code review)
```

If CRITICAL issues found: dispatch a developer with the specific
violations. Wait for fixes. Re-run the relevant check before
spawning the review team.

## Phase 5: Spawn Review Team

> Canonical panel: `knowledge/review-panel-pattern.md`.
> Role descriptions and synthesis steps are in that doc.

When all developers complete, spawn 3 reviewers in parallel
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

Each reviewer reads ALL implemented AL files.

Write `.dev/progress.md` per `knowledge/workflow-resilience.md`.

## Phase 6: Synthesise Review Findings

When all reviewers complete:

1. Read all three review outputs
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

**Standard mode** (no `--autonomous`): Follow
`knowledge/compile-lint-procedure.md` in full.

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

---

**Autonomous mode** (`--autonomous` in `$ARGUMENTS`):

Run the compile-verify loop. Track attempt count.

### Setup

Always initialize these at Phase 8 entry:

```bash
mkdir -p .dev
ATTEMPT=1
MAX_ATTEMPTS=5
```

### Compile Step

```bash
if command -v al-compile &>/dev/null; then
  al-compile --output \
    .dev/compile-errors-attempt-${ATTEMPT}.log
else
  al compile /project:. /packagecachepath:.alpackages \
    /errorlog:.dev/compile-errors-attempt-${ATTEMPT}.log
fi
```

### After Each Compile

**If log is absent, empty, or contains no `Error` lines:**
Compilation is clean. Record that it took N attempts.
Proceed to Phase 9.

**If only `Warning` lines (no `Error` lines):**
Spawn `al-dev-diagnostics-fixer` once to resolve warnings.
Do NOT count this as a failed attempt.
After it completes, read its lint report to confirm clean
compile, then proceed to Phase 9.

**If `Error` lines found:**

Parse the log. Extract per error: file path, line number,
error code, message text. Group by file.

Resolve the signatures file path before spawning:

```bash
SIGFILE=$(ls .dev/*-al-dev-autonomous-signatures.md \
  2>/dev/null | sort | tail -1)
```

If `SIGFILE` is empty (Phase 1.5 did not run or MCP was unavailable),
omit the signatures section from the developer prompt and add this
warning instead:

```text
⚠️ Signature file not found — MCP verification was not completed.
Developers MUST verify signatures manually before fixing errors.
```

Spawn **al-dev-developer** with this prompt (substitute actual
values of `ATTEMPT` and `SIGFILE` — do not paste literal variable names):

```text
Fix compilation errors in the AL project.
This is attempt [ATTEMPT] of 5.

Errors from .dev/compile-errors-attempt-[ATTEMPT].log:
[paste full error list grouped by file]

Verified signatures (use these exactly — do NOT alter):
[paste relevant entries from [SIGFILE]]

Context from solution plan for each erroring file:
[paste relevant plan excerpt per file]

Rules:
- Fix ONLY the listed errors — do not refactor other code
- If a signature error matches an "unverified" procedure,
  use the AL symbols MCP NOW to get the correct signature
  before fixing
- Do NOT re-compile after fixing (the orchestrator compiles)
- Report: [file:line] → [what changed] for each fix
```

Increment: `ATTEMPT=$((ATTEMPT + 1))`

If `ATTEMPT <= MAX_ATTEMPTS`: return to Compile Step.

### After 5 Failed Attempts

Present to user:

```text
Compilation still failing after 5 attempts.

Remaining errors (.dev/compile-errors-attempt-5.log):
[list all remaining errors]

Summary of fix attempts:
- Attempt 1: [files changed, what was tried]
- Attempt 2: [files changed, what was tried]
...

These errors likely require architectural review or a
change to the solution plan approach.
```

USER_GATE — ask the user with options:

- Show full error detail for all 5 logs
- Assign manual fix with more context
- Revise solution plan approach

## Phase 9: Validate and Write Code Review

YOU write the synthesis yourself. Write to:
`.dev/$(date +%Y-%m-%d)-al-dev-develop-code-review.md`

Use the structure defined in `knowledge/code-review-template.md`.
In autonomous mode (`--autonomous`), append the Autonomous Verification Results section from the same file.

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

**Autonomous mode addition** (`--autonomous`):
Append this additional section to the code review:

```markdown
### Autonomous Verification Results

#### Signature Verification
| Procedure | Status | Source |
| --- | --- | --- |
| ObjectName.ProcedureName | ✅ Verified | al_search_object_members |
| ObjectName.OtherProc | ⚠️ Not verified | Not found in MCP |

Unverified risks: [describe any NOT VERIFIED entries]

#### Static Validation
| Check | Result |
| --- | --- |
| Object names (≤30 chars) | ✅ All valid / ❌ N fixed |
| Compile guards (#if logic) | ✅ All correct / ❌ N fixed |
| Label consistency | ✅ Matches plan / ⚠️ N flagged |

#### Compile-Verify Loop
- Attempts required: N of 5
- Final status: ✅ Clean / ⚠️ N warnings remain
```

In autonomous mode, use the standard develop validator:
`$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-develop/validate-code-review.py`

## Phase 10: Present to User for Approval

```text
Implementation complete -> [list AL files created]

Review findings (3 specialist reviewers):
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

**Autonomous mode:** add this block before "Review findings":

```text
Autonomous verification:
✅ N external signatures verified via AL symbols MCP
   [N unverified — see risks in code review]
✅ Object names: all ≤30 chars [or: N violations fixed]
✅ Compile guards: all correct [or: N inversions fixed]
✅ Labels: consistent with plan [or: N discrepancies flagged]
✅ Compilation clean (N of 5 attempts)
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

