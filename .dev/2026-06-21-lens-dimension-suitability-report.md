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
| Naming | Cross-object | 1 | `naming-convention-lens` |

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

## 2. Lens -> Dimension Classification

Verdict legend: **Correct** means the lens concern matches its declared dimension. Flagged verdict labels used by later sections are **Questionable** and **Misclassified**; neither appears in the table below because no lens concern conflicts with its declared dimension after the singleton exception documented in `docs/al-dev-naming-convention.md:23`.

| Lens | Declared dim. | Object | Actual concern (quoted) | Verdict | Evidence |
| --- | --- | --- | --- | --- | --- |
| design-agent-lens-caller-alignment | design | agent | "evaluates documented Inputs/Outputs against how spawning skills actually invoke each agent" | Correct | `.claude/agents/design-agent-lens-caller-alignment.md:3`; caller contract analysis is structural design fit, reinforced by caller-map checks at `.claude/agents/design-agent-lens-caller-alignment.md:36`. |
| design-agent-lens-model-fit | design | agent | "evaluates whether haiku/sonnet/opus assignment matches task complexity" | Correct | `.claude/agents/design-agent-lens-model-fit.md:3`; model tier selection is design-level execution fit, with explicit criteria at `.claude/agents/design-agent-lens-model-fit.md:39`. |
| design-agent-lens-scope-isolation | design | agent | "identifies agents with two clearly separable concerns" | Correct | `.claude/agents/design-agent-lens-scope-isolation.md:3`; concern separation is structural scope design, tested at `.claude/agents/design-agent-lens-scope-isolation.md:25`. |
| design-agent-lens-tool-hygiene | design | agent | "identifies tools declared in frontmatter but unused in the system prompt body" | Correct | `.claude/agents/design-agent-lens-tool-hygiene.md:3`; declared capability hygiene affects the agent's operational design surface, with red flags at `.claude/agents/design-agent-lens-tool-hygiene.md:34`. |
| design-agent-lens-usage-patterns | design | agent | "identifies single-use agents with small bodies and no documented contract" | Correct | `.claude/agents/design-agent-lens-usage-patterns.md:3`; inline candidacy is architectural placement, with criteria at `.claude/agents/design-agent-lens-usage-patterns.md:27`. |
| design-skill-lens-complexity | design | skill | "evaluates skills ranked by phase count to find high-phase skills with separable concerns" | Correct | `.claude/agents/design-skill-lens-complexity.md:3`; atomise/absorb decisions are workflow-structure design concerns, with gates at `.claude/agents/design-skill-lens-complexity.md:26`. |
| design-skill-lens-handoff-gaps | design | skill | "traces .dev/ file handoff chains to find established chains with obvious next steps or orphaned outputs" | Correct | `.claude/agents/design-skill-lens-handoff-gaps.md:3`; handoff-chain extension is cross-skill architecture, scoped at `.claude/agents/design-skill-lens-handoff-gaps.md:26`. |
| design-skill-lens-near-duplicates | design | skill | "identifies pairs with similar structure ... that could be merged" | Correct | `.claude/agents/design-skill-lens-near-duplicates.md:3`; merge candidacy is duplication and workflow-shape design, tested at `.claude/agents/design-skill-lens-near-duplicates.md:31`. |
| design-skill-lens-preplanning | design | skill | "checks whether pre-planning/brainstorming skills appear correctly in the Layer 1 diagram" | Correct | `.claude/agents/design-skill-lens-preplanning.md:3`; diagram placement and downstream handoff coverage are design concerns, with checks at `.claude/agents/design-skill-lens-preplanning.md:50`. |
| design-skill-lens-shared-backbone | design | skill | "identifies agent types used by 2+ skills whose invocation patterns could be documented in knowledge/" | Correct | `.claude/agents/design-skill-lens-shared-backbone.md:3`; shared invocation backbone extraction is architecture/duplication design, with pattern comparison at `.claude/agents/design-skill-lens-shared-backbone.md:39`. |
| design-skill-lens-surface-placement | design | skill | "flags skills that reference internal repo paths, exist to maintain/audit the plugin itself, and spawn no agents" | Correct | `.claude/agents/design-skill-lens-surface-placement.md:3`; surface placement is explicitly structural placement, with scoring signals at `.claude/agents/design-skill-lens-surface-placement.md:32`. |
| naming-convention-lens | naming | cross-object | "flags any tool name or output filename that violates docs/al-dev-naming-convention.md" | Correct | `.claude/agents/naming-convention-lens.md:3`; it reads the naming doc as source of truth at `.claude/agents/naming-convention-lens.md:34` and enforces the cross-object lens-agent exception at `.claude/agents/naming-convention-lens.md:42`. |
| quality-agent-lens-bloat | quality | agent | "detects oversized sections, dead conditional branches, repetitive instruction blocks, and historical commentary" | Correct | `.claude/agents/quality-agent-lens-bloat.md:3`; it judges prompt body maintainability rather than architecture, with bloat checks at `.claude/agents/quality-agent-lens-bloat.md:30`. |
| quality-agent-lens-clarity | quality | agent | "identifies ambiguous instructions, vague qualifiers, incomplete conditionals, and bash code blocks that are pseudo-code" | Correct | `.claude/agents/quality-agent-lens-clarity.md:3`; ambiguity and runnable prose are instruction-quality concerns, with checks at `.claude/agents/quality-agent-lens-clarity.md:55`. |
| quality-agent-lens-description | quality | agent | "compares description field against body content to detect disconnected verbs, missing outputs, and caller contract mismatches" | Correct | `.claude/agents/quality-agent-lens-description.md:3`; description/body drift is file-quality alignment, with comparison rules at `.claude/agents/quality-agent-lens-description.md:25`. |
| quality-agent-lens-name-fit | quality | agent | "compares agent name against primary verb and scope in description and body" | Correct | `.claude/agents/quality-agent-lens-name-fit.md:3`; semantic name fit is quality of discoverability, distinct from pattern conformance, with checks at `.claude/agents/quality-agent-lens-name-fit.md:25`. |
| quality-agent-lens-structure | quality | agent | "checks frontmatter completeness, tool canonicality, Inputs/Outputs tables, and header numbering" | Correct | `.claude/agents/quality-agent-lens-structure.md:3`; these are file-structure conventions, not architectural placement, with checks at `.claude/agents/quality-agent-lens-structure.md:36`. |
| quality-skill-lens-bloat | quality | skill | "detects oversized steps, dead conditional branches, repetitive instruction blocks, and historical commentary" | Correct | `.claude/agents/quality-skill-lens-bloat.md:3`; it judges skill-file maintainability, with bloat checks at `.claude/agents/quality-skill-lens-bloat.md:32`. |
| quality-skill-lens-clarity | quality | skill | "identifies ambiguous instructions, vague qualifiers, incomplete conditionals, and pseudo-code blocks" | Correct | `.claude/agents/quality-skill-lens-clarity.md:3`; clarity of executable instructions is quality, with checks at `.claude/agents/quality-skill-lens-clarity.md:52`. |
| quality-skill-lens-description | quality | skill | "compares description and trigger phrases against body content to detect disconnected verbs, missing outputs, and absent use cases" | Correct | `.claude/agents/quality-skill-lens-description.md:3`; description/trigger drift is file-quality alignment, with comparison rules at `.claude/agents/quality-skill-lens-description.md:36`. |
| quality-skill-lens-name-fit | quality | skill | "compares skill name against primary verb and scope in description and body" | Correct | `.claude/agents/quality-skill-lens-name-fit.md:3`; semantic fit between name, trigger, and behavior is quality, with checks at `.claude/agents/quality-skill-lens-name-fit.md:36`. |
| quality-skill-lens-structure | quality | skill | "checks frontmatter fields, argument-hint presence, output file naming, and header numbering" | Correct | `.claude/agents/quality-skill-lens-structure.md:3`; this is structural quality of the skill file, with checks at `.claude/agents/quality-skill-lens-structure.md:36`. |

