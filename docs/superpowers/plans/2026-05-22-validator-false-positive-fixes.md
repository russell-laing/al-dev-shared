# Validator False Positive Elimination Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce validator false positives from 32 of 40 flags (~80%) to near-zero by fixing path resolution, emoji parsing, and intentional-brevity detection.

**Architecture:** Fix three root causes in `scripts/validate-knowledge-quality.py`:
1. **DEAD-REF (11 false positives):** Fix path reference parsing — references include "knowledge/" prefix but validator duplicates it
2. **NO-CODE (9 false positives):** Fix emoji/checkmark heading detection — don't flag sections with emoji/checkmark headers as [NO-CODE]
3. **THIN (12 false positives):** Fix intentional-brevity detection — exclude summary sections and sections followed by meaningful subsections

**Tech Stack:** Python 3, regex, pathlib

---

## File Structure

**Modified:**
- `scripts/validate-knowledge-quality.py` — Fix false positive detectors

**Test:**
- Create inline validation tests (no separate test file needed; script is small)

---

### Task 1: Fix DEAD-REF False Positives (Path Resolution)

**Files:**
- Modify: `scripts/validate-knowledge-quality.py:94-155` (find_knowledge_references and check_references)

**Root Cause:** References like `knowledge/proportional-planning.md` are extracted by the regex, then the validator looks for `knowledge_dir / "knowledge/proportional-planning.md"`, duplicating the "knowledge/" prefix. Should be `knowledge_dir / "proportional-planning.md"`.

- [ ] **Step 1: Update regex to capture just filename without "knowledge/" prefix**

Replace the `find_knowledge_references` function (currently line 94-97):

```python
def find_knowledge_references(content: str) -> List[Tuple[str, int]]:
    """Extract all knowledge file references (filename only, no 'knowledge/' prefix)."""
    pattern = r"knowledge/([\w\-]+\.md)"
    matches = re.finditer(pattern, content)
    return [(match.group(1), match.start()) for match in matches]
```

This extracts just the filename (e.g., "proportional-planning.md") from references like "knowledge/proportional-planning.md".

- [ ] **Step 2: Update check_references to use the clean filename**

Replace the `check_references` function (currently line 141-155):

```python
def check_references(filepath: str, content: str, knowledge_dir: Path) -> List[str]:
    """Check for broken cross-references."""
    issues = []
    refs = find_knowledge_references(content)

    for ref_filename, _ in refs:
        # Skip self-references (file referencing itself is fine)
        if ref_filename == Path(filepath).name:
            continue

        ref_path = knowledge_dir / ref_filename
        if not ref_path.exists():
            issues.append(f"[DEAD-REF] {filepath}: knowledge/{ref_filename} (not found)")

    return issues
```

- [ ] **Step 3: Test the fix manually**

Run the validator:
```bash
python3 scripts/validate-knowledge-quality.py --path "profile-al-dev-shared/knowledge" --verbose
```

Expected: workflow-routing.md and other files should NO LONGER report [DEAD-REF] for proportional-planning.md

- [ ] **Step 4: Commit**

```bash
git add scripts/validate-knowledge-quality.py
git commit -m "fix(validate-knowledge-quality): resolve DEAD-REF path duplication bug"
```

---

### Task 2: Fix NO-CODE False Positives (Emoji/Checkmark Headers)

**Files:**
- Modify: `scripts/validate-knowledge-quality.py:117-138` (check_code_implication)

**Root Cause:** Headings with emoji/checkmarks like "❌ BAD: SIMPLE Feature" contain the word "bad" which is in CODE_KEYWORDS. The validator checks if "bad:" is in the heading, and it is (as part of the emoji text). But these are section titles, not code-implication keywords. Should skip headings that contain emoji/checkmarks.

- [ ] **Step 1: Add emoji detection helper**

Add this new function after `count_body_lines` (after line 91):

```python
def has_emoji_or_checkmark(text: str) -> bool:
    """Check if text contains emoji or checkmark characters.
    
    Common emoji/checkmark patterns in markdown:
    - ❌ ✅ 🔴 🟡 🟢 🔵 etc. (Unicode emoji)
    - Common markdown markers: [x] [ ] etc.
    """
    emoji_pattern = r'[☺-\U0001F999]|[☀-➿]|[ἰ0-ᾟF]'
    return bool(re.search(emoji_pattern, text))
```

