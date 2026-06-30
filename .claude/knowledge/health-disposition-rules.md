# Health Disposition Rules

> Storage contract: see `.claude/knowledge/health-disposition-storage-contract.md` for the canonical artifact roles, source-of-truth event store, and generated read views.

Shared rules extracted from `/record-plugin-dispositions` for loop-state adoption,
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

When adopting from loop-state, skip the `python3 scripts/select_health_artifacts.py` calls;
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

Any session that resolves an `accepted` event must close the ledger in the same
session. Use `.claude/knowledge/ledger-closure-protocol.md` for the background
and full rule set.

- Append a `fixed` event via `python3 scripts/health_disposition_store.py append_event`,
  setting `closes_event_ids` to the accepted `event_id` being resolved.
- Run `python3 scripts/health_disposition_store.py regenerate` after appending.
- After the source change, run `python3 scripts/check_ledger_staleness.py` to
  confirm the event no longer appears as effectively open.
