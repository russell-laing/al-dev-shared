# AL-Dev Compilation Efficiency & Context Management

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix compilation output bloat that caused context window exhaustion, reduce iterative compilation loops, and improve error categorization during AL development.

**Architecture:** 
- Move large compilation outputs from stdout to file-based logging (`.dev/compile-errors.log`)
- Enforce single-compile-per-module discipline in developer workflow
- Parse and categorize errors into meaningful groups (naming, schema, compilation, warnings)
- Add explicit context preservation checkpoints before overflow occurs
- Document schema mapping decisions in solution architect templates

**Tech Stack:** AL/BC development, shell scripting (bash), markdown-based skills/agents, MCP tools for AL symbol resolution

---

## Task Decomposition

**Files to modify:**
1. `~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/hooks/al-hook-compile.sh` — Suppress stdout, log to file
2. `~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/skills/al-dev-develop/SKILL.md` — Phase 5, 8, 9 updates + Phase 0.5 addition
3. `~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/agents/al-dev-solution-architect.md` — Extend template with schema mapping section

**Files to create:**
- `.tools/error-categorizer.py` — Helper script to parse and group compilation errors

---

### Task 1: Suppress Compilation Output in Hook Script

**Files:**
- Modify: `~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/hooks/al-hook-compile.sh`

- [ ] **Step 1: Read the current hook script**

```bash
cat ~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/hooks/al-hook-compile.sh
```

- [ ] **Step 2: Update hook to suppress stdout and log to file**

Replace the section that captures compiler output with file-based logging only:

```bash
#!/usr/bin/env bash
# al-hook-compile.sh — AL compilation hook for al-dev-develop

set -e

if [[ ! -f "app.json" ]]; then
    exit 0
fi

# Create .dev directory if it doesn't exist
mkdir -p .dev

# Run compilation with output redirected to file only
al-compile --output .dev/compile-errors.log

# Exit with success; errors are logged to file, not stdout
exit 0
```

- [ ] **Step 3: Verify the script is executable**

```bash
chmod +x ~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/hooks/al-hook-compile.sh
```

- [ ] **Step 4: Commit the hook change**

```bash
git -C /Users/russelllaing/al-dev-shared add hooks/al-hook-compile.sh
git -C /Users/russelllaing/al-dev-shared commit -m "fix(hook): suppress al-compile stdout, log to file only

- Move full compiler output from stderr/stdout to .dev/compile-errors.log
- Prevents 40KB+ logs flooding message history on each compile attempt
- Reduces context window exhaustion in compile-heavy development sessions"
```

---

### Task 2: Add Error Categorizer Utility Script

**Files:**
- Create: `.tools/error-categorizer.py` (used by al-dev-develop Phase 9)
- Modify: `~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/skills/al-dev-develop/SKILL.md` (reference this script)

- [ ] **Step 1: Create error categorizer script**

```python
#!/usr/bin/env python3
"""
Parse AL compilation errors from .dev/compile-errors.log and group by category.
Outputs a markdown summary suitable for message reporting.
"""

import sys
import re
from collections import defaultdict

def categorize_errors(log_file):
    """Read compile log and return errors grouped by category."""
    
    categories = {
        'naming_violations': [],    # AS0011, AS0012
        'schema_errors': [],         # E2007, E2008 (field/table not found)
        'compilation_errors': [],    # General compilation failures
        'warnings': []               # Minor issues
    }
    
    try:
        with open(log_file, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        return categories, "No compile errors found"
    
    lines = content.split('\n')
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
        
        # Naming violations
        if 'AS0011' in line or 'AS0012' in line:
            categories['naming_violations'].append(line.strip())
        # Schema errors (field/table not found)
        elif 'E2007' in line or 'E2008' in line or 'not found' in line.lower():
            categories['schema_errors'].append(line.strip())
        # Warnings
        elif 'warning' in line.lower():
            categories['warnings'].append(line.strip())
        # Compilation errors
        elif 'error' in line.lower():
            categories['compilation_errors'].append(line.strip())
    
    return categories, None

def format_summary(categories):
    """Format categorized errors into markdown summary."""
    
    summary = []
    
    for category_name, errors in categories.items():
        if not errors:
            continue
        
        # Format category name as title
        title = category_name.replace('_', ' ').title()
        summary.append(f"\n**{title}:** {len(errors)} issue(s)")
        
        # Show first 3 errors per category, abbreviated
        for error in errors[:3]:
            # Truncate long lines
            if len(error) > 120:
                error = error[:120] + "…"
            summary.append(f"  - {error}")
        
        if len(errors) > 3:
            summary.append(f"  - ... and {len(errors) - 3} more (see .dev/compile-errors.log)")
    
    return "\n".join(summary) if summary else "No errors found"

if __name__ == '__main__':
    log_path = sys.argv[1] if len(sys.argv) > 1 else '.dev/compile-errors.log'
    categories, error = categorize_errors(log_path)
    
    if error:
        print(error)
    else:
        print(format_summary(categories))
```

