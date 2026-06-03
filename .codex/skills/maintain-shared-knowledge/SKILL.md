---
name: maintain-shared-knowledge
description: Use when updating shared knowledge files, agent manifests, or harness instruction docs that must stay aligned with current Claude Code, Copilot CLI, and Codex capabilities.
---

# Maintain Shared Knowledge

## Overview

Keep shared knowledge current, harness-neutral, and projection-friendly. Use this skill when docs such as `profile-al-dev-shared/knowledge/*.md`, `profile-al-dev-shared/agents/*.md`, and downstream `AGENTS.md` / `CLAUDE.md` files need to reflect the current state of the harnesses and the generator mapping between shared intent and harness-native projections.

## When to Use

- A knowledge file describes harness behavior, tools, or workflow rules that may have drifted
- `agents/*.md` changed and the generated projections may need refresh
- `AGENTS.md`, `CLAUDE.md`, or `CODEX.md` need wording aligned with shared docs
- The repo’s projection policy or harness vocabulary changed
- A maintainer needs the latest real-world capabilities, not stale assumptions

## Live Verification Loop

1. Verify the current source of truth before editing:
   - shared docs in `profile-al-dev-shared/knowledge/`
   - shared agents in `profile-al-dev-shared/agents/`
   - projection policy in `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md`
   - harness vocabulary in `profile-al-dev-shared/knowledge/harness-concepts.md`
2. Verify live harness capability claims against current official docs or current runtime surfaces.
3. Update the shared authored file first.
4. If agent source changed, regenerate the harness projections.
5. Re-run neutrality and projection checks before claiming the docs are current.

## Quick Reference

| If you changed | Also check |
|---|---|
| `knowledge/*.md` | Harness neutrality, duplicate guidance, stale capability claims |
| `agents/*.md` | Generated projections, tool mappings, agent references |
| `AGENTS.md` / `CLAUDE.md` / `CODEX.md` | Local harness wording matches shared vocabulary |
| Projection policy docs | Generator behavior and emitted projections stay in sync |

## Common Mistakes

- Treating old docs as current without live verification
- Editing generated projection files by hand
- Letting shared knowledge drift into harness-specific tooling names
- Updating one harness instruction file but not the matching shared reference

## Required Checks

Run the repo validators that match the change:

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
python3 scripts/generate-agent-projections.py
```

Use the first two checks for authored-source changes and the third when agent source or projection mapping changes.
