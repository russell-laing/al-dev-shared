# Tooling Health Top-5 Actions — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Address the 4 actionable items from the 2026-05-29 tooling health sweep (the 2 Merge suggestions were rubber-ducked and skipped — the pairs have orthogonal structures and incompatible logic).

**Architecture:** All changes are documentation/skill edits. Tasks 1 and 3 create new knowledge files; Tasks 2 and 4 update existing maintainer skills to reference them; Task 5 refactors audit-quality Phase 4; Task 6 performs a mechanical Glob removal across 20 agent frontmatter files.

**Tech Stack:** Markdown, YAML frontmatter; files in `profile-al-dev-shared/` and `.claude/skills/`

---

## File Map

| Task | Operation | Path |
|------|-----------|------|
| 1 | Create | `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md` |
| 2 | Modify | `.claude/skills/plan-map-changes/SKILL.md` |
| 3 | Create | `profile-al-dev-shared/knowledge/lens-invocation-patterns.md` |
| 4 | Modify | `.claude/skills/plugin-health/SKILL.md` |
| 5 | Modify | `.claude/skills/audit-quality/SKILL.md` |
| 6 | Modify ×20 | `profile-al-dev-shared/agents/design-agent-lens-*.md` × 5 |
|   |            | `profile-al-dev-shared/agents/design-skill-lens-*.md` × 5 |
|   |            | `profile-al-dev-shared/agents/quality-agent-lens-*.md` × 5 |
|   |            | `profile-al-dev-shared/agents/quality-skill-lens-*.md` × 5 |

---

## Skipped suggestions (with rationale)

**Merge: analyze-agent-design + analyze-skill-design → SKIP**
Rubber-duck confirmed: they dispatch completely different lens agents (5 agent-domain lenses vs 5 skill-domain lenses), build different context inventories (7 agent fields vs 5 skill fields), and use unrelated argument vocabularies (trim/remodel/split/inline/align vs atomise/connect/merge/all). No code reuse is possible beyond the outer loop. Merging would create false coupling and confuse callers.

**Merge: review-agent-map + review-skill-map → SKIP**
Rubber-duck confirmed: agent map is table-based; skill map requires Mermaid diagram editing with orphaned-node detection. Extraction targets differ entirely (model/tools/docs vs phases/agents-spawned/outputs). Each has domain-specific detection logic (Inline vs Move candidates) with incompatible signals. Downstream skills depend on both as separate prerequisites.

---

### Task 1: Create knowledge/map-change-rubber-duck-checks.md

**Files:**
- Create: `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`

This extracts the 9 type-specific check sections from `plan-map-changes` Phase 2 (currently inline at ~64 lines). The Merge check is updated here with the validator-absent remediation that was missing from the source.

- [ ] **Step 1: Confirm directory exists**

```bash
ls profile-al-dev-shared/knowledge/ | grep -c "\.md"
```

Expected: a non-zero count (the directory is populated).

- [ ] **Step 2: Write the new knowledge file**

Write to `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`:

```markdown
# Map Change Rubber-Duck Checks

Type-specific verification checks for the `/plan-map-changes` skill Phase 2.
Apply these after completing the Universal checks (U1–U3) documented in the
skill body. Each section corresponds to one suggestion type.

---

## Connect — "document a shared pattern used by two skills"

- Read both skills' relevant sections. Are the definitions actually
  identical, or just similar? Quote both to confirm.
- Is the pattern stable, or does each skill customize it?

## Extend — "add nodes to a diagram"

- Is the change purely additive, or does it also require removing
  existing nodes? Check if a subsequent task (e.g., a Merge) will
  also touch the same diagram and plan the ordering accordingly.

## Merge — "consolidate skill B into skill A with a flag"

- Read skill B in full. List ALL phases, templates, and validators
  that are unique to it — the flag must activate all of them.
- If skill B has a validator script, confirm it exists with `ls`.
  If the script is absent, note in the rubber-duck record:
  `Scope gap: validator missing; plan must include manual validation or script creation`.
- What does archiving do to other skills that reference skill B?

## Move — "relocate a skill to .claude/skills/"

- Does any file in the skill directory use `Path(__file__)` or relative
  paths to locate other files? If yes, moving the SKILL.md vs. moving
  the whole directory have different effects — choose carefully.
- Does any other skill or script reference the current path?

## Promote — "extract pattern into a knowledge doc"

- Read all caller skills. Are the local definitions truly independent,
  or do some already reference the pattern? Confirm per-file.

## Trim — "remove unused tools from an agent's frontmatter"

- Read the agent file in full (`profile-al-dev-shared/agents/<name>.md`).
  List every tool in the frontmatter tools list.
- Quote any line in the system prompt body that uses each tool. A tool with
  no corresponding usage is a confirmed Trim candidate.
- Does removing this tool break any documented input or output contract?

## Remodel — "change an agent's model assignment"

- Read the agent file. Identify the heaviest reasoning step in the system
  prompt. Does it require multi-file synthesis or competitive analysis?
- Confirm the proposed new model is appropriate for that step:
  haiku for single-step retrieval; sonnet for general tasks; opus only for
  multi-file synthesis or competitive design.

## Split — "extract one concern from an agent into a new agent file"

- Read the agent file in full. Quote the two concerns named in the suggestion.
- Does an agent file for the extracted concern already exist in
  `profile-al-dev-shared/agents/`? If yes, this may be a merge rather than
  a split.
- What would the new agent's type name be? Confirm it is ≤30 characters.

## Inline — "absorb a single-use agent into its calling skill"

- Read the agent file and the spawning skill in full.
- Quote the exact section of the skill where the agent is spawned — this is
  where the inlined prompt will live.
- What is the exact path of the agent file to delete?
- Does any other skill reference this agent type? Confirm with:

```bash
grep -r "al-dev-shared:<agent-type-name>" profile-al-dev-shared/skills/ .claude/skills/
```

## Align — "fix mismatch between caller contract and agent documentation"

- Read both the agent file and every spawning skill identified in the map.
- Quote the exact mismatch: what the skill passes vs. what the agent's Inputs
  table documents (or "Not documented").
- Is the fix to update the agent's Inputs/Outputs tables, or to update how
  the skill calls the agent?
```

- [ ] **Step 3: Verify the file was written**

```bash
ls -la profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md
wc -l profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md
```

Expected: file exists; line count ~80.

- [ ] **Step 4: Confirm no forbidden patterns**

```bash
grep -n "TODO\|TBD\|YYYY-MM-DD\|\[date\]" profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md
```

Expected: no output.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
docs(knowledge): extract plan-map-changes type-specific rubber-duck checks

Moves the 9 type-specific check sections from plan-map-changes Phase 2 into
a standalone reference document. Also adds missing validator-absent remediation
to the Merge check.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Fix plan-map-changes — Phase 1 variable definition + Phase 2 bloat

**Files:**
- Modify: `.claude/skills/plan-map-changes/SKILL.md`

Three edits: (1) replace undefined `$ARGUMENTS` reference with an explicit `FILTER_TYPE` capture instruction, (2) replace the 64-line type-specific checks block with a reference to the knowledge file created in Task 1, (3) no edit needed for Merge check — that fix is in the knowledge file.

- [ ] **Step 1: Read the current Phase 1 tail and confirm $ARGUMENTS location**

```bash
grep -n 'ARGUMENTS\|FILTER_TYPE' .claude/skills/plan-map-changes/SKILL.md
```

Expected: one hit at line ~76 with `$ARGUMENTS`.

- [ ] **Step 2: Fix the $ARGUMENTS → FILTER_TYPE definition**

In `.claude/skills/plan-map-changes/SKILL.md`, replace:

```
If `$ARGUMENTS` names a suggestion type (`connect`, `merge`, `trim`, etc.),
filter to that type across whichever documents are in scope and note the filter.
```

with:

```
If the user passed a suggestion type as an argument (e.g., `connect`, `merge`,
`trim`), capture it as `FILTER_TYPE` and filter collected suggestions to that
type. If no type argument was passed, set `FILTER_TYPE=all` and process all
collected suggestions. Note the active filter before proceeding to Phase 2.
```

- [ ] **Step 3: Replace the 9 type-specific check sections with a reference**

In `.claude/skills/plan-map-changes/SKILL.md`, replace the entire block from `### Type-specific checks` through the `**Align** — ...` section (the 9 inline check blocks). The replacement:

```
### Type-specific checks

For type-specific checks (Connect, Extend, Merge, Move, Promote, Trim, Remodel,
Split, Inline, Align), see:

`profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`

Each section in that file corresponds to one suggestion type and lists the
questions to answer before writing the rubber-duck record.
```

- [ ] **Step 4: Verify Phase 2 is now well under 30 lines**

```bash
awk '/^## Phase 2/,/^## Phase 3/' .claude/skills/plan-map-changes/SKILL.md | wc -l
```

Expected: ≤50 lines (was 128).

- [ ] **Step 5: Verify $ARGUMENTS is gone**

```bash
grep -n 'ARGUMENTS' .claude/skills/plan-map-changes/SKILL.md
```

Expected: no output.

- [ ] **Step 6: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/skills/plan-map-changes/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
fix(skill): resolve plan-map-changes $ARGUMENTS definition + Phase 2 bloat

Defines FILTER_TYPE capture in Phase 1 (replacing undefined $ARGUMENTS reference).
Collapses 64-line type-specific check block in Phase 2 to a knowledge-file reference.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Create knowledge/lens-invocation-patterns.md

**Files:**
- Create: `profile-al-dev-shared/knowledge/lens-invocation-patterns.md`

Documents which context fields each design lens class actually requires, plus templates for dispatchers to use. Enables `/plugin-health` (Task 4) to pass minimal, correct context per lens class instead of all 10 fields to all lenses.

Note from rubber-duck: `layer1_diagram_content` is required by `design-skill-lens-preplanning` but is NOT currently in the plugin-health Phase 2.0 named-variable list (only described implicitly). Task 4 adds it explicitly.

- [ ] **Step 1: Write the knowledge file**

Write to `profile-al-dev-shared/knowledge/lens-invocation-patterns.md`:

```markdown
# Lens Invocation Patterns

Canonical context requirements for design lens agents. Use this reference when
building dispatch prompts in skills that invoke design lenses. Quality lenses and
the naming-convention lens need only a file list.

See also: `knowledge/architect-invocation-patterns.md` (parallel pattern for
`al-dev-solution-architect`).

---

## Design Agent Lenses

Agents: `design-agent-lens-caller-alignment`, `design-agent-lens-model-fit`,
`design-agent-lens-scope-isolation`, `design-agent-lens-tool-hygiene`,
`design-agent-lens-usage-patterns`

### Required context fields per lens

| Lens | Required context fields |
|------|------------------------|
| `design-agent-lens-tool-hygiene` | `tool_inventory` |
| `design-agent-lens-model-fit` | `model_assignments` |
| `design-agent-lens-scope-isolation` | *(none — file list only)* |
| `design-agent-lens-caller-alignment` | `caller_map` |
| `design-agent-lens-usage-patterns` | `single_use_agents`, `already_inline_candidates` |

### Dispatch template

```
Analyze the following agent files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]

Context (include only the fields this lens requires per the table above):

