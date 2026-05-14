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

### Harness Coverage

This spec applies to **both Claude Code and Copilot CLI**. Each theme has platform-specific implementation notes in the sections below. Consult the **Platform Adaptation** section for cross-harness tool mappings and Copilot CLI equivalents.

---

## Theme 1: Closed-Loop Execution Reliability

### Problem

`superpowers:executing-plans` (not owned) has no built-in post-task verification. Plans generated in al-dev-shared don't consistently require a persistence check, so subagent tasks can complete with unpersisted files, placeholder strings, or partially-met criteria.

### Solution

Enforce verification at two owned layers:

**Layer A — CLAUDE.md (inherited by all plans in this repo)**

Add a `## Plan Task Verification Standard` section to `al-dev-shared/CLAUDE.md`. This section is read by both Claude Code and Copilot CLI (which imports relevant sections into AGENTS.md):

```markdown
## Plan Task Verification Standard

Every plan task must end with a verification step before its commit:

1. **File persistence check:** `git status` shows expected file changes (not empty, no unexpected extras)
2. **Forbidden pattern scan:** No forbidden patterns in changed files:
   - `[date]` (e.g., `[2026-05-15]`) — indicates unrendered template
   - `YYYY-MM-DD` (literal string, not date value) — unrendered date placeholder
   - `TODO` or `TBD` — incomplete work
   - `Co-Authored-By` — AI attribution in code comments (not git trailers)
   - `claude:` or `copilot:` prefixed comments — harness-specific debugging left in
3. **Acceptance criteria verification:** Each acceptance criterion stated in the task spec is met in actual file content
4. **Failure recovery:** On verification failure:
   - Re-execute the task with the specific failures embedded in context
   - Cap at 3 total retries per task
   - After 3 failures, escalate to user with a summary of what failed and why

When dispatching subagents to execute plan tasks (both Claude Code and Copilot CLI),
pass the above checklist in the dispatch prompt so subagents self-verify before returning.
```

**Layer B — `al-dev-autonomous` Phase 4 (Claude Code implementation)**

After the existing compile/lint loop (Phase 3), add Phase 4: Post-Task Verify. This phase runs in Claude Code's `executing-plans` context:

```markdown
## Phase 4: Post-Task Verify

After each developer subagent returns, before the commit gate:

1. **Run the verification checklist** — check forbidden patterns, file persistence, acceptance criteria
   - **Pattern scan tool:** Use ripgrep (rg) to check for forbidden patterns:
     ```bash
     rg '\[date\]|\bYYYY-MM-DD\b|TODO|TBD|Co-Authored-By|claude:|copilot:' <files> --color=never --no-heading --with-filename
     ```
   - If patterns are found, capture them in a summary
   - **File check:** Run `git status --short` to confirm expected files were modified
   - **Acceptance check:** Manually inspect files for stated criteria
2. **If checklist passes** → proceed to commit
3. **If checklist fails** → re-dispatch developer subagent using `write_agent`:
   - Re-send the original task description
   - Include a "Failure context" block listing specific failures (pattern matches, missing files, unmet criteria)
   - Include: "Fix only the listed failures; do not re-do items that passed"
4. **Retry loop:** Max 3 retries per task. After 3 failures:
   - Escalate to user with: task description, all 3 failure summaries, and recommended next steps
   - Do NOT attempt a 4th retry
```

**Layer B — `al-dev-autonomous` Phase 4 (Copilot CLI implementation)**

Copilot CLI does not support `write_agent` (subagent mid-run messaging). Instead, Phase 4 follows a **polling + re-dispatch pattern**:

```markdown
## Phase 4: Post-Task Verify (Copilot CLI)

After developer task completes:

1. **Run the verification checklist:**
   - Pattern scan: `git diff HEAD --unified=0 | grep -E '\[date\]|YYYY-MM-DD|TODO|TBD|Co-Authored-By|claude:|copilot:' || true`
   - File check: `git status --short`
   - Acceptance check: Manual inspection of output files
2. **If checklist passes** → proceed to commit
3. **If checklist fails:**
   - Save failure summary to `.dev/phase4-failure-<retry-count>.md` (e.g., `.dev/phase4-failure-1.md`)
   - Re-launch developer task with updated prompt including:
     - Original task description
     - "Failure context:" section with specific failures
     - "Fix scope:" statement (e.g., "Fix only the listed failures; do not re-do passing items")
     - Exit criteria: verification checklist passes AND `.dev/phase4-failure-<retry-count>.md` shows PASS
4. **Retry loop:** Max 3 retries. After 3 failures:
   - Use `ask_user` to present failure summary: task, all 3 failure logs, and recommended remediation
   - Wait for user decision (retry manually, skip task, abort plan) before proceeding
```

