# Plugin Reliability & Quality Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved reliability/quality spec across `al-dev-shared` and `claude-configs` by adding closed-loop verification, external-claims validation, target disambiguation gates, and stronger adversarial planning requirements.

**Architecture:** Execute in two phases: Phase A updates shared planning/execution skills and governance docs in `al-dev-shared`; Phase B applies the same target-confirmation gate to vault skills in `claude-configs`. Each task is independently committable, with a mandatory mid-point integration review after Task 5. All changes are additive insertions/replacements in markdown skill docs only.

**Tech Stack:** Markdown (`.md`) skill docs, `rg`, `wc`, `git`, and shell checks.

---

## Scope & Repo Split

This spec spans two repos but remains one cohesive subsystem (planning/execution reliability rules propagated across shared + vault skills). Keep one plan with strict sequencing:

1. Complete **Task 1–5** in `/Users/russelllaing/al-dev-shared`.
2. Run the mid-point integration review checkpoint (included in Task 5).
3. Complete **Task 6–9** in `/Users/russelllaing/claude-configs`.

---

## File Map

| File | Repo | Responsibility |
| --- | --- | --- |
| `CLAUDE.md` | al-dev-shared | Add verification standard and planning routing guidance |
| `profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md` | al-dev-shared | Add Post-Task Verify loop and retry/escalation instructions |
| `profile-al-dev-shared/skills/al-dev-plan/SKILL.md` | al-dev-shared | Add external-claim verification, target confirmation gate, and architect critique/falsification requirements |
| `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md` | al-dev-shared | Add Step 0 target confirmation + tool-output-as-hypothesis framing |
| `profile-al-dev-shared/knowledge/verification-and-planning.md` | al-dev-shared | Shared parity checklist + platform mapping source |
| `AGENTS.md` | al-dev-shared | Copilot parity link/reference to shared verification/planning knowledge |
| `profile-claude-vault/skills/vault-weave/SKILL.md` | claude-configs | Add Step 0 target confirmation at start |
| `profile-claude-vault/skills/vault-add-project/SKILL.md` | claude-configs | Add Step 0 target confirmation after protocol check |
| `profile-claude-vault/skills/vault-distill/SKILL.md` | claude-configs | Add Step 0 target confirmation at start |
| `profile-claude-vault/skills/vault-induct/SKILL.md` | claude-configs | Add Step 0 target confirmation at start |

---

### Task 1: Add verification standard + routing guidance in CLAUDE.md

**Files:**
- Modify: `CLAUDE.md` (insert after `## Diagram Guidance` block and before `## Quality Review Conventions`)

- [ ] **Step 1: Verify baseline anchors**

```bash
wc -l CLAUDE.md
rg -n "^## (Diagram Guidance|Quality Review Conventions|Plan Task Verification Standard|Planning Routing)$" CLAUDE.md
```

Expected: `Diagram Guidance` and `Quality Review Conventions` exist; `Plan Task Verification Standard` and `Planning Routing` do not.

- [ ] **Step 2: Insert `## Plan Task Verification Standard` section**

Insert this exact section:

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

- [ ] **Step 3: Insert `## Planning Routing` section immediately after verification standard**

Insert this exact section:

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

- [ ] **Step 4: Verify insertion and line growth**

```bash
rg -n "^## (Plan Task Verification Standard|Planning Routing)$" CLAUDE.md
rg -n "Every plan task must end with a verification step before its commit|SMALL/TRIVIAL|MEDIUM|LARGE/COMPLEX" CLAUDE.md
wc -l CLAUDE.md
```

Expected: both headings present; key phrases found once; line count increased.

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
🔒 feat(claude): add plan verification standard and planning routing guidance
EOF
)"
```

---

### Task 2: Add Post-Task Verify retry loop in al-dev-autonomous

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md` (insert between `## Phase 4A: Static Validation` and `## Phase 5: Spawn Review Team`)

- [ ] **Step 1: Verify insertion anchors**

```bash
wc -l profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md
rg -n "^## (Phase 4A: Static Validation|Phase 5: Spawn Review Team|Phase 4: Post-Task Verify)$" profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md
```

Expected: Phase 4A and Phase 5 exist; `Phase 4: Post-Task Verify` does not yet exist.

- [ ] **Step 2: Insert new post-task verification phase**

Insert this exact block (use heading `## Phase 4: Post-Task Verify` as required by spec):

