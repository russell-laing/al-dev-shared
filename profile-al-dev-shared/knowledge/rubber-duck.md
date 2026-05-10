# Rubber Duck Protocol

Rubber ducking is self-review before handoff. Before completing a phase and returning
output to the next step, the agent reviews its own work as if explaining it to a
sceptical observer — not to justify decisions, but to find gaps.

## The Rule

> If you find a gap during rubber ducking, **fix it before proceeding**. Do not log it,
> defer it, or note it for later. The rubber duck step is a blocker, not a suggestion.

## Format

Each phase that uses rubber ducking has 3–4 specific questions. Work through each
question honestly. If the answer is "no" or "I'm not sure", treat it as a gap.

## Where It's Applied

| Phase | File | Gate |
|-------|------|------|
| Requirements gathered | `skills/al-dev-interview/SKILL.md` | Before Phase 3 summary |
| Solution designed | `agents/al-dev-solution-architect.agent.md` | End of Execution Checklist |
| Plan validated | `skills/al-dev-plan/SKILL.md` | Before Phase 7 approval gate |
| Code implemented (traditional) | `agents/al-dev-developer.agent.md` | Before Step 6 session log |
| Code implemented (TDD) | `agents/al-dev-developer.agent.md` | Before TDD Step 7 report |
| Code reviewed | `skills/al-dev-develop/SKILL.md` | Before Phase 10 approval gate |
| Tests written | `skills/al-dev-test/SKILL.md` | Before Phase 9 approval gate |
| Bug fixed | `commands/al-dev-fix.md` | Before Step 6 report (only gate in flow) |

## Why It Matters

The most expensive mistakes are the ones that pass silently through a gate. A missed
requirement discovered after development costs one review cycle. The same gap discovered
after testing costs a full iteration. Rubber ducking is cheap; rework is not.
