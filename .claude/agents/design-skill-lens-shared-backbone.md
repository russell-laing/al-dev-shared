---
name: design-skill-lens-shared-backbone
description: Apply Shared Execution Backbone lens to plugin skills — identifies agent types used by 2+ skills whose invocation patterns could be documented in knowledge/ to prevent drift. Returns findings for Connect/Promote suggestions.
model: haiku
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |
| agent_usage_counts | Mapping of agent-type → list of skills that use it (provided in dispatch prompt) |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Shared Execution Backbone (→ Connect or Promote)

Read every file path provided in the dispatch prompt. Use `agent_usage_counts` to
identify agent types used by 2 or more skills.

For each such agent type:

1. Read the relevant SKILL.md files to compare how each skill spawns the agent.
2. Ask: are the spawn patterns identical or significantly different?
   - **Identical patterns** → Connect candidate: document a canonical invocation
     in `knowledge/` to prevent drift.
   - **Different patterns** → Promote candidate: make the variation explicit and
     decide if a shared base pattern is worth extracting.

**What constitutes an "identical" pattern:** a structural workflow match, not an
exact string match. Treat patterns as identical when all three hold (ignoring
whitespace, ordering, and incidental wording):

- Same dispatch prompt template (same steps/structure, even if phrased differently)
- Same context fields passed (same field set, regardless of order)
- Same output expectation

Patterns are **significantly different** when at least two of these three signals
differ; a single differing signal still counts as identical for drift purposes.

**Severity rules:**

- Medium: identical pattern copy-pasted across 2+ skills (drift risk when pattern needs updating)
- Low: patterns with exactly one differing signal (structurally close; lower drift risk than copy-paste)

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Shared Execution Backbone Findings

- **[agent-type]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Shared Execution Backbone Findings

_No issues found._
