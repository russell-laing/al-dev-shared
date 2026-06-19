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
# A deterministic *candidate* matcher for /plugin-health-report Phase 1d. It
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
        if not item:
            continue
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
    return findings


def _cli_match(findings_path: Path, ledger_path: Path) -> int:
    rows = materialize_current_view(parse_ledger_file(ledger_path))
    findings = parse_findings_file(findings_path)
    results = match_against_ledger(findings, rows)
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

    _HISTORY_DEFAULT = Path("docs/health/dispositions-history")

    ap = sub.add_parser(
        "append_row",
        help="Append one disposition row to its month shard (chosen by the row date).",
    )
    for field in ("id", "surface", "dimension", "object", "finding", "disposition", "date", "note"):
        ap.add_argument(f"--{field}", required=True)
    ap.add_argument("--history-root", type=Path, default=_HISTORY_DEFAULT)

    ih = sub.add_parser(
        "iter_history_rows",
        help="Print every history-shard row in chronological order as JSON lines.",
    )
    ih.add_argument("--history-root", type=Path, default=_HISTORY_DEFAULT)

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
        raise SystemExit(_cli_match(args.findings, args.ledger))
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
    if args.command == "list-open":
        import json

        for r in list_open(args.ledger, args.status, args.surface, args.dimension):
            print(json.dumps(r, ensure_ascii=False))
        raise SystemExit(0)
