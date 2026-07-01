---
name: implement-plugin-health
description: >-
  Closes the health-audit loop: executes an accepted implementation plan,
  verifies each change, and appends `fixed` events to the JSONL event store
  for every **verified** `closes_event_ids:` entry (the distinguishing ledger close-back); tasks that declare no `closes_event_ids:` are skipped. If a task's verification fails, close-back is blocked for that
  task and a `blocked` state is recorded in the run checkpoint.
  Locates the latest docs/superpowers/plans/ plan containing `closes_event_ids:`,
  executes tasks inline (one at a time), archives consumed artifacts, and
  optionally triggers downstream regeneration.
  Triggers on:
  "implement health plan", "run the health plan", "execute health findings plan",
  "implement the accepted plan", "close the ledger", "run implement-plugin-health".
argument-hint: "[--plan <path>] [--compact-every <N>]"
workflow:
  stage: implement
  invoked-by: user
  repeatable: true
  inputs:
    - docs/superpowers/plans/<date>-<topic>.md
    - docs/health/dispositions-open.md
    - .dev/health-loop-state.md
  outputs:
    - docs/health/dispositions-events/<year>/<year>-<month>.jsonl
    - .dev/implement-plugin-health-progress.md
    - .dev/health-loop-state.md
  next: [regenerate-agent-projections, audit-plugin-neutrality, audit-plugin-health]
---

# Implement Health Plan

Closes the self-healing loop by executing an accepted implementation plan
produced by `/plan-plugin-findings` and appending `fixed` events to the JSONL
event store for every `closes_event_ids:` entry in the plan.

Loop position:

`/audit-plugin-health` → dossier → `/record-plugin-dispositions` →
`/plan-plugin-findings` → plan → **`/implement-plugin-health`** → fixed events →
`/regenerate-agent-projections` / `/audit-plugin-neutrality`

---

## Phase-proof requirement

This skill follows `../../knowledge/phase-proof-contract.md` — emit a phase-proof block at each phase boundary before reporting completion or updating `.dev/health-loop-state.md`.

## Prospective procedure log

In addition to the phase-proof block, append one JSON object per completed
phase to `.dev/implement-plugin-health-procedure-log.jsonl`. The log records
the prospective phase sequence that `scripts/health_benchmark_adapter.py`
summarizes against `docs/health/expected_phases.md`.

Use this record shape:

```json
{"skill":"implement-plugin-health","phase":"0","status":"complete","proof":"plan_located","artifact":".dev/implement-plugin-health-progress.md","run_id":"<8-hex>","recorded_at":"2026-06-29T00:00:00+13:00"}
```

Append the record after the phase-proof block and before advancing to the next
phase. Keep the `proof` value aligned with the expected phase table:

| Phase | proof |
| --- | --- |
| 0 | plan_located |
| 1 | tasks_executing |
| 2 | per_task_verified |
| 3 | ledger_closed |
| 4 | artifacts_finalized |
| 5 | loop_closed |

If a phase blocks, append the same shape with `status:"blocked"` and a
`reason` field, then stop without writing later phase records.

## Inputs / Outputs

**Inputs:**

- `docs/superpowers/plans/<date>-*.md` — the accepted plan (must contain
  `closes_event_ids:` entries)
- `docs/health/dispositions-open.md` — the live open accepted events
- `docs/health/dispositions-index.json` — for count verification
- Live subject files named in the plan tasks (skills, agents, knowledge docs)

**Outputs:**

- Edited subject files (from task execution)
- `fixed` JSONL events appended to `docs/health/dispositions-events/`
- Regenerated views: `dispositions-open.md`, `dispositions-current.md`, `dispositions-index.json`
- Archived plan → `docs/superpowers/plans/archived/`
- Archived dossier + findings → `docs/health/archived/`
- `.dev/implement-plugin-health-progress.md` — progress checkpoint (undated,
  fixed path)
- `.dev/implement-plugin-health-procedure-log.jsonl` — prospective phase log

---

## Prerequisites

- A plan file exists in `docs/superpowers/plans/` that contains at least one
  `closes_event_ids:` entry (produced by `/plan-plugin-findings`)
- `docs/health/dispositions-open.md` exists with the relevant `accepted` events
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
`closes_event_ids:`**. Do NOT glob all plans blindly; presence of
`closes_event_ids:` is the mandatory filter.

