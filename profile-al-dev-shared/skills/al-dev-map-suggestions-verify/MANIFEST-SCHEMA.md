# Plan-Map-Changes Artifact Schemas

This document defines the JSON and markdown schemas for checkpoint, queue, manifest, and duck record artifacts used by the al-dev-map-suggestions-verify skill and its remote verification team.

---

## Checkpoint File Format

**Location:** `.dev/progress.md`

**Section name:** `## Plan-Map-Changes State`

The checkpoint is a YAML-like section in `.dev/progress.md` that tracks the active run state. It allows multi-session resume if the user exits mid-operation.

### Checkpoint Fields

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `run_id` | string | yes | Unique identifier for this run | UUID v4 format, e.g., `f47ac10b-58cc-4372-a567-0e02b2c3d479` |
| `surface` | string | yes | Which maps were analyzed | Enum: `skills`, `agents`, `both` |
| `filter` | string | yes | Suggestion type filter applied | Enum: `all`, `trim`, `merge`, `split`, `inline`, `align`, `connect`, `promote` |
| `phase` | string | yes | Current phase of execution | Enum: `extracting`, `dispatched`, `collecting`, `completed` |
| `status` | string | yes | Status within phase | Enum: `in_progress`, `waiting`, `completed`, `failed` |
| `started_at` | string | no | ISO 8601 timestamp when run started | e.g., `2026-05-31T14:22:35Z` |
| `suggestion_count` | integer | no | Number of suggestions extracted | ≥ 0 |
| `manifest_path` | string | no | Relative path to manifest.json | e.g., `.dev/al-dev-map-suggestions-verify-runs/f47ac10b-58cc-4372-a567-0e02b2c3d479/manifest.json` |

### Checkpoint Update Protocol

- **Phase 1 (extracting):** Write checkpoint after extraction completes with `phase=extracting`, `status=in_progress` or `completed`
- **Phase 2 (dispatched):** Update checkpoint to `phase=dispatched`, `status=waiting` after team is spawned
- **Phase 3 (collecting):** Update checkpoint to `phase=collecting`, `status=in_progress`, then to `completed` when done
- **On Resume:** Read this section to resume from last known state

### Checkpoint Example

```text
## Plan-Map-Changes State

run_id: f47ac10b-58cc-4372-a567-0e02b2c3d479
surface: both
filter: all
phase: dispatched
status: waiting
started_at: 2026-05-31T14:22:35Z
suggestion_count: 5
manifest_path: .dev/al-dev-map-suggestions-verify-runs/f47ac10b-58cc-4372-a567-0e02b2c3d479/manifest.json
```text

### How Main Skill Reads/Updates

1. **On startup:** Read `.dev/progress.md` and search for `## Plan-Map-Changes State` section
2. **On state change:** Find the section, replace all key-value pairs in-place, preserve adjacent text
3. **On cleanup:** Remove the entire section after run completes (status=completed)
4. **On resume:** Parse the section and extract all fields into a checkpoint dict; validate manifest_path exists before proceeding

---

## Suggestion Queue Format

**Location:** `.dev/al-dev-map-suggestions-verify-runs/<run_id>/suggestion-queue.json`

The suggestion queue is the output of Phase 1 extraction. It contains all unimplemented suggestions extracted from map Observations sections.

### Suggestion Queue Schema

**Root object fields:**

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `run_id` | string | yes | Matches checkpoint run_id | UUID v4 format |
| `surface` | string | yes | Which maps were analyzed | Enum: `skills`, `agents`, `both` |
| `type_filter` | string | yes | Filter applied during extraction | Enum: `all`, `trim`, `merge`, `split`, `inline`, `align`, `connect`, `promote` |
| `suggestion_count` | integer | yes | Length of suggestions array | ≥ 0 |
| `extracted_at` | string | yes | ISO 8601 timestamp | e.g., `2026-05-31T14:22:35Z` |
| `suggestions` | array | yes | Array of suggestion objects | See Suggestion Object schema below |