```markdown
## Phase 4: Post-Task Verify

After each developer subagent returns, before the commit gate:

1. **Run the verification checklist** — check forbidden patterns, file persistence, acceptance criteria
   - **Pattern scan (Claude Code):**
     ```bash
     rg '\[date\]|\bYYYY-MM-DD\b|TODO|TBD|Co-Authored-By|claude:|copilot:' <files> --color=never --no-heading --with-filename
     ```
   - **Pattern scan (Copilot CLI fallback):**
     ```bash
     git diff HEAD --unified=0 | grep -E '\[date\]|YYYY-MM-DD|TODO|TBD|Co-Authored-By|claude:|copilot:' || true
     ```
   - **File check:** `git status --short` to confirm expected files were modified
   - **Acceptance check:** Manually inspect output files for stated criteria
2. **If checklist passes** → proceed to commit
3. **If checklist fails**:
   - Claude Code: re-dispatch developer subagent using `write_agent` with:
     - original task description
     - `Failure context:` block (pattern matches, missing files, unmet criteria)
     - `Fix only the listed failures; do not re-do items that passed`
   - Copilot CLI: save `.dev/phase4-failure-<retry-count>.md`, then re-launch developer task with:
     - original task description
     - `Failure context:` block
     - `Fix scope:` statement limiting scope to failed items
     - exit criteria: checklist passes and failure log indicates PASS
4. **Retry loop:** Max 3 retries per task. After 3 failures:
   - Claude Code: escalate with task description + all 3 failure summaries + recommended next steps
   - Copilot CLI: use `ask_user` to present failure summary and wait for decision (retry manually / skip task / abort plan)
```

- [ ] **Step 3: Add cross-reference note in existing Phase 4 verification section**

Append this sentence at end of existing `## Phase 4: Verify on Completion` section:

```markdown
For per-task persistence/pattern/acceptance verification with retries, follow **Phase 4: Post-Task Verify** before entering the review gate.
```

- [ ] **Step 4: Verify resulting structure**

```bash
rg -n "^## Phase 4: Verify on Completion|^## Phase 4A: Static Validation|^## Phase 4: Post-Task Verify|^## Phase 5: Spawn Review Team" profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md
rg -n "write_agent|ask_user|phase4-failure-<retry-count>|git status --short" profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md
wc -l profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md
```

Expected: new Phase 4 Post-Task Verify is present between Phase 4A and Phase 5; Claude and Copilot variants both present.

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md
git commit -m "$(cat <<'EOF'
🔒 feat(al-dev-autonomous): add post-task verification retry loop for claude and copilot
EOF
)"
```

---

### Task 3: Add Phase 1.5 claim verification + Step 0 target check + architect critique requirements in al-dev-plan

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`

- [ ] **Step 1: Verify target anchors and baseline phrase**

```bash
wc -l profile-al-dev-shared/skills/al-dev-plan/SKILL.md
rg -n "^## (Phase 1: Gather Context|Phase 2: Spawn Architect Team \\(2-3 agents\\)|Phase 3: Facilitate Debate|Phase 1.5: Verify External Claims|Step 0: Target Confirmation \\(Phase 1.5.5\\)|Architect Output Requirements)$" profile-al-dev-shared/skills/al-dev-plan/SKILL.md
rg -n "Be prepared to debate trade-offs with other architects." profile-al-dev-shared/skills/al-dev-plan/SKILL.md
```

Expected: Phase 1 and 2 exist; new headings absent; old passive debate sentence present once.

- [ ] **Step 2: Insert `## Phase 1.5: Verify External Claims` after Phase 1 and before Phase 2**

Insert this exact section:

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
   - Use AL MCP (`al-mcp-server-al_search_objects` or `al-mcp-server-al_find_references`) to confirm the symbol exists
   - Cross-harness fallback: `grep -r "symbol_name" src/ --include="*.al"`
   - If not found → mark as **unverified**
   - If found but context differs → mark as **partially verified**
3. **Build evidence summary** as Markdown table:

   | Claim | Type | Status | Evidence |
   | --- | --- | --- | --- |
   | "File X has problem Y" | file+issue | ✅ Verified | File exists, issue confirmed at line Z |
   | "Function Q is slow" | performance | ⚠️ Unverified | Function exists but no profiling data provided |
   | "Table R has no indexes" | schema | ✅ Verified | Grep confirms table R, no index definitions found |

4. **Communicate findings to architects** under `**External findings status:**`
   - ✅ Verified — treat as design input
   - ⚠️ Unverified — treat as hypothesis to test, not requirement
   - ⚠️ Partially verified — details differ; assume claims are approximate