```bash
# List candidates containing closes_event_ids:
grep -rl "closes_event_ids:" docs/superpowers/plans/ \
  --include="*.md" \
  --exclude-dir=archived \
  | sort | tail -1
```

If no plan passes the filter, stop with:

> No plan containing `closes_event_ids:` found in `docs/superpowers/plans/`. Run
> `/plan-plugin-findings` first to produce an accepted plan, or pass
> `--plan <path>` to target a specific file.

### Resume check

**If the checkpoint file exists,** first check whether it belongs to the current
plan. If the checkpoint's `plan_path` differs from the plan selected above
(`--plan` arg or scan result), the checkpoint belongs to a different plan —
discard it and write a fresh Phase 0 checkpoint for the current plan. Do not
apply the table below to a mismatched checkpoint.

When `plan_path` matches, check `phase` and `status`:

| phase | status | Action |
| --- | --- | --- |
| `0` | `complete` | Proceed to Phase 1 Task 1 |
| `1` | `in_progress` (non-empty `tasks_completed`) | Offer Resume or Restart |
| `1` | `complete` | Proceed to Phase 2 / 3 |
| `3` | `complete` + `result: ledger_closed` | Inform user; ask whether to re-run |
| any other combination | — | Treat as corrupted; default to Restart |

On Restart, **overwrite** the existing checkpoint with the fresh Phase 0 checkpoint
below. If the user does not respond, default to Restart.

On resume, if the current `executor_revision` differs from the checkpoint's, this
skill was self-edited mid-run — require a restart (the self-edit ordering rule
already mandates that a task editing this skill runs last, with a restart
boundary before any later phase; do not re-add that rule, cross-reference it).

**Restart boundary field:** If the checkpoint has `restart_boundary: true` and
`phase: 1` with `status: complete`, skip the restart option and proceed directly
to Phase 2. This enforces a clean phase boundary when a task has marked restart
as blocked (e.g., after a mid-run self-edit that requires a restart).

**If the checkpoint file does not exist:** proceed to Phase 1.

Write initial checkpoint before proceeding:

```yaml
phase: 0
status: complete
result: plan_located
plan_path: <path>
tasks_total: <N>
tasks_completed: []
executor_revision: <git short-hash of .claude/skills/implement-plugin-health/SKILL.md at run start>
run_id: <8-hex generated once at Phase 0 start, e.g. via `python3 -c "import uuid; print(uuid.uuid4().hex[:8])"`>
```

Append the Phase 0 procedure-log record immediately after writing the
checkpoint:

```bash
python3 - <<'PY'
import json
import yaml
from datetime import datetime
from pathlib import Path
# Read run_id from checkpoint
checkpoint_path = Path(".dev/implement-plugin-health-progress.md")
if checkpoint_path.exists():
    with checkpoint_path.open() as f:
        lines = f.read().split("---")
        checkpoint = yaml.safe_load(lines[1]) if len(lines) > 1 else {}
        run_id = checkpoint.get("run_id", "")
else:
    import uuid
    run_id = uuid.uuid4().hex[:8]
    # Generate checkpoint with run_id
    checkpoint = {
        "phase": "0",
        "status": "complete",
        "result": "plan_located",
        "run_id": run_id,
    }
record = {
    "skill": "implement-plugin-health",
    "phase": "0",
    "status": "complete",
    "proof": "plan_located",
    "artifact": ".dev/implement-plugin-health-progress.md",
    "run_id": run_id,
    "recorded_at": datetime.now().astimezone().isoformat(),
}
path = Path(".dev/implement-plugin-health-procedure-log.jsonl")
path.parent.mkdir(parents=True, exist_ok=True)
with path.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps(record, separators=(",", ":")) + "\n")
PY
```

Repeat the same append pattern after each later phase boundary, changing
`phase` and `proof` to the values listed above, and reuse the same `run_id` read back from the checkpoint file — do not generate a new one.

---

## Phase 1: Execute Tasks

### Phase 1–3: Execution and Verification Structure

**Sequential, not coupled:** Phase 1 executes tasks and writes a checkpoint with `tasks_completed[].commit` entries and `closes_event_ids` from the plan. Phase 2 verifies each task's changes against the live repository state. Phase 3 reads the Phase 2 verification results and appends `fixed` events to the ledger.