tool_inventory: {mapping of agent → [tools]}
model_assignments: {mapping of agent → model}
caller_map: {mapping of agent → [spawning skills]}
single_use_agents: [list of agents with exactly one spawning skill]
already_inline_candidates: [single-use agents that could be inlined]
```

---

## Design Skill Lenses

Agents: `design-skill-lens-shared-backbone`, `design-skill-lens-complexity`,
`design-skill-lens-near-duplicates`, `design-skill-lens-handoff-gaps`,
`design-skill-lens-preplanning`

### Required context fields per lens

| Lens | Required context fields |
|------|------------------------|
| `design-skill-lens-shared-backbone` | `agent_usage_counts` |
| `design-skill-lens-complexity` | `phase_counts`, `no_agent_skills` |
| `design-skill-lens-near-duplicates` | `agent_usage_counts`, `phase_counts` |
| `design-skill-lens-handoff-gaps` | `handoff_chains` |
| `design-skill-lens-preplanning` | `preplanning_skills`, `layer1_diagram_content` |

### Dispatch template

```
Analyze the following SKILL.md files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]

Context (include only the fields this lens requires per the table above):

agent_usage_counts: {mapping of agent-type → [skill names that spawn it]}
phase_counts: {mapping of skill → phase count}
no_agent_skills: [list of skills with zero spawned agents]
handoff_chains: {mapping of skill → [output files]}
preplanning_skills: [pre-planning skill names — skills shown with dashed arrows in Layer 1]
layer1_diagram_content: [raw text of the Layer 1 Mermaid diagram from docs/al-dev-plugin-map.md]
```

---

## Quality and Naming Lenses

Agents: `quality-agent-lens-*`, `quality-skill-lens-*`, `naming-convention-lens`

These lenses derive all findings from the file list alone. No context structures
are required.

### Dispatch template (quality agent lenses)

```
Analyze the following agent files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]
```

### Dispatch template (quality skill lenses)

```
Analyze the following SKILL.md files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]
```

### Dispatch template (naming-convention-lens)

```
Analyze the following files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]

Convention doc:
/Users/russelllaing/al-dev-shared/docs/al-dev-naming-convention.md
```

---

## Background

`/plugin-health` Phase 2.1 historically passed all 10 context structures to
every design and quality lens. This created maintenance burden: callers that
needed 2 fields received 8 inert ones. This file canonicalizes the minimum
required context per lens class so dispatchers pass lean, correct prompts.

**Inert fields by lens class (confirmed by rubber-duck 2026-05-29):**
- Design agent lenses receive: `phase_counts`, `handoff_chains`, `preplanning_skills`,
  `agent_usage_counts`, `no_agent_skills` — not used
- Design skill lenses receive: `tool_inventory`, `model_assignments`, `caller_map`,
  `single_use_agents`, `already_inline_candidates` — not used
- Quality lenses: all 10 context structures — not used
```

- [ ] **Step 2: Verify the file was written**

```bash
ls -la profile-al-dev-shared/knowledge/lens-invocation-patterns.md
wc -l profile-al-dev-shared/knowledge/lens-invocation-patterns.md
```

Expected: file exists; line count ~110.

- [ ] **Step 3: Confirm no forbidden patterns**

```bash
grep -n "TODO\|TBD\|YYYY-MM-DD\|\[date\]" profile-al-dev-shared/knowledge/lens-invocation-patterns.md
```

Expected: no output.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/lens-invocation-patterns.md
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
docs(knowledge): add lens-invocation-patterns with required context per lens class

Canonicalises the context fields each design lens type actually requires.
Identifies layer1_diagram_content as required by design-skill-lens-preplanning
but missing from plugin-health Phase 2.1 dispatch (fixed in next commit).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Update plugin-health Phase 2.1 dispatch templates

**Files:**
- Modify: `.claude/skills/plugin-health/SKILL.md`

Replace the single 10-field dispatch template (passed to all lenses) with
three targeted templates: one for design-agent lenses, one for design-skill
lenses, and one for quality/naming lenses. Also adds `layer1_diagram_content`
to the Phase 2.0 named-variable list (it was captured implicitly but not named).

- [ ] **Step 1: Read Phase 2.0 named-variable list**

```bash
grep -n "layer1_diagram_content\|no_agent_skills\|Store all" .claude/skills/plugin-health/SKILL.md | head -10
```

Expected: `no_agent_skills` at line ~80; `Store all 10` at line ~82; `layer1_diagram_content` absent (to confirm it needs to be added).

