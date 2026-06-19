#!/usr/bin/env python3
"""JSONL disposition event store consistency checker.

Reads docs/health/dispositions-events/ via health_disposition_store helpers and
verifies internal consistency. Prints a short summary. Exits 0 when consistent
so the PostToolUse git-commit hook stays green; exits 1 only on a real
inconsistency (unparseable events or dangling closes_event_ids references).

This script is intentionally read-only: it never writes to
docs/health/dispositions-history/ or any other file.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
EVENTS_ROOT = REPO_ROOT / "docs" / "health" / "dispositions-events"


def _load_store():
    store_path = Path(__file__).resolve().parent / "health_disposition_store.py"
    spec = importlib.util.spec_from_file_location("health_disposition_store", store_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load health_disposition_store from {store_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def run(events_root: Path) -> int:
    """Check JSONL event store consistency. Returns 0 if consistent, 1 if not."""
    if not events_root.exists():
        print("JSONL store: no dispositions-events directory found — skipping check")
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


def main() -> int:
    return run(EVENTS_ROOT)


if __name__ == "__main__":
    sys.exit(main())
