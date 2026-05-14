# Verification and Planning Parity Guide

This guide is the shared reference for cross-harness parity between Claude Code and Copilot CLI for:

1. Plan task verification
2. External claims verification
3. Target confirmation
4. Depth-first planning (proposal + critique + falsification)

## Cross-Harness Parity Checklist

- [ ] Theme 1 verification standard is aligned in CLAUDE.md and AGENTS.md
- [ ] al-dev-autonomous includes explicit post-task verify retry handling
- [ ] al-dev-plan includes evidence-summary verification and threshold gating
- [ ] al-dev-plan includes mandatory architect proposal/critique/falsification outputs
- [ ] Step 0 target confirmation wording is consistent across impacted skills
- [ ] Token/time impact guidance is documented in routing guidance

## Tool Mapping

| Need | Claude Code | Copilot CLI |
| --- | --- | --- |
| user decision gate | conversational prompt / ask tool | `ask_user` |
| subagent retry | `write_agent` | re-dispatch with updated prompt |
| pattern scan | `rg` | `rg` or `git diff \| grep` |

## Usage

- Reference this file when updating skill behavior across harnesses.
- Prefer additive edits and avoid diverging behavior wording between CLAUDE.md and AGENTS.md.
