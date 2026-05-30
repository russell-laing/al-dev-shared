---
name: al-dev-review-develop
description: >-
  Orchestrate multi-reviewer code review, compilation verification, and code-review
  output for implemented AL solutions. Consumes Phase 4 output from /al-dev-develop
  (completed developer work) and focuses exclusively on post-implementation quality gates
  and review synthesis.
argument-hint: ""
---

# Review-Develop Skill

Post-implementation review orchestration for /al-dev-develop Phase 5–10.

Dispatched by /al-dev-develop after Phase 4 (developer dispatch and implementation completion).

## Prerequisites

Phase 4 handoff artifact must exist:
`.dev/*-al-dev-develop-phase4-handoff.md` (or latest from /al-dev-develop Phase 4 output).

## Artifact Contract

Use `knowledge/artifact-contracts.md` as the source of truth for this skill's
required handoff artifact, durable outputs, and success evidence.

Do not claim the review is complete, validated, clean, or ready for the next
workflow step until the success evidence named in
`knowledge/artifact-contracts.md` for `al-dev-review-develop` has been
produced and read for the current run.

## Review Panel

Three specialist agents (sonnet):
- **al-dev-security-reviewer** — permission/auth/data exposure
- **al-dev-expert-reviewer** — AL conventions/BC patterns
- **al-dev-performance-reviewer** — N+1/SetLoadFields/efficiency

## Outputs

`.dev/$(date +%Y-%m-%d)-al-dev-develop-code-review.md` — synthesized review findings from all three reviewers; this file is also the downstream handoff artifact named in `knowledge/artifact-contracts.md` and must be read before any final clean/ready claim.

## Execution Order

Phases run in this order: **5 → 8 → 8.5 → 6-7 → 9 → 10** (see Run labels on each header).
Phase headers retain parent-workflow numbering; execute in the order shown, not by header number.

---

## Phase 5 (Run 1st): Prepare Review Context

**Input:** Phase 4 handoff artifact from `/al-dev-develop`.

1. **Locate the Phase 4 handoff artifact:**

   ```bash
   ls .dev/*-al-dev-develop-phase4-handoff.md 2>/dev/null | sort | tail -1
   ```

   If no handoff artifact is found, stop and tell the user:
   "No Phase 4 handoff found. Run `/al-dev-develop` first and wait for it to complete Phase 4."

2. **Read the Phase 4 handoff in full** — note the developer module assignments and status.

3. **Identify changed AL files** — combine two sources:
   - Files listed in the handoff's module assignments section
   - `git diff --cached --name-only --diff-filter=ACMR` filtered to `*.al`, `app.json`, and `*.al.json`
   - `git ls-files --others --exclude-standard` filtered to `*.al`, `app.json`, and `*.al.json`

   Build a deduplicated list: `CHANGED_FILES`

4. **Write progress checkpoint:**

   ```bash
   echo "Phase 5 complete — $(date +%Y-%m-%d %H:%M): context loaded, CHANGED_FILES identified" >> .dev/progress.md
   ```

5. Proceed to Phase 8.

---

## Phase 8 (Run 2nd): Compile Verification

Run `al-compile` and handle errors. This phase must pass before the review panel is spawned.

1. **Run compile:**

   ```bash
   al-compile --output .dev/compile-errors.log
   ```

2. **Check for errors:**

   ```bash
   grep -c "error AL" .dev/compile-errors.log 2>/dev/null || echo "0"
   ```

3. **If errors found:**

   - **Standard mode:** Show the errors and stop. Ask the user to fix compilation errors before proceeding to code review.

   - **`--autonomous` mode:** Spawn `al-dev-shared:al-dev-developer` to fix errors:

     ```text
     Agent: al-dev-shared:al-dev-developer
     Prompt:
       "Fix compilation errors in .dev/compile-errors.log for the current Phase 4 handoff.
        Read the errors, identify root causes, and apply minimal fixes.
        Use the current solution plan and handoff context; if either is missing, stop and escalate to the user.
        Compile after each fix. Return: files changed, errors resolved."
     ```

     Re-run compile after fixes. Repeat up to 5 cycles total. If errors remain after 5 cycles, stop and escalate to user.

4. **Read compile verification result** (required by artifact contract):

   ```bash
   cat .dev/compile-errors.log
   ```

   Read the file contents — the artifact contract requires the compile result to be read, not merely confirmed to exist.

