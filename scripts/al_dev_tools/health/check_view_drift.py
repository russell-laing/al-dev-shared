#!/usr/bin/env python3
"""Store-vs-view drift checker for the health disposition ledger.

Re-derives the four generated views (dispositions_open.md,
dispositions_current.md, dispositions.md, dispositions_index.json) in memory
from the authoritative JSONL event store and compares them against the
committed on-disk views. Detects the drift class the other health checks miss:
a view that no longer matches the store because it was hand-edited, or because
a commit appended/closed events without running `regenerate`.

The motivating incident: a finding "closed" by deleting its row from
dispositions_open.md without appending a `fixed` event. The JSONL store still
holds it as open-accepted, so `check_disposition_store_consistency.py` stays
green while the committed view under-reports the open backlog.

Read-only: expected views are rendered into a temp directory, so the canonical
docs/health/ files are never touched. Exits 0 when every view matches the store,
1 on any drift (so the pre-commit hook can block a stale-view commit).
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from .disposition_events import validate_index_freshness
from .disposition_views import (
    render_current_events_view,
    render_legacy_compatibility_view,
    render_open_view,
)
from .paths import (
    compatibility_ledger_path,
    dispositions_current_view_path,
    dispositions_events_root,
    dispositions_index_path,
    dispositions_open_view_path,
)

REPO_ROOT = Path(__file__).resolve().parents[3]

# Markdown views rendered deterministically from the event stream: the same
# render function that `regenerate` uses produces the expected bytes, so any
# byte difference against the on-disk file is genuine drift.
_MARKDOWN_VIEWS = (
    ("dispositions_open.md", dispositions_open_view_path, render_open_view),
    ("dispositions_current.md", dispositions_current_view_path, render_current_events_view),
    ("dispositions.md", compatibility_ledger_path, render_legacy_compatibility_view),
)


def _load_events(events_root: Path) -> list[dict[str, object]]:
    from . import health_disposition_store as store

    return list(store.iter_event_rows(events_root))


def _check_markdown_views(root: Path, events: list[dict[str, object]]) -> list[str]:
    """Render each markdown view to a temp file and byte-compare to disk."""
    drift: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        for label, path_fn, render_fn in _MARKDOWN_VIEWS:
            on_disk = path_fn(root)
            expected = tmp_root / label
            render_fn(expected, events)
            if not on_disk.exists():
                drift.append(f"{label}: missing on disk (store holds {len(events)} events)")
                continue
            if on_disk.read_text(encoding="utf-8") != expected.read_text(encoding="utf-8"):
                drift.append(
                    f"{label}: content differs from store-derived view "
                    f"(stale or hand-edited)"
                )
    return drift


def _check_index(root: Path, events: list[dict[str, object]]) -> list[str]:
    """Compare the on-disk index against the store via freshness invariants.

    Uses validate_index_freshness (deterministic source_hash / total_events /
    open_accepted checks) rather than a byte compare, because the index carries
    a volatile generated_at timestamp that legitimately differs every run.
    """
    index_path = dispositions_index_path(root)
    if not index_path.exists():
        return ["dispositions_index.json: missing on disk"]
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"dispositions_index.json: unparseable ({exc})"]
    return [f"dispositions_index.json: {err}" for err in validate_index_freshness(index, events)]


def run(root: Path) -> int:
    """Compare generated views against the store. Returns 0 if in sync, 1 if drifted."""
    events_root = dispositions_events_root(root)
    if not events_root.exists():
        print("view drift: no dispositions_events directory found — skipping check")
        return 0

    try:
        events = _load_events(events_root)
    except (ValueError, OSError) as exc:
        print(f"view drift: cannot load event store: {exc}", file=sys.stderr)
        return 1

    drift = _check_markdown_views(root, events) + _check_index(root, events)

    if drift:
        print(
            f"view drift: {len(drift)} generated view(s) disagree with the JSONL "
            f"store — run `python3 scripts/health_disposition_store.py regenerate`:",
            file=sys.stderr,
        )
        for msg in drift:
            print(f"  {msg}", file=sys.stderr)
        return 1

    print(f"view drift: 4 generated views match the store ({len(events)} events)")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=REPO_ROOT, help="Repository root to inspect."
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return run(args.root)


if __name__ == "__main__":
    sys.exit(main())