- [ ] **Step 2: Update check_code_implication to skip emoji headers**

Replace the `check_code_implication` function (currently line 117-138):

```python
def check_code_implication(filepath: str, sections: List) -> List[str]:
    """Check sections that imply code but have no code blocks."""
    issues = []
    for heading, level, body_start, body in sections:
        # Skip sections that are short by design
        if heading.lower() in ("overview", "usage", "references"):
            continue

        # Skip sections with emoji/checkmark headers (typically section titles with examples below)
        if has_emoji_or_checkmark(heading):
            continue

        heading_lower = heading.lower()
        body_lower = body.lower()

        # Check if heading or first line implies code
        implies_code = any(
            keyword in heading_lower or keyword in body_lower for keyword in CODE_KEYWORDS
        )

        if implies_code and not has_code_block(body) and count_body_lines(body) > 2:
            issues.append(
                f"[NO-CODE]  {filepath}: {heading} — body implies code but has none"
            )

    return issues
```

- [ ] **Step 3: Test the fix manually**

Run the validator:
```bash
python3 scripts/validate-knowledge-quality.py --path "profile-al-dev-shared/knowledge" --verbose
```

Expected: proportional-planning.md should NO LONGER report [NO-CODE] for "❌ BAD: SIMPLE Feature with 946-line Plan"

- [ ] **Step 4: Commit**

```bash
git add scripts/validate-knowledge-quality.py
git commit -m "fix(validate-knowledge-quality): skip NO-CODE check for emoji/checkmark headers"
```

---

### Task 3: Fix THIN False Positives (Intentional Brevity Detection)

**Files:**
- Modify: `scripts/validate-knowledge-quality.py:100-114` (check_thin_sections)

**Root Cause:** Sections titled "Goal" are intentionally one-line summaries. The validator flags them as [THIN] because they have < 3 lines. But these are meant to be concise, with detailed content in subsections below. Need to either:
1. Exclude known summary-header names ("Goal", "Summary", etc.)
2. Don't flag a section as THIN if it has substantive subsections immediately below it

- [ ] **Step 1: Identify summary section names that should be skipped**

Add this set after CODE_KEYWORDS (after line 38):

```python
# Section names that are intentionally brief summaries
SUMMARY_SECTIONS = {
    "goal",
    "summary",
    "overview",
    "introduction",
    "rationale",
    "motivation",
    "purpose",
}
```

- [ ] **Step 2: Update parse_sections to include heading text**

The current parse_sections function strips the heading, but we need it. Verify the heading is stored correctly in the tuple (it is at index 0). No change needed here.

- [ ] **Step 3: Update check_thin_sections to skip summary sections**

Replace the `check_thin_sections` function (currently line 100-114):

```python
def check_thin_sections(filepath: str, sections: List) -> List[str]:
    """Check for sections with minimal body content.
    
    Skip:
    - Level 1-2 headings (document titles and section headers)
    - Known summary sections (Goal, Summary, Overview, etc.)
    - Sections with emoji/checkmark headers
    """
    issues = []
    for i, (heading, level, body_start, body) in enumerate(sections):
        # Skip level-2 (##) headings and special sections
        if level <= 2:
            continue

        # Skip known summary sections that are intentionally brief
        if heading.lower() in SUMMARY_SECTIONS:
            continue

        # Skip sections with emoji/checkmark headers (typically have content in subsections)
        if has_emoji_or_checkmark(heading):
            continue

        line_count = count_body_lines(body)
        if line_count < 3:
            issues.append(
                f"[THIN]     {filepath}: {heading} ({line_count} lines)"
            )

    return issues
```

- [ ] **Step 4: Test the fix manually**

Run the validator:
```bash
python3 scripts/validate-knowledge-quality.py --path "profile-al-dev-shared/knowledge" --verbose
```

Expected: tdd-workflow.md should NO LONGER report [THIN] for any "Goal" sections

- [ ] **Step 5: Commit**

```bash
git add scripts/validate-knowledge-quality.py
git commit -m "fix(validate-knowledge-quality): exclude summary sections from THIN check"
```

