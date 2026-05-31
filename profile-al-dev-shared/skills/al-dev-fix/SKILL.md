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

## Intent Preflight

Before spawning an architect or developer, editing files, or running a mutating
fix path, apply `knowledge/intent-preflight.md`.

Default intent for this skill is `EDIT`. If the request asks only to review,
audit, investigate, explain, or assess a possible fix without applying changes,
stop and ask the intent-mismatch prompt from `knowledge/intent-preflight.md`
before any mutating action or implementation agent dispatch.

## Artifact Contract

Use `knowledge/artifact-contracts.md` as the source of truth for this skill's
durable outputs and success evidence.

Do not claim the fix is complete, validated, or ready for the next workflow
step until the success evidence named in
`knowledge/artifact-contracts.md` for `al-dev-fix` has been produced and read
for the current run.

---

## Usage

```bash
/fix "Customer validation not working for negative credit limits"
```

---

## How This Command Works (v3.0)

**Your Role:** Engineering Manager (but streamlined)
**Teammates:** Usually 1 al-dev-shared:al-dev-developer-traditional (or -tdd if test plan), sometimes 1 al-dev-shared:al-dev-solution-architect for complex fixes
**You:** Quick analysis, delegate implementation, verify fix, present

### ❌ DON'T

- Implement the fix yourself
- Skip all planning (for non-trivial fixes)
- Run this for new features (use `/al-dev-plan` → `/al-dev-develop` instead)

### ✅ DO

- Analyze complexity first (trivial vs non-trivial)
- Spawn architect for quick plan if needed (5 min max)
- Spawn single developer for implementation
- Verify fix using the current-run success evidence required by `knowledge/artifact-contracts.md` for `al-dev-fix` (compile/lint output or other bounded verification result)
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

### Step 2: Trivial Fix (2-5 min)

```text
For trivial fixes:

1. Identify the file and issue
   - Use Grep/Read to locate the problem
   - Verify you understand the issue

2. Spawn single al-dev-shared:al-dev-developer-traditional
   (trivial fixes have no test plan — see
   `knowledge/developer-invocation-patterns.md`, Context 2):
   "Fix [specific issue] in [file path].

    Issue: [description]
    Expected fix: [what needs to change]

    Verify the fix compiles.
    Keep it minimal - only change what's necessary."

3. Developer implements fix

4. Run compile + lint pass per
   `knowledge/compile-lint-procedure.md`.
   (See `markdown/compile-output-best-practices.md` for critical safeguards on compile output handling — never pipe to terminal viewers.)
   If compilation fails, fix only errors caused by the small
   change and re-run compile once.

5. Pre-commit scope check — run `git status` and classify every
   changed file against the original symptom. Populate each entry
   below from the `git status` output — list every modified or new
   file, classified as in- or out-of-scope:

   ~~~text
   **Scope diff:**

   In scope (directly fixes the reported symptom):
   - path/to/file1.al — [one-line reason]

   Out of scope (encountered while fixing, not in original request):
   - path/to/extra.al — [what was changed and why]
   ~~~

   **Decision rule:**

   - If "Out of scope" is empty → proceed to step 6.
   - If "Out of scope" has entries → STOP. Show the list to the
     user and ask: "These are outside the original fix. Keep, revert,
     or split into a separate commit?" Wait for per-item decisions
     before presenting.

6. Present fix to user:
   "Fix complete → [file path]

    Changed: [1-line description]
    [Show code diff if small]

    Compilation: [✅ Success / Not verified]
    Lint: [✅ Clean / N unresolved items → lint-report.md]

    Ready to test?"
```

**No approval gate - present fix directly.**

### Step 3: Non-Trivial Fix (10-20 min)

Follow the **Quick Analysis** pattern in
`knowledge/architect-invocation-patterns.md`.

