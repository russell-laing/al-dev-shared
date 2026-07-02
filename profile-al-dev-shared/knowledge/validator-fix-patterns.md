# Validator Fix Patterns

Reusable recovery patterns for common validation failures in plan writing.

## Pattern 1: Missing Required Sections

**Trigger:** Validator reports "required section X not present in task N"

**Fix:** Add the missing section block to the task. Sections are:

- `Files:` (create/modify paths)
- `Interfaces:` (consumes/produces)
- Step blocks (numbered `- [ ] **Step N:**`)
- `Verification Block:` (closes_event_ids)

**Steps:**

1. Locate the task
2. Add the missing section in the documented order
3. Re-run validation

## Pattern 2: Duplicate Object IDs

**Trigger:** Validator reports "object X appears in 2 tasks"

**Fix:** An object (file path) can only close one event at a time.

**Steps:**

1. Identify which task's fix is the primary one
2. Merge the other task's steps into it, or
3. Defer one task to a follow-up plan (close_event_ids: [])

## Pattern 3: No REQ Tokens in Specs

**Trigger:** Spec-only task has no verification gate

**Fix:** Spec-only tasks (no behavior change, doc only) carry `closes_event_ids: []`

**Steps:**

1. Confirm the task is documentation-only
2. Set closes_event_ids: [] in verification block
3. Note that the accepted event stays open for future behavior plan

## Pattern 4: Untraced Requirements

**Trigger:** Validator reports "spec requirement X has no task that implements it"

**Fix:** Add a task or extend an existing one.

**Steps:**

1. Map the spec requirement to existing task(s)
2. If unmet, add a new task before commit
3. Ensure each task closes at least one event_id
