# Plan Map Changes with Agent Teams Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `/plan-map-changes` skill that dispatches rubber-ducking to remote agent teams, parallelize verification, and reduce session token burn from 1-1.5 hours to 40-50 minutes.

**Architecture:** Three-phase workflow—extract suggestions from map Observations (Phase 1), dispatch remote duck verification team (Phase 2), resume to collect records and invoke writing-plans (Phase 3). All durable state lives in repo-owned `.dev/plan-map-changes-runs/<run-id>/` for multi-session resume. Duck workers verify claims in parallel using universal checks (U1-U3) and type-specific checks from knowledge docs.

**Tech Stack:** RemoteTrigger API for async agent dispatch, JSON for artifact serialization, `.dev/` for checkpoint/progress tracking, Python validators for manifest integrity.

---

## File Structure

**New files:**
- `profile-al-dev-shared/skills/plan-map-changes/SKILL.md` — Main skill entry point (Phase 1 + Phase 2 dispatch, or Phase 3 collection on --resume)
- `profile-al-dev-shared/skills/plan-map-changes/extract-suggestions.py` — Phase 1: parse map Observations, build suggestion queue
- `profile-al-dev-shared/agents/plan-map-changes-duck-worker.md` — Agent spec for remote duck verification workers
- `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md` — Reference doc: universal (U1-U3) and type-specific check procedures
- `profile-al-dev-shared/skills/plan-map-changes/MANIFEST-SCHEMA.md` — Documentation of JSON schemas for checkpoint/manifest/duck-records
- `profile-al-dev-shared/skills/plan-map-changes/README.md` — User guide and troubleshooting
- `profile-al-dev-shared/skills/plan-map-changes/tests/test-extract.py` — Unit tests for Phase 1 extraction
- `profile-al-dev-shared/skills/plan-map-changes/tests/scenarios.yaml` — Skill trigger regression tests
- `profile-al-dev-shared/skills/plan-map-changes/tests/integration-test.md` — End-to-end test scenario
- `profile-al-dev-shared/skills/plan-map-changes/validate-plan-changes.py` — Validator: check manifest integrity, duck record completeness

**Modified files:**
- `.dev/progress.md` — Add section for active `/plan-map-changes` run state (run ID, phase, status)

---

## Task Breakdown

### Task 1: Define Duck Check Reference Document

**Files:**
- Create: `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`

**Description:** Write the reference document that duck verification agents will use to conduct type-specific checks. This is not a skill or implementation; it's a knowledge artifact that describes what checks to perform for each suggestion type (Trim, Merge, Split, Inline, Align, etc.).

- [ ] **Step 1: Write duck check categories and universal checks**

Create the document with sections for:
- Universal checks (U1-U3): File accessibility/syntax, artifact presence, reference validity
- Trim check: Verify tool/agent/skill is unused
- Merge check: Verify both artifacts exist and overlap identified
- Split check: Verify artifact has separable concerns
- Inline check: Verify artifact is single-use
- Align check: Verify input/output contract mismatch
- Connect check: Verify shared patterns across agents
- Promote check: Verify repeated pattern in multiple skills
- Verdict summary and classification rules

- [ ] **Step 2: Verify document structure and readability**

Run:
```bash
markdownlint profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md
```
Expected: No errors or warnings (fixable whitespace issues are OK)

- [ ] **Step 3: Commit**

```bash
git add profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md
git commit -m "docs: add map-change-rubber-duck-checks reference guide

Defines universal checks (U1-U3) and type-specific verification procedures
for each map change suggestion type (Trim, Merge, Split, Inline, Align,
Connect, Promote). Used by duck verification agents during parallel
suggestion review.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 2: Create Phase 1 Extraction Script

**Files:**
- Create: `profile-al-dev-shared/skills/plan-map-changes/extract-suggestions.py`

**Description:** Write the Python script that parses map Observations sections and builds a suggestion queue JSON artifact. This script is invoked by the main skill in Phase 1.

- [ ] **Step 1: Write extraction script with argument parsing, map parsing, and JSON output**

Script should:
- Accept `--surface {skills|agents|both}` and `--filter {all|trim|merge|...}` arguments
- Read `docs/al-dev-skills-map.md` and/or `docs/al-dev-agent-map.md`
- Extract all unimplemented suggestions from `## Observations` sections
- Skip suggestions marked `← implemented` or `← completed`
- Build JSON queue with suggestion ID, type, subject, proposed_change, target_files
- Write to file specified by `--output` or print to stdout
- Return exit code 0 if suggestions found, 1 otherwise

