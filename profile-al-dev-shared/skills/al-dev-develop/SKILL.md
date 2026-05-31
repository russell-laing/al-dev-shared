---
name: al-dev-develop
description: >-
  Prepare implementation context, validate scope, partition work across developers,
  and dispatch developers to implement AL code. Consumes a solution plan and orchestrates
  parallel developer agents through pre-flight validation and implementation.
  Produces Phase 4 handoff artifact for /al-dev-review-develop (review orchestration).
  Requires a solution plan. Pass --autonomous to activate signature verification
  and static validation.
argument-hint: "[--autonomous] [module or scope override]"
---

# Develop Skill

Prepare implementation context, validate scope, partition work across developers,
and dispatch developers to implement AL code. You do NOT write code yourself.

After all developers complete, /al-dev-review-develop orchestrates the review panel,
compilation, and code-review output.

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

## Artifact Contract

Use `knowledge/artifact-contracts.md` as the source of truth for this skill's
durable outputs, resume read order, handoff artifact, and success evidence.

Do not claim implementation is complete or ready for `/al-dev-review-develop`
until the success evidence named in `knowledge/artifact-contracts.md` for
`al-dev-develop` has been produced and read for the current run.

## Scope Expansion Gate

The full gate rules (procedure, in-scope/out-of-scope definitions, and propagation
requirement) are in `knowledge/scope-expansion-gate.md`. Read it before dispatching
any developer.

Summary: BEFORE editing any file or line not in the approved plan, stop, list
proposed out-of-scope changes as numbered items, present to the user for per-item
approval, and wait before resuming. If no out-of-scope changes are proposed,
proceed.

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

## Phase 1.5: Signature Verification (Autonomous Mode Only — activated by Phase 1)

Phase 1 routes here when `--autonomous` is present in `$ARGUMENTS`. In standard
mode, Phase 1 skips this phase entirely and proceeds to Phase 2.

Before dispatching any developer, verify every external procedure
signature using the strongest available AL symbol evidence.

Preferred evidence order:
1. `AL LSP` through active harness/adapter semantic operations:
   go-to-definition, find-references, document symbols, and
   hover/type information.
2. `AL MCP` through `al-mcp-server`, using the appropriate MCP
   query:

```text
al_get_object_definition — for base objects being extended:
  confirms field names, IDs, and trigger signatures

al_search_object_members — for event signatures and methods:
  locates exact event publisher signatures with var parameters

al_find_references — to detect existing similar extensions:
  avoids duplicate subscriber registration
```

3. `text search` through scoped `rg` only when no semantic provider
   is available. Label it as weaker evidence and include file:line
   references.

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
- Evidence source: [AL LSP / AL MCP / text search]
- Evidence: [go-to-definition result / al_search_object_members / file:line]
- Verified: [ISO timestamp]

### NOT VERIFIED: [ProcedureName]
- Evidence source: unverified
- Reason: [not found in semantic provider / ambiguous match / no provider available]
- Risk: Developer must not guess this signature
```

A procedure is "required" if it is explicitly referenced in the approved solution plan
and the assigned developer task must call it. If any required external procedure is
NOT VERIFIED, do not spawn developers for code that depends on that signature.
Stop and report the unverified required signature to the orchestrator or user.

Only carry a NOT VERIFIED item forward as a documented risk when the
procedure is explicitly optional or no assigned developer task depends on
calling it. If an optional item is carried forward, include this block in the
developer spawn prompt:

```text
Optional unverified signatures — do NOT guess these:
- [ProcedureName]: [reason not verified; not required for assigned task]
STOP and report back if the implementation would need to call this procedure.
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

See `knowledge/developer-invocation-patterns.md` for dispatcher consistency
across all developer spawns.

### Phase 3.0: Write Scope Boundary Document

Before spawning developers, write
`.dev/$(date +%Y-%m-%d)-al-dev-develop-scope.md` with:
- `Files in scope`
- `Permitted change types per file`
- `Files explicitly out of scope`
- `Escalation rule if an out-of-scope edit appears necessary`

Reviewers validate the implementation against this scope file,
not memory alone.

See `knowledge/al-dev-develop-spawn-prompt.md` for the developer spawn prompt template and instructions for instantiating it per module assignment.

For each module in the solution plan:
1. Gather module-specific context (objects, ID range, symbols)
2. Instantiate the spawn prompt template
3. Detect test plan: `ls .dev/*-al-dev-test-test-plan.md`
4. Dispatch al-dev-developer-tdd (if test plan) or al-dev-developer-traditional (if no test plan)

Before spawning each developer, check for a test plan and route to
the matching specialized agent:

1. Check for test plan:

   ```bash
   TEST_PLAN=$(ls .dev/*-al-dev-test-test-plan.md 2>/dev/null | sort | tail -1)
   ```

2. If a test plan exists, spawn **al-dev-developer-tdd**:

   ```text
   Agent: al-dev-shared:al-dev-developer-tdd
   ```

   Include in the prompt: reference to the test plan, TDD cycle
   expectations (RED-GREEN-REFACTOR), and the `TDD_CYCLE_GATE` approval
   gates after each phase.

3. If no test plan exists, spawn **al-dev-developer-traditional**:

   ```text
   Agent: al-dev-shared:al-dev-developer-traditional
   ```

   Include in the prompt: the traditional build-verify workflow and
   compilation after each file or logical group.

If parallel, spawn all developers at once (each routed per the test-plan
check above).

Dispatch context reference: `knowledge/developer-invocation-patterns.md`
(Context 1: Full Scope Implementation).

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

## Phase 4.5: Static Validation (Autonomous Mode Only — activated by Phase 1)

Phase 1 routes here when `--autonomous` is present in `$ARGUMENTS`. In standard
mode, Phase 1 skips this phase entirely and proceeds to review dispatch.

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
proceeding to review.

---

## Phase 4 Output: Handoff to /al-dev-review-develop

After Phase 4 (or Phase 4.5 if autonomous), all developers have completed implementation:

**Handoff artifact:**
`.dev/$(date +%Y-%m-%d)-al-dev-develop-phase4-handoff.md`

This document is created at Phase 4 completion and includes:
- List of developers and their module assignments
- File ownership verification (no overlap)
- Naming consistency status
- Object ID verification results
- Status: Ready for review team dispatch
- References to scope document and checklist artifacts

**Next step:** Dispatch to `/al-dev-review-develop` only after reading the current
Phase 4 handoff artifact and confirming it satisfies the `al-dev-develop`
success evidence in `knowledge/artifact-contracts.md`.
