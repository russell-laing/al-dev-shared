# Agent Quality Audit Fix Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement all 65 quality findings from the agent audit (29 High, 26 Medium, 10 Low severity), removing harness-specific notation and fixing structural, clarity, and bloat issues.

**Architecture:** Create new knowledge files for code examples, templates, and reusable content; update each agent to reference these files instead of duplicating content inline. Fix structural violations (sections >30 lines, >6 top-level sections) by moving content to knowledge files or collapsing sections. Correct prompt clarity issues (undefined variables, tool mismatches, naming inconsistencies). Remove or replace harness-specific notation.

**Tech Stack:** Markdown agent definitions, knowledge files, agent tool lists.

---

## Knowledge Files to Create

### Task 1: Create knowledge files for agent-referenced examples and templates

**Files:**
- Create: `profile-al-dev-shared/knowledge/al-developer-patterns.md`
- Create: `profile-al-dev-shared/knowledge/documentation-rtm-guide.md`
- Create: `profile-al-dev-shared/knowledge/script-engineer-conventions.md`
- Create: `profile-al-dev-shared/knowledge/security-review-examples.md`
- Create: `profile-al-dev-shared/knowledge/performance-review-examples.md`
- Create: `profile-al-dev-shared/knowledge/code-review-patterns.md`
- Create: `profile-al-dev-shared/knowledge/release-notes-template.md`
- Create: `profile-al-dev-shared/knowledge/interview-question-bank.md`

- [ ] **Step 1: Create al-developer-patterns.md**

This file consolidates AL code patterns, error handling, and anti-patterns for the developer agent.

```markdown
# AL Developer Patterns and Conventions

Referenced by: `al-dev-developer` agent

## Standard AL Patterns

### RecordRef Operations
Pattern for operations on record references with error handling.

### Query Performance Best Practices
When writing queries, use filters to reduce record set scope; avoid FINDSET in loops.

## Common AL Mistakes to Avoid

### Incorrect Event Subscriber Signature
Do not use incompatible parameter types.

### Performance Anti-Pattern: N+1 Queries
Use batch operations instead of record-by-record processing.

## Error Handling Rules

### String Substitution with Labels
Use `Error(label, args)` instead of `Error(StrSubstNo(...))` to satisfy AA0231.

### User-Facing Errors
Wrap in Error() function with user-friendly message text.
```

- [ ] **Step 2: Create documentation-rtm-guide.md**

This file consolidates documentation generation guidance, RTM handling, and folder structure.

```markdown
# Documentation RTM Guide

Referenced by: `al-dev-docs-writer` agent

## RTM Handling

### Status Inference
Infer RTM status from existing doc structure and codebase state.

### Token Parsing
Parse RTM tokens from markdown frontmatter or comment blocks.

### Documentation Output
RTM documentation goes to the standard folder (docs/ or wiki/).

### RTM Rules
Follow these rules when generating documentation:
- Status tokens must match the codebase state
- Document all public APIs
- Update status when implementation changes

## Folder Structure

### docs/ Folder
Use for technical and API documentation.

### wiki/ Folder
Use for conceptual and architectural documentation.
```

- [ ] **Step 3: Create script-engineer-conventions.md**

This file consolidates script conventions, examples, and language selection guidance.

```markdown
# Script Engineer Conventions

Referenced by: `al-dev-script-engineer` agent

## Script Conventions (follow strictly)

### Async-First Design
Write async code patterns; use proper concurrency primitives.

### Protocol-Based Integration
Scripts must export structured output (JSON/CSV) that parses cleanly.

### Strict Typing
Define input/output schemas; validate at boundaries.

## Toolkit Reference

The `al-analysis-toolkit` is optional:
```bash
TOOLKIT_PATH=$(find ~ -name "al-analysis-toolkit" -maxdepth 5 -type d 2>/dev/null | head -1)
if [ -z "$TOOLKIT_PATH" ]; then
  echo "Toolkit not found; continuing without it"
else
  source "$TOOLKIT_PATH/init.sh"
fi
```

## Code Examples

### Python Async Pattern
[Include minimal Python async example]

### Error Handling Pattern
[Include error handling with clean stdout/stderr]
```

- [ ] **Step 4: Create security-review-examples.md**

This file consolidates security issue examples for the security reviewer agent.

```markdown
# Security Review Code Examples

Referenced by: `al-dev-security-reviewer` agent

## Common Security Issues in AL/BC

### SQL Injection via String Concatenation
**Bad:**
```al
query := 'SELECT * FROM ' + tableName;
```

**Good:**
```al
// Use filters instead of string concatenation
rec.SetFilter("Field", value);
```

### Credential Storage
**Bad:** Storing tokens in plain text fields.

**Good:** Use credential management APIs.
```

- [ ] **Step 5: Create performance-review-examples.md**

This file consolidates performance issue examples for the performance reviewer agent.

```markdown
# Performance Review Code Examples

Referenced by: `al-dev-performance-reviewer` agent

## Common Performance Issues

### N+1 Query Pattern
**Bad:**
```al
rec.FindSet();
repeat
  subRec.Get(rec.Id);  // Query inside loop
until rec.Next() = 0;
```

**Good:**
```al
rec.FindSet();
repeat
  // Process batched data, not individual queries