- [ ] **Step 2: Add layer1_diagram_content to Phase 2.0 named-variable list**

In `.claude/skills/plugin-health/SKILL.md`, replace:

```
**Store all 10 context structures as named variables for reuse in dispatch prompts:**
1. `tool_inventory`
2. `model_assignments`
3. `caller_map`
4. `phase_counts`
5. `handoff_chains`
6. `preplanning_skills`
7. `agent_usage_counts`
8. `single_use_agents`
9. `already_inline_candidates`
10. `no_agent_skills`
```

with:

```
**Store all 11 context structures as named variables for reuse in dispatch prompts:**
1. `tool_inventory`
2. `model_assignments`
3. `caller_map`
4. `phase_counts`
5. `handoff_chains`
6. `preplanning_skills`
7. `agent_usage_counts`
8. `single_use_agents`
9. `already_inline_candidates`
10. `no_agent_skills`
11. `layer1_diagram_content` — raw text of the Layer 1 Mermaid diagram from
    `docs/al-dev-plugin-map.md` (required by `design-skill-lens-preplanning`)
```

- [ ] **Step 3: Read the current Phase 2.1 dispatch template**

```bash
grep -n "Dispatch prompt template\|Convention doc" .claude/skills/plugin-health/SKILL.md
```

Note the exact line numbers. The template block starts at "Dispatch prompt template" and ends after the convention doc line.

- [ ] **Step 4: Replace the single dispatch template with three targeted templates**

In `.claude/skills/plugin-health/SKILL.md`, replace:

```
Dispatch prompt template (substitute real paths and context):

```
Analyze the following files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]

Context structures (provided for all design and quality lenses):

tool_inventory: {mapping of agent → [tools]}
model_assignments: {mapping of agent → model}
caller_map: {mapping of agent → [spawning skills]}
phase_counts: {mapping of skill → phase count}
handoff_chains: {mapping of skill → [output files]}
preplanning_skills: [list of pre-planning skill names]
agent_usage_counts: {mapping of agent → spawn count}
single_use_agents: [list of agents with exactly one spawning skill]
already_inline_candidates: [single-use agents that could be inlined]
no_agent_skills: [list of skills with zero spawned agents]

Convention doc (naming-convention-lens only):
/Users/russelllaing/al-dev-shared/docs/al-dev-naming-convention.md
```
```

with:

```
Dispatch prompt templates — use the variant matching each lens class.
See `knowledge/lens-invocation-patterns.md` for the full context-field reference.

**For design-agent-lens-* agents:**
```
Analyze the following agent files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]

Context (include only the fields this lens requires — see knowledge/lens-invocation-patterns.md):

tool_inventory: {mapping of agent → [tools]}
model_assignments: {mapping of agent → model}
caller_map: {mapping of agent → [spawning skills]}
single_use_agents: [list of agents with exactly one spawning skill]
already_inline_candidates: [single-use agents that could be inlined]
```

**For design-skill-lens-* agents:**
```
Analyze the following SKILL.md files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]

Context (include only the fields this lens requires — see knowledge/lens-invocation-patterns.md):

agent_usage_counts: {mapping of agent-type → [skill names that spawn it]}
phase_counts: {mapping of skill → phase count}
no_agent_skills: [list of skills with zero spawned agents]
handoff_chains: {mapping of skill → [output files]}
preplanning_skills: [pre-planning skill names (dashed arrows in Layer 1)]
layer1_diagram_content: [raw text of Layer 1 Mermaid diagram from docs/al-dev-plugin-map.md]
```

**For quality-agent-lens-*, quality-skill-lens-*, and naming-convention-lens:**
```
Analyze the following files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]
```

Convention doc (naming-convention-lens only):
/Users/russelllaing/al-dev-shared/docs/al-dev-naming-convention.md
```

- [ ] **Step 5: Verify the old 10-field block is gone**

```bash
grep -n "Context structures (provided for all" .claude/skills/plugin-health/SKILL.md
```

