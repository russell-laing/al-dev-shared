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
