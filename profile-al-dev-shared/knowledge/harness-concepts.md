# Harness Concepts — Abstraction Contract

This file defines the generic vocabulary used across all `al-dev-shared`
skills and agents. Each profile repo implements concrete mappings in its
always-loaded instructions file (CLAUDE.md, AGENTS.md, etc.).

Shared capability-to-harness tool translation rules live in
`knowledge/agent-tool-projection-policy.md`. This file remains the prose
vocabulary contract; the projection policy defines how shared `tools:` intent
is translated into harness-native metadata, including the documented
translation tables and fail-closed generation rules for Claude, Copilot, and
Codex projections.

## Skill Author Guidelines

When writing skills for `al-dev-shared`:

- Use generic concept names from the table below — never harness-specific names
- Use `USER_GATE` for any blocking approval or confirmation point
- Use `AL_DEV_SHARED_PLUGIN_ROOT` for any path into the plugin
- Reference MCP tools by capability name — never by raw harness-specific tool ID
- Use `AL semantic navigation` when guidance needs symbol-aware AL operations
  such as definition lookup, reference search, document symbols, hover/type
  information, or rename-impact checks
- Treat AL LSP as an optional provider of `AL semantic navigation` only when
  the active harness or adapter exposes it; do not assume availability from
  ALTool documentation alone
- Label symbol evidence as `AL LSP`, `AL MCP`, `text search`, or `unverified`
  whenever the distinction affects planning, implementation, or risk
- Use plain English for file operations ("read the file", "write to disk")
- When dispatching a named agent, write: `Dispatch agent: <namespace>:<agent-name>`

## Generic Concept Vocabulary

| Concept | Description | Claude Code | Copilot CLI | Codex |
|---|---|---|---|---|
| **project instructions file** | The file that provides the AI agent with project-specific instructions | `CLAUDE.md` | `AGENTS.md` | `AGENTS.md` |
| **harness settings file** | The file where harness-wide settings (e.g. API keys) are stored | `~/.claude/settings.json` | `~/.copilot/settings.json` | harness/runtime configuration outside the repo-local instructions contract |
| **AL_DEV_SHARED_PLUGIN_ROOT** | The installed path of the al-dev-shared plugin | `~/.claude/plugins/al-dev-shared/profile-al-dev-shared` | `~/.copilot/installed-plugins/<plugin-id>/profile-al-dev-shared` | session-defined plugin/workspace path supplied by the active Codex environment |
| **USER_GATE** | A blocking user-confirmation point; never continue past this without a user response | `AskUserQuestion` tool | `ask_user` tool | no single full-equivalence primitive; in Plan mode use `request_user_input`, otherwise stop in the session transcript and wait for the user's next message |
| **explore agent** | A fast parallel exploration agent | `subagent_type: Explore` | `agent_type: "explore"` in task tool | delegated subagent or parallel exploration workflow in the active Codex session |
| **restart the agent** | Instruction to the user to start a new AI coding session | "Restart Claude Code" | "start a new Copilot CLI session" | "start a new Codex session" |
| **Dispatch agent: X** | Dispatch a named agent; X is the fully-qualified agent name (namespace:agent) | `Agent` tool with `subagent_type: X` | `task` tool with `agent_type: X` | delegated agent workflow using the active Codex session's supported agent/subtask mechanism |
| **AL semantic navigation** | Preferred symbol-aware AL workspace operations: go-to-definition, find-references, document symbols, hover/type information, and rename/refactor impact checks. Providers are harness-dependent and optional. | AL LSP when exposed by Claude Code or an adapter; otherwise use supported AL symbol tools | AL LSP when exposed by Copilot CLI or an adapter; otherwise use supported AL symbol tools | AL LSP when exposed by the active Codex environment or adapter; otherwise use supported AL symbol tools |
| **MCP: al-mcp-server** | AL symbol lookup, object definitions, references | `mcp__plugin_profile-claude-al-dev_al-mcp-server__<tool>` | `al-mcp-server-<tool>` | active Codex MCP/tool binding for `al-mcp-server` |
| **MCP: bc-code-intelligence** | BC knowledge, specialist consultation, code analysis | `mcp__plugin_profile-claude-al-dev_bc-code-intelligence-mcp__<tool>` | `bc-code-intelligence-mcp-<tool>` | active Codex MCP/tool binding for `bc-code-intelligence` |
| **MCP: microsoft-docs** | Microsoft documentation search and fetch | `mcp__plugin_profile-claude-al-dev_microsoft_docs_mcp__<tool>` | `microsoft_docs_mcp-<tool>` | active Codex MCP/tool binding for `microsoft-docs` |

## USER_GATE Semantics

`USER_GATE` is a hard blocking point. Regardless of harness:

- The agent MUST stop and present the question/choice to the user
- The agent MUST NOT continue until a user response is received
- The question SHOULD include options where applicable
- There is no timeout — wait indefinitely

Codex limitation:

- Codex does not provide one general-purpose tool that is equivalent to the shared `USER_GATE` contract in every workflow state
- In Plan mode, `request_user_input` is the closest structured mechanism
- Outside Plan mode, the agent must enforce the contract behaviorally by asking the question in the session and doing no further work until the user replies

## AL Semantic Navigation and Evidence Labels

`AL semantic navigation` is a generic capability, not a required tool. Use it
when the active harness exposes a workspace-aware AL semantic provider such as
AL LSP through the harness itself or an adapter.

Preferred order for AL symbol questions:

1. `AL LSP` — workspace-semantic verification for go-to-definition,
   find-references, document symbols, hover/type information, and rename or
   refactor impact checks.
2. `AL MCP` — object/member/package symbol verification through
   `al-mcp-server`, including object definitions, member searches, and
   reference lookup.
3. `text search` — tightly scoped `rg` or file-read evidence when no semantic
   provider is available. Report this as text-verified only.
4. `unverified` — required symbol evidence was not established. Stop or
   escalate before implementation if the symbol is required.

Do not claim AL LSP is available because ALTool documentation exists. Use AL
LSP only when the active harness exposes an LSP-capable tool or adapter.

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
| Codex-only agents | `profile-codex-al-dev:<agent-name>` |
