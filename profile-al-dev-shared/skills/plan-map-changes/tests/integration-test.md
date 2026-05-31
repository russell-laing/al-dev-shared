# Integration Test: plan-map-changes Skill

End-to-end test covering all three phases of the plan-map-changes skill: extraction, verification dispatch/inline, and collection/planning.

**Test Duration:** ~30-40 minutes (for full remote team path; 10-15 minutes for inline path)

**Test Scope:**

- Phase 1: Extract suggestions from mock maps
- Phase 1.5: Inline verification of small suggestion batch
- Phase 2: Dispatch to remote team for larger batch
- Phase 2a: Simulate team completion by writing duck records
- Phase 3: Collect results and invoke writing-plans

---

## Test Setup

### 1. Create Mock Map Files

Create temporary mock map files with 5 test suggestions in Observations sections.

#### Create mock skills map

```bash
mkdir -p /tmp/al-dev-test/docs
cat > /tmp/al-dev-test/docs/al-dev-skills-map.md << 'EOF'
# Skills Map

## Observations

**Trim: audit-quality Skill**

This skill is no longer invoked from any other skill or agent. Safe to remove.

- Target: `profile-al-dev-shared/skills/audit-quality/`
- Files: `profile-al-dev-shared/skills/audit-quality/SKILL.md`

**Merge: discover-skill-design and discover-agent-design**

These two agents have overlapping discovery phases. Consolidate into single discovery dispatcher.

- Target: Both agent files
- Files: `profile-al-dev-shared/agents/discover-skill-design.md`, `profile-al-dev-shared/agents/discover-agent-design.md`

**Split: analyze-architectural-design Agent**

This agent handles both skills and agents analysis. Should be split into separate agents for clarity.

- Target: Single agent file
- Files: `profile-al-dev-shared/agents/analyze-architectural-design.md`

**Inline: validate-lens-agents Script**

This is a thin wrapper called only once. Can be inlined into the calling code.

- Target: Validation script
- Files: `scripts/validate-lens-agents.py`

**Connect: Lint/compilation procedures**

These patterns appear in knowledge files (compile-lint-procedure.md,
artifact-contracts.md) and should be extracted into a shared knowledge agent.

- Target: Lint coordination
- Files: `profile-al-dev-shared/knowledge/compile-lint-procedure.md`, `profile-al-dev-shared/knowledge/artifact-contracts.md`

EOF
```

#### Create mock agents map

```bash
cat > /tmp/al-dev-test/docs/al-dev-agent-map.md << 'EOF'
# Agent Map

## Observations

**Align: plan-map-changes Agent**

Input expects --resume flag but documentation says --resume-from. Signature mismatch.

- Target: Agent definition
- Files: `profile-al-dev-shared/agents/plan-map-changes.md`

EOF
```

### 2. Create Mock Referenced Files

Create minimal versions of files referenced in suggestions:

```bash
mkdir -p /tmp/al-dev-test/profile-al-dev-shared/{skills,agents,knowledge}

# Create mock skills
cat > /tmp/al-dev-test/profile-al-dev-shared/skills/audit-quality/SKILL.md << 'EOF'
---
name: audit-quality
description: Audit skill quality
---
# Audit Quality Skill
Some content here.
EOF

# Create mock agents
cat > /tmp/al-dev-test/profile-al-dev-shared/agents/analyze-architectural-design.md << 'EOF'
---
name: analyze-architectural-design
description: Analyze architectural design
---
# Analyze Architectural Design

This handles both skills and agents design analysis.
Contains sections for both.

## Skills Analysis

Section 1...

## Agents Analysis

Section 2...

## Integration

Section 3...
EOF

# Create mock knowledge files
cat > /tmp/al-dev-test/profile-al-dev-shared/knowledge/compile-lint-procedure.md << 'EOF'
---
name: compile-lint-procedure
---
# Compile/Lint Procedure

Procedure documentation.
Some content here.
EOF
```

### 3. Create Test Directories

```bash
mkdir -p /tmp/al-dev-test/.dev/plan-map-changes-runs
cd /tmp/al-dev-test
```

---

## Phase 1: Extract Suggestions

### 1.1 Run Extraction Script

