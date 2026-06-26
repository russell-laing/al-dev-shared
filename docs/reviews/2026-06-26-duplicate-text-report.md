# Duplicate Text Report

**Date:** 2026-06-26

## Scan Configuration

- Inputs: `.claude`, `profile-al-dev-shared`
- Minimum duplicate length: 8 lines
- Minimum nonblank lines: 4
- Minimum characters: 80
- Include archived content: no
- Include generated content: no
- Text files scanned: 222
- Files excluded: 126

Trailing whitespace and line endings are normalized. Other text remains exact.

## Summary

Found 38 grouped duplicate blocks.

Generated and archived matches are excluded by default because they are often
intentional. Each finding still requires human review before refactoring.

## Findings

### 1. 16 lines, 2 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/agents/al-dev-developer-tdd.md:77`
  - `profile-al-dev-shared/agents/al-dev-developer-traditional.md:62`

Excerpt:

```text

## Shared Standards

Follow `knowledge/al-developer-shared-standards.md` for shared
pre-flight, AL coding standards, and compile-output safeguards.

Route-specific execution rules still apply:

- TDD agent: use `TDD_CYCLE_GATE` after each RED, GREEN, and REFACTOR phase.
- Traditional agent: use `BUILD_VERIFY_GATE` after implementation.
- `/al-dev-fix` dispatches to the traditional agent without inheriting
  orchestrate-only ownership-report wording from the spawn prompt.
```

### 2. 13 lines, 4 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/sync-map-documentation-agent-metadata.md:10`
  - `.claude/agents/sync-map-documentation-agent-update.md:10`
  - `.claude/agents/sync-map-documentation-skill-metadata.md:11`
  - `.claude/agents/sync-map-documentation-skill-update.md:11`

Excerpt:

```text
model: sonnet
tools: ["Read", "Bash", "Write"]
---

## Inputs

| Field | Description |
|---|---|
| run_id | The timestamp run ID (e.g. `20260531T143000`) |
| result_dir | Absolute path to `.dev/sync-map-documentation-runs/<run_id>/` |

## Outputs
```

### 3. 13 lines, 2 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/skills/al-dev-commit-preflight/SKILL.md:23`
  - `profile-al-dev-shared/skills/al-dev-commit/SKILL.md:23`

Excerpt:

```text

---

## Intent Preflight

Before dispatching commit agents, staging files, unstaging files, or committing,
apply `knowledge/intent-preflight.md`.

Default intent for this skill is `COMMIT`. If the request is review-only,
edit-only, assessment-only, or asks for a commit plan without committing, stop
and ask the intent-mismatch prompt from `knowledge/intent-preflight.md` before
continuing.
```

### 4. 12 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/design-agent-lens-scope-isolation.md:4`
  - `.claude/agents/quality-agent-multilens.md:4`

Excerpt:

```text
model: haiku
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` files |

## Outputs

```

### 5. 12 lines, 2 occurrences

- Scope: within one file
- Locations:
  - `profile-al-dev-shared/knowledge/tdd-credit-limit-example.md:98`
  - `profile-al-dev-shared/knowledge/tdd-credit-limit-example.md:167`

Excerpt:

````text
        exit(Outstanding + OrderAmount <= Customer.CreditLimit);
    end;
}
```

```bash
# Compile the app
al-compile

# Publish to BC server
bc-publish

````

### 6. 12 lines, 3 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/skills/al-dev-develop-orchestrate/validate-code-review.py:6`
  - `profile-al-dev-shared/skills/al-dev-interview/validate-requirements.py:6`
  - `profile-al-dev-shared/skills/al-dev-plan/validate-plan.py:6`

Excerpt:

```text

Exit codes:
    0 - All checks pass
    1 - Validation issues found (printed to stdout)
"""

import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
```

### 7. 11 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/design-skill-lens-preplanning.md:22`
  - `.claude/agents/design-skill-lens-shared-backbone.md:21`

Excerpt:

````text

| Severity | File:Line | Finding | Suggested fix |
|----------|-----------|---------|---------------|
| High/Medium/Low | skills/name/SKILL.md:NN | description | fix description |
```

Returns `_No issues found._` when no violations are detected. The caller includes
this block verbatim in the aggregated dossier.

---

````

### 8. 11 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/quality-agent-multilens.md:13`
  - `.claude/agents/quality-skill-multilens.md:13`

Excerpt:

```text

## Outputs

Four findings blocks in one return, each preceded by its own lens marker
(`lens: <name>`). See Output Format.

---

## Procedure

Read every file path in the dispatch prompt **once**. Hold all files in context,
```

### 9. 11 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/quality-agent-multilens.md:92`
  - `.claude/agents/quality-skill-multilens.md:96`

Excerpt:

```text
- Steps that reference undefined placeholders or variables

**Severity rules:**

- High: ambiguity that changes observable behavior
- Medium: vague qualifiers with no definition
- Low: minor style issues

## Lens 3: Description Drift

Read every file path provided in the dispatch prompt. For each file, derive the
```

### 10. 11 lines, 6 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/sync-map-documentation-agent-compare.md:8`
  - `.claude/agents/sync-map-documentation-agent-metadata.md:10`
  - `.claude/agents/sync-map-documentation-agent-update.md:10`
  - `.claude/agents/sync-map-documentation-skill-compare.md:8`
  - `.claude/agents/sync-map-documentation-skill-metadata.md:11`
  - `.claude/agents/sync-map-documentation-skill-update.md:11`

Excerpt:

```text
model: sonnet
tools: ["Read", "Bash", "Write"]
---

## Inputs

| Field | Description |
|---|---|
| run_id | The timestamp run ID (e.g. `20260531T143000`) |
| result_dir | Absolute path to `.dev/sync-map-documentation-runs/<run_id>/` |

```

### 11. 11 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/sync-map-documentation-agent-compare.md:81`
  - `.claude/agents/sync-map-documentation-skill-compare.md:82`

Excerpt:

```text

If that section is missing or unreadable, **stop and report** the missing
canonical comparison contract (`.claude/knowledge/sync-maps-edit-cases.md`).
Do not emit a discrepancy report from the legal `type` names alone — the section
holds the classification rules (either-layer absence, archived-object detection,
tools/caller normalization, phase-node interpretation), without which the audit
cannot be relied on.

If that section is **present but contains definitions for only a subset of the
valid `type` values**, use the definitions that are present. For any `type` value
that appears in the audit JSON but has no definition in the section, add a
```

### 12. 11 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/sync-map-documentation-agent-update.md:25`
  - `.claude/agents/sync-map-documentation-skill-update.md:26`

Excerpt:

```text
Returns absolute path only — no other prose.

---

## Instructions

All relative paths in these instructions are from the repository root:
`/Users/russelllaing/al-dev-shared`. Before proceeding, run
`git rev-parse --show-toplevel` to confirm the repo root matches this path;
if not, substitute the actual repo root in all relative paths below.

```

### 13. 11 lines, 2 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/agents/al-dev-ticket-context-writer.md:109`
  - `profile-al-dev-shared/knowledge/ticket-agent-invocation-pattern.md:55`

Excerpt:

````text

```text
TICKET_CONTEXT_WRITTEN: .dev/YYYY-MM-DD-al-dev-ticket-ticket-context.md
TICKET_ID: [ID]
STATUS: [Status]
PRIORITY: [Priority]
COMMENTS_COUNT: [N]
ATTACHMENTS: [Count or "None"]
INLINE_IMAGES_COUNT: [N or "None"]
```

````

### 14. 11 lines, 3 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/skills/al-dev-develop-orchestrate/validate-code-review.py:45`
  - `profile-al-dev-shared/skills/al-dev-interview/validate-requirements.py:37`
  - `profile-al-dev-shared/skills/al-dev-plan/validate-plan.py:47`

Excerpt:

```text
        )

    headings = [
        ln.lstrip("#").strip() for ln in lines if ln.startswith("#")
    ]
    heading_text = " ".join(headings).lower()

    for section in REQUIRED_SECTIONS:
        if section.lower() not in heading_text:
            issues.append(f"Missing required section: '{section}'")

```

### 15. 11 lines, 3 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/skills/al-dev-develop-orchestrate/validate-code-review.py:55`
  - `profile-al-dev-shared/skills/al-dev-interview/validate-requirements.py:61`
  - `profile-al-dev-shared/skills/al-dev-plan/validate-plan.py:64`

Excerpt:

```text

    for i, line in enumerate(lines[:-1]):
        if line.startswith("#") and lines[i + 1].startswith("#"):
            issues.append(
                f"Possibly empty section at line {i + 1}: "
                f"'{line.strip()}'"
            )

    return issues


```

### 16. 10 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/quality-agent-multilens.md:143`
  - `.claude/agents/quality-skill-multilens.md:144`

Excerpt:

```text
- Low: minor verb mismatch with no behavioral consequence

---

## Output Format

Your entire reply is exactly four blocks, in the order below, and nothing else.
The reply must **begin** with the first `<!-- lens: … -->` marker — no preamble,
no plan, no "Now I'll analyze…"/"Now I'll apply…" sentence, no closing summary.

```

### 17. 10 lines, 6 occurrences