**Suggestion object fields (within suggestions array):**

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `id` | string | yes | Unique suggestion identifier | e.g., `s-001`, `s-002` |
| `type` | string | yes | Classification of suggestion | Enum: `trim`, `merge`, `split`, `inline`, `align`, `connect`, `promote` |
| `subject` | string | yes | Name of artifact being suggested | e.g., `al-dev-plan` (agent), `obsidian` (skill) |
| `proposed_change` | string | yes | Human-readable description of the change | e.g., `Remove unused --output flag from agent arguments` |
| `target_files` | array | yes | Absolute paths affected by this suggestion | e.g., `["profile-al-dev-shared/agents/al-dev-plan.md"]` |
| `file_count` | integer | yes | Length of target_files array | ≥ 1 |

### Suggestion Queue Example

```json
{
  "run_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "surface": "both",
  "type_filter": "all",
  "suggestion_count": 3,
  "extracted_at": "2026-05-31T14:22:35Z",
  "suggestions": [
    {
      "id": "s-001",
      "type": "trim",
      "subject": "al-dev-plan",
      "proposed_change": "Remove --output flag; plan always writes to .dev/YYYY-MM-DD-al-dev-plan-solution-plan.md",
      "target_files": ["profile-al-dev-shared/agents/al-dev-plan.md"],
      "file_count": 1
    },
    {
      "id": "s-002",
      "type": "merge",
      "subject": "al-dev-develop + al-dev-review-develop",
      "proposed_change": "Merge al-dev-review-develop into al-dev-develop; post-commit review is internal, not external agent",
      "target_files": [
        "profile-al-dev-shared/agents/al-dev-develop.md",
        "profile-al-dev-shared/agents/al-dev-review-develop.md"
      ],
      "file_count": 2
    },
    {
      "id": "s-003",
      "type": "split",
      "subject": "al-dev-develop",
      "proposed_change": "Extract code review into separate agent; al-dev-develop is implementing + reviewing simultaneously",
      "target_files": ["profile-al-dev-shared/agents/al-dev-develop.md"],
      "file_count": 1
    }
  ]
}
```text

---

## Manifest Format

**Location:** `.dev/al-dev-map-suggestions-verify-runs/<run_id>/manifest.json`

The manifest is created by Phase 2 (dispatch) and updated by Phase 3 (collection). It tracks the dispatch status of each suggestion and where its duck record is stored.

### Manifest Schema

**Root object fields:**

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `operation` | string | yes | Type of operation | Enum: `inline`, `remote` |
| `run_id` | string | yes | Matches checkpoint and queue run_id | UUID v4 format |
| `team_id` | string | no | ID of remote team (remote operation only) | e.g., `team-2026-05-31-001` |
| `phase` | string | yes | Current phase | Enum: `phase2`, `phase3` |
| `status` | string | yes | Overall manifest status | Enum: `pending`, `in_progress`, `completed`, `failed` |
| `dispatched_at` | string | yes | ISO 8601 timestamp when team was spawned or inline started | e.g., `2026-05-31T14:22:40Z` |
| `expected_completion` | string | no | ISO 8601 timestamp when team is expected to finish | e.g., `2026-05-31T14:27:40Z` |
| `suggestion_count` | integer | yes | Total suggestions in manifest (matches queue) | ≥ 0 |
| `suggestions` | array | yes | Array of suggestion status objects | See Suggestion Status schema below |

**Suggestion Status object fields (within suggestions array):**

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `id` | string | yes | Matches suggestion queue id | e.g., `s-001` |
| `type` | string | yes | Matches suggestion type | Enum: `trim`, `merge`, `split`, `inline`, `align`, `connect`, `promote` |
| `status` | string | yes | Verification status | Enum: `pending`, `in_progress`, `completed`, `failed` |
| `duck_record_path` | string | no | Relative path to duck record JSON | e.g., `.dev/al-dev-map-suggestions-verify-runs/f47ac10b-58cc-4372-a567-0e02b2c3d479/duck-records/s-001.json` |
| `error` | object | no | Error details if status=failed | See Error Record schema below |

### Manifest Example

