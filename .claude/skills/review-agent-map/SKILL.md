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
