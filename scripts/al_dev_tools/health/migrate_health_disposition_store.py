#!/usr/bin/env python3
"""Shard-migrate the monolithic health disposition ledger.

Reads docs/health/dispositions.md, splits rows into per-month shards under
docs/health/dispositions-history/, and rewrites docs/health/dispositions.md
as a generated current-state projection.

This is a one-shot migration tool. Do not confuse it with
scripts/migrate_health_disposition_columns.py, which adds ID/surface/dimension
columns to legacy 5-column rows.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from . import health_disposition_store as store
from .paths import compatibility_ledger_path, dispositions_history_root


def migrate_store(
    source: Path,
    history_root: Path,
    dry_run: bool = False,
) -> dict[str, int]:
    rows = store.parse_ledger_file(source)
    by_shard: dict[Path, list[dict]] = {}
    for row in rows:
        shard = history_root / store.shard_path_for_date(row["date"])
        by_shard.setdefault(shard, []).append(row)

    if not dry_run:
        for shard, shard_rows in by_shard.items():
            store.write_shard(shard, shard_rows)
        store.render_current_view(source, rows)

    return {
        "source_rows": len(rows),
        "written_rows": sum(len(v) for v in by_shard.values()),
        "current_rows": len(store.materialize_current_view(rows)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        default=compatibility_ledger_path(),
        help="Path to the monolithic ledger (default: docs/health/dispositions.md)",
    )
    parser.add_argument(
        "--history-root",
        default=dispositions_history_root(),
        help="Destination directory for month shards",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the migration plan without writing any files",
    )
    parser.add_argument(
        "--rebuild-current-only",
        action="store_true",
        help="Regenerate dispositions.md from history shards without touching shards",
    )
    args = parser.parse_args()

    source = Path(args.source)
    history_root = Path(args.history_root)

    if args.rebuild_current_only:
        store.render_current_view(source, list(store.iter_history_rows(history_root)))
        print("rebuilt current view")
        return

    report = migrate_store(source, history_root, dry_run=args.dry_run)

    label = "[DRY-RUN] " if args.dry_run else ""
    print(f"{label}source rows:  {report['source_rows']}")
    print(f"{label}written rows: {report['written_rows']}")
    print(f"{label}current rows: {report['current_rows']}")


if __name__ == "__main__":
    main()
