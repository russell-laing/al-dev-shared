---
name: al-dev-commit
description: >-
  Use when ready to commit staged changes — especially after
  development work where scope creep (unapproved field removals,
  extra file deletions, hallucinated changes) may have occurred.
argument-hint: "[optional args]"
---

# `/al-dev-commit` — Atomic Commit Workflow

Thin orchestrator for the two-phase commit workflow. Collects
context, dispatches the analysis agent, handles all user
confirmation gates, then dispatches the execution agent.

You never run `git commit` yourself — always delegate.

Follow every step in order. Do not skip steps or proceed past a
stop condition.

---

## Intent Preflight

Before dispatching commit agents, staging files, unstaging files, or committing,
apply `knowledge/intent-preflight.md`.

Default intent for this skill is `COMMIT`. If the request is review-only,
edit-only, assessment-only, or asks for a commit plan without committing, stop
and ask the intent-mismatch prompt from `knowledge/intent-preflight.md` before
continuing.

## Artifact Contract

Use `knowledge/artifact-contracts.md` as the source of truth for this skill's
required staged-state checks and success evidence.

Do not claim the staged set is ready, validated, or safe to commit until the
success evidence named in `knowledge/artifact-contracts.md` for
`al-dev-commit` has been produced and read for the current staged state.

The six-agent commit dispatch contract is documented in
`../../knowledge/commit-workflow-orchestration.md` — keep phase prompt templates in sync with it.

---

## Phase 0 — Setup & Validation

### 0.1 — Guard: Verify Project Context

