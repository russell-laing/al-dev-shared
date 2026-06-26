---
name: al-dev-commit-execute
description: >-
  Run lint preflight, OOXML validation, and git commits for an approved commit
  plan. Reads .dev/commit-preflight.md written by /al-dev-commit-preflight.
  Phases 3–4 of the commit workflow; dispatches al-dev-commit-executor to perform the commits. Called by /al-dev-commit; can also run
  standalone when an approved plan already exists in .dev/commit-preflight.md.
  Triggers on: "execute the commits", "run the commit plan", "commit now".
---

# `/al-dev-commit-execute` — Commit Execution

Phases 3–4 of the atomic commit workflow. Loads the approved plan from
`.dev/commit-preflight.md`, runs lint preflight and OOXML validation, dispatches
the execution agent, handles hook failures via the classifier+fixer recovery
pipeline, and summarises results.

You never run `git commit` yourself — always delegate to the execution agent.

Follow every step in order. Do not skip steps or proceed past a stop condition.

---

## Phase 0 — Load Approved Plan

Load the approved commit plan written by `/al-dev-commit-preflight`:

```bash
ls .dev/commit-preflight.md 2>/dev/null
```

If the file is missing, stop:

> "No approved commit plan found in `.dev/commit-preflight.md`. Run
> `/al-dev-commit-preflight` first to analyse staged changes and collect
> approval, then re-run `/al-dev-commit-execute`."

Read `.dev/commit-preflight.md`. Extract and hold in working memory:

- `APPROVED_GROUPS` block (all GROUP_N entries with files and messages)
- `LINT_CONTEXT.prior_lint_report` — path or "none"
- `LINT_CONTEXT.mixed_al_docx` — "yes" or "no"

Store the reconstructed `APPROVED_PLAN` for use in Phases 3 and 4.

Proceed to Phase 3.

---

> **Lint path ownership:** `al-dev-commit` runs its own internal lint preflight
> via `al-dev-commit-lint-fixer` (this phase). This is the canonical path for
> pre-commit lint validation within the commit workflow. `/al-dev-lint` is a
> standalone skill for on-demand linting outside the commit workflow — do not
> chain it into this phase sequence.

## Phase 3 — Preflight

**File-type gate (run before dispatching 3.1 or 3.2):**

```bash
OOXML_STAGED=$(git diff --cached --name-only | grep -E '\.(docx|xlsx|pptx|odt)$' || true)
```

- If `OOXML_STAGED` is **empty**: set `OOXML_FAILURES=NONE` inline and skip 3.2 entirely.
- If `OOXML_STAGED` is **non-empty**: dispatch both 3.1 and 3.2 as below.

Run preflight as up to two **parallel** agent dispatches — always 3.1
(`al-dev-commit-lint-fixer`); conditionally 3.2 (`al-dev-commit-ooxml-validator`) when
OOXML files are staged — then **await all dispatched agents** before Phase 4.1.
The agents operate on disjoint state (lint-fixer excludes OOXML files and is the
only Phase-3 agent that stages via `git add`; the validator sources its file list
from `APPROVED_PLAN` and never reads the git index), so concurrent execution has
no race. **Do not** add `git diff --cached` reads to the validator — that would
reintroduce `.git/index` contention with the lint-fixer's `git add`.

### 3.1 — Dispatch Lint Preflight Agent

Dispatch the lint fixer agent with the approved plan from Phase 0:

Dispatch:

- agent: `al-dev-shared:al-dev-commit-lint-fixer`
- description: "Pre-flight lint and trailing whitespace fixes"
- phase label: `Perform LINT-PREFLIGHT phase for git commit workflow.`
- prompt body: verbatim:

  ```text
  APPROVED_PLAN:
  [paste the approved plan from Phase 0]

  CRITICAL RULES:
  - NEVER use Write or Edit on staged source files — all fixes via Bash only
  - Skip binary and OOXML files in trailing-whitespace step (binary = *.png, *.jpg, *.gif, *.ico, *.pdf, *.zip, *.tar, *.gz, or any file where `file --mime-type` returns a non-text/* type; OOXML = *.docx, *.xlsx, *.pptx, *.odt)
  - Stop immediately if corruption detected (line count collapses)
  ```

