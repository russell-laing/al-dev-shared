# Agent Model Changes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update three agent model assignments and fix one outputs documentation mismatch based on model-fit analysis.

**Architecture:** Model changes are single-field updates to agent frontmatter; outputs fix is a table row deletion. All changes are localized to agent definition files. No downstream skill changes required.

**Tech Stack:** Markdown files in `profile-al-dev-shared/agents/`

---

## Task 1: Remodel al-dev-interview to sonnet (HIGHEST PRIORITY)

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-interview.md:6`

**Reasoning:** Agent conducts 40+ adaptive questions, handles requirement conflicts, synthesizes specs with REQ/ACC tokens and risk assessments. Haiku cannot sustain this level of reasoning across multiple turns.

- [ ] **Step 1: Open the agent file**

```bash
cat profile-al-dev-shared/agents/al-dev-interview.md | head -10
```

Expected output shows current model: `model: haiku`

- [ ] **Step 2: Update model field to sonnet**

```markdown
---
description: >-
  Interview the user to extract complete BC/AL implementation
  details through structured questioning. Spawned by the
  al-dev-interview skill.
model: sonnet
tools: ["Read", "Write", "USER_GATE"]
---
```

Change line 6 from `model: haiku` to `model: sonnet`

- [ ] **Step 3: Verify the change**

```bash
head -10 profile-al-dev-shared/agents/al-dev-interview.md | grep "^model:"
```

Expected: `model: sonnet`

- [ ] **Step 4: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-interview.md
git commit -m "Remodel al-dev-interview: haiku → sonnet for sustained adaptive reasoning

Agent conducts 40+ structured questions with adaptive follow-up,
handles requirement conflicts, and synthesizes complete specs with
REQ/ACC tokens and risk assessments. Haiku cannot sustain this level
of multi-turn reasoning. Sonnet justified due to high downstream impact
(missed requirements cause 3× rework in /al-dev-plan).

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Remodel al-dev-commit-recover-verifier to sonnet

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md:7`

**Reasoning:** Agent selects recovery strategies per file (git restore vs regex reconstruction vs schema rebuild), documents findings, synthesizes recovery report. Requires multi-step judgment, not mechanical execution.

- [ ] **Step 1: Open the agent file**

```bash
head -10 profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md | grep "^model:"
```

Expected output: `model: haiku`

- [ ] **Step 2: Update model field to sonnet**

```markdown
---
name: al-dev-commit-recover-verifier
description: >-
  Recover corrupted AL files using fallback strategies (git restore, regex reconstruction,
  schema rebuild). Dispatched by /commit-recover Step 2 with one verifier spawned per
  corruption incident found in .dev/commit-integrity.log.
model: sonnet
tools: ["Bash", "Read", "Write"]
---
```

Change line 7 from `model: haiku` to `model: sonnet`

- [ ] **Step 3: Verify the change**

```bash
head -10 profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md | grep "^model:"
```

Expected: `model: sonnet`

- [ ] **Step 4: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md
git commit -m "Remodel al-dev-commit-recover-verifier: haiku → sonnet for recovery judgment

Agent selects recovery strategies per file (three fallbacks: git restore,
regex reconstruction, schema rebuild), makes judgment calls about which
fallback to apply, and synthesizes recovery report. Task requires sustained
judgment and evidence documentation beyond mechanical execution.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Remodel al-dev-code-review to haiku

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-code-review.md:7`

**Reasoning:** Agent performs single-file pattern matching (logic errors, security issues), categorizes by severity. No multi-file synthesis or architecture review. Task is read + categorize, within haiku's capability range.

- [ ] **Step 1: Open the agent file**

```bash
head -10 profile-al-dev-shared/agents/al-dev-code-review.md | grep "^model:"
```

Expected output: `model: sonnet`

- [ ] **Step 2: Update model field to haiku**

```markdown
---
description: >-
  General code review specialist — finds bugs, logic errors, and security
  issues with high signal-to-noise ratio. Available for standalone use;
  not integrated into /al-dev-develop (which uses specialist reviewers
  for security, patterns, and performance).
model: haiku
tools: ["Read"]
---
```

Change line 7 from `model: sonnet` to `model: haiku`

- [ ] **Step 3: Verify the change**

```bash
head -10 profile-al-dev-shared/agents/al-dev-code-review.md | grep "^model:"
```

Expected: `model: haiku`

- [ ] **Step 4: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-code-review.md
git commit -m "Remodel al-dev-code-review: sonnet → haiku for pattern classification

Agent performs single-file code review via pattern matching (logic errors,
security issues, categorization by severity). No multi-file synthesis or
architectural reasoning required. Task scope (read + categorize) is within
haiku's capability range. Reduces cost without sacrificing signal quality.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Fix al-dev-commit-agent-execute outputs documentation

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md:22-29`

**Reasoning:** Agent's Outputs table documents STRIPPED_ATTRIBUTIONS but (1) agent body doesn't describe implementation, (2) caller skill doesn't request it, (3) summary step doesn't display it. Mismatch indicates undocumented/unused behavior. Remove from Outputs table.

- [ ] **Step 1: Examine the current Outputs table**

```bash
sed -n '22,29p' profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
```

Expected output shows:
```
## Outputs

| Output | Description |
|--------|-------------|
| `COMMITS` block | SHA and message for each committed group |
| `SKIPPED` | Number of skipped groups |
| `HOOK_FAILURES` | Raw hook output for any failed groups (or `NONE`) |
| `STRIPPED_ATTRIBUTIONS` | Removed AI attribution lines (or `NONE`) |
```

- [ ] **Step 2: Remove STRIPPED_ATTRIBUTIONS row**

Replace the Outputs table to remove line 29 (the STRIPPED_ATTRIBUTIONS row):

```markdown
## Outputs

| Output | Description |
|--------|-------------|
| `COMMITS` block | SHA and message for each committed group |
| `SKIPPED` | Number of skipped groups |
| `HOOK_FAILURES` | Raw hook output for any failed groups (or `NONE`) |
```

- [ ] **Step 3: Verify the change**

```bash
sed -n '22,28p' profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
```

Expected: Table has 4 rows (header + 3 data rows), no STRIPPED_ATTRIBUTIONS

- [ ] **Step 4: Verify consistency with caller**

The agent's Return Block (lines 55–67) also mentions STRIPPED_ATTRIBUTIONS. Check if the caller skill (/al-dev-commit) expects this output.

```bash
grep -n "STRIPPED_ATTRIBUTIONS" profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```

Expected: No results (caller doesn't reference STRIPPED_ATTRIBUTIONS)

If no results, proceed to commit. If results found, escalate to controller.

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
git commit -m "Align al-dev-commit-agent-execute outputs: remove undocumented STRIPPED_ATTRIBUTIONS

Outputs table documented STRIPPED_ATTRIBUTIONS but agent body provides
no implementation details on how/when stripping occurs. Caller skill
(/al-dev-commit) does not request or consume this output. Removed
documented output to match actual implementation scope (COMMITS, SKIPPED,
HOOK_FAILURES only).

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Self-Review Checklist

**Spec Coverage:**
- ✅ Task 1: al-dev-interview haiku → sonnet
- ✅ Task 2: al-dev-commit-recover-verifier haiku → sonnet
- ✅ Task 3: al-dev-code-review sonnet → haiku
- ✅ Task 4: al-dev-commit-agent-execute outputs alignment

**Placeholders:** None detected. Every step has exact file paths, line numbers, and complete code blocks.

**Type Consistency:** All four tasks are independent file modifications; no cross-task type dependencies.
