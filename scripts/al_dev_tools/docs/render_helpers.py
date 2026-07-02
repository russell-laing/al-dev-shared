"""Shared helper functions for documentation rendering."""

from typing import Iterable


def mermaid_block(lines: Iterable[str]) -> str:
    """Wrap lines in a mermaid code block."""
    return "```mermaid\n" + "\n".join(lines).rstrip() + "\n```"


def wrap_generated_section(key: str, body: str) -> str:
    """Wrap content in a generated section marker for safe update operations."""
    return f"<!-- BEGIN GENERATED: {key} -->\n{body.rstrip()}\n<!-- END GENERATED: {key} -->"