- return format: `LINT_FIXES`

Store the `LINT_FIXES` value for display in Phase 4.

**Sentinel convention:** The value `NONE` (all-caps literal string) means "no failures in this category." It is used as the empty-state sentinel for `OOXML_FAILURES`, `LINT_FIXES`, and `HOOK_FAILURES` throughout this skill. An agent returning one of these fields should set it to exactly `NONE` when there is nothing to report.

### 3.2 — Validate Office Documents (OOXML files)

- [ ] **Step 3.2.1:** Identify OOXML files in staged commits

Run: `grep -E '\.(docx|xlsx|pptx|odt)$' <(git diff --cached --name-only)`

If no files match, skip to Phase 4.

- [ ] **Step 3.2.2:** Run unzip -t validation on each OOXML file

```bash
OOXML_FILES=$(git diff --cached --name-only | grep -E '\.(docx|xlsx|pptx|odt)$')
OOXML_FAILURES=""

if [ -n "$OOXML_FILES" ]; then
  while IFS= read -r file; do
    if [ -f "$file" ] && ! unzip -t "$file" > /dev/null 2>&1; then
      OOXML_FAILURES="$OOXML_FAILURES$file (unzip test failed)\n"
    fi
  done <<< "$OOXML_FILES"
fi

if [ -n "$OOXML_FAILURES" ]; then
  echo "OOXML validation failed:"
  echo -e "$OOXML_FAILURES"
  exit 1
fi
```

Expected: PASS if all OOXML files are valid archives; FAIL if any fail unzip test

- [ ] **Step 3.2.3:** Record validation result for Phase 3 summary

Set: `OOXML_STATUS="PASS"` (if all valid) or abort execution

If any file fails, present failure list to user and block commit.

**Barrier:** await 3.1 (`LINT_FIXES`) and, if dispatched, 3.2 (`OOXML_FAILURES`) before
proceeding to Phase 4.1. When 3.2 was skipped (no OOXML files staged), `OOXML_FAILURES`
is already set to `NONE` inline — treat it as in-hand and proceed to Phase 4.1 immediately
after 3.1 completes.

---

## Phase 4 — Execution & Summary

### 4.1 — Dispatch Execution Agent

Construct the approved plan from Phase 0:

```text
GROUP_1:
  files: [files]
  message: |
    [approved message verbatim]
GROUP_2:
  ...
```

Dispatch the execution agent:

Dispatch:

- agent: `al-dev-shared:al-dev-commit-executor`
- description: "Commit execution: [N] commits"
- phase label: `Perform EXECUTE phase for git commit workflow.` followed by a
  `Phase: execute` line
- prompt body: verbatim:

  ```text
  APPROVED_PLAN:
  [paste the approved plan constructed above]

  CRITICAL RULES:
  - NEVER add Co-Authored-By trailers to commit messages
  - Use git -C <path> instead of cd <path> && git
  - Verify file integrity (wc -l) for all modified files after commits
  ```

  then `Follow the execute phase instructions in your agent definition.`
- return format: `COMMITS, SKIPPED, HOOK_FAILURES`

**Branch on execution result:**

- **`HOOK_FAILURES` is not `NONE`** (one or more groups rejected by a
  pre-commit hook) — proceed to 4.3 for error recovery before any summary.
- **`HOOK_FAILURES` is `NONE`** (clean `COMMITS` block) — skip 4.3 and proceed
  directly to 4.4 to summarize.

### 4.3 — Dispatch Hook-Failure Recovery (Error Path)

Persist the failure context:

```bash
# Write the execution agent's HOOK_FAILURES output to .dev/hook-failures.json
# Write the approved plan (groups, files, messages) to .dev/commits.json
```

**Step A — Dispatch the classifier agent:**

