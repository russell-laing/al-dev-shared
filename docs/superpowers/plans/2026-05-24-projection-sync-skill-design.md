# Projection Sync Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a `/projection-sync` maintainer skill that validates shared agent source, regenerates harness-native projections, summarizes changes, and prompts for commit approval.

**Architecture:** Single skill file implementing a four-phase workflow (resume check → validate → regenerate → summarize → user gate) with progress checkpointing. Each phase runs existing repo scripts, inspects output, and conditionally proceeds. Failures are conservative: no auto-fix, no cleanup, progress state preserved.

**Tech Stack:** Bash script orchestration, Python subprocess execution, YAML progress checkpointing, git commands.

---

## File Structure

```
.claude/skills/projection-sync/
  SKILL.md                    # Main skill file (phase 0–4 implementation)
  run.sh                      # Executable orchestration script
```

**Runtime checkpoint:**
- `.dev/projection-sync-progress.md` — created/updated during execution (not under source control)

---

## Task Breakdown

### Task 1: Create Skill Frontmatter and Phase 0 (Resume Check)

**Files:**
- Create: `.claude/skills/projection-sync/SKILL.md`

- [ ] **Step 1: Write the skill file with frontmatter and Phase 0 instructions**

```markdown
---
name: projection-sync
description: >-
  Validate shared agent source, regenerate harness-native projections,
  summarize changes, and ask before committing. Use after editing
  profile-al-dev-shared/agents/*.md files.
---

# Projection Sync Skill

## Overview

This skill validates the canonical agent source under `profile-al-dev-shared/agents/`, regenerates harness-native projections (Claude Code, Copilot CLI, Codex), summarizes the changes, and asks for approval before committing.

**Narrow scope:** Orchestrates existing scripts and managed outputs. Does not auto-fix validation failures or replace broader alignment workflows like `/align-harness-repos`.

---

## Workflow: Four Phases

### Phase 0: Resume Check

Check `.dev/projection-sync-progress.md`:

- **If exists:** Offer `Resume` (continue from next incomplete phase) or `Restart` (begin from Phase 1)
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

```
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

---
```

- [ ] **Step 2: Verify the file was created**

Run: `ls -la .claude/skills/projection-sync/SKILL.md`  
Expected: File exists, 1000+ characters

---

### Task 2: Create Orchestration Script

**Files:**
- Create: `.claude/skills/projection-sync/run.sh`

- [ ] **Step 1: Write the executable orchestration script**

```bash
#!/bin/bash
set -e

# Projection Sync — Phase 0–4 orchestrator

PROGRESS_FILE=".dev/projection-sync-progress.md"
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# Phase 0: Resume Check
if [ -f "$PROGRESS_FILE" ]; then
  echo "Found existing progress checkpoint at $PROGRESS_FILE"
  echo ""
  cat "$PROGRESS_FILE"
  echo ""
  read -p "Resume (r) or Restart (s)? [r/s]: " resume_choice
  
  if [ "$resume_choice" = "s" ] || [ "$resume_choice" = "S" ]; then
    rm "$PROGRESS_FILE"
    echo "Checkpoint cleared. Starting from Phase 1..."
    current_phase=0
  else
    # Extract current phase from checkpoint
    if grep -q '^phase:' "$PROGRESS_FILE"; then
      current_phase=$(grep '^phase:' "$PROGRESS_FILE" | head -1 | awk '{print $2}')
      if [ "$current_phase" = "1" ] && grep -q 'blocked' "$PROGRESS_FILE"; then
        current_phase=1  # Stay on Phase 1 if blocked, user can retry
      else
        current_phase=$((current_phase + 1))
      fi
    else
      current_phase=1
    fi
    echo "Resuming from Phase $current_phase..."
  fi
else
  current_phase=0
  echo "No checkpoint found. Starting from Phase 1..."
fi