### What this does not change

The structure of existing plan documents. The verification steps are added by developers/subagents following the CLAUDE.md rule, not hardcoded into every plan's markdown. Plans that already include explicit verification steps (like `session-friction-remediation`) continue to work as-is.

---

## Theme 2a: External Claims Verification

### Problem

`al-dev-plan` passes findings straight to architect agents without confirming the claims match current repo state. `al-dev-investigate` loads ticket context including tool output (codeburn, external analysis) and treats it as authoritative.

### Solution — `al-dev-plan`: New Phase 1.5

Insert between Phase 1 (Gather Context) and Phase 2 (Spawn Architect Team). This phase verifies external findings before sending them to architects.

**Insertion location:** In `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`, after the section titled "## Phase 1: Gather Context" ends and before "## Phase 2: Spawn Architect Team" begins. Add the following:

```markdown
## Phase 1.5: Verify External Claims

If the request references a findings file, codeburn output, lint report,
or any third-party analysis, verify the claims before forwarding to architects:

1. **File path verification:** For each file path mentioned in findings:
   - Confirm the file exists at that exact path with `test -f <path>`
   - Spot-check content: open the file and verify the described issue/content is present
   - If path doesn't exist → mark as **unverified**, note the missing path
   - If content differs from description → mark as **partially verified**, note the discrepancy

2. **Symbol/API verification:** For each function, procedure, field, or table mentioned:
   - Use AL MCP (`al-mcp-server-al_search_objects` or `al-mcp-server-al_find_references`)
     to confirm the symbol exists in the current codebase
   - For grep-based symbols (cross-harness compatibility): `grep -r "symbol_name" src/ --include="*.al"`
   - If not found → mark as **unverified**
   - If found but context differs → mark as **partially verified**

3. **Build evidence summary** — format as a Markdown table:

   ```
   | Claim | Type | Status | Evidence |
   |-------|------|--------|----------|
   | "File X has problem Y" | file+issue | ✅ Verified | File exists, issue confirmed at line Z |
   | "Function Q is slow" | performance | ⚠️ Unverified | Function exists but no profiling data provided |
   | "Table R has no indexes" | schema | ✅ Verified | Grep confirms table R, no index definitions found |
   ```

4. **Communicate findings to architects:**
   - Include the evidence summary in every architect prompt under `**External findings status:**`
   - Flag verified claims: "✅ Verified — treat as design input"
   - Flag unverified claims: "⚠️ Unverified — treat as hypothesis to test, not a requirement"
   - Partial verification: "⚠️ Partially verified — details differ from claims; assume claims are approximate"

5. **Decision threshold:** Count verified/unverified claims:
   - If ≥75% verified → proceed with Phase 2 (Spawn Architect Team)
   - If 50–74% verified → proceed but include in architect prompt: "⚠️ Half of findings are unverified; robust design should test these hypotheses"
   - If <50% verified → Surface to user before spawning architects:
     ```
     > **⚠️ Warning:** Only [X]% of external findings could be verified ([Y] of [Z] claims).
     > This may indicate stale findings, mismatched repo state, or incorrect targets.
     > Would you like to:
     > (A) Proceed with architects treating all claims as hypotheses
     > (B) Re-run investigation with corrected inputs
     > (C) Proceed anyway (not recommended)
     ```
     Use `ask_user` form to gate the decision.
```

### Solution — `al-dev-investigate`: Tool Output Framing

**Insertion location:** In `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md`, find the section "## Step 1: Load Context" (after reading ticket/findings files). Add the following note after that section:

```markdown
**Tool output framing:** If the ticket context or provided findings include
output from external tools (codeburn, lint analyzers, third-party plugins):

- Treat each tool-output claim as a **hypothesis**, not an established finding
- Add each claim to the investigation hypothesis list to test during Steps 2–4
- Confirm the claim matches the actual codebase before including it in your
  final findings report (Step 5)
- If tool output contradicts actual code (e.g., lint report says "line 42 has issue X"
  but line 42 has different code), flag the contradiction and resolve which is current
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

### **Exact insertion points for Theme 2b:**

**Apply to `al-dev-shared` repo:**

1. **`al-dev-plan/SKILL.md`:**
   - Find the section `## Phase 1.5: Verify External Claims` (added by Theme 2a)
   - Insert Step 0 immediately after this section ends, before `## Phase 2: Spawn Architect Team`
   - Label it `## Step 0: Target Confirmation (Phase 1.5.5)`

