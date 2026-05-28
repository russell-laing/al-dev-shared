#!/usr/bin/env python3
"""Validate that authored shared-surface docs stay harness-neutral."""

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
import re
import sys

SCAN_DIRS = ("skills", "agents", "knowledge", "markdown", "bc-code-intel-knowledge")
SCAN_SUFFIXES = {".md", ".yaml", ".yml"}
ALLOWLIST = {
    "knowledge/harness-concepts.md",
    "knowledge/agent-tool-projection-policy.md",
}
FORBIDDEN_PATTERNS = {
    "Open Claude Code": re.compile(r"\bOpen Claude Code\b", re.IGNORECASE),
    "Restart Claude Code": re.compile(r"\bRestart Claude Code\b", re.IGNORECASE),
    "Copilot session wording": re.compile(r"\bstart a new Copilot CLI session\b", re.IGNORECASE),
    "Claude tool token": re.compile(r"\bAskUserQuestion\b"),
    "Copilot tool token": re.compile(r"\bask_user\b"),
    "Claude dispatch token": re.compile(r"\bsubagent_type\b"),
    "Copilot dispatch token": re.compile(
        r"""\bagent_type:\s*(?:['"][^'"\n]+['"]|[^\s#][^\n#]*)"""
    ),
    "Claude MCP token": re.compile(r"\bmcp__plugin_profile-claude\b"),
    "Claude settings path": re.compile(r"~/\.claude\b"),
    "Copilot settings path": re.compile(r"~/\.copilot\b"),
}


@dataclass(frozen=True)
class Finding:
    path: str
    rule: str
    excerpt: str


_RULE_FIX: dict[str, str] = {
    "Open Claude Code": (
        'replace "Open Claude Code" with "open the harness" or '
        "move the line to .claude/ if it must be harness-specific"
    ),
    "Restart Claude Code": (
        'replace "Restart Claude Code" with "restart the session" or '
        "move the line to .claude/ if it must be harness-specific"
    ),
    "Copilot session wording": (
        "replace with generic session-restart phrasing; "
        "see knowledge/harness-concepts.md for neutral equivalents"
    ),
    "Claude tool token": (
        'replace "AskUserQuestion" with the generic tool name from knowledge/harness-concepts.md'
    ),
    "Copilot tool token": (
        'replace "ask_user" with the generic tool name from knowledge/harness-concepts.md'
    ),
    "Claude dispatch token": (
        'replace "subagent_type" with the generic agent dispatch syntax from knowledge/harness-concepts.md'
    ),
    "Copilot dispatch token": (
        "replace the agent_type: dispatch syntax with the generic equivalent "
        "from knowledge/harness-concepts.md"
    ),
    "Claude MCP token": (
        'replace "mcp__plugin_profile-claude" with the generic identifier '
        "from knowledge/harness-concepts.md"
    ),
    "Claude settings path": (
        'remove "~/.claude" or move the reference to .claude/ '
        "so it does not appear in the shared authored surface"
    ),
    "Copilot settings path": (
        'remove "~/.copilot" or move the reference to a harness-specific location'
    ),
    "Unreadable file": (
        "check file encoding (must be UTF-8) or fix file permissions"
    ),
}


def _format_finding(f: Finding) -> str:
    fix = _RULE_FIX.get(
        f.rule,
        "replace with generic vocabulary from knowledge/harness-concepts.md",
    )
    return (
        f"{f.path}\n"
        f"  rule: neutrality-violation\n"
        f"  issue: forbidden harness token ({f.rule!r}); matched text: {f.excerpt!r}\n"
        f"  fix: {fix}"
    )


def iter_markdown_files(plugin_root: Path):
    """Yield markdown and yaml files from shared authored directories."""
    for directory in SCAN_DIRS:
        base = plugin_root / directory
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in SCAN_SUFFIXES:
                yield path


def should_skip(relative_path: str) -> bool:
    """Return True for files intentionally outside neutrality enforcement."""
    return relative_path in ALLOWLIST


def scan_paths(plugin_root: Path) -> list[Finding]:
    """Scan the plugin root for harness-specific tokens in shared content."""
    findings: list[Finding] = []

    for path in iter_markdown_files(plugin_root):
        relative_path = path.relative_to(plugin_root).as_posix()
        if should_skip(relative_path):
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            findings.append(Finding(relative_path, "Unreadable file", exc.__class__.__name__))
            continue

        for rule, pattern in FORBIDDEN_PATTERNS.items():
            match = pattern.search(text)
            if match:
                findings.append(Finding(relative_path, rule, match.group(0)))

    return findings


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    plugin_root = Path(args[0]) if args else Path("profile-al-dev-shared")
    findings = scan_paths(plugin_root)

    if not findings:
        print("PASS: no harness-specific leakage in shared authored surface")
        return 0

    blocks = "\n\n".join(_format_finding(f) for f in findings)
    print(blocks)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
