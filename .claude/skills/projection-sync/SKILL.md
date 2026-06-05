---
name: projection-sync
description: >-
  Validates shared agent source and unidirectionally regenerates harness-native projections
  from the canonical agent source, summarizes changes, and asks before committing.
  Use after editing profile-al-dev-shared/agents/*.md files.
argument-hint: ""
workflow:
  stage: derive
  invoked-by: user
  repeatable: true
  inputs:
    - profile-al-dev-shared/agents/
  outputs:
    - profile-al-dev-shared/generated/agents/
  next: [align-harness-repos]
---

# Projection Sync Skill

## Overview

This skill validates the canonical agent source under `profile-al-dev-shared/agents/`, regenerates harness-native projections (Claude Code, Copilot CLI, Codex), summarizes the changes, and asks for approval before committing.

---

## Workflow: Four Phases

### Phase 0: Resume Check

Check `.dev/projection-sync-progress.md`:

- **If exists:** Offer `Resume` (continue from next incomplete phase) or `Restart` (begin from Phase 1). If the user does not respond, default to `Restart` (regenerate from a clean state).
- **If not exists:** Proceed to Phase 1

Progress checkpoint file location: `.dev/projection-sync-progress.md`

---

### Phase 1: Validate Shared Source

**Command:**

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

**Expected contract:**

- Exit 0: validation passed
- Exit 1: findings reported (plain text lines)
- Any other exit: runtime error

**On exit 0:**

- Record in progress file: `phase: 1, status: complete, result: pass`
- Proceed to Phase 2

**On exit 1:**

- Present findings to user
- Record in progress file: `phase: 1, status: blocked, result: findings_reported`
- Stop (do not proceed to Phase 2)

**On runtime error:**

- Present command error
- Record in progress file: `phase: 1, status: blocked, result: command_failed`
- Stop

---

### Phase 2: Regenerate Projections

This phase only runs if Phase 1 passes.

**Command:**

```bash
python3 scripts/generate-agent-projections.py
```

**Expected contract:**

- Exit 0: regeneration complete
- Exit 1 or other: runtime error

**On success:**

- Record in progress file: `phase: 2, status: complete, result: projections_regenerated`
- Proceed to Phase 3

**On failure:**

- Present generator error
- Record in progress file: `phase: 2, status: blocked, result: command_failed`
- Stop

---

### Phase 3: Summarize Changes

Determine what changed after regeneration:

**Commands:**

```bash
git diff --name-only
git diff --name-only -- profile-al-dev-shared/generated/agents
```

**Summary includes:**

- Whether any files changed at all
- Which files changed under `profile-al-dev-shared/generated/agents/`
- Whether only generated projections changed or other tracked files also differ
- Note about progress checkpoint file

**On no projection diffs:**

- Report "Regeneration produced no changes"
- Record in progress file: `phase: 3, status: complete, result: no_changes`
- Stop (do not proceed to Phase 4)

**On projection diffs:**

- Record in progress file with changed files list
- Proceed to Phase 4

Progress checkpoint example:

```yaml
phase: 3
status: complete
result: diff_summarized
changed_files:
  - profile-al-dev-shared/generated/agents/claude/example.md
```

---

### Phase 4: User Gate and Commit

**Approval gate (ask user before any git add/commit):**

```text
Projection regeneration is complete.

Changed files:
- [list from Phase 3]

Do you want me to stage and commit these changes?
```

**On user approval:**

1. Stage the changed files: `git add [files]`
2. Create one atomic commit: `git commit -m "chore: regenerate harness-native agent projections"`
3. Capture commit hash: `git rev-parse HEAD`
4. Record in progress file: `phase: 4, status: complete, result: committed, commit_hash: <hash>`

**On user decline:**

- Record in progress file: `phase: 4, status: complete, result: user_declined_commit`
- Stop (leave working tree unchanged)

---

## Error Handling

Conservative failure mode:

- Do not run `git checkout profile-al-dev-shared/`
- Do not delete `profile-al-dev-shared/generated/agents/`
- Do not clean up unrelated working-tree changes
- Always preserve the working tree as-is on failure
- Always update progress checkpoint to reflect blocked state

---

## Progress Checkpoint Format

Location: `.dev/projection-sync-progress.md`

YAML structure:

```yaml
phase: <0|1|2|3|4>
status: <pending|complete|blocked>
result: <description>
[optional fields like commit_hash or changed_files]
```

---

## Execution

This skill runs the orchestration script:

```bash
bash .claude/skills/projection-sync/run.sh
```

The script handles all four phases, manages progress checkpointing, and stops on failures.
