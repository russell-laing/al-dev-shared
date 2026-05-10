---
name: al-dev-autonomous
description: Implement AL code with automatic symbol verification and compile loop.
argument-hint: "[optional: specific module or scope override]"
---

# Skill: /al-dev-autonomous

Extends al-dev-develop with pre-generation signature
verification and a self-healing compile-verify loop.
You do NOT write code yourself.

## Prerequisites

`.dev/*-al-dev-plan-solution-plan.md` must exist (from /plan).
If missing, tell the user to run /plan first and stop.

---

## Phase 0: Check for Existing Progress

Per `knowledge/workflow-resilience.md` Phase 0 Read Protocol.

---

## Phase 1: Read Context

If `$ARGUMENTS` is provided, treat it as a scope override.
Apply that scope when partitioning work — skip modules outside
the specified scope.

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
4. Extract a list of every external procedure the solution
   will call — base app methods, event subscriptions,
   extension points

---

## Phase 1A: Signature Verification

Before dispatching any developer, verify every external
procedure signature via the AL symbols MCP.

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

---

## Phase 2: Partition Work

Analyze the plan and partition into independent modules.
Each module must own different files — no overlap.

Partition boundaries:

- Data model (tables, table extensions, enums)
- Business logic (codeunits, interfaces)
- UI (pages, page extensions)
- Integration (APIs, event subscribers)

Developers per object count:

| Objects | Developers |
| --- | --- |
| 1-3 | 1 |
| 4-8 | 2-3 |
| 9+ | 3-4 |

For 1-3 objects, skip partitioning and spawn one developer.

---

## Phase 3: Spawn Developer Team

For each developer, include in the prompt:

```text
Implement [module name] from the latest solution plan
(.dev/*-al-dev-plan-solution-plan.md).

Your assigned objects:
- [Object list from partition]

VERIFIED SIGNATURES — use these exactly, do not modify:
[paste relevant entries from signatures.md]

SIGNATURE RULES:
- Use ONLY the signatures listed above for any external call
- For any procedure NOT listed: STOP and report back — do not
  guess parameter names, types, or var modifiers
- var parameters must match exactly — a missing var causes a
  compile error that restarts the entire fix loop

Object name length: STRICT 30-character maximum
(count the characters before writing — do not exceed)

Compile guards: If using #if directives, write a comment
explaining the intended condition before the directive.
Triple-check you have NOT inverted the condition.

Before writing code, also use the AL Symbols MCP to verify
any base app objects you will extend or subscribe to:
- al_get_object_definition — field names, IDs, triggers
- al_search_object_members — exact event publisher signatures
- al_find_references — check for existing similar extensions

Object IDs: [range from plan]
Naming prefix: [from plan or project-context.md]
Project patterns: [from project-context.md if available]
```

Spawn as **al-dev-developer** agents. If parallel, spawn
all at once.

---

## Phase 4: Verify on Completion

When all developers complete:

1. Check file ownership — no two developers wrote the same file
2. Verify naming consistency across all objects
3. Check object ID usage — no duplicates, all in range
4. Answer tactical questions left open
5. Escalate to user only for architectural blocking issues

Write `.dev/progress.md` per `knowledge/workflow-resilience.md`.

---

## Phase 4A: Static Validation

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

- The condition matches the intended feature flag (common
  error: `#if NOT SLADATE` when `#if SLADATE` was intended)
- Every `#if` has a matching `#endif`
- The `#else` branch, if present, contains the correct fallback

Flag any inverted condition or unmatched directive as CRITICAL.

### Check 3: Label and Message Consistency

```bash
grep -rn "label\|Error(\|Message(\|FieldCaption" \
  --include="*.al" . | head -50
```

Cross-reference against the solution plan's feature
descriptions. Flag any label using different terminology than
the plan (e.g. plan says "allocation" but code says
"distribution") as a HIGH issue.

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

If CRITICAL issues found: dispatch a developer with the
specific violations. Wait for fixes. Re-run the relevant
check before spawning the review team.

---

## Phase 5: Spawn Review Team

Spawn 4 reviewers in parallel as a single batch.

**al-dev-security-reviewer:** Review all code for permission
issues, data exposure risks, authentication gaps.

