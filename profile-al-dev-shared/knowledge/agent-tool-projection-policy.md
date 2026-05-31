---
shared_capabilities:
  - USER_GATE
  - shared `tools:` metadata
shared_model_aliases:
  - haiku
  - sonnet
  - opus
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
    "MCP: al-mcp-server":
      tool: "mcp__plugin_profile-claude-al-dev_al-mcp-server__<tool>"
    "MCP: bc-code-intelligence":
      tool: "mcp__plugin_profile-claude-al-dev_bc-code-intelligence-mcp__<tool>"
    "MCP: microsoft-docs":
      tool: "mcp__plugin_profile-claude-al-dev_microsoft_docs_mcp__<tool>"
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
    "MCP: al-mcp-server":
      tool: "al-mcp-server-<tool>"
    "MCP: bc-code-intelligence":
      tool: "bc-code-intelligence-mcp-<tool>"
    "MCP: microsoft-docs":
      tool: "microsoft_docs_mcp-<tool>"
  codex:
    USER_GATE:
      developer_instruction: request_user_input
    Read:
      native_capability: read files available in the active Codex session
    Write:
      native_capability: edit files available in the active Codex session
    Edit:
      native_capability: edit files available in the active Codex session
    Glob:
      native_capability: search files available in the active Codex session
    Grep:
      native_capability: search file contents available in the active Codex session
    Bash:
      native_capability: run shell commands allowed by the active Codex session
    "MCP: al-mcp-server":
      native_capability: use the AL symbol lookup MCP capability available in the active Codex session
    "MCP: bc-code-intelligence":
      native_capability: use the BC code intelligence MCP capability available in the active Codex session
    "MCP: microsoft-docs":
      native_capability: use the Microsoft Docs MCP capability available in the active Codex session
failure_policy:
  - Generation fails if a shared capability has no documented harness mapping.
  - Codex output must use documented TOML keys only; do not invent a synthetic tools field.
---

# Agent Tool Projection Policy

This policy defines how shared agent capability declarations are projected into
harness-native tool metadata. Shared files keep the canonical vocabulary.
Harness-specific instructions files and profile repos perform the projection.
For a repo-local maintainer walkthrough of the broader architecture and
historical context, see `docs/projection-layer-readme.md`.

## Canonical Shared Vocabulary

- `USER_GATE` is the only shared term for a blocking user approval or decision
  point.
- Shared agent definitions may use shared `tools:` wording to describe intended
  capabilities.
- Shared files must not replace canonical vocabulary with harness-native tool
  names.
- `rg` and `jq` are local CLI conventions, not shared capabilities and not
  projection targets.
- Shared skills and knowledge may recommend them inside Bash-based workflows.
- If `rg` or `jq` is unavailable, fall back to `grep` or Python in the workflow
  body rather than changing the projection contract.

## Maintainer Boundary and Regeneration Rules

### Authored vs. Generated Files

- Edit shared authored source directly in:
  - `profile-al-dev-shared/agents/*.md`
  - `profile-al-dev-shared/skills/<name>/SKILL.md`
  - `profile-al-dev-shared/knowledge/*.md`
- Never hand-edit generated projections in:
  - `profile-al-dev-shared/generated/agents/claude/`
  - `profile-al-dev-shared/generated/agents/copilot/`
  - `profile-al-dev-shared/generated/agents/codex/`

Generated projection files are derived artifacts. Any manual edits there will
be overwritten the next time projections are regenerated.

### When to Regenerate Projections

Regenerate projections after either of these changes:

- You edit shared agent source in `profile-al-dev-shared/agents/*.md`
- You change implemented projection behavior in
  `scripts/generate-agent-projections.py`

Policy-only or knowledge-only documentation edits do not require regeneration
by themselves. If you change the intended mapping contract, keep the generator
implementation aligned with that contract. The generator remains the runtime
source of truth for emitted projection artifacts.

### Minimum Projection Integrity Checks

Run these checks when changing shared projection behavior or the shared
authored surface around it:

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
python3 scripts/tests/test_generate_agent_projections.py
```

Use `profile-al-dev-shared/knowledge/harness-concepts.md` for the generic
vocabulary contract when replacing harness-specific names in shared source.

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
