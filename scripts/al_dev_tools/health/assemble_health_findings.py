#!/usr/bin/env python3
"""Assemble the discover findings file from per-lens JSON artifacts.

Reads the `.dev/<date>-plugin-health-lens-<lens>.json` files written by the
lens dispatches and the static runner, and writes the findings file that
`/report-plugin-health` consumes. Keeping this deterministic means the
discover orchestrator never reads the findings corpus back into its own
context to re-emit it (the round-trip this script removes).

Each lens block is preceded by a `<!-- lens: <name> -->` marker so downstream
consumers can identify a finding's source lens unambiguously (two lenses share
the heading "Structural Conventions Findings").
"""
import argparse
import glob
import json
import os
import re
from datetime import datetime, timezone

# Canonical block order in the findings file. Lenses not listed here sort to the
# end, alphabetically, so a new lens never silently disappears.
LENS_ORDER = [
    # design (agent then skill)
    "design-agent-lens-tool-hygiene",
    "design-agent-lens-scope-isolation",
    "design-agent-lens-model-fit",
    "design-agent-lens-caller-alignment",
    "design-agent-lens-usage-patterns",
    "design-skill-lens-complexity",
    "design-skill-lens-near-duplicates",
    "design-skill-lens-shared-backbone",
    "design-skill-lens-handoff-gaps",
    "design-skill-lens-preplanning",
    "design-skill-lens-surface-placement",
    "design-skill-lens-maintainer-handoff",
    # quality (agent then skill): structure first, then bloat/clarity/description/name-fit
    "quality-agent-lens-structure",
    "quality-agent-lens-bloat",
    "quality-agent-lens-clarity",
    "quality-agent-lens-description",
    "quality-agent-lens-name-fit",
    "quality-skill-lens-structure",
    "quality-skill-lens-bloat",
    "quality-skill-lens-clarity",
    "quality-skill-lens-description",
    "quality-skill-lens-name-fit",
    # naming
    "naming-convention-lens",
]

_LENS_FILE_RE = re.compile(r"-plugin-health-lens-(?P<lens>[a-z0-9-]+)\.json$")

# Map each requested dimension to the lens-name prefix it owns. A lens JSON is
# assembled only when its name starts with a prefix for one of the requested
# dimensions; `all` disables filtering.
_DIMENSION_PREFIX = {
    "design": "design-",
    "quality": "quality-",
    "naming": "naming-",
}


def _allowed_prefixes(dimensions):
    """Return the tuple of in-scope lens-name prefixes, or None for no filter."""
    if "all" in dimensions:
        return None
    return tuple(_DIMENSION_PREFIX.get(d, f"{d}-") for d in dimensions)


def _load_lens_blocks(lens_dir, date, dimensions):
    """Return [(lens, findings_block), ...] in canonical order, restricted to the
    requested dimensions. Same-date lens JSONs outside those dimensions (e.g. a
    stale design lens left by an interrupted run) are ignored, not assembled."""
    allowed = _allowed_prefixes(dimensions)
    paths = glob.glob(os.path.join(lens_dir, f"{date}-plugin-health-lens-*.json"))
    by_lens = {}
    for p in paths:
        m = _LENS_FILE_RE.search(os.path.basename(p))
        if not m:
            continue
        data = json.load(open(p))
        lens = data["lens"]
        if allowed is not None and not lens.startswith(allowed):
            continue  # stale out-of-dimension JSON — skip silently
        by_lens[lens] = data["findings"].strip()

    def sort_key(lens):
        return (LENS_ORDER.index(lens) if lens in LENS_ORDER else len(LENS_ORDER), lens)

    return [(lens, by_lens[lens]) for lens in sorted(by_lens, key=sort_key)]


def _object_suffix(lens):
    """Object-type tag for disambiguating duplicate headings across lenses."""
    if "-agent-" in lens:
        return "agents"
    if "-skill-" in lens:
        return "skills"
    return lens


def _first_heading(block):
    """Return the first `### ` heading line of a block, or None."""
    for line in block.splitlines():
        if line.startswith("### "):
            return line
    return None


