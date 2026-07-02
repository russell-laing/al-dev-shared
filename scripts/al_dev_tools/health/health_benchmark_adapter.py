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
from .paths import (
    dispositions_archived_root,
    dispositions_current_view_path,
    dispositions_events_root,
    dispositions_index_path,
    dispositions_open_view_path,
    docs_health_root,
)
from .select_health_artifacts import select_artifacts
from ..companion_surface_contract import (
    canonical_companion_surfaces,
    legacy_surface_aliases,
)

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
TOKEN_FIELDS = (
    "token_data_available",
    "prompt_tokens",
    "completion_tokens",
    "context_compaction_events",
)

NOT_AVAILABLE = "not available"
LEGACY_ALIASES = legacy_surface_aliases()
FALSE_POSITIVE_CLASS_PATH = Path("docs/health/false_positive_classes.md")
FALSE_POSITIVE_STATUSES = ("Candidate", "Monitor", "Suppress")
PROCEDURE_LOG_PATH = Path(".dev/implement-plugin-health-procedure-log.jsonl")
EXPECTED_PHASES_PATH = Path("docs/health/expected_phases.md")

_METRICS_BLOCK = re.compile(r"<!--\s*benchmark-metrics\b(.*?)-->", re.DOTALL)
_TOKEN_BLOCK = re.compile(r"<!--\s*token-usage\b(.*?)-->", re.DOTALL)
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


def parse_token_usage_block(text: str) -> tuple[dict[str, object], bool]:
    defaults: dict[str, object] = {
        "token_data_available": False,
        "prompt_tokens": NOT_AVAILABLE,
        "completion_tokens": NOT_AVAILABLE,
        "context_compaction_events": NOT_AVAILABLE,
    }
    match = _TOKEN_BLOCK.search(text)
    if match is None:
        return defaults, False
    parsed = defaults.copy()
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, raw = line.partition(":")
        key = key.strip()
        value = raw.strip()
        if key == "token_data_available":
            parsed[key] = value.lower() == "true"
        elif key in TOKEN_FIELDS:
            parsed[key] = _coerce_count(value)
    return parsed, True


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
    token_usage, token_block_present = parse_token_usage_block(text)
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
    record.update(token_usage)
    record["token_usage_block_present"] = token_block_present
    return record


def _parse_markdown_table_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    if not cells:
        return None
    if all(set(cell) <= {"-", ":", " "} for cell in cells):
        return None
    return cells


