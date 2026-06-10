#!/usr/bin/env python3
"""Report effective-open accepted rows in the health disposition ledger.

The ledger (docs/health/dispositions.md) is append-only: a committed
`accepted` row is superseded by a later `fixed` row for the same object,
optionally disambiguated by a `closes row N` token in the fixed row's note
(N = data-row number, counting table rows from 1).

This script computes the *effective-open* accepted rows (accepted rows not
superseded by a later fixed row) and flags rows whose object has commits
after the row date — usually a fix that landed without the closure
write-back required by /record-health-dispositions.

Modes:
  (default)   list effective-open rows and stale-open warnings; exit 0
  --strict    exit 1 if any stale-open rows exist
  --staged    pre-commit mode: warn when staged files touch an open
              accepted row's object and the ledger itself is not staged
"""

from __future__ import annotations

import argparse
import glob
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

LEDGER = Path("docs/health/dispositions.md")
CLOSES_RE = re.compile(r"closes row (\d+)", re.IGNORECASE)
CLOSES_ID_RE = re.compile(r"closes #([\w-]+)", re.IGNORECASE)
PAREN_RE = re.compile(r"\s*\([^)]*\)")

# Surfaces an object name may live under (skills are directories,
# agents are single markdown files).
PATH_TEMPLATES = (
    "profile-al-dev-shared/skills/{name}",
    ".claude/skills/{name}",
    "profile-al-dev-shared/agents/{name}.md",
    ".claude/agents/{name}.md",
)


@dataclass
class Row:
    number: int  # 1-based data-row number
    surface: str
    dimension: str
    obj: str
    issue: str
    disposition: str
    date: str
    note: str
    id: str = ""  # stable ID from 8-column ledger; empty for 7-column legacy
    closed_by: int | None = None
    paths: list[str] = field(default_factory=list)


def parse_ledger_text(text: str) -> list[Row]:
    rows: list[Row] = []
    n = 0
    header_col_count = None

    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or set(cells[0]) <= {"-"}:
            continue

        # Detect header row to determine column structure
        if cells[0] in ("ID", "Surface"):
            # 8-column format: ID | Surface | Dimension | Object | Issue | Disposition | Date | Note
            if cells[0] == "ID":
                header_col_count = 8
            else:
                # Legacy 7-column format: Surface | Dimension | Object | Issue | Disposition | Date | Note
                header_col_count = 7
            continue

        if cells[0] in ("Object",):
            continue

        n += 1

        # Default to 7-column if no header detected yet
        if header_col_count is None:
            header_col_count = 7
            if len(cells) == 8:
                header_col_count = 8

        # Warn if 7-column file is detected
        if header_col_count == 7 and n == 1:
            print("Ledger lacks ID column — run migrate_health_dispositions.py --stamp-ids", file=sys.stderr)

        if header_col_count == 8 and len(cells) >= 8:
            # 8-column: ID | Surface | Dimension | Object | Issue | Disposition | Date | Note
            rows.append(
                Row(
                    n,
                    cells[1],
                    cells[2],
                    cells[3],
                    cells[4],
                    cells[5].lower(),
                    cells[6],
                    cells[7],
                    id=cells[0],
                )
            )
            continue

        if len(cells) >= 7:
            # 7-column legacy: Surface | Dimension | Object | Issue | Disposition | Date | Note
            rows.append(
                Row(
                    n,
                    cells[0],
                    cells[1],
                    cells[2],
                    cells[3],
                    cells[4].lower(),
                    cells[5],
                    cells[6],
                    id="",
                )
            )
            continue

        if len(cells) >= 5:
            rows.append(
                Row(
                    n,
                    "unknown",
                    "unknown",
                    cells[0],
                    cells[1],
                    cells[2].lower(),
                    cells[3],
                    cells[4],
                    id="",
                )
            )
    return rows


def parse_ledger(path: Path) -> list[Row]:
    return parse_ledger_text(path.read_text(encoding="utf-8"))


def norm_object(obj: str) -> str:
    return PAREN_RE.sub("", obj.replace("`", "")).strip().lower()


