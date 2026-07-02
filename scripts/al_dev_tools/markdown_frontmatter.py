from __future__ import annotations

from typing import Any
import re

import yaml


# Tolerate CRLF (\r\n) as well as LF: Windows-authored SKILL.md/agent files
# would otherwise silently fail to parse in every downstream validator.
_FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", re.DOTALL)
_HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*$")


def _coerce_mapping(raw: Any) -> dict[str, Any]:
    data = raw or {}
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data


def _parse_frontmatter(text: str, *, required: bool) -> tuple[dict[str, Any], str]:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        if required:
            raise ValueError("missing or malformed frontmatter")
        return {}, text
    try:
        return _coerce_mapping(yaml.safe_load(match.group(1))), match.group(2)
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML frontmatter: {exc}") from exc


def parse_required_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    return _parse_frontmatter(text, required=True)


def parse_optional_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    return _parse_frontmatter(text, required=False)


def find_markdown_heading(text: str, heading: str) -> bool:
    target = heading.strip()
    # Strip ALL leading '#' so a caller passing "## Output Format" matches a
    # heading at any level, which is the point of the level-insensitive compare.
    target = target.lstrip("#").strip()
    fence_char = None

    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```"):
            if fence_char == "`":
                fence_char = None
            elif not fence_char:
                fence_char = "`"
            continue
        if stripped.startswith("~~~"):
            if fence_char == "~":
                fence_char = None
            elif not fence_char:
                fence_char = "~"
            continue
        if fence_char or stripped.startswith(">"):
            continue
        match = _HEADING_RE.match(line)
        if not match:
            continue
        candidate = match.group(1).strip()
        if candidate == target:
            return True
        if line.strip() == heading.strip():
            return True

    return False
