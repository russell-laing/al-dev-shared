"""Validates all lens agent files and refactored skills meet the spec."""
import os
import re
import sys
from pathlib import Path


def _format_failure(path: str, rule: str, issue: str, fix: str) -> str:
    return (
        f"{path}\n"
        f"  rule: {rule}\n"
        f"  issue: {issue}\n"
        f"  fix: {fix}"
    )


REPO = str(Path(__file__).resolve().parents[1])
AGENTS_DIR = os.path.join(REPO, ".claude/agents")

EXPECTED_AGENTS = [
    "quality-agent-lens-clarity",
    "quality-agent-lens-structure",
    "quality-agent-lens-description",
    "quality-agent-lens-bloat",
    "quality-agent-lens-name-fit",
    "design-agent-lens-tool-hygiene",
    "design-agent-lens-model-fit",
    "design-agent-lens-scope-isolation",
    "design-agent-lens-caller-alignment",
    "design-agent-lens-usage-patterns",
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
    "naming-convention-lens",
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
        failures.append(_format_failure(
            path,
            "agent-exists",
            "agent file not found",
            f"create {path} with required frontmatter (model: haiku, tools list, ## Output Format section)",
        ))
        continue

    content = open(path).read()

    if "model: haiku" not in content:
        failures.append(_format_failure(
            path,
            "agent-model",
            "model is not set to haiku",
            f'add "model: haiku" to the YAML frontmatter in {path}',
        ))

    tools_match = re.search(r'tools:\s*\[([^\]]*)\]', content)
    if tools_match:
        tools_str = tools_match.group(1)
        for tool in FORBIDDEN_TOOLS:
            if tool in tools_str:
                failures.append(_format_failure(
                    path,
                    "agent-forbidden-tool",
                    f'tool "{tool}" is not permitted for lens agents (cannot mutate files)',
                    f'remove "{tool}" from the tools list in {path}',
                ))

    if "## Output Format" not in content:
        failures.append(_format_failure(
            path,
            "agent-output-format-section",
            'no "## Output Format" section in body',
            f'add a "## Output Format" section to {path} describing the findings block structure',
        ))

    if "_No issues found._" not in content:
        failures.append(_format_failure(
            path,
            "agent-no-issues-pattern",
            'no "_No issues found._" fallback pattern in body',
            f'add "_No issues found._" to the ## Output Format section in {path}',
        ))

for skill_path in SKILLS_TO_CHECK:
    if not os.path.exists(skill_path):
        failures.append(_format_failure(
            skill_path,
            "skill-exists",
            "skill file not found",
            f"create {skill_path} or remove it from SKILLS_TO_CHECK in the validator",
        ))
        continue
    content = open(skill_path).read()
    if "Phase 2" not in content:
        failures.append(_format_failure(
            skill_path,
            "skill-parallel-dispatch",
            'no "Phase 2" section — parallel agent dispatch not implemented',
            f"add a Phase 2 section with parallel agent dispatch to {skill_path}",
        ))
    if "parallel" not in content.lower() and "simultaneously" not in content.lower():
        failures.append(_format_failure(
            skill_path,
            "skill-parallel-language",
            'no parallel dispatch language ("parallel" or "simultaneously") found in body',
            f"add explicit parallel dispatch phrasing to Phase 2 in {skill_path}",
        ))

if failures:
    print(f"FAIL — {len(failures)} issue(s):\n")
    print("\n\n".join(failures))
    sys.exit(1)
else:
    print(f"PASS — {len(EXPECTED_AGENTS)} agents valid, 4 skills refactored.")