5. **Decision threshold:**
   - ≥75% verified → proceed
   - 50–74% verified → proceed with explicit caveat in prompt
   - <50% verified → gate with `ask_user` decision (proceed as hypotheses / re-run investigation / proceed anyway)
```

- [ ] **Step 3: Insert `## Step 0: Target Confirmation (Phase 1.5.5)` between Phase 1.5 and Phase 2**

Insert this exact block:

```markdown
## Step 0: Target Confirmation (Phase 1.5.5)

Before acting on any findings file or context document:

1. **Identify targets:**
   - Findings reference: Extract the target name/path from the document
   - Your request: Extract target from user message (skill, repo, file, or project)
   - Output path: Absolute path where work will land
2. **Validate match:**
   ```
   > **Target check:**
   > - Findings reference: [extracted from findings]
   > - Your request: [extracted from your message]
   > - Output path: [absolute path where work will land]
   >
   > Do these match? If findings and request disagree, stop and confirm before proceeding.
   ```
3. **Decision:**
   - If all align → continue
   - If findings/request disagree → flag mismatch and wait
   - If mismatch is fundamental → stop and escalate to user
```

- [ ] **Step 4: Replace passive architect debate line with mandatory output requirements**

Replace:

```text
Be prepared to debate trade-offs with other architects.
```

With:

```markdown
## Architect Output Requirements

Each architect must produce THREE outputs (not one):

1. **Proposal** — complete solution design (recommended approach)
2. **Critique** — specific critique of ONE other approach from briefing
   - Must name concrete failure modes
   - Must identify observable condition or code-level breakage
3. **Falsification** — one realistic condition where YOUR approach fails
   - State design limits honestly

Architects without all three outputs are excluded from Phase 3 synthesis.
Quality bar: critiques/falsifications must be substantive enough to force re-evaluation of a design.
```

- [ ] **Step 5: Verify all additions**

```bash
rg -n "^## (Phase 1.5: Verify External Claims|Step 0: Target Confirmation \\(Phase 1.5.5\\)|Architect Output Requirements)$" profile-al-dev-shared/skills/al-dev-plan/SKILL.md
rg -n "≥75% verified|50–74% verified|<50% verified|External findings status|THREE outputs" profile-al-dev-shared/skills/al-dev-plan/SKILL.md
rg -n "Be prepared to debate trade-offs with other architects." profile-al-dev-shared/skills/al-dev-plan/SKILL.md || echo "PASS: passive line removed"
wc -l profile-al-dev-shared/skills/al-dev-plan/SKILL.md
```

Expected: new sections present; old passive line absent.

- [ ] **Step 6: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-plan/SKILL.md
git commit -m "$(cat <<'EOF'
🔒 feat(al-dev-plan): add external-claim verification, target confirmation, and mandatory architect critique outputs
EOF
)"
```

---

### Task 4: Add Step 0 target confirmation + tool-output framing to al-dev-investigate

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md`

- [ ] **Step 1: Verify baseline step headings**

```bash
wc -l profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
rg -n "^### Step (0|1|2) —" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
```

Expected: Step 1 exists, Step 0 does not.

- [ ] **Step 2: Insert new Step 0 section immediately before existing Step 1**

Insert:

```markdown
### Step 0 — Target Confirmation

Before acting on any findings file or context document:

1. **Identify targets:**
   - Findings reference: target name/path from findings
   - Your request: target from user request
   - Output path: where investigation output will be written
2. **Validate match:**
   ```
   > **Target check:**
   > - Findings reference: [extracted from findings]
   > - Your request: [extracted from your message]
   > - Output path: [absolute path where work will land]
   >
   > Do these match? If findings and request disagree, stop and confirm before proceeding.
   ```
3. **Decision:**
   - If aligned → continue
   - If mismatched → stop and wait for user confirmation
```

- [ ] **Step 3: Add tool-output framing note directly after Step 1 section**

Insert:

```markdown
**Tool output framing:** If ticket context or findings include output from external tools
(codeburn, lint analyzers, third-party plugins):

- Treat each tool-output claim as a **hypothesis**, not an established finding
- Add each claim to the hypothesis list to test during investigation steps
- Confirm claim vs actual codebase before including it in final findings report
- If tool output contradicts code, flag contradiction and resolve which source is current
```

- [ ] **Step 4: Verify insertion points and ordering**

