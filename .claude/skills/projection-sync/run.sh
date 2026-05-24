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
