---
name: heal-surface
description: Use when one profile-al-dev-shared surface needs a narrow end-of-session self-heal, especially for a single skill, agent, knowledge doc, or generated artifact with only a few small improvements to make.
---

# Heal Surface

Use this for a narrow pass at the end of a session.

## Surface Selector

1. `skill` - a file under `profile-al-dev-shared/skills/`
2. `agent` - a file under `profile-al-dev-shared/agents/`
3. `knowledge doc` - a file under `profile-al-dev-shared/knowledge/`
4. `generated artifact` - a file under `profile-al-dev-shared/generated/`

Invocation pattern:

- `[1=skill|2=agent|3=knowledge doc|4=generated artifact] [optional path or short focus]`

## Workflow

- Resolve the target file before reviewing content.
- If the user provides an explicit path, use it only if it stays within the selected surface. Otherwise stop and report the mismatch.
- If the user provides a short focus, narrow to matching files on the selected surface.
- If the focus matches no files, stop and report that no file matched.
- If the focus matches multiple files, choose the oldest modified match and say that multiple matches existed.
- If the user provides only the surface selector, choose the oldest modified file on that surface.
- Treat "oldest modified" as the file with the earliest filesystem modification time among regular files on the selected surface.
- If the selected surface is `generated artifact`, review the generated file only to identify the likely authored source and the smallest safe upstream fix. Do not recommend hand-editing the generated file.
- Read the selected surface plus only the minimum nearby context needed to understand it.
- Look for at most 1-5 concrete improvements.
- Prefer tiny fixes: wording, scope narrowing, missing guardrails, stale references, or obvious consistency cleanup.
- Rank by impact/effort and call out the smallest safe self-heal first.
- Stop if the surface is already consistent; do not expand into a broader audit.

## Output

Return a short note with:

- selected surface
- resolved file path
- whether multiple matches were collapsed to the oldest modified file
- for generated artifacts, the likely authored source to change instead
- 1-5 improvements
- which one is the best tiny self-heal
- whether it is safe to apply immediately

## Guardrails

- Do not review the whole plugin.
- Do not draft a full plan unless the user asks.
- Do not touch `profile-al-dev-shared` unless the user explicitly asks for edits.
- Do not hand-edit generated projection artifacts; point to the authored source and regenerate only if an approved edit requires it.
- If no file exists on the selected surface, stop and report that the surface is empty.