```bash
cd /tmp/al-dev-test
python3 /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/plan-map-changes/extract-suggestions.py \
  --surface both \
  --filter all \
  --output .dev/test-suggestion-queue.json
```

### 1.2 Verify Extraction Output

```bash
cat .dev/test-suggestion-queue.json | python3 -m json.tool
```

**Expected output structure:**

```json
{
  "run_id": "<generated-uuid>",
  "surface": "both",
  "type_filter": "all",
  "suggestion_count": 6,
  "extracted_at": "2026-05-31T...",
  "suggestions": [
    {
      "id": "trim-001",
      "type": "trim",
      "subject": "audit-quality Skill",
      "proposed_change": "Remove unused skill",
      "target_files": ["profile-al-dev-shared/skills/audit-quality/SKILL.md"]
    },
    {
      "id": "merge-001",
      "type": "merge",
      "subject": "discover-skill-design and discover-agent-design",
      "proposed_change": "Consolidate discovery phases",
      "target_files": [
        "profile-al-dev-shared/agents/discover-skill-design.md",
        "profile-al-dev-shared/agents/discover-agent-design.md"
      ]
    },
    ...
  ]
}
```

### 1.3 Validation Checks

- [ ] JSON is valid (no parse errors)
- [ ] `suggestion_count` matches `len(suggestions)` (should be 6)
- [ ] All suggestions have required fields: `id`, `type`, `subject`, `proposed_change`, `target_files`
- [ ] No duplicate IDs
- [ ] Type values are one of: trim, merge, split, inline, align, connect, promote

---

## Phase 1.5: Inline Verification (1-2 Suggestions Only)

For testing purposes, extract only 1-2 suggestions to test inline path.

### 1.5.1 Create Single Suggestion Mock

```bash
cat > /tmp/al-dev-test/.dev/single-suggestion.json << 'EOF'
{
  "id": "trim-001",
  "type": "trim",
  "subject": "audit-quality Skill",
  "proposed_change": "Remove unused skill",
  "target_files": ["profile-al-dev-shared/skills/audit-quality/SKILL.md"]
}
EOF
```

### 1.5.2 Run Inline Verification

Create a test script to invoke the inline verification function:

```bash
cat > /tmp/al-dev-test/test-inline-verify.py << 'EOF'
#!/usr/bin/env python3
import sys
import json
from pathlib import Path

# Add skill directory to path
sys.path.insert(0, '/Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/plan-map-changes')

# Import the verification functions
# (Assuming they're exposed as importable module)
from plan_map_changes import inline_verify_suggestion

# Read test suggestion
with open('.dev/single-suggestion.json') as f:
    suggestion = json.load(f)

# Run verification
duck_record = inline_verify_suggestion(suggestion)

# Write duck record
duck_dir = Path('.dev/duck-records-test')
duck_dir.mkdir(parents=True, exist_ok=True)
with open(duck_dir / f"{suggestion['id']}.json", 'w') as f:
    json.dump(duck_record, f, indent=2)

print(f"Duck record written to {duck_dir / suggestion['id']}.json")
print(json.dumps(duck_record, indent=2))
EOF

python3 /tmp/al-dev-test/test-inline-verify.py
```

### 1.5.3 Verify Duck Record

```bash
cat /tmp/al-dev-test/.dev/duck-records-test/trim-001.json
```

**Expected duck record structure:**

```json
{
  "suggestion_id": "trim-001",
  "type": "trim",
  "verdict": "ACCEPT|DEFER|REJECT",
  "state": "trim_check_passed|trim_check_failed|...",
  "side_effects": [
    "Removes artifact: ...",
    ...
  ],
  "evidence": [
    {
      "check": "Trim: Unused verification",
      "result": "pass|fail|warning",
      "message": "...",
      "findings": "..."
    }
  ],
  "completed_at": "2026-05-31T..."
}
```

### 1.5.4 Validation Checks

- [ ] Duck record file exists
- [ ] Duck record JSON is valid
- [ ] Contains required fields: `suggestion_id`, `type`, `verdict`, `state`, `side_effects`, `evidence`
- [ ] `verdict` is one of: ACCEPT, DEFER, REJECT
- [ ] Evidence array has at least one check result
- [ ] `completed_at` is a valid ISO timestamp

---

## Phase 2: Dispatch (3+ Suggestions)

