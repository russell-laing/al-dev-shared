"""Validates all lens agent files and refactored skills meet the spec."""
import os
import re
import sys
from pathlib import Path

try:
    from _entrypoint_bootstrap import bootstrap_repo
except ModuleNotFoundError:  # pragma: no cover - direct-script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _entrypoint_bootstrap import bootstrap_repo

REPO = bootstrap_repo(__file__)

from scripts.al_dev_tools.markdown_frontmatter import find_markdown_heading, parse_required_frontmatter


def _format_failure(path: str, rule: str, issue: str, fix: str) -> str:
    return (
        f"{path}\n"
        f"  rule: {rule}\n"
        f"  issue: {issue}\n"
        f"  fix: {fix}"
    )


AGENTS_DIR = REPO / ".claude" / "agents"

# Deterministic static-lens runner that replaces the four converted LLM lenses
# (naming-convention-lens, quality-agent-lens-structure,
# quality-skill-lens-structure, design-agent-lens-tool-hygiene). It reads the
# canonical tool set directly from the projection policy, so the prior
# canonical-tools marker-sync check has been retired.
STATIC_LENS_SCRIPT = REPO / "scripts" / "health_static_lenses.py"


# The 13 LLM lens agents still dispatched on disk (11 design + 2 combined
# quality readers). The four deterministic lenses converted to
# scripts/health_static_lenses.py are intentionally absent, and the eight
# individual quality lenses are now bundled into quality-agent-multilens and
# quality-skill-multilens (each reads its corpus once and applies all four
# quality rubrics).
#
# MAINTENANCE NOTE: This list must be manually kept in sync with the active
# lens agents under .claude/agents/. It cannot be auto-derived because:
# 1. The list intentionally excludes converted static lenses (naming-convention-lens, etc.)
# 2. The list intentionally excludes archived agents
# If an agent is renamed, created, or archived, update this list and SONNET_AGENTS below.
# Canonical source: .claude/agents/ directory (filter for lens agents only).
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
    REPO / ".claude" / "skills" / "discover-plugin-health" / "SKILL.md",
]

FORBIDDEN_TOOLS = ["Bash", "Write", "Edit"]
SONNET_AGENTS = {
    "design-skill-lens-shared-backbone",
    "design-skill-lens-handoff-gaps",
    "design-agent-lens-model-fit",
    "design-agent-lens-scope-isolation",
    "design-skill-lens-complexity",
    "design-skill-lens-near-duplicates",
    "design-skill-lens-maintainer-handoff",
    "design-skill-lens-preplanning",
    "quality-agent-multilens",
    "quality-skill-multilens",
}


def _has_output_format_section(content: str) -> bool:
    return find_markdown_heading(content, "## Output Format")


def _has_phase_two_heading(content: str) -> bool:
    in_fence = False
    for line in content.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or stripped.startswith(">"):
            continue
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            if heading.startswith("Phase 2"):
                return True
    return False