---

### Task 4: Run Full Validation and Verify False Positives Eliminated

**Files:**
- Test: Run validator on full knowledge directory

- [ ] **Step 1: Run the validator with verbose output**

```bash
python3 scripts/validate-knowledge-quality.py --path "profile-al-dev-shared/knowledge" --verbose 2>&1 | tee /tmp/validator-output.txt
```

- [ ] **Step 2: Count warnings before and after**

Before fixes: 40 warnings total
- [DEAD-REF]: 11 (all false positives)
- [NO-CODE]: 9 (mostly false positives)
- [THIN]: 20 (mostly false positives)

After fixes, expect:
- [DEAD-REF]: 0 (all fixed)
- [NO-CODE]: ~2-3 (real issues like code-review-patterns.md)
- [THIN]: ~3-5 (real issues like perf-anti-patterns-prompt.md decision sections)

Total expected: ~5-10 real warnings (down from 40)

- [ ] **Step 3: Manually verify remaining warnings are real issues**

For each remaining warning, check:
- [THIN] on perf-anti-patterns-prompt.md sections: Actual brief sections (1-2 lines) that SHOULD be expanded
- [NO-CODE] on code-review-patterns.md: Actual missing code examples

These are real issues, not false positives.

- [ ] **Step 4: Update docs/al-dev-knowledge-quality.md with new results**

```markdown
## Validator Fix Results (2026-05-22)

**Before fixes:** 40 warnings (32 false positives)
**After fixes:** ~8 real warnings (100% false positive elimination)

**False Positives Eliminated:**
- ✅ [DEAD-REF] path duplication (11 fixed)
- ✅ [NO-CODE] emoji/checkmark headers (9 fixed)  
- ✅ [THIN] summary sections (12 fixed)

**Remaining Real Issues:** 8 HIGH severity that require knowledge file content updates
(See HIGH Severity Issues section for details)
```

- [ ] **Step 5: Commit validator test results**

```bash
git add docs/al-dev-knowledge-quality.md
git commit -m "docs: update knowledge quality audit with validator fix results"
```

---

### Task 5: Test Edge Cases and Document Behavior

**Files:**
- Modify: `scripts/validate-knowledge-quality.py` (add comments)

- [ ] **Step 1: Verify edge cases**

Test these manually by running validator:

1. **File with multiple emoji headers:** proportional-planning.md has "❌ BAD" and "✅ GOOD" sections
   - Expected: Both should skip [NO-CODE] check
   
2. **File with emoji in middle of text:** If a section mentions "❌ this is bad practice" in the body
   - Expected: Only the emoji_or_checkmark in HEADING matters, not in body
   
3. **Mixed real and false [THIN]:** tdd-workflow.md has both "Goal" (skip) and other sections (check)
   - Expected: Only non-Goal sections should be flagged

- [ ] **Step 2: Document the fixes in code comments**

Add comment block above each checker function explaining what false positives it eliminates:

```python
def check_thin_sections(filepath: str, sections: List) -> List[str]:
    """Check for sections with minimal body content.
    
    FALSE POSITIVES FIXED:
    - Skips sections with emoji/checkmark headers (e.g., "❌ BAD: SIMPLE Feature")
    - Skips known summary sections (Goal, Overview, etc.) which are intentionally brief
    
    REAL ISSUES DETECTED:
    - Sections with < 3 lines that need actual content expansion
    """
```

- [ ] **Step 3: Update script docstring**

Update the module docstring to document false positive fixes:

```python
"""
Validator for knowledge file quality. Detects structural stubs and issues.

FALSE POSITIVES ELIMINATED (2026-05-22):
- [DEAD-REF] path resolution: Fixed double "knowledge/" prefix in reference checks
- [NO-CODE] emoji headers: Skip sections with emoji/checkmark titles (have content in body)
- [THIN] summary sections: Skip intentional summary sections (Goal, Overview, etc.)

Usage:
  python3 validate-knowledge-quality.py [--path <dir>] [--strict] [--verbose]

Exit codes:
  0: No issues (or advisory-only with --strict off)
  1: Issues found (when --strict is set)
"""
```

- [ ] **Step 4: Commit**

