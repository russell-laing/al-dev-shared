# Harness Token Map

Use this map when `/align-harness-repos` finds harness-branded wording in the
shared authored surface.

## Replacement rules

Apply the generic replacement only when the token appears in ordinary prose or a
shared-schema field name. If the token appears inside a fenced code block, flag
it for manual review instead of auto-replacing it.

| Harness-specific token | Neutral replacement |
| --- | --- |
| `AskUserQuestion` | `USER_GATE` |
| `subagent_type` | `agent_spawn` |
| `ask_user` | `USER_GATE` |
| `agent_type:` | `agent_spawn:` |
| `~/.claude` | `~/.harness-config` |
| `~/.copilot` | `~/.harness-config` |
| `Open Claude Code` | `Invoke the harness` |
| `start a new Copilot CLI session` | `Start a new harness session` |

## Review rule

When a finding falls outside the table or the surrounding text would become
ambiguous after replacement, stop and report it as a manual-review item instead
of guessing.
