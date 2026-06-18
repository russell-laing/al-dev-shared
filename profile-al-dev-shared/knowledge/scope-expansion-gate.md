# Scope Expansion Gate

A governance checkpoint enforced during development that prevents out-of-scope
changes. Before editing outside the approved scope baseline, the developer must
stop and present proposed changes to the user for per-item approval. The scope
baseline may come from an approved solution plan or, for request-driven fix
workflows, from the original reported symptom and agreed fix target. Prevents
scope creep and ensures the solution stays true to the approved work.

## Gate Procedure

BEFORE editing outside the approved scope baseline:

1. **Stop** — do not invoke the edit tool yet.
2. List the proposed out-of-scope change(s) as numbered items:

   ```text
   **Proposed out-of-scope changes:**
   1. [file:line] — [what would change and why]
   2. [file:line] — [what would change and why]
   ```

3. Present to the user with this exact prompt:
   "These changes are outside the approved scope. Approve, reject,
   or defer each. Reply with item numbers (e.g., '1 approve, 2 defer')."
4. Wait for per-item decision before resuming. Do NOT continue writing code
   until the user confirms each item.

`defer` means do not make that proposed change in the current run.

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
agent. For plan-driven implementation workflows, include this gate (or a
reference to this file) in every developer spawn prompt so the rule propagates
to subagents. For request-driven fix workflows, an equivalent lightweight scope
check may be used as long as it stops on out-of-scope changes and gets explicit
per-item user decisions before those changes are kept.

## Delegated-Task Scope Pack

When an orchestrating skill delegates work to a spawned agent, the scope
baseline must travel with the task as an explicit scope pack so the agent
enforces the same gate the orchestrator would. A scope pack is the minimal set
of fields a delegated agent needs to know what is in scope and to stop on
anything outside it:

- **In-scope objects/files** — the exact objects, files, or modules the agent
  owns for this task.
- **In-scope change description** — what the agent is expected to change, drawn
  from the approved plan or the agreed fix target.
- **Out-of-scope rule** — a reference to the "What Counts as Out of Scope" list
  above and the instruction to stop and surface numbered proposals before
  editing anything outside the in-scope set.
- **Halt-and-report contract** — the agent returns a numbered out-of-scope
  proposal list instead of making the change, and waits for per-item approval.

Every developer spawn prompt MUST include the scope pack. The pack is how the
Propagation rule reaches subagents: without it, a spawned agent has no scope
baseline to enforce.
