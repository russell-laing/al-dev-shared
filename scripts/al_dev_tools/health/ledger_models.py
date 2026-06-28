"""Row model and parsing helpers for ledger staleness checks."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
import sys
from pathlib import Path

from .paths import compatibility_ledger_path


LEDGER = compatibility_ledger_path()


@dataclass
class Row:
    number: int
    surface: str
    dimension: str
    obj: str
    issue: str
    disposition: str
    date: str
    note: str
    id: str = ""
    closed_by: int | None = None
    closed_via: str = ""
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

        if cells[0] in ("ID", "Surface"):
            header_col_count = 8 if cells[0] == "ID" else 7
            continue

        if cells[0] in ("Object",):
            continue

        n += 1
        if header_col_count is None:
            header_col_count = 8 if len(cells) == 8 else 7

        if header_col_count == 7 and n == 1:
            print(
                "Ledger lacks ID column — run migrate_health_dispositions.py --stamp-ids",
                file=sys.stderr,
            )

        if header_col_count == 8 and len(cells) >= 8:
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