def parse_false_positive_classes(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = _parse_markdown_table_row(line)
        if cells is None or len(cells) != 5 or cells[0] == "ID":
            continue
        status = cells[4]
        if status not in FALSE_POSITIVE_STATUSES:
            status = NOT_AVAILABLE
        rows.append(
            {
                "id": cells[0],
                "description": cells[1],
                "first_seen": cells[2],
                "last_seen": cells[3],
                "status": status,
            }
        )
    return rows


def false_positive_status_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    counts = {status: 0 for status in FALSE_POSITIVE_STATUSES}
    for row in rows:
        status = row.get("status", NOT_AVAILABLE)
        if status in counts:
            counts[status] += 1
    return counts


def parse_expected_phases(text: str) -> dict[str, list[str]]:
    expected: dict[str, list[str]] = {}
    current_skill: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            current_skill = stripped[3:].strip()
            expected[current_skill] = []
            continue
        cells = _parse_markdown_table_row(stripped)
        if (
            current_skill
            and cells is not None
            and len(cells) >= 2
            and cells[0] != "Phase"
        ):
            expected[current_skill].append(cells[0])
    return expected


def load_expected_phases(path: Path) -> dict[str, list[str]]:
    if not path.is_file():
        return {}
    return parse_expected_phases(path.read_text(encoding="utf-8"))


def parse_procedure_log(path: Path) -> list[dict[str, object]]:
    if not path.is_file():
        return []
    records: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            records.append(json.loads(stripped))
        except json.JSONDecodeError:
            records.append({"parse_error": stripped})
    return records


def summarize_procedure_log(
    records: list[dict[str, object]],
    expected: dict[str, list[str]],
) -> dict[str, dict[str, object]]:
    summary: dict[str, dict[str, object]] = {}
    by_skill: dict[str, set[str]] = {}
    for record in records:
        skill = str(record.get("skill", NOT_AVAILABLE))
        phase = str(record.get("phase", NOT_AVAILABLE))
        if skill == NOT_AVAILABLE or phase == NOT_AVAILABLE:
            continue
        if record.get("status") == "complete":
            by_skill.setdefault(skill, set()).add(phase)
    for skill, phases in expected.items():
        completed = by_skill.get(skill, set())
        missing = [phase for phase in phases if phase not in completed]
        summary[skill] = {
            "complete": not missing,
            "completed_phases": sorted(completed),
            "missing_phases": missing,
        }
    return summary


def read_index(root: Path) -> dict:
    index_path = dispositions_index_path(root)
    if not index_path.is_file():
        return {}
    return json.loads(index_path.read_text(encoding="utf-8"))


def run_list_open(root: Path) -> object:
    """Count open accepted events via the JSONL store when it exists."""
    events_root = dispositions_events_root(root)
    if not events_root.is_dir():
        return NOT_AVAILABLE
    current = materialize_current_events(list(iter_event_rows(events_root)))
    return sum(1 for event in current if event["disposition"] == "accepted")


def run_staleness(root: Path) -> object:
    """Count effective-open accepted rows via the packaged ledger checker."""
    rows = load_rows_from_store(root)
    resolve_closures(rows)
    return sum(1 for row in rows if row.disposition == "accepted" and row.closed_by is None)


def load_disposition_events(root: Path) -> list[dict[str, object]]:
    events_root = dispositions_events_root(root)
    if not events_root.is_dir():
        return []
    return list(iter_event_rows(events_root))


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
    events_root = dispositions_events_root(root)
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


def compute_self_healing_signals(
    events: list[dict[str, object]],
    records: list[dict[str, object]],
) -> dict[str, object]:
    disposition_counts: dict[str, int] = {}
    close_back_events = 0
    for event in events:
        disposition = str(event.get("disposition", NOT_AVAILABLE))
        disposition_counts[disposition] = disposition_counts.get(disposition, 0) + 1
        if disposition == "fixed" and event.get("closes_event_ids"):
            close_back_events += 1

    raw_total = 0
    dropped_total = 0
    for record in records:
        raw = record.get("raw_count")
        dropped = record.get("dropped_unverified_count")
        if isinstance(raw, int) and isinstance(dropped, int) and raw > 0:
            raw_total += raw
            dropped_total += dropped

    cascade_rate: object = NOT_AVAILABLE
    if raw_total:
        cascade_rate = round(dropped_total / raw_total, 4)

    return {
        "disposition_event_counts": disposition_counts,
        "close_back_event_count": close_back_events,
        "cascade_prevention_rate": cascade_rate,
        "cascade_prevention_denominator": raw_total,
    }


def jsonl_views_present(root: Path) -> bool:
    base = docs_health_root(root)
    return all(
        (base / name).is_file()
        for name in (
            dispositions_index_path().name,
            dispositions_open_view_path().name,
            dispositions_current_view_path().name,
        )
    )


def resolve_surfaces(surface: str) -> tuple[str, ...]:
    return LEGACY_ALIASES.get(surface, (surface,))


def collect_dossiers(root: Path, surface: str, limit: int) -> list[Path]:
    surfaces = resolve_surfaces(surface)
    directories = [docs_health_root(root), dispositions_archived_root(root)]
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
    events = load_disposition_events(root)
    close_back = count_close_back(root)
    false_positive_classes = parse_false_positive_classes(
        root / FALSE_POSITIVE_CLASS_PATH
    )
    expected_phases = load_expected_phases(root / EXPECTED_PHASES_PATH)
    procedure_log = parse_procedure_log(root / PROCEDURE_LOG_PATH)
    prospective_procedure = summarize_procedure_log(procedure_log, expected_phases)

    records = []
    for path in collect_dossiers(root, surface, limit):
        record = parse_dossier(path)
        record["jsonl_open_accepted_count"] = open_accepted
        record["legacy_effective_open_count"] = legacy_open
        record["integrity_warning_count"] = integrity
        record["loop_stage_completed"] = loop["loop_stage_completed"]
        record["next_command"] = loop["next_command"]
        records.append(record)

    self_healing_signals = compute_self_healing_signals(events, records)

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
        "false_positive_classes": false_positive_classes,
        "false_positive_status_counts": false_positive_status_counts(
            false_positive_classes
        ),
        "self_healing_signals": self_healing_signals,
        "prospective_procedure": prospective_procedure,
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
    lines.append("## Prospective procedure")
    prospective = report.get("prospective_procedure", {})
    if prospective:
        for skill, summary in prospective.items():
            mark = "✅" if summary.get("complete") else "❌"
            missing = ", ".join(summary.get("missing_phases", [])) or "none"
            lines.append(f"- {mark} `{skill}` missing phases: {missing}")
    else:
        lines.append("- not available")
    lines.append("")
    lines.append(
        f"list-open accepted: {report['list_open_accepted_count']} · "
        f"close-back events: {report['close_back_event_count']}"
    )
    lines.append("")
    lines.append("## Self-healing signals")
    signals = report.get("self_healing_signals", {})
    if signals:
        lines.append(
            f"- cascade_prevention_rate: {signals.get('cascade_prevention_rate')}"
        )
        lines.append(
            f"- cascade_prevention_denominator: {signals.get('cascade_prevention_denominator')}"
        )
        lines.append(
            f"- close_back_event_count: {signals.get('close_back_event_count')}"
        )
    else:
        lines.append("- not available")
    lines.append("")
    lines.append("## False-positive classes")
    counts = report.get("false_positive_status_counts", {})
    if counts:
        for status in FALSE_POSITIVE_STATUSES:
            lines.append(f"- {status}: {counts.get(status, 0)}")
    else:
        lines.append("- not available")
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
        "--surface", choices=("plugin", "tooling", "both", "companions", "everything", *canonical_companion_surfaces()), default="both"
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
