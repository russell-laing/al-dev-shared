---
name: al-dev-test
description: Develop comprehensive test suite with parallel test engineers.
argument-hint: "[optional: specific test focus or scope]"
---

# Test Skill

Develop a comprehensive AL test suite by spawning 4 specialized
test engineer agents in parallel, then iterating until all
tests pass. You do NOT write tests yourself.

## Prerequisites

AL implementation must exist (source files to test).
Optionally: solution plan from `.dev/*-al-dev-plan-solution-plan.md`
for context.

## Phase 1: Analyse Implementation

If `$ARGUMENTS` is provided, treat it as a scope override
(e.g. "validation logic only", "scenario tests"). Restrict
the test engineering team to that scope in Phase 4.

1. Use the AL Symbols MCP (`al-mcp-server`) to analyse
   implemented objects:
   - `al_search_objects` — locate all project AL objects
     in scope
   - `al_get_object_summary` — get a quick overview of
     each object's purpose, fields, and procedures
   - `al_get_object_definition` — inspect codeunits and
     their method signatures in detail to understand
     what needs unit testing
2. Read solution plan from `.dev/*-al-dev-plan-solution-plan.md` if
   available
3. Read `.dev/project-context.md` if available
4. Identify what needs testing:
   - Business logic and calculation methods
   - Data validation rules
   - UI workflows
   - Integration points and event subscribers

## Phase 2: Categorise Test Scenarios

Sort test needs into four categories:

**Unit tests** — isolated functions:
- Calculation methods, validation logic
- Data transformations, pure functions

**Integration tests** — object interactions:
- Table-codeunit flows, event subscribers
- Multi-object workflows, API integrations

**Scenario tests** — end-to-end:
- Complete user workflows (UI -> logic -> database)
- Real-world business use cases

**Edge case tests** — boundaries and errors:
- Null/empty inputs, boundary values (min/max)
- Error conditions, invalid data

## Phase 3: Assign Object ID Ranges

Check `.dev/project-context.md` for the project's available
ID ranges before assigning anything. Test codeunit IDs must
not overlap with production objects.

If project-context.md specifies available test ranges, use
those. If not, use these defaults — but verify they are free:

| Engineer | Default ID Range |
| -------- | ---------------- |
| Unit | 50100-50199 |
| Integration | 50200-50299 |
| Scenario | 50300-50399 |
| Edge case | 50400-50499 |

If any default range conflicts with existing project objects,
shift all four ranges by 100 (e.g. 50500-50899) until a clean
block is found, and note the chosen ranges in the prompt to
each engineer.

## Phase 4: Spawn Test Engineering Team

Spawn all 4 agents in parallel:

Use the ID ranges assigned in Phase 3 (not the defaults if
you shifted them).

**al-dev-unit-test-engineer:**
```text
Develop unit tests for [feature].
Test codeunit ID range: [assigned range from Phase 3]
Focus: [list key methods to test]
Use AL Test Framework. One behaviour per test method.
```

**al-dev-integration-test-engineer:**
```text
Develop integration tests for [feature].
Test codeunit ID range: [assigned range from Phase 3]
Focus: [list integration points]
Test event subscribers, table-codeunit flows.
```

**al-dev-scenario-test-engineer:**
```text
Develop end-to-end scenario tests for [feature].
Test codeunit ID range: [assigned range from Phase 3]
Focus: [list business scenarios]
Simulate real user actions through to database.
```

**al-dev-edge-case-test-engineer:**
```text
Develop edge case and error tests for [feature].
Test codeunit ID range: [assigned range from Phase 3]
Focus: [list edge cases]
Test error handling, validation failures, boundaries.
```

Include context from solution plan and project-context.md
in each prompt.

## Phase 5: Verify on Completion

When all engineers complete:

1. Check for ID conflicts — no two engineers should have
   used the same codeunit ID
2. Verify coverage alignment — all key scenarios from
   Phase 2 have at least one test
3. Resolve any open questions about mocking or test
   fixtures before proceeding to bc-test

## Phase 6: Run bc-test

When all engineers complete:

```bash
bc-test -o .dev/test-results.txt
```

- All passing: proceed to Phase 8
- Some failing: proceed to Phase 7

## Phase 7: Iterate on Failures

For each failing test:

1. Identify owner by ID range
2. Diagnose the failure — is it a test bug (wrong
   assertion, bad fixture) or an implementation bug
   (the code under test is broken)?
3. **Test bug:** Assign fix to that engineer with the
   error message, re-run, repeat.
4. **Implementation bug:** Do not silently loop. Stop
   and escalate to the user — explain which test is
   failing, what the test expects, and what the code
   actually does. The user decides whether to fix the
   implementation or adjust the requirement.

If the same test keeps failing after 2 fix attempts by
the engineer, treat it as an implementation bug and
escalate regardless.

## Phase 8: Validate and Write Test Plan

YOU write the synthesis yourself to
`.dev/$(date +%Y-%m-%d)-al-dev-test-test-plan.md`:

```markdown
## Test Plan: [Feature Name]

### Test Coverage Summary
- Unit tests: [N] tests covering [methods/functions]
- Integration tests: [N] tests covering [integrations]
- Scenario tests: [N] tests covering [workflows]
- Edge case tests: [N] tests covering [boundaries/errors]

**Total:** [N] tests, all passing

### Test Codeunits Created
- Test Codeunit 501xx: "[Name]" - Unit tests
- Test Codeunit 502xx: "[Name]" - Integration tests
- Test Codeunit 503xx: "[Name]" - Scenario tests
- Test Codeunit 504xx: "[Name]" - Edge case tests

### Key Test Scenarios
[5-10 most important test scenarios]

### Test Execution
Command: bc-test -o .dev/test-results.txt
Result: All [N] tests passing

### Coverage Analysis
Covered:
- [Key functionality 1]
- [Key functionality 2]

Not covered (if applicable):
- [Gap]: [Rationale for skipping]

### Test Maintenance Notes
[How to run tests, dependencies, special setup]
```

After writing, run the validator:

```bash
VALIDATOR="$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-test/validate-test-plan.py"
TEST_PLAN=$(ls .dev/*-al-dev-test-test-plan.md 2>/dev/null | sort | tail -1)
[ -f "$VALIDATOR" ] && [ -n "$TEST_PLAN" ] && \
  python3 "$VALIDATOR" "$TEST_PLAN" \
  || echo "Validator not found — skipping"
```

Fix any issues before presenting.

## Phase 9: Present to User

```text
Test suite complete -> [N] tests, all passing

Test coverage:
- Unit: [N] tests
- Integration: [N] tests
- Scenario: [N] tests
- Edge cases: [N] tests

Test results -> .dev/test-results.txt
Test plan -> .dev/<date>-al-dev-test-test-plan.md

Ready for deployment?
```

USER_GATE — ask the user with options:
- Approve - Tests are adequate
- Add More Tests - What scenarios should I add?
- Review Failures - Show me problematic tests
- Stop - Cancel testing

