# Documentation Map Comparison Rules

Use this reference when `/review-documentation-map` compares live source
profiles against the existing documentation map.

## Agent caller-set build

Caller-set cross-referencing applies only to the agents surface.

For each active agent:

1. Search `profile-al-dev-shared/skills/` and `.claude/skills/` for qualified
   `al-dev-shared:<agent-name>` dispatch references.
2. Search the same skill roots for short-name prose references.
3. Union both result sets, then run one final `sort -u` across the merged list.
4. Extract the skill directory names from the matching paths to build the
   caller set.

Record:

- `Spawned by` — deduped list of skill names.
- `Spawn count` — `single-use` for one caller or `shared` for two or more.

## Comparison rules

When the working tables are complete, compare them against the selected map:

- Skills map Layer 1: nodes, edges, `style` directives, and handoff labels must
  match the live lifecycle.
- Skills map Layer 2: each active skill needs a drill-down whose phases, agent
  usage, and outputs match the working table.
- Agent map Layer 1: each active agent row must match live model, tools, and
  caller set.
- Agent map Layer 2: each active agent profile must match the live description,
  caller set, and documented Inputs/Outputs.

## Mermaid guard

For Mermaid-backed skills maps, treat ghost nodes and orphaned `style`
directives as discrepancies. A `style` line is valid only when its node ID
still appears in a node declaration or edge.
