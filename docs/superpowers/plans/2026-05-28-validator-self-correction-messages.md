# Validator Self-Correction Messages

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Standardise the failure output of the three existing repo-local validators so every message names the file, the rule-id, the violation, and a single concrete fix — matching the canonical shape already used by `validate_artifact_contracts.py`.

**Architecture:** Output-only change. Detection logic in all three scripts is untouched. Each script gets a private `_format_*()` helper function and a per-rule fix lookup; the existing data structures (`Finding`, `failures` list, `warnings` list) stay the same where possible. One commit per validator so diffs stay reviewable. Tests are written before implementation (TDD).

**Tech Stack:** Python 3, stdlib only. Same `importlib.util` pattern used in `test-validator-false-positives.py` for hyphenated filenames. Canonical output shape from `validate_artifact_contracts.py:_format_violation()`.

---

## File Map

| Path | Status | Responsibility |
|---|---|---|
| `scripts/validate_harness_neutrality.py` | Modify | Add `_RULE_FIX` dict + `_format_finding()` + update `main()` loop |
| `scripts/validate-lens-agents.py` | Modify | Add `_format_failure()` + update all 8 `failures.append()` calls + update output |
| `scripts/validate-knowledge-quality.py` | Modify | Add `_format_issue()` + update 4 issue-building calls + update `main()` print loop |
| `scripts/tests/test_validate_harness_neutrality.py` | Modify | Add `test_formatted_output_has_canonical_shape()` |
| `scripts/tests/test_validate_lens_agents.py` | New | Two tests covering `_format_failure()` output shape |
| `scripts/tests/test_validate_knowledge_quality.py` | New | Four tests covering `_format_issue()` and each check function |

---

## Canonical Output Shape

The reference implementation is `validate_artifact_contracts.py:_format_violation()`. Every failure block must follow this exact shape:

```text
{path}
  rule: {rule-id}
  issue: {one-sentence statement of the violation}
  fix: {single concrete action}
```

Multiple blocks are separated by a blank line. Success emits one line: `PASS: …`.

---

## Task 1: Harness-Neutrality Validator — Write Failing Test

**Files:**
- Modify: `scripts/tests/test_validate_harness_neutrality.py`

- [ ] **Step 1: Add the failing test to the existing test file**

Append this function to `scripts/tests/test_validate_harness_neutrality.py` (before the `_run_pytest_style_test` helper at the bottom):

```python
def test_formatted_output_has_canonical_shape() -> None:
    from scripts.validate_harness_neutrality import _format_finding, Finding
    f = Finding("skills/demo/SKILL.md", "Claude tool token", "AskUserQuestion")
    output = _format_finding(f)
    lines = output.splitlines()
    assert lines[0] == "skills/demo/SKILL.md", f"First line must be the path, got: {lines[0]!r}"
    assert any(ln.strip().startswith("rule:") for ln in lines), "Missing 'rule:' field"
    assert any(ln.strip().startswith("issue:") for ln in lines), "Missing 'issue:' field"
    assert any(ln.strip().startswith("fix:") for ln in lines), "Missing 'fix:' field"
    assert "AskUserQuestion" in output, "Matched text must appear in output"
    assert "harness-concepts.md" in output, "Fix must reference the rule document"
```

- [ ] **Step 2: Verify the test fails before implementation**

Run:
```bash
python3 scripts/tests/test_validate_harness_neutrality.py 2>&1 | tail -5
```
Expected: `ImportError: cannot import name '_format_finding'` (or similar).

---

## Task 2: Harness-Neutrality Validator — Implement Canonical Output

**Files:**
- Modify: `scripts/validate_harness_neutrality.py`

- [ ] **Step 1: Read the current file before editing**

Open `scripts/validate_harness_neutrality.py`. The current `main()` output loop is (lines ~88–89):
```python
for finding in findings:
    print(f"{finding.path}: {finding.rule}: {finding.excerpt}")
```

- [ ] **Step 2: Insert `_RULE_FIX` dict and `_format_finding()` after the `Finding` dataclass**

Insert the following block after the `Finding` dataclass definition (after `class Finding` closes, before `def iter_markdown_files`):

```python
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
```

- [ ] **Step 3: Replace the output loop in `main()`**

In `main()`, replace:
```python
for finding in findings:
    print(f"{finding.path}: {finding.rule}: {finding.excerpt}")
return 1
```
with:
```python
blocks = "\n\n".join(_format_finding(f) for f in findings)
print(blocks)
return 1
```

