# Health Disposition Storage Contract

## Purpose

Keep the human-facing ledger small without losing append-only provenance.

## Canonical Artifacts

- `docs/health/dispositions_events/YYYY/YYYY-MM.jsonl`
  - append-only event log; one JSON object per disposition event
  - **Year-partitioned:** the top level contains `YYYY/` subdirectories, not JSONL files
    directly. Format-reference lookups must use
    `find docs/health/dispositions_events/ -name "*.jsonl"` (or
    `ls docs/health/dispositions_events/YYYY/` once the year is known);
    `ls docs/health/dispositions_events/ | tail -1` returns a year directory, not a JSONL file.
- `docs/health/dispositions_open.md`
  - generated small read for open accepted events; Claude reads this by default
- `docs/health/dispositions_current.md`
  - generated human current-state view
- `docs/health/dispositions_index.json`
  - generated totals, source hash, open counts, integrity counts, and breakdowns
- `docs/health/dispositions.md`
  - temporary compatibility view during rollout; generated, not hand-edited
- `scripts/health_disposition_store.py`
  - the only supported parser, appender, matcher, and materializer

## Matching Key

`surface + dimension + object + finding`

Normalize only surrounding whitespace and internal whitespace runs.
Do not do fuzzy synonym matching in the storage layer.

**The key must stay stable across a row's lifetime.** A later row supersedes an
earlier one in the materialized current view only when all four key fields are
identical (last-writer-wins). When you flip a disposition (e.g. `accepted` →
`fixed`/`declined`/`grandfathered`), append a **new** event through `append_event`
whose four key fields (`surface` + `dimension` + `object` + `finding`) are
byte-identical to the accepted event; the new event gets a **fresh auto-allocated
`event_id`** and lists the accepted event's id in `closes_event_ids`. Do **not**
reuse the accepted event's id — `append_event`'s duplicate-id guard rejects any
reused id, and `--event-id` exists only for migration/recovery. Closure is
therefore by **object/key match plus `closes_event_ids`, never by id reuse**.
Editing the `finding` text forks the key, so both rows survive under separate ids
— the duplicate-key / ambiguous-closure class that `check_ledger_staleness.py`
`integrity_warnings()` flags. See `ledger-closure-protocol.md` for the full
write-back procedure.

## Rules

- Never append rows directly to `docs/health/dispositions.md`.
- All new decisions are appended through `scripts/health_disposition_store.py append_event`.
- After every append, run `scripts/health_disposition_store.py regenerate`.
- Every superseding event (`fixed`/`declined`/`grandfathered`) sets `closes_event_ids` to list the accepted event IDs it resolves.
- Any step that needs historical closure evidence queries the JSONL event store via `iter_event_rows()`.
