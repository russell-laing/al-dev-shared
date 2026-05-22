# Verification and Planning Parity Guide

This guide is the shared reference for cross-harness operational standards in multi-phase workflows. Referenced by agents in al-dev-shared that need to:
- Verify completed work before moving to the next phase
- Confirm targets before starting work
- Run adversarial architecture planning

Read this when: running `/al-dev-plan`, building multi-phase skills, or implementing robust task verification.

---

## Plan Task Verification

Every plan task must end with a verification step before its commit. This is the completion criteria for task execution.

### The 4-Step Verification Checklist

**1. File Persistence Check**
- Run: `git status` to confirm expected files were written
- Verify: No empty files (file size > 0), no unexpected extra files added
- Fail if: A file you claimed to write doesn't appear or is empty

**2. Forbidden Pattern Scan**

Scan all changed files for patterns that indicate incomplete work. Use grep to find:

```bash
# Check for unrendered date placeholders ([date], [YYYY-MM-DD])
git diff --name-only --cached | xargs grep -l "\[date\]\|\[YYYY-MM-DD\]" 2>/dev/null && echo "FAIL: Found unrendered date placeholders"

# Check for TODO/TBD markers (incomplete work)
git diff --cached --unified=0 | grep "^+" | grep -E "TODO|TBD" && echo "FAIL: Found incomplete work markers"

# Check for harness-specific debug comments
git diff --cached | grep -E "claude:|copilot:" && echo "FAIL: Found harness-specific debug code"

# If all checks pass:
echo "PASS: No forbidden patterns found"
```

Run this before committing to catch common verification failures.

Patterns that must not appear in changed files:

- `[date]` (e.g., `[2026-05-15]`) — indicates unrendered template variable
- `YYYY-MM-DD` (literal string, not a date value) — unrendered placeholder
- `TODO` or `TBD` — incomplete work
- `Co-Authored-By` (in code comments — allowed only in git trailers)
- `claude:` or `copilot:` prefixed comments — harness-specific debugging left in

**3. Acceptance Criteria Verification**
- Read the task spec / requirements
- For each acceptance criterion stated, verify it is **actually met** in the file content
- Example: If task says "SetLoadFields example must appear," grep for `SetLoadFields` in the written file
- Do NOT assume acceptance criteria are met because the file exists

**4. Failure Recovery**
On verification failure:
1. Re-execute the task with the specific failures embedded in the prompt for context
2. Cap at **3 total retries** per task
3. After 3 failures, escalate to the user with a summary of what failed and why

---

## External Claims Verification

Whenever an agent reports that something was done — a file written, code compiled, tests passed — the claim must be verified externally, not just inferred from a non-error return.

### What Counts as a Claim

- "File written" — the agent called Write
- "Compilation succeeded" — the agent ran `al-compile`
- "Tests passed" — the agent ran a test suite
- "Pattern scan found N matches" — the agent ran grep/rg
- "Branch created" — the agent ran git commands

### Verification Pattern

For each claim, follow this pattern:

1. **Don't rely on tool return codes alone** — a tool returning exit code 0 does NOT prove the claim
2. **Verify the output artifact exists** — For file writes: `ls -la <path>` or `wc -l <path>`. For compilation: check the output log file exists and has content. For tests: read the test result file.
3. **Spot-check the content** — Don't just check that the file exists; sample its content to confirm it's not corrupted or empty
4. **State what was verified** — In the response: "File written: confirmed via `ls -la`, 245 lines, no forbidden patterns"

### Special Case: Write Tool

After every Write tool call:
- Run `ls -la <file>` immediately
- If file is large or its content matters downstream, also run `wc -l <file>` or Read the first N lines
- If verification fails, escalate to user immediately — do NOT silently retry with Write

### Example

**Wrong:** "Code review written to `.dev/2026-05-19-code-review.md`" (claims without verifying)

**Right:** "Code review written to `.dev/2026-05-19-code-review.md` (verified: 187 lines, no forbidden patterns, all acceptance criteria present)"

### Verification Checkpoint Template

Every multi-phase skill should use this checkpoint structure after each phase:

**File:** `.dev/progress.md`

