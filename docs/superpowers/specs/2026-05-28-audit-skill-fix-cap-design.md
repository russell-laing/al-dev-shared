# Audit Skill Fix Cap Design

**Date:** 2026-05-28
**Status:** Approved

## Problem

The audit skills (`/audit-agent-quality`, `/audit-skill-quality`) were removing too much content when the user chose to apply fixes after an audit run. Phase 6 of both skills asks "Would you like to fix any of these now?" but provides no instructions on how to apply fixes — the model improvises, leading to aggressive content removal.

## Goal

Add a hard per-file content reduction cap of 5% to the fix application step in both audit skills. Each file being fixed may lose at most 5% of its original line count in a single audit pass.

Execution is tracked outside this design doc. Checklist state changes are not repository changes.

## Scope

- **Files changed:** 2
  - `.claude/skills/audit-agent-quality/SKILL.md` — Phase 6
  - `.claude/skills/audit-skill-quality/SKILL.md` — Phase 6
- **Files unchanged:** All lens agents, `audit-knowledge-quality`, reporting format

## Design

### What Changes

Phase 6 of both audit skills gains a "Fix Application Protocol" subsection that activates when the user says yes.

**Current Phase 6 (both skills):**

```
Ask: "Would you like to fix any of these now?"
[no further instructions — model improvises]
```

**New Phase 6 — Fix Application Protocol:**

```markdown
### If the user says yes — Fix Application Protocol

For each file to be modified:

1. **Read the file** and record its original line count (`original_lines`).
2. **Calculate budget:** `floor(original_lines × 0.05)` — max net lines
   removable from this file in this pass.
   If the result is `0`, skip all non-atomic edits for that file this pass.
3. **Apply only atomic fixes** per finding, in priority order:
   High → Medium → Low. An atomic fix is one that fully resolves a finding
   without rewriting unrelated sections.
4. **If the next full fix would exceed `budget`:**
   skip that finding for this pass, append to the report section for that file:
   `"Skipped — full fix exceeds remaining budget; queue for next audit pass."`
5. **Do not partially rewrite structural blocks** such as headings, lists,
   frontmatter, or phase instructions. If a finding touches a structural block
   and cannot be resolved atomically within the remaining budget, skip it.
6. **Verify after edit:** `wc -l <file>` — confirm net reduction ≤ budget.
   Also confirm the edited file still contains the required structural sections
   for its type before proceeding to the next file.
7. **Leave commits to the surrounding workflow.** The protocol only governs
   safe edit application; it does not introduce a new commit step.
```

### What Does Not Change

- Bloat lens thresholds (30 lines / 6 sections for agents; 30 lines / 8 phases for skills) — detection accuracy is preserved
- Audit report format
- `audit-knowledge-quality` skill — it offers guidance, not direct content edits

### Rationale

The lens agents are reporting tools — they should surface real issues accurately. The aggressive removal problem is in the fix-application layer, not detection. Constraining fixes at the action layer solves the problem without degrading detection. Future passes can address remaining bloat incrementally.

## Acceptance Criteria

- [ ] `audit-agent-quality/SKILL.md` Phase 6 includes the Fix Application Protocol with a 5% per-file cap
- [ ] `audit-skill-quality/SKILL.md` Phase 6 includes the Fix Application Protocol with a 5% per-file cap
- [ ] The protocol specifies: read line count, calculate budget, apply atomic fixes, skip-and-queue behavior, structural verification, verify with `wc -l`
- [ ] No changes to lens agents or other skills, and no unrelated worktree files are treated as implementation output