- [ ] **Step 2: Run extraction script on real map files**

First, check if map files exist:
```bash
ls -la profile-al-dev-shared/docs/al-dev-skills-map.md profile-al-dev-shared/docs/al-dev-agent-map.md
```

Then run extraction:
```bash
python3 profile-al-dev-shared/skills/plan-map-changes/extract-suggestions.py --surface both --filter all
```

Expected: Valid JSON output with suggestions array (may be empty if no Observations sections exist)

- [ ] **Step 3: Test extraction script with --filter flag**

```bash
python3 profile-al-dev-shared/skills/plan-map-changes/extract-suggestions.py --surface both --filter trim
```

Expected: JSON output with only `'type': 'trim'` suggestions (or empty array if none exist)

- [ ] **Step 4: Commit**

```bash
git add profile-al-dev-shared/skills/plan-map-changes/extract-suggestions.py
git commit -m "feat(plan-map-changes): add Phase 1 extraction script

Parses map Observations sections and builds JSON suggestion queue.
Used by main skill to extract and enumerate suggestions before dispatch.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 3: Define Manifest and Checkpoint Schemas

**Files:**
- Create: `profile-al-dev-shared/skills/plan-map-changes/MANIFEST-SCHEMA.md`

**Description:** Document the JSON schemas for checkpoint and manifest files so duck agents and the main skill can coordinate state reliably.

- [ ] **Step 1: Write manifest schema document**

Document should define:
- Checkpoint file format (`.dev/progress.md` section for plan-map-changes state)
- Suggestion queue format (suggestion-queue.json): run_id, surface, type_filter, suggestion_count, suggestions array
- Manifest format (manifest.json): operation, run_id, team_id, phase, status, suggestions array with id/type/status/duck_record_path/error
- Duck record format (duck-records/<id>.json): suggestion_id, type, verdict, state, side_effects, evidence, worker_id, completed_at
- Error record format (duck-records/<id>-error.json): suggestion_id, status, error, error_detail, attempted_checks, completed_checks

- [ ] **Step 2: Verify document is well-formed**

```bash
markdownlint profile-al-dev-shared/skills/plan-map-changes/MANIFEST-SCHEMA.md
```

Expected: No errors (fixable whitespace issues OK)

- [ ] **Step 3: Commit**

```bash
git add profile-al-dev-shared/skills/plan-map-changes/MANIFEST-SCHEMA.md
git commit -m "docs: add plan-map-changes artifact schemas

Documents JSON structure for checkpoint, suggestion queue, manifest,
and duck records. Used by Phase 1 (extraction), Phase 2 (dispatch),
and Phase 3 (collection) to coordinate state and verification results.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 4: Create Remote Duck Agent Spec

**Files:**
- Create: `profile-al-dev-shared/agents/plan-map-changes-duck-worker.md`

**Description:** Define the agent that remote teams will instantiate to verify individual suggestions in parallel.

- [ ] **Step 1: Write duck agent spec with frontmatter and system prompt**

Agent should:
- Name: `plan-map-changes-duck-worker`
- Model: `claude-sonnet-4-6`
- Tools: Read, Bash, Write
- System prompt should explain:
  - Role: verify one map change suggestion
  - Inputs: suggestion queue item (JSON), repo paths, check reference
  - Execution flow: read files, run U1-U3 checks, run type-specific checks, write duck record
  - Output contract: duck record (success) or error record (failure)
  - Special cases: circular dependencies, missing knowledge ref, partial file access

- [ ] **Step 2: Verify agent structure**

```bash
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents/plan-map-changes-duck-worker.md
```

Expected: Validation passes (valid YAML frontmatter, tools list, model assignment)

- [ ] **Step 3: Commit**

