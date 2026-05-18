---
name: analyze-plugin-design
description: >-
  Analyze profile-al-dev-shared plugin architecture for improvement opportunities,
  then write concrete Atomise / Connect / Merge / Promote suggestions to the
  Observations section of docs/al-dev-plugin-map.md. Use whenever you want
  strategic recommendations for making the plugin easier to maintain or more
  composable — including when someone asks "should these skills be merged?",
  "what patterns could be shared?", "is this skill doing too much?", "how can
  we simplify the plugin?", or "what's missing from the plugin?". Run after
  /review-plugin-map so the map is accurate before analysis begins.
  Triggers on: "analyze plugin design", "suggest skill improvements",
  "atomise skill", "merge agents", "plugin architecture review",
  "optimize plugin", "plugin improvement suggestions".
argument-hint: "[focus: atomise|connect|merge|all]"
---

# Skill: /analyze-plugin-design

Strategic analysis of the al-dev plugin architecture. Reads the current plugin
map, applies four analytical lenses, and writes concrete improvement suggestions
to the `## Observations` section of `docs/al-dev-plugin-map.md`.

Run `/review-plugin-map` first if the map may be out of date.

---

## Step 1 — Read the Plugin Map

Read `docs/al-dev-plugin-map.md` in full. As you read, build four working lists:

1. **Agent inventory** — for every `al-dev-shared:` agent type mentioned in
   drill-downs, note which skills use it and how many times.

2. **Phase counts** — record the number of named phases per skill.

3. **File handoff chains** — trace `.dev/` output files from Layer 1 and Layer 2.
   Note when one skill's output (e.g. `solution-plan.md`) is consumed by another.

4. **No-agent skills** — list skills whose drill-down contains only `(skill itself)`
   nodes (no dedicated agent spawned).

5. **Pre-planning tributaries** — list skills that produce output files consumed
   by `/al-dev-plan` or `/al-dev-investigate` before implementation begins (e.g.
   `interview-requirements.md`, `explore-findings.md`). For each, note whether it
   appears in the Layer 1 diagram as a dashed tributary arrow (`-.->`) rather than
   a main-spine node.

If an argument was passed, restrict analysis to that category
(`atomise`, `connect`, `merge`, or `all` / no argument = `all`).

---

## Step 2 — Apply Four Analytical Lenses

### Lens A — Shared Execution Backbone (→ Connect or Promote)

For each agent type used by 2+ skills:
- Are the spawn patterns identical or slightly different?
- If identical: this is a candidate for a documented "canonical pattern" in
  `knowledge/` that all callers can reference — preventing drift when the
  pattern needs updating.
- If different: note what varies; that variation might be worth making explicit.

### Lens B — Complexity Outliers (→ Atomise or Absorb)

Rank skills by phase count.

**High-phase skills (6+ phases):** Ask whether phases cluster into two
distinct concerns (e.g., pre-flight + execution + review). If yes, the skill
may be doing two separable jobs and a split would make each half easier to
understand and test independently.

**Zero-agent, 2-phase skills:** Ask whether they could be absorbed into an
adjacent skill as an option flag rather than a separate invocation.

### Lens C — Near-Duplicate Shapes (→ Merge)

Find pairs of skills with similar drill-down structure: same agent types,
similar phase count, similar output file name pattern.

Ask: is the difference between them a small delta (one extra phase, one
extra output file)? If yes, could the simpler skill become an option or
mode of the more complex one?

### Lens D — Handoff Chain Gaps (→ Extend)

Trace the longest file handoff chains in Layer 1. Look for:
- A well-established chain that has an obvious next step not yet covered
  (e.g., the dev chain ends at commit — is there a natural next skill?).
- Outputs that are produced but never consumed by any downstream skill
  (orphaned outputs that could be useful if a skill consumed them).

### Lens E — Pre-planning and Brainstorming Skills

Pre-planning skills produce structured outputs that feed into the planning phase.
They are optional but high-value tributaries to the main development spine.

**Canonical pre-planning skills in this plugin:**

- `/al-dev-interview` — requirements-gathering for AL/BC features. Analogous to
  `superpowers:brainstorming` in the general superpowers skill set, but domain-
  specific: conducts a structured BC/AL interview, pre-researches base app objects
  via the AL symbols MCP, and produces a formal requirements document with
  acceptance-criteria tokens (`interview-requirements.md`).
- `/al-dev-explore` — fast codebase investigation producing `explore-findings.md`,
  consumed by `/al-dev-investigate` and `/al-dev-plan`.

For each pre-planning skill found in the inventory, ask:
- Does it appear in the Layer 1 diagram as a dashed tributary (`-.->`) rather
  than a main-spine node?
- Is its output filename referenced in the Layer 1 handoff labels?
- Is there a downstream skill that explicitly names it as an input?

Flag any pre-planning skill that is active but absent from the Layer 1 diagram as
an **Extend** candidate. Flag any skill that feeds a downstream step but whose
output is unnamed in the diagram as a labelling gap.

---

## Step 3 — Draft Suggestions

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

## Step 4 — Complete the Agent Inventory Tables

Fill in the four inventory tables for the Observations section:

**Agents used by only one skill** — list each single-use agent and its skill.
These are candidates for inlining into the skill body if they're simple, or
for abstraction if they're likely to be reused.

**Skills with no dedicated agent** — list each. Note whether they're candidates
for absorption into an adjacent skill.

**Potential shared agents** — list agent types used by 2+ skills.

---

## Step 5 — Write to `docs/al-dev-plugin-map.md`

Replace the entire `## Observations` section (from the `## Observations` heading
to the end of the file) with:

```markdown
## Observations

> Generated by /analyze-plugin-design on [today's date].
> Run /review-plugin-map first if the skill list has changed since this was written.

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

## Step 6 — Present to User

After writing the file:

1. Print a one-line summary per suggestion (type + subject).
2. Mark the **highest-leverage** suggestion (best improvement-to-disruption ratio)
   with `← highest leverage`.
3. Ask: "Would you like to act on any of these now?"
