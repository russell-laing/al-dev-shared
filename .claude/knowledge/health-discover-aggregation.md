# Health Discover — Pre-dispatch Aggregation

The context-extraction procedure run by `/discover-plugin-health` Phase 2 before
lenses are dispatched. Lenses in Phase 3 consume the mappings built here.

## Read and parse `docs/agent_map.md`

- Extract the Agent Catalog table.
- For each agent row: extract agent name, model, tools list, and "Spawned by" field.
- Build: `tool_inventory`, `model_assignments`, `caller_map`.
- "Spawned by" may contain comma-separated names or "(none found)" — treat the
  latter as an empty list.

## Read and parse `docs/skills_map.md`

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

## Write the run manifest

After computing the mappings, write one manifest artifact at
`.dev/<date>-discover-plugin-health-context.md` containing:

- `## Agent file list` — the absolute agent paths, one per line.
- `## Skill file list` — the absolute skill `SKILL.md` paths, one per line.
- One `##` section per context mapping (`tool_inventory`, `model_assignments`,
  `caller_map`, `single_use_agents`, `already_inline_candidates`, `phase_counts`,
  `handoff_chains`, `agent_usage_counts`, `no_agent_skills`, `preplanning_skills`,
  `layer1_diagram_content`), each rendering the mapping as readable text.

Phase 3 dispatch prompts reference this single file so the file list and context
are written once, not re-inlined into every per-lens prompt. Each lens reads only
the sections it needs: agent lenses read the agent list, skill lenses read the
skill list, and every lens reads the context fields named in its dispatch prompt
(per the per-lens table in
`profile-al-dev-shared/knowledge/lens-invocation-patterns.md`).

## Dimension-Aware Context Scope

When `--dimension` is set to `quality` or `naming`, skip the design-only
context mappings listed below — they are only consumed by design lenses and
extracting them on a quality- or naming-only run is wasted work.

| Dimension | Context mappings required |
| --- | --- |
| `naming` | None — file list only. Skip all 11 derived mappings. |
| `quality` | None — file list only. Skip all 11 derived mappings. |
| `design` | All 11 mappings (full procedure above) |
| `all` | All 11 mappings |

When `--dimension quality` or `--dimension naming`, build **no derived context at
all** — the quality combined readers and the static naming lens both run from the
file list alone (`profile-al-dev-shared/knowledge/lens-invocation-patterns.md`:
"Quality lenses: all 10 context structures — not used"). The
`discover-plugin-health` Phase 2 call passes the active `--dimension`; for
`quality`/`naming` it skips the map-parsing subagent entirely and writes the
Phase 1 globbed file lists straight to the manifest. Build the full 11 mappings
only for `design` and `all`.
