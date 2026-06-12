# Duplicate Text Findings

**Review date:** 2026-06-12

## Purpose

This document preserves the initial review of exact duplicate text in
`.claude` and `profile-al-dev-shared` for later assessment. It records
potential maintenance risks without proposing or applying refactors.

## Method

The scan used the repo-local `generate-duplicate-text-report` script with its
active-authored defaults:

```bash
python3 .codex/skills/generate-duplicate-text-report/scripts/generate_duplicate_text_report.py \
  --output /private/tmp/2026-06-12-duplicate-text-report.md \
  --date 2026-06-12
```

The scanner:

- required at least 8 consecutive matching lines
- required at least 4 nonblank lines and 80 characters
- normalized line endings and trailing whitespace only
- collapsed overlapping windows into maximal duplicate blocks
- grouped all occurrences of the same block
- excluded generated projections, archives, caches, binary files, and
  `.DS_Store`

The live scan inspected 212 text files, excluded 131 files, and found 49
grouped duplicate blocks. These are exact-text matches, not semantic or
near-duplicate findings.

## Executive Summary

Six duplicate families warrant later review. The strongest drift risks are the
two developer spawn branches and the duplicated compile command, because both
repeat operational behavior and the compile copies have already diverged.
Canonical routing and filter summaries are lower-volume but can become stale
when their source contracts change. Validator and lens-agent duplication is
mostly structural and should be weighed against the cost of introducing shared
helpers or templates.

## Findings

### 1. Developer Spawn Branches Repeat Common Gates

**Priority:** High

The TDD and traditional branches repeat 29 lines covering symbol preflight,
AL standards, scope expansion, and commit restrictions:

- `profile-al-dev-shared/knowledge/al-dev-develop-spawn-prompt.md:66`
- `profile-al-dev-shared/knowledge/al-dev-develop-spawn-prompt.md:126`

Only the workflow-specific lines need to differ. Future changes to the common
gate text must currently be applied twice in the same canonical document.

**Later review:** Consider one shared prompt backbone with explicit TDD and
traditional workflow inserts.

### 2. Compile Commands Are Duplicated and Divergent

**Priority:** High

The compiler selection command appears in:

- `profile-al-dev-shared/knowledge/compile-lint-procedure.md:61`
- `profile-al-dev-shared/skills/al-dev-lint/SKILL.md:52`

The copies share ten lines, but the skill exits with status 1 when no compiler
is found while the knowledge procedure does not. This is evidence of current
behavioral drift, not only repeated wording.

**Later review:** Choose one authoritative executable contract and make the
other surface reference or invoke it.

### 3. Health Filter Ordering Is Copied from Its Canonical Contract

**Priority:** Medium

The eight-line filter-order block appears in:

- `.claude/knowledge/health-filter-contract.md:83`
- `.claude/skills/plan-health-findings/SKILL.md:85`

The knowledge file is explicitly canonical, so the skill copy can silently
drift if routing order changes.

**Later review:** Keep only a short pointer in the skill unless the inline
summary is required for reliable execution.

### 4. Complexity Routing Table Is Repeated

**Priority:** Medium

The eight-line complexity table appears in:

- `profile-al-dev-shared/knowledge/al-dev-plan-phase-routing.md:13`
- `profile-al-dev-shared/skills/al-dev-plan-preflight/SKILL.md:117`

The knowledge file states that routing logic is canonical there and that
skills should retain only lightweight summaries. The full table tests that
boundary.

**Later review:** Decide whether the inline table is a deliberate quick
reference or should be reduced to the canonical reference plus tier outcome.

### 5. Document Validators Repeat Parsing and Reporting Logic

**Priority:** Medium

The following validators share blocks of 11 to 12 lines for imports, heading
extraction, empty-section detection, argument handling, and result reporting:

- `profile-al-dev-shared/skills/al-dev-plan/validate-plan.py`
- `profile-al-dev-shared/skills/al-dev-develop/validate-code-review.py`
- `profile-al-dev-shared/skills/al-dev-interview/validate-requirements.py`

The repeated code is simple, but fixes to document parsing or diagnostics must
be synchronized across three scripts.

**Later review:** Extract a helper only if another validator change is needed;
avoid adding an abstraction solely to remove a small amount of stable code.

### 6. Claude Lens Agents Repeat Template Structures

**Priority:** Low

Quality and design lens agents repeat 8 to 16-line blocks for model/tool
frontmatter, inputs, outputs, severity rules, and result formats. Examples:

- `.claude/agents/quality-agent-lens-clarity.md:43`
- `.claude/agents/quality-skill-lens-clarity.md:38`
- `.claude/agents/design-agent-lens-scope-isolation.md:4`
- `.claude/agents/quality-agent-lens-bloat.md:4`

These files are intentionally self-contained, and their agent-versus-skill
differences are meaningful. A generation or shared-backbone approach could
reduce drift, but would also add maintainer machinery.

**Later review:** Change only when there is evidence of inconsistent behavior,
not merely because the template text is repeated.

## Intentional or Low-Risk Matches

The scan also found duplication that should not be treated as immediate debt:

- GREEN and REFACTOR code examples repeat unchanged production logic in
  `tdd-workflow.md` to demonstrate a staged transformation.
- Ticket invocation examples repeat a complete dispatch block for
  self-contained documentation.
- Commit workflow skills repeat intent-preflight wording to preserve local
  safety contracts.
- Developer agents repeat standards and compile safeguards because each agent
  must remain executable in isolation.
- Generated agent projections and archived content were excluded by default;
  their duplication is expected.

## Review Guidance

For each candidate, verify current divergence and caller behavior before
refactoring. Prefer an existing canonical knowledge contract over a new helper.
Do not centralize text when doing so would make an independently dispatched
agent or skill incomplete at runtime.