def candidate_paths(obj: str) -> list[str]:
    """Map an object cell to existing repo paths (git pathspecs)."""
    paths: list[str] = []
    for token in norm_object(obj).split(","):
        token = token.strip()
        if not token:
            continue
        if "/" in token:
            if glob.glob(token):
                paths.append(token)
            continue
        for tpl in PATH_TEMPLATES:
            cand = tpl.format(name=token)
            if glob.glob(cand):  # tolerates * wildcards in object names
                paths.append(cand)
    return paths


def resolve_closures(rows: list[Row]) -> None:
    """Mark accepted rows closed by later fixed rows (token first, then object order)."""
    by_number = {r.number: r for r in rows}
    by_id = {r.id: r for r in rows if r.id}  # Build ID lookup for 8-column ledger
    accepted = [r for r in rows if r.disposition == "accepted"]
    explicit_fixed_rows: set[int] = set()

    # Pass 1: explicit `closes #ID` tokens (prefer ID-based), then `closes row N` (legacy).
    for r in rows:
        if r.disposition != "fixed":
            continue
        # Try ID-based lookup first
        for m in CLOSES_ID_RE.finditer(r.note):
            target_id = m.group(1)
            target = by_id.get(target_id)
            if target and target.disposition == "accepted" and target.number < r.number:
                target.closed_by = r.number
                explicit_fixed_rows.add(r.number)
        # Fall back to number-based lookup for legacy format
        for m in CLOSES_RE.finditer(r.note):
            target = by_number.get(int(m.group(1)))
            if target and target.disposition == "accepted" and target.number < r.number:
                target.closed_by = r.number
                explicit_fixed_rows.add(r.number)

    # Pass 2: object-order matching — each later fixed row closes the earliest
    # still-open accepted row with the same normalized object. A fixed row that
    # applied an explicit token must not also consume another accepted row.
    for r in rows:
        if r.disposition != "fixed" or r.number in explicit_fixed_rows:
            continue
        for a in accepted:
            if a.closed_by is None and a.number < r.number and norm_object(a.obj) == norm_object(r.obj):
                a.closed_by = r.number
                break


def commits_since(date: str, paths: list[str]) -> list[str]:
    if not paths:
        return []
    # Anchor to midnight: git's approxidate fills a bare date's missing
    # time-of-day with the current time, silently excluding same-day commits.
    out = subprocess.run(
        ["git", "log", f"--since={date} 00:00", "--format=%h %s", "--", *paths],
        capture_output=True, text=True, check=False,
    ).stdout.strip()
    return out.splitlines() if out else []


def staged_files() -> set[str]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True, check=False,
    ).stdout
    return {line.strip() for line in out.splitlines() if line.strip()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--strict", action="store_true", help="exit 1 on stale-open rows")
    ap.add_argument("--staged", action="store_true", help="pre-commit warn mode")
    args = ap.parse_args()

    if not LEDGER.exists():
        print(f"ledger-check: {LEDGER} not found (run from repo root)", file=sys.stderr)
        return 0 if args.staged else 1

    rows = parse_ledger(LEDGER)
    resolve_closures(rows)
    open_rows = [r for r in rows if r.disposition == "accepted" and r.closed_by is None]
    for r in open_rows:
        r.paths = candidate_paths(r.obj)

    if args.staged:
        staged = staged_files()
        if str(LEDGER) in staged:
            return 0  # ledger is being updated in this commit — write-back honored
        warned = False
        for r in open_rows:
            hit = [p for p in r.paths for s in staged if s == p or s.startswith(p.rstrip("/") + "/")]
            if hit:
                warned = True
                print(f"WARN: staged change touches open accepted ledger row {r.number} "
                      f"({r.obj}) but {LEDGER} is not staged.")
        if warned:
            print("  If this commit resolves the finding, flip/append its row to "
                  "fixed (closure write-back rule in /record-health-dispositions).")
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
        commits = commits_since(r.date, r.paths)
        if commits:
            stale += 1
            print(line + " | STALE-OPEN: object changed since row date:")
            for c in commits[:5]:
                print(f"      {c}")
            print("      → verify whether a commit resolved it; if so, flip/append the row to fixed.")
        else:
            print(line + " | no commits since row date")

    return 1 if (args.strict and stale) else 0


if __name__ == "__main__":
    sys.exit(main())
