---
name: skill-description-validator
description: Rules and usage for validate_skill_descriptions.py hardening validator
---

# Skill Description Validator

## Overview

`scripts/validate_skill_descriptions.py` enforces rules around skill description frontmatter to prevent workflow-summary bloat and phase-enumeration drift. Descriptions should describe **when to use** (trigger conditions) and **purpose only**; implementation mechanics belong in the skill body where agents will read them instead of shortcutting on the description.

## Why This Matters

Testing by Anthropic showed that when a description summarizes workflow/phases, agents follow the shortcut description instead of reading the full skill body. A description saying "code review between tasks" caused an agent to do ONE review, even though the skill's flowchart showed TWO reviews (spec compliance + code quality). When the description was changed to just triggering conditions, the agent correctly read the flowchart and followed both stages.

**Reference:** `writing-skills` convention, "Rich Description Field" section.

## Rules

### HIGH-severity (Blocking for maintainer skills)

**Phase Enumeration**

- Triggers: "Phase 1", "Phase 2.5", "phase 4-5", "first phase", "second phase"
- Anti-pattern: "Phase 1-3 verification portion of health-finding planning"
- Fix: Remove all phase labels. Describe purpose: "Verify findings from the latest dossier..."

**Constraint Language**

- Triggers: "Single-concern pipeline", "No separable concerns", "Each phase depends on", "Mandatory X gate"
- Anti-pattern: "Single-concern validation pipeline: runs validator script, parses... No separable concerns; each phase depends on the previous phase's output."
- Fix: Move design rationale to skill body. Trim description to purpose + scope: "Apply Harness Neutrality lens to knowledge files — finds harness-specific tokens that should be generic. Scoped to a single file or recursive directory."

### MEDIUM-severity (Warning for both surfaces)

**Implementation Detail**

- Triggers: "appends JSONL", "through scripts/", "syncs shard", "syncs ledger"
- Anti-pattern: "appends `fixed` events to the JSONL event store for every **verified** `closes_event_ids:` entry"
- Fix: Abstract to purpose. "Closes the health-audit loop by executing an accepted implementation plan and appending verified fixed events to the ledger."

**Word-Count Violations**

- Distributed skills: >50 words (~200 chars)
- Maintainer skills: >80 words (~350 chars)
- Trigger: Description exceeds limit
- Fix: Trim to purpose + trigger conditions; move examples and mechanics to body

## Usage

### Run standalone

```bash
python3 scripts/validate_skill_descriptions.py
```

### Run with strict mode (includes word-count flags)

```bash
python3 scripts/validate_skill_descriptions.py --strict
```

### Pre-commit integration

The validator runs automatically at commit time (warning-only gate, non-blocking). Violations are printed but do not prevent commit. To block on violations (e.g., in a CI pipeline), use the exit code:

```bash
python3 scripts/validate_skill_descriptions.py
if [ $? -ne 0 ]; then
  echo "Fix violations and re-commit."
  exit 1
fi
```

## Current Status

**Maintainer skills** (.claude/skills/):

- ✓ All 21 active skills pass validation
- Bloat trimmed in commit 13baf18e (16 skills)

**Distributed skills** (profile-al-dev-shared/skills/):

- ⚠ 4 skills have HIGH phase-enumeration violations (out of scope for current pass)
  - develop-orchestrate, plan, plan-final-review, support-reply
- Planned fix: separate development-flow refactor pass

## Rules Maintenance

To add or adjust rules, edit the `RULES` dict in `validate_skill_descriptions.py`:

```python
RULES = {
    "rule_name": {
        "patterns": [r"regex1", r"regex2"],
        "severity": "HIGH|MEDIUM|LOW",
        "reason": "Why this matters...",
        "fix": "How to fix it...",
    },
    ...
}
```

Patterns are matched case-insensitively. One match per rule per description (stops after first match).

## Integration with Writing Conventions

This validator enforces the `writing-skills` convention for the al-dev-shared plugin:

| Document | Link |
|----------|------|
| writing-skills (Superpowers) | "Rich Description Field" section |
| Repo house style | profile-al-dev-shared/knowledge/commit-conventions.md |
| Maintainer contracts | profile-al-dev-shared/knowledge/skill-description-validator.md (this doc) |
