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

## 3. Surface-Object x Dimension Coverage Matrix

Object-type counts from live filesystem commands: plugin agents **24**, plugin
skills **24**, tooling agents **29**, tooling skills **16**. The tooling-skill
count uses the workflow-contracted filter from `discover-plugin-health`, which
excludes adjacent `.claude/skills` tools without a `workflow:` block
(`.claude/skills/discover-plugin-health/SKILL.md:85-88`). The surface contract
maps `plugin` to `profile-al-dev-shared/` and `tooling` to `.claude/`
(`.claude/knowledge/health-filter-contract.md:31-35`). The dimension contract
maps `design`, `quality`, and `naming` to design lenses, quality lenses, and
the naming-convention lens respectively
(`.claude/knowledge/health-filter-contract.md:37-42`).

| Object type | design | quality | naming |
| --- | --- | --- | --- |
| plugin agents | 5 design-agent lenses | 5 quality-agent lenses | naming-convention-lens |
| plugin skills | 6 design-skill lenses | 5 quality-skill lenses | naming-convention-lens |
| tooling agents | 5 design-agent lenses | 5 quality-agent lenses | naming-convention-lens |
| tooling skills | 5 design-skill lenses (surface-placement excluded) | 5 quality-skill lenses | naming-convention-lens |

### 3.1 Dimension Weight Asymmetry

Design has 11 active lenses before surface filtering: 5 agent lenses and 6 skill
lenses. Quality has 10 active lenses: 5 agent lenses and 5 skill lenses. Naming
has one cross-object singleton. This is a real asymmetry, but it is not
automatically a defect. Section 2 found the naming singleton correctly scoped to
convention conformance rather than semantic name fit; semantic name/body drift is
already covered by `quality-agent-lens-name-fit` and
`quality-skill-lens-name-fit`.

The risk is operational rather than numeric: naming has no object-specific
redundancy if the singleton misses a convention class, while design and quality
can still catch adjacent problems through several object-specific lenses.
Naming is under-resourced only for future naming policy expansion. For the
current contract, one cross-object lens is acceptable if validation keeps the
singleton exception explicit and the quality name-fit lenses remain separate.

### 3.2 Formal vs Semantic Coverage Gaps

`design-skill-lens-complexity` still has meaningful signal for tooling skills.
Its required-context row is
"| `design-skill-lens-complexity` | `phase_counts`, `no_agent_skills` |"
(`profile-al-dev-shared/knowledge/lens-invocation-patterns.md:100`). Phase
counts and no-agent status are surface-neutral enough to evaluate workflow
shape, even though the remediation may differ for repo-local maintainer skills.

`design-skill-lens-handoff-gaps` still has meaningful signal for tooling
skills. Its required-context row is
"| `design-skill-lens-handoff-gaps` | `handoff_chains` |"
(`profile-al-dev-shared/knowledge/lens-invocation-patterns.md:102`). Tooling
skills often create or consume `.dev/` handoff artifacts, so handoff-chain
coverage is not merely a distributed-plugin concern.

`design-skill-lens-shared-backbone` is formally applicable to tooling skills
but semantically weaker there. Its required-context row is
"| `design-skill-lens-shared-backbone` | `agent_usage_counts` |"
(`profile-al-dev-shared/knowledge/lens-invocation-patterns.md:99`). It can
still find repeated agent-invocation patterns when tooling skills spawn agents,
but workflow-contracted tooling skills that do not use the distributed plugin
agent model provide little signal for a shared plugin backbone recommendation.

`design-skill-lens-near-duplicates` is also formally applicable but partly
weaker for tooling skills. Its required-context row is
"| `design-skill-lens-near-duplicates` | `agent_usage_counts`, `phase_counts` |"
(`profile-al-dev-shared/knowledge/lens-invocation-patterns.md:101`). Phase
counts transfer cleanly, but the `agent_usage_counts` half is less informative
for tooling skills that are small repo-local workflows or do not call agents.