These phases are **sequential** — each reads the previous phase's output — but they are **not tightly coupled** by design. The checkpoint stores fully self-describing task data (plan task definition + commit hash + closes_event_ids). Phase 3 could logically be separated into a standalone skill, but the current structure keeps execution and ledger closure together for clarity: a single skill owns the complete lifecycle from task execution to ledger closure, with verification as an intermediate gate.

**No atomization needed:** The phases are ordered correctly, and the checkpoint design already supports potential future separation if needed.

---

**Execution mode:** Inline, one task at a time. These tasks are characteristically
small (targeted single-file edits); subagent dispatch adds briefing overhead without
benefit. Execute each task directly using Read/Edit/Bash, then commit before moving
to the next.

**Plan-size guidance:** Plans with more than ~10 tasks risk context compaction in a
single session. If the plan exceeds 10 tasks, note it to the user before starting
and recommend passing `--compact-every 3` on Sonnet or Haiku. If compaction occurs
mid-run, start a fresh session and re-invoke — Phase 0 resumes from the checkpoint.

**`--compact-every <N>` flag:** Inserts voluntary compaction pause points every N
tasks. After each Nth task's checkpoint is written and the pre-task gate passes,
stop and prompt the user to run `/compact` before continuing (see "Compact pause"
below). Recommended cadence: `--compact-every 3` on Sonnet or Haiku; not needed on
Opus for plans ≤10 tasks.

**Sequential enforcement:** Execute one task at a time. If you are about to begin a
second task before the first has committed, stop and report: "Sequential-only
enforcement: the prior task has not yet committed. Complete and commit it before
starting the next."

**Task ordering rule:** Execute tasks in plan order by default. A task may be
scheduled out of order only when its write set is disjoint from every other
task's write set and it reads no other task's output (the independence
definition in `.claude/knowledge/rubber-duck-orchestration.md`). A task that
edits this skill itself must run last, with a restart boundary before any
later phase that depends on the edited text. (A *restart boundary* means: stop
after the task's commit and require an explicit re-invocation of this skill
before any later phase proceeds.)

**Per-task verification** (run before each commit):

1. File persistence check: `git status` shows expected file changes (not
   empty, no unexpected extras)
2. Forbidden-pattern scan: no `[date]`, bare `YYYY-MM-DD` placeholders,
   `TODO`, `TBD`, `Co-Authored-By` (forbidden in file content AND git trailers,
   per `commit-conventions.md`), or `claude:`/`copilot:` prefixed debug tokens
   in changed files (full pattern list: `.claude/knowledge/forbidden-pattern-scan.md`)
3. Acceptance criteria: each criterion stated in the task spec is met in
   actual file content
4. On verification failure: re-execute with the specific failure embedded in
   context; cap at 3 retries; escalate on the third failure

**Commit discipline:** commit per task. Do NOT squash task commits — the
per-task commit hashes are needed for Phase 3 ledger close-back.

Update `.dev/implement-plugin-health-progress.md` **after each task's commit lands:**

```yaml
phase: 1
status: in_progress
result: tasks_executing
tasks_completed:
  - task: "Task 1 — <title>"
    commit: <hash>
    closes_event_ids:
      - disp_20260619_000001
      - disp_20260619_000002
```

**Pre-task commit-hash gate (run before reading the next task spec):** after the
checkpoint write above, read back the last `tasks_completed[].commit` value and
confirm it resolves:

```bash
git log --oneline -1 <hash>   # the just-recorded tasks_completed[].commit
```

If `git log` does not resolve the hash (empty output or non-zero exit), the
prior task's commit did not land as recorded — **stop and report** (the same
failure action as the sequential-enforcement rule above); do not start the next
task. This is a procedural pre-task gate, distinct from the post-hoc Phase 2
verification sweep.

**Compact pause (if `--compact-every N` is set):** After the checkpoint write and
pre-task gate above both pass, check whether `tasks_completed` count is a non-zero
multiple of N. If so, pause before reading the next task spec and prompt:

> "Compact pause: [count] tasks complete. Run `/compact` in your shell, then reply
> 'continue' to proceed to Task [next]."

