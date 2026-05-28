# AL Dev Lint Review-Only Regression Design

## Goal

Add one focused regression check that keeps `/al-dev-lint` from silently
mutating files when the user only asked to inspect diagnostics or summarize
compile failures.

This is the smallest high-leverage improvement I found that is not already
covered by existing shared-profile tests: `al-dev-plan`, `al-dev-develop`,
`al-dev-fix`, and `al-dev-commit` already have scenario coverage for intent
misroutes, but `al-dev-lint` does not.

## Context

`profile-al-dev-shared/skills/al-dev-lint/SKILL.md` already defines the
behavior in prose:

- default intent is `EDIT`
- review-only and explanation-only requests must stop before mutating action
- the skill should ask for intent clarification instead of entering the fix loop

That rule is currently only a documentation rule. The missing piece is a
durable regression sensor that proves the skill does not compile, fix, or
dispatch the diagnostics-fixer path when the prompt is clearly review-only.

The nearby skills show the intended pattern:

- `al-dev-fix` has a review-only misfire scenario
- `al-dev-develop` has a review-only misfire scenario
- `al-dev-plan` has a validation-audit misfire scenario
- `al-dev-commit` has compile-gate and scope-gate scenarios

`al-dev-lint` should match that standard.

## Recommended Approach

Add a single `tests/scenarios.yaml` file under `profile-al-dev-shared/skills/al-dev-lint/`
with one golden scenario:

- prompt: a review-only compile-failure summary request
- expected artifacts: none
- forbidden agent invocation: `al-dev-shared:al-dev-diagnostics-fixer`

This is enough to catch the failure mode that matters most: a user asked for
diagnosis only, but the skill drifted into mutation or fix orchestration.

## Alternatives Considered

### Option 1: Add only the review-only regression scenario

This is the recommended option.

Benefits:

- lowest effort
- directly protects the documented intent-preflight rule
- aligns `al-dev-lint` with the existing scenario-based safety net used by
  neighboring skills

Trade-off:

- it covers only the highest-value misfire, not the broader compile/fix path
  behavior

### Option 2: Add the review-only scenario plus a clean-compile pass-through

This would add one more scenario that confirms `al-dev-lint` stays on the
lightweight path when there are no diagnostics.

Benefits:

- slightly broader regression coverage

Trade-off:

- more harness setup for a smaller incremental gain
- less attractive as the first step because the main gap is the missing
  review-only guard

## Design

### Test Surface

Create:

- `profile-al-dev-shared/skills/al-dev-lint/tests/scenarios.yaml`

Pattern to follow:

- one `skill:` header
- one `scenarios:` list
- a single `golden` scenario with a clear review-only prompt
- `expected_artifacts: []`
- `must_not_invoke_agent: al-dev-shared:al-dev-diagnostics-fixer`

The scenario text should make the intent unmistakable, for example:

> "Summarize the compile failures without fixing anything."

That wording matches the existing trigger corpus style and makes it obvious
that the correct behavior is to stop before mutation.

### Data Flow

1. Skill-test harness presents the review-only prompt.
2. `al-dev-lint` applies intent preflight.
3. The skill classifies the request as review-only.
4. The skill stops before compiling or entering the diagnostics-fixer loop.
5. The scenario passes only if no mutation path is taken and the fixer agent is
   not invoked.

### Error Handling

If the skill begins compile or fix work anyway, the scenario should fail as a
misroute regression. That failure is the signal that the documented intent
preflight rule has drifted out of enforcement.

If the skill asks for clarification instead of editing, that still counts as a
pass, because the goal is to block silent mutation, not force a specific reply
shape.

## Validation

Validate the new scenario by checking that:

- the new file exists under `profile-al-dev-shared/skills/al-dev-lint/tests/`
- the scenario uses the existing scenario schema style from neighboring skills
- the prompt is clearly review-only
- the diagnostics-fixer agent is forbidden
- no artifacts are expected for the misfire case

After implementation, run the relevant repository validation surface for shared
profile changes if any authored files change outside the new test file.

## Out of Scope

- Changing `al-dev-lint` runtime logic unless the regression exposes a real gap
- Adding broad compile-fix loop tests before the review-only path is covered
- Introducing new harness policies or new shared runtime concepts
- Moving the check into repo-local maintainer tooling

## Success Criteria

- `al-dev-lint` has at least one scenario-based regression for review-only
  misfires
- the skill cannot silently enter the diagnostics-fixer path for a
  review-only prompt without failing the test
- the change stays focused on the existing intent-preflight rule instead of
  adding new workflow surface