`design-skill-lens-preplanning` is the clearest semantic coverage gap for
tooling skills. Its required-context row is
"| `design-skill-lens-preplanning` | `preplanning_skills`, `layer1_diagram_content` |"
(`profile-al-dev-shared/knowledge/lens-invocation-patterns.md:103`). That
context is anchored in Layer 1 skill-diagram placement, which is a distributed
plugin design surface; repo-local tooling skills can be useful without having a
meaningful Layer 1 position to audit.

### 3.3 Tooling-Skill Design Under-Coverage

The matrix shows tooling skills with 5 design-skill lenses, but effective design
coverage is thinner than that cell implies. `discover-plugin-health` explicitly
starts from the full lens set, then excludes
`design-skill-lens-surface-placement` for `tooling` because it "targets
distributed skills and produces only non-actionable Move false positives
against tooling-surface files" (`.claude/skills/discover-plugin-health/SKILL.md:126-130`).

After that formal exclusion, two included lenses have partial semantic signal
(`design-skill-lens-shared-backbone` and `design-skill-lens-near-duplicates`),
and one included lens is weak for tooling in most cases
(`design-skill-lens-preplanning`). The practical result is that tooling skills
receive strong design coverage for complexity and handoff-chain fit, weaker
coverage for shared-backbone and duplicate-shape analysis, little meaningful
coverage from preplanning placement, and no surface-placement coverage by
design. The matrix is formally accurate, but it overstates effective
tooling-skill design coverage unless those semantic gaps are considered.

## 4. Recommendations

> Read-only report - these are proposals, not applied changes. Feed accepted
> items into `/plan-plugin-findings` or a follow-up plan.

### R1 - Sync or document the validator registry gap (priority: High)

- **Change:** Add `design-skill-lens-surface-placement` to `EXPECTED_AGENTS` at `scripts/validate-lens-agents.py:47`, or document why the validator intentionally excludes a dispatched active lens.
- **Why:** Section 1 found 22 active lens files, but the validator registry has 21 entries and omits a lens that `discover-plugin-health` dispatches for plugin surface.
- **Tradeoff:** Adding it tightens validation but may require updating the validator's expected success message and any tests that assume 21 registered lenses.
- **Risk if unchanged:** The validator can continue passing while one active dispatched lens is outside registry enforcement.

### R2 - Keep the name-fit versus naming split explicit (priority: Low)

- **Change:** Add a short boundary note near `docs/al-dev-naming-convention.md:23` or the name-fit lens descriptions that semantic name/body drift belongs to name-fit while pattern conformance belongs to naming.
- **Why:** Section 2.1 found the split sound, with name-fit checking semantic behavior and `naming-convention-lens` checking documented naming rules.
- **Tradeoff:** Extra documentation adds a small amount of maintenance overhead when the naming policy changes.
- **Risk if unchanged:** Future cleanup work may incorrectly merge semantic name-fit checks into the naming-convention lens.

### R3 - Keep structure lenses under quality and document the boundary (priority: Low)

- **Change:** Add a one-sentence boundary note at `.claude/agents/quality-agent-lens-structure.md:31` and `.claude/agents/quality-skill-lens-structure.md:31` that structural conventions are file-quality checks, not design placement checks.
- **Why:** Section 2.2 found the structure lenses correctly placed under quality because they check frontmatter, tool canonicality, output paths, and header conventions.
- **Tradeoff:** The lens prompts become slightly longer for a distinction that is already inferable from their checklists.
- **Risk if unchanged:** Future audits may relabel structure as design based on wording instead of actual checks.

### R4 - Decide whether the naming singleton should split if policy expands (priority: Med)

