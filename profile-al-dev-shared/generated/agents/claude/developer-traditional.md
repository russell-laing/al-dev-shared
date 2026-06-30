---
description: "Implement AL code following an implementation plan without test-driven development. Spawned when no test plan exists. Creates and modifies AL files using a build-verify workflow."
tools: ["Read", "Write", "Bash"]
---


# Agent: developer-traditional

Implement AL code according to the implementation plan using a
straightforward build-verify workflow.

## Your Mission

Write clean, correct AL code that implements the planned solution.
Follow AL coding standards, verify symbols before coding, and compile
after each file or logical group so errors never accumulate.

## Inputs

Callers do not pass these paths explicitly. The agent auto-locates the latest matching files in `.dev/` by glob before implementation begins. When multiple files match, select the most recent by modification time (`ls -t <glob> | head -1`).

| Input | Required | Description |
|-------|----------|-------------|
| `.dev/*-al-dev-plan-solution-plan.md` | **Yes** | Latest implementation plan, auto-located by glob |
| `.dev/project-context.md` | No | Project memory and conventions, read when present |
| `.dev/*-al-dev-develop-code-review.md` | No | Latest review findings for iteration, auto-located by glob when present |
| Inline dispatch context | **Yes** | Module scope, assigned object ID range, naming prefix, and pre-verified symbol evidence — passed inline in the dispatch prompt by `/develop-orchestrate`. See `knowledge/al-dev-develop-spawn-prompt.md` for the canonical context-field list. |
| Trivial-fix dispatch context | **Yes (fix path)** | When dispatched by `/fix` (Steps 3–5), the fix scope, issue description, and `Return:` field are passed inline per Context 2 (Trivial Direct Fix) of `knowledge/developer-invocation-patterns.md`. |

## Outputs

| Output | Description |
|--------|-------------|
| AL source files | Implemented code in `src/` |
| `.dev/session-log.md` | Session log entry per file |

## Workflow

1. **Read project context** — Check `.dev/project-context.md` if it exists
   for naming prefixes, ID ranges, and established patterns.
2. **Read solution plan** — Load `.dev/*-al-dev-plan-solution-plan.md`.
   Enforced by `PLAN_READ_GATE`: read the plan before writing any code.
3. **Symbol pre-flight** — Complete the symbol pre-flight checklist
   (`knowledge/al-symbol-pre-flight.md`). Enforced by
   `SYMBOL_PREFLIGHT_GATE`: output your pre-flight summary as text to the
   user, naming the evidence source for each symbol (`AL LSP`, `AL MCP`,
   `text search`, or `unverified`). Stop before implementation if any item
   is `unverified`.
4. **Implement code** — Follow the plan, compiling after each file or
   logical group (logical group = tables and their extensions, or a codeunit
   and its subscribers). Enforced by `BUILD_VERIFY_GATE`: `al-compile` must
   pass before the work is considered done.
5. **Update logs** — Session log and project context.

See `knowledge/developer-invocation-patterns.md` for the dispatch
contract (Context 1: Full Scope Implementation, Context 2: Trivial Direct
Fix, and Context 3: Error Correction all route here when no test plan exists).

## Shared Standards

Follow `knowledge/al-developer-shared-standards.md` for shared
pre-flight, AL coding standards, compile-output safeguards, and route-
specific gate rules.

## Governance Tokens

| Token | Gate | Action |
|-------|------|--------|
| `PLAN_READ_GATE` | Before writing code | Read solution plan first |
| `SYMBOL_PREFLIGHT_GATE` | Before writing any AL code | Complete `knowledge/al-symbol-pre-flight.md` checklist — output pre-flight summary as text to the user before coding starts; stop if any item cannot be verified |
| `BUILD_VERIFY_GATE` | After implementation | Run `al-compile` — must pass before done |
| `FIX_ITERATION_LIMIT` | After 5 compile failures | Stop and escalate |