Expected: no output.

- [ ] **Step 6: Verify the three new templates are present**

```bash
grep -n "For design-agent-lens\|For design-skill-lens\|For quality-agent-lens" .claude/skills/plugin-health/SKILL.md
```

Expected: 3 matching lines.

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/skills/plugin-health/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
fix(skill): plugin-health Phase 2.1 passes lean context per lens class

Replaces single 10-field dispatch template with three targeted templates:
design-agent (5 fields), design-skill (6 fields including missing
layer1_diagram_content), quality/naming (file list only).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Fix audit-quality — Phase 4 bloat + pseudo-code clarity

**Files:**
- Modify: `.claude/skills/audit-quality/SKILL.md`

Two edits: (1) add a "Reference only" comment to the pseudo-code block at lines 32–49, (2) extract the duplicated agent/skill report templates in Phase 4 (lines 146–241) into a shared parameterised template, reducing Phase 4 from ~96 lines to ~55.

- [ ] **Step 1: Confirm pseudo-code block location**

```bash
grep -n "import sys\|# Reference only" .claude/skills/audit-quality/SKILL.md
```

Expected: `import sys` at line ~34; no "Reference only" hit.

- [ ] **Step 2: Add the "Reference only" comment above the pseudo-code block**

In `.claude/skills/audit-quality/SKILL.md`, replace:

```
```python
import sys
args = sys.argv[1:]  # Get arguments after command name
```

with:

```
```python
# Reference only — this parsing logic is embedded in the skill's runtime.
# Do not execute this block directly.
import sys
args = sys.argv[1:]  # Get arguments after command name
```

- [ ] **Step 3: Confirm the Phase 4 duplication**

```bash
grep -n "## Phase 4\|### Full run\|### Scoped run\|For agents\|For skills" .claude/skills/audit-quality/SKILL.md | head -20
```

Identify the line numbers for Phase 4 start, the "For agents" template block, and the "For skills" template block. Confirm they have the same structure with only Type/Types/prefix/output-file substitutions.

- [ ] **Step 4: Replace Phase 4 with a parameterised template**

In `.claude/skills/audit-quality/SKILL.md`, replace the entire Phase 4 block from `## Phase 4 — Write the Report` through the line just before `## Phase 5`:

Old (lines 146–241):

```
## Phase 4 — Write the Report

### Full run (no object name passed)

**For agents, fully replace `docs/al-dev-agent-quality.md`:**

```markdown
# AL Dev Agent Quality Audit

**Last run:** <today's date>
**Agents audited:** <N>

## Summary

| Severity | Count |
|----------|-------|
| High     | <N>   |
| Medium   | <N>   |
| Low      | <N>   |

## Findings

### al-dev-<agent-name>

**[High] Prompt Clarity**
Observation: <offending text or pattern>
Fix: <one-line suggestion>

**[Medium] Bloat**
Observation: <what is bloated>
Fix: <one-line suggestion>

---

### al-dev-<other-agent> — No findings.

---
```

**For skills, fully replace `docs/al-dev-skill-quality.md`:**

```markdown
# AL Dev Skill Quality Audit

**Last run:** <today's date>
**Skills audited:** <N>

## Summary

| Severity | Count |
|----------|-------|
| High     | <N>   |
| Medium   | <N>   |
| Low      | <N>   |

## Findings

### /<skill-name>

**[High] Prompt Clarity**
Observation: <offending text or pattern>
Fix: <one-line suggestion>

**[Medium] Bloat**
Observation: <what is bloated>
Fix: <one-line suggestion>

---

### /<other-skill> — No findings.

---
```

Ordering: objects with findings first (highest-severity finding descending), then
clean objects. Each object section ends with `---`.

### Scoped run (object name passed)

1. Determine report file:
   - **For agents:** `docs/al-dev-agent-quality.md`
   - **For skills:** `docs/al-dev-skill-quality.md`

2. Read the report file if it exists.
3. Locate the section for the named object:
   - **For agents:** from `### al-dev-<arg>` to just before the next `### al-dev-` heading or end of `## Findings`
   - **For skills:** from `### /<arg>` to just before the next `### /` heading or end of `## Findings`
