# CODEX.md

This file provides guidance to Codex when working with this repository.

## What This Repo Is

`al-dev-shared` is a **shared AI development plugin** — a unified library of AL/BC development skills, agents, and knowledge documents consumed by three AI coding harnesses:

- **Claude Code** (claude.ai/code) — Desktop app, CLI, and IDE extensions (see `CLAUDE.md`)
- **Copilot CLI** — Autonomous command-line agent (see `AGENTS.md`)
- **Codex** — Autonomous development system (you are here)

It maintains one canonical authored surface (`profile-al-dev-shared/`) and generates harness-native projection artifacts for each consumer. This document covers Codex registration and usage; refer to `CLAUDE.md` (Claude Code) and `AGENTS.md` (Copilot CLI) for harness-specific guidance.

This repository is not itself an AL project; it contains no `.al` source files.

### Codex Registration and Plugin Loading

`al-dev-shared` is registered as a Codex plugin and loaded into the active session environment. Codex consumes:

- **Shared skills** from `profile-al-dev-shared/skills/`
- **Generated agent projections** from `profile-al-dev-shared/generated/agents/codex/` (TOML format)
- **Shared knowledge** from `profile-al-dev-shared/knowledge/` and `bc-code-intel-knowledge/`

### Repo-Local Codex Skills

This repository may also contain repo-local Codex skills under `.codex/skills/`.
These are not part of the shared plugin surface and should be used only for
repository-specific workflows that should not be projected into other harnesses.

Repo-local skill names should follow the same verb-first convention used by the
maintainer tool naming policy in `.claude`: prefer `{verb}-{object}-{aspect}`
and keep the skill name aligned with the actual task it performs. Existing
repo-local names are kept where they are already established, but new skills
should follow the same pattern.

Current repo-local skills:

- `.codex/skills/generate-usage-report/` — converts harness-specific usage
  artifacts into neutral markdown reports and can optionally add Codex-derived
  local usage observations.
- `.codex/skills/cleanup-docs-health/` — removes dated health clutter without
  rewriting live evidence or current aliases.
- `.codex/skills/implement-plugin-map-findings/` — implements corrected
  plugin-map and tooling-surface findings plans.
- `.codex/skills/maintain-shared-knowledge/` — keeps shared knowledge and
  harness instruction docs aligned with current capabilities.
- `.codex/skills/maintain-skill-naming-conventions/` — keeps local skill
  names, descriptions, and inventory docs aligned with the intent they
  express.
- `.codex/skills/review-improvement-reports/` — reviews supplied usage or
  improvement reports and writes evidence-backed assessments without editing
  the shared plugin profile directly.
- `.codex/skills/research-harness-improvements/` — researches current AI
  harness practices and produces source-backed briefings for evidence-gated
  improvement review.
- `.codex/skills/heal-surface/` — performs a small, surface-specific self-heal
  pass near the end of a session.
- `.codex/skills/repeat-plan-execution/` — runs an established implementation
  plan task-by-task with isolated execution and review gates.
- `.codex/skills/review-self-healing-report/` — rechecks recommendation-heavy
  reports against live repo state before trusting rankings or counts.
- `.codex/skills/cleanup-superpowers-history/` — preserves provenance for
  `docs/superpowers/` history while removing obsolete raw artifacts.
- `.codex/skills/write-superpowers-plan-commentary/` — creates, appends, or
  losslessly consolidates review-only findings for Superpowers plans after live
  repo checks.
- `.codex/skills/extract-mermaid-diagrams/` — extracts Mermaid diagrams from
  Markdown and renders image artifacts plus metadata for AI visual analysis.

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

For harness-native task execution, the projection layer generates Codex-specific artifacts in `profile-al-dev-shared/generated/agents/codex/` in TOML format. These apply the mappings from `knowledge/agent-tool-projection-policy.md` to translate generic capability names (e.g., `USER_GATE`, `Read`, `Bash`) into Codex-native behavior directives.

## Skill File Format

Each skill is a markdown file in `profile-al-dev-shared/skills/<name>/SKILL.md` with YAML frontmatter. Skills use generic capability names; Codex applies projections automatically through the active session environment.

## Agent File Format

Each agent is a markdown file in `profile-al-dev-shared/agents/<name>.md` with YAML frontmatter. Agents declare generic capabilities in the `tools:` section; Codex consumes the generated Codex-native TOML projection.

## Key Architectural Patterns

**Complexity routing** (`knowledge/workflow-routing.md`): All skills classify tasks as TRIVIAL / SIMPLE / MEDIUM / COMPLEX and route accordingly.

**Workflow resilience** (`knowledge/workflow-resilience.md`): Multi-phase skills checkpoint to `.dev/progress.md` after each phase. Codex sessions respect these checkpoints for resumable workflows.

**`.dev/` directory convention**: All skill artifacts are written here — progress checkpoints, solution plans, code reviews, lint reports.

## Validation and Projection

To validate the plugin and regenerate Codex projections after changes to shared source:

```bash
# Validate that shared source has no harness-specific leakage
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared

# Validate agent structure
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents

# Regenerate projections for all harnesses (including Codex)
python3 scripts/generate-agent-projections.py
```

## Commit Conventions

project-type: tool
Full spec: `profile-al-dev-shared/knowledge/commit-conventions.md`
