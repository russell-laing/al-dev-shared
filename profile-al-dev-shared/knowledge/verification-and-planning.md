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
| User decision gate | AskUserQuestion tool | USER_GATE |
| Subagent retry | re-dispatch Agent with updated prompt | re-dispatch with updated prompt |
| Pattern scan (grep) | Bash tool: `grep` or `rg` | Bash tool: `rg` or `git diff \| grep` |

---

## References

- **CLAUDE.md** → "Plan Task Verification Standard" and "Write-Persistence Verification" sections (project instructions)
- **skills/al-dev-investigate/SKILL.md** → Step 0 — Target Confirmation (workflow implementation)
- **skills/al-dev-plan/SKILL.md** → Phase 2–4 architect briefing and facilitation (workflow implementation)