4. Build a replacement section with new findings (or the no-findings variant).
5. Replace in-place using the Edit tool, with the old section as `old_string`.
6. If the section doesn't exist yet: append at the end of `## Findings`.
7. Recalculate Summary counts by scanning all `**[High]`, `**[Medium]`, `**[Low]`
   occurrences in the updated file, then rewrite the Summary table.
8. If the report file doesn't exist: write a new full report containing only
   the named object's section.
```

New (replaces lines 146–241):

```
## Phase 4 — Write the Report

**Report template** (shared structure for agent and skill full runs):

```markdown
# AL Dev {Type} Quality Audit

**Last run:** {today's date}
**{Types} audited:** {N}

## Summary

| Severity | Count |
|----------|-------|
| High     | {N}   |
| Medium   | {N}   |
| Low      | {N}   |

## Findings

### {prefix}{name}

**[High] Prompt Clarity**
Observation: {offending text or pattern}
Fix: {one-line suggestion}

**[Medium] Bloat**
Observation: {what is bloated}
Fix: {one-line suggestion}

---

### {prefix}{other} — No findings.

---
```

**Substitution variables:**

| Variable | Agents | Skills |
|----------|--------|--------|
| `{Type}` | `Agent` | `Skill` |
| `{Types}` | `Agents` | `Skills` |
| `{prefix}` | `al-dev-` | `/` |
| Output file | `docs/al-dev-agent-quality.md` | `docs/al-dev-skill-quality.md` |

### Full run (no object name passed)

Fully replace the output file using the report template with the appropriate
substitution variables. Ordering: objects with findings first (highest-severity
finding descending), then clean objects. Each object section ends with `---`.

### Scoped run (object name passed)

1. Determine report file per the substitution table above.
2. Read the report file if it exists.
3. Locate the section for the named object:
   - **For agents:** from `### al-dev-<arg>` to just before the next `### al-dev-` heading or end of `## Findings`
   - **For skills:** from `### /<arg>` to just before the next `### /` heading or end of `## Findings`
4. Build a replacement section with new findings (or the no-findings variant).
5. Replace in-place using the Edit tool, with the old section as `old_string`.
6. If the section doesn't exist yet: append at the end of `## Findings`.
7. Recalculate Summary counts by scanning all `**[High]`, `**[Medium]`, `**[Low]`
   occurrences in the updated file, then rewrite the Summary table.
8. If the report file doesn't exist: write a new full report containing only
   the named object's section.
