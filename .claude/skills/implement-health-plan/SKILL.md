---
name: implement-health-plan
description: >-
  Execute an accepted health-findings implementation plan and close the
  disposition ledger. Locates the latest docs/superpowers/plans/ plan containing
  `closes_rows:`, dispatches superpowers:subagent-driven-development for task
  execution, verifies each change, appends `fixed` rows to
  docs/health/dispositions.md, archives consumed artifacts, and optionally
  triggers downstream regeneration. Triggers on:
  "implement health plan", "run the health plan", "execute health findings plan",
  "implement the accepted plan", "close the ledger", "run implement-health-plan".
argument-hint: "[--plan <path>]"
workflow:
  stage: implement
  invoked-by: user
  repeatable: true
  inputs:
    - docs/superpowers/plans/<date>-<topic>.md
    - docs/health/dispositions.md
  outputs:
    - docs/health/dispositions.md
    - .dev/implement-health-plan-progress.md
  next: [projection-sync, align-harness-repos, audit-knowledge-quality]
---

# Implement Health Plan

Closes the self-healing loop by executing an accepted implementation plan
produced by `/plan-health-findings` and writing `fixed` rows back to the
disposition ledger for every `closes_rows:` entry in the plan.

Loop position:

`/plugin-health-audit` → dossier → `/record-health-dispositions` →
`/plan-health-findings` → plan → **`/implement-health-plan`** → fixed rows →
`/projection-sync` / `/align-harness-repos`

---

## Inputs / Outputs

**Inputs:**

- `docs/superpowers/plans/<date>-*.md` — the accepted plan (must contain
  `closes_rows:` entries)
- `docs/health/dispositions.md` — the live disposition ledger
- Live subject files named in the plan tasks (skills, agents, knowledge docs)

**Outputs:**

- Edited subject files (from task execution)
- `fixed` rows appended to `docs/health/dispositions.md`
- Archived plan → `docs/superpowers/plans/archived/`
- Archived dossier + findings → `docs/health/archived/`
- `.dev/implement-health-plan-progress.md` — progress checkpoint (undated,
  fixed path)

---

## Prerequisites

- A plan file exists in `docs/superpowers/plans/` that contains at least one
  `closes_rows:` entry (produced by `/plan-health-findings`)
- `docs/health/dispositions.md` exists with the relevant `accepted` rows
- The pre-commit gate passes: `python3 scripts/check_ledger_staleness.py`
  exits 0 before this skill begins

---

## Phase 0: Locate Plan and Resume

### Locate the target plan

First read `.dev/health-loop-state.md` if it exists (schema:
`.claude/knowledge/health-loop-state-contract.md`). If its `next_command` names
this skill, prefer its `next_inputs` plan path over a blind scan. If it names a
different loop step, tell the user the pointer expects `<that command>` and ask
whether to continue here anyway. If absent, fall back to the scan below.

If `--plan <path>` was passed, use that path directly. Otherwise, scan
`docs/superpowers/plans/` (non-recursively — archived/ is excluded) and select
the **latest file by date prefix that contains the literal string
`closes_rows:`**. Do NOT glob all plans blindly; presence of `closes_rows:` is
the mandatory filter.

```bash
# List candidates containing closes_rows:
grep -rl "closes_rows:" docs/superpowers/plans/ \
  --include="*.md" \
  --exclude-dir=archived \
  | sort | tail -1
```

If no plan passes the filter, stop with:

> No plan containing `closes_rows:` found in `docs/superpowers/plans/`. Run
> `/plan-health-findings` first to produce an accepted plan, or pass
> `--plan <path>` to target a specific file.

### Resume check

**If the checkpoint file exists,** check `phase` and `status`:

| phase | status | Action |
|---|---|---|
| `0` | `complete` | Proceed to Phase 1 Task 1 |
| `1` | `in_progress` (non-empty `tasks_completed`) | Offer Resume or Restart |
| `1` | `complete` | Proceed to Phase 2 / 3 |
| `3` | `complete` + `result: ledger_closed` | Inform user; ask whether to re-run |
| any other combination | — | Treat as corrupted; default to Restart |

**Plan-path guard (evaluate after reading the resume table, before acting on it):** Compare the
checkpoint's `plan_path` to the plan selected above (`--plan` arg or scan
result). If they differ, the checkpoint belongs to a different plan — do NOT
resume it. Discard it and write a fresh Phase 0 checkpoint for the current plan.
Apply the resume table only when `plan_path` matches.

