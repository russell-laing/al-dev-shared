# Design: Harness-Specific Agent Tool Declarations

**Date:** 2026-05-22  
**Audience:** Agent authors in `al-dev-shared`  
**Status:** Revised after claim verification

---

## Motivation

`al-dev-shared` is shared across multiple agent harnesses, but those harnesses do not expose agent configuration through one uniform format.

The current design problem is real:

1. Agent authors need one shared source of intent for what an agent is allowed to do.
2. Harnesses expose tool restrictions differently, so a single literal `tools:` schema cannot be treated as universal.
3. Some current agent bodies and declared tools are inconsistent, which makes author intent unclear.

The `al-dev-explore` agent is the clearest example. Its frontmatter declares `["Read", "Glob", "Grep", "Write"]`, but the body contains a dedicated "Bash Output Capture" section with `al-compile` examples and mandatory shell-output handling guidance. That is a real mismatch in the current repo and should be fixed independently of any broader format work.

---

## Verified Findings

### Repo facts

- Shared agents in this repo are currently Markdown files under `profile-al-dev-shared/agents/`.
- Those files currently use YAML frontmatter with fields such as `description`, `model`, and `tools`.
- `al-dev-explore` currently declares no `Bash` tool but includes shell-specific instructions in its body.
- `al-dev-interview` currently declares `AskUserQuestion` in frontmatter while its body correctly uses the harness-neutral concept `USER_GATE`.

### Claude Code

Official Claude Code subagent docs support Markdown subagent files with an optional `tools` field.

- If `tools` is omitted, the subagent inherits all tools available to the parent conversation.
- If `tools` is present, it acts as a restriction.
- Claude Code also supports MCP tools for subagents.

This means `tools` is not required in principle, though this repo may still choose to require it as a local convention.

### Copilot CLI

Official Copilot docs support Markdown custom agent profiles with a `tools` property.

- By default, custom agents have access to all tools.
- A `tools` entry is added when access is intentionally restricted.
- Copilot also supports `target` to scope an agent profile to `vscode` or `github-copilot`.
- Copilot tool names are alias-based (`execute`, `read`, `edit`, `search`, etc.), not guaranteed to match this repo's current Claude-oriented spellings one-for-one.

This means the old claim that Copilot `tools:` is always required and always restrictive was overstated.

### Codex

Current Codex documentation does not describe shared-agent Markdown frontmatter with `tools_codex` overrides.
Instead, Codex custom agents are defined as standalone TOML config layers under `~/.codex/agents/` or `.codex/agents/`.

- Required fields are `name`, `description`, and `developer_instructions`.
- Optional settings such as `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, and `skills.config` inherit from the parent session when omitted.
- Subagents inherit the current sandbox policy unless explicitly overridden.
- Codex documents MCP support.

The practical consequence is important: Codex agent configuration is a separate integration target, not a third consumer of the same YAML frontmatter shape used by Claude Code and Copilot.

---

## Design Decision

Do **not** introduce `tools_claude`, `tools_copilot`, or `tools_codex` keys into shared agent Markdown.

Instead, standardize on a two-layer model:

1. **Shared agent intent layer**
   - Keep a harness-neutral shared agent definition in the existing Markdown agent file.
   - Treat the agent body as the canonical statement of purpose, workflow, outputs, and constraints.
   - Keep tool intent expressed in a harness-neutral way wherever possible.

2. **Harness projection layer**
   - Claude Code projection: generate Claude-compatible Markdown tool restrictions.
   - Copilot projection: generate Copilot-compatible Markdown tool restrictions and, if needed, `target`.
   - Codex projection: generate Codex TOML agent config, including sandbox and inherited defaults where relevant.

This avoids pretending all harnesses share one literal config schema when they do not.

### First implementation defaults

This design now fixes the previously-open choices:

- Shared agent Markdown remains canonical.
- The existing `tools:` field stays in the shared file.
- Harness projections are generated, not hand-maintained.
- First-generation projection artifacts live in this repo, not external harness repos.

---

## Shared Authoring Model

### Canonical source

The shared Markdown agent file remains the canonical authored artifact in this repo.

It should define:

- agent purpose
- expected inputs and outputs
- behavioral constraints
- harness-neutral workflow guidance
- tool intent expressed in terms of capabilities, not brand-specific syntax where possible

### Tool intent vocabulary

Within shared docs, use capability-level language first:

- file read
- file write/edit
- file search
- shell/command execution
- user gate / blocking question
- MCP access by capability

The canonical meaning of the shared file's literal `tools:` field is:

- it declares the agent's shared capability intent using the repo's current canonical tool vocabulary
- it serves as the default source for generated Claude and Copilot projections
- it is not treated as a literal cross-harness schema for Codex

If the shared body and shared `tools:` list disagree, the file is invalid and the validator must fail. The body plus declared capability intent is authoritative; stale `tools:` content is a defect, not an ambiguity to resolve silently.

### Body/frontmatter consistency rule

A shared agent must not instruct the agent to use a capability that its maintained harness projection denies.

Examples:

- If the body includes compile commands or shell redirection guidance, the Claude/Copilot projections must allow shell execution, or the body must be rewritten to remove shell behavior.
- If the body requires blocking user interaction, the projection for each harness must map that requirement to the harness's actual user-gate mechanism.

---

## Harness-Specific Projections

### Projection artifact locations

Generated projections live in-repo under a dedicated generated tree so they are easy to diff and are clearly non-canonical:

```text
profile-al-dev-shared/generated/agents/
  claude/<agent>.md
  copilot/<agent>.md
  codex/<agent>.toml