until rec.Next() = 0;
```
```

- [ ] **Step 6: Create code-review-patterns.md**

This file consolidates AL code review patterns and severity classifications.

```markdown
# Code Review Patterns and Severity

Referenced by: `al-dev-code-review` and `al-dev-expert-reviewer` agents

## Common AL Issues

### Naming Convention Violations
Object names must be ≤30 characters; use AL prefix conventions.

### Event Subscriber Mismatches
Procedure signature must match event signature (var parameters, order).

## Severity Classification

### Critical
- Security vulnerabilities
- Data loss risks
- Compilation failure

### High
- Performance bottlenecks
- Missing error handling
- Incorrect AL patterns

### Medium
- Code style violations
- Naming inconsistencies
- Documentation gaps

### Low
- Formatting
- Comment clarity
```

- [ ] **Step 7: Create release-notes-template.md (if not using existing)**

Check if `solution-plan-template.md` is sufficient or if a separate release notes template is needed.

```markdown
# Release Notes Template

Referenced by: `al-dev-release-notes-agent` agent

## Release Notes Structure

### Summary Section
One-paragraph overview of major changes.

### New Features
- Feature 1 with impact statement
- Feature 2 with impact statement

### Bug Fixes
- Bug 1 with fix details
- Bug 2 with fix details

### Breaking Changes
- Change 1 with migration guidance
- Change 2 with migration guidance

### Performance Improvements
- Improvement 1 with metric (if available)
```

- [ ] **Step 8: Create interview-question-bank.md**

This file consolidates BC/AL interview question categories and examples.

```markdown
# Interview Question Bank for BC/AL Projects

Referenced by: `al-dev-interview` agent

## Question Categories

### Business Requirements
- What is the primary business problem this module solves?
- Who are the end users and what is their workflow?
- What are the success criteria?

### Data Model
- What tables and fields are affected?
- Are there relationships to standard BC tables?
- What data transformations are needed?

### Integration Points
- Does this module integrate with external systems?
- What APIs or webhooks are required?
- What are the integration failure modes?

### Performance & Scaling
- What is the expected data volume?
- What are the performance SLAs?
- Are there batch processing requirements?

### Security & Compliance
- What data is sensitive?
- What are the access control requirements?
- Are there compliance rules to follow?

### Testing & UAT
- What test scenarios are critical?
- Who performs UAT and when?
- What is the rollback plan?
```

---

## Agent-Specific Fixes

### Task 2: Fix al-dev-developer

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-developer.md`

**Changes:**
1. Remove TDD Implementation Process section (290 lines); replace with one-line pointer to `knowledge/tdd-workflow.md`
2. Collapse 24 sections to 6: Your Mission, Inputs, Outputs, Workflow, Standards, Governance Tokens
3. Move AL code patterns to `knowledge/al-developer-patterns.md`
4. Remove emoji response templates from Chat Response Format
5. Fix tool list: Remove reference to `AskUserQuestion` and `TaskCreate`/`TaskUpdate` from instructions if not in tools list, or add them to tools list if they're needed

- [ ] **Step 1: Read al-dev-developer.md to understand current structure**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-developer.md
```

- [ ] **Step 2: Identify sections to remove and consolidate**

- Sections to move to knowledge: "Standard AL Patterns", "Common AL Mistakes to Avoid", "Performance Best Practices"
- Sections to collapse: "TDD Implementation Process" → reference to `knowledge/tdd-workflow.md`
- Sections to merge: "Error Handling Rules" + "Handling Missing Information" into "Standards"

- [ ] **Step 3: Rewrite al-dev-developer.md with collapsed structure**

Keep only 6 top-level sections:
1. Your Mission
2. Inputs
3. Outputs  
4. Workflow (2-4 steps)
5. Standards (brief, references knowledge files)
6. Governance Tokens (keep existing table)

- [ ] **Step 4: Fix tool list mismatch**

Check if instructions reference tools not in the tools list. Update either the tools list or remove gate instructions that require missing tools.

- [ ] **Step 5: Remove bc-publish references or annotate as optional**

If bc-publish is project-specific, add a note: "Optional if your project uses bc-publish; skip this step otherwise."

- [ ] **Step 6: Verify line count and commit**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-developer.md
git add profile-al-dev-shared/agents/al-dev-developer.md profile-al-dev-shared/knowledge/al-developer-patterns.md
git commit -m "fix(agents): al-dev-developer — collapse sections, move patterns to knowledge file"
```

---

### Task 3: Fix al-dev-docs-writer

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-docs-writer.md`

**Changes:**
1. Move RTM sections to `knowledge/documentation-rtm-guide.md`
2. Collapse 20 sections to 6: Your Mission, Inputs, Outputs, Workflow, RTM Handling (brief reference), Output Format
3. Move API Documentation Template to knowledge file
4. Fix tool list: Remove "ask user" from Step 1 or add `AskUserQuestion` to tools

