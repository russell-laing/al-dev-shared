# Scope Expansion Gate

A governance checkpoint enforced during development that prevents out-of-scope
changes. Before editing any file or line not explicitly named in the approved
solution plan, the developer must stop and present proposed changes to the user
for per-item approval. Prevents scope creep and ensures the solution stays true
to the plan.

## Gate Procedure

BEFORE editing a file or line not explicitly named in the approved plan:

1. **Stop** — do not invoke the edit tool yet.
2. List the proposed out-of-scope change(s) as numbered items:

   ```text
   **Proposed out-of-scope changes:**
   1. [file:line] — [what would change and why]
   2. [file:line] — [what would change and why]
   ```

3. Present to the user with this exact prompt:
   "These changes are outside the approved plan. Approve, reject,
   or defer each. Reply with item numbers (e.g., '1 approve, 2 defer')."
4. Wait for per-item decision before resuming. Do NOT continue writing code
   until the user confirms each item.

If no out-of-scope changes are proposed, proceed with the edits.

## What Counts as "Out of Scope"

- New file not listed in the plan
- Edit to a procedure, field, or object not referenced in the plan, even if
  it is in a file the plan does name
- Fixing an "encountered" issue (lint warning, deprecated API, unrelated bug)
  that the plan did not call out

## What Does NOT Count as "Out of Scope"

- Cosmetic adjustments inside an in-scope edit (whitespace, formatter output)
- Importing a dependency required to implement an in-scope change

## Propagation

This gate applies to the orchestrating skill and to every spawned developer
agent. Include this gate (or a reference to this file) in every developer
spawn prompt so the rule propagates to subagents.