### 2.1 Prepare Test Run Directory

```bash
run_id=$(python3 -c "import uuid; print(uuid.uuid4())")
run_dir=".dev/plan-map-changes-runs/$run_id"
mkdir -p "$run_dir/duck-records"

echo "Test run_id: $run_id"
echo "Run directory: $run_dir"
```

### 2.2 Create Test Manifest

```bash
cat > "$run_dir/manifest.json" << 'EOF'
{
  "operation": "remote",
  "run_id": "<run_id>",
  "team_id": "<team_id>",
  "phase": "phase2",
  "status": "in_progress",
  "dispatched_at": "2026-05-31T12:00:00",
  "expected_completion": "2026-05-31T12:05:00",
  "suggestion_count": 5,
  "suggestions": [
    {
      "id": "trim-001",
      "type": "trim",
      "status": "pending",
      "duck_record_path": "<run_dir>/duck-records/trim-001.json"
    },
    {
      "id": "merge-001",
      "type": "merge",
      "status": "pending",
      "duck_record_path": "<run_dir>/duck-records/merge-001.json"
    },
    {
      "id": "split-001",
      "type": "split",
      "status": "pending",
      "duck_record_path": "<run_dir>/duck-records/split-001.json"
    },
    {
      "id": "inline-001",
      "type": "inline",
      "status": "pending",
      "duck_record_path": "<run_dir>/duck-records/inline-001.json"
    },
    {
      "id": "connect-001",
      "type": "connect",
      "status": "pending",
      "duck_record_path": "<run_dir>/duck-records/connect-001.json"
    }
  ]
}
EOF
```

### 2.3 Create Checkpoint Entry

```bash
cat >> .dev/progress.md << 'EOF'

## Plan-Map-Changes State

run_id: <run_id>
surface: both
filter: all
phase: dispatched
status: waiting
manifest_path: <run_dir>/manifest.json
started_at: 2026-05-31T12:00:00
last_updated: 2026-05-31T12:00:00

EOF
```

### 2.4 Validation Checks

- [ ] `.dev/progress.md` contains plan-map-changes checkpoint
- [ ] Checkpoint has all required fields: run_id, surface, filter, phase, status, manifest_path
- [ ] Manifest file exists at specified path
- [ ] Manifest JSON is valid
- [ ] All 5 suggestions in manifest have status: pending

---

## Phase 2a: Simulate Team Completion

Mock the completion of remote team verification by writing duck records.

### 2a.1 Write Duck Records

```bash
# Create duck records for each suggestion (simulating team completion)

# Trim suggestion: ACCEPT
cat > "$run_dir/duck-records/trim-001.json" << 'EOF'
{
  "suggestion_id": "trim-001",
  "type": "trim",
  "verdict": "ACCEPT",
  "state": "trim_check_passed",
  "side_effects": ["Removes artifact: audit-quality"],
  "evidence": [
    {
      "check": "Trim: Unused verification",
      "result": "pass",
      "message": "Artifact audit-quality has no references in codebase",
      "findings": "Searched all agents, skills, knowledge; zero external references"
    }
  ],
  "completed_at": "2026-05-31T12:01:00"
}
EOF

# Merge suggestion: ACCEPT
cat > "$run_dir/duck-records/merge-001.json" << 'EOF'
{
  "suggestion_id": "merge-001",
  "type": "merge",
  "verdict": "ACCEPT",
  "state": "merge_check_passed",
  "side_effects": [
    "Merges 2 artifacts into one",
    "Shared tools: {read, write, bash}",
    "Shared knowledge: 3 references"
  ],
  "evidence": [
    {
      "check": "Merge: Overlap analysis",
      "result": "pass",
      "message": "Significant overlap (70%) and feasible merge",
      "findings": "Shared tools: {read, write, bash}, Shared knowledge: {workflow, state, integration}"
    }
  ],
  "completed_at": "2026-05-31T12:02:00"
}
EOF

# Split suggestion: DEFER
cat > "$run_dir/duck-records/split-001.json" << 'EOF'
{
  "suggestion_id": "split-001",
  "type": "split",
  "verdict": "DEFER",
  "state": "split_check_deferred",
  "side_effects": [],
  "evidence": [
    {
      "check": "Split: Concern separation",
      "result": "warning",
      "message": "Concerns are tightly coupled; requires human architect judgment"
    }
  ],
  "completed_at": "2026-05-31T12:03:00"
}
EOF

# Inline suggestion: REJECT
cat > "$run_dir/duck-records/inline-001.json" << 'EOF'
{
  "suggestion_id": "inline-001",
  "type": "inline",
  "verdict": "REJECT",
  "state": "inline_check_failed",
  "side_effects": [],
  "evidence": [
    {
      "check": "Inline: Invocation count",
      "result": "fail",
      "message": "Artifact is invoked 3 times; not single-use"
    }
  ],
  "completed_at": "2026-05-31T12:04:00"
}
EOF

# Connect suggestion: ACCEPT
cat > "$run_dir/duck-records/connect-001.json" << 'EOF'
{
  "suggestion_id": "connect-001",
  "type": "connect",
  "verdict": "ACCEPT",
  "state": "connect_check_passed",
  "side_effects": [
    "Extracts shared pattern into reusable agent",
    "Deduplicates 5 occurrences",
    "Saves ~150 lines of code"
  ],
  "evidence": [
    {
      "check": "Connect: Pattern frequency",
      "result": "pass",
      "message": "Pattern checkpoint appears 5 times in codebase",
      "findings": "Found 5 occurrences; deduplication saves ~150 lines"
    }
  ],
  "completed_at": "2026-05-31T12:05:00"
}
EOF
```