- [ ] **Step 1: Read al-dev-docs-writer.md**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-docs-writer.md
```

- [ ] **Step 2: Extract RTM sections and templates to knowledge/documentation-rtm-guide.md**

- RTM Status Inference
- RTM Token Parsing
- RTM Documentation Output
- RTM Rules
- API Documentation Template (move entire 40+ line template)

- [ ] **Step 3: Rewrite al-dev-docs-writer.md with collapsed structure**

6 sections:
1. Your Mission
2. Inputs
3. Outputs
4. Workflow (3-4 steps, with defaults instead of "ask user")
5. Documentation Guidelines (brief, references knowledge files)
6. Output Format (brief)

- [ ] **Step 4: Fix Step 1 "ask user" issue**

Replace "ask user which to create" with: "Create `docs/` by default; use `wiki/` if the project convention specifies it."

- [ ] **Step 5: Add Workflow steps that read from knowledge files**

```
- Read knowledge/documentation-rtm-guide.md for RTM handling rules
- Follow the Output Format template (reference knowledge file)
```

- [ ] **Step 6: Merge Output and Chat Response Format sections**

Create one section: `## Output & Response` that covers both file deliverables and session log entry.

- [ ] **Step 7: Verify and commit**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-docs-writer.md
git add profile-al-dev-shared/agents/al-dev-docs-writer.md profile-al-dev-shared/knowledge/documentation-rtm-guide.md
git commit -m "fix(agents): al-dev-docs-writer — collapse sections, move RTM guide to knowledge file"
```

---

### Task 4: Fix al-dev-script-engineer

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-script-engineer.md`

**Changes:**
1. Replace hardcoded path with dynamic lookup
2. Move script conventions code examples to `knowledge/script-engineer-conventions.md`
3. Collapse 9 sections to 6: Your Mission, Inputs, Outputs, Workflow, Conventions, Standards
4. Fix `.dev/02-solution-plan.md` reference to glob pattern

- [ ] **Step 1: Replace hardcoded toolkit path**

Old:
```
`/Users/russelllaing/Documents/Repositories/al-analysis-toolkit`
```

New (in Toolkit Reference section):
```bash
TOOLKIT_PATH=$(find ~ -name "al-analysis-toolkit" -maxdepth 5 -type d 2>/dev/null | head -1)
if [ -z "$TOOLKIT_PATH" ]; then
  echo "al-analysis-toolkit not found; continuing without it"
else
  source "$TOOLKIT_PATH/init.sh"
fi
```

- [ ] **Step 2: Move Script Conventions section to knowledge file**

Extract ~45 lines of `## Script Conventions (follow strictly)` and move to `knowledge/script-engineer-conventions.md`.

- [ ] **Step 3: Collapse sections**

Merge:
- Error Handling Standards + CLI Output → `## Standards`
- Token Generation + Script Conventions → `## Conventions` (brief reference to knowledge file)

Result: 6 sections total.

- [ ] **Step 4: Fix solution plan reference**

Old:
```
`.dev/02-solution-plan.md`
```

New:
```
latest `*-al-dev-plan-solution-plan.md` in `.dev/`
```

- [ ] **Step 5: Fix "when possible" language**

Old:
```
Always match the language to the project's existing stack when possible
```

New:
```
Always match the language to the project's existing stack (detect via package.json, go.mod, etc.; if none found, default to Python)
```

- [ ] **Step 6: Verify and commit**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-script-engineer.md
git add profile-al-dev-shared/agents/al-dev-script-engineer.md profile-al-dev-shared/knowledge/script-engineer-conventions.md
git commit -m "fix(agents): al-dev-script-engineer — fix toolkit path, move conventions to knowledge, collapse sections"
```

---

### Task 5: Fix al-dev-solution-architect

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-solution-architect.md`

**Changes:**
1. Change body H1 from "Solution Planner" to "Agent: al-dev-solution-architect"
2. Move Output Format template (200+ lines) to `knowledge/solution-plan-template.md` (already exists; just reference it)
3. Collapse 18 sections to 6: Your Mission, Inputs, Outputs, Workflow, MCP Tools Available, Output Format (brief reference)
4. Fix MCP tool notation to be clearer (add note that these are pseudo-code representations)

- [ ] **Step 1: Fix body H1**

Change:
```markdown
# Solution Planner
```

To:
```markdown
# Agent: al-dev-solution-architect
```

- [ ] **Step 2: Extract Output Format template reference**

The 200-line `## Output Format` section should be replaced with:

```markdown
## Output Format

Write to `.dev/$(date +%Y-%m-%d)-al-dev-plan-solution-plan.md`. The file structure is documented in `knowledge/solution-plan-template.md` — read that file for the complete template, then populate each section with your design findings.
```

- [ ] **Step 3: Move MCP Tools section to knowledge file or collapse**

Create brief reference section:

```markdown
## MCP Tools Available

The following MCP servers are available:
- AL Code Intelligence (for BC symbol lookup)
- Microsoft Docs (for AL/BC API reference)
- BC Code History (for pattern research)

For tool invocation syntax, use the standard tool-call mechanism provided by your environment.
```

- [ ] **Step 4: Collapse sections**

Result: 6 sections
1. Your Mission
2. Inputs
3. Outputs
4. Workflow (reference knowledge/solution-plan-template.md for structure)
5. MCP Tools Available (brief, no examples)
6. Output Format (brief reference to template)

- [ ] **Step 5: Verify line count reduction**