# Helper: write progress checkpoint
write_progress() {
  local phase=$1
  local status=$2
  local result=$3
  
  mkdir -p .dev
  cat > "$PROGRESS_FILE" << EOF
phase: $phase
status: $status
result: $result
timestamp: $(date -u '+%Y-%m-%dT%H:%M:%SZ')
EOF
}

# Phase 1: Validate (if current_phase <= 1)
if [ $current_phase -le 1 ]; then
  echo ""
  echo "=== Phase 1: Validate Shared Source ==="
  echo "Running: python3 scripts/validate_harness_neutrality.py profile-al-dev-shared"
  
  if python3 scripts/validate_harness_neutrality.py profile-al-dev-shared; then
    echo "✓ Validation passed"
    write_progress 1 complete pass
  else
    validator_exit=$?
    echo "✗ Validation failed with exit code $validator_exit"
    write_progress 1 blocked findings_reported
    echo ""
    echo "Review the findings above. Run /projection-sync again when ready to retry."
    exit 1
  fi
  current_phase=2
fi

# Phase 2: Regenerate (if current_phase <= 2)
if [ $current_phase -le 2 ]; then
  echo ""
  echo "=== Phase 2: Regenerate Projections ==="
  echo "Running: python3 scripts/generate-agent-projections.py"
  
  if python3 scripts/generate-agent-projections.py; then
    echo "✓ Projections regenerated"
    write_progress 2 complete projections_regenerated
  else
    echo "✗ Projection generator failed"
    write_progress 2 blocked command_failed
    exit 1
  fi
  current_phase=3
fi

# Phase 3: Summarize (if current_phase <= 3)
if [ $current_phase -le 3 ]; then
  echo ""
  echo "=== Phase 3: Summarize Changes ==="
  
  changed_files=$(git diff --name-only)
  projection_diffs=$(git diff --name-only -- profile-al-dev-shared/generated/agents)
  
  if [ -z "$projection_diffs" ]; then
    echo "✓ No projection changes detected"
    write_progress 3 complete no_changes
    echo ""
    echo "Regeneration produced no changes. Workflow complete."
    exit 0
  fi
  
  echo "✓ Changed projection files:"
  echo "$projection_diffs" | sed 's/^/  - /'
  
  if [ -n "$changed_files" ]; then
    # Check if changes extend beyond projections
    other_files=$(echo "$changed_files" | grep -v '^profile-al-dev-shared/generated/agents' || true)
    if [ -n "$other_files" ]; then
      echo ""
      echo "Note: Other tracked files also changed:"
      echo "$other_files" | sed 's/^/  - /'
    fi
  fi
  
  write_progress 3 complete diff_summarized
  current_phase=4
fi

# Phase 4: User Gate and Commit (if current_phase <= 4)
if [ $current_phase -le 4 ]; then
  echo ""
  echo "=== Phase 4: Approval Gate ==="
  changed_files=$(git diff --name-only)
  
  echo "Projection regeneration is complete."
  echo ""
  echo "Changed files:"
  echo "$changed_files" | sed 's/^/  - /'
  echo ""
  read -p "Stage and commit these changes? [y/n]: " commit_choice
  
  if [ "$commit_choice" = "y" ] || [ "$commit_choice" = "Y" ]; then
    echo "Staging files..."
    git add $changed_files
    
    echo "Creating commit..."
    git commit -m "chore: regenerate harness-native agent projections"
    commit_hash=$(git rev-parse HEAD)
    
    write_progress 4 complete committed
    echo "" >> "$PROGRESS_FILE"
    echo "commit_hash: $commit_hash" >> "$PROGRESS_FILE"
    
    echo "✓ Committed as $commit_hash"
  else
    write_progress 4 complete user_declined_commit
    echo ""
    echo "Changes left uncommitted. You can run /projection-sync again to commit later."
    exit 0
  fi
fi

