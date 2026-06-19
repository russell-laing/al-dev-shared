# Disposition JSONL Store Design

## Goal

Make the Claude Code health-disposition workflow faster to analyse and harder to drift by moving canonical disposition history to append-only JSONL, while keeping generated Markdown views for humans.

The migration must not start until the current disposition backlog is clean:

```bash
python3 scripts/check_ledger_staleness.py
```

must report `0 effective-open accepted row(s)`.

## Current Context

The repository already split disposition history from a generated current-state view:

- `docs/health/dispositions-history/YYYY/YYYY-MM.md` stores append-only Markdown history.
- `docs/health/dispositions.md` is a generated Markdown current-state view.
- `scripts/health_disposition_store.py` owns some parsing, appending, matching, and current-view rendering.

This reduced some risk, but the default read path is still too large. The current generated Markdown view can exceed 800 lines, and reconciliation still has row-number, duplicate legacy ID, stale-open, and ambiguous closure failure modes.

## Architecture

Use JSONL as the canonical append-only event store. Each disposition event is one line. Scripts generate every human- and Claude-facing view from that source.

Historical Markdown IDs are not canonical after migration. Each migrated event receives a new stable `event_id`, and the old Markdown ID is retained as `legacy_id` for compatibility and audit. New workflow references use `event_id`. Once the JSONL workflow has proven stable, new events can omit `legacy_id`, while migrated events keep it for traceability.

Generated artifacts:

- `docs/health/dispositions-events/YYYY/YYYY-MM.jsonl` — canonical append-only event history.
- `docs/health/dispositions-open.md` — default small Claude read containing only effective-open accepted events.
- `docs/health/dispositions-current.md` — generated human current-state view.
- `docs/health/dispositions-index.json` — generated totals, hashes, open counts, integrity counts, and surface/dimension breakdowns.
- `docs/health/dispositions.md` — optional temporary compatibility view during rollout.

No skill should hand-edit generated views or append directly to Markdown disposition files.

## Event Model

Each JSONL event has required fields:

```json
{
  "event_id": "disp_20260619_000001",
  "legacy_id": "#976",
  "surface": "tooling",
  "dimension": "quality",
  "object": "validate_health_loop_state.py",
  "finding": "Validator stage enum omits revise-health-plan.",
  "disposition": "fixed",
  "date": "2026-06-19",
  "closes_event_ids": ["disp_20260619_000000"],
  "evidence": "8f3c205 verified live 2026-06-19",
  "source": "migration"
}
```

`legacy_id` is optional for new events after the compatibility period. `closes_event_ids` is valid for `fixed`, `declined`, and `grandfathered` events, because `/revise-health-plan` can settle accepted work by re-dispositioning it rather than implementing it.

The generated index stores row totals and derived counts. Totals are never hand-maintained in JSONL history.

## Workflow

### Pre-Migration Reconciliation

Before storage migration, close or explicitly re-disposition all current open accepted rows. The pre-migration gate is:

```bash
python3 scripts/check_ledger_staleness.py
```

The command must report zero effective-open accepted rows. Existing data-integrity warnings should be captured in the migration audit, not silently normalized away.

### Record Dispositions

`/record-health-dispositions` reads the health dossier and queries the store matcher against generated/indexed state. It appends one JSONL event per accepted, declined, grandfathered, or already-fixed finding, then regenerates views.

### Plan Accepted Findings

`/plan-health-findings` reads `dispositions-open.md` and targeted event records. Plans use `closes_event_ids`, not Markdown row numbers or legacy IDs.

### Revise Plans

`/revise-health-plan` is a first-class optional decide-stage step. It reads a plan, a review/commentary document, and targeted event records.

For each critique it chooses one route:

- in-scope plan correction, preserving the relevant `closes_event_ids`
- out-of-scope re-disposition, appending a `declined` or `grandfathered` event with `closes_event_ids`

It must prove coverage arithmetic:

```text
planned closes_event_ids + re-disposition closes_event_ids = accepted event set
```

No event ID may appear in both routes.

### Implement Plans

`/implement-health-plan` executes the final plan and appends `fixed` events for each completed `closes_event_ids` entry. It regenerates views and verifies that the plan's target events are closed. Global backlog checks remain visible, but the workflow should not require loading full history to close a scoped plan.

## Error Handling

The workflow fails closed when identity, closure, or generated-view freshness cannot be proven.

- If an event references an unknown `closes_event_ids` value, validation fails.
- If generated files are stale relative to JSONL history, readers stop and regenerate.
- If an accepted event is closed twice without an explicit supersession rule, validation fails.
- If migration cannot resolve a duplicate or ambiguous legacy closure, the JSONL event is still emitted with a new `event_id`, but the ambiguity is recorded in the audit report.
- If the index says there are open accepted events, Claude reads `dispositions-open.md`, not the full current view.

## Testing

Store tests cover:

- append JSONL event
- generate stable unique `event_id`
- preserve `legacy_id`
- reject malformed events
- resolve `closes_event_ids`
- compute current state from event history
- generate index totals by disposition, surface, dimension, and open accepted count

Migration tests cover:

- migrate a Markdown fixture with duplicate legacy IDs
- preserve old IDs as `legacy_id`
- emit an audit report for ambiguous legacy state
- produce deterministic JSONL and generated views

Workflow contract tests cover:

- `record-health-dispositions` no longer instructs manual Markdown appends
- `plan-health-findings` reads the open/index view and writes `closes_event_ids`
- `revise-health-plan` uses event-ID coverage arithmetic
- `implement-health-plan` closes event IDs and regenerates views

Validator tests cover:

- stale generated views fail
- open accepted count matches event history
- closure references must exist
- ambiguous duplicate closure is reported instead of guessed

## Rollout

1. Reconcile current open accepted rows to zero.
2. Add JSONL event-store tests around the new contract.
3. Extend `scripts/health_disposition_store.py` with JSONL parsing, appending, ID generation, closure validation, and view regeneration.
4. Add a migration command that reads Markdown history/current state, assigns stable `event_id` values, preserves `legacy_id`, and writes a migration audit.
5. Generate the first JSONL history and compact views.
6. Update Claude workflow skills and knowledge docs to use `event_id`, `dispositions-open.md`, and `dispositions-index.json`.
7. Update checker and validators to use the store-backed model.
8. Keep `legacy_id` compatibility during initial operation, then stop writing it for new events once the workflow has proven stable.

## Non-Goals

- Do not delete historical Markdown evidence during the migration.
- Do not hand-normalize duplicate legacy IDs into canonical keys.
- Do not remove `/revise-health-plan`; it remains part of the decide-stage workflow.
- Do not require Claude to read full disposition history for ordinary planning or implementation.
