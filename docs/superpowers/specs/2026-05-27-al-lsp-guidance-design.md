# AL LSP Guidance Design

## Summary

Update `profile-al-dev-shared` guidance so AL Language Server Protocol support is recognized as a preferred semantic navigation provider when it is exposed by the active harness or adapter.

This is a guidance-only change. It does not add scripts, generated projections, manifest changes, or any runtime dependency on `al launchlspserver`.

## Goal

Improve AL/Business Central agent workflows by making symbol verification more semantic and less text-search dependent, while preserving the existing `al-mcp-server` workflow as the supported current fallback.

The guidance should help agents answer questions such as:

- Where is this AL symbol defined?
- Where is this procedure, event, or field referenced?
- What is the type or signature of this symbol?
- Is a planned subscriber or refactor based on semantic evidence, MCP evidence, or only text search?

## Architecture

Add a neutral concept for AL semantic navigation rather than binding shared guidance directly to ALTool.

`AL semantic navigation` is the preferred capability for symbol-aware operations in a target AL workspace. Providers may include:

- AL LSP exposed through the active harness or an adapter
- `al-mcp-server`
- another harness-native semantic AL tool

`AL symbol/object lookup` remains the existing MCP-oriented capability for object definitions, references, and base-app/package exploration.

When AL LSP is available through the active harness, agents should prefer it for:

- go-to-definition
- find-references
- document symbols
- hover/type information
- rename or refactor impact checks

When AL LSP is not available, agents continue using `al-mcp-server` exactly as today. When no semantic provider is available, agents may use tightly scoped `rg` searches, but must label the result as text-verified rather than semantically verified.

## Profile Guidance Changes

Update a narrow set of shared-profile docs:

- `profile-al-dev-shared/knowledge/harness-concepts.md`
  - Add `AL semantic navigation` as a generic concept.
  - Keep provider details harness-dependent and avoid raw tool IDs.

- `profile-al-dev-shared/knowledge/al-symbol-pre-flight.md`
  - Reframe symbol pre-flight around semantic verification where possible.
  - Keep existing MCP examples as concrete fallback examples.
  - Require verification summaries to name the evidence source.

- `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`
  - Prefer semantic navigation during base-app and project pre-research for symbol-heavy planning.
  - Continue when LSP is unavailable by using existing MCP or text-search fallback behavior.

- `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`
  - Prefer semantic navigation during implementation pre-flight and signature verification.
  - Require developers to report whether symbols were verified by AL LSP, AL MCP, text search, or not verified.

- `profile-al-dev-shared/agents/al-dev-solution-architect.md`
  - Ask architects to include verification source labels in schema mapping and external symbol evidence.

- `profile-al-dev-shared/agents/al-dev-developer.md`
  - Ask developers to complete pre-flight with a named evidence source before writing AL code.

- `profile-al-dev-shared/skills/al-dev-perf/SKILL.md`
  - Clarify that codeunit classification can use semantic document symbols when available, otherwise keep current MCP/text fallback behavior.

## Behavioral Rules

1. Semantic-first evidence
   - For AL symbol questions, prefer a semantic provider when available.
   - Treat AL LSP as the best semantic source for workspace-aware operations such as go-to-definition, find-references, document symbols, hover/type information, and rename impact.
   - Treat AL MCP as valid for object definitions, object/member search, references, and packaged symbol exploration.

2. Evidence labels
   - `AL LSP`: workspace-semantic verification.
   - `AL MCP`: object/member/package symbol verification.
   - `text search`: weaker fallback; describe as text-verified only.
   - `unverified`: stop or escalate if the symbol is required before implementation.

3. No availability assumptions
   - Do not claim AL LSP exists because ALTool documentation exists.
   - Use AL LSP only when the active harness exposes an LSP-capable tool or adapter.
   - If no LSP path is exposed, continue with current MCP guidance and targeted `rg`.

## Out of Scope

- Adding scripts or helper commands.
- Editing generated projections.
- Editing plugin manifests.
- Launching `al launchlspserver`.
- Adding JSON-RPC examples.
- Requiring Business Central 2026 release wave 1 tooling.
- Replacing `al-mcp-server` as the supported current provider.

## Test Plan

- Run harness neutrality validation:
  - `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared`
- If agent frontmatter or projection-sensitive files are touched, run projection tests:
  - `python3 scripts/tests/test_generate_agent_projections.py`
- Search updated docs for accidental hard dependency language such as `must use LSP`.
- Search affected symbol-preflight and planning guidance for stale MCP-only phrasing.

## Acceptance Criteria

- Shared guidance describes AL LSP as an optional preferred semantic provider, not a dependency.
- Existing MCP workflows remain valid and concrete.
- Plans, pre-flight summaries, and agent outputs can distinguish `AL LSP`, `AL MCP`, `text search`, and `unverified` evidence.
- No generated projection or manifest files are changed for this guidance-only pass.
