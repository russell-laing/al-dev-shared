---
shared_capabilities:
  - USER_GATE
  - shared `tools:` metadata
projection_rules:
  claude:
    USER_GATE: Project to the `AskUserQuestion` tool.
    tools: Project shared `tools:` intent into Claude Code tool allowlists and Claude-form MCP tool IDs.
  copilot:
    USER_GATE: Project to the `ask_user` tool.
    tools: Project shared `tools:` intent into Copilot CLI tool allowlists and Copilot-form MCP tool IDs.
  codex:
    USER_GATE: Project to the `request_user_input` tool.
    tools: Project shared `tools:` intent into Codex tool metadata and Codex-form MCP or native tool IDs.
failure_policy:
  - Never silently drop a required capability during projection.
  - If no safe projection exists, preserve the shared intent in prose and stop at USER_GATE.
  - If the harness lacks an equivalent tool, record the mismatch explicitly instead of inventing a new shared term.
---

# Agent Tool Projection Policy

This policy defines how shared agent capability declarations are projected into
harness-native tool metadata. Shared files keep the canonical vocabulary.
Harness-specific instructions files and profile repos perform the projection.

## Canonical Shared Vocabulary

- `USER_GATE` is the only shared term for a blocking user approval or decision
  point.
- Shared agent definitions may use shared `tools:` wording to describe intended
  capabilities.
- Shared files must not replace canonical vocabulary with harness-native tool
  names.

## Projection Rules

### Claude

- Project `USER_GATE` to the `AskUserQuestion` tool.
- Project shared `tools:` intent into Claude Code tool allowlists.
- Project shared MCP capability references into Claude-form MCP tool IDs.

### Copilot

- Project `USER_GATE` to the `ask_user` tool.
- Project shared `tools:` intent into Copilot CLI tool allowlists.
- Project shared MCP capability references into Copilot-form MCP tool IDs.

### Codex

- Project `USER_GATE` to the `request_user_input` tool.
- Project shared `tools:` intent into Codex tool metadata.
- Project shared MCP capability references into Codex-form MCP or native tool
  IDs.

## Failure Policy

- Do not silently weaken or remove a required capability during projection.
- If a harness cannot safely represent shared `tools:` intent, keep the shared
  wording in prose and stop at `USER_GATE`.
- If a harness has no equivalent tool, document the mismatch explicitly rather
  than inventing a new shared vocabulary term.
