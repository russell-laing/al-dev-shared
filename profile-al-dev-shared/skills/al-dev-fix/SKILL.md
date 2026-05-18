---
name: al-dev-fix
description: Lightweight bug fix workflow without approval gates (fast iteration)
argument-hint: "[description of the bug or issue]"
---


**Lightweight bug fix workflow without formal approval gates.**

---

## Purpose

Quick iteration for bug fixes and small changes:
- Fast analysis (1-2 min)
- Minimal planning for non-trivial fixes
- Direct implementation
- No formal approval gates (faster flow)

---

## Usage

```bash
/fix "Customer validation not working for negative credit limits"
```

---

## How This Command Works (v3.0)

**Your Role:** Engineering Manager (but streamlined)
**Teammates:** Usually 1 al-developer, sometimes 1 solution-architect for complex fixes
**You:** Quick analysis, delegate implementation, verify fix, present

### ❌ DON'T

- Implement the fix yourself
- Skip all planning (for non-trivial fixes)
- Run this for new features (use `/al-dev-plan` → `/al-dev-develop` instead)

### ✅ DO

- Analyze complexity first (trivial vs non-trivial)
- Spawn architect for quick plan if needed (5 min max)
- Spawn single developer for implementation
- Verify fix compiles
- Present fix directly (no formal approval gate)

---

## Implementation Steps

### Step 1: Quick Analysis (1-2 min)

```text
Read user's fix request and classify complexity:

TRIVIAL (90% of fixes):
- Typo or simple logic error
- Missing validation
- Wrong field reference
- Clear, obvious fix
- Single file change

Example: "Fix typo in error message"
Example: "Add missing null check"
Example: "Change >= to > in validation"

NON-TRIVIAL (10% of fixes):
- Root cause unclear
- Multiple files affected
- BC integration issue
- Architectural change needed
- Requires understanding complex flow

Example: "Posting fails intermittently"
Example: "Event subscriber not triggering"
Example: "Performance degradation after upgrade"
```

### Step 2a: Trivial Fix (2-5 min)

```text
For trivial fixes:

1. Identify the file and issue
   - Use Grep/Read to locate the problem
   - Verify you understand the issue

2. Spawn single al-developer:
   "Fix [specific issue] in [file path].

    Issue: [description]
    Expected fix: [what needs to change]

    Verify the fix compiles.
    Keep it minimal - only change what's necessary."

3. Developer implements fix

4. Run compile + lint pass per
   `knowledge/compile-lint-procedure.md`.
   No re-iteration gate in this skill — if compilation fails,
   have the developer fix the error and re-run.

5. Present fix to user:
   "Fix complete → [file path]

    Changed: [1-line description]
    [Show code diff if small]

    Compilation: [✅ Success / Not verified]
    Lint: [✅ Clean / N unresolved items → lint-report.md]

    Ready to test?"

6. Clean up (shut down developer)
```

**No approval gate - present fix directly.**

### Step 2b: Non-Trivial Fix (10-20 min)

Follow the **Quick Analysis** pattern in
`knowledge/architect-invocation-patterns.md`.

```text
For non-trivial fixes:

1. Spawn solution-architect for quick analysis:
   "Analyze this issue and provide quick fix approach:

    Issue: [user's description]
    Context: [relevant files/objects]

    Provide:
    1. Root cause hypothesis (2-3 sentences)
    2. Recommended fix approach (bullet points)
    3. Files that need changes
    4. Risks/side effects to watch for

    Keep it concise - 5 min analysis, not full solution plan."

2. Review architect's analysis yourself:
   - Does root cause make sense?
   - Is fix approach sound?
   - Are there risks?

3. If approach unclear, refine with the architect:
   "Your hypothesis about [X] doesn't account for [Y].
    Re-analyze considering [constraint]."

4. Present root-cause confirmation to the user:

   "Root cause hypothesis: [architect's 2-3 sentences]
    Evidence: [key evidence points]
    Alternative considered: [one alternative]
    Estimated scope: [files that will change]

    Proceed with this fix approach? (yes / revise)"

   - yes → proceed to step 5
   - revise → feed user's correction back to architect for
     one more pass, re-present once; if still unclear after
     that, ask the user to decide directly

5. Spawn al-developer with confirmed approach:
   "Implement fix based on this approach:

    Root cause: [from architect]
    Fix approach: [from architect]
    Files to change: [from architect]

    Follow the recommended approach.
    Verify compilation after changes."

6. Developer implements fix

7. Run compile + lint pass per
   `knowledge/compile-lint-procedure.md`.
   No re-iteration gate in this skill — if compilation fails,
   have the developer fix the error and re-run.

8. Present fix to user:
   "Fix complete → [files changed]

    Root cause: [brief explanation]
    Fix approach: [1-2 sentences]

    Changed files:
    - [file 1]: [change description]
    - [file 2]: [change description]

    Compilation: [✅ Success / Not verified]
    Lint: [✅ Clean / N unresolved items → lint-report.md]

    Risks to watch: [from architect analysis]

    Ready to test?"

9. Clean up (shut down architect, developer)
```