Target: Agent body < 150 lines total.

- [ ] **Step 6: Verify and commit**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-solution-architect.md
git add profile-al-dev-shared/agents/al-dev-solution-architect.md
git commit -m "fix(agents): al-dev-solution-architect — fix H1, move template reference, collapse sections"
```

---

### Task 6: Fix al-dev-commit-agent-analysis

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md`

**Changes:**
1. Add `REPO` to Inputs table (project root path, passed in dispatch)
2. Split Phase: analysis (290 lines) into sub-sections: Manifest Extraction, Validation Checks, Return Format
3. Remove duplicate PROJECT_CONTEXT/FD_TICKET bullet list from Phase body
4. Renumber decimal steps (4.5, 6.5, 6.7) to sequential integers (4, 5, 6, 7)

- [ ] **Step 1: Add REPO to Inputs table**

Add row:
```
| REPO | string | Project root directory (e.g., /path/to/project) |
```

- [ ] **Step 2: Update steps to use REPO**

Replace `$REPO` references in steps with the variable now documented in Inputs.

- [ ] **Step 3: Split Phase: analysis into sub-sections**

```markdown
## Phase: analysis

### Manifest Extraction (Steps 1–3)
Extract per-file manifests from staged changes...
[Step 1, Step 2, Step 3 content]

### Validation Checks (Steps 4–6)
Validate manifests and detect grouping conflicts...
[Step 4, Step 5, Step 6 content]

### Return Format (Step 7)
Return structured commit plan...
[Step 7 content]
```

Each sub-section ≤ 30 lines.

- [ ] **Step 4: Remove duplicate input description**

Delete the bullet list that repeats PROJECT_CONTEXT and FD_TICKET at the start of the Phase body.

- [ ] **Step 5: Renumber steps sequentially**

Old → New:
- Step 4, Step 4.5, Step 5 → Step 1, Step 2, Step 3, Step 4
- Step 6, Step 6.5, Step 6.7, Step 6.8, Step 7 → Step 5, Step 6, Step 7, Step 8, Step 9

- [ ] **Step 6: Verify and commit**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md
git add profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md
git commit -m "fix(agents): al-dev-commit-agent-analysis — add REPO input, split phase, renumber steps"
```

---

### Task 7: Fix al-dev-security-reviewer

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-security-reviewer.md`

**Changes:**
1. Add missing body H1: `# Agent: al-dev-security-reviewer`
2. Move "Common Security Issues in AL/BC" code examples to `knowledge/security-review-examples.md`
3. Merge Spawn Context into Role; merge Success Criteria into Output Format
4. Result: 6 sections (from 9)
5. Fix Step 3 wording ("When other reviewers present findings" → "When other reviewers' findings are included in dispatch")
6. Remove "or message lead" from Output Format

- [ ] **Step 1: Add H1 heading**

Insert at top of body (before current content):
```markdown
# Agent: al-dev-security-reviewer
```

- [ ] **Step 2: Extract code examples to knowledge file**

Move ~60 lines of security issue code examples to `knowledge/security-review-examples.md`.

Replace section with:
```markdown
## Common Security Issues in AL/BC

For detailed examples and code patterns, see `knowledge/security-review-examples.md`. Key categories:
- SQL Injection via string concatenation
- Credential storage vulnerabilities
- Permission elevation risks
- Data exposure in logs
```

- [ ] **Step 3: Merge Spawn Context into Role**

Combine the Spawn Context heading/content into the Role section.

- [ ] **Step 4: Merge Success Criteria into Output Format**

Combine Success Criteria content into Output Format section.

- [ ] **Step 5: Fix Step 3 wording**

Old:
```
When other reviewers present findings...
```

New:
```
When other reviewers' findings are included in the dispatch prompt...
```

- [ ] **Step 6: Remove "message lead" reference**

Old:
```
Write your findings (or message lead if that's the team pattern)
```

New:
```
Write your findings as the agent's text response.
```

- [ ] **Step 7: Verify structure**

Confirm 6 sections: Role, Inputs, Outputs, Review Focus, Review Process, Output Format.

- [ ] **Step 8: Verify and commit**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-security-reviewer.md
git add profile-al-dev-shared/agents/al-dev-security-reviewer.md profile-al-dev-shared/knowledge/security-review-examples.md
git commit -m "fix(agents): al-dev-security-reviewer — add H1, merge sections, move code examples"
```

---

### Task 8: Fix al-dev-interview

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-interview.md`

**Changes:**
1. Replace `USER_GATE` with `AskUserQuestion` throughout
2. Move Question Categories (~120 lines) to `knowledge/interview-question-bank.md`
3. Collapse 11 sections to 6: Your Mission, Inputs, Outputs, Interview Process, Writing Refined Spec, Completion
4. Merge Interview Guidelines and Tips into Interview Process
5. Add step to read `knowledge/interview-question-bank.md` in Workflow

- [ ] **Step 1: Replace USER_GATE with AskUserQuestion**

Global replace in file:
```
USER_GATE → AskUserQuestion
```

- [ ] **Step 2: Extract Question Categories**

Move entire `## Question Categories for BC/AL Projects` section (~120 lines) to `knowledge/interview-question-bank.md`.

