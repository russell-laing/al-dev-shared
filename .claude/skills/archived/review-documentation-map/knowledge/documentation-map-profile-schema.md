# Documentation Map Profile Schema

Use this reference when `/review-documentation-map` builds the working profile
table for a documentation map audit.

## Skills surface

For each active skill, read `profile-al-dev-shared/skills/<name>/SKILL.md` and
record one row with:

1. Phase count from the live phase headers.
2. Spawned agents named in explicit dispatch instructions.
3. Parallel pattern, if the skill documents one.
4. Output artifacts the skill writes.

Use the working table shape:

| Skill | Phases | Agents spawned | Pattern | Outputs |
| --- | --- | --- | --- | --- |

## Agents surface

For each active agent, read `profile-al-dev-shared/agents/<name>.md` and record
one row with:

1. `model` from frontmatter.
2. `tools` from frontmatter.
3. The first sentence of the frontmatter description.
4. Whether the body documents `## Inputs`.
5. Whether the body documents `## Outputs`.

Use the working table shape:

| Agent | Model | Tools | Has Inputs? | Has Outputs? |
| --- | --- | --- | --- | --- |

## Extraction checks

- Count only live phase or step headings that describe executable workflow
  stages.
- Treat missing `## Inputs` or `## Outputs` sections as `Not documented`.
- Keep archived items out of the table; Phase 1 has already filtered them out.
