---
name: analyze-skill-design
description: >-
  Analyze profile-al-dev-shared plugin architecture for improvement opportunities,
  then write concrete Atomise / Connect / Merge / Promote suggestions to the
  Observations section of docs/al-dev-plugin-map.md. Use whenever you want
  strategic recommendations for making the plugin easier to maintain or more
  composable — including when someone asks "should these skills be merged?",
  "what patterns could be shared?", "is this skill doing too much?", "how can
  we simplify the plugin?", or "what's missing from the plugin?". Run after
  /review-skill-map so the map is accurate before analysis begins.
  Triggers on: "analyze skill design", "suggest skill improvements",
  "atomise skill", "merge agents", "skill architecture review",
  "optimize skill design", "skill improvement suggestions".
argument-hint: "[focus: atomise|connect|merge|all]"
---

# Skill: /analyze-skill-design

Strategic analysis of the al-dev plugin architecture. Reads the current plugin
map, applies four analytical lenses, and writes concrete improvement suggestions
to the `## Observations` section of `docs/al-dev-plugin-map.md`.

Run `/review-skill-map` first if the map may be out of date.

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

## Phase 3 — Aggregate Findings

Collect all returned findings blocks. Parse each line:
`- **[subject]** | [Severity] | [observation] | [fix]`

Group by lens type to produce candidate lists for Phase 4:
- **Connect/Promote candidates** — from Shared Execution Backbone findings
- **Atomise/Absorb candidates** — from Complexity Outliers findings
- **Merge candidates** — from Near-Duplicate Shapes findings
- **Extend candidates** — from Handoff Chain Gaps findings
- **Diagram/labelling gaps** — from Pre-planning Skills findings

Keep the raw findings lines — they form the basis of Phase 4 suggestions.

---

## Phase 5 — Draft Suggestions, Inventory Tables, Diagram and Map

Invoke `/draft-map-suggestions --type skill`. Pass as context:
- The candidate lists from Phase 3 (Connect/Promote, Atomise/Absorb, Merge, Extend candidates with raw finding lines)
- The working lists from Phase 1 (agent usage counts, phase counts, file handoff chains,
  no-agent skills, pre-planning tributaries, Layer 1 diagram content)

`/draft-map-suggestions` handles: drafting suggestions, completing inventory tables,
dispatching the diagram generator, and writing to `docs/al-dev-plugin-map.md`.

---

## Phase 6 — Present to User

After Phase 5 invocation completes and both files are written:

1. Print a one-line summary per suggestion (type + subject).
2. Mark the **highest-leverage** suggestion (best improvement-to-disruption ratio)
   with `← highest leverage`.
3. Print: `Workflow diagram written to docs/al-dev-workflow-diagrams.md`
4. Ask: "Would you like to act on any of these now?"
