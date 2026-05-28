# Profile-al-dev-shared Hybrid Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Strengthen three existing friction points in the shared profile by enforcing compile discipline before commits, tightening investigation guidance, and completing the intent-preflight model across all entry skills.

**Architecture:** This design avoids duplicating existing knowledge by refining and enforcing what already exists. The compile gate reuses the existing `compile-lint-procedure.md` workflow; investigation tightening keeps that skill as the single root-cause framework; intent-preflight completion extends the existing model to lint and expands the trigger corpus.

**Tech Stack:** YAML test scenarios, Markdown skill documentation, existing shared-profile knowledge surfaces

---

## File Structure

| File | Responsibility |
|------|---|
| `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` | Pre-commit compile verification step; blocks commits with AL errors |
| `profile-al-dev-shared/knowledge/compile-lint-procedure.md` | Cross-reference noting that commit workflow applies this |
| `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md` | Framing that this skill IS the root-cause framework |
| `profile-al-dev-shared/knowledge/intent-preflight.md` | Artifact-mismatch guidance; lint skill default |
| `profile-al-dev-shared/skills/al-dev-lint/SKILL.md` | Intent-preflight section before mutating lint paths |
| `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml` | Expanded near-miss prompts for spec/plan/review wording |
| `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml` | Compile-gate regression coverage |

---

## Task 1: Add Cross-Reference to compile-lint-procedure.md

**Files:**
- Modify: `profile-al-dev-shared/knowledge/compile-lint-procedure.md`

- [ ] **Step 1: Read the compile-lint-procedure.md file**

Run: `head -50 profile-al-dev-shared/knowledge/compile-lint-procedure.md`

Locate the summary/reporting section (lines discussing "Summary-Only Reporting" or "Hard Blocks").

- [ ] **Step 2: Find the exact insertion point**

Read the full file to find where compile reporting rules are finalized. The cross-reference should go near the end, right after the hard-block rules about compile errors.

Expected location: around the line that says "If any diagnostic is an error, do not claim success until the error is resolved."

- [ ] **Step 3: Add the cross-reference note**

Edit the file to add this line after the hard-block error rules (before any closing section):

```markdown
**Note:** `al-dev-commit` must consume this procedure before any commit orchestration begins.
```

This cross-reference is intentionally brief — it names the consumer without restating the whole workflow.

- [ ] **Step 4: Verify the edit**

Run: `grep -n "al-dev-commit" profile-al-dev-shared/knowledge/compile-lint-procedure.md`

Expected: One line showing the new cross-reference.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/compile-lint-procedure.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(compile-lint): add al-dev-commit cross-reference

Note that al-dev-commit applies this procedure before commit execution.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Add Step 4a Compile Gate to al-dev-commit/SKILL.md

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`

- [ ] **Step 1: Read the skill to find the insertion point**

Run: `grep -n "^## Step" profile-al-dev-shared/skills/al-dev-commit/SKILL.md | head -10`

This shows the current step structure. The compile gate should go after "Step 4" (or whichever step confirms staged files) and before commit dispatch.

- [ ] **Step 2: Locate the exact line after Step 4 or the staged-file presence confirmation**

Read the skill file to find where the workflow confirms staged files exist. The compile gate should be inserted right after that point.

Expected: A section discussing staged files or commit group analysis.

- [ ] **Step 3: Insert the compile gate section**

Add this complete section at the identified insertion point (after staged-file presence is confirmed, before commit analysis/dispatch):

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

- [ ] **Step 4: Verify the insertion**

Run: `grep -A 5 "Step 4a" profile-al-dev-shared/skills/al-dev-commit/SKILL.md`

Expected: The compile gate section appears correctly.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/skills/al-dev-commit/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(al-dev-commit): add pre-commit compile verification gate

Step 4a enforces compile discipline before commit orchestration by requiring
a fresh compile check for AL-affecting staged changes. Reuses existing
compile-lint-procedure.md and blocks commits with errors.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Add Compile-Gate Scenario to al-dev-commit Test Suite

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml`