```markdown
# Skill Execution Progress

## Phase 0: Requirements Analysis
- [x] Read ticket/spec
- [x] Identified 3 affected modules (Table, Codeunit, Page)
- [x] Risk assessment complete (medium complexity, 1 data model change)

**Output:** Requirements context file saved to `.dev/requirements.md`

**Resume capability:** Can restart from Phase 1 with requirements cached

---

## Phase 1: Design & Planning
- [ ] Architect debate completed
- [ ] Design decision: Use event-based architecture (vs. procedure override)
- [ ] Plan written to `.dev/2026-05-22-solution-plan.md`

**Next:** Phase 2 (Implementation) can proceed with design from Phase 1

---

## Phase 2: Implementation
- [ ] Code changes: Table 18 (+5 fields), Codeunit 50000 (new procedure), Page 42 (new FactBox)
- [ ] Tests written: 8 test procedures
- [ ] Code review: Waiting for approval

**Status:** Paused pending review

---

## Phase 3: Verification
- [ ] Local test run: 8/8 tests passing
- [ ] Compile check: 0 errors
- [ ] Integration test: Feature end-to-end verified

**Result:** Ready for commit
```

This structure lets agents:
1. Resume at any phase (check `.dev/progress.md` at start)
2. Know what was output from prior phases (references to `.dev/*.md` files)
3. Checkpoint after each phase (prevents context loss in long sessions)

---

## Target Confirmation (Step 0)

Before acting on any user request, investigation findings, or requirements, confirm the target. This prevents cross-talk where the current context doesn't match the stated task.

### Three Targets to Match

1. **Findings reference** — If acting on an investigation result, what did the findings document claim needs fixing?
2. **User request** — What did the user explicitly ask you to do?
3. **Output path** — Where will the result be written?

### The Confirmation Process

Identify and validate alignment:

```
**Target Check:**

- Findings reference: [extracted from findings file, or "none if no findings"]
- User request: [extracted from user message]
- Output path: [absolute path where work will land]

Do these match?
```

**If all three align:** Continue to the next step.

**If findings and request disagree:**
1. STOP — do not proceed
2. Ask the user to confirm:
   - "Restart the investigation with clarified requirements?" OR
   - "Proceed with the current scope despite the mismatch?"
3. Wait for explicit user answer before proceeding

### Example

User says: "Fix the authentication bug in the new signup flow."

You find: Investigation findings mention a bug in login flow, not signup.

**Action:** Stop and ask the user which one. Don't guess.

---

## Depth-First Planning (Proposal + Critique + Falsification)

For complex architectural decisions, use adversarial planning: architect agents propose solutions, critique each other, and identify their own limitations. All three outputs are required.

### Why Three Outputs?

- **Proposal alone** is prone to confirmation bias (the proposer sees only its strengths)
- **Proposal + Critique** catches obvious flaws but may miss subtle risks
- **Proposal + Critique + Falsification** forces honest assessment of design limits

### The Three Architect Outputs

Each architect MUST produce all three. Architects without all three are excluded from the final decision phase.

**1. Proposal** — The recommended approach
- Complete solution design addressing all requirements
- Object structure, extension points, BC integration, data model
- Why this approach is better than the alternatives you were briefed on

**2. Critique** — Specific critique of ONE other approach from the briefing
- Name concrete failure modes (not vague concerns)
- Identify observable conditions or code-level breakage where the other approach fails
- Example (strong): "Approach B will deadlock under concurrent order processing because it holds table locks across two FindSet loops without releasing — concurrent orders on the same customer trigger the deadlock" (specific, testable)
- Example (weak): "Approach B may have performance issues" (vague, not actionable)

**3. Falsification** — Where YOUR approach fails
- State the design limits honestly
- Describe realistic conditions where your solution breaks or doesn't scale
- Example: "This approach requires all documents to fit in memory; if processing > 100MB of line items, memory pressure becomes a concern"
- Example: "Event handling adds ~50ms per order in high-concurrency scenarios"

#### Example: Architect Debate on Caching Strategy

