# Plugin Improvement Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a bounded, evidence-based workflow for turning harness usage reports into reviewable shared-plugin improvement candidates without letting report-specific recommendations leak directly into `profile-al-dev-shared`.

**Architecture:** Keep report assessment repository-local under `.codex/skills/`, and keep durable AL/BC workflow hardening inside the shared profile. Add one central shared intent-preflight knowledge file, reference it from the non-trivial shared workflows that can dispatch agents, edit, or commit, repair rubber-duck guidance around a suggestion-of-merit gate, and expand misfire regression data in the existing trigger corpus and per-skill scenario files.

**Tech Stack:** Markdown skills and knowledge files, YAML scenario data, Python 3 repository validation scripts, git

---

## File Structure

- Create: `.codex/skills/plugin-improvement-review/SKILL.md` — repo-local Codex maintainer skill for report-driven plugin improvement assessment only
- Modify: `CODEX.md` — register the new repo-local skill in the Codex maintainer guidance
- Create: `profile-al-dev-shared/knowledge/intent-preflight.md` — harness-neutral shared rule for REVIEW / EDIT / COMMIT intent classification
- Modify: `profile-al-dev-shared/knowledge/rubber-duck.md` — repair stale file references and add the suggestion-of-merit gate
- Modify: `profile-al-dev-shared/skills/al-dev-plan/SKILL.md` — apply intent preflight before architect dispatch
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` — apply intent preflight and clarify normal versus autonomous compile verification
- Modify: `profile-al-dev-shared/skills/al-dev-fix/SKILL.md` — apply intent preflight and clarify small-fix compile verification
- Modify: `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` — apply intent preflight before commit analysis/execution
- Modify: `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml` — add near-miss routing prompts for review/edit/commit/autonomous compile boundaries
- Modify: `profile-al-dev-shared/skills/al-dev-plan/tests/scenarios.yaml` — add validation-audit misfire scenario
- Modify: `profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml` — add review-only and autonomous compile routing scenarios
- Modify: `profile-al-dev-shared/skills/al-dev-fix/tests/scenarios.yaml` — add review-only no-edit scenario
- Modify: `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml` — add explicit scoped commit scenario

---

### Task 1: Create the Repo-Local Assessment Skill

**Files:**
- Create: `.codex/skills/plugin-improvement-review/SKILL.md`
- Modify: `CODEX.md`

- [ ] **Step 1: Verify the repo-local skill does not already exist**

Run:
```bash
test ! -e .codex/skills/plugin-improvement-review && echo "NOT FOUND"
```

Expected:
```text
NOT FOUND
```

- [ ] **Step 2: Create the skill directory**

Run:
```bash
mkdir -p .codex/skills/plugin-improvement-review
```

Expected: command exits `0` with no output.

- [ ] **Step 3: Write the repo-local skill instructions**

Create `.codex/skills/plugin-improvement-review/SKILL.md` with this exact content:

```markdown
---
name: plugin-improvement-review
description: Review a supplied usage report or improvement report and produce an evidence-backed assessment of possible improvements to the al-dev-shared plugin. Use only for repository-local plugin maintainer analysis; it must not edit profile-al-dev-shared directly.
---

# Plugin Improvement Review

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

- `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`
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
```

- [ ] **Step 4: Verify the skill file is repo-local only**

Run:
```bash
test -f .codex/skills/plugin-improvement-review/SKILL.md
test ! -e profile-al-dev-shared/skills/plugin-improvement-review
```

Expected: both commands exit `0` with no output.

- [ ] **Step 5: Update Codex maintainer guidance**

In `CODEX.md`, replace the current repo-local skill list:

```markdown
Current repo-local skill:

- `.codex/skills/ai-usage-report/` — converts harness-specific usage artifacts
  into neutral markdown reports and can optionally add Codex-derived local
  usage observations.
```

with:

```markdown
Current repo-local skills:

- `.codex/skills/ai-usage-report/` — converts harness-specific usage artifacts
  into neutral markdown reports and can optionally add Codex-derived local
  usage observations.
- `.codex/skills/plugin-improvement-review/` — reviews supplied usage or
  improvement reports and writes evidence-backed plugin improvement
  assessments without editing the shared plugin profile directly.
```

- [ ] **Step 6: Verify only repo-local and guidance files changed**

Run:
```bash
git status --short .codex/skills/plugin-improvement-review CODEX.md profile-al-dev-shared
```

Expected:
```text
 M CODEX.md
?? .codex/skills/plugin-improvement-review/
```

- [ ] **Step 7: Commit**

Run:
```bash
git add .codex/skills/plugin-improvement-review/SKILL.md CODEX.md
git commit -m "chore: add plugin improvement review skill"
```

Expected: commit succeeds. If the user has asked not to commit, stop after staging guidance and report the staged files instead.

---

### Task 2: Add Shared Intent Preflight Guidance

**Files:**
- Create: `profile-al-dev-shared/knowledge/intent-preflight.md`
- Modify: `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`
- Modify: `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`
- Modify: `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`

- [ ] **Step 1: Write the shared intent-preflight knowledge file**

Create `profile-al-dev-shared/knowledge/intent-preflight.md` with this exact content:

```markdown
# Intent Preflight

Intent preflight prevents a skill from silently doing a different class of work than the user asked for.

Run this preflight before a non-trivial workflow dispatches agents, edits files, stages files, or commits.

## Intent Classes

Classify the user's request as exactly one of:

| Intent | Meaning | Allowed Work |
|---|---|---|
| `REVIEW` | Analyze, inspect, summarize, audit, or critique only. | Read files, run non-mutating inspection commands, write an explicitly requested report artifact. Do not edit project/runtime files. Do not commit. |
| `EDIT` | Modify files, implement a fix, or generate changed artifacts. | Edit files inside the approved scope. Do not commit unless the user separately asks for a commit. |
| `COMMIT` | Stage and commit explicitly approved changes. | Inspect and commit staged or approved changes after all commit gates pass. Do not add unrelated files. |

## Mismatch Rule

If the invoked skill and detected intent disagree, stop before any mutating action and ask for confirmation.

Use this prompt:

```text
Intent mismatch: this request appears to be [REVIEW|EDIT|COMMIT], but [skill-name] normally performs [expected intent]. Confirm the intended action before I continue.
```

Continue only after the user confirms the intended action.

## Skill Defaults

| Skill | Default Intent |
|---|---|
| `al-dev-plan` | `REVIEW` for design-only planning artifacts; `EDIT` only for writing the requested `.dev/` plan artifact |
| `al-dev-develop` | `EDIT` |
| `al-dev-fix` | `EDIT` |
| `al-dev-commit` | `COMMIT` |

## Examples

| User Request | Intent | Result |
|---|---|---|
| "review this usage report and suggest possible plugin improvements" | `REVIEW` | Do not invoke implementation or commit workflows. |
| "audit the validation output and tell me what failed" | `REVIEW` | Do not route to implementation planning. |
| "fix the posting bug" | `EDIT` | A fix workflow may edit files after normal scope checks. |
| "implement the approved plan" | `EDIT` | A develop workflow may proceed after confirming the plan exists. |
| "commit the staged changes" | `COMMIT` | A commit workflow may proceed through commit gates. |
```

- [ ] **Step 2: Add intent preflight to `al-dev-plan`**

In `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`, add this section immediately after the opening purpose/overview section and before the first phase or workflow step:

```markdown
## Intent Preflight

Before dispatching architect agents or writing a plan artifact, apply
`knowledge/intent-preflight.md`.

Default intent for this skill is `REVIEW` when the user asks for design,
planning, or architecture output. Writing the requested `.dev/` plan artifact is
allowed as part of that planning request.

