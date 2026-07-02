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
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from ..io_utils import write_json_atomic

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


def _is_passing_bullet(line: str) -> bool:
    """True for a per-file "OK" row a reader may emit despite the Output Format
    contract, e.g. `- **al-dev-foo** | Low | No issues found.`

    Precise by design: only a bullet whose *entire* pipe-delimited field equals
    "no issues found" is treated as a passing row. A real finding that merely
    mentions the phrase inside a longer observation is never matched.
    """
    s = line.strip()
    if not s.startswith("- **"):
        return False
    fields = [f.strip().rstrip(".").lower() for f in s.split("|")]
    return any(f == "no issues found" for f in fields)


def _strip_passing_bullets(block: str) -> str:
    """Drop per-file passing bullets from a lens block (deterministic backstop
    for the terse-return contract). Block-level `_No issues found._` sentinels and
    real findings are preserved. If stripping removes every finding bullet and no
    sentinel remains, a single `_No issues found._` line is inserted after the
    heading so downstream assembly still sees a well-formed clean lens.
    """
    kept = [ln for ln in block.splitlines() if not _is_passing_bullet(ln)]
    result = "\n".join(kept)
    has_finding = any(ln.strip().startswith("- **") for ln in kept)
    has_sentinel = any(tok in result for tok in _NO_ISSUES)
    if has_finding or has_sentinel:
        return result
    out = []
    inserted = False
    for ln in kept:
        out.append(ln)
        if not inserted and ln.strip().startswith("#"):
            # Insert sentinel after any heading (handles ### or #### etc.)
            out.append("")
            out.append("_No issues found._")
            inserted = True
    if not inserted:
        out.append("_No issues found._")
    return "\n".join(out)

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
        block = _strip_passing_bullets(text[start:end].strip())
        payload = {
            "lens": lens,
            "findings": block,
            "suggestion_count": _count_suggestions(block),
            "completed_at": completed_at,
        }
        path = os.path.join(out_dir, f"{date}-plugin-health-lens-{lens}.json")
        write_json_atomic(Path(path), payload)
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
        write_json_atomic(Path(path), payload)
        written.append(path)
    return written


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="path to combined agent return (markdown)")
    ap.add_argument("--date", required=True, help="ISO date for filenames, e.g. 2026-06-25")
    ap.add_argument("--out-dir", default=".dev")
    args = ap.parse_args()
    written = split_combined(Path(args.input).read_text(encoding="utf-8"), args.date, args.out_dir)
    for p in written:
        print(p)


if __name__ == "__main__":
    main()
