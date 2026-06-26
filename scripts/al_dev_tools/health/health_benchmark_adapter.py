#!/usr/bin/env python3
"""Rerunnable evidence adapter for the self-healing health-loop benchmark.

Extracts the Harness Follow-Up fields named in
docs/reviews/2026-06-20-claude-self-healing-benchmark-baseline.md from the
machine-readable loop surfaces — the JSONL disposition index, the open-row
view, the legacy staleness checker, the loop-state breadcrumb, and the
``<!-- benchmark-metrics -->`` block in each dossier — and reports them as one
JSON record per dossier plus a top-level procedure-integrity checklist.

This tool reports only. It never assigns the 1-5 benchmark scores, never edits
loop state, and never infers an unavailable count: when a dossier carries no
metrics block (or a field reads ``not available``), the count is surfaced as the
string ``not available`` rather than derived from other fields.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from .check_ledger_staleness import load_rows_from_store, resolve_closures
from .health_disposition_store import iter_event_rows, materialize_current_events
from .select_health_artifacts import select_artifacts

METRIC_FIELDS = (
    "raw_count",
    "verified_count",
    "dropped_unverified_count",
    "stale_dropped_count",
    "suppressed_count",
    "failed_lens_count",
    "new_count",
    "recurring_count",
)

NOT_AVAILABLE = "not available"

_METRICS_BLOCK = re.compile(r"<!--\s*benchmark-metrics\b(.*?)-->", re.DOTALL)
_FILENAME = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})-(?P<surface>plugin|tooling)-"
)
_EFFECTIVE_OPEN = re.compile(r"(\d+)\s+effective-open accepted row")


def _coerce_count(value: str) -> object:
    """Return an int for numeric counts, else the literal ``not available``."""
    value = value.strip()
    if value.lower() == NOT_AVAILABLE:
        return NOT_AVAILABLE
    if re.fullmatch(r"\d+", value):
        return int(value)
    return NOT_AVAILABLE


def parse_metrics_block(text: str) -> dict | None:
    """Parse the ``<!-- benchmark-metrics -->`` block from dossier text.

    Returns a dict keyed by METRIC_FIELDS, or None when no block is present.
    A field absent from a present block is recorded as ``not available`` — the
    parser never scrapes the human-facing prose summary as a fallback.
    """
    match = _METRICS_BLOCK.search(text)
    if match is None:
        return None
    body = match.group(1)
    parsed: dict[str, object] = {}
    for line in body.splitlines():
        if ":" not in line:
            continue
        key, _, raw = line.partition(":")
        key = key.strip()
        if key in METRIC_FIELDS:
            parsed[key] = _coerce_count(raw)
    return {field: parsed.get(field, NOT_AVAILABLE) for field in METRIC_FIELDS}


def _dossier_surface_dimensions(text: str, path: Path) -> tuple[str, list[str]]:
    surface = ""
    name_match = _FILENAME.match(path.name)
    if name_match:
        surface = name_match["surface"]
    dimensions: list[str] = []
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not surface and stripped.startswith("surface:"):
            surface = stripped.split(":", 1)[1].strip()
        if stripped.startswith("dimensions:"):
            for follow in lines[idx + 1 :]:
                fstripped = follow.strip()
                if fstripped.startswith("- "):
                    dimensions.append(fstripped[2:].strip())
                elif fstripped.startswith("##") or fstripped == "":
                    if dimensions:
                        break
                else:
                    break
            break
    return surface, dimensions


def parse_dossier(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    surface, dimensions = _dossier_surface_dimensions(text, path)
    metrics = parse_metrics_block(text)
    record: dict[str, object] = {
        "artifact_path": str(path),
        "surface": surface,
        "dimensions": dimensions,
    }
    if metrics is None:
        for field in METRIC_FIELDS:
            record[field] = NOT_AVAILABLE
        record["metrics_block_present"] = False
    else:
        record.update(metrics)
        record["metrics_block_present"] = True
    return record


def read_index(root: Path) -> dict:
    index_path = root / "docs/health/dispositions-index.json"
    if not index_path.is_file():
        return {}
    return json.loads(index_path.read_text(encoding="utf-8"))


def run_list_open(root: Path) -> object:
    """Count open accepted events via the JSONL store when it exists."""
    events_root = root / "docs" / "health" / "dispositions-events"
    if not events_root.is_dir():
        return NOT_AVAILABLE
    current = materialize_current_events(list(iter_event_rows(events_root)))
    return sum(1 for event in current if event["disposition"] == "accepted")


def run_staleness(root: Path) -> object:
    """Count effective-open accepted rows via the packaged ledger checker."""
    rows = load_rows_from_store(root)
    resolve_closures(rows)
    return sum(1 for row in rows if row.disposition == "accepted" and row.closed_by is None)


def read_loop_state(root: Path) -> dict:
    state_path = root / ".dev/health-loop-state.md"
    fields = {"loop_stage_completed": NOT_AVAILABLE, "next_command": NOT_AVAILABLE}
    if not state_path.is_file():
        return fields
    for line in state_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("stage_completed:"):
            fields["loop_stage_completed"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("next_command:"):
            fields["next_command"] = stripped.split(":", 1)[1].strip()
    return fields


def count_close_back(root: Path) -> int:
    """Count fixed events carrying closes_event_ids in the JSONL event store."""
    events_root = root / "docs/health/dispositions-events"
    total = 0
    if not events_root.is_dir():
        return total
    for shard in sorted(events_root.rglob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("disposition") == "fixed" and event.get("closes_event_ids"):
                total += 1
    return total


def jsonl_views_present(root: Path) -> bool:
    base = root / "docs/health"
    return all(
        (base / name).is_file()
        for name in (
            "dispositions-index.json",
            "dispositions-open.md",
            "dispositions-current.md",
        )
    )


def collect_dossiers(root: Path, surface: str, limit: int) -> list[Path]:
    surfaces = ("plugin", "tooling") if surface == "both" else (surface,)
    directories = [root / "docs/health", root / "docs/health/archived"]
    selected: list[Path] = []
    for surf in surfaces:
        candidates: list[Path] = []
        for directory in directories:
            candidates.extend(
                select_artifacts(
                    directory,
                    kind="health",
                    surface=surf,
                    limit=limit,
                    offset=0,
                )
            )
        # Re-rank the merged set by filename (date prefix) descending.
        candidates.sort(key=lambda p: p.name, reverse=True)
        selected.extend(candidates[:limit])
    return selected


def build_report(root: Path, surface: str, limit: int) -> dict:
    index = read_index(root)
    open_accepted = index.get("open_accepted", NOT_AVAILABLE)
    integrity = index.get("integrity_warnings", NOT_AVAILABLE)
    legacy_open = run_staleness(root)
    list_open = run_list_open(root)
    loop = read_loop_state(root)
    close_back = count_close_back(root)

    records = []
    for path in collect_dossiers(root, surface, limit):
        record = parse_dossier(path)
        record["jsonl_open_accepted_count"] = open_accepted
        record["legacy_effective_open_count"] = legacy_open
        record["integrity_warning_count"] = integrity
        record["loop_stage_completed"] = loop["loop_stage_completed"]
        record["next_command"] = loop["next_command"]
        records.append(record)

    checklist = {
        "evidence_gate_run": any(
            r["metrics_block_present"]
            and isinstance(r["raw_count"], int)
            and isinstance(r["verified_count"], int)
            and r["raw_count"] >= r["verified_count"]
            for r in records
        ),
        "jsonl_views_generated": jsonl_views_present(root),
        "loop_state_closed": loop["next_command"] == "none",
        "jsonl_open_accepted_zero": open_accepted == 0,
        "legacy_staleness_clean": legacy_open == 0,
        "integrity_clean": integrity == 0,
        "close_back_ids_present": close_back > 0,
    }

    return {
        "procedure_integrity": checklist,
        "list_open_accepted_count": list_open,
        "close_back_event_count": close_back,
        "dossiers": records,
    }


def _fmt(value: object) -> str:
    return str(value)


def render_markdown(report: dict) -> str:
    lines = ["# Health Benchmark Adapter Report", "", "## Procedure integrity", ""]
    for key, value in report["procedure_integrity"].items():
        mark = "✅" if value else "❌"
        lines.append(f"- {mark} `{key}`: {_fmt(value)}")
    lines.append("")
    lines.append(
        f"list-open accepted: {report['list_open_accepted_count']} · "
        f"close-back events: {report['close_back_event_count']}"
    )
    lines.append("")
    lines.append("## Dossiers")
    for record in report["dossiers"]:
        lines.append("")
        lines.append(f"### {record['artifact_path']}")
        lines.append("")
        for key, value in record.items():
            if key == "artifact_path":
                continue
            lines.append(f"- {key}: {_fmt(value)}")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--surface", choices=("plugin", "tooling", "both"), default="both"
    )
    parser.add_argument("--limit", type=int, default=1, help="dossiers per surface")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--root", type=Path, default=Path("."))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args.root.resolve(), args.surface, args.limit)
    if args.format == "markdown":
        print(render_markdown(report), end="")
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
