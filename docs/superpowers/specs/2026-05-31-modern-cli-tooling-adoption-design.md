# Modern CLI Tooling Adoption for `al-dev-shared` - Design Spec

**Date:** 2026-05-31  
**Status:** Draft  
**Author:** Brainstorming collaboration  

## Executive Summary

**Problem:** The repo already relies on shell-driven validation, search, and JSON editing, but its guidance is uneven. Some workflows already prefer `rg`, some use ad hoc `grep`/`sed`, and JSON updates are still described inconsistently. The shared plugin surface also does not clearly distinguish between "preferred local CLI tool" and "harness-native capability."

**Solution:** Standardize two modern CLI tools across both surfaces:
- `rg` for fast, scoped text search and pattern verification
- `jq` for safe inspection and mutation of JSON state files and other structured artifacts

The change is intentionally policy and guidance focused. It does not introduce a new shared capability or change the projection contract. Instead, it teaches repo tooling and shared skills/knowledge to prefer `rg` and `jq` when they are available, with explicit fallbacks when they are not.

**Expected outcome:**
- More consistent maintainer workflows
- Less reliance on broad `grep`/manual parsing when `rg` is available
- Safer JSON edits in `.claude/`, `.dev/`, and other structured artifacts
- Clearer distinction between shell tooling choices and harness-native capabilities

---

## Problem Statement

### Current State

The repo already contains many `rg`-based examples and shell-driven validation steps, but they are not presented as a standard convention. JSON handling is more fragmented: some docs already use `jq`, others rely on manual editing or shell text substitution. The result is a mixed guidance surface where maintainers must infer which tool is preferred in a given workflow.

The plugin surface has a second ambiguity: `rg` and `jq` are useful implementation tools, but they are not shared harness capabilities. If the repo treats them as if they were cross-harness primitives, projection policy gets muddy.

### Why This Matters

- `rg` is already installed in this environment and is a better default for scoped text search than broad grep patterns.
- `jq` is already installed and is the safer default for JSON reads and updates than line-oriented shell text edits.
- The repo increasingly uses structured artifacts and generated metadata, so the lack of a clear JSON tool policy creates avoidable friction.
- Shared agent and knowledge content should stay harness-neutral while still giving maintainers concrete tool preferences.

---

## Goals

1. Make `rg` the default search tool in repo guidance wherever the task is text search, pattern verification, or file discovery by content.
2. Make `jq` the default tool in repo guidance wherever the task is JSON inspection, filtering, or field updates.
3. Update shared plugin guidance so skills and BC knowledge documents recommend `rg` and `jq` inside Bash-based workflows without changing the projection model.
4. Preserve a clear fallback path when either tool is missing.
5. Avoid introducing a new shared capability or a new projection mapping for `rg` or `jq`.

## Non-Goals

1. Do not add a new harness capability such as `JsonQuery` or `StructuredSearch`.
2. Do not require installation of additional CLI tools beyond what is already available in the environment.
3. Do not rewrite the entire repo to use `jq` or `rg`; only update the high-leverage docs and shared guidance surfaces.
4. Do not change the existing agent projection policy to map `rg` or `jq` as native cross-harness tools.

---

## Proposed Design

### Architecture

The design has two layers:

1. **Tooling surface conventions**  
   Repo-facing docs, maintainer notes, and validation guidance will explicitly state:
   - use `rg` first for scoped search
   - use `jq` first for JSON reads and updates
   - fall back to `grep`, `sed`, or Python only when the preferred tool is unavailable or inappropriate

2. **Plugin surface guidance**  
   Shared skills, agents, and BC knowledge docs will continue to project harness-neutral capabilities, but the text inside those artifacts will tell maintainers and agents to prefer `rg`/`jq` when they are using Bash-based workflows.

This keeps the projection layer simple: `rg` and `jq` remain implementation choices inside Bash, not new cross-harness abstractions.

### Components

#### Repo Tooling Guidance

Update the repo-maintainer-facing guidance so it states the standard search/edit preferences clearly. Initial targets:
- `profile-al-dev-shared/knowledge/script-engineer-conventions.md`
- `profile-al-dev-shared/knowledge/compile-lint-procedure.md`
- any plan/spec template that shows shell examples for search or JSON manipulation

These updates should say:
- prefer `rg -n` for content search and pattern validation
- prefer `jq` for JSON field inspection and updates
- use narrower fallbacks only when needed

#### Shared Plugin Guidance

