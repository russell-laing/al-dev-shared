# Plugin Reliability & Quality Improvements — Design Spec

**Date:** 2026-05-15
**Status:** Approved
**Repos:** `al-dev-shared`, `claude-configs`

## Background

Usage data (2026-04-11 to 2026-05-11, 205 sessions) surfaced three recurring friction categories not addressed by in-flight plans (`session-friction-remediation`, `commit-validation-enforcement`, `commit-conventions-adoption`, `trim-md-mermaid-helper`):

1. **Subagent outputs don't get verified before commit** — 31 buggy-code and 20 wrong-approach friction events trace to tasks completing without checking that files persisted, acceptance criteria were met, or forbidden patterns were absent.
2. **External findings accepted without verification** — plans built on codeburn output, lint reports, or mismatched findings files required costly mid-session rewrites after the user prompted fact-checking.
3. **Architect debate is passive, not adversarial** — al-dev-plan spawns architects but the debate prompt allows convergence; writing-plans doesn't debate at all.

This spec covers surgical extensions to address all three. Out of scope: self-healing nightly skill library (separate infrastructure concern, warrants its own spec).

---

## Architecture

9 targeted file changes across two repos. No new skill files, no new infrastructure.

| File | Repo | Theme |
|---|---|---|
| `CLAUDE.md` | al-dev-shared | 1, 3 |
| `profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md` | al-dev-shared | 1 |
| `profile-al-dev-shared/skills/al-dev-plan/SKILL.md` | al-dev-shared | 2a, 3 |
| `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md` | al-dev-shared | 2a |
| `profile-claude-vault/skills/vault-weave/SKILL.md` | claude-configs | 2b |
| `profile-claude-vault/skills/vault-add-project/SKILL.md` | claude-configs | 2b |
| `profile-claude-vault/skills/vault-distill/SKILL.md` | claude-configs | 2b |
| `profile-claude-vault/skills/vault-induct/SKILL.md` | claude-configs | 2b |

All changes are additive — prepend or append text; no section rewrites. Existing skill invocations are unaffected.

---

## Theme 1: Closed-Loop Execution Reliability

### Problem

`superpowers:executing-plans` (not owned) has no built-in post-task verification. Plans generated in al-dev-shared don't consistently require a persistence check, so subagent tasks can complete with unpersisted files, placeholder strings, or partially-met criteria.

### Solution

Enforce verification at two owned layers:

**Layer A — CLAUDE.md (inherited by all plans in this repo)**

Add a `## Plan Task Verification Standard` section to `al-dev-shared/CLAUDE.md`:

```markdown
## Plan Task Verification Standard

Every plan task must end with a verification step before its commit:

1. `git status` shows expected file changes (not empty, no unexpected extras)
2. No forbidden patterns in changed files: `[date]`, `YYYY-MM-DD`, `TODO`, `Co-Authored-By`
3. Each acceptance criterion stated in the task spec is met in actual file content
4. On failure: re-execute with failure context embedded; cap at 3 retries; escalate after

When dispatching subagents to execute plan tasks, pass the above checklist in the
dispatch prompt so subagents self-verify before returning.
```

**Layer B — `al-dev-autonomous` Phase 4**

After the existing compile/lint loop (Phase 3), add Phase 4: Post-Task Verify:

```markdown
## Phase 4: Post-Task Verify

After each developer subagent returns, before the commit gate:

1. Run the Plan Task Verification Standard checklist (see CLAUDE.md)
2. If checklist passes → proceed to commit
3. If checklist fails → re-dispatch developer subagent with:
   - The original task description
   - The specific failure items from the checklist
   - Instruction: fix only the listed failures, do not re-do passing items
4. Maximum 3 retries; after 3 failures escalate to user with failure summary
```

### What this does not change

The structure of existing plan documents. The verification steps are added by developers/subagents following the CLAUDE.md rule, not hardcoded into every plan's markdown. Plans that already include explicit verification steps (like `session-friction-remediation`) continue to work as-is.

---

## Theme 2a: External Claims Verification

### Problem

`al-dev-plan` passes findings straight to architect agents without confirming the claims match current repo state. `al-dev-investigate` loads ticket context including tool output (codeburn, external analysis) and treats it as authoritative.

### Solution — `al-dev-plan`: New Phase 1.5

Insert between Phase 1 (Gather Context) and Phase 2 (Spawn Architect Team):

```markdown
## Phase 1.5: Verify External Claims

If the request references a findings file, codeburn output, lint report,
or any third-party analysis:

1. For each file path mentioned in the findings:
   - Confirm the file exists at that exact path
   - Spot-check that the described content/issue is present
2. For each symbol, procedure, or API mentioned:
   - Grep or use AL MCP to confirm it exists in the current codebase
3. Build an evidence summary:
   - ✅ Verified claims — pass to architects as facts
   - ⚠️ Unverified claims — pass to architects as hypotheses to test, not design inputs
4. Include the evidence summary in every architect prompt under a
   `**External findings status:**` heading

If >50% of claims are unverified, surface this to the user before spawning
architects and offer to re-run investigation with corrected inputs.
```