On Restart, **overwrite** the existing checkpoint with the fresh Phase 0 checkpoint
below. If the user does not respond, default to Restart.

On resume, if the current `executor_revision` differs from the checkpoint's, this
skill was self-edited mid-run — require a restart (the self-edit ordering rule
already mandates that a task editing this skill runs last, with a restart
boundary before any later phase; do not re-add that rule, cross-reference it).

**If the checkpoint file does not exist:** proceed to Phase 1.

Write initial checkpoint before proceeding:

```yaml
phase: 0
status: complete
result: plan_located
plan_path: <path>
tasks_total: <N>
tasks_completed: []
executor_revision: <git short-hash of .claude/skills/implement-health-plan/SKILL.md at run start>
```

---

## Phase 1: Execute Tasks

**REQUIRED SUB-SKILL:** Invoke `superpowers:subagent-driven-development` for
same-session execution, or `superpowers:executing-plans` for execution in a
separate session. Both run one implementation subagent at a time — never
dispatch two implementation subagents concurrently in one worktree.

**Task ordering rule:** Execute tasks in plan order by default. A task may be
scheduled out of order only when its write set is disjoint from every other
task's write set and it reads no other task's output (the independence
definition in `.claude/knowledge/rubber-duck-orchestration.md`). A task that
edits this skill itself must run last, with a restart boundary before any
later phase that depends on the edited text.

Pass the full CLAUDE.md **Plan Task Verification Standard** checklist into
every dispatch prompt:

> Before completing each task:
>
> 1. File persistence check: `git status` shows expected file changes (not
>    empty, no unexpected extras)
> 2. Forbidden-pattern scan: no `[date]`, bare `YYYY-MM-DD` placeholders,
>    `TODO`, `TBD`, `Co-Authored-By` (forbidden in file content AND git trailers,
>    per `commit-conventions.md`), or `claude:`/`copilot:` prefixed debug tokens
>    in changed files
> 3. Acceptance criteria: each criterion stated in the task spec is met in
>    actual file content
> 4. On verification failure: re-execute with the specific failure embedded in
>    context; cap at 3 retries; escalate on the third failure

**Commit discipline:** commit per task as the sub-skill default. Do NOT squash
task commits — the per-task commit hashes are needed for Phase 3 ledger
close-back.

Update `.dev/implement-health-plan-progress.md` as each task completes:

```yaml
phase: 1
status: in_progress
result: tasks_executing
tasks_completed:
  - task: "Task 1 — <title>"
    commit: <hash>
    closes_rows: ["#NNN", "#MMM"]
```

---

## Phase 1b: Code Review

**REQUIRED SUB-SKILL:** After each task, invoke
`superpowers:requesting-code-review` for a per-task scope review.

For plans with more than two tasks, schedule a **mid-point integration review**
after the halfway task (e.g., after Task 2 of 4, or Task 3 of 5). The
integration review inspects the whole module assembled so far, not just the
latest task. Integration review checklist:

- Patterns and rules tested against the full input set, not only inputs
  introduced in the current task
- Interface names (flags, field names) consistent across all definitions added
  so far
- No cross-task regressions introduced by the sequence of changes

---

## Phase 2: Verify Per Task (Gate Before Close-Back)

For each completed task, run the following gate before proceeding to Phase 3.
A task that fails this gate must be re-executed before ledger close-back
proceeds.

### File persistence check

For each completed task, resolve its recorded commit hash from
`tasks_completed[].commit` in the checkpoint and verify that commit's scope. Do
NOT use a bare `HEAD~1` — when Phase 2 runs after all tasks it covers only the
final commit, so earlier task commits escape verification.

```bash
git show --stat <task-commit>                 # files changed in that task's commit
git show <task-commit> -- <changed-files> | grep -E '\[date\]|TODO|TBD|claude:|copilot:'
```

If a task has no recorded commit hash, or the commit is missing/out of scope,
fail the gate for that task.

### Forbidden-pattern scan

Scan every changed file for:

- `[date]` — unrendered date placeholder
- Bare `YYYY-MM-DD` as a literal value (not a path-format specifier or example)
- `TODO` or `TBD`
- `Co-Authored-By` — AI attribution forbidden per `commit-conventions.md` (file content AND git trailers)
- `claude:` or `copilot:` prefixed debug tokens

