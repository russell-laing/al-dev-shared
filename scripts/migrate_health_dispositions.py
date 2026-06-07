#!/usr/bin/env python3
"""Migrate the health disposition ledger to surface/dimension columns."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


LEDGER_HEADER = (
    "Surface",
    "Dimension",
    "Object",
    "Finding",
    "Disposition",
    "Date",
    "Evidence / note",
)
LEGACY_HEADER = ("Object", "Issue", "Disposition", "Date", "Evidence / note")
ARTIFACT_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})-(?P<surface>plugin|tooling)-"
    r"(?P<kind>findings|health)\.md$"
)
FINDING_LINE_RE = re.compile(
    r"^- \*\*(?P<object>.+?)\*\* \| (?P<severity>[^|]+) \| "
    r"(?P<finding>.+?) \| (?P<fix>.+)$"
)
FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)


@dataclass(frozen=True)
class LegacyRow:
    object_name: str
    finding: str
    disposition: str
    date: str
    note: str


@dataclass(frozen=True)
class LedgerRow:
    surface: str
    dimension: str
    object_name: str
    finding: str
    disposition: str
    date: str
    note: str


@dataclass(frozen=True)
class UnresolvedRow:
    row_number: int
    object_name: str
    finding: str
    date: str
    resolved_surface: str
    resolved_dimension: str
    reason: str


def normalize_text(value: str) -> str:
    cleaned = value.replace("`", "").lower()
    cleaned = re.sub(r"\([^)]*\)", " ", cleaned)
    cleaned = re.sub(r"[^a-z0-9]+", " ", cleaned)
    return " ".join(cleaned.split())


def parse_table_rows(text: str) -> tuple[list[str], list[list[str]]]:
    header: list[str] | None = None
    rows: list[list[str]] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells:
            continue
        if header is None:
            header = cells
            continue
        if all(set(cell) <= {"-"} for cell in cells):
            continue
        rows.append(cells)
    return (header or []), rows


def extract_preamble(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("|"):
            break
        lines.append(line)
    return "\n".join(lines).rstrip()


def parse_legacy_rows(text: str) -> list[LegacyRow]:
    header, rows = parse_table_rows(text)
    if tuple(header[:5]) == LEDGER_HEADER[:5] and len(header) >= 7:
        legacy_rows: list[LegacyRow] = []
        for cells in rows:
            legacy_rows.append(
                LegacyRow(
                    object_name=cells[2],
                    finding=cells[3],
                    disposition=cells[4],
                    date=cells[5],
                    note=cells[6],
                )
            )
        return legacy_rows
    if tuple(header[:5]) != LEGACY_HEADER:
        raise ValueError("expected legacy or migrated dispositions table header")
    return [
        LegacyRow(
            object_name=cells[0],
            finding=cells[1],
            disposition=cells[2],
            date=cells[3],
            note=cells[4],
        )
        for cells in rows
    ]


def parse_frontmatter(text: str) -> dict[str, object]:
    match = FRONTMATTER_RE.match(text)
    if match is None:
        return {}
    metadata: dict[str, object] = {}
    current_key: str | None = None
    for raw_line in match.group("body").splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("  - ") and current_key is not None:
            metadata.setdefault(current_key, [])
            assert isinstance(metadata[current_key], list)
            metadata[current_key].append(line[4:].strip())
            continue
        if ":" not in line:
            current_key = None
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value:
            metadata[key] = value
            current_key = None
        else:
            metadata[key] = []
            current_key = key
    return metadata


def dimension_from_heading(heading: str) -> str | None:
    lowered = heading.lower()
    if "design" in lowered:
        return "design"
    if "quality" in lowered:
        return "quality"
    if "naming" in lowered:
        return "naming"
    return None


def build_findings_index(directory: Path) -> dict[tuple[str, str, str], tuple[str, str]]:
    index: dict[tuple[str, str, str], tuple[str, str]] = {}
    if not directory.is_dir():
        return index
    for path in directory.iterdir():
        match = ARTIFACT_RE.fullmatch(path.name)
        if match is None or match["kind"] != "findings":
            continue
        text = path.read_text(encoding="utf-8")
        metadata = parse_frontmatter(text)
        surface = str(metadata.get("surface", match["surface"]))
        current_heading = ""
        current_dimensions = metadata.get("dimensions", [])
        for line in text.splitlines():
            if line.startswith("### "):
                current_heading = line[4:].strip()
                continue
            finding_match = FINDING_LINE_RE.match(line)
            if finding_match is None:
                continue
            dimension = dimension_from_heading(current_heading)
            if dimension is None and isinstance(current_dimensions, list) and len(current_dimensions) == 1:
                dimension = str(current_dimensions[0])
            if dimension is None:
                continue
            key = (
                normalize_text(finding_match.group("object")),
                normalize_text(finding_match.group("finding")),
                match["date"],
            )
            index.setdefault(key, (surface, dimension))
    return index


def build_dossier_index(directory: Path) -> dict[tuple[str, str, str], tuple[str, str]]:
    index: dict[tuple[str, str, str], tuple[str, str]] = {}
    if not directory.is_dir():
        return index
    for path in directory.iterdir():
        match = ARTIFACT_RE.fullmatch(path.name)
        if match is None or match["kind"] != "health":
            continue
        current_dimension: str | None = None
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                heading = line[3:].strip()
                if heading == "Design suggestions":
                    current_dimension = "design"
                elif heading == "Quality findings":
                    current_dimension = "quality"
                elif heading == "Naming violations":
                    current_dimension = "naming"
                else:
                    current_dimension = None
                continue
            if current_dimension is None:
                continue
            finding_match = FINDING_LINE_RE.match(line)
            if finding_match is None:
                continue
            key = (
                normalize_text(finding_match.group("object")),
                normalize_text(finding_match.group("finding")),
                match["date"],
            )
            index.setdefault(key, (match["surface"], current_dimension))
    return index


def load_override_index(path: Path | None) -> dict[tuple[str, str, str], tuple[str, str]]:
    if path is None:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    index: dict[tuple[str, str, str], tuple[str, str]] = {}
    for item in payload:
        key = (
            normalize_text(item["object"]),
            normalize_text(item["finding"]),
            item["date"],
        )
        index[key] = (item["surface"], item["dimension"])
    return index


def infer_surface_dimension(
    row: LegacyRow,
    *,
    override_index: dict[tuple[str, str, str], tuple[str, str]],
    findings_index: dict[tuple[str, str, str], tuple[str, str]],
    dossier_index: dict[tuple[str, str, str], tuple[str, str]],
) -> tuple[str, str, str]:
    norm_object = normalize_text(row.object_name)
    norm_finding = normalize_text(row.finding)
    key = (norm_object, norm_finding, row.date)
    if key in override_index:
        surface, dimension = override_index[key]
        return surface, dimension, "override map"
    if key in findings_index:
        surface, dimension = findings_index[key]
        return surface, dimension, "findings metadata/context"
    if key in dossier_index:
        surface, dimension = dossier_index[key]
        return surface, dimension, "dossier section context"
    fuzzy_match = fuzzy_match_provenance(
        object_name=norm_object,
        finding=norm_finding,
        date=row.date,
        indexes=(findings_index, dossier_index),
    )
    if fuzzy_match is not None:
        return fuzzy_match
    return "unknown", "unknown", "no live provenance match"


def fuzzy_match_provenance(
    *,
    object_name: str,
    finding: str,
    date: str,
    indexes: tuple[dict[tuple[str, str, str], tuple[str, str]], ...],
) -> tuple[str, str, str] | None:
    candidates: list[tuple[str, str, str, str]] = []
    for index_name, index in (
        ("findings metadata/context", indexes[0]),
        ("dossier section context", indexes[1]),
    ):
        for (candidate_object, candidate_finding, candidate_date), (surface, dimension) in index.items():
            if candidate_object != object_name or candidate_date != date:
                continue
            if finding in candidate_finding or candidate_finding in finding:
                candidates.append((surface, dimension, candidate_finding, index_name))
    unique_pairs = {(surface, dimension, source) for surface, dimension, _, source in candidates}
    if len(unique_pairs) == 1 and candidates:
        surface, dimension, source = unique_pairs.pop()
        return surface, dimension, f"{source} fuzzy same-object/date match"
    return None


def migrate_ledger_rows(
    rows: list[LegacyRow],
    *,
    override_index: dict[tuple[str, str, str], tuple[str, str]],
    findings_index: dict[tuple[str, str, str], tuple[str, str]],
    dossier_index: dict[tuple[str, str, str], tuple[str, str]],
) -> tuple[list[LedgerRow], list[UnresolvedRow]]:
    migrated: list[LedgerRow] = []
    unresolved: list[UnresolvedRow] = []
    for row_number, row in enumerate(rows, start=1):
        surface, dimension, reason = infer_surface_dimension(
            row,
            override_index=override_index,
            findings_index=findings_index,
            dossier_index=dossier_index,
        )
        migrated.append(
            LedgerRow(
                surface=surface,
                dimension=dimension,
                object_name=row.object_name,
                finding=row.finding,
                disposition=row.disposition,
                date=row.date,
                note=row.note,
            )
        )
        if surface == "unknown" or dimension == "unknown":
            unresolved.append(
                UnresolvedRow(
                    row_number=row_number,
                    object_name=row.object_name,
                    finding=row.finding,
                    date=row.date,
                    resolved_surface=surface,
                    resolved_dimension=dimension,
                    reason=reason,
                )
            )
    return migrated, unresolved


def render_ledger(rows: list[LedgerRow], *, preamble: str = "") -> str:
    lines: list[str] = []
    if preamble:
        lines.extend([preamble, ""])
    lines.extend(
        [
        "| Surface | Dimension | Object | Finding | Disposition | Date | Evidence / note |",
        "|---------|-----------|--------|---------|-------------|------|------------------|",
        ]
    )
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row.surface,
                    row.dimension,
                    row.object_name,
                    row.finding,
                    row.disposition,
                    row.date,
                    row.note,
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def render_report(
    *,
    source_path: Path,
    migrated_count: int,
    unresolved: list[UnresolvedRow],
) -> str:
    lines = [
        "# Health Dispositions Migration Audit",
        "",
        f"Source ledger: `{source_path}`",
        "",
        f"- Migrated rows: {migrated_count}",
        f"- Rows requiring manual provenance cleanup: {len(unresolved)}",
        "",
    ]
    if not unresolved:
        lines.append("All rows were migrated with concrete surface/dimension values.")
        lines.append("")
        return "\n".join(lines)

    lines.extend(
        [
            "## Unresolved Rows",
            "",
            "| Row | Surface | Dimension | Object | Finding | Date | Reason |",
            "|-----|---------|-----------|--------|---------|------|--------|",
        ]
    )
    for row in unresolved:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row.row_number),
                    row.resolved_surface,
                    row.resolved_dimension,
                    row.object_name,
                    row.finding,
                    row.date,
                    row.reason,
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def migrate_ledger_text(
    text: str,
    *,
    override_index: dict[tuple[str, str, str], tuple[str, str]] | None = None,
    findings_index: dict[tuple[str, str, str], tuple[str, str]] | None = None,
    dossier_index: dict[tuple[str, str, str], tuple[str, str]] | None = None,
) -> tuple[str, list[UnresolvedRow]]:
    rows = parse_legacy_rows(text)
    preamble = extract_preamble(text)
    migrated, unresolved = migrate_ledger_rows(
        rows,
        override_index=override_index or {},
        findings_index=findings_index or {},
        dossier_index=dossier_index or {},
    )
    return render_ledger(migrated, preamble=preamble), unresolved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ledger",
        type=Path,
        default=Path("docs/health/dispositions.md"),
        help="ledger file to read",
    )
    parser.add_argument(
        "--write",
        type=Path,
        help="write migrated ledger to this path; otherwise print to stdout",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="write migration audit report to this path",
    )
    parser.add_argument(
        "--inference-map",
        type=Path,
        help="optional JSON override map for exact (object, finding, date) matches",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    text = args.ledger.read_text(encoding="utf-8")
    override_index = load_override_index(args.inference_map)
    findings_index = build_findings_index(args.ledger.parent)
    dossier_index = build_dossier_index(args.ledger.parent)
    migrated_text, unresolved = migrate_ledger_text(
        text,
        override_index=override_index,
        findings_index=findings_index,
        dossier_index=dossier_index,
    )

    if args.write is not None:
        args.write.write_text(migrated_text, encoding="utf-8")
    else:
        sys.stdout.write(migrated_text)

    report_path = args.report
    if report_path is None and args.write is not None:
        report_path = args.ledger.parent / "dispositions-migration-audit.md"
    if report_path is not None:
        report_path.write_text(
            render_report(
                source_path=args.ledger,
                migrated_count=len(parse_legacy_rows(text)),
                unresolved=unresolved,
            ),
            encoding="utf-8",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
