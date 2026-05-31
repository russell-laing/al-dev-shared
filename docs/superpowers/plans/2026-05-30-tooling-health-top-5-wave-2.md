# Tooling Health Top-5 Wave 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement 4 remaining high-severity actions from `docs/health/2026-05-30-tooling-health.md` (Item 2 — model field for all 21 lens agents — was verified complete before this plan was written: all agents already have `model: haiku`).

**Architecture:** 4 tasks executed sequentially from smallest to largest impact. Each task is self-contained and verifiable without depending on the others. Map merge (Task 4) is last to avoid breaking callers before the `--no-update` replacement is live.

**Tech Stack:** Markdown SKILL.md files, YAML frontmatter, `profile-al-dev-shared/knowledge/` documents.

---

## File Structure

**Create:**
- `profile-al-dev-shared/knowledge/map-suggestion-templates.md` — Trim/Remodel/Split/Inline/Align/Atomise/Connect/Merge/Promote/Extend templates extracted from `draft-map-suggestions`
- `.claude/skills/discover-skill-design/SKILL.md` — Phases 1–2 of `analyze-skill-design` as standalone discovery skill
- `.claude/skills/discover-agent-design/SKILL.md` — Phases 1–2 of `analyze-agent-design` as standalone discovery skill

**Modify:**
- `.claude/skills/audit-knowledge-quality/SKILL.md` — add argument-hint, replace TodoWrite with TaskCreate, specify subagent return format
- `.claude/skills/plan-map-changes/SKILL.md` — add skip action; trim U1–U3 body to knowledge reference
- `.claude/skills/draft-map-suggestions/SKILL.md` — replace Phase 3 template blocks with knowledge reference
- `.claude/skills/audit-quality/SKILL.md` — consolidate duplicate agent/skill dispatch blocks into one parameterized block
- `.claude/skills/analyze-skill-design/SKILL.md` — replace Phases 1–2 with `/discover-skill-design` invocation
- `.claude/skills/analyze-agent-design/SKILL.md` — replace Phases 1–2 with `/discover-agent-design` invocation
- `.claude/skills/review-agent-map/SKILL.md` — add `--no-update` flag and Phase 5b audit-only exit
- `.claude/skills/review-skill-map/SKILL.md` — add `--no-update` flag and Phase 4b audit-only exit
- `.claude/skills/sync-documentation-maps/SKILL.md` — replace `audit-*/update-*` calls with `review-* --no-update` / `review-*`
- `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md` — add Universal checks U1–U3 section
- `CLAUDE.md` — update audit-only skill reference

**Archive (move directory + add notice):**
- `.claude/skills/audit-agents-against-map/` → `.claude/skills/archived/audit-agents-against-map/`
- `.claude/skills/update-agent-map/` → `.claude/skills/archived/update-agent-map/`
- `.claude/skills/audit-skills-against-map/` → `.claude/skills/archived/audit-skills-against-map/`
- `.claude/skills/update-skill-map/` → `.claude/skills/archived/update-skill-map/`

---

## Task 1: Fix Clarity Blockers in audit-knowledge-quality and plan-map-changes (Item 4)

**Files:**
- Modify: `.claude/skills/audit-knowledge-quality/SKILL.md` (currently 142 lines)
- Modify: `.claude/skills/plan-map-changes/SKILL.md` (currently 174 lines)

---

- [ ] **Step 1: Add argument-hint and expand description in audit-knowledge-quality**

In `.claude/skills/audit-knowledge-quality/SKILL.md`, replace this frontmatter block (exact string):

```
---
name: audit-knowledge-quality
description: Audit knowledge files for stub sections and structural issues.
---
```

with:

```
---
name: audit-knowledge-quality
description: >-
  Audit knowledge files for stub sections and structural issues.
  Dispatches parallel agents for large audit scopes (4+ files).
argument-hint: "[--path <directory>] [--verbose]"
---
```

- [ ] **Step 2: Replace undefined TodoWrite with TaskCreate**

In `.claude/skills/audit-knowledge-quality/SKILL.md`, find (exact string):

```
Before analyzing any file, create one TodoWrite todo per flagged file named `[issue-type] [filename]`. Mark each todo in-progress when analysis begins, complete when the file analysis is written to findings.
```

Replace with:

```
Before analyzing any file, create one task per flagged file using `TaskCreate` named `[issue-type] [filename]`. Update each task to `in_progress` when analysis begins, `completed` when the file analysis is written to findings.
```

- [ ] **Step 3: Specify parallel subagent return format**

In `.claude/skills/audit-knowledge-quality/SKILL.md`, find (exact string):

```
Dispatch one Explore subagent per file to: read the knowledge file, search for referencing agent/skill, and run the gap/severity assessment (steps 1–4). Each agent returns a structured analysis record. Collect all records before proceeding to Phase 3.
```

Replace with:

```
Dispatch one Explore subagent per file to: read the knowledge file, search for referencing agent/skill, and run the gap/severity assessment (steps 1–4). Each subagent must return YAML with fields: `{file, issue_type, gap_description, severity}`. Collect all records before proceeding to Phase 3.
```

- [ ] **Step 4: Add skip action for infeasible suggestions in plan-map-changes**

In `.claude/skills/plan-map-changes/SKILL.md`, find the closing triple-backtick of the rubber duck record block. The block ends with:

```
Verdict:      proceed | modify [reason] | skip [reason]
```
```

(that is: `Verdict:      proceed | modify [reason] | skip [reason]` followed by a closing ```` ``` ````). After the closing triple-backtick, insert:

```

If the verdict is `skip [reason]`, exclude that suggestion from Phase 3 entirely — do not create a plan task for it. Record skipped suggestions in a `## Skipped` section at the end of the plan file with the reason noted.
```

- [ ] **Step 5: Verify Task 1**

```bash
grep -n "argument-hint" /Users/russelllaing/al-dev-shared/.claude/skills/audit-knowledge-quality/SKILL.md
grep -n "TaskCreate" /Users/russelllaing/al-dev-shared/.claude/skills/audit-knowledge-quality/SKILL.md
grep -n "YAML with fields" /Users/russelllaing/al-dev-shared/.claude/skills/audit-knowledge-quality/SKILL.md
grep -c "skip \[reason\].*exclude\|exclude.*skip \[reason\]" /Users/russelllaing/al-dev-shared/.claude/skills/plan-map-changes/SKILL.md
wc -l /Users/russelllaing/al-dev-shared/.claude/skills/audit-knowledge-quality/SKILL.md /Users/russelllaing/al-dev-shared/.claude/skills/plan-map-changes/SKILL.md
```

Expected: all 4 greps match exactly once; `audit-knowledge-quality` is 145–150 lines; `plan-map-changes` is 177–183 lines.

- [ ] **Step 6: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  .claude/skills/audit-knowledge-quality/SKILL.md \
  .claude/skills/plan-map-changes/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "fix(tooling): resolve clarity blockers in audit-knowledge-quality and plan-map-changes"
```

