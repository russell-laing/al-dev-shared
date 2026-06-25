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
