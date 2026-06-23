"""Shared helper for reading, appending, and materializing health dispositions."""

from __future__ import annotations

from collections import Counter, defaultdict, OrderedDict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Iterator
import json
import re
import sys


TABLE_HEADER = (
    "| ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence / note |"
)
TABLE_DIVIDER = (
    "|----|---------|-----------|--------|---------|-------------|------|------------------|"
)

EVENT_REQUIRED_FIELDS = (
    "event_id",
    "surface",
    "dimension",
    "object",
    "finding",
    "disposition",
    "date",
    "closes_event_ids",
    "evidence",
    "source",
)
VALID_DISPOSITIONS = {"accepted", "declined", "fixed", "grandfathered"}
EVENT_ID_RE = re.compile(r"^disp_(\d{8})_(\d{6})$")


def normalize_finding(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _escape_cell(text: object) -> str:
    """Escape bare pipe characters in a Markdown table cell value."""
    return str(text).replace("|", r"\|")


def _unescape_cell(text: str) -> str:
    """Unescape \\| back to | when reading a Markdown table cell."""
    return text.replace(r"\|", "|")


def disposition_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        row["surface"].strip(),
        row["dimension"].strip(),
        row["object"].strip(),
        normalize_finding(row["finding"]),
    )


def event_shard_path_for_date(iso_date: str) -> Path:
    """Return relative JSONL shard path YYYY/YYYY-MM.jsonl for an ISO date."""
    year, month, _ = iso_date.split("-")
    return Path(year) / f"{year}-{month}.jsonl"


def next_event_id(events: list[dict[str, object]], iso_date: str) -> str:
    """Allocate the next stable event ID for the given date."""
    date_token = iso_date.replace("-", "")
    max_seq = 0
    for event in events:
        raw = str(event.get("event_id", ""))
        match = EVENT_ID_RE.match(raw)
        if not match or match.group(1) != date_token:
            continue
        max_seq = max(max_seq, int(match.group(2)))
    return f"disp_{date_token}_{max_seq + 1:06d}"


def validate_event(event: dict[str, object]) -> list[str]:
    """Return validation errors for one JSONL disposition event."""
    errors: list[str] = []
    for field in EVENT_REQUIRED_FIELDS:
        if field not in event:
            errors.append(f"{field} is required")
    if not str(event.get("event_id", "")).strip():
        errors.append("event_id is required")
    if str(event.get("disposition", "")).strip().lower() not in VALID_DISPOSITIONS:
        errors.append("disposition must be one of accepted, declined, fixed, grandfathered")
    closes = event.get("closes_event_ids", [])
    if not isinstance(closes, list) or not all(isinstance(v, str) for v in closes):
        errors.append("closes_event_ids must be a list of strings")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(event.get("date", ""))):
        errors.append("date must be YYYY-MM-DD")
    return errors


def parse_event_file(path: Path) -> list[dict[str, object]]:
    """Parse a JSONL event shard into event dictionaries."""
    events: list[dict[str, object]] = []
    if not path.exists():
        return events
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno}: invalid JSONL: {exc}") from exc
        if not isinstance(event, dict):
            raise ValueError(f"{path}:{lineno}: event must be a JSON object")
        errors = validate_event(event)
        if errors:
            raise ValueError(f"{path}:{lineno}: " + "; ".join(errors))
        event["disposition"] = str(event["disposition"]).lower()
        events.append(event)
    return events


def iter_event_rows(events_root: Path) -> Iterator[dict[str, object]]:
    """Yield JSONL events from all shards in sorted order."""
    for shard in sorted(events_root.rglob("*.jsonl")):
        yield from parse_event_file(shard)