```bash
git add scripts/validate-knowledge-quality.py
git commit -m "docs(validate-knowledge-quality): document false positive fixes and edge cases"
```

---

### Task 6: Create Regression Test to Prevent Future False Positives

**Files:**
- Create: `scripts/test-validator-false-positives.py`

- [ ] **Step 1: Create test file with sample knowledge excerpts**

```python
#!/usr/bin/env python3
"""
Regression tests for validate-knowledge-quality.py false positive fixes.

Tests ensure that known false positive patterns continue to be skipped.
"""

import re
from pathlib import Path

# Import validator functions (assuming same directory)
import sys
sys.path.insert(0, str(Path(__file__).parent))
from validate_knowledge_quality import (
    find_knowledge_references,
    has_emoji_or_checkmark,
    check_thin_sections,
    check_code_implication,
)


def test_dead_ref_path_resolution():
    """Verify DEAD-REF false positives from path duplication are fixed."""
    content = """
# Some Section

See knowledge/proportional-planning.md for more info.
"""
    refs = find_knowledge_references(content)
    # Should return just "proportional-planning.md", not "knowledge/proportional-planning.md"
    assert refs[0][0] == "proportional-planning.md", f"Got {refs[0][0]}"
    print("✓ DEAD-REF path resolution test passed")


def test_emoji_detection():
    """Verify emoji/checkmark detection works."""
    assert has_emoji_or_checkmark("❌ BAD: Example") == True
    assert has_emoji_or_checkmark("✅ GOOD: Example") == True
    assert has_emoji_or_checkmark("🔴 COMPLEX") == True
    assert has_emoji_or_checkmark("Plain text heading") == False
    print("✓ Emoji detection test passed")


def test_no_code_emoji_skip():
    """Verify [NO-CODE] is skipped for emoji headers."""
    # Section with emoji header should not be flagged [NO-CODE]
    sections = [
        ("❌ BAD: SIMPLE Feature with 946-line Plan", 3, 0, "Long explanation here.\nWith multiple lines.\nBut no code block."),
    ]
    issues = check_code_implication("test.md", sections)
    # Should be empty because emoji header is skipped
    assert len(issues) == 0, f"Got issues: {issues}"
    print("✓ NO-CODE emoji skip test passed")


def test_thin_goal_section_skip():
    """Verify [THIN] is skipped for 'Goal' sections."""
    # Goal section with 1 line should not be flagged [THIN]
    sections = [
        ("### Goal", 3, 0, "Write minimal code to make test pass."),
    ]
    issues = check_thin_sections("test.md", sections)
    # Should be empty because "Goal" section is skipped
    assert len(issues) == 0, f"Got issues: {issues}"
    print("✓ THIN goal section skip test passed")


if __name__ == "__main__":
    test_dead_ref_path_resolution()
    test_emoji_detection()
    test_no_code_emoji_skip()
    test_thin_goal_section_skip()
    print("\n✅ All regression tests passed!")
```

- [ ] **Step 2: Run the regression tests**

```bash
python3 scripts/test-validator-false-positives.py
```

Expected output:
```
✓ DEAD-REF path resolution test passed
✓ Emoji detection test passed
✓ NO-CODE emoji skip test passed
✓ THIN goal section skip test passed

✅ All regression tests passed!
```

- [ ] **Step 3: Commit regression tests**

```bash
git add scripts/test-validator-false-positives.py
git commit -m "test(validate-knowledge-quality): add regression tests for false positive fixes"
```

---

## Summary

**Changes Made:**
1. Fixed DEAD-REF path resolution (11 false positives eliminated)
2. Added emoji/checkmark detection to skip NO-CODE check (9 false positives eliminated)
3. Added summary section detection to skip THIN check (12 false positives eliminated)
4. Created regression test suite to prevent regressions

**Result:** Validator output reduced from 40 warnings (32 false positives) to ~8 real warnings requiring knowledge file content updates.

**Verification:**
- Run `python3 scripts/validate-knowledge-quality.py --path "profile-al-dev-shared/knowledge" --verbose`
- Expected: ~8 warnings total (real issues, not false positives)
- Run `python3 scripts/test-validator-false-positives.py` to verify no regressions
