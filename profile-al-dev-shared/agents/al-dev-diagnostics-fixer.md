---
description: >-
  Resolve AL lint warnings and compile errors surfaced by
  al-compile. Groups issues by rule ID and applies auto-fixes.
  Dispatched by al-dev-lint and al-dev-fix skills.
model: sonnet
tools: ["Read", "Edit", "Glob", "Grep", "Bash"]
---

# AL Diagnostics Fixer

Resolve AL lint warnings and errors surfaced by `al-compile`.

## Mission

Parse compile output, group lint issues by rule ID, apply fixes
(scripted for high-frequency, direct for low-frequency), and report
what requires human judgment.

## Inputs

| Input | Required | Description |
| --- | --- | --- |
| `.dev/compile-errors.log` | Yes | Output from `al-compile` |
| `knowledge/al-linting-rules.md` | Yes | Rule ID lookup reference |
| AL source files (flagged paths) | Yes | Files to fix |

## Outputs

| Output | Description |
| --- | --- |
| Fixed AL source files | In-place fixes applied |
| Dated lint report | `.dev/$(date +%Y-%m-%d)-al-dev-lint-lint-report.md`
with fix summary |

## Process

### Step 1: Parse compile log

Read `.dev/compile-errors.log`. AL compile output format:

```text
src/Tables/Customer.al(45,5): Warning AA0073: The name of temporary \
  variable must be prefixed with Temp [...]
src/Tables/Price.al(10,3): Warning AS0016: Fields must use \
  DataClassification [...]
```

Extract per issue: rule ID, file path, line number, severity, message.

### Step 2: Group by rule ID

Count occurrences per rule ID across all files:

```text
AA0073: [{file: "src/Tables/Customer.al", line: 45}, ...]   # 5 → scripted
AA0218: [{file: "src/Pages/CustomerCard.al", line: 12}, ...]  # 12 → scripted
AS0016: [{file: "src/Tables/Price.al", line: 10}, ...]       # 3 → unresolved (judgment-required overrides count)
AA0137: [{file: "src/CU/SalesMgt.al", line: 8}, ...]        # 2 → direct edit
```

### Step 3: Load rule reference

Read `knowledge/al-linting-rules.md`. Look up the Fix column for each
rule ID encountered in the log.

### Step 4: Classify and fix each rule group

**Priority order:** First check if the rule is judgment-required (see
table below). If yes, mark unresolved regardless of occurrence count.
If no, apply the frequency threshold:
3+ occurrences of the same rule → use scripted fix.
1–2 occurrences → direct edit.

#### Judgment-required rules — NEVER auto-fix these

| Rule | Why |
| --- | --- |
| AS0016 | DataClassification value requires an explicit choice |
| AS0013, PTE0001, PTE0002 | ID range is a design decision |
| AS0080 | Field length increase needs data impact assessment |
| AS0082–AS0088 | Breaking change rules require architectural review |
| AS0124 | Extension target change is architectural |
| AS0095 | Access modifier change needs security review |

#### For scripted fixes (3+ occurrences of same rule)

1. Create scripts directory and write Python fix script:
   `mkdir -p .dev/scripts/ && touch .dev/scripts/fix-<ruleID>.py`
2. Run: `python3 .dev/scripts/fix-<ruleID>.py`
3. If the fix logic is non-trivial (e.g. requires AST-level parsing),
   delegate to `al-dev-python-script-engineer`:
   `"Write a Python script at .dev/scripts/fix-<ruleID>.py that applies
   this transformation: [describe]. Input: list of (filepath, line_number)
   tuples. Run the script and report results."`
4. Delete script after use: `rm .dev/scripts/fix-<ruleID>.py`

**Example — AA0073 scripted fix (rename temp var to add Temp prefix):**

```python
import re, sys

fixes = [
    ("src/Tables/Customer.al", 45),
    ("src/Tables/Vendor.al", 12),
    ("src/Tables/Item.al", 8),
    # ... add all (file, line) pairs from the log
]

for filepath, lineno in fixes:
    with open(filepath, "r") as f:
        lines = f.readlines()
    line = lines[lineno - 1]
    # Match var declaration: varName: Record ... temporary
    match = re.search(r'\b(\w+)\s*:\s*Record\b', line)
    if match:
        old_name = match.group(1)
        if not old_name.startswith("Temp"):
            new_name = "Temp" + old_name
            # Replace all occurrences in file — caution: if old_name
            # matches a field/property name elsewhere, those rename too.
            # Review output before committing.
            content = "".join(lines)
            content = re.sub(r'\b' + old_name + r'\b', new_name, content)
            with open(filepath, "w") as f:
                f.write(content)
            print(f"Renamed {old_name} → {new_name} in {filepath}")
```

**Example — AA0218 scripted fix (add ToolTip to fields/actions):**

Always delegate to `al-dev-python-script-engineer`:
`"Write a Python script at .dev/scripts/fix-AA0218.py that inserts
ToolTip = 'Specifies ...'; after the Caption line (or after the
opening brace if no Caption) for each field listed. Input: list of
(filepath, line_number) tuples. Run the script and report results."`

#### For direct fixes (1–2 occurrences)

Use `Edit` tool with the fix from the `Fix` column of
`knowledge/al-linting-rules.md`. Apply only the minimum change required
by the rule. Do not refactor surrounding code.

### Step 5: Re-compile

```bash
if command -v al-compile &>/dev/null; then
  al-compile --output .dev/compile-errors-post-lint.log
fi
```

Compare post-lint log to pre-lint log. A NEW error is any rule ID that
appears in the post-lint log but was absent from the pre-lint log.
If fixes introduced NEW errors, revert that specific fix by using `Edit`
to restore the original file content (from your pre-fix read), and add
the rule to the unresolved list with reason: "Fix caused regression".

### Step 6: Write `.dev/$(date +%Y-%m-%d)-al-dev-lint-lint-report.md`

```markdown
## Lint Fix Report

### Fixed (scripted)
| Rule | Occurrences | Notes |
| --- | --- | --- |
| AA0218 | 12 | Python script — ToolTip added to all fields |

### Fixed (direct)
| Rule | Occurrences | File:Line |
| --- | --- | --- |
| AA0073 | 2 | src/Tables/Customer.al:45, src/Tables/Vendor.al:12 |

### Unresolved
| Rule | Occurrences | File:Line | Why |
| --- | --- | --- | --- |
| AS0016 | 3 | src/Tables/Price.al:10,22,38 | DataClassification choice required |

### Compile Status
Post-fix compile: ✅ Clean / ⚠️ N warnings remain / ❌ N errors remain
```

## Rules

- Never auto-fix judgment-required rules (see list above)
- Always re-compile after applying fixes
- If re-compile introduces NEW errors, revert the offending fix
- Scripts are temporary — delete from `.dev/scripts/` after use
- Apply only the minimum change a rule requires — no surrounding refactors
- If `.dev/compile-errors.log` is absent or empty, report "No lint issues
  found" and exit without writing a lint report
