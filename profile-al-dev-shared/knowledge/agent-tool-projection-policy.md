---
shared_capabilities:
  - USER_GATE
  - shared `tools:` metadata
projection_rules:
  claude:
    USER_GATE:
      tool: AskUserQuestion
    Read:
      tool: Read
    Write:
      tool: Write
    Edit:
      tool: Edit
    Glob:
      tool: Glob
    Grep:
      tool: Grep
    Bash:
      tool: Bash
  copilot:
    USER_GATE:
      tool: ask_user
    Read:
      tool: read
    Write:
      tool: edit
    Edit:
      tool: edit
    Glob:
      tool: glob
    Grep:
      tool: grep
    Bash:
      tool: execute
  codex:
    USER_GATE:
      developer_instruction: request_user_input
    Read:
      native_capability: read-only file access through the active Codex session
    Write:
      native_capability: apply_patch or equivalent file-edit capability in the active Codex session
    Edit:
      native_capability: apply_patch or equivalent file-edit capability in the active Codex session
    Glob:
      native_capability: search files through the active Codex session
    Grep:
      native_capability: search file contents through the active Codex session
    Bash:
      native_capability: run shell commands allowed by the active Codex session
failure_policy:
  - Generation fails if a shared capability has no documented harness mapping.
  - Codex output must use documented TOML keys only; do not invent a synthetic tools field.
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

- `USER_GATE` projects to the `AskUserQuestion` tool.
- `Read`, `Write`, `Edit`, `Glob`, `Grep`, and `Bash` project to the matching
  Claude tool names.

### Copilot

- `USER_GATE` projects to the `ask_user` tool.
- `Read` projects to `read`.
- `Write` and `Edit` project to `edit`.
- `Glob` projects to `glob`.
- `Grep` projects to `grep`.
- `Bash` projects to `execute`.

### Codex

- `USER_GATE` projects to the `request_user_input` developer instruction.
- `Read` uses native read-only file access through the active Codex session.
- `Write` and `Edit` use `apply_patch` or an equivalent active-session edit
  capability.
- `Glob` and `Grep` use the active session's file and content search
  capabilities.
- `Bash` uses the active session's allowed shell command capability.

## Failure Policy

- Generation fails if a shared capability has no documented harness mapping.
- Codex output must use documented TOML keys only; do not invent a synthetic
  `tools` field.