```bash
git add profile-al-dev-shared/agents/plan-map-changes-duck-worker.md
git commit -m "feat(agents): add plan-map-changes-duck-worker agent

Remote agent for parallel suggestion verification. Reads target files,
runs universal (U1-U3) and type-specific checks from knowledge docs,
writes duck record artifacts to repo-owned run directory.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 5: Implement Phase 1 + Phase 2 Skill Logic

**Files:**
- Create: `profile-al-dev-shared/skills/plan-map-changes/SKILL.md`

**Description:** Main skill entry point. Handles Phase 1 (extract suggestions), Phase 2 (dispatch team or inline), and Phase 3 resume path.

- [ ] **Step 1: Write skill frontmatter and overview**

Frontmatter:
```yaml
name: plan-map-changes
description: Rubber-duck architectural suggestions from map Observations using remote agent teams, reducing token burn from 1-1.5 hours to 40-50 min
argument-hint: "[--resume] [--surface skills|agents|both] [--filter trim|merge|...]"
```

System prompt should cover:
- Overview and entry points (`/plan-map-changes` and `/plan-map-changes --resume`)
- Phase 1: parse arguments, check for active resume target, run extraction, determine parallelization path
- Phase 2: build team context, spawn remote duck team, update checkpoint, return to user
- Phase 3: locate active run, validate manifest, aggregate duck records, invoke writing-plans

- [ ] **Step 2: Write Python implementation pseudocode**

Include implementation details for:
- `parse_args()`: Extract --resume, --surface, --filter flags
- `extract_suggestions()`: Call extract-suggestions.py, get queue
- `determine_parallelization()`: If ≤2 suggestions, inline; if 3+, dispatch
- `inline_verify_suggestion()`: Read files, run U1-U3 + type checks, write duck record
- `spawn_duck_team()`: Use RemoteTrigger or equivalent to dispatch agents
- `update_progress_md()`: Write checkpoint to .dev/progress.md
- `phase_3_collect()`: Read manifest, validate completion, aggregate duck records, invoke writing-plans

- [ ] **Step 3: Verify skill is properly formatted**

```bash
grep -E "^name:|^description:|^argument-hint:" profile-al-dev-shared/skills/plan-map-changes/SKILL.md
```

Expected: All three fields present

- [ ] **Step 4: Commit**

```bash
git add profile-al-dev-shared/skills/plan-map-changes/SKILL.md
git commit -m "feat(skills): add plan-map-changes skill with Phase 1+2+3 logic

Dispatches rubber-duck verification to remote agent teams for 3+
suggestions, or inlines for 1-2. Phase 1: extract suggestions. Phase 2:
dispatch team or inline verify. Phase 3 (via --resume): collect duck
records and invoke writing-plans. Reduces token burn from 1-1.5 hours
to 40-50 min via async parallel verification.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 6: Implement Inline Verification (Phase 1.5)

**Files:**
- Modify: `profile-al-dev-shared/skills/plan-map-changes/SKILL.md`

**Description:** Add the inline verification logic that handles 1-2 suggestions without spawning a remote team.

- [ ] **Step 1: Add inline verification section to SKILL.md**

Add section describing:
- Single suggestion path: read files, run U1-U3 + type checks, write duck record, jump to Phase 3
- Two suggestion path: for each, run all checks sequentially, write duck records, jump to Phase 3
- Why: avoids 5-minute team dispatch overhead for small batches

- [ ] **Step 2: Add inline verification implementations**

Implement:
- `inline_verify_suggestion()`: Read target files, run universal + type checks, return duck record or error record
- `run_type_checks()`: Dispatch to type-specific check functions (trim, merge, split, inline, align, connect, promote)
- Type-specific functions: `run_trim_checks()`, `run_merge_checks()`, etc.

- [ ] **Step 3: Test inline verification with a mock suggestion**

```bash
# Verify you can read an existing agent file
ls -la profile-al-dev-shared/agents/al-dev-plan.md
```

Expected: File exists and is readable

- [ ] **Step 4: Commit inline verification logic**