```json
{
  "operation": "remote",
  "run_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "team_id": "team-2026-05-31-001",
  "phase": "phase2",
  "status": "in_progress",
  "dispatched_at": "2026-05-31T14:22:40Z",
  "expected_completion": "2026-05-31T14:27:40Z",
  "suggestion_count": 3,
  "suggestions": [
    {
      "id": "s-001",
      "type": "trim",
      "status": "completed",
      "duck_record_path": ".dev/al-dev-map-suggestions-verify-runs/f47ac10b-58cc-4372-a567-0e02b2c3d479/duck-records/s-001.json"
    },
    {
      "id": "s-002",
      "type": "merge",
      "status": "in_progress",
      "duck_record_path": ".dev/al-dev-map-suggestions-verify-runs/f47ac10b-58cc-4372-a567-0e02b2c3d479/duck-records/s-002.json"
    },
    {
      "id": "s-003",
      "type": "split",
      "status": "failed",
      "duck_record_path": ".dev/al-dev-map-suggestions-verify-runs/f47ac10b-58cc-4372-a567-0e02b2c3d479/duck-records/s-003-error.json",
      "error": {
        "status": "file_not_found",
        "error": "Target file not accessible",
        "error_detail": "profile-al-dev-shared/agents/al-dev-develop.md is not readable (permission denied)"
      }
    }
  ]
}
```text

---

## Duck Record Format

**Location:** `.dev/al-dev-map-suggestions-verify-runs/<run_id>/duck-records/<id>.json`

A successful duck record documents the verification result of one suggestion. Created by duck verification workers (either inline or remote team).

### Duck Record Schema

**Root object fields:**

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `suggestion_id` | string | yes | Matches suggestion.id from queue | e.g., `s-001` |
| `type` | string | yes | Suggestion type being verified | Enum: `trim`, `merge`, `split`, `inline`, `align`, `connect`, `promote` |
| `verdict` | string | yes | Overall verification result | Enum: `ACCEPT`, `DEFER`, `REJECT` |
| `state` | string | yes | Comma-separated list of check phases passed | e.g., `u1_passed,u2_passed,u3_passed,type_checks_passed` |
| `side_effects` | array | yes | List of side effect warnings | e.g., `["Will remove 3 import statements", "Affects 2 downstream agents"]` |
| `evidence` | array | yes | Check results with details | See Evidence Entry schema below |
| `worker_id` | string | no | ID of worker that ran verification | e.g., `worker-42` |
| `completed_at` | string | yes | ISO 8601 timestamp when verification completed | e.g., `2026-05-31T14:24:10Z` |

**Evidence entry fields (within evidence array):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `check` | string | yes | Name of check that ran |
| `result` | string | yes | Result of check |
| `message` | string | yes | Human-readable check result |
| `findings` | string | no | Detailed findings if applicable |

### Duck Record Example (Success)

```json
{
  "suggestion_id": "s-001",
  "type": "trim",
  "verdict": "ACCEPT",
  "state": "u1_passed,u2_passed,u3_passed,type_checks_passed",
  "side_effects": [
    "Removes --output flag documentation from agent argument-hint",
    "No external callers of this flag found"
  ],
  "evidence": [
    {
      "check": "U1: File accessibility",
      "result": "pass",
      "message": "All 1 target files are readable and syntactically valid"
    },
    {
      "check": "U2: Artifact presence",
      "result": "pass",
      "message": "Target artifact al-dev-plan exists and has all required sections (frontmatter, system prompt)"
    },
    {
      "check": "U3: Reference validity",
      "result": "pass",
      "message": "All internal references in al-dev-plan resolve to existing files"
    },
    {
      "check": "Trim: Unused verification",
      "result": "pass",
      "message": "Flag --output is mentioned only in argument-hint and in ARTIFACT-CONTRACT section. No external references found.",
      "findings": "Searched all agents and skills; no callers detected"
    }
  ],
  "worker_id": "worker-42",
  "completed_at": "2026-05-31T14:24:10Z"
}
```text

### Duck Record Example (DEFER)

