# Harness Demo Three-Improvements: Planning Enhancements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adopt two durable planning improvements from `coleam00/harness-engineering-demo`: pattern references in solution plans and constrained acceptance criteria format.

**Architecture:** Two related changes to the shared authored surface:
1. Add `Pattern reference:` field to Object Design section in solution plans, requiring architects to cite existing analogues
2. Add structured Acceptance Criteria section with four allowed forms (structural, gate, pattern, manual) instead of free-form prose
Both changes propagate to the solution architect agent and commit skill to enforce the format.

**Tech Stack:** Markdown (knowledge/template documents), Agent definitions (architect + commit skill)

---

## File Structure

```
profile-al-dev-shared/
  knowledge/
    solution-plan-template.md          # Update: add Pattern reference + Acceptance Criteria sections
  agents/
    al-dev-solution-architect.md       # Update: add pattern research step + constrained criteria requirement
  skills/
    al-dev-commit/SKILL.md             # Update: add acceptance criteria verification step
```

---

## Task 1: Update solution-plan-template.md — Add Pattern Reference Section

**Files:**
- Modify: `profile-al-dev-shared/knowledge/solution-plan-template.md:9-24`

- [ ] **Step 1: Read the current Object Design section**

The section currently spans lines 9-24 and shows object definitions without pattern references.

- [ ] **Step 2: Add Pattern reference field to each object type**

Update the template to include `Pattern reference:` line for Tables, Pages, Codeunits, and Enums. Pattern reference can be:
- A file path and line number (e.g., `src/Codeunit/CustomerCreditCheck.Codeunit.al:L45`)
- The phrase `none — [one-line rationale]` when no useful analogue exists

Edit the template to add the pattern reference line after the "Purpose:" line for each object type:

```markdown
## Solution Plan: [Feature Name]

### Overview
[1-2 paragraphs: what we're building, why this approach]

### Object Design

**Tables / Table Extensions:**
- Object ID 50xxx: "[Name]"
  Purpose: [1 sentence]
  Pattern reference: [file:line or "none — rationale"]
  Fields: [list key fields with IDs and types]

**Pages / Page Extensions:**
- Object ID 51xxx: "[Name]"
  Purpose: [1 sentence]
  Pattern reference: [file:line or "none — rationale"]
  Modifications: [what's being added/changed]

**Codeunits:**
- Object ID 52xxx: "[Name]" (Interface: "[Interface Name]")
  Purpose: [1 sentence]
  Pattern reference: [file:line or "none — rationale"]
  Key Methods: [list with signatures]

**Enums** (if any):
- Object ID 53xxx: "[Name]"
  Pattern reference: [file:line or "none — rationale"]
  Values: [list]
```

- [ ] **Step 3: Verify the edit preserves all original content**

Read the modified file to confirm:
- All original Object Design sections are present
- Pattern reference lines are added after Purpose (or at the start of each block for Enums)
- No original content was removed or corrupted

---

## Task 2: Update solution-plan-template.md — Add Acceptance Criteria Section

**Files:**
- Modify: `profile-al-dev-shared/knowledge/solution-plan-template.md:45-57` (end of template)

- [ ] **Step 1: Understand the current template ending**

The template currently ends with "Winning Approach Rationale" section (lines 45-57).

- [ ] **Step 2: Add Acceptance Criteria section before Winning Approach Rationale**

Insert a new `Acceptance Criteria` section that documents the required format. Add this section between "Implementation Notes" (line 42) and "Winning Approach Rationale" (line 45):