- [ ] **Step 2: Make script executable and save to project**

```bash
chmod +x ~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/.tools/error-categorizer.py
```

Note: Save this script at `.tools/error-categorizer.py` in the al-dev-shared plugin so it's available to subagents.

- [ ] **Step 3: Commit the utility**

```bash
git -C /Users/russelllaing/al-dev-shared add .tools/error-categorizer.py
git -C /Users/russelllaing/al-dev-shared commit -m "feat(tool): add error-categorizer for compilation output parsing

Parses .dev/compile-errors.log and groups errors by type:
- Naming violations (AS0011, AS0012)
- Schema errors (field/table not found)
- Compilation errors
- Warnings

Outputs markdown summary for message reporting instead of raw logs."
```

---

### Task 3: Update al-dev-develop Phase 5 (Batch-Compile Discipline)

**Files:**
- Modify: `~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, Phase 5 section

- [ ] **Step 1: Read Phase 5 of al-dev-develop skill**

```bash
grep -A 30 "## Phase 5:" ~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

- [ ] **Step 2: Add batch-compile discipline instruction to Phase 5 developer spawn prompt**

Update the developer spawn instruction to include:

```markdown
**Compilation Discipline (MANDATORY):**
- Do NOT run `al-compile` after each function or small change
- Write all code for your assigned module (30–50 lines of code) BEFORE compiling
- When code is complete, run `al-compile --output .dev/compile-errors.log` ONCE
- Do NOT iterate with compile-fix-compile-fix cycles; batch your fixes after the single compile run
- Log files: Read errors from `.dev/compile-errors.log`, NOT stdout — errors are logged to file only
```

This instruction should be added to the developer agent spawn in Phase 5 (where developers are assigned modules).

- [ ] **Step 3: Commit Phase 5 update**

```bash
git -C /Users/russelllaing/al-dev-shared add skills/al-dev-develop/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(skill): enforce batch-compile discipline in Phase 5

Developers now write complete modules before compiling once, reducing
iterative compilation overhead and token waste on redundant error reporting."
```

---

### Task 4: Update al-dev-develop Phase 8 (Error Summarization)

**Files:**
- Modify: `~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, Phase 8 section

- [ ] **Step 1: Read current Phase 8 logic**

Phase 8 currently handles the post-development compilation check. Update it to:

```markdown
## Phase 8: Compilation & Error Handling

**Execution:**
1. **Read** `.dev/compile-errors.log` (compiled by Phase 5 batch compile)
2. **Categorize** errors using: `python3 .tools/error-categorizer.py .dev/compile-errors.log`
3. **Report** the summary to conversation (NOT raw output)
4. **If no errors:** Proceed to Phase 9 (code review)
5. **If errors exist:** 
   - Group by category (naming, schema, compilation, warnings)
   - Assign fixes to reviewers based on error type
   - Compile once more after all fixes applied
```

- [ ] **Step 2: Commit Phase 8 update**

```bash
git -C /Users/russelllaing/al-dev-shared add skills/al-dev-develop/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(skill): use error categorization in Phase 8 compilation check

- Read compilation output from .dev/compile-errors.log
- Parse and group errors by category (naming, schema, etc)
- Report summaries instead of raw 40KB logs
- Prevents context window exhaustion in compile-heavy workflows"
```

---

### Task 5: Update al-dev-develop Phase 9 (Error Categorization in Code Review)

**Files:**
- Modify: `~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, Phase 9 section