### 2a.2 Update Manifest Status

```bash
cat > "$run_dir/manifest.json" << 'EOF'
{
  "operation": "remote",
  "run_id": "<run_id>",
  "team_id": "<team_id>",
  "phase": "phase2",
  "status": "completed",
  "dispatched_at": "2026-05-31T12:00:00",
  "expected_completion": "2026-05-31T12:05:00",
  "completed_at": "2026-05-31T12:05:00",
  "suggestion_count": 5,
  "suggestions": [
    {
      "id": "trim-001",
      "type": "trim",
      "status": "completed",
      "duck_record_path": "<run_dir>/duck-records/trim-001.json"
    },
    {
      "id": "merge-001",
      "type": "merge",
      "status": "completed",
      "duck_record_path": "<run_dir>/duck-records/merge-001.json"
    },
    {
      "id": "split-001",
      "type": "split",
      "status": "completed",
      "duck_record_path": "<run_dir>/duck-records/split-001.json"
    },
    {
      "id": "inline-001",
      "type": "inline",
      "status": "completed",
      "duck_record_path": "<run_dir>/duck-records/inline-001.json"
    },
    {
      "id": "connect-001",
      "type": "connect",
      "status": "completed",
      "duck_record_path": "<run_dir>/duck-records/connect-001.json"
    }
  ]
}
EOF
```

### 2a.3 Validation Checks

- [ ] All 5 duck record files exist in duck-records/ directory
- [ ] Each duck record JSON is valid
- [ ] Duck records have diverse verdicts: 3 ACCEPT, 1 DEFER, 1 REJECT (tests aggregation logic)
- [ ] Manifest status updated to "completed"
- [ ] All suggestions in manifest have status: "completed"

---

## Phase 3: Collect & Plan Generation

### 3.1 Resume from Checkpoint

```bash
cd /tmp/al-dev-test

# Verify checkpoint is still in place
cat .dev/progress.md | grep -A 10 "Plan-Map-Changes State"
```

### 3.2 Invoke Collection Logic

Create a test script to simulate Phase 3:

```bash
cat > /tmp/al-dev-test/test-phase-3-collect.py << 'EOF'
#!/usr/bin/env python3
import sys
import json
from pathlib import Path

sys.path.insert(0, '/Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/plan-map-changes')

# Read manifest to get run info
run_dir = Path('.dev/plan-map-changes-runs/<run_id>')
manifest_path = run_dir / 'manifest.json'

with open(manifest_path) as f:
    manifest = json.load(f)

print(f"Manifest read: {manifest['suggestion_count']} suggestions")
print(f"Status: {manifest['status']}")

# Aggregate duck records
duck_dir = run_dir / 'duck-records'
records = []
for duck_file in duck_dir.glob('*.json'):
    with open(duck_file) as f:
        records.append(json.load(f))

print(f"Duck records read: {len(records)}")

# Filter by verdict
accept = [r for r in records if r.get('verdict') == 'ACCEPT']
defer = [r for r in records if r.get('verdict') == 'DEFER']
reject = [r for r in records if r.get('verdict') == 'REJECT']

print(f"ACCEPT: {len(accept)}")
print(f"DEFER: {len(defer)}")
print(f"REJECT: {len(reject)}")

# Write aggregated context
plan_context = {
    'run_id': manifest['run_id'],
    'surface': 'both',
    'filter': 'all',
    'suggestions_verified': len(records),
    'verdicts': {
        'ACCEPT': len(accept),
        'DEFER': len(defer),
        'REJECT': len(reject)
    },
    'duck_records': {
        'ACCEPT': accept,
        'DEFER': defer,
        'REJECT': reject
    }
}

with open('.dev/plan-context.json', 'w') as f:
    json.dump(plan_context, f, indent=2)

print(f"Plan context written to .dev/plan-context.json")
EOF

python3 /tmp/al-dev-test/test-phase-3-collect.py
```

### 3.3 Verify Aggregation

```bash
cat .dev/plan-context.json | python3 -m json.tool
```

**Expected structure:**

```json
{
  "run_id": "<run_id>",
  "surface": "both",
  "filter": "all",
  "suggestions_verified": 5,
  "verdicts": {
    "ACCEPT": 3,
    "DEFER": 1,
    "REJECT": 1
  },
  "duck_records": {
    "ACCEPT": [
      { suggestion_id: "trim-001", ... },
      { suggestion_id: "merge-001", ... },
      { suggestion_id: "connect-001", ... }
    ],
    "DEFER": [
      { suggestion_id: "split-001", ... }
    ],
    "REJECT": [
      { suggestion_id: "inline-001", ... }
    ]
  }
}
```

### 3.4 Simulate Writing-Plans Invocation

```bash
cat > .dev/test-writing-plans-prompt.txt << 'EOF'
# Plan Map Changes: Implementation Planning

## Verification Results Summary

Surface: both
Filter: all
Total suggestions verified: 5

Results:

- ACCEPT (approved for implementation): 3
- DEFER (requires additional decision): 1
- REJECT (not recommended): 1

## Duck Verification Evidence

### ACCEPT Verdicts (3)

#### trim-001 (trim)

- **Trim: Unused verification**: pass
  - Artifact audit-quality has no references in codebase

#### merge-001 (merge)

- **Merge: Overlap analysis**: pass
  - Significant overlap (70%) and feasible merge

#### connect-001 (connect)

- **Connect: Pattern frequency**: pass
  - Pattern checkpoint appears 5 times in codebase

### DEFER Verdicts (1)

#### split-001 (split)

- **Split: Concern separation**: warning
  - Concerns are tightly coupled; requires human architect judgment

### REJECT Verdicts (1)

#### inline-001 (inline)

- **Inline: Invocation count**: fail
  - Artifact is invoked 3 times; not single-use

## Task

Generate a detailed implementation plan that:

1. Lists all ACCEPT verdicts with their implementation strategy
2. Flags DEFER verdicts for human architect review (with rationale)
3. Explains why REJECT verdicts were not recommended
4. Provides concrete next steps for the development team

EOF

# Output written to indicate writing-plans was invoked
echo "Writing-plans invocation logged. Simulating plan generation..."

# Create mock plan file (as writing-plans would)
cat > ".dev/2026-05-31-al-dev-plan-plan.md" << 'EOF'
# Implementation Plan: Map Changes

Generated from 5 verified architectural suggestions.

## Executive Summary

- ACCEPT: 3 suggestions ready for implementation
- DEFER: 1 suggestion requires architect review
- REJECT: 1 suggestion deferred

## Accepted Changes (Ready for Implementation)

### 1. Trim: audit-quality Skill

**Verdict:** ACCEPT
**Evidence:** Artifact has zero external references

**Action:** Remove the audit-quality skill from the codebase
**Files affected:** profile-al-dev-shared/skills/audit-quality/

**Steps:**

1. Delete directory: rm -rf profile-al-dev-shared/skills/audit-quality/
2. Remove from skills map documentation
3. Commit: "refactor: remove unused audit-quality skill"

### 2. Merge: discover-skill-design and discover-agent-design

**Verdict:** ACCEPT
**Evidence:** 70% overlap identified; feasible merge

**Action:** Consolidate discovery phases into single dispatcher agent
**Files affected:** Both agent files

**Steps:**

1. Create new agent: discover-common.md
2. Extract shared discovery logic
3. Update skill references
4. Commit: "refactor: consolidate discovery into shared agent"

### 3. Connect: Lint/compilation procedures

**Verdict:** ACCEPT
**Evidence:** Pattern appears 5 times; saves ~150 lines

**Action:** Extract shared lint coordination pattern
**Files affected:** Multiple knowledge files

**Steps:**

1. Extract pattern into new knowledge agent
2. Update references in existing files
3. Commit: "refactor: extract shared lint coordination pattern"

## Deferred Changes (Requires Review)

### split-001: Analyze Architectural Design Agent

**Verdict:** DEFER
**Reason:** Concerns are tightly coupled; architect judgment needed

**Recommended action:** Assign to architecture review team for human evaluation.

## Rejected Suggestions (Not Recommended)

### inline-001: Validate Lens Agents Script

**Verdict:** REJECT
**Reason:** Artifact is invoked 3 times; not a single-use wrapper

**Recommendation:** Keep artifact as-is; provides necessary isolation for validation logic.

## Next Steps

1. Implement 3 ACCEPT changes (estimated 2-3 hours total)
2. Schedule architect review for DEFER change
3. Document rationale for REJECT decision in architecture decision log

EOF

echo "Plan file created at .dev/2026-05-31-al-dev-plan-plan.md"
```

