# al-dev-align Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `/al-dev-align` skill — a Python script plus SKILL.md that audits harness-specific token leaks in shared skill/agent/knowledge files and verifies mapping table completeness in both harness profile repos.

**Architecture:** A standalone Python CLI script (`check-alignment.py`) performs all checks and emits structured JSON; SKILL.md is a thin orchestrator that runs the script, presents findings, offers auto-fix via USER_GATE, applies prose fixes using `harness-concepts.md` as a substitution guide, then re-runs to confirm. Two existing skills (al-dev-commit, al-dev-handoff) gain a one-liner advisory check.

**Tech Stack:** Python 3 stdlib only (argparse, json, re, pathlib, glob), pytest for tests, markdown skill files following existing al-dev-shared conventions.

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `profile-al-dev-shared/skills/al-dev-align/SKILL.md` | Skill orchestrator |
| Create | `profile-al-dev-shared/skills/al-dev-align/check-alignment.py` | All audit logic + JSON output |
| Create | `profile-al-dev-shared/skills/al-dev-align/tests/__init__.py` | Empty, makes tests importable |
| Create | `profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py` | Unit + integration tests |
| Modify | `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` | Add advisory alignment check at Step 5.5 |
| Modify | `profile-al-dev-shared/skills/al-dev-handoff/SKILL.md` | Add advisory alignment check before Step 1 |

---

## Task 1: Test scaffold + `strip_frontmatter` + `is_in_code_fence`

**Files:**
- Create: `profile-al-dev-shared/skills/al-dev-align/tests/__init__.py`
- Create: `profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py`
- Create: `profile-al-dev-shared/skills/al-dev-align/check-alignment.py` (initial skeleton)

- [ ] **Step 1: Create the test directory and empty `__init__.py`**

```bash
mkdir -p profile-al-dev-shared/skills/al-dev-align/tests
touch profile-al-dev-shared/skills/al-dev-align/tests/__init__.py
```

- [ ] **Step 2: Write the failing tests for `strip_frontmatter` and `is_in_code_fence`**

Create `profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py`:

```python
"""Tests for check-alignment.py"""
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "check-alignment.py"
spec = importlib.util.spec_from_file_location("check_alignment", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

strip_frontmatter = mod.strip_frontmatter
is_in_code_fence = mod.is_in_code_fence


class TestStripFrontmatter:
    def test_file_with_frontmatter_preserves_line_count(self):
        lines = ["---\n", "name: foo\n", "---\n", "Body line\n"]
        result = strip_frontmatter(lines)
        assert len(result) == 4

    def test_file_with_frontmatter_replaces_fm_lines_with_blank(self):
        lines = ["---\n", "name: foo\n", "---\n", "Body line\n"]
        result = strip_frontmatter(lines)
        assert result[0] == ""
        assert result[1] == ""
        assert result[2] == ""
        assert result[3] == "Body line\n"

    def test_file_without_frontmatter_returns_unchanged(self):
        lines = ["# Title\n", "Some content\n"]
        result = strip_frontmatter(lines)
        assert result == lines

    def test_body_after_frontmatter_is_preserved(self):
        lines = ["---\n", "key: val\n", "---\n", "line1\n", "line2\n"]
        result = strip_frontmatter(lines)
        assert result[3] == "line1\n"
        assert result[4] == "line2\n"

    def test_file_starting_with_dashes_not_frontmatter(self):
        lines = ["-- not frontmatter\n", "body\n"]
        result = strip_frontmatter(lines)
        assert result == lines


class TestIsInCodeFence:
    def test_line_before_fence_is_not_in_fence(self):
        lines = ["normal\n", "```\n", "code\n", "```\n"]
        assert not is_in_code_fence(0, lines)

    def test_line_inside_fence_is_in_fence(self):
        lines = ["normal\n", "```\n", "code\n", "```\n"]
        assert is_in_code_fence(2, lines)

    def test_line_after_closed_fence_is_not_in_fence(self):
        lines = ["```\n", "code\n", "```\n", "normal\n"]
        assert not is_in_code_fence(3, lines)

    def test_second_fence_block(self):
        lines = ["```\n", "code\n", "```\n", "normal\n", "```\n", "more\n", "```\n"]
        assert is_in_code_fence(5, lines)
        assert not is_in_code_fence(3, lines)

    def test_opening_fence_line_itself_is_not_inside(self):
        lines = ["```\n", "code\n", "```\n"]
        assert not is_in_code_fence(0, lines)
```

- [ ] **Step 3: Run tests to verify they fail (module not found)**

```bash
cd /Users/russelllaing/al-dev-shared
python3 -m pytest profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py -v 2>&1 | head -20
```