**Still no approval gate, but more context provided.**

---

## Decision Tree

```text
User: "/fix [issue]"
    ↓
You: Analyze complexity
    ↓
    ├─→ TRIVIAL (simple, obvious)
    │   ├─→ Spawn 1 al-developer
    │   ├─→ Fix implemented
    │   ├─→ Verify compilation
    │   └─→ Present to user ✅
    │
    └─→ NON-TRIVIAL (complex, unclear)
        ├─→ Spawn solution-architect (5 min analysis)
        ├─→ Review approach yourself
        ├─→ Spawn al-developer with approach
        ├─→ Fix implemented
        ├─→ Verify compilation
        └─→ Present to user ✅
```

---

## When to Use /al-dev-fix vs Other Commands

**✅ Use /al-dev-fix for:**
- Bug fixes
- Small corrections
- Logic errors
- Missing validations
- Quick improvements
- Anything you'd call a "fix" not a "feature"

**❌ Don't use /al-dev-fix for:**
- New features → Use `/al-dev-plan` then `/al-dev-develop`
- Architectural changes → Use `/al-dev-plan` first
- Multiple related changes → Use `/al-dev-plan` for coordination
- Anything needing formal approval gates

**Rule of thumb:** If it's fixing something broken, use `/al-dev-fix`.
If it's adding something new, use `/al-dev-plan`.

---

## Fast Iteration Philosophy

This command intentionally **skips approval gates** for fast iteration:

**Traditional workflow:**

```text
Fix → Code Review → User Approval → Testing
(Slow but thorough)
```

**/fix workflow:**

```text
Fix → Compilation Check → Present to User → User Tests
(Fast but requires user to verify)
```

**Trade-off accepted:**
- ✅ Faster feedback loop
- ✅ Less overhead for small changes
- ❌ User must verify fix works (testing phase)
- ❌ Less formal review process

**This is intentional** - fixes need speed, features need thoroughness.

---

## Compilation Verification

This skill uses `knowledge/compile-lint-procedure.md` for all
compile and lint passes. Surface the result using the format below:

```text
✅ Compilation successful
❌ Compilation failed: [error]
⚠️  Compilation not verified (al-compile unavailable)
```

If compilation fails: have the developer fix errors and re-run before
presenting to the user.

---

## Examples

### Example 1: Trivial Fix

```text
User: "/fix Customer validation allows negative credit limits"

You (analysis):
"Trivial - missing validation check in Customer table extension"

You (to developer):
"Add validation in CustomerExt OnValidate trigger for Credit Limit field.
 Error if value < 0."

Developer: [Implements]

You (to user):
"Fix complete → CustomerExt.Table.al

 Added validation: Credit Limit cannot be negative
 Compilation: ✅ Success

 Ready to test?"
```

**Time: 3-4 minutes**

### Example 2: Non-Trivial Fix

```text
User: "/fix Sales posting fails when credit limit is exactly 0"

You (analysis):
"Non-trivial - need to understand posting flow and where check happens"

You (spawn architect):
"Analyze why posting fails when credit limit is exactly 0"

Architect:
"Root cause: CreditValidator uses > instead of >= for comparison.
 Fix: Change comparison logic in ValidateCredit method.
 Risk: Ensure 0 is treated as 'no limit' if that's business rule."

You (review):
"Approach makes sense. Clarify: is 0 'no limit' or 'zero limit'?
 [Ask user or check existing code patterns]"

[User clarifies or you determine from code]

You (to developer):
"Fix comparison in CreditValidator.Codeunit.al ValidateCredit method.
 Change > to >= and document that 0 means [no limit/zero limit]."

Developer: [Implements]

You (to user):
"Fix complete → CreditValidator.Codeunit.al

 Root cause: Comparison logic excluded exactly 0
 Fix: Changed > to >= in ValidateCredit method
 Documented: 0 is treated as [no limit/zero limit]

 Compilation: ✅ Success
 Risk: Watch for edge cases where 0 limit is set intentionally

 Ready to test?"
```

**Time: 12-15 minutes**

---

## Success Criteria

✅ Complexity classified correctly (trivial vs non-trivial)
✅ Developer spawned with clear instructions
✅ Architect spawned only when needed (not for trivial fixes)
✅ Fix compiles successfully
✅ Root cause understood (for non-trivial fixes)
✅ Risks identified (for non-trivial fixes)
✅ Presented to user quickly (no approval gate delays)

---

## Troubleshooting

**Can't determine if trivial or non-trivial?**
→ Default to non-trivial (spawn architect for 5 min analysis)

**Architect's analysis is wrong?**
→ Challenge it yourself, don't blindly accept

**Developer's fix doesn't compile?**
→ Have them fix errors, re-compile, iterate

**Fix seems to need multiple approaches?**
→ This might be a feature, not a fix. Suggest `/al-dev-plan` instead.

**Unclear if 0 vs null vs empty means "no limit"?**
→ Grep existing code for patterns, or escalate to user

---

**Remember:** /al-dev-fix is for speed. Analyze quickly, delegate clearly,
verify compilation, present directly.
