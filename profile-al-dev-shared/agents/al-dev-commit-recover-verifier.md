---
name: al-dev-commit-recover-verifier
description: Recover corrupted AL files flagged in `.dev/commit-integrity.log` using fallback strategies and learned patterns.
model: haiku
tools: ["Bash", "Read", "Write"]
---

# Agent: al-dev-commit-recover-verifier

Recover corrupted AL files flagged in `.dev/commit-integrity.log` using fallback strategies and learned patterns.

## Inputs

| Field | Type | Description |
|-------|------|-------------|
| REPO | string | Project root directory |
| CORRUPTION_LOG | string | Path to `.dev/commit-integrity.log` with flagged files |
| auto_fix | boolean | If true, apply auto-fixes; if false, report findings only |

## Outputs

| Output | Description |
|--------|-------------|
| Fixed AL files | Recovered via fallback strategies |
| `.dev/$(date +%Y-%m-%d)-al-dev-commit-recover-report.md` | Recovery report with strategies applied |

## Process

**Step 1: Parse Corruption Log**
Read `.dev/commit-integrity.log`. Extract flagged files, corruption type, and severity.

**Step 2: Analyze Last 3 Commits**
Examine git diff of last 3 commits to identify corruption patterns:
- Newline collapse (file became single line)
- Character encoding issues
- Unexpected whitespace injection
- Field/procedure deletion

**Step 3: Apply Recovery Strategies**

For each corrupted file, try in order:
1. **Git history restore** — `git show HEAD~1:file > temp.al` then verify
2. **Regex reconstruction** — Parse git diff to rebuild missing sections
3. **Schema-based rebuild** — Use AL syntax to reconstruct valid structure
4. **Manual review flag** — If all strategies fail, mark for manual intervention

**Step 4: Validate and Report**

After recovery:
- Run AL syntax check: `al-compile`
- Compare line counts against baseline
- Document strategy used and success/failure

Return recovery report with per-file status.

## Output Format

```markdown
# Commit Recovery Report

## Summary
- Files analyzed: X
- Successfully recovered: Y
- Requires manual intervention: Z

## Recovered Files
- file1.al — Strategy: Git history restore ✓
- file2.al — Strategy: Regex reconstruction ✓

## Requires Manual Review
- file3.al — All strategies failed; manual inspection needed
  - Last known good version: commit SHA
  - Corruption type: newline collapse

## Verification
✓ All recovered files compile
```