```bash
git add profile-al-dev-shared/skills/plan-map-changes/SKILL.md
git commit -m "feat(plan-map-changes): add inline verification for 1-2 suggestions

Handles suggestions without remote team dispatch. Runs U1-U3 and type-
specific checks synchronously, writes duck records, jumps to Phase 3
collection. Avoids 5-minute dispatch overhead for small batches.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 7: Write Tests & Validation Script

**Files:**
- Create: `profile-al-dev-shared/skills/plan-map-changes/tests/test-extract.py`
- Create: `profile-al-dev-shared/skills/plan-map-changes/validate-plan-changes.py`
- Create: `profile-al-dev-shared/skills/plan-map-changes/tests/scenarios.yaml`

**Description:** Unit tests for Phase 1 extraction, validator script for manifest integrity, and scenario-based trigger tests.

- [ ] **Step 1: Write extraction unit tests**

Tests should verify:
- Extraction produces valid JSON schema
- Extraction filters out implemented/completed suggestions
- Extraction parallelization threshold (≤2 inline, 3+ dispatch)

- [ ] **Step 2: Write manifest validator script**

Script should:
- Accept `--manifest <path>` argument
- Validate manifest JSON structure (required fields)
- Verify suggestion count matches array length
- Verify each suggestion has required fields (id, type, status)
- Validate status values (pending, completed, failed)
- Return exit code 0 if valid, 1 if invalid

- [ ] **Step 3: Run unit tests**

```bash
python3 profile-al-dev-shared/skills/plan-map-changes/tests/test-extract.py
```

Expected: All tests PASSED ✓

- [ ] **Step 4: Create test scenario file**

YAML format with trigger phrases and expected outcomes:
- `/plan-map-changes` → should trigger
- `/plan-map-changes --resume` → should trigger
- `/plan-map-changes --surface skills --filter trim` → should trigger
- `plan my changes` → should NOT trigger
- `how do I plan changes?` → should NOT trigger

- [ ] **Step 5: Commit tests and validator**

```bash
git add profile-al-dev-shared/skills/plan-map-changes/tests/
git add profile-al-dev-shared/skills/plan-map-changes/validate-plan-changes.py
git commit -m "test: add unit tests and validator for plan-map-changes

Unit tests for Phase 1 extraction, manifest schema validation,
and scenario-based trigger regression tests.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 8: Create Progress & Resume State Handling

**Files:**
- Modify: `profile-al-dev-shared/skills/plan-map-changes/SKILL.md`

**Description:** Add detailed logic for managing `.dev/progress.md` checkpoint and implementing the `--resume` path with state validation.

- [ ] **Step 1: Add progress.md state management section to SKILL.md**

