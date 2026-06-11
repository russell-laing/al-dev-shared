# Health Plan Context Template

This document defines the context block passed to `superpowers:writing-plans` in
Phase 3 of `plan-health-findings`. Pass all items in this list as context to
`writing-plans` when invoking it.

## Context items to pass

- All rubber duck records
- Corrected flag names, file paths, and scope (use these, not the
  original suggestion wording where rubber ducking found a mismatch)
- Cross-layer coupling constraints, including changes that must share a task or
  be linked by explicit task dependencies
- Task ordering: additive changes first (new knowledge docs, diagram
  extensions), structural changes last (merges, archives, moves)
- The verification pattern for each task, mapped by finding verb:

  | Verb | Evidences | Command |
  | --- | --- | --- |
  | Atomise / Split | New phase/file boundaries exist | `grep -n '## Phase'` + `wc -l` |
  | Absorb / Merge / Inline | Source folded in, original removed | `wc -l` (delta) + `ls` (absence) |
  | Connect / Promote | Knowledge doc created and referenced | `ls` (new doc) + `grep` (reference) |
  | Move | File relocated to target surface | `ls` (new path) + `ls` (old path gone) |
  | Extend | New downstream consumer reads the artifact | `grep` (read site) |
  | Trim / Remodel / Align | Field/tool removed or value changed | `grep` (presence/absence) |

- The ledger row IDs captured in Phase 1 for the accepted findings each
  task implements. Each task's **verification block** must include a
  `closes_rows:` line in this exact format:

  ```text
  closes_rows: ["#NNN", "#MMM", ...]   # IDs from docs/health/dispositions.md
  ```

  Place this line **inside the verification block**, not in the task title or
  header. `implement-health-plan` Phase 3 greps for this token to close the
  ledger entries after implementation.

- **Suppress your Execution Handoff.** Do not present the "Subagent-Driven /
  Inline" prompt or ask "Which approach?". Hand control back to the caller
  (`plan-health-findings` Phase 4), which routes execution to
  `/implement-health-plan`.
