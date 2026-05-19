"""Validates all lens agent files and refactored skills meet the spec."""
import os
import re
import sys

REPO = "/Users/russelllaing/al-dev-shared"
AGENTS_DIR = os.path.join(REPO, ".claude/agents")

EXPECTED_AGENTS = [
    "quality-lens-clarity",
    "quality-lens-structure",
    "quality-lens-description",
    "quality-lens-bloat",
    "quality-lens-name-fit",
    "design-lens-tool-hygiene",
    "design-lens-model-fit",
    "design-lens-scope-isolation",
    "design-lens-caller-alignment",
    "design-lens-usage-patterns",
    "quality-skill-lens-clarity",
    "quality-skill-lens-structure",
    "quality-skill-lens-description",
    "quality-skill-lens-bloat",
    "quality-skill-lens-name-fit",
    "design-skill-lens-shared-backbone",
    "design-skill-lens-complexity",
    "design-skill-lens-near-duplicates",
    "design-skill-lens-handoff-gaps",
    "design-skill-lens-preplanning",
]

SKILLS_TO_CHECK = [
    os.path.join(REPO, ".claude/skills/audit-agent-quality/SKILL.md"),
    os.path.join(REPO, ".claude/skills/audit-skill-quality/SKILL.md"),
    os.path.join(REPO, ".claude/skills/analyze-agent-design/SKILL.md"),
    os.path.join(REPO, ".claude/skills/analyze-skill-design/SKILL.md"),
]

FORBIDDEN_TOOLS = ["Bash", "Write", "Edit"]

failures = []

for name in EXPECTED_AGENTS:
    path = os.path.join(AGENTS_DIR, f"{name}.md")
    if not os.path.exists(path):
        failures.append(f"MISSING: {path}")
        continue

    content = open(path).read()

    if "model: haiku" not in content:
        failures.append(f"NOT HAIKU model: {path}")

    tools_match = re.search(r'tools:\s*\[([^\]]*)\]', content)
    if tools_match:
        tools_str = tools_match.group(1)
        for tool in FORBIDDEN_TOOLS:
            if tool in tools_str:
                failures.append(f"FORBIDDEN TOOL '{tool}' in tools list: {path}")

    if "## Output Format" not in content:
        failures.append(f"MISSING '## Output Format' section: {path}")

    if "_No issues found._" not in content:
        failures.append(f"MISSING no-issues pattern: {path}")

for skill_path in SKILLS_TO_CHECK:
    if not os.path.exists(skill_path):
        failures.append(f"MISSING SKILL: {skill_path}")
        continue
    content = open(skill_path).read()
    if "Phase 2" not in content:
        failures.append(f"MISSING 'Phase 2' (parallel dispatch not added): {skill_path}")
    if "parallel" not in content.lower() and "simultaneously" not in content.lower():
        failures.append(f"MISSING parallel dispatch language: {skill_path}")

if failures:
    print(f"FAIL — {len(failures)} issue(s):")
    for f in failures:
        print(f"  {f}")
    sys.exit(1)
else:
    print(f"PASS — {len(EXPECTED_AGENTS)} agents valid, 4 skills refactored.")
