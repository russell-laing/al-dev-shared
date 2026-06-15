# Duplicate Text Report

**Date:** 2026-06-15

## Scan Configuration

- Inputs: `.claude`, `profile-al-dev-shared`
- Minimum duplicate length: 8 lines
- Minimum nonblank lines: 4
- Minimum characters: 80
- Include archived content: no
- Include generated content: no
- Text files scanned: 216
- Files excluded: 133

Trailing whitespace and line endings are normalized. Other text remains exact.

## Summary

Found 50 grouped duplicate blocks.

Generated and archived matches are excluded by default because they are often
intentional. Each finding still requires human review before refactoring.

## Findings

### 1. 29 lines, 2 occurrences

- Scope: within one file
- Locations:
  - `profile-al-dev-shared/knowledge/al-dev-develop-spawn-prompt.md:66`
  - `profile-al-dev-shared/knowledge/al-dev-develop-spawn-prompt.md:126`

Excerpt:

```text

SYMBOL_PREFLIGHT_GATE — Complete BEFORE writing any AL code.
Follow `knowledge/al-symbol-pre-flight.md` for the full checklist; that
file is the authoritative source. Use the strongest available evidence
source and label every item as `AL LSP`, `AL MCP`, `text search`, or
`unverified`.

Symbol evidence collected during planning:
- [Verified signatures / fields / events from planning, with sources]
- [Any optional unverified item: do NOT guess; STOP and report if needed]

Report your pre-flight summary before writing a single line of AL.
```

### 2. 22 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/sync-documentation-maps-agent-update.md:27`
  - `.claude/agents/sync-documentation-maps-skill-update.md:27`

Excerpt:

```text
Returns absolute path only — no other prose.

---

## Instructions

All relative paths in these instructions are from the repository root:
`/Users/russelllaing/al-dev-shared`. Adjust paths if the working directory differs.

Verify `.claude/knowledge/sync-map-update-shared.md` exists before following it;
if it is absent, stop and emit:

```

### 3. 19 lines, 2 occurrences

- Scope: within one file
- Locations:
  - `profile-al-dev-shared/knowledge/tdd-workflow.md:993`
  - `profile-al-dev-shared/knowledge/tdd-workflow.md:1067`

Excerpt:

```text
        exit(Outstanding + OrderAmount <= Customer."Credit Limit (LCY)");
    end;

    local procedure GetOutstandingAmount(CustomerNo: Code[20]): Decimal
    var
        SalesHeader: Record "Sales Header";
        Outstanding: Decimal;
    begin
        SalesHeader.SetRange("Sell-to Customer No.", CustomerNo);
        SalesHeader.SetFilter(Status, '<>%1', SalesHeader.Status::Released);
        if SalesHeader.FindSet() then
            repeat
```

### 4. 16 lines, 5 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/design-agent-lens-scope-isolation.md:4`
  - `.claude/agents/quality-agent-lens-bloat.md:4`
  - `.claude/agents/quality-agent-lens-description.md:4`
  - `.claude/agents/quality-agent-lens-name-fit.md:4`
  - `.claude/agents/quality-agent-lens-structure.md:4`

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

### 5. 16 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/quality-agent-lens-clarity.md:60`
  - `.claude/agents/quality-skill-lens-clarity.md:59`

Excerpt:

```text
- Steps that reference undefined placeholders or variables

**Severity rules:**

- High: ambiguity that changes observable behavior
- Medium: vague qualifiers with no definition
- Low: minor style issues

---

## Output Format

```

### 6. 16 lines, 3 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/quality-skill-lens-description.md:4`
  - `.claude/agents/quality-skill-lens-name-fit.md:4`
  - `.claude/agents/quality-skill-lens-structure.md:4`

Excerpt:

```text
model: haiku
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |

## Outputs

```

### 7. 14 lines, 4 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/quality-skill-lens-clarity.md:4`
  - `.claude/agents/quality-skill-lens-description.md:4`
  - `.claude/agents/quality-skill-lens-name-fit.md:4`
  - `.claude/agents/quality-skill-lens-structure.md:4`

Excerpt:

```text
model: haiku
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |

## Outputs

```

### 8. 13 lines, 2 occurrences

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

### 9. 12 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/quality-agent-lens-bloat.md:52`
  - `.claude/agents/quality-skill-lens-bloat.md:54`

Excerpt:

```text
  repetitive, dead, or extractable (not merely long inherent content)
- Medium: dead branches or repetitive instruction blocks
- Low: minor historical commentary

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Bloat Findings

```

### 10. 12 lines, 2 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/agents/al-dev-developer-tdd.md:77`
  - `profile-al-dev-shared/agents/al-dev-developer-traditional.md:60`

Excerpt:

