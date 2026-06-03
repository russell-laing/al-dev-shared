---
name: maintain-skill-naming-conventions
description: Use when repo-local skill names, descriptions, or root inventory docs may have drifted from the actual intent they represent, especially after a rename, a new skill is added, or stale references remain in AGENTS.md or CODEX.md.
---

# Maintain Skill Naming Conventions

## Overview

Keep repo-local skill names and their intent aligned so future runs can find the right skill quickly and avoid misleading labels. Use this skill for review-and-update passes on `.codex/skills/`, `AGENTS.md`, and `CODEX.md`.

## When to Use

- a repo-local skill name no longer matches what the skill actually does
- `name:` frontmatter disagrees with the directory name or body
- root inventory docs still list an old skill name
- a skill description is too vague, too broad, or reads like a workflow summary
- a new local skill should follow the repo's verb-first naming pattern

## Quick Checks

| Check | Expected |
|---|---|
| Directory name | Verb-first and aligned with the actual intent |
| `name:` frontmatter | Matches the directory name exactly |
| Description | Starts with `Use when...` and describes the trigger, not the workflow |
| Prefix smell | Avoid `plugin-` unless the skill truly needs to name the plugin surface itself |
| Root inventory docs | `AGENTS.md` and `CODEX.md` list current local skills only |
| Cross-references | No stale skill names remain in doc prose or examples |

## Review Loop

1. Inspect the live `.codex/skills/` inventory.
2. Compare each skill directory name to the `name:` frontmatter and body intent.
3. Update the skill body if the name is accurate but the wording is misleading.
4. Rename the skill if the directory name is misleading or the intent has shifted.
5. Update `AGENTS.md` and `CODEX.md` so the local inventory stays current.
6. Search for stale references to the old name and replace them.

## Common Mistakes

- keeping a skill name because it is familiar even though it no longer matches the task
- writing a description that summarizes the workflow instead of the trigger
- updating the skill file but forgetting the root inventory docs
- allowing old names to linger in examples or helper text after a rename