### Solution — `al-dev-investigate`: Tool Output Framing

Add to Step 1 Load Context, after reading ticket context:

```markdown
**Tool output framing:** If the ticket context or provided findings include
output from external tools (codeburn, lint analyzers, third-party plugins),
treat each claim as a hypothesis to test — not an established finding.
Add each tool-output claim to the hypothesis list and test it against the
actual codebase before including it in the confirmed findings.
```

---

## Theme 2b: Target Disambiguation

### Problem

Skills that accept findings files don't confirm whether the document's target matches the user's intent before acting. This caused the vault-add-project vs al-dev-review mismatch (findings targeting the wrong skill, only caught mid-session).

### Solution — Disambiguation gate

Add the following block at the start of each affected skill, before any other action, as **Phase 0 / Step 0**:

```markdown
## Step 0: Target Confirmation

Before acting on any findings file or context document:

1. Identify the target named in the findings (skill, file, or repo)
2. Identify the target from the user's request
3. Output:

   > **Target check:**
   > - Findings reference: [name from findings]
   > - Your request: [name from user message]
   > - Output path: [absolute path where work will land]
   >
   > Do these match? If findings and request disagree, stop and confirm before
   > proceeding.

If they match, continue. If they differ, flag the mismatch and wait.
```

**Apply to (al-dev-shared):**
- `al-dev-plan/SKILL.md` — insert after Phase 1 step 2 (requirements file check), before Phase 1.5
- `al-dev-investigate/SKILL.md` — insert as Step 0 before Step 1

**Apply to (claude-configs vault):**
- `vault-weave/SKILL.md` — insert as Step 0 before first action
- `vault-add-project/SKILL.md` — insert after existing `client-protocol.md` check (that check verifies the *vault*, this check verifies the *project target*)
- `vault-distill/SKILL.md` — insert as Step 0 before first action
- `vault-induct/SKILL.md` — insert as Step 0 before first action

---

## Theme 3: Depth-First Planning

### Problem

`al-dev-plan` Phase 2 tells architects to "be prepared to debate trade-offs" — a passive instruction that allows convergence. Writing-plans produces a single plan with no adversarial review.

### Solution — `al-dev-plan` Phase 2: Mandatory Critique

Extend each architect prompt to require adversarial output:

```markdown
Each architect must produce THREE outputs (not one):

1. **Proposal** — their complete solution design (current behavior)
2. **Critique** — a specific critique of ONE other approach listed in the
   Phase 2 briefing. Must name concrete failure modes, not vague concerns.
   Example: "Approach B's event-driven model fails if the subscriber fires
   before the header is fully committed — race condition in posting codeunit."
3. **Falsification** — one condition under which their OWN approach fails.
   Example: "This table extension approach breaks if the customer later
   requires multi-company consolidation because..."

Architects without all three outputs will not be included in Phase 3 synthesis.
```

Extend Phase 3 (Facilitate Debate) synthesis instructions to explicitly incorporate the critiques and falsifications when producing the winning plan.

### Solution — CLAUDE.md routing note

Add to `al-dev-shared/CLAUDE.md` (near the AL Development section):

```markdown
## Planning Routing

For MEDIUM+ plans (4+ files, novel architecture, or ambiguous requirements):
prefer starting with `/al-dev-plan` to run the competitive architect debate,
then use `superpowers:writing-plans` to convert the winning design into a
task plan. Using `writing-plans` alone for MEDIUM+ work skips adversarial
review and increases wrong-approach risk.
```

---

## Spec Self-Review

**Placeholder scan:**
- No `TBD`, `TODO`, or incomplete sections
- All code blocks are complete examples
- All file paths are exact

**Internal consistency:**
- Theme 1 (verification) and Theme 3 (planning depth) both touch `al-dev-plan` and `CLAUDE.md` — changes are additive and non-overlapping
- Theme 2b disambiguation gate is identical text across all 6 skill files — easy to apply uniformly
- al-dev-autonomous Phase 4 references CLAUDE.md rule rather than duplicating it — single source of truth

**Constraint propagation:**
- No "must not contain X" rules defined in this spec
- All changes are additive; nothing removes existing behaviour

**Scope check:**
- 9 file changes; implementation plan should be 9 tasks (one per file), each independently committable
- Vault changes (4 files) are in a separate repo — plan must note this and sequence or separate accordingly

---

## Implementation Notes

- Vault changes require opening Claude Code from `~/claude-configs/`
- al-dev-shared changes can be executed in this repo
- Recommend grouping into two plans: one for al-dev-shared (5 tasks), one for claude-configs vault (4 tasks)
- Each task should include a `wc -l` before/after check per the File Editing Safety rule in global CLAUDE.md