**Proposal (Architect A):**
> "Use in-memory cache with 5-minute TTL. Pros: fast, simple. Cons: stale data risk if config changes during window."

**Strong Critique (Architect B):**
> "5-minute TTL is risky for multi-tenant scenarios where tenant A's config could pollute tenant B's cache if deletion happens mid-window. Proposal lacks tenant isolation strategy. Better: use Redis with event-driven invalidation so cache clears immediately when config changes."

**Why that's a strong critique:** It identifies a specific failure case (tenant pollution), explains why it matters (correctness issue), and proposes a concrete alternative (Redis with invalidation).

**Weak Critique (Architect C):**
> "In-memory cache might not be performant enough."

**Why it's weak:** "Might not" is vague (no concrete scenario). No data supporting the concern. No alternative proposed.

**Falsification (You, the decision-maker):**
> "Test case: In-memory cache with Event Subscriber that clears cache on config-change events. Tenant A creates config, Tenant B reads it (should miss cache). Tenant A deletes config, Tenant B reads again (should still miss). If this test passes with immediate invalidation, Architect A's proposal is falsified — we need Redis only if we cannot guarantee event-driven invalidation. Let's prototype event-driven invalidation first."

**Why that's a strong falsification:** It proposes a testable scenario that would validate or invalidate the proposal. Testing beats philosophy.

### Quality Bar

Critiques and falsifications must be substantive enough to force re-evaluation of a design. Weak outputs ("might be slow", "could be hard to maintain") do not meet the bar.

### The Facilitation Process

After all architects submit proposals:

1. Let them work independently (2–5 min, no cross-talk)
2. Facilitate cross-architect debate:
   - "Architect A, explain why your approach is better for maintainability"
   - "Architect B, what's your response to A's upgrade complexity concerns?"
   - "All: Compare event-driven overhead vs. direct integration"
3. Challenge weak points:
   - "Your plan doesn't address scenario X. How would your approach handle it?"
   - "What happens when edge case Y occurs?"
4. Require use of external tools:
   - BC Code Intelligence for architecture patterns
   - MS Docs for BC API specifics
   - AL Symbols MCP for base app exploration

Push architects to think deeper. Superficial solutions are not acceptable.

### Example: Architect Debate on Caching Strategy

**Problem Statement:** Sales order posting takes 2.5 seconds for 100+ lines due to repeated customer balance lookups.

**Three Design Proposals:**

**Proposal 1: Query Optimization (Solo Architect)**
```
Approach: Index customer ledger by customer number, add early-exit in query loop.

Pros: 
- Simplest change: 5 lines of code, no new tables/fields
- Balance remains real-time (no stale cache risk)
- No performance variation (consistent <500ms)

Cons:
- Won't scale beyond 500 lines (index hit still O(n) lookups)
- Ignores root cause (repeated balance calculation inside line loop)

Risk: Medium (low code change, but incomplete solution)
```

**Proposal 2: In-Memory Cache (Conservative)**
```
Approach: Load customer balance into Dictionary on order entry, reuse throughout posting.

Pros:
- Significant speed gain (90% reduction: 2.5s → 0.25s)
- Clear cache invalidation (disposed when order posting done)
- Backward compatible

Cons:
- Requires new Dictionary variable, increases function size
- Breaks if balance changes mid-posting (rare, but possible in integration scenarios)

Risk: Low (well-understood pattern, clear scope)
```

**Proposal 3: Database View + Materialized Cache (Aggressive)**
```
Approach: Create materialized view of customer balance, refresh every 1 hour via batch job, query view instead of ledger.

Pros:
- Fastest performance (0.05s lookup in view)
- Scales to 1000s of lines
- Works across all modules (not just sales posting)

Cons:
- High complexity: new view, new batch job, new sync logic
- Cache can be 1 hour stale (balance might be wrong for recent transactions)
- Requires new monitoring (batch failure alerts)

Risk: High (complex implementation, stale-data risk, cross-module dependencies)
```

