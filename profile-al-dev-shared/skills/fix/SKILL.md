---
name: fix
description: Lightweight bug fix workflow without approval gates (fast iteration)
argument-hint: "[description of the bug or issue]"
---


# Lightweight bug fix workflow without formal approval gates

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
`knowledge/artifact-contracts.md` for `fix` has been produced and read
for the current run.

When shell search or structured-file inspection is required, prefer `rg` and
`jq` before falling back to broader shell text processing.

---

## Usage

```bash
/fix "Customer validation not working for negative credit limits"
```

---

## How This Command Works

**Your Role:** Engineering Manager (but streamlined)
**Teammates:** Usually 1 al-dev-shared:developer-traditional (or -tdd if test plan), sometimes 1 al-dev-shared:solution-architect for complex fixes
**You:** Quick analysis, delegate implementation, verify fix, present

### ❌ DON'T

- Implement the fix yourself
- Skip all planning (for non-trivial fixes)
- Run this for new features (use `/plan` → `/develop-orchestrate` instead)

### ✅ DO

- Analyze complexity first (trivial vs non-trivial)
- Spawn architect for quick plan if needed (5 min max)
- Spawn single developer for implementation
- Verify fix using the current-run success evidence required by `knowledge/artifact-contracts.md` for `fix` (compile/lint output or other bounded verification result)
- Present fix directly (no formal approval gate)

---

## Implementation Steps

### Step 1: Quick Analysis (1-2 min)

**Context load (if present):** Before classifying, glob for the latest
investigation findings and read them when present — they often name the exact
file and confirmed root cause:

<!-- Cross-skill dependency: /investigate → /fix artifact handoff documented in knowledge/artifact-contracts.md -->

`$(ls .dev/*-investigate-findings.md 2>/dev/null | sort | tail -1)`

If a findings file exists, read it and use its confirmed root cause to scope the
fix. This is the handoff from `/investigate`.

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

NON-TRIVIAL (10% of fixes — you don't know exactly where the bug is OR you don't know the exact lines to change):
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

For trivial fixes:

1. Identify the file and issue
   - Use Grep/Read to locate the problem
   - Verify you understand the issue

2. Spawn single `al-dev-shared:developer-traditional` using the
   Context 2 (Traditional path) spawn block of
   `knowledge/developer-invocation-patterns.md` — it includes the `Return:`
   field (files changed + confirmation the fix resolves the issue) that the
   former inline template omitted. Trivial fixes have no test plan, so the
   Traditional path applies.

3. Developer implements fix

4. Run compile + lint pass per
   `knowledge/compile-lint-procedure.md`.
   (See `../../markdown/compile-output-best-practices.md` for critical safeguards on compile output handling — never pipe to terminal viewers.)
   If compilation fails, fix only errors caused by the small
   change and re-run compile once.

5. Pre-commit scope check (implements `../../knowledge/scope-expansion-gate.md`) —
   run `git status` and classify every changed file against the original symptom.
   Populate each entry below from the `git status` output — list every modified or
   new file, classified as in- or out-of-scope:

   ```text
   Scope diff:

   In scope (directly fixes the reported symptom):
   - path/to/file1.al — [one-line reason]

   Out of scope (encountered while fixing, not in original request):
   - path/to/extra.al — [what was changed and why]
   ```

   **Decision rule:**

   - If "Out of scope" is empty → proceed to step 6.
   - If "Out of scope" has entries → STOP. Show the list to the
     user and ask: "These are outside the original fix. Keep, revert,
     or split into a separate commit?" Wait for per-item decisions
     before presenting.

6. Present fix to user:

   ```text
   Fix complete → [file path]

   Changed: [1-line description]
   [Show code diff if small]

   Compilation: [pass / Not verified]
   Lint: [Clean / N unresolved items → lint-report.md]

   Ready to test?
   ```

**No approval gate - present fix directly.**

### Step 3: Stage and Commit Changes

After the fix is verified and ready, stage and commit it:

Run: `/commit` to stage all modified files and create a git commit with a descriptive message.

This is the standard next step after fix verification. See `/commit` skill for details on commit conventions and optional post-commit workflows.

### Step 4: Test-Plan Routing

After classification (Step 1):

```text
IF complexity == "trivial":
  └─ Test via direct verification (see Step 2 compile pass) (no test plan needed)
  └─ Skip to Step 4

IF complexity == "simple":
  └─ Check if .dev/*-test-test-plan.md exists
  │   ├─ If exists: Read test plan and execute tests using the runner specified in the plan (see knowledge/compile-lint-procedure.md for compile + lint steps)
  │   └─ If not exists: Create simple test case inline, execute, verify
  └─ Move to Step 4

IF complexity == "medium" OR complexity == "complex":
  └─ [ERROR] Non-trivial fixes require the /develop-orchestrate workflow
  └─ Escalate to /plan → /develop-orchestrate
```

Architect dispatch for the non-trivial path follows **Pattern 2: Quick
Analysis** in `../../knowledge/architect-invocation-patterns.md` — one
architect, time-bounded, four-section return.

---

## When to Use /fix vs Other Commands

**✅ Use /fix for:**

- Bug fixes
- Small corrections
- Logic errors
- Missing validations
- Quick improvements
- Anything you'd call a "fix" not a "feature"

**❌ Don't use /fix for:**

- New features → Use `/plan` then `/develop-orchestrate`
- Architectural changes → Use `/plan` first
- Multiple related changes → Use `/plan` for coordination
- Anything needing formal approval gates

**Rule of thumb:** If it's fixing something broken, use `/fix`.
If it's adding something new, use `/plan`.

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

For detailed walkthroughs of two common fix scenarios, see [`knowledge/fix-examples.md`](../../knowledge/fix-examples.md).

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
→ This might be a feature, not a fix. Suggest `/plan` instead.

**Unclear if 0 vs null vs empty means "no limit"?**
→ Grep existing code for patterns, or escalate to user

---

**Remember:** /fix is for speed. Analyze quickly, delegate clearly,
verify compilation, present directly.

---

## Optional: Formal Code Review After Fix

`/fix` intentionally skips the formal review panel for speed. If you
decide to run the full three-reviewer panel after a non-trivial fix (for
example, because the change touches critical business logic), use the two-step
pattern:

1. Run `/review-develop-preflight` and wait for the preflight output.
   Confirm it reports "Prerequisites: all met" before proceeding.

2. Then run `/review-develop` to dispatch the reviewer panel.

Do not run `/review-develop` directly — the preflight step locates the
correct handoff, identifies changed files, and verifies compile status first.
