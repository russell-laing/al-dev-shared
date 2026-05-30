---
name: draft-map-suggestions
description: >-
  Drafts improvement suggestions from aggregated lens findings and writes them
  to the Observations section of the appropriate map document. Called by
  /analyze-agent-design (--type agent) and /analyze-skill-design (--type skill)
  after lens aggregation. Requires --type argument; not intended as a standalone
  user-facing entry point.
argument-hint: "--type agent|skill"
---

# Skill: /draft-map-suggestions

Converts aggregated lens findings into structured map observations. Requires
`--type agent` or `--type skill` to select the correct templates and output file.

---

## Phase 1 — Parse argument

Read the required `--type` argument:
- `--type agent` → writes to `docs/al-dev-agent-map.md`; uses Trim/Remodel/Split/Inline/Align vocabulary
- `--type skill` → writes to `docs/al-dev-skills-map.md`; uses Atomise/Connect/Merge/Promote/Extend vocabulary

If `--type` is missing or not `agent`/`skill`, report the error and stop.

---

## Phase 2 — Receive aggregated findings

The caller passes findings as input context in the dispatch prompt.

For `--type agent`, expect: Trim candidates, Remodel candidates, Split candidates,
Align candidates, Inline candidates — from Phase 3 of `analyze-agent-design`.
Also receive the working lists from Phase 1 of `analyze-agent-design`: tool inventory,
model assignments, caller map, single-use agents, undocumented agents, existing inline candidates.

For `--type skill`, expect: Connect/Promote candidates, Atomise/Absorb candidates,
Merge candidates, Extend candidates, Diagram/labelling gaps — from Phase 3 of `analyze-skill-design`.
Also receive the working lists from Phase 1 of `analyze-skill-design`: agent usage counts,
phase counts, file handoff chains, no-agent skills, pre-planning tributaries.

---

## Phase 3 — Draft suggestions

Write 3–6 high-quality suggestions. Skip patterns that don't yield a real improvement.
Before writing each suggestion, check the current `## Observations` section of the
target map file — skip anything already marked `← implemented`.

**For `--type agent`**, use these templates:

```
**Trim: al-dev-<name>**
Observation: Tools list includes [tool]; system prompt body contains no [tool] usage.
Suggestion: Remove [tool] from the tools list in the agent frontmatter.
Trade-off: Minimal — tool wasn't used; tighter least-privilege posture.
```

```
**Remodel: al-dev-<name>**
Observation: Agent performs [task description]; currently assigned [current-model].
Suggestion: Change model to [new-model] — task [does/does not] require multi-file synthesis.
Trade-off: [Faster + cheaper / More capable]; justified because [reason].
```

```
**Split: al-dev-<name>**
Observation: System prompt describes [concern A] and [concern B] — separable concerns.
Suggestion: Extract [concern B] into a new agent al-dev-<new-name>.
Trade-off: New agent file to maintain; each agent's scope becomes narrower and easier to evolve.
```

```
**Inline: al-dev-<name>**
Observation: Spawned only by /skill-name; [N]-line system prompt; no Inputs/Outputs documented.
Suggestion: Absorb system prompt into /skill-name's dispatch block; delete the agent file.
Trade-off: Less indirection; agent no longer reusable if a second caller is added later.
```

```
**Align: al-dev-<name>**
Observation: /skill-name passes [file/param X]; agent Inputs table does not document [X].
Suggestion: Update the agent's Inputs table to reflect the actual caller contract.
Trade-off: Documentation-only change; prevents future caller confusion.
```

**For `--type skill`**, use these templates:

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

## Phase 4 — Complete inventory tables

**For `--type agent`**, build three inventory tables from the working lists supplied by the caller:

1. **Agents used by only one skill** — list each single-use agent and its sole caller.
2. **Agents with no inputs/outputs documentation** — list each (black-box agents).
3. **Potential shared agents** — list agents spawned by 2+ skills.

**For `--type skill`**, build three inventory tables:

1. **Agents used by only one skill** — list each single-use agent and its skill.
2. **Skills with no dedicated agent** — list each; note absorption candidates.
3. **Potential shared agents** — list agent types used by 2+ skills.

---

## Phase 5 — Dispatch diagram generation

Dispatch the `al-dev-diagram-generator` agent to generate the workflow diagram.
Pass the caller name so the diagram references the correct re-run command:
- For `--type agent`: pass `--caller-name analyze-agent-design`
- For `--type skill`: pass `--caller-name analyze-skill-design`

The generator writes `docs/al-dev-workflow-diagrams.md`.

---

## Phase 6 — Write observations to the map file

**For `--type agent`** — replace the entire `## Observations` section of `docs/al-dev-agent-map.md`:

```markdown
## Observations

> Generated by /analyze-agent-design on [today's date].
> Run /review-agent-map first if the agent list has changed since this was written.

### Agents used by only one skill

- **al-dev-<name>** — used only by /skill-name
[one bullet per single-use agent]

### Agents with no inputs/outputs documentation

- **al-dev-<name>** — [one-line description]
[one bullet per undocumented agent]

### Potential shared agents

- **al-dev-<name>** — used by /skill-a, /skill-b
[one bullet per shared agent]

### Quality suggestions

[one suggestion block per finding in Trim/Remodel/Split/Inline/Align format]
```

Update `**Last updated:**` in the document header to today's date.

**For `--type skill`** — replace the entire `## Observations` section of `docs/al-dev-skills-map.md`:

```markdown
## Observations

> Generated by /analyze-skill-design on [today's date].
> Run /review-skill-map first if the skill list has changed since this was written.

### Agents used by only one skill

[bullet per agent: "- **agent-type** — used only by /skill-name"]

### Skills with no dedicated agent (skill does the work itself)

[bullet per skill: "- **/skill-name** — [one-line description]"]

### Potential shared agents not yet extracted

[bullet per shared agent: "- **agent-type** — used by /skill-a, /skill-b, /skill-c"]

### Architectural suggestions

[one suggestion block per finding in Atomise / Connect / Merge / Promote / Extend format]

### Extension opportunities

[1–2 forward-looking Extend blocks, or "None identified at this time."]
```

Update `**Last updated:**` in the document header to today's date.

---

## Phase 7 — Present to user

After Phase 5 dispatch returns and the map file is written:

1. Print a one-line summary per suggestion (type + subject).
2. Mark the **highest-leverage** suggestion with `← highest leverage`.
3. Print: `Workflow diagram written to docs/al-dev-workflow-diagrams.md`
4. Ask: "Would you like to act on any of these now?"
