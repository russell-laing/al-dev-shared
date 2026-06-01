#!/usr/bin/env python3
import sys
import json
import subprocess
import os

try:
    event = json.load(sys.stdin)
    tool_input = event.get("tool_input", {})
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
    if not file_path:
        sys.exit(0)

    project_root = os.environ.get(
        "CLAUDE_PROJECT_DIR",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    shared_prefix = os.path.join(project_root, "profile-al-dev-shared")
    generated_prefix = os.path.join(shared_prefix, "generated")
    agents_prefix = os.path.join(shared_prefix, "agents")

    abs_path = os.path.abspath(file_path)

    # Check harness neutrality for shared surface files (excluding generated)
    if abs_path.startswith(shared_prefix) and not abs_path.startswith(generated_prefix):
        result = subprocess.run(
            ["python3", os.path.join(project_root, "scripts", "validate_harness_neutrality.py"), shared_prefix],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("[post-edit] harness-neutrality: OK")
        else:
            print("[post-edit] harness-neutrality: issues found — fix before committing")
            print(result.stdout[:500])

    # Check agent structure for agent files
    if abs_path.startswith(agents_prefix) and abs_path.endswith(".md"):
        result = subprocess.run(
            ["python3", os.path.join(project_root, "scripts", "validate-lens-agents.py"),
             "--path", agents_prefix],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("[post-edit] agent-structure: OK")
        else:
            print("[post-edit] agent-structure: issues found")
            print(result.stdout[:500])

    # Validate shared-surface agents and skills via validate-shared-surface.py
    validator = os.path.join(project_root, "scripts", "validate-shared-surface.py")
    agents_prefix = os.path.join(shared_prefix, "agents")
    skills_prefix = os.path.join(shared_prefix, "skills")
    if abs_path.startswith((agents_prefix, skills_prefix)) and abs_path.endswith(".md"):
        result = subprocess.run(
            ["python3", validator, abs_path],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"[post-edit] shared-surface-validate: {result.stdout.strip()}")
            print("  Fix before committing.")
        else:
            print(f"[post-edit] shared-surface-validate: OK ({os.path.basename(abs_path)})")

except Exception:
    pass  # Fail open — never block on hook error

sys.exit(0)
