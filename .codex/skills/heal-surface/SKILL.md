---
name: heal-surface
description: Use when one repo surface or tightly related file set needs a narrow end-of-session review or tiny self-heal, especially repo-local skills, shared authored files, maintainer docs, reports, scripts, configs, or generated artifacts.
---

# Heal Surface

Use this for one small, bounded quality pass. Improve the selected surface without turning a tiny self-heal into a broad audit, rewrite, or plan.

## Surface Selector

| Selector | Surface | Default edit rule |
| --- | --- | --- |
| `1` | `repo-local skill`: active `.codex/skills/` or `.claude/skills/`; exclude `archived/` | Edit only when asked |
| `2` | `shared authored file`: canonical `profile-al-dev-shared/skills/`, `agents/`, `knowledge/`, or `markdown/` | Edit only when explicit |
| `3` | `maintainer doc or report`: `docs/`, `.dev/`, findings, plans, reports, or commentary | Prefer review notes |
| `4` | `script or config`: small maintainer script, validator input, manifest, or config | Guardrails only |
| `5` | `generated artifact`: projection, rendered artifact, generated report, or derived index | Never hand-edit |

Invocation pattern:

- `[1=repo-local skill|2=shared authored file|3=maintainer doc or report|4=script or config|5=generated artifact] [optional path or short focus]`
- An explicit path without a selector may be inferred when the surface class is unambiguous.

## Workflow

1. Decide whether the request is review-only or edit-authorized.
2. Resolve exactly one target file or tightly related file set.
3. Read the target plus minimum nearby context.
4. Identify at most 1-5 concrete improvements.
5. Return recommendations or apply the smallest safe patch.

### Target Resolution

- Resolve the target file before reviewing content.
- If the user provides an explicit path without a selector, infer the surface from the path when it is unambiguous. Otherwise stop and ask for the surface.
- If the user provides an explicit path, use it only if it stays within the selected surface class. Otherwise stop and report the mismatch.
- If the user provides a short focus, narrow to matching files on the selected surface.
- If the focus matches no files, stop and report that no file matched.
- If the focus matches multiple files, choose the oldest modified match and say that multiple matches existed.
- If the user provides only the surface selector, choose the oldest modified file on that surface.
- For `repo-local skill`, resolve only active skills; do not select files under `archived/`.
- Treat "oldest modified" as the regular file with the earliest filesystem modification time, excluding `.DS_Store`.
- The user can move a file to the bottom of the candidate list with `touch`.

### Review Rules

- `review`, `check`, or `suggest` means no edits; return findings and a recommended action.
- `make improvements`, `apply now`, or `fix` authorizes only the smallest safe patch to a selected non-generated surface.
- If the selected surface is `generated artifact`, review the generated file only to identify the likely authored source, generator script, or config that should change upstream. Do not recommend hand-editing the generated file.
- If the selected surface is `script or config`, keep the pass small: prefer guardrails, stale-path cleanup, argument consistency, scope narrowing, or obvious contract fixes over behavior expansion.
- If the selected surface is `script or config` and the target implies multi-file behavioral refactoring or runtime feature expansion, stop and report that it is outside the tiny self-heal scope.
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

When edits were applied, keep the final note shorter:

- selected surface and path
- what changed
- validation performed
- any remaining risk

## Guardrails

- Do not review the whole plugin.
- Do not draft a full plan unless the user asks.
- Do not edit shared authored files unless the user explicitly asks for edits.
- Do not hand-edit generated projection artifacts; point to the authored source and regenerate only if an approved edit requires it.
- If no file exists on the selected surface, stop and report that the surface is empty.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating an explicit path as permission for a broad sibling sweep | Stay on that file unless nearby context is required |
| Editing on a review-only request | Return recommendations and ask for approval only when needed |
| Patching generated output | Find and change the authored source or generator instead |
| Expanding a script/config cleanup into a feature | Stop and report that the work exceeds tiny self-heal scope |
| Counting archived skills as repo-local candidates | Exclude archived paths from selection and oldest-modified checks |
