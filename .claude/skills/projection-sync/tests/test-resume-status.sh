#!/bin/bash
# Test suite for resolve_checkpoint_status() in run.sh
# Tests that the status-decision function enforces the recognized set
# (complete, blocked) and returns "corrupt" for unknown/missing values.
#
# How this is testable:
#   resolve_checkpoint_status() was extracted from Phase 0 of run.sh into a
#   named shell function.  This test sources run.sh with PROJECTION_SYNC_TEST=1
#   set — the script checks that variable and exits early after defining helper
#   functions (before executing any phase logic or spawning git/python).  The
#   test then calls resolve_checkpoint_status() directly with a temporary file.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUN_SH="$SCRIPT_DIR/run.sh"

# Source run.sh in test mode: only load function definitions, skip phase execution.
# run.sh checks PROJECTION_SYNC_TEST and exits before Phase 1 when it is set.
PROJECTION_SYNC_TEST=1 source "$RUN_SH" 2>/dev/null || true

# Ensure the function was loaded
if ! command -v resolve_checkpoint_status >/dev/null 2>&1; then
  echo "FAIL: resolve_checkpoint_status not found after sourcing run.sh" >&2
  exit 1
fi

PASS=0
FAIL=0

assert_eq() {
  local label="$1" expected="$2" actual="$3"
  if [ "$actual" = "$expected" ]; then
    echo "PASS: $label"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $label — expected '$expected', got '$actual'" >&2
    FAIL=$((FAIL + 1))
  fi
}

TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

# Case 1: unknown status → corrupt
printf 'phase: 2\nstatus: pending\nresult: something\n' > "$TMP"
assert_eq "unknown status (pending) → corrupt" "corrupt" "$(resolve_checkpoint_status "$TMP")"

# Case 2: missing status field → corrupt
printf 'phase: 2\nresult: something\n' > "$TMP"
assert_eq "missing status field → corrupt" "corrupt" "$(resolve_checkpoint_status "$TMP")"

# Case 3: recognized value 'complete' → complete
printf 'phase: 2\nstatus: complete\nresult: projections_regenerated\n' > "$TMP"
assert_eq "recognized status (complete) → complete" "complete" "$(resolve_checkpoint_status "$TMP")"

# Case 4: recognized value 'blocked' → blocked
printf 'phase: 1\nstatus: blocked\nresult: findings_reported\n' > "$TMP"
assert_eq "recognized status (blocked) → blocked" "blocked" "$(resolve_checkpoint_status "$TMP")"

# Case 5: empty file → corrupt
printf '' > "$TMP"
assert_eq "empty file → corrupt" "corrupt" "$(resolve_checkpoint_status "$TMP")"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
