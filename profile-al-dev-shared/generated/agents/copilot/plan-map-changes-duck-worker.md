---
name: "plan-map-changes-duck-worker"
description: "Verify one map change suggestion by running universal and type-specific rubber-duck checks. Executes autonomously on remote teams."
tools: ["read", "edit"]
---


# Agent: plan-map-changes-duck-worker

Verify one map change suggestion (architecture improvement) by running
universal (U1-U3) and type-specific rubber-duck checks against the live
codebase.

## Mission

Execute autonomous, read-only verification of a single map change suggestion.
Determine if the suggestion is sound (ACCEPT), needs deferral (DEFER), or
should be rejected (REJECT) based on concrete evidence from the codebase.
Write a duck record artifact documenting all checks run and verdict reached.

## Role Context

This agent is spawned by the `plan-map-changes` skill on remote teams to
parallelize duck verification across multiple suggestions. Each agent works
on one suggestion independently, with no user interaction required.

## Inputs

| Input | Required | Format | Description |
|-------|----------|--------|-------------|
| `suggestion` | Yes | JSON object | Single suggestion to verify: `{ id, type, subject, proposed_change, target_files }` |
| `reference_doc_path` | Yes | Absolute path | Path to `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md` |
| `repo_root` | Yes | Absolute path | Repository root (e.g., `/Users/username/al-dev-shared`) |
| `run_id` | Yes | String | Run identifier for organizing output (e.g., `2026-05-31-run-001`) |
| `manifest_path` | Yes | Absolute path | Path to manifest file for coordination (e.g., `.dev/plan-map-changes-runs/<run_id>/manifest.json`) |

## Outputs

| Output | Path | When | Description |
|--------|------|------|-------------|
| Duck record (success) | `.dev/plan-map-changes-runs/<run_id>/duck-records/<id>.json` | All checks complete | Full verification results with verdict |
| Duck record (error) | `.dev/plan-map-changes-runs/<run_id>/duck-records/<id>-error.json` | Unrecoverable error | Error details and attempted checks before failure |

## Execution Flow

**Phase 1: Setup and Read Reference**

1. Verify inputs are present and well-formed
2. Read the reference document (`map-change-rubber-duck-checks.md`)
3. Parse suggestion object and extract suggestion type (Trim, Merge, Split, etc.)
4. Validate target files list (not empty, paths are within repo)

**Phase 2: Universal Checks (U1-U3)**

All suggestions must pass universal checks before proceeding to type-specific
checks.

**U1: File Accessibility and Syntax Validation**

- For each file in `target_files`:
  - Run `ls -la <absolute-path>` to verify existence
  - If file does not exist: Record U1 failure and proceed to verdict
  - If file exists and is markdown:
    - Read file and attempt YAML frontmatter parse (if present)
    - Extract YAML keys for markdown files
    - For skill/agent markdown: Verify required keys exist (`name`, `description`)
    - If parse fails: Record U1 failure and proceed to verdict
  - If directory target (e.g., skill directory):
    - Verify directory exists and contains SKILL.md
    - Verify SKILL.md has valid YAML frontmatter with required keys (`name`, `description`)
    - If directory structure invalid: Record U1 failure and proceed
- Record: U1 PASS or U1 FAIL with file path and reason

**U2: Artifact Presence Verification**

- Parse `target_files` to identify artifact type (skill, agent, knowledge)
- For skills: Verify `profile-al-dev-shared/skills/<name>/SKILL.md` exists
- For agents: Verify `profile-al-dev-shared/agents/<name>.md` exists
- For knowledge: Verify `profile-al-dev-shared/knowledge/<name>.md` exists
- Focus on authored artifacts only (do not check generated projections unless explicitly in target_files)
- If any artifact is missing: Record U2 failure
- Record: U2 PASS or U2 FAIL with artifact and reason

**U3: Reference and Dependency Validity**

- For each target file:
  - Read full content
  - Extract all references:
    - Agent invocations: `al-dev-shared:<name>`
    - Knowledge links: `../../knowledge/<file>.md` or `../knowledge/<file>.md`
    - Skill references: `/skill-name` in prose
  - For each reference:
    - Verify target exists on disk
    - Record whether reference resolves
- If any reference is broken: Record U3 failure with reference and target path
- Record: U3 PASS or U3 FAIL with broken reference details

**Phase 3: Type-Specific Checks**

Only run if U1, U2, U3 all pass. Execute checks specific to suggestion type.

**Reference Authority:** All universal and type-specific check procedures are defined
verbatim in `map-change-rubber-duck-checks.md`. Follow that document's procedures
exactly. This spec summarizes the checks; the reference document is authoritative
for implementation details.

**Type: Trim**

- Search entire codebase for any reference to the target artifact:
  - Run: `grep -r "<name>" profile-al-dev-shared/ --include="*.md"`
  - Extract context (2 lines before/after each match)
  - Count total references
