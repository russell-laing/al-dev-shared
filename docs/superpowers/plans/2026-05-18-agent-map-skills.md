# Agent Map Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create two project-local skills (`/review-agent-map`, `/analyze-agent-design`), seed their output document (`docs/al-dev-agent-map.md`), and extend `/plan-plugin-map-changes` with an `--agents` routing mode.

**Architecture:** The two new skills mirror the existing `/review-plugin-map` + `/analyze-plugin-design` pair but focus on agent `.md` files rather than skill `SKILL.md` files. The output document uses a table-based Layer 1 (agents don't form a workflow graph) and a flat Layer 2 of per-agent profiles. The `--agents` flag in `/plan-plugin-map-changes` switches the source document from `docs/al-dev-plugin-map.md` to `docs/al-dev-agent-map.md` and adds Trim/Remodel/Split/Inline/Align vocabulary.

**Tech Stack:** Markdown skill files; bash for file inspection; git for commits.

---

### Task 1: Create `/review-agent-map` skill

**Files:**
- Create: `.claude/skills/review-agent-map/SKILL.md`

- [ ] **Step 1: Create directory**

```bash
mkdir -p .claude/skills/review-agent-map
```

- [ ] **Step 2: Write `.claude/skills/review-agent-map/SKILL.md`**

```markdown
---
name: review-agent-map
description: >-
  Review profile-al-dev-shared agents for accuracy and update
  docs/al-dev-agent-map.md. Use whenever agents are added, removed, or
  restructured in the plugin, or when you want to verify the map reflects
  the current state of agent files.
  Triggers on: "review agent map", "update agent map", "sync agent map",
  "is the agent map accurate".
argument-hint: "[optional: agent name to focus on]"
---

# Review Agent Map

Audit `profile-al-dev-shared/agents/` and update `docs/al-dev-agent-map.md`
so it accurately reflects the current active agents, their models, tools,
and caller relationships.

---

## Phase 1: Scan Agent Files

Run these commands and record the results:

```bash
# Active agents
ls profile-al-dev-shared/agents/

# Archived agents (excluded from the map)
ls profile-al-dev-shared/archived/agents/ 2>/dev/null
```

Build two lists:
- **Active agents** — `.md` files in `agents/` minus anything in `archived/agents/`
- **Archived agents** — excluded from all subsequent phases

---

## Phase 2: Extract Agent Profiles

For each active agent (read `profile-al-dev-shared/agents/<name>.md`):

Extract from frontmatter:
1. **model** — `sonnet`, `opus`, or `haiku`
2. **tools** — full tools list
3. **description** — first sentence only

Extract from body:
4. **Inputs table** — the `## Inputs` section (or "Not documented" if absent)
5. **Outputs table** — the `## Outputs` section (or "Not documented" if absent)

Record in a working table:

| Agent | Model | Tools | Has Inputs? | Has Outputs? |
|-------|-------|-------|-------------|--------------|

If `$ARGUMENTS` is an agent name, focus only on that agent and skip the rest.

---

## Phase 3: Cross-Reference Callers

For each active agent, grep every skill body for the agent's type name to
determine which skills spawn it:

```bash
# For most agents (al-dev-shared:al-dev-<name>)
grep -rl "al-dev-shared:al-dev-<name>" \
  profile-al-dev-shared/skills/ .claude/skills/ 2>/dev/null

# For commit-learn-verifier specifically
grep -rl "al-dev-shared:commit-learn-verifier" \
  profile-al-dev-shared/skills/ .claude/skills/ 2>/dev/null
```

The agent's type name is `al-dev-shared:<filename-without-.md>`.

Record:
- **Spawned by:** list of skill names (extract directory name from matching paths)
- **Spawn count:** single-use (1 skill) or shared (2+ skills)

---

## Phase 4: Compare Against `docs/al-dev-agent-map.md`

If `docs/al-dev-agent-map.md` does not exist, skip to Phase 6 (write from
scratch).

Read the file. Check:

### Layer 1 (Agent Catalog table)

Verify:
- All active agents appear as table rows
- No archived agent appears as a row
- Model and tools match the actual frontmatter values
- "Spawned by" matches the grep results from Phase 3

### Layer 2 (Per-agent profiles)

For each active agent, verify the `### al-dev-<name>` section:
- Model and tools list match the frontmatter
- Spawned-by list matches Phase 3 results
- Inputs/Outputs match Phase 2 findings (or "Not documented" if absent)

---

## Phase 5: Report Discrepancies

Before editing, summarise findings:

```
Agent map review findings:
Layer 1:
  - [issue or "✅ accurate"]
Layer 2 per-agent:
  - al-dev-developer: [issue or "✅ accurate"]
  - al-dev-solution-architect: [issue or "✅ accurate"]
  ...
Missing from map: [agents not in map]
Stale in map:    [agents in map but now archived]
```

If everything is accurate, say so and stop.

---

## Phase 6: Update the Map

If `docs/al-dev-agent-map.md` does not exist, create it. Otherwise make
targeted edits to fix each discrepancy found in Phase 5.

**Document structure (full template for first-run creation):**

```markdown
# AL Dev Agent Map

**Last updated:** YYYY-MM-DD

## Layer 1: Agent Catalog

| Agent | Model | Tools | Spawned by |
|-------|-------|-------|------------|
| al-dev-developer | sonnet | Read, Write, Edit, Glob, Grep, Bash | /al-dev-develop, /al-dev-fix |
...

## Layer 2: Per-Agent Profiles

### al-dev-<name>

**Description:** [first sentence from the agent description frontmatter]
**Model:** sonnet/opus/haiku
**Tools:** [comma-separated list from frontmatter]
**Spawned by:** /skill-a, /skill-b
**Inputs:** [table reproduced from agent file, or "Not documented"]
**Outputs:** [table reproduced from agent file, or "Not documented"]

---

[repeat for each active agent]

## Observations

> Run /review-agent-map first if the agent list has changed before running
> /analyze-agent-design.

*(Populated by /analyze-agent-design)*
```

After writing or updating, confirm:
```bash
wc -l docs/al-dev-agent-map.md
# Expected: 80+ lines for a full 16-agent roster
```

Set `**Last updated:**` to today's date.

---

## Phase 7: Detect Inline Candidates

Score each active agent against three signals:

| Signal | What to check |
|--------|---------------|
| **Single caller** | Spawned by exactly one skill (from Phase 3) |
| **Minimal body** | System prompt body (lines after the closing `---` of frontmatter) is fewer than 10 lines |
| **No inputs/outputs docs** | Neither an Inputs nor an Outputs section exists in the agent file |

An agent scoring **2 or more signals** is an inline candidate.

Append findings to the `## Observations` section of `docs/al-dev-agent-map.md`:

```markdown
### Inline candidates

> Detected by /review-agent-map on YYYY-MM-DD.

**Inline: al-dev-<name>**
Signals: single caller (✓/✗), minimal body (✓/✗), no inputs/outputs docs (✓/✗).
Spawned by: /skill-name.
Suggestion: Absorb system prompt into /skill-name's body; delete the agent file.
Trade-off: Less indirection; agent no longer reusable if a second caller is added.
```

If no candidates are found, append:

```markdown
### Inline candidates

None detected.
```

Commit if any edits were made:

```bash
git -C . add docs/al-dev-agent-map.md
git -C . commit -m "docs: sync agent map with current agent roster"
```
```

- [ ] **Step 3: Verify the file exists and has correct structure**

```bash
ls -la .claude/skills/review-agent-map/SKILL.md
grep "^name:" .claude/skills/review-agent-map/SKILL.md
# Expected: name: review-agent-map

grep "^## Phase" .claude/skills/review-agent-map/SKILL.md | wc -l
# Expected: 7

wc -l .claude/skills/review-agent-map/SKILL.md
# Expected: 140+ lines
```

- [ ] **Step 4: Verify frontmatter is well-formed (two `---` fences)**

```bash
grep -n "^---$" .claude/skills/review-agent-map/SKILL.md | head -3
# Expected: line 1 and line 10 (approximately) — open and close of frontmatter block
```

- [ ] **Step 5: Commit**

```bash
git -C . add .claude/skills/review-agent-map/SKILL.md
git -C . commit -m "feat(skills): add /review-agent-map skill"
```

Expected output: `[master <hash>] feat(skills): add /review-agent-map skill`

---

### Task 2: Seed `docs/al-dev-agent-map.md` by running `/review-agent-map`

**Files:**
- Create: `docs/al-dev-agent-map.md`

- [ ] **Step 1: Invoke `/review-agent-map` via the Skill tool**

Use the Skill tool with skill name `review-agent-map`. The skill will run
all 7 phases against the live `profile-al-dev-shared/agents/` directory and
create `docs/al-dev-agent-map.md` from scratch (Phase 6 first-run path).

- [ ] **Step 2: Verify the document was created and is non-empty**

```bash
ls -la docs/al-dev-agent-map.md
wc -l docs/al-dev-agent-map.md
# Expected: exists; 80+ lines
```

- [ ] **Step 3: Verify Layer 1 table covers all 16 active agents**

```bash
grep "^| al-dev-" docs/al-dev-agent-map.md | wc -l
# Expected: 15 (al-dev-* agents)

grep "^| commit-learn-verifier" docs/al-dev-agent-map.md | wc -l
# Expected: 1
```

- [ ] **Step 4: Verify Layer 2 per-agent sections exist**

```bash
grep "^### al-dev-" docs/al-dev-agent-map.md | wc -l
# Expected: 15

grep "^### commit-learn-verifier" docs/al-dev-agent-map.md | wc -l
# Expected: 1
```

- [ ] **Step 5: Verify no archived agent appears in the map**

```bash
grep -E "(al-dev-edge-case-test|al-dev-integration-test|al-dev-scenario-test|al-dev-test-coverage|al-dev-unit-test)" docs/al-dev-agent-map.md
# Expected: no output (archived agents must not appear)
```

- [ ] **Step 6: Verify Observations section and Last updated header**

```bash
grep "^## Observations" docs/al-dev-agent-map.md
grep "^\*\*Last updated:\*\*" docs/al-dev-agent-map.md
# Expected: one match each; date is today's date (2026-05-18)
```

- [ ] **Step 7: Commit**

```bash
git -C . add docs/al-dev-agent-map.md
git -C . commit -m "docs: seed al-dev-agent-map.md from first run of /review-agent-map"
```

---

### Task 3: Create `/analyze-agent-design` skill

**Files:**
- Create: `.claude/skills/analyze-agent-design/SKILL.md`

- [ ] **Step 1: Create directory**

```bash
mkdir -p .claude/skills/analyze-agent-design
```

- [ ] **Step 2: Write `.claude/skills/analyze-agent-design/SKILL.md`**

```markdown
---
name: analyze-agent-design
description: >-
  Analyze profile-al-dev-shared agents for design quality and write
  concrete Trim / Remodel / Split / Inline / Align suggestions to the
  Observations section of docs/al-dev-agent-map.md. Use whenever you want
  strategic recommendations for making agents leaner, better-modelled, or
  better-documented — including when someone asks "is this agent doing too
  much?", "what tools does this agent not need?", "are any agents over-
  allocated on model?", or "how can we improve agent quality?". Run after
  /review-agent-map so the map is accurate before analysis begins.
  Triggers on: "analyze agent design", "agent quality review",
  "review agent quality", "agent improvement suggestions".
argument-hint: "[focus: trim|remodel|split|inline|align|all]"
---

# Skill: /analyze-agent-design

Strategic analysis of al-dev agent files. Reads the current agent map,
applies five analytical lenses, and writes concrete improvement suggestions
to the `## Observations` section of `docs/al-dev-agent-map.md`.

Run `/review-agent-map` first if the map may be out of date.

---

## Step 1 — Read the Agent Map and Build Working Lists

Read `docs/al-dev-agent-map.md` in full. As you read, build these lists:

1. **Tool inventory** — for every agent, record its tools list from Layer 2.
2. **Model assignments** — for every agent, record its model.
3. **Caller map** — for every agent, record which skills spawn it (from "Spawned by").
4. **Single-use agents** — agents spawned by exactly one skill.
5. **Shared agents** — agents spawned by 2+ skills.
6. **Undocumented agents** — agents with "Not documented" for both Inputs and Outputs.

If an argument was passed, restrict analysis to that lens:
`trim`, `remodel`, `split`, `inline`, `align`, or `all` / no argument = `all`.

---

## Step 2 — Apply Five Analytical Lenses

### Lens 1 — Tool Hygiene (→ Trim)

For each agent, compare the tools list in Layer 2 against what the system
prompt body actually uses. Read the agent file:

```bash
cat profile-al-dev-shared/agents/<name>.md
```

Red flags:
- Agent described as "read-only" or analysis-only but has `Write` or `Edit`
- Agent has `Bash` but no commands are mentioned in the system prompt
- Agent has MCP tools but no MCP usage is described in the body

A tool present in the frontmatter but unused in the system prompt is a Trim
candidate.

### Lens 2 — Model Fit (→ Remodel)

For each agent, evaluate whether `sonnet` / `opus` / `haiku` is appropriate:

- **Haiku-appropriate:** Single-step retrieval, simple API calls, basic
  formatting — no multi-file reasoning needed
- **Sonnet (default):** Most implementation, code review, and analysis tasks
- **Opus justified:** Competitive design tasks, multi-file synthesis, complex
  reasoning requiring broad codebase understanding

An agent assigned `opus` for a single-step or single-file task, or `sonnet`
for a clearly haiku-appropriate task, is a Remodel candidate.

### Lens 3 — Scope Isolation (→ Split)

For each agent, read its system prompt body. Ask: does it describe two clearly
separable concerns?

Signals:
- System prompt contains two distinct "## Phase" or "## Mission" sections
  addressing unrelated outputs
- The Inputs and Outputs tables serve two different downstream consumers
- The description uses "and" to connect two distinct task categories

A system prompt with two separable concerns is a Split candidate.

### Lens 4 — Caller Alignment (→ Align)

For each agent, compare its documented Inputs/Outputs against how the spawning
skill(s) actually invoke it:

```bash
# Read how a skill spawns the agent
grep -A 20 "al-dev-<name>" profile-al-dev-shared/skills/<skill-name>/SKILL.md
```

Red flags:
- Spawning skill passes a file the agent's Inputs table doesn't list
- Agent's Outputs table names a file the spawning skill never reads
- Agent Inputs is "Not documented" but spawning skill passes structured prompt

A mismatch between caller behaviour and agent documentation is an Align
candidate.

### Lens 5 — Usage Patterns (→ Inline)

For single-use agents, ask: does the complexity justify a dedicated agent file?

Inline criteria (all three must apply):
- Spawned by exactly one skill
- System prompt body (after frontmatter) is fewer than 15 lines
- No Inputs or Outputs tables documented

An agent meeting all three is an Inline candidate. Before flagging, check the
existing `### Inline candidates` section in `docs/al-dev-agent-map.md` —
skip any agent already listed there.

---

## Step 3 — Draft Suggestions

Write 3–6 high-quality suggestions. Skip patterns that don't yield a real
improvement.

Before writing each suggestion, check the current `## Observations` section —
skip anything already marked `← implemented`.

Use these templates:

```
**Trim: al-dev-<name>**
Observation: Tools list includes [tool]; system prompt body contains no [tool] usage.
Suggestion: Remove [tool] from the tools list in the agent frontmatter.
Trade-off: Minimal — tool wasn't used; tighter least-privilege posture.
```

```
**Remodel: al-dev-<name>**
Observation: Agent performs [task description]; currently assigned [current-model].
Suggestion: Change model to [new-model] — task [does/does not] require multi-file synthesis.
Trade-off: [Faster + cheaper / More capable]; justified because [reason].
```

```
**Split: al-dev-<name>**
Observation: System prompt describes [concern A] and [concern B] — separable concerns.
Suggestion: Extract [concern B] into a new agent al-dev-<new-name>.
Trade-off: New agent file to maintain; each agent's scope becomes narrower and easier to evolve.
```

```
**Inline: al-dev-<name>**
Observation: Spawned only by /skill-name; [N]-line system prompt; no Inputs/Outputs documented.
Suggestion: Absorb system prompt into /skill-name's dispatch block; delete the agent file.
Trade-off: Less indirection; agent no longer reusable if a second caller is added later.
```

```
**Align: al-dev-<name>**
Observation: /skill-name passes [file/param X]; agent Inputs table does not document [X].
Suggestion: Update the agent's Inputs table to reflect the actual caller contract.
Trade-off: Documentation-only change; prevents future caller confusion.
```

---

## Step 4 — Complete Inventory Tables

Build the three inventory tables from your working lists in Step 1:

**Agents used by only one skill** — list each single-use agent and its
sole caller. These are Inline candidates if they are also simple.

**Agents with no inputs/outputs documentation** — list each. These are
"black box" agents — callers must read the spawning skill to understand
the contract.

**Potential shared agents** — list agent types spawned by 2+ skills. These
are candidates for caller-contract documentation in `knowledge/`.

---

## Step 5 — Write to `docs/al-dev-agent-map.md`

Replace the entire `## Observations` section (from the `## Observations`
heading to the end of the file) with:

```markdown
## Observations

> Generated by /analyze-agent-design on YYYY-MM-DD.
> Run /review-agent-map first if the agent list has changed since this was written.

### Agents used by only one skill

- **al-dev-<name>** — used only by /skill-name
[one bullet per single-use agent]

### Agents with no inputs/outputs documentation

- **al-dev-<name>** — [one-line description of what it does]
[one bullet per undocumented agent]

### Potential shared agents

- **al-dev-<name>** — used by /skill-a, /skill-b
[one bullet per shared agent]

### Quality suggestions

[one suggestion block per finding in Trim/Remodel/Split/Inline/Align format]
```

Update `**Last updated:**` in the document header to today's date.

---

## Step 6 — Present to User

After writing the file:

1. Print a one-line summary per suggestion (type + subject).
2. Mark the **highest-leverage** suggestion with `← highest leverage`.
3. Ask: "Would you like to act on any of these now?"
```

- [ ] **Step 3: Verify the file exists and has expected structure**

```bash
ls -la .claude/skills/analyze-agent-design/SKILL.md
grep "^name:" .claude/skills/analyze-agent-design/SKILL.md
# Expected: name: analyze-agent-design

grep "^## Step" .claude/skills/analyze-agent-design/SKILL.md | wc -l
# Expected: 6

grep "^### Lens" .claude/skills/analyze-agent-design/SKILL.md | wc -l
# Expected: 5

wc -l .claude/skills/analyze-agent-design/SKILL.md
# Expected: 160+ lines
```

- [ ] **Step 4: Verify all five suggestion vocabulary templates are present**

```bash
grep "^\*\*Trim:" .claude/skills/analyze-agent-design/SKILL.md
grep "^\*\*Remodel:" .claude/skills/analyze-agent-design/SKILL.md
grep "^\*\*Split:" .claude/skills/analyze-agent-design/SKILL.md
grep "^\*\*Inline:" .claude/skills/analyze-agent-design/SKILL.md
grep "^\*\*Align:" .claude/skills/analyze-agent-design/SKILL.md
# Expected: one match each
```

- [ ] **Step 5: Commit**

```bash
git -C . add .claude/skills/analyze-agent-design/SKILL.md
git -C . commit -m "feat(skills): add /analyze-agent-design skill"
```

---

### Task 4: Extend `/plan-plugin-map-changes` with `--agents` routing

**Files:**
- Modify: `.claude/skills/plan-plugin-map-changes/SKILL.md`

- [ ] **Step 1: Read the current file**

```bash
cat .claude/skills/plan-plugin-map-changes/SKILL.md
```

Confirm the current `argument-hint` line and that the `## Prerequisites`
section exists (this is where the routing block will be inserted after it).

- [ ] **Step 2: Update the `argument-hint` in the frontmatter**

Find the line:
```
argument-hint: "[optional: connect | merge | promote | move | extend | all]"
```

Replace it with:
```
argument-hint: "[optional: connect | merge | trim | remodel | inline | align | all | --agents]"
```

Use the Edit tool with exact string match.

- [ ] **Step 3: Insert the `## Argument Routing` section after `## Prerequisites`**

Find the line immediately after the `## Prerequisites` block ends (the blank
line before `## Phase 1:`). Insert this new section there:

```markdown
## Argument Routing

If `$ARGUMENTS` is `--agents`:

- **Source document:** `docs/al-dev-agent-map.md` (not `docs/al-dev-plugin-map.md`)
- **Rubber-duck reads:** `profile-al-dev-shared/agents/<name>.md` (not skills/)
- **Plan task file paths:** reference agent file paths
- **Suggestion vocabulary:** Trim, Remodel, Split, Inline, Align — in addition
  to the existing Connect, Merge, Promote, Move, Extend types

Everything else — the rubber-duck protocol, plan output format, verification
checklist — stays identical.

---

```

- [ ] **Step 4: Add agent-specific type checks to the Phase 2 rubber duck section**

In the `### Type-specific checks` block in Phase 2, append these five new
type blocks after the existing **Extend** block:

```markdown
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
  grep -r "al-dev-shared:al-dev-<name>" profile-al-dev-shared/skills/ .claude/skills/
  ```

**Align** — "fix mismatch between caller contract and agent documentation":
- Read both the agent file and every spawning skill identified in the map.
- Quote the exact mismatch: what the skill passes vs. what the agent's Inputs
  table documents (or "Not documented").
- Is the fix to update the agent's Inputs/Outputs tables, or to update how
  the skill calls the agent?
```

- [ ] **Step 5: Verify all changes are present**

```bash
grep "argument-hint" .claude/skills/plan-plugin-map-changes/SKILL.md
# Expected: includes "--agents"

grep "^## Argument Routing" .claude/skills/plan-plugin-map-changes/SKILL.md
# Expected: one match

grep "^\*\*Trim\*\*\|^\*\*Remodel\*\*\|^\*\*Split\*\*\|^\*\*Inline\*\*\|^\*\*Align\*\*" \
  .claude/skills/plan-plugin-map-changes/SKILL.md | wc -l
# Expected: 5 matches

wc -l .claude/skills/plan-plugin-map-changes/SKILL.md
# Expected: more than original line count
```

- [ ] **Step 6: Confirm no placeholder text was introduced**

```bash
grep -E "\[date\]|YYYY-MM-DD|TODO|TBD" .claude/skills/plan-plugin-map-changes/SKILL.md
# Expected: no output
```

- [ ] **Step 7: Commit**

```bash
git -C . add .claude/skills/plan-plugin-map-changes/SKILL.md
git -C . commit -m "feat(skills): extend /plan-plugin-map-changes with --agents routing"
```

---

### Task 5: Final verification

**Files:** No new files — verification only.

- [ ] **Step 1: Confirm all four deliverables exist**

```bash
ls -la .claude/skills/review-agent-map/SKILL.md
ls -la .claude/skills/analyze-agent-design/SKILL.md
ls -la docs/al-dev-agent-map.md
grep "^## Argument Routing" .claude/skills/plan-plugin-map-changes/SKILL.md
# Expected: all four exist
```

- [ ] **Step 2: Confirm new skills appear in the project skills directory**

```bash
ls .claude/skills/
# Expected: al-dev-align  analyze-agent-design  analyze-plugin-design
#           plan-plugin-map-changes  review-agent-map  review-plugin-map
```

- [ ] **Step 3: Confirm no forbidden patterns in the output document**

The skill files intentionally contain `YYYY-MM-DD` as runtime-filled
template text — check the output document only:

```bash
grep -E "\[date\]|YYYY-MM-DD|TODO|TBD|Co-Authored-By|claude:|copilot:" \
  docs/al-dev-agent-map.md
# Expected: no output (Last updated header should contain a real date)
```

Spot-check skill files for accidental unresolved placeholders:
```bash
grep -E "TODO|TBD|Co-Authored-By" \
  .claude/skills/review-agent-map/SKILL.md \
  .claude/skills/analyze-agent-design/SKILL.md
# Expected: no output
```

- [ ] **Step 4: Confirm archived agents are excluded from the map**

```bash
grep -E "(al-dev-edge-case-test|al-dev-unit-test|al-dev-integration-test|al-dev-scenario-test|al-dev-test-coverage)" \
  docs/al-dev-agent-map.md
# Expected: no output
```

- [ ] **Step 5: Confirm the agent map has both layers and an Observations section**

```bash
grep -E "^## Layer 1:|^## Layer 2:|^## Observations" docs/al-dev-agent-map.md
# Expected: three matches in order
```
