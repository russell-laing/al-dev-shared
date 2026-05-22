#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path


def default_projection_policy() -> dict:
    return {
        "claude": {
            "USER_GATE": "AskUserQuestion",
            "Read": "Read",
            "Write": "Write",
            "Edit": "Edit",
            "Glob": "Glob",
            "Grep": "Grep",
            "Bash": "Bash",
            "MCP: al-mcp-server": "mcp__plugin_profile-claude-al-dev_al-mcp-server__<tool>",
            "MCP: bc-code-intelligence": "mcp__plugin_profile-claude-al-dev_bc-code-intelligence-mcp__<tool>",
            "MCP: microsoft-docs": "mcp__plugin_profile-claude-al-dev_microsoft_docs_mcp__<tool>",
        },
        "copilot": {
            "USER_GATE": "ask_user",
            "Read": "read",
            "Write": "edit",
            "Edit": "edit",
            "Glob": "glob",
            "Grep": "grep",
            "Bash": "execute",
            "MCP: al-mcp-server": "al-mcp-server-<tool>",
            "MCP: bc-code-intelligence": "bc-code-intelligence-mcp-<tool>",
            "MCP: microsoft-docs": "microsoft_docs_mcp-<tool>",
        },
        "codex": {
            "USER_GATE": {"developer_instruction": "request_user_input"},
            "Read": {"native_capability": "read files available in the active Codex session"},
            "Write": {"native_capability": "edit files available in the active Codex session"},
            "Edit": {"native_capability": "edit files available in the active Codex session"},
            "Glob": {"native_capability": "search files available in the active Codex session"},
            "Grep": {"native_capability": "search file contents available in the active Codex session"},
            "Bash": {"native_capability": "run shell commands allowed by the active Codex session"},
            "MCP: al-mcp-server": {"native_capability": "use the AL symbol lookup MCP capability available in the active Codex session"},
            "MCP: bc-code-intelligence": {"native_capability": "use the BC code intelligence MCP capability available in the active Codex session"},
            "MCP: microsoft-docs": {"native_capability": "use the Microsoft Docs MCP capability available in the active Codex session"},
        },
    }


def _project_tools(shared_tools: list[str], mapping: dict[str, object]) -> list[object]:
    projected: list[object] = []
    for tool in shared_tools:
        if tool not in mapping:
            raise ValueError(f"Unsupported shared tool mapping: {tool}")
        projected.append(mapping[tool])
    return projected


def render_claude_projection(agent: dict, policy: dict) -> str:
    tools = _project_tools(agent["tools"], policy["claude"])
    return (
        "---\n"
        f'description: "{agent["description"]}"\n'
        f"tools: {json.dumps(tools)}\n"
        "---\n\n"
        f'{agent["body"]}'
    )


def render_copilot_projection(agent: dict, policy: dict) -> str:
    tools = _project_tools(agent["tools"], policy["copilot"])
    return (
        "---\n"
        f'name: "{agent["name"]}"\n'
        f'description: "{agent["description"]}"\n'
        f"tools: {json.dumps(tools)}\n"
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


def _extract_frontmatter(text: str) -> tuple[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError("Agent file is missing YAML frontmatter")
    return match.group(1), match.group(2)


def _extract_name(frontmatter: str, path: Path) -> str:
    match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    if match:
        return match.group(1).strip().strip('"')
    return path.stem


def _extract_description(frontmatter: str) -> str:
    block_match = re.search(r"^description:\s*>-\s*\n((?:[ \t].*\n?)*)", frontmatter, re.MULTILINE)
    if block_match and block_match.group(1).strip():
        lines = [line.strip() for line in block_match.group(1).splitlines() if line.strip()]
        return " ".join(lines)
    inline_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if inline_match:
        return inline_match.group(1).strip().strip('"')
    raise ValueError("Agent frontmatter is missing description")


def _extract_tools(frontmatter: str) -> list[str]:
    match = re.search(r"^tools:\s*(\[[\s\S]*?\])", frontmatter, re.MULTILINE)
    if not match:
        return []
    return list(ast.literal_eval(match.group(1)))


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
    frontmatter, body = _extract_frontmatter(text)
    return {
        "name": _extract_name(frontmatter, path),
        "description": _extract_description(frontmatter),
        "tools": _extract_tools(frontmatter),
        "body": body,
    }


def write_projection_set(output_root: Path, agent: dict, policy: dict) -> None:
    (output_root / "claude").mkdir(parents=True, exist_ok=True)
    (output_root / "copilot").mkdir(parents=True, exist_ok=True)
    (output_root / "codex").mkdir(parents=True, exist_ok=True)
    (output_root / "claude" / f'{agent["name"]}.md').write_text(
        render_claude_projection(agent, policy),
        encoding="utf-8",
    )
    (output_root / "copilot" / f'{agent["name"]}.md').write_text(
        render_copilot_projection(agent, policy),
        encoding="utf-8",
    )
    (output_root / "codex" / f'{agent["name"]}.toml').write_text(
        render_codex_projection(agent, policy),
        encoding="utf-8",
    )


def write_all_projections(output_root: Path, agents: list[dict], policy: dict) -> None:
    for agent in sorted(agents, key=lambda item: item["name"]):
        write_projection_set(output_root, agent, policy)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents-root", default="profile-al-dev-shared/agents")
    parser.add_argument("--output-root", default="profile-al-dev-shared/generated/agents")
    args = parser.parse_args()

    agents_root = Path(args.agents_root)
    output_root = Path(args.output_root)
    agents = [load_agent(path) for path in sorted(agents_root.glob("*.md"))]
    write_all_projections(output_root, agents, default_projection_policy())


if __name__ == "__main__":
    main()
