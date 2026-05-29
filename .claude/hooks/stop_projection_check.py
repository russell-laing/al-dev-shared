#!/usr/bin/env python3
import sys
import json
import subprocess
import os

try:
    event = json.load(sys.stdin)

    # Prevent infinite blocking: if hook already fired once this stop, pass through
    if event.get("stop_hook_active"):
        sys.exit(0)

    project_root = os.environ.get(
        "CLAUDE_PROJECT_DIR",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    # Get all changed files (tracked, staged, untracked)
    tracked = subprocess.run(
        ["git", "-C", project_root, "diff", "--name-only", "HEAD"],
        capture_output=True,
        text=True
    )
    staged = subprocess.run(
        ["git", "-C", project_root, "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True
    )
    untracked = subprocess.run(
        ["git", "-C", project_root, "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True
    )
    changed = (tracked.stdout + staged.stdout + untracked.stdout).splitlines()

    # Detect agent source changes and projection staleness
    agent_changes = [f for f in changed if "profile-al-dev-shared/agents/" in f and f.endswith(".md")]
    generated_changes = [f for f in changed if "profile-al-dev-shared/generated/agents/" in f]

    # Block if agents changed but projections were not regenerated
    if agent_changes and not generated_changes:
        reason = (
            "Agent source files modified but projections not regenerated.\n"
            "Run: python3 scripts/generate-agent-projections.py\n"
            f"Modified agents: {', '.join(agent_changes)}"
        )
        print(f"[stop-hook] warning: {reason}", file=sys.stderr)
        print(json.dumps({"decision": "block", "reason": reason}))
        sys.exit(0)

except Exception:
    pass  # Fail open

sys.exit(0)
