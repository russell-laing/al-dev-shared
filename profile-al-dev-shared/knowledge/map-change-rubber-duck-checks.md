# Map Change Rubber-Duck Checks

Type-specific verification checks for the `/plan-map-changes` skill Phase 2.
Apply these after completing the Universal checks (U1–U3) documented in the
skill body. Each section corresponds to one suggestion type.

---

## Connect — "document a shared pattern used by two skills"

- Read both skills' relevant sections. Are the definitions actually
  identical, or just similar? Quote both to confirm.
- Is the pattern stable, or does each skill customize it?

## Extend — "add nodes to a diagram"

- Is the change purely additive, or does it also require removing
  existing nodes? Check if a subsequent task (e.g., a Merge) will
  also touch the same diagram and plan the ordering accordingly.

## Merge — "consolidate skill B into skill A with a flag"

- Read skill B in full. List ALL phases, templates, and validators
  that are unique to it — the flag must activate all of them.
- If skill B has a validator script, confirm it exists with `ls`.
  If the script is absent, note in the rubber-duck record:
  `Scope gap: validator missing; plan must include manual validation or script creation`.
- What does archiving do to other skills that reference skill B?

## Move — "relocate a skill to .claude/skills/"

- Does any file in the skill directory use `Path(__file__)` or relative
  paths to locate other files? If yes, moving the SKILL.md vs. moving
  the whole directory have different effects — choose carefully.
- Does any other skill or script reference the current path?

## Promote — "extract pattern into a knowledge doc"

- Read all caller skills. Are the local definitions truly independent,
  or do some already reference the pattern? Confirm per-file.

## Trim — "remove unused tools from an agent's frontmatter"

- Read the agent file in full (`profile-al-dev-shared/agents/<name>.md`).
  List every tool in the frontmatter tools list.
- Quote any line in the system prompt body that uses each tool. A tool with
  no corresponding usage is a confirmed Trim candidate.
- Does removing this tool break any documented input or output contract?

## Remodel — "change an agent's model assignment"

- Read the agent file. Identify the heaviest reasoning step in the system
  prompt. Does it require multi-file synthesis or competitive analysis?
- Confirm the proposed new model is appropriate for that step:
  haiku for single-step retrieval; sonnet for general tasks; opus only for
  multi-file synthesis or competitive design.

## Split — "extract one concern from an agent into a new agent file"

- Read the agent file in full. Quote the two concerns named in the suggestion.
- Does an agent file for the extracted concern already exist in
  `profile-al-dev-shared/agents/`? If yes, this may be a merge rather than
  a split.
- What would the new agent's type name be? Confirm it is ≤30 characters.

## Inline — "absorb a single-use agent into its calling skill"

- Read the agent file and the spawning skill in full.
- Quote the exact section of the skill where the agent is spawned — this is
  where the inlined prompt will live.
- What is the exact path of the agent file to delete?
- Does any other skill reference this agent type? Confirm with:

```bash
grep -r "al-dev-shared:<agent-type-name>" profile-al-dev-shared/skills/ .claude/skills/
```

## Align — "fix mismatch between caller contract and agent documentation"

- Read both the agent file and every spawning skill identified in the map.
- Quote the exact mismatch: what the skill passes vs. what the agent's Inputs
  table documents (or "Not documented").
- Is the fix to update the agent's Inputs/Outputs tables, or to update how
  the skill calls the agent?
