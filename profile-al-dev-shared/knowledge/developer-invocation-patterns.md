# Developer Invocation Patterns

Reference document for the three contexts in which `al-dev-developer` is spawned.

## Context 1: Full Scope Implementation (develop-orchestrate Phase 3)

**Caller:** `/develop-orchestrate` (Phase 3: Developer Dispatch and Implementation)

**Trigger:** User has approved a solution plan and /develop-orchestrate is
orchestrating parallel developer agents to implement it.

**Developer is responsible for:**

- Reading the full solution plan (`.dev/*-plan-solution-plan.md`)
- Implementing a specific module/component assignment
- TDD workflow if test plan exists; traditional workflow otherwise
- Scope Expansion Gate: stopping before out-of-scope edits for user approval
- Compiling after each file or logical group
- Recording session log in `.dev/session-log.md`

**Dispatch prompt structure:**

- Solution plan reference + module assignment
- Object list and object ID range
- AL symbol preflight evidence (AL LSP, AL MCP, text search)
- Scope Expansion Gate rules
- Code quality standards reference
- TDD vs. traditional path decision (test plan present?)

**Success evidence:**

- All assigned objects implemented and compiling cleanly
- Session log updated
- Code ready for review panel (security-reviewer,

  al-pattern-reviewer, performance-reviewer)

**Routing decision:**

```text
If a test plan file exists (.dev/*-test-test-plan.md is present and non-empty):
  spawn al-dev-shared:developer-tdd
  Include in prompt: TDD cycle expectations (RED-GREEN-REFACTOR),
    TDD_CYCLE_GATE approval gates after each phase
Else:
  spawn al-dev-shared:developer-traditional
  Include in prompt: traditional build-verify workflow,
    compilation after each file or logical group
```

**Example spawn block (Context 1 — TDD path):**

```text
Agent: al-dev-shared:developer-tdd
Prompt:
  Implement the following module from the approved solution plan.

  Solution plan: [paste .dev/*-plan-solution-plan.md]
  Module assignment: [paste the assigned module/component section]
  Test plan: [paste .dev/*-test-test-plan.md]

  Follow the TDD cycle: RED → GREEN → REFACTOR for each requirement.
  Stop at the TDD_CYCLE_GATE after each phase for approval before proceeding.
  Compile after each file or logical group. Record progress in .dev/session-log.md.
```

**Example spawn block (Context 1 — Traditional path):**

```text
Agent: al-dev-shared:developer-traditional
Prompt:
  Implement the following module from the approved solution plan.

  Solution plan: [paste .dev/*-plan-solution-plan.md]
  Module assignment: [paste the assigned module/component section]

  Follow the traditional build-verify workflow.
  Compile after each file or logical group. Record progress in .dev/session-log.md.
```

---

## Context 2: Trivial Direct Fix (fix Task 3–5)

**Caller:** `/fix` (Steps 3–5: Non-Trivial Implementation Path)

**Trigger:** User approved a trivial fix scope (single file, obvious
implementation), and /fix is dispatching a developer for quick
implementation.

**Developer is responsible for:**

- Reading the fix scope and requirements (from /fix context)
- Implementing a single, focused change
- No full solution plan; minimal context gathering
- Direct implementation without TDD (test plan typically absent for trivial fixes)
- Compiling once at the end (or immediately if change is complex)
- Returning: files changed, verification that fix resolves the stated issue

**Dispatch prompt structure:**

- Issue description and fix scope
- Single file path or object name
- AL symbol preflight evidence (focused on the changed object)
- Implementation constraints from /fix scope check
- Code quality standards (same as Context 1)
- Traditional workflow assumed (no test plan)

**Success evidence:**

- File modified and compiling cleanly
- Fix verified to resolve the stated issue
- Code ready for optional code review (developer quality check, not

  multi-reviewer panel)

**Routing decision:**

Trivial fixes typically have no test plan — route to `developer-traditional`.
If a test plan is present, route to `developer-tdd` (rare for trivial fixes).