Stop before architect dispatch if the request is only an audit, validation
review, code review, or report assessment that does not ask for a design or
implementation plan. Ask the intent-mismatch prompt from
`knowledge/intent-preflight.md` before continuing.
```

- [ ] **Step 3: Add intent preflight to `al-dev-develop`**

In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, add this section immediately after the `# Develop Skill` introduction and before `## Prerequisites`:

```markdown
## Intent Preflight

Before reading the solution plan for execution, dispatching developers, editing
files, staging files, or spawning reviewers, apply
`knowledge/intent-preflight.md`.

Default intent for this skill is `EDIT`. If the request is review-only,
assessment-only, validation-audit-only, planning-only, or commit-only, stop and
ask the intent-mismatch prompt from `knowledge/intent-preflight.md` before any
mutating action or agent dispatch.
```

- [ ] **Step 4: Add intent preflight to `al-dev-fix`**

In `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`, add this section immediately after the `## Purpose` section:

```markdown
## Intent Preflight

Before spawning an architect or developer, editing files, or running a mutating
fix path, apply `knowledge/intent-preflight.md`.

Default intent for this skill is `EDIT`. If the request asks only to review,
audit, investigate, explain, or assess a possible fix without applying changes,
stop and ask the intent-mismatch prompt from `knowledge/intent-preflight.md`
before any mutating action or implementation agent dispatch.
```

- [ ] **Step 5: Add intent preflight to `al-dev-commit`**

In `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`, add this section after the opening workflow description and before `## Step 1 — Guard: Verify Project Context`:

```markdown
## Intent Preflight

Before dispatching commit agents, staging files, unstaging files, or committing,
apply `knowledge/intent-preflight.md`.

Default intent for this skill is `COMMIT`. If the request is review-only,
edit-only, assessment-only, or asks for a commit plan without committing, stop
and ask the intent-mismatch prompt from `knowledge/intent-preflight.md` before
continuing.
```

- [ ] **Step 6: Verify all four shared skills reference the new knowledge file**

Run:
```bash
rg -n "knowledge/intent-preflight.md|Intent Preflight" profile-al-dev-shared/skills/al-dev-plan/SKILL.md profile-al-dev-shared/skills/al-dev-develop/SKILL.md profile-al-dev-shared/skills/al-dev-fix/SKILL.md profile-al-dev-shared/skills/al-dev-commit/SKILL.md profile-al-dev-shared/knowledge/intent-preflight.md
```

Expected: matches in all five files.

- [ ] **Step 7: Validate shared-source neutrality**

Run:
```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Expected: command exits `0`; any output reports no harness-specific leakage.

- [ ] **Step 8: Commit**

Run:
```bash
git add profile-al-dev-shared/knowledge/intent-preflight.md profile-al-dev-shared/skills/al-dev-plan/SKILL.md profile-al-dev-shared/skills/al-dev-develop/SKILL.md profile-al-dev-shared/skills/al-dev-fix/SKILL.md profile-al-dev-shared/skills/al-dev-commit/SKILL.md
git commit -m "docs: add shared intent preflight"
```

Expected: commit succeeds. If committing is not approved for the implementation run, stop after validation and report the modified files.

---

### Task 3: Repair Rubber-Duck Guidance

**Files:**
- Modify: `profile-al-dev-shared/knowledge/rubber-duck.md`

- [ ] **Step 1: Replace the stale application table**

In `profile-al-dev-shared/knowledge/rubber-duck.md`, replace the entire table under `## Where It's Applied` with:

```markdown
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
```

- [ ] **Step 2: Add the suggestion-of-merit gate**

After the repaired table, insert:

```markdown
## Suggestion-of-Merit Gate

Use this gate before turning a usage-report recommendation, retrospective note,
or maintainer observation into shared-profile implementation scope.

Each accepted suggestion must answer all five questions:

| Question | Passing Standard |
|---|---|
| What report evidence supports it? | The report contains a concrete failure mode, repeated friction pattern, metric, or traceable recommendation. |
| Which existing shared-profile file already covers part of the behavior? | The answer names the current file path and explains whether existing guidance is missing, unclear, contradictory, or untested. |
| Why does this belong in the shared plugin rather than repo-local tooling? | The behavior is durable, harness-neutral, and useful to downstream AL/BC workflows. |
| What risk does it reduce? | The answer names a concrete risk such as skill misfire, scope creep, compile false-success, stale debugging context, or unreviewed commits. |
| How can it be tested or reviewed? | The answer names a scenario file, trigger-corpus prompt, validation command, or manual review checklist. |

If any answer is missing, weak, or harness-specific, classify the suggestion as
`defer` or `reject` instead of adding it to shared-profile scope.
```

- [ ] **Step 3: Verify stale paths were removed**

Run:
```bash
rg -n "agent.md|commands/al-dev-fix|skills/al-dev-test|\\.agent\\.md" profile-al-dev-shared/knowledge/rubber-duck.md || echo "NO STALE PATHS"
```

Expected:
```text
NO STALE PATHS
```

- [ ] **Step 4: Commit**

Run:
```bash
git add profile-al-dev-shared/knowledge/rubber-duck.md
git commit -m "docs: repair rubber duck suggestion gate"
```

Expected: commit succeeds, unless commits are deferred by the user.

---

### Task 4: Clarify Compile Verification Behavior

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`
- Modify: `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`

- [ ] **Step 1: Add a compile-mode summary to `al-dev-develop`**

In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, add this section immediately before `## Phase 8: Compilation & Error Handling`:

```markdown
## Compile Verification Modes

Compilation must be reported from `.dev/compile-errors.log` using concise
summaries, not raw terminal output.

| Mode | Compile Behavior | Success Rule |
|---|---|---|
| Normal `/al-dev-develop` | Run one implementation compile pass, summarize diagnostics, assign one batched fix pass if errors exist, then compile once more. | Do not report success while new compile errors remain. If errors remain after the batched fix pass, write them into the review artifact as blocking compilation issues. |
| `/al-dev-develop --autonomous` | Run bounded compile-fix iterations, up to five compile attempts total. | Do not leave autonomous mode through the success path while new compile errors remain. If five attempts are exhausted, stop with a blocking review artifact. |
| Small fixes | Use `/al-dev-fix`, not `/al-dev-develop`, for a tightly scoped one-file or trivial correction. | Compile once and report the concise result; if compilation fails, fix only errors caused by the small change. |

Hook setup is optional environment guidance. This shared profile defines the
compile discipline, but does not require harness-specific hook installation.
```

- [ ] **Step 2: Replace the contradictory Phase 8 error branch**

In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, replace the Phase 8 bullet that currently starts with:

```markdown
6. **If errors exist:** 
   - Group by category (naming, schema, compilation, warnings)
   - Assign fixes to developers based on error type
   - Compile once more after all fixes applied
```

with:

```markdown
6. **If errors exist in normal mode:**
   - Group by category (naming, schema, compilation, warnings)
   - Assign one batched fix pass to the relevant developer(s)
   - Compile once more after all fixes are applied
   - If new compile errors remain, do not report success; write the remaining
     diagnostics into the Phase 9 review artifact as blocking compilation
     issues
7. **If errors exist in autonomous mode (`--autonomous`):**
   - Run a bounded compile-fix loop with at most five compile attempts total
   - After each failed attempt, summarize the error count, representative
     diagnostics, affected files, and assigned fix owner
   - Stop immediately when a compile attempt has no new errors and proceed to
     Phase 8.5
   - If attempt five still has new compile errors, do not report success; write
     a blocking review artifact with the remaining diagnostics and attempts
     summary
```

- [ ] **Step 3: Clarify small-fix compile reporting in `al-dev-fix`**