- [ ] **Step 4: Run all harness-neutrality tests**

Run:
```bash
python3 scripts/tests/test_validate_harness_neutrality.py -v 2>&1
```
Expected: all tests PASS including the new `test_formatted_output_has_canonical_shape`.

- [ ] **Step 5: Spot-check the live output shape**

Run:
```bash
python3 -c "
from pathlib import Path
from scripts.validate_harness_neutrality import _format_finding, Finding
f = Finding('skills/demo/SKILL.md', 'Claude tool token', 'AskUserQuestion')
print(_format_finding(f))
"
```
Expected output shape:
```text
skills/demo/SKILL.md
  rule: neutrality-violation
  issue: forbidden harness token ('Claude tool token'); matched text: 'AskUserQuestion'
  fix: replace "AskUserQuestion" with the generic tool name from knowledge/harness-concepts.md
```

- [ ] **Step 6: Commit**

```bash
git add scripts/validate_harness_neutrality.py scripts/tests/test_validate_harness_neutrality.py
git commit -m "fix(validators): add self-correction messages to harness-neutrality validator"
```

---

## Task 3: Lens-Agents Validator — Write Failing Tests

**Files:**
- Create: `scripts/tests/test_validate_lens_agents.py`

- [ ] **Step 1: Write the test file**

```python
# scripts/tests/test_validate_lens_agents.py
"""Tests for canonical self-correction output shape in validate-lens-agents."""
from __future__ import annotations

import importlib.util
import inspect
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "validate_lens_agents",
    REPO_ROOT / "scripts" / "validate-lens-agents.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

_format_failure = _mod._format_failure


def test_format_failure_has_canonical_shape() -> None:
    output = _format_failure(
        path=".claude/agents/quality-lens-clarity.md",
        rule="agent-model",
        issue="model is not set to haiku",
        fix='add "model: haiku" to the YAML frontmatter',
    )
    lines = output.splitlines()
    assert lines[0] == ".claude/agents/quality-lens-clarity.md", (
        f"First line must be path, got: {lines[0]!r}"
    )
    assert any(ln.strip().startswith("rule:") for ln in lines), "Missing 'rule:' field"
    assert any(ln.strip().startswith("issue:") for ln in lines), "Missing 'issue:' field"
    assert any(ln.strip().startswith("fix:") for ln in lines), "Missing 'fix:' field"
    assert "haiku" in output


def test_format_failure_embeds_path_in_fix_when_provided() -> None:
    output = _format_failure(
        path=".claude/agents/foo.md",
        rule="agent-forbidden-tool",
        issue='tool "Bash" is not permitted for lens agents',
        fix='remove "Bash" from the tools list in .claude/agents/foo.md',
    )
    assert ".claude/agents/foo.md" in output
    assert "Bash" in output
    assert "fix:" in output


def _run(func):
    sig = inspect.signature(func)
    if not sig.parameters:
        func()
    elif list(sig.parameters) == ["tmp_path"]:
        with tempfile.TemporaryDirectory() as td:
            func(Path(td))
    else:
        raise TypeError(f"Unsupported signature: {func.__name__}{sig}")


def load_tests(loader, tests, pattern):  # noqa: ARG001
    suite = unittest.TestSuite()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            suite.addTest(unittest.FunctionTestCase(lambda fn=fn: _run(fn)))
    return suite


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Verify the test fails before implementation**

Run:
```bash
python3 scripts/tests/test_validate_lens_agents.py 2>&1 | tail -5
```
Expected: `AttributeError: module 'validate_lens_agents' has no attribute '_format_failure'`.

---

## Task 4: Lens-Agents Validator — Implement Canonical Output

**Files:**
- Modify: `scripts/validate-lens-agents.py`

- [ ] **Step 1: Read the current file before editing**

Open `scripts/validate-lens-agents.py`. It has:
- `failures = []` list at module level
- 8 `failures.append(f"...")` calls in two loops
- Output block at the bottom: `print(f"FAIL — {len(failures)} issue(s):")` etc.

- [ ] **Step 2: Add `_format_failure()` after the imports**

Insert after the last import line (after `import sys`) and before `REPO = ...`:

```python
def _format_failure(path: str, rule: str, issue: str, fix: str) -> str:
    return (
        f"{path}\n"
        f"  rule: {rule}\n"
        f"  issue: {issue}\n"
        f"  fix: {fix}"
    )