**Example spawn block (Context 2 — Traditional path):**

```text
Agent: al-dev-shared:developer-traditional
Prompt:
  Fix [specific issue] in [file path].
  Issue: [description from fix context]
  Expected fix: [what needs to change]
  Verify the fix compiles. Keep it minimal — only change what is necessary.
  Return: files changed and confirmation that fix resolves the stated issue.
```

---

## Context 3: Error Correction (review-develop Phase 2, Autonomous Mode)

**Caller:** `/review-develop` (Phase 2: Compile Verification,
--autonomous mode only)

**Trigger:** Compilation has errors after Phase 4 implementation, and
/review-develop --autonomous is dispatching a developer to fix them
before the review panel runs.

**Developer is responsible for:**

- Reading `.dev/compile-errors.log` and identifying root causes
- Applying minimal, targeted fixes
- Re-compiling after each fix (5-cycle limit)
- Returning: files changed, errors resolved (or errors for escalation)

**Dispatch prompt structure:**

- Compile error log reference
- Phase 4 handoff context (what was implemented)
- Minimal scope: only fix errors, do not refactor
- AL symbol evidence for changed objects
- Compile-fix-compile cycle discipline
- Stop after 5 failed attempts (escalate to user)

**Success evidence:**

- Zero `error AL` lines in `.dev/compile-errors.log`
- Fixes are minimal (no scope expansion)
- Code ready for review panel

**Routing decision:**

Error correction targets known failing cases from a code review. Route to
`developer-traditional` unless a regression test plan was written
during the review phase.

**Example spawn block (Context 3 — Traditional path):**

```text
Agent: al-dev-shared:developer-traditional
Prompt:
  Apply the following corrections from the code review.

  Code review: [paste .dev/*-develop-code-review.md]
  Corrections required: [paste the specific correction list]

  Fix each listed item. Compile after each correction. Do not change code
  outside the review-flagged areas. Return: corrections applied and compile result.
```

---

## Model Parameter Routing

The `model` parameter in Agent tool invocations can override agent-level
defaults at dispatch time. This enables complexity-aware routing without
modifying agent files.

### When to route Haiku vs. Sonnet

**Route `model: claude-haiku-4-5`** when:

- Task is TRIVIAL (single file, obvious fix, symbol locations already known)
- Decision tree is linear (no branching based on symbol analysis)
- Context is minimal (one file, one function, one issue)

**Route `model: claude-sonnet-4-6`** when:

- Task is SIMPLE or COMPLEX (requires analysis, planning, multi-step reasoning)
- Code change crosses file boundaries or affects multiple objects
- Risk assessment needed (performance, security, patterns)

Note: The MEDIUM tier also routes to sonnet. The haiku/sonnet boundary
aligns with single-file/multi-file scope, not the complexity taxonomy.
See workflow-routing.md for the full tiers (TRIVIAL/SIMPLE/MEDIUM/COMPLEX).

### Example: Conditional routing in spawning skill

When a spawning skill needs to dispatch a developer agent, the `model` parameter can be selected at dispatch time based on task complexity and scope — rather than using the agent's default model for all invocations.

Conditional routing applies when a spawning skill has classified the incoming task using the TRIVIAL/SIMPLE/MEDIUM/COMPLEX taxonomy (see `workflow-routing.md`) and needs to select a model for the developer spawn. The decision criteria are straightforward: TRIVIAL tasks route to `claude-haiku-4-5` (single file, all symbols known, no scope expansion risk), while MEDIUM and COMPLEX tasks route to `claude-sonnet-4-6` (multi-file, symbol verification required, or integration risk present). SIMPLE tasks default to sonnet for safety unless symbols are fully pre-verified. The spawning skill must make this choice explicitly at dispatch time because the agent's declared model can be overridden via the `model` parameter — it cannot be changed mid-run.