In `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`, replace the first paragraph under `## Compilation Summary Format` with:

```markdown
This skill uses `knowledge/compile-lint-procedure.md` for compile and lint
passes. For trivial fixes, compile once after the minimal edit and report a
concise result. If compilation fails, fix only errors caused by the small change
and re-run compile once; do not expand into a broad compile-fix loop. For
non-trivial fixes, keep compile correction bounded to the confirmed root-cause
scope.
```

- [ ] **Step 4: Verify the success rule is explicit**

Run:
```bash
rg -n "Do not report success|five compile attempts|compile once after the minimal edit|Hook setup is optional" profile-al-dev-shared/skills/al-dev-develop/SKILL.md profile-al-dev-shared/skills/al-dev-fix/SKILL.md
```

Expected: matches for all four phrases.

- [ ] **Step 5: Validate shared-source neutrality**

Run:
```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Expected: command exits `0`.

- [ ] **Step 6: Commit**

Run:
```bash
git add profile-al-dev-shared/skills/al-dev-develop/SKILL.md profile-al-dev-shared/skills/al-dev-fix/SKILL.md
git commit -m "docs: clarify compile verification modes"
```

Expected: commit succeeds, unless commits are deferred by the user.

---

### Task 5: Add Misfire Regression Data

**Files:**
- Modify: `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml`
- Modify: `profile-al-dev-shared/skills/al-dev-plan/tests/scenarios.yaml`
- Modify: `profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml`
- Modify: `profile-al-dev-shared/skills/al-dev-fix/tests/scenarios.yaml`
- Modify: `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml`

- [ ] **Step 1: Add near-miss prompts to the trigger corpus**

In `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml`, append this block before the final existing `expected to route elsewhere or to NONE` section if possible; otherwise append it at the end of `corpus`:

```yaml
  # --- intent preflight and near-miss prompts -----------------------------
  - prompt: "review this usage report and suggest possible plugin improvements without editing files"
    expected: NONE
  - prompt: "audit the validation output and tell me what failed, do not plan implementation"
    expected: NONE
  - prompt: "assess whether these recommendations belong in the shared plugin"
    expected: NONE
  - prompt: "commit only the staged docs changes after checking scope"
    expected: al-dev-commit
  - prompt: "implement the approved plan in autonomous mode and keep compiling until it builds"
    expected: al-dev-develop
```

- [ ] **Step 2: Add the validation-audit scenario to `al-dev-plan`**

Append this scenario to `profile-al-dev-shared/skills/al-dev-plan/tests/scenarios.yaml`:

```yaml
  - id: plan-rejects-validation-audit-misfire
    status: golden
    user_prompt: "Audit the validation output and summarize what failed. Do not create an implementation plan."
    expected_artifacts: []
    must_not_invoke_agent: al-dev-shared:al-dev-solution-architect
    notes: "Intent preflight regression. A validation-audit prompt is REVIEW intent and must not route to competitive implementation planning."
```

- [ ] **Step 3: Add review-only and autonomous compile scenarios to `al-dev-develop`**

Append these scenarios to `profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml`:

```yaml
  - id: develop-rejects-review-only-misfire
    status: golden
    user_prompt: "Review the approved plan for risks only. Do not edit files or dispatch developers."
    expected_artifacts: []
    must_not_invoke_agent:
      - al-dev-shared:al-dev-developer
      - al-dev-shared:al-dev-security-reviewer
      - al-dev-shared:al-dev-expert-reviewer
      - al-dev-shared:al-dev-performance-reviewer
    notes: "Intent preflight regression. Review-only prompts must not enter edit or review-panel execution flow."

  - id: develop-autonomous-compile-routing
    status: golden
    user_prompt: "Implement the latest approved plan in autonomous mode and keep compiling until it builds."
    expected_artifacts:
      - ".dev/*-al-dev-autonomous-signatures.md"
      - ".dev/*-al-dev-autonomous-static-validation.md"
      - ".dev/*-al-dev-develop-code-review.md"
    must_invoke_agent:
      - al-dev-shared:al-dev-developer
      - al-dev-shared:al-dev-security-reviewer
      - al-dev-shared:al-dev-expert-reviewer
      - al-dev-shared:al-dev-performance-reviewer
    notes: "Locks autonomous compile prompts to al-dev-develop autonomous behavior instead of ad-hoc fixes."
