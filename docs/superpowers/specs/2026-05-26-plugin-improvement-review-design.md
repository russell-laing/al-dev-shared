# Plugin Improvement Review Design

## Goal

Use harness usage reports as evidence for improving `profile-al-dev-shared`
without letting report-specific recommendations leak directly into the
distributed plugin. Each suggestion of merit must be rubber-ducked before it
can become a shared-profile change.

## Context

The reviewed report shows a mature plan-first workflow with recurring friction
around late AL compile failures, skill intent mismatches, git scope mistakes,
and occasionally stale or noisy debugging context. The shared profile already
contains partial countermeasures: autonomous compile verification,
compile-output discipline, scope gates, commit gates, and rubber-ducking
guidance. The design therefore focuses on making those safeguards clearer,
better routed, and testable instead of adding a broad new autonomous pipeline.

Repo-local `.codex/skills/` files are allowed when they directly support
improving the plugin, such as report analysis, plugin documentation, and
assessment of proposed improvements. They must not become an alternate runtime
surface for AL/BC plugin behavior that belongs in `profile-al-dev-shared`.

## Recommended Approach

Use a combined but bounded approach:

1. Harden the shared plugin profile where evidence points to durable,
   harness-neutral workflow improvements.
2. Add a repo-local maintainer skill under `.codex/skills/` for repeatable
   report-driven plugin assessment.
3. Keep implementation of accepted changes behind a separate plan or
   implementation step.

This gives the shared plugin durable improvements while keeping report analysis
reviewable and repository-local.

## Shared Profile Changes

### Intent Preflight

Add a lightweight intent preflight to non-trivial shared workflows. Before a
skill performs edits, dispatches agents, or commits work, it should classify the
request as one of:

- `REVIEW` — analyze only, no edits.
- `EDIT` — modify files but do not commit.
- `COMMIT` — stage and commit explicitly approved changes.

If the user request and invoked skill disagree, the skill must stop and ask for
confirmation instead of silently proceeding. This targets the observed class of
skill misfires without making every workflow conversational.

### Rubber-Duck Gate Repair

Update `profile-al-dev-shared/knowledge/rubber-duck.md` so it references real
current shared-profile files and defines a suggestion-of-merit gate. Each
accepted suggestion must answer:

- What report evidence supports it?
- Which existing shared-profile file already covers part of the behavior?
- Why does this belong in the shared plugin rather than repo-local tooling?
- What risk does it reduce?
- How can it be tested or reviewed?

Suggestions that fail this gate are either deferred or rejected with a short
reason.

### Compile Verification Clarity

Clarify `/al-dev-develop` compile behavior so normal mode, autonomous mode, and
small-fix flows do not contradict each other. The shared profile should make the
safe default obvious:

- Trivial fixes compile once and report concise results.
- Planned AL implementation should prefer autonomous compile verification unless
  explicitly scoped down.
- Autonomous mode owns bounded compile-fix iterations and must not report
  success while new compile errors remain.

This does not require harness-specific hooks. Hook setup can remain optional
environment guidance because hook behavior differs by harness.

### Misfire Regression Tests

Expand shared test data with near-miss prompts that reflect observed friction:

- Review-only prompts must not route to edit or commit flows.
- Validation-audit prompts must not route to implementation planning.
- Commit prompts must route to explicit scoped commit behavior.
- Autonomous compile prompts must route to `/al-dev-develop`, not ad-hoc fixes.

These cases belong in `knowledge/skill-test-trigger-corpus.yaml` and focused
per-skill `tests/scenarios.yaml` files where artifact or agent expectations can
be checked.

## Repo-Local Maintainer Skill

Create a repo-local skill:

```text
.codex/skills/plugin-improvement-review/
  SKILL.md
```

The skill reviews a supplied usage report or improvement report and produces:

```text
.dev/<current-date>-plugin-improvement-assessment.md
```

For example, a run on May 26, 2026 writes
`.dev/2026-05-26-plugin-improvement-assessment.md`.

The assessment must include:

- Source artifact and reporting window when available.
- Evidence-backed findings.
- Mapping from each finding to existing `profile-al-dev-shared` files.
- Candidate improvements classified as `keep`, `defer`, or `reject`.
- A rubber-duck table for every `keep` item.
- Recommended next step: spec, implementation plan, or no action.

The maintainer skill must not edit `profile-al-dev-shared` directly. It is an
assessment and planning aid only.

## Data Flow

1. User supplies a report, for example `~/.claude/usage-data/report.html`.
2. Repo-local maintainer skill extracts evidence-backed findings.
3. Findings are mapped to existing shared-profile surfaces.
4. Candidate suggestions are rubber-ducked and classified.
5. The skill writes a `.dev/` assessment artifact.
6. User reviews the assessment.
7. Accepted shared-profile changes proceed through a separate implementation
   plan.

This preserves a clean boundary between external report analysis and plugin
runtime behavior.

## Validation

Shared-profile changes should use the existing repository validation surface:

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
python3 scripts/generate-agent-projections.py
```

Projection regeneration is required only when shared agents change.

The repo-local maintainer skill should be validated with a dry run against the
current report. The output passes review only if every kept suggestion has
evidence, target file mapping, rubber-duck rationale, and a test or review
strategy.

## Out of Scope

- Adding harness-specific compile hooks to the distributed plugin.
- Building a one-command audit-plan-implement-commit pipeline.
- Moving report-analysis tooling into `profile-al-dev-shared`.
- Implementing accepted shared-profile changes in the same step as report
  assessment.

## Success Criteria

- Shared workflow changes are harness-neutral and pass validation.
- Skill misfire and review-vs-edit boundaries are covered by test prompts.
- Rubber-duck guidance references current files and produces actionable gates.
- Future report analyses can produce a reviewable `.dev/` assessment without
  editing the shared plugin.