```bash
rg -n "^### Step (0|1|2) —" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
rg -n "Tool output framing|hypothesis, not an established finding" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
wc -l profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
```

Expected: Step order is 0 → 1 → 2; framing note appears after Step 1.

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
git commit -m "$(cat <<'EOF'
🔒 feat(al-dev-investigate): add target confirmation gate and external-tool hypothesis framing
EOF
)"
```

---

### Task 5: Add shared knowledge doc + AGENTS parity link + integration review checkpoint

**Files:**
- Create: `profile-al-dev-shared/knowledge/verification-and-planning.md`
- Modify: `AGENTS.md`
- Modify: `CLAUDE.md` (single-line reference to shared knowledge doc)

- [ ] **Step 1: Create shared knowledge doc with parity checklist**

Create `profile-al-dev-shared/knowledge/verification-and-planning.md` with:

```markdown
# Verification and Planning Parity Guide

This guide is the shared reference for cross-harness parity between Claude Code and Copilot CLI for:

1. Plan task verification
2. External claims verification
3. Target confirmation
4. Depth-first planning (proposal + critique + falsification)

## Cross-Harness Parity Checklist

- [ ] Theme 1 verification standard is aligned in CLAUDE.md and AGENTS.md
- [ ] al-dev-autonomous includes explicit post-task verify retry handling
- [ ] al-dev-plan includes evidence-summary verification and threshold gating
- [ ] al-dev-plan includes mandatory architect proposal/critique/falsification outputs
- [ ] Step 0 target confirmation wording is consistent across impacted skills
- [ ] Token/time impact guidance is documented in routing guidance

## Tool Mapping

| Need | Claude Code | Copilot CLI |
| --- | --- | --- |
| user decision gate | conversational prompt / ask tool | `ask_user` |
| subagent retry | `write_agent` | re-dispatch with updated prompt |
| pattern scan | `rg` | `rg` or `git diff | grep` |

## Usage

- Reference this file when updating skill behavior across harnesses.
- Prefer additive edits and avoid diverging behavior wording between CLAUDE.md and AGENTS.md.
```

- [ ] **Step 2: Link shared guide from CLAUDE.md**

Under planning-related guidance, add:

```markdown
Shared parity reference: `profile-al-dev-shared/knowledge/verification-and-planning.md`.
```

- [ ] **Step 3: Link shared guide from AGENTS.md**

Under planning/review guidance, add:

```markdown
Shared parity reference: `profile-al-dev-shared/knowledge/verification-and-planning.md`.
Use it to keep Claude Code and Copilot CLI verification/planning behavior aligned.
```

- [ ] **Step 4: Mid-point integration review (required checkpoint)**

Run and inspect:

```bash
rg -n "^## (Plan Task Verification Standard|Planning Routing)$" CLAUDE.md
rg -n "verification-and-planning.md" CLAUDE.md AGENTS.md
rg -n "^## (Phase 4: Post-Task Verify|Phase 1.5: Verify External Claims|Step 0: Target Confirmation \\(Phase 1.5.5\\)|Architect Output Requirements)$" profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md profile-al-dev-shared/skills/al-dev-plan/SKILL.md
rg -n "^### Step 0 — Target Confirmation|Tool output framing" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
```

Expected: all Theme 1/2a/2b/3 anchors are present before moving to vault tasks.

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/knowledge/verification-and-planning.md AGENTS.md CLAUDE.md
git commit -m "$(cat <<'EOF'
🔒 feat(docs): add shared verification-planning parity guide and cross-harness references
EOF
)"
```

---

### Task 6: Add Step 0 target confirmation to vault-weave

**Files:**
- Modify: `/Users/russelllaing/claude-configs/profile-claude-vault/skills/vault-weave/SKILL.md`

- [ ] **Step 1: Verify insertion anchor**

```bash
git -C /Users/russelllaing/claude-configs --no-pager grep -n "^## Prerequisites\|^## Step 0: Target Confirmation" -- profile-claude-vault/skills/vault-weave/SKILL.md
```

Expected: `## Prerequisites` exists; `## Step 0: Target Confirmation` absent.

- [ ] **Step 2: Insert Step 0 block before current prerequisites**

Insert this exact block near top of skill body:

```markdown
## Step 0: Target Confirmation

Before acting on any findings file or context document:

1. **Identify targets:**
   - Findings reference: Extract target name/path from document
   - Your request: Extract target from user message
   - Output path: Absolute path where work will land
2. **Validate match:**
   ```
   > **Target check:**
   > - Findings reference: [extracted from findings]
   > - Your request: [extracted from your message]
   > - Output path: [absolute path where work will land]
   >
   > Do these match? If findings and request disagree, stop and confirm before proceeding.
   ```
3. **Decision:**
   - If aligned → continue
   - If mismatched → flag and wait for user confirmation
   - If mismatch is fundamental → stop and escalate
```

- [ ] **Step 3: Verify**

```bash
git -C /Users/russelllaing/claude-configs --no-pager grep -n "^## Step 0: Target Confirmation" -- profile-claude-vault/skills/vault-weave/SKILL.md
wc -l /Users/russelllaing/claude-configs/profile-claude-vault/skills/vault-weave/SKILL.md
```

Expected: Step 0 present once; line count increased.

- [ ] **Step 4: Commit in claude-configs**

```bash
git -C /Users/russelllaing/claude-configs add profile-claude-vault/skills/vault-weave/SKILL.md
git -C /Users/russelllaing/claude-configs commit -m "$(cat <<'EOF'
🔒 feat(vault-weave): add Step 0 target confirmation gate
EOF
)"
```

---

### Task 7: Add Step 0 target confirmation to vault-add-project

**Files:**
- Modify: `/Users/russelllaing/claude-configs/profile-claude-vault/skills/vault-add-project/SKILL.md`

- [ ] **Step 1: Verify insertion anchor after protocol check**

```bash
git -C /Users/russelllaing/claude-configs --no-pager grep -n "^## Prerequisites\|^Read `client-protocol.md`\|^## Step 1: Gather Inputs\|^## Step 0: Target Confirmation (Project Validation)$" -- profile-claude-vault/skills/vault-add-project/SKILL.md
```

Expected: prerequisite protocol check exists; Step 0 (Project Validation) absent.

- [ ] **Step 2: Insert project-validation variant of Step 0 after prerequisites and before Step 1**

Insert:

```markdown
## Step 0: Target Confirmation (Project Validation)

Before acting on any findings file or context document:

1. **Identify targets:**
   - Findings reference: project/skill/repo target named in findings
   - Your request: project target from user message
   - Output path: vault project path to be modified
2. **Validate match:**
   ```
   > **Target check:**
   > - Findings reference: [extracted from findings]
   > - Your request: [extracted from your message]
   > - Output path: [absolute path where work will land]
   >
   > Do these match? If findings and request disagree, stop and confirm before proceeding.
   ```
3. **Decision:**
   - If aligned → continue
   - If mismatched → flag and wait
   - If mismatch is fundamental (wrong project/skill) → stop and escalate
```

- [ ] **Step 3: Verify**

```bash
git -C /Users/russelllaing/claude-configs --no-pager grep -n "^## Step 0: Target Confirmation (Project Validation)$" -- profile-claude-vault/skills/vault-add-project/SKILL.md
wc -l /Users/russelllaing/claude-configs/profile-claude-vault/skills/vault-add-project/SKILL.md
```

Expected: Step 0 heading present once and positioned before Step 1.

- [ ] **Step 4: Commit in claude-configs**

```bash
git -C /Users/russelllaing/claude-configs add profile-claude-vault/skills/vault-add-project/SKILL.md
git -C /Users/russelllaing/claude-configs commit -m "$(cat <<'EOF'
🔒 feat(vault-add-project): add project target confirmation gate
EOF
)"
```

---

### Task 8: Add Step 0 target confirmation to vault-distill

**Files:**
- Modify: `/Users/russelllaing/claude-configs/profile-claude-vault/skills/vault-distill/SKILL.md`

- [ ] **Step 1: Verify insertion anchor**

```bash
git -C /Users/russelllaing/claude-configs --no-pager grep -n "^## Prerequisites\|^## Step 0: Target Confirmation" -- profile-claude-vault/skills/vault-distill/SKILL.md
```

Expected: prerequisites exists; Step 0 absent.

- [ ] **Step 2: Insert Step 0 block at beginning before prerequisites**

Insert the same unified block text used in Task 6 (without project-validation subtitle):

```markdown
## Step 0: Target Confirmation

Before acting on any findings file or context document:

1. **Identify targets:**
   - Findings reference: Extract target name/path from document
   - Your request: Extract target from user message
   - Output path: Absolute path where work will land
2. **Validate match:**
   ```
   > **Target check:**
   > - Findings reference: [extracted from findings]
   > - Your request: [extracted from your message]
   > - Output path: [absolute path where work will land]
   >
   > Do these match? If findings and request disagree, stop and confirm before proceeding.
   ```
3. **Decision:**
   - If aligned → continue
   - If mismatched → flag and wait
   - If mismatch is fundamental → stop and escalate
```