---

## Task 2: Extract Template Prose to Knowledge Files (Item 5)

**Files:**
- Create: `profile-al-dev-shared/knowledge/map-suggestion-templates.md`
- Modify: `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`
- Modify: `.claude/skills/draft-map-suggestions/SKILL.md` (currently 231 lines)
- Modify: `.claude/skills/plan-map-changes/SKILL.md`
- Modify: `.claude/skills/audit-quality/SKILL.md` (currently 276 lines)

---

- [ ] **Step 1: Create knowledge/map-suggestion-templates.md**

Write `profile-al-dev-shared/knowledge/map-suggestion-templates.md` with this exact content:

```markdown
# Map Suggestion Templates

Suggestion format templates used by `/draft-map-suggestions` when writing to
map Observations sections. Reference this file instead of embedding templates
inline in the skill body.

---

## Agent templates (--type agent)

### Trim

```
**Trim: al-dev-<name>**
Observation: Tools list includes [tool]; system prompt body contains no [tool] usage.
Suggestion: Remove [tool] from the tools list in the agent frontmatter.
Trade-off: Minimal — tool wasn't used; tighter least-privilege posture.
```

### Remodel

```
**Remodel: al-dev-<name>**
Observation: Agent performs [task description]; currently assigned [current-model].
Suggestion: Change model to [new-model] — task [does/does not] require multi-file synthesis.
Trade-off: [Faster + cheaper / More capable]; justified because [reason].
```

### Split

```
**Split: al-dev-<name>**
Observation: System prompt describes [concern A] and [concern B] — separable concerns.
Suggestion: Extract [concern B] into a new agent al-dev-<new-name>.
Trade-off: New agent file to maintain; each agent's scope becomes narrower and easier to evolve.
```

### Inline

```
**Inline: al-dev-<name>**
Observation: Spawned only by /skill-name; [N]-line system prompt; no Inputs/Outputs documented.
Suggestion: Absorb system prompt into /skill-name's dispatch block; delete the agent file.
Trade-off: Less indirection; agent no longer reusable if a second caller is added later.
```

### Align

```
**Align: al-dev-<name>**
Observation: /skill-name passes [file/param X]; agent Inputs table does not document [X].
Suggestion: Update the agent's Inputs table to reflect the actual caller contract.
Trade-off: Documentation-only change; prevents future caller confusion.
```

---

## Skill templates (--type skill)

### Atomise

```
**Atomise: /skill-name**
Observation: Phases N–M handle X; phases N–M handle Y — separable concerns.
Suggestion: Extract [phase group] into /new-skill-name.
Trade-off: New skill to learn; each skill's scope becomes narrower and clearer.
```

### Connect

```
**Connect: /skill-a and /skill-b**
Observation: Both spawn [agent-type] with the same pattern but define it independently.
Suggestion: Document the canonical spawn pattern in knowledge/[pattern-name].md;
  have both skills reference it.
Trade-off: Small authoring cost; drift is prevented when the pattern needs updating.
```

### Merge

```
**Merge: /skill-a + /skill-b**
Observation: /skill-b is /skill-a plus [small delta]; users must choose between two
  near-identical skills.
Suggestion: Add [delta] as an option to /skill-a; archive /skill-b.
Trade-off: Simpler skill list; /skill-a's interface becomes slightly broader.
```

### Promote

```
**Promote: [agent usage pattern]**
Observation: [agent-type] is invoked by N skills. The invocation is copy-pasted
  rather than shared.
Suggestion: Write a canonical invocation template in knowledge/ and link from each
  skill that uses it.
Trade-off: One canonical source; callers adapt slightly to reference it.
```

### Extend

```
**Extend: [gap description]**
Observation: The [X → Y → Z] chain is well-established but stops at Z.
Suggestion: A /new-skill-name that consumes Z's output would complete the natural
  workflow and enable [use case].
Trade-off: Adds scope; only worth building if the use case is frequent.
```
```

After writing, verify:

```bash
ls -la /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/map-suggestion-templates.md
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/map-suggestion-templates.md
grep -c "^### " /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/map-suggestion-templates.md
```

Expected: file exists, 95–110 lines, 10 section headers (Trim through Extend).

- [ ] **Step 2: Add Universal checks U1–U3 to map-change-rubber-duck-checks.md**

In `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`, replace the header block (exact string):

```
# Map Change Rubber-Duck Checks

Type-specific verification checks for the `/plan-map-changes` skill Phase 2.
Apply these after completing the Universal checks (U1–U3) documented in the
skill body. Each section corresponds to one suggestion type.

---
```

with:

```
# Map Change Rubber-Duck Checks

Verification checks for the `/plan-map-changes` skill Phase 2. The Universal
checks (U1–U3) below apply to every suggestion type. Each section below the
separator is a type-specific check.

---

## Universal checks (all suggestion types)

**U1. Read the affected files in full.**
Do NOT infer current state from the plugin map — read the actual SKILL.md
or knowledge file. The map is a snapshot; the code is the truth.

**U2. Verify referenced artifacts exist.**
If the suggestion mentions a validator script, helper file, or Python tool:
run `ls` on the directory. Build plans around files that exist, not files
that are assumed to exist.

```bash
ls profile-al-dev-shared/skills/<skill-name>/
```

**U3. Check whether the suggested flag, name, or path captures the full scope.**
Read the source skill. List every structural difference between the skills being
merged or connected. A flag named after one feature but activating three is a
scope gap — rename or expand the scope in the plan.

---

## Type-specific checks

Each section below corresponds to one suggestion type.

---
```

- [ ] **Step 3: Trim U1–U3 inline body in plan-map-changes and replace with reference**

In `.claude/skills/plan-map-changes/SKILL.md`, find the Universal checks section (exact string):

