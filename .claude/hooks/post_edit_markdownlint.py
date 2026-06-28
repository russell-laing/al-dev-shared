#!/usr/bin/env python3
import sys
import json
import subprocess
import os
import hashlib
from pathlib import Path

try:
    event = json.load(sys.stdin)
    tool_input = event.get("tool_input", {})
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
    if not file_path or not file_path.endswith(".md"):
        sys.exit(0)

    project_root = Path(
        os.environ.get(
            "CLAUDE_PROJECT_DIR",
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        )
    ).resolve()
    raw_path = Path(file_path)
    abs_path = (project_root / raw_path).resolve() if not raw_path.is_absolute() else raw_path.resolve()

    if not os.path.exists(abs_path):
        sys.exit(0)

    try:
        rel_path = Path(abs_path).resolve().relative_to(project_root)
    except ValueError:
        rel_path = None

    # Skip markdownlint --fix for repo-root .dev/ and docs/health/ markdown files
    # because both surfaces carry structured metadata that markdownlint --fix
    # can corrupt by reformatting list items and blank lines.
    if rel_path and (
        rel_path.parts[:1] == (".dev",) or rel_path.parts[:2] == ("docs", "health")
    ):
        sys.exit(0)

    config = os.path.join(str(project_root), ".markdownlint.json")

    # Snapshot before so we can detect whether --fix actually changed the file
    with open(abs_path, "rb") as f:
        before_hash = hashlib.md5(f.read()).hexdigest()

    result = subprocess.run(
        ["markdownlint", "--fix", "--config", config, abs_path],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        with open(abs_path, "rb") as f:
            after_hash = hashlib.md5(f.read()).hexdigest()
        if before_hash != after_hash:
            # File was mutated — warn so the caller re-reads before further edits
            print(f"[post-edit] markdownlint: auto-fixed {os.path.basename(abs_path)} — re-read before further edits")
    else:
        msg = (result.stdout.strip() or result.stderr.strip())[:200]
        print(f"[post-edit] markdownlint: unfixed issues remain — {msg}")
except Exception as exc:
    print(f"[post-edit] markdownlint hook skipped: {exc}", file=sys.stderr)

sys.exit(0)
