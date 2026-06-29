#!/usr/bin/env python3
"""Verify that precision-gate fixture findings were retained in a health dossier."""

from __future__ import annotations

import argparse
from pathlib import Path


def read_expected_ids(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def verify_retained_ids(dossier_text: str, expected_ids: list[str]) -> list[str]:
    retained_section = []
    in_quality_findings = False
    for line in dossier_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_quality_findings = stripped == "## Quality findings"
            continue
        if in_quality_findings:
            retained_section.append(line)
    retained_text = "\n".join(retained_section)
    return [
        expected_id
        for expected_id in expected_ids
        if f"**[{expected_id}]**" not in retained_text
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dossier", type=Path, required=True)
    parser.add_argument("--expected", type=Path, required=True)
    args = parser.parse_args(argv)

    missing = verify_retained_ids(
        args.dossier.read_text(encoding="utf-8"),
        read_expected_ids(args.expected),
    )
    if missing:
        print("precision-gate fixture: FAIL")
        for expected_id in missing:
            print(f"  missing retained fixture: {expected_id}")
        return 1
    print("precision-gate fixture: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