### 2.1 Overlap Hotspot - Name-Fit vs Naming Dimension

The name-fit lenses and naming lens are split soundly. `quality-skill-lens-name-fit` says it "compares skill name against primary verb and scope in description and body" (`.claude/agents/quality-skill-lens-name-fit.md:3`) and then checks cases where the "Name implies X but body primarily does Y" (`.claude/agents/quality-skill-lens-name-fit.md:39`). `quality-agent-lens-name-fit` uses the same semantic test for agent files, comparing the "agent name against primary verb and scope in description and body" (`.claude/agents/quality-agent-lens-name-fit.md:3`) and checking when a name "conflicts with the agent's actual action verb" (`.claude/agents/quality-agent-lens-name-fit.md:31`). By contrast, `naming-convention-lens` flags names or output filenames that violate `docs/al-dev-naming-convention.md` (`.claude/agents/naming-convention-lens.md:3`) and enforces the documented lens-agent naming section, including the pattern, `design|quality` dimension vocabulary, `agent|skill` object vocabulary, examples, and the cross-object singleton exception (`docs/al-dev-naming-convention.md:11-26`). Verdict: name-fit is a semantic quality concern, while the naming dimension is convention conformance; the split is sound.

### 2.2 Overlap Hotspot - Structure (Quality) vs Design

The structure lenses use the word "Structural", but their actual checks target file conventions rather than architecture. `quality-agent-lens-structure` "checks frontmatter completeness, tool canonicality, Inputs/Outputs tables, and header numbering" (`.claude/agents/quality-agent-lens-structure.md:3`) and its checklist is filename convention, frontmatter fields, canonical source-vocabulary tools, invalid skill-only fields, Inputs/Outputs sections, and numbering consistency (`.claude/agents/quality-agent-lens-structure.md:36`). `quality-skill-lens-structure` similarly "checks frontmatter fields, argument-hint presence, output file naming, and header numbering" (`.claude/agents/quality-skill-lens-structure.md:3`) with a checklist for frontmatter/body conventions and dated `.dev` skill-output naming (`.claude/agents/quality-skill-lens-structure.md:36`). Verdict: these are quality concerns because they judge whether the instruction file itself follows structural conventions. They do not decide model tier, scope isolation, surface placement, handoff chains, or other architectural fit questions covered by the design dimension.

### 2.3 The Naming-Dimension Singleton (Naming-Convention-Lens)

`naming-convention-lens` is intentionally asymmetric. The naming convention says lens agents normally use `{dimension}-{object}-lens-{aspect}` (`docs/al-dev-naming-convention.md:14`) with `dimension` limited to `design` or `quality` and `object` limited to `agent` or `skill` (`docs/al-dev-naming-convention.md:16-17`), but it then declares: "`naming-convention-lens` is a cross-object lens" and "intentionally omits the `{dimension}` and `{object}` words" (`docs/al-dev-naming-convention.md:23-26`). The lens body mirrors that exception by requiring `*-lens-*` files to match the pattern while naming `naming-convention-lens` as "The single allowed exception" (`.claude/agents/naming-convention-lens.md:42`). Verdict: the singleton belongs to the naming dimension and is not misclassified, but the asymmetry is a structural weakness for Section 3 because inventory, row-count, and validator logic cannot infer its dimension/object from the filename prefix the same way they can for the other 21 lenses.
