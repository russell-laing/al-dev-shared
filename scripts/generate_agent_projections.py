#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _entrypoint_bootstrap import bootstrap_repo

REPO_ROOT = bootstrap_repo(__file__)

from scripts.al_dev_tools.markdown_frontmatter import parse_required_frontmatter
from scripts.al_dev_tools.io_utils import write_text_atomic


def load_projection_policy(policy_path: Path) -> dict:
    """Load the projection table from the policy frontmatter.

    claude/copilot capabilities map to a flat tool-name string (the `tool`
    key); codex capabilities keep their dict form (`developer_instruction`
    or `native_capability`), matching what the render functions expect.
    """
    data, _body = parse_required_frontmatter(policy_path.read_text(encoding="utf-8"))
    rules = data.get("projection_rules")
    if not rules:
        raise ValueError(f"Projection policy {policy_path} has no projection_rules")
    policy: dict = {}
    for harness, capabilities in rules.items():
        policy[harness] = {}
        for capability, mapping in capabilities.items():
            if "tool" in mapping:
                policy[harness][capability] = mapping["tool"]
            else:
                policy[harness][capability] = dict(mapping)
    return policy


def default_projection_policy() -> dict:
    """Load the repository-default agent tool projection policy."""
    return load_projection_policy(
        REPO_ROOT / "profile-al-dev-shared/knowledge/agent-tool-projection-policy.md"
    )


def render_generated_agents_readme() -> str:
    return """# Generated Agent Projections

This directory contains generated harness-native agent artifacts.

- `claude/` contains generated Claude Markdown manifests (`*.md`).
- `copilot/` contains generated Copilot Markdown manifests (`*.md`).
- `codex/` contains generated Codex TOML manifests (`*.toml`).

These files are derived from `profile-al-dev-shared/agents/*.md` and
`profile-al-dev-shared/knowledge/agent-tool-projection-policy.md`.

Do not hand-edit files in this directory. Edit the shared agent source or
projection policy instead, then regenerate with:

```bash
python3 scripts/generate_agent_projections.py
```
"""


def _project_tools(shared_tools: list[str], mapping: dict[str, Any]) -> list[Any]:
    projected: list[object] = []
    for tool in shared_tools:
        if tool not in mapping:
            raise ValueError(f"Unsupported shared tool mapping: {tool}")
        projected.append(mapping[tool])
    return projected


def render_claude_projection(agent: dict, policy: dict) -> str:
    tools = _project_tools(agent["tools"], policy["claude"])
    tools_line = f"tools: {json.dumps(tools)}\n" if tools else ""
    return (
        "---\n"
        f'description: "{agent["description"]}"\n'
        f"{tools_line}"
        "---\n\n"
        f'{agent["body"]}'
    )


def render_copilot_projection(agent: dict, policy: dict) -> str:
    tools = _project_tools(agent["tools"], policy["copilot"])
    tools_line = f"tools: {json.dumps(tools)}\n" if tools else ""
    return (
        "---\n"
        f'name: "{agent["name"]}"\n'
        f'description: "{agent["description"]}"\n'
        f"{tools_line}"
        "---\n\n"
        f'{agent["body"]}'
    )


def render_codex_projection(agent: dict, policy: dict) -> str:
    codex_rules = _project_tools(agent["tools"], policy["codex"])
    instructions = agent["body"].rstrip().replace('"""', '\\"\\"\\"')
    capability_lines = [
        f"- {rule['developer_instruction']}" if "developer_instruction" in rule
        else f"- {rule['native_capability']}"
        for rule in codex_rules
    ]
    capability_block = "\n".join(capability_lines)
    return (
        f'name = "{agent["name"]}"\n'
        f'description = "{agent["description"]}"\n'
        'developer_instructions = """'
        f"{instructions}\n\nCodex capability notes:\n{capability_block}"
        '"""\n'
    )


def _normalize_agent(path: Path, data: dict[str, Any], body: str) -> dict[str, Any]:
    name = str(data.get("name", path.stem)).strip() or path.stem
    description = str(data.get("description", path.stem)).strip() or path.stem
    tools = data.get("tools", [])
    if not isinstance(tools, list) or any(not isinstance(tool, str) for tool in tools):
        raise ValueError(f"{path}: tools must be a list of strings")
    return {
        "name": name,
        "description": description,
        "tools": tools,
        "body": body,
    }


def load_agent(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return {
            "name": path.stem,
            "description": path.stem,
            "tools": [],
            "body": "",
        }
    if not text.startswith("---\n"):
        return {
            "name": path.stem,
            "description": path.stem,
            "tools": [],
            "body": text,
        }
    data, body = parse_required_frontmatter(text)
    return _normalize_agent(path, data, body)


def write_projection_set(output_root: Path, agent: dict, policy: dict) -> None:
    (output_root / "claude").mkdir(parents=True, exist_ok=True)
    (output_root / "copilot").mkdir(parents=True, exist_ok=True)
    (output_root / "codex").mkdir(parents=True, exist_ok=True)
    write_text_atomic(output_root / "claude" / f'{agent["name"]}.md', render_claude_projection(agent, policy))
    write_text_atomic(output_root / "copilot" / f'{agent["name"]}.md', render_copilot_projection(agent, policy))
    write_text_atomic(output_root / "codex" / f'{agent["name"]}.toml', render_codex_projection(agent, policy))


def write_all_projections(output_root: Path, agents: list[dict], policy: dict) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    write_text_atomic(output_root / "README.md", render_generated_agents_readme())

    # Compute desired filenames per harness before writing
    desired_claude = {f'{a["name"]}.md' for a in agents}
    desired_copilot = {f'{a["name"]}.md' for a in agents}
    desired_codex = {f'{a["name"]}.toml' for a in agents}

    # Remove orphaned projection files (agent renamed or deleted since last run)
    # Only delete if we found agents to keep (guard against empty glob due to wrong cwd)
    # Always clean up orphaned projections, even if no agents to generate (fail-open guard)
    if not (desired_claude or desired_copilot or desired_codex):
        import sys
        print("⚠ No agents to project — cleaning up all generated outputs", file=sys.stderr)
    for fname in (output_root / "claude").glob("*.md"):
        if fname.name not in desired_claude:
            fname.unlink()
    for fname in (output_root / "copilot").glob("*.md"):
        if fname.name not in desired_copilot:
            fname.unlink()
    for fname in (output_root / "codex").glob("*.toml"):
        if fname.name not in desired_codex:
            fname.unlink()

    for agent in agents:
        write_projection_set(output_root, agent, policy)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents-root", default="profile-al-dev-shared/agents")
    parser.add_argument("--output-root", default="profile-al-dev-shared/generated/agents")
    parser.add_argument(
        "--policy-path",
        default="profile-al-dev-shared/knowledge/agent-tool-projection-policy.md",
    )
    args = parser.parse_args()

    agents_root = Path(args.agents_root)
    if not agents_root.is_absolute():
        agents_root = REPO_ROOT / agents_root
    if not agents_root.exists():
        raise ValueError(f"agents_root not found: {agents_root}")
    output_root = Path(args.output_root)
    if not output_root.is_absolute():
        output_root = REPO_ROOT / output_root
    policy_path = Path(args.policy_path)
    if not policy_path.is_absolute():
        policy_path = REPO_ROOT / policy_path
    if not policy_path.exists():
        raise ValueError(f"policy_path not found: {policy_path}")
    policy = load_projection_policy(policy_path)
    agents = [load_agent(path) for path in sorted(agents_root.glob("*.md"))]
    write_all_projections(output_root, agents, policy)


if __name__ == "__main__":
    main()