```

- [ ] **Step 3: Replace all 8 `failures.append(...)` calls**

Replace each current single-line append with a canonical multi-line block. The complete set of replacements:

**For agents loop (lines ~43–65 approx):**

Replace `failures.append(f"MISSING: {path}")` with:
```python
failures.append(_format_failure(
    path,
    "agent-exists",
    "agent file not found",
    f"create {path} with required frontmatter (model: haiku, tools list, ## Output Format section)",
))
```

Replace `failures.append(f"NOT HAIKU model: {path}")` with:
```python
failures.append(_format_failure(
    path,
    "agent-model",
    "model is not set to haiku",
    f'add "model: haiku" to the YAML frontmatter in {path}',
))
```

Replace `failures.append(f"FORBIDDEN TOOL '{tool}' in tools list: {path}")` with:
```python
failures.append(_format_failure(
    path,
    "agent-forbidden-tool",
    f'tool "{tool}" is not permitted for lens agents (cannot mutate files)',
    f'remove "{tool}" from the tools list in {path}',
))
```

Replace `failures.append(f"MISSING '## Output Format' section: {path}")` with:
```python
failures.append(_format_failure(
    path,
    "agent-output-format-section",
    'no "## Output Format" section in body',
    f'add a "## Output Format" section to {path} describing the findings block structure',
))
```

Replace `failures.append(f"MISSING no-issues pattern: {path}")` with:
```python
failures.append(_format_failure(
    path,
    "agent-no-issues-pattern",
    'no "_No issues found._" fallback pattern in body',
    f'add "_No issues found._" to the ## Output Format section in {path}',
))
```

**For skills loop (lines ~67–76 approx):**

Replace `failures.append(f"MISSING SKILL: {skill_path}")` with:
```python
failures.append(_format_failure(
    skill_path,
    "skill-exists",
    "skill file not found",
    f"create {skill_path} or remove it from SKILLS_TO_CHECK in the validator",
))
```

Replace `failures.append(f"MISSING 'Phase 2' (parallel dispatch not added): {skill_path}")` with:
```python
failures.append(_format_failure(
    skill_path,
    "skill-parallel-dispatch",
    'no "Phase 2" section — parallel agent dispatch not implemented',
    f"add a Phase 2 section with parallel agent dispatch to {skill_path}",
))
```

Replace `failures.append(f"MISSING parallel dispatch language: {skill_path}")` with:
```python
failures.append(_format_failure(
    skill_path,
    "skill-parallel-language",
    'no parallel dispatch language ("parallel" or "simultaneously") found in body',
    f"add explicit parallel dispatch phrasing to Phase 2 in {skill_path}",
))
```

- [ ] **Step 4: Update the output block**

Replace the current output section:
```python
if failures:
    print(f"FAIL — {len(failures)} issue(s):")
    for f in failures:
        print(f"  {f}")
    sys.exit(1)
else:
    print(f"PASS — {len(EXPECTED_AGENTS)} agents valid, 4 skills refactored.")
```
with:
```python
if failures:
    print(f"FAIL — {len(failures)} issue(s):\n")
    print("\n\n".join(failures))
    sys.exit(1)
else:
    print(f"PASS — {len(EXPECTED_AGENTS)} agents valid, 4 skills refactored.")
```

- [ ] **Step 5: Run lens-agents tests**

Run:
```bash
python3 scripts/tests/test_validate_lens_agents.py -v 2>&1
```
Expected: both tests PASS.

- [ ] **Step 6: Verify the validator itself still passes on the live tree**

Run:
```bash
python3 scripts/validate-lens-agents.py 2>&1
```
Expected: `PASS — 20 agents valid, 4 skills refactored.` (exit 0).

- [ ] **Step 7: Commit**

```bash
git add scripts/validate-lens-agents.py scripts/tests/test_validate_lens_agents.py
git commit -m "fix(validators): add self-correction messages to lens-agents validator"
```

---

## Task 5: Knowledge-Quality Validator — Write Failing Tests

**Files:**
- Create: `scripts/tests/test_validate_knowledge_quality.py`

- [ ] **Step 1: Write the test file**

```python
# scripts/tests/test_validate_knowledge_quality.py
"""Tests for canonical self-correction output shape in validate-knowledge-quality."""
from __future__ import annotations

