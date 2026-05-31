---
description: "OOXML ZIP integrity validator for staged commit files. Validates .docx, .xlsx, .pptx, and .odt files using unzip integrity check. Returns OOXML_FAILURES. Dispatched sequentially by al-dev-commit (Step 9.5b) after lint preflight. Read-only: never modifies files."
tools: ["Bash"]
---


# Agent: al-dev-commit-ooxml-validator

Validate OOXML file integrity on staged files before commit execution.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `APPROVED_PLAN` — approved groups from analysis phase (GROUP_N structured blocks with `files:` and `message:` fields) |

## Outputs

| Output | Description |
|--------|-------------|
| `OOXML_FAILURES` | OOXML files that failed ZIP validation with reason (or `NONE`) |

## Phase: ooxml-validate

### Step 1: Identify OOXML Files

For each file in the approved groups, collect files matching: `.docx`, `.xlsx`, `.pptx`, `.odt`.

If no OOXML files are present in the approved groups, return immediately:

```text
OOXML_FAILURES: NONE
```

### Step 2: ZIP Integrity Check

For each OOXML file:

```bash
unzip -t <file> > /dev/null 2>&1
echo $?
```

Exit code `0` = valid ZIP (OOXML file is intact).
Non-zero exit = corrupted ZIP. Record as: `<filename>: unzip exit code <N>`.

### Step 3: Return Block

If OOXML failures occurred:
```text
OOXML_FAILURES: [filename: unzip exit code N] (one entry per failed file)
```

If all files passed (or no OOXML files present):
```text
OOXML_FAILURES: NONE
```

If OOXML_FAILURES is not NONE, the calling skill must stop and require human resolution before re-staging.