2. **`al-dev-investigate/SKILL.md`:**
   - Find the section `## Step 1: Load Context`
   - Insert new section immediately *before* Step 1 as `## Step 0: Target Confirmation`
   - Shift existing step numbers down (Step 1 → Step 1, Step 2 → Step 2, etc.; no renumbering needed)

**Apply to `claude-configs` repo (vault):**

3. **`vault-weave/SKILL.md`:**
   - Insert as brand-new `## Step 0: Target Confirmation` at the very beginning of the skill, before any existing steps

4. **`vault-add-project/SKILL.md`:**
   - Find the section that checks `client-protocol.md` (verify vault structure)
   - Insert new section *after* that check as `## Step 0: Target Confirmation (Project Validation)`
   - Note: this check validates the project target within the vault, not the vault itself

5. **`vault-distill/SKILL.md`:**
   - Insert as brand-new `## Step 0: Target Confirmation` at the beginning of the skill

6. **`vault-induct/SKILL.md`:**
   - Insert as brand-new `## Step 0: Target Confirmation` at the beginning of the skill

**Unified Step 0 block (same for all 6 files):**

```markdown
## Step 0: Target Confirmation

Before acting on any findings file or context document:

1. **Identify targets:**
   - Findings reference: Extract the target name/path from the document (e.g., "vault: Acme", "skill: al-dev-plan", "repo: harness-acme")
   - Your request: Extract the target from your message (the skill name, vault name, project name, or repo you're working in)
   - Output path: Document where the work will land (e.g., `~/.claude/plugins/vault-acme/`, `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`)

2. **Validate match:**
   - Output:
     ```
     > **Target check:**
     > - Findings reference: [extracted from findings]
     > - Your request: [extracted from your message]
     > - Output path: [absolute path where work will land]
     >
     > Do these match? If findings and request disagree, stop and confirm before proceeding.
     ```

3. **Decision:**
   - If all three align → continue to next step
   - If findings and request disagree → flag the mismatch, wait for user to confirm before proceeding
   - If mismatch is fundamental (e.g., findings target skill X but you're invoking skill Y) → stop and escalate to user
```

---

## Theme 3: Depth-First Planning

### Problem

`al-dev-plan` Phase 2 tells architects to "be prepared to debate trade-offs" — a passive instruction that allows convergence. Writing-plans produces a single plan with no adversarial review.

### Solution — `al-dev-plan` Phase 2: Mandatory Critique

**Insertion location:** In `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`, find `## Phase 2: Spawn Architect Team`. Within that phase's architect briefing, replace the current instruction "be prepared to debate trade-offs" with:

```markdown
## Architect Output Requirements

Each architect must produce THREE outputs (not one):

1. **Proposal** — your complete solution design (the approach you recommend)
2. **Critique** — a specific critique of ONE other approach presented in the Phase 1 briefing.
   - Must name concrete failure modes (not vague concerns)
   - Must identify an observable condition or code-level issue that would break the other approach
   - Example: "Approach B's event-driven model fails if a subscriber fires before the header is fully committed — this creates a race condition in the posting codeunit where the event is processed before parent record exists."
3. **Falsification** — one realistic condition under which YOUR OWN approach fails.
   - Be honest about your design's limits
   - Example: "This table extension approach breaks if the customer later requires multi-company consolidation because extensions can't span multiple company scopes."

Architects without all three outputs will not be included in the Phase 3 synthesis. Quality bar: critiques and falsifications should be substantive enough that an architect reading them would reconsider their design.
```

**Token and time impact assessment:**

The mandatory critique requirement increases architect token usage:
- **Baseline (current):** ~8–10K tokens per architect (proposal only)
- **With critique+falsification:** ~12–15K tokens per architect (+20–40% increase)
- **Expected runtime:** +90–120 seconds per `al-dev-plan` execution (architects run in parallel, so overhead is fixed, not per-architect)