Check whether the project instructions file exists in the current directory (use your harness's concrete filename).

If no project instructions file is found:

Tell the user: "No project instructions file found in this repository.
Project context is required to generate correct commit
messages. Would you like me to create it now via
`/al-dev-init-context`? (yes / no)"

- **yes** — invoke the `al-dev-init-context` skill via the
  Skill tool (not a subagent), wait for it to complete, then
  proceed to 0.2 to load the newly created project
  instructions file
- **init-context fails** — stop with: "Could not create
  the project instructions file automatically. Please run
  `/al-dev-init-context` or create it manually, then re-run
  `/al-dev-commit`."
- **no** — stop with: "Please create the project
  instructions file manually or run `/al-dev-init-context`,
  then re-run `/al-dev-commit`."

### 0.2 — Load Project Context

Load the project instructions file from these standard locations
(earlier files provide defaults, later files override):

1. The global project instructions file — global defaults (if present)
2. The AL profile project instructions file in `$AL_DEV_SHARED_PLUGIN_ROOT` — AL profile defaults (if present)
3. The project instructions file — project-specific (required)

Extract and hold in working memory:

- **Valid scopes** — e.g. `price`, `rebate`, `ui`, `config`, `docs`
- **Object ID prefix** — e.g. `ACUKPR`
- **Object ID range** — e.g. `50901–50950`
- **AL file naming pattern** — e.g. `Name.ObjectType.al`

### 0.2.1 — Freshdesk Ticket Context (Optional)

Ticket context is optional. If available, load it; otherwise skip to 0.3.

```bash
# 1. Prefer --ticket-id if supplied by caller
if [[ "$ARGUMENTS" =~ --ticket-id=([^ ]+) ]]; then
  TICKET_ID="${BASH_REMATCH[1]}"
  # Fetch context from Freshdesk API; append to commit message
  # (Freshdesk unreachable → log warning and proceed without ticket context)
else
  # 2. Fall back to a prior /al-dev-ticket context file
  TICKET=$(ls .dev/*-al-dev-ticket-ticket-context.md 2>/dev/null | sort | tail -1)
  if [[ -n "$TICKET" ]]; then
    head -10 "$TICKET"
    # Extract ticket number from "TICKET: #<number>" if present
  fi
  # No file found → proceed without ticket context (ticket link is optional)
fi
# Continue to 0.3 in all cases
```

### 0.3 — Verify File Integrity & Staged Files

For each staged modified file (ACMRT):

```bash
git diff --cached --name-only --diff-filter=ACMRT
```

For each file listed, run:

```bash
wc -l <file>
```

Compare against file's last recorded size in `.dev/file-sizes.json` (if exists).

If **any modified file's line count collapsed** (e.g., newlines stripped):

Tell the user: "File integrity check failed — FILE lost lines
during edit. This may indicate a bash heredoc or perl regex issue.
Check your edits before committing."

**Stop.** Do not proceed.

Check what is staged:

```bash
git diff --cached --name-only --diff-filter=ACMRDT
```

If empty:

Tell the user: "No staged files found. Use `git add` to stage
your changes, then run `/al-dev-commit` again."

**Stop.**

**AL-affecting staged set check:** Run this compile gate when staged changes include any
`.al`, `app.json`, or `.al.json` files. Skip for pure documentation (`.md`, `.txt`),
changelog, or manifest-only edits.

```bash
AL_STAGED=$(git diff --cached --name-only --diff-filter=ACMRDT \
  | grep -E '(^|/)(app\.json|[^/]+\.al|[^/]+\.al\.json)$')
```

If `$AL_STAGED` is non-empty, run the compile gate before proceeding:

1. Apply `knowledge/compile-lint-procedure.md`
2. Produce a fresh `.dev/compile-errors.log` if the current log is absent or stale
3. Read the log and report:
   - `Errors:` count
   - `Warnings:` count
   - up to 3 representative diagnostics
   - `Detailed log:` `.dev/compile-errors.log`
4. If `Errors > 0`, stop the commit workflow and tell the user the staged changes are not ready to commit
5. Only continue when the compile result shows zero errors

Critical rule: never claim the staged set is ready, "clean compile", or "zero errors"
without reading the actual success evidence required by
`knowledge/artifact-contracts.md` for the current staged state.

### 0.4 — Optional Context: Prior Lint Findings & Acceptance Criteria

**If a prior lint report exists,** load it to inform the commit workflow:

1. **Check for lint report:**

   ```bash
   ls .dev/*-al-dev-lint-lint-report.md 2>/dev/null | sort | tail -1
   ```

2. **If found, read the report:**

   Show the user:

   ```text
   Prior lint findings found. Review before committing?

   [paste lint report content — unresolved issues]

   Note: These findings may inform your grouping decisions if lint fixes
   need atomic separation.
   ```

3. **If not found, continue:** Proceed to next section.

This is optional; missing lint report does not block commit workflow.

**If a solution plan exists,** verify acceptance criteria:

Check whether a solution plan exists:

```bash
PLAN=$(ls .dev/*-al-dev-plan-solution-plan.md 2>/dev/null | sort | tail -1)
```

If a solution plan file is found, read its Acceptance Criteria section. For each directly checkable criterion (structural, gate, pattern forms):

- **Structural criteria:** Verify that named files exist and contain named symbols (use `grep` or `al-compile` output)
- **Gate criteria:** Confirm that referenced gates (e.g., `al-compile`) exit 0
- **Pattern criteria:** Use `git diff --cached` to verify patterns do or do not appear in changed code

Do not treat `[manual]` criteria as automatic blockers. Surface any pending manual criteria as a note to the user: "Manual validation pending: [list]"

If verification of any directly checkable criterion fails, stop the commit workflow and report the failure to the user.

If no solution plan exists, skip this step and continue to 0.5.

### 0.5 — Establish Gitmoji Style

Check the project's recent commit style:

```bash
git log -5 --oneline
```

Extract the emoji pattern (e.g., `✨ feat:`, `🐛 fix:`, `📝 docs:`).

Hold as **PROJECT_GITMOJI_STYLE**.

Continue to Phase 1.

---

## Phase 1 — Analysis & Message Drafting

### 1.1 — Dispatch Analysis Agent (Manifest Extraction)

Dispatch the analysis agent to extract manifests from staged changes:

Dispatch per `knowledge/commit-dispatch-template.md`:

- agent: `al-dev-shared:al-dev-commit-analyzer`
- description: "Commit analysis: extract manifests from staged changes"
- phase label: `Perform ANALYSIS phase for git commit workflow.` followed by a
  `Phase: analysis` line
- prompt body: include the shared project-context preamble (PROJECT_CONTEXT +
  FD_TICKET) from the template; then `Follow the analysis phase instructions in
  your agent definition.`
- return format: `MANIFESTS block, DELETIONS, WARNINGS` — append verbatim
  `Message drafting is handled in the next step.` after the return-format line

### 1.2 — Deletion Audit Gate

Read the `DELETIONS` block from the analysis agent output.

If **any deleted files** appear, display them prominently:

```text
⚠️  STAGED DELETIONS — explicit approval required

  The following files are staged for deletion:
    - [filename]
    - [filename]

  Were ALL of these deletions explicitly approved?
  (yes / no / list-to-keep)
```

Wait for user response:

- **yes** — continue to 1.3
- **no** — run `git restore --staged <file>` for every deleted
  file, then **stop** (user must re-run `/al-dev-commit` after
  reviewing their staged files)
- **list-to-keep** — user names files to unstage; run
  `git restore --staged <file>` for each, then **stop**

If no deleted files: continue to 1.3.

### 1.3 — Dispatch Message-Drafting Agent

Dispatch the message-drafting agent with the analysis results:

Dispatch per `knowledge/commit-dispatch-template.md`:

- agent: `al-dev-shared:al-dev-commit-message-drafter` (model: haiku)
- description: "Draft commit messages and propose groups"
- phase label: `Perform MESSAGE-DRAFTING phase for git commit workflow.`
  followed by a `Phase: message-drafting` line
- prompt body: include the shared project-context preamble (PROJECT_CONTEXT +
  FD_TICKET) from the template; then verbatim:

  ```text
  MANIFESTS FROM ANALYSIS PHASE:
  [paste the MANIFESTS block from the analysis agent output]
  ```

  then `Follow the message-drafting phase instructions in your agent
  definition.`
- return format: `PROPOSED_GROUPS block with commit messages for each group`

Continue to Phase 2.

---

## Phase 2 — Confirmation

### 2.1 — Present Manifests and Confirm Plan

Display the `MANIFESTS` block from the analysis agent output (Phase 1.1), then the
`PROPOSED_GROUPS` block from the message-drafting agent output (Phase 1.3):

```text
Change manifests:

[MANIFESTS block — paste from agent output]

Proposed commit plan ([N] commits):

Commit 1 of N — [type(scope)]
  Files: [file list]
  Reason: [reason from agent]

Commit 2 of N — [type(scope)]
  Files: [file list]
  Reason: [reason from agent]

Confirm this plan? (yes / adjust / cancel)
```

Wait for user response:

- **yes** — continue to 2.2
- **adjust** — user provides revised groupings; update your
  working copy of the plan and re-present, then wait for
  confirmation again
- **cancel** — abort everything, leave all files staged unchanged

### 2.2 — Confirm and Refine Each Commit Message

For each group in the plan, display the draft message from the agent output
alongside the change manifest for that group, and ask for confirmation:

```text
Commit [N] of [total]:

[Draft message from agent]

CHANGED COMPONENTS:
[Component lines from agent's PROPOSED_GROUPS block]

Confirm? (yes / edit / skip / cancel-all)
```

- **yes** — record the approved message, move to next group
- **edit** — user provides revised message text; re-display and
  ask for confirmation again
- **skip** — skip this group; leave its files staged
- **cancel-all** — abort all remaining; leave all files staged

### 2.3 — Check Mixed AL/DOCX Warning

After all groups are confirmed or skipped, check the analysis agent output `WARNINGS` block for a `MIXED_AL_DOCX` entry.

If present, show:

```text
⚠️  MIXED AL + DOCX STAGING DETECTED

This commit plan includes both `.al` source files and `.docx` layout files.
High-risk pattern: automated tool rewrites of Word layouts can produce malformed OOXML.

Confirm all `.docx` files were edited and saved in Microsoft Word (not scripted),
and that OOXML ZIP validation has passed.

Proceed to preflight? (yes / no)
```

User response:

- `yes` — proceed to Phase 3
- `no` — stop; leave staged files unchanged (user must re-run `/al-dev-commit` after reviewing staged files)

If no `MIXED_AL_DOCX` warning exists, proceed directly to Phase 3.

---

> **Lint path ownership:** `al-dev-commit` runs its own internal lint preflight
> via `al-dev-commit-lint-fixer` (this phase). This is the canonical path for
> pre-commit lint validation within the commit workflow. `/al-dev-lint` is a
> standalone skill for on-demand linting outside the commit workflow — do not
> chain it into this phase sequence.

## Phase 3 — Preflight

Run preflight sequentially: lint fixes first, then OOXML validation.

### 3.1 — Dispatch Lint Preflight Agent

Dispatch the lint fixer agent with the approved plan from Phase 2:

Dispatch per `knowledge/commit-dispatch-template.md`:

- agent: `al-dev-shared:al-dev-commit-lint-fixer`
- description: "Pre-flight lint and trailing whitespace fixes"
- phase label: `Perform LINT-PREFLIGHT phase for git commit workflow.`
- prompt body: verbatim:

  ```text
  APPROVED_PLAN:
  [paste the approved plan from Phase 2]

  CRITICAL RULES:
  - NEVER use Write or Edit on staged source files — all fixes via Bash only
  - Skip binary and OOXML files in trailing-whitespace step
  - Stop immediately if corruption detected (line count collapses)
  ```

- return format: `LINT_FIXES`

Store the `LINT_FIXES` value for display in Phase 4.

### 3.2 — Dispatch OOXML Validation Agent

Dispatch the OOXML validator agent with the approved plan:

Dispatch per `knowledge/commit-dispatch-template.md`:

- agent: `al-dev-shared:al-dev-commit-ooxml-validator`
- description: "OOXML ZIP integrity validation"
- phase label: `Perform OOXML-VALIDATE phase for git commit workflow.`
- prompt body: verbatim:

  ```text
  APPROVED_PLAN:
  [paste the approved plan from Phase 2]
  ```

- return format: `OOXML_FAILURES`

If `OOXML_FAILURES` is not `NONE`, show:

```text
⚠️  OOXML VALIDATION FAILURE

The following files failed ZIP validation and cannot be committed:
[OOXML_FAILURES output]

Resolve these files (save in Microsoft Word, not via script), re-stage, and re-run.
```

Stop if any OOXML failures — do not proceed to Phase 4.

---

## Phase 4 — Execution & Summary

### 4.1 — Dispatch Execution Agent

Construct the approved plan from Phase 2:

```text
GROUP_1:
  files: [files]
  message: |
    [approved message verbatim]
GROUP_2:
  ...
```

Dispatch the execution agent:

Dispatch per `knowledge/commit-dispatch-template.md`:

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

Persist the failure context for the recovery agent:

```bash
# Write the execution agent's HOOK_FAILURES output to .dev/hook-failures.json
# Write the approved plan (groups, files, messages) to .dev/commits.json
```

Dispatch the hook-fixer agent (the dispatch frame is documented in
`knowledge/commit-dispatch-template.md`; this phase's prompt differs from the
shared frame and is given in full below):

```text
Agent tool:
  agent: al-dev-shared:al-dev-commit-hook-fixer
  description: "Diagnose and recover from pre-commit hook failures"

Prompt:
  "Diagnose and recover from the pre-commit hook failures from the commit
   execution phase.

   Inputs:
   - .dev/hook-failures.json (hook output and error logs)
   - .dev/commits.json (commit details that triggered the hooks)

   HOOK_FAILURES from execution agent (fallback if files are missing):
   [paste the HOOK_FAILURES block from the execution agent output]

   Follow your agent definition. Return output in exactly the format specified
   (HOOK_FAILURES block with failures array, recovery_status, next_step)."
```

Read the returned `recovery_status` and act:

- **`ready-to-retry`** — scripted fixes were applied and re-staged. Re-dispatch
  the execution agent (4.1) for the affected groups, then re-enter 4.2.
- **`needs-manual-intervention`** — surface each `manual-review` failure
  (`root_cause` + `recommendation`) to the user and stop. Do not retry until
  the user resolves and re-runs `/al-dev-commit`.
- **`non-recoverable`** — report the condition (e.g., a broken hook) to the
  user and abort the commit workflow.

### 4.4 — Summary

Parse the agent output and display the final summary:

```text
Commit workflow complete.

[For each line in COMMITS block:]
  [sha] [emoji] [type(scope)]: [subject]

[N] commits created. [N] skipped.
[If LINT_FIXES from Phase 3.1 is not NONE:]
  Files re-staged after lint: [LINT_FIXES]
[If a hook-fixer recovery ran:]
  Hook recovery: [recovery_status] — [next_step]
```