- [ ] **Step 1: Read the existing scenarios.yaml to understand the format**

Run: `head -30 profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml`

Understand the existing YAML structure for scenarios (scenario name, trigger, expected assertion, etc.).

- [ ] **Step 2: Identify the insertion point**

Read the full file to see where new scenarios should be added (typically at the end, but follow the existing structure).

- [ ] **Step 3: Add the compile-gate regression scenario**

Add this complete scenario to the file:

```yaml
compile_gate_blocks_errors:
  trigger: |
    AL project with staged .al files that have compile errors
  workflow:
    - confirm staged files include .al files
    - run Step 4a compile verification
    - read .dev/compile-errors.log
  assertions:
    - compile verification surfaces before commit dispatch
    - error count is reported from the log file
    - up to 3 representative diagnostics are displayed
    - dispatch to al-dev-commit-agent-execute does not occur while errors remain
    - user is told: "staged changes are not ready to commit"

docs_only_commits_skip_compile_gate:
  trigger: |
    Commit request with only docs, markdown, or non-AL staged changes
  workflow:
    - confirm staged set includes no .al files
    - skip Step 4a compile verification
    - proceed to existing commit workflow
  assertions:
    - compile gate is skipped
    - commit orchestration proceeds without AL compile check
    - docs-only changes are not blocked by AL compilation state
```

- [ ] **Step 4: Verify the YAML syntax**

Run: `python3 -c "import yaml; yaml.safe_load(open('profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml'))" && echo "YAML valid"`

Expected: "YAML valid"

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml
git -C /Users/russelllaing/al-dev-shared commit -m "test(al-dev-commit): add compile-gate regression scenarios

Two scenarios: compile gate blocks errors and surfaces before dispatch;
docs-only commits skip AL compile verification.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Tighten al-dev-investigate/SKILL.md Framing

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md`

- [ ] **Step 1: Read the skill to find the opening section**

Run: `head -50 profile-al-dev-shared/skills/al-dev-investigate/SKILL.md`

Locate the first major section or introduction where the skill describes its purpose.

- [ ] **Step 2: Find the insertion point for the framing line**

Read the full skill to identify where the root-cause workflow is introduced. The framing addition should go near the start, before the detailed steps.

Expected: A section titled something like "## Workflow", "## Investigation Process", or similar.

- [ ] **Step 3: Add the framing statement**

Insert this text near the beginning of the skill body (before the detailed steps):

```markdown
This skill itself is the shared-profile root-cause framework.
Do not create an ad-hoc implementation hypothesis and jump straight to fixes.
Use the regression timeline, competing-hypothesis, and evidence gates below before recommending any implementation path.
```

- [ ] **Step 4: Find the findings synthesis section**

Locate the section where the skill describes synthesizing findings and presenting recommendations.

Expected: A section discussing how to present the diagnosis and next steps.

- [ ] **Step 5: Add the enforcement line**

Insert this line at the point where findings are synthesized and recommendations are about to be presented:

```markdown
Do not present a fix path until the findings file contains at least one confirmed or best-supported hypothesis and the rejected alternatives are named.
```

- [ ] **Step 6: Verify both insertions are in place**

Run: `grep -n "This skill itself is the shared-profile root-cause framework" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md`

Run: `grep -n "Do not present a fix path until" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md`

Expected: Both lines appear in the file.

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(al-dev-investigate): clarify as shared-profile root-cause framework

Add framing that this skill IS the root-cause framework, not a starting
point for ad-hoc hypotheses. Enforce that findings must be complete before
fix guidance is presented.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Extend intent-preflight.md with Artifact-Mismatch Section

**Files:**
- Modify: `profile-al-dev-shared/knowledge/intent-preflight.md`

- [ ] **Step 1: Read the intent-preflight file**

Run: `cat profile-al-dev-shared/knowledge/intent-preflight.md`

Understand the current structure and sections.

- [ ] **Step 2: Identify the insertion point**

Locate where to add the new "Artifact Mismatch Checks" section. It should go near the end, after the main intent definitions but before any closing remarks.

- [ ] **Step 3: Add the artifact-mismatch section**

Insert this section at the identified point:

```markdown
## Artifact Mismatch Checks