**Debate:**
- **Conservative advocate:** "Proposal 2 (in-memory) hits the sweet spot. We're optimizing a single operation (order posting), not the whole system. Materialized view is overengineering."
- **Aggressive advocate:** "Proposal 2 fails if balance changes mid-posting. We should use Proposal 3 — the view is the right abstraction, and we can invest in refresh logic now."
- **Solo architect:** "Actually, let's try Proposal 1 first (query optimization). If it meets the 500ms target, we avoid cache complexity entirely."

**Decision:** Proposal 2 (in-memory cache)

Rationale: Proposal 1 insufficient (doesn't scale), Proposal 3 over-scoped (introduces stale-data risk and cross-module dependencies). Proposal 2 is minimal, isolated, and provides the needed performance (0.25s << 2.5s). Revisit if posting expands beyond 500 lines.

**Implementation task:** Add `customerBalanceCache: Dictionary` to posting procedure, load once, query from cache for all line lookups, clear on exit.

**Verification:** Measure posting time for 100-line order; confirm < 0.5s.

---

### Example: Architect Debate Output — Caching Strategy Decision Document

After the debate resolves, the architect creates a one-page decision document:

```markdown
# Caching Strategy for Sales Order Posting

## Decision: In-Memory Customer Balance Cache

### Context
Sales order posting (100+ lines) takes 2.5s due to repeated ledger lookups.

### Rejected Alternatives
- Query optimization alone (Proposal 1): insufficient scaling past 500 lines
- Materialized view (Proposal 3): over-scoped, introduces stale-data risk

### Implementation
\`\`\`al
procedure PostSalesOrder(var SalesHeader: Record "Sales Header")
var
    customerBalanceCache: Dictionary of [Code[20], Decimal];
begin
    // Load balance once
    LoadCustomerBalances(SalesHeader, customerBalanceCache);
    
    // Query cache for all line lookups (no repeated ledger queries)
    ProcessSalesLines(SalesHeader, customerBalanceCache);
    
    // Clear cache on exit (order-scoped, not persistent)
    customerBalanceCache.Clear();
end;
\`\`\`

### Test Coverage
- test_PostSalesOrder_UsesCache() — verify cache loaded once
- test_PostSalesOrder_Performance() — confirm < 0.5s for 100-line order

### Risk Mitigation
- Cache is order-scoped (cleared on function exit)
- Falls back to ledger query if cache miss (defensible)
- Only used in posting; doesn't affect balance queries in UI

### Rollback Plan
If cache causes test failure: Remove customerBalanceCache variable, revert to uncached ledger queries (recovers original 2.5s behavior).
\`\`\`

This output:
- States the decision clearly
- Documents why alternatives were rejected
- Shows the code implementation
- Lists verification steps
- Includes risk mitigation and rollback path

All future work references this decision document, so developers don't re-litigate the choice.

---

### Evaluation Criteria (for the facilitator)

After debate, evaluate all proposals on:
1. **Completeness** — All requirements addressed? Object design complete?
2. **Technical Quality** — AL best practices? Testability? Edge cases handled?
3. **BC Integration** — Right base objects extended? Appropriate events? Upgrade-safe?
4. **Maintainability** — Clear responsibilities? Extensible design? Follows project patterns?
5. **Trade-offs** — Costs acknowledged? Weak scenarios identified? Complexity justified?

Then decide (facilitator's tactical choice, not the user's):
- **Pick one approach** with clear rationale
- **Create hybrid** combining best elements from multiple approaches
- **Send back** for refinement if all approaches are weak

---

## Cross-Harness Tool Mapping

When updating skill behavior across Claude Code and Copilot CLI, use this mapping:

| Need | Claude Code | Copilot CLI |
|---|---|---|
| User decision gate | USER_GATE | USER_GATE |
| Subagent retry | re-dispatch Agent with updated prompt | re-dispatch with updated prompt |
| Pattern scan (grep) | Bash tool: `grep` or `rg` | Bash tool: `rg` or `git diff \| grep` |

---

## References

- **project instructions file** → "Plan Task Verification Standard" and "Write-Persistence Verification" sections
- **skills/al-dev-investigate/SKILL.md** → Step 0 — Target Confirmation (workflow implementation)
- **skills/al-dev-plan/SKILL.md** → Phase 2–4 architect briefing and facilitation (workflow implementation)