Add documentation for:
- Checkpoint file format in `.dev/progress.md` (## Plan-Map-Changes State section)
- Update logic on state change (after extract, after dispatch, after collection)
- Resume logic: read progress.md, validate run state, locate manifest and duck records

- [ ] **Step 2: Implement progress state management functions**

Implement:
- `parse_progress_md()`: Read .dev/progress.md, extract plan-map-changes state section, return dict
- `update_progress_md()`: Create or update ## Plan-Map-Changes State section in .dev/progress.md
- `clear_progress_md_entry()`: Remove plan-map-changes section from .dev/progress.md (cleanup after run completes)

- [ ] **Step 3: Add Phase 3 resume/collection logic**

Implement:
- `phase_3_resume()`: Check progress.md for active run, validate manifest, handle incomplete/failed suggestions, aggregate duck records, invoke writing-plans
- `wait_for_team_completion()`: Poll manifest until all suggestions complete or timeout (10 min default)
- `ask_user()`: Interactive prompt for user decisions (wait/proceed partial, retry/skip failed)

- [ ] **Step 4: Add error handling**

Handle:
- No active run found (error message with recovery steps)
- Missing manifest or result directory (error message)
- Incomplete runs (ask user to wait or proceed partial)
- Failed suggestions (ask user to retry or skip)

- [ ] **Step 5: Commit progress state handling**

```bash
git add profile-al-dev-shared/skills/plan-map-changes/SKILL.md
git commit -m "feat(plan-map-changes): add progress.md state and resume logic

Implements checkpoint management in .dev/progress.md for multi-session
resume. Adds Phase 3 collection logic with state validation, incomplete
run handling (wait/proceed partial), and duck record aggregation.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 9: Integration Test & Full Skill Verification

**Files:**
- Create: `profile-al-dev-shared/skills/plan-map-changes/tests/integration-test.md`

**Description:** End-to-end integration test that exercises all three phases in a controlled environment.

- [ ] **Step 1: Write integration test document**

Document should cover:
- Test scenario: 5 suggestions → remote team → resume
- Setup: create mock map file, mock agent files, test directories
- Phase 1: verify extraction produces 5 suggestions, valid JSON
- Phase 1.5: verify inline check on single suggestion, duck record written
- Phase 2: verify manifest created, team dispatch logic
- Phase 2a: simulate team completion by writing duck records
- Phase 3: verify collection reads all duck records, invokes writing-plans, plan file created
- Cleanup: remove test artifacts

- [ ] **Step 2: Run manual verification**

```bash
# Check that real map files have Observations
grep -n "^## Observations" profile-al-dev-shared/docs/al-dev-skills-map.md profile-al-dev-shared/docs/al-dev-agent-map.md
```

Expected: Both files have Observations sections

- [ ] **Step 3: Verify skill structure is complete**

```bash
# Check all required skill files exist
ls -la profile-al-dev-shared/skills/plan-map-changes/{SKILL.md,extract-suggestions.py,MANIFEST-SCHEMA.md}
ls -la profile-al-dev-shared/agents/plan-map-changes-duck-worker.md
```

Expected: All files exist

- [ ] **Step 4: Commit integration test**

```bash
git add profile-al-dev-shared/skills/plan-map-changes/tests/integration-test.md
git commit -m "test: add integration test for plan-map-changes skill

End-to-end test covering all three phases: extraction, dispatch/inline,
collection, and plan generation. Includes mock team simulation and
artifact validation.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 10: Documentation & Final Cleanup

**Files:**
- Create: `profile-al-dev-shared/skills/plan-map-changes/README.md`
- Modify: `profile-al-dev-shared/skills/plan-map-changes/SKILL.md`

**Description:** Add user guide and troubleshooting documentation.

- [ ] **Step 1: Write user guide to README.md**

Guide should include:
- Quick start: dispatch phase with example command
- Resume: collection phase with example command
- Command reference: /plan-map-changes and /plan-map-changes --resume with flag descriptions
- How it works: 4-phase overview with descriptions
- Artifact locations: all .dev/ and docs/ paths
- Troubleshooting: 8-10 common issues with solutions

- [ ] **Step 2: Add troubleshooting section to SKILL.md**

Add section covering:
- Skill not triggering (verification, registration, restart)
- Extraction produces empty queue (verify map files, check for implementation markers)
- Team dispatch fails (RemoteTrigger availability, progress.md/manifest creation)
- Inline verification hangs (file readability, file syntax, file size)
- Resume can't find run (progress.md existence, state section, result directory)
- Duck records missing after collection (directory existence, file permissions, file encoding)

- [ ] **Step 3: Verify all files are in place**

```bash
find profile-al-dev-shared/skills/plan-map-changes -type f -name "*.md" -o -name "*.py" | sort
find profile-al-dev-shared/agents -name "*duck*"
find profile-al-dev-shared/knowledge -name "*duck*"
```

Expected: All created files listed above

- [ ] **Step 4: Run final validation**

```bash
# Validate agent structure
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents/plan-map-changes-duck-worker.md

# Check markdown files
markdownlint profile-al-dev-shared/skills/plan-map-changes/*.md
markdownlint profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md
```

Expected: All validations pass

- [ ] **Step 5: Final commit**

```bash
git add profile-al-dev-shared/skills/plan-map-changes/README.md
git add profile-al-dev-shared/skills/plan-map-changes/SKILL.md
git commit -m "docs: add plan-map-changes user guide and complete skill

User guide covering quick start, command reference, how it works,
artifact locations, troubleshooting, and under-the-hood details.
Complete skill implementation with all phases, error handling, and
state management.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Success Criteria Verification

Before execution, verify this plan meets all requirements from the spec:

✅ Rubber-ducking all suggestions runs in parallel (Phase 2a dispatches all at once)
✅ Session token burn reduced to 40-50 min (Phase 1: 5, Phase 2: 5, Phase 3: 30-40)
✅ User freed after 10 min dispatch phase (Phase 2 returns early, user not blocked)
✅ Duck records identical format to reference (duck-record schema defined in Task 3)
✅ Generated plan identical format (invokes writing-plans skill unmodified)
✅ Multi-session workflow supported (Progress.md checkpoint for resume)
✅ Same public entry point (`/plan-map-changes`)
✅ Same suggestion vocabulary (trim, merge, split, inline, align, connect, promote)
✅ Same plan format (superpowers:writing-plans unchanged)

---