import importlib.util
import inspect
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "validate_knowledge_quality",
    REPO_ROOT / "scripts" / "validate-knowledge-quality.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

_format_issue = _mod._format_issue
check_thin_sections = _mod.check_thin_sections
check_code_implication = _mod.check_code_implication
check_references = _mod.check_references


def test_format_issue_has_canonical_shape() -> None:
    output = _format_issue(
        "knowledge/foo.md",
        "knowledge-stub",
        'section "Usage" has 1 content line — too thin',
        "expand the section body or remove the header",
    )
    lines = output.splitlines()
    assert lines[0] == "knowledge/foo.md", f"First line must be path, got: {lines[0]!r}"
    assert any(ln.strip().startswith("rule:") for ln in lines), "Missing 'rule:' field"
    assert any(ln.strip().startswith("issue:") for ln in lines), "Missing 'issue:' field"
    assert any(ln.strip().startswith("fix:") for ln in lines), "Missing 'fix:' field"
    assert "knowledge-stub" in output


def test_check_thin_sections_emits_canonical_shape() -> None:
    sections = [("Usage Details", 3, 0, "short")]
    issues = check_thin_sections("knowledge/foo.md", sections)
    assert issues, "Expected at least one issue for a 1-line section"
    output = issues[0]
    assert "rule:" in output
    assert "knowledge-stub" in output
    assert "issue:" in output
    assert "fix:" in output


def test_check_code_implication_emits_canonical_shape() -> None:
    body = "Line one.\nLine two.\nLine three.\nNo code block here."
    sections = [("Usage: Example Pattern", 3, 0, body)]
    issues = check_code_implication("knowledge/foo.md", sections)
    assert issues, "Expected at least one issue for a code-implying section without code block"
    output = issues[0]
    assert "rule:" in output
    assert "knowledge-no-code" in output
    assert "fix:" in output


def test_check_references_emits_canonical_shape(tmp_path: Path) -> None:
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    content = "See knowledge/missing-file.md for details.\n"
    issues = check_references("knowledge/foo.md", content, knowledge_dir)
    assert issues, "Expected a dead-ref issue for a reference to a non-existent file"
    output = issues[0]
    assert "rule:" in output
    assert "knowledge-dead-ref" in output
    assert "fix:" in output
    assert "missing-file.md" in output


def _run(func):
    sig = inspect.signature(func)
    if not sig.parameters:
        func()
    elif list(sig.parameters) == ["tmp_path"]:
        with tempfile.TemporaryDirectory() as td:
            func(Path(td))
    else:
        raise TypeError(f"Unsupported signature: {func.__name__}{sig}")


def load_tests(loader, tests, pattern):  # noqa: ARG001
    suite = unittest.TestSuite()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            suite.addTest(unittest.FunctionTestCase(lambda fn=fn: _run(fn)))
    return suite


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Verify the test fails before implementation**

Run:
```bash
python3 scripts/tests/test_validate_knowledge_quality.py 2>&1 | tail -5
```
Expected: `AttributeError: module 'validate_knowledge_quality' has no attribute '_format_issue'`.

---

## Task 6: Knowledge-Quality Validator — Implement Canonical Output

**Files:**
- Modify: `scripts/validate-knowledge-quality.py`

- [ ] **Step 1: Read the current file before editing**

Open `scripts/validate-knowledge-quality.py`. Locate:
- `check_thin_sections()` — emits `[THIN] ...` strings
- `check_code_implication()` — emits `[NO-CODE] ...` strings
- `check_references()` — emits `[DEAD-REF] ...` strings
- `validate_knowledge_dir()` — emits `[ERROR] ...` strings
- `main()` print loop: `for warning in warnings: print(f"  {warning}")`

- [ ] **Step 2: Insert `_format_issue()` at module level**

Insert after the module docstring/imports block, before `EXCLUDED_PATTERNS`:

```python
def _format_issue(path: str, rule: str, issue: str, fix: str) -> str:
    return (
        f"{path}\n"
        f"  rule: {rule}\n"
        f"  issue: {issue}\n"
        f"  fix: {fix}"
    )
```

- [ ] **Step 3: Update `check_thin_sections()`**

Replace:
```python
issues.append(
    f"[THIN]     {filepath}: {heading} ({line_count} lines)"
)
```
with:
```python
issues.append(
    _format_issue(
        filepath,
        "knowledge-stub",
        f'section "{heading}" has {line_count} content line(s) — too thin for a level-{level} section',
        "expand the section body or remove the header if the content belongs elsewhere",
    )
)
```

