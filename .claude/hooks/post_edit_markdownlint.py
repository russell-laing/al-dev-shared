#!/usr/bin/env python3
import sys
import json
import subprocess
import os

try:
    event = json.load(sys.stdin)
    tool_input = event.get("tool_input", {})
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
    if not file_path or not file_path.endswith(".md"):
        sys.exit(0)

    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        sys.exit(0)

    project_root = os.environ.get(
        "CLAUDE_PROJECT_DIR",
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    config = os.path.join(project_root, ".markdownlint.json")

    result = subprocess.run(
        ["markdownlint", "--fix", "--config", config, abs_path],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"[post-edit] markdownlint: fixed {os.path.basename(abs_path)}")
    else:
        print(f"[post-edit] markdownlint: {result.stderr.strip()[:200]}")
except Exception:
    pass

sys.exit(0)