Update a small number of shared authored surfaces where shell usage is already part of the workflow. Initial targets:
- `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md`
- `profile-al-dev-shared/bc-code-intel-knowledge/README.md`
- `profile-al-dev-shared/bc-code-intel-knowledge/specialists/sam-coder.md`
- `profile-al-dev-shared/bc-code-intel-knowledge/specialists/roger-reviewer.md`
- `profile-al-dev-shared/bc-code-intel-knowledge/specialists/terry-test.md`
- `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-lint/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-script-engineer/SKILL.md`

The intended behavior is not to make `rg` and `jq` first-class shared capabilities. It is to make them the preferred command-line implementation details when the workflow already uses Bash.

#### Boundary Statement

Clarify in the projection-policy documentation that:
- shared capabilities remain generic (`Read`, `Grep`, `Bash`, `USER_GATE`, etc.)
- `rg` and `jq` are local tooling conventions, not projection targets
- plugin docs may recommend them, but generator rules do not need new mappings

---

## Concrete Behavior

### `rg` Usage

Use `rg` for:
- searching repo files for specific text or patterns
- finding all occurrences of a symbol-like string
- checking that a pattern appears or does not appear in a file set
- validating generated-doc consistency with one-line or multi-file scans

Preferred pattern:

```bash
rg -n "pattern" path/to/scope
```

Use a fallback such as `grep -R` only when `rg` is unavailable or the caller explicitly needs a POSIX-only command.

### `jq` Usage

Use `jq` for:
- reading `.json` configuration and state files
- extracting specific fields from structured output
- updating one or two fields without reserializing the whole file by hand
- checking generated metadata and checkpoint files

Preferred pattern:

```bash
jq '.field.subfield' path/to/file.json
```

For updates, prefer a temporary-file or in-place-safe flow that preserves formatting and avoids partial writes.

### Fallback Policy

If `rg` is missing:
- use `grep` or a targeted Python fallback

If `jq` is missing:
- use Python for structured JSON handling
- avoid manual JSON text rewriting unless the change is trivial and low risk

The fallback should be explicit in the tool guidance so future maintainers do not guess.

---

## Files to Update

This design expects changes in both surfaces:

### Repo Tooling Surface

- `profile-al-dev-shared/knowledge/script-engineer-conventions.md`
- `profile-al-dev-shared/knowledge/compile-lint-procedure.md`
- the shared plan/spec templates that show shell command conventions for validation or state handling

### Shared Plugin Surface

- `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md`
- `profile-al-dev-shared/bc-code-intel-knowledge/README.md`
- `profile-al-dev-shared/bc-code-intel-knowledge/specialists/sam-coder.md`
- `profile-al-dev-shared/bc-code-intel-knowledge/specialists/roger-reviewer.md`
- `profile-al-dev-shared/bc-code-intel-knowledge/specialists/terry-test.md`
- `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-lint/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-script-engineer/SKILL.md`

The exact edit set should stay small and focused. The goal is to align the strongest, most reused guidance surfaces rather than rewrite every file in the repo.

---

## Error Handling and Risk

### Tool Availability

This environment currently has `rg` and `jq` available. Other popular modern CLI tools such as `fd`, `fzf`, `bat`, `delta`, `gum`, `yq`, `eza`, `lsd`, and `xh` are not installed here.

The spec therefore avoids making adoption depend on those tools. If they are added later, they should be treated as separate follow-on decisions rather than assumed as part of this work.

### Projection Safety

The main risk is accidental scope creep into the projection contract. The design avoids that by explicitly keeping `rg` and `jq` out of the shared capability vocabulary. If the repo later wants a higher-level abstraction, that should be a separate design.

### Guidance Drift

If only some docs mention `rg`/`jq`, the repo will remain inconsistent. The implementation should therefore update the highest-leverage guidance files first and keep the wording aligned across tooling and plugin surfaces.

---

## Validation

Validation should confirm three things:

1. The updated docs consistently prefer `rg` for search and `jq` for JSON work.
2. Shared authored content remains harness-neutral at the capability level.
3. No new projection mapping or generated artifact is required.

Suggested checks:
- `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared`
- `python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents`
- targeted `rg` checks to confirm the new wording appears where expected
- targeted `jq`-based inspection of any updated JSON examples or state files, if applicable

---

## Rollout Strategy

1. Update the repo-facing tooling guidance first.
2. Update the most reused shared plugin guidance next.
3. Verify the wording stays consistent with the projection policy.
4. Leave generator code unchanged unless later work proves the policy boundary is insufficient.

This keeps the change low-risk and easy to audit.
