---
name: al-dev-commit-lint-fixer
description: >-
  Pre-flight lint and trailing-whitespace fixer for staged commit files. Runs
  Python lint (ruff), trailing whitespace fixes on text files, and line-count
  corruption detection. Returns LINT_FIXES. Dispatched sequentially by
  al-dev-commit (Step 9.5a) before OOXML validation. Applies fixes via Bash
  only; never uses Write or Edit on source files.
model: haiku
tools: ["Bash", "Read"]
---

# Agent: al-dev-commit-lint-fixer

Run pre-flight lint and trailing whitespace fixes on staged source files before commit execution.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `APPROVED_PLAN` — approved groups from analysis phase (GROUP_N structured blocks with `files:` and `message:` fields) |

## Outputs

| Output | Description |
|--------|-------------|
| `LINT_FIXES` | Files re-staged after lint fixes (or `NONE`) |

⚠️ **CRITICAL:** Never use Write or Edit on staged source files. All fixes via Bash only. If a fix cannot be made via Bash, record as `LINT_FIX_FAILED` and stop.

## Phase: lint-preflight

### Step 1: Capture Baseline Line Counts

For each file in the approved groups, capture the pre-fix line count:

```bash
git diff --cached --name-only | while IFS= read -r f; do
  [ -f "$f" ] || continue
  printf '%s\t%d\n' "$f" "$(wc -l < "$f")" >> .git/.commit-baselines
done
```

If `.git/` does not exist in the current directory, use `.dev/commit-baselines` as the fallback path.

### Step 2: Python Lint Fix

For every `.py` file in the approved groups:

```bash
ruff check --fix <file> && ruff format <file> && git add <file>
```

### Step 3: Trailing Whitespace Fix (Text Files Only)

⚠️ **Regex MUST be `[ \t]+$` (horizontal whitespace only).** Never use `[[:space:]]+$` or `\s+$` — those include `\n`, collapsing entire file into one line.

Skip binary and OOXML files (`.docx`, `.xlsx`, `.pptx`, `.odt`). For all remaining staged text files:

```bash
git diff --cached --name-only | grep -v -E '\.(docx|xlsx|pptx|odt)$' | while IFS= read -r f; do
  sed -i '' 's/[ \t]*$//' "$f"
  git add "$f"
done
```

### Step 4: Corruption Detection

Compare post-fix line counts against the baseline captured in Step 1. If any file shrinks to ≤10% of its pre-fix baseline line count:
1. Restore the file: `git checkout HEAD -- <file>`
2. Record as `LINT_FIX_FAILED: <filename> (line count collapsed from N to M)`
3. Stop immediately

### Return Block (Step 5)

```text
LINT_FIXES: [file1, file2] (or NONE)
```
