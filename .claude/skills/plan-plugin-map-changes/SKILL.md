---
name: plan-plugin-map-changes
description: >-
  Use when the Observations section of docs/al-dev-plugin-map.md has
  Architectural suggestions, Move candidates, or Extension opportunities
  that need implementing. Rubber-ducks each suggestion against the live
  codebase before any plan is written. Run /review-plugin-map first if
  skills or agents have changed since the map was last updated.
  Triggers on: "implement plugin map suggestions", "plan architectural
  changes", "plan the suggestions", "create a plan for plugin map changes",
  "implement the observations", "implement the plugin map".
argument-hint: "[optional: connect | merge | trim | remodel | inline | align | all | --agents]"
---

# Plan Plugin Map Changes

Translates suggestions from `docs/al-dev-plugin-map.md` into a verified
implementation plan. The rubber-ducking phase is **mandatory** — no plan
task is written until the live codebase state behind each suggestion is
confirmed. This prevents plans based on suggestion text that diverges from
actual code.

---

## Prerequisites

- `docs/al-dev-plugin-map.md` exists with an `## Observations` section
- Run `/review-plugin-map` first if skills or agents have changed since
  the map was last updated — stale suggestions produce wrong plans
- The Observations section has at least one suggestion or candidate

---

## Argument Routing

If `$ARGUMENTS` is `--agents`:

- **Source document:** `docs/al-dev-agent-map.md` (not `docs/al-dev-plugin-map.md`)
- **Rubber-duck reads:** `profile-al-dev-shared/agents/<name>.md` (not skills/)
- **Plan task file paths:** reference agent file paths
- **Suggestion vocabulary:** Trim, Remodel, Split, Inline, Align — these
  replace Connect, Merge, Promote, Move, Extend for agent-map suggestions

Everything else — the rubber-duck protocol, plan output format, verification
checklist — stays identical.

---

## Phase 1: Extract Suggestions

If `$ARGUMENTS` is `--agents`, read `docs/al-dev-agent-map.md` and collect
every item from `## Observations`. Otherwise read `docs/al-dev-plugin-map.md`
and collect every item from:

- `### Architectural suggestions` (Connect, Merge, Promote)
- `### Move candidates`
- `### Extension opportunities`

List each as: **type — subject — proposed change**.

If `$ARGUMENTS` names a type (`connect`, `merge`, `trim`, etc.), filter to
that type only and note it. If `$ARGUMENTS` is `--agents`, apply routing from
the section above instead of a type filter.

---

## Phase 2: Rubber Duck Each Suggestion

For **every** suggestion, run the checklist below. Do not write any plan
content until all suggestions are rubber-ducked.

> **The rubber duck is a blocker, not a suggestion.** If a check finds a
> mismatch or gap, resolve it before moving to the next suggestion.
> See `knowledge/rubber-duck.md` for the underlying protocol.

### Universal checks (all suggestion types)

**U1. Read the affected files in full.**
Do NOT infer current state from the plugin map — read the actual SKILL.md
or knowledge file. The map is a snapshot; the code is the truth.

**U2. Verify referenced artifacts exist.**
If the suggestion mentions a validator script, helper file, or Python
tool: run `ls` on the directory. Build plans around files that exist,
not files that are assumed to exist.

```bash
ls profile-al-dev-shared/skills/<skill-name>/
```

**U3. Check whether the suggested flag, name, or path captures the full scope.**
Read the source skill. List every structural difference between the
skills being merged or connected. A flag named after one feature but
activating three is a scope gap — rename or expand the scope in the plan.

### Type-specific checks

**Connect** — "document a shared pattern used by two skills":
- Read both skills' relevant sections. Are the definitions actually
  identical, or just similar? Quote both to confirm.
- Is the pattern stable, or does each skill customize it?

**Merge** — "consolidate skill B into skill A with a flag":
- Read skill B in full. List ALL phases, templates, and validators
  that are unique to it — the flag must activate all of them.
- If skill B has a validator script, confirm it exists with `ls`.
- What does archiving do to other skills that reference skill B?

**Promote** — "extract pattern into a knowledge doc":
- Read all caller skills. Are the local definitions truly independent,
  or do some already reference the pattern? Confirm per-file.

**Move** — "relocate a skill to .claude/skills/":
- Does any file in the skill directory use `Path(__file__)` or relative
  paths to locate other files? If yes, moving the SKILL.md vs. moving
  the whole directory have different effects — choose carefully.
- Does any other skill or script reference the current path?

**Extend** — "add nodes to a diagram":
- Is the change purely additive, or does it also require removing
  existing nodes? Check if a subsequent task (e.g., a Merge) will
  also touch the same diagram and plan the ordering accordingly.

**Trim** — "remove unused tools from an agent's frontmatter":
- Read the agent file in full (`profile-al-dev-shared/agents/<name>.md`).
  List every tool in the frontmatter tools list.
- Quote any line in the system prompt body that uses each tool. A tool with
  no corresponding usage is a confirmed Trim candidate.
- Does removing this tool break any documented input or output contract?

**Remodel** — "change an agent's model assignment":
- Read the agent file. Identify the heaviest reasoning step in the system
  prompt. Does it require multi-file synthesis or competitive analysis?
- Confirm the proposed new model is appropriate for that step.
  (haiku for single-step retrieval; sonnet for general tasks; opus only for
  multi-file synthesis or competitive design.)

**Split** — "extract one concern from an agent into a new agent file":
- Read the agent file in full. Quote the two concerns named in the suggestion.
- Does an agent file for the extracted concern already exist in
  `profile-al-dev-shared/agents/`? If yes, this may be a merge rather than
  a split.
- What would the new agent's type name be? Confirm it's ≤30 characters.

**Inline** — "absorb a single-use agent into its calling skill":
- Read the agent file and the spawning skill in full.
- Quote the exact section of the skill where the agent is spawned — this is
  where the inlined prompt will live.
- What is the exact path of the agent file to delete?
- Does any other skill reference this agent type? Confirm with:
  ```bash
  # Substitute the exact `name:` value from the agent frontmatter (not the filename)
  grep -r "al-dev-shared:<agent-type-name>" profile-al-dev-shared/skills/ .claude/skills/
  ```

**Align** — "fix mismatch between caller contract and agent documentation":
- Read both the agent file and every spawning skill identified in the map.
- Quote the exact mismatch: what the skill passes vs. what the agent's Inputs
  table documents (or "Not documented").
- Is the fix to update the agent's Inputs/Outputs tables, or to update how
  the skill calls the agent?

### Rubber duck record

After each suggestion, write:

```
RUBBER DUCK: [Type — Subject]
Claim:        [what the suggestion says]
State:        [what reading the code reveals]
Side-effects: [files/scripts that depend on what's being changed]
Scope gap:    [anything the suggestion underspecifies, or "none"]
Verdict:      proceed | modify [reason] | skip [reason]
```

---

## Phase 3: Write the Implementation Plan

After all suggestions are rubber-ducked, invoke:

**REQUIRED SUB-SKILL: Use superpowers:writing-plans**

Pass as context to writing-plans:
- All rubber duck records
- Corrected flag names, file paths, and scope (use these, not the
  original suggestion wording where rubber ducking found a mismatch)
- Task ordering: additive changes first (new knowledge docs, diagram
  extensions), structural changes last (merges, archives, moves)
- The verification pattern for each task: `ls`, `diff`, `wc -l`, `grep`

Plan saves to:
`docs/superpowers/plans/YYYY-MM-DD-plugin-map-<short-label>.md`
