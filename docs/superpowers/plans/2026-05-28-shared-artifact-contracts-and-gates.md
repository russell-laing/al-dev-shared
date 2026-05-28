# Shared Artifact Contracts and Final Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one shared artifact-contract reference, tighten final completion claims across the listed shared skills, and publish one compact example artifact bundle that matches the new contract.

**Architecture:** Keep the change harness-neutral and documentation-led. The new `artifact-contracts.md` file becomes the source of truth for required inputs, durable outputs, resume order, handoff artifacts, and success evidence; the targeted skills only cross-reference that source and enforce final-claim discipline instead of redefining their own evidence model.

**Tech Stack:** Markdown knowledge files, Markdown skill docs, YAML scenario fixtures, existing Python validation scripts

---

## File Structure

| File | Responsibility |
|------|---|
| `profile-al-dev-shared/knowledge/artifact-contracts.md` | Canonical contract matrix for the six named workflows |
| `profile-al-dev-shared/skills/al-dev-fix/SKILL.md` | Add cross-reference and final-gate wording for lightweight fixes |
| `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` | Add cross-reference and final-gate wording for plan execution and Phase 4 handoff |
| `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md` | Add cross-reference and final-gate wording for post-implementation review completion |
| `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` | Align existing commit gate wording with the contract doc |
| `profile-al-dev-shared/skills/al-dev-lint/SKILL.md` | Add cross-reference and final-gate wording for lint completion claims |
| `docs/example-runs/al-dev-core/README.md` | Explain the example bundle sequence and how it maps to the contract matrix |
| `docs/example-runs/al-dev-core/sample-solution-plan.md` | Compact example plan artifact |
| `docs/example-runs/al-dev-core/sample-progress.md` | Compact example checkpoint/resume artifact |
| `docs/example-runs/al-dev-core/sample-checklist.md` | Compact example implementation checklist artifact |
| `docs/example-runs/al-dev-core/sample-scope.md` | Compact example scope-boundary artifact |
| `docs/example-runs/al-dev-core/sample-code-review.md` | Compact example final review artifact |
| `profile-al-dev-shared/skills/al-dev-fix/tests/scenarios.yaml` | Regression coverage for blocked final claims in fix flow |
| `profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml` | Regression coverage for handoff and completion-evidence discipline |
| `profile-al-dev-shared/skills/al-dev-lint/tests/scenarios.yaml` | Regression coverage for lint summary vs. final success language |
| `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml` | Regression coverage for commit success-evidence discipline |
| `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml` | Near-miss prompts that must not produce unsupported “done/validated” claims |

---

### Task 1: Create the Canonical Artifact Contract Matrix

**Files:**
- Create: `profile-al-dev-shared/knowledge/artifact-contracts.md`
- Reference: `profile-al-dev-shared/knowledge/workflow-resilience.md`
- Reference: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`
- Reference: `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`

- [ ] **Step 1: Read the current artifact and resume sources**

Run:

```bash
sed -n '1,220p' profile-al-dev-shared/knowledge/workflow-resilience.md
sed -n '470,540p' profile-al-dev-shared/skills/al-dev-develop/SKILL.md
sed -n '1,120p' profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Expected: Confirm the existing durable artifacts already named in the shared surface, including `.dev/progress.md`, the dated develop resume pack, and `.dev/*-al-dev-develop-phase4-handoff.md`.

- [ ] **Step 2: Write the new knowledge file with the full contract matrix**

Create `profile-al-dev-shared/knowledge/artifact-contracts.md` with this content:

```markdown
# Artifact Contracts

Shared artifact contract matrix for the main execution skills in `profile-al-dev-shared`.

Use this document when:
- deciding which artifacts a skill may claim as durable output
- resuming a partially completed workflow
- handing work from one skill to another
- deciding whether a final completion or validation claim is supported by current-run evidence

## Rules

1. Do not name a durable output here unless the current workflow already writes it or the implementation in this repo is being updated in the same change set to write it.
2. If multiple resume artifacts can exist, list them in strict read order.
3. If a downstream workflow depends on a handoff artifact, name the exact file pattern it expects.
4. Final completion, validation, “clean”, or “ready” claims require the success evidence listed for the current skill to exist and be read in the current run.
5. If the required handoff artifact or success evidence is missing, stop and report the missing file instead of guessing.

## Contract Matrix

| Skill | Required inputs | Durable outputs | Resume read order | Handoff artifact | Success evidence |
|------|---|---|---|---|---|
| `al-dev-plan` | user requirement, current repo context, `.dev/` write access | `.dev/*-al-dev-plan-solution-plan.md`, `.dev/progress.md` when checkpointing | `.dev/progress.md`, latest `.dev/*-al-dev-plan-solution-plan.md` | `.dev/*-al-dev-plan-solution-plan.md` | latest solution plan file exists, is non-empty, and was read after write in the current run |
| `al-dev-develop` | latest `.dev/*-al-dev-plan-solution-plan.md` | `.dev/progress.md`, `.dev/*-al-dev-develop-progress.md`, `.dev/*-al-dev-develop-checklist.md`, `.dev/*-al-dev-develop-scope.md`, `.dev/*-al-dev-develop-phase4-handoff.md` | `.dev/progress.md`, latest `.dev/*-al-dev-develop-progress.md`, latest `.dev/*-al-dev-develop-checklist.md`, latest `.dev/*-al-dev-develop-scope.md`, latest solution plan only if the resume pack is missing or contradictory | `.dev/*-al-dev-develop-phase4-handoff.md` | current Phase 4 handoff exists, is non-empty, and was read before telling the user implementation is ready for review |
| `al-dev-review-develop` | latest `.dev/*-al-dev-develop-phase4-handoff.md` | `.dev/*-al-dev-develop-code-review.md`, `.dev/compile-errors.log` when compile verification runs | latest `.dev/*-al-dev-develop-phase4-handoff.md`, latest `.dev/*-al-dev-develop-code-review.md` only for context, never as a substitute for the current handoff | `.dev/*-al-dev-develop-code-review.md` | current code-review artifact exists, compile/review result has been read, and the skill has evidence for any clean/ready claim it makes |
| `al-dev-fix` | user bug description, repo context, compile/lint workflow when verification is needed | `.dev/compile-errors.log` when compile verification runs | `.dev/progress.md` only if future resilience work adds it; otherwise resume is request-driven and should not assume durable fix-state artifacts | none | current compile/lint verification output or an explicit bounded verification result has been produced and read before claiming the fix is complete |
| `al-dev-commit` | staged changes, project instructions, optional `.dev/file-sizes.json`, `.dev/compile-errors.log` when AL-affecting | commit-analysis outputs already produced by the workflow, `.dev/compile-errors.log` when Step 4a runs | staged state is authoritative; do not resume from stale commit artifacts without re-reading the staged diff and required context files | commit-ready staged set after the analysis gate; no downstream markdown handoff file | current staged diff has been read, any required compile evidence has been read for the current staged state, and commit-readiness has been confirmed before saying the staged set is ready |
| `al-dev-lint` | current AL project or provided compile log | `.dev/compile-errors.log`, `.dev/*-al-dev-lint-lint-report.md` | provided log path when explicitly supplied, otherwise fresh `.dev/compile-errors.log`, then latest lint report only for context | `.dev/*-al-dev-lint-lint-report.md` | current compile output and current lint report have been read before claiming the project is clean or the lint pass is complete |

## Failure Handling

- Missing required input artifact: stop and report the missing file pattern.
- Missing handoff artifact: refuse the downstream step and name the missing handoff file.
- Missing or stale success evidence: regenerate it when the workflow can, otherwise refuse the final claim.
- Contradictory resume artifacts: stop and ask instead of silently choosing a branch.
```

- [ ] **Step 3: Verify the new file is structurally sound**

Run:

```bash
python3 scripts/validate-knowledge-quality.py --path profile-al-dev-shared/knowledge --strict
grep -n "al-dev-review-develop\|Success evidence\|Handoff artifact" profile-al-dev-shared/knowledge/artifact-contracts.md
```

Expected:
- validator exits `0`
- `grep` shows the matrix headings and all six seeded skill rows

- [ ] **Step 4: Commit the new contract document**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/artifact-contracts.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(workflows): add shared artifact contract matrix"
```

---

### Task 2: Add Final-Gate Discipline to `al-dev-fix` and `al-dev-lint`

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`
- Modify: `profile-al-dev-shared/skills/al-dev-lint/SKILL.md`
- Reference: `profile-al-dev-shared/knowledge/artifact-contracts.md`

- [ ] **Step 1: Read the two target skill openings and summary sections**

Run:

```bash
sed -n '1,140p' profile-al-dev-shared/skills/al-dev-fix/SKILL.md
sed -n '1,160p' profile-al-dev-shared/skills/al-dev-lint/SKILL.md
```

Expected: Confirm where each skill explains intent, verification, and final summary language.

- [ ] **Step 2: Add the contract cross-reference and gate wording to `al-dev-fix`**

Insert this block immediately after the `Intent Preflight` section in `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`:

```markdown
## Artifact Contract

Use `knowledge/artifact-contracts.md` as the source of truth for this skill's
durable outputs and success evidence.

Do not claim the fix is complete, validated, or ready for the next workflow
step until the success evidence named in
`knowledge/artifact-contracts.md` for `al-dev-fix` has been produced and read
for the current run.
```

Also replace the existing verification-oriented line in Step 2:

```markdown
- Verify fix compiles
```

with:

```markdown
- Verify fix using the current-run success evidence required by `knowledge/artifact-contracts.md` for `al-dev-fix` (compile/lint output or other bounded verification result)
```

- [ ] **Step 3: Add the contract cross-reference and gate wording to `al-dev-lint`**

Insert this block immediately after the `Intent Preflight` section in `profile-al-dev-shared/skills/al-dev-lint/SKILL.md`:

```markdown
## Artifact Contract

Use `knowledge/artifact-contracts.md` as the source of truth for this skill's
durable outputs and success evidence.

Do not claim the project is clean, the lint pass is complete, or the result is
ready for the next workflow step until the success evidence named in
`knowledge/artifact-contracts.md` for `al-dev-lint` has been produced and read
for the current run.
```

Then replace the “clean compile” early-exit text:

```text
✅ No lint issues found. Compile clean.
```

with:

```text
No lint issues found in the current compile output. Current-run success evidence read from `.dev/compile-errors.log`.
```

- [ ] **Step 4: Verify the wording landed exactly once in each file**

Run:

```bash
grep -n "Artifact Contract\|Do not claim" profile-al-dev-shared/skills/al-dev-fix/SKILL.md
grep -n "Artifact Contract\|Do not claim" profile-al-dev-shared/skills/al-dev-lint/SKILL.md
```

Expected: each file shows one `Artifact Contract` heading and one `Do not claim` rule.

- [ ] **Step 5: Commit the two skill updates**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/skills/al-dev-fix/SKILL.md \
  profile-al-dev-shared/skills/al-dev-lint/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(skills): add final-gate rules to fix and lint"
```

---

### Task 3: Add Final-Gate Discipline to `al-dev-develop` and `al-dev-review-develop`

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`
- Modify: `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`
- Reference: `profile-al-dev-shared/knowledge/artifact-contracts.md`

- [ ] **Step 1: Read the develop handoff section and review-develop preamble**

Run:

```bash
sed -n '1,120p' profile-al-dev-shared/skills/al-dev-develop/SKILL.md
sed -n '470,540p' profile-al-dev-shared/skills/al-dev-develop/SKILL.md
sed -n '1,120p' profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Expected: Confirm the current Phase 4 handoff wording and the review skill’s prerequisite/output sections.

- [ ] **Step 2: Add the contract section to `al-dev-develop`**

Insert this block after `## Prerequisites` in `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`:

```markdown
## Artifact Contract

Use `knowledge/artifact-contracts.md` as the source of truth for this skill's
durable outputs, resume read order, handoff artifact, and success evidence.

Do not claim implementation is complete or ready for `/al-dev-review-develop`
until the success evidence named in `knowledge/artifact-contracts.md` for
`al-dev-develop` has been produced and read for the current run.
```

Then tighten the Phase 4 output sentence:

```markdown
**Next step:** Dispatch to `/al-dev-review-develop` to begin compilation verification,
multi-reviewer code review, and code-review output generation (Phases 5–10).
```

to:

```markdown
**Next step:** Dispatch to `/al-dev-review-develop` only after reading the current
Phase 4 handoff artifact and confirming it satisfies the `al-dev-develop`
success evidence in `knowledge/artifact-contracts.md`.
```

- [ ] **Step 3: Add the contract section to `al-dev-review-develop`**

Insert this block after `## Prerequisites` in `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`:

```markdown
## Artifact Contract

Use `knowledge/artifact-contracts.md` as the source of truth for this skill's
required handoff artifact, durable outputs, and success evidence.

Do not claim the review is complete, validated, clean, or ready for the next
workflow step until the success evidence named in
`knowledge/artifact-contracts.md` for `al-dev-review-develop` has been
produced and read for the current run.
```

Also replace the one-line `## Outputs` section body:

```markdown
`.dev/$(date +%Y-%m-%d)-al-dev-develop-code-review.md` — Synthesized review findings from all three reviewers
```

with:

```markdown
`.dev/$(date +%Y-%m-%d)-al-dev-develop-code-review.md` — synthesized review findings from all three reviewers; this file is also the downstream handoff artifact named in `knowledge/artifact-contracts.md` and must be read before any final clean/ready claim.
```

- [ ] **Step 4: Verify the handoff and gate wording**

Run:

```bash
grep -n "Artifact Contract\|Phase 4 handoff artifact\|Do not claim" profile-al-dev-shared/skills/al-dev-develop/SKILL.md
grep -n "Artifact Contract\|Do not claim\|code-review.md" profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Expected: the develop skill references the handoff artifact and the review skill references the code-review artifact as current-run success evidence.

- [ ] **Step 5: Commit the develop/review skill updates**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
  profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(skills): tie develop and review flow to artifact contracts"
```

---

### Task 4: Align `al-dev-commit` to the Shared Contract

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`
- Reference: `profile-al-dev-shared/knowledge/artifact-contracts.md`

- [ ] **Step 1: Read the intent-preflight and Step 4a sections**

Run:

```bash
sed -n '1,170p' profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```

Expected: Confirm the existing compile gate is already present and only needs to be tied to the new contract doc.

- [ ] **Step 2: Add the contract section near the top of the skill**

Insert this block immediately after `## Intent Preflight`:

```markdown
## Artifact Contract

Use `knowledge/artifact-contracts.md` as the source of truth for this skill's
required staged-state checks and success evidence.

Do not claim the staged set is ready, validated, or safe to commit until the
success evidence named in `knowledge/artifact-contracts.md` for
`al-dev-commit` has been produced and read for the current staged state.
```

- [ ] **Step 3: Tighten the Step 4a critical rule**

Replace the final Step 4a sentence:

```markdown
Critical rule: never claim "clean compile" or "zero errors" without reading the actual log file produced for the current working tree state.
```

with:

```markdown
Critical rule: never claim the staged set is ready, "clean compile", or "zero errors"
without reading the actual success evidence required by
`knowledge/artifact-contracts.md` for the current staged state.
```

- [ ] **Step 4: Verify the new wording**

Run:

```bash
grep -n "Artifact Contract\|current staged state\|Do not claim" profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```

Expected: one contract section and one staged-state final-gate rule.

- [ ] **Step 5: Commit the commit-skill wording**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/skills/al-dev-commit/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(commit): align commit gate with artifact contract"
```

---

### Task 5: Publish the Canonical Example Run Bundle

**Files:**
- Create: `docs/example-runs/al-dev-core/README.md`
- Create: `docs/example-runs/al-dev-core/sample-solution-plan.md`
- Create: `docs/example-runs/al-dev-core/sample-progress.md`
- Create: `docs/example-runs/al-dev-core/sample-checklist.md`
- Create: `docs/example-runs/al-dev-core/sample-scope.md`
- Create: `docs/example-runs/al-dev-core/sample-code-review.md`
- Reference: `profile-al-dev-shared/knowledge/artifact-contracts.md`

- [ ] **Step 1: Create the directory and read the contract doc**

Run:

```bash
mkdir -p docs/example-runs/al-dev-core
sed -n '1,240p' profile-al-dev-shared/knowledge/artifact-contracts.md
```

Expected: The example directory exists and the contract doc is available as the content source of truth.

- [ ] **Step 2: Write the example bundle files**

Create `docs/example-runs/al-dev-core/README.md`:

```markdown
# AL Dev Core Example Run

This bundle shows the minimum durable artifact set for a healthy plan -> develop
-> review flow in `profile-al-dev-shared`.

Sequence:
1. `sample-solution-plan.md` defines the approved work.
2. `sample-checklist.md` and `sample-scope.md` capture execution boundaries.
3. `sample-progress.md` shows the latest resume checkpoint.
4. `sample-code-review.md` shows the final review artifact that supports a
   completion claim.

These files are synthetic examples. They are not raw session dumps.
```

Create `docs/example-runs/al-dev-core/sample-solution-plan.md`:

```markdown
# Example Solution Plan

Goal: Add a posting-date validation to a sales-order extension.

Files:
- `src/Codeunit/SalesPostingGuard.Codeunit.al`
- `src/PageExtension/SalesOrderExt.PageExt.al`

Acceptance criteria:
- validation blocks posting dates before work date
- page surfaces the validation message consistently
```

Create `docs/example-runs/al-dev-core/sample-checklist.md`:

```markdown
# Example Develop Checklist

- [x] Read approved solution plan
- [x] Identify in-scope AL objects
- [x] Dispatch developer
- [x] Verify no out-of-scope file edits
- [x] Write Phase 4 handoff artifact
```

Create `docs/example-runs/al-dev-core/sample-scope.md`:

```markdown
# Example Scope Boundary

In scope:
- `src/Codeunit/SalesPostingGuard.Codeunit.al`
- `src/PageExtension/SalesOrderExt.PageExt.al`

Out of scope:
- table schema changes
- posting setup refactors
- unrelated lint cleanup
```

Create `docs/example-runs/al-dev-core/sample-progress.md`:

```markdown
# Example Progress Checkpoint

## Progress Checkpoint

**Completed phases:** Phase 1 - Read Context, Phase 3 - Developer Dispatch, Phase 4 - Handoff Written

**Current state:** Implementation finished and the Phase 4 handoff artifact was reviewed for the current run.

**Next step:** Run `/al-dev-review-develop` using the Phase 4 handoff artifact.

**Pending decisions:** none
```

Create `docs/example-runs/al-dev-core/sample-code-review.md`:

```markdown
# Example Code Review

Result: Ready for user review

Compile summary:
- Errors: 0
- Warnings: 1
- Detailed log: `.dev/compile-errors.log`

Review findings:
- Security: no blocking findings
- AL expert: naming consistent with plan
- Performance: no blocking findings
```

- [ ] **Step 3: Verify the example bundle matches the contract model**

Run:

```bash
find docs/example-runs/al-dev-core -maxdepth 1 -type f | sort
grep -n "Phase 4 handoff\|Ready for user review\|Progress Checkpoint" docs/example-runs/al-dev-core/*
```

Expected:
- six files exist
- `grep` confirms the example bundle includes resume, handoff, and final-review concepts

- [ ] **Step 4: Commit the example bundle**

```bash
git -C /Users/russelllaing/al-dev-shared add docs/example-runs/al-dev-core
git -C /Users/russelllaing/al-dev-shared commit -m "docs(example-runs): add shared artifact bundle example"
```

---

### Task 6: Add Regression Coverage on Existing Test Surfaces

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-fix/tests/scenarios.yaml`
- Modify: `profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml`
- Modify: `profile-al-dev-shared/skills/al-dev-lint/tests/scenarios.yaml`
- Modify: `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml`
- Modify: `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml`
- Reference: `profile-al-dev-shared/knowledge/skill-test-format.md`

- [ ] **Step 1: Read the scenario schema before editing**

Run:

```bash
sed -n '1,140p' profile-al-dev-shared/knowledge/skill-test-format.md
sed -n '1,220p' profile-al-dev-shared/skills/al-dev-fix/tests/scenarios.yaml
sed -n '1,220p' profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml
sed -n '1,220p' profile-al-dev-shared/skills/al-dev-lint/tests/scenarios.yaml
sed -n '1,220p' profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml
```

Expected: Confirm the current schema and reuse the same `skill:` / `scenarios:` layout.

- [ ] **Step 2: Add final-gate scenarios to the three per-skill scenario files**

Append this scenario to `profile-al-dev-shared/skills/al-dev-fix/tests/scenarios.yaml`:

```yaml
  - id: fix-blocks-final-claim-without-current-verification
    status: golden
    user_prompt: "Fix the bug, but do not call it complete unless you have current verification evidence."
    expected_artifacts: []
    must_invoke_agent: al-dev-shared:al-dev-developer
    notes: "Final-gate regression. The skill may implement the fix path, but must not claim completion without current-run compile/lint or other bounded success evidence."
```

Append this scenario to `profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml`:

```yaml
  - id: develop-requires-phase4-handoff-before-ready-claim
    status: golden
    user_prompt: "Implement the approved plan and do not say it is ready for review unless the Phase 4 handoff artifact exists and has been read."
    expected_artifacts:
      - ".dev/*-al-dev-develop-phase4-handoff.md"
      - ".dev/*-al-dev-develop-code-review.md"
    must_invoke_agent:
      - al-dev-shared:al-dev-developer
      - al-dev-shared:al-dev-security-reviewer
      - al-dev-shared:al-dev-expert-reviewer
      - al-dev-shared:al-dev-performance-reviewer
    notes: "Final-gate regression. The develop flow must produce and read the Phase 4 handoff before making a ready-for-review claim."
```

Append this scenario to `profile-al-dev-shared/skills/al-dev-lint/tests/scenarios.yaml`:

```yaml
  - id: lint-blocks-clean-claim-without-current-log
    status: golden
    user_prompt: "Run lint, but do not call it clean unless you read the current compile log."
    expected_artifacts:
      - ".dev/compile-errors.log"
    must_invoke_agent: al-dev-shared:al-dev-diagnostics-fixer
    notes: "Final-gate regression. A clean/complete claim must be tied to the current compile log and lint report."
```

Do not add a new `al-dev-review-develop/tests/scenarios.yaml` in this change; the design says to use existing test surfaces only.

- [ ] **Step 3: Tighten the existing commit scenarios and trigger corpus**

In `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml`, replace the `notes` values for the last two scenarios with:

```yaml
    notes: "Compile gate regression. Harness pre-seeds staged .al files that contain compile errors. Skill must read current staged-state success evidence from `.dev/compile-errors.log`, refuse any ready-to-commit claim, and halt before `al-dev-commit-agent-execute`."
```

and:

```yaml
    notes: "Docs-only optimization regression. Harness pre-seeds only non-AL staged changes. Skill may skip Step 4a, but it still must base any ready-to-commit claim on the current staged diff and required staged-state evidence."
```

Then append these corpus entries to `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml`:

```yaml
  - prompt: "fix the bug, but do not say it is done unless you verified it this run"
    expected: al-dev-fix
  - prompt: "implement the approved plan and only call it ready when the handoff artifact exists"
    expected: al-dev-develop
  - prompt: "run lint, but do not claim clean without reading the current compile log"
    expected: al-dev-lint
  - prompt: "commit the staged changes, but only if the current staged-state evidence says they are ready"
    expected: al-dev-commit
```

- [ ] **Step 4: Validate all YAML files**

Run:

```bash
python3 -c "import yaml; yaml.safe_load(open('profile-al-dev-shared/skills/al-dev-fix/tests/scenarios.yaml'))"
python3 -c "import yaml; yaml.safe_load(open('profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml'))"
python3 -c "import yaml; yaml.safe_load(open('profile-al-dev-shared/skills/al-dev-lint/tests/scenarios.yaml'))"
python3 -c "import yaml; yaml.safe_load(open('profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml'))"
python3 -c "import yaml; yaml.safe_load(open('profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml'))"
echo "YAML valid"
```

Expected: `YAML valid`

- [ ] **Step 5: Commit the regression fixtures**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/skills/al-dev-fix/tests/scenarios.yaml \
  profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml \
  profile-al-dev-shared/skills/al-dev-lint/tests/scenarios.yaml \
  profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml \
  profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml
git -C /Users/russelllaing/al-dev-shared commit -m "test(skills): add artifact-contract gate regressions"
```

---

### Task 7: Run Final Validation Across the Shared Surface

**Files:**
- Verify: `profile-al-dev-shared/knowledge/artifact-contracts.md`
- Verify: `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`
- Verify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`
- Verify: `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`
- Verify: `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`
- Verify: `profile-al-dev-shared/skills/al-dev-lint/SKILL.md`
- Verify: `docs/example-runs/al-dev-core/*`
- Verify: scenario YAML files from Task 6

- [ ] **Step 1: Run the shared validators**

Run:

```bash
python3 scripts/validate-knowledge-quality.py --path profile-al-dev-shared/knowledge --strict
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Expected:
- both commands exit `0`
- no harness-specific leakage is reported

- [ ] **Step 2: Spot-check that every skill references the contract doc**

Run:

```bash
rg -n "knowledge/artifact-contracts.md" \
  profile-al-dev-shared/skills/al-dev-fix/SKILL.md \
  profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
  profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md \
  profile-al-dev-shared/skills/al-dev-commit/SKILL.md \
  profile-al-dev-shared/skills/al-dev-lint/SKILL.md
```

Expected: five hits, one per targeted skill file.

- [ ] **Step 3: Verify the example bundle and contract terminology line up**

Run:

```bash
rg -n "Success evidence|Handoff artifact|Resume read order" profile-al-dev-shared/knowledge/artifact-contracts.md
rg -n "Ready for user review|Phase 4 handoff|Progress Checkpoint" docs/example-runs/al-dev-core
```

Expected: the contract doc exposes all three core concepts, and the example bundle shows the handoff/checkpoint/review terminology consistently.

- [ ] **Step 4: Final persistence check**

Run:

```bash
git status --short
```

Expected: only the planned knowledge, skill, example-run, and scenario files are modified or newly created.

- [ ] **Step 5: Commit any validation-driven touchups**

If validation required no content changes, do not create an extra commit.

If validation required small wording or YAML touchups, commit them with:

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared docs/example-runs
git -C /Users/russelllaing/al-dev-shared commit -m "chore(validation): align artifact-contract updates"
```

---

## Self-Review

### Spec Coverage

- Shared artifact contract matrix: covered by Task 1.
- Final-gate claim discipline in the five named skills: covered by Tasks 2, 3, and 4.
- Canonical example run bundle: covered by Task 5.
- Focused trigger/scenario coverage using existing test surfaces: covered by Task 6.
- Shared-surface validation and harness-neutrality checks: covered by Task 7.

### Placeholder Scan

- No `TODO`, `TBD`, “implement later”, or “similar to Task N” placeholders remain.
- Every code-edit step includes exact insertion or replacement text.
- Every verification step includes exact commands and expected outcomes.

### Type Consistency

- Contract terminology is consistent across the plan: `required inputs`, `durable outputs`, `resume read order`, `handoff artifact`, and `success evidence`.
- The same file pattern is used consistently for the develop handoff artifact: `.dev/*-al-dev-develop-phase4-handoff.md`.
- The same final review artifact is used consistently for review completion: `.dev/*-al-dev-develop-code-review.md`.