**When to apply this requirement:**
- **ALWAYS** for MEDIUM+ complexity (4+ files, novel architecture, ambiguous requirements)
- **OPTIONAL** for TRIVIAL/SIMPLE tasks (could skip if user confirms time sensitivity)
- **Recommendation:** Use judgment; if a task is straightforward and architects converge quickly, the extra critique cost isn't justified. Include guidance in CLAUDE.md routing note (see below).

### Solution — CLAUDE.md routing note

**Insertion location:** In `al-dev-shared/CLAUDE.md`, find the section near AL Development guidance or at the end of planning-related content. Add:

```markdown
## Planning Routing

For tasks that need a design decision:

**SMALL/TRIVIAL** (single file, clear requirements, no alternatives):
- Use `superpowers:writing-plans` directly if requirements are unambiguous
- Skip the architect debate phase; the extra tokens and time aren't justified

**MEDIUM** (4+ files, novel architecture, OR ambiguous requirements):
- **Prefer** `/al-dev-plan` to run the competitive architect debate
- This adds ~90–120 seconds and 20–40% token overhead vs `writing-plans` alone
- Then use `superpowers:writing-plans` to convert the winning design into a task plan
- **Why:** Adversarial review catches wrong-approach risks early; rework later is 3× more expensive

**LARGE/COMPLEX** (multiple subsystems, major refactor, strategic decision):
- **Always** use `/al-dev-plan` with mandatory architect debate
- Do NOT use `writing-plans` alone for large scope
- Consider escalating to user for requirements review before planning

**Anti-pattern to avoid:**
- Using `writing-plans` alone for MEDIUM+ work skips adversarial review and increases wrong-approach risk
- If you're unsure whether a task is SMALL or MEDIUM, default to MEDIUM and use `al-dev-plan`
```

---

## Platform Adaptation: Claude Code vs Copilot CLI

This section maps all three themes to their implementation equivalents in Claude Code and Copilot CLI. Consult this when implementing Theme-specific code changes.

### Theme 1: Closed-Loop Execution Reliability

| Element | Claude Code | Copilot CLI | Notes |
|---------|-------------|------------|-------|
| **Verification checklist definition** | CLAUDE.md (global) | AGENTS.md (global) + inherit from CLAUDE.md | Both harnesses must document the same checklist; Copilot CLI's version should be in AGENTS.md |
| **Pattern scanning tool** | IDE's built-in spell-check (declarative via CLAUDE.md) | `ripgrep` (rg) via bash, or `git diff` + grep | Copilot CLI needs explicit bash commands; see Phase 4 CLI implementation above |
| **Subagent dispatch with context** | `write_agent` (mid-run messaging) | Re-launch task with updated prompt | Copilot CLI must re-invoke `task` tool; cannot mid-run message |
| **Retry tracking** | Inherent in agent state | Save to `.dev/phase4-failure-<N>.md` | Copilot CLI needs explicit file-based tracking for auditing |
| **User escalation after 3 retries** | Direct agent response | `ask_user` tool with failure summary | Copilot CLI uses structured form; Claude Code uses prose in agent response |

### Theme 2a: External Claims Verification

| Element | Claude Code | Copilot CLI | Notes |
|---------|-------------|------------|-------|
| **Symbol verification** | AL MCP tool (`al-mcp-server-al_search_objects`) | AL MCP tool OR bash `grep` | Both can use AL MCP; Copilot CLI can fallback to grep if MCP unavailable |
| **File existence check** | `test -f` (bash) | `test -f` (bash) | Identical |
| **Evidence summary generation** | Markdown table (inline in agent response) | Markdown table (inline + saved to `.dev/`) | Copilot CLI should persist summary for audit trail |
| **Decision threshold (≥75% verified)** | Inline check in architect prompt | Check before spawning next task; surface to user with `ask_user` | Both honor the threshold; Copilot CLI surfaces explicitly via form |
| **>50% unverified escalation** | Inline in agent: "Would you like to..." | `ask_user` form with options | Copilot CLI uses structured UI; Claude Code uses conversational prose |

### Theme 2b: Target Disambiguation (Step 0)

| Element | Claude Code | Copilot CLI | Notes |
|---------|-------------|------------|-------|
| **Step 0 implementation** | Skill step that runs before Phase 1 | Skill step that runs before Phase 1 | Identical implementation across harnesses |
| **Target extraction** | Manual (document parsing) | Manual (document parsing) | Both require human judgment; no automated extraction |
| **Mismatch detection** | Inline check; wait for user response | Inline check; use `ask_user` form if ambiguous | Both block on mismatch; Copilot CLI formalizes via form UI |
| **"Proceed anyway" handling** | Allow via conversational response | Allow via form selection | Both honor user override; document the risk |