- [ ] **Step 1: Read current Phase 9 (Code Review) logic**

Phase 9 is the code review and quality checks phase. Add error categorization here:

```markdown
## Phase 9: Code Review & Quality Report

**Error Summary Section:**
Before reviewers analyze code, include this in the code review report:

**Compilation Issues by Category:**
- Extract from `.dev/compile-errors.log` using error categorizer
- Separate: naming violations, schema errors, compilation errors, warnings
- For each category, show:
  - Count
  - 2–3 representative examples (truncated)
  - Suggested fix pattern
  - Files affected

**Example format:**
```
## Compilation Status

**Naming Violations (5 fields):**
- Fields missing 'AC' prefix in Customer.Table.al:45-89
- Suggested fix: Rename fields to AC[FieldName] pattern
- Files: Customer.Table.al

**Schema Errors (2 references):**
- Field "G/L Register No." not found in G/L Entry table
- Suggested fix: Use "Entry No." instead (primary key exists)
- Files: JournalEntryAllocation.Table.al:123
```

This structure helps reviewers prioritize fixes by category and understand root causes quickly.
```

- [ ] **Step 2: Commit Phase 9 update**

```bash
git -C /Users/russelllaing/al-dev-shared add skills/al-dev-develop/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(skill): add error categorization to Phase 9 code review report

Code review now includes structured error summary:
- Errors grouped by type (naming, schema, compilation, warnings)
- Truncated examples per category instead of raw logs
- Suggested fixes for each category
- Improves root-cause identification during review"
```

---

### Task 6: Add Phase 0.5 (Context Preservation Checkpoint)

**Files:**
- Modify: `~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, add new Phase 0.5

- [ ] **Step 1: Insert new Phase 0.5 after Phase 0 (Setup)**

Add a new phase before Phase 1:

```markdown
## Phase 0.5: Context Preservation Checkpoint

**Purpose:** Before development starts, create a resumable checkpoint in case context compaction occurs.

**Execution:**
1. Check if `.dev/resume-context.md` exists
   - If yes, read it and offer resume/restart option to user
   - If restart chosen, delete checkpoint and proceed to Phase 1
   - If resume chosen, inject checkpoint state into Phase 1 restart

2. If starting fresh, write `.dev/resume-context.md`:
   ```markdown
   # Development Resume Checkpoint — [ISO-8601 timestamp]

   ## Current State
   - **Phase:** 1 (Design & Module Planning)
   - **Modules assigned:** [List of module assignments by developer]
   - **Last compilation:** [Timestamp or "not yet run"]
   - **Error summary:** [If any errors from previous compile]
   - **Developer progress:**
     - Developer A: [Module name, lines written, current task]
     - Developer B: [Module name, lines written, current task]

   ## Resumption Instructions
   If context overflow occurs, inject this section into the next session's developer spawn:
   > "Previous session checkpoint: [current state details]. Resume from this point."

   ## Next Steps
   - [Task 1]
   - [Task 2]
   - [Task 3]
   ```

3. **Update checkpoint after each phase completes** — append new state before proceeding to next phase

**Why this helps:**
- Explicit record of where development left off
- Prevents asking developers to re-explain design decisions after compaction
- Enables instant resumption without re-planning

**When to enable:** After first context compaction is detected
```

- [ ] **Step 2: Commit Phase 0.5 addition**

```bash
git -C /Users/russelllaing/al-dev-shared add skills/al-dev-develop/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(skill): add Phase 0.5 context preservation checkpoint

Before development begins, create .dev/resume-context.md with:
- Current phase and module assignments
- Last compilation status and errors
- Developer progress per module
- Resumption instructions

On context overflow, this checkpoint provides instant context recovery
without re-planning or re-explaining design decisions."
```

---

### Task 7: Extend Solution Architect Agent Template with Schema Mapping Decisions

**Files:**
- Modify: `~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/agents/al-dev-solution-architect.md`

- [ ] **Step 1: Read the solution architect agent**

```bash
cat ~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/agents/al-dev-solution-architect.md
```

- [ ] **Step 2: Find the solution plan template section**

Look for the markdown template that solution architects use to write solution plans (usually after the "## Solution Plan" heading or similar).

- [ ] **Step 3: Add Schema Mapping Decisions section to template**

Add this section after "## Architecture" or "## Technical Design":

```markdown
## Schema Mapping Decisions