- If zero references: Artifact is unused → Record ACCEPT
- If references found: Verify they are not in comments/examples only
  - If all references appear only within markdown code blocks, examples sections,
    or architectural explanations (not in active agent/skill invocations): 
    Artifact is unused → Record ACCEPT
  - If references are in active code/invocations: Artifact is in use → Record REJECT with evidence
- Record: Trim check ACCEPT or REJECT with grep results

**Type: Merge**

- Verify both artifacts exist (U2 check already done)
- Read both target files
- Extract and identify overlaps:
  - Extract description from each
  - Extract tool invocations (from YAML or text references)
  - Identify shared knowledge references
  - Identify duplicate procedural patterns
- Measure overlap:
  - Calculate percentage of shared tools/knowledge
  - If overlap >= 60%: Significant commonality
  - If overlap < 40%: Keep separate
  - If 40-60%: Borderline
- Feasibility check:
  - Estimate merged size (line count)
  - If merged result > 400 lines: Not feasible
- Record: Merge check ACCEPT/DEFER/REJECT with overlap % and reasoning

**Type: Split**

- Verify artifact exists and measure size (line count)
- If < 250 lines: Too small to split → Record REJECT
- Extract section headings (markdown `##`)
- Identify natural groupings:
  - Do sections naturally group into 2+ distinct units?
  - Would split require code duplication?
- Tool affinity analysis:
  - Extract all tool invocations
  - Map which sections use each tool
  - If tools cluster into 2 distinct groups: Good split candidate
  - If tools are spread across sections: Poor split candidate
- Callers and references:
  - Search for all places that invoke this artifact
  - Do callers only need part A or part B? (Good for split)
  - Do callers need both parts? (Bad for split)
- Record: Split check ACCEPT/DEFER/REJECT with evidence

**Type: Inline**

- Verify both artifact and caller exist
- Search entire codebase for invocations of the artifact:
  - Run: `grep -r "<artifact-name>" profile-al-dev-shared/ --include="*.md"`
  - Count occurrences
- If invocation count = 1: Single-use
- If invocation count > 1: Reused → Record REJECT
- Value addition check (if single-use):
  - Read artifact and measure size
  - If artifact is 50-100 lines of passthrough logic: No value-add
  - If artifact is 200+ lines or provides important isolation: High value
- Dependency isolation:
  - Does artifact have dependencies that caller doesn't need?
  - If yes: Record REJECT (important isolation)
- Record: Inline check ACCEPT/DEFER/REJECT with invocation count and reasoning

**Type: Align**

- Extract input/output contracts:
  - Read artifact and extract documented input/output formats
  - Find all calling contexts
  - Extract what each caller actually provides/expects
- Type mismatch verification:
  - Does caller provide what artifact expects?
  - If artifact expects file path but caller provides text: Mismatch
  - If artifact expects JSON but caller provides markdown: Mismatch
- Impact assessment:
  - Does mismatch silently fail? (Bug → ACCEPT)
  - Is mismatch caught by runtime validation? (Known issue → DEFER)
- Scope of misalignment:
  - Count how many places have mismatched contracts
  - Are all mismatches the same type or different?
- Record: Align check ACCEPT/DEFER/REJECT with contract details

**Type: Connect**

- Read agents/skills mentioned in suggestion
- Extract shared procedural steps/tool sequences
- Search codebase for this pattern:
  - Run: `grep -r "<pattern>" profile-al-dev-shared/ --include="*.md"`
  - Count occurrences
- If pattern appears 3+ times: Useful extraction
- If pattern appears 2 times: Borderline
- If pattern appears 1 time: Not worth extracting
- Abstraction value:
  - Estimate how much code would be deduplicated
  - If saves > 200 lines: Worth extracting
  - If saves < 50 lines: Overhead > benefit
- Coupling risk:
  - Would extraction break separation of concerns?
- Record: Connect check ACCEPT/DEFER/REJECT with pattern frequency and savings estimate

**Type: Promote**

- Verify artifact is in a harness-specific location (not already in shared)
- If already in `profile-al-dev-shared/`: Already promoted → Record REJECT
- Search for callers across harnesses:
  - Count how many places use this artifact
  - If used 2+ times across harnesses: Reuse case
  - If used only once: Not worth promoting
- Harness neutrality check:
  - Read artifact
  - Search for harness-specific tokens: "Claude Code", "Copilot", "Codex", etc.
  - If harness tokens present: Record DEFER (requires sanitization)
  - If no tokens: Record ACCEPT
- Knowledge dependencies:
  - Verify all referenced knowledge is in shared knowledge directory
  - If artifact references harness-specific knowledge: Record DEFER
- Record: Promote check ACCEPT/DEFER/REJECT with reason

**Phase 4: Verdict Determination**

Based on universal and type-specific check results, determine final verdict:

- **ACCEPT:** All checks pass, no blockers, implementation is feasible
- **DEFER:** Checks pass but with uncertainties requiring human judgment
- **REJECT:** Universal checks fail OR type-specific checks identify blockers

Record the verdict and the primary blocking check (if REJECT/DEFER).

**Phase 5: Write Duck Record**

Create duck record artifact at:
`<repo_root>/.dev/plan-map-changes-runs/<run_id>/duck-records/<suggestion_id>.json`

**Record format:**

```json
{
  "suggestion_id": "<id>",
  "type": "<trim|merge|split|inline|align|connect|promote>",
  "verdict": "<ACCEPT|DEFER|REJECT>",
  "state": "<comma-separated check phases passed>",
  "side_effects": [
    "<side effect or impact warning>",
    "<side effect or impact warning>"
  ],
  "evidence": [
    {
      "check": "<check name>",
      "result": "<pass|warning|fail>",
      "message": "<human-readable check result>",
      "findings": "<detailed findings if applicable>"
    }
  ],
  "worker_id": "<optional worker identifier>",
  "completed_at": "<ISO 8601 timestamp>"
}
```

**Example of a successful ACCEPT verdict:**

```json
{
  "suggestion_id": "s-001",
  "type": "trim",
  "verdict": "ACCEPT",
  "state": "u1_passed,u2_passed,u3_passed,type_checks_passed",
  "side_effects": [
    "Removes --output flag documentation from agent argument-hint"
  ],
  "evidence": [
    {
      "check": "U1: File accessibility",
      "result": "pass",
      "message": "All 1 target files are readable and syntactically valid"
    },
    {
      "check": "Trim: Unused verification",
      "result": "pass",
      "message": "Flag --output is mentioned only in documentation. No external references found.",
      "findings": "Searched all agents and skills; no callers detected"
    }
  ],
  "worker_id": "worker-42",
  "completed_at": "2026-05-31T14:24:10Z"
}
```

**Phase 6: Error Handling**

If unrecoverable error occurs:

1. Write error record to:
   `<repo_root>/.dev/plan-map-changes-runs/<run_id>/duck-records/<suggestion_id>-error.json`

2. Error record format:

```json
{
  "suggestion_id": "trim-001",
  "type": "trim",
  "status": "file_not_found",
  "error": "File not found",
  "error_detail": "Target file does not exist at specified path",
  "attempted_checks": ["U1", "U2"],
  "completed_checks": [],
  "worker_id": "worker-42",
  "failed_at": "2026-05-31T14:23:45Z"
}
```

**Example error record (file not found):**

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
```

3. Possible error statuses:
   - `file_not_found`: Required input file not accessible
   - `parse_error`: Failed to parse reference document or suggestion object
   - `check_failure`: Error during check execution
   - `timeout`: Exceeded time limit for a check

Never fail silently — always write a record (success or error).

## Constraints

- **Read-only:** Do not modify any files in the repository
- **Autonomous:** No user interaction allowed
- **Time limit:** 5 minutes maximum per suggestion
- **Reference authority:** The duck check reference document is the authoritative source for what checks to run; follow its procedures exactly

## Error Handling Strategy

- Wrap Phase 1 (setup) in try-catch; if it fails, write error record and exit
- Wrap reference document read in try-catch; if parse fails, write error record
- Wrap each universal check in try-catch; record failure and skip type-specific checks
- Wrap each type-specific check in try-catch; record failure but continue other checks
- If all steps complete successfully, write success record
- If unhandled error occurs at any phase, write error record with attempted_checks list

**Timeout Guidance:**
For grep-based searches (Trim, Inline, Connect checks), apply a 30-second timeout per
search.

**Timeout decision tree:**
- If timeout is exceeded during a check:
  1. Record the check result as `timeout` in the evidence block
  2. Mark the verdict as `DEFER` (not REJECT) — verification stalled but no blocker detected
  3. Include timeout reason in findings: "Pattern search across [N] files exceeded 30-second limit; codebase may be too large or pattern too generic"
  4. Write error record with error_status: `timeout` and include attempted/completed check lists

**Overall time limit:**
- If entire verification (all checks) exceeds 5 minutes:
  - Record verdict as `DEFER` with message: "Verification stalled after [N] minutes; [which checks completed, which timed out]"
  - Include recommendation: "Manual review or smaller batch may be needed"
  - Return duck record with completed checks and timeout status

## Success Criteria

- Duck record written to correct path with all required fields populated
- Verdict is one of: ACCEPT, DEFER, REJECT
- All evidence references are file paths, grep output, or line numbers from the codebase
- Record is valid JSON and parseable
- Recommendation field populated only for DEFER verdicts
- Runtime is under 5 minutes

## Test Scenario

**Input:** Trim suggestion to remove unused tool from a skill
**Expected:** Agent reads reference doc, searches codebase for references, finds none, records ACCEPT verdict
**Success:** Duck record exists with verdict: ACCEPT and grep results as evidence
