---
name: review-improvement-reports
description: Use when a supplied usage report or improvement report needs an evidence-backed assessment of possible improvements to the shared plugin surface, especially when the source may be stale or incomplete.
---

# Review Improvement Reports

Review a supplied usage report, improvement report, or report-derived recommendation list and write a repository-local assessment artifact.

This skill is an assessment and planning aid only. It must not edit `profile-al-dev-shared`, generated projections, shared agents, shared skills, or shared knowledge files.

## Output

Write one markdown report to:

- `.dev/YYYY-MM-DD-plugin-improvement-assessment.md`

If that file already exists for the current day, append a short suffix that identifies the source, for example:

- `.dev/YYYY-MM-DD-plugin-improvement-assessment-claude-insights.md`
- `.dev/YYYY-MM-DD-plugin-improvement-assessment-codex-summary.md`

## Required Inputs

Use the source artifact named by the user. Examples:

- `.dev/2026-05-24-ai-harness-neutral-usage-report.md`
- `~/.claude/usage-data/report.html`
- a markdown improvement report
- pasted report findings in the current conversation

If the user does not supply a source artifact or pasted report content, stop and ask for the report path or content.

## Workflow

### Phase 1: Read the Source Artifact

Read the supplied source. Extract:

- source artifact path or description
- reporting window when available
- evidence-backed findings
- recommendations or proposed improvements
- explicit caveats or missing data

Do not invent counts, dates, metrics, or recommendations. Mark inferred findings as inferred.

### Phase 2: Map Findings to Shared-Profile Surfaces

For each finding, search the current repository for existing coverage before proposing a change.

Start with:

```bash
rg -n "compile|scope|commit|rubber|intent|review|autonomous|misfire|routing|validation" profile-al-dev-shared
```

Map each finding to the most relevant current files, usually one or more of:

- `profile-al-dev-shared/skills/plan/SKILL.md`
- `profile-al-dev-shared/skills/develop-orchestrate/SKILL.md`
- `profile-al-dev-shared/skills/fix/SKILL.md`
- `profile-al-dev-shared/skills/commit/SKILL.md`
- `profile-al-dev-shared/knowledge/workflow-routing.md`
- `profile-al-dev-shared/knowledge/workflow-resilience.md`
- `profile-al-dev-shared/knowledge/rubber-duck.md`
- `profile-al-dev-shared/knowledge/compile-lint-procedure.md`
- `profile-al-dev-shared/markdown/compile-output-best-practices.md`
- `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml`
- `profile-al-dev-shared/skills/*/tests/scenarios.yaml`

If an existing file already covers the behavior adequately, classify the candidate as `reject` or `defer`; do not propose duplicate guidance.

### Phase 3: Classify Candidate Improvements

Classify every candidate as exactly one of:

- `keep` — evidence supports a durable, harness-neutral plugin improvement
- `defer` — evidence is real, but the right change needs more data, a separate design, or a larger implementation plan
- `reject` — evidence is weak, harness-specific, duplicate, or better handled by repo-local tooling

Use `keep` only when the candidate passes the suggestion-of-merit gate.

### Phase 4: Apply the Suggestion-of-Merit Gate

For every `keep` item, answer all five questions:

| Gate Question | Required Answer |
|---|---|
| What report evidence supports it? | Cite the source section, metric, quote summary, or observed failure mode. |
| Which existing shared-profile file already covers part of the behavior? | Name the current file path and the relevant behavior already present. |
| Why does this belong in the shared plugin rather than repo-local tooling? | Explain why it is durable, harness-neutral AL/BC workflow behavior. |
| What risk does it reduce? | Name the concrete workflow risk, such as misrouting, scope creep, compile false-success, or noisy debugging context. |
| How can it be tested or reviewed? | Name a trigger corpus case, scenario file, validation command, or manual review check. |

If any answer is missing or weak, change the classification from `keep` to `defer` or `reject`.

### Phase 5: Write the Assessment

Write the final report with this structure:

```markdown
# Plugin Improvement Assessment

## Source

- Artifact: state the exact source path, or write `conversation-supplied content`
- Reporting window: state the exact reporting window, or write `not stated`
- Assessment date: YYYY-MM-DD

## Executive Summary

Write three to five sentences summarizing the strongest evidence and the recommended next step.

## Evidence-Backed Findings

| Finding | Evidence | Existing Coverage |
|---|---|---|
| Write one concrete finding per row. | Cite the source-backed evidence for the finding. | Name the current `profile-al-dev-shared` path that already covers part of the behavior, or write `none found`. |

## Candidate Improvements

| Candidate | Classification | Reason |
|---|---|---|
| Write one candidate improvement per row. | keep | Explain why this passed the suggestion-of-merit gate. |
| Write one candidate improvement per row. | defer | Explain what data, design, or approval is missing. |
| Write one candidate improvement per row. | reject | Explain why this should not change the shared profile. |

## Rubber-Duck Gate for Kept Items

| Candidate | Evidence | Existing Coverage | Shared-Plugin Fit | Risk Reduced | Test or Review Strategy |
|---|---|---|---|---|---|
| Write one kept candidate per row. | State the supporting report evidence. | Name the existing shared-profile file. | Explain why this belongs in the shared plugin. | Name the workflow risk reduced. | Name the test, validation command, or review check. |

## Recommended Next Step

Choose exactly one:

- No action: state the reason.
- Write a spec: state the proposed spec scope.
- Write an implementation plan: state the proposed plan scope.
- Implement an already-approved plan: state the exact approved plan path.

## Out of Scope

- This assessment did not edit `profile-al-dev-shared`.
- This assessment did not regenerate projections.
- This assessment did not commit changes.
```

Replace instructional row text with concrete assessment content. Do not leave generic example rows in the final report.

## Guardrails

- Do not edit `profile-al-dev-shared` directly.
- Do not create implementation plans unless the user explicitly asks for a plan.
- Do not classify harness-specific setup as a shared-plugin change unless it has a harness-neutral rule underneath.
- Do not treat report recommendations as accepted requirements.
- Do not claim a suggestion is evidence-backed unless the source artifact contains the evidence or the current repo search confirms it.
- Do not commit unless the user explicitly asks for a commit after reviewing the assessment.

## Validation

Before reporting completion:

1. Confirm the assessment file exists under `.dev/`.
2. Re-open the assessment and verify every `keep` item has a complete rubber-duck row.
3. Run:

   ```bash
   git status --short
   ```

4. Confirm no `profile-al-dev-shared` files were modified by this assessment run.
