"""Compatibility facade and CLI for health finding disposition helpers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .disposition_events import (
    append_event,
    batch_decline,
    build_disposition_index,
    event_shard_path_for_date,
    iter_event_rows,
    materialize_current_events,
    next_event_id,
    parse_event_file,
    validate_event,
    validate_index_freshness,
)
from .disposition_matching import match_against_ledger, normalize_type, object_members, parse_findings_file
from .disposition_models import (
    EVENT_ID_RE,
    EVENT_REQUIRED_FIELDS,
    TABLE_DIVIDER,
    TABLE_HEADER,
    VALID_DISPOSITIONS,
    disposition_key,
    normalize_finding,
)
from .disposition_views import (
    append_row,
    iter_history_rows,
    list_open,
    materialize_current_view,
    parse_ledger_file,
    render_current_events_view,
    render_current_view,
    render_index,
    render_legacy_compatibility_view,
    render_open_view,
    shard_path_for_date,
    write_shard,
)
from .paths import (
    compatibility_ledger_path,
    dispositions_current_view_path,
    dispositions_events_root,
    dispositions_history_root,
    dispositions_index_path,
    dispositions_open_view_path,
)

parse_ledger = parse_ledger_file

__all__ = [
    "EVENT_ID_RE",
    "EVENT_REQUIRED_FIELDS",
    "TABLE_DIVIDER",
    "TABLE_HEADER",
    "VALID_DISPOSITIONS",
    "append_event",
    "append_row",
    "batch_decline",
    "build_disposition_index",
    "disposition_key",
    "event_shard_path_for_date",
    "iter_event_rows",
    "iter_history_rows",
    "list_open",
    "materialize_current_events",
    "materialize_current_view",
    "match_against_ledger",
    "next_event_id",
    "normalize_finding",
    "normalize_type",
    "object_members",
    "parse_event_file",
    "parse_findings_file",
    "parse_ledger",
    "parse_ledger_file",
    "render_current_events_view",
    "render_current_view",
    "render_index",
    "render_legacy_compatibility_view",
    "render_open_view",
    "shard_path_for_date",
    "validate_event",
    "validate_index_freshness",
    "write_shard",
]


def _event_to_legacy_row(event: dict[str, object]) -> dict[str, str]:
    return {
        "id": str(event.get("event_id", "")),
        "surface": str(event.get("surface", "")),
        "dimension": str(event.get("dimension", "")),
        "object": str(event.get("object", "")),
        "finding": str(event.get("finding", "")),
        "disposition": str(event.get("disposition", "")),
        "date": str(event.get("date", "")),
        "note": str(event.get("evidence", "")),
    }


def _cli_match(
    findings_path: Path,
    ledger_path: Path,
    events_root: Path | None = None,
) -> int:
    _DEFAULT_EVENTS_ROOT = dispositions_events_root()
    resolved_events_root = events_root if events_root is not None else _DEFAULT_EVENTS_ROOT

    if resolved_events_root.exists() and any(resolved_events_root.rglob("*.jsonl")):
        events = list(iter_event_rows(resolved_events_root))
        current_events = materialize_current_events(events)
        rows = [_event_to_legacy_row(e) for e in current_events]
        source_label = f"JSONL ({resolved_events_root})"
    else:
        if not ledger_path.exists():
            print(
                f"No JSONL event store found at {resolved_events_root} and "
                f"no Markdown ledger at {ledger_path}; nothing to match against."
            )
            return 1
        rows = materialize_current_view(parse_ledger_file(ledger_path))
        source_label = f"Markdown ledger ({ledger_path}) [legacy fallback]"

    findings = parse_findings_file(findings_path)
    results = match_against_ledger(findings, rows)
    print(f"# source: {source_label}")
    counts = {"suppress": 0, "verify": 0, "keep": 0}
    for r in results:
        counts[str(r["classification"])] += 1
        matched = r["matched"]
        f = r["finding"]
        assert isinstance(f, dict)
        mid = matched["id"] if isinstance(matched, dict) else "-"
        snippet = f.get("finding", "")[:120]
        print(f"{r['classification']:8} {mid:24} {f.get('object', ''):55} {snippet}")
    print(
        f"\nsuppress={counts['suppress']} verify={counts['verify']} "
        f"keep={counts['keep']} (total={len(results)})"
    )
    return 0


def _cli_show(event_id: str, events_root: Path) -> int:
    for ev in iter_event_rows(events_root):
        if ev.get("event_id") == event_id:
            print(json.dumps(ev, indent=2, ensure_ascii=False))
            return 0
    print(f"show: no event found: {event_id}", file=sys.stderr)
    return 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Health disposition store utilities.")
    sub = parser.add_subparsers(dest="command", required=True)
    _HISTORY_DEFAULT = dispositions_history_root()
    _EVENTS_DEFAULT = dispositions_events_root()
    _LEDGER_DEFAULT = compatibility_ledger_path()
    _OPEN_VIEW_DEFAULT = dispositions_open_view_path()
    _CURRENT_VIEW_DEFAULT = dispositions_current_view_path()
    _INDEX_DEFAULT = dispositions_index_path()

    pm = sub.add_parser("match", help="Classify findings against the disposition ledger.")
    pm.add_argument("findings", type=Path, help="Path to health findings file (e.g., docs/health/2026-07-01-plugin-health.md)")
    pm.add_argument("ledger", type=Path, help="Path to disposition ledger file (e.g., docs/health/dispositions-open.md)")
    pm.add_argument("--events-root", type=Path, default=_EVENTS_DEFAULT)

    ap = sub.add_parser(
        "append_row",
        help="Append one disposition row to its month shard (chosen by the row date).",
    )
    for field in ("id", "surface", "dimension", "object", "finding", "disposition", "date", "note"):
        ap.add_argument(f"--{field}", required=True)
    ap.add_argument("--history-root", type=Path, default=_HISTORY_DEFAULT)

    p_sync = sub.add_parser("sync_shard", help="Sync one or more JSONL events to the Markdown history shard")
    p_sync_group = p_sync.add_mutually_exclusive_group(required=True)
    p_sync_group.add_argument("--event-id", help="Sync the single event matching this ID")
    p_sync_group.add_argument("--since", metavar="YYYY-MM-DD", help="Sync all events on or after this date")
    p_sync.add_argument("--events-root", type=Path, default=_EVENTS_DEFAULT)
    p_sync.add_argument("--history-root", type=Path, default=_HISTORY_DEFAULT)
    p_sync.add_argument(
        "--verbose",
        action="store_true",
        help="Print one line per synced event (default: summary only).",
    )

    ih = sub.add_parser(
        "iter_history_rows",
        help="Print every history-shard row in chronological order as JSON lines.",
    )
    ih.add_argument("--history-root", type=Path, default=_HISTORY_DEFAULT)

    ae = sub.add_parser("append_event", help="Append one JSONL disposition event.")
    for field in ("surface", "dimension", "object", "finding", "disposition", "date", "evidence", "source"):
        ae.add_argument(f"--{field}", required=True)
    ae.add_argument("--event-id", default="", help="Override auto-allocation for migration/recovery only.")
    ae.add_argument("--legacy-id", default="")
    ae.add_argument("--closes-event-ids", default="")
    ae.add_argument("--events-root", type=Path, default=_EVENTS_DEFAULT)

    bd = sub.add_parser(
        "batch_decline",
        help="Append a `declined` event per refuted-skip row from a JSON input file.",
    )
    bd.add_argument(
        "--input",
        required=True,
        type=Path,
        help="JSON array of {surface, dimension, object, finding, reason, closes_event_id}",
    )
    bd.add_argument("--date", required=True)
    bd.add_argument("--source", default="plan-plugin-findings")
    bd.add_argument("--events-root", type=Path, default=_EVENTS_DEFAULT)

    regen = sub.add_parser("regenerate", help="Regenerate disposition views from JSONL events.")
    regen.add_argument("--events-root", type=Path, default=_EVENTS_DEFAULT)
    regen.add_argument("--open-view", type=Path, default=_OPEN_VIEW_DEFAULT)
    regen.add_argument("--current-view", type=Path, default=_CURRENT_VIEW_DEFAULT)
    regen.add_argument("--index", type=Path, default=_INDEX_DEFAULT)
    regen.add_argument("--compatibility-view", type=Path, default=_LEDGER_DEFAULT)

    lo = sub.add_parser(
        "list-open",
        help="Print current-view rows with a given disposition (default accepted) as JSON lines.",
    )
    lo.add_argument("--ledger", type=Path, default=_LEDGER_DEFAULT)
    lo.add_argument("--status", default="accepted")
    lo.add_argument("--surface")
    lo.add_argument("--dimension")

    sh = sub.add_parser("show", help="Print full JSON for a single event by its event_id.")
    sh.add_argument("--event-id", required=True, help="The event_id to look up (e.g. disp_20260626_000070).")
    sh.add_argument("--events-root", type=Path, default=_EVENTS_DEFAULT)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "match":
        return _cli_match(args.findings, args.ledger, args.events_root)
    if args.command == "append_row":
        row = {
            f: getattr(args, f)
            for f in ("id", "surface", "dimension", "object", "finding", "disposition", "date", "note")
        }
        shard = append_row(args.history_root, row)
        print(shard)
        return 0
    if args.command == "iter_history_rows":
        for r in iter_history_rows(args.history_root):
            print(json.dumps(r, ensure_ascii=False))
        return 0
    if args.command == "append_event":
        event_id = args.event_id or next_event_id(list(iter_event_rows(args.events_root)), args.date)
        event = {
            "event_id": event_id,
            "legacy_id": args.legacy_id,
            "surface": args.surface,
            "dimension": args.dimension,
            "object": args.object,
            "finding": args.finding,
            "disposition": args.disposition,
            "date": args.date,
            "closes_event_ids": [v.strip() for v in args.closes_event_ids.split(",") if v.strip()],
            "evidence": args.evidence,
            "source": args.source,
        }
        shard = append_event(args.events_root, event)
        print(shard)
        return 0
    if args.command == "batch_decline":
        rows = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            print("batch_decline: input must be a JSON array", file=sys.stderr)
            return 1
        written = batch_decline(args.events_root, rows, args.date, args.source)
        for event_id, shard in written:
            print(f"{event_id} -> {shard}")
        print(f"batch_decline: wrote {len(written)} declined event(s)")
        return 0
    if args.command == "regenerate":
        events = list(iter_event_rows(args.events_root))
        render_open_view(args.open_view, events)
        render_current_events_view(args.current_view, events)
        render_index(args.index, events)
        render_legacy_compatibility_view(args.compatibility_view, events)
        print(f"regenerated {len(events)} event(s)")
        return 0
    if args.command == "show":
        return _cli_show(args.event_id, args.events_root)
    if args.command == "list-open":
        for r in list_open(args.ledger, args.status, args.surface, args.dimension):
            print(json.dumps(r, ensure_ascii=False))
        return 0
    elif args.command == "sync_shard":
        events = []
        for ev in iter_event_rows(args.events_root):
            if args.event_id and ev.get("event_id") == args.event_id:
                events.append(ev)
            elif args.since and ev.get("date", "") >= args.since:
                events.append(ev)
        if not events:
            print("sync_shard: no matching events found", file=sys.stderr)
            return 1
        synced_shards: set[str] = set()
        for ev in events:
            row = {
                "id": ev.get("legacy_id") or ev["event_id"],
                "surface": ev["surface"],
                "dimension": ev["dimension"],
                "object": ev["object"],
                "finding": ev["finding"],
                "disposition": ev["disposition"],
                "date": ev["date"],
                "note": ev.get("evidence", ""),
            }
            shard = append_row(args.history_root, row)
            synced_shards.add(str(shard))
            if args.verbose:
                print(f"sync_shard: wrote shard row for {ev['event_id']}")
        shard_list = ", ".join(sorted(synced_shards))
        print(f"sync_shard: synced {len(events)} row(s) to {shard_list}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
