---
name: update-agent-map
description: >-
  Use after /audit-agents-against-map to apply discrepancies to docs/al-dev-agent-map.md.
  Writes/updates the agent map file, detects inline candidates (agents that could be absorbed),
  appends findings to Observations section, and commits changes.
argument-hint: "[optional: agent name to focus on]"
---

> **ARCHIVED 2026-05-31** — Use `/review-agent-map` instead.

---

# Update Agent Map

Apply audit findings from `/audit-agents-against-map` to update `docs/al-dev-agent-map.md`.
Writes changes, detects inline candidates, commits to git.

---

## Phase 1: Audit (Optional Re-scan)

If audit findings are not provided, run the full audit from Phase 1-5 of `/audit-agents-against-map`:
- Scan agent files
- Extract agent profiles
- Cross-reference callers
- Compare against current map
- Report discrepancies

Otherwise, use findings provided by previous audit run.

---

## Phase 2: Create or Update Layer 1

If `docs/al-dev-agent-map.md` does not exist, create it with this template:

```markdown
# AL Dev Agent Map

**Last updated:** YYYY-MM-DD

## Layer 1: Agent Catalog

| Agent | Model | Tools | Spawned by |
|-------|-------|-------|------------|
| [agent-name] | [sonnet/opus/haiku] | [comma-separated tools] | [/skill-a, /skill-b] |
...

## Layer 2: Per-Agent Profiles

[Repeat per-agent profiles below]

## Observations

> Run /audit-agents-against-map first if the agent list has changed before running
> /analyze-agent-design.

*(Populated by /analyze-agent-design)*
```

For each discrepancy found in the audit:
- To add an agent row: insert name, model, tools, spawned-by columns
- To remove an agent row: delete the table row
- To fix values: correct model, tools list, or spawned-by list

---

## Phase 3: Create or Update Layer 2

For each active agent, create or update the `### <agent-name>` section following this template:

```markdown
### agent-name

**Description:** [first sentence from the agent description frontmatter]
**Model:** [sonnet/opus/haiku]
**Tools:** [comma-separated list from frontmatter]
**Spawned by:** [/skill-a, /skill-b]
**Inputs:** [table reproduced from agent file, or "Not documented"]
**Outputs:** [table reproduced from agent file, or "Not documented"]

---
```

For each discrepancy:
- To update a profile: rewrite the section with corrected content
- To add a missing profile: insert a new section following the template
- To remove a stale profile: delete its `### agent-name` section entirely

---

## Phase 4: Update Metadata

Set `**Last updated:**` in the document header to today's date (YYYY-MM-DD format).

---

## Phase 5: Detect Inline Candidates

Score each active agent against three signals:

| Signal | What to check |
|--------|---------------|
| **Single caller** | Spawned by exactly one skill (from audit Phase 3) |
| **Minimal body** | System prompt body (lines after the closing `---` of frontmatter) is fewer than 10 lines |
| **No inputs/outputs docs** | Neither an Inputs nor an Outputs section exists in the agent file |

An agent scoring **2 or more signals** is an inline candidate.

### Output

Ensure `docs/al-dev-agent-map.md` has an `## Observations` section. If not, create it.

Within `## Observations`, ensure an `### Inline candidates` subsection exists. Create if missing.

For each inline candidate, append inside `### Inline candidates`:

```markdown
**Inline: al-dev-<name>**
Signals: single caller (✓/✗), minimal body (✓/✗), no inputs/outputs docs (✓/✗).
Spawned by: /skill-name.
Suggestion: Absorb system prompt into /skill-name's body; delete the agent file.
Trade-off: Less indirection; agent no longer reusable if a second caller is added.
```

If no candidates are found, ensure this subsection exists:

```markdown
### Inline candidates

None detected.
```

---

## Phase 6: Verify and Commit

Run a quick sanity check:

```bash
# Verify file structure (should have Layer 1 table and Layer 2 sections)
grep -c "^### " docs/al-dev-agent-map.md

# Expect no archived agent names
grep -E "(archived)" docs/al-dev-agent-map.md
```

If checks pass, commit:

```bash
git -C . add docs/al-dev-agent-map.md
git -C . commit -m "docs: sync agent map with current agent roster"
```

Report what changed and what was verified as already correct.

---

## Notes

- This skill only updates the **agent map** (docs/al-dev-agent-map.md)
- For skills map updates, use `/update-skill-map`
- For coordinated audit+update of both maps, use `/sync-documentation-maps`