- [ ] **Step 3: Verify**

```bash
git -C /Users/russelllaing/claude-configs --no-pager grep -n "^## Step 0: Target Confirmation$" -- profile-claude-vault/skills/vault-distill/SKILL.md
wc -l /Users/russelllaing/claude-configs/profile-claude-vault/skills/vault-distill/SKILL.md
```

Expected: Step 0 exists once; line count increased.

- [ ] **Step 4: Commit in claude-configs**

```bash
git -C /Users/russelllaing/claude-configs add profile-claude-vault/skills/vault-distill/SKILL.md
git -C /Users/russelllaing/claude-configs commit -m "$(cat <<'EOF'
🔒 feat(vault-distill): add Step 0 target confirmation gate
EOF
)"
```

---

### Task 9: Add Step 0 target confirmation to vault-induct

**Files:**
- Modify: `/Users/russelllaing/claude-configs/profile-claude-vault/skills/vault-induct/SKILL.md`

- [ ] **Step 1: Verify insertion anchor**

```bash
git -C /Users/russelllaing/claude-configs --no-pager grep -n "^## Prerequisites\|^## Step 0: Target Confirmation" -- profile-claude-vault/skills/vault-induct/SKILL.md
```

Expected: prerequisites exists; Step 0 absent.

- [ ] **Step 2: Insert Step 0 block before prerequisites**

Insert the same unified Step 0 block used in Task 6/8.

- [ ] **Step 3: Verify**

```bash
git -C /Users/russelllaing/claude-configs --no-pager grep -n "^## Step 0: Target Confirmation$" -- profile-claude-vault/skills/vault-induct/SKILL.md
wc -l /Users/russelllaing/claude-configs/profile-claude-vault/skills/vault-induct/SKILL.md
```

Expected: Step 0 exists once; line count increased.

- [ ] **Step 4: Commit in claude-configs**

```bash
git -C /Users/russelllaing/claude-configs add profile-claude-vault/skills/vault-induct/SKILL.md
git -C /Users/russelllaing/claude-configs commit -m "$(cat <<'EOF'
🔒 feat(vault-induct): add Step 0 target confirmation gate
EOF
)"
```

---

## Final Verification & Completion

- [ ] **Step 1: Cross-harness parity verification (al-dev-shared + claude-configs)**

```bash
rg -n "^## (Plan Task Verification Standard|Planning Routing)$" /Users/russelllaing/al-dev-shared/CLAUDE.md
rg -n "verification-and-planning.md" /Users/russelllaing/al-dev-shared/CLAUDE.md /Users/russelllaing/al-dev-shared/AGENTS.md
rg -n "^## (Phase 1.5: Verify External Claims|Step 0: Target Confirmation \\(Phase 1.5.5\\)|Architect Output Requirements)$" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-plan/SKILL.md
rg -n "^## Phase 4: Post-Task Verify$" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md
rg -n "^## Step 0: Target Confirmation" /Users/russelllaing/claude-configs/profile-claude-vault/skills/vault-{weave,add-project,distill,induct}/SKILL.md
```

Expected: all required headings present.

- [ ] **Step 2: Repo status checks**

```bash
git --no-pager -C /Users/russelllaing/al-dev-shared status --short
git --no-pager -C /Users/russelllaing/claude-configs status --short
```

Expected: clean working tree after all nine commits.

---

## Self-Review

### 1. Spec coverage check

- Theme 1 covered by Tasks 1–2 (+ parity linking in Task 5)
- Theme 2a covered by Task 3 and Task 4
- Theme 2b covered by Task 3/4/6/7/8/9
- Theme 3 covered by Task 1 (routing) + Task 3 (architect output requirements)
- Cross-harness parity checklist captured in Task 5 + Final Verification

### 2. Placeholder scan

No `TBD`, `TODO`, or “similar to previous task” placeholders in execution steps.
Each code-change step includes concrete markdown content and concrete commands.

### 3. Type/term consistency

- Uses consistent naming: **Plan Task Verification Standard**, **Planning Routing**, **Phase 1.5: Verify External Claims**, **Step 0: Target Confirmation**, **Architect Output Requirements**, **Phase 4: Post-Task Verify**.
- Uses unified Step 0 target-check block across all six skill files, with only the `vault-add-project` subtitle variation required by spec.

