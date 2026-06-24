#!/usr/bin/env python3
import sys
import json
import subprocess
import os
import hashlib

try:
    event = json.load(sys.stdin)
    tool_input = event.get("tool_input", {})
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
    if not file_path or not file_path.endswith(".md"):
        sys.exit(0)

    # Skip markdownlint --fix for .dev/ progress checkpoints (structured YAML that
    # markdownlint --fix corrupts by dedenting list items and inserting blank lines)
    if "/.dev/" in file_path and file_path.endswith("-progress.md"):
        sys.exit(0)

    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        sys.exit(0)

    project_root = os.environ.get(
        "CLAUDE_PROJECT_DIR",
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    config = os.path.join(project_root, ".markdownlint.json")

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
except Exception:
    pass

sys.exit(0)