- [ ] **Step 3: Replace section with reference**

In Agent body, replace with:

```markdown
## Interview Process

[Opening and warmup guidance...]

### Question Selection

Read `knowledge/interview-question-bank.md` for a comprehensive list of question categories and examples. Adapt questions to the specific project context.

[Continue with rest of interview process...]
```

- [ ] **Step 4: Merge Interview Guidelines into Interview Process**

Add guideline content as sub-sections within Interview Process (e.g., "Clarification Technique", "Handling Ambiguity").

- [ ] **Step 5: Merge Tips into Interview Process or Completion**

Add tips as guidance notes within relevant steps.

- [ ] **Step 6: Remove Tool Usage table or fix USER_GATE naming**

If the Tool Usage table lists USER_GATE, update it to list AskUserQuestion with its actual name.

- [ ] **Step 7: Verify section count**

Target: 6 sections
1. Your Mission
2. Inputs
3. Outputs
4. Interview Process
5. Writing Refined Spec
6. Completion

- [ ] **Step 8: Verify and commit**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-interview.md
git add profile-al-dev-shared/agents/al-dev-interview.md profile-al-dev-shared/knowledge/interview-question-bank.md
git commit -m "fix(agents): al-dev-interview — fix tool naming, move questions to knowledge, collapse sections"
```

---

### Task 9: Fix al-dev-performance-reviewer

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-performance-reviewer.md`

**Changes:**
1. Add missing `## Review Process` section with sequential steps (read → identify → classify → output)
2. Move "Common Performance Issues" code examples (~60 lines) to `knowledge/performance-review-examples.md`
3. Merge "Debate with Other Reviewers" into Output Format
4. Result: 6 sections (from 7)

- [ ] **Step 1: Create Review Process section**

Add after Review Focus:

```markdown
## Review Process

1. **Read all staged files:** Scan the diff to understand scope and code structure.
2. **Identify performance issues:** Look for N+1 patterns, inefficient queries, unnecessary loops, resource leaks.
3. **Classify by severity:** High (blocks scaling), Medium (measurable regression), Low (optimization opportunity).
4. **Output findings:** Return structured findings with reproduction steps.
```

- [ ] **Step 2: Extract code examples to knowledge file**

Move ~60 lines from "Common Performance Issues" to `knowledge/performance-review-examples.md`.

Replace section with brief reference:

```markdown
## Common Performance Issues

For detailed code examples, see `knowledge/performance-review-examples.md`. Key patterns:
- N+1 query loops
- Inefficient FINDSET/CALCS
- Missing table indexes
- Blocking operations in triggers
```

- [ ] **Step 3: Merge "Debate with Other Reviewers" into Output Format**

Add at end of Output Format section:

```
When other reviewers' findings are included, structure your response as independent findings; the lead agent will synthesize across the panel.
```

- [ ] **Step 4: Verify section count**

Target: 6 sections
1. Role
2. Inputs
3. Outputs
4. Review Focus
5. Review Process
6. Output Format

- [ ] **Step 5: Verify and commit**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-performance-reviewer.md
git add profile-al-dev-shared/agents/al-dev-performance-reviewer.md profile-al-dev-shared/knowledge/performance-review-examples.md
git commit -m "fix(agents): al-dev-performance-reviewer — add Review Process, move examples, merge sections"
```

---

### Task 10: Fix al-dev-expert-reviewer

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-expert-reviewer.md`

**Changes:**
1. Add missing H1: `# Agent: al-dev-expert-reviewer`
2. Move "Common AL Issues" code examples (~70 lines) to `knowledge/code-review-patterns.md`
3. Merge "Debate with Other Reviewers" into Output Format
4. Result: 6 sections (from 7)

- [ ] **Step 1: Add H1 heading**

Insert at top of body:
```markdown
# Agent: al-dev-expert-reviewer
```

- [ ] **Step 2: Extract code examples to knowledge file**

Move ~70 lines from "Common AL Issues" to `knowledge/code-review-patterns.md`.

Replace with brief reference:

```markdown
## Common AL Issues

For detailed examples, see `knowledge/code-review-patterns.md`. Key patterns:
- Naming convention violations
- Event subscriber signature mismatches
- Missing error handling
- Incorrect scope or visibility
```

- [ ] **Step 3: Merge "Debate with Other Reviewers" into Output Format**

Add guidance about multi-reviewer context at end of Output Format.

- [ ] **Step 4: Verify section count**

Target: 6 sections
1. Role
2. Inputs
3. Outputs
4. Review Focus
5. Output Format
6. (Optional: Review Process if missing, or remove extra section)

- [ ] **Step 5: Verify and commit**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-expert-reviewer.md
git add profile-al-dev-shared/agents/al-dev-expert-reviewer.md profile-al-dev-shared/knowledge/code-review-patterns.md
git commit -m "fix(agents): al-dev-expert-reviewer — add H1, move examples, merge sections"
```

---

### Task 11: Fix al-dev-code-review

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-code-review.md`

**Changes:**
1. Fix description drift: Update description to reflect agent can be used in 3-reviewer team OR standalone
2. Merge Spawn Context into Role
3. Merge "What NOT to Review" into Review Focus
4. Move or consolidate severity definitions (currently duplicated in Review Process and Output Format)
5. Result: 6 sections (from 9)
6. Add language tag to code block in Output Format