Expected: error because `check-alignment.py` doesn't exist yet.

- [ ] **Step 4: Create the skeleton `check-alignment.py` with just these two functions**

Create `profile-al-dev-shared/skills/al-dev-align/check-alignment.py`:

```python
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


def strip_frontmatter(lines: list[str]) -> list[str]:
    """Replace frontmatter lines with blank strings, preserving line count.

    A file has frontmatter only if its first line is exactly '---'.
    Frontmatter ends at the next '---' line.
    """
    if not lines or lines[0].rstrip("\n") != "---":
        return lines
    result: list[str] = [""]  # replace opening ---
    i = 1
    while i < len(lines):
        if lines[i].rstrip("\n") == "---":
            result.append("")  # replace closing ---
            i += 1
            break
        result.append("")
        i += 1
    result.extend(lines[i:])
    return result


def is_in_code_fence(line_idx: int, lines: list[str]) -> bool:
    """Return True if line_idx falls inside an open ``` fence."""
    in_fence = False
    for i in range(line_idx):
        if lines[i].strip().startswith("```"):
            in_fence = not in_fence
    return in_fence


if __name__ == "__main__":
    print("{}")
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
python3 -m pytest profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py -v
```

Expected output:
```
test_check_alignment.py::TestStripFrontmatter::test_file_with_frontmatter_preserves_line_count PASSED
test_check_alignment.py::TestStripFrontmatter::test_file_with_frontmatter_replaces_fm_lines_with_blank PASSED
test_check_alignment.py::TestStripFrontmatter::test_file_without_frontmatter_returns_unchanged PASSED
test_check_alignment.py::TestStripFrontmatter::test_body_after_frontmatter_is_preserved PASSED
test_check_alignment.py::TestStripFrontmatter::test_file_starting_with_dashes_not_frontmatter PASSED
test_check_alignment.py::TestIsInCodeFence::test_line_before_fence_is_not_in_fence PASSED
... all PASSED
```

- [ ] **Step 6: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-align/
git commit -m "✨ feat(al-dev-align): scaffold skill, add strip_frontmatter and is_in_code_fence"
```

---

## Task 2: `parse_forbidden_tokens`

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py`
- Modify: `profile-al-dev-shared/skills/al-dev-align/check-alignment.py`

- [ ] **Step 1: Write failing tests for `parse_forbidden_tokens`**

Append to `test_check_alignment.py` (after the existing imports, reload `mod`):

```python
parse_forbidden_tokens = mod.parse_forbidden_tokens

SAMPLE_HARNESS_CONCEPTS = """\
| Concept | Description | Claude Code | Copilot CLI |
|---|---|---|---|
| **project instructions file** | The file | `CLAUDE.md` | `AGENTS.md` |
| **harness settings file** | Settings | `~/.claude/settings.json` | `~/.copilot/settings.json` |
| **USER_GATE** | Blocking gate | `AskUserQuestion` tool | `ask_user` tool |
| **explore agent** | Fast agent | `subagent_type: Explore` | `agent_type: "explore"` in task tool |
| **restart the agent** | New session | "Restart Claude Code" | "start a new Copilot CLI session" |
| **MCP: al-mcp-server** | AL symbols | `mcp__plugin_prefix_al-mcp-server__<tool>` | `al-mcp-server-<tool>` |
"""


class TestParseForbiddenTokens:
    def test_includes_hardcoded_tokens(self):
        tokens = parse_forbidden_tokens(SAMPLE_HARNESS_CONCEPTS)
        assert "~/.claude" in tokens
        assert "~/claude-configs" in tokens
        assert "~/.copilot" in tokens
        assert "~/copilot-configs" in tokens
        assert "CLAUDE_CODE" in tokens

    def test_extracts_claude_md(self):
        tokens = parse_forbidden_tokens(SAMPLE_HARNESS_CONCEPTS)
        assert "CLAUDE.md" in tokens

    def test_extracts_agents_md(self):
        tokens = parse_forbidden_tokens(SAMPLE_HARNESS_CONCEPTS)
        assert "AGENTS.md" in tokens

    def test_extracts_tool_name_without_tool_suffix(self):
        tokens = parse_forbidden_tokens(SAMPLE_HARNESS_CONCEPTS)
        assert "AskUserQuestion" in tokens
        assert "ask_user" in tokens

    def test_strips_in_task_tool_suffix(self):
        tokens = parse_forbidden_tokens(SAMPLE_HARNESS_CONCEPTS)
        # "agent_type: "explore" in task tool" -> "agent_type: explore"
        assert any("agent_type" in t for t in tokens)

    def test_extracts_mcp_prefix_before_angle_bracket(self):
        tokens = parse_forbidden_tokens(SAMPLE_HARNESS_CONCEPTS)
        assert "mcp__plugin_prefix_al-mcp-server__" in tokens

    def test_extracts_copilot_mcp_prefix_before_angle_bracket(self):
        tokens = parse_forbidden_tokens(SAMPLE_HARNESS_CONCEPTS)
        assert "al-mcp-server-" in tokens

    def test_empty_table_returns_only_hardcoded(self):
        tokens = parse_forbidden_tokens("no table here")
        assert tokens == mod.HARDCODED_TOKENS
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
python3 -m pytest profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py::TestParseForbiddenTokens -v 2>&1 | head -20
```

Expected: `AttributeError: module ... has no attribute 'parse_forbidden_tokens'`

- [ ] **Step 3: Implement `_extract_token` and `parse_forbidden_tokens` in `check-alignment.py`**

Add after the constants (before `strip_frontmatter`):

```python
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
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
python3 -m pytest profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-align/
git commit -m "✨ feat(al-dev-align): add parse_forbidden_tokens with dynamic harness-concepts extraction"
```

---

## Task 3: `classify_hit` + `scan_file`

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py`
- Modify: `profile-al-dev-shared/skills/al-dev-align/check-alignment.py`

- [ ] **Step 1: Write failing tests**

Append to `test_check_alignment.py`:

```python
classify_hit = mod.classify_hit
scan_file = mod.scan_file


class TestClassifyHit:
    def test_prose_line_is_error_and_autofixable(self):
        lines = ["Use CLAUDE.md as your guide.\n"]
        result = classify_hit(0, lines)
        assert result["context_type"] == "prose"
        assert result["severity"] == "error"
        assert result["autofixable"] is True

    def test_line_inside_code_fence_is_warning_not_autofixable(self):
        lines = ["```\n", "use CLAUDE.md here\n", "```\n"]
        result = classify_hit(1, lines)
        assert result["context_type"] == "code_block"
        assert result["severity"] == "warning"
        assert result["autofixable"] is False

    def test_indented_line_is_code_block(self):
        lines = ["    CLAUDE.md is set here\n"]
        result = classify_hit(0, lines)
        assert result["context_type"] == "code_block"
        assert result["autofixable"] is False

    def test_prohibition_rule_line(self):
        lines = ["Never use CLAUDE.md directly.\n"]
        result = classify_hit(0, lines)
        assert result["context_type"] == "prohibition_rule"
        assert result["severity"] == "manual_review"
        assert result["autofixable"] is False

    def test_do_not_line(self):
        lines = ["Do not reference CLAUDE.md.\n"]
        result = classify_hit(0, lines)
        assert result["context_type"] == "prohibition_rule"

    def test_must_not_line(self):
        lines = ["You must not use CLAUDE.md.\n"]
        result = classify_hit(0, lines)
        assert result["context_type"] == "prohibition_rule"

    def test_dont_contraction_line(self):
        lines = ["Don't use CLAUDE.md.\n"]
        result = classify_hit(0, lines)
        assert result["context_type"] == "prohibition_rule"


class TestScanFile:
    def test_finds_token_in_prose(self):
        lines = ["---\n", "name: test\n", "---\n", "Open CLAUDE.md to configure.\n"]
        hits = scan_file("skills/foo/SKILL.md", lines, {"CLAUDE.md"})
        assert len(hits) == 1
        assert hits[0]["token"] == "CLAUDE.md"
        assert hits[0]["line"] == 4  # 1-indexed; frontmatter preserved as blanks
        assert hits[0]["file"] == "skills/foo/SKILL.md"

    def test_returns_empty_for_clean_file(self):
        lines = ["---\n", "name: test\n", "---\n", "Use the project instructions file.\n"]
        hits = scan_file("skills/foo/SKILL.md", lines, {"CLAUDE.md"})
        assert hits == []

    def test_hit_in_code_fence_has_warning_severity(self):
        lines = ["```\n", "cp CLAUDE.md dest\n", "```\n"]
        hits = scan_file("agents/foo.md", lines, {"CLAUDE.md"})
        assert len(hits) == 1
        assert hits[0]["severity"] == "warning"
        assert hits[0]["autofixable"] is False

    def test_multiple_tokens_on_same_line_produces_multiple_hits(self):
        lines = ["Use CLAUDE.md and AGENTS.md together.\n"]
        hits = scan_file("skills/x/SKILL.md", lines, {"CLAUDE.md", "AGENTS.md"})
        assert len(hits) == 2

    def test_context_field_contains_token(self):
        lines = ["Open CLAUDE.md now.\n"]
        hits = scan_file("skills/x/SKILL.md", lines, {"CLAUDE.md"})
        assert "CLAUDE.md" in hits[0]["context"]

    def test_context_type_field_is_present(self):
        lines = ["Reference CLAUDE.md here.\n"]
        hits = scan_file("skills/x/SKILL.md", lines, {"CLAUDE.md"})
        assert "context_type" in hits[0]
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
python3 -m pytest profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py::TestClassifyHit profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py::TestScanFile -v 2>&1 | head -20
```

Expected: `AttributeError` for `classify_hit` and `scan_file`.

- [ ] **Step 3: Implement `classify_hit` and `scan_file` in `check-alignment.py`**

Add after `is_in_code_fence`:

```python
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
```

- [ ] **Step 4: Run all tests**

```bash
python3 -m pytest profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-align/
git commit -m "✨ feat(al-dev-align): add classify_hit and scan_file"
```

---

## Task 4: Harness coverage audit — `parse_concepts_from_harness_md`, `parse_mapping_table`, `compute_coverage_gaps`

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py`
- Modify: `profile-al-dev-shared/skills/al-dev-align/check-alignment.py`

- [ ] **Step 1: Write failing tests**

Append to `test_check_alignment.py`:

```python
parse_concepts_from_harness_md = mod.parse_concepts_from_harness_md
parse_mapping_table = mod.parse_mapping_table
compute_coverage_gaps = mod.compute_coverage_gaps

HARNESS_CONCEPTS_FULL = """\
## Generic Concept Vocabulary

