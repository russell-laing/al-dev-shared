---
name: plugin-mini-heal
description: Quick end-of-session self-heal for one profile-al-dev-shared surface. Use when you want 1-5 minimal improvements on a single skill, agent, knowledge doc, or generated artifact without a full review.
argument-hint: "[1=skill|2=agent|3=knowledge doc|4=generated artifact] [path or short focus]"
---

# Plugin Mini Heal

Use this for a narrow pass at the end of a session.

## Surface Selector

1. `skill` - a file under `profile-al-dev-shared/skills/`
2. `agent` - a file under `profile-al-dev-shared/agents/`
3. `knowledge doc` - a file under `profile-al-dev-shared/knowledge/`
4. `generated artifact` - a file under `profile-al-dev-shared/generated/`

## Workflow

- Read the selected surface plus only the minimum nearby context needed to understand it.
- Look for at most 1-5 concrete improvements.
- Prefer tiny fixes: wording, scope narrowing, missing guardrails, stale references, or obvious consistency cleanup.
- Rank by impact/effort and call out the smallest safe self-heal first.
- Stop if the surface is already consistent; do not expand into a broader audit.

## Output

Return a short note with:

- selected surface
- 1-5 improvements
- which one is the best tiny self-heal
- whether it is safe to apply immediately

## Guardrails

- Do not review the whole plugin.
- Do not draft a full plan unless the user asks.
- Do not touch `profile-al-dev-shared` unless the user explicitly asks for edits.
- Do not regenerate projections unless the selected surface is generated output and regeneration is actually required.
