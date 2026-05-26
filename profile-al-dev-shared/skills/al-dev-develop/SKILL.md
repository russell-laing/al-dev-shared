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

## Intent Preflight

Before reading the solution plan for execution, dispatching developers, editing
files, staging files, or spawning reviewers, apply
`knowledge/intent-preflight.md`.

Default intent for this skill is `EDIT`. If the request is review-only,
assessment-only, validation-audit-only, planning-only, or commit-only, stop and
ask the intent-mismatch prompt from `knowledge/intent-preflight.md` before any
mutating action or agent dispatch.

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
Phase 0 checks for resumed progress; Phase 0.5 establishes the
resume pack; Phases 1–3 prepare context, checklist, scope, and
developer assignments; Phases 4–4.5 verify implementation
ownership and optional autonomous checks; Phase 5 prepares the
review entry and compile discipline; Phases 8 and 8.5 must pass
before the review panel is spawned; Phases 6–7 then synthesize and
manage review findings; Phase 9 writes the review artifact
(success review or blocking note); Phase 10 presents to the
user. Each phase is a checkpoint with specific
inputs and outputs.

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

**Review Panel:** The three-specialist review team spawned only after
Phases 8 and 8.5 complete cleanly:
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

**Purpose:** Establish the resume pack that `/al-dev-develop`
maintains through the run so context compaction and session
hand-off do not require a full re-read of the solution plan.

**Resume pack artifacts:**
- `.dev/progress.md` — latest phase checkpoint, overwritten each phase
- `.dev/$(date +%Y-%m-%d)-al-dev-develop-progress.md` — dated session snapshot
- `.dev/$(date +%Y-%m-%d)-al-dev-develop-checklist.md` — implementation checklist extracted from plan
- `.dev/$(date +%Y-%m-%d)-al-dev-develop-scope.md` — file-level scope contract

At fresh start:
1. Create or overwrite `.dev/progress.md` per
   `knowledge/workflow-resilience.md`
2. Create the dated progress snapshot for the current run
3. Continue building the rest of the resume pack in later phases:
   - Phase 2.5 writes the checklist artifact
   - Phase 3.0 writes the scope artifact
4. Refresh the resume pack at each named phase boundary

If resuming:
1. Read `.dev/progress.md`
2. Read the latest dated `*-al-dev-develop-progress.md` if present
3. Read the latest dated `*-al-dev-develop-checklist.md` if present
4. Read the latest dated `*-al-dev-develop-scope.md` if present
5. Resume from the recorded next step using the artifacts that
   exist; only re-scan the full plan if a required resume detail
   is missing or contradictory

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

### Phase 2.5: Extract Implementation Checklist

Write `.dev/$(date +%Y-%m-%d)-al-dev-develop-checklist.md`
from the approved solution plan.

Required sections:
- `File` — each in-scope file path
- `Module Variables / Objects` — concrete additions expected
- `Procedures / Triggers` — concrete additions or edits expected
- `Integration Points` — exact existing procedures or trigger
  locations to touch
- `Verification` — compile, review, and artifact checks

Developers and reviewers must reference this checklist instead
of repeatedly re-reading the full solution plan.

## Phase 3: Spawn Developer Team

### Phase 3.0: Write Scope Boundary Document

Before spawning developers, write
`.dev/$(date +%Y-%m-%d)-al-dev-develop-scope.md` with:
- `Files in scope`
- `Permitted change types per file`
- `Files explicitly out of scope`
- `Escalation rule if an out-of-scope edit appears necessary`

Reviewers validate the implementation against this scope file,
not memory alone.

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

## Phase 5: Prepare Review Team

> Canonical panel: `knowledge/review-panel-pattern.md`.
> Role descriptions and synthesis steps are in that doc.

**Compilation Discipline (MANDATORY):**
- Do NOT run `al-compile` after each function or small change
- Write all code for your assigned module (30–50 lines of code) BEFORE compiling
- When code is complete, run `al-compile --output .dev/compile-errors.log` ONCE
- In normal mode, do NOT iterate with compile-fix-compile-fix cycles; batch your fixes after the single compile run
- In autonomous mode (`--autonomous`), follow the bounded compile-fix loop in Phase 8 instead
- Log files: Read errors from `.dev/compile-errors.log`, NOT stdout — errors are logged to file only

Compile result reporting rules:
- Run `al-compile --output .dev/compile-errors.log` with no pipes
- Inspect the file after compile; never pipe the compile command into `head`, `tail`, or `grep`
- In conversation, report only:
  - error count
  - warning count
  - up to 3 representative diagnostics
  - affected files
- Reference `.dev/compile-errors.log` for the full log
- Do not paste raw tail output into the session

(See `markdown/compile-output-best-practices.md` for critical safeguards on compile output handling — never pipe to terminal viewers.)

When all developers complete, finish the implementation compile
pass first using the `.dev/compile-errors.log` generated from
the Phase 5 compilation discipline. Do not spawn reviewers yet.
Phase 8 compilation handling and the Phase 8.5 pre-review
staging gate must both complete cleanly before review begins.

Once Phase 8.5 is satisfied, spawn 3 reviewers in parallel as
a single batch:

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

Execute this phase only after the reviewer batch has actually
been spawned following successful completion of Phases 8 and
8.5.

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

Execute this phase only after Phase 6 has synthesized findings
from the reviewer batch spawned after Phases 8 and 8.5.

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

