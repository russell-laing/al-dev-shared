"""Query and closure helpers for ledger staleness checks."""

from __future__ import annotations

import glob
import re
import subprocess
from collections import defaultdict
from pathlib import Path

from . import health_disposition_store as store
from .ledger_models import LEDGER, Row, dict_to_row, parse_ledger
from .paths import dispositions_events_root, dispositions_history_root


CLOSES_RE = re.compile(r"closes row (\d+)", re.IGNORECASE)
CLOSES_ID_RE = re.compile(r"closes #([\w-]+)", re.IGNORECASE)
PAREN_RE = re.compile(r"\s*\([^)]*\)")
PATH_TEMPLATES = (
    "profile-al-dev-shared/skills/{name}",
    ".claude/skills/{name}",
    "profile-al-dev-shared/agents/{name}.md",
    ".claude/agents/{name}.md",
)


def load_rows_from_store(repo_root: Path) -> list[Row]:
    events_root = dispositions_events_root(repo_root)
    if events_root.exists():
        raw_events = list(store.iter_event_rows(events_root))
        current_events = store.materialize_current_events(raw_events)
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

    history_root = dispositions_history_root(repo_root)
    if history_root.exists():
        raw = list(store.iter_history_rows(history_root))
        current = store.materialize_current_view(raw)
        return [dict_to_row(d, i + 1) for i, d in enumerate(current)]

    return parse_ledger(repo_root / LEDGER)


def norm_object(obj: str) -> str:
    return PAREN_RE.sub("", obj.replace("`", "")).strip().lower()


def _has_valid_content(repo_root: Path, glob_pattern: str) -> bool:
    """Check if glob pattern matches and directory contains expected files."""
    matches = glob.glob(str(repo_root / glob_pattern))
    if not matches:
        return False
    # Verify that at least one matched directory contains expected content:
    # skills/ have SKILL.md, agents/ have *.md files
    for match in matches:
        path = Path(match)
        if "skills" in glob_pattern and (path / "SKILL.md").exists():
            return True
        elif "agents" in glob_pattern and any(path.glob("*.md")):
            return True
        elif "/" not in glob_pattern:  # Direct file path
            # Verify file actually exists, don't assume
            if path.exists():
                return True
    return False


def candidate_paths(obj: str, repo_root: Path) -> list[str]:
    paths: list[str] = []
    for token in norm_object(obj).split(","):
        token = token.strip()
        if not token:
            continue
        if "/" in token:
            if _has_valid_content(repo_root, token):
                paths.append(token)
            continue
        for tpl in PATH_TEMPLATES:
            cand = tpl.format(name=token)
            if _has_valid_content(repo_root, cand):
                paths.append(cand)
    return paths


def resolve_closures(rows: list[Row]) -> None:
    by_number = {r.number: r for r in rows}
    by_id: dict[str, Row] = {}
    for r in rows:
        if r.id and r.id not in by_id:
            by_id[r.id] = r
    accepted = [r for r in rows if r.disposition == "accepted"]
    explicit_fixed_rows: set[int] = set()

    for r in rows:
        if r.disposition != "fixed":
            continue
        for m in CLOSES_ID_RE.finditer(r.note):
            target_id = m.group(1)
            # Try both ID formats (legacy sans-# and auto-generated with-#) to maintain
            # backwards compatibility. Note: if both variants exist in by_id, this will
            # match the first one tried. Expected format: auto-generated IDs are always
            # lowercase-normalized in norm_object(); legacy IDs should follow the same
            # normalization to avoid collisions.
            target = by_id.get(f"#{target_id}") or by_id.get(target_id)
            if target and target.disposition == "accepted" and target.number < r.number:
                target.closed_by = r.number
                target.closed_via = "token"
                explicit_fixed_rows.add(r.number)
        for m in CLOSES_RE.finditer(r.note):
            target = by_number.get(int(m.group(1)))
            if target and target.disposition == "accepted" and target.number < r.number:
                target.closed_by = r.number
                target.closed_via = "token"
                explicit_fixed_rows.add(r.number)

    for r in rows:
        if r.disposition != "fixed" or r.number in explicit_fixed_rows:
            continue
        for a in accepted:
            if a.closed_by is None and a.number < r.number and norm_object(a.obj) == norm_object(r.obj):
                a.closed_by = r.number
                a.closed_via = "objorder"
                break

    for r in rows:
        if r.disposition not in ("grandfathered", "declined"):
            continue
        if r.id:
            target = by_id.get(r.id)
            if target and target.disposition == "accepted" and target.closed_by is None and target.number < r.number:
                target.closed_by = r.number
                target.closed_via = "dg-id"
                continue
        for a in accepted:
            if a.closed_by is None and a.number < r.number and norm_object(a.obj) == norm_object(r.obj):
                a.closed_by = r.number
                a.closed_via = "dg-obj"
                break


def _issue_key(r: Row) -> tuple[str, str, str, str]:
    return (
        r.surface.strip(),
        r.dimension.strip(),
        norm_object(r.obj),
        re.sub(r"\s+", " ", r.issue.strip()),
    )


def integrity_warnings(rows: list[Row]) -> list[str]:
    warnings: list[str] = []
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


def commits_since(date: str, paths: list[str], repo_root: Path) -> list[str]:
    if not paths:
        return []
    out = subprocess.run(
        ["git", "log", f"--since={date} 00:00", "--format=%h %s", "--", *paths],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    return out.splitlines() if out else []


def staged_files(repo_root: Path) -> set[str]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    return {line.strip() for line in out.splitlines() if line.strip()}
