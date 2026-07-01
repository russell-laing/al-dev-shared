# Ledger Closure Protocol

> See `.claude/knowledge/health-disposition-storage-contract.md` for the
> authoritative storage layout. `docs/health/dispositions-events/` is the
> append-only source of truth; `docs/health/dispositions-open.md` and
> `docs/health/dispositions-index.json` are generated read artifacts.
> Never append rows directly to `docs/health/dispositions.md`.

Use this protocol when a fix session resolves an `accepted` health finding.

## Why closure matters

`docs/health/dispositions-open.md` is the small generated view of open accepted
events. A code change without same-session ledger closure leaves the event open
and causes later sweeps to re-rank fixed work.

## Closure rules

Closure references use `event_id` values from the JSONL store. A resolving event
sets `disposition` to `fixed`, `declined`, or `grandfathered` and lists the
accepted event IDs in `closes_event_ids`.

Do not use Markdown table row numbers or `legacy_id` values for new closures.
`legacy_id` exists only for migration traceability.

1. Append a new `fixed` event via `scripts/health_disposition_store.py append_event`,
   setting `closes_event_ids` to list the accepted `event_id` it resolves.
2. Run `scripts/health_disposition_store.py regenerate` after every append to
   update `dispositions-open.md`, `dispositions-current.md`, and
   `dispositions-index.json`.
3. Keep closure auditability in the appended event and its
   `closes_event_ids`; do not rely on extra commit-message identifiers.

## Verification

Run `python3 scripts/check_ledger_staleness.py` after the source change. Then:

- Any remaining `STALE-OPEN` row for the resolved object means the closure
  write-back did not happen correctly.
- Any `data-integrity warning` naming the resolved event (duplicate event_id,
  or an ambiguous closure) means the write-back omitted `closes_event_ids` —
  fix it so the closure is deterministic.
