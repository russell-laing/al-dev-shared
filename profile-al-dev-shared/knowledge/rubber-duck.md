# Rubber Duck Protocol

Rubber ducking is self-review before handoff. Before completing a phase and returning
output to the next step, the agent reviews its own work as if explaining it to a
sceptical observer — not to justify decisions, but to find gaps.

## The Rule

> If you find a gap during rubber ducking, **fix it before proceeding**. Do not log it,
> defer it, or note it for later. The rubber duck step is a blocker, not a suggestion.

## Format

Each phase that uses rubber ducking has a small set of specific questions. Work
through each question honestly. If the answer is "no" or "I'm not sure", treat
it as a gap.

## Where It's Applied

| Phase | File | Gate |
|-------|------|------|
| Requirements gathered | `profile-al-dev-shared/skills/al-dev-interview/SKILL.md` | Before final interview summary |
| Solution designed | `profile-al-dev-shared/agents/al-dev-solution-architect.md` | Before returning the recommended option |
| Plan validated | `profile-al-dev-shared/skills/al-dev-plan/SKILL.md` | Before presenting the plan for approval |
| Code implemented | `profile-al-dev-shared/agents/al-dev-developer.md` | Before reporting implementation complete |
| Code reviewed | `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` | Before Phase 10 presentation |
| Bug fixed | `profile-al-dev-shared/skills/al-dev-fix/SKILL.md` | Before presenting the fix |
| Commit prepared | `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` | Before commit execution |
| Report-driven plugin suggestion accepted | `profile-al-dev-shared/knowledge/rubber-duck.md` | Before a report suggestion becomes shared-profile scope |

## Suggestion-of-Merit Gate

Use this gate before turning a usage-report recommendation, retrospective note,
or maintainer observation into shared-profile implementation scope.

Each accepted suggestion must answer all five questions:

| Question | Passing Standard |
|---|---|
| What source evidence supports it? | The source contains a concrete failure mode, repeated friction pattern, metric, or traceable recommendation. |
| Which existing shared-profile file already covers part of the behavior? | The answer names the current file path and explains whether existing guidance is missing, unclear, contradictory, or untested. |
| Why does this belong in the shared plugin rather than repo-local tooling? | The behavior is durable, harness-neutral, and useful to downstream AL/BC workflows. |
| What risk does it reduce? | The answer names a concrete risk such as skill misfire, scope creep, compile false-success, stale debugging context, or unreviewed commits. |
| How can it be tested or reviewed? | The answer names a scenario file, trigger-corpus prompt, validation command, or manual review checklist. |

If any answer is missing, weak, or harness-specific, classify the suggestion as
`defer` or `reject` instead of adding it to shared-profile scope.

## Coverage Model Ratchet

When a suggestion passes the gate and becomes shared-profile scope, update or
check `docs/harness-coverage-model.md` before changing distributed guidance.

The coverage row must name:

- the behavior being regulated
- the existing guide or the new guide being added
- the sensor, test, scenario, validator, or manual review path
- the enforcement strength
- the owner
- the remaining gap

Choose the smallest durable control. Prefer a wording clarification,
trigger-corpus case, focused scenario, or existing validator/test update before
adding a broader workflow gate.

## Why It Matters

The most expensive mistakes are the ones that pass silently through a gate. A missed
requirement discovered after development costs one review cycle. The same gap discovered
after testing costs a full iteration. Rubber ducking is cheap; rework is not.