def main() -> int:
    failures = []

    for name in EXPECTED_AGENTS:
        path = AGENTS_DIR / f"{name}.md"
        if not path.exists():
            failures.append(_format_failure(
                str(path),
                "agent-exists",
                "agent file not found",
                f"create {path} with required frontmatter (model: haiku, tools list, ## Output Format section)",
            ))
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            failures.append(_format_failure(
                str(path),
                "agent-read-error",
                f"cannot read agent file ({type(e).__name__})",
                f"ensure {path} is readable and not corrupted",
            ))
            continue
        try:
            frontmatter, _body = parse_required_frontmatter(content)
        except ValueError as exc:
            failures.append(_format_failure(
                str(path),
                "agent-frontmatter",
                str(exc),
                f"fix the YAML frontmatter in {path}",
            ))
            continue

        # sonnet exceptions: shared-backbone (multi-file synthesis), handoff-gaps (chain tracing), model-fit (multi-file evaluative analysis), complexity (multi-file phase-count ranking + Atomise/Absorb synthesis), near-duplicates (multi-file comparative synthesis with multi-criterion judgement), maintainer-handoff (multi-file maintainer chain tracing from skill bodies), preplanning (multi-skill diagram cross-reference validation), quality-agent-multilens/quality-skill-multilens (corpus retention across 4 sequential synthesis lenses)
        if name in SONNET_AGENTS:
            model = str(frontmatter.get("model", "")).strip()
            if model != "sonnet":
                failures.append(_format_failure(
                    str(path),
                    "agent-model",
                    "model is not set to sonnet",
                    f'add "model: sonnet" to the YAML frontmatter in {path}',
                ))
        else:
            model = str(frontmatter.get("model", "")).strip()
            if model != "haiku":
                failures.append(_format_failure(
                    str(path),
                    "agent-model",
                    "model is not set to haiku",
                    f'add "model: haiku" to the YAML frontmatter in {path}',
                ))

        tools = frontmatter.get("tools", [])
        if isinstance(tools, list):
            for tool in FORBIDDEN_TOOLS:
                if tool in tools:
                    failures.append(_format_failure(
                        str(path),
                        "agent-forbidden-tool",
                        f'tool "{tool}" is not permitted for lens agents (cannot mutate files)',
                        f'remove "{tool}" from the tools list in {path}',
                    ))

        if not _has_output_format_section(content):
            failures.append(_format_failure(
                str(path),
                "agent-output-format-section",
                'no "## Output Format" section in body',
                f'add a "## Output Format" section to {path} describing the findings block structure',
            ))

        if "_No issues found._" not in content and "*No issues found.*" not in content:
            failures.append(_format_failure(
                str(path),
                "agent-no-issues-pattern",
                'no "No issues found." fallback pattern in body',
                f'add "_No issues found._" (or "*No issues found.*") to the ## Output Format section in {path}',
            ))

    for skill_path in SKILLS_TO_CHECK:
        if not skill_path.exists():
            failures.append(_format_failure(
                str(skill_path),
                "skill-exists",
                "skill file not found",
                f"create {skill_path} or remove it from SKILLS_TO_CHECK in the validator",
            ))
            continue
        try:
            content = skill_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            failures.append(_format_failure(
                str(skill_path),
                "skill-read-error",
                f"cannot read skill file ({type(e).__name__})",
                f"ensure {skill_path} is readable and not corrupted",
            ))
            continue
        if not _has_phase_two_heading(content):
            failures.append(_format_failure(
                str(skill_path),
                "skill-parallel-dispatch",
                'no "Phase 2" section — parallel agent dispatch not implemented',
                f"add a Phase 2 section with parallel agent dispatch to {skill_path}",
            ))
        if not re.search(r'\b(?:parallel|simultaneously)\b', content, re.IGNORECASE):
            failures.append(_format_failure(
                str(skill_path),
                "skill-parallel-language",
                'no parallel dispatch language ("parallel" or "simultaneously") found in body',
                f"add explicit parallel dispatch phrasing to Phase 2 in {skill_path}",
            ))

    if not STATIC_LENS_SCRIPT.exists():
        failures.append(_format_failure(
            str(STATIC_LENS_SCRIPT),
            "static-lens-script-exists",
            "deterministic static-lens runner not found",
            "create scripts/health_static_lenses.py (the four converted lenses)",
        ))
    elif not os.access(STATIC_LENS_SCRIPT, os.X_OK):
        failures.append(_format_failure(
            str(STATIC_LENS_SCRIPT),
            "static-lens-script-executable",
            "deterministic static-lens runner is not executable",
            "chmod +x scripts/health_static_lenses.py",
        ))

    if failures:
        print(f"FAIL — {len(failures)} issue(s):\n")
        print("\n\n".join(failures))
        return 1

    print(
        f"PASS — {len(EXPECTED_AGENTS)} LLM lens agents valid, "
        f"{len(SKILLS_TO_CHECK)} dispatch skill(s) checked, static-lens runner present."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
