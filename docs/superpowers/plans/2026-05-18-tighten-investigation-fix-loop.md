# Tighten Investigation/Fix Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three surgical guardrails — regression-timeline gate, scope-lock checks, and Write-persistence verification — to prevent the three failure patterns identified in the 2026-05-18 session insights report.

**Architecture:** Five additive file edits across four files in `al-dev-shared`. All changes insert new sections or checkpoints; nothing is removed or restructured. No new skills, agents, or validator scripts are created. Each task is a self-contained markdown edit with its own commit.

**Tech Stack:** Markdown, Edit tool, Bash grep for verification.

---

## File Map

| File | Change | Task |
| --- | --- | --- |
| `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md` | A1: Step 1.5, A2: findings template, A3: reconciliation gate | Task 1 |
| `profile-al-dev-shared/skills/al-dev-fix/SKILL.md` | B1: pre-commit scope check in both fix paths | Task 2 |
| `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` | B2: Scope Expansion Gate + developer prompt pass-through | Task 3 |
| `~/.claude/CLAUDE.md` | C1: Write-Persistence Verification subsection | Task 4 |
| `profile-al-dev-shared/knowledge/verification-and-planning.md` | C2: Write-Persistence cross-reference | Task 4 |

---

## Task 1: Suggestion A — Regression-timeline gate (al-dev-investigate)

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md`

Three coordinated edits to one file. Each edit is independent — A1 inserts before Step 2, A2 and A3 insert inside the findings template in Step 4.

- [ ] **Step 1: Read the file to confirm current state**

```bash
wc -l profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
grep -n "### Step" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
```

Expected: ~268 lines; Step 0 at ~37, Step 1 at ~57, Step 2 at ~93, Steps 3/4/5 further down.

- [ ] **Step 2 (A1): Insert Step 1.5 between Step 1 and Step 2**

Find this exact string (the `---` separator between Step 1 and Step 2):

```
---

### Step 2 — Formulate Hypotheses
```

Replace with:

```
---

### Step 1.5 — Regression Timeline

Before formulating hypotheses, capture the regression timeline.
This is metadata for the investigation and a gate against
"pre-existing" misdiagnosis.

Extract or ask the user for:

- **Last known good:** date/version when this last worked correctly
  (or "unknown" if never confirmed working)
- **First reported failure:** date/event of the first failure report
- **Recently working?** yes / no / unknown

If the user did not provide these and they are not in the ticket
context, ASK before proceeding to Step 2. One combined question is
fine ("When did this last work, and when did it first fail?").

Carry these three captured values forward. They become required
fields in the findings file (Step 4) — alongside one derived field
("Implications for hypothesis prioritisation", which you fill in
during Step 4 synthesis based on the captured timeline). They also
influence hypothesis prioritisation during Step 2:

- If **Recently working = yes**, prioritise change-timeline
  hypotheses (recent deployments, platform updates, IP/cert
  changes, dependency upgrades) over pre-existing-defect hypotheses
- If **Recently working = unknown**, treat both hypothesis families
  as equally likely

---

### Step 2 — Formulate Hypotheses
```

- [ ] **Step 3: Verify A1**

```bash
grep -n "Regression Timeline" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
```

Expected: at least two matches — one for `### Step 1.5` (between steps 1 and 2) and one for `## Regression Timeline` (in the template, added in Step 4 below). After this step, only one match is expected.

- [ ] **Step 4 (A2): Insert `## Regression Timeline` block in the findings template**

In Step 4's markdown code block, find:

```
| H4: [text] | ❌ REJECTED | Medium |

## Root Cause
```

Replace with:

```
| H4: [text] | ❌ REJECTED | Medium |

## Regression Timeline

- **Last known good:** YYYY-MM-DD / version / "unknown"
- **First reported failure:** YYYY-MM-DD / event
- **Recently working?** yes | no | unknown
- **Implications for hypothesis prioritisation:** [1 sentence]

## Root Cause
```

- [ ] **Step 5 (A3): Insert reconciliation gate after Root Cause description in the findings template**

In the same Step 4 markdown code block, find:

```
## Root Cause

[1–3 sentences. State which confirmed hypothesis is the actual
cause. If inconclusive, state what data is needed to resolve it.]

## Evidence
```

Replace with:

```
## Root Cause

[1–3 sentences. State which confirmed hypothesis is the actual
cause. If inconclusive, state what data is needed to resolve it.]

**Pre-existing claim reconciliation (required if Root Cause is
labelled "pre-existing" or "environmental"):**

If you are about to write Root Cause as a pre-existing defect or
environmental cause, you MUST first reconcile with the Regression
Timeline above:

- If **Recently working = yes**: a pre-existing label is a
  contradiction. Either (a) the defect was latent and a recent
  change triggered it — identify the trigger, OR (b) the Recently
  Working assessment was wrong — explain how. Do NOT submit
  "pre-existing" without one of these reconciliations.
- If **Recently working = no/unknown**: state the evidence that
  rules out a recent trigger before accepting pre-existing.

Write the reconciliation as a paragraph immediately under Root
Cause, prefixed `**Reconciliation:**`.

## Evidence
```

- [ ] **Step 6: Verify all three A-changes**

```bash
grep -n "Step 1.5" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
grep -n "## Regression Timeline" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
grep -n "Pre-existing claim reconciliation" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
```

Expected:
- `Step 1.5` on a line between Step 1 and Step 2 headings
- `## Regression Timeline` on a line inside the Step 4 template (between `## Verdict` and `## Root Cause`)
- `Pre-existing claim reconciliation` on a line inside the Step 4 template (between `## Root Cause` and `## Evidence`)

- [ ] **Step 7: Line count sanity check**

```bash
wc -l profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
```

Expected: substantially more than the original ~268 lines (A1 adds ~23 lines, A2 adds ~7 lines, A3 adds ~14 lines → approximately 312 lines total).

- [ ] **Step 8: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
git commit -m "$(cat <<'EOF'
feat(investigate): add regression-timeline gate (A1, A2, A3)

Step 1.5 captures last-known-good/first-failure/recently-working before
hypothesis formulation. Required Regression Timeline section added to the
findings template. Pre-existing claim reconciliation gate added to Root
Cause section — fires only when verdict would be labelled pre-existing or
environmental, requiring explicit reconciliation with the timeline.

Addresses 'confident pre-existing conclusions' friction pattern from
2026-05-18 insights report.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Suggestion B1 — Pre-commit scope check (al-dev-fix)

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`

Two edits: one in the Trivial Fix path (Step 2a), one in the Non-Trivial Fix path (Step 2b). Each inserts a scope-check step between the compile step and the "Present fix to user" step, and renumbers the steps that follow.

- [ ] **Step 1: Read the file to confirm current state**

```bash
wc -l profile-al-dev-shared/skills/al-dev-fix/SKILL.md
grep -n "^[0-9]\+\." profile-al-dev-shared/skills/al-dev-fix/SKILL.md
```

Expected: ~402 lines; numbered steps appear in both the Step 2a and Step 2b sections.

- [ ] **Step 2: Insert scope check in Step 2a (Trivial Fix path)**

Find this exact block (steps 4–6 of the trivial path):

```
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

Replace with:

```
4. Run compile + lint pass per
   `knowledge/compile-lint-procedure.md`.
   No re-iteration gate in this skill — if compilation fails,
   have the developer fix the error and re-run.

5. Pre-commit scope check — run `git status` and classify every
   changed file against the original symptom:

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

7. Clean up (shut down developer)
```

- [ ] **Step 3: Insert scope check in Step 2b (Non-Trivial Fix path)**

Find this exact block (steps 7–9 of the non-trivial path):

```
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

Replace with:

```
7. Run compile + lint pass per
   `knowledge/compile-lint-procedure.md`.
   No re-iteration gate in this skill — if compilation fails,
   have the developer fix the error and re-run.

8. Pre-commit scope check — run `git status` and classify every
   changed file against the original symptom:

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

10. Clean up (shut down architect, developer)
```

- [ ] **Step 4: Verify B1 insertion**

```bash
grep -n "Pre-commit Scope Check\|Pre-commit scope check" profile-al-dev-shared/skills/al-dev-fix/SKILL.md
```

Expected: two matches — one in Step 2a (trivial path) and one in Step 2b (non-trivial path).

- [ ] **Step 5: Verify no step-number collision (check that 6 and 9 appear as expected)**

```bash
grep -n "^6\. Present\|^9\. Present\|^7\. Clean\|^10\. Clean" profile-al-dev-shared/skills/al-dev-fix/SKILL.md
```

Expected: `6. Present` in the trivial block, `9. Present` in the non-trivial block, `7. Clean up` after trivial present, `10. Clean up` after non-trivial present.

- [ ] **Step 6: Line count sanity check**

```bash
wc -l profile-al-dev-shared/skills/al-dev-fix/SKILL.md
```

Expected: ~402 + ~20 lines per insertion = approximately 440 lines.

- [ ] **Step 7: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-fix/SKILL.md
git commit -m "$(cat <<'EOF'
feat(fix): add pre-commit scope diff checkpoint (B1)

Inserts a scope-check step between compile and present in both the
trivial and non-trivial fix paths. Lists all changed files, classifies
each as in/out of scope, and gates on user confirmation before presenting
when out-of-scope files are detected.

Addresses 'scope creep during fixes' friction pattern from
2026-05-18 insights report.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Suggestion B2 — Scope Expansion Gate (al-dev-develop)

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`