## Compile Verification Modes

Compilation must be reported from `.dev/compile-errors.log` using concise
summaries, not raw terminal output.

| Mode | Compile Behavior | Success Rule |
|---|---|---|
| Normal `/al-dev-develop` | Run one implementation compile pass, summarize diagnostics, assign one batched fix pass if errors exist, then compile once more. | Do not report success while new compile errors remain. If errors remain after the batched fix pass, write them into the review artifact as blocking compilation issues. |
| `/al-dev-develop --autonomous` | Run bounded compile-fix iterations, up to five compile attempts total. | Do not leave autonomous mode through the success path while new compile errors remain. If five attempts are exhausted, stop with a blocking review artifact. |
| Small fixes | Use `/al-dev-fix`, not `/al-dev-develop`, for a tightly scoped one-file or trivial correction. | Compile once and report the concise result; if compilation fails, fix only errors caused by the small change. |

Hook setup is optional environment guidance. This shared profile defines the
compile discipline, but does not require harness-specific hook installation.

## Phase 8: Compilation & Error Handling

**Execution:**
1. **Read** `.dev/compile-errors.log` (generated after the
   implementation compile pass described in Phase 5)
2. **Categorize** errors using: `python3 .tools/error-categorizer.py .dev/compile-errors.log`
3. **Report** the summary to conversation (NOT raw output):
   - error count
   - warning count
   - up to 3 representative diagnostics
   - affected files
   - reference `.dev/compile-errors.log` as the full log
4. **If no errors:** Proceed to Phase 8.5 (pre-review
   staging). If Phase 8.5 passes, return to the Phase 5
   reviewer batch. If Phase 8.5 finds unexpected residue,
   skip the reviewer batch and continue directly to the
   blocking-note path in Phase 9
5. **After the reviewer batch completes:** continue to
   Phase 6 (synthesise findings) and then Phase 9 (write the
   code review)
6. **If errors exist in normal mode:**
   - Group by category (naming, schema, compilation, warnings)
   - Assign one batched fix pass to the relevant developer(s)
   - Compile once more after all fixes are applied
   - If new compile errors remain, do not report success; write the remaining
     diagnostics into the Phase 9 review artifact as blocking compilation
     issues
7. **If errors exist in autonomous mode (`--autonomous`):**
   - Run a bounded compile-fix loop with at most five compile attempts total
   - After each failed attempt, summarize the error count, representative
     diagnostics, affected files, and assigned fix owner
   - Stop immediately when a compile attempt has no new errors and proceed to
     Phase 8.5
   - If attempt five still has new compile errors, do not report success; write
     a blocking review artifact with the remaining diagnostics and attempts
     summary

### Phase 8.5: Pre-Review File Staging

Before spawning reviewers or beginning review synthesis:
1. Read `.dev/$(date +%Y-%m-%d)-al-dev-develop-scope.md`
2. Run:
   `git -C <repo> status --porcelain`
3. From that status output, collect only paths that both:
   - appear in the scope file's `Files in scope` list
   - currently appear in `git status --porcelain`
4. Stage only the collected in-scope changed paths that exist in
   the working tree. Do not blindly `git add` the full allowlist.
   If a path is deleted and the scope file explicitly permits a
   delete for that file, stage that delete intentionally.
5. Re-run:
   `git -C <repo> status --porcelain`
6. Interpret the output entry-by-entry against both the path list
   and the `Permitted change types per file` section in the scope
   artifact:
   - Acceptable entries are staged-only paths that are listed
     in the scope file and whose staged change type matches what
     that file is permitted to do (for example, edit-only,
     create, delete, rename)
   - If an in-scope path still has unstaged worktree changes,
     stage it and re-run status
   - If any entry is untracked, has unstaged residue after
     re-staging, names a path outside the scope file, or uses a
     staged change type not permitted for that file, mark it as
     unexpected residue
7. If only acceptable staged in-scope entries remain, this
   gate passes and review may continue
8. If any unexpected residue remains:
   - Do not spawn reviewers
   - Do not begin review synthesis
   - Do not continue to the normal success-review path
   - Continue directly to Phase 9 and write the blocking note
     artifact instead

## Phase 9: Validate and Write Code Review

YOU write the synthesis yourself. Write to:
`.dev/$(date +%Y-%m-%d)-al-dev-develop-code-review.md`

Use the structure defined in `knowledge/code-review-template.md`.
In autonomous mode (`--autonomous`), append the Autonomous Verification Results section from the same file.

**Error Summary Section:**

Include this structured error summary in the final code review report:

**Compilation Issues by Category:**
- Extract from `.dev/compile-errors.log` using error categorizer
- Separate: naming violations, schema errors, compilation errors, warnings
- For each category, show:
  - Count
  - Up to 3 representative diagnostics (truncated)
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

This structure helps the user and any follow-up reviewer
understand the remaining fix patterns and affected files quickly.

If Phase 8.5 found unexpected residue, do not write a success
review and do not describe reviewer findings that were never run.
Instead, write a blocking note that lists:
- file path
- why it is outside the approved scope
- user decision status: `pending` if no reply yet, otherwise
  `approved`, `rejected`, or `deferred`

This blocking note is the final review artifact for that run.
Normal reviewer flow resumes only after the unexpected residue
is resolved in a later run.

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