```text
For non-trivial fixes:

0. Load performance constraints if available:
   PERF=$(ls .dev/*-al-dev-perf-perf-analysis.md 2>/dev/null | sort | tail -1)
   If found: read CRITICAL/HIGH findings. Pass them as
   "Known performance constraints: [findings]" in the architect prompt (step 1).
   If not found: skip this step.

0.5. Load prior lint findings if available:
   LINT=$(ls .dev/*-al-dev-lint-lint-report.md 2>/dev/null | sort | tail -1)
   If found: parse UNRESOLVED items and include in the architect dispatch prompt
   as "Known linting constraints: [list of UNRESOLVED items]".
   If not found: skip this step.

1. Assess fix complexity to determine architect model tier:
   - **SIMPLE tier** (use sonnet): root cause is obvious, 1-2 files, < 20 lines to change
   - **COMPLEX tier** (use opus — default): root cause is unclear, multi-file, ≥ 20 lines, or architectural impact

   Spawn al-dev-shared:al-dev-solution-architect for quick analysis.
   - If complexity = SIMPLE: include `model: sonnet` in the Agent tool invocation
   - If complexity = COMPLEX: omit model parameter (agent default opus applies)

   Include this in the dispatch prompt:
   "**Fix Complexity Tier:** [SIMPLE|COMPLEX]
   Follow `knowledge/al-symbol-pre-flight.md` for symbol verification rigor. Ensure all proposed changes reference verified AL symbol definitions."

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

5. Spawn the developer with the confirmed approach.

   See `knowledge/developer-invocation-patterns.md` (Context 2: Trivial
   Direct Fix) for dispatcher consistency when spawning a developer.

   For non-trivial fixes: check for a test plan (same as /al-dev-develop),
   then dispatch al-dev-developer-tdd or al-dev-developer-traditional
   accordingly:

   ```bash
   TEST_PLAN=$(ls .dev/*-al-dev-test-test-plan.md 2>/dev/null | sort | tail -1)
   ```

   - Test plan present → `al-dev-shared:al-dev-developer-tdd`
   - No test plan → `al-dev-shared:al-dev-developer-traditional`

   Dispatch prompt:
   "Implement fix based on this approach:

    Root cause: [from architect]
    Fix approach: [from architect]
    Files to change: [from architect]

    Follow the recommended approach.
    Verify compilation after changes."

6. Developer implements fix

7. Run compile + lint pass per
   `knowledge/compile-lint-procedure.md`.
   (See `markdown/compile-output-best-practices.md` for critical safeguards on compile output handling — never pipe to terminal viewers.)
   If compilation fails, keep compile correction bounded to the
   confirmed root-cause scope.

8. Pre-commit scope check — run `git status` and classify every
   changed file against the original symptom. Populate each entry
   below from the `git status` output — list every modified or new
   file, classified as in- or out-of-scope:

   ~~~text
   **Scope diff:**

   In scope (directly fixes the reported symptom):
   - path/to/file1.al — [one-line reason]

   Out of scope (encountered while fixing, not in original request):
   - path/to/extra.al — [what was changed and why]
   ~~~

   **Decision rule:**

   - If "Out of scope" is empty → proceed to step 9.
   - If "Out of scope" has entries → STOP. Show the list to the
     user and ask: "These are outside the original fix. Keep, revert,
     or split into a separate commit?" Wait for per-item decisions
     before presenting.

9. Present fix to user:

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
```

**Still no approval gate, but more context provided.**

---

## Decision Tree

```text
User: "/fix [issue]"
    ↓
You: Analyze complexity [Is it TRIVIAL or NON-TRIVIAL?]
    ↓
    ├─→ TRIVIAL (simple, obvious, single-file)
    │   ├─→ Spawn 1 al-dev-shared:al-dev-developer-traditional
    │   ├─→ Fix implemented
    │   ├─→ Verify compilation
    │   ├─→ Scope check
    │   └─→ Present to user ✅
    │
    └─→ NON-TRIVIAL (complex, unclear)
        ├─→ Spawn al-dev-shared:al-dev-solution-architect (5 min analysis)
        ├─→ Review approach yourself
        ├─→ Spawn al-dev-shared:al-dev-developer-tdd (if test plan) or al-dev-developer-traditional (if no test plan) with approach
        ├─→ Fix implemented
        ├─→ Verify compilation
        ├─→ Scope check
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

This skill uses `knowledge/compile-lint-procedure.md` for compile and lint
passes. For trivial fixes, compile once after the minimal edit and report a
concise result. If compilation fails, fix only errors caused by the small change
and re-run compile once; do not expand into a broad compile-fix loop. For
non-trivial fixes, keep compile correction bounded to the confirmed root-cause
scope.

```text
✅ Compilation successful
❌ Compilation failed: [error]
⚠️  Compilation not verified (al-compile unavailable)
```

If compilation fails: for trivial fixes, fix only errors caused by the small
change and re-run compile once; for non-trivial fixes, keep compile correction
bounded to the confirmed root-cause scope before presenting to the user.

---

## Examples

For detailed walkthroughs of two common fix scenarios, see [`knowledge/al-dev-fix-examples.md`](../knowledge/al-dev-fix-examples.md).

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
→ For trivial fixes, fix only errors caused by the small change and re-run
compile once. For non-trivial fixes, keep compile correction bounded to the
confirmed root-cause scope.

**Fix seems to need multiple approaches?**
→ This might be a feature, not a fix. Suggest `/al-dev-plan` instead.

**Unclear if 0 vs null vs empty means "no limit"?**
→ Grep existing code for patterns, or escalate to user

---

**Remember:** /al-dev-fix is for speed. Analyze quickly, delegate clearly,
verify compilation, present directly.