```

These files are derived artifacts.

- They must not be edited by hand.
- Regeneration must be deterministic from the shared source plus projection policy metadata.
- External harness repos may consume these artifacts later, but that is not part of the first implementation.

### Claude Code projection

Keep the existing Markdown agent format.

- `tools` may be omitted to inherit parent tools, but this repo should continue to prefer explicit tool lists for auditability.
- Tool names should follow Claude Code naming for the projection file.
- MCP access should be declared in the way Claude expects for subagents, not inferred from shared prose alone.

In the first implementation, generated Claude projections should keep the current shared tool spellings where they already match Claude conventions.

### Copilot projection

Use a Markdown custom-agent profile.

- Restrict tools only when needed.
- Normalize tool names to Copilot-supported aliases.
- Use `target` only when a Copilot-specific split is needed; do not use `target` as a substitute for broader harness branching.

Because Copilot aliases differ from this repo's existing tool naming, projection requires a translation layer even when capability intent is identical.

The translation source of truth should be a dedicated policy document in `profile-al-dev-shared/knowledge/` that defines:

- shared capability/tool token
- generated Copilot alias
- whether the mapping is lossless
- failure behavior when no valid Copilot alias exists

Failure behavior should be strict: if no supported Copilot alias exists for a required shared capability, generation must fail rather than emit a partial or guessed projection.

### Codex projection

Use a TOML custom-agent file rather than extending YAML frontmatter.

- Map shared intent into `name`, `description`, and `developer_instructions`.
- Configure sandbox and inherited behavior using Codex-native settings.
- Configure MCP and skill behavior through Codex-native settings, not synthetic YAML keys.
- Do not invent a fake `tools_codex` schema unless Codex officially adds equivalent support in its documented agent format.

The Codex projection policy must also define how shared capabilities map into Codex-native config decisions. In the first implementation:

- shared shell capability maps to Codex guidance and config that permit command execution in the generated agent context
- shared user-gate capability maps to documented Codex-compatible interaction instructions rather than a fabricated tool name
- unsupported capability mappings fail generation explicitly

If Codex later adds first-class per-agent tool restriction fields, that can be adopted as a Codex projection detail without changing the shared authored model.

---

## Drift Prevention Policy

Preventing drift is a first-class requirement, not a follow-up cleanup task.

### 1. One policy vocabulary

`profile-al-dev-shared/knowledge/harness-concepts.md` remains the shared vocabulary contract for harness-agnostic prose.

- Shared agent bodies and shared knowledge files must use that vocabulary.
- Projection generation may translate that vocabulary into harness-native syntax.
- Generated projections must never become the place where new semantics are invented.

### 2. One canonical authored source

The shared agent Markdown file is the only hand-edited source for shared agent behavior.

- Generated Claude, Copilot, and Codex projections are derived outputs only.
- Any repeated dispatch or invocation shape that appears in more than one skill or agent should be extracted into a canonical pattern document in `profile-al-dev-shared/knowledge/`, following the same pattern already used by `ticket-agent-invocation-pattern.md`.

This keeps behavioral duplication out of multiple files and reduces copy/paste drift.

### 3. Deterministic generation

Projection generation must be deterministic from:

- shared agent Markdown
- harness vocabulary policy
- tool/capability translation policy

No projection file may contain hand-edited exceptions. If a harness-specific exception is needed, it must be represented as declared metadata in the canonical source or in a documented projection policy file.

### 4. Alignment gate

The existing `check-alignment.py` policy should be extended rather than bypassed.

It should remain the guard against harness-specific token leaks in shared files, and it should gain projection-aware checks for:

- shared body uses harness-neutral vocabulary where required
- shared `tools:` values stay within the canonical shared tool vocabulary
- generated projections do not leak unsupported or unmapped capabilities
- generated projections remain consistent with the shared source

This keeps harness-agnostic policy enforcement and projection consistency under one audit model rather than creating separate, drifting validators.

### 5. Fail closed on unsupported mappings

When a required shared capability cannot be represented safely in a harness projection:

- generation fails
- validation fails
- the incompatibility is reported explicitly

Do not silently drop capabilities, guess aliases, or emit partial agent outputs that look valid but change behavior.

---

## Validation Rules

### Shared-file validation

Validate the canonical shared agent file for:

- required frontmatter fields used by this repo's authoring convention
- presence of `## Inputs` and `## Outputs` where expected
- body/frontmatter consistency
- harness-neutral language in body text where the repo has already standardized terms such as `USER_GATE`
- `tools:` values use only the canonical shared tool vocabulary adopted by this repo
- repeated harness-specific dispatch patterns are referenced from canonical knowledge documents when such a pattern already exists

