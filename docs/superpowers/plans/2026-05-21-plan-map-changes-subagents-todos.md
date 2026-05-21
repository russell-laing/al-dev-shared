# Plan: Add Subagents and TodoWrite to plan-map-changes

## Context

The skill at `.claude/skills/plan-map-changes/SKILL.md` translates Observations
sections from plugin/agent maps into verified implementation plans. It currently
runs entirely sequentially in the main context: it reads files inline, rubber-ducks
each suggestion one-by-one, then invokes `writing-plans`.

Two structural gaps reduce its effectiveness for realistic workloads (typically
3–8 open suggestions):

1. **No parallel exploration** — Phase 2 reads multiple unrelated skill/agent files
   sequentially inside the main context window. When suggestions are independent
   (e.g., Trim agent X, Merge skills A+B, Connect pattern Y) these reads can be
   parallelized with Explore subagents, keeping rubber-duck findings out of the
   main context.

2. **No progress tracking** — Phase 2 processes N suggestions with a multi-step
   checklist per suggestion (U1–U3 + type-specific checks). Nothing instructs the
   agent to create todos, so multi-suggestion runs have no checkpoint structure.
   A missed suggestion or skipped check is invisible.

## What Changes

### Change 1: Parallel rubber-ducking via Explore subagents

Add a preamble to Phase 2 that says:

> When there are 3+ independent suggestions, invoke `superpowers:dispatching-parallel-agents`
> before starting rubber-ducking. Dispatch one Explore subagent per suggestion.
> Each agent should: read the affected file(s) in full, run U2 artifact checks,
> run the type-specific grep(s), and return a structured rubber duck record.
> Collect all records before writing any plan content.

For ≤2 suggestions (or suggestions with ordering dependencies), the sequential
inline path is fine — keep it as the fallback.

### Change 2: TodoWrite per suggestion at Phase 2 start

Add an instruction at the top of Phase 2:

> Before rubber-ducking any suggestion, create one TodoWrite todo per suggestion
> named `[Type] [Subject]`. Mark each todo in-progress when rubber-ducking begins,
> complete when the rubber duck record is written.

This gives a visible checkpoint list without changing the rubber-duck output format.

## Files to Modify

Single file: `.claude/skills/plan-map-changes/SKILL.md`

- Add ~4 lines at the very start of Phase 2 (TodoWrite instruction)
- Add ~8 lines after the TodoWrite instruction, before Universal checks (parallel dispatch gate)
- No changes to Phase 1, Phase 3, or the type-specific checks

## Verification

1. Confirm file was edited: `wc -l` shows line count increased by ~12 lines
2. Confirm no forbidden patterns:
   ```bash
   grep -E '\[date\]|TODO|TBD|YYYY-MM-DD' .claude/skills/plan-map-changes/SKILL.md
   ```
   Expect no output.
3. Manual trace: read the Phase 2 section and confirm:
   - TodoWrite instruction appears before U1
   - Parallel-dispatch gate appears between the todo instruction and U1