```

- [ ] **Step 5: Verify Phase 4 line count is reduced**

```bash
awk '/^## Phase 4/,/^## Phase 5/' .claude/skills/audit-quality/SKILL.md | wc -l
```

Expected: ≤60 lines (was 96).

- [ ] **Step 6: Verify "Reference only" comment is present**

```bash
grep -n "Reference only" .claude/skills/audit-quality/SKILL.md
```

Expected: 1 hit at line ~32.

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/skills/audit-quality/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
fix(skill): audit-quality Phase 4 extract shared template + clarify pseudo-code

Adds 'Reference only' comment to pseudo-code block. Reduces Phase 4 from 96
to ~55 lines by extracting shared agent/skill report template with substitution
variables, eliminating ~70 lines of duplication.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Trim Glob from 20 lens agents

**Files:**
- Modify: `profile-al-dev-shared/agents/design-agent-lens-caller-alignment.md` → `tools: ["Read", "Grep"]`
- Modify ×19: all other lens agents → `tools: ["Read"]`

Rubber-duck confirmed: all 20 agents have `Glob` in frontmatter `tools` but never use it in their bodies — dispatchers provide explicit file lists via the dispatch prompt. `design-agent-lens-caller-alignment` keeps `Grep` (actively used in body to search skill files).

- [ ] **Step 1: Confirm current Glob count**

```bash
grep -rl '"Glob"' profile-al-dev-shared/agents/ | grep "lens" | wc -l
```

Expected: 20.

- [ ] **Step 2: Edit design-agent-lens-caller-alignment (keep Grep, remove Glob)**

Read `profile-al-dev-shared/agents/design-agent-lens-caller-alignment.md` first.
In the frontmatter, replace:

```
tools: ["Read", "Glob", "Grep"]
```

with:

```
tools: ["Read", "Grep"]
```

- [ ] **Step 3: Edit the remaining 19 lens agents (remove Glob, keep Read)**

For each of the following 19 files, read the file, then replace `tools: ["Read", "Glob"]` with `tools: ["Read"]`:

```
profile-al-dev-shared/agents/design-agent-lens-model-fit.md
profile-al-dev-shared/agents/design-agent-lens-scope-isolation.md
profile-al-dev-shared/agents/design-agent-lens-tool-hygiene.md
profile-al-dev-shared/agents/design-agent-lens-usage-patterns.md
profile-al-dev-shared/agents/design-skill-lens-complexity.md
profile-al-dev-shared/agents/design-skill-lens-handoff-gaps.md
profile-al-dev-shared/agents/design-skill-lens-near-duplicates.md
profile-al-dev-shared/agents/design-skill-lens-preplanning.md
profile-al-dev-shared/agents/design-skill-lens-shared-backbone.md
profile-al-dev-shared/agents/quality-agent-lens-bloat.md
profile-al-dev-shared/agents/quality-agent-lens-clarity.md
profile-al-dev-shared/agents/quality-agent-lens-description.md
profile-al-dev-shared/agents/quality-agent-lens-name-fit.md
profile-al-dev-shared/agents/quality-agent-lens-structure.md
profile-al-dev-shared/agents/quality-skill-lens-bloat.md
profile-al-dev-shared/agents/quality-skill-lens-clarity.md
profile-al-dev-shared/agents/quality-skill-lens-description.md
profile-al-dev-shared/agents/quality-skill-lens-name-fit.md
profile-al-dev-shared/agents/quality-skill-lens-structure.md
```

- [ ] **Step 4: Verify Glob is fully removed**

```bash
grep -rl '"Glob"' profile-al-dev-shared/agents/ | grep "lens"
```

Expected: no output.

- [ ] **Step 5: Verify Grep is still present in caller-alignment**

```bash
grep -n '"Grep"' profile-al-dev-shared/agents/design-agent-lens-caller-alignment.md
```

Expected: 1 hit in frontmatter.

- [ ] **Step 6: Run agent structure validator**

```bash
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
```

Expected: no errors (or same errors as before this task — the validator checks structure, not tool lists).

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
fix(agents): trim Glob from all 20 lens agent frontmatter

Lens agents receive explicit file lists via dispatch prompt and have no need
for pattern-based discovery. Retains Grep in design-agent-lens-caller-alignment
(actively used to search skill files for invocation patterns).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Execution Order

```
Task 1 → Task 2    (create knowledge file, then update plan-map-changes to reference it)
Task 3 → Task 4    (create lens patterns doc, then update plugin-health)
Task 5             (independent — audit-quality fix)
Task 6             (independent — Glob trim)
```

Tasks 3–6 are independent of Tasks 1–2. Tasks 5 and 6 are independent of each other
and of the knowledge-file pair. If running with parallel subagents, Tasks 1 and 3
can be dispatched together (both create new files with no dependencies), then Tasks
2, 4, 5, 6 dispatched in parallel once their dependencies are met.

## Token Estimate

- Task 1: ~400 tokens (new file write)
- Task 2: ~600 tokens (3 edits to plan-map-changes)
- Task 3: ~700 tokens (new file write)
- Task 4: ~800 tokens (2 edits to plugin-health)
- Task 5: ~900 tokens (2 edits to audit-quality)
- Task 6: ~1 200 tokens (20 × read + edit)

**Total:** ~4 600 tokens
