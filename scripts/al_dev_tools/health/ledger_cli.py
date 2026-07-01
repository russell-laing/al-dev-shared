"""CLI entrypoint for ledger staleness checks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .ledger_models import LEDGER
from .ledger_queries import (
    candidate_paths,
    commits_since,
    integrity_warnings,
    load_rows_from_store,
    resolve_closures,
    staged_files,
)
from .paths import dispositions_history_root


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--strict", action="store_true", help="exit 1 on stale-open rows")
    ap.add_argument("--staged", action="store_true", help="pre-commit warn mode")
    ap.add_argument(
        "--root",
        default=".",
        help="Repo root to resolve ledger paths against (default: cwd)",
    )
    args = ap.parse_args(argv)

    repo_root = Path(args.root).resolve()
    if not (repo_root / LEDGER).exists() and not dispositions_history_root(repo_root).exists():
        print(f"ledger-check: {LEDGER} not found (run from repo root)", file=sys.stderr)
        return 0 if args.staged else 1

    rows = load_rows_from_store(repo_root)
    resolve_closures(rows)
    open_rows = [r for r in rows if r.disposition == "accepted" and r.closed_by is None]
    for r in open_rows:
        r.paths = candidate_paths(r.obj, repo_root)

    if args.staged:
        staged = staged_files(repo_root)
        if str(LEDGER) in staged:
            return 0
        warned = False
        for r in open_rows:
            hit = [p for p in r.paths for s in staged if s == p or s.startswith(p.rstrip("/") + "/")]
            if hit:
                warned = True
                print(
                    f"WARN: staged change touches open accepted ledger row {r.number} "
                    f"({r.obj}) but {LEDGER} is not staged."
                )
        if warned:
            print(
                "  INFO: ledger row still open; /implement-plugin-health defers "
                "close-back to its final phase."
            )
        return 0

    stale = 0
    print(f"ledger-check: {len(open_rows)} effective-open accepted row(s)")
    for r in open_rows:
        line = f"  row {r.number}"
        if r.id:
            line += f" (ID {r.id})"
        line += f" | {r.obj} | accepted {r.date}"
        if not r.paths:
            print(line + " | (object not mappable to repo paths — verify manually)")
            continue
        commits = commits_since(r.date, r.paths, repo_root)
        if commits:
            stale += 1
            print(line + " | STALE-OPEN: object changed since row date:")
            for c in commits[:5]:
                print(f"      {c}")
            print("      → INFO: verify whether a commit resolved it; /implement-plugin-health defers close-back.")
        else:
            print(line + " | no commits since row date")

    warnings = integrity_warnings(rows)
    if warnings:
        print(f"\nledger-check: {len(warnings)} data-integrity warning(s) (informational):")
        for w in warnings:
            print(f"  WARN: {w}")

    return 1 if (args.strict and stale) else 0


if __name__ == "__main__":
    raise SystemExit(main())