Two edits: insert the gate as a named section near the top, then add a pass-through reference in the Phase 3 developer prompt template.

- [ ] **Step 1: Read the file to confirm current state**

```bash
wc -l profile-al-dev-shared/skills/al-dev-develop/SKILL.md
grep -n "^## " profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Expected: ~604 lines; top-level sections visible including Prerequisites, Phase 0 through Phase 10.

- [ ] **Step 2: Insert Scope Expansion Gate section between Prerequisites and Phase 0**

Find:

```
## Prerequisites

`.dev/*-al-dev-plan-solution-plan.md` must exist (from
/plan). If missing, tell the user to run /plan first
and stop.

## Phase 0: Check for Existing Progress
```

Replace with:

```
## Prerequisites

`.dev/*-al-dev-plan-solution-plan.md` must exist (from
/plan). If missing, tell the user to run /plan first
and stop.

## Scope Expansion Gate

While executing this skill, BEFORE you (or any dispatched
developer agent) edit a file or change a line that is not
explicitly named in the approved plan, you MUST:

1. Pause the in-flight edit.
2. List the proposed out-of-scope change(s) as numbered items:

   ~~~text
   **Proposed out-of-scope changes:**
   1. [file:line] — [what would change and why]
   2. [file:line] — [what would change and why]
   ~~~

