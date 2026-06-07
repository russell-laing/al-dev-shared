---
name: heal-surface
description: Use when one repo surface needs a narrow self-heal for a single file or tightly related file set, especially a repo-local skill, shared authored file, maintainer doc or report, script or config, or generated artifact, with only a few small improvements to make.
---

# Heal Surface

Use this for a narrow pass at the end of a session.

## Surface Selector

1. `repo-local skill` - a file under repo-local maintainer surfaces such as `.codex/skills/` or `.claude/skills/`
2. `shared authored file` - a file under canonical shared source such as `profile-al-dev-shared/skills/`, `profile-al-dev-shared/agents/`, `profile-al-dev-shared/knowledge/`, or `profile-al-dev-shared/markdown/`
3. `maintainer doc or report` - a maintainer-facing markdown file such as `docs/`, `.dev/`, findings, plans, reports, or commentary artifacts
4. `script or config` - a small script, validator input, manifest, or config file used by the maintainer workflow
5. `generated artifact` - a generated file such as a projection, rendered artifact, generated report, or derived index

Invocation pattern:

- `[1=repo-local skill|2=shared authored file|3=maintainer doc or report|4=script or config|5=generated artifact] [optional path or short focus]`

## Workflow

- Resolve the target file before reviewing content.
- If the user provides an explicit path without a selector, infer the surface from the path when it is unambiguous. Otherwise stop and ask for the surface.
- If the user provides an explicit path, use it only if it stays within the selected surface class. Otherwise stop and report the mismatch.
- If the user provides a short focus, narrow to matching files on the selected surface.
- If the focus matches no files, stop and report that no file matched.
- If the focus matches multiple files, choose the oldest modified match and say that multiple matches existed.
- If the user provides only the surface selector, choose the oldest modified file on that surface.
- Treat "oldest modified" as the file with the earliest filesystem modification time among regular files on the selected surface.
- If the selected surface is `generated artifact`, review the generated file only to identify the likely authored source, generator script, or config that should change upstream. Do not recommend hand-editing the generated file.
- If the selected surface is `script or config`, keep the pass small: prefer guardrails, stale-path cleanup, argument consistency, scope narrowing, or obvious contract fixes over behavior expansion.
- If the selected surface is `script or config` and the target implies multi-file behavioral refactoring or runtime feature expansion, stop and report that it is outside the tiny self-heal scope.
- Read the selected surface plus only the minimum nearby context needed to understand it.
- Look for at most 1-5 concrete improvements.
- Prefer tiny fixes: wording, scope narrowing, missing guardrails, stale references, obvious consistency cleanup, or small contract corrections.
- Rank by impact/effort and call out the smallest safe self-heal first.
- State why the selected file is in scope for the chosen surface if that is not obvious from the path.
- Stop if the surface is already consistent; do not expand into a broader audit.

## Output

Return a short note with:

- selected surface
- resolved file path
- why the file was in scope for that surface
- whether multiple matches were collapsed to the oldest modified file
- for generated artifacts, the likely authored source, generator script, or config to change instead
- 1-5 improvements
- which one is the best tiny self-heal
- recommended action: `apply now`, `review first`, or `do not apply`

## Guardrails

- Do not review the whole plugin.
- Do not draft a full plan unless the user asks.
- Do not edit shared authored files unless the user explicitly asks for edits.
- Do not hand-edit generated projection artifacts; point to the authored source and regenerate only if an approved edit requires it.
- If no file exists on the selected surface, stop and report that the surface is empty.
