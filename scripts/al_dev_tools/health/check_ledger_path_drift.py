#!/usr/bin/env python3
"""Disposition-ledger path-drift checker.

Guards against the failure mode that forked the ledger on 2026-06-30: an
on-disk rename (or a `paths.py` edit) that leaves the canonical path constants
resolving to a location that does not exist, so subsequent writes silently
fork a brand-new event log while the real data sits elsewhere.

For every canonical disposition path declared in `paths.py`, this checker
asserts the path actually resolves to something on disk. It is intentionally
read-only and never writes any file.

Exit codes:
  0 — every canonical path is present (or the ledger is not initialised yet).
  1 — at least one canonical path is missing, or the event store exists but
      holds no `.jsonl` shard (the classic fork signature).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import paths as ledger_paths

REPO_ROOT = Path(__file__).resolve().parents[3]


def _find_problems(root: Path) -> list[str]:
    """Return a list of human-readable drift problems (empty when healthy)."""
    events_root = ledger_paths.dispositions_events_root(root)

    # A repo that has never initialised the JSONL store is healthy-by-absence:
    # mirror check_disposition_store_consistency's skip behaviour so fresh
    # checkouts and unrelated repos do not fail the gate.
    if not events_root.exists():
        return []

    problems: list[str] = []

    shards = list(events_root.rglob("*.jsonl"))
    if not shards:
        problems.append(
            f"event store '{_rel(events_root, root)}' exists but contains no .jsonl "
            f"shard — canonical path may have forked away from the real data"
        )

    # Generated views: present whenever the store has been regenerated. A
    # missing view here means paths.py resolves somewhere the regenerate step
    # never wrote, i.e. a path/store fork.
    for label, view in (
        ("open-accepted view", ledger_paths.dispositions_open_view_path(root)),
        ("current view", ledger_paths.dispositions_current_view_path(root)),
        ("index", ledger_paths.dispositions_index_path(root)),
        ("compatibility ledger", ledger_paths.compatibility_ledger_path(root)),
    ):
        if not view.exists():
            problems.append(
                f"{label} '{_rel(view, root)}' is missing — run "
                f"`python3 scripts/health_disposition_store.py regenerate`, and if it "
                f"stays missing suspect a paths.py/on-disk name mismatch"
            )

    history_root = ledger_paths.dispositions_history_root(root)
    if not history_root.exists():
        problems.append(
            f"history root '{_rel(history_root, root)}' is missing — expected to "
            f"exist alongside the event store"
        )

    return problems


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def run(root: Path) -> int:
    """Check canonical ledger paths under ``root``. Returns 0 healthy, 1 drift."""
    problems = _find_problems(root)
    if problems:
        print(
            f"ledger path drift: {len(problems)} problem(s) detected:",
            file=sys.stderr,
        )
        for msg in problems:
            print(f"  {msg}", file=sys.stderr)
        return 1

    events_root = ledger_paths.dispositions_events_root(root)
    if not events_root.exists():
        print("ledger path drift: no dispositions_events directory — skipping check")
        return 0

    print("ledger path drift: all canonical disposition paths present")
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