```text

## Standards

### AL Code Patterns

See `knowledge/al-symbol-pre-flight.md` for the pre-flight checklist and
tool selection guidance (`AL LSP` → `AL MCP` → text search; stop on
`unverified`). See `knowledge/al-developer-patterns.md` for AL patterns,
error handling, naming conventions, and performance rules.

### Compilation

```

### 11. 12 lines, 2 occurrences

- Scope: within one file
- Locations:
  - `profile-al-dev-shared/knowledge/ticket-agent-invocation-pattern.md:134`
  - `profile-al-dev-shared/knowledge/ticket-agent-invocation-pattern.md:166`

Excerpt:

````text

```text
Agent invocation (Skill tool):
  skill: al-dev-ticket-context-writer
  args: "TICKET_ID=12345"

This internally dispatches:
  agent: al-dev-shared:al-dev-ticket-context-writer
  with environment: FRESHDESK_API_KEY, FRESHDESK_DOMAIN
  with prompt: "Fetch Freshdesk ticket and write .dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md. Phase: fetch. Ticket ID: 12345"
```

````

### 12. 12 lines, 3 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/skills/al-dev-develop/validate-code-review.py:6`
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

### 13. 11 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/sync-documentation-maps-agent-discrepancy.md:80`
  - `.claude/agents/sync-documentation-maps-skill-discrepancy.md:84`

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

### 14. 11 lines, 2 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/agents/al-dev-commit-lint-fixer.md:16`
  - `profile-al-dev-shared/agents/al-dev-commit-ooxml-validator.md:15`

Excerpt:

```text

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `APPROVED_PLAN` (inline text block) — approved groups from analysis phase (GROUP_N structured blocks with `files:` and `message:` fields) |

## Outputs

| Output | Description |
|--------|-------------|
```

### 15. 11 lines, 2 occurrences

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

### 16. 11 lines, 2 occurrences

- Scope: within one file
- Locations:
  - `profile-al-dev-shared/knowledge/al-dev-develop-spawn-prompt.md:54`
  - `profile-al-dev-shared/knowledge/al-dev-develop-spawn-prompt.md:116`

Excerpt:

```text

Implement [module name] from the latest solution plan
(.dev/*-al-dev-plan-solution-plan.md).

Your assigned objects:
- [Object list from the Phase 2 partition]

Object IDs: [assigned range from plan]
Naming prefix: [from plan or project-context.md]
Project patterns: [from project-context.md if available]

```

### 17. 11 lines, 3 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/skills/al-dev-develop/validate-code-review.py:45`
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

### 18. 11 lines, 3 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/skills/al-dev-develop/validate-code-review.py:55`
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

### 19. 10 lines, 6 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/design-agent-lens-scope-isolation.md:4`
  - `.claude/agents/quality-agent-lens-bloat.md:4`
  - `.claude/agents/quality-agent-lens-clarity.md:4`
  - `.claude/agents/quality-agent-lens-description.md:4`
  - `.claude/agents/quality-agent-lens-name-fit.md:4`
  - `.claude/agents/quality-agent-lens-structure.md:4`

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

### 20. 10 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/quality-agent-lens-bloat.md:13`
  - `.claude/agents/quality-skill-lens-bloat.md:15`

Excerpt:

```text

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Bloat

Read every file path provided in the dispatch prompt. For each file, derive the
```

### 21. 10 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/quality-agent-lens-description.md:13`
  - `.claude/agents/quality-skill-lens-description.md:13`

Excerpt:

```text

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Description Drift

Read every file path provided in the dispatch prompt. For each file, derive the
```

### 22. 10 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/quality-agent-lens-name-fit.md:13`
  - `.claude/agents/quality-skill-lens-name-fit.md:13`

Excerpt:

```text

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Name Fit

Read every file path provided in the dispatch prompt. For each file, derive the
```

### 23. 10 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/quality-agent-lens-structure.md:13`
  - `.claude/agents/quality-skill-lens-structure.md:13`

Excerpt:

```text

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Structural Conventions

Read every file path provided in the dispatch prompt. For each file, derive the
```

### 24. 10 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/quality-agent-lens-structure.md:68`
  - `.claude/agents/quality-skill-lens-structure.md:44`

Excerpt:

```text
- Low: numbering inconsistency or missing code block language tags

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Structural Conventions Findings

```

### 25. 10 lines, 5 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/quality-skill-lens-bloat.md:4`
  - `.claude/agents/quality-skill-lens-clarity.md:4`
  - `.claude/agents/quality-skill-lens-description.md:4`
  - `.claude/agents/quality-skill-lens-name-fit.md:4`
  - `.claude/agents/quality-skill-lens-structure.md:4`

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

