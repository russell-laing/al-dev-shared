# Generated Agent Projections

This directory contains generated harness-native agent artifacts.

- `claude/` contains generated Claude Markdown manifests (`*.md`).
- `copilot/` contains generated Copilot Markdown manifests (`*.md`).
- `codex/` contains generated Codex TOML manifests (`*.toml`).

These files are derived from `profile-al-dev-shared/agents/*.md` and
`profile-al-dev-shared/knowledge/agent-tool-projection-policy.md`.

Do not hand-edit files in this directory. Edit the shared agent source or
projection policy instead, then regenerate with:

```bash
python3 scripts/generate_agent_projections.py
```
