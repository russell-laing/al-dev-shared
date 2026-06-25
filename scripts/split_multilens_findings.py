#!/usr/bin/env python3
"""Split a combined multi-lens agent return into per-lens findings JSON files.

The quality multi-lens agents (quality-agent-multilens, quality-skill-multilens)
read the corpus once and emit four labelled findings blocks in a single return,
each preceded by a `<!-- lens: <name> -->` marker. This script fans that return
into the four per-lens `.dev/<date>-plugin-health-lens-<lens>.json` files the
discover Phase 4 assembly and `--resume` logic already consume — nothing
downstream changes.
"""
import argparse
import json
import os
import re
from datetime import datetime, timezone

MARKER_RE = re.compile(r"<!--\s*lens:\s*([a-z0-9-]+)\s*-->")

# The four child quality lenses each combined reader fans out into, keyed by
# object type. The discover-plugin-health resume-collapse rule and the Phase 4
# all-clean fallback both key off these fixed sets.
OBJECT_LENSES = {
    "agent": [
        "quality-agent-lens-bloat",
        "quality-agent-lens-clarity",
        "quality-agent-lens-description",
        "quality-agent-lens-name-fit",
    ],
    "skill": [
        "quality-skill-lens-bloat",
        "quality-skill-lens-clarity",
        "quality-skill-lens-description",
        "quality-skill-lens-name-fit",
    ],
}

_NO_ISSUES = ("_No issues found._", "*No issues found.*")

_LENS_HEADINGS = {
    "bloat": "Bloat Findings",
    "clarity": "Prompt Clarity Findings",
    "description": "Description Drift Findings",
    "name-fit": "Name Fit Findings",
}


def _count_suggestions(block: str) -> int:
    if "_No issues found._" in block or "*No issues found.*" in block:
        return 0
    return sum(1 for line in block.splitlines() if line.strip().startswith("- **"))


def split_combined(text, date, out_dir, completed_at=None):
    if completed_at is None:
        completed_at = datetime.now(timezone.utc).isoformat()
    matches = list(MARKER_RE.finditer(text))
    if not matches:
        raise ValueError("no '<!-- lens: ... -->' markers found in combined return")
    written = []
    for i, m in enumerate(matches):
        lens = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end].strip()
        payload = {
            "lens": lens,
            "findings": block,
            "suggestion_count": _count_suggestions(block),
            "completed_at": completed_at,
        }
        path = os.path.join(out_dir, f"{date}-plugin-health-lens-{lens}.json")
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        written.append(path)
    return written


def classify_raw(text, object_type):
    """Classify a combined-reader raw return for the discover state machine.

    Returns one of:
      "complete"  — all four expected lens markers for object_type are present
                    (the splitter can fan it out into four child JSONs).
      "all-clean" — no markers, but a No-issues sentinel is present and there are
                    no `- **` findings bullets (Phase 4 writes empty child JSONs).
      "malformed" — anything else: truncated, a partial marker set, or a
                    marker-less return that still carries findings bullets.
    """
    found = set(MARKER_RE.findall(text))
    if set(OBJECT_LENSES[object_type]).issubset(found):
        return "complete"
    no_issues = any(token in text for token in _NO_ISSUES)
    has_bullets = any(line.strip().startswith("- **") for line in text.splitlines())
    if not found and no_issues and not has_bullets:
        return "all-clean"
    return "malformed"


def reader_complete(object_type, present_child_lenses, raw_text=None):
    """Resume-collapse rule for a combined reader.

    A combined reader is complete iff *all four* of its child-lens JSONs are
    already present, OR a raw return is present that classifies as `complete` or
    `all-clean`. A partial child set or a malformed/truncated raw return ⇒ not
    complete, so the reader is re-dispatched on `--resume`.
    """
    if set(OBJECT_LENSES[object_type]).issubset(set(present_child_lenses)):
        return True
    if raw_text is not None and classify_raw(raw_text, object_type) in ("complete", "all-clean"):
        return True
    return False


def write_allclean_children(object_type, date, out_dir, completed_at=None):
    """Phase 4 all-clean fallback: write the four empty-block child JSONs for a
    marker-less all-clean raw return.

    `split_combined` raises `ValueError` on marker-less input by design, so the
    all-clean case (a reader that reported no issues without emitting markers) is
    handled here instead — each child JSON carries its heading + the No-issues
    sentinel, `suggestion_count` 0, and the shared assembly timestamp.
    """
    if completed_at is None:
        completed_at = datetime.now(timezone.utc).isoformat()
    written = []
    for lens in OBJECT_LENSES[object_type]:
        short = lens.rsplit("-lens-", 1)[1]
        heading = _LENS_HEADINGS[short]
        payload = {
            "lens": lens,
            "findings": f"### {heading}\n\n_No issues found._",
            "suggestion_count": 0,
            "completed_at": completed_at,
        }
        path = os.path.join(out_dir, f"{date}-plugin-health-lens-{lens}.json")
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        written.append(path)
    return written


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="path to combined agent return (markdown)")
    ap.add_argument("--date", required=True, help="ISO date for filenames, e.g. 2026-06-25")
    ap.add_argument("--out-dir", default=".dev")
    args = ap.parse_args()
    written = split_combined(open(args.input).read(), args.date, args.out_dir)
    for p in written:
        print(p)


if __name__ == "__main__":
    main()
