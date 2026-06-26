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

# Deterministic static-lens runner that replaces the four converted LLM lenses
# (naming-convention-lens, quality-agent-lens-structure,
# quality-skill-lens-structure, design-agent-lens-tool-hygiene). It reads the
# canonical tool set directly from the projection policy, so the prior
# canonical-tools marker-sync check has been retired.
STATIC_LENS_SCRIPT = os.path.join(REPO, "scripts/health_static_lenses.py")


# The 13 LLM lens agents still dispatched on disk (11 design + 2 combined
# quality readers). The four deterministic lenses converted to
# scripts/health_static_lenses.py are intentionally absent, and the eight
# individual quality lenses are now bundled into quality-agent-multilens and
# quality-skill-multilens (each reads its corpus once and applies all four
# quality rubrics).
EXPECTED_AGENTS = [
    "quality-agent-multilens",
    "quality-skill-multilens",
    "design-agent-lens-model-fit",
    "design-agent-lens-scope-isolation",
    "design-agent-lens-caller-alignment",
    "design-agent-lens-usage-patterns",
    "design-skill-lens-shared-backbone",
    "design-skill-lens-complexity",
    "design-skill-lens-near-duplicates",
    "design-skill-lens-handoff-gaps",
    "design-skill-lens-preplanning",
    "design-skill-lens-surface-placement",
    "design-skill-lens-maintainer-handoff",
]

SKILLS_TO_CHECK = [
    os.path.join(REPO, ".claude/skills/discover-plugin-health/SKILL.md"),
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

    # sonnet exceptions: shared-backbone (multi-file synthesis), handoff-gaps (chain tracing), model-fit (multi-file evaluative analysis), complexity (multi-file phase-count ranking + Atomise/Absorb synthesis), near-duplicates (multi-file comparative synthesis with multi-criterion judgement), maintainer-handoff (multi-file maintainer chain tracing from skill bodies), quality-agent-multilens/quality-skill-multilens (corpus retention across 4 sequential synthesis lenses)
    SONNET_AGENTS = {"design-skill-lens-shared-backbone", "design-skill-lens-handoff-gaps", "design-agent-lens-model-fit", "design-skill-lens-complexity", "design-skill-lens-near-duplicates", "design-skill-lens-maintainer-handoff", "quality-agent-multilens", "quality-skill-multilens"}
    if name in SONNET_AGENTS:
        if "model: sonnet" not in content:
            failures.append(_format_failure(
                path,
                "agent-model",
                "model is not set to sonnet",
                f'add "model: sonnet" to the YAML frontmatter in {path}',
            ))
    else:
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

    # Accept either emphasis marker: markdownlint MD049 (default "consistent")
    # normalizes the sentinel's emphasis to each file's dominant marker via the
    # post-edit --fix hook, so this content-presence check must not pin one form.
    if "_No issues found._" not in content and "*No issues found.*" not in content:
        failures.append(_format_failure(
            path,
            "agent-no-issues-pattern",
            'no "No issues found." fallback pattern in body',
            f'add "_No issues found._" (or "*No issues found.*") to the ## Output Format section in {path}',
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

# The deterministic static-lens runner must exist and be executable — it now
# carries the four converted lenses (incl. the structure lens's canonical-tool
# check, which it reads directly from the projection policy).
if not os.path.exists(STATIC_LENS_SCRIPT):
    failures.append(_format_failure(
        STATIC_LENS_SCRIPT,
        "static-lens-script-exists",
        "deterministic static-lens runner not found",
        "create scripts/health_static_lenses.py (the four converted lenses)",
    ))
elif not os.access(STATIC_LENS_SCRIPT, os.X_OK):
    failures.append(_format_failure(
        STATIC_LENS_SCRIPT,
        "static-lens-script-executable",
        "deterministic static-lens runner is not executable",
        "chmod +x scripts/health_static_lenses.py",
    ))

if failures:
    print(f"FAIL — {len(failures)} issue(s):\n")
    print("\n\n".join(failures))
    sys.exit(1)
else:
    print(
        f"PASS — {len(EXPECTED_AGENTS)} LLM lens agents valid, "
        f"{len(SKILLS_TO_CHECK)} dispatch skill(s) checked, static-lens runner present."
    )
