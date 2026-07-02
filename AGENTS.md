# AGENTS.md

This file provides **harness-agnostic** guidance for AGENTS-compatible runtimes working in this repository.

## What This Repo Is

`al-dev-shared` is a shared AI development plugin for AL/BC workflows. It contains reusable:

- skills
- agents
- knowledge
- projection tooling

This repository is **not** an AL app project and does not contain `.al` source as its primary product.

## Canonical Source and Projection Boundary

The canonical authored surface is:

```text
profile-al-dev-shared/
  skills/<name>/SKILL.md
  agents/<name>.md
  knowledge/
  bc-code-intel-knowledge/
  markdown/
```

Generated harness-native artifacts are under:

```text
profile-al-dev-shared/generated/agents/
  claude/
  copilot/
  codex/
```

Do not hand-edit generated projection artifacts. Update shared authored files and regenerate projections.

## Shared Surface Rules

When editing shared authored content:

- keep wording harness-neutral
- use generic vocabulary from `profile-al-dev-shared/knowledge/harness-concepts.md`
- keep tool/capability mapping contracts aligned with `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md`
- avoid introducing harness-branded operational instructions into shared files

Intentional mapping documents are allowed to name harnesses where comparison is the purpose.

## Repo-Local Maintainer Tooling

Repository-local harness tooling (for example `.claude/` or `.codex/`) is maintainer infrastructure, not distributed shared plugin content.

It may inspect shared source and generated artifacts, but any outputs written back to shared content should remain harness-agnostic.

Repo-local skill names should follow the same verb-first convention used by the `.claude` naming policy: prefer `{verb}-{object}-{aspect}` and keep the name aligned with the actual task it performs.

Current repo-local Codex skills:

- `.codex/skills/generate-usage-report/` — converts harness-specific usage artifacts into neutral markdown reports and can optionally add Codex-derived local usage observations.
- `.codex/skills/review-improvement-reports/` — reviews supplied usage or improvement reports and writes evidence-backed assessments without editing the shared plugin profile directly.
- `.codex/skills/research-harness-improvements/` — researches current AI harness practices and produces source-backed briefings for evidence-gated improvement review.
- `.codex/skills/heal-surface/` — performs a small, surface-specific self-heal pass near the end of a session.
- `.codex/skills/review-self-healing-report/` — rechecks recommendation-heavy reports against live repo state before trusting rankings or counts.
- `.codex/skills/validate-health-loop-second-opinion/` — performs bounded, report-only second-opinion validation of one Claude-produced plugin-health artifact before the maintainer acts on it.
- `.codex/skills/cleanup-superpowers-history/` — preserves provenance for `docs/superpowers/` history while removing obsolete raw artifacts.
- `.codex/skills/write-superpowers-plan-commentary/` — creates, appends, or losslessly consolidates review-only findings for Superpowers plans after live repo checks.
- `.codex/skills/extract-mermaid-diagrams/` — extracts Mermaid diagrams from Markdown and renders image artifacts plus metadata for AI visual analysis.
- `.codex/skills/generate-duplicate-text-report/` — scans active repository surfaces for exact repeated text blocks and writes durable Markdown reports for maintainer review.
- `.codex/skills/generate-benchmark-report/` — creates benchmark baseline reports from live health artifacts and includes a final live-state validation loop that re-checks counts and patches drift before the report is trusted.

## Core Workflow Contracts

### 1. Complexity routing

Use `profile-al-dev-shared/knowledge/workflow-routing.md` to classify work as TRIVIAL, SIMPLE, MEDIUM, or COMPLEX and route accordingly.

### 2. Resumable multi-phase workflows

Use `profile-al-dev-shared/knowledge/workflow-resilience.md` and `.dev/progress.md` checkpoints for multi-phase execution.

### 3. Artifact contracts

Use `profile-al-dev-shared/knowledge/artifact-contracts.md` as the source of truth for required handoff artifacts and completion evidence.

### 4. Skill trigger regression scenarios

Use `profile-al-dev-shared/skills/<name>/tests/scenarios.yaml` and `profile-al-dev-shared/knowledge/skill-test-format.md` when adding or fixing skill trigger behavior.

## Preferred Editing Practice

1. Edit shared source only (skills/agents/knowledge).
2. Keep changes scoped and pattern-consistent with neighboring files.
3. Regenerate projections when shared agents or projection logic changes.
4. Run validations before finalizing.

## Validation Commands

Run the applicable checks after shared-surface changes:

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
python3 scripts/validate_lens_agents.py --path profile-al-dev-shared/agents
python3 scripts/validate_knowledge_quality.py --path profile-al-dev-shared/knowledge
python3 scripts/tests/test_generate_agent_projections.py
```

Projection regeneration:

```bash
python3 scripts/generate_agent_projections.py
python3 scripts/generate_maintainer_guide.py
```

Use `docs/development_commands.md` for the full maintainer command set.

## Documentation Quality Standards

- Keep markdown structurally valid (headings, fenced code blocks with language tags, spacing).
- Avoid placeholder text (`TODO`, `TBD`, literal `YYYY-MM-DD`, unresolved templates).
- When reporting counts of skills/agents, verify with filesystem queries rather than manual estimates.

Example count checks:

```bash
find profile-al-dev-shared/skills -name "SKILL.md" | wc -l
find profile-al-dev-shared/agents -name "*.md" | wc -l
```

## Planning and Execution Guidance

- For small, unambiguous changes: execute directly with focused verification.
- For medium or ambiguous changes: use `plan` style competitive planning before implementation.
- For large cross-surface changes: use a staged plan with explicit checkpoints and integration reviews.

## Commit Conventions

Project type: `tool`.

Source of truth: `profile-al-dev-shared/knowledge/commit-conventions.md`.