```text
## Determine developer model based on complexity

IF scope crosses 2+ files OR symbols unknown:
  model = claude-sonnet-4-6
ELSE IF scope is 1 file AND symbols are known:
  model = claude-haiku-4-5
ELSE:
  model = claude-sonnet-4-6  (default to safer choice)

Agent(
  agent: al-dev-shared:al-dev-developer-<variant>
  # variant selection is separate (see Context 2)
  model: <model>
  description: "Implement development workflow"
  prompt: "...dispatch prompt..."
)

# Note: <variant> (tdd vs. traditional) is determined by test plan presence.
# <model> (haiku vs. sonnet) is determined by complexity tier and scope.
# Both selections are orthogonal.
```

#### How to measure complexity tier

The model routing decision hinges on objective scope measures. Use this algorithm:

**Step 1: Count affected files**

```python
affected_files = count_files_in_scope(assignment)
```

- **1 file** → candidate for TRIVIAL
- **2–3 files** → SIMPLE or candidate for conditional haiku if homogeneous
- **4+ files** → MEDIUM or COMPLEX

**Step 2: Symbol verification**

For each symbol referenced in the implementation:

```python
symbols_unverified = []
for symbol in required_symbols:
  evidence_source = check_al_lsp() or check_al_mcp() or check_text_search()
  if not evidence_source:
    symbols_unverified.append(symbol)

if symbols_unverified:
  model = claude-sonnet-4-6  # Must verify before proceeding
else:
  model = <candidate_from_step_1>
```

See `knowledge/al-symbol-pre-flight.md` for preflight checklist.

**Step 3: Scope expansion risk assessment**

Check for signals that scope may expand mid-task:

```python
scope_risks = [
  "Touches validation or integration logic",
  "Requires changes to multiple subsystems",
  "Affects external APIs or notifications",
  "References symbols from multiple modules"
]

if any(risk in assignment for risk in scope_risks):
  model = claude-sonnet-4-6  # Higher risk → sonnet for safety
```

**Concrete tier mapping:**

| Tier | Files | Symbols | Risk | Model |
|------|-------|---------|------|-------|
| TRIVIAL | 1 | all known via LSP | none | haiku |
| SIMPLE | 2–3 | all known | low | haiku or sonnet (prefer sonnet for safety) |
| MEDIUM | 4–8 | mostly known | medium | sonnet |
| COMPLEX | 8+ | mixed/unknown | high | sonnet |

#### Real example: Conditional spawn logic

The two examples below illustrate the extremes of the routing decision: Example 1 shows a genuinely TRIVIAL scope where haiku is appropriate (single file, pre-verified symbol, no integration risk), while Example 2 shows a MEDIUM scope where sonnet is required (multiple files, validation logic, risk signals present).

**Example 1: Haiku dispatch (TRIVIAL scope)**

```python
# Fix: Change field caption from "Amount" to "Invoice Amount" in Codeunit 50101

scope = {
  "files": ["SalesInvoiceExt.al"],
  "symbols": ["MyTableExt"],  # Verified via AL LSP in prior phase
  "changes": ["update field caption"],
  "risk_signals": []
}

# Decision logic
if len(scope["files"]) == 1 and scope["risk_signals"] == []:
  model = "claude-haiku-4-5"
  context = "Single file, obvious change, no scope expansion risk"

# Spawn
agent = spawn_developer(
  agent: al-dev-shared:developer-traditional,
  model: claude-haiku-4-5,
  prompt: f"Fix: {description}. File: {scope['files'][0]}. Change: {scope['changes'][0]}"
)
```

**Example 2: Sonnet dispatch (MEDIUM scope)**

