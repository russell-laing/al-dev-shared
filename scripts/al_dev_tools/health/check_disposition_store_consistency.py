#!/usr/bin/env python3
"""JSONL disposition event store consistency checker.

Reads the shared disposition-event root via health_disposition_store helpers and
verifies internal consistency. Prints a short summary. Exits 0 when consistent
so the PostToolUse git-commit hook stays green; exits 1 only on a real
inconsistency (unparseable events or dangling closes_event_ids references).

This script is intentionally read-only: it never writes to
docs/health/dispositions_history/ or any other file.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .paths import dispositions_events_root

REPO_ROOT = Path(__file__).resolve().parents[3]
EVENTS_ROOT = dispositions_events_root(REPO_ROOT)


def _load_store():
    from . import health_disposition_store as store

    return store


def run(events_root: Path) -> int:
    """Check JSONL event store consistency. Returns 0 if consistent, 1 if not."""
    if not events_root.exists():
        print("JSONL store: no dispositions_events directory found — skipping check")
        return 0

    mod = _load_store()

    try:
        events = list(mod.iter_event_rows(events_root))
    except (ValueError, OSError) as exc:
        print(f"JSONL store: parse error: {exc}", file=sys.stderr)
        return 1

    # Build event_id set for referential integrity check.
    known_ids: set[str] = {str(e["event_id"]) for e in events}
    dangling: list[str] = []
    for event in events:
        for ref in event.get("closes_event_ids", []):
            if str(ref) not in known_ids:
                dangling.append(
                    f"event {event['event_id']} closes_event_ids references "
                    f"unknown event_id {ref!r}"
                )

    if dangling:
        print(
            f"JSONL store: {len(dangling)} referential integrity error(s):",
            file=sys.stderr,
        )
        for msg in dangling:
            print(f"  {msg}", file=sys.stderr)
        return 1

    print(f"JSONL store: {len(events)} events verified — consistent")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root to inspect.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    events_root = dispositions_events_root(args.root)
    return run(events_root)


if __name__ == "__main__":
    sys.exit(main())
