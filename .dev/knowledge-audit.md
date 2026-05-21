# Knowledge Folder Audit — Stub Detection

**Date:** 2026-05-19
**Scope:** `/Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/` (all 35 files, recursive)
**Method:** Full read of every file + grep for referencing agents/skills

---

## Verdict Summary

| File | Status | Notes |
|------|--------|-------|
| `al-linting-rules.md` | RICH | 250 lines of concrete rule tables |
| `workflow-resilience.md` | RICH | Concrete checkpointing protocol |
| `proportional-planning.md` | RICH | Detailed target tables, examples, enforcement |
| `workflow-routing.md` | RICH | Concrete decision tree, examples, routing paths |
| `compile-lint-procedure.md` | RICH | Specific shell commands, step-by-step |
| `doc-templates/executive.md` | RICH | Concrete template with guidance |
| `doc-templates/functional.md` | RICH | Full template with RTM section |
| `doc-templates/user.md` | RICH | Concrete template |
| `doc-templates/technical.md` | RICH | Full template with RTM reference |
| `anti-patterns.md` | ADEQUATE | 10-row table; thin but self-contained |
| `quality-checklist.md` | ADEQUATE | Focused checklist; does what it says |
| `rubber-duck.md` | RICH | Concrete rules and application table |
| `tdd-workflow.md` | RICH | Extremely detailed 3-phase TDD protocol |
| `feedback-resolution.md` | RICH | Clear severity/disposition system with examples |
| `session-analysis-report-format.md` | RICH | Precise canonical format specification |
| `commit-conventions.md` | RICH | Full spec with examples and violation callouts |
| `harness-concepts.md` | RICH | Concrete vocabulary/mapping tables |
| `skill-test-format.md` | RICH | Full schema docs for both YAML formats |
| `explore-subagent-pattern.md` | RICH | Concrete Steps A-D with naming conventions |
| `review-panel-pattern.md` | RICH | Clear composition + synthesis rules |
| `skill-test-trigger-corpus.yaml` | RICH | Concrete corpus entries |
| `architect-invocation-patterns.md` | RICH | Two concrete patterns with instructions |
| `code-review-template.md` | ADEQUATE | Template is concrete but brief |
| `solution-plan-template.md` | ADEQUATE | Template with section guidance |
| `perf-anti-patterns-prompt.md` | RICH | 8 named patterns with severity/exclusion rules |
| `al-dev-fix-examples.md` | ADEQUATE | Two walkthroughs, brief but sufficient |
| `al-developer-patterns.md` | **STUB** | See flag below |
| `script-engineer-conventions.md` | **STUB** | See flag below |
| `security-review-examples.md` | ADEQUATE | 5 examples with bad/good code |
| `performance-review-examples.md` | **STUB** | See flag below |
| `code-review-patterns.md` | ADEQUATE | Examples + severity table, usable |
| `release-notes-template.md` | RICH | Template + guidelines + example |
| `interview-question-bank.md` | RICH | 7 categories + interview guidelines |
| `verification-and-planning.md` | **STUB** | See flag below |
| `documentation-rtm-guide.md` | RICH | (Just fixed; now complete) |

---

## Flagged Files — Stubs or Thin Content

### 1. `al-developer-patterns.md` — STUB

**Claims:** "Standard AL Patterns" with RecordRef operations, query performance, record modification patterns, error handling rules, naming conventions. The header says "Referenced by: al-dev-developer agent."

**Agent expectation** (`al-dev-developer.md` line 63): "Reference knowledge/al-developer-patterns.md for standard AL patterns, common mistakes to avoid, error handling rules, and naming conventions."

**Actual content (53 lines):**
- RecordRef section: one sentence ("Use RecordRef for dynamic table access when the table isn't known at compile time. Always validate the table ID before operations.") — no code example
- Query Performance: one sentence ("use filters to reduce record set scope; avoid FINDSET in loops. Instead, collect IDs and batch-process.") — no code example
- Record Modification Patterns: one sentence ("Use ModifyAll for batch updates.") — no code
- Error Handling Rules: only the StrSubstNo → Error(label) rule with code examples — this section is OK
- AL Naming Conventions: 3 bullets, all already in CLAUDE.md

