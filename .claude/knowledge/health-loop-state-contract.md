# Health Loop State Contract

Canonical schema and lifecycle for `.dev/health-loop-state.md` — the single
durable breadcrumb that carries the health-audit loop from one skill to the
next. Each loop skill **reads** this file at its Phase 0 and **writes** it on
completion. The breadcrumb is what lets the loop survive context-window
compaction and fresh-session boundaries: the "what runs next" pointer lives on
disk, not only in conversation context.

## Loop order

`/plugin-health-audit` → dossier → `/plugin-health-report` →
`/record-health-dispositions` → `/plan-health-findings` → plan →
`/implement-health-plan` → ledger closed

## File location

`.dev/health-loop-state.md` (undated, fixed path — there is only ever one live
loop pointer). It references generic skill slash-commands and artifact paths
only; never harness-specific tokens.

## Persistence semantics

`.dev/health-loop-state.md` is git-tracked, so the durability claim above
(surviving fresh sessions and worktree boundaries) holds only when the latest
breadcrumb write is **committed**. Therefore:

- A loop skill MUST write the breadcrumb **before** creating its final commit
  and include it in that commit. For the loop-closing skill
  (`/implement-health-plan`), that is the ledger-close commit.
- A breadcrumb write left uncommitted after the final commit is
  local-working-tree-only: it is lost if the worktree is removed, and the
  committed copy reflects the prior loop step. Treat that as a defect, not a
  supported mode.

## Schema

```yaml
stage_completed: <name of the skill that just finished>
completed_at: <today's ISO date>
next_command: <exact next slash-command + args, or `none` when the loop is closed>
next_inputs:
  - <artifact path the next skill consumes>
fresh_session_recommended: <true | false>
note: <one line; why this is next, and any guard the next skill should honour>
```

## Validation

The schema above is machine-checked by `scripts/validate_health_loop_state.py`,
run in `--staged` mode at pre-commit (blocking). It verifies required fields,
date format, `fresh_session_recommended` boolean, `next_inputs` list structure,
`next_command` token against the lifecycle table, and the lifecycle-consistency
invariant (given `stage_completed`, `next_command` must equal the successor from
the table below).

## Lifecycle

| Skill | Reads | Writes `next_command` |
| --- | --- | --- |
| `/ingest-friction-log` | loop breadcrumb (warn if later step in flight) | `/plugin-health-report` |
| `/plugin-health-report` | breadcrumb (warn if a loop is already in flight) | `/record-health-dispositions` |
| `/record-health-dispositions` | breadcrumb | `/plan-health-findings` |
| `/plan-health-findings` | breadcrumb | `/implement-health-plan --plan <path>` |
| `/implement-health-plan` | breadcrumb | `none` (loop closed) |

## Phase-0 read rule (every loop skill)

Read `.dev/health-loop-state.md` if it exists.

- If `next_command` names **this** skill → you are resuming the loop correctly;
  adopt `next_inputs` as your inputs.
- If `next_command` names a **different** skill → tell the user the loop pointer
  expects `<that command>` next, and ask whether to continue here anyway or
  follow the pointer.
- If `next_command` is **`none`** → the previous loop closed cleanly; treat as a
  fresh entry and proceed normally (overwrite the breadcrumb when you complete).
- If the file is **absent** → fresh entry; proceed normally.

## Completion write rule (every loop skill)

On successful completion, overwrite `.dev/health-loop-state.md` with the schema
above, filling `next_command` per the lifecycle table. Set
`fresh_session_recommended: true` at heavy transitions (any handoff into a skill
that dispatches sub-agents or re-reads many full files — notably
`plan-health-findings → implement-health-plan`).

## writing-plans override rule (binding on plan-health-findings)

`/plan-health-findings` delegates plan authoring to
`superpowers:writing-plans`. That sub-skill's **Execution Handoff** section
offers its own two endings ("Subagent-Driven / Inline"). Inside the health
loop those endings are **wrong**: executing the plan through them skips
`/implement-health-plan` Phase 3, so the `closes_rows:` ledger rows are never
written `fixed` and the loop silently never closes. `/plan-health-findings`
MUST therefore (a) instruct `writing-plans`, in the context it passes, **not**
to present its Execution Handoff, and (b) as a backstop, if that prompt appears
anyway, supersede it rather than answer it — routing the user to
`/implement-health-plan` via its own closing phase.

## Stop-and-handoff rule

At a transition whose `fresh_session_recommended` is `true`, the completing
skill stops after writing the breadcrumb and recommends running `next_command`
in a fresh session. It does **not** auto-invoke the next skill in the same
context — that is what drives mid-loop compaction.
