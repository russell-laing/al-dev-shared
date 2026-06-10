---
name: audit-knowledge-quality
description: >-
  Audit knowledge files for stub sections and structural issues. Dispatches
  parallel agents for large audit scopes (4+ files) and optionally provides fix
  guidance for HIGH-severity findings when the user opts in after reporting.
argument-hint: "[--path <directory>] [--verbose]"
workflow:
  stage: derive
  invoked-by: user
  repeatable: true
  inputs:
    - profile-al-dev-shared/knowledge/
  outputs:
    - docs/al-dev-knowledge-quality.md
  next: [fix-knowledge-quality]
---

# Audit Knowledge Quality

Review all knowledge files in `profile-al-dev-shared/knowledge/` for stub sections, thin content, and structural issues.
After reporting, this audit optionally provides fix guidance for HIGH-severity findings when the user opts in; it does not edit files autonomously.

## Purpose

Detects knowledge files that are referenced by agents for operational guidance but contain incomplete or thin section bodies. Complements the automated validator run at commit time by providing semantic context for why sections are stubs and what content should be added.

## Your Mission

1. Run the structural validator to identify potential stubs
2. For each flagged file, read it and the agent/skill that references it
3. Understand what content is missing or incomplete
4. Write findings to `docs/al-dev-knowledge-quality.md` with recommendations
5. Offer the user targeted fixes

## Implementation

### Phase 1: Discover Issues

```bash
VALIDATOR="$(find ~/.claude/plugins -name "validate-knowledge-quality.py" 2>/dev/null | head -1)"
if [ -z "$VALIDATOR" ]; then
  echo "Error: validate-knowledge-quality.py not found"
  exit 1
fi
python3 "$VALIDATOR" --path "profile-al-dev-shared/knowledge" --verbose
```

Extract flagged files and issue codes from output. Group by issue type: [THIN], [NO-CODE], [DEAD-REF].

### Phase 2: Choose analysis path

#### Progress Tracking

Before analyzing any file, create one task per flagged file using `TaskCreate` named `[issue-type] [filename]`. Update each task to `in_progress` when analysis begins, `completed` when the file analysis is written to findings.

#### Decision

Count the flagged files and choose the execution path with one threshold-driven
decision:

- **4 or more flagged files AND no ordering dependencies among them** → parallel path (Phase 2b, Parallel Exploration).
- **Otherwise** (3 or fewer flagged files, or any ordering dependency between flagged files) → sequential path (Phase 2b, Sequential Analysis).

### Phase 2b: Analyze (parallel or sequential)

#### Parallel Exploration (4+ files)

Invoke `superpowers:dispatching-parallel-agents` (if parallel dispatch is unavailable, use the sequential path instead). Dispatch one Explore subagent per file to: read the knowledge file, search for referencing agent/skill, and run the gap/severity assessment (steps 1–4). Each subagent must return YAML with fields: `{file, issue_type, gap_description, severity}`. Collect all records before proceeding to Phase 3.

#### Sequential Analysis (≤3 files or fallback)

For each flagged file:

1. **Read the file** — Understand its structure and current content
2. **Read the referencing agent/skill** — Find where the file is referenced and what guidance it's supposed to provide (search `.md` files in `profile-al-dev-shared/agents/` and `profile-al-dev-shared/skills/` for references to the knowledge file)
   - If no referencing agent or skill is found, note the file as orphaned with severity LOW.
3. **Understand the gap** — Determine why the section is flagged:
   - **[THIN]:** Is the section intentionally brief (overview/summary)? Or is it a topic that SHOULD have more content?
   - **[NO-CODE]:** The heading implies a pattern/example/usage. What code examples should be in the body?
   - **[DEAD-REF]:** Is the referenced file truly missing, or is the reference malformed?

4. **Assess severity:**
   - **HIGH:** Agent explicitly references the file for guidance it doesn't contain (e.g., "Reference knowledge/X.md for examples"). Missing content blocks the agent.
   - **MEDIUM:** File is referenced but content gap is incomplete/shallow (agent can work around it).
   - **LOW:** False positive (file is intentionally brief) or formatting issue (easily fixed).

### Phase 3: Write Findings Report

Write to `docs/al-dev-knowledge-quality.md` with structure:

```markdown
# Knowledge File Quality Report

Generated: [timestamp]
Issues: [count by severity]

## HIGH Severity (Blocks Agent Guidance)

- **File:** knowledge/X.md
  - **Reference:** `agents/Y.md:NN` — agent explicitly defers to this file
  - **Issue:** [THIN|NO-CODE|DEAD-REF] — specific detail
  - **Missing Content:** [What should be in the section]
  - **Fix:** [Concrete recommendation]

## MEDIUM Severity (Incomplete Guidance)

[Same structure as HIGH]

## LOW Severity (Minor/False Positives)

[Same structure]

---

## Fix Recommendations

### High Priority
[Actionable next steps for HIGH issues]

### Medium Priority
[Actionable next steps for MEDIUM issues]
```

After the HIGH findings narrative, append a machine-readable task block:

```yaml
## High-Priority Fix Tasks
<!-- auto-generated by /audit-knowledge-quality — consumed by /fix-knowledge-quality -->
tasks:
  - file: <exact-path-to-knowledge-file>
    issue_type: <THIN|NO-CODE|DEAD-REF>
    description: <one-line description of the issue>
    suggested_action: <concrete fix instruction>
```

One entry per HIGH issue. Use the exact file path from the finding. Do not include
MEDIUM or LOW issues in this block.

### Phase 4: Offer Fixes

After writing the report:

1. Print: `Knowledge quality report written to docs/al-dev-knowledge-quality.md`
2. Ask the user: "Would you like to fix any of these issues?"
3. If yes, present a structured list of concrete fix instructions, one per HIGH issue

## Output Format

```text
## Knowledge File Quality Audit

Scanning profile-al-dev-shared/knowledge/ for structural issues...

FINDINGS SUMMARY:
- HIGH (blocks agent guidance): N
- MEDIUM (incomplete): N  
- LOW (minor/false positives): N

Report written to: docs/al-dev-knowledge-quality.md

[Top 3 HIGH issues listed]

Run `cat docs/al-dev-knowledge-quality.md` to see full report.
```

## When to Run

- After `/audit-knowledge-quality` is invoked (user-triggered)
- Periodically (e.g., before major plugin releases)
- After significant knowledge file updates
- If the `/al-dev-commit` advisory surfaces knowledge warnings

## Success Criteria

✅ All HIGH severity findings have concrete fix recommendations  
✅ False positives (LOW severity) are clearly marked and explained  
✅ Report is actionable — user can immediately address MEDIUM/HIGH issues  
✅ DEAD-REF issues are investigated (not every broken link is a real problem)
