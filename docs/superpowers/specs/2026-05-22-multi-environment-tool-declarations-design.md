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
   - Claude Code projection: generate or maintain Claude-compatible Markdown tool restrictions.
   - Copilot projection: generate or maintain Copilot-compatible Markdown tool restrictions and, if needed, `target`.
   - Codex projection: generate or maintain Codex TOML agent config, including sandbox and inherited defaults where relevant.

This avoids pretending all harnesses share one literal config schema when they do not.

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

Where the file keeps a literal `tools:` list for Claude/Copilot compatibility, treat it as a projection-friendly field rather than a universal truth about every harness.

### Body/frontmatter consistency rule

A shared agent must not instruct the agent to use a capability that its maintained harness projection denies.

Examples:

- If the body includes compile commands or shell redirection guidance, the Claude/Copilot projections must allow shell execution, or the body must be rewritten to remove shell behavior.
- If the body requires blocking user interaction, the projection for each harness must map that requirement to the harness's actual user-gate mechanism.

---

## Harness-Specific Projections

### Claude Code projection

Keep the existing Markdown agent format.

- `tools` may be omitted to inherit parent tools, but this repo should continue to prefer explicit tool lists for auditability.
- Tool names should follow Claude Code naming for the projection file.
- MCP access should be declared in the way Claude expects for subagents, not inferred from shared prose alone.

### Copilot projection

Use a Markdown custom-agent profile.

- Restrict tools only when needed.
- Normalize tool names to Copilot-supported aliases.
- Use `target` only when a Copilot-specific split is needed; do not use `target` as a substitute for broader harness branching.

Because Copilot aliases differ from this repo's existing tool naming, projection may require name translation even when capability intent is identical.

### Codex projection

Use a TOML custom-agent file rather than extending YAML frontmatter.

- Map shared intent into `name`, `description`, and `developer_instructions`.
- Configure sandbox and inherited behavior using Codex-native settings.
- Configure MCP and skill behavior through Codex-native settings, not synthetic YAML keys.
- Do not invent a fake `tools_codex` schema unless Codex officially adds equivalent support in its documented agent format.

If Codex later adds first-class per-agent tool restriction fields, that can be adopted as a Codex projection detail without changing the shared authored model.

---

## Validation Rules

### Shared-file validation

Validate the canonical shared agent file for:

- required frontmatter fields used by this repo's authoring convention
- presence of `## Inputs` and `## Outputs` where expected
- body/frontmatter consistency
- harness-neutral language in body text where the repo has already standardized terms such as `USER_GATE`

### Projection validation

Validate each emitted or maintained harness projection against that harness's real documented schema.

- Claude projection: valid Markdown subagent metadata and tool names
- Copilot projection: valid Markdown custom-agent metadata, aliases, and optional `target`
- Codex projection: valid TOML keys and value types

### Cross-projection validation

For every shared agent:

- If the body requires shell execution, Claude and Copilot projections must expose shell capability, and Codex must either expose equivalent command capability through its native config or the shared body must be split or rewritten.
- If the body requires a blocking user gate, each harness projection must provide a valid mechanism for that behavior.
- If a harness cannot support a required capability, that incompatibility must be explicit in docs rather than hidden in a partial tools list.

---

## Migration Plan

### Phase 1: Fix current inaccuracies

- Remove or rewrite shell-specific guidance from shared agents that do not actually declare shell capability in their maintained projections.
- Start with `al-dev-explore`, because its mismatch is already confirmed.
- Audit `AskUserQuestion` references in frontmatter and map them to harness-neutral `USER_GATE` intent plus harness-specific projection rules.

### Phase 2: Introduce projection-aware documentation

Add a new knowledge document describing:

- shared capability vocabulary
- Claude projection rules
- Copilot projection rules
- Codex TOML projection rules
- current verified doc links and known constraints

This should replace the earlier idea of a single universal tool table that mixes schema and capability claims.

### Phase 3: Add projection validation or generation

Introduce validation and, if useful later, generation scripts that:

- read the shared agent definition
- check consistency against projection files
- flag unsupported capability combinations

Do this only after the projection model is documented. The validator should enforce documented truth, not invent undocumented semantics.

---

## Non-Goals

This design does not:

- claim that all harnesses share one common agent manifest schema
- introduce undocumented `tools_codex` behavior
- assume tool names are identical across harnesses
- assume omitted `tools` means the same thing in every harness for every future release

---

## Acceptance Criteria

- The spec no longer claims Codex shares the shared Markdown `tools:` schema.
- The spec no longer claims `tools:` must always be present because of harness behavior; any such requirement is clearly identified as a repo convention if retained.
- The spec explicitly distinguishes shared agent intent from harness-specific projections.
- The spec records the verified `al-dev-explore` mismatch as a concrete repo issue.
- The spec treats Copilot and Claude `tools` behavior as restrictive only when explicitly set.
- The spec treats Codex configuration as TOML-based and inheritance-driven according to current docs.

---

## Summary

The corrected design is to keep one shared authored agent definition, but stop modeling tool declarations as a single cross-harness schema.

Claude Code and Copilot can continue to consume Markdown agent manifests with restricted tool lists when needed. Codex must be handled through its own TOML custom-agent configuration model. Shared authoring should therefore center on capability intent and consistency, with harness-specific projections carrying the concrete syntax and limitations.