```
### Universal checks (all suggestion types)

**U1. Read the affected files in full.**
Do NOT infer current state from the plugin map — read the actual SKILL.md
or knowledge file. The map is a snapshot; the code is the truth.

**U2. Verify referenced artifacts exist.**
If the suggestion mentions a validator script, helper file, or Python
tool: run `ls` on the directory. Build plans around files that exist,
not files that are assumed to exist.

```bash
ls profile-al-dev-shared/skills/<skill-name>/
```

**U3. Check whether the suggested flag, name, or path captures the full scope.**
Read the source skill. List every structural difference between the
skills being merged or connected. A flag named after one feature but
activating three is a scope gap — rename or expand the scope in the plan.

### Type-specific checks

For type-specific checks (Connect, Extend, Merge, Move, Promote, Trim, Remodel,
Split, Inline, Align), see:

`profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`

Each section in that file corresponds to one suggestion type and lists the
questions to answer before writing the rubber-duck record.
```

Replace with:

```
### Checks

For all checks — Universal (U1–U3) and type-specific (Connect, Extend, Merge,
Move, Promote, Trim, Remodel, Split, Inline, Align) — see:

`profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`
```

- [ ] **Step 4: Replace Phase 3 templates in draft-map-suggestions with knowledge reference**

In `.claude/skills/draft-map-suggestions/SKILL.md`, find the Phase 3 section opening lines (exact string):

```
## Phase 3 — Draft suggestions

Write 3–6 high-quality suggestions. Skip patterns that don't yield a real improvement.
Before writing each suggestion, check the current `## Observations` section of the
target map file — skip anything already marked `← implemented`.

**For `--type agent`**, use these templates:
```

Replace everything from that opening line through the closing triple-backtick of the final Extend template block (which ends `...Adds scope; only worth building if the use case is frequent.\n` `` ``` ``) with:

```
## Phase 3 — Draft suggestions

Write 3–6 high-quality suggestions. Skip patterns that don't yield a real improvement.
Before writing each suggestion, check the current `## Observations` section of the
target map file — skip anything already marked `← implemented`, `← completed`,
`← done`, or `← deferred`.

Read `knowledge/map-suggestion-templates.md` for the exact template formats:
- For `--type agent`: use the agent templates (Trim, Remodel, Split, Inline, Align).
- For `--type skill`: use the skill templates (Atomise, Connect, Merge, Promote, Extend).
```

- [ ] **Step 5: Consolidate duplicate agent/skill dispatch blocks in audit-quality Phase 2**

In `.claude/skills/audit-quality/SKILL.md`, find the agent/skill dispatch section (exact string):

```
**For agents, pass this prompt (substitute actual paths):**
```
Analyze the following agent files. Apply your lens to every file and return a findings block.

File list:
/absolute/path/to/agent1.md
/absolute/path/to/agent2.md
[one path per line — paste all paths from Phase 1 here]
```

Agents to dispatch simultaneously (spawn each in parallel):
- `quality-agent-lens-clarity`
- `quality-agent-lens-structure`
- `quality-agent-lens-description`
- `quality-agent-lens-bloat`
- `quality-agent-lens-name-fit`

**For skills, pass this prompt (substitute actual paths):**
```
Analyze the following SKILL.md files. Apply your lens to every file and return a findings block.

File list:
/absolute/path/to/skills/skill-name/SKILL.md
/absolute/path/to/skills/other-skill/SKILL.md
[one path per line — paste all paths from Phase 1 here]
```

Agents to dispatch simultaneously (spawn each in parallel):
- `quality-skill-lens-clarity`
- `quality-skill-lens-structure`
- `quality-skill-lens-description`
- `quality-skill-lens-bloat`
- `quality-skill-lens-name-fit`

Each agent returns one block headed `### [Lens Name] Findings`.
```

Replace with:

```
Pass this prompt to each of the five lenses (substitute `{file_list}` with paths from Phase 1):

```
Analyze the following files. Apply your lens to every file and return a findings block.

File list:
{file_list}
```

**For `--type agent`**, dispatch these five agents simultaneously:
- `quality-agent-lens-clarity`
- `quality-agent-lens-structure`
- `quality-agent-lens-description`
- `quality-agent-lens-bloat`
- `quality-agent-lens-name-fit`

**For `--type skill`**, dispatch these five agents simultaneously:
- `quality-skill-lens-clarity`
- `quality-skill-lens-structure`
- `quality-skill-lens-description`
- `quality-skill-lens-bloat`
- `quality-skill-lens-name-fit`

Each agent returns one block headed `### [Lens Name] Findings`.
```

- [ ] **Step 6: Verify Task 2**

```bash
# New knowledge file created
ls -la /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/map-suggestion-templates.md

# U1-U3 added to rubber-duck knowledge
grep -n "Universal checks" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md

# draft-map-suggestions references knowledge file, no longer embeds templates
grep -n "map-suggestion-templates" /Users/russelllaing/al-dev-shared/.claude/skills/draft-map-suggestions/SKILL.md
grep -c "^\*\*Trim: al-dev" /Users/russelllaing/al-dev-shared/.claude/skills/draft-map-suggestions/SKILL.md

# plan-map-changes now references knowledge for all checks
grep -n "map-change-rubber-duck-checks" /Users/russelllaing/al-dev-shared/.claude/skills/plan-map-changes/SKILL.md

# audit-quality dispatch consolidated
grep -c "For agents, pass this prompt\|For skills, pass this prompt" /Users/russelllaing/al-dev-shared/.claude/skills/audit-quality/SKILL.md

# Line count reductions
wc -l \
  /Users/russelllaing/al-dev-shared/.claude/skills/draft-map-suggestions/SKILL.md \
  /Users/russelllaing/al-dev-shared/.claude/skills/plan-map-changes/SKILL.md \
  /Users/russelllaing/al-dev-shared/.claude/skills/audit-quality/SKILL.md
```

Expected:
- `map-suggestion-templates.md` exists.
- `map-change-rubber-duck-checks.md` has "Universal checks" header.
- `draft-map-suggestions` references `map-suggestion-templates`; inline agent template count is 0.
- `plan-map-changes` references `map-change-rubber-duck-checks.md`.
- `audit-quality` has 0 lines matching the old duplicate block pattern.
- `draft-map-suggestions` ≤ 155 lines (was 231); `plan-map-changes` ≤ 160 lines; `audit-quality` ≤ 265 lines (was 276).

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/knowledge/map-suggestion-templates.md \
  profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md \
  .claude/skills/draft-map-suggestions/SKILL.md \
  .claude/skills/plan-map-changes/SKILL.md \
  .claude/skills/audit-quality/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "refactor(tooling): extract suggestion templates and rubber-duck checks to knowledge files"
```