```python
# Implement: Add credit limit validation across sales orders
# (requires event subscriber, validation codeunit, and page UI changes)

scope = {
  "files": ["SalesOrderExt.al", "CreditValidationMgt.Codeunit.al", "SalesOrderPageExt.al"],
  "symbols": ["SalesHeader", "SalesLine", "Customer"],  # Some verified, some require MCP
  "changes": ["event subscriber", "validation logic", "page warning control"],
  "risk_signals": [
    "Touches validation logic",
    "Affects multiple subsystems (schema, UI, logic)"
  ]
}

# Decision logic
if len(scope["files"]) >= 3 or any(risk in scope["risk_signals"]):
  model = "claude-sonnet-4-6"
  context = "Multi-file scope + validation integration = sonnet required"

# Spawn
agent = spawn_developer(
  agent: al-dev-shared:developer-traditional,
  model: claude-sonnet-4-6,
  prompt: f"Implement credit limit validation. Files: {scope['files']}. Pattern: existing validation codeunit referenced. Stop before out-of-scope edits."
)
```

Together, these examples instantiate the decision logic from the preceding subsection: the scope object's `files` count and `risk_signals` list map directly onto the tier table, and the resulting `model` value is passed unchanged to the Agent dispatch call.

#### Applicable contexts

Not all three spawning contexts are candidates for conditional routing:

**Context 1 (Full Scope Implementation)** — ✅ **PRIMARY CANDIDATE**

Conditional routing is most useful here because:

- Solution plan contains detailed scope; file list and complexity are known
- Developer is implementing a pre-planned module, not exploratory work
- Risk is contained: architect has already decided on approach
- Example: "Implement the CreditValidationMgt module from the approved plan"

**Context 2 (Trivial Direct Fix)** — ⚠️ **CONSTRAINED CANDIDATE**

Conditional routing is possible but less valuable because:

- Trivial fixes are already pre-filtered to single-file scope
- If the fix proves non-trivial mid-task, /fix escalates to architect
- Conditional routing here mostly avoids unnecessary sonnet overhead for obvious fixes

**Context 3 (Error Correction)** — ❌ **NOT APPLICABLE**

Do not apply conditional routing here because:

- Error correction is reactive (fixing failures, not executing a plan)
- Scope is determined by the error list, not architectural decisions
- The developer must fully understand the context of the failure
- Always use sonnet for error correction to ensure correctness

**Recommendation:** Wire Context 1 first. Context 2 is lower priority; Context 3 should always use sonnet.

Quick reference — context → model routing:

| Context | Apply conditional routing? | Model at dispatch |
| ------- | ------------------------- | ----------------- |
| Context 1 — Full Scope Implementation | ✅ Primary candidate | haiku (1 file, symbols known) or sonnet (SIMPLE+) |
| Context 2 — Trivial Direct Fix | ⚠️ Optional | haiku (trivial pre-filtered) or sonnet (if risk signals present) |
| Context 3 — Error Correction | ❌ No — always sonnet | sonnet unconditionally |

```text
# Dispatch-time model selection (apply to Context 1 and 2 only):
IF context == 3:
  model = claude-sonnet-4-6
ELSE IF scope.files == 1 AND scope.risk_signals == [] AND scope.symbols_unverified == []:
  model = claude-haiku-4-5
ELSE:
  model = claude-sonnet-4-6
```

See the tier table and concrete examples in the "Real example" subsection above.

#### Safety: mid-task scope expansion

A haiku developer may discover mid-task that scope expands beyond single-file expectations. Provide clear escalation guidance:

**If scope expansion is detected:**

```text
You started with 1 file, but the fix requires changes to [X, Y, Z] files.
This crosses the haiku/sonnet boundary.

ACTION: Do not continue. Halt implementation and report the scope expansion.

Options for developer:
1. Return: "Scope expanded to {files}. Requires sonnet model. Return to spawning skill for restart."
2. (If spawning skill supports it) Request mid-session model swap: "Requesting upgrade from haiku to sonnet for scope {new_scope}."

Examples of mid-task expansion:
- Started: "Fix field caption in one extension" (1 file)
  Discovered: "Must also update validation in base table event subscriber" (2+ files)
  → Escalate

- Started: "Add single field to page" (1 file)
  Discovered: "Field requires new table relation to Customer" (2+ files)
  → Escalate

- Started: "Update variable name for consistency" (1 file, 1 scope)
  Discovered: "Variable also used in 4 other objects; refactoring required" (5+ files)
  → Escalate
```