- [ ] **Step 4: Update `check_code_implication()`**

Replace:
```python
issues.append(
    f"[NO-CODE]  {filepath}: {heading} — body implies code but has none"
)
```
with:
```python
issues.append(
    _format_issue(
        filepath,
        "knowledge-no-code",
        f'section "{heading}" implies code (keyword in heading or body) but has no fenced code block',
        "add a fenced code block example, or rename the heading to remove the code implication",
    )
)
```

- [ ] **Step 5: Update `check_references()`**

Replace:
```python
issues.append(f"[DEAD-REF] {filepath}: knowledge/{ref_filename} (not found)")
```
with:
```python
issues.append(
    _format_issue(
        filepath,
        "knowledge-dead-ref",
        f"reference to knowledge/{ref_filename} does not resolve to an existing file",
        f"check the filename for typos or create the missing file at knowledge/{ref_filename}",
    )
)
```

- [ ] **Step 6: Update `validate_knowledge_dir()` error handling**

Replace:
```python
warnings.append(f"[ERROR]    {str_path}: {e}")
```
with:
```python
warnings.append(
    _format_issue(
        str_path,
        "file-unreadable",
        f"could not read file: {e}",
        "check file encoding (must be UTF-8) or fix file permissions",
    )
)
```

- [ ] **Step 7: Update `main()` print loop**

Replace:
```python
if warnings:
    print(f"\nWARNINGS ({len(warnings)}):")
    for warning in warnings:
        print(f"  {warning}")
```
with:
```python
if warnings:
    print(f"\nWARNINGS ({len(warnings)}):")
    print()
    print("\n\n".join(warnings))
```

- [ ] **Step 8: Run knowledge-quality tests**

Run:
```bash
python3 scripts/tests/test_validate_knowledge_quality.py -v 2>&1
```
Expected: all 4 tests PASS.

- [ ] **Step 9: Run the existing false-positive regression tests**

Run:
```bash
python3 scripts/test-validator-false-positives.py 2>&1
```
Expected: `All regression tests passed!` (exit 0). These tests only check `len(issues) == 0` — they are format-agnostic.

- [ ] **Step 10: Spot-check the live output shape**

Run:
```bash
python3 scripts/validate-knowledge-quality.py --path profile-al-dev-shared/knowledge 2>&1 | head -20
```
Expected: either `PASS (N files clean)` or warning blocks in canonical shape (no `[THIN]`, `[NO-CODE]`, `[DEAD-REF]` prefixes).

- [ ] **Step 11: Commit**

```bash
git add scripts/validate-knowledge-quality.py scripts/tests/test_validate_knowledge_quality.py
git commit -m "fix(validators): add self-correction messages to knowledge-quality validator"
```

---

## Task 7: Integration Verification

Run all three validators against the live tree to confirm no behavioural regression (same violations found, new format only).

- [ ] **Step 1: Run harness-neutrality validator**

Run:
```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared 2>&1
```
Expected: `PASS: no harness-specific leakage in shared authored surface` (exit 0).

- [ ] **Step 2: Run lens-agents validator**

Run:
```bash
python3 scripts/validate-lens-agents.py 2>&1
```
Expected: `PASS — 20 agents valid, 4 skills refactored.` (exit 0).

- [ ] **Step 3: Run knowledge-quality validator**

Run:
```bash
python3 scripts/validate-knowledge-quality.py --path profile-al-dev-shared/knowledge 2>&1
```
Expected: `PASS (N files clean)` (exit 0 with or without `--strict`).

- [ ] **Step 4: Run the artifact-contract validator**

Run:
```bash
python3 scripts/validate_artifact_contracts.py 2>&1
```
Expected: `OK: 6 skills conform to artifact-contracts.md`. This validator was unchanged; confirm it still runs cleanly.

- [ ] **Step 5: Run the full test suite**

Run:
```bash
python3 scripts/tests/test_validate_harness_neutrality.py -v 2>&1
python3 scripts/tests/test_validate_artifact_contracts.py -v 2>&1
python3 scripts/tests/test_validate_lens_agents.py -v 2>&1
python3 scripts/tests/test_validate_knowledge_quality.py -v 2>&1
```
Expected: all test files report OK / PASS with no failures.