3. Present to the user with this exact prompt:
   "These changes are outside the approved plan. Approve, reject,
   or defer each. Reply with item numbers (e.g., '1 approve, 2
   defer')."
4. Wait for per-item decision before resuming.

**What counts as "out of scope":**

- New file not listed in the plan
- Edit to a file listed in the plan but to a line/function the
  plan does not name
- Fixing an "encountered" issue (lint warning, deprecated API,
  unrelated bug) that the plan did not call out

**What does NOT count as "out of scope":**

- Cosmetic adjustments inside an in-scope edit (whitespace,
  formatter output)
- Importing a dependency required to implement an in-scope change

This gate is passed verbatim into every developer agent dispatch
in Phase 3 so the rule propagates to subagents.

## Phase 0: Check for Existing Progress
```

- [ ] **Step 3: Add scope gate pass-through to Phase 3 developer prompt template**

In Phase 3, find the end of the developer prompt template block. The current template ends with:

```
IMPORTANT: Do NOT run git commit. Your role is to implement
and verify compilation only. Commits are handled separately
by /al-dev-commit after user approval.
```

Replace with:

```
IMPORTANT: Do NOT run git commit. Your role is to implement
and verify compilation only. Commits are handled separately
by /al-dev-commit after user approval.

SCOPE EXPANSION GATE: Before editing any file or line not
explicitly named in the plan, you MUST pause and list the
proposed change(s) as numbered items in this format:

  **Proposed out-of-scope changes:**
  1. [file:line] — [what would change and why]

Then present to the user: "These changes are outside the
approved plan. Approve, reject, or defer each. Reply with
item numbers (e.g., '1 approve, 2 defer')."

Wait for per-item decision before resuming. Do NOT silently
expand scope by fixing encountered lint warnings, deprecated
APIs, or unrelated issues not named in the plan.
```

- [ ] **Step 4: Verify B2 insertions**

```bash
grep -n "Scope Expansion Gate" profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Expected: two matches — one for the `## Scope Expansion Gate` section header, one inside the Phase 3 developer prompt template as `SCOPE EXPANSION GATE:`.

- [ ] **Step 5: Verify gate is inside the Phase 3 prompt block**

```bash
grep -n "Phase 3\|SCOPE EXPANSION GATE\|Phase 4" profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Expected: `SCOPE EXPANSION GATE:` appears on a line number between `Phase 3` and `Phase 4`.

- [ ] **Step 6: Line count sanity check**

```bash
wc -l profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Expected: ~604 + ~38 lines (gate section) + ~12 lines (prompt addition) = approximately 654 lines.

- [ ] **Step 7: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-develop/SKILL.md
git commit -m "$(cat <<'EOF'
feat(develop): add Scope Expansion Gate with developer prompt pass-through (B2)

Inserts named Scope Expansion Gate section near the skill top — fires when
Claude or a dispatched developer agent is about to edit outside the approved
plan. Gate propagates verbatim into the Phase 3 developer dispatch prompt so
subagents apply the same rule.

Addresses 'scope creep during multi-task development' friction pattern from
2026-05-18 insights report.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Suggestion C — Write-Persistence Verification rule

**Files:**
- Modify: `~/.claude/CLAUDE.md` (global)
- Modify: `profile-al-dev-shared/knowledge/verification-and-planning.md`

Both are in different repos and neither targets AL source; apply the Write-persistence rule globally, then add a pointer in the knowledge layer.

- [ ] **Step 1: Read global CLAUDE.md to confirm current state**

```bash
wc -l ~/.claude/CLAUDE.md
grep -n "File Editing Safety\|Directories to Avoid" ~/.claude/CLAUDE.md
```

Expected: `## File Editing Safety` at line 15, `## Directories to Avoid` at line 25; that's 9 lines for the section (lines 15–23).

- [ ] **Step 2 (C1): Add Write-Persistence Verification subsection in global CLAUDE.md**

Find the exact string at the end of the "File Editing Safety" section:

```
- When referencing code, use exact line numbers
  (e.g., `AssignJobV6.Codeunit.al:45-67`) to avoid re-reads.

## Directories to Avoid
```

Replace with:

```
- When referencing code, use exact line numbers
  (e.g., `AssignJobV6.Codeunit.al:45-67`) to avoid re-reads.

### Write-Persistence Verification

The Write tool can silently fail to persist a file (e.g., on
cross-repo handoffs, when path parents are missing, or when the
harness drops the result). Treat a Write tool call as a *claim*
of success — verify before acting on it.

Rules:

- After every Write tool call that creates a NEW file path,
  immediately run `ls -la <path>` (or read the file) to confirm
  the file exists on disk before reporting the work complete or
  moving to the next step.
- If the file is large or its content matters for downstream
  steps, also confirm content (e.g., `wc -l <path>`, or Read the
  first N lines).
- If verification fails, do NOT silently retry with Write — switch
  to Bash (`mkdir -p` parent, then `cat <<EOF > path`) and re-verify.
- Never tell the user "I've written X" without having verified
  X exists on disk.

Edit-tool calls do not need this check (Edit errors loudly on
mismatch), but a Write to a path the harness has not yet seen
does.

## Directories to Avoid
```

- [ ] **Step 3: Verify C1**

```bash
grep -n "Write-Persistence Verification" ~/.claude/CLAUDE.md
```

Expected: one match under `## File Editing Safety` (before `## Directories to Avoid`).

- [ ] **Step 4: Read verification-and-planning.md to confirm current state**

```bash
wc -l profile-al-dev-shared/knowledge/verification-and-planning.md
```

Expected: 31 lines (last line is `- Prefer additive edits and avoid diverging behavior wording across harness project instructions files.`).

- [ ] **Step 5 (C2): Append Write-Persistence cross-reference to verification-and-planning.md**

Find the last line of the file:

```
- Prefer additive edits and avoid diverging behavior wording across harness project instructions files.
```

Replace with:

```
- Prefer additive edits and avoid diverging behavior wording across harness project instructions files.

## Write-Persistence

See `~/.claude/CLAUDE.md` → "File Editing Safety" → "Write-Persistence
Verification" for the project-wide rule. Skills that produce new
artefact files (findings, plans, reports, contexts) MUST verify
file existence after Write before reporting the artefact complete.
```

- [ ] **Step 6: Verify C2**

```bash
grep -n "Write-Persistence" profile-al-dev-shared/knowledge/verification-and-planning.md
```

Expected: one match — the new `## Write-Persistence` section header.

- [ ] **Step 7: Line count checks**

```bash
wc -l ~/.claude/CLAUDE.md
wc -l profile-al-dev-shared/knowledge/verification-and-planning.md
```

Expected: `~/.claude/CLAUDE.md` increases from 43 to ~63 lines; `verification-and-planning.md` increases from 31 to ~37 lines.

- [ ] **Step 8: Commit verification-and-planning.md**

Note: `~/.claude/CLAUDE.md` is the global user config — it lives outside this repo and should NOT be committed via git. The change there is a direct file edit only.

```bash
git add profile-al-dev-shared/knowledge/verification-and-planning.md
git commit -m "$(cat <<'EOF'
docs(knowledge): add Write-Persistence cross-reference to verification-and-planning

Points skills that produce new artefact files to the Write-Persistence
Verification rule in ~/.claude/CLAUDE.md so the rule surfaces at skill time
without duplicating the canonical text in every skill file.

Addresses 'Write tool calls that silently fail to persist' friction pattern
from 2026-05-18 insights report.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Full Verification Sweep

Run all seven spec-mandated grep checks to confirm every change landed correctly on `HEAD`.

- [ ] **Step 1: A1 — Step 1.5 inserted between Step 1 and Step 2**

```bash
grep -n "Step 1.5" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
```

Expected: one match labelled `### Step 1.5 — Regression Timeline`. Confirm the line number falls between the Step 1 header line and the Step 2 header line:

```bash
grep -n "### Step 1 —\|### Step 1.5\|### Step 2 —" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
```

Expected: Step 1 line < Step 1.5 line < Step 2 line.

- [ ] **Step 2: A2 — `## Regression Timeline` present in the Step 4 template**

```bash
grep -n "## Regression Timeline\|## Verdict\|## Root Cause" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
```

Expected: `## Verdict` line < `## Regression Timeline` line < `## Root Cause` line (all inside the Step 4 template block).

- [ ] **Step 3: A3 — Reconciliation gate present**

```bash
grep -n "Pre-existing claim reconciliation" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
```

Expected: one match inside the Step 4 template, after the `## Root Cause` line and before `## Evidence`.

- [ ] **Step 4: B1 — Pre-commit scope check in al-dev-fix**

```bash
grep -n "Pre-commit scope check" profile-al-dev-shared/skills/al-dev-fix/SKILL.md
```

Expected: two matches — one in the trivial path (Step 2a) and one in the non-trivial path (Step 2b).

- [ ] **Step 5: B2 — Scope Expansion Gate in al-dev-develop**

```bash
grep -n "Scope Expansion Gate\|SCOPE EXPANSION GATE" profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Expected: two matches — one `## Scope Expansion Gate` section header near the top, one `SCOPE EXPANSION GATE:` inside the Phase 3 developer dispatch prompt.

- [ ] **Step 6: C1 — Write-Persistence Verification in CLAUDE.md**

```bash
grep -n "Write-Persistence Verification" ~/.claude/CLAUDE.md
```

Expected: one match under the `## File Editing Safety` section.

- [ ] **Step 7: C2 — Write-Persistence cross-reference in knowledge file**

```bash
grep -n "Write-Persistence" profile-al-dev-shared/knowledge/verification-and-planning.md
```

Expected: one match — the `## Write-Persistence` section.

- [ ] **Step 8: Forbidden pattern scan on all changed tracked files**

```bash
git diff HEAD~4 --name-only | xargs grep -l "YYYY-MM-DD\|TODO\|TBD\|Co-Authored-By" 2>/dev/null || echo "No forbidden patterns found"
```

Expected: `No forbidden patterns found` (or only hits in commit trailers which are outside file content).

- [ ] **Step 9: Final summary**

All 7 spec grep checks pass. Report to user:

```text
Verification complete — all 7 spec checks pass.

A1: Step 1.5 (Regression Timeline) inserted ✅
A2: ## Regression Timeline block in findings template ✅
A3: Pre-existing claim reconciliation gate in Root Cause ✅
B1: Pre-commit scope check in al-dev-fix (both paths) ✅
B2: Scope Expansion Gate in al-dev-develop + developer prompt ✅
C1: Write-Persistence Verification in ~/.claude/CLAUDE.md ✅
C2: Write-Persistence cross-reference in verification-and-planning.md ✅

Smoke tests (manual, next real use):
1. /al-dev-investigate — confirm regression-timeline question appears and findings file contains ## Regression Timeline
2. /al-dev-fix — let one out-of-scope file slip through; confirm scope check surfaces it
3. /al-dev-develop — observe developer agents pause before out-of-scope edits
4. Write-persistence — implicit; confirm ls -la follows any new artefact Write
```
