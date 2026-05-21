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

## Glossary

**Scope Expansion Gate:** A governance checkpoint enforced during
development that prevents out-of-scope changes. Before editing any
file or line not explicitly named in the approved solution plan, you
must stop and present proposed changes to the user for per-item
approval. Prevents scope creep and ensures the solution stays true
to the plan.

**Developer Spawn Prompt:** The structured prompt dispatched to each
spawned `al-dev-developer` agent. Contains the module assignment,
object list, object ID range, naming conventions, code patterns,
and the Scope Expansion Gate rules. Ensures consistency across
parallel developers.

**Phase 0–10:** Semantic workflow layers of the /al-dev-develop skill.
Phase 0 checks for resumed progress; Phases 1–4 read context and
partition work; Phase 5 spawns developers; Phases 6–7 handle review;
Phase 8 compiles and lints; Phase 9 writes the code review; Phase 10
presents to user. Each phase is a checkpoint with specific inputs
and outputs.

**Phase 1.5 (Autonomous):** Optional signature verification phase
activated by the `--autonomous` flag. Uses AL Symbols MCP to verify
external procedure signatures before developers are spawned, reducing
downstream compilation errors.

**Phase 4.5 (Autonomous):** Optional static validation phase that
runs after developer completion but before the review team is spawned.
Checks object name lengths, compile guards, and label consistency
against the solution plan.

**Phase 8 Compile-Verify Loop:** Extended compilation strategy used
in autonomous mode. Runs up to 5 sequential compile-fix-compile
cycles with detailed error tracking per attempt. After each compile,
parses errors, spawns a developer to fix them, and re-compiles.
Stops after 5 failed attempts and escalates to the user.

**Review Panel:** The three-specialist review team spawned in Phase 5:
**al-dev-security-reviewer** (permission/auth/data exposure),
**al-dev-expert-reviewer** (AL conventions/BC patterns), and
**al-dev-performance-reviewer** (N+1/SetLoadFields/efficiency).
Each reviewer reads all implemented AL files independently.

**Autonomous Mode:** Optional hardened workflow activated by the
`--autonomous` flag. Adds Phase 1.5 (signature verification),
Phase 4.5 (static validation), and a 5-attempt compile loop in Phase 8.
Produces verified signatures and validation reports before review,
reducing review iteration.

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

## Phase 0.5: Context Preservation Checkpoint

**Purpose:** Before development starts, create a resumable checkpoint in case context compaction occurs.

**Execution:**

1. Check if `.dev/resume-context.md` exists
   - If yes, read it and offer resume/restart option to user
   - If restart chosen, delete checkpoint and proceed to Phase 1
   - If resume chosen, inject checkpoint state into Phase 1 restart

2. If starting fresh, write `.dev/resume-context.md`:

   ```markdown
   # Development Resume Checkpoint — [ISO-8601 timestamp]

   ## Current State
   - **Phase:** 1 (Design & Module Planning)
   - **Modules assigned:** [List of module assignments by developer]
   - **Last compilation:** [Timestamp or "not yet run"]
   - **Error summary:** [If any errors from previous compile]
   - **Developer progress:**
     - Developer A: [Module name, lines written, current task]
     - Developer B: [Module name, lines written, current task]

   ## Resumption Instructions
   If context overflow occurs, inject this section into the next session's developer spawn:
   > "Previous session checkpoint: [current state details]. Resume from this point."

   ## Next Steps
   - [Task 1]
   - [Task 2]
   - [Task 3]
   ```

3. **Update checkpoint after each phase completes** — append new state before proceeding to next phase

**Why this helps:**
- Explicit record of where development left off
- Prevents asking developers to re-explain design decisions after compaction
- Enables instant resumption without re-planning

**When to enable:** After first context compaction is detected

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

SYMBOL_PREFLIGHT_GATE — Complete BEFORE writing any AL code.
Follow `knowledge/al-symbol-pre-flight.md` for the full checklist.
Required checks:
1. Field references: verify each base field via al_get_object_definition
   (exact field name, including spacing and capitalisation)
2. Event signatures: verify via al_search_object_members — every var
   parameter in the publisher MUST be declared var in your subscriber;
   missing var = AL0118 compile error
3. Object names: count characters — each must be ≤30
4. Object IDs: confirm all are in your assigned range with no duplicates

Report your pre-flight summary before writing a single line of AL:
"Pre-flight complete: fields verified [list], events verified [list],
names/IDs OK [or: issue found]."

DO NOT proceed past pre-flight if any item is unverified. Stop and
report back to the orchestrator with the unverified item.

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

**Compilation Discipline (MANDATORY):**
- Do NOT run `al-compile` after each function or small change
- Write all code for your assigned module (30–50 lines of code) BEFORE compiling
- When code is complete, run `al-compile --output .dev/compile-errors.log` ONCE
- Do NOT iterate with compile-fix-compile-fix cycles; batch your fixes after the single compile run
- Log files: Read errors from `.dev/compile-errors.log`, NOT stdout — errors are logged to file only

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

## Phase 8: Compilation & Error Handling

**Execution:**
1. **Read** `.dev/compile-errors.log` (compiled by Phase 5 batch compile)
2. **Categorize** errors using: `python3 .tools/error-categorizer.py .dev/compile-errors.log`
3. **Report** the summary to conversation (NOT raw output)
4. **If no errors:** Proceed to Phase 9 (code review)
5. **If errors exist:** 
   - Group by category (naming, schema, compilation, warnings)
   - Assign fixes to reviewers based on error type
   - Compile once more after all fixes applied

## Phase 9: Validate and Write Code Review

YOU write the synthesis yourself. Write to:
`.dev/$(date +%Y-%m-%d)-al-dev-develop-code-review.md`

Use the structure defined in `knowledge/code-review-template.md`.
In autonomous mode (`--autonomous`), append the Autonomous Verification Results section from the same file.

**Error Summary Section:**

Before reviewers analyze code, include this structured error summary in the code review report:

**Compilation Issues by Category:**
- Extract from `.dev/compile-errors.log` using error categorizer
- Separate: naming violations, schema errors, compilation errors, warnings
- For each category, show:
  - Count
  - 2–3 representative examples (truncated)
  - Suggested fix pattern
  - Files affected

**Example format:**

```
## Compilation Status

**Naming Violations (5 fields):**
- Fields missing 'AC' prefix in Customer.Table.al:45-89
- Suggested fix: Rename fields to AC[FieldName] pattern
- Files: Customer.Table.al

**Schema Errors (2 references):**
- Field "G/L Register No." not found in G/L Entry table
- Suggested fix: Use "Entry No." instead (primary key exists)
- Files: JournalEntryAllocation.Table.al:123
```

This structure helps reviewers prioritize fixes by category and understand root causes quickly.

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

