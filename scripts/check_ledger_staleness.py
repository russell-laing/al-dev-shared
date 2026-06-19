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
from collections import defaultdict
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
    closed_via: str = ""  # token | objorder | dg-id | dg-obj — closure provenance
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


def dict_to_row(d: dict[str, str], n: int) -> Row:
    return Row(
        number=n,
        surface=d["surface"],
        dimension=d["dimension"],
        obj=d["object"],
        issue=d["finding"],
        disposition=d["disposition"].lower(),
        date=d["date"],
        note=d["note"],
        id=d.get("id", ""),
    )


def load_rows_from_store(repo_root: Path) -> list[Row]:
    import importlib.util as _ilu
    import sys as _sys

    # Locate the store helper relative to this script, not repo_root,
    # so that --root pointing to a temp/test tree still resolves the helper.
    store_path = Path(__file__).resolve().parent / "health_disposition_store.py"
    spec = _ilu.spec_from_file_location("health_disposition_store", store_path)
    if spec is None or spec.loader is None:
        return []
    mod = _ilu.module_from_spec(spec)
    _sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)

    events_root = repo_root / "docs" / "health" / "dispositions-events"
    if events_root.exists():
        raw_events = list(mod.iter_event_rows(events_root))
        current_events = mod.materialize_current_events(raw_events)
        rows: list[Row] = []
        for i, event in enumerate(current_events, start=1):
            rows.append(
                Row(
                    number=i,
                    surface=str(event["surface"]),
                    dimension=str(event["dimension"]),
                    obj=str(event["object"]),
                    issue=str(event["finding"]),
                    disposition=str(event["disposition"]).lower(),
                    date=str(event["date"]),
                    note=str(event["evidence"]),
                    id=str(event["event_id"]),
                )
            )
        return rows

    history_root = repo_root / "docs" / "health" / "dispositions-history"
    if history_root.exists():
        raw = list(mod.iter_history_rows(history_root))
        current = mod.materialize_current_view(raw)
        return [dict_to_row(d, i + 1) for i, d in enumerate(current)]

    # fallback: monolithic file
    ledger = repo_root / LEDGER
    return parse_ledger(ledger)


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
    # Build ID lookup — keep the FIRST occurrence per ID so that later fixed rows
    # do not shadow the accepted row they are meant to close.
    by_id: dict[str, Row] = {}
    for r in rows:
        if r.id and r.id not in by_id:
            by_id[r.id] = r
    accepted = [r for r in rows if r.disposition == "accepted"]
    explicit_fixed_rows: set[int] = set()

    # Pass 1: explicit `closes #ID` tokens (prefer ID-based), then `closes row N` (legacy).
    for r in rows:
        if r.disposition != "fixed":
            continue
        # Try ID-based lookup first
        for m in CLOSES_ID_RE.finditer(r.note):
            target_id = m.group(1)
            # by_id keys include the '#' prefix (e.g. '#398'); the regex captures
            # without it (e.g. '398') — try both forms.
            target = by_id.get(f"#{target_id}") or by_id.get(target_id)
            if target and target.disposition == "accepted" and target.number < r.number:
                target.closed_by = r.number
                target.closed_via = "token"
                explicit_fixed_rows.add(r.number)
        # Fall back to number-based lookup for legacy format
        for m in CLOSES_RE.finditer(r.note):
            target = by_number.get(int(m.group(1)))
            if target and target.disposition == "accepted" and target.number < r.number:
                target.closed_by = r.number
                target.closed_via = "token"
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
                a.closed_via = "objorder"
                break

    # Pass 3: grandfathered/declined rows also close accepted rows for the same
    # finding — handles the case where a disposition changes after initial acceptance.
    # ID-based match takes priority; fall back to object-order matching.
    for r in rows:
        if r.disposition not in ("grandfathered", "declined"):
            continue
        # ID-based: a later row with the same stable ID supersedes the earlier accepted row.
        if r.id:
            target = by_id.get(r.id)
            if target and target.disposition == "accepted" and target.closed_by is None and target.number < r.number:
                target.closed_by = r.number
                target.closed_via = "dg-id"
                continue
        # Object-order fallback: close the earliest still-open accepted row for the same object.
        for a in accepted:
            if a.closed_by is None and a.number < r.number and norm_object(a.obj) == norm_object(r.obj):
                a.closed_by = r.number
                a.closed_via = "dg-obj"
                break


