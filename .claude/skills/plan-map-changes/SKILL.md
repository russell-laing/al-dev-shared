---
name: plan-map-changes
description: >-
  Use when the Observations section of docs/al-dev-skills-map.md or
  docs/al-dev-agent-map.md has suggestions that need implementing.
  Rubber-ducks each suggestion against the live codebase before any plan
  is written. Run /review-skill-map and /review-agent-map first if
  skills or agents have changed since the maps were last updated.
  Triggers on: "implement skill map suggestions", "plan architectural
  changes", "plan the suggestions", "create a plan for skill map changes",
  "implement the observations", "implement the skill map",
  "implement agent map suggestions", "plan agent map changes",
  "implement the agent map".
argument-hint: "[optional: connect | merge | trim | remodel | inline | align | all | --agents | --plugin-map]"
---

# Plan Map Changes

Translates suggestions from `docs/al-dev-skills-map.md` and
`docs/al-dev-agent-map.md` into a verified implementation plan. The
rubber-ducking phase is **mandatory** — no plan task is written until the
live codebase state behind each suggestion is confirmed. This prevents
plans based on suggestion text that diverges from actual code.

---

## Prerequisites

- `docs/al-dev-skills-map.md` and/or `docs/al-dev-agent-map.md` exist
  with an `## Observations` section
- Run `/review-skill-map` and `/review-agent-map` first if skills or
  agents have changed since the maps were last updated — stale suggestions
  produce wrong plans
- At least one Observations section has an open suggestion or candidate

---

## Argument Routing

**Default (no argument):** process both `docs/al-dev-skills-map.md` and
`docs/al-dev-agent-map.md`. Collect suggestions from all Observations
sections and rubber-duck them together before writing a single unified plan.

**`--plugin-map`:** process only `docs/al-dev-skills-map.md`. Suggestion
vocabulary: Connect, Merge, Promote, Move, Extend.

**`--agents`:** process only `docs/al-dev-agent-map.md`:
- **Source document:** `docs/al-dev-agent-map.md`
- **Rubber-duck reads:** `profile-al-dev-shared/agents/<name>.md` (not skills/)
- **Plan task file paths:** reference agent file paths
- **Suggestion vocabulary:** Trim, Remodel, Split, Inline, Align

Everything else — the rubber-duck protocol, plan output format, verification
checklist — stays identical across all routing modes.

---

## Phase 1: Extract Suggestions

Apply the Argument Routing rules above to determine which documents to read.

**From `docs/al-dev-skills-map.md`** (default or `--plugin-map`), collect
every open item from:
- `### Architectural suggestions` (Connect, Merge, Promote)
- `### Move candidates`
- `### Extension opportunities`

**From `docs/al-dev-agent-map.md`** (default or `--agents`), collect every
open item from `## Observations` (Trim, Remodel, Split, Inline, Align).

Skip any suggestion already marked `← implemented`, `← completed`, or
`← already implemented`.

List each collected item as: **type — subject — proposed change**.

If the user passed a suggestion type as an argument (e.g., `connect`, `merge`,
`trim`), capture it as `FILTER_TYPE` and filter collected suggestions to that
type. If no type argument was passed, set `FILTER_TYPE=all` and process all
collected suggestions. Note the active filter before proceeding to Phase 2.

---

## Phase 2: Rubber Duck Each Suggestion

For **every** suggestion, run the checklist below. Do not write any plan
content until all suggestions are rubber-ducked.

> **The rubber duck is a blocker, not a suggestion.** If a check finds a
> mismatch or gap, resolve it before moving to the next suggestion.
> See `knowledge/rubber-duck.md` for the underlying protocol.

### Progress tracking

Before rubber-ducking any suggestion, create one TodoWrite todo per suggestion
named `[Type] [Subject]`. Mark each todo in-progress when rubber-ducking begins,
complete when the rubber duck record is written.

### Parallel exploration

Two suggestions are **independent** if they modify no overlapping files and neither
suggestion's output is an input to the other's rubber-duck phase. If suggestion A
writes a file that suggestion B must read before it can be rubber-ducked, B is
ordered after A.

When there are 3+ independent suggestions, invoke `superpowers:dispatching-parallel-agents`
before starting rubber-ducking. Dispatch one Explore subagent per suggestion.
Each agent should: read the affected file(s) in full, run U2 artifact checks,
run the type-specific grep(s), and return a structured rubber duck record.
Collect all records before writing any plan content.

For ≤2 suggestions (or suggestions with ordering dependencies), the sequential
inline path is fine — keep it as the fallback.

### Checks

For all checks — Universal (U1–U3) and type-specific (Connect, Extend, Merge,
Move, Promote, Trim, Remodel, Split, Inline, Align) — see:

`profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`

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

If the verdict is `skip [reason]`, exclude that suggestion from Phase 3 entirely — do not create a plan task for it. Record skipped suggestions in a `## Skipped` section at the end of the plan file with the reason noted.

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