**al-dev-expert-reviewer:** Review for AL naming conventions,
BC best practices (SetLoadFields, FieldCaption), code
organization, event patterns.

**al-dev-performance-reviewer:** Review for query efficiency,
N+1 patterns, SetLoadFields usage, loop efficiency, record
variable scoping.

**al-dev-test-coverage-reviewer:** Review for testability,
interfaces for mocking, event extensibility, test scenario
coverage vs solution plan.

Each reviewer reads ALL implemented AL files.

Write `.dev/progress.md` per `knowledge/workflow-resilience.md`.

---

## Phase 6: Synthesise Review Findings

When all reviewers complete:

1. Read all four review outputs
2. Cross-reference overlapping findings — issues raised by
   multiple reviewers are higher priority
3. Resolve contradictions using your own judgement
4. Consolidate into a single categorised list

---

## Phase 7: Manage Review Iteration

Categorize findings:

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

If CRITICAL found: assign fixes, re-review, iterate until
resolved. Do NOT present to user until critical issues are
resolved.

---

## Phase 8: Compile-Verify Loop

Run the compile-verify loop. Track attempt count.

### Setup

Always initialize these at Phase 8 entry — do not carry over
any attempt count from earlier phases:

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
The diagnostics-fixer re-compiles internally (see
`al-dev-diagnostics-fixer.md` Step 5). After it completes,
read its lint report to confirm clean compile, then proceed
to Phase 9.

**If `Error` lines found:**

Parse the log. Extract per error: file path, line number,
error code, message text. Group by file.

Resolve the actual signatures file path before spawning:

```bash
SIGFILE=$(ls .dev/*-al-dev-autonomous-signatures.md \
  2>/dev/null | sort | tail -1)
```

Spawn **al-dev-developer** with this prompt (substitute the
actual values of `ATTEMPT` and `SIGFILE` before pasting —
do not paste the literal variable names):

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

Increment the counter: `ATTEMPT=$((ATTEMPT + 1))`

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

---

## Phase 9: Validate and Write Code Review

YOU write the code review. Write to:
`.dev/$(date +%Y-%m-%d)-al-dev-autonomous-code-review.md`

Include all sections from the al-dev-develop code review
template (see `skills/al-dev-develop/SKILL.md` Phase 9 for
the full structure) PLUS this additional section:

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

After writing, run the validator:

```bash
VALIDATOR="$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-autonomous/validate-code-review.py"
PLAN=$(ls .dev/*-al-dev-plan-solution-plan.md \
  2>/dev/null | sort | tail -1)
REVIEW=$(ls .dev/*-al-dev-autonomous-code-review.md \
  2>/dev/null | sort | tail -1)
[ -f "$VALIDATOR" ] && [ -n "$PLAN" ] && \
  [ -n "$REVIEW" ] && python3 "$VALIDATOR" \
  "$REVIEW" "$PLAN" || echo \
  "Validator not found — skipping"
```

Fix any issues before presenting to the user.

---

## Phase 10: Present to User for Approval

```text
Implementation complete → [list AL files created]

Autonomous verification:
✅ N external signatures verified via AL symbols MCP
   [N unverified — see risks in code review]
✅ Object names: all ≤30 chars [or: N violations fixed]
✅ Compile guards: all correct [or: N inversions fixed]
✅ Labels: consistent with plan [or: N discrepancies flagged]
✅ Compilation clean (N of 5 attempts)

Review findings (4 specialist reviewers):
[N] critical issues found and fixed
[N] high-priority issues for your decision
[N] minor suggestions documented

Key implementations:
- [Object 1]: [1-sentence description]
- [Object 2]: [1-sentence description]

Code review → .dev/[date]-al-dev-autonomous-code-review.md
Signatures → .dev/[date]-al-dev-autonomous-signatures.md
Static validation →
  .dev/[date]-al-dev-autonomous-static-validation.md
Lint report → .dev/[date]-al-dev-lint-lint-report.md
  (only present if warnings were found; N unresolved if any)

Ready to proceed to testing?
```

USER_GATE — ask the user with options:

- Approve — Proceed to testing
- Review Issues — Show high-priority issues in detail
- Fix Issues First — Address high-priority issues now
- Refine — Adjust implementation
- Stop — Cancel development
