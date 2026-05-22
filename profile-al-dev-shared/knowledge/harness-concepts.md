# Harness Concepts — Abstraction Contract

This file defines the generic vocabulary used across all `al-dev-shared`
skills and agents. Each profile repo implements concrete mappings in its
always-loaded instructions file (CLAUDE.md, AGENTS.md, etc.).

Shared capability-to-harness tool translation rules live in
`knowledge/agent-tool-projection-policy.md`. This file remains the prose
vocabulary contract; the projection policy defines how shared `tools:` intent
is translated into harness-native metadata.

## Skill Author Guidelines

When writing skills for `al-dev-shared`:

- Use generic concept names from the table below — never harness-specific names
- Use `USER_GATE` for any blocking approval or confirmation point
- Use `AL_DEV_SHARED_PLUGIN_ROOT` for any path into the plugin
- Reference MCP tools by capability name — never by raw harness-specific tool ID
- Use plain English for file operations ("read the file", "write to disk")
- When dispatching a named agent, write: `Dispatch agent: <namespace>:<agent-name>`

## Generic Concept Vocabulary

| Concept | Description | Claude Code | Copilot CLI |
|---|---|---|---|
| **project instructions file** | The file that provides the AI agent with project-specific instructions | `CLAUDE.md` | `AGENTS.md` |
| **harness settings file** | The file where harness-wide settings (e.g. API keys) are stored | `~/.claude/settings.json` | `~/.copilot/settings.json` |
| **AL_DEV_SHARED_PLUGIN_ROOT** | The installed path of the al-dev-shared plugin | `~/.claude/plugins/al-dev-shared/profile-al-dev-shared` | `~/.copilot/installed-plugins/<plugin-id>/profile-al-dev-shared` |
| **USER_GATE** | A blocking user-confirmation point; never continue past this without a user response | `AskUserQuestion` tool | `ask_user` tool |
| **explore agent** | A fast parallel exploration agent | `subagent_type: Explore` | `agent_type: "explore"` in task tool |
| **restart the agent** | Instruction to the user to start a new AI coding session | "Restart Claude Code" | "start a new Copilot CLI session" |
| **Dispatch agent: X** | Dispatch a named agent; X is the fully-qualified agent name (namespace:agent) | `Agent` tool with `subagent_type: X` | `task` tool with `agent_type: X` |
| **MCP: al-mcp-server** | AL symbol lookup, object definitions, references | `mcp__plugin_profile-claude-al-dev_al-mcp-server__<tool>` | `al-mcp-server-<tool>` |
| **MCP: bc-code-intelligence** | BC knowledge, specialist consultation, code analysis | `mcp__plugin_profile-claude-al-dev_bc-code-intelligence-mcp__<tool>` | `bc-code-intelligence-mcp-<tool>` |
| **MCP: microsoft-docs** | Microsoft documentation search and fetch | `mcp__plugin_profile-claude-al-dev_microsoft_docs_mcp__<tool>` | `microsoft_docs_mcp-<tool>` |

## USER_GATE Semantics

`USER_GATE` is a hard blocking point. Regardless of harness:

- The agent MUST stop and present the question/choice to the user
- The agent MUST NOT continue until a user response is received
- The question SHOULD include options where applicable
- There is no timeout — wait indefinitely

## AL_DEV_SHARED_PLUGIN_ROOT

Each profile's instructions file defines `AL_DEV_SHARED_PLUGIN_ROOT`. Skills use it for
validator script discovery:

```bash
VALIDATOR="$AL_DEV_SHARED_PLUGIN_ROOT/skills/<skill-name>/validate-*.py"
```

## Agent Dispatch Syntax

Skills reference agents using a harness-neutral format. The profile's harness
mapping defines the concrete dispatch mechanism:

```
Dispatch agent: <namespace>:<agent-name>
  description: "<short description>"
  prompt: "<prompt text>"
```

For explore agents, use:

```
Spawn an explore agent:
  purpose: <purpose>
  prompt: <prompt>
  output: <expected output>
```

## Agent Namespace Rules

| Agent location | Reference syntax |
|---|---|
| Shared agents (in al-dev-shared) | `al-dev-shared:<agent-name>` |
| Claude Code-only agents | `profile-claude-al-dev:<agent-name>` |
| Copilot CLI-only agents | `profile-copilot-al-dev:<agent-name>` |