---

## Task 3: Extract Discovery Phases into Standalone Skills (Item 3)

**Files:**
- Create: `.claude/skills/discover-skill-design/SKILL.md`
- Create: `.claude/skills/discover-agent-design/SKILL.md`
- Modify: `.claude/skills/analyze-skill-design/SKILL.md` (currently 153 lines)
- Modify: `.claude/skills/analyze-agent-design/SKILL.md` (currently 145 lines)

---

- [ ] **Step 1: Create discover-skill-design/SKILL.md**

```bash
mkdir -p /Users/russelllaing/al-dev-shared/.claude/skills/discover-skill-design
```

Write `.claude/skills/discover-skill-design/SKILL.md` with this exact content:

```markdown
---
name: discover-skill-design
description: >-
  Discovery phase for skill design analysis. Reads the plugin map, builds working
  lists, and dispatches design-skill lens agents. Returns candidate lists and
  working lists for synthesis. Called by /analyze-skill-design; can also be
  invoked standalone by health sweeps or other synthesis consumers.
  Output: structured context returned to caller (no file written).
argument-hint: "[focus: atomise|connect|merge|all]"
---

# Skill: /discover-skill-design

Discovery phase for skill design analysis. Returns **working_lists** (context built
from the plugin map) and **candidate_lists** (findings from lens dispatch) to the
caller. Consumed by `/analyze-skill-design`'s synthesis phase, or by health sweeps
that need design-skill lens results without full synthesis.

---

## Phase 1 — Read the Plugin Map and Build Working Lists

Read `docs/al-dev-plugin-map.md` in full. Build these working lists:

1. **Agent usage counts** — for every `al-dev-shared:` agent type mentioned in
   drill-downs, record which skills use it and how many times.
2. **Phase counts** — record the number of named phases per skill.
3. **File handoff chains** — trace `.dev/` output files. Note when one skill's
   output is consumed by another.
4. **No-agent skills** — list skills whose drill-down contains only `(skill itself)`
   nodes.
5. **Pre-planning tributaries** — list skills that produce output files consumed
   by `/al-dev-plan` or `/al-dev-investigate`. Note whether each appears in the
   Layer 1 diagram as a dashed tributary arrow (`-.->`).

Also read the Layer 1 diagram content from `docs/al-dev-plugin-map.md` for use
in the pre-planning lens.

Get SKILL.md file paths:

```bash
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills -name "SKILL.md" | sort
```

If an argument was passed, restrict analysis to that category
(`atomise`, `connect`, `merge`, or `all` / no argument = `all`).

---

## Phase 2 — Parallel Lens Dispatch

Dispatch the relevant lens agents in a **single response** (parallel Agent tool calls).

For each lens, pass only the context fields it requires (per `knowledge/lens-invocation-patterns.md`).
Construct one dispatch prompt per lens:

**design-skill-lens-shared-backbone:**
```
Analyze the following SKILL.md files. Apply your lens and return a findings block.
File list: [one path per line]
agent_usage_counts: {agent-type → [skills that spawn it]}
```

**design-skill-lens-complexity:**
```
Analyze the following SKILL.md files. Apply your lens and return a findings block.
File list: [one path per line]
phase_counts: {skill → phase count}
no_agent_skills: [list]
```

**design-skill-lens-near-duplicates:**
```
Analyze the following SKILL.md files. Apply your lens and return a findings block.
File list: [one path per line]
agent_usage_counts: {agent-type → [skills that spawn it]}
phase_counts: {skill → phase count}
```

**design-skill-lens-handoff-gaps:**
```
Analyze the following SKILL.md files. Apply your lens and return a findings block.
File list: [one path per line]
handoff_chains: {skill → [output files]}
```

**design-skill-lens-preplanning:**
```
Analyze the following SKILL.md files. Apply your lens and return a findings block.
File list: [one path per line]
preplanning_skills: [list]
layer1_diagram_content: [raw text of Layer 1 Mermaid diagram]
```

Agents to dispatch based on the focus argument:
- `all` or no argument: dispatch all five simultaneously
  - `design-skill-lens-shared-backbone`
  - `design-skill-lens-complexity`
  - `design-skill-lens-near-duplicates`
  - `design-skill-lens-handoff-gaps`
  - `design-skill-lens-preplanning`
- `connect`: dispatch only `design-skill-lens-shared-backbone`
- `atomise`: dispatch only `design-skill-lens-complexity`
- `merge`: dispatch only `design-skill-lens-near-duplicates`

Each agent returns one block headed `### [Lens Name] Findings`.

---

## Output

Return the following structured context to the caller:

**working_lists:**
- `agent_usage_counts`: {agent-type → [skills]}
- `phase_counts`: {skill → count}
- `handoff_chains`: {skill → [output files]}
- `no_agent_skills`: [list]
- `preplanning_tributaries`: [list]
- `layer1_diagram_content`: [raw text]

**candidate_lists** (parsed from Phase 2 findings blocks):
- Connect/Promote candidates — from Shared Execution Backbone findings
- Atomise/Absorb candidates — from Complexity Outliers findings
- Merge candidates — from Near-Duplicate Shapes findings
- Extend candidates — from Handoff Chain Gaps findings
- Diagram/labelling gaps — from Pre-planning Skills findings
```

After writing, verify:

```bash
ls -la /Users/russelllaing/al-dev-shared/.claude/skills/discover-skill-design/SKILL.md
wc -l /Users/russelllaing/al-dev-shared/.claude/skills/discover-skill-design/SKILL.md
```

Expected: file exists, 85–105 lines.

- [ ] **Step 2: Create discover-agent-design/SKILL.md**

```bash
mkdir -p /Users/russelllaing/al-dev-shared/.claude/skills/discover-agent-design
```

Write `.claude/skills/discover-agent-design/SKILL.md` with this exact content:

```markdown
---
name: discover-agent-design
description: >-
  Discovery phase for agent design analysis. Reads the agent map, builds working
  lists, and dispatches design-agent lens agents. Returns candidate lists and
  working lists for synthesis. Called by /analyze-agent-design; can also be
  invoked standalone by health sweeps or other synthesis consumers.
  Output: structured context returned to caller (no file written).
argument-hint: "[focus: trim|remodel|split|inline|align|all]"
---

# Skill: /discover-agent-design

Discovery phase for agent design analysis. Returns **working_lists** (context built
from the agent map) and **candidate_lists** (findings from lens dispatch) to the
caller. Consumed by `/analyze-agent-design`'s synthesis phase, or by health sweeps
that need design-agent lens results without full synthesis.