```bash
git show <task-commit> -- <changed-files> | grep -E '\[date\]|TODO|TBD|claude:|copilot:'
grep -rEn '[0-9]{4}-[0-9]{2}-[0-9]{2}' <changed-files>   # bare YYYY-MM-DD placeholders
grep -rn  'Co-Authored-By'             <changed-files>   # AI attribution (forbidden per commit-conventions.md)
```

Any hit is a blocker. Fix the file and amend or commit a correction before
continuing.

<!-- Note: the global CLAUDE.md commit practice appends a Co-Authored-By trailer;
     that practice must be reconciled against commit-conventions.md separately — do not
     edit CLAUDE.md or commit-conventions.md here. -->

### Acceptance criteria check

Re-read each acceptance criterion from the task spec and confirm it is met in
the live file content. Use `grep` or `Read` as appropriate — do not rely on
memory of what was written.

---

## Phase 3: Close the Ledger

This is the core new behavior. For each completed task, resolve its
`closes_rows:` list.

**Tasks without `closes_rows:`:** If a completed task has no `closes_rows:`
field (or the field is present but empty), skip ledger close-back for that
task entirely. Record it in the final report as "no ledger rows to close" and
continue with the next task.

For each `#NNN` ID in a completed task's `closes_rows:`, work through one
Resolve → Verify → Append pass before moving to the next ID:

1. **Resolve** — `closes_rows:` lists `#NNN` IDs from the ID column (leftmost)
   of `docs/health/dispositions.md` — never a file-line number. Locate the row
   with that ID and extract its ID, Surface, Dimension, Object, and Finding
   verbatim.
2. **Verify** — read the live subject file named in the task and confirm the
   change is present. Do not append a row for an unverified change.
3. **Append** — add one `fixed` row at the bottom of the table. The ledger
   uses the **eight-column** schema:

   `| ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence / note |`

   Copy ID, Surface, Dimension, Object, and Finding verbatim from the
   accepted row, then set Disposition = `fixed`, Date = today's ISO date
   (never a placeholder), and Evidence / note =
   `<commit-hash> — <brief evidence>; verified live <date>; closes #NNN`.
   Re-read the appended row and confirm all eight cells are populated. Never
   reorder or rewrite existing rows.

Example:

| #042 | tooling | quality | my-skill | Description too long | fixed | 2026-06-10 | a1b2c3d — trimmed to 150 chars; verified live 2026-06-10; closes #042 |

**Post-loop close gate (scoped to this plan)** — after all `fixed` rows are
appended, confirm each `#NNN` in the plan's `closes_rows` list now has a `fixed` row
in the ledger. This scoped check is the closure gate — not a global pass.

The global checker is run for INFORMATION only; an unrelated open backlog does
NOT block closing this plan:

```bash
python3 scripts/check_ledger_staleness.py --strict || true   # informational; unrelated backlog reported, not blocking
```

**Success criteria:** every `closes_rows` ID for this plan has a verified `fixed`
row. Report the global backlog count separately.

Update checkpoint:

```yaml
phase: 3
status: complete
result: ledger_closed
stale_open_rows: 0
```

---

## Phase 4: Archive Consumed Artifacts

Move the implemented plan and its source health artifacts to the archive
directories. The `archived/` subdirectory is auto-excluded by
`select_health_artifacts.py`'s non-recursive `iterdir()` — no exclusion guard
is needed in this skill.

### Archive the plan

```bash
mv <plan-path> docs/superpowers/plans/archived/
```

### Archive the dossier and findings file

Identify the dossier that sourced the plan. Check the plan's `health_filters:`
block for the surface(s), then select the matching dossier. **If
`health_filters.surfaces` lists multiple values (e.g., `[plugin, tooling]`),
run the selection and archival steps once per surface.**

```bash
python3 scripts/select_health_artifacts.py \
  --directory docs/health \
  --kind health \
  --surface <surface>
```

Move the dossier and its companion `*-findings.md` (same date prefix):

```bash
mv docs/health/<date>-<surface>-health.md docs/health/archived/
mv docs/health/<date>-<surface>-findings.md docs/health/archived/
```

