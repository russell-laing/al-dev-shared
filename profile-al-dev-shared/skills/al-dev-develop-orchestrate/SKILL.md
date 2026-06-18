---
name: al-dev-develop-orchestrate
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
`al-dev-develop-orchestrate` has been produced and read for the current run.

When shell search or structured-file inspection is required, prefer `rg` and
`jq` before falling back to broader shell text processing.

## Scope Expansion Gate

The full gate rules (procedure, in-scope/out-of-scope definitions, and propagation
requirement) are in `knowledge/scope-expansion-gate.md`. Read it before dispatching
any developer.

Summary: BEFORE editing any file or line not in the approved plan, stop, list
proposed out-of-scope changes as numbered items, present to the user for per-item
approval, and wait before resuming. If no out-of-scope changes are proposed,
proceed.

## Phase 0: Initialize and Resume

Per the Phase 0 Read Protocol in `knowledge/workflow-resilience.md`.

**Purpose:** Check for existing progress and establish the resume pack that
`/al-dev-develop-orchestrate` maintains through the run so context compaction and session
hand-off do not require a full re-read of the solution plan.

**Resume pack artifacts:**

- `.dev/progress.md` — latest phase checkpoint, overwritten each phase
- `.dev/$(date +%Y-%m-%d)-al-dev-develop-progress.md` — dated session snapshot
- `.dev/$(date +%Y-%m-%d)-al-dev-develop-checklist.md` — implementation checklist extracted from plan
- `.dev/$(date +%Y-%m-%d)-al-dev-develop-scope.md` — file-level scope contract

At fresh start:

1. Create or overwrite `.dev/progress.md` per
   `knowledge/workflow-resilience.md`
2. Create the dated progress snapshot for the current run; after writing
   both `.dev/progress.md` and the dated snapshot, emit a brief
   confirmation: "Progress checkpoint written → .dev/progress.md"
3. Continue building the rest of the resume pack in later phases:
   - Phase 2 writes the checklist artifact
   - Phase 2 writes the scope artifact
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

## Phase 1: Read Context & Route Mode

**Mode detection:**
Check `$ARGUMENTS` for `--autonomous`. Set `AUTONOMOUS_MODE=true` if found;
otherwise `AUTONOMOUS_MODE=false`. This value applies for the entire run:

- After Step 3 below, run signature verification (inlined below)
- After Phase 4 (Verify on Completion), run static validation (inlined in Phase 4)
- Signature verification and static validation gates must pass before proceeding to review dispatch

If `$ARGUMENTS` is provided, treat it as a scope override
(e.g. "data-model-only", "UI layer", "integration module").
Apply that scope when partitioning work in Phase 2 — skip
modules outside the specified scope.

### Step 1: Read Solution Plan

1. Read the latest solution plan:
   `$(ls .dev/*-al-dev-plan-solution-plan.md 2>/dev/null \
   | sort | tail -1)`
2. Read `.dev/project-context.md` if it exists; if absent, degrade to a minimal inferred context per `knowledge/companion-context-ownership.md` (the `al-dev-init-context` producer is a companion-layer capability) — do not block the build
3. Identify:
   - Objects to create (tables, pages, codeunits, enums)
   - BC integration points
   - Validation rules
   - Testability requirements
   - Object ID ranges

### Step 2: Signature Verification (Autonomous Mode Only)

If `AUTONOMOUS_MODE=true`, before dispatching any developer,
verify every external procedure signature using the strongest available AL symbol evidence.

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

A procedure is "required" if it is named in the approved solution plan's
**Procedures/Triggers** section (or equivalent implementation-step) and the assigned
developer task must call it. Acceptance criteria alone do not qualify.

**Decision tree if any required external procedure is NOT VERIFIED:**

1. Stop developer spawn immediately — do not proceed to Phase 3
2. Generate report block with exact procedure name and reason for non-verification:

   ```text
   SIGNATURE_VERIFICATION_FAILED
   
   Unverified required signature: [ProcedureName]
   Evidence source attempted: [AL LSP / AL MCP / text search]
   Reason: [not found / ambiguous match / no provider available]
   
   Impact: This procedure is required for the implementation plan.
   Cannot proceed without verification.
   
   Resolution required: 
   - Verify the procedure exists and signature is correct
   - Consult BC documentation or base app source
   - Confirm exact parameter names and types (including var modifiers)
   - Rerun /al-dev-develop-orchestrate with --autonomous after verification
   ```

3. Escalate to user with this report
4. Do NOT spawn developers until signature is verified

Only carry a NOT VERIFIED item forward as a documented risk when the
procedure is explicitly optional or no assigned developer task depends on
calling it. If an optional item is carried forward, include this block in the
developer spawn prompt:

```text
Optional unverified signatures — do NOT guess these:
- [ProcedureName]: [reason not verified; not required for assigned task]
STOP and report back if the implementation would need to call this procedure.
```

If not in autonomous mode, skip this step and proceed to Phase 2.