---

## Phase 1 — Read the Agent Map and Build Working Lists

Read `docs/al-dev-agent-map.md` in full. Build these working lists:

1. **Tool inventory** — for every agent, record its tools list from the map.
2. **Model assignments** — for every agent, record its model.
3. **Caller map** — for every agent, record which skills spawn it.
4. **Single-use agents** — agents spawned by exactly one skill.
5. **Shared agents** — agents spawned by 2+ skills.
6. **Undocumented agents** — agents with "Not documented" for both Inputs and Outputs.
7. **Existing inline candidates** — agents already listed in `### Inline candidates`
   in `docs/al-dev-agent-map.md`.

If an argument was passed, restrict analysis to that lens:
`trim`, `remodel`, `split`, `inline`, `align`, or `all` / no argument = `all`.

Also run this command to get agent file paths:

```bash
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents -name "*.md" | sort
```

---

## Phase 2 — Parallel Lens Dispatch

Dispatch the relevant lens agents in a **single response** (parallel Agent tool calls).

For each lens, pass only the context fields it requires (per `knowledge/lens-invocation-patterns.md`).
Construct one dispatch prompt per lens:

**design-agent-lens-tool-hygiene:**
```
Analyze the following agent files. Apply your lens and return a findings block.
File list: [one path per line]
tool_inventory: {agent → [tools]}
```

**design-agent-lens-model-fit:**
```
Analyze the following agent files. Apply your lens and return a findings block.
File list: [one path per line]
model_assignments: {agent → model}
```

**design-agent-lens-scope-isolation:**
```
Analyze the following agent files. Apply your lens and return a findings block.
File list: [one path per line]
```

**design-agent-lens-caller-alignment:**
```
Analyze the following agent files. Apply your lens and return a findings block.
File list: [one path per line]
caller_map: {agent → [spawning skills]}
```

**design-agent-lens-usage-patterns:**
```
Analyze the following agent files. Apply your lens and return a findings block.
File list: [one path per line]
single_use_agents: [list]
already_inline_candidates: [agents already in ### Inline candidates in docs/al-dev-agent-map.md]
```

Agents to dispatch based on the focus argument:
- `all` or no argument: dispatch all five simultaneously
  - `design-agent-lens-tool-hygiene`
  - `design-agent-lens-model-fit`
  - `design-agent-lens-scope-isolation`
  - `design-agent-lens-caller-alignment`
  - `design-agent-lens-usage-patterns`
- `trim`: dispatch only `design-agent-lens-tool-hygiene`
- `remodel`: dispatch only `design-agent-lens-model-fit`
- `split`: dispatch only `design-agent-lens-scope-isolation`
- `align`: dispatch only `design-agent-lens-caller-alignment`
- `inline`: dispatch only `design-agent-lens-usage-patterns`

Each agent returns one block headed `### [Lens Name] Findings`.

---

## Output

Return the following structured context to the caller:

**working_lists:**
- `tool_inventory`: {agent → [tools]}
- `model_assignments`: {agent → model}
- `caller_map`: {agent → [spawning skills]}
- `single_use_agents`: [list]
- `shared_agents`: [list]
- `undocumented_agents`: [list]
- `existing_inline_candidates`: [list]

**candidate_lists** (parsed from Phase 2 findings blocks):
- Trim candidates — from Tool Hygiene findings
- Remodel candidates — from Model Fit findings
- Split candidates — from Scope Isolation findings
- Align candidates — from Caller Alignment findings
- Inline candidates — from Usage Patterns findings
```

After writing, verify:

```bash
ls -la /Users/russelllaing/al-dev-shared/.claude/skills/discover-agent-design/SKILL.md
wc -l /Users/russelllaing/al-dev-shared/.claude/skills/discover-agent-design/SKILL.md
```

Expected: file exists, 85–105 lines.

- [ ] **Step 3: Update analyze-skill-design — replace Phases 1–2 with discovery invocation**

In `.claude/skills/analyze-skill-design/SKILL.md`, find the Phase 1 and Phase 2 sections. The block to replace starts at `## Phase 1 — Read the Plugin Map and Build Working Lists` and ends just before `## Phase 3 — Aggregate Findings`.

Find this exact start string:

```
## Phase 1 — Read the Plugin Map and Build Working Lists

Read `docs/al-dev-plugin-map.md` in full. Build these working lists:
```

Find the end boundary — the line just before `## Phase 3 — Aggregate Findings`:

```
Each agent returns one block headed `### [Lens Name] Findings`.

---

## Phase 3 — Aggregate Findings
```

Replace everything from `## Phase 1` through and including the `---` separator before Phase 3 with:

```
## Phase 1 — Discovery

Invoke `/discover-skill-design`. Pass the focus argument if one was supplied.

Receive from `/discover-skill-design`:
- **working_lists**: `agent_usage_counts`, `phase_counts`, `handoff_chains`,
  `no_agent_skills`, `preplanning_tributaries`, `layer1_diagram_content`
- **candidate_lists**: Connect/Promote, Atomise/Absorb, Merge, Extend,
  Diagram/labelling gaps

---

## Phase 2 — Aggregate Findings
```

Also update the Phase 3 reference in the description so the subsequent phases renumber correctly. Find (exact string):

```
## Phase 3 — Aggregate Findings
```

Replace with:

```
## Phase 2 — Aggregate Findings
```

Then update the Phase 5 that calls `/draft-map-suggestions`: Find (exact string):

```
## Phase 5 — Draft Suggestions, Inventory Tables, Diagram and Map

Invoke `/draft-map-suggestions --type skill`. Pass as context:
- The candidate lists from Phase 3 (Connect/Promote, Atomise/Absorb, Merge, Extend candidates with raw finding lines)
```

Replace with:

```
## Phase 3 — Draft Suggestions, Inventory Tables, Diagram and Map

Invoke `/draft-map-suggestions --type skill`. Pass as context:
- The candidate lists from Phase 2 (Connect/Promote, Atomise/Absorb, Merge, Extend candidates with raw finding lines)
```

And update the final phase number. Find (exact string):

```
## Phase 6 — Present to User
```

Replace with:

```
## Phase 4 — Present to User
```

- [ ] **Step 4: Update analyze-agent-design — replace Phases 1–2 with discovery invocation**

Apply the same pattern to `.claude/skills/analyze-agent-design/SKILL.md`:

Replace Phase 1 through the separator before Phase 3 with:

```
## Phase 1 — Discovery

Invoke `/discover-agent-design`. Pass the focus argument if one was supplied.

Receive from `/discover-agent-design`:
- **working_lists**: `tool_inventory`, `model_assignments`, `caller_map`,
  `single_use_agents`, `shared_agents`, `undocumented_agents`,
  `existing_inline_candidates`
- **candidate_lists**: Trim, Remodel, Split, Align, Inline candidates

---

## Phase 2 — Aggregate Findings
```

Then rename the aggregate findings phase header (find exact string):

```
## Phase 3 — Aggregate Findings
```

Replace with:

```
## Phase 2 — Aggregate Findings
```

Update Phase 5 reference. Find (exact string):

```
## Phase 5 — Draft Suggestions, Inventory Tables, Diagram and Map

Invoke `/draft-map-suggestions --type agent`. Pass as context:
- The candidate lists from Phase 3 (Trim, Remodel, Split, Align, Inline candidates with raw finding lines)
```

Replace with:

```
## Phase 3 — Draft Suggestions, Inventory Tables, Diagram and Map

Invoke `/draft-map-suggestions --type agent`. Pass as context:
- The candidate lists from Phase 2 (Trim, Remodel, Split, Align, Inline candidates with raw finding lines)
```

Update the final phase. Find (exact string):

```
## Phase 6 — Present to User
```

Replace with:

```
## Phase 4 — Present to User
```

- [ ] **Step 5: Verify Task 3**

```bash
# New skills exist
ls /Users/russelllaing/al-dev-shared/.claude/skills/discover-skill-design/SKILL.md \
   /Users/russelllaing/al-dev-shared/.claude/skills/discover-agent-design/SKILL.md

# analyze-skill-design invokes the discovery skill
grep -n "discover-skill-design" /Users/russelllaing/al-dev-shared/.claude/skills/analyze-skill-design/SKILL.md

# analyze-agent-design invokes the discovery skill
grep -n "discover-agent-design" /Users/russelllaing/al-dev-shared/.claude/skills/analyze-agent-design/SKILL.md

# No find commands remain inline in analyze-* (moved to discover-*)
grep -c "find.*profile-al-dev-shared.*skills" /Users/russelllaing/al-dev-shared/.claude/skills/analyze-skill-design/SKILL.md
grep -c "find.*profile-al-dev-shared.*agents" /Users/russelllaing/al-dev-shared/.claude/skills/analyze-agent-design/SKILL.md

# Phase structure correct
grep "^## Phase" /Users/russelllaing/al-dev-shared/.claude/skills/analyze-skill-design/SKILL.md
grep "^## Phase" /Users/russelllaing/al-dev-shared/.claude/skills/analyze-agent-design/SKILL.md

# Line counts reduced
wc -l /Users/russelllaing/al-dev-shared/.claude/skills/analyze-skill-design/SKILL.md \
      /Users/russelllaing/al-dev-shared/.claude/skills/analyze-agent-design/SKILL.md
```

Expected:
- Both discover-* files exist.
- Both analyze-* files reference their discovery skill.
- `find` command count is 0 in both analyze-* files.
- Phase headers: Phase 1 (Discovery), Phase 2 (Aggregate Findings), Phase 3 (Draft Suggestions...), Phase 4 (Present to User).
- `analyze-skill-design` ≤ 65 lines (was 153); `analyze-agent-design` ≤ 60 lines (was 145).

- [ ] **Step 6: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  .claude/skills/discover-skill-design/SKILL.md \
  .claude/skills/discover-agent-design/SKILL.md \
  .claude/skills/analyze-skill-design/SKILL.md \
  .claude/skills/analyze-agent-design/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "refactor(tooling): extract discovery phases from analyze-*-design into standalone skills"
```

---

## Task 4: Merge 6 Map Management Skills into 2 with --no-update Flag (Item 1)

**Files:**
- Modify: `.claude/skills/review-agent-map/SKILL.md` (currently 223 lines)
- Modify: `.claude/skills/review-skill-map/SKILL.md` (currently 210 lines)
- Modify: `.claude/skills/sync-documentation-maps/SKILL.md`
- Modify: `CLAUDE.md`
- Archive: 4 skill directories

---

- [ ] **Step 1: Add --no-update mode to review-agent-map**

In `.claude/skills/review-agent-map/SKILL.md`, replace the frontmatter (exact string):

```
---
name: review-agent-map
description: >-
  Review profile-al-dev-shared agents for accuracy and update
  docs/al-dev-agent-map.md. Use whenever agents are added, removed, or
  restructured in the plugin, or when you want to verify the map reflects
  the current state of agent files.
  Triggers on: "review agent map", "update agent map", "sync agent map",
  "is the agent map accurate".
argument-hint: "[optional: agent name to focus on]"
---
```

with:

```
---
name: review-agent-map
description: >-
  Review profile-al-dev-shared agents for accuracy and update
  docs/al-dev-agent-map.md. Use whenever agents are added, removed, or
  restructured in the plugin, or when you want to verify the map reflects
  the current state of agent files. Pass --no-update to audit-only mode:
  reports discrepancies and suggests fixes without modifying any files.
  Replaces /audit-agents-against-map (use --no-update) and /update-agent-map.
  Triggers on: "review agent map", "update agent map", "sync agent map",
  "is the agent map accurate".
argument-hint: "[--no-update] [optional: agent name to focus on]"
---
```

Then, in the skill body, insert a Phase 0 immediately after the `# Review Agent Map` heading and its intro paragraph. Find (exact string):

```
# Review Agent Map

Audit `profile-al-dev-shared/agents/` and update `docs/al-dev-agent-map.md`
so it accurately reflects the current active agents, their models, tools,
and caller relationships.

---

## Phase 1: Scan Agent Files
```

Replace with:

```
# Review Agent Map

Audit `profile-al-dev-shared/agents/` and update `docs/al-dev-agent-map.md`
so it accurately reflects the current active agents, their models, tools,
and caller relationships.

---

## Phase 0: Parse Arguments

Read `$ARGUMENTS`:
- If `--no-update` is present, set `NO_UPDATE=true`.
- If an agent name is present (not a flag), set it as `TARGET_AGENT` and
  focus all subsequent phases on that agent only.
- Flags are not exclusive: `--no-update al-dev-developer` is valid.

---

## Phase 1: Scan Agent Files
```

Then insert Phase 5b between Phase 5 and Phase 6. Find (exact string):

```
If everything is accurate, say so and stop.

---

## Phase 6: Update the Map
```

