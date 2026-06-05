# Commit Workflow Orchestration

The six-agent commit dispatch is the standard sequential execution contract
used by `/al-dev-commit`. Each phase dispatches one agent; the output of each
phase feeds the next. Changing any phase prompt template requires checking all
six templates for consistency.

## Agent Sequence

The six agents are dispatched in strict sequential order:

| Phase | Agent | Role |
|---|---|---|
| 1.1 | `al-dev-shared:al-dev-commit-analyzer` | Extract file manifests and deletion list from staged changes |
| 1.3 | `al-dev-shared:al-dev-commit-message-drafter` | Draft commit messages and propose file groupings |
| 3.1 | `al-dev-shared:al-dev-commit-lint-fixer` | Run lint preflight and fix trailing whitespace |
| 3.2 | `al-dev-shared:al-dev-commit-ooxml-validator` | Validate OOXML ZIP integrity for `.docx` files |
| 4.1 | `al-dev-shared:al-dev-commit-agent-execute` | Execute approved commits via `git` |
| 4.3 | `al-dev-shared:al-dev-commit-hook-fixer` | Diagnose and recover from pre-commit hook failures (error path only) |

Phase 4.3 (`al-dev-commit-hook-fixer`) is conditional — it is dispatched only
when `al-dev-commit-agent-execute` returns a non-`NONE` `HOOK_FAILURES` block.

## Phase Flow

```text
Phase 0  Setup & Validation (orchestrator only — no agent dispatch)
  │
  ▼
Phase 1.1  al-dev-commit-analyzer
  │  Output: MANIFESTS block, DELETIONS block, WARNINGS block
  ▼
Phase 1.2  Deletion Audit Gate (USER_GATE — orchestrator only)
  │
  ▼
Phase 1.3  al-dev-commit-message-drafter
  │  Input: MANIFESTS from Phase 1.1
  │  Output: PROPOSED_GROUPS block
  ▼
Phase 2  Confirmation (USER_GATE — orchestrator only)
  │  Output: approved plan (groups, files, messages)
  ▼
Phase 3.1  al-dev-commit-lint-fixer
  │  Input: approved plan from Phase 2
  │  Output: LINT_FIXES
  ▼
Phase 3.2  al-dev-commit-ooxml-validator
  │  Input: approved plan from Phase 2
  │  Output: OOXML_FAILURES
  ▼
Phase 4.1  al-dev-commit-agent-execute
  │  Input: approved plan from Phase 2
  │  Output: COMMITS, SKIPPED, HOOK_FAILURES
  ▼
Phase 4.2  Branch on HOOK_FAILURES
  │
  ├─ HOOK_FAILURES == NONE ──────────────────────► Phase 4.4 Summary
  │
  └─ HOOK_FAILURES != NONE
       │
       ▼
     Phase 4.3  al-dev-commit-hook-fixer
       │  Input: .dev/hook-failures.json, .dev/commits.json
       │  Output: HOOK_FAILURES block with recovery_status, next_step
       │
       ├─ ready-to-retry  ──────────────────────► re-dispatch Phase 4.1
       ├─ needs-manual-intervention  ──────────► surface to user, stop
       └─ non-recoverable  ─────────────────────► abort, report to user

Phase 4.4  Summary (orchestrator only — no agent dispatch)
```

## Shared Dispatch-Prompt Contract

Every agent dispatch in this workflow shares three structural elements.

### 1 — Phase label

Each prompt opens with a `Phase:` declaration so the agent knows where it sits
in the workflow:

```text
Phase: analysis          # Phase 1.1
Phase: message-drafting  # Phase 1.3
Phase: lint-preflight    # Phase 3.1 (implicit in agent instructions)
Phase: ooxml-validate    # Phase 3.2 (implicit in agent instructions)
Phase: execute           # Phase 4.1
```

`al-dev-commit-hook-fixer` does not use a phase label — it receives structured
JSON inputs via file references instead.

### 2 — Context block

Phases 1.1, 1.3, and 4.1 receive a `PROJECT_CONTEXT` block carrying the values
loaded in Phase 0:

```text
PROJECT_CONTEXT:
- Valid scopes: [list from Phase 0.2]
- Object ID prefix: [from Phase 0.2]
- AL naming pattern: [from Phase 0.2]
- Gitmoji style: [from Phase 0.7]

FD_TICKET: [ticket number from Phase 0.2.1, or empty]
```

Phases 3.1 and 3.2 do not repeat the project context — they receive the
approved plan directly and operate independently of project-level metadata.

### 3 — Prior-phase output pass-through

Each agent receives the outputs it needs from the preceding step. The
orchestrator pastes these verbatim — never summarizes or transforms them:

| Receiving agent | Prior-phase output passed in |
|---|---|
| `al-dev-commit-message-drafter` (1.3) | `MANIFESTS` block from Phase 1.1 |
| `al-dev-commit-lint-fixer` (3.1) | `APPROVED_PLAN` from Phase 2 |
| `al-dev-commit-ooxml-validator` (3.2) | `APPROVED_PLAN` from Phase 2 |
| `al-dev-commit-agent-execute` (4.1) | `APPROVED_PLAN` from Phase 2 |
| `al-dev-commit-hook-fixer` (4.3) | `.dev/hook-failures.json`, `.dev/commits.json`; `HOOK_FAILURES` inline fallback |

## Per-Agent Verification Checklist

Each agent prompt includes a `CRITICAL RULES` or equivalent section. When
changing a phase's prompt template, verify that the following constraints
remain present:

**All agents:**

- Return output in exactly the format specified — the orchestrator parses the
  named output blocks (`MANIFESTS`, `PROPOSED_GROUPS`, `LINT_FIXES`,
  `OOXML_FAILURES`, `COMMITS`, `SKIPPED`, `HOOK_FAILURES`)
- No free-form narrative in output blocks — structured format only

**`al-dev-commit-lint-fixer` (Phase 3.1) — additional rules:**

- Never use Write or Edit on staged source files — all fixes via shell commands
  only
- Skip binary and OOXML files in the trailing-whitespace step
- Stop immediately if line-count collapse detected (corruption signal)

**`al-dev-commit-agent-execute` (Phase 4.1) — additional rules:**

- Never add `Co-Authored-By` trailers to commit messages
- Use `git -C <path>` instead of `cd <path> && git`
- Verify file integrity (`wc -l`) for all modified files after commits

**`al-dev-commit-hook-fixer` (Phase 4.3) — additional rules:**

- Apply only scripted fixes; escalate anything requiring manual intervention
- Re-stage fixed files before returning `ready-to-retry`
- `recovery_status` must be one of: `ready-to-retry`, `needs-manual-intervention`,
  `non-recoverable`

## Strong-Coupling Note

All six agents share a single structured output vocabulary (`MANIFESTS`,
`PROPOSED_GROUPS`, `LINT_FIXES`, `OOXML_FAILURES`, `COMMITS`, `SKIPPED`,
`HOOK_FAILURES`). The orchestrator (`al-dev-commit/SKILL.md`) parses these
blocks by name without transformation.

**If you rename or restructure a block in one agent, update all of the following:**

1. The producing agent's output format instructions
2. The consuming agent's input instructions (if it receives that block)
3. The orchestrator's parse and display logic in `SKILL.md`
4. This document's dispatch contract tables

Do not change block names in isolation — the parse failure is silent (the
orchestrator will display empty or malformed output rather than raising an
error).

## Adding a Seventh Agent

If a new commit phase is added (e.g., a signature-verification agent):

1. Add a row to the Agent Sequence table above with the phase number and role.
2. Add the new node to the Phase Flow diagram with its input/output labels.
3. Document its dispatch-prompt contract in the Shared Dispatch-Prompt Contract
   section — especially what prior-phase output it receives and what it returns.
4. Add its verification checklist to Per-Agent Verification Checklist.
5. Update the Strong-Coupling Note if the new agent introduces new output blocks.
6. Add the dispatch block to `al-dev-commit/SKILL.md` in the correct phase.

This checklist mirrors the "Adding a Fourth Reviewer" pattern in
`knowledge/review-panel-pattern.md`.
