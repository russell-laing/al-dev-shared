# Archive Test-Related Skills and Agents

**Date:** 2026-05-16
**Status:** Ready for implementation
**Scope:** `profile-al-dev-shared/` only

## Goal

Move all test-related skills and agents out of the active plugin directories into an
`archived/` holding area. The plugin should no longer surface `/al-dev-test` or spawn
any test-engineer agents. All files must be recoverable intact.

## What Gets Archived

### Skill (full directory)

| Source path | Archive path |
|-------------|--------------|
| `profile-al-dev-shared/skills/al-dev-test/` | `profile-al-dev-shared/archived/skills/al-dev-test/` |

Includes `SKILL.md` and `validate-test-plan.py`.

### Agents (individual files)

| Source path | Archive path |
|-------------|--------------|
| `agents/al-dev-unit-test-engineer.md` | `archived/agents/al-dev-unit-test-engineer.md` |
| `agents/al-dev-integration-test-engineer.md` | `archived/agents/al-dev-integration-test-engineer.md` |
| `agents/al-dev-scenario-test-engineer.md` | `archived/agents/al-dev-scenario-test-engineer.md` |
| `agents/al-dev-edge-case-test-engineer.md` | `archived/agents/al-dev-edge-case-test-engineer.md` |
| `agents/al-dev-test-coverage-reviewer.md` | `archived/agents/al-dev-test-coverage-reviewer.md` |

All paths above are relative to `profile-al-dev-shared/`.

> **Note on `al-dev-test-coverage-reviewer`:** This agent is used by `/al-dev-develop`
> and `/al-dev-autonomous` as one of their 4 parallel code reviewers. Archiving it
> reduces both skills to a 3-reviewer panel. The edits required are described below.

## Archive Directory Structure

Create the following layout via `git mv`:

```
profile-al-dev-shared/
  archived/
    README.md            ← created new (see below)
    skills/
      al-dev-test/
        SKILL.md
        validate-test-plan.py
    agents/
      al-dev-unit-test-engineer.md
      al-dev-integration-test-engineer.md
      al-dev-scenario-test-engineer.md
      al-dev-edge-case-test-engineer.md
      al-dev-test-coverage-reviewer.md
```

Use `git mv` for all moves so history is preserved.

### archived/README.md content

```markdown
# Archived Skills and Agents

Files here are inactive — not loaded by the plugin. Move them back to
`skills/` or `agents/` to reinstate.

## What is here

| Item | Type | Archived reason |
|------|------|-----------------|
| `skills/al-dev-test/` | Skill | Test codeunit workflow not yet in use |
| `agents/al-dev-unit-test-engineer.md` | Agent | Spawned by al-dev-test |
| `agents/al-dev-integration-test-engineer.md` | Agent | Spawned by al-dev-test |
| `agents/al-dev-scenario-test-engineer.md` | Agent | Spawned by al-dev-test |
| `agents/al-dev-edge-case-test-engineer.md` | Agent | Spawned by al-dev-test |
| `agents/al-dev-test-coverage-reviewer.md` | Agent | Spawned by al-dev-develop/al-dev-autonomous |

## Reinstatement steps

1. `git mv archived/skills/al-dev-test skills/al-dev-test`
2. `git mv archived/agents/al-dev-unit-test-engineer.md agents/`
3. `git mv archived/agents/al-dev-integration-test-engineer.md agents/`
4. `git mv archived/agents/al-dev-scenario-test-engineer.md agents/`
5. `git mv archived/agents/al-dev-edge-case-test-engineer.md agents/`
6. `git mv archived/agents/al-dev-test-coverage-reviewer.md agents/`
7. Revert all edits described in the spec:
   `docs/superpowers/specs/2026-05-16-archive-test-skills-design.md`
```

## Required Edits to Active Skills

### 1. `skills/al-dev-develop/SKILL.md`

**Frontmatter description** — change:
```
4-specialist review (security, AL expert, performance, test coverage)
```
to:
```
3-specialist review (security, AL expert, performance)
```

**Phase 5 reviewer block** — remove the entire `al-dev-test-coverage-reviewer`
paragraph (currently at line ~143). The block reads:

```
**al-dev-test-coverage-reviewer:**
Review for testability (dependency injection present?),
interfaces for mocking, event extensibility, test scenario
coverage. Compare to the latest solution plan
(.dev/*-al-dev-plan-solution-plan.md) testability
requirements.
```

After removal, Phase 5 should list only 3 reviewers:
`al-dev-code-review`, `al-dev-expert-reviewer`, `al-dev-performance-reviewer`.

Also update any Phase 5 header or preamble that says "4 reviewers" or "4-specialist"
to say "3 reviewers" / "3-specialist".

---

### 2. `skills/al-dev-autonomous/SKILL.md`

Same change as above. Remove the `al-dev-test-coverage-reviewer` paragraph
(currently at line ~311):

```
**al-dev-test-coverage-reviewer:** Review for testability,
interfaces for mocking, event extensibility, test scenario
coverage vs solution plan.
```

Update any "4 reviewers" / "4-specialist" references in the same section to "3".

---

### 3. `skills/al-dev-help/SKILL.md`

Remove all references to test-related items. Specifically:

- Remove the `/al-dev-test` row from any workflow tables
  (currently at lines 63 and 80).
- Remove the 5 test-agent rows from the agent catalogue table
  (currently at lines 106–110: `test-coverage-reviewer`,
  `unit-test-engineer`, `integration-test-engineer`,
  `scenario-test-engineer`, `edge-case-test-engineer`).
- Remove any conditional suggestions that say "run `/al-dev-test`
  if coverage matters" or similar (lines ~138, ~163, ~200, ~228).
- Remove `05-test-plan.md` from the `.dev/` artifact list (line ~152).

Do not remove references to the word "test" in general explanatory prose
— only remove rows/suggestions that point to the archived skill or agents.

---

### 4. `skills/al-dev-document/SKILL.md`

- Remove `05-test-plan.md` as a state-detection input (lines ~87, ~92, ~113).
- Remove the sentence that tells the user to run `/al-dev-test` (line ~353).
- Do not change prose that uses the word "test" in a general sense.

---

## Verification

After all moves and edits, verify:

1. `ls profile-al-dev-shared/skills/` — `al-dev-test` must not appear.
2. `ls profile-al-dev-shared/agents/` — none of the 5 archived agent files appear.
3. `grep -r "al-dev-test\|test-coverage-reviewer\|test-engineer" profile-al-dev-shared/skills/ --include="*.md"` — no matches in any **active** skill file except benign prose uses of the word "test".
4. `ls profile-al-dev-shared/archived/skills/al-dev-test/` — `SKILL.md` and `validate-test-plan.py` both present.
5. `ls profile-al-dev-shared/archived/agents/` — all 5 agent files present.
6. `git status` shows only expected moves and edits — no unexpected deletions.

## Commit Message

```
chore(al-dev-shared): archive test skill and test-engineer agents

Move al-dev-test skill and 5 test-related agents to
profile-al-dev-shared/archived/ to reduce active plugin surface
while AL test codeunit workflow is not in use. Files are preserved
intact for future reinstatement.

Update al-dev-develop, al-dev-autonomous, al-dev-help, and
al-dev-document to remove references to archived items.
```