Wait for the user to reply before reading the next task spec. `/compact` trims the
conversation context in-place — continue in the same session without re-invoking.
The checkpoint on disk is the resume anchor if the session is interrupted instead.

### Mid-point consistency check

For plans with more than 5 tasks, pause at the halfway point and verify
cross-task consistency before continuing:

- No two tasks introduce conflicting terminology or instruction patterns in
  the same shared surface
- Interface names (flags, field names) consistent across all tasks completed
  so far
- No cross-task regressions visible in the changed files

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
```

See `.claude/knowledge/forbidden-pattern-scan.md` for the forbidden-pattern list and scan
command. Run the scan against every changed file in this task's commit.

If a task has no recorded commit hash, or the commit is missing/out of scope,
fail the gate for that task.

**Working-tree-clean gate (post-task).** After resolving a task's commit, confirm
the task left no uncommitted residue in its own paths:

```bash
git status --short -- <task-paths>
```

Expected: empty. A non-empty result means the task under-committed (a changed file
escaped its `git add`) — fail the gate for that task and re-commit the residue
before close-back.

**Rename-task handling.** When a task renames a file with `git mv old new`, `git
mv` already stages **both** the deletion of `old` and the addition of `new`. Never
pass the pre-rename path to a later `git add` — `git add old` after `git mv` errors
with `pathspec 'old' did not match any files` and aborts the task. Stage only the
new path (already staged by `git mv`) and verify with `git status --short -- new`.

### Forbidden-pattern scan

Scan every changed file for:

- `[date]` — unrendered date placeholder
- Bare `YYYY-MM-DD` as a literal value (not a path-format specifier or example)
- `TODO` or `TBD`
- `Co-Authored-By` — AI attribution forbidden per `commit-conventions.md` (file content AND git trailers)
- `claude:` or `copilot:` prefixed debug tokens

See `.claude/knowledge/forbidden-pattern-scan.md` for the forbidden-pattern list and scan
command. Run the scan against every changed file in this task's commit.

Any hit is a blocker. Fix the file and amend or commit a correction before
continuing.

### Acceptance criteria check

Re-read each acceptance criterion from the task spec and confirm it is met in
the live file content. Use `grep` or `Read` as appropriate — do not rely on
memory of what was written.

---

## Phase 3: Close the Ledger

This is the core new behavior. For each completed task, resolve its
`closes_event_ids:` list.

**Tasks without `closes_event_ids:`:** If a completed task has no
`closes_event_ids:` field (or the field is present but empty), skip ledger
close-back for that task entirely. Record it in the final report as "no events
to close" and continue with the next task.

For each `event_id` listed in a completed task's `closes_event_ids`, append a
new `fixed` event with `closes_event_ids` containing that `event_id`, then run
`scripts/health_disposition_store.py regenerate`.

Work through one Resolve → Verify → Append pass before moving to the next event_id:

**Note:** `dispositions-open.md` may appear empty if accepted events have not yet been synced to the markdown history shard. This is expected behavior (file is gitignored; only live-accepted rows appear). If the file appears empty but the plan lists `closes_event_ids:`, proceed to step 1.b (JSONL store lookup) to locate the events.

1. **Resolve** — `closes_event_ids:` lists `event_id` values. Locate the
   event and extract its surface, dimension, object, and finding verbatim
   using this two-step lookup:

   a. **Open-view lookup (primary):** search `docs/health/dispositions-open.md`
      for a row with that `event_id`. This covers the common case where the
      accepted event is still visible.

   b. **JSONL-store fallback (when not in open view):** if the event_id is
      absent from the open view (object-level closure removed it), derive the
      shard path from the event_id date prefix and grep directly:

      ```bash
      # event_id format: disp_YYYYMMDD_NNNNNN
      # Extract YYYY and MM; e.g. disp_20260619_000001 → 2026/2026-06.jsonl
      YEAR=$(echo "$EVENT_ID" | sed 's/disp_\([0-9]\{4\}\).*/\1/')
      MONTH=$(echo "$EVENT_ID" | sed 's/disp_[0-9]\{4\}\([0-9]\{2\}\).*/\1/')
      SHARD="docs/health/dispositions-events/${YEAR}/${YEAR}-${MONTH}.jsonl"
      grep "\"event_id\": \"$EVENT_ID\"" "$SHARD"
      ```

      Parse the returned JSON line to extract `surface`, `dimension`, `object`,
      and `finding` verbatim. If the event_id is not in the shard, escalate to
      the user — do not proceed with an unresolved event.
2. **Verify** — read the live subject file named in the task and confirm the
   change is present. Do not append an event for an unverified change.
   If verification fails: report the failure, omit the event for that task,
   write `phase: 3` and `status: blocked` to
   `.dev/implement-plugin-health-progress.md`, and stop. Do not continue close-back
   and do not write `result: ledger_closed` while any task is unverified. (To drop
   a task from the closure set, amend or re-disposition its events first — there is
   no in-run abandonment path.)
3. **Append** — call `scripts/health_disposition_store.py append_event` with the
   **full required argument set** (`append_event` makes all eight mandatory; see
   the argparse in `scripts/health_disposition_store.py`). The four key fields are
   copied **verbatim** from the accepted event located in step 1:
   - `--surface` / `--dimension` / `--object` / `--finding` — copied verbatim from
     the accepted event being closed (so the new event supersedes it by key match)
   - `--disposition fixed`
   - `--date` today's ISO date (never a placeholder)
   - `--source` the plan path that resolved the finding
   - `--evidence "<commit-hash> — <brief evidence>; verified live <date>"`
   - `--closes-event-ids` the accepted `event_id` being resolved
   Do **not** pass `--event-id`: the new `fixed` event auto-allocates a fresh id and
   the duplicate-id guard rejects reuse. Then run
   `scripts/health_disposition_store.py regenerate` to update
   `dispositions-open.md`, `dispositions-current.md`, and `dispositions-index.json`.
4. **Sync the history shard** — after `append_event`/`regenerate`, run
   `sync_shard --since` to copy all events from today's date into the
   markdown month shard under `docs/health/dispositions-history/`:

   ```bash
   python3 scripts/health_disposition_store.py sync_shard --since <today's ISO date>
   ```

   The shard is an append-only log read by the report phase (`iter_history_rows`,
   for closure chronology and recurrence counts); events not synced here leave
   recurrence accounting wrong in the next sweep.

**Post-loop close gate (scoped to this plan)** — after all `fixed` events are
appended, confirm each `event_id` in the plan's `closes_event_ids` lists no
longer appears in `docs/health/dispositions-open.md`. This scoped check is the
closure gate — not a global pass.

The global checker is run for INFORMATION only; an unrelated open backlog does
NOT block closing this plan:

```bash
python3 scripts/check_ledger_staleness.py --strict || true   # informational; unrelated backlog reported, not blocking
```

**Success criteria:** every `closes_event_ids` entry for this plan has a verified `fixed`
event in the store. Report the global backlog count separately.

Update checkpoint:

```yaml
phase: 3
status: complete
result: ledger_closed
stale_open_rows: 0
```

---

## Phase 4: Finalize Artifacts

Move the implemented plan and its source health artifacts to the archive
directories. The `archived/` subdirectory is auto-excluded by
`select_health_artifacts.py`'s non-recursive `iterdir()` — no exclusion guard
is needed in this skill.

### Archive the plan

> **Note:** `docs/superpowers/plans/` is gitignored, so the plan and archive are
> untracked files — use plain `mv`, **not** `git mv` (which fails with
> `fatal: not under version control`).

```bash
PLAN_ARCHIVE="docs/superpowers/plans/archived/$(date +%Y-%m-%d-%H-%M-%S)-$(basename "<plan-path>")"
mv <plan-path> "$PLAN_ARCHIVE"
```

This prevents same-day plan collisions by adding HH-MM-SS timestamp to the archive filename.

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

### Regenerate derived artifacts

Run downstream regeneration **only if source files changed** during task
execution.

- If any `profile-al-dev-shared/agents/*.md` changed → invoke
  `regenerate-agent-projections`
- If any skills, agents, or knowledge files under `profile-al-dev-shared/`
  changed → invoke `audit-plugin-neutrality`

Check by inspecting the task commits. `<first-task-commit>` is the `commit`
value of the first entry in `tasks_completed` from the checkpoint file
(`.dev/implement-plugin-health-progress.md`):

```bash
git diff <first-task-commit>~1 HEAD --name-only \
  | grep "profile-al-dev-shared/"
```

If no `profile-al-dev-shared/` files changed, skip this phase entirely.

---

## Phase 5: Commit and Report

### Pre-flight clean-tree check

Before proceeding, confirm Phase 3 left no uncommitted residue in the
repository:

```bash
git status --short
```

Expected: empty. A non-empty result means a Phase 3 task under-committed —
return to Phase 2/3 and resolve the residue before continuing Phase 5.

### Close the loop breadcrumb

Read `.dev/health-loop-state.md` if it exists (ignore a missing-file error on
a first-ever run where no prior loop has completed). This read satisfies the
Write tool's in-session read-before-write contract, which is required after a
`/compact` call or a cross-session Phase-5-only resumption where Phase 0's
read is no longer in context.

**Write this BEFORE the ledger-close commit.** Overwrite `.dev/health-loop-state.md`
(schema: `.claude/knowledge/health-loop-state-contract.md`) to mark the loop
closed:

- `stage_completed: implement-plugin-health`
- `completed_at:` today's ISO date
- `next_command: none`
- `next_inputs: []`
- `fresh_session_recommended: false`
- `note:` loop closed; ledger staleness check passed. If source under
  `profile-al-dev-shared/` changed, run `/regenerate-agent-projections` and
  `/audit-plugin-neutrality` next (see Phase 4 "Regenerate derived artifacts").
  If any task changed a skill or agent that the documentation maps describe, a
  `/sync-map-documentation` refresh is **owed** — record it here so the deferred
  map update is not lost. Then run `/audit-plugin-health` to start the next health
  loop.

### Ledger-close commit

The per-task implementation commits were already created in Phase 1. Add ONE
dedicated commit covering:

- The `fixed` events appended to `docs/health/dispositions-events/`
- The synced history shard under `docs/health/dispositions-history/` (the
  `append_row` rows from Phase 3 step 4)
- The regenerated views — `dispositions-current.md`, `dispositions-index.json`,
  and `dispositions.md` (the compatibility view). `dispositions-open.md` may show
  **no diff** when the close empties the open view, and that is expected — stage
  it if changed, do not force it.
- The `.dev/health-loop-state.md` breadcrumb written above

Stage these paths explicitly (the archived dossier/findings are gitignored, so
there is no deletion to stage):

```bash
git add docs/health/dispositions-open.md docs/health/dispositions-events/ \
        docs/health/dispositions-history/ docs/health/dispositions-current.md \
        docs/health/dispositions-index.json docs/health/dispositions.md \
        docs/superpowers/history.md .dev/health-loop-state.md
git commit -m "📦 chore(health): close disposition events for <plan-topic>"
```

### Final report

Present:

- Tasks completed (count and titles)
- Disposition events closed (event IDs and objects)
- Artifacts archived (plan path → archived path)
- Global backlog count from `check_ledger_staleness.py --strict` (informational)

The loop is closed when all `closes_event_ids` in the plan have verified `fixed`
events in the store and the ledger-close commit has landed. Report the global
backlog count separately.

---

## Error Handling

Conservative failure mode:

- Do not append `fixed` events until Phase 2 verification passes
  for the relevant task
- Do not archive any artifact until the ledger-close commit is staged
- Do not claim the loop is closed until all plan `closes_event_ids` have `fixed`
  events in the store (run `check_ledger_staleness.py --strict` for informational backlog count)
- Always update `.dev/implement-plugin-health-progress.md` to reflect blocked
  state on failure; do not delete the checkpoint

---

## Progress Checkpoint Format

Location: `.dev/implement-plugin-health-progress.md`

YAML structure:

```yaml
phase: <0|1|2|3|4|5>
status: <pending|in_progress|complete|blocked>
result: <description>
plan_path: <path>
tasks_total: <N>
tasks_completed:
  - task: "Task N — <title>"
    commit: <hash>
    closes_event_ids:
      - disp_20260619_000001
      - disp_20260619_000002
stale_open_rows: <count>    # populated in Phase 3
executor_revision: <git short-hash of implement-plugin-health/SKILL.md at run start>
restart_boundary: <bool>    # optional; when true and phase 1 is complete, skip restart at this boundary
```
