# Audit Skill Fix Cap Design

**Date:** 2026-05-28
**Status:** Approved

## Problem

The audit skills (`/audit-agent-quality`, `/audit-skill-quality`) were removing too much content when the user chose to apply fixes after an audit run. Phase 6 of both skills asks "Would you like to fix any of these now?" but provides no instructions on how to apply fixes — the model improvises, leading to aggressive content removal.

## Goal

Add a hard per-file content reduction cap of 5% to the fix application step in both audit skills. Each file being fixed may lose at most 5% of its original line count in a single audit pass.

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
3. **Apply the minimum effective fix** per finding, in priority order:
   High → Medium → Low. Stop adding fixes to a file once the running
   removal total would exceed `budget`.
4. **If a finding requires more than the remaining budget to fully resolve:**
   apply the highest-impact partial fix within the remaining budget, then
   append to the report section for that file:
   `"Partial fix applied — remainder queued for next audit pass."`
5. **Verify after edit:** `wc -l <file>` — confirm net reduction ≤ budget
   before proceeding to the next file.
6. **Commit** changes to fixed files.
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
- [ ] The protocol specifies: read line count, calculate budget, apply minimum effective fix, partial-fix path, verify with `wc -l`
- [ ] No changes to lens agents or other skills