```json
{
  "suggestion_id": "s-003",
  "type": "split",
  "verdict": "DEFER",
  "state": "u1_passed,u2_passed,u3_passed,type_checks_deferred",
  "side_effects": [
    "Would create new agent al-dev-develop-reviewer with separate tool assignment",
    "May require changes to skill dispatch logic in al-dev-develop caller"
  ],
  "evidence": [
    {
      "check": "U1: File accessibility",
      "result": "pass",
      "message": "All 1 target files are readable and syntactically valid"
    },
    {
      "check": "U2: Artifact presence",
      "result": "pass",
      "message": "Target artifact al-dev-develop exists and has all required sections"
    },
    {
      "check": "U3: Reference validity",
      "result": "pass",
      "message": "All internal references resolve"
    },
    {
      "check": "Split: Separable concerns",
      "result": "warning",
      "message": "al-dev-develop combines implementation and review; concerns are separable but highly coupled",
      "findings": "Implementation and review logic share state (code_context, compile_errors). Splitting requires state threading architecture decision. Recommend architect review before proceeding."
    }
  ],
  "worker_id": "worker-43",
  "completed_at": "2026-05-31T14:25:05Z"
}
```text

---

## Error Record Format

**Location:** `.dev/al-dev-map-suggestions-verify-runs/<run_id>/duck-records/<id>-error.json`

An error record documents a failed verification attempt. Created when duck verification workers encounter unrecoverable errors.

### Error Record Schema

**Root object fields:**

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `suggestion_id` | string | yes | Matches suggestion.id from queue | e.g., `s-003` |
| `type` | string | yes | Suggestion type being verified | Enum: `trim`, `merge`, `split`, `inline`, `align`, `connect`, `promote` |
| `status` | string | yes | Error category | Enum: `file_not_found`, `parse_error`, `check_failure`, `timeout` |
| `error` | string | yes | Short error title | e.g., `File not accessible` |
| `error_detail` | string | yes | Long-form error message with context | e.g., `profile-al-dev-shared/agents/nonexistent.md: permission denied` |
| `attempted_checks` | array | yes | List of checks attempted before failure | e.g., `["U1: File accessibility", "U2: Artifact presence"]` |
| `completed_checks` | array | yes | List of checks that passed before failure | e.g., `["U1: File accessibility"]` |
| `worker_id` | string | no | ID of worker that encountered error | e.g., `worker-44` |
| `failed_at` | string | yes | ISO 8601 timestamp when error occurred | e.g., `2026-05-31T14:26:00Z` |

### Error Record Example (File Not Found)

```json
{
  "suggestion_id": "s-003",
  "type": "split",
  "status": "file_not_found",
  "error": "Target file not accessible",
  "error_detail": "profile-al-dev-shared/agents/al-dev-develop.md: file does not exist or is not readable (permission denied on parent directory)",
  "attempted_checks": [
    "U1: File accessibility",
    "U2: Artifact presence",
    "U3: Reference validity"
  ],
  "completed_checks": [],
  "worker_id": "worker-44",
  "failed_at": "2026-05-31T14:26:00Z"
}
```text

### Error Record Example (Parse Error)

```json
{
  "suggestion_id": "s-002",
  "type": "merge",
  "status": "parse_error",
  "error": "Invalid JSON in target artifact",
  "error_detail": "profile-al-dev-shared/agents/al-dev-review-develop.md: frontmatter YAML is invalid. Expected 'tools:' to be an array, got string.",
  "attempted_checks": [
    "U1: File accessibility",
    "U2: Artifact presence"
  ],
  "completed_checks": [
    "U1: File accessibility"
  ],
  "worker_id": "worker-45",
  "failed_at": "2026-05-31T14:26:15Z"
}
```text

### Error Record Example (Timeout)

```json
{
  "suggestion_id": "s-004",
  "type": "align",
  "status": "timeout",
  "error": "Verification took too long",
  "error_detail": "Connect: Pattern verification timed out after 30 seconds while scanning 12 files for shared patterns. Likely very large file tree or circular reference scan.",
  "attempted_checks": [
    "U1: File accessibility",
    "U2: Artifact presence",
    "U3: Reference validity",
    "Connect: Pattern matching"
  ],
  "completed_checks": [
    "U1: File accessibility",
    "U2: Artifact presence",
    "U3: Reference validity"
  ],
  "worker_id": "worker-46",
  "failed_at": "2026-05-31T14:27:30Z"
}
```text

