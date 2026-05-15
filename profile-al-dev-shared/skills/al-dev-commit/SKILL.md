---
name: al-dev-commit
description: >-
  Use when ready to commit staged changes — especially after
  development work where scope creep (unapproved field removals,
  extra file deletions, hallucinated changes) may have occurred.
---

# `/al-dev-commit` — Atomic Commit Workflow

Thin orchestrator for the two-phase commit workflow. Collects
context, dispatches the analysis agent, handles all user
confirmation gates, then dispatches the execution agent.

You never run `git commit` yourself — always delegate.

Follow every step in order. Do not skip steps or proceed past a
stop condition.

---

## Step 1 — Guard: Verify Project Context

Check for the project instructions file (project instructions file, AGENTS.md,
or equivalent for your harness):

```bash
ls project instructions file AGENTS.md 2>/dev/null | head -1
```

If no project instructions file is found:

Tell the user: "No project instructions file found in this repository.
Project context is required to generate correct commit
messages. Would you like me to create it now via
`/al-dev-init-context`? (yes / no)"

- **yes** — invoke the `al-dev-init-context` skill via the
  Skill tool (not a subagent), wait for it to complete, then
  proceed to Step 2 to load the newly created project
  instructions file
- **init-context fails** — stop with: "Could not create
  the project instructions file automatically. Please run
  `/al-dev-init-context` or create it manually, then re-run
  `/al-dev-commit`."
- **no** — stop with: "Please create the project
  instructions file manually or run `/al-dev-init-context`,
  then re-run `/al-dev-commit`."

---

## Step 2 — Load Project Context

Load the project instructions file from your harness's standard
locations (earlier files provide defaults, later files override):

1. Global defaults location (if present, per harness mapping)
2. AL profile defaults location (if present, per harness mapping)
3. `./[project instructions file]` — project-specific (required)

Extract and hold in working memory:

- **Valid scopes** — e.g. `price`, `rebate`, `ui`, `config`, `docs`
- **Object ID prefix** — e.g. `ACUKPR`
- **Object ID range** — e.g. `50901–50950`
- **AL file naming pattern** — e.g. `Name.ObjectType.al`

Check for a Freshdesk ticket:

```bash
TICKET=$(ls .dev/*-al-dev-ticket-ticket-context.md 2>/dev/null \
  | sort | tail -1)
[ -n "$TICKET" ] && head -10 "$TICKET"
```

Extract ticket number from `TICKET: #<number>` if present.
Hold as **FD ticket number**.

---

## Step 3 — Verify File Integrity

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

Tell the user: "File integrity check failed — <file> lost lines
during edit. This may indicate a bash heredoc or perl regex issue.
Check your edits before committing."

**Stop.** Do not proceed.

---

## Step 4 — Check Staged Files

```bash
git diff --cached --name-only --diff-filter=ACMRDT
```

If empty:

Tell the user: "No staged files found. Use `git add` to stage
your changes, then run `/al-dev-commit` again."

**Stop.**

---

## Step 5 — Establish Gitmoji Style

Check the project's recent commit style:

```bash
git log -5 --oneline
```

Extract the emoji pattern (e.g., `✨ feat:`, `🐛 fix:`, `📝 docs:`).

Hold as **PROJECT_GITMOJI_STYLE**.

---

## Step 5.5 — Advisory Alignment Check

Run the alignment check in advisory mode (non-blocking):

```bash
SCRIPT="$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-align/check-alignment.py"
if [ -f "$SCRIPT" ]; then
  ALIGN_ADVISORY=$(python3 "$SCRIPT" --mode advisory)
fi
```

If `$ALIGN_ADVISORY` JSON contains non-empty `forbidden_tokens` or `missing_mappings`, surface a warning (N = `len(forbidden_tokens) + len(missing_mappings)`):

```
⚠️  Alignment advisory: N issue(s) found. Run /al-dev-align to inspect and fix.
```

Continue to Step 6 regardless — this check is advisory only.

