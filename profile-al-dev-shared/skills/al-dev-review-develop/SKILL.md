---
name: al-dev-review-develop
description: >-
  Dispatches the three-reviewer panel and synthesizes findings. Run
  /al-dev-review-develop-preflight first to locate the develop handoff,
  identify changed files, and verify compile status.
---

# Review-Develop Skill

Reviewer dispatch and synthesis for post-implementation code review.

Reads the preflight context written by `/al-dev-review-develop-preflight`,
then dispatches the three-specialist review panel in parallel and synthesises
findings into a single code-review artifact.

> **Run from a low-context state.** This skill dispatches a parallel reviewer
> panel, which injects a large prompt. If the session has already accumulated
> bulky tool output (compile logs, large diffs), that injection can overflow the
> context window mid-dispatch. When the session is already context-heavy,
> compact it before invoking this skill so the panel dispatches cleanly.

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
- **al-dev-al-pattern-reviewer** — AL conventions/BC patterns
- **al-dev-performance-reviewer** — N+1/SetLoadFields/efficiency

## Outputs

`.dev/$(date +%Y-%m-%d)-al-dev-develop-code-review.md` — synthesized review findings from all three reviewers; this file is also the downstream handoff artifact named in `knowledge/artifact-contracts.md` and must be read before any final clean/ready claim.

---

## Phase 0: Verify Preflight

Read the most recent preflight context file:

```bash
ls .dev/*-plugin-review-preflight.md 2>/dev/null | sort | tail -1
```

Extract `CHANGED_FILES` and `COMPILE_STATUS` from the file.

**If no preflight file found:** stop and tell the user:

```text
No preflight context found.

Run /al-dev-review-develop-preflight first to locate the develop handoff,
identify changed files, and verify compile status.
```

**If COMPILE_STATUS is `fail`:** stop and report the compile errors to the
user before proceeding. Do not dispatch reviewers until compile passes.

If preflight file exists and `COMPILE_STATUS` is `pass`: proceed to Phase 4.

---

## Phase 4: Dispatch Review Panel

Spawn all three specialist reviewer agents simultaneously — do not wait for one
agent to return before spawning the next. Pass each agent the same `CHANGED_FILES`
list and implementation context from the Phase 4 handoff (referenced in the
preflight file).

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
- `al-dev-shared:al-dev-al-pattern-reviewer` — focus: AL conventions, naming, BC patterns
- `al-dev-shared:al-dev-performance-reviewer` — focus: N+1 queries, SetLoadFields, resource loops

Collect all three outputs before proceeding to Phase 5. If any agent fails to
spawn or returns no output, report this to the user and ask whether to retry the
failed reviewer or proceed with a partial review. If proceeding partial, carry the
absent reviewer forward so Phase 5 can mark it explicitly.

---

## Phase 5: Write Code-Review Artifact

Synthesize findings from all three reviewers into a single dated code-review file.
If a reviewer was absent from a partial review (see Phase 4), mark its row in the
Review Panel Summary table as `— (not run)` rather than omitting it, and note the
partial-review status near the top of the artifact.

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
   echo "Phase 5 complete — $(date +%Y-%m-%d %H:%M): code-review artifact written" >> .dev/progress.md
   ```

---

## Phase 6: Present Review Findings

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