---

## Schema Validation Rules

All JSON artifacts must satisfy these validation constraints:

1. **UUID format:** `run_id` and `team_id` must be valid UUID v4 format
2. **ISO 8601 timestamps:** All `*_at` fields must be valid ISO 8601 format with timezone (e.g., `2026-05-31T14:22:35Z`)
3. **Enum values:** All fields with enum constraints must match exactly one value from the enum list
4. **Array consistency:** Array length fields (e.g., `suggestion_count`, `file_count`) must equal array length
5. **Path consistency:** Relative paths in manifest must resolve from repo root
6. **Reference integrity:** All `id` fields must be referenced consistently across artifacts
7. **No null fields:** No required fields may be null or missing in valid artifacts
8. **Optional fields:** Fields marked "no" in Required column may be omitted but must not be null if present

---

## Artifact Lifecycle

### Phase 1 (Extraction)

1. Skill calls `extract-suggestions.py`
2. Script writes `.dev/al-dev-map-suggestions-verify-runs/<run_id>/suggestion-queue.json`
3. Skill updates checkpoint: `phase=extracting`, `status=completed`

### Phase 2 (Dispatch or Inline)

**If 1-2 suggestions (inline path):**

1. Skill calls inline verification for each suggestion
2. Workers write duck records directly to `.dev/al-dev-map-suggestions-verify-runs/<run_id>/duck-records/<id>.json`
3. Skill skips manifest creation and proceeds to Phase 3

**If 3+ suggestions (background path):**

1. Skill creates manifest with all suggestions in `pending` status
2. Skill dispatches a background team (one agent per suggestion)
3. Skill updates checkpoint: `phase=dispatched`, `status=waiting`
4. Skill returns control to user

### Phase 3 (Collection)

1. User invokes `/al-dev-map-suggestions-verify --resume`
2. Skill reads checkpoint, validates manifest, polls for completion
3. Skill reads all duck records from `.dev/al-dev-map-suggestions-verify-runs/<run_id>/duck-records/`
4. Skill filters by verdict (ACCEPT/DEFER/REJECT)
5. Skill invokes `superpowers:writing-plans` with filtered suggestions
6. Skill updates checkpoint: `phase=completed`, `status=completed`

---

## File Naming Conventions

| Artifact | Path Pattern | Example |
|----------|--------------|---------|
| Checkpoint | `.dev/progress.md` (section within) | (section header: `## Plan-Map-Changes State`) |
| Suggestion Queue | `.dev/al-dev-map-suggestions-verify-runs/<run_id>/suggestion-queue.json` | `.dev/al-dev-map-suggestions-verify-runs/f47ac10b-58cc-4372-a567-0e02b2c3d479/suggestion-queue.json` |
| Manifest | `.dev/al-dev-map-suggestions-verify-runs/<run_id>/manifest.json` | `.dev/al-dev-map-suggestions-verify-runs/f47ac10b-58cc-4372-a567-0e02b2c3d479/manifest.json` |
| Duck Record (success) | `.dev/al-dev-map-suggestions-verify-runs/<run_id>/duck-records/<suggestion_id>.json` | `.dev/al-dev-map-suggestions-verify-runs/f47ac10b-58cc-4372-a567-0e02b2c3d479/duck-records/s-001.json` |
| Duck Record (error) | `.dev/al-dev-map-suggestions-verify-runs/<run_id>/duck-records/<suggestion_id>-error.json` | `.dev/al-dev-map-suggestions-verify-runs/f47ac10b-58cc-4372-a567-0e02b2c3d479/duck-records/s-003-error.json` |

---

## Backward Compatibility

As the schema evolves, maintain compatibility by:

1. Only adding new optional fields to existing objects (do not remove fields)
2. Maintaining enum value stability (do not remove or rename values)
3. Incrementing schema version if breaking changes required (add `schema_version: "1.0"` field to root objects)
4. Documenting migration paths in CHANGELOG

Current schema version: `1.0`