def assemble_findings(lens_dir, date, surface, dimensions, failed_lenses,
                      total_lenses, completed_session, completed_prior, skipped,
                      completed_at=None):
    if completed_at is None:
        completed_at = datetime.now(timezone.utc).isoformat()
    blocks = _load_lens_blocks(lens_dir, date, dimensions)

    dims_yaml = "".join(f"  - {d}\n" for d in dimensions)
    parts = [
        "---\n",
        f"surface: {surface}\n",
        "dimensions:\n",
        dims_yaml,
        "source_contract: .claude/knowledge/health-filter-contract.md\n",
        "resume_mode: false\n",
        "---\n\n",
        f"# {surface.capitalize()} Findings — {date}\n\n",
        "## Raw lens output\n\n",
    ]
    # Uniquify duplicate `### ` headings (two lenses share "Structural
    # Conventions Findings") by appending an object-type suffix to every block
    # carrying a colliding heading, so the assembled file passes markdownlint
    # MD024. The `<!-- lens: -->` marker still carries exact lens identity.
    heading_counts = {}
    for _lens, block in blocks:
        h = _first_heading(block)
        if h:
            heading_counts[h] = heading_counts.get(h, 0) + 1
    rendered = []
    for lens, block in blocks:
        h = _first_heading(block)
        if h and heading_counts.get(h, 0) > 1:
            block = block.replace(h, f"{h} ({_object_suffix(lens)})", 1)
        rendered.append(f"<!-- lens: {lens} -->\n{block}\n")
    # rstrip the joined body so the trailing per-block newline plus the section
    # separator collapse to exactly one blank line (markdownlint MD012).
    parts.append("\n---\n\n".join(rendered).rstrip() + "\n\n")

    parts.append("## Failed lenses\n\n")
    if failed_lenses:
        parts.append("\n".join(f"- {l}" for l in failed_lenses) + "\n\n")
    else:
        parts.append("None\n\n")

    accounted = completed_session + completed_prior + skipped
    status = "COMPLETE" if accounted >= total_lenses else "INCOMPLETE"
    parts.append("## Resume information\n\n")
    parts.append(f"- Total lenses in scope: {total_lenses}\n")
    parts.append(f"- Completed this session: {completed_session}\n")
    parts.append(f"- Completed in prior sessions: {completed_prior}\n")
    parts.append(f"- Skipped (no changed files in scope): {skipped}\n")
    suffix = "" if status == "COMPLETE" else " — call with --resume to finish"
    parts.append(f"- Status: {status}{suffix}\n")
    return "".join(parts)


_METRIC_FIELDS = ("raw_count", "verified_count", "dropped_unverified_count",
                  "stale_dropped_count", "suppressed_count", "failed_lens_count",
                  "new_count", "recurring_count")
_SEVERITY_DIMS = ("design", "quality", "naming")
_SEVERITY_LEVELS = ("high", "medium", "low")


def format_metrics(counts):
    missing = [f for f in _METRIC_FIELDS if f not in counts]
    if missing:
        raise ValueError(f"missing metric fields: {missing}")
    sev = counts.get("severity", {})
    if sev:
        unknown_dims = [k for k in sev if k not in _SEVERITY_DIMS]
        if unknown_dims:
            raise ValueError(
                f"unknown severity dimension keys: {unknown_dims}; "
                f"expected lowercase {_SEVERITY_DIMS}"
            )
        for dim in sev:
            if not isinstance(sev[dim], dict):
                raise ValueError(f"severity[{dim!r}] must be a dict, got {type(sev[dim]).__name__}")
            unknown_levels = [k for k in sev[dim] if k not in _SEVERITY_LEVELS]
            if unknown_levels:
                raise ValueError(
                    f"unknown severity level keys in {dim!r}: {unknown_levels}; "
                    f"expected {_SEVERITY_LEVELS}"
                )

    def row(label, key):
        d = sev.get("design", {}).get(key, 0)
        q = sev.get("quality", {}).get(key, 0)
        n = sev.get("naming", {}).get(key, 0)
        return f"| {label:<8} | {d} | {q} | {n} | {d + q + n} |"

    table = "\n".join([
        "| Severity | Design | Quality | Naming | Total |",
        "|----------|--------|---------|--------|-------|",
        row("High", "high"), row("Medium", "medium"), row("Low", "low"),
    ])
    metrics = "\n".join(f"{f}: {counts[f]}" for f in _METRIC_FIELDS)
    return (
        f"{table}\n\n"
        f"New this sweep: {counts['new_count']} · "
        f"Recurring from prior sweeps: {counts['recurring_count']} · "
        f"Stale (dropped): {counts['stale_dropped_count']} · "
        f"Dropped (unverified): {counts['dropped_unverified_count']}\n\n"
        f"<!-- benchmark-metrics\n{metrics}\n-->\n"
    )


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)
    a = sub.add_parser("assemble", help="Assemble the discover findings file.")
    a.add_argument("--lens-dir", default=".dev")
    a.add_argument("--date", required=True)
    a.add_argument("--surface", required=True, choices=["plugin", "tooling"])
    a.add_argument("--dimensions", required=True, help="comma-separated")
    a.add_argument("--failed-lenses", default="none", help="comma-separated or 'none'")
    a.add_argument("--total-lenses", type=int, required=True)
    a.add_argument("--completed-session", type=int, required=True)
    a.add_argument("--completed-prior", type=int, default=0)
    a.add_argument("--skipped", type=int, default=0)
    a.add_argument("--out", required=True)

    mt = sub.add_parser("metrics", help="Format the dossier metrics block from a counts JSON.")
    mt.add_argument("--counts", required=True, help="path to counts JSON")

    args = ap.parse_args()

    if args.command == "metrics":
        counts = json.load(open(args.counts))
        print(format_metrics(counts))
        return

    failed = [] if args.failed_lenses.strip().lower() == "none" else \
        [s.strip() for s in args.failed_lenses.split(",") if s.strip()]
    text = assemble_findings(
        lens_dir=args.lens_dir, date=args.date, surface=args.surface,
        dimensions=[s.strip() for s in args.dimensions.split(",") if s.strip()],
        failed_lenses=failed, total_lenses=args.total_lenses,
        completed_session=args.completed_session, completed_prior=args.completed_prior,
        skipped=args.skipped)
    with open(args.out, "w") as f:
        f.write(text)
    print(args.out)


if __name__ == "__main__":
    main()
