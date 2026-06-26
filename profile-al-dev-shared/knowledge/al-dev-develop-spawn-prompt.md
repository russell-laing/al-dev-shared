# al-dev-develop-orchestrate Developer Spawn Prompt

This document defines the structured prompt template used to dispatch
developer agents during `al-dev-develop-orchestrate` Phase 3 (Spawn Developers).
The orchestrating skill instantiates this template once per module
assignment so that every spawned developer receives consistent scope,
standards, and gate rules.

The spawn prompt is canonical here; the skill references this file rather
than embedding the full prompt inline. Use
`knowledge/developer-invocation-patterns.md` for the broader dispatch
consistency rules that sit around this template.

## Prompt Structure

Each instantiated developer prompt must carry the following elements:

- **Module assignment** — the named module from the Phase 2 partition.
- **Object list** — the concrete objects (tables, pages, codeunits,
  enums, extensions) the developer owns.
- **Object ID range** — the assigned range from the solution plan; no
  overlap with other developers.
- **Naming conventions** — the project prefix and naming rules (from
  `.dev/project-context.md` or the plan).
- **AL code patterns** — the standards in `knowledge/al-developer-patterns.md`
  (SetLoadFields, FieldCaption error handling, dependency injection,
  events for extensibility).
- **Scope Expansion Gate rules** — the governance checkpoint from
  `knowledge/scope-expansion-gate.md` that blocks out-of-scope edits. Carry the
  Delegated-Task Scope Pack (in-scope objects/files, in-scope change
  description, out-of-scope rule, halt-and-report contract) defined in that
  file's "Delegated-Task Scope Pack" section.
- **Symbol preflight evidence** — verified signatures and field/event
  evidence collected during planning, plus the preflight checklist from
  `knowledge/al-symbol-pre-flight.md`.
- **Test plan indication** — whether a test plan exists, which determines
  agent routing and workflow.

## Template — Dispatch routing based on test plan

Check for a test plan before instantiating the prompt:

```bash
TEST_PLAN=$(ls .dev/*-al-dev-test-test-plan.md 2>/dev/null | sort | tail -1)
[ -n "$TEST_PLAN" ] && [ -s "$TEST_PLAN" ]
```

Choose the matching path below. Do not emit both — select one and
substitute the bracketed placeholders before dispatching.

---

### Common dispatched prompt content

Each selected route must include this common instruction body immediately after
the route-specific `Agent:` line:

```text
Implement [module name] from the latest solution plan
(.dev/*-al-dev-plan-solution-plan.md).

Your assigned objects:
- [Object list from the Phase 2 partition]

Object IDs: [assigned range from plan]
Naming prefix: [from plan or project-context.md]
Project patterns: [from project-context.md if available]

Shared standards:
Follow `knowledge/al-developer-shared-standards.md`.

Scope expansion gate:
Apply the full gate procedure from `knowledge/scope-expansion-gate.md`.
Before editing any file or line not in the plan: stop, list proposed
changes as numbered items, present to the user, and wait for per-item
approval. Do NOT continue writing code until confirmed. Do NOT silently
fix lint warnings, deprecated APIs, or unrelated issues not named in
the plan.

Commit boundary:
Do NOT run git commit. Your role is to implement and verify compilation
only. Commits are handled separately by /al-dev-commit after user
approval.
```

---

**If a non-empty test plan exists at `$TEST_PLAN` — use `al-dev-developer-tdd`:**

```text
Agent: al-dev-shared:al-dev-developer-tdd

Include the common dispatched prompt content above.

Route-specific workflow:
- Test plan: [path from $TEST_PLAN]
- Workflow: TDD cycle (RED-GREEN-REFACTOR)
- Gate: Apply `TDD_CYCLE_GATE` approval gates after each phase
- Completion report:
  - Pre-flight summary reported before code was written
  - Compilation verified for the assigned module
  - Any out-of-scope proposals surfaced through the Scope Expansion Gate
- Final ownership note: report files created/modified for Phase 3 ownership verification
```

---

**If no non-empty test plan exists at `$TEST_PLAN` — use `al-dev-developer-traditional`:**

```text
Agent: al-dev-shared:al-dev-developer-traditional

Include the common dispatched prompt content above.

Route-specific workflow:
- Workflow: Traditional build-verify
- Gate: compile after each file or logical group to catch errors early
- Completion report:
  - Pre-flight summary reported before code was written
  - Compilation verified for the assigned module
  - Any out-of-scope proposals surfaced through the Scope Expansion Gate
- Final ownership note: report files created/modified for Phase 4 ownership verification
```

## Usage Notes (Phase 3)

1. **Gather context** — read the solution plan,
   the latest `.dev/*-al-dev-develop-checklist.md`, the latest
   `.dev/*-al-dev-develop-scope.md`, and any planning symbol evidence.
2. **Instantiate the template** once per module assignment, filling all
   placeholders from the partition, plan, and project context.
3. **Detect the test plan** and route the agent:

   ```bash
   TEST_PLAN=$(ls .dev/*-al-dev-test-test-plan.md 2>/dev/null | sort | tail -1)
   [ -n "$TEST_PLAN" ] && [ -s "$TEST_PLAN" ]
   ```

   - If a non-empty test plan exists, route to `al-dev-developer-tdd`
     and include TDD cycle expectations and the `TDD_CYCLE_GATE`
     approval gates.
   - If no non-empty test plan exists, route to
     `al-dev-developer-traditional` and include the traditional
     build-verify workflow.
4. **Dispatch** all developers (in parallel where modules own disjoint
   files), each with its instantiated prompt. See
   `knowledge/developer-invocation-patterns.md` (Context 1: Full Scope
   Implementation) for dispatcher consistency.
