---
name: "al-dev-commit-preflight"
description: "Pre-flight lint and OOXML validation for staged commit files. Runs Python lint, trailing whitespace fixes, line-count corruption detection, and ZIP validation on OOXML files. Returns LINT_FIXES and OOXML_FAILURES. Dispatched by al-dev-commit (Step 9.5) before commit execution."
tools: ["execute", "read"]
---


# Agent: al-dev-commit-preflight

Run pre-flight validation on staged files before commit execution.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `APPROVED_PLAN` — approved groups and messages from analysis phase |

## Outputs

| Output | Description |
|--------|-------------|
| `LINT_FIXES` | Files re-staged after lint fixes (or `NONE`) |
| `OOXML_FAILURES` | OOXML files that failed ZIP validation (or `NONE`) |

⚠️ **CRITICAL:** Never use Write or Edit on staged source files. All fixes via Bash only. If a fix cannot be made via Bash, record as OOXML_FAILURE and stop.

## Phase: preflight

### Pre-flight Lint (Step 1)

For each approved group:
1. Capture line counts baseline: `git diff --cached --name-only | while IFS= read -r f; do [ -f "$f" ] || continue; printf '%s\t%d\n' "$f" "$(wc -l < "$f")" >> .git/.commit-baselines; done`
2. For every `.py` file: `ruff check --fix <file> && ruff format <file> && git add <file>`
3. Trailing whitespace: `git diff --cached --name-only | while IFS= read -r f; do perl -pi -e 's/[ \t]+$//' "$f"; git add "$f"; done`
4. Detect corruption by comparing post-lint line counts against baseline. If drastically shrunk, restore and halt.

⚠️ **Regex MUST be `[ \t]+$` (horizontal whitespace only).** Never use `[[:space:]]+$` or `\s+$` — those include `\n`, collapsing entire file into one line.

### OOXML Gate (Step 2)

For files with OOXML extensions (`.docx`, `.xlsx`, `.pptx`, `.odt`):
1. Run ZIP validation: `unzip -t <file> > /dev/null 2>&1`
2. If validation fails: record as OOXML_FAILURE, do not proceed to commit
3. Require human review before re-staging OOXML files

### Return Block (Step 3)

```text
LINT_FIXES: [file1, file2] (or NONE)
OOXML_FAILURES: [filename: reason] (or NONE)
```
