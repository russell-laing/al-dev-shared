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

    for finding in findings:
        print(f"{finding.path}: {finding.rule}: {finding.excerpt}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
