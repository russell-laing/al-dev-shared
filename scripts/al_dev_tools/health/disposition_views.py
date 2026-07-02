"""Markdown history and view helpers for health finding dispositions."""

from __future__ import annotations

import re
from collections import OrderedDict
from pathlib import Path
from typing import Iterator

from .disposition_events import build_disposition_index, materialize_current_events
from .disposition_models import TABLE_DIVIDER, TABLE_HEADER, _escape_cell, _unescape_cell, disposition_key
from ..io_utils import write_json_atomic, write_text_atomic


def shard_path_for_date(iso_date: str) -> Path:
    year, month, _ = iso_date.split("-")
    return Path(year) / f"{year}-{month}.md"


def parse_ledger_file(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [
            _unescape_cell(c.strip())
            for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))
        ]
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
    latest: OrderedDict[tuple[str, str, str, str], dict[str, str]] = OrderedDict()
    for row in rows:
        latest[disposition_key(row)] = row
    return list(latest.values())


def write_shard(shard: Path, shard_rows: list[dict[str, str]]) -> None:
    shard.parent.mkdir(parents=True, exist_ok=True)
    if shard.exists():
        existing_content = shard.read_text(encoding="utf-8")
    else:
        existing_content = TABLE_HEADER + "\n" + TABLE_DIVIDER + "\n"
    # Check for duplicates before writing
    existing_ids = set()
    for line in existing_content.splitlines():
        if line.startswith("|") and line.count("|") >= 8:
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if cells:
                existing_ids.add(cells[0])
    
    body_lines = []
    for r in shard_rows:
        if r['id'] in existing_ids:
            continue
        existing_ids.add(r['id'])
        body_lines.append(
            f"| {r['id']} | {r['surface']} | {r['dimension']} | {r['object']} | "
            f"{r['finding']} | {r['disposition']} | {r['date']} | {r['note']} |"
        )
    
    if not body_lines:
        return
    
    # Ensure existing_content ends with newline so appended rows don't merge
    if existing_content and not existing_content.endswith("\n"):
        existing_content += "\n"
    new_content = existing_content + "\n".join(body_lines) + "\n"
    write_text_atomic(shard, new_content)


def append_row(history_root: Path, row: dict[str, str]) -> Path:
    shard = history_root / shard_path_for_date(row["date"])
    write_shard(shard, [row])
    return shard


def render_current_view(output: Path, rows: list[dict[str, str]]) -> None:
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
    write_text_atomic(output, "\n".join(header_lines + body_lines) + "\n")


def iter_history_rows(history_root: Path) -> Iterator[dict[str, str]]:
    for shard in sorted(history_root.rglob("*.md")):
        yield from parse_ledger_file(shard)


def list_open(
    ledger_path: Path,
    status: str = "accepted",
    surface: str | None = None,
    dimension: str | None = None,
) -> list[dict[str, str]]:
    target = status.strip().lower()
    rows = materialize_current_view(parse_ledger_file(ledger_path))
    out = [r for r in rows if r["disposition"].strip().lower() == target]
    if surface:
        out = [r for r in out if r["surface"].strip() == surface]
    if dimension:
        out = [r for r in out if r["dimension"].strip() == dimension]
    return out


def _markdown_event_row(event: dict[str, object]) -> str:
    legacy = str(event.get("legacy_id", ""))
    legacy_part = f" ({legacy})" if legacy else ""
    closes = ", ".join(str(v) for v in event.get("closes_event_ids", []))
    return (
        f"| {event['event_id']}{legacy_part} | {event['surface']} | {event['dimension']} | "
        f"{event['object']} | {_escape_cell(event['finding'])} | {event['disposition']} | "
        f"{event['date']} | {_escape_cell(event['evidence'])} | {closes} |"
    )


def _markdown_legacy_row(event: dict[str, object]) -> str:
    legacy_id = str(event.get("legacy_id", "")).strip() or str(event["event_id"])
    closes = ", ".join(str(v) for v in event.get("closes_event_ids", []))
    note = str(event.get("evidence", ""))
    if closes:
        note = f"{note}; closes {closes}" if note else f"closes {closes}"
    return (
        f"| {legacy_id} | {event['surface']} | {event['dimension']} | "
        f"{event['object']} | {_escape_cell(event['finding'])} | {event['disposition']} | "
        f"{event['date']} | {_escape_cell(note)} |"
    )


def render_open_view(output: Path, events: list[dict[str, object]]) -> None:
    current = [event for event in materialize_current_events(events) if event["disposition"] == "accepted"]
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Open Health Dispositions",
        "",
        "<!-- generated from docs/health/dispositions_events/; do not edit directly -->",
        "",
        "| Event ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence | Closes |",
        "|----------|---------|-----------|--------|---------|-------------|------|----------|--------|",
    ]
    lines.extend(_markdown_event_row(event) for event in current)
    write_text_atomic(output, "\n".join(lines) + "\n")


def render_current_events_view(output: Path, events: list[dict[str, object]]) -> None:
    current = materialize_current_events(events)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Health Finding Dispositions",
        "",
        "<!-- generated from docs/health/dispositions_events/; do not edit directly -->",
        "",
        "| Event ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence | Closes |",
        "|----------|---------|-----------|--------|---------|-------------|------|----------|--------|",
    ]
    lines.extend(_markdown_event_row(event) for event in current)
    write_text_atomic(output, "\n".join(lines) + "\n")


def render_legacy_compatibility_view(output: Path, events: list[dict[str, object]]) -> None:
    current = materialize_current_events(events)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Health Finding Dispositions",
        "",
        "<!-- generated from docs/health/dispositions_events/; do not edit directly -->",
        "",
        "| ID | Surface | Dimension | Object | Finding | Disposition | Date | Note |",
        "|----|---------|-----------|--------|---------|-------------|------|------|",
    ]
    lines.extend(_markdown_legacy_row(event) for event in current)
    write_text_atomic(output, "\n".join(lines) + "\n")


def render_index(output: Path, events: list[dict[str, object]]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(output, build_disposition_index(events))