**Spawning skill responsibility:**

The skill that spawned the developer should:

1. Provide a clear halt condition in the dispatch prompt:

   ```text
   "Stop before implementing changes outside your assigned scope.
    If you discover multi-file scope, return a scope-expansion summary
    instead of implementing further. Do not attempt multi-file changes."
   ```

2. Check the developer's return message for scope-expansion indicators.

3. If scope expanded: either restart the developer with sonnet + expanded scope, or
   return to user for approval of new scope.

Example restart dispatch:

```python
# Developer reported scope expansion
prior_scope = ["SalesOrderExt.al"]
expanded_scope = ["SalesOrderExt.al", "SalesHeaderExt.al", "PostingMgt.Codeunit.al"]

# Restart with sonnet
agent = spawn_developer(
  agent: al-dev-shared:developer-traditional,
  model: claude-sonnet-4-6,  # Upgraded from haiku
  context: "Previous scope was single-file. Scope has expanded; restarting with full context.",
  prompt: f"Implement across {expanded_scope}. Original assignment: {original_assignment}. Expand to handle: {expanded_changes}."
)
```

### Current implementation status

- `/fix`: Has explicit conditional routing on the *architect* spawn
  (sonnet for SIMPLE, opus for COMPLEX). Developer routing is not yet
  conditional — the spawn does not vary model by scope complexity.

- `/develop-orchestrate`: Always uses developer; complexity routing not yet wired
- `/review-develop`: Always uses developer; complexity routing not yet wired

This pattern is reserved for future enhancement. When wired, it will apply to:

- Context 1 (`/develop-orchestrate`, Phase 3 dispatch) — model selection for
  developer spawn
- Context 3 (`/review-develop`, Phase 2 dispatch) — model selection
  for developer spawn

No spawning skills currently use conditional developer routing; the
architect in `/fix` has explicit routing already wired.

---

## Shared Pattern: SYMBOL_PREFLIGHT_GATE

All three contexts enforce the symbol preflight checklist (`knowledge/al-symbol-pre-flight.md`).

```text
SYMBOL_PREFLIGHT_GATE:

- Summary required before implementation
- Evidence source named per symbol
- Stop if any required symbol remains unverified

```

Developer must:

1. Report pre-flight summary before writing any AL code
2. Name the evidence source for each required symbol (AL LSP, AL MCP,

   text search, or unverified)

3. **Stop before implementation if any required symbol remains

   unverified**

When dispatching in any context, include:

- `SYMBOL_PREFLIGHT_GATE: pre-flight summary required before implementation starts`

---

## Dispatch Prompt Template

Use this structure when spawning a developer agent from any of the three
contexts. Note: the bare agent name below is a placeholder — resolve it
based on test-plan presence:

```text
Agent: al-dev-shared:developer-tdd (test plan present)
Agent: al-dev-shared:developer-traditional (no test plan)

For Context 3 (error correction): always use developer-traditional.

Context: [CONTEXT 1 | CONTEXT 2 | CONTEXT 3]

[Context-specific preamble — see Context 1/2/3 above]

Solution Plan / Scope: [reference to .dev/*.md or direct scope statement]

Module Assignment / Object List: [specific objects to implement or fix]

Implementation Notes:

- [Key pattern from solution plan or /fix scope]
- [AL symbol evidence from preflight or prior search]
- [Code quality standards: labels for errors, symbol preflight, compile

  after each file]
- [Delegated-Task Scope Pack: in-scope objects/files, in-scope change
  description, out-of-scope rule, and halt-and-report contract — see
  `knowledge/scope-expansion-gate.md`]

[Append SYMBOL_PREFLIGHT_GATE requirement]

Return: files changed, session log entry, any blockers or scope clarifications.
```