```markdown
### Acceptance Criteria

Use numbered criteria in one of four allowed forms:

**Structural check** — file or symbol existence:
1. `src/Codeunit/SalesPostingGuard.Codeunit.al` exists and contains `procedure ValidatePostingDate`
2. `src/PageExtension/SalesOrderExt.PageExt.al` contains reference to `SalesPostingGuard.ValidatePostingDate`

**Gate check** — tool exit code or existing skill gate:
3. `al-compile` exits 0 with no new errors in `.dev/compile-errors.log`

**Pattern check** — a required or forbidden pattern in changed code:
4. No `Error(StrSubstNo(` appears in new or modified files

**Manual check** — user or tester validation that cannot be machine-checked:
5. [manual] Posting is blocked when order date is before work date

Unlabelled prose criteria are not permitted. Each criterion must be numbered and use one of the four forms above.
```

- [ ] **Step 3: Verify content and structure**

Read the modified file to confirm:
- Acceptance Criteria section is present with clear examples of all four forms
- The section appears before "Winning Approach Rationale"
- All four allowed forms are documented with examples
- Line count is preserved or increased (no content loss)

---

## Task 3: Update al-dev-solution-architect.md — Add Pattern Research Step

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-solution-architect.md:43-64`

- [ ] **Step 1: Identify the Research phase section**

Read lines 43-64 which contain the current research phase guidance and evidence preference.

- [ ] **Step 2: Add pattern reference research sub-step**

Add a new sub-step after line 50 (after "AL semantic navigation" bullet) that requires pattern research for each object:

Edit the research phase to add this guidance:

```markdown
5. **Research phase (MEDIUM/COMPLEX only):**
   - Pattern references: For each object in the Object Design, locate the best existing
     analogue in the project using the strongest available evidence source: `AL LSP`
     when exposed by the active harness or adapter, otherwise `AL MCP`, otherwise
     scoped `text search`. Record the file path and line number as the `Pattern reference`.
     If no useful analogue exists, record `none` with a one-line rationale. This is not
     exact structural matching—only the best analogue the developer should inspect first.
   - AL semantic navigation: use `AL LSP` when the active harness exposes it
     for definitions, references, document symbols, hover/type information,
     and rename/refactor impact checks
   - Base app exploration: [rest of existing content]
```

- [ ] **Step 3: Verify the edit**

Read the modified file to confirm:
- The pattern reference research step is clearly added as a first research sub-bullet
- The evidence source preference (LSP > MCP > text search) is documented
- The distinction that this is not exact matching is clear
- All original research guidance is preserved

---

## Task 4: Update al-dev-solution-architect.md — Add Constrained Criteria Requirement

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-solution-architect.md:81-99` (Output Format section)

- [ ] **Step 1: Read the Output Format section**

Lines 81-99 describe the output format and detail level by complexity.

- [ ] **Step 2: Add constrained acceptance criteria requirement to Write output step**

Update the Write output section to add guidance on acceptance criteria format:

Find the line that says "Write to `.dev/$(date +%Y-%m-%d)-al-dev-plan-solution-plan.md`" and after the existing bullet list, add:

```markdown
Write to `.dev/$(date +%Y-%m-%d)-al-dev-plan-solution-plan.md`. 

For complete structure and template content, read `knowledge/solution-plan-template.md`. The solution plan must include:
- Executive summary
- Requirements analysis
- Design decisions with rationale
- Testability architecture (with interfaces, injection points, mocks)
- Implementation plan (files, steps, code templates)
- **Acceptance Criteria section:** Add a numbered `Acceptance Criteria` section where each
  criterion uses one of the allowed forms: structural, gate, pattern, or `[manual]`. Do not
  write free-form prose criteria. See `knowledge/solution-plan-template.md` for examples.
```

- [ ] **Step 3: Verify the edit**

Read the modified section to confirm:
- The acceptance criteria requirement is clearly stated
- The four allowed forms are referenced
- The prohibition on free-form prose is clear
- A pointer to the template for examples is included

---

## Task 5: Update al-dev-commit/SKILL.md — Add Acceptance Criteria Verification

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-commit/SKILL.md:156-161`

- [ ] **Step 1: Read the pre-commit checklist area**

Lines 156-161 describe the compile verification gate, just before the Step 5 section.

- [ ] **Step 2: Add acceptance criteria verification instruction**

Add a new step between the compile verification gate and Step 5 that references acceptance criteria. Add this new section after line 161:

```markdown

## Step 4b — Verify Acceptance Criteria (If Solution Plan Exists)

Check whether a solution plan exists:

```bash
PLAN=$(ls .dev/*-al-dev-plan-solution-plan.md 2>/dev/null | sort | tail -1)
```

If a solution plan file is found, read its Acceptance Criteria section. For each directly checkable criterion (structural, gate, pattern forms):

- **Structural criteria:** Verify that named files exist and contain named symbols (use `grep` or `al-compile` output)
- **Gate criteria:** Confirm that referenced gates (e.g., `al-compile`) exit 0
- **Pattern criteria:** Use `git diff --cached` to verify patterns do or do not appear in changed code

Do not treat `[manual]` criteria as automatic blockers. Surface any pending manual criteria as a note to the user: "Manual validation pending: [list]"

If verification of any directly checkable criterion fails, stop the commit workflow and report the failure to the user.

If no solution plan exists, skip this step and continue to Step 5.
```

- [ ] **Step 3: Verify the edit**

Read the modified file to confirm:
- The new Step 4b section is clearly added
- It references the solution plan location correctly
- It covers all three directly checkable forms (structural, gate, pattern)
- It explicitly exempts `[manual]` criteria from blocking
- The step is positioned before Step 5

---

## Task 6: Run Validation Scripts

**Files:**
- Test: No files modified; validation only

- [ ] **Step 1: Run agent validation**

Run the agent structure validator to ensure both modified agents are correctly formatted:

```bash
cd /Users/russelllaing/al-dev-shared
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
```

Expected output: Exit code 0, no errors for `al-dev-solution-architect.md`

- [ ] **Step 2: Run harness neutrality check**

Verify that no harness-specific tokens were accidentally introduced:

```bash
cd /Users/russelllaing/al-dev-shared
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Expected output: Exit code 0, no forbidden tokens found in modified files

- [ ] **Step 3: Report validation results**

If both validations exit 0:
- All changes are valid
- Solution plan template is well-formed
- Agent files have correct structure
- No harness-specific leakage in shared surface

If either validation fails, read the error output and fix the issue before committing.

---

## Task 7: Create Single Atomic Commit

**Files:**
- Modified: 
  - `profile-al-dev-shared/knowledge/solution-plan-template.md`
  - `profile-al-dev-shared/agents/al-dev-solution-architect.md`
  - `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`

- [ ] **Step 1: Stage all modified files**

```bash
cd /Users/russelllaing/al-dev-shared
git add profile-al-dev-shared/knowledge/solution-plan-template.md \
        profile-al-dev-shared/agents/al-dev-solution-architect.md \
        profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```

- [ ] **Step 2: Create commit with clear message**

```bash
cd /Users/russelllaing/al-dev-shared
git commit -m "docs: add pattern references and constrained acceptance criteria to planning

- Add Pattern reference field to Object Design section in solution-plan-template.md
- Add Acceptance Criteria section with four constrained forms to solution-plan-template.md
- Require pattern research step in al-dev-solution-architect.md Research phase
- Require constrained criteria format in al-dev-solution-architect.md Output Format
- Add acceptance criteria verification step to al-dev-commit/SKILL.md pre-commit checklist

Implements Change A (pattern references) and Change B (constrained acceptance criteria)
from Design: Harness Demo Three-Improvements (2026-05-28)."
```

- [ ] **Step 3: Verify commit was created**

```bash
git log --oneline -1
```

Expected: Shows the new commit with the message starting with `docs: add pattern references`

---

## Acceptance Criteria for This Plan

1. **Pattern reference field added to solution-plan-template.md** — Each object type block includes `Pattern reference:` line accepting file:line or "none — rationale"
2. **Acceptance Criteria section added to solution-plan-template.md** — New section documents four allowed forms with examples
3. **Pattern research step in al-dev-solution-architect.md** — Research phase explicitly requires pattern lookup with evidence source preference
4. **Constrained criteria requirement in al-dev-solution-architect.md** — Output Format section requires constrained criteria format
5. **Acceptance criteria verification in al-dev-commit/SKILL.md** — New Step 4b checks directly checkable criteria before commit
6. **No harness-specific tokens** — `validate_harness_neutrality.py` exits 0 on modified files
7. **Agent structure valid** — `validate-lens-agents.py` exits 0 for modified agents
8. **Single atomic commit created** — Git log shows one commit with all three files modified
9. **Spec requirements met** — All 10 acceptance criteria from the design spec are addressed in the implementation

---

## Notes

- **Scope:** This plan covers only Changes A and B from the spec; invocation-safety follow-up is deferred
- **Shared surface only:** All changes remain in the authored shared plugin surface; no projection changes needed
- **Validation:** Both `validate-lens-agents.py` and `validate_harness_neutrality.py` must pass before commit