def _issue_key(r: Row) -> tuple[str, str, str, str]:
    """The disposition matching key: (surface, dimension, norm-object, norm-finding)."""
    return (
        r.surface.strip(),
        r.dimension.strip(),
        norm_object(r.obj),
        re.sub(r"\s+", " ", r.issue.strip()),
    )


def integrity_warnings(rows: list[Row]) -> list[str]:
    """Flag ledger data-integrity problems that corrupt closure provenance.

    Run after resolve_closures so closed_by/closed_via are populated. Reports:
    - duplicate IDs naming distinct findings (key forked by editing finding text
      on a disposition flip — breaks `closes #ID` referential integrity);
    - accepted rows closed by positional object-order matching on a multi-finding
      object (attribution unverified — a `closes #ID` token would have been exact);
    - objects with more than one effective-open accepted row (the next tokenless
      fix will close one positionally).
    """
    warnings: list[str] = []

    # Duplicate IDs across distinct keys.
    id_keys: dict[str, set[tuple[str, str, str, str]]] = defaultdict(set)
    for r in rows:
        if r.id:
            id_keys[r.id].add(_issue_key(r))
    for rid, keys in sorted(id_keys.items()):
        if len(keys) > 1:
            warnings.append(
                f"duplicate ID {rid}: names {len(keys)} distinct findings "
                f"(key forked — finding text likely edited on a disposition flip)"
            )

    # Positional closures on multi-finding objects.
    obj_accepted: dict[str, list[Row]] = defaultdict(list)
    for r in rows:
        if r.disposition == "accepted":
            obj_accepted[norm_object(r.obj)].append(r)
    for r in rows:
        if (
            r.disposition == "accepted"
            and r.closed_by is not None
            and r.closed_via in ("objorder", "dg-obj")
            and len(obj_accepted[norm_object(r.obj)]) > 1
        ):
            tag = f" (ID {r.id})" if r.id else ""
            warnings.append(
                f"row {r.number}{tag} closed by positional match on multi-finding "
                f"object '{norm_object(r.obj)}' — attribution unverified; the "
                f"resolving row should carry 'closes #ID'"
            )

    # Multiple effective-open accepted rows on one object.
    open_by_obj: dict[str, list[Row]] = defaultdict(list)
    for r in rows:
        if r.disposition == "accepted" and r.closed_by is None:
            open_by_obj[norm_object(r.obj)].append(r)
    for obj, rs in sorted(open_by_obj.items()):
        if len(rs) > 1:
            ids = ", ".join(r.id or str(r.number) for r in rs)
            warnings.append(
                f"object '{obj}' has {len(rs)} effective-open accepted rows "
                f"({ids}) — a tokenless fix will close one positionally; use 'closes #ID'"
            )

    return warnings


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
    ap.add_argument(
        "--root",
        default=".",
        help="Repo root to resolve ledger paths against (default: cwd)",
    )
    args = ap.parse_args()

    repo_root = Path(args.root).resolve()
    if not (repo_root / LEDGER).exists() and not (repo_root / "docs" / "health" / "dispositions-history").exists():
        print(f"ledger-check: {LEDGER} not found (run from repo root)", file=sys.stderr)
        return 0 if args.staged else 1

    rows = load_rows_from_store(repo_root)
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

    warnings = integrity_warnings(rows)
    if warnings:
        print(f"\nledger-check: {len(warnings)} data-integrity warning(s) (informational):")
        for w in warnings:
            print(f"  WARN: {w}")

    return 1 if (args.strict and stale) else 0


if __name__ == "__main__":
    sys.exit(main())