Repeat the `select_health_artifacts.py` call and both `mv` commands for each
additional surface listed in `health_filters.surfaces`.

If a `*-findings.md` does not exist for the selected dossier (e.g., the dossier
predates the findings-file convention), skip the findings move and note it in
the report.

### Archive paired review artifacts and record terminal status

If the plan has paired review/commentary artifacts (e.g.
`docs/superpowers/plans/<plan>-review.md`, or per-task code-review outputs in
`.dev/`), move them alongside the plan:

```bash
mv docs/superpowers/plans/<plan>-review.md docs/superpowers/plans/archived/ 2>/dev/null || true
```

Append a terminal-status entry for the consumed plan to
`docs/superpowers/history.md` (tracked): one line —
`<date> | <plan-topic> | implemented; rows closed: [#NNN, ...]`.

---

## Phase 4.5: Regenerate Derived Artifacts

Run downstream regeneration **only if source files changed** during task
execution.

- If any `profile-al-dev-shared/agents/*.md` changed → invoke
  `projection-sync`
- If any skills, agents, or knowledge files under `profile-al-dev-shared/`
  changed → invoke `align-harness-repos`

Check by inspecting the task commits. `<first-task-commit>` is the `commit`
value of the first entry in `tasks_completed` from the checkpoint file
(`.dev/implement-health-plan-progress.md`):

```bash
git diff <first-task-commit>~1 HEAD --name-only \
  | grep "profile-al-dev-shared/"
```

If no `profile-al-dev-shared/` files changed, skip this phase entirely.

---

## Phase 5: Commit and Report

### Close the loop breadcrumb

**Write this BEFORE the ledger-close commit.** Overwrite `.dev/health-loop-state.md`
(schema: `.claude/knowledge/health-loop-state-contract.md`) to mark the loop
closed:

- `stage_completed: implement-health-plan`
- `completed_at:` today's ISO date
- `next_command: none`
- `next_inputs: []`
- `fresh_session_recommended: false`
- `note:` loop closed; ledger staleness check passed. If source under
  `profile-al-dev-shared/` changed, run `/projection-sync` and
  `/align-harness-repos` next (see Phase 4.5).

### Ledger-close commit

The per-task implementation commits were already created in Phase 1. Add ONE
dedicated commit covering:

- The `fixed` rows appended to `docs/health/dispositions.md`
- The `.dev/health-loop-state.md` breadcrumb written above

```bash
git add docs/health/dispositions.md
# docs/superpowers/plans/ and docs/health/* are gitignored (see .gitignore); the
# archived plan and dossier were relocated by `mv` in Phase 4 and are NOT tracked
# — do NOT `git add` them (the add is a no-op/error). Stage only tracked files.
git add .dev/health-loop-state.md            # tracked breadcrumb — write it BEFORE this commit (see health-loop-state-contract Persistence semantics)
git commit -m "chore(health): close ledger rows [N,...] — <plan-topic>"
```

### Final report

Present:

- Tasks completed (count and titles)
- Disposition rows closed (row numbers and objects)
- Artifacts archived (plan path → archived path)
- Global backlog count from `check_ledger_staleness.py --strict` (informational)

The loop is closed when all `closes_rows` IDs in the plan have verified `fixed`
rows in the ledger and the ledger-close commit has landed. Report the global
backlog count separately.

---

## Error Handling

Conservative failure mode:

- Do not edit `docs/health/dispositions.md` until Phase 2 verification passes
  for the relevant task
- Do not archive any artifact until the ledger-close commit is staged
- Do not claim the loop is closed until all plan `closes_rows` IDs have `fixed`
  rows (run `check_ledger_staleness.py --strict` for informational backlog count)
- Always update `.dev/implement-health-plan-progress.md` to reflect blocked
  state on failure; do not delete the checkpoint

---

## Progress Checkpoint Format

Location: `.dev/implement-health-plan-progress.md`

YAML structure:

```yaml
phase: <0|1|1b|2|3|4|5>
status: <pending|in_progress|complete|blocked>
result: <description>
plan_path: <path>
tasks_total: <N>
tasks_completed:
  - task: "Task N — <title>"
    commit: <hash>
    closes_rows: ["#NNN", "#MMM"]
stale_open_rows: <count>    # populated in Phase 3
executor_revision: <git short-hash of implement-health-plan/SKILL.md at run start>
```