---

## Phase 2: Partition and Prepare

Analyze the plan and partition into independent modules.
Each module must own different files — no overlap. Every in-scope file
belongs to exactly one partition: if a file spans two partition
categories (e.g. a codeunit containing both business logic and
integration subscribers), assign the whole file to a single module
owner rather than splitting it across modules.

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

### Step 1: Extract Implementation Checklist

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

### Step 2: Write Scope Boundary Document

Write `.dev/$(date +%Y-%m-%d)-al-dev-develop-scope.md` with:

- `Files in scope`
- `Permitted change types per file`
- `Files explicitly out of scope`
- `Escalation rule if an out-of-scope edit appears necessary`

Reviewers validate the implementation against this scope file,
not memory alone.

---

## Phase 3: Spawn Developers

See `knowledge/developer-invocation-patterns.md` for dispatcher consistency
across all developer spawns.

See `knowledge/al-dev-develop-spawn-prompt.md` for the developer spawn prompt template and instructions for instantiating it per module assignment.

### Developer Spawn Routing: Detailed Steps

For each module in the solution plan, execute these routing steps:

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

### Scope Expansion Decision Tree

After each developer agent completes, evaluate the reported outcome before
proceeding:

```text
IF developer agent reports "scope incomplete" in output:
  ├─ AND plan allows scope expansion: Add new tasks
  └─ AND plan forbids scope expansion: Escalate to caller

IF developer agent reports "implementation complete":
  └─ Proceed to Phase 4 (verification)

IF developer agent reports "blocking issue":
  └─ [ERROR] Return findings to caller for resolution
```

**Definitions:**

- `scope incomplete` — developer signals that the assigned module cannot be
  fully implemented without touching files or objects outside the approved plan.
- `plan allows scope expansion` — the solution plan contains an explicit
  "scope expansion permitted" marker or the user approved expansion in this
  session.
- `plan forbids scope expansion` — no expansion marker present; default
  posture is to escalate rather than assume permission.
- `blocking issue` — developer encountered an unresolvable dependency,
  missing prerequisite, or contradictory requirement that prevents progress.

Do NOT continue to Phase 4 if any developer has reported a blocking issue
or an unresolved scope-incomplete state. Resolve all open states first.

---

## Phase 4: Verify and Handoff

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

Write `.dev/progress.md` per `knowledge/workflow-resilience.md`. After
writing, emit a brief confirmation: "Progress checkpoint written →
.dev/progress.md"

### Step 2: Static Validation (Autonomous Mode Only)

If `AUTONOMOUS_MODE=true`, run these checks on all newly
created AL files before the review team is spawned. Fix CRITICAL issues by
dispatching a developer before proceeding.

### Check 1: Object Name Length

```bash
rg -rn -e \
  '^(table|page|codeunit|report|enum|interface|xmlport|query|permissionset)\s+[0-9]+\s+' \
  --glob="*.al" .
```

For each match, the object name is the identifier token immediately after the numeric ID —
the name itself, excluding any surrounding whitespace. Count only the name
token's characters (not the leading whitespace or numeric ID). Flag any name
token exceeding 30 characters as a CRITICAL issue.

### Check 2: Compile Guard Logic

```bash
rg -rn -e '#if|#else|#endif' --glob="*.al" .
```

For each `#if` directive, read the surrounding block. Verify:

- The condition matches the intended feature flag
- Every `#if` has a matching `#endif`
- The `#else` branch, if present, contains the correct fallback (correct fallback = the code under `#else` restores baseline behavior when the feature flag is disabled)

Flag any inverted condition or unmatched directive as CRITICAL.

### Check 3: Label and Message Consistency

```bash
rg -rn -m 50 -e 'label|Error\(|Message\(|FieldCaption' --glob="*.al" .
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

If not in autonomous mode, skip this step and proceed directly to handoff.

---

### Handoff to /al-dev-review-develop

After Phase 4 completes (including autonomous static validation if enabled), all developers have completed implementation:

**Handoff artifact:**
`.dev/$(date +%Y-%m-%d)-al-dev-develop-phase4-handoff.md`

This document is created at Phase 4 completion and includes:

- List of developers and their module assignments
- File ownership verification (no overlap)
- Naming consistency status
- Object ID verification results
- Status: Ready for review team dispatch
- References to scope document and checklist artifacts

**Announce the transition to the user before dispatching** (so the user does not
have to type the next skill name manually):

```text
All developers complete — running /al-dev-review-develop-preflight, then
dispatching /al-dev-review-develop once prerequisites are confirmed.
```

**Next step:**

1. Run `/al-dev-review-develop-preflight` and wait for the preflight output.
   Confirm it reports "Prerequisites: all met" before proceeding.

2. Then dispatch `/al-dev-review-develop` — only after reading the current
   Phase 4 handoff artifact and confirming it satisfies the `al-dev-develop-orchestrate`
   success evidence in `knowledge/artifact-contracts.md`.