echo ""
echo "✓ Projection sync complete"
```

- [ ] **Step 2: Make the script executable**

Run: `chmod +x .claude/skills/projection-sync/run.sh`  
Expected: No output

- [ ] **Step 3: Verify the script is executable**

Run: `test -x .claude/skills/projection-sync/run.sh && echo "executable" || echo "not executable"`  
Expected: Output is `executable`

---

### Task 3: Verify Skill Structure

**Files:**
- (Verification only)

- [ ] **Step 1: Confirm directory structure**

Run: `ls -la .claude/skills/projection-sync/`  
Expected: Lists both `SKILL.md` and `run.sh`

- [ ] **Step 2: Verify frontmatter**

Run: `head -10 .claude/skills/projection-sync/SKILL.md`  
Expected: Shows YAML frontmatter with `name: projection-sync` and `description:`

- [ ] **Step 3: Check for forbidden patterns**

Run: `grep -E 'TODO|TBD|FIXME|\[date\]|YYYY-MM-DD' .claude/skills/projection-sync/SKILL.md .claude/skills/projection-sync/run.sh || echo "No forbidden patterns found"`  
Expected: Output is "No forbidden patterns found"

- [ ] **Step 4: Verify bash syntax**

Run: `bash -n .claude/skills/projection-sync/run.sh`  
Expected: No output (script is syntactically valid)

---

### Task 4: Commit Skill Files

**Files:**
- `.claude/skills/projection-sync/SKILL.md`
- `.claude/skills/projection-sync/run.sh`

- [ ] **Step 1: Check git status**

Run: `git status --short .claude/skills/projection-sync/`  
Expected: Shows `?? .claude/skills/projection-sync/SKILL.md` and `?? .claude/skills/projection-sync/run.sh`

- [ ] **Step 2: Stage the files**

Run: `git add .claude/skills/projection-sync/SKILL.md .claude/skills/projection-sync/run.sh`  
Expected: No output

- [ ] **Step 3: Create commit**

```bash
git commit -m "chore: add projection-sync maintainer skill

- Validate shared agent source before projection regeneration
- Orchestrate harness-native projection generator
- Summarize changes and request user approval before commit
- Implement four-phase workflow with resume checkpoint support
- Conservative error handling preserves working tree on failure

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 4: Verify commit**

Run: `git log --oneline -1`  
Expected: Shows new commit with "add projection-sync maintainer skill"

- [ ] **Step 5: Verify commit count**

Run: `git log --oneline -1 | wc -l`  
Expected: Output is `1`

---

### Task 5: Final Verification

**Files:**
- (Verification only)

- [ ] **Step 1: Confirm no forbidden patterns in new files**

Run: `grep -E '\[date\]|YYYY-MM-DD|TODO|TBD' .claude/skills/projection-sync/SKILL.md .claude/skills/projection-sync/run.sh || echo "No forbidden patterns found"`  
Expected: Output is "No forbidden patterns found"

- [ ] **Step 2: Verify file sizes**

Run: `wc -l .claude/skills/projection-sync/SKILL.md .claude/skills/projection-sync/run.sh`  
Expected: SKILL.md ≥ 120 lines, run.sh ≥ 130 lines

- [ ] **Step 3: Verify clean git status**

Run: `git status --short`  
Expected: No untracked files in `.claude/skills/projection-sync/`

---

## Success Criteria

✓ Skill file created at `.claude/skills/projection-sync/SKILL.md` with complete Phase 0–4 instructions  
✓ Executable orchestration script at `.claude/skills/projection-sync/run.sh` implements all four phases  
✓ Phase 1 validates using existing `scripts/validate_harness_neutrality.py`  
✓ Phase 2 regenerates using existing `scripts/generate-agent-projections.py`  
✓ Phase 3 summarizes changes and detects when no changes occurred  
✓ Phase 4 asks for user approval before committing (USER_GATE)  
✓ Progress checkpointing allows resume/restart from Phase 0  
✓ Errors do not discard unrelated working-tree changes  
✓ No forbidden patterns in new files  
✓ Commit created with correct count  