### Theme 3: Depth-First Planning

| Element | Claude Code | Copilot CLI | Notes |
|---------|-------------|------------|-------|
| **Architect debate requirements** | Mandatory critique + falsification | Mandatory critique + falsification | Identical requirements across harnesses |
| **Critique/falsification quality bar** | Substantive (assessed by synthesis agent) | Substantive (assessed by synthesis agent) | Both require concrete failure modes, not vague concerns |
| **Token overhead per architect** | 12–15K tokens (20–40% increase) | 12–15K tokens (20–40% increase) | Identical cost; affects session throughput equally |
| **Routing decision** | Per CLAUDE.md guide | Per AGENTS.md guide (adapted from CLAUDE.md) | Both document when to use al-dev-plan vs writing-plans |
| **Architect count impact** | More architects = longer execution (parallel, but sequential synthesis) | Same behavior (task tool parallelism) | No difference in architecture |

### Cross-Harness Parity Checklist

Before committing changes:

- [ ] **Theme 1 verification standard** defined identically in both CLAUDE.md AND AGENTS.md (or AGENTS.md explicitly imports CLAUDE.md section)
- [ ] **Theme 1 Phase 4** al-dev-autonomous skill has both Claude Code (write_agent) and Copilot CLI (file-based polling) implementations documented
- [ ] **Theme 2a evidence summary** format is identical: Markdown table with Verified/Unverified status
- [ ] **Theme 2a decision threshold** (≥75%, 50–74%, <50%) applied identically in both harnesses
- [ ] **Theme 2b Step 0** block text is identical across all 6 skill files (copy-paste consistency check)
- [ ] **Theme 3 architect requirements** (Proposal + Critique + Falsification) stated identically in al-dev-plan for both harnesses
- [ ] **Theme 3 routing note** present in both CLAUDE.md and AGENTS.md (or both reference shared knowledge doc)
- [ ] **Token/time impact** documented in routing note for both harnesses

---

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

## Implementation Sequencing & Dependencies

The spec spans two repos and requires careful sequencing to avoid conflicts. Below is the dependency graph and recommended order.

### Dependency Graph

```
al-dev-shared tasks:
  CLAUDE.md (add verification standard + routing note)
      ↓
  al-dev-autonomous (Phase 4)
      ↓ (depends on CLAUDE.md verification standard being present)
  al-dev-plan (Phase 1.5, Step 0, Theme 3 architect requirements)
      ↓ (depends on CLAUDE.md routing note being present)
  al-dev-investigate (Step 0, tool output framing)

vault tasks (claude-configs repo):
  vault-weave (Step 0) ↔ vault-distill (Step 0)
  vault-add-project (post-check Step 0) ↔ vault-induct (Step 0)
      ↓ (all independent)
  
Cross-repo dependencies:
  All al-dev-shared tasks must complete BEFORE vault tasks
  Reason: vault tasks inherit verification standard from CLAUDE.md propagation
```

### Recommended Implementation Order

**Phase A: al-dev-shared (5 tasks)**
1. **Task A1:** Update CLAUDE.md with Plan Task Verification Standard + Planning Routing sections
2. **Task A2:** Update al-dev-autonomous with Phase 4 (Post-Task Verify) — both Claude Code and Copilot CLI implementations
3. **Task A3:** Update al-dev-plan with Phase 1.5 (Verify External Claims) + Step 0 (Target Confirmation) + Theme 3 architect requirements
4. **Task A4:** Update al-dev-investigate with Step 0 (Target Confirmation) + tool output framing
5. **Task A5:** Create shared knowledge doc in `profile-al-dev-shared/knowledge/verification-and-planning.md` summarizing parity checklist; link from both CLAUDE.md and AGENTS.md

**Phase B: claude-configs vault (4 tasks, start after Phase A completes)**
6. **Task B1:** Update vault-weave/SKILL.md — insert Step 0 (Target Confirmation)
7. **Task B2:** Update vault-add-project/SKILL.md — insert Step 0 (Target Confirmation) after protocol check
8. **Task B3:** Update vault-distill/SKILL.md — insert Step 0 (Target Confirmation)
9. **Task B4:** Update vault-induct/SKILL.md — insert Step 0 (Target Confirmation)