Before continuing, compare the user's wording with the artifact they pointed to:

- design/spec document + "implement/execute" → confirm whether the user wants planning output or implementation
- plan document + "review/audit only" → treat as `REVIEW` unless the user confirms implementation
- code or diagnostics + "summarize what failed" → treat as `REVIEW`, not `EDIT`

Use existing shared-profile skills when clarifying. Do not route through external skill names that are outside this profile's published surface.
```

- [ ] **Step 4: Verify the insertion**

Run: `grep -A 5 "Artifact Mismatch Checks" profile-al-dev-shared/knowledge/intent-preflight.md`

Expected: The new section appears correctly.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/intent-preflight.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(intent-preflight): add artifact-mismatch checks

New section clarifies how to detect and handle intent/artifact mismatches
when spec/plan/code artifacts conflict with user wording.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Add al-dev-lint to Intent-Preflight Skill Defaults Table

**Files:**
- Modify: `profile-al-dev-shared/knowledge/intent-preflight.md`

- [ ] **Step 1: Find the Skill Defaults table**

Run: `grep -n "Skill Defaults" profile-al-dev-shared/knowledge/intent-preflight.md`

Expected: Shows the line number of the table header.

- [ ] **Step 2: Read the table structure**

Read the table to understand its format (skill name, default intent).

Expected format:
```markdown
| Skill | Default Intent |
|-------|---|
| `al-dev-fix` | `EDIT` |
```

- [ ] **Step 3: Add al-dev-lint to the table**

Add this row to the table (in alphabetical order or at the end):

```markdown
| `al-dev-lint` | `EDIT` |
```

- [ ] **Step 4: Verify the table syntax and alignment**

Run: `grep -A 10 "Skill Defaults" profile-al-dev-shared/knowledge/intent-preflight.md | head -20`

Expected: The table includes `al-dev-lint` with `EDIT` as the default.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/intent-preflight.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(intent-preflight): add al-dev-lint to skill defaults table

al-dev-lint defaults to EDIT intent. This change is part of extending
intent-preflight to all entry skills.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Add Intent-Preflight Section to al-dev-lint/SKILL.md

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-lint/SKILL.md`

- [ ] **Step 1: Read the al-dev-lint skill**

Run: `head -50 profile-al-dev-shared/skills/al-dev-lint/SKILL.md`

Understand the opening sections and where to add the intent-preflight step.

- [ ] **Step 2: Find the insertion point**

Locate the beginning of the main workflow (before any steps or major action sections). The intent-preflight section should go at the very start, right after any introductory text.

- [ ] **Step 3: Add the intent-preflight section**

Insert this section at the top of the workflow (before any lint or fix steps):

```markdown
## Intent Preflight

Before compiling, fixing diagnostics, or writing a lint report, apply `knowledge/intent-preflight.md`.

Default intent for this skill is `EDIT`. If the request is review-only, explanation-only, or asks to assess diagnostics without changing files, stop and ask the intent-mismatch prompt before any mutating action.
```

- [ ] **Step 4: Verify the insertion**

Run: `grep -A 3 "Intent Preflight" profile-al-dev-shared/skills/al-dev-lint/SKILL.md`

Expected: The section appears at the top of the skill.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/skills/al-dev-lint/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(al-dev-lint): add intent-preflight check

al-dev-lint now checks intent against artifact before mutating actions.
Aligns with the intent-preflight model used by other entry skills.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Expand skill-test-trigger-corpus.yaml with Near-Miss Prompts