- Scope: across files
- Locations:
  - `.claude/skills/audit-knowledge-quality/SKILL.md:36`
  - `.claude/skills/discover-plugin-health/SKILL.md:40`
  - `.claude/skills/fix-knowledge-quality/SKILL.md:29`
  - `.claude/skills/plan-plugin-findings/SKILL.md:50`
  - `.claude/skills/report-plugin-health/SKILL.md:34`
  - `.claude/skills/sync-map-documentation/SKILL.md:41`

Excerpt:

```text

## Maintainer Contracts

Apply `../../knowledge/phase-proof-contract.md` at every phase boundary before
reporting completion or updating `.dev/health-loop-state.md`.

Apply `../../knowledge/dispatch-fallback-contract.md` before every agent
dispatch. Declare the preferred path, run preflight, fall back
deterministically, and log `preferred → outcome → fallback → reason`.

```

### 18. 10 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/skills/sync-map-documentation-apply/SKILL.md:39`
  - `.claude/skills/sync-map-documentation-write/SKILL.md:41`

Excerpt:

```text

**Working directory assumption:** All relative paths are resolved from
`/Users/russelllaing/al-dev-shared`. Use absolute paths in Bash commands.

---

## Phase-proof requirement

This skill follows `../../knowledge/phase-proof-contract.md` — emit a phase-proof block at each phase boundary before reporting completion or updating `.dev/health-loop-state.md`.

```

### 19. 10 lines, 2 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/knowledge/compile-lint-procedure.md:72`
  - `profile-al-dev-shared/skills/al-dev-lint/SKILL.md:55`

Excerpt:

```text

```bash
if command -v al-compile &>/dev/null; then
  al-compile --output .dev/compile-errors.log
elif command -v al &>/dev/null; then
  al compile /project:. /packagecachepath:.alpackages \
    /errorlog:.dev/compile-errors.log
else
  echo "AL compiler not found; install al-compile or AL CLI tools before retrying." \
    | tee .dev/compile-errors.log
```

### 20. 9 lines, 3 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/design-agent-lens-scope-isolation.md:4`
  - `.claude/agents/design-agent-lens-usage-patterns.md:4`
  - `.claude/agents/quality-agent-multilens.md:4`

Excerpt:

```text
model: haiku
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` files |
```

### 21. 9 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/design-skill-lens-complexity.md:4`
  - `.claude/agents/design-skill-lens-shared-backbone.md:4`

Excerpt:

```text
model: sonnet
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |
```

### 22. 9 lines, 3 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/design-skill-lens-preplanning.md:4`
  - `.claude/agents/design-skill-lens-surface-placement.md:4`
  - `.claude/agents/quality-skill-multilens.md:4`

Excerpt:

```text
model: haiku
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |
```

### 23. 9 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/sync-map-documentation-agent-compare.md:25`
  - `.claude/agents/sync-map-documentation-agent-metadata.md:24`

Excerpt:

```text
Do not summarise findings — return only the path.

**JSON schema:**

```json
{
  "surface": "agents",
  "run_id": "<run_id>",
  "total_files": 12,
```

### 24. 9 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/sync-map-documentation-agent-compare.md:51`
  - `.claude/agents/sync-map-documentation-skill-compare.md:48`

Excerpt:

```text

---

## Instructions

All relative paths are from the repository root: `/Users/russelllaing/al-dev-shared`.

### Step 1 — Load metadata

```

### 25. 9 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/sync-map-documentation-skill-compare.md:25`
  - `.claude/agents/sync-map-documentation-skill-metadata.md:25`

Excerpt:

```text
Do not summarise findings — return only the path.

**JSON schema:**

```json
{
  "surface": "skills",
  "run_id": "<run_id>",
  "total_files": 19,
```

### 26. 9 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/knowledge/report-input-gates.md:121`
  - `.claude/skills/report-plugin-health/SKILL.md:144`

Excerpt:

```text

Run `python3 scripts/health_disposition_store.py match` against the JSONL event
store and generated views. Read `docs/health/dispositions-index.json` first for
counts, then read `docs/health/dispositions-open.md` only when open accepted
events need inspection. New decisions are appended with `append_event` and
views are regenerated; do not call `append_row`, read
`docs/health/dispositions.md` for ordinary suppression, or use
`iter_history_rows` for new closure chronology.

```

### 27. 9 lines, 2 occurrences

- Scope: within one file
- Locations:
  - `profile-al-dev-shared/knowledge/tdd-credit-limit-example.md:25`
  - `profile-al-dev-shared/knowledge/tdd-credit-limit-example.md:78`

Excerpt:

```text

```al
codeunit 50100 "Credit Limit Validator"
{
    procedure ValidateCreditLimit(
        CustomerNo: Code[20];
        OrderAmount: Decimal;
        Repo: Interface ICustomerRepository
    ): Boolean
```

### 28. 9 lines, 3 occurrences

- Scope: within one file
- Locations:
  - `profile-al-dev-shared/knowledge/tdd-workflow.md:51`
  - `profile-al-dev-shared/knowledge/tdd-workflow.md:129`
  - `profile-al-dev-shared/knowledge/tdd-workflow.md:215`

Excerpt:

````text

   ```bash
   # Compile the app
   al-compile

   # Publish to BC server
   bc-publish
   ```

````

### 29. 8 lines, 4 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/design-agent-lens-model-fit.md:5`
  - `.claude/agents/design-agent-lens-scope-isolation.md:5`
  - `.claude/agents/design-agent-lens-usage-patterns.md:5`
  - `.claude/agents/quality-agent-multilens.md:5`

Excerpt:

```text
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` files |
```

### 30. 8 lines, 5 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/design-skill-lens-complexity.md:5`
  - `.claude/agents/design-skill-lens-preplanning.md:5`
  - `.claude/agents/design-skill-lens-shared-backbone.md:5`
  - `.claude/agents/design-skill-lens-surface-placement.md:5`
  - `.claude/agents/quality-skill-multilens.md:5`

Excerpt:

```text
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |
```

### 31. 8 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/verify-health-finding.md:105`
  - `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md:603`

Excerpt:

```text

```text
RUBBER DUCK: [Type — Subject]
Claim:        [what the suggestion says]
State:        [what reading the code reveals]
Side-effects: [files/scripts that depend on what's being changed]
Scope gap:    [anything the suggestion underspecifies, or "none"]
Verdict:      proceed | modify [reason] | skip [reason]
```

### 32. 8 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/knowledge/health-audit-preconditions.md:62`
  - `.claude/skills/implement-plugin-health/SKILL.md:438`

Excerpt:

````text

```bash
python3 scripts/select_health_artifacts.py \
  --directory docs/health \
  --kind health \
  --surface <surface>
```

````

### 33. 8 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/knowledge/health-filter-contract.md:144`
  - `.claude/skills/plan-plugin-findings/SKILL.md:105`

Excerpt:

```text

Apply filters in this order:

1. surface
2. dimension
3. object-type routing (`--skills` or `--agents`)
4. finding-type routing

```

### 34. 8 lines, 2 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/agents/al-dev-al-pattern-reviewer.md:83`
  - `profile-al-dev-shared/agents/al-dev-performance-reviewer.md:64`

Excerpt:

```text

## Output Format

Use the canonical findings format and severity scale from
`knowledge/reviewer-findings-template.md`. Each finding must include:
File + Line, Severity, Issue, Impact, Fix — in the table format shown there.

When other reviewers' findings are included, structure as independent findings; the lead agent will synthesize.
```

### 35. 8 lines, 2 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/agents/al-dev-developer-tdd.md:23`
  - `profile-al-dev-shared/agents/al-dev-developer-traditional.md:21`

Excerpt:

```text

## Inputs

Callers do not pass these paths explicitly. The agent auto-locates the latest matching files in `.dev/` by glob before implementation begins. When multiple files match, select the most recent by modification time (`ls -t <glob> | head -1`).

| Input | Required | Description |
|-------|----------|-------------|
| `.dev/*-al-dev-plan-solution-plan.md` | **Yes** | Latest implementation plan, auto-located by glob |
```

### 36. 8 lines, 2 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/knowledge/al-dev-plan-phase-routing.md:13`
  - `profile-al-dev-shared/skills/al-dev-plan-preflight/SKILL.md:136`

Excerpt:

```text

| Signal | SIMPLE | MEDIUM / COMPLEX |
| --- | --- | --- |
| Estimated file count | ≤ 3 | 4+ or unclear |
| Pattern in codebase (if known) | Yes | No / unclear |
| New architecture needed | No | Yes |
| Requirements ambiguous | No | Yes |

```

### 37. 8 lines, 3 occurrences

- Scope: within one file
- Locations:
  - `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml:4`
  - `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml:15`
  - `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml:46`

Excerpt:

```text
    status: golden
    user_prompt: "Commit the staged changes."
    expected_artifacts: []
    must_invoke_agent:
      - al-dev-shared:al-dev-commit-analyzer
      - al-dev-shared:al-dev-commit-lint-fixer
      - al-dev-shared:al-dev-commit-ooxml-validator
      - al-dev-shared:al-dev-commit-executor
```

### 38. 8 lines, 2 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md:54`
  - `profile-al-dev-shared/skills/al-dev-plan-preflight/SKILL.md:241`

Excerpt:

```text
2. **Validate match:**

   ```text
   > **Target check:**
   > - Findings reference: [extracted from findings]
   > - Your request: [extracted from your message]
   > - Output path: [absolute path where work will land]
   >
```

## Exclusions

- archived: 53
- generated: 73
