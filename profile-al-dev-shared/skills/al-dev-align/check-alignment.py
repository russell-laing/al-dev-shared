#!/usr/bin/env python3
"""check-alignment.py — AL Dev Shared alignment auditor.

Usage:
    python3 check-alignment.py [--mode advisory|enforce]
                               [--claude-profile PATH]
                               [--copilot-profile PATH]

Exit codes:
    0 — All checks passed
    1 — Alignment issues found (enforce mode only)
    2 — Configuration / parse / runtime error
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

HARDCODED_TOKENS = {
    "~/.claude",
    "~/claude-configs",
    "~/.copilot",
    "~/copilot-configs",
    "CLAUDE_CODE",
}

SCAN_PATTERNS = ["skills/*/SKILL.md", "agents/*.md", "knowledge/*.md"]
EXCLUDED_RELPATHS = {"knowledge/harness-concepts.md"}


def _extract_token(cell: str) -> str | None:
    """Normalise a vocabulary table cell into a scannable token string."""
    s = cell.strip()
    s = s.replace("`", "")
    s = re.sub(r"\*\*", "", s)
    # Strip curly and straight quote characters
    s = s.replace("\u201c", "").replace("\u201d", "").replace('"', "")
    # Strip trailing context suffixes (order matters: longest first)
    for suffix in (" in task tool", " tool"):
        if s.endswith(suffix):
            s = s[: -len(suffix)]
            break
    # Strip anything after " in " (e.g., remaining context annotations)
    if " in " in s:
        s = s[: s.index(" in ")]
    # Extract prefix before template placeholder
    if "<" in s:
        s = s[: s.index("<")]
    s = s.strip()
    return s if len(s) >= 2 else None


def parse_forbidden_tokens(harness_concepts_text: str) -> set[str]:
    """Derive forbidden tokens from the vocabulary table in harness-concepts.md.

    Reads columns 3 (Claude Code) and 4 (Copilot CLI) of the vocabulary table,
    normalises each cell, and merges with HARDCODED_TOKENS.
    """
    tokens: set[str] = set(HARDCODED_TOKENS)
    in_table = False
    header_passed = False

    for line in harness_concepts_text.splitlines():
        stripped = line.strip()
        if "| Concept |" in stripped and "Description" in stripped:
            in_table = True
            header_passed = False
            continue
        if not in_table:
            continue
        if stripped.startswith("|---") or stripped.startswith("| ---"):
            header_passed = True
            continue
        if not stripped.startswith("|"):
            in_table = False
            continue
        if not header_passed:
            continue
        # Row format: | Concept | Description | Claude Code | Copilot CLI |
        parts = [p.strip() for p in stripped.split("|")]
        # parts[0]='', parts[1]=Concept, parts[2]=Desc, parts[3]=Claude, parts[4]=Copilot
        for col_idx in (3, 4):
            if col_idx < len(parts):
                token = _extract_token(parts[col_idx])
                if token:
                    tokens.add(token)

    return tokens


def strip_frontmatter(lines: list[str]) -> list[str]:
    """Replace frontmatter lines with blank strings, preserving line count.

    A file has frontmatter only if its first line is exactly '---' and a
    matching closing '---' line exists. If no closing delimiter is found,
    the file is treated as having no frontmatter and returned unchanged.
    """
    if not lines or lines[0].rstrip("\n") != "---":
        return lines
    result: list[str] = [""]  # replace opening ---
    i = 1
    found_close = False
    while i < len(lines):
        if lines[i].rstrip("\n") == "---":
            result.append("")  # replace closing ---
            i += 1
            found_close = True
            break
        result.append("")
        i += 1
    if not found_close:
        return lines  # no closing delimiter — treat as no frontmatter
    result.extend(lines[i:])
    return result


def is_in_code_fence(line_idx: int, lines: list[str]) -> bool:
    """Return True if line_idx falls inside an open ``` fence."""
    in_fence = False
    for i in range(line_idx):
        if lines[i].strip().startswith("```"):
            in_fence = not in_fence
    return in_fence


def classify_hit(line_idx: int, lines: list[str]) -> dict:
    """Classify a token hit by context type, severity, and autofixability."""
    line = lines[line_idx]
    if is_in_code_fence(line_idx, lines) or line.startswith("    "):
        return {"context_type": "code_block", "autofixable": False, "severity": "warning"}
    line_lower = line.lower()
    if any(kw in line_lower for kw in ["never", "do not", "must not", "don't"]):
        return {
            "context_type": "prohibition_rule",
            "autofixable": False,
            "severity": "manual_review",
        }
    return {"context_type": "prose", "autofixable": True, "severity": "error"}


def scan_file(rel_path: str, raw_lines: list[str], forbidden_tokens: set[str]) -> list[dict]:
    """Scan a file's body for forbidden tokens and return classified hits."""
    body = strip_frontmatter(raw_lines)
    hits: list[dict] = []
    for i, raw_line in enumerate(body):
        line_text = raw_line.rstrip("\n")
        for token in forbidden_tokens:
            if not token or token not in line_text:
                continue
            classification = classify_hit(i, body)
            pos = line_text.find(token)
            start = max(0, pos - 20)
            end = min(len(line_text), pos + len(token) + 20)
            hits.append(
                {
                    "file": rel_path,
                    "line": i + 1,
                    "token": token,
                    "context": line_text[start:end],
                    **classification,
                }
            )
    return hits


if __name__ == "__main__":
    print("{}")