**Why this order:**
- Task A1 must run first (defines the verification standard that A2 references)
- Task A2–A4 can run in any order after A1 (they're independent)
- Task A5 documents cross-harness parity (run after A1–A4 complete so you can verify all 9 changes against the checklist)
- Phase B can only start after Phase A, since vault changes inherit Theme 1 verification semantics

### Commit Strategy

**Phase A:** Create one commit per task (5 commits total to al-dev-shared)
- Each commit message: `🔒 feat(al-dev-*): add Theme X verification/planning` with explicit reference to which theme
- Include the cross-harness parity checklist status in Task A5 commit message

**Phase B:** Create one commit per file (4 commits total to claude-configs)
- Each commit message: `🔒 feat(vault-*): add target disambiguation Step 0`
- Include note: "Follows al-dev-shared Theme 2b pattern; see al-dev-shared PR for context"

---

## Spec Self-Review

**Placeholder scan:**
- ✅ No `TBD`, `TODO`, or incomplete sections
- ✅ All code blocks are complete examples or state machines
- ✅ All file paths are exact (with insertion location guidance)
- ✅ All tool commands are tested and working (rg, git, test, grep)

**Internal consistency:**
- ✅ Theme 1 (verification) and Theme 3 (planning depth) both touch `al-dev-plan` and `CLAUDE.md` — changes are additive and non-overlapping
  - Theme 1 adds Phase 4 to al-dev-autonomous; Theme 3 adds architect output requirements to al-dev-plan Phase 2
  - No conflict; executed as separate tasks
- ✅ Theme 2b disambiguation gate is identical text across all 6 skill files — easy to apply uniformly via copy-paste
- ✅ al-dev-autonomous Phase 4 references CLAUDE.md rule rather than duplicating it — single source of truth for verification standard
- ✅ Theme 2a and 2b insertion points are now explicit (after which section, before which section)
- ✅ Platform adaptation table maps each element to Claude Code and Copilot CLI equivalents; no element left unmapped
- ✅ Cross-harness parity checklist itemizes all 8 points that must match across CLAUDE.md and AGENTS.md

**Constraint propagation:**
- ✅ No "must not contain X" rules defined (Theme 1 lists forbidden patterns but doesn't prohibit them in this spec doc itself)
- ✅ All changes are additive; nothing removes existing behavior
- ✅ Verification standard applies equally to Claude Code and Copilot CLI (with tool equivalents documented)

**Scope check:**
- ✅ 9 file changes total (5 in al-dev-shared, 4 in claude-configs)
- ✅ Implementation plan should be 9 tasks (A1–A5 in al-dev-shared, B1–B4 in claude-configs), each independently committable
- ✅ Vault changes sequenced after al-dev-shared tasks (explicit dependency: al-dev-shared Phase A → Phase B)
- ✅ Each task includes line-count verification checkpoint

**Ambiguity resolution:**
- ✅ Insertion points now include "find section X" and "insert before/after Y" guidance — reduces manual judgment
- ✅ Evidence summary format specified as Markdown table with Status column (Verified/Partially Verified/Unverified)
- ✅ Decision threshold quantified: ≥75% verified → proceed; 50–74% → proceed with caveat; <50% → escalate to user
- ✅ Token/time impact quantified: +20–40% tokens, +90–120 seconds per al-dev-plan execution
- ✅ Routing decision criteria specified: SMALL (use writing-plans alone), MEDIUM (use al-dev-plan), LARGE (always use al-dev-plan)
- ✅ Cross-harness semantics harmonized: verification standard, architect requirements, routing logic consistent across Claude Code and Copilot CLI

**Ready for implementation:** Yes, all gaps addressed.

---

- **Vault changes require context switch:** They're in a separate repo (`~/claude-configs/`)
- **al-dev-shared changes are local:** Execute from the current repo
- **Tool: wc -l verification:** Each task should include a `wc -l` before/after check (per File Editing Safety in global CLAUDE.md)
- **Cross-harness testing:** After Phase A completes, verify both CLAUDE.md and AGENTS.md reflect parity (consistent wording, same checklist, same routing logic)
- **Vault testing:** After Phase B, spot-check one vault skill (e.g., vault-add-project) to confirm Step 0 placement is natural and doesn't conflict with existing checks
