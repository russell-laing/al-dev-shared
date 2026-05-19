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

For each agent, pass this prompt (substituting actual data from Phase 1):

```
Analyze the following skill files. Apply your lens and return a findings block.

## File list
/absolute/path/to/skills/skill-name/SKILL.md
[one path per line]

## Context from plugin map analysis
Agent usage counts (agent-type → skills that use it):
[paste agent_usage_counts here]

Phase counts (skill-name → count):
[paste phase_counts here]

No-agent skills:
[comma-separated list]

Handoff chains:
[paste handoff_chains here — skill → output-file → consuming-skill]

Pre-planning skills:
[comma-separated list]

Layer 1 diagram content:
[paste the Layer 1 diagram block from docs/al-dev-plugin-map.md]
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

## Phase 5 — Draft Suggestions

Write 3–6 high-quality suggestions. Skip patterns that don't yield a real
improvement. Before writing a suggestion, check the current `## Observations`
section — if a suggestion identical or equivalent to yours is already marked
`← implemented`, skip it. Use these templates:

```
**Atomise: /skill-name**
Observation: Phases N–M handle X; phases N–M handle Y — separable concerns.
Suggestion: Extract [phase group] into /new-skill-name.
Trade-off: New skill to learn; each skill's scope becomes narrower and clearer.
```

```
**Connect: /skill-a and /skill-b**
Observation: Both spawn [agent-type] with the same pattern but define it independently.
Suggestion: Document the canonical spawn pattern in knowledge/[pattern-name].md;
  have both skills reference it.
Trade-off: Small authoring cost; drift is prevented when the pattern needs updating.
```

```
**Merge: /skill-a + /skill-b**
Observation: /skill-b is /skill-a plus [small delta]; users must choose between two
  near-identical skills.
Suggestion: Add [delta] as an option to /skill-a; archive /skill-b.
Trade-off: Simpler skill list; /skill-a's interface becomes slightly broader.
```

```
**Promote: [agent usage pattern]**
Observation: [agent-type] is invoked by N skills. The invocation is copy-pasted
  rather than shared.
Suggestion: Write a canonical invocation template in knowledge/ and link from each
  skill that uses it.
Trade-off: One canonical source; callers adapt slightly to reference it.
```

```
**Extend: [gap description]**
Observation: The [X → Y → Z] chain is well-established but stops at Z.
Suggestion: A /new-skill-name that consumes Z's output would complete the natural
  workflow and enable [use case].
Trade-off: Adds scope; only worth building if the use case is frequent.
```

---

## Phase 6 — Complete the Agent Inventory Tables

Fill in the four inventory tables for the Observations section:

**Agents used by only one skill** — list each single-use agent and its skill.
These are candidates for inlining into the skill body if they're simple, or
for abstraction if they're likely to be reused.

**Skills with no dedicated agent** — list each. Note whether they're candidates
for absorption into an adjacent skill.

**Potential shared agents** — list agent types used by 2+ skills.

---

## Phase 7 — Write to `docs/al-dev-plugin-map.md`

Replace the entire `## Observations` section (from the `## Observations` heading
to the end of the file) with:

```markdown
## Observations

> Generated by /analyze-skill-design on [today's date].
> Run /review-skill-map first if the skill list has changed since this was written.

### Agents used by only one skill

[bullet per agent: "- **agent-type** — used only by /skill-name"]

### Skills with no dedicated agent (skill does the work itself)

[bullet per skill: "- **/skill-name** — [one-line description of what it does alone]"]

### Potential shared agents not yet extracted

[bullet per shared agent: "- **agent-type** — used by /skill-a, /skill-b, /skill-c"]

### Architectural suggestions

[one suggestion block per finding in Atomise / Connect / Merge / Promote / Extend format]

### Extension opportunities

[1–2 forward-looking Extend blocks, or "None identified at this time."]
```

Update `**Last updated:**` in the document header to today's date.

---

## Phase 8 — Present to User

After writing the file:

1. Print a one-line summary per suggestion (type + subject).
2. Mark the **highest-leverage** suggestion (best improvement-to-disruption ratio)
   with `← highest leverage`.
3. Ask: "Would you like to act on any of these now?"