### Projection validation

Validate each emitted or maintained harness projection against that harness's real documented schema.

- Claude projection: valid Markdown subagent metadata and tool names
- Copilot projection: valid Markdown custom-agent metadata, aliases, and optional `target`
- Codex projection: valid TOML keys and value types
- Generated file paths and filenames match the in-repo projection tree exactly

### Cross-projection validation

For every shared agent:

- If the body requires shell execution, Claude and Copilot projections must expose shell capability, and Codex must either expose equivalent command capability through its native config or the shared body must be split or rewritten.
- If the body requires a blocking user gate, each harness projection must provide a valid mechanism for that behavior.
- If a harness cannot support a required capability, that incompatibility must be explicit in docs rather than hidden in a partial tools list.
- If a shared capability has no documented translation rule for a harness, generation fails.

---

## Migration Plan

### Phase 1: Fix current inaccuracies

- Remove or rewrite shell-specific guidance from shared agents that do not actually declare shell capability in their maintained projections.
- Start with `al-dev-explore`, because its mismatch is already confirmed.
- Audit `AskUserQuestion` references in frontmatter and map them to harness-neutral `USER_GATE` intent plus harness-specific projection rules.

### Phase 2: Introduce projection-aware documentation

Add a new knowledge document describing:

- shared capability vocabulary
- canonical meaning of shared `tools:`
- Claude projection rules
- Copilot projection rules
- Codex TOML projection rules
- translation tables and failure behavior
- current verified doc links and known constraints

This should replace the earlier idea of a single universal tool table that mixes schema and capability claims.

### Phase 3: Add deterministic generation and validation

Introduce scripts that:

- read the shared agent definition
- generate the in-repo Claude, Copilot, and Codex projection files
- check consistency against generated projection files
- flag unsupported capability combinations

Do this only after the projection model is documented. The generator and validator must enforce documented truth, not invent undocumented semantics.

---

## Non-Goals

This design does not:

- claim that all harnesses share one common agent manifest schema
- introduce undocumented `tools_codex` behavior
- assume tool names are identical across harnesses
- assume omitted `tools` means the same thing in every harness for every future release
- rely on hand-maintained harness projection files in the first implementation

---

## Acceptance Criteria

- The spec no longer claims Codex shares the shared Markdown `tools:` schema.
- The spec no longer claims `tools:` must always be present because of harness behavior; any such requirement is clearly identified as a repo convention if retained.
- The spec explicitly distinguishes shared agent intent from harness-specific projections.
- The spec records the verified `al-dev-explore` mismatch as a concrete repo issue.
- The spec treats Copilot and Claude `tools` behavior as restrictive only when explicitly set.
- The spec treats Codex configuration as TOML-based and inheritance-driven according to current docs.
- The spec defines concrete in-repo output paths for generated harness projections.
- The spec defines `tools:` as shared capability intent plus Claude/Copilot default projection source.
- The spec requires anti-drift enforcement through canonical vocabulary, deterministic generation, and an alignment gate.

---

## Summary

The corrected design is to keep one shared authored agent definition, but stop modeling tool declarations as a single cross-harness schema.

Claude Code and Copilot can continue to consume Markdown agent manifests with restricted tool lists when needed. Codex must be handled through its own TOML custom-agent configuration model. Shared authoring should therefore center on capability intent and consistency, with harness-specific projections carrying the concrete syntax and limitations.