**Files:**
- Modify: `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml`

- [ ] **Step 1: Read the trigger corpus file**

Run: `head -50 profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml`

Understand the YAML structure (prompt examples, skill routing, expected behavior).

- [ ] **Step 2: Identify the insertion point**

Read the full file to find where near-miss examples should be added (typically organized by skill or scenario type).

- [ ] **Step 3: Add near-miss scenarios for spec/plan/review wording**

Add these entries to the corpus (organized in a logical section, e.g., "Review-Only and Artifact-Mismatch Scenarios"):

```yaml
review_spec_ready_to_implement:
  prompt: "review this spec and tell me if it is ready to implement"
  artifact: design spec document
  expected_routing: NONE (clarify intent; review-only is not an implementation trigger)
  expected_response: "This spec is well-formed and covers requirements X, Y, Z. Are you ready for me to create a plan?"

audit_plan_for_risk:
  prompt: "audit this plan for risk only"
  artifact: implementation plan
  expected_routing: NONE (clarify intent; audit-only is not an implementation trigger)
  expected_response: "I'll review this plan for risks without executing it. Here are my concerns: ..."

summarize_compile_failures:
  prompt: "summarize the compile failures without fixing anything"
  artifact: code with compile errors
  expected_routing: NONE or al-dev-lint with REVIEW intent (diagnostic summary, not EDIT)
  expected_response: "The staged changes have X errors and Y warnings. Details: ... Should I fix these, or is this review-only?"

spec_plus_implement_mismatch:
  prompt: "here's my spec, implement it now"
  artifact: design spec document + "implement/execute" keyword
  expected_routing: Clarify whether user wants planning output (al-dev-plan) or direct implementation (al-dev-develop)
  expected_response: "I see you have a spec. Do you want me to create a detailed plan first, or jump straight to implementation?"

plan_plus_review_only_mismatch:
  prompt: "review this plan and audit only"
  artifact: implementation plan + "review/audit only" keywords
  expected_routing: Treat as REVIEW (no implementation)
  expected_response: "I'll review this plan for completeness and risk. I won't execute it unless you confirm."
```

- [ ] **Step 4: Verify the YAML syntax**

Run: `python3 -c "import yaml; yaml.safe_load(open('profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml'))" && echo "YAML valid"`

Expected: "YAML valid"

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml
git -C /Users/russelllaing/al-dev-shared commit -m "test(trigger-corpus): expand with spec/plan/review near-miss scenarios

Add five near-miss prompts covering artifact/intent mismatches: spec
review-only, plan audit-only, compile summary-only, spec+implement
conflict, and plan+review conflict. Each scenario maps to expected
routing and response pattern.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Summary of Changes

| Change | Files | Impact |
|--------|-------|--------|
| Pre-Commit Compile Gate | `al-dev-commit/SKILL.md`, `compile-lint-procedure.md`, `al-dev-commit/tests/scenarios.yaml` | Enforces compile discipline before commits; blocks AL errors |
| Investigation Guidance Tightening | `al-dev-investigate/SKILL.md` | Clarifies this skill as the root-cause framework |
| Intent-Preflight Completion | `intent-preflight.md`, `al-dev-lint/SKILL.md`, `skill-test-trigger-corpus.yaml` | Extends intent-preflight to lint; improves near-miss routing |

**Total:** 7 files, 8 tasks, ~90 minutes of work

---

## Verification Checklist

Before completing the plan:

- [ ] All 8 tasks committed with separate atomic commits
- [ ] No forbidden patterns in any changed files (no TODO, TBD, [date] placeholders, or harness-specific tokens)
- [ ] All YAML files pass Python yaml.safe_load validation
- [ ] Grep confirms all new sections appear in their files
- [ ] Commit count matches task count: `git log --oneline -n 8` shows 8 commits
- [ ] No line-count changes in automated edits (verify with `wc -l` if using Write tool)
