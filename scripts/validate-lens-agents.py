"""Validates all lens agent files and refactored skills meet the spec."""
import os
import re
import sys
from pathlib import Path
import yaml


def _format_failure(path: str, rule: str, issue: str, fix: str) -> str:
    return (
        f"{path}\n"
        f"  rule: {rule}\n"
        f"  issue: {issue}\n"
        f"  fix: {fix}"
    )


REPO = str(Path(__file__).resolve().parents[1])
AGENTS_DIR = os.path.join(REPO, ".claude/agents")

POLICY_PATH = os.path.join(REPO, "profile-al-dev-shared/knowledge/agent-tool-projection-policy.md")
STRUCTURE_LENS = os.path.join(AGENTS_DIR, "quality-agent-lens-structure.md")


def _canonical_tools_from_lens(path: str):
    """Extract the backtick-quoted tokens between the canonical-tools markers."""
    text = open(path).read()
    block = re.search(
        r"<!-- canonical-tools:start -->(.*?)<!-- canonical-tools:end -->",
        text,
        re.DOTALL,
    )
    if not block:
        return None
    return set(re.findall(r"`([^`]+)`", block.group(1)))


def _policy_source_tokens(path: str):
    """Return the projection_rules.claude capability keys from the policy."""
    m = re.match(r"^---\n(.*?)\n---", open(path).read(), re.DOTALL)
    if not m:
        raise ValueError(f"No YAML frontmatter found in {path}")
    data = yaml.safe_load(m.group(1))
    return set(data["projection_rules"]["claude"].keys())


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
    "design-skill-lens-surface-placement",
    "naming-convention-lens",
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

    # sonnet exceptions: shared-backbone (multi-file synthesis), handoff-gaps (chain tracing), model-fit (multi-file evaluative analysis), complexity (multi-file phase-count ranking + Atomise/Absorb synthesis), near-duplicates (multi-file comparative synthesis with multi-criterion judgement)
    SONNET_AGENTS = {"design-skill-lens-shared-backbone", "design-skill-lens-handoff-gaps", "design-agent-lens-model-fit", "design-skill-lens-complexity", "design-skill-lens-near-duplicates"}
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

lens_tokens = _canonical_tools_from_lens(STRUCTURE_LENS)
policy_tokens = _policy_source_tokens(POLICY_PATH)
if lens_tokens is None:
    failures.append(_format_failure(
        STRUCTURE_LENS,
        "lens-canonical-markers",
        "could not find <!-- canonical-tools:start/end --> markers",
        "wrap the canonical tool list in canonical-tools:start/end HTML comments",
    ))
elif lens_tokens != policy_tokens:
    missing = policy_tokens - lens_tokens
    extra = lens_tokens - policy_tokens
    failures.append(_format_failure(
        STRUCTURE_LENS,
        "lens-policy-sync",
        f"canonical tool list diverges from projection policy "
        f"(missing from lens: {sorted(missing)}; extra in lens: {sorted(extra)})",
        "reconcile the structure lens canonical-tools list with "
        "projection_rules.claude keys in agent-tool-projection-policy.md",
    ))

if failures:
    print(f"FAIL — {len(failures)} issue(s):\n")
    print("\n\n".join(failures))
    sys.exit(1)
else:
    print(f"PASS — {len(EXPECTED_AGENTS)} agents valid, {len(SKILLS_TO_CHECK)} dispatch skill(s) checked.")