---

## Step 6 — Dispatch Analysis Agent

```text
Agent tool:
  agent: al-dev-shared:al-dev-commit-agent
  description: "Commit analysis: analyse staged changes"

Prompt:
  "Perform ANALYSIS phase for git commit workflow.

   Phase: analysis

   PROJECT_CONTEXT:
   - Valid scopes: [list from Step 2]
   - Object ID prefix: [from Step 2]
   - AL naming pattern: [from Step 2]
   - Gitmoji style: [from Step 5]

   FD_TICKET: [ticket number from Step 2, or empty]

   Follow the analysis phase instructions in your agent definition.

   Return output in exactly the format specified (MANIFESTS block,
   PROPOSED_GROUPS block, DELETIONS, WARNINGS)."
```

---

## Step 7 — Deletion Audit Gate

Read the `DELETIONS` block from the agent output.

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

- **yes** — continue to Step 6
- **no** — run `git restore --staged <file>` for every deleted
  file, then **stop** (user must re-run `/al-dev-commit` after
  reviewing their staged files)
- **list-to-keep** — user names files to unstage; run
  `git restore --staged <file>` for each, then **stop**

If no deleted files: continue to Step 8.

---

## Step 8 — Present Manifests and Confirm Commit Groups

Display the `MANIFESTS` block from the agent output, then the
`PROPOSED_GROUPS` block:

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

- **yes** — continue to Step 7
- **adjust** — user provides revised groupings; update your
  working copy of the plan and re-present, then wait for
  confirmation again
- **cancel** — abort everything, leave all files staged unchanged

---

## Step 9 — Confirm Each Commit Message

For each group, display the draft message from the agent output
alongside the change manifest for that group, and ask for
confirmation:

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

After all groups are confirmed or skipped, proceed to Step 10.

---

## Step 9.5 — Mixed `.al` + `.docx` acknowledgement gate

Inspect the analysis agent output `WARNINGS` block for a `MIXED_AL_DOCX` entry.

If present, show:

```text
⚠️  MIXED AL + DOCX STAGING DETECTED

This commit plan includes both `.al` source files and `.docx` layout files.
High-risk pattern: automated tool rewrites of Word layouts can produce malformed OOXML.

Confirm all `.docx` files were edited and saved in Microsoft Word (not scripted),
and that OOXML ZIP validation has passed.

Proceed to execution? (yes / no)
```

User response:

- `yes` → continue to Step 10
- `no` → stop; leave staged files unchanged (user must re-run `/al-dev-commit` after reviewing staged files)

If no `MIXED_AL_DOCX` warning exists, continue directly to Step 10.

---

## Step 10 — Dispatch Execution Agent

Construct the approved plan from Step 9:

```text
GROUP_1:
  files: [files]
  message: |
    [approved message verbatim]
GROUP_2:
  ...
```

```text
Agent tool:
  agent: al-dev-shared:al-dev-commit-agent
  description: "Commit execution: [N] commits"

Prompt:
  "Perform EXECUTE phase for git commit workflow.

   Phase: execute

   APPROVED_PLAN:
   [paste the approved plan constructed above]

   CRITICAL RULES:
   - NEVER add Co-Authored-By trailers to commit messages
   - Use git -C <path> instead of cd <path> && git
   - Verify file integrity (wc -l) for all modified files after commits

   Follow the execute phase instructions in your agent definition.

   Return output in exactly the format specified (COMMITS, SKIPPED,
   LINT_FIXES, HOOK_FAILURES)."
```

---

## Step 11 — Summary

Parse the agent output. Display:

```text
Commit workflow complete.

[For each line in COMMITS block:]
  [sha] [emoji] [type(scope)]: [subject]

[N] commits created. [N] skipped.
[If LINT_FIXES is not NONE:]
  Files re-staged after lint: [LINT_FIXES]
[If HOOK_FAILURES is not NONE:]
  Hook failures:
    [HOOK_FAILURES block]
```
