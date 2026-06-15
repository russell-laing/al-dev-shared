# Lens Invocation Patterns

Canonical context requirements for design lens agents. Use this reference when
building dispatch prompts in skills that invoke design lenses. Quality lenses and
the naming-convention lens need only a file list.

See also: `knowledge/architect-invocation-patterns.md` (parallel pattern for
`al-dev-solution-architect`).

---

## Finding evidence contract

Append this contract to every lens prompt, regardless of lens class. It is the
first-line defence against false-positive findings: a lens that must quote the
offending text cannot flag a problem that is not actually present.

Every finding a lens returns must include:

- the subject location as `file:line`,
- a short quoted snippet of the offending text at that location, and
- a one-line reason the snippet is a real issue (not a stylistic preference).

A lens must **omit** any finding it cannot ground in a quoted snippet — drop
speculative "consider whether…" or "it may be worth…" observations rather than
emitting them. Unverifiable findings are downstream-dropped at the report stage,
so emitting them only adds noise.

---

## Design Agent Lenses

Agents: `design-agent-lens-caller-alignment`, `design-agent-lens-model-fit`,
`design-agent-lens-scope-isolation`, `design-agent-lens-tool-hygiene`,
`design-agent-lens-usage-patterns`

### Required context fields per lens (agent lenses)

| Lens | Required context fields |
|------|------------------------|
| `design-agent-lens-tool-hygiene` | `tool_inventory` |
| `design-agent-lens-model-fit` | `model_assignments` |
| `design-agent-lens-scope-isolation` | *(none — file list only)* |
| `design-agent-lens-caller-alignment` | `caller_map` |
| `design-agent-lens-usage-patterns` | `single_use_agents`, `already_inline_candidates` |

### Dispatch template (agent lenses)

```text
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
`design-skill-lens-preplanning`, `design-skill-lens-surface-placement`

### Required context fields per lens (skill lenses)

| Lens | Required context fields |
|------|------------------------|
| `design-skill-lens-shared-backbone` | `agent_usage_counts` |
| `design-skill-lens-complexity` | `phase_counts`, `no_agent_skills` |
| `design-skill-lens-near-duplicates` | `agent_usage_counts`, `phase_counts` |
| `design-skill-lens-handoff-gaps` | `handoff_chains` |
| `design-skill-lens-preplanning` | `preplanning_skills`, `layer1_diagram_content` |
| `design-skill-lens-surface-placement` | `no_agent_skills` |

### Dispatch template (skill lenses)

```text
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

### Complexity Outliers — Verdict Field

Lines from the Complexity Outliers lens carry an extra `verdict` field between
severity and the observation:

```text
verdict=[Atomise|Absorb|None]
```

- `verdict=Atomise`: skill has two independently-runnable phase groups separated
  by a USER_GATE or phase boundary; recommend splitting into two skills.
- `verdict=Absorb`: skill has zero core logic (≤2 phases, no agent dispatch);
  recommend folding into its caller.
- `verdict=None`: monitor only; no structural action required.

When parsing Complexity Outliers findings, extract and act on this field before
writing the dossier section.

---

## Quality and Naming Lenses

Agents: `quality-agent-lens-*`, `quality-skill-lens-*`, `naming-convention-lens`

These lenses derive all findings from the file list alone. No context structures
are required.

### Dispatch template (quality agent lenses)

```text
Analyze the following agent files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]
```

### Dispatch template (quality skill lenses)

```text
Analyze the following SKILL.md files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]
```

### Dispatch template (naming-convention-lens)

```text
Analyze the following files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]

Convention doc:
[absolute path to docs/al-dev-naming-convention.md in the repo under audit]
```

> **Caller contract:** `naming-convention-lens` has exactly one dispatcher
> (`plugin-health-discover`) and one downstream consumer (`plugin-health-report`).
> Changes to this lens's input contract or output format affect only those two
> skills — no other callers exist in the tooling surface.

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

---

## Workflow Dispatch Pattern

When dispatching multiple lens agents in parallel, use the canonical in-session
background-dispatch pattern in
[`background-agent-dispatch.md`](background-agent-dispatch.md): dispatch one
background agent per lens, hand off through artifact files, and gate on artifact
presence. This is the canonical orchestration mechanism for multi-lens sweeps.
Individual lens dispatches use the single-lens template above.

### Sequential single-lens dispatch

For one lens or sequentially ordered lenses:

```text
Dispatch: <lens-agent-name>
Context: [fields from the per-lens table above — include only required fields]
```

### Parallel multi-lens dispatch (health sweep)

For 3+ independent lenses (e.g., a full plugin health audit), dispatch all in
one parallel call. Lenses are independent — no lens output is another's input.

Steps:

1. Build the file list for each surface (agents or skills).
2. Build the per-lens context fields (tool_inventory, model_assignments, etc.)
   from the plugin graph and map files.
3. Dispatch all lenses in a single parallel block.
4. Collect all outputs before synthesising findings.

See `/plugin-health-discover` for the canonical multi-lens dispatch implementation.