- [ ] **Step 1: Update description**

Old:
```
For standalone manual use only; not part of the automated /al-dev-develop pipeline...
```

New:
```
Standalone code reviewer for general code quality. May also be spawned as part of the 3-reviewer team in /al-dev-develop.
```

- [ ] **Step 2: Merge Spawn Context into Role**

Move Spawn Context content into Role section as an additional paragraph.

- [ ] **Step 3: Merge "What NOT to Review" into Review Focus**

Add as final subsection:

```markdown
### Out of Scope

Do not review:
- Formatting/whitespace
- Comments on style preferences unrelated to readability
- Hypothetical future features
```

- [ ] **Step 4: Deduplicate severity definitions**

Review Process Step 3 and Output Format both define severity bands. Choose one canonical location and reference from the other.

- [ ] **Step 5: Add language tag to code block**

In Output Format, change:
```markdown
```
```
to:
```markdown
```markdown
```

- [ ] **Step 6: Verify section count**

Target: 6 sections
1. Role
2. Inputs
3. Outputs
4. Review Focus
5. Review Process
6. Output Format

- [ ] **Step 7: Verify and commit**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-code-review.md
git add profile-al-dev-shared/agents/al-dev-code-review.md
git commit -m "fix(agents): al-dev-code-review — fix description drift, merge sections, add code block tag"
```

---

### Task 12: Fix al-dev-release-notes-agent

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-release-notes-agent.md`
- Rename: `al-dev-release-notes-agent.md` → `al-dev-release-notes-writer.md`

**Changes:**
1. Rename agent file to `al-dev-release-notes-writer.md` (drop `-agent` suffix for consistency)
2. Update frontmatter name field to `al-dev-release-notes-writer`
3. Merge Phase: identify-diagrams into Phase: write-notes as a sub-step
4. Move release notes template (~60 lines) to reference to `knowledge/release-notes-template.md`
5. Fix `$AL_DEV_SHARED_PLUGIN_ROOT` env var reference (use Read tool with absolute path or resolve via find)
6. Result: 7 sections (from 9; remove one Phase and merge another)

- [ ] **Step 1: Read current agent file**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-release-notes-agent.md
```

- [ ] **Step 2: Create al-dev-release-notes-writer.md (copy and edit)**

```bash
cp /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-release-notes-agent.md \
   /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-release-notes-writer.md
```

- [ ] **Step 3: Update frontmatter name**

Change in new file:
```yaml
name: al-dev-release-notes-writer
```

- [ ] **Step 4: Merge Phase: identify-diagrams into Phase: write-notes**

Replace:
```markdown
## Phase: identify-diagrams
```

With a sub-step in write-notes:
```markdown
### Identify Diagrams
If the changes include architecture or data model updates, identify and reference relevant diagrams.
```

- [ ] **Step 5: Extract template to knowledge file**

The inline release notes template (~60 lines) should be moved to `knowledge/release-notes-template.md`.

Replace with:
```markdown
Write to `.dev/$(date +%Y-%m-%d)-al-dev-release-notes.md`. Follow the template structure in `knowledge/release-notes-template.md` — read that file and populate each section.
```

- [ ] **Step 6: Fix environment variable reference**

Old:
```bash
$AL_DEV_SHARED_PLUGIN_ROOT/markdown/md-mermaid-helper.md
```

New (use find or absolute path):
```bash
MERMAID_HELPER=$(find ~/.claude/plugins -name "md-mermaid-helper.md" -type f 2>/dev/null | head -1)
if [ -z "$MERMAID_HELPER" ]; then
  MERMAID_HELPER="profile-al-dev-shared/markdown/md-mermaid-helper.md"
fi
```

- [ ] **Step 7: Delete old agent file**

```bash
rm /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-release-notes-agent.md
```

- [ ] **Step 8: Update any skill that references the old agent name**

Search for skills that dispatch `al-dev-release-notes-agent` and update to `al-dev-release-notes-writer`.

```bash
grep -r "al-dev-release-notes-agent" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/
```

- [ ] **Step 9: Verify and commit**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-release-notes-writer.md
git add profile-al-dev-shared/agents/al-dev-release-notes-writer.md profile-al-dev-shared/knowledge/release-notes-template.md
git rm profile-al-dev-shared/agents/al-dev-release-notes-agent.md
git commit -m "fix(agents): al-dev-release-notes-writer — rename, merge phase, move template, fix env var"
```

---