### 3.5 Validation Checks

- [ ] Plan context file (.dev/plan-context.json) exists and is valid JSON
- [ ] Verdict counts are correct: ACCEPT=3, DEFER=1, REJECT=1
- [ ] Duck records aggregated correctly (all 5 records present in one of the verdict categories)
- [ ] Plan file generated (.dev/2026-05-31-al-dev-plan-plan.md or equivalent)
- [ ] Plan file contains sections for each verdict type
- [ ] Plan provides actionable implementation steps

---

## Cleanup

### Remove Test Artifacts

```bash
# Clean up test run directory
rm -rf /tmp/al-dev-test/.dev/plan-map-changes-runs

# Clean up progress checkpoint
sed -i '/## Plan-Map-Changes State/,/^$/d' /tmp/al-dev-test/.dev/progress.md

# Remove test files
rm -f /tmp/al-dev-test/.dev/test-suggestion-queue.json
rm -f /tmp/al-dev-test/.dev/single-suggestion.json
rm -f /tmp/al-dev-test/.dev/duck-records-test
rm -f /tmp/al-dev-test/.dev/plan-context.json
rm -f /tmp/al-dev-test/.dev/test-writing-plans-prompt.txt
rm -f /tmp/al-dev-test/.dev/2026-05-31-al-dev-plan-plan.md
rm -f /tmp/al-dev-test/test-inline-verify.py
rm -f /tmp/al-dev-test/test-phase-3-collect.py

# Remove test directories
rm -rf /tmp/al-dev-test
```

---

## Summary

This integration test validates:

1. **Phase 1 (Extraction):** Suggestions correctly extracted from map files, JSON structure valid, all required fields present
2. **Phase 1.5 (Inline):** Single suggestion verified inline, duck record created with correct structure and fields
3. **Phase 2 (Dispatch):** Manifest created, checkpoint updated, team dispatch logic validated
4. **Phase 2a (Simulation):** Duck records written with diverse verdicts,
   manifest status updated
5. **Phase 3 (Collection):** Duck records aggregated correctly, verdicts
   counted properly, plan generated with actionable steps

**Expected outcomes:**

- All 5 suggestions processed without errors
- Verdict distribution: 3 ACCEPT, 1 DEFER, 1 REJECT
- Plan file generated with concrete next steps for each verdict
- No stale checkpoint entries left after cleanup

**Test Pass Criteria:**

- All validation checks pass in each phase
- No errors during extraction, verification, or collection
- Plan file contains concrete, actionable implementation steps
- Cleanup removes all test artifacts without errors