- **Change:** Add a decision gate near `docs/al-dev-naming-convention.md:23` requiring object-specific naming lenses if future policy adds materially different agent and skill naming rules.
- **Why:** Sections 2.3 and 3.1 found the singleton acceptable now but structurally asymmetric if naming policy grows beyond one cross-object rule set.
- **Tradeoff:** A decision gate avoids premature lens proliferation but leaves current coverage centralized in one lens.
- **Risk if unchanged:** Expanded naming rules could accumulate in a singleton lens with no object-specific redundancy.

### R5 - Add or scope a tooling-skill design lens (priority: Med)

- **Change:** Add a follow-up tooling-skill-specific design lens, or narrow the semantic scope documented around `.claude/skills/discover-plugin-health/SKILL.md:126` and `profile-al-dev-shared/knowledge/lens-invocation-patterns.md:99`.
- **Why:** Section 3.3 found tooling skills have no surface-placement coverage by design, weak preplanning signal, and only partial shared-backbone or near-duplicate signal.
- **Tradeoff:** A new lens improves tooling-skill coverage but increases dispatch fan-out and review volume.
- **Risk if unchanged:** The matrix will continue to overstate effective tooling-skill design coverage.

## Appendix A - Evidence Commands

### Inventory and Counts

```bash
find .claude/agents -maxdepth 1 -name '*lens*.md' ! -path '*/archived/*' | sort
```

Value produced: 22 active non-archived lens agent paths, matching the Section 1 inventory list.

```bash
find .claude/agents -maxdepth 1 -name '*lens*.md' ! -path '*/archived/*' | wc -l
```

Value produced: `22`.

```bash
find .claude/agents -maxdepth 1 -name 'design-agent-lens-*.md' | wc -l
```

Value produced: `5`.

```bash
find .claude/agents -maxdepth 1 -name 'design-skill-lens-*.md' | wc -l
```

Value produced: `6`.

```bash
find .claude/agents -maxdepth 1 -name 'quality-agent-lens-*.md' | wc -l
```

Value produced: `5`.

```bash
find .claude/agents -maxdepth 1 -name 'quality-skill-lens-*.md' | wc -l
```

Value produced: `5`.

```bash
find profile-al-dev-shared/agents -maxdepth 1 -name '*.md' | wc -l
```

Value produced: `24`.

```bash
find profile-al-dev-shared/skills -mindepth 2 -maxdepth 2 -name 'SKILL.md' | wc -l
```

Value produced: `24`.

```bash
find .claude/agents -maxdepth 1 -name '*.md' | wc -l
```

Value produced: `29`.

```bash
find .claude/skills -mindepth 2 -maxdepth 2 -name 'SKILL.md' -exec grep -l '^workflow:' {} \; | wc -l
```

Value produced: `16`.

### Registry Checks

```bash
grep -nE '"(design|quality)-.*-lens-|"naming-convention-lens"' scripts/validate-lens-agents.py
```

Value produced: 23 matching lines because the broad grep includes `STRUCTURE_LENS` and `SONNET_AGENTS` references as well as the registry block.

```bash
grep -cE '"(design|quality)-.*-lens-|"naming-convention-lens"' scripts/validate-lens-agents.py
```

Value produced: `23`.

```bash
python3 -c "import ast, pathlib; tree=ast.parse(pathlib.Path('scripts/validate-lens-agents.py').read_text()); vals=[]; [vals := ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign) and any(getattr(t, 'id', None)=='EXPECTED_AGENTS' for t in node.targets)]; print(len(vals)); print('design-skill-lens-surface-placement' in vals)"
```

Value produced:

```text
21
False
```

```bash
grep -n "design-skill-lens-surface-placement" scripts/validate-lens-agents.py
```

Value produced: no output, exit code 1.

### Source Spot Checks

```bash
nl -ba scripts/validate-lens-agents.py | sed -n '47,70p'
```

Value produced: `EXPECTED_AGENTS` spans lines 47-69 and lists 21 names.

```bash
nl -ba docs/al-dev-naming-convention.md | sed -n '11,28p'
```