| Concept | Description | Claude Code | Copilot CLI |
|---|---|---|---|
| **project instructions file** | File desc | `CLAUDE.md` | `AGENTS.md` |
| **USER_GATE** | Blocking gate | `AskUserQuestion` tool | `ask_user` tool |
| **explore agent** | Fast agent | `subagent_type: Explore` | `agent_type: "explore"` in task tool |
"""

CLAUDE_MD_WITH_MAPPING = """\
# Project Instructions

Some intro text.

## Harness Mapping

| Concept | Claude Code Value |
|---|---|
| **project instructions file** | `CLAUDE.md` |
| **USER_GATE** | `AskUserQuestion` tool |

## Other Section

More content.
"""

AGENTS_MD_WITH_MAPPING = """\
## Harness Mapping

| Concept | Copilot CLI Value |
|---|---|
| **project instructions file** | `AGENTS.md` |

## Next Section
"""


class TestParseConceptsFromHarnessMd:
    def test_extracts_concept_names(self):
        concepts = parse_concepts_from_harness_md(HARNESS_CONCEPTS_FULL)
        assert "project instructions file" in concepts
        assert "USER_GATE" in concepts
        assert "explore agent" in concepts

    def test_strips_bold_markers(self):
        concepts = parse_concepts_from_harness_md(HARNESS_CONCEPTS_FULL)
        assert "**project instructions file**" not in concepts

    def test_returns_empty_set_for_no_table(self):
        concepts = parse_concepts_from_harness_md("No table here.")
        assert concepts == set()


class TestParseMappingTable:
    def test_extracts_concepts_from_harness_mapping_section(self):
        concepts = parse_mapping_table(CLAUDE_MD_WITH_MAPPING)
        assert "project instructions file" in concepts
        assert "USER_GATE" in concepts

    def test_stops_at_next_heading(self):
        concepts = parse_mapping_table(CLAUDE_MD_WITH_MAPPING)
        assert "Other Section" not in concepts

    def test_skips_separator_rows(self):
        concepts = parse_mapping_table(CLAUDE_MD_WITH_MAPPING)
        assert "---" not in concepts

    def test_skips_header_row(self):
        concepts = parse_mapping_table(CLAUDE_MD_WITH_MAPPING)
        assert "Concept" not in concepts

    def test_strips_bold_and_backticks(self):
        concepts = parse_mapping_table(CLAUDE_MD_WITH_MAPPING)
        assert "**project instructions file**" not in concepts

    def test_returns_empty_set_when_no_section(self):
        concepts = parse_mapping_table("# No mapping here\nContent.\n")
        assert concepts == set()


class TestComputeCoverageGaps:
    def test_missing_concept_appears_in_missing_list(self):
        concepts = {"project instructions file", "USER_GATE"}
        claude = {"project instructions file"}
        copilot = {"project instructions file"}
        missing, orphaned = compute_coverage_gaps(concepts, claude, copilot)
        assert any(m["concept"] == "USER_GATE" for m in missing)

    def test_missing_in_field_lists_correct_harnesses(self):
        concepts = {"USER_GATE"}
        claude = set()
        copilot = {"USER_GATE"}
        missing, _ = compute_coverage_gaps(concepts, claude, copilot)
        gap = next(m for m in missing if m["concept"] == "USER_GATE")
        assert gap["missing_in"] == ["claude"]
        assert "copilot" not in gap["missing_in"]

    def test_no_gaps_when_all_covered(self):
        concepts = {"project instructions file"}
        claude = {"project instructions file"}
        copilot = {"project instructions file"}
        missing, orphaned = compute_coverage_gaps(concepts, claude, copilot)
        assert missing == []
        assert orphaned == []

    def test_orphaned_row_not_in_concepts(self):
        concepts = {"USER_GATE"}
        claude = {"USER_GATE", "old concept"}
        copilot = {"USER_GATE"}
        _, orphaned = compute_coverage_gaps(concepts, claude, copilot)
        assert any(o["concept"] == "old concept" for o in orphaned)
        orphan = next(o for o in orphaned if o["concept"] == "old concept")
        assert "claude" in orphan["present_in"]
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
python3 -m pytest profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py::TestParseConceptsFromHarnessMd profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py::TestParseMappingTable profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py::TestComputeCoverageGaps -v 2>&1 | head -20
```

Expected: `AttributeError` for the three functions.

- [ ] **Step 3: Implement the three functions in `check-alignment.py`**

Add after `scan_file`:

```python
def parse_concepts_from_harness_md(text: str) -> set[str]:
    """Extract concept names (column 1) from the vocabulary table in harness-concepts.md."""
    concepts: set[str] = set()
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
        parts = [p.strip() for p in stripped.split("|")]
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
```

- [ ] **Step 4: Run all tests**

```bash
python3 -m pytest profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-align/
git commit -m "✨ feat(al-dev-align): add harness coverage audit functions"
```

---

## Task 5: CLI wrapper — `find_scan_files`, `run_checks`, `main`

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py`
- Modify: `profile-al-dev-shared/skills/al-dev-align/check-alignment.py`

- [ ] **Step 1: Write failing integration tests**

Append to `test_check_alignment.py`:

```python
import json
import subprocess
import tempfile
import textwrap


SCRIPT_PATH = str(SCRIPT)


class TestCLI:
    def _run(self, args: list[str], *, plugin_root: str = "") -> subprocess.CompletedProcess:
        env = os.environ.copy()
        if plugin_root:
            env["AL_DEV_SHARED_PLUGIN_ROOT"] = plugin_root
        return subprocess.run(
            [sys.executable, SCRIPT_PATH, *args],
            capture_output=True,
            text=True,
            env=env,
        )

    def test_exit_2_when_harness_concepts_missing(self, tmp_path):
        result = self._run(
            ["--claude-profile", str(tmp_path), "--copilot-profile", str(tmp_path)],
            plugin_root=str(tmp_path),
        )
        assert result.returncode == 2

    def test_exit_0_when_all_clean(self, tmp_path):
        # Set up a minimal valid plugin root
        skills_dir = tmp_path / "skills" / "test-skill"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text("---\nname: test\n---\nUse the project instructions file.\n")
        (tmp_path / "knowledge").mkdir()
        harness_concepts = (
            "| Concept | Description | Claude Code | Copilot CLI |\n"
            "|---|---|---|---|\n"
            "| **project instructions file** | desc | `CLAUDE.md` | `AGENTS.md` |\n"
        )
        (tmp_path / "knowledge" / "harness-concepts.md").write_text(harness_concepts)
        mapping_table = (
            "## Harness Mapping\n\n"
            "| Concept | Value |\n"
            "|---|---|\n"
            "| **project instructions file** | `CLAUDE.md` |\n\n"
            "## End\n"
        )
        (tmp_path / "CLAUDE.md").write_text(mapping_table)
        (tmp_path / "AGENTS.md").write_text(mapping_table)
        result = self._run(
            ["--claude-profile", str(tmp_path), "--copilot-profile", str(tmp_path)],
            plugin_root=str(tmp_path),
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["forbidden_tokens"] == []
        assert data["missing_mappings"] == []

    def test_exit_1_enforce_when_issues_found(self, tmp_path):
        skills_dir = tmp_path / "skills" / "bad-skill"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text("---\nname: bad\n---\nOpen CLAUDE.md here.\n")
        (tmp_path / "knowledge").mkdir()
        harness_concepts = (
            "| Concept | Description | Claude Code | Copilot CLI |\n"
            "|---|---|---|---|\n"
            "| **project instructions file** | desc | `CLAUDE.md` | `AGENTS.md` |\n"
        )
        (tmp_path / "knowledge" / "harness-concepts.md").write_text(harness_concepts)
        (tmp_path / "CLAUDE.md").write_text("## Harness Mapping\n\n| Concept | Value |\n|---|---|\n| **project instructions file** | x |\n")
        (tmp_path / "AGENTS.md").write_text("## Harness Mapping\n\n| Concept | Value |\n|---|---|\n| **project instructions file** | x |\n")
        result = self._run(
            ["--mode", "enforce", "--claude-profile", str(tmp_path), "--copilot-profile", str(tmp_path)],
            plugin_root=str(tmp_path),
        )
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert len(data["forbidden_tokens"]) >= 1

    def test_exit_0_advisory_even_with_issues(self, tmp_path):
        skills_dir = tmp_path / "skills" / "bad-skill"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text("---\nname: bad\n---\nOpen CLAUDE.md here.\n")
        (tmp_path / "knowledge").mkdir()
        harness_concepts = (
            "| Concept | Description | Claude Code | Copilot CLI |\n"
            "|---|---|---|---|\n"
            "| **project instructions file** | desc | `CLAUDE.md` | `AGENTS.md` |\n"
        )
        (tmp_path / "knowledge" / "harness-concepts.md").write_text(harness_concepts)
        (tmp_path / "CLAUDE.md").write_text("## Harness Mapping\n\n| Concept | Value |\n|---|---|\n| **project instructions file** | x |\n")
        (tmp_path / "AGENTS.md").write_text("## Harness Mapping\n\n| Concept | Value |\n|---|---|\n| **project instructions file** | x |\n")
        result = self._run(
            ["--mode", "advisory", "--claude-profile", str(tmp_path), "--copilot-profile", str(tmp_path)],
            plugin_root=str(tmp_path),
        )
        assert result.returncode == 0

    def test_output_is_valid_json(self, tmp_path):
        (tmp_path / "knowledge").mkdir()
        (tmp_path / "knowledge" / "harness-concepts.md").write_text(
            "| Concept | Description | Claude Code | Copilot CLI |\n|---|---|---|---|\n"
        )
        (tmp_path / "CLAUDE.md").write_text("")
        (tmp_path / "AGENTS.md").write_text("")
        result = self._run(
            ["--claude-profile", str(tmp_path), "--copilot-profile", str(tmp_path)],
            plugin_root=str(tmp_path),
        )
        data = json.loads(result.stdout)
        assert "forbidden_tokens" in data
        assert "missing_mappings" in data
        assert "orphaned_mappings" in data
```

Also add these imports to the top of the test file (needed by the integration tests):

```python
import os
import sys
```

- [ ] **Step 2: Run tests to confirm integration tests fail**

```bash
python3 -m pytest profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py::TestCLI -v 2>&1 | head -30
```

Expected: tests fail because `run_checks` and `main` are not yet implemented.

- [ ] **Step 3: Implement `find_scan_files`, `run_checks`, and `main` in `check-alignment.py`**

Replace the `if __name__ == "__main__": print("{}")` block with:

```python
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
```

- [ ] **Step 4: Run all tests**

```bash
python3 -m pytest profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py -v
```

Expected: all tests pass (including integration tests).

- [ ] **Step 5: Verify the script is executable end-to-end against the real repo**

```bash
AL_DEV_SHARED_PLUGIN_ROOT=/Users/russelllaing/al-dev-shared/profile-al-dev-shared \
  python3 profile-al-dev-shared/skills/al-dev-align/check-alignment.py \
  --mode advisory 2>&1 | python3 -m json.tool | head -40
```

Expected: valid JSON output (may have issues — that's fine, advisory mode exits 0).

- [ ] **Step 6: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-align/
git commit -m "✨ feat(al-dev-align): add find_scan_files, run_checks, main CLI"
```

---

## Task 6: Write SKILL.md

**Files:**
- Create: `profile-al-dev-shared/skills/al-dev-align/SKILL.md`

- [ ] **Step 1: Write failing test to verify SKILL.md exists and has required frontmatter**

Append to `test_check_alignment.py`:

```python
class TestSkillFile:
    SKILL_MD = Path(__file__).parent.parent / "SKILL.md"

    def test_skill_md_exists(self):
        assert self.SKILL_MD.exists(), "SKILL.md must exist"

    def test_skill_md_has_name_frontmatter(self):
        text = self.SKILL_MD.read_text()
        assert "name: al-dev-align" in text

    def test_skill_md_has_description(self):
        text = self.SKILL_MD.read_text()
        assert "description:" in text
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
python3 -m pytest profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py::TestSkillFile -v
```

Expected: `SKILL.md must exist` assertion failure.

- [ ] **Step 3: Create SKILL.md**

> **Important:** The scanner audits `skills/*/SKILL.md`, so this file's body must use only generic concept names — no harness-specific tokens.

Create `profile-al-dev-shared/skills/al-dev-align/SKILL.md`:

```markdown
---
name: al-dev-align
description: >-
  Check alignment between al-dev-shared and harness repos. Audits for forbidden
  harness-specific tokens in shared skill/agent bodies and verifies harness
  mapping tables are complete. Run after changes to al-dev-shared or harness profiles.
argument-hint: ""
---

# Skill: /al-dev-align

Audit alignment between `al-dev-shared` and the two harness profile repos.
Checks for forbidden harness-specific tokens in shared files, and verifies
the Harness Mapping tables are complete in both harness profile instruction files.

---

## Step 1 — Locate and run the script

```bash
SCRIPT="$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-align/check-alignment.py"
if [ ! -f "$SCRIPT" ]; then
  echo "Script not found at $SCRIPT — is AL_DEV_SHARED_PLUGIN_ROOT set?"
  exit 1
fi
python3 "$SCRIPT" --mode enforce
ALIGN_EXIT=$?
```

Capture the JSON output and exit code.

---

## Step 2 — Handle exit 0 (clean)

If `ALIGN_EXIT` is 0:

```
All checks passed — no forbidden tokens or mapping gaps found.
```

Stop.

---

## Step 3 — Handle exit 2 (runtime error)

If `ALIGN_EXIT` is 2:

Report the `"error"` field from the JSON output:

```
Alignment check failed with a configuration error:
  [error message from JSON]

Possible causes:
- AL_DEV_SHARED_PLUGIN_ROOT is not set or points to wrong directory
- harness-concepts.md is missing from knowledge/
- Harness profile paths are wrong (use --claude-profile / --copilot-profile to override)
```

Stop.

---

## Step 4 — Present findings (exit 1)

Parse the JSON output. Present findings in two sections:

**Section A — Forbidden tokens** (grouped by file):

```
Forbidden tokens found in shared files:

  skills/al-dev-foo/SKILL.md
    Line 12 [error, autofixable]: token "X"
      Context: "...surrounding text..."
    Line 34 [warning, code_block]: token "Y"
      Context: "...surrounding text..."
    Line 56 [manual_review, prohibition_rule]: token "Z"
      Context: "...surrounding text..."
```

**Section B — Coverage gaps** (grouped by type):

```
Harness mapping gaps:

  Missing mappings (concept exists in harness-concepts.md but has no row in a mapping table):
    - "USER_GATE": missing in [claude, copilot]
    - "explore agent": missing in [copilot]

  Orphaned mappings (row exists in a mapping table but concept is not in harness-concepts.md):
    - "old concept": present in [claude]  <- may be intentional
```

---

## Step 5 — USER_GATE: offer fixes

Present a summary count and offer to fix:

```
Found N forbidden token(s) across M file(s), and P mapping gap(s).

Want me to attempt fixes?
- Autofixable prose hits will be substituted with the generic concept name from harness-concepts.md.
- code_block and prohibition_rule hits will be flagged for manual review (not auto-changed).
- Missing mapping rows will be added to the appropriate harness profile instruction file.
- Orphaned rows will be flagged for manual review (not auto-deleted).

Proceed? (yes / no)
```

USER_GATE — wait for user response. Do not proceed until answered.

---

## Step 6 — Fix flow (if user consents)

### 6a — Auto-fix prose hits (`autofixable: true`)

For each `forbidden_tokens` entry where `autofixable` is `true`:

1. Read the vocabulary table in `knowledge/harness-concepts.md`.
2. Find the row where the harness-specific concrete value matches the reported token.
3. Replace the forbidden token in the file with the generic concept name from column 1 of that row.
4. Preserve all surrounding text exactly.

### 6b — Flag non-autofixable hits

For each `code_block` or `prohibition_rule` hit, output:

```
Manual review needed:
  [file]:[line] — token "[X]" appears in a [context_type] context.
  Suggestion: verify this is intentional or replace with the generic concept name.
```

Do not modify these lines automatically.

### 6c — Fix missing mapping rows

For each entry in `missing_mappings`:

1. Open the harness profile instruction file for each harness listed in `missing_in`.
2. Locate the `## Harness Mapping` section.
3. Append a new stub row at the end of the table:
   `| **[concept name]** | _(fill in concrete value)_ |`
4. Tell the user: "Added stub row for '[concept]' — fill in the concrete harness value."

### 6d — Flag orphaned rows

For each entry in `orphaned_mappings`, output:

```
Orphaned mapping "[concept]" present in [harness] profile — concept not found in harness-concepts.md.
Verify this is intentional. If the concept was renamed, update harness-concepts.md.
```

Do not auto-delete orphaned rows.

---

## Step 7 — Re-run to confirm

After applying all fixes, re-run the script:

```bash
python3 "$SCRIPT" --mode enforce
ALIGN_EXIT=$?
```

If exit 0, report: "All alignment issues resolved."

If exit 1, present remaining issues and note which require manual review.
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
python3 -m pytest profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py::TestSkillFile -v
```

Expected: all 3 skill file tests pass.

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-align/SKILL.md
git commit -m "✨ feat(al-dev-align): add SKILL.md with full orchestration instructions"
```

---

## Task 7: Integration into al-dev-commit and al-dev-handoff

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`
- Modify: `profile-al-dev-shared/skills/al-dev-handoff/SKILL.md`

- [ ] **Step 1: Add advisory check to al-dev-commit (new Step 5.5)**

In `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`, locate the line:

```
## Step 6 — Dispatch Analysis Agent
```

Insert immediately before it:

```markdown
## Step 5.5 — Advisory Alignment Check

Run the alignment check in advisory mode (non-blocking):

```bash
SCRIPT="$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-align/check-alignment.py"
if [ -f "$SCRIPT" ]; then
  python3 "$SCRIPT" --mode advisory
fi
```

If the output JSON contains non-empty `forbidden_tokens` or `missing_mappings`, surface them as a warning:

```
⚠️  Alignment advisory: N issue(s) found. Run /al-dev-align to inspect and fix.
```

Continue to Step 6 regardless — this check is advisory only.
```

- [ ] **Step 2: Add advisory check to al-dev-handoff (new Step 0.5)**

In `profile-al-dev-shared/skills/al-dev-handoff/SKILL.md`, locate the line:

```
### Step 1 — Identify Target Repository
```

Insert immediately before it:

```markdown
### Step 0.5 — Advisory Alignment Check

Run the alignment check in advisory mode (non-blocking):

```bash
SCRIPT="$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-align/check-alignment.py"
if [ -f "$SCRIPT" ]; then
  python3 "$SCRIPT" --mode advisory
fi
```

If the output JSON contains non-empty `forbidden_tokens` or `missing_mappings`, surface them as a warning before handoff:

```
⚠️  Alignment advisory: N issue(s) found in shared files. Consider running /al-dev-align before handing off.
```

Continue to Step 1 regardless — this check is advisory only.
```

- [ ] **Step 3: Run full test suite to confirm nothing is broken**

```bash
python3 -m pytest profile-al-dev-shared/skills/al-dev-align/tests/test_check_alignment.py -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-commit/SKILL.md
git add profile-al-dev-shared/skills/al-dev-handoff/SKILL.md
git commit -m "✨ feat(al-dev-align): add advisory alignment check to al-dev-commit and al-dev-handoff"
```

---

## Self-Review

**Spec coverage:**

| Spec Requirement | Covered By |
|---|---|
| `check-alignment.py` CLI with `--mode`, `--claude-profile`, `--copilot-profile` | Task 5 |
| Exit codes 0 / 1 / 2 | Task 5 |
| JSON output with `forbidden_tokens`, `missing_mappings`, `orphaned_mappings` | Task 5 |
| Forbidden token derivation from harness-concepts.md columns 3+4 | Task 2 |
| Hardcoded path/config tokens | Task 2 |
| Frontmatter handling (line preservation) | Task 1 |
| File scan patterns (skills/*/SKILL.md, agents/*.md, knowledge/*.md) | Task 5 |
| Exclude harness-concepts.md from scan | Task 5 |
| Context classification (prose / code_block / prohibition_rule) | Task 3 |
| Severity and autofixable fields | Task 3 |
| Harness coverage audit — concept source from harness-concepts.md | Task 4 |
| Harness coverage audit — parse ## Harness Mapping tables | Task 4 |
| Missing and orphaned mapping reporting | Task 4 |
| SKILL.md with correct frontmatter | Task 6 |
| USER_GATE before auto-fix | Task 6 |
| Fix flow: prose auto-fix, code_block/prohibition flag, missing rows add, orphaned flag | Task 6 |
| Re-run to confirm after fixes | Task 6 |
| Integration into al-dev-commit (advisory) | Task 7 |
| Integration into al-dev-handoff (advisory) | Task 7 |
| `--mode advisory` integration snippet in spec | Task 7 |
| Path assumptions: AL_DEV_SHARED_PLUGIN_ROOT, fallback to script location | Task 5 |

**Placeholder scan:** No TBDs, TODOs, or vague steps. All code blocks contain real, runnable code.

**Type consistency:** `scan_file` returns `list[dict]` with keys `file`, `line`, `token`, `context`, `context_type`, `severity`, `autofixable` — matches the JSON output schema in the spec. `compute_coverage_gaps` returns `(list[dict], list[dict])` matching `missing_mappings` and `orphaned_mappings` shapes.
