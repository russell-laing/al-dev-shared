"""Shared helper for reading, appending, and materializing health dispositions."""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Iterator
import re


TABLE_HEADER = (
    "| ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence / note |"
)
TABLE_DIVIDER = (
    "|----|---------|-----------|--------|---------|-------------|------|------------------|"
)


def normalize_finding(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def disposition_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        row["surface"].strip(),
        row["dimension"].strip(),
        row["object"].strip(),
        normalize_finding(row["finding"]),
    )


def shard_path_for_date(iso_date: str) -> Path:
    """Return relative shard path YYYY/YYYY-MM.md for the given ISO date.

    Callers combine with a history root: history_root / shard_path_for_date(date).
    """
    year, month, _ = iso_date.split("-")
    return Path(year) / f"{year}-{month}.md"


def parse_ledger_file(path: Path) -> list[dict[str, str]]:
    """Parse an 8-column disposition Markdown table into a list of row dicts."""
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or set(cells[0]) <= {"-"}:
            continue
        if cells[0] in ("ID", "Surface", "Object"):
            continue
        if len(cells) < 8:
            continue
        rows.append(
            {
                "id": cells[0],
                "surface": cells[1],
                "dimension": cells[2],
                "object": cells[3],
                "finding": cells[4],
                "disposition": cells[5].lower(),
                "date": cells[6],
                "note": cells[7],
            }
        )
    return rows


def materialize_current_view(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return one row per latest disposition key (last writer wins)."""
    latest: OrderedDict[tuple[str, str, str, str], dict[str, str]] = OrderedDict()
    for row in rows:
        latest[disposition_key(row)] = row
    return list(latest.values())


def write_shard(shard: Path, shard_rows: list[dict[str, str]]) -> None:
    """Write or append rows to a month shard file, creating it with header if new."""
    shard.parent.mkdir(parents=True, exist_ok=True)
    if not shard.exists():
        header = TABLE_HEADER + "\n" + TABLE_DIVIDER + "\n"
    else:
        header = ""
    body_lines = [
        f"| {r['id']} | {r['surface']} | {r['dimension']} | {r['object']} | "
        f"{r['finding']} | {r['disposition']} | {r['date']} | {r['note']} |"
        for r in shard_rows
    ]
    mode = "a" if shard.exists() else "w"
    with open(shard, mode, encoding="utf-8") as f:
        f.write(header + "\n".join(body_lines) + "\n")


def append_row(history_root: Path, row: dict[str, str]) -> Path:
    """Append a single row to its month shard under history_root. Returns the shard path."""
    shard = history_root / shard_path_for_date(row["date"])
    write_shard(shard, [row])
    return shard


def render_current_view(output: Path, rows: list[dict[str, str]]) -> None:
    """Write the generated current-state projection to output path."""
    current = materialize_current_view(rows)
    output.parent.mkdir(parents=True, exist_ok=True)
    header_lines = [
        "# Health Finding Dispositions",
        "",
        "<!-- generated current-state view — do not edit directly -->",
        "<!-- append rows via scripts/health_disposition_store.py -->",
        "",
        TABLE_HEADER,
        TABLE_DIVIDER,
    ]
    body_lines = [
        f"| {r['id']} | {r['surface']} | {r['dimension']} | {r['object']} | "
        f"{r['finding']} | {r['disposition']} | {r['date']} | {r['note']} |"
        for r in current
    ]
    output.write_text(
        "\n".join(header_lines + body_lines) + "\n", encoding="utf-8"
    )


def iter_history_rows(history_root: Path) -> Iterator[dict[str, str]]:
    """Yield all rows from all month shard files in ascending chronological order."""
    for shard in sorted(history_root.rglob("*.md")):
        yield from parse_ledger_file(shard)