Document all external field/table references with existence verification:

| Field/Table | Source | Exists? | Rationale | Risk |
|-----------|--------|---------|-----------|------|
| G/L Register No. | G/L Entry | NO | Use "Entry No." (PK) instead | Low |
| Customer Type | Customer | YES | Link to code in AC_CUSTOMER_TYPE | Low |
| Document No. | Purch. Header | YES | Primary document identifier | Low |

**Format per mapping:**
- **[Field Name]** in [Source Table]: [YES/NO]
  - Alternative: [If field doesn't exist, what should be used?]
  - Rationale: [Why this choice is correct]
  - Risk: [Low/Medium/High — data integrity implications]

**Why this section matters:**
- Developers verify field existence against AL symbols BEFORE writing code
- Prevents compile errors from field misreferences mid-implementation
- Documents design choices for future reference
- Speeds up schema review during code review phase
```

- [ ] **Step 4: Commit the agent template update**

```bash
git -C /Users/russelllaing/al-dev-shared add agents/al-dev-solution-architect.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(agent): add Schema Mapping Decisions to solution plan template

Solution architects now document all external field/table references:
- Existence verification (YES/NO)
- Alternatives for non-existent fields
- Design rationale
- Data integrity risk assessment

Prevents field-not-found errors at development time and clarifies
schema design decisions for the implementation team."
```

---

### Task 8: Final Integration Verification

**Files:**
- No files created; verification only

- [ ] **Step 1: Verify all commits are in place**

```bash
git -C /Users/russelllaing/al-dev-shared log --oneline -10
```

Expected output shows 7 new commits (hook fix, error categorizer, Phase 5, Phase 8, Phase 9, Phase 0.5, architect template).

- [ ] **Step 2: Verify error categorizer is executable**

```bash
ls -la ~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/.tools/error-categorizer.py
file ~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/.tools/error-categorizer.py
```

Expected: File is regular text, executable bit set.

- [ ] **Step 3: Verify hook script syntax**

```bash
bash -n ~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/hooks/al-hook-compile.sh
```

Expected: No output (syntax check passes).

- [ ] **Step 4: Test error categorizer with sample input**

```bash
# Create sample compile-errors.log
cat > /tmp/test-compile.log << 'EOF'
error AS0011: Field 'MyField' is missing required 'AC' prefix
error E2007: Field 'G/L Register No.' not found in table 'G/L Entry'
warning: Unused variable 'TempVar'
EOF

# Run categorizer
python3 ~/.claude/plugins/cache/claude-plugins-official/profile-al-dev-shared/.tools/error-categorizer.py /tmp/test-compile.log
```

Expected output:
```
**Naming Violations:** 1 issue(s)
  - error AS0011: Field 'MyField' is missing required 'AC' prefix

**Schema Errors:** 1 issue(s)
  - error E2007: Field 'G/L Register No.' not found in table 'G/L Entry'

**Warnings:** 1 issue(s)
  - warning: Unused variable 'TempVar'
```

- [ ] **Step 5: Commit any test artifacts cleanup (if needed)**

```bash
rm /tmp/test-compile.log
```

---

## Summary

**What was fixed:**

1. **Hook script** — Suppressesstdout, logs full output to file only
2. **Batch-compile discipline** — Phase 5 now instructs developers to write complete modules before compiling
3. **Error categorization** — Phase 8 and 9 parse errors into structured categories (naming, schema, compilation, warnings) instead of raw logs
4. **Context preservation** — Phase 0.5 checkpoints development state before overflow occurs
5. **Schema mapping documentation** — Solution architect template now requires explicit field/table existence verification

**Expected outcome:**
- Prevents 40KB+ logs from flooding conversation history
- Reduces compilation iterations from 4 per session to 1–2 (saves ~30–40% of development tokens)
- No more context window exhaustion from compiler output bloat
- Developers can resume interrupted sessions instantly with checkpoint context
- Schema errors caught during planning, not during implementation
