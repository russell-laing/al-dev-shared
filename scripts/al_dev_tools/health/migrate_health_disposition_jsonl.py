#!/usr/bin/env python3
"""Migrate Markdown health disposition history to JSONL event shards."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import argparse
import json
import re
import shutil

from ..io_utils import write_text_atomic


REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_store():
    from . import health_disposition_store as store

    return store


def _legacy_closes_ids(note: str) -> list[str]:
    return [f"#{m}" for m in re.findall(r"closes #(\d+)", note, flags=re.IGNORECASE)]


def _audit_text(report: dict[str, object]) -> str:
    lines = [
        "# Disposition JSONL Migration Audit",
        "",
        f"- Total events: {report['total_events']}",
        f"- Duplicate legacy IDs: {len(report['duplicate_legacy_ids'])}",
        f"- Ambiguous closures: {len(report['ambiguous_closures'])}",
        "",
        "## Duplicate Legacy IDs",
        "",
    ]
    duplicates = report["duplicate_legacy_ids"]
    if duplicates:
        lines.extend(f"- {legacy_id}" for legacy_id in duplicates)
    else:
        lines.append("- none")
    lines.extend(["", "## Ambiguous Closures", ""])
    ambiguous = report["ambiguous_closures"]
    if ambiguous:
        lines.extend(f"- {item}" for item in ambiguous)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def migrate_to_jsonl(repo_root: Path = REPO_ROOT) -> dict[str, object]:
    store = _load_store()
    history_root = repo_root / "docs" / "health" / "dispositions-history"
    events_root = repo_root / "docs" / "health" / "dispositions-events"
    current_output = repo_root / "docs" / "health" / "dispositions-current.md"
    open_output = repo_root / "docs" / "health" / "dispositions-open.md"
    index_output = repo_root / "docs" / "health" / "dispositions-index.json"
    compatibility_output = repo_root / "docs" / "health" / "dispositions.md"
    audit_output = repo_root / "docs" / "health" / "dispositions-jsonl-migration-audit.md"

    if events_root.exists():
        shutil.rmtree(events_root)

    markdown_rows = list(store.iter_history_rows(history_root))
    legacy_counts = Counter(row.get("id", "") for row in markdown_rows if row.get("id"))
    duplicate_legacy_ids = sorted(k for k, v in legacy_counts.items() if v > 1)

    events: list[dict[str, object]] = []
    legacy_to_event: dict[str, str] = {}
    open_accepted_by_legacy: dict[str, str] = {}
    open_accepted_by_object: dict[str, list[str]] = defaultdict(list)
    ambiguous_closures: list[str] = []
    for row in markdown_rows:
        event_id = store.next_event_id(events, row["date"])
        closes_event_ids: list[str] = []
        for legacy_id in _legacy_closes_ids(row.get("note", "")):
            target = legacy_to_event.get(legacy_id)
            if target:
                closes_event_ids.append(target)
            else:
                ambiguous_closures.append(f"{row.get('id', '')} references unknown {legacy_id}")
        if row["disposition"] in ("declined", "grandfathered") and not closes_event_ids:
            legacy_id = str(row.get("id", "")).strip()
            if legacy_id and legacy_id in open_accepted_by_legacy:
                closes_event_ids.append(open_accepted_by_legacy[legacy_id])
            else:
                candidates = open_accepted_by_object.get(row["object"], [])
                if candidates:
                    closes_event_ids.append(candidates.pop(0))
        event = {
            "event_id": event_id,
            "legacy_id": row.get("id", ""),
            "surface": row["surface"],
            "dimension": row["dimension"],
            "object": row["object"],
            "finding": row["finding"],
            "disposition": row["disposition"],
            "date": row["date"],
            "closes_event_ids": closes_event_ids,
            "evidence": row["note"],
            "source": "markdown-migration",
        }
        store.append_event(events_root, event)
        events.append(event)
        legacy_id = str(row.get("id", ""))
        if legacy_id and legacy_id not in legacy_to_event:
            legacy_to_event[legacy_id] = event_id
        if row["disposition"] == "accepted":
            if legacy_id:
                open_accepted_by_legacy[legacy_id] = event_id
            open_accepted_by_object[row["object"]].append(event_id)

    store.render_current_events_view(current_output, events)
    store.render_open_view(open_output, events)
    store.render_index(index_output, events)
    store.render_legacy_compatibility_view(compatibility_output, events)

    report = {
        "total_events": len(events),
        "duplicate_legacy_ids": duplicate_legacy_ids,
        "ambiguous_closures": ambiguous_closures,
    }
    write_text_atomic(audit_output, _audit_text(report))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    report = migrate_to_jsonl(args.root)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
