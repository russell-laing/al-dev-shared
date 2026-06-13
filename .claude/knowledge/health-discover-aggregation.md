# Health Discover — Pre-dispatch Aggregation

The context-extraction procedure run by `/plugin-health-discover` Phase 2 before
lenses are dispatched. Lenses in Phase 3 consume the mappings built here.

## Read and parse `docs/al-dev-agent-map.md`

- Extract the Agent Catalog table.
- For each agent row: extract agent name, model, tools list, and "Spawned by" field.
- Build: `tool_inventory`, `model_assignments`, `caller_map`.
- "Spawned by" may contain comma-separated names or "(none found)" — treat the
  latter as an empty list.

## Read and parse `docs/al-dev-skills-map.md`

- Extract the Layer 1 diagram block → `layer1_diagram_content`.
- For each skill section: extract phase count, agent references, output files.
- Build: `phase_counts`, `handoff_chains`, `preplanning_skills` (skills with
  `-.->` arrows).

## Derived dispatch context

Compute derived mappings:

- `agent_usage_counts`: agent → count of spawning skills.
- `single_use_agents`: agents where `agent_usage_counts == 1`.
- `already_inline_candidates`: filter of `single_use_agents`.
- `no_agent_skills`: skills with zero spawned agents.
