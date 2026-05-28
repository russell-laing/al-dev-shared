# Design: Targeted Hybrid Improvements for `profile-al-dev-shared`

**Date:** 2026-05-28  
**Goal:** Address three recurring friction patterns from the Claude Code usage review without duplicating guidance that already exists in the shared profile  
**Scope:** 3 bounded changes affecting 7 files total  
**Effort:** ~90 minutes  
**Impact:** Adds an actual pre-commit compile gate, tightens existing investigation guidance, and closes one remaining intent-preflight gap

---

## Reviewed Baseline

This design starts from the current shared-profile state, not from the usage report alone.

Already present in `profile-al-dev-shared`:

- `knowledge/compile-lint-procedure.md` already defines stale-log checks, file-based compile verification, summary-only reporting, and a hard block on compile errors.
- `skills/al-dev-investigate/SKILL.md` already requires competing hypotheses, evidence gathering, findings-file output, and reconciliation against the regression timeline.
- `knowledge/intent-preflight.md` already defines `REVIEW` vs `EDIT` vs `COMMIT` and is already consumed by `al-dev-plan`, `al-dev-develop`, `al-dev-fix`, and `al-dev-commit`.
- `knowledge/skill-test-trigger-corpus.yaml` and existing scenario files already cover several review-only and near-miss routing cases.

Because these baselines already exist, this design avoids creating a second source of truth. Each change below is framed as an enforcement or refinement of existing shared-profile behavior.

---

## Problem Statement

The usage review still points to three real friction patterns:

1. **Post-commit compilation surprises**
   - Agents sometimes report a clean result before a later compile or stop hook proves otherwise.
   - The shared profile already has compile-discipline guidance, but `al-dev-commit` does not currently enforce it before commit orchestration.

2. **Misdiagnosed first fixes**
   - Some bugs still consume a full implement-commit cycle before the actual cause is isolated.
   - The investigation skill already contains the right structure, but the profile can make its evidence-first expectation more explicit and easier to test.

3. **Intent and artifact mismatches**
   - Review-only or audit prompts can still be phrased in ways that resemble implementation work.
   - The profile already has intent-preflight, but `al-dev-lint` does not currently apply it and the trigger corpus can be sharpened around spec/plan/review near-misses.

---

## Solution Overview

Three bounded changes strengthen existing knowledge documents and skills without introducing new cross-cutting frameworks:

| Change | Existing Surface | Update | Intended Effect |
|---|---|---|---|
| **1. Pre-Commit Compile Gate** | `knowledge/compile-lint-procedure.md`, `skills/al-dev-commit/SKILL.md` | Reuse existing compile guidance from the commit workflow before commit grouping or execution | Converts compile discipline from documentation into an actual commit gate |
| **2. Investigation Guidance Tightening** | `skills/al-dev-investigate/SKILL.md` | Clarify that the current investigation workflow is the root-cause framework and make evidence-first expectations more explicit | Reduces drift from the intended investigation pattern without adding a duplicate knowledge file |
| **3. Intent-Preflight Completion** | `knowledge/intent-preflight.md`, `skills/al-dev-lint/SKILL.md`, `knowledge/skill-test-trigger-corpus.yaml` | Extend existing intent-preflight guidance and apply it to the remaining entry skill gap | Improves routing on review/audit/execute near-misses using shared-profile skill names only |

---

## Change 1: Pre-Commit Compile Gate

### Current State

`knowledge/compile-lint-procedure.md` already says:

- stale logs must be rejected before use
- compile output must be written to `.dev/compile-errors.log`
- `Error` diagnostics are hard blockers
- compile reporting must summarize counts and representative diagnostics instead of replaying the full log

The missing piece is not more compile doctrine. The missing piece is that `al-dev-commit` does not currently require this verification before it starts commit analysis and execution.

### Recommended Update

**Primary file:** `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`

Add a new compile gate after staged-file presence is confirmed and only for AL-affecting staged changes:

```markdown
## Step 4a — Pre-Commit Compile Verification

Run this gate only when the staged set includes `.al` files or other files that can affect AL compilation.
Skip it for docs-only or other non-AL staged changes.

Run this gate after the workflow has already confirmed that staged files exist.

Before dispatching commit agents or confirming commit groups for an AL-affecting staged set:

1. Apply `knowledge/compile-lint-procedure.md`
2. Produce a fresh `.dev/compile-errors.log` if the current log is absent or stale
3. Read the log and report:
   - `Errors:` count
   - `Warnings:` count
   - up to 3 representative diagnostics
   - `Detailed log:` `.dev/compile-errors.log`
4. If `Errors > 0`, stop the commit workflow and tell the user the staged changes are not ready to commit
5. Only continue to the existing commit workflow when the compile result shows zero errors

Critical rule: never claim "clean compile" or "zero errors" without reading the actual log file produced for the current working tree state.
```

### Supporting Knowledge Update

**Optional small edit:** `profile-al-dev-shared/knowledge/compile-lint-procedure.md`

Do not add a large new section that restates the whole document. Add only a short cross-reference note near the summary/reporting rules:

```markdown
`al-dev-commit` must consume this procedure before any commit orchestration begins.
```

### Test Coverage

**Update:** `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml`

Add a scenario asserting that:

- an AL-affecting commit request surfaces compile verification before commit execution
- the skill surfaces a bounded compile summary
- the workflow does not dispatch `al-dev-commit-agent-execute` while compile errors remain
- docs-only staged changes continue to bypass AL compile gating

---

## Change 2: Investigation Guidance Tightening

### Current State

`skills/al-dev-investigate/SKILL.md` already includes the real root-cause workflow:

- target confirmation
- regression timeline capture
- 2-4 competing hypotheses
- evidence-based confirmation or rejection
- findings-file output in `.dev/`
- reconciliation when the diagnosis appears pre-existing or environmental

Creating `knowledge/root-cause-investigation.md` would duplicate this workflow and create a second authoritative description.

### Recommended Update

**Primary file:** `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md`

Tighten the existing skill with a short framing addition near the start:

```markdown
This skill itself is the shared-profile root-cause framework.
Do not create an ad-hoc implementation hypothesis and jump straight to fixes.
Use the regression timeline, competing-hypothesis, and evidence gates below before recommending any implementation path.
```

Add one explicit enforcement line where findings are synthesized:

```markdown
Do not present a fix path until the findings file contains at least one confirmed or best-supported hypothesis and the rejected alternatives are named.
```

### Deliberate Non-Changes

Do not:

- create `knowledge/root-cause-investigation.md`
- add a second findings template
- add external-tool requirements that the current skill does not actually enforce
- recast existing behavior as a net-new framework

### Test Coverage

If scenario coverage is added later, it should verify:

- multi-hypothesis structure is preserved for unclear bugs
- review-only or inconclusive investigations do not skip straight to implementation guidance
- findings output remains the single durable artifact

This can be deferred if no investigate scenario harness exists yet.

---

## Change 3: Intent-Preflight Completion

### Current State

The shared profile already has a solid intent-preflight base:

- `knowledge/intent-preflight.md` defines `REVIEW`, `EDIT`, and `COMMIT`
- `al-dev-plan`, `al-dev-develop`, `al-dev-fix`, and `al-dev-commit` already apply it
- the trigger corpus already contains review-only and near-miss prompts

The remaining gap is narrower than the original draft suggested:

- `al-dev-lint` does not currently apply intent preflight
- the corpus does not yet lock in spec/plan/review wording specific to this friction pattern

### Recommended Update

**Files:**

- `profile-al-dev-shared/knowledge/intent-preflight.md`
- `profile-al-dev-shared/skills/al-dev-lint/SKILL.md`
- `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml`

#### 1. Extend `intent-preflight.md`

Add a short subsection focused on artifact mismatch using shared-profile terminology only:

```markdown
## Artifact Mismatch Checks

Before continuing, compare the user's wording with the artifact they pointed to:

- design/spec document + "implement/execute" -> confirm whether the user wants planning output or implementation
- plan document + "review/audit only" -> treat as `REVIEW` unless the user confirms implementation
- code or diagnostics + "summarize what failed" -> treat as `REVIEW`, not `EDIT`

Use existing shared-profile skills when clarifying. Do not route through external skill names that are outside this profile's published surface.
```

This keeps the current intent model intact and avoids introducing foreign routing names such as `brainstorming`, `writing-plans`, or `executing-plans`.

Also extend the `Skill Defaults` table so it explicitly includes:

```markdown
| `al-dev-lint` | `EDIT` |
```

#### 2. Add intent preflight to `al-dev-lint`

At the top of `skills/al-dev-lint/SKILL.md`, add:

```markdown
## Intent Preflight

Before compiling, fixing diagnostics, or writing a lint report, apply `knowledge/intent-preflight.md`.

Default intent for this skill is `EDIT`. If the request is review-only, explanation-only, or asks to assess diagnostics without changing files, stop and ask the intent-mismatch prompt before any mutating action.
```

#### 3. Expand the trigger corpus

Add near-miss prompts to `knowledge/skill-test-trigger-corpus.yaml` for cases like:

- "review this spec and tell me if it is ready to implement"
- "audit this plan for risk only"
- "summarize the compile failures without fixing anything"

Expected routing should stay within the shared profile's current intent model, typically `NONE` for review-only prompts or the existing profile skill when the wording clearly requests action.

### Test Coverage

Reuse existing scenario surfaces where possible:

- keep `plan-rejects-validation-audit-misfire`
- keep `develop-rejects-review-only-misfire`
- add a lint-specific review-only scenario if the lint harness supports it

---

## Files Changed Summary

| File | Type | Change |
|---|---|---|
| `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` | Skill | Add a real pre-commit compile verification gate that consumes existing compile guidance |
| `profile-al-dev-shared/knowledge/compile-lint-procedure.md` | Knowledge | Add `al-dev-commit` to the applicability note and a small cross-reference; no large duplicate section |
| `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md` | Skill | Tighten framing so the existing skill remains the single root-cause framework |
| `profile-al-dev-shared/knowledge/intent-preflight.md` | Knowledge | Add artifact-mismatch clarifications using shared-profile terminology |
| `profile-al-dev-shared/skills/al-dev-lint/SKILL.md` | Skill | Add intent-preflight before any mutating lint path |
| `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml` | Knowledge/Test | Add near-miss prompts covering spec/plan/review phrasing |
| `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml` | Test | Add commit-gate regression coverage |

**Total:** 7 files changed  
**New files:** 0

---

## Success Criteria

After these changes are implemented:

1. **Pre-Commit Compile Gate**
   - `al-dev-commit` explicitly runs compile verification for AL-affecting staged changes before commit execution
   - compile results are reported from `.dev/compile-errors.log` using the existing summary pattern
   - docs-only staged changes do not trigger AL compile verification
   - commit execution does not proceed while compile errors remain

2. **Investigation Guidance Tightening**
   - `al-dev-investigate` is clearly documented as the shared-profile root-cause framework
   - no duplicate root-cause knowledge document is introduced
   - the skill continues to require hypotheses, evidence, and findings-file output before fix guidance

3. **Intent-Preflight Completion**
   - `al-dev-lint` gains the same intent-preflight discipline already used by the other entry skills
   - artifact-mismatch wording is covered in `intent-preflight.md`
   - trigger-corpus coverage improves for spec/plan/review near-miss prompts

---

## Implementation Notes

- Changes remain harness-neutral by using only shared-profile concepts and paths.
- This design intentionally avoids introducing external Superpowers routing names into `profile-al-dev-shared`.
- The largest net-new behavioral change is the `al-dev-commit` compile gate.
- The other two changes are refinements to existing shared-profile behavior, not new frameworks.

---

## Timeline

- **Commit gate update + scenario:** ~35 min
- **Investigation skill tightening:** ~15 min
- **Intent-preflight + lint + trigger corpus:** ~40 min
- **Total:** ~90 min
