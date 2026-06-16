# Workflow Resilience

Protocols for multi-phase skills (`al-dev-plan`,
`al-dev-develop-orchestrate`) to survive usage limits and resume cleanly.

## Progress Checkpointing

### Write Protocol

Ensure `.dev/` exists before writing:

```bash
mkdir -p .dev
```

**Write guard (apply to every `.dev/` write):**

- **New file** (path does not yet exist): write directly — no prior Read needed.
- **Existing file** (path may already exist): before overwriting, run
  `ls -la <path>`; if it exists, Read it first. Overwriting a file that was not
  Read in this session fails with "File has not been read yet". This is a
  *pre-write Read-if-exists* check.
- **After every write** (*post-write* check): confirm with `ls -la <path>`, and
  `wc -l <path>` when the content matters, before reporting the step complete.

After each named phase boundary, overwrite
`.dev/progress.md` with:

```markdown
## Progress Checkpoint

**Completed phases:** Phase 1 — Read Context, Phase 3 — Architect Debate

**Current state:** [1-2 sentences]

**Next step:** [exact next action]

**Pending decisions:** [list, or "none"]
```

The newest checkpoint state is authoritative — overwrite, never append.
Write the checkpoint before spawning subagents for the next
phase and again after collecting their output.

For `/al-dev-develop-orchestrate`, also refresh the dated
`.dev/YYYY-MM-DD-al-dev-develop-progress.md` after each named
phase so the durable session narrative stays aligned with the
latest checkpoint.

### Develop-Specific Resume Pack

For `/al-dev-develop-orchestrate`, maintain these files together:

- `.dev/progress.md` — latest checkpoint
- `.dev/YYYY-MM-DD-al-dev-develop-progress.md` — dated session
  narrative
- `.dev/YYYY-MM-DD-al-dev-develop-checklist.md` — extracted
  implementation checklist
- `.dev/YYYY-MM-DD-al-dev-develop-scope.md` — approved scope
  boundary

Resume order:

1. `.dev/progress.md`
2. latest dated progress file
3. latest checklist
4. latest scope file

Only re-read the full solution plan if one of the above files
is missing or contradictory.

### Read Protocol (Phase 0)

At skill startup, before Phase 1, follow the applicable resume
path for the current skill.

For `/al-dev-develop-orchestrate`, the Develop-Specific Resume Pack above is
authoritative:

- Read `.dev/progress.md` if it exists
- Read the latest dated develop progress file if it exists
- Read the latest checklist if it exists
- Read the latest scope file if it exists
- Present the gathered resume state and ask:
  *"Resume from checkpoint? (yes / restart)"*

This prompt is user-facing and must be surfaced before any later
phase work begins.

For other skills covered by this document, read `.dev/progress.md`
if it exists. If the file exists, display its contents and ask:
*"Resume from checkpoint? (yes / restart)"*

- **yes** — skip completed phases, start from the recorded
  next step
- **restart** — start fresh and do not reuse checkpoint artifacts
  from the abandoned run:
  - delete `.dev/progress.md`
  - for `/al-dev-develop-orchestrate`, either delete the latest dated develop
    progress/checklist/scope files from that abandoned run or
    ignore them explicitly for the restarted session and record
    that choice in the new `.dev/progress.md`
  - create a new dated develop progress file for the restarted run
    before later phases regenerate checklist and scope

If no file exists, proceed to Phase 1 normally.

## Subagent Fallback

If an agent returns empty output or hits a usage limit:

1. Use any partial output the agent returned before failing
2. If no output at all, synthesize from the relevant plan
   document:
   - For develop phases: `.dev/02-solution-plan.md`
   - For plan phases: latest `.dev/*-al-dev-interview-requirements.md`
3. Log the fallback in `.dev/progress.md` under
   **Pending decisions**: `"Phase X synthesized directly
   (agent hit limit)"`
4. For plan/develop waves, prefer single-agent execution if
   a parallel wave has already failed once

## Recovery After Working-Tree Loss

If a user reports that a working-tree change was lost — for example after a
`git reset`, `git checkout`, or a failed stash pop — and asks you to reapply
it, **do not search git history**. Git only records *committed* work; an
uncommitted edit that was discarded leaves no trace in `git show`, `git log`,
or `git reflog` of a commit. Searching history burns tool calls on a dead end.

Instead, reconstruct the intended final state directly from the source:

1. Ask the user (or infer from the request) what the change was meant to
   achieve.
2. Search the relevant source files for the current state and apply the
   intended edit directly.

Example: a user reports that a procedure was made `internal` and the change was
lost to a hard reset. Do not hunt for the commit — grep the feature's source
for the public procedure and change its scope to `internal` directly.
