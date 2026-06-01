# Developer Invocation Patterns

Reference document for the three contexts in which `al-dev-developer` is spawned.

## Context 1: Full Scope Implementation (al-dev-develop Phase 4)

**Caller:** `/al-dev-develop` (Phase 4: Developer Dispatch and Implementation)

**Trigger:** User has approved a solution plan and /al-dev-develop is
orchestrating parallel developer agents to implement it.

**Developer is responsible for:**

- Reading the full solution plan (`.dev/*-al-dev-plan-solution-plan.md`)
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
- Code ready for review panel (al-dev-security-reviewer,
  al-dev-expert-reviewer, al-dev-performance-reviewer)

---

## Context 2: Trivial Direct Fix (al-dev-fix Task 3–5)

**Caller:** `/al-dev-fix` (Steps 3–5: Non-Trivial Implementation Path)

**Trigger:** User approved a trivial fix scope (single file, obvious
implementation), and /al-dev-fix is dispatching a developer for quick
implementation.

**Developer is responsible for:**

- Reading the fix scope and requirements (from /al-dev-fix context)
- Implementing a single, focused change
- No full solution plan; minimal context gathering
- Direct implementation without TDD (test plan typically absent for trivial fixes)
- Compiling once at the end (or immediately if change is complex)
- Returning: files changed, verification that fix resolves the stated issue

**Dispatch prompt structure:**

- Issue description and fix scope
- Single file path or object name
- AL symbol preflight evidence (focused on the changed object)
- Implementation constraints from /al-dev-fix scope check
- Code quality standards (same as Context 1)
- Traditional workflow assumed (no test plan)

**Success evidence:**

- File modified and compiling cleanly
- Fix verified to resolve the stated issue
- Code ready for optional code review (developer quality check, not
  multi-reviewer panel)

---

## Context 3: Error Correction (al-dev-review-develop Phase 2, Autonomous Mode)

**Caller:** `/al-dev-review-develop` (Phase 2: Compile Verification,
--autonomous mode only)

**Trigger:** Compilation has errors after Phase 4 implementation, and
/al-dev-review-develop --autonomous is dispatching a developer to fix them
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

---

## Model Parameter Routing

The `model` parameter in Agent tool invocations can override agent-level
defaults at dispatch time. This enables complexity-aware routing without
modifying agent files.

### When to route Haiku vs. Sonnet

**Route `model: claude-haiku-4-5`** when:

- Task is TRIVIAL (single file, obvious fix, no judgment required)
- Decision tree is linear (no branching based on symbol analysis)
- Context is minimal (one file, one function, one issue)

**Route `model: claude-sonnet-4-6`** when:

- Task is SIMPLE or COMPLEX (requires analysis, planning, multi-step reasoning)
- Code change crosses file boundaries or affects multiple objects
- Risk assessment needed (performance, security, patterns)

### Example: Conditional routing in spawning skill

```text
## Determine developer model based on complexity

IF scope crosses 2+ files OR symbols unknown:
  model = claude-sonnet-4-6
ELSE IF scope is 1 file AND symbols are known:
  model = claude-haiku-4-5
ELSE:
  model = claude-sonnet-4-6  (default to safer choice)

Agent(
  agent: al-dev-shared:al-dev-developer-tdd
  model: <model>
  description: "Implement TDD workflow"
  prompt: "...dispatch prompt..."
)
```

### Current implementation status

- `/al-dev-fix`: Uses architect for non-trivial path (implicit sonnet
  upgrade via architect dispatch)
- `/al-dev-develop`: Always uses developer; complexity routing not yet wired
- `/al-dev-review-develop`: Always uses developer; complexity routing not yet wired

This pattern is reserved for future enhancement; current spawning skills
do not yet implement conditional routing.

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
Agent: al-dev-shared:al-dev-developer-tdd (test plan present)
Agent: al-dev-shared:al-dev-developer-traditional (no test plan)

For Context 3 (error correction): always use al-dev-developer-traditional.

Context: [CONTEXT 1 | CONTEXT 2 | CONTEXT 3]

[Context-specific preamble — see Context 1/2/3 above]

Solution Plan / Scope: [reference to .dev/*.md or direct scope statement]

Module Assignment / Object List: [specific objects to implement or fix]

Implementation Notes:
- [Key pattern from solution plan or /al-dev-fix scope]
- [AL symbol evidence from preflight or prior search]
- [Code quality standards: labels for errors, symbol preflight, compile
  after each file]

[Append SYMBOL_PREFLIGHT_GATE requirement]

Return: files changed, session log entry, any blockers or scope clarifications.
```