### Task 13: Fix al-dev-diagnostics-fixer

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-diagnostics-fixer.md`

**Changes:**
1. Split Step 4 (Classify and Fix, ~80 lines) into Step 4a (Judgment-required check) and Step 4b (Direct edit path)
2. Move Python code example to `knowledge/` or inline it more compactly
3. Fix agent name reference: `al-dev-python-script-engineer` → `al-dev-script-engineer`
4. Update delegation text to "delegate to `al-dev-script-engineer` (Python mode)"

- [ ] **Step 1: Split Step 4 into two steps**

In the Process section, find Step 4 and split:

**Step 4a: Judgment-Required Check**
```
If the issue requires judgment (e.g., custom fix logic):
1. Check the rules table below for scripted fixes
2. If no scripted fix exists, proceed to Step 4b
```

**Step 4b: Direct Edit Path**
```
For issues with scripted fixes:
1. Apply the fix using Edit or Bash
2. Run validation
3. Return results
```

- [ ] **Step 2: Fix agent name reference**

Old:
```
delegate to `al-dev-python-script-engineer`
```

New:
```
delegate to `al-dev-script-engineer` with mode=Python
```

- [ ] **Step 3: Verify Step 4 is now ≤30 lines per sub-step**

Move Python code example to a knowledge file or reduce inline example.

- [ ] **Step 4: Verify and commit**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-diagnostics-fixer.md
git add profile-al-dev-shared/agents/al-dev-diagnostics-fixer.md
git commit -m "fix(agents): al-dev-diagnostics-fixer — split Step 4, fix agent name"
```

---

### Task 14: Fix al-dev-commit-agent-execute

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md`

**Changes:**
1. Remove duplicate ⚠️ CRITICAL warning block (appears before ## Inputs and inside ## Phase)
2. Split Phase: execute (~185 lines) into sub-sections: Pre-flight Lint, OOXML Gate, Commit & Retry, Return Block (each ≤30 lines)
3. Renumber Step 1.5 to Step 2, push subsequent steps

- [ ] **Step 1: Remove duplicate warning block**

Find and remove the ⚠️ CRITICAL block that appears before ## Inputs. Keep only the one inside Phase body.

- [ ] **Step 2: Add sub-sections to Phase: execute**

```markdown
## Phase: execute

### Pre-flight Lint (Steps 1–1.5)
[Content about lint baseline and initial checks]

### OOXML Gate (Steps 2–2.5)
[Content about OOXML validation]

### Commit & Retry (Steps 3–4)
[Content about committing and retry logic]

### Return Block (Step 5)
[Content about return format]
```

- [ ] **Step 3: Renumber steps**

Old numbering:
```
Step 1, Step 1.5, Step 2, Step 3
```

New numbering (sequential):
```
Step 1, Step 2, Step 3, Step 4
```

Update all references.

- [ ] **Step 4: Verify bloat is resolved**

Each sub-section should be ≤30 lines.

- [ ] **Step 5: Verify and commit**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
git add profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
git commit -m "fix(agents): al-dev-commit-agent-execute — remove duplicate warning, split phase, renumber steps"
```

---

### Task 15: Fix al-dev-support-agent

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-support-agent.md`

**Changes:**
1. Split Step 2 (Research, ~90 lines) into sub-sections: Source 1 (AL Symbols), Source 2 (MS Docs), Source 3 (BC Code History)
2. Fix `$AL_DEV_SHARED_PLUGIN_ROOT` env var reference (same fix as al-dev-release-notes-writer)
3. Optional: Consider renaming to `al-dev-support-researcher` for naming consistency

- [ ] **Step 1: Split Step 2 into sub-sections**

In the workflow/phase, replace flat Step 2 with:

```markdown
## Step 2: Research

### Source 1: AL Symbols
[~20 lines about querying AL symbols]

### Source 2: MS Docs
[~20 lines about searching MS Docs]

### Source 3: BC Code History
[~20 lines about querying BC code history]
```

- [ ] **Step 2: Fix environment variable reference**

Old:
```
$AL_DEV_SHARED_PLUGIN_ROOT/markdown/md-mermaid-helper.md
```

New (same as Task 12):
```bash
MERMAID_HELPER=$(find ~/.claude/plugins -name "md-mermaid-helper.md" -type f 2>/dev/null | head -1)
```

- [ ] **Step 3: Optional — rename to al-dev-support-researcher**

If renaming, update:
- File name
- Frontmatter name field
- Any skills that dispatch this agent
- Description to reflect researcher role

For now, skip this as a low-priority naming consistency issue.

- [ ] **Step 4: Verify and commit**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-agent.md
git add profile-al-dev-shared/agents/al-dev-support-agent.md
git commit -m "fix(agents): al-dev-support-agent — split Step 2 Research, fix env var"
```

---

### Task 16: Fix al-dev-ticket-agent

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-ticket-agent.md`

**Changes:**
1. Add `## Inputs` and `## Outputs` tables (missing entirely)
2. Split Phase: fetch (~120 lines) into sub-sections: Step 1 (Fetch), Step 2 (Write context file), Step 3 (Return output)
3. Change Step 1 title from "Fetch ticket and conversations in parallel" to "Fetch ticket and conversations"

- [ ] **Step 1: Add Inputs and Outputs tables**

Before the ## Phase section, add:

```markdown
## Inputs

| Field | Type | Description |
|-------|------|-------------|
| TICKET_ID | string | Freshdesk ticket ID |
| FRESHDESK_API_KEY | string | Freshdesk API key (from settings) |
| FRESHDESK_DOMAIN | string | Freshdesk domain (e.g., company.freshdesk.com) |

## Outputs

| File | Description |
|------|-------------|
| `.dev/<date>-al-dev-ticket-ticket-context.md` | Structured ticket context with fields, comments, metadata |
```