```text
Agent tool:
  agent: al-dev-shared:al-dev-commit-hook-classifier
  description: "Classify pre-commit hook failures"

Prompt:
  "Classify the pre-commit hook failures from the commit execution phase.

   Input:
   - .dev/hook-failures.json (hook output and error logs)

   HOOK_FAILURES from execution agent (fallback if file is missing):
   [paste the HOOK_FAILURES block from the execution agent output]

   Follow your agent definition. Return the HOOK_CLASSIFICATIONS block."
```

Read the returned `overall` field:

- **non-fixable** — skip Step B. For each non-fixable failure, surface
  `root_cause` and `recommended_fix` to the user as manual-review items.
  Treat overall `recovery_status` as `needs-manual-intervention` and stop.
- **fixable** or **mixed** — proceed to Step B.

**Step B — Dispatch the fixer agent:**

```text
Agent tool:
  agent: al-dev-shared:al-dev-commit-hook-fixer
  description: "Apply scripted recovery for classified hook failures"

Prompt:
  "Apply scripted fixes for the classified pre-commit hook failures.

   HOOK_CLASSIFICATIONS from classifier agent:
   [paste the HOOK_CLASSIFICATIONS block]

   Commit context:
   - .dev/commits.json (commit details that triggered the hooks)

   CRITICAL RULES:
   - NEVER use Write or Edit on staged source files — all fixes via Bash only
   - Do not re-run the commit yourself — return next_step guidance

   Follow your agent definition. Return the HOOK_FAILURES block."
```

Read the returned `recovery_status` and act:

- **`ready-to-retry`** — scripted fixes were applied and re-staged. Re-dispatch
  the execution agent (4.1) for the affected groups, then re-enter Phase 4.
- **`needs-manual-intervention`** — surface each `manual-review` failure
  (`root_cause` + `recommendation`) to the user and stop. Do not retry until
  the user resolves and re-runs `/al-dev-commit-execute`.
- **`non-recoverable`** — report the condition (e.g., broken hook) to the user
  and abort the commit workflow.

### 4.4 — Final Verification (Commit Count & History Integrity)

- [ ] **Step 4.4.1:** Read approved commit plan artifact

Run: `cat ".dev/$(date +%Y-%m-%d)-al-dev-plan-solution-plan.md" | grep -A 100 "## Commits" | head -50`

Expected: List of expected commit subjects and files

- [ ] **Step 4.4.2:** Count expected commit groups from plan

Run: `grep -c "^### Commit" ".dev/$(date +%Y-%m-%d)-al-dev-plan-solution-plan.md"`

Store: `EXPECTED_COMMITS=<count>`

- [ ] **Step 4.4.3:** Compare against actual commits since base branch

Run: `git log --oneline --since="$PLAN_DATE" -- | wc -l`

Store: `ACTUAL_COMMITS=<count>`

- [ ] **Step 4.4.4:** Safety gate — unpublished commits only

Run: `git log --oneline origin/main.. 2>/dev/null | wc -l`

If result = 0, commit is publishable. If greater, warn user: "Commits already pushed; history rewrite blocked."

- [ ] **Step 4.4.5:** (Optional) Reset and re-commit if user confirms

If ACTUAL_COMMITS ≠ EXPECTED_COMMITS and user confirms rewrite:

```bash
git reset --soft HEAD~$ACTUAL_COMMITS
git commit -m "<consolidated message from plan>"
```

Expected: Commits consolidated to match plan.

- [ ] **Step 4.4.6:** Final verification — confirm commit presence

Run: `git log --oneline --since="$PLAN_DATE" -- | head -5`

Expected: Commit subjects match plan exactly

- [ ] **Step 4.4.7:** Log final SHAs for handoff

```bash
git log --oneline --since="$PLAN_DATE" -- > ".dev/$(date +%Y-%m-%d)-al-dev-commit-verified-shas.txt"
echo "Commits verified and logged to .dev/$(date +%Y-%m-%d)-al-dev-commit-verified-shas.txt"
```

Summary: `COMMIT_VERIFICATION_STATUS="READY"` (present in summary output for next step)