**What's missing:**
- No RecordRef code examples (when is RecordRef necessary? What does the template look like?)
- No SetLoadFields guidance (mentioned everywhere else but not here)
- No event subscriber pattern (mentioned in the header promises but absent)
- No interface/dependency injection patterns
- No Commit() handling guidance
- No FilterGroup usage
- No locking patterns (LockTable, ReadIsolation)
- The "RecordRef Operations" section header promises a pattern but delivers a sentence

**Severity:** Medium-high. The developer agent is told to "reference" this file but it adds almost nothing beyond what's already in the agent itself.

---

### 2. `script-engineer-conventions.md` — STUB

**Claims:** "Script Conventions (follow strictly)" — async-first design, protocol-based integration, strict typing, toolkit reference, language selection, code examples.

**Agent expectation** (`al-dev-script-engineer.md`): "Reference knowledge/script-engineer-conventions.md for: [conventions]"

**Actual content (66 lines):**
- Async-First Design: one paragraph, no code example for async pattern itself
- Protocol-Based Integration: two sentences, no schema example
- Strict Typing: two sentences, no schema validation example
- Toolkit Reference: an optional `al-analysis-toolkit` find command — this is a real tool hint
- Language Selection: a detection order using `package.json`, `go.mod`, etc. — this is useful
- Code Examples: one Python error handling pattern — genuinely useful

**What's missing:**
- No async code example (the section says "write async code patterns when possible" but shows none)
- No JSON/CSV output schema example for "Protocol-Based Integration"
- No type hints example for Python or TypeScript explicit types
- The "Strict Typing" section says "Define input/output schemas; validate at boundaries" with no example of what that looks like
- Overall: ~40% of sections have the heading but not the promised content

**Severity:** Low-medium. The language detection and Python error pattern are useful. But several sections are one-sentence placeholders.

---

### 3. `performance-review-examples.md` — STUB (partial)

**Claims:** Code examples for performance reviewer. Referenced by `al-dev-performance-reviewer.md` line 62.

**Actual content (111 lines total):** 5 examples:
1. N+1 Query Pattern — bad example shows `subRec.Get(rec.Id)` inside loop (ok), but the "Good" version says "Load all data first, then process in memory / or use a JOIN/FILTER" with NO actual code showing how to do it
2. Inefficient FINDSET Usage — bad example is actually not clearly wrong (the comment says "Default sort, slow on large tables" but the "good" version just adds a comment about `SetCurrentKey`), and the fix is identical to the bad except for `if rec.FindSet() then` guard — which is an error check not a performance fix
3. Missing Table Indexes — the "good" version shows adding a key definition, which is accurate
4. Blocking Operations in Triggers — useful example
5. Unnecessary Loops — `rec.Count()` in loop condition — useful example

**What's missing/wrong:**
- The N+1 "Good" example is incomplete — it says "load all data first" but shows no code
- Example 2 (Inefficient FINDSET) conflates "using SetCurrentKey" (a legitimate fix) with the "Inefficient" label, which is confusing — the bad code already has `rec.SetCurrentKey(Name)` in it
- No SetLoadFields example (critical omission given how frequently this is cited)
- No CalcFields-inside-loop example
- No example corresponding to the P1-P8 patterns defined in `perf-anti-patterns-prompt.md` — these two files don't cross-reference each other

**Severity:** Medium. The file is referenced as the authoritative example source for performance review, but has an incomplete example and conflates a different pattern in example 2. The more detailed pattern specification lives in `perf-anti-patterns-prompt.md` which this file doesn't reference.

---

### 4. `verification-and-planning.md` — STUB

**Claims:** "Shared reference for cross-harness parity between Claude Code and Copilot CLI" for plan task verification, external claims verification, target confirmation, depth-first planning.

**Actual content (38 lines):**
- A cross-harness parity checklist (6 checkbox items, none with implementation detail)
- A tool mapping table with 3 rows (user gate, subagent retry, pattern scan)
- A usage note: "Reference this file when updating skill behavior across harnesses"
- A "Write-Persistence Verification" section that just says "See the global project instructions file → File Editing Safety"

**What's missing:**
- The checklist items are pure declarations ("al-dev-plan includes mandatory architect proposal/critique/falsification outputs") with no specification of what those outputs should look like
- "External claims verification" is in the title and mentioned in the intro but never defined anywhere in the file
- "Target confirmation" is in the title but the only mention is "Step 0 target confirmation wording is consistent across impacted skills" — no example, no wording
- "Depth-first planning (proposal + critique + falsification)" is in the intro but never explained
- The tool mapping is extremely sparse and largely redundant with `harness-concepts.md`
- The Write-Persistence section deflects entirely to CLAUDE.md instead of providing local guidance