- [ ] **Step 2: Split Phase: fetch into sub-sections**

```markdown
## Phase: fetch

### Step 1: Fetch Ticket and Conversations
[Fetch API calls — sequential, not parallel]

### Step 2: Write Context File
[Write .dev/ context file with template structure]

### Step 3: Return Output
[Return output file path and summary]
```

Each sub-section ≤30 lines.

- [ ] **Step 3: Fix Step 1 title**

Old:
```
"Fetch ticket and conversations in parallel"
```

New:
```
"Fetch ticket and conversations"
```

Add note: "Fetch operations are sequential API calls (not parallel)."

- [ ] **Step 4: Verify and commit**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-ticket-agent.md
git add profile-al-dev-shared/agents/al-dev-ticket-agent.md
git commit -m "fix(agents): al-dev-ticket-agent — add Input/Output tables, split phase, fix title"
```

---

### Task 17: Fix commit-learn-verifier

**Files:**
- Modify: `profile-al-dev-shared/agents/commit-learn-verifier.md`

**Changes:**
1. Rename to `al-dev-commit-learn-verifier.md` (add al-dev prefix for consistency)
2. Rename `## Input` to `## Inputs` (align with other agents)
3. Align history scope: specify "last 3 commits" consistently in both `## Input` section and `## Analysis Process` Step 1
4. Add `auto_fix` (boolean) to `## Inputs` and specify dispatch format

- [ ] **Step 1: Rename file**

```bash
mv /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/commit-learn-verifier.md \
   /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-learn-verifier.md
```

- [ ] **Step 2: Update frontmatter name**

Change:
```yaml
name: commit-learn-verifier
```

To:
```yaml
name: al-dev-commit-learn-verifier
```

- [ ] **Step 3: Rename Input to Inputs**

Change:
```markdown
## Input
```

To:
```markdown
## Inputs
```

- [ ] **Step 4: Align history scope**

Both places should say:
```
Last 3 commits: examine git diff to identify corruption patterns
```

- [ ] **Step 5: Add auto_fix to Inputs table**

Add row:
```
| auto_fix | boolean | If true, apply auto-fixes; if false, report findings only |
```

- [ ] **Step 6: Document dispatch format**

Add note in Inputs or at top of Analysis Process:
```
The auto_fix parameter is passed as: `--auto-fix` flag in dispatch prompt or `auto_fix=true` in context.
```

- [ ] **Step 7: Update skills that reference old agent name**

Search for `commit-learn-verifier` and update to `al-dev-commit-learn-verifier`.

```bash
grep -r "commit-learn-verifier" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/
```

- [ ] **Step 8: Verify and commit**

```bash
git add profile-al-dev-shared/agents/al-dev-commit-learn-verifier.md
git rm profile-al-dev-shared/agents/commit-learn-verifier.md
git commit -m "fix(agents): al-dev-commit-learn-verifier — rename for consistency, align history scope, add auto_fix input"
```

---

### Task 18: Fix al-dev-explore

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-explore.md`

**Changes:**
1. Fix description: Replace "Complements the al-dev-explore skill" with "Used when exploration results need to persist beyond the current session context"
2. Either add Write tool and final step to write findings to `.dev/explore-<date>.md`, OR remove "persist as a file" from description
3. Rename `## Input` and `## Output` to `## Inputs` and `## Outputs` (plural, consistent with others)

- [ ] **Step 1: Fix description**

Old:
```
Complements the al-dev-explore skill
```

New:
```
Used when exploration results need to persist beyond the current session context as a shareable artifact.
```

- [ ] **Step 2: Option A — Add Write capability**

Add `Write` to tools list in frontmatter.

Add final step to workflow:
```
Write findings to `.dev/$(date +%Y-%m-%d)-al-dev-explore.md` for future reference.
```

OR

- [ ] **Step 2: Option B — Remove persist qualifier**

Remove "persist as a file" from description:

Old:
```
Use when exploration results need to persist as a file for later reference
```

New:
```
Use when you need to explore a codebase fast and return detailed findings.
```

Choose Option A (add Write) for consistency with agent design pattern.

- [ ] **Step 3: Rename singular to plural**

Change:
```markdown
## Input
## Output
```

To:
```markdown
## Inputs
## Outputs
```

- [ ] **Step 4: Verify and commit**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-explore.md
git add profile-al-dev-shared/agents/al-dev-explore.md
git commit -m "fix(agents): al-dev-explore — fix description, add Write tool, rename to plural"
```

---

## Summary

All 65 quality issues have been addressed:

- **Structural Conventions** (sections > 6 or > 30 lines): Collapsed and split into sub-sections
- **Prompt Clarity** (undefined variables, tool mismatches, naming): Fixed with explicit definitions and tool list updates
- **Bloat** (inline code examples, templates): Moved to knowledge files with Read-based references
- **Description Drift**: Updated to match actual agent capabilities
- **Naming Inconsistencies**: Agents renamed to follow consistent conventions; singular Input/Output changed to plural Inputs/Outputs
- **Harness-Specific Notation**: Removed all undefined environment variables; replaced with Read tools or bash lookups

All changes maintain agent functionality while improving clarity, maintainability, and structural consistency.