Replace with:

```
If everything is accurate, say so and stop.

---

## Phase 5b: Audit-Only Exit (--no-update)

If `NO_UPDATE=true`:

For each discrepancy found in Phase 5, suggest specific fixes without modifying files:

**For Layer 1 (Catalog table):**
- To add an agent row: insert name, model, tools, spawned-by columns
- To remove an agent row: delete the table row
- To fix values: correct model, tools list, or spawned-by list

**For Layer 2 (Per-agent profiles):**
- To update a profile: rewrite the `### agent-name` section with corrected content
- To add a missing profile: insert a new section following the existing template
- To remove a stale profile: delete its `### agent-name` section entirely

**Present all suggested fixes without modifying files.** The user may:
- Run `/review-agent-map` (without `--no-update`) to apply all fixes.

Then stop. Do not proceed to Phase 6 or 7.

---

## Phase 6: Update the Map
```

- [ ] **Step 2: Add --no-update mode to review-skill-map**

In `.claude/skills/review-skill-map/SKILL.md`, replace the frontmatter (exact string):

```
---
name: review-skill-map
description: >-
  Review profile-al-dev-shared for accuracy and update docs/al-dev-skills-map.md.
  Use whenever skills or agents are added, removed, or restructured in the plugin,
  or when you want to verify the map reflects the current state of the codebase.
  Triggers on: "review skill map", "update skill map", "sync skill map",
  "is the skill map accurate", "update the map", "check the map".
argument-hint: "[optional: skill name to focus on]"
---
```

with:

```
---
name: review-skill-map
description: >-
  Review profile-al-dev-shared for accuracy and update docs/al-dev-skills-map.md.
  Use whenever skills or agents are added, removed, or restructured in the plugin,
  or when you want to verify the map reflects the current state of the codebase.
  Pass --no-update to audit-only mode: reports discrepancies and suggests fixes
  without modifying any files.
  Replaces /audit-skills-against-map (use --no-update) and /update-skill-map.
  Triggers on: "review skill map", "update skill map", "sync skill map",
  "is the skill map accurate", "update the map", "check the map".
argument-hint: "[--no-update] [optional: skill name to focus on]"
---
```

Add Phase 0 after `# Review Skill Map` and its intro paragraph. Find (exact string):

```
# Review Skill Map

Audit `profile-al-dev-shared` and update `docs/al-dev-skills-map.md` so it
accurately reflects the current active skills, agents, phases, file handoffs,
and generated projection surfaces under `profile-al-dev-shared/generated/agents/`.

---

## Phase 1: Scan Plugin Structure
```

Replace with:

```
# Review Skill Map

Audit `profile-al-dev-shared` and update `docs/al-dev-skills-map.md` so it
accurately reflects the current active skills, agents, phases, file handoffs,
and generated projection surfaces under `profile-al-dev-shared/generated/agents/`.

---

## Phase 0: Parse Arguments

Read `$ARGUMENTS`:
- If `--no-update` is present, set `NO_UPDATE=true`.
- If a skill name is present (not a flag), set it as `TARGET_SKILL` and
  focus all subsequent phases on that skill only.
- Flags are not exclusive: `--no-update al-dev-develop` is valid.

---

## Phase 1: Scan Plugin Structure
```

Insert Phase 4b between Phase 4 and Phase 5. Find (exact string):

```
If everything is accurate, say so and stop.

---

## Phase 5: Update the Map
```

Replace with:

```
If everything is accurate, say so and stop.

---

## Phase 4b: Audit-Only Exit (--no-update)

If `NO_UPDATE=true`:

For each discrepancy found in Phase 4, suggest specific fixes without modifying files:

**For Layer 1 fixes:**
- To add a skill: add a node and edge in the flowchart, add a `style` directive
- To remove a skill: remove its node declaration, all edges, and its `style` directive — leave no orphaned `style` lines
- To fix a handoff label: update the `-->|label|` on the relevant edge

**For Layer 2 fixes:**
- To update a drill-down: rewrite the affected `flowchart LR` block
- To add a missing skill: insert a new `### /skill-name` section following existing style conventions
- To remove a stale skill: delete its `### /skill-name` section entirely

**Present all suggested fixes without modifying files.** The user may:
- Run `/review-skill-map` (without `--no-update`) to apply all fixes.

Then stop. Do not proceed to Phase 5, 6, or 7.

---

## Phase 5: Update the Map
```

- [ ] **Step 3: Update sync-documentation-maps to use review-*-map**

In `.claude/skills/sync-documentation-maps/SKILL.md`, replace Phase 1 (exact string):

```
## Phase 1: Parallel Audits

Dispatch both audits to run in parallel:

```
Spawn: /audit-skills-against-map
Spawn: /audit-agents-against-map
```

Wait for both to complete. Collect audit findings for each map.
```

with:

```
## Phase 1: Parallel Audits

Dispatch both audits to run in parallel:

```
Spawn: /review-skill-map --no-update
Spawn: /review-agent-map --no-update
```

Wait for both to complete. Collect audit findings for each map.
```

Replace the update dispatches in Phase 4 (exact string):

```
**If skills map selected:**
```
Spawn: /update-skill-map
Wait for completion
```

**If agent map selected:**
```
Spawn: /update-agent-map
Wait for completion
```

**If both selected:**
```
Spawn: /update-skill-map
Spawn: /update-agent-map
Wait for both to complete
```
```

with:

```
**If skills map selected:**
```
Spawn: /review-skill-map
Wait for completion
```

**If agent map selected:**
```
Spawn: /review-agent-map
Wait for completion
```

**If both selected:**
```
Spawn: /review-skill-map
Spawn: /review-agent-map
Wait for both to complete
```
```

Also replace the "For audit-only" line in the `## When to Use` section (exact string):

```
**For audit-only (no updates):**
- Use `/audit-skills-against-map` and `/audit-agents-against-map` directly
```

with:

```
**For audit-only (no updates):**
- Use `/review-skill-map --no-update` and `/review-agent-map --no-update`
```

- [ ] **Step 4: Archive the 4 deprecated skills**

```bash
cp -r /Users/russelllaing/al-dev-shared/.claude/skills/audit-agents-against-map \
      /Users/russelllaing/al-dev-shared/.claude/skills/archived/audit-agents-against-map
cp -r /Users/russelllaing/al-dev-shared/.claude/skills/update-agent-map \
      /Users/russelllaing/al-dev-shared/.claude/skills/archived/update-agent-map
cp -r /Users/russelllaing/al-dev-shared/.claude/skills/audit-skills-against-map \
      /Users/russelllaing/al-dev-shared/.claude/skills/archived/audit-skills-against-map
cp -r /Users/russelllaing/al-dev-shared/.claude/skills/update-skill-map \
      /Users/russelllaing/al-dev-shared/.claude/skills/archived/update-skill-map
```