Value produced: lens naming pattern plus the `naming-convention-lens` exception at lines 23-25.

```bash
nl -ba .claude/agents/quality-agent-lens-structure.md | sed -n '1,45p'
```

Value produced: frontmatter and structural convention checks, including filename, frontmatter, tool, Inputs/Outputs, and heading checks.

```bash
nl -ba .claude/agents/design-agent-lens-tool-hygiene.md | sed -n '1,50p'
```

Value produced: a direct design-agent lens spot check showing tool-hygiene inputs, design concern, red flags, and severity rules.

```bash
nl -ba .claude/agents/design-skill-lens-surface-placement.md | sed -n '1,45p'
```

Value produced: a direct design-skill lens spot check showing surface-placement scope, maintainer-surface guard, and Move scoring signals.

```bash
nl -ba .claude/agents/quality-skill-lens-name-fit.md | sed -n '1,48p'
```

Value produced: the skill name-fit lens checks semantic name, description, body, and trigger alignment.

```bash
nl -ba .claude/agents/naming-convention-lens.md | sed -n '1,58p'
```

Value produced: the naming-convention lens reads the convention doc and enforces the single lens-agent exception.

```bash
nl -ba .claude/skills/discover-plugin-health/SKILL.md | sed -n '120,135p'
```

Value produced: dispatch excludes `design-skill-lens-surface-placement` only for tooling surface at lines 126-130.

```bash
nl -ba profile-al-dev-shared/knowledge/lens-invocation-patterns.md | sed -n '96,105p'
```

Value produced: design-skill required context fields for shared-backbone, complexity, near-duplicates, handoff-gaps, preplanning, and surface-placement.

### Final Self-Review Commands

```bash
REPO=$(git rev-parse --show-toplevel)
```

Value produced: `/Users/russelllaing/al-dev-shared/.worktrees/lens-dimension-suitability-report`.

```bash
RPT="$REPO/.dev/2026-06-21-lens-dimension-suitability-report.md"
```

Value produced: report path variable set.

```bash
grep -nE 'TO''DO|TB''D|Y{4}-MM-DD|\[d''ate\]|fi''ll in|<''[a-z ]+>' "$RPT" && echo "FAIL: placeholders" || echo "OK: no placeholders"
```

Value produced after final run: `OK: no placeholders`.

```bash
grep -cE '^### R[0-9]+' "$RPT"
```

Value produced after final run: `5`.

```bash
grep -c '\*\*Change:\*\*' "$RPT"
```

Value produced after final run: `5`.

```bash
grep -c '\*\*Why:\*\*' "$RPT"
```

Value produced after final run: `5`.

```bash
grep -c '\*\*Tradeoff:\*\*' "$RPT"
```

Value produced after final run: `5`.

```bash
grep -c '\*\*Risk if unchanged:\*\*' "$RPT"
```

Value produced after final run: `5`.

```bash
python3 "$REPO/scripts/validate-lens-agents.py" 2>&1 | tail -1
```

Value produced after final run: `PASS - 21 agents valid, 1 dispatch skill(s) checked.`

```bash
grep -n 'surface-placement' "$REPO/scripts/validate-lens-agents.py" || echo "still ABSENT - recommendation R-registry stands"
```

Value produced after final run: `still ABSENT - recommendation R-registry stands`.

```bash
markdownlint "$RPT"
```

Value produced after final run: no output, exit code 0.

```bash
ls -la "$RPT"
```

Value produced after final run: file present at `/Users/russelllaing/al-dev-shared/.worktrees/lens-dimension-suitability-report/.dev/2026-06-21-lens-dimension-suitability-report.md`.

```bash
wc -l "$RPT"
```

Value produced after final run: `478` lines.

```bash
git -C "$REPO" status --short .dev/2026-06-21-lens-dimension-suitability-report.md
```

Value produced after final committed run: no output, meaning the report path was clean.
