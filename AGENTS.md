# AGENTS.md

This file provides guidance to Copilot CLI when working with this repository.

## What This Repo Is

`al-dev-shared` is a **shared AI development plugin** — a unified library of AL/BC development skills, agents, and knowledge documents consumed by three AI coding harnesses:

- **Claude Code** (claude.ai/code) — Desktop app, CLI, and IDE extensions (see `CLAUDE.md`)
- **Copilot CLI** — Autonomous command-line agent (you are here)
- **Codex** — Autonomous development system (see `CODEX.md`)

It maintains one canonical authored surface (`profile-al-dev-shared/`) and generates harness-native projection artifacts for each consumer. This document covers Copilot CLI registration and usage; refer to `CLAUDE.md` (Claude Code) and `CODEX.md` (Codex) for harness-specific guidance.

This repository is not itself an AL project; it contains no `.al` source files.

### Copilot CLI Registration

`al-dev-shared` is registered in `~/.copilot/settings.json` as:

```json
"al-dev-shared": {
  "source": { "source": "directory", "path": "/Users/russelllaing/al-dev-shared" }
}
```

Copilot CLI consumes:

- **Shared skills** from `profile-al-dev-shared/skills/` (invoked as `/name`)
- **Generated agent projections** from `profile-al-dev-shared/generated/agents/copilot/`
- **Shared knowledge** from `profile-al-dev-shared/knowledge/` and `bc-code-intel-knowledge/`

## Shared Plugin Surface (All Harnesses)

All three harnesses consume the same authored source:

```text
profile-al-dev-shared/          # Canonical authored plugin surface
  skills/<name>/SKILL.md        # Skill definitions
  agents/<name>.md              # Agent definitions (harness-neutral)
  knowledge/                    # Generic workflow knowledge
  bc-code-intel-knowledge/      # BC Code Intelligence specialist knowledge
  markdown/                     # Markdown and Mermaid style guides
```

## Generated Projection Artifacts (Per-Harness Native Formats)

For harness-native tool execution, the projection layer generates harness-specific artifacts in `profile-al-dev-shared/generated/agents/copilot/` that map generic capability names (e.g., `USER_GATE`, `Read`, `Bash`) to Copilot CLI tool names (e.g., `ask_user`, `read`, `execute`).
.claude/agents/                 # Repo-local Claude maintainer agents for this source repo
.claude/skills/                 # Repo-local Claude maintainer skills for this source repo
.claude-plugin/marketplace.json # Marketplace registration schema
```

## Repo-Local Maintainer Tooling

`.claude/agents/` and `.claude/skills/` are repo-local Claude maintainer
tooling. They help audit, document, and iteratively improve this repository,
but they are not part of the distributed `al-dev-shared` plugin and must not
be treated as projection inputs or downstream harness-consumer artifacts.

## Generated Projection Artifacts (Per-Harness Native Formats)

For harness-native tool execution, the projection layer generates harness-specific artifacts in `profile-al-dev-shared/generated/agents/copilot/` that map generic capability names (e.g., `USER_GATE`, `Read`, `Bash`) to Copilot CLI tool names (e.g., `ask_user`, `read`, `execute`).

## Repo-Local Maintainer Tooling

`.claude/agents/` and `.claude/skills/` are repo-local Claude maintainer
tooling. They help audit, document, and iteratively improve this repository,
but they are not part of the distributed `al-dev-shared` plugin and must not
be treated as projection inputs, expected generated output, or downstream
harness-consumer artifacts.

## Skill File Format

Each skill is a markdown file in `profile-al-dev-shared/skills/<name>/SKILL.md` with YAML frontmatter. Skills use generic capability names; Copilot CLI applies projections automatically.

## Agent File Format

Each agent is a markdown file in `profile-al-dev-shared/agents/<name>.md` with YAML frontmatter. Agents declare generic capabilities in the `tools:` section; Copilot CLI consumes the generated Copilot-native projection.

## Key Architectural Patterns

**Complexity routing** (`knowledge/workflow-routing.md`): All skills classify tasks as TRIVIAL / SIMPLE / MEDIUM / COMPLEX and route accordingly.

**Workflow resilience** (`knowledge/workflow-resilience.md`): Multi-phase skills checkpoint to `.dev/progress.md` after each phase.

**`.dev/` directory convention**: All skill artifacts are written here — progress checkpoints, solution plans, code reviews, lint reports.

## Validation and Projection

To validate the plugin and regenerate Copilot CLI projections after changes to shared source:

```bash
# Validate that shared source has no harness-specific leakage
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared

# Validate agent structure
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents

# Regenerate projections for all harnesses (including Copilot CLI)
python3 scripts/generate-agent-projections.py
```

## Commit Conventions

project-type: tool
Full spec: `profile-al-dev-shared/knowledge/commit-conventions.md`
