#!/usr/bin/env python3
"""Content validator for .dev/health-loop-state.md.

Validates the on-disk breadcrumb against the schema and lifecycle invariants
in .claude/knowledge/health-loop-state-contract.md. The companion script
check_health_loop_handoffs.py is a static-text guard on skill wiring bodies;
this script validates breadcrumb content.

Exits 0 if valid or if the file is absent (no live loop). Exits 1 on violations.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

BREADCRUMB = Path(".dev/health-loop-state.md")

REQUIRED_FIELDS = (
    "stage_completed",
    "completed_at",
    "next_command",
    "next_inputs",
    "fresh_session_recommended",
    "note",
)

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Lifecycle successor map from health-loop-state-contract.md § Lifecycle.
# Maps stage_completed → expected next_command prefix (None means "none").
SUCCESSOR: dict[str, str | None] = {
    "plugin-health-report":       "/record-health-dispositions",
    "record-health-dispositions": "/plan-health-findings",
    "plan-health-findings":       "/implement-health-plan",
    "implement-health-plan":      None,
}

_VALID_NC_TOKENS: frozenset[str] = frozenset(
    {v for v in SUCCESSOR.values() if v is not None} | {"none"}
)


def _parse(text: str) -> dict[str, object]:
    """Parse bare-YAML breadcrumb into a field dict (stdlib-only)."""
    fields: dict[str, object] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if ":" not in stripped:
            i += 1
            continue
        key, _, rest = stripped.partition(":")
        key = key.strip()
        rest = rest.strip()
        if rest == "[]":
            fields[key] = []
            i += 1
        elif rest == "":
            items: list[str] = []
            i += 1
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:].strip())
                i += 1
            fields[key] = items
        else:
            fields[key] = rest
            i += 1
    return fields


def validate_text(text: str) -> list[str]:
    """Return a list of error strings; empty list means the breadcrumb is valid."""
    fields = _parse(text)
    errors: list[str] = []

    missing = [f for f in REQUIRED_FIELDS if f not in fields]
    if missing:
        for f in missing:
            errors.append(f"missing required field: {f!r}")
        return errors  # remaining checks need all fields present

    if not DATE_RE.match(str(fields["completed_at"])):
        errors.append(
            f"completed_at must be YYYY-MM-DD, got: {fields['completed_at']!r}"
        )

    fsr = str(fields["fresh_session_recommended"]).lower()
    if fsr not in ("true", "false"):
        errors.append(
            f"fresh_session_recommended must be true or false, "
            f"got: {fields['fresh_session_recommended']!r}"
        )

    if not isinstance(fields["next_inputs"], list):
        errors.append(
            f"next_inputs must be a list (inline [] or block - items), "
            f"got: {fields['next_inputs']!r}"
        )

    nc = str(fields["next_command"]).strip()
    stage = str(fields["stage_completed"]).strip()
    nc_token = nc.split()[0] if nc else ""

    if nc_token not in _VALID_NC_TOKENS:
        errors.append(
            f"next_command {nc_token!r} is not a known loop command; "
            f"expected one of: {', '.join(sorted(_VALID_NC_TOKENS))}"
        )
    else:
        if stage in SUCCESSOR:
            expected = SUCCESSOR[stage]
            if expected is None:
                if nc != "none":
                    errors.append(
                        f"stage_completed={stage!r} requires next_command=none, "
                        f"got: {nc!r}"
                    )
            elif not nc.startswith(expected):
                errors.append(
                    f"stage_completed={stage!r} requires next_command starting with "
                    f"{expected!r}, got: {nc!r}"
                )
        else:
            errors.append(
                f"stage_completed={stage!r} is not a known loop stage; "
                f"expected one of: {', '.join(sorted(SUCCESSOR))}"
            )

    ni = fields["next_inputs"]
    if nc_token == "none" and isinstance(ni, list) and ni:
        errors.append(
            "next_command is none but next_inputs is non-empty; "
            "use next_inputs: [] when the loop is closed"
        )

    return errors


def _staged_files() -> set[str]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True, check=False,
    ).stdout
    return {line.strip() for line in out.splitlines() if line.strip()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--staged",
        action="store_true",
        help="pre-commit mode: only validate when breadcrumb is staged",
    )
    ap.add_argument(
        "--root",
        default=".",
        help="repo root to resolve breadcrumb path against (default: cwd)",
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    breadcrumb = root / BREADCRUMB

    if args.staged:
        if str(BREADCRUMB) not in _staged_files():
            return 0  # breadcrumb not staged — nothing to check

    if not breadcrumb.exists():
        print("health-loop-state: no breadcrumb found (no live loop) — OK")
        return 0

    errors = validate_text(breadcrumb.read_text(encoding="utf-8"))

    if errors:
        print("health-loop-state: FAIL")
        for e in errors:
            print(f"  - {e}")
        if args.staged:
            print(
                "  Breadcrumb is staged but fails schema validation. "
                "Fix .dev/health-loop-state.md before committing."
            )
        return 1

    print("health-loop-state: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
