# Health Plan Context Template

This document defines the context block passed to `superpowers:writing-plans` in
Phase 3 of `plan-plugin-findings`. Pass all items in this list as context to
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

- The event IDs captured in Phase 1 for the accepted findings each task
  implements. Each task's **verification block** must include a
  `closes_event_ids:` block in this exact format:

  ```yaml
  closes_event_ids:
    - disp_20260619_000001
    - disp_20260619_000002
  ```

  Use `closes_event_ids` from `docs/health/dispositions-open.md` or targeted store
  queries; do not use Markdown row numbers or legacy IDs.

  Place this block **inside the verification block**, not in the task title or
  header. `implement-plugin-health` Phase 3 greps for this token to close the
  ledger entries after implementation.

- **Commit-message format.** Every task's `git commit -m` must follow
  `profile-al-dev-shared/knowledge/commit-conventions.md`:
  `<emoji> type(scope): subject` — **subject line only** (this is a `tool` repo:
  no WHY block, no body), with the full subject ≤72 characters. Put event IDs in
  the task's `closes_event_ids:` verification block, **never** in the commit
  message (no `[#event_id]` suffix and no `closes_event_ids:` body). Emoji come
  from the canonical table — `🐛` for `fix`, `🚚` for `move`/rename, `📦` for
  `chore`. One compliant example:

  ```bash
  git commit -m "🐛 fix(tooling): narrow lens description to bash blocks"
  ```

- **Path placeholders in spec content.** When a task writes a spec file to disk
  that includes file-path examples (e.g., in JSON schemas or workflow sections),
  use `<date>` as the date placeholder rather than `YYYY-MM-DD`. The plan's own
  forbidden-pattern scan runs `grep -n 'YYYY-MM-DD'` over the created spec file
  at step completion — a literal `YYYY-MM-DD` in path examples will cause that
  scan to fail even though it is intentional documentation.

- **Suppress your Execution Handoff.** Do not present the "Subagent-Driven /
  Inline" prompt or ask "Which approach?". Hand control back to the caller
  (`plan-plugin-findings` Phase 4), which routes execution to
  `/implement-plugin-health`.