Add a deprecation notice to each archived SKILL.md. For each of the four archived files, use Edit to prepend a notice after the closing `---` of frontmatter and before the `# ...` heading:

For `archived/audit-agents-against-map/SKILL.md`, insert after the frontmatter `---`:

```
> **ARCHIVED 2026-05-30** — Use `/review-agent-map --no-update` instead.

---

```

For `archived/update-agent-map/SKILL.md`, insert after the frontmatter `---`:

```
> **ARCHIVED 2026-05-30** — Use `/review-agent-map` instead.

---

```

For `archived/audit-skills-against-map/SKILL.md`, insert after the frontmatter `---`:

```
> **ARCHIVED 2026-05-30** — Use `/review-skill-map --no-update` instead.

---

```

For `archived/update-skill-map/SKILL.md`, insert after the frontmatter `---`:

```
> **ARCHIVED 2026-05-30** — Use `/review-skill-map` instead.

---

```

Then remove the active copies:

```bash
rm -rf /Users/russelllaing/al-dev-shared/.claude/skills/audit-agents-against-map
rm -rf /Users/russelllaing/al-dev-shared/.claude/skills/update-agent-map
rm -rf /Users/russelllaing/al-dev-shared/.claude/skills/audit-skills-against-map
rm -rf /Users/russelllaing/al-dev-shared/.claude/skills/update-skill-map
```

- [ ] **Step 5: Update CLAUDE.md audit-only reference**

In `CLAUDE.md`, replace (exact string):

```
For audit-only (no updates):
```bash
/audit-skills-against-map   # Verify skills map accuracy without modifying
/audit-agents-against-map   # Verify agent map accuracy without modifying
```
```

with:

```
For audit-only (no updates):
```bash
/review-skill-map --no-update   # Verify skills map accuracy without modifying
/review-agent-map --no-update   # Verify agent map accuracy without modifying
```
```

- [ ] **Step 6: Verify Task 4**

```bash
# Deprecated skills no longer in active directory
ls /Users/russelllaing/al-dev-shared/.claude/skills/ | grep -E "^audit-agents|^update-agent|^audit-skills|^update-skill"

# Archived skills exist
ls /Users/russelllaing/al-dev-shared/.claude/skills/archived/audit-agents-against-map/SKILL.md
ls /Users/russelllaing/al-dev-shared/.claude/skills/archived/update-agent-map/SKILL.md
ls /Users/russelllaing/al-dev-shared/.claude/skills/archived/audit-skills-against-map/SKILL.md
ls /Users/russelllaing/al-dev-shared/.claude/skills/archived/update-skill-map/SKILL.md

# review-agent-map has --no-update in frontmatter and Phase 5b
grep -c "no-update" /Users/russelllaing/al-dev-shared/.claude/skills/review-agent-map/SKILL.md

# review-skill-map has --no-update in frontmatter and Phase 4b
grep -c "no-update" /Users/russelllaing/al-dev-shared/.claude/skills/review-skill-map/SKILL.md

# sync-documentation-maps uses new calls
grep -c "review-skill-map --no-update\|review-agent-map --no-update" /Users/russelllaing/al-dev-shared/.claude/skills/sync-documentation-maps/SKILL.md

# CLAUDE.md updated
grep -n "review-skill-map --no-update" /Users/russelllaing/al-dev-shared/CLAUDE.md

# No active references to deprecated skill names remain (outside archived/)
grep -r "audit-agents-against-map\|update-agent-map\|audit-skills-against-map\|update-skill-map" \
  /Users/russelllaing/al-dev-shared/.claude/skills/ \
  --include="SKILL.md" | grep -v "/archived/"
```

Expected:
- Active directory listing returns empty (no deprecated skill directories).
- All 4 archived SKILL.md files exist.
- `review-agent-map` has ≥ 4 `no-update` occurrences (frontmatter × 2 + Phase 5b × 2+).
- `review-skill-map` has ≥ 4 `no-update` occurrences.
- `sync-documentation-maps` has ≥ 2 `--no-update` lines.
- `CLAUDE.md` has the updated reference.
- Final grep returns empty (no live references to deprecated skill names).

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  .claude/skills/review-agent-map/SKILL.md \
  .claude/skills/review-skill-map/SKILL.md \
  .claude/skills/sync-documentation-maps/SKILL.md \
  .claude/skills/archived/audit-agents-against-map/SKILL.md \
  .claude/skills/archived/update-agent-map/SKILL.md \
  .claude/skills/archived/audit-skills-against-map/SKILL.md \
  .claude/skills/archived/update-skill-map/SKILL.md \
  CLAUDE.md
git -C /Users/russelllaing/al-dev-shared status
git -C /Users/russelllaing/al-dev-shared commit -m "refactor(tooling): merge 6 map-management skills into 2 with --no-update flag; archive deprecated skills"
```

---

## Self-Review

**Spec coverage check:**

| Health finding (2026-05-30-tooling-health.md top 5) | Task | Status |
|------------------------------------------------------|------|--------|
| Item 1: Map management skills severe duplication | Task 4 | ✓ planned |
| Item 2: All 21 lens agents missing model field | — | ✓ already done (verified) |
| Item 3: analyze-skill/agent-design separable phases | Task 3 | ✓ planned |
| Item 4: Clarity blockers in plan-map-changes + audit-knowledge-quality | Task 1 | ✓ planned |
| Item 5: draft-map-suggestions/audit-quality/plan-map-changes bloat | Task 2 | ✓ planned |

**Placeholder scan:** No TBD, TODO, or "similar to Task N" patterns. All file content is explicit. `YYYY-MM-DD` appears only in archive deprecation notice as a literal date value.

**Constraint check:** No harness-specific tokens (subagent_type, Claude Code, etc.) in any skill file content. Template blocks in new `map-suggestion-templates.md` are harness-neutral.

**Type consistency:** Phase numbers in `analyze-skill-design` and `analyze-agent-design` renumber from 1–6 (old) to 1–4 (new) consistently. Phase references in `/draft-map-suggestions` dispatch calls updated from "Phase 3" to "Phase 2" to match renumbered Aggregate Findings phase.
