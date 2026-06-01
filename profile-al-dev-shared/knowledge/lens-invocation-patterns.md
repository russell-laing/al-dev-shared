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
layer1_diagram_content: [raw text of the Layer 1 Mermaid diagram from docs/al-dev-skills-map.md]
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

`/plugin-health-audit` Phase 2.1 historically passed all 10 context structures to
every design and quality lens. This created maintenance burden: callers that
needed 2 fields received 8 inert ones. This file canonicalizes the minimum
required context per lens class so dispatchers pass lean, correct prompts.

**Inert fields by lens class (confirmed by rubber-duck 2026-05-29):**
- Design agent lenses receive: `phase_counts`, `handoff_chains`, `preplanning_skills`,
  `agent_usage_counts`, `no_agent_skills` — not used
- Design skill lenses receive: `tool_inventory`, `model_assignments`, `caller_map`,
  `single_use_agents`, `already_inline_candidates` — not used
- Quality lenses: all 10 context structures — not used
