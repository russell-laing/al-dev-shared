# Health Disposition Rules

Shared rules extracted from `/record-health-dispositions` for loop-state adoption,
batch guards, and re-litigation prevention.

## Loop-State Adoption

Read `.dev/health-loop-state.md` if present (schema:
`.claude/knowledge/health-loop-state-contract.md`):

- `next_command` names this skill → adopt `next_inputs` as located dossier path(s).
- `next_command` names a different step → tell the user the pointer expects
  `<that command>` and ask whether to continue here anyway.
- `next_command` is `none` → previous loop closed cleanly; treat as a fresh
  entry and proceed normally.
- File absent → proceed normally.

When adopting from loop-state, skip the `select_health_artifacts.py` calls;
the dossier path(s) are already resolved.

## Contradictory-Batch Guard

Before writing any row from a batched response, check whether the same
object + issue essence appears twice with different decisions in the current
batch. If it does, stop and ask the user to resolve the conflict first.
Do not append a partial batch.

## Re-Litigation Guard

If a user decision contradicts an existing `declined` or `grandfathered` row
for the same object + issue essence, refuse to append a new row. Per the ledger
rules, the existing row must be edited first — name the conflicting row and stop
on that finding only.

## Closure Write-Back Rule (binding on fix sessions)

Any session that resolves an `accepted` row must close the ledger in the same
session. Use `.claude/knowledge/ledger-closure-protocol.md` for the background
and full rule set.

- Uncommitted accepted row → flip it in place to `fixed`.
- Committed accepted row → append a later `fixed` row with the resolving commit
  and `closes #NNN`.
- After the source change, run `python3 scripts/check_ledger_staleness.py` to
  confirm the row no longer appears as effectively open.
