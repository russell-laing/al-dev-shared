# Health Disposition Storage Contract

## Purpose

Keep the human-facing ledger small without losing append-only provenance.

## Canonical Artifacts

- `docs/health/dispositions-events/YYYY/YYYY-MM.jsonl`
  - append-only event log; one JSON object per disposition event
- `docs/health/dispositions-open.md`
  - generated small read for open accepted events; Claude reads this by default
- `docs/health/dispositions-current.md`
  - generated human current-state view
- `docs/health/dispositions-index.json`
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
`fixed`/`declined`/`grandfathered`), keep the `finding` text byte-identical and
reuse the same `ID`; change only the `disposition`, `date`, and `note`. Editing
the `finding` text forks the key, so both rows survive sharing one `ID` — the
duplicate-ID / ambiguous-closure class that `check_ledger_staleness.py`
`integrity_warnings()` flags. See `ledger-closure-protocol.md` for the full
write-back procedure.

## Rules

- Never append rows directly to `docs/health/dispositions.md`.
- All new decisions are appended through `scripts/health_disposition_store.py append_event`.
- After every append, run `scripts/health_disposition_store.py regenerate`.
- Every superseding event (`fixed`/`declined`/`grandfathered`) sets `closes_event_ids` to list the accepted event IDs it resolves.
- Any step that needs historical closure evidence queries the JSONL event store via `iter_event_rows()`.
