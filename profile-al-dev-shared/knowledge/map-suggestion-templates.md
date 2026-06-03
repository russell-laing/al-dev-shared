# Map Suggestion Templates

Suggestion format templates used by `/verify-map-suggestions` when
writing map observations and verification outputs. Reference this file instead
of embedding templates inline in the skill body.

---

## Agent suggestion templates

### Trim

```
**Trim: al-dev-<name>**
Observation: Tools list includes [tool]; system prompt body contains no [tool] usage.
Suggestion: Remove [tool] from the tools list in the agent frontmatter.
Trade-off: Minimal — tool wasn't used; tighter least-privilege posture.
```

### Promote

```
**Promote: al-dev-<name>**
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

## Skill suggestion templates

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