def append_event(events_root: Path, event: dict[str, object]) -> Path:
    """Append one event to its JSONL month shard and return the shard path."""
    errors = validate_event(event)
    if errors:
        raise ValueError("; ".join(errors))
    event_id = str(event["event_id"])
    existing_ids = {str(existing["event_id"]) for existing in iter_event_rows(events_root) if existing.get("event_id")}
    if event_id in existing_ids:
        raise ValueError(f"duplicate event_id: {event_id}")
    shard = events_root / event_shard_path_for_date(str(event["date"]))
    shard.parent.mkdir(parents=True, exist_ok=True)
    with open(shard, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return shard


def _event_key(event: dict[str, object]) -> tuple[str, str, str, str]:
    return (
        str(event["surface"]).strip(),
        str(event["dimension"]).strip(),
        str(event["object"]).strip(),
        normalize_finding(str(event["finding"])),
    )


def materialize_current_events(events: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return current event state, preserving legacy closure semantics during migration."""
    by_id = {str(event["event_id"]): event for event in events}
    closed_ids: set[str] = set()
    for event in events:
        for closed_id in event.get("closes_event_ids", []):
            if closed_id not in by_id:
                raise ValueError(f"unknown closes_event_ids value: {closed_id}")
            closed_ids.add(str(closed_id))

    open_accepted: list[dict[str, object]] = []
    by_legacy_id: dict[str, dict[str, object]] = {}
    for event in events:
        event_id = str(event["event_id"])
        if event_id in closed_ids:
            continue
        legacy_id = str(event.get("legacy_id", "")).strip()
        if str(event["disposition"]) == "accepted":
            open_accepted.append(event)
            if legacy_id:
                by_legacy_id[legacy_id] = event
            continue
        if str(event["disposition"]) in ("declined", "grandfathered") and legacy_id:
            target = by_legacy_id.get(legacy_id)
            if target:
                closed_ids.add(str(target["event_id"]))
                open_accepted = [e for e in open_accepted if str(e["event_id"]) != str(target["event_id"])]
                by_legacy_id.pop(legacy_id, None)
                continue
        if str(event["disposition"]) in ("declined", "grandfathered"):
            for accepted in list(open_accepted):
                if str(accepted["object"]).strip() == str(event["object"]).strip():
                    closed_ids.add(str(accepted["event_id"]))
                    open_accepted.remove(accepted)
                    break

    latest: OrderedDict[tuple[str, str, str, str], dict[str, object]] = OrderedDict()
    for event in events:
        if str(event["event_id"]) not in closed_ids:
            latest[_event_key(event)] = event
    return list(latest.values())


def _source_hash(events: list[dict[str, object]]) -> str:
    payload = "\n".join(json.dumps(e, ensure_ascii=False, sort_keys=True) for e in events)
    return sha256(payload.encode("utf-8")).hexdigest()


def build_disposition_index(
    events: list[dict[str, object]], *, source_hash: str | None = None
) -> dict[str, object]:
    current = materialize_current_events(events)
    by_disposition = Counter(str(e["disposition"]) for e in current)
    by_surface: dict[str, dict[str, int]] = defaultdict(lambda: {"current_rows": 0, "open_accepted": 0})
    by_dimension: dict[str, dict[str, int]] = defaultdict(lambda: {"current_rows": 0, "open_accepted": 0})
    for event in current:
        surface = str(event["surface"])
        dimension = str(event["dimension"])
        by_surface[surface]["current_rows"] += 1
        by_dimension[dimension]["current_rows"] += 1
        if event["disposition"] == "accepted":
            by_surface[surface]["open_accepted"] += 1
            by_dimension[dimension]["open_accepted"] += 1
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_hash": source_hash or _source_hash(events),
        "total_events": len(events),
        "current_rows": len(current),
        "open_accepted": by_disposition.get("accepted", 0),
        "integrity_warnings": 0,
        "by_disposition": dict(sorted(by_disposition.items())),
        "by_surface": dict(sorted(by_surface.items())),
        "by_dimension": dict(sorted(by_dimension.items())),
    }


def validate_index_freshness(index: dict[str, object], events: list[dict[str, object]]) -> list[str]:
    errors: list[str] = []
    if index.get("source_hash") != _source_hash(events):
        errors.append("source_hash is stale")
    if index.get("total_events") != len(events):
        errors.append("total_events is stale")
    if index.get("open_accepted") != build_disposition_index(events)["open_accepted"]:
        errors.append("open_accepted is stale")
    return errors


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
    """Write the compact open-accepted view Claude should read by default."""
    current = [
        event for event in materialize_current_events(events)
        if event["disposition"] == "accepted"
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Open Health Dispositions",
        "",
        "<!-- generated from docs/health/dispositions-events/; do not edit directly -->",
        "",
        "| Event ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence | Closes |",
        "|----------|---------|-----------|--------|---------|-------------|------|----------|--------|",
    ]
    lines.extend(_markdown_event_row(event) for event in current)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_current_events_view(output: Path, events: list[dict[str, object]]) -> None:
    """Write the human current-state view from JSONL events."""
    current = materialize_current_events(events)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Health Finding Dispositions",
        "",
        "<!-- generated from docs/health/dispositions-events/; do not edit directly -->",
        "",
        "| Event ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence | Closes |",
        "|----------|---------|-----------|--------|---------|-------------|------|----------|--------|",
    ]
    lines.extend(_markdown_event_row(event) for event in current)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_legacy_compatibility_view(output: Path, events: list[dict[str, object]]) -> None:
    """Write the temporary legacy eight-column Markdown view from JSONL events."""
    current = materialize_current_events(events)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Health Finding Dispositions",
        "",
        "<!-- generated from docs/health/dispositions-events/; do not edit directly -->",
        "",
        "| ID | Surface | Dimension | Object | Finding | Disposition | Date | Note |",
        "|----|---------|-----------|--------|---------|-------------|------|------|",
    ]
    lines.extend(_markdown_legacy_row(event) for event in current)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_index(output: Path, events: list[dict[str, object]]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(build_disposition_index(events), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
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


def list_open(
    ledger_path: Path,
    status: str = "accepted",
    surface: str | None = None,
    dimension: str | None = None,
) -> list[dict[str, str]]:
    """Rows in the current view whose disposition == status.

    Optionally filtered by surface/dimension. Because the current view is
    last-writer-wins (``materialize_current_view``), an ``accepted`` row here
    has no later ``fixed``/``declined``/``grandfathered`` superseding it — so
    ``status='accepted'`` is exactly the genuinely-open backlog.
    """
    target = status.strip().lower()
    rows = materialize_current_view(parse_ledger_file(ledger_path))
    out = [r for r in rows if r["disposition"].strip().lower() == target]
    if surface:
        out = [r for r in out if r["surface"].strip() == surface]
    if dimension:
        out = [r for r in out if r["dimension"].strip() == dimension]
    return out


# ---------------------------------------------------------------------------
# Suppression matcher
#
# A deterministic *candidate* matcher for /report-plugin-health Phase 1d. It
# classifies each new finding against the current-view ledger so the report
# stops eyeballing the whole ledger by hand. Output is advisory: the model
# confirms `suppress`/`verify` candidates before acting (see
# .claude/knowledge/report-input-gates.md §1d). Matching is intentionally
# tolerant of lens rephrasing but guarded by object membership + text overlap
# so a different issue on the same object is not silently suppressed.
# ---------------------------------------------------------------------------

SIMILARITY_THRESHOLD = 0.4  # when finding-type is unknown, text must carry the match
SIMILARITY_THRESHOLD_SAME_TYPE = 0.25  # same type already excludes cross-type, so relax
_SUBSTRING_MIN = 25  # ignore trivial substring containment below this length
# Types with one verdict per object (a name either conforms or it does not):
# object + type membership is sufficient, no text overlap required. Types that
# can have many verdicts per object (bloat, clarity, structure, …) keep the text
# gate so a different aspect/phase stays distinct.
_OBJECT_SUFFICIENT_TYPES = {"naming", "name-fit"}
_WILDCARD = "unknown"  # legacy rows carry surface/dimension == "unknown"
_KEBAB_RE = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)+")
_WORD_RE = re.compile(r"[a-z0-9]+")
_PREFIX_RE = re.compile(r"^[a-z][a-z0-9 /-]*:\s*")  # leading "Bloat:" / "clarity:" label
# Leading file:line citation that findings-file observations open with, e.g.
# `.claude/agents/foo.md:82` or skills/bar/SKILL.md:10-20 — stripped before
# tokenizing so path components (dir names, extensions) do not flood the token
# set and dilute the Jaccard overlap against terse ledger paraphrases (#974).
# Requires a file extension so ordinary "Label:" prefixes are left to _PREFIX_RE.
_PATH_CITATION_RE = re.compile(
    r"^`?[a-z0-9_./-]+\.[a-z0-9]+(?::\d+(?:-\d+)?)?`?\s*(?:[—–-]+\s*)?"
)
_STOPWORDS = {
    "the", "a", "an", "of", "to", "in", "is", "it", "that", "this",
    "and", "or", "for", "with", "but", "not", "no", "are", "was", "its",
}


def object_members(cell: str) -> set[str]:
    """Return the set of kebab-case object names named in a ledger Object cell.

    Handles single objects, comma lists, and parenthetical lists such as
    ``11 design-lens agents (caller-alignment, model-fit, ...)``.
    """
    return set(_KEBAB_RE.findall(cell.lower()))


_TYPE_ALIASES = {
    "bloat": "bloat",
    "clarity": "clarity",
    "prompt clarity": "clarity",
    "structure": "structure",
    "structural": "structure",
    "structural conventions": "structure",
    "description": "description",
    "description drift": "description",
    "name fit": "name-fit",
    "name-fit": "name-fit",
    "naming": "naming",
    "naming convention": "naming",
    "tool hygiene": "tool-hygiene",
    "tool-hygiene": "tool-hygiene",
    "scope isolation": "scope-isolation",
    "model fit": "model-fit",
    "caller alignment": "caller-alignment",
    "usage patterns": "usage-patterns",
    "complexity": "complexity",
    "complexity outliers": "complexity",
    "handoff": "handoff",
    "handoff chain gaps": "handoff",
    "near-duplicate": "near-duplicate",
    "near-duplicate shapes": "near-duplicate",
    "pre-planning": "preplanning",
    "pre-planning skills": "preplanning",
    "shared execution backbone": "shared-backbone",
    "surface placement": "surface-placement",
}


def normalize_type(raw: str) -> str:
    """Map a finding-type label or block title to a canonical type, or '' if unknown."""
    key = re.sub(r"\s+", " ", raw.strip().lower()).rstrip("s")
    if key in _TYPE_ALIASES:
        return _TYPE_ALIASES[key]
    return _TYPE_ALIASES.get(raw.strip().lower(), "")


def _finding_type(text: str) -> str:
    """Derive a canonical finding type from a leading 'Label:' prefix, else ''."""
    head = normalize_finding(text)
    if ":" in head:
        label = head.split(":", 1)[0]
        if len(label) <= 32 and re.fullmatch(r"[A-Za-z][A-Za-z /-]*", label):
            return normalize_type(label)
    return ""


def _finding_tokens(text: str) -> set[str]:
    body = normalize_finding(text).lower()
    body = _PATH_CITATION_RE.sub("", body)  # drop a leading file:line citation (#974)
    body = _PREFIX_RE.sub("", body)         # then drop a leading "Bloat:"/"clarity:" label
    return {t for t in _WORD_RE.findall(body) if len(t) >= 3 and t not in _STOPWORDS}


def _text_similar(a: str, b: str, threshold: float = SIMILARITY_THRESHOLD) -> bool:
    na, nb = normalize_finding(a).lower(), normalize_finding(b).lower()
    shorter = min(na, nb, key=len)
    if len(shorter) >= _SUBSTRING_MIN and (na in nb or nb in na):
        return True
    ta, tb = _finding_tokens(a), _finding_tokens(b)
    if not ta or not tb:
        return False
    overlap = len(ta & tb)
    union = len(ta | tb)
    return union > 0 and (overlap / union) >= threshold


def _field_compatible(finding_val: str, row_val: str) -> bool:
    fv, rv = finding_val.strip(), row_val.strip()
    return fv == rv or rv == _WILDCARD or fv == _WILDCARD


def _classification_for(disposition: str) -> str:
    d = disposition.strip().lower()
    if d in ("declined", "grandfathered"):
        return "suppress"
    if d == "fixed":
        return "verify"
    return "keep"  # accepted (or anything else) — surfaced, not auto-suppressed


_PRECEDENCE = {"suppress": 0, "verify": 1, "keep": 2}


def match_against_ledger(
    findings: list[dict[str, str]], current_rows: list[dict[str, str]]
) -> list[dict[str, object]]:
    """Classify each finding against the current-view ledger.

    Each finding dict needs ``surface``, ``dimension``, ``object``, ``finding``.
    Returns one result per finding: ``{"finding": <input>, "classification":
    suppress|verify|keep, "matched": <row or None>}``. ``suppress`` =
    declined/grandfathered match; ``verify`` = fixed match (re-check live file);
    ``keep`` = no decided match (or accepted — surface annotated).
    """
    results: list[dict[str, object]] = []
    for finding in findings:
        f_obj = finding.get("object", "").strip()
        f_type = finding.get("type", "") or _finding_type(finding.get("finding", ""))
        best: tuple[str, dict[str, str]] | None = None
        for row in current_rows:
            if not _field_compatible(finding.get("surface", ""), row["surface"]):
                continue
            if not _field_compatible(finding.get("dimension", ""), row["dimension"]):
                continue
            members = object_members(row["object"])
            if f_obj and f_obj.lower() not in members and f_obj != row["object"].strip():
                continue
            # Different *known* finding-types on the same object (e.g. bloat vs
            # clarity) are never the same issue — reject outright. Same type
            # relaxes the text threshold (cross-type is already excluded) so a
            # rephrase still matches, but text must still overlap enough to keep
            # a different aspect/phase of the same type (Phase 0 vs Phase 2)
            # distinct. Unknown type falls back to the stricter text gate.
            r_type = _finding_type(row["finding"])
            same_type = bool(f_type) and f_type == r_type
            if f_type and r_type and f_type != r_type:
                continue
            if same_type and f_type in _OBJECT_SUFFICIENT_TYPES:
                pass  # one verdict per object — object + type is enough
            else:
                threshold = (
                    SIMILARITY_THRESHOLD_SAME_TYPE if same_type else SIMILARITY_THRESHOLD
                )
                if not _text_similar(
                    finding.get("finding", ""), row["finding"], threshold
                ):
                    continue
            cls = _classification_for(row["disposition"])
            if cls == "keep":
                # accepted match: only record if nothing stronger seen
                if best is None:
                    best = (cls, row)
                continue
            if best is None or _PRECEDENCE[cls] < _PRECEDENCE[best[0]]:
                best = (cls, row)
        classification = best[0] if best else "keep"
        results.append(
            {
                "finding": finding,
                "classification": classification,
                "matched": best[1] if best else None,
            }
        )
    return results


def parse_findings_file(path: Path) -> list[dict[str, str]]:
    """Extract (surface, dimension, object, finding) tuples from a findings file.

    Reads the ``surface:`` frontmatter and walks ``### <Lens> Findings`` blocks,
    mapping each block to a dimension and parsing ``- **object** | sev | obs | fix``
    lines (uses the observation as the finding text).
    """
    text = path.read_text(encoding="utf-8")
    surface = _WILDCARD
    fm = re.search(r"^surface:\s*(\S+)\s*$", text, re.MULTILINE)
    if fm:
        surface = fm.group(1).strip()

    quality_kw = ("bloat", "clarity", "description", "name fit", "name-fit",
                  "structural", "structure")
    findings: list[dict[str, str]] = []
    dimension = "design"
    ftype = ""
    parsed_count = 0
    for line in text.splitlines():
        header = re.match(r"^#{2,4}\s+(.*?)\s+Findings\b", line)
        if header:
            raw_title = header.group(1)
            # Drop a trailing surface qualifier like "(agents)" / "(skills)".
            title = re.sub(r"\s*\([^)]*\)\s*$", "", raw_title).lower()
            if "naming" in title:
                dimension = "naming"
            elif any(kw in title for kw in quality_kw):
                dimension = "quality"
            else:
                dimension = "design"
            ftype = normalize_type(title)
            continue
        item = re.match(r"^- \*\*(.+?)\*\*\s*\|(.*)$", line)
        if item:
            obj = item.group(1).strip()
            cells = [c.strip() for c in item.group(2).split("|")]
            observation = cells[1] if len(cells) >= 2 else (cells[0] if cells else "")
            findings.append(
                {
                    "surface": surface,
                    "dimension": dimension,
                    "object": obj,
                    "finding": observation,
                    "type": ftype,
                }
            )
            parsed_count += 1
        elif line.startswith("|") and not line.startswith("| Object") and not line.startswith("| Event") and not line.startswith("|---") and not line.startswith("| ---"):
            # Table-format finding row: | object | finding | ...
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) >= 2 and cols[0]:
                obj = cols[0]
                finding_text = cols[1] if len(cols) > 1 else ""
                findings.append({"object": obj, "finding": finding_text})
                parsed_count += 1
    total_data_lines = sum(
        1 for ln in text.splitlines()
        if ln.startswith("|") and not ln.startswith("| Object") and not ln.startswith("| Event")
        and not ln.startswith("|---") and not ln.startswith("| ---")
    )
    if total_data_lines > 0 and parsed_count < total_data_lines:
        print(f"[parse_findings_file] WARNING: parsed {parsed_count} / {total_data_lines} table rows — check format", file=sys.stderr)
    return findings


def _event_to_legacy_row(event: dict[str, object]) -> dict[str, str]:
    """Convert a JSONL event dict to a legacy row dict for match_against_ledger."""
    return {
        "id": str(event.get("event_id", "")),
        "surface": str(event.get("surface", "")),
        "dimension": str(event.get("dimension", "")),
        "object": str(event.get("object", "")),
        "finding": str(event.get("finding", "")),
        "disposition": str(event.get("disposition", "")),
        "date": str(event.get("date", "")),
        "note": str(event.get("evidence", "")),
    }


def _cli_match(
    findings_path: Path,
    ledger_path: Path,
    events_root: Path | None = None,
) -> int:
    """Classify findings against the JSONL event store when present, else Markdown ledger.

    When ``events_root`` exists (or the default ``docs/health/dispositions-events/``
    directory is present), the JSONL event store is used as the authoritative
    source. The Markdown ``ledger_path`` is used only as a fallback for
    repositories that do not yet have JSONL events. This prevents a stale or
    absent Markdown file from silently hiding newer JSONL events.
    """
    _DEFAULT_EVENTS_ROOT = Path("docs/health/dispositions-events")
    resolved_events_root = events_root if events_root is not None else _DEFAULT_EVENTS_ROOT

    if resolved_events_root.exists() and any(resolved_events_root.rglob("*.jsonl")):
        # Primary path: read from JSONL event store
        events = list(iter_event_rows(resolved_events_root))
        current_events = materialize_current_events(events)
        rows = [_event_to_legacy_row(e) for e in current_events]
        source_label = f"JSONL ({resolved_events_root})"
    else:
        # Fallback: legacy Markdown ledger (historical compatibility only)
        if not ledger_path.exists():
            print(
                f"No JSONL event store found at {resolved_events_root} and "
                f"no Markdown ledger at {ledger_path}; nothing to match against."
            )
            return 1
        rows = materialize_current_view(parse_ledger_file(ledger_path))
        source_label = f"Markdown ledger ({ledger_path}) [legacy fallback]"

    findings = parse_findings_file(findings_path)
    results = match_against_ledger(findings, rows)
    print(f"# source: {source_label}")
    counts = {"suppress": 0, "verify": 0, "keep": 0}
    for r in results:
        counts[str(r["classification"])] += 1
        matched = r["matched"]
        f = r["finding"]
        assert isinstance(f, dict)
        mid = matched["id"] if isinstance(matched, dict) else "-"
        snippet = f.get("finding", "")[:60]
        print(f"{r['classification']:8} {mid:6} {f.get('object', ''):45} {snippet}")
    print(
        f"\nsuppress={counts['suppress']} verify={counts['verify']} "
        f"keep={counts['keep']} (total={len(results)})"
    )
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Health disposition store utilities.")
    sub = parser.add_subparsers(dest="command", required=True)
    m = sub.add_parser("match", help="Classify findings against the disposition ledger.")
    m.add_argument("--findings", required=True, type=Path)
    m.add_argument(
        "--ledger", type=Path, default=Path("docs/health/dispositions.md")
    )
    m.add_argument(
        "--events-root",
        type=Path,
        default=None,
        help="Override default JSONL events root (docs/health/dispositions-events/). "
             "When present and non-empty, takes precedence over the Markdown ledger.",
    )

    _HISTORY_DEFAULT = Path("docs/health/dispositions-history")

    ap = sub.add_parser(
        "append_row",
        help="Append one disposition row to its month shard (chosen by the row date).",
    )
    for field in ("id", "surface", "dimension", "object", "finding", "disposition", "date", "note"):
        ap.add_argument(f"--{field}", required=True)
    ap.add_argument("--history-root", type=Path, default=_HISTORY_DEFAULT)

    p_sync = sub.add_parser("sync_shard", help="Sync one or more JSONL events to the Markdown history shard")
    p_sync_group = p_sync.add_mutually_exclusive_group(required=True)
    p_sync_group.add_argument("--event-id", help="Sync the single event matching this ID")
    p_sync_group.add_argument("--since", metavar="YYYY-MM-DD", help="Sync all events on or after this date")
    p_sync.add_argument("--events-root", type=Path, default=Path("docs/health/dispositions-events"))
    p_sync.add_argument("--history-root", type=Path, default=_HISTORY_DEFAULT)

    ih = sub.add_parser(
        "iter_history_rows",
        help="Print every history-shard row in chronological order as JSON lines.",
    )
    ih.add_argument("--history-root", type=Path, default=_HISTORY_DEFAULT)

    _EVENTS_DEFAULT = Path("docs/health/dispositions-events")

    ae = sub.add_parser("append_event", help="Append one JSONL disposition event.")
    for field in ("surface", "dimension", "object", "finding", "disposition", "date", "evidence", "source"):
        ae.add_argument(f"--{field}", required=True)
    ae.add_argument("--event-id", default="", help="Override auto-allocation for migration/recovery only.")
    ae.add_argument("--legacy-id", default="")
    ae.add_argument("--closes-event-ids", default="")
    ae.add_argument("--events-root", type=Path, default=_EVENTS_DEFAULT)

    regen = sub.add_parser("regenerate", help="Regenerate disposition views from JSONL events.")
    regen.add_argument("--events-root", type=Path, default=_EVENTS_DEFAULT)
    regen.add_argument("--open-view", type=Path, default=Path("docs/health/dispositions-open.md"))
    regen.add_argument("--current-view", type=Path, default=Path("docs/health/dispositions-current.md"))
    regen.add_argument("--index", type=Path, default=Path("docs/health/dispositions-index.json"))
    regen.add_argument("--compatibility-view", type=Path, default=Path("docs/health/dispositions.md"))

    lo = sub.add_parser(
        "list-open",
        help="Print current-view rows with a given disposition (default accepted) as JSON lines.",
    )
    lo.add_argument("--ledger", type=Path, default=Path("docs/health/dispositions.md"))
    lo.add_argument("--status", default="accepted")
    lo.add_argument("--surface")
    lo.add_argument("--dimension")

    args = parser.parse_args()
    if args.command == "match":
        raise SystemExit(_cli_match(args.findings, args.ledger, args.events_root))
    if args.command == "append_row":
        row = {
            f: getattr(args, f)
            for f in ("id", "surface", "dimension", "object", "finding", "disposition", "date", "note")
        }
        shard = append_row(args.history_root, row)
        print(shard)
        raise SystemExit(0)
    if args.command == "iter_history_rows":
        import json

        for r in iter_history_rows(args.history_root):
            print(json.dumps(r, ensure_ascii=False))
        raise SystemExit(0)
    if args.command == "append_event":
        event_id = args.event_id or next_event_id(list(iter_event_rows(args.events_root)), args.date)
        event = {
            "event_id": event_id,
            "legacy_id": args.legacy_id,
            "surface": args.surface,
            "dimension": args.dimension,
            "object": args.object,
            "finding": args.finding,
            "disposition": args.disposition,
            "date": args.date,
            "closes_event_ids": [v.strip() for v in args.closes_event_ids.split(",") if v.strip()],
            "evidence": args.evidence,
            "source": args.source,
        }
        shard = append_event(args.events_root, event)
        print(shard)
        raise SystemExit(0)
    if args.command == "regenerate":
        events = list(iter_event_rows(args.events_root))
        render_open_view(args.open_view, events)
        render_current_events_view(args.current_view, events)
        render_index(args.index, events)
        render_legacy_compatibility_view(args.compatibility_view, events)
        print(f"regenerated {len(events)} event(s)")
        raise SystemExit(0)
    if args.command == "list-open":
        import json

        for r in list_open(args.ledger, args.status, args.surface, args.dimension):
            print(json.dumps(r, ensure_ascii=False))
        raise SystemExit(0)
    elif args.command == "sync_shard":
        events = []
        for ev in iter_event_rows(args.events_root):
            if args.event_id and ev.get("event_id") == args.event_id:
                events.append(ev)
            elif args.since and ev.get("date", "") >= args.since:
                events.append(ev)
        if not events:
            print("sync_shard: no matching events found", file=sys.stderr)
            sys.exit(1)
        for ev in events:
            row = {
                "id": ev.get("legacy_id") or ev["event_id"],
                "surface": ev["surface"],
                "dimension": ev["dimension"],
                "object": ev["object"],
                "finding": ev["finding"],
                "disposition": ev["disposition"],
                "date": ev["date"],
                "note": ev.get("evidence", ""),
            }
            append_row(args.history_root, row)
            print(f"sync_shard: wrote shard row for {ev['event_id']}")
        raise SystemExit(0)