**This file is referenced in CLAUDE.md** as "Shared parity reference: profile-al-dev-shared/knowledge/verification-and-planning.md" — it's a central document but delivers essentially no specification.

**Severity:** High. The file promises to be the shared specification for cross-harness parity but contains only a checklist of things-that-should-exist without defining them. Any agent reading this learns nothing actionable about HOW to do cross-harness parity.

---

## Adequate-but-Borderline Files

### `anti-patterns.md`

A 10-row table. Each row has an anti-pattern name, a one-line problem description, and a one-line correct approach. Referenced by nothing in agents/ or skills/ (no grep hits). It may be informally used or was intended for orchestrator-level guidance but isn't directly referenced. The table itself is accurate and self-contained. Not a stub — just thin.

### `code-review-template.md`

Referenced by `al-dev-develop/SKILL.md`. Contains the standard review structure template and an autonomous mode addition. Adequate — it does what it says. The "Implementation Summary" placeholder text could be more specific, but it's a template by nature.

### `solution-plan-template.md`

Referenced by `al-dev-solution-architect.md` and `al-dev-plan/SKILL.md`. Contains a template with section guidance. The `[list key fields with IDs and types]` and `[list with signatures]` instructions are brief, but for a template file that's acceptable. Adequate.

### `quality-checklist.md`

Three checklists (solution plans, code implementation, test suites). These are concrete and actionable. Thin but not a stub — it does exactly what it claims.

---

## Files That Are Fine (brief notes)

- **`al-linting-rules.md`**: 250 lines of dense rule tables. Exemplary reference document.
- **`commit-conventions.md`**: Fully specified with project-type variants, examples, violation callouts.
- **`workflow-routing.md`**: Decision tree, complexity criteria, example classifications, runtime optimization rules.
- **`proportional-planning.md`**: Detailed line targets, enforcement sections, concrete bad/good examples.
- **`tdd-workflow.md`**: 568 lines covering all three TDD phases in detail, bc-test CLI usage, CI/CD integration.
- **`documentation-rtm-guide.md`**: Comprehensive — token format, parsing rules, status inference, audience tables, inline reference format, folder structure, completeness checklist.
- **`perf-anti-patterns-prompt.md`**: The most operationally precise file in the folder — 8 named patterns with severity, exact reporting format, explicit exclusion rules.
- **`harness-concepts.md`**: Clean vocabulary contract with concrete mapping tables.
- **`session-analysis-report-format.md`**: Canonical format spec with examples for every section.

---

## Cross-File Inconsistency

`performance-review-examples.md` and `perf-anti-patterns-prompt.md` cover overlapping territory with no cross-reference:
- `perf-anti-patterns-prompt.md` defines P1-P8 patterns with severities
- `performance-review-examples.md` defines 5 anonymous examples that mostly duplicate P1, P5-P7 without using P-codes
- `al-dev-performance-reviewer.md` references only `performance-review-examples.md` — it never points to `perf-anti-patterns-prompt.md`
- `al-dev-perf/SKILL.md` (the perf skill) presumably uses `perf-anti-patterns-prompt.md`

Result: The performance reviewer agent uses a weaker example set while the richer P1-P8 taxonomy sits in a separate file it's never told about.

---

## Recommended Priority Fixes

1. **HIGH — `verification-and-planning.md`**: Either expand it to actually define the cross-harness standards it claims to specify, or delete it and point CLAUDE.md to the relevant sections in `workflow-routing.md` and `harness-concepts.md` instead.

2. **MEDIUM — `al-developer-patterns.md`**: Add actual code examples for RecordRef operations, SetLoadFields, and event subscriber patterns. The developer agent is told to "reference" this file but it's nearly content-free for those areas.

3. **MEDIUM — `performance-review-examples.md`**: Fix the incomplete N+1 "Good" example. Cross-reference `perf-anti-patterns-prompt.md`. Consider pointing `al-dev-performance-reviewer.md` to both files.

4. **LOW — `script-engineer-conventions.md`**: Add async pattern example (at minimum a Python asyncio skeleton) and a JSON schema validation example to deliver on the "strict typing" promise.
