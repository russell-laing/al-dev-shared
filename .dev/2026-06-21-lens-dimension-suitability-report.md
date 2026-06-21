---
title: Lens / Dimension Suitability Report
date: 2026-06-21
subject: Self-healing plugin-health audit lens and dimension suitability
sources:
  - .claude/agents/*lens*.md
  - .claude/skills/discover-plugin-health/SKILL.md
  - scripts/validate-lens-agents.py
status: draft
---

<!-- markdownlint-disable-next-line MD025 -->
# Lens / Dimension Suitability Report

## 0. Scope & Method

This report assesses whether the self-healing plugin-health audit's current lens and dimension model is suitable for ongoing use.

The assessment uses two axes:

1. **Lens coverage by dimension and object:** whether the active lens set gives each audited object type enough design, quality, and naming coverage without obvious gaps or duplication.
2. **Operational alignment:** whether discovery, dispatch, and validator registries agree about the active lens set that the audit can run.

Method: this pass is read-only except for this report. It uses live filesystem inventory from `.claude/agents`, direct source inspection of `discover-plugin-health`, and direct source inspection of `scripts/validate-lens-agents.py`. Counts below are from the current worktree at report creation time, not from prior summaries.

## 1. Lens Inventory

Total lenses on disk: **22** active non-archived lens agent files.

| Dimension | Object | Count | Lenses |
| --- | ---: | ---: | --- |
| Design | Agent | 5 | `caller-alignment`, `model-fit`, `scope-isolation`, `tool-hygiene`, `usage-patterns` |
| Design | Skill | 6 | `complexity`, `handoff-gaps`, `near-duplicates`, `preplanning`, `shared-backbone`, `surface-placement` |
| Quality | Agent | 5 | `bloat`, `clarity`, `description`, `name-fit`, `structure` |
| Quality | Skill | 5 | `bloat`, `clarity`, `description`, `name-fit`, `structure` |
| Naming | Shared | 1 | `naming-convention-lens` |

Active lens files observed:

```text
.claude/agents/design-agent-lens-caller-alignment.md
.claude/agents/design-agent-lens-model-fit.md
.claude/agents/design-agent-lens-scope-isolation.md
.claude/agents/design-agent-lens-tool-hygiene.md
.claude/agents/design-agent-lens-usage-patterns.md
.claude/agents/design-skill-lens-complexity.md
.claude/agents/design-skill-lens-handoff-gaps.md
.claude/agents/design-skill-lens-near-duplicates.md
.claude/agents/design-skill-lens-preplanning.md
.claude/agents/design-skill-lens-shared-backbone.md
.claude/agents/design-skill-lens-surface-placement.md
.claude/agents/naming-convention-lens.md
.claude/agents/quality-agent-lens-bloat.md
.claude/agents/quality-agent-lens-clarity.md
.claude/agents/quality-agent-lens-description.md
.claude/agents/quality-agent-lens-name-fit.md
.claude/agents/quality-agent-lens-structure.md
.claude/agents/quality-skill-lens-bloat.md
.claude/agents/quality-skill-lens-clarity.md
.claude/agents/quality-skill-lens-description.md
.claude/agents/quality-skill-lens-name-fit.md
.claude/agents/quality-skill-lens-structure.md
```

Validator-registry drift fact: `scripts/validate-lens-agents.py` defines `EXPECTED_AGENTS` from lines 47-69 and that registry enumerates 21 lens agent names. The active file `.claude/agents/design-skill-lens-surface-placement.md` exists and declares `name: design-skill-lens-surface-placement` at line 2, but that name is absent from `EXPECTED_AGENTS`. `discover-plugin-health` nevertheless treats it as part of the full plugin-surface lens set: its frontmatter explicitly calls out the `design-skill-lens-surface-placement` surface-scoped exception at lines 6-7, Phase 3 starts with the full lens set and excludes that lens only for `tooling` at lines 126-130, then dispatches `remaining_lenses` and checks returned identifiers at lines 132-173. The requested broad `grep -cE` probe returned 23 matching lines in this worktree because it also matches non-registry references such as `STRUCTURE_LENS` at line 22 and `SONNET_AGENTS` at line 93; the actual validator registry block remains 21 names.