5. **Write progress checkpoint:**

   ```bash
   echo "Phase 8 complete — $(date +%Y-%m-%d %H:%M): compile verification passed" >> .dev/progress.md
   ```

---

## Phase 8.5 (Run 3rd): Pre-Review Staging

Verify all prerequisites are met before spawning the review panel.

1. **Confirm compile passed** (zero `error AL` lines in `.dev/compile-errors.log`).
2. **Confirm `CHANGED_FILES` list is non-empty** — if empty, stop and tell the user no changed AL files were detected.
3. If both checks pass, proceed to Phase 6-7.

---

## Phase 6-7 (Run 4th): Dispatch Review Panel

Spawn all three specialist reviewer agents simultaneously — do not wait for one agent to return before spawning the next. Pass each agent the same `CHANGED_FILES` list and implementation context from the Phase 4 handoff.

**Dispatch prompt for each reviewer:**

```text
Review the following AL files for [reviewer specialty]:
[CHANGED_FILES list — one file per line]

Implementation context (from Phase 4 handoff):
[Summary of what was implemented — module assignments and scope from handoff]

Return findings in this format:
CRITICAL: [issues that block release]
HIGH: [significant issues to fix]
MEDIUM: [notable issues to address]
LOW: [minor improvements]

If no issues found in your specialty: return "NONE" under each severity.
```

Spawn these three agents with the above prompt adapted to each specialty:
- `al-dev-shared:al-dev-security-reviewer` — focus: permissions, data exposure, auth checks
- `al-dev-shared:al-dev-expert-reviewer` — focus: AL conventions, naming, BC patterns
- `al-dev-shared:al-dev-performance-reviewer` — focus: N+1 queries, SetLoadFields, resource loops

Collect all three outputs before proceeding to Phase 9.

---

## Phase 9 (Run 5th): Write Code-Review Artifact

Synthesize findings from all three reviewers into a single dated code-review file.

1. **Create the code-review artifact:**

   ```bash
   CODE_REVIEW_FILE=".dev/$(date +%Y-%m-%d)-al-dev-develop-code-review.md"
   ```

2. **Write the file** using this structure:

   ```markdown
   # Code Review: [date]

   **Scope:** [CHANGED_FILES list]
   **Phase 4 handoff:** [handoff filename]
   **Compile:** ✅ Passed

   ## Critical Issues

   [All CRITICAL findings from all three reviewers, deduplicated and attributed]

   ## High Issues

   [All HIGH findings, deduplicated and attributed]

   ## Medium Issues

   [All MEDIUM findings, deduplicated and attributed]

   ## Low / Minor

   [All LOW findings, deduplicated and attributed]

   ## Review Panel Summary

   | Reviewer | Critical | High | Medium | Low |
   |----------|----------|------|--------|-----|
   | Security | N | N | N | N |
   | AL Expert | N | N | N | N |
   | Performance | N | N | N | N |

   ## Verdict

   [BLOCKING: N critical issues must be resolved before commit]
   [READY: no blocking issues found — proceed to /al-dev-commit]
   ```

3. **Read the file back** to confirm it was written and satisfy the artifact contract:

   ```bash
   cat "$CODE_REVIEW_FILE"
   ```

   Read the file contents — the artifact contract requires the code-review artifact to be read in this run, not merely confirmed to exist.

4. **Write progress checkpoint:**

   ```bash
   echo "Phase 9 complete — $(date +%Y-%m-%d %H:%M): code-review artifact written" >> .dev/progress.md
   ```

---

## Phase 10 (Run 6th): Present Review Findings

1. **Display a summary** of the code-review artifact:

   ```text
   Code review complete.

   Scope: [N files reviewed]
   Compile: ✅ Passed

   Critical: [N] | High: [N] | Medium: [N] | Low: [N]

   [If BLOCKING:]
   ⚠️  [N] critical issue(s) must be resolved before committing.
   Full findings: [CODE_REVIEW_FILE]
   Next step: Fix critical issues, then re-run /al-dev-review-develop (or proceed directly to /al-dev-commit if you accept the risk).

   [If READY:]
   ✅  No blocking issues found.
   Full findings: [CODE_REVIEW_FILE]
   Next step: /al-dev-commit
   ```

2. **Do not claim "clean" or "ready" until** the code-review artifact file has been read in this run (per `knowledge/artifact-contracts.md`).