```

- [ ] **Step 4: Add the review-only no-edit scenario to `al-dev-fix`**

Append this scenario to `profile-al-dev-shared/skills/al-dev-fix/tests/scenarios.yaml`:

```yaml
  - id: fix-rejects-review-only-misfire
    status: golden
    user_prompt: "Review this suspected posting bug and explain the likely cause. Do not change files."
    expected_artifacts: []
    must_not_invoke_agent:
      - al-dev-shared:al-dev-solution-architect
      - al-dev-shared:al-dev-developer
    notes: "Intent preflight regression. A review-only request must not silently enter the lightweight edit path."
```

- [ ] **Step 5: Add the scoped commit scenario to `al-dev-commit`**

Append this scenario to `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml`:

```yaml
  - id: commit-explicit-scoped-docs
    status: golden
    user_prompt: "Commit only the staged docs changes after checking scope."
    expected_artifacts: []
    must_invoke_agent:
      - al-dev-shared:al-dev-commit-agent-analysis
      - al-dev-shared:al-dev-commit-agent-execute
    notes: "Commit intent regression. Explicit scoped commit prompts must route to commit gates and commit agents, not edit or planning flows."
```

- [ ] **Step 6: Verify the new scenario IDs and prompts exist**

Run:
```bash
rg -n "review this usage report|plan-rejects-validation-audit-misfire|develop-rejects-review-only-misfire|develop-autonomous-compile-routing|fix-rejects-review-only-misfire|commit-explicit-scoped-docs" profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml profile-al-dev-shared/skills/*/tests/scenarios.yaml
```

Expected: one or more matches for every ID or prompt in the command.

- [ ] **Step 7: Run lightweight schema sanity checks**

Run:
```bash
python3 - <<'PY'
from pathlib import Path

checks = {
    Path("profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml"): [
        "review this usage report",
        "commit only the staged docs changes",
        "implement the approved plan in autonomous mode",
    ],
    Path("profile-al-dev-shared/skills/al-dev-plan/tests/scenarios.yaml"): [
        "plan-rejects-validation-audit-misfire",
        "must_not_invoke_agent: al-dev-shared:al-dev-solution-architect",
    ],
    Path("profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml"): [
        "develop-rejects-review-only-misfire",
        "develop-autonomous-compile-routing",
    ],
    Path("profile-al-dev-shared/skills/al-dev-fix/tests/scenarios.yaml"): [
        "fix-rejects-review-only-misfire",
    ],
    Path("profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml"): [
        "commit-explicit-scoped-docs",
        "al-dev-shared:al-dev-commit-agent-analysis",
        "al-dev-shared:al-dev-commit-agent-execute",
    ],
}

missing = []
for path, needles in checks.items():
    text = path.read_text()
    for needle in needles:
        if needle not in text:
            missing.append(f"{path}: {needle}")

if missing:
    raise SystemExit("Missing expected content:\n" + "\n".join(missing))

print("scenario content sanity checks passed")
PY
```

Expected:
```text
scenario content sanity checks passed
```

- [ ] **Step 8: Commit**

Run:
```bash
git add profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml profile-al-dev-shared/skills/al-dev-plan/tests/scenarios.yaml profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml profile-al-dev-shared/skills/al-dev-fix/tests/scenarios.yaml profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml
git commit -m "test: add intent misfire regression scenarios"
```

Expected: commit succeeds, unless commits are deferred by the user.

---

### Task 6: Validate the Full Change Set

**Files:**
- Validate: `profile-al-dev-shared/**`
- Validate: `.codex/skills/plugin-improvement-review/SKILL.md`
- Validate: `CODEX.md`

- [ ] **Step 1: Run harness-neutrality validation**

Run:
```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Expected: command exits `0`.

- [ ] **Step 2: Run agent structure validation**

Run:
```bash
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
```

Expected: command exits `0`.

- [ ] **Step 3: Regenerate projections only if shared agents changed**

Run:
```bash
git diff --name-only HEAD -- profile-al-dev-shared/agents
```

Expected for this plan:
```text
```

If the command prints no paths, skip projection regeneration because this plan does not change shared agent files.

If the command prints any shared agent path, run:

```bash
python3 scripts/generate-agent-projections.py
```

Expected: command exits `0`, and generated agent diffs correspond only to the changed shared agents.

- [ ] **Step 4: Dry-run the repo-local assessment skill manually**

Use an existing report artifact, for example:

```bash
test -f .dev/2026-05-24-ai-harness-neutral-usage-report.md && echo "REPORT FOUND"
```

Expected if the artifact exists:
```text
REPORT FOUND
```

Then invoke the new skill in the active harness with:

```text
Use the repo-local plugin-improvement-review skill at .codex/skills/plugin-improvement-review/SKILL.md to assess .dev/2026-05-24-ai-harness-neutral-usage-report.md. Write the assessment only; do not edit profile-al-dev-shared.
```

Expected: `.dev/YYYY-MM-DD-plugin-improvement-assessment.md` is created, and `git status --short profile-al-dev-shared` shows no changes from the assessment run.

- [ ] **Step 5: Verify no generated projections were accidentally changed**

Run:
```bash
git status --short profile-al-dev-shared/generated
```

Expected:
```text
```

If projection regeneration was intentionally run because shared agents changed, expected output may list generated files; verify each generated path maps to an intentional shared-agent source change.

- [ ] **Step 6: Review final changed files**

Run:
```bash
git status --short
```

Expected: only files from this plan are modified or added, plus any pre-existing unrelated dirty files that were present before implementation.

- [ ] **Step 7: Commit final validation adjustments if needed**

If validation required small follow-up fixes, commit them:

```bash
git add .codex/skills/plugin-improvement-review/SKILL.md CODEX.md profile-al-dev-shared/knowledge/intent-preflight.md profile-al-dev-shared/knowledge/rubber-duck.md profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml profile-al-dev-shared/skills/al-dev-plan/SKILL.md profile-al-dev-shared/skills/al-dev-develop/SKILL.md profile-al-dev-shared/skills/al-dev-fix/SKILL.md profile-al-dev-shared/skills/al-dev-commit/SKILL.md profile-al-dev-shared/skills/al-dev-plan/tests/scenarios.yaml profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml profile-al-dev-shared/skills/al-dev-fix/tests/scenarios.yaml profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml
git commit -m "chore: validate plugin improvement review workflow"
```

Expected: commit succeeds only if there are uncommitted plan-related validation adjustments and the implementation run is allowed to commit.

---

## Self-Review

- Spec coverage: The plan covers shared profile hardening, the repo-local maintainer skill, intent preflight, rubber-duck gate repair, compile clarity, misfire regression data, validation, and the boundary that accepted shared-profile changes require separate review or implementation.
- Placeholder scan: The plan contains no unfinished placeholder tokens, angle-bracket placeholders, or "similar to" implementation steps. Template rows in the repo-local skill body are instructional and explicitly require replacement with concrete assessment content.
- Type consistency: Intent classes are consistently `REVIEW`, `EDIT`, and `COMMIT`; candidate classifications are consistently `keep`, `defer`, and `reject`; scenario field names match `profile-al-dev-shared/knowledge/skill-test-format.md`.
