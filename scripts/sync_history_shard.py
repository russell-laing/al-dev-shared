#!/usr/bin/env python3
"""Verify that all 'fixed' rows in dispositions.md appear in history shards.

Usage:
    python3 scripts/sync_history_shard.py          # report mode; exits 1 if missing
    python3 scripts/sync_history_shard.py --fix    # append missing rows, then re-verify
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from health_disposition_store import parse_ledger_file, iter_history_rows, append_row

REPO_ROOT = Path(__file__).resolve().parent.parent
DISPOSITIONS = REPO_ROOT / "docs/health/dispositions.md"
HISTORY_ROOT = REPO_ROOT / "docs/health/dispositions-history"


def run(dispositions: Path, history_root: Path, fix: bool) -> int:
    """Verify (and optionally sync) fixed ledger rows into history shards.

    Returns 0 when all fixed rows are present (or none exist), 1 otherwise.
    Tests drive this directly with temporary paths.
    """
    if not dispositions.exists():
        print(f"Shard sync: {dispositions} not found — skipping")
        return 0

    all_rows = parse_ledger_file(dispositions)
    fixed_rows = [r for r in all_rows if r["disposition"] == "fixed"]

    if not fixed_rows:
        print("Shard sync: no fixed rows found")
        return 0

    if not history_root.exists():
        print(f"Shard sync: history directory {history_root} missing — cannot verify")
        return 1

    shard_ids = {r["id"] for r in iter_history_rows(history_root)}
    missing = [r for r in fixed_rows if r["id"] not in shard_ids]

    if not missing:
        print(f"Shard sync: {len(fixed_rows)} fixed rows verified ✓")
        return 0

    if fix:
        for row in missing:
            append_row(history_root, row)
        shard_ids_after = {r["id"] for r in iter_history_rows(history_root)}
        still_missing = [r for r in missing if r["id"] not in shard_ids_after]
        if still_missing:
            print(f"Shard sync: --fix applied but {len(still_missing)} rows still missing")
            for r in still_missing:
                print(f"  {r['id']} {r['date']} {r['surface']}/{r['dimension']}")
            return 1
        print(f"Shard sync: synced {len(missing)} rows, {len(fixed_rows)} total verified ✓")
        return 0

    print(
        f"Shard sync: {len(missing)} rows missing from shards"
        " — run sync_history_shard.py --fix"
    )
    for r in missing:
        print(f"  {r['id']} {r['date']} {r['surface']}/{r['dimension']}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify history shard sync for fixed ledger rows."
    )
    parser.add_argument("--fix", action="store_true", help="Append missing rows to shards.")
    args = parser.parse_args()
    return run(DISPOSITIONS, HISTORY_ROOT, args.fix)


if __name__ == "__main__":
    sys.exit(main())
