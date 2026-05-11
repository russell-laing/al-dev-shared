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


def _iter_vocabulary_table_rows(text: str):
    """Yield parsed column lists for each data row in the vocabulary table."""
    in_table = False
    header_passed = False
    for line in text.splitlines():
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
        yield [p.strip() for p in stripped.split("|")]


def parse_forbidden_tokens(harness_concepts_text: str) -> set[str]:
    """Derive forbidden tokens from the vocabulary table in harness-concepts.md.

    Reads columns 3 (Claude Code) and 4 (Copilot CLI) of the vocabulary table,
    normalises each cell, and merges with HARDCODED_TOKENS.
    """
    tokens: set[str] = set(HARDCODED_TOKENS)
    for parts in _iter_vocabulary_table_rows(harness_concepts_text):
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
    """Return True if line_idx falls inside an open ``` or ~~~ fence."""
    in_fence = False
    for i in range(line_idx):
        stripped = lines[i].strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
    return in_fence


def classify_hit(line_idx: int, lines: list[str]) -> dict:
    """Classify a token hit by context type, severity, and autofixability."""
    line = lines[line_idx]
    if is_in_code_fence(line_idx, lines) or line.startswith("    "):
        return {"context_type": "code_block", "autofixable": False, "severity": "warning"}
    line_lower = line.lower()
    if any(kw in line_lower for kw in ["never", "do not", "must not", "don't", "don\u2019t"]):
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


def parse_concepts_from_harness_md(text: str) -> set[str]:
    """Extract concept names (column 1) from the vocabulary table in harness-concepts.md."""
    concepts: set[str] = set()
    for parts in _iter_vocabulary_table_rows(text):
        if len(parts) >= 2:
            concept = re.sub(r"\*\*", "", parts[1]).strip()
            if concept:
                concepts.add(concept)
    return concepts


def parse_mapping_table(text: str) -> set[str]:
    """Parse concept names from the '## Harness Mapping' table in CLAUDE.md / AGENTS.md."""
    concepts: set[str] = set()
    in_section = False
    for line in text.splitlines():
        if line.startswith("## Harness Mapping"):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if stripped.startswith("|---") or stripped.startswith("| ---"):
            continue
        parts = [p.strip() for p in stripped.split("|")]
        if len(parts) >= 2:
            concept = re.sub(r"\*\*", "", parts[1])
            concept = re.sub(r"`", "", concept).strip()
            if concept and concept.lower() != "concept":
                concepts.add(concept)
    return concepts


def compute_coverage_gaps(
    concepts: set[str],
    claude_mapping: set[str],
    copilot_mapping: set[str],
) -> tuple[list[dict], list[dict]]:
    """Return (missing, orphaned) coverage gap lists."""
    missing: list[dict] = []
    for concept in sorted(concepts):
        missing_in = []
        if concept not in claude_mapping:
            missing_in.append("claude")
        if concept not in copilot_mapping:
            missing_in.append("copilot")
        if missing_in:
            missing.append({"concept": concept, "missing_in": missing_in})

    orphaned: list[dict] = []
    for concept in sorted((claude_mapping | copilot_mapping) - concepts):
        present_in = []
        if concept in claude_mapping:
            present_in.append("claude")
        if concept in copilot_mapping:
            present_in.append("copilot")
        orphaned.append({"concept": concept, "present_in": present_in})

    return missing, orphaned


def find_scan_files(plugin_root: Path) -> list[tuple[Path, str]]:
    """Return (absolute_path, relative_path) pairs for all files to scan."""
    results: list[tuple[Path, str]] = []
    for pattern in SCAN_PATTERNS:
        for filepath in plugin_root.glob(pattern):
            rel = filepath.relative_to(plugin_root).as_posix()
            if rel not in EXCLUDED_RELPATHS:
                results.append((filepath, rel))
    return results


def run_checks(
    plugin_root: Path,
    claude_profile: Path,
    copilot_profile: Path,
) -> dict:
    """Run all alignment checks and return the result dict."""
    harness_concepts_path = plugin_root / "knowledge" / "harness-concepts.md"
    if not harness_concepts_path.exists():
        raise FileNotFoundError(
            f"harness-concepts.md not found at {harness_concepts_path}"
        )

    harness_text = harness_concepts_path.read_text(encoding="utf-8")
    forbidden_tokens = parse_forbidden_tokens(harness_text)
    concepts = parse_concepts_from_harness_md(harness_text)

    all_hits: list[dict] = []
    for filepath, rel in find_scan_files(plugin_root):
        raw_lines = filepath.read_text(encoding="utf-8").splitlines(keepends=True)
        all_hits.extend(scan_file(rel, raw_lines, forbidden_tokens))

    claude_md = claude_profile / "CLAUDE.md"
    agents_md = copilot_profile / "AGENTS.md"
    claude_mapping = (
        parse_mapping_table(claude_md.read_text(encoding="utf-8"))
        if claude_md.exists()
        else set()
    )
    copilot_mapping = (
        parse_mapping_table(agents_md.read_text(encoding="utf-8"))
        if agents_md.exists()
        else set()
    )

    missing, orphaned = compute_coverage_gaps(concepts, claude_mapping, copilot_mapping)

    return {
        "forbidden_tokens": all_hits,
        "missing_mappings": missing,
        "orphaned_mappings": orphaned,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check alignment between al-dev-shared and harness profile repos."
    )
    parser.add_argument(
        "--mode",
        choices=["advisory", "enforce"],
        default="enforce",
        help="advisory exits 0 even with issues; enforce exits 1 on issues.",
    )
    parser.add_argument(
        "--claude-profile",
        default=str(Path.home() / "claude-configs" / "profile-claude-al-dev"),
        metavar="PATH",
    )
    parser.add_argument(
        "--copilot-profile",
        default=str(Path.home() / "copilot-configs" / "profile-copilot-al-dev"),
        metavar="PATH",
    )
    args = parser.parse_args()

    env_root = os.environ.get("AL_DEV_SHARED_PLUGIN_ROOT", "").strip()
    if env_root:
        plugin_root = Path(env_root).expanduser().resolve()
    else:
        # Script is at skills/al-dev-align/check-alignment.py inside plugin root
        plugin_root = Path(__file__).resolve().parent.parent.parent

    claude_profile = Path(args.claude_profile).expanduser().resolve()
    copilot_profile = Path(args.copilot_profile).expanduser().resolve()

    try:
        result = run_checks(plugin_root, claude_profile, copilot_profile)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"error": str(exc)}, indent=2))
        sys.exit(2)

    print(json.dumps(result, indent=2))

    has_issues = bool(
        result["forbidden_tokens"]
        or result["missing_mappings"]
        or result["orphaned_mappings"]
    )
    if has_issues and args.mode == "enforce":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