### 26. 10 lines, 4 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/sync-documentation-maps-agent-metadata.md:13`
  - `.claude/agents/sync-documentation-maps-agent-update.md:15`
  - `.claude/agents/sync-documentation-maps-skill-metadata.md:14`
  - `.claude/agents/sync-documentation-maps-skill-update.md:15`

Excerpt:

```text

## Inputs

| Field | Description |
|---|---|
| run_id | The timestamp run ID (e.g. `20260531T143000`) |
| result_dir | Absolute path to `.dev/sync-documentation-maps-runs/<run_id>/` |

## Outputs

```

### 27. 10 lines, 2 occurrences

- Scope: within one file
- Locations:
  - `profile-al-dev-shared/knowledge/al-dev-develop-spawn-prompt.md:97`
  - `profile-al-dev-shared/knowledge/al-dev-develop-spawn-prompt.md:157`

Excerpt:

```text

IMPORTANT: Do NOT run git commit. Your role is to implement and verify
compilation only. Commits are handled separately by /al-dev-commit after
user approval.

Expected Output:
- All assigned objects implemented per the plan and patterns
- Pre-flight summary reported before code was written
- Compilation verified for the assigned module
- Any out-of-scope proposals surfaced through the Scope Expansion Gate
```

### 28. 10 lines, 2 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/knowledge/compile-lint-procedure.md:72`
  - `profile-al-dev-shared/skills/al-dev-lint/SKILL.md:52`

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

### 29. 9 lines, 9 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/design-agent-lens-model-fit.md:4`
  - `.claude/agents/design-agent-lens-scope-isolation.md:4`
  - `.claude/agents/design-agent-lens-tool-hygiene.md:4`
  - `.claude/agents/design-agent-lens-usage-patterns.md:4`
  - `.claude/agents/quality-agent-lens-bloat.md:4`
  - `.claude/agents/quality-agent-lens-clarity.md:4`
  - `.claude/agents/quality-agent-lens-description.md:4`
  - `.claude/agents/quality-agent-lens-name-fit.md:4`
  - `.claude/agents/quality-agent-lens-structure.md:4`

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

### 30. 9 lines, 7 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/design-skill-lens-complexity.md:4`
  - `.claude/agents/design-skill-lens-preplanning.md:4`
  - `.claude/agents/quality-skill-lens-bloat.md:4`
  - `.claude/agents/quality-skill-lens-clarity.md:4`
  - `.claude/agents/quality-skill-lens-description.md:4`
  - `.claude/agents/quality-skill-lens-name-fit.md:4`
  - `.claude/agents/quality-skill-lens-structure.md:4`

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

### 31. 9 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/quality-agent-lens-clarity.md:24`
  - `.claude/agents/quality-skill-lens-clarity.md:24`

Excerpt:

```text
  define the term or supply the missing `else` branch. If the term is defined,
  enumerated, or disambiguated anywhere in the same file, do **not** flag it.
- If the text defers definition to a named repo doc (e.g. "see
  `knowledge/foo.md`") and that relative path resolves, Read it; if the term is
  defined there, do **not** flag it.

Flag only what stays unresolved after both checks. Resolving a term elsewhere is
not a miss — genuine ambiguity (undefined everywhere) still fires.

```

### 32. 9 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/quality-agent-lens-description.md:41`
  - `.claude/agents/quality-skill-lens-description.md:37`

Excerpt:

```text
- Low: minor verb mismatch that does not affect behavior

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Description Drift Findings
```

### 33. 9 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/quality-agent-lens-name-fit.md:36`
  - `.claude/agents/quality-skill-lens-name-fit.md:37`

Excerpt:

```text
- Low: minor verb mismatch with no behavioral consequence

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Name Fit Findings
```

### 34. 9 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/sync-documentation-maps-agent-discrepancy.md:27`
  - `.claude/agents/sync-documentation-maps-agent-metadata.md:24`

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

### 35. 9 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/sync-documentation-maps-agent-discrepancy.md:50`
  - `.claude/agents/sync-documentation-maps-skill-discrepancy.md:50`

Excerpt:

```text

---

## Instructions

All relative paths are from the repository root: `/Users/russelllaing/al-dev-shared`.

### Step 1 — Load metadata

```

### 36. 9 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/sync-documentation-maps-skill-discrepancy.md:27`
  - `.claude/agents/sync-documentation-maps-skill-metadata.md:25`

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

### 37. 9 lines, 2 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/agents/al-dev-developer-tdd.md:32`
  - `profile-al-dev-shared/agents/al-dev-developer-traditional.md:29`

Excerpt:

```text
| `.dev/project-context.md` | No | Project memory and conventions, read when present |
| `.dev/*-al-dev-develop-code-review.md` | No | Latest review findings for iteration, auto-located by glob when present |
| Inline dispatch context | **Yes** | Module scope, assigned object ID range, naming prefix, and pre-verified symbol evidence — passed inline in the dispatch prompt by `/al-dev-develop`. See `knowledge/al-dev-develop-spawn-prompt.md` for the canonical context-field list. |

## Outputs

| Output | Description |
|--------|-------------|
| AL source files | Implemented code in `src/` |
```

### 38. 8 lines, 8 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/design-skill-lens-complexity.md:5`
  - `.claude/agents/design-skill-lens-preplanning.md:5`
  - `.claude/agents/design-skill-lens-shared-backbone.md:5`
  - `.claude/agents/quality-skill-lens-bloat.md:5`
  - `.claude/agents/quality-skill-lens-clarity.md:5`
  - `.claude/agents/quality-skill-lens-description.md:5`
  - `.claude/agents/quality-skill-lens-name-fit.md:5`
  - `.claude/agents/quality-skill-lens-structure.md:5`

Excerpt:

```text
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |
```

### 39. 8 lines, 6 occurrences

- Scope: across files
- Locations:
  - `.claude/agents/sync-documentation-maps-agent-discrepancy.md:13`
  - `.claude/agents/sync-documentation-maps-agent-metadata.md:13`
  - `.claude/agents/sync-documentation-maps-agent-update.md:15`
  - `.claude/agents/sync-documentation-maps-skill-discrepancy.md:13`
  - `.claude/agents/sync-documentation-maps-skill-metadata.md:14`
  - `.claude/agents/sync-documentation-maps-skill-update.md:15`

Excerpt:

```text

## Inputs

| Field | Description |
|---|---|
| run_id | The timestamp run ID (e.g. `20260531T143000`) |
| result_dir | Absolute path to `.dev/sync-documentation-maps-runs/<run_id>/` |

```

### 40. 8 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/hooks/post_edit_validate.py:1`
  - `.claude/hooks/stop_projection_check.py:1`

Excerpt:

```text
#!/usr/bin/env python3
import sys
import json
import subprocess
import os

try:
    event = json.load(sys.stdin)
```

### 41. 8 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/knowledge/health-audit-preconditions.md:59`
  - `.claude/skills/implement-health-plan/SKILL.md:359`

Excerpt:

````text

```bash
python3 scripts/select_health_artifacts.py \
  --directory docs/health \
  --kind health \
  --surface <surface>
```

````

### 42. 8 lines, 2 occurrences

- Scope: across files
- Locations:
  - `.claude/knowledge/health-filter-contract.md:121`
  - `.claude/skills/plan-health-findings/SKILL.md:85`

Excerpt:

```text

Apply filters in this order:

1. surface
2. dimension
3. object-type routing (`--skills` or `--agents`)
4. finding-type routing

```

### 43. 8 lines, 2 occurrences

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

### 44. 8 lines, 2 occurrences

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

### 45. 8 lines, 2 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/agents/al-dev-developer-tdd.md:92`
  - `profile-al-dev-shared/agents/al-dev-developer-traditional.md:74`

Excerpt:

```text

### Compile Output — Critical Safeguard

See `knowledge/compile-output-safeguard.md`.

## Governance Tokens

| Token | Gate | Action |
```

### 46. 8 lines, 2 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/knowledge/al-dev-plan-phase-routing.md:13`
  - `profile-al-dev-shared/skills/al-dev-plan-preflight/SKILL.md:117`

Excerpt:

```text

| Signal | SIMPLE | MEDIUM / COMPLEX |
| --- | --- | --- |
| Estimated file count | ≤ 3 | 4+ or unclear |
| Pattern in codebase (if known) | Yes | No / unclear |
| New architecture needed | No | Yes |
| Requirements ambiguous | No | Yes |

```

### 47. 8 lines, 2 occurrences

- Scope: within one file
- Locations:
  - `profile-al-dev-shared/knowledge/tdd-workflow.md:65`
  - `profile-al-dev-shared/knowledge/tdd-workflow.md:148`

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

### 48. 8 lines, 3 occurrences

- Scope: within one file
- Locations:
  - `profile-al-dev-shared/knowledge/tdd-workflow.md:81`
  - `profile-al-dev-shared/knowledge/tdd-workflow.md:175`
  - `profile-al-dev-shared/knowledge/tdd-workflow.md:271`

Excerpt:

````text
   ```bash
   # Compile the app
   al-compile

   # Publish to BC server
   bc-publish
   ```

````

### 49. 8 lines, 3 occurrences

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

### 50. 8 lines, 2 occurrences

- Scope: across files
- Locations:
  - `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md:48`
  - `profile-al-dev-shared/skills/al-dev-plan-preflight/SKILL.md:215`

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

- .DS_Store: 6
- archived: 40
- cache: 14
- generated: 73
