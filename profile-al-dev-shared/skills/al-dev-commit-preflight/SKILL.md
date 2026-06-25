---
name: al-dev-commit-preflight
description: >-
  Validate staged changes, dispatch analysis and message-drafting agents,
  collect user approval, and persist the approved commit plan to
  .dev/commit-preflight.md. Phases 0–2 of the commit workflow. Called by
  /al-dev-commit; can also run standalone when a user wants to plan commits
  without immediately executing them.
  Triggers on: "plan these commits", "draft commit messages", "analyse staged changes".
argument-hint: "[--ticket-id=<id>]"
---

# `/al-dev-commit-preflight` — Commit Analysis and Confirmation

Phases 0–2 of the atomic commit workflow. Validates staged files, dispatches
the analysis and message-drafting agents, handles user confirmation gates,
and persists the approved plan to `.dev/commit-preflight.md` for consumption
by `/al-dev-commit-execute`.

You never run `git commit` yourself — always delegate via `/al-dev-commit-execute`.

Follow every step in order. Do not skip steps or proceed past a stop condition.

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
- **init-context fails** — do not hard-stop solely because the companion
  `al-dev-init-context` capability is unavailable. Warn that no project
  instructions file could be created, then degrade to a minimal inferred
  context (naming prefix, conventions, and patterns observed in nearby
  files) per `knowledge/companion-context-ownership.md`, marking the
  commit-message context as provisional, and proceed to 0.2.
- **no** — warn that commit-message quality may be reduced without project
  instructions, then degrade to the same minimal inferred context per
  `knowledge/companion-context-ownership.md` and proceed to 0.2 rather than
  stopping.

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

`$ARGUMENTS` is harness-supplied — it contains the user's typed arguments after the skill name (e.g. `--ticket-id=12345`). `$BASH_REMATCH` is a standard bash variable populated by `=~` and needs no further explanation.

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
```

Continue to Step 0.3 regardless of which branch was taken.

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

Run AL compile and verify any errors originate in staged files before proceeding.

**See:** `knowledge/commit-compile-gate.md` for the full compile-gate decision tree.

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

---

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

---

### 1.3 — Dispatch Message-Drafting Agent

Dispatch the message-drafting agent with the analysis results:

Dispatch per `knowledge/commit-dispatch-template.md`:

- agent: `al-dev-shared:al-dev-commit-group-drafter` (model: haiku)
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

## Phase 2 Completion — Persist Approved Plan

After all groups are confirmed or skipped in Phase 2.2, and after the Phase 2.3
Mixed AL/DOCX check completes (or is skipped), persist the approved plan to disk:

```bash
mkdir -p .dev
```

> **Write guard (pre-write):** if `.dev/commit-preflight.md` already exists from
> a prior run, Read it before overwriting (an unread existing file fails the
> write). The post-write existence check is already enforced below. See
> `knowledge/workflow-resilience.md` Write Protocol.

Write `.dev/commit-preflight.md` with this content (one `GROUP_N` block per
confirmed commit from Phase 2.2; omit skipped groups entirely):

> **Co-Authored-By prohibition:** Do NOT include a `Co-Authored-By`
> trailer in any `message:` block. Strip any trailer the drafter agent
> added before writing.

```text
# Approved Commit Plan
# Written by /al-dev-commit-preflight — consumed by /al-dev-commit-execute

APPROVED_GROUPS:
  GROUP_1:
    files:
      - <file path>
      - <file path>
    message: |
      <approved message verbatim — do NOT include a Co-Authored-By trailer>
  GROUP_2:
    files:
      - ...
    message: |
      ...

LINT_CONTEXT:
  prior_lint_report: <absolute path from Phase 0.4, or "none">
  mixed_al_docx: <yes | no — from Phase 2.3>
  pre_existing_errors_acknowledged: <true | false — from Phase 0.3 step 4>
```

Verify the file was written:

```bash
ls -la .dev/commit-preflight.md
wc -l .dev/commit-preflight.md
```

If the file is missing or empty, stop and report: "Failed to write
`.dev/commit-preflight.md`. Check that `.dev/` is writable and retry."

Tell the user:

```text
Commit plan approved and saved → .dev/commit-preflight.md
<N> commit(s) planned.

Run /al-dev-commit-execute to run lint preflight and execute the commits,
or /al-dev-commit again to restart the full workflow.
```

Return normally. Do not invoke `/al-dev-commit-execute` from here — the caller
(`/al-dev-commit`) handles the handoff.
