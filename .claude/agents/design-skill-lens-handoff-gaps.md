---
name: design-skill-lens-handoff-gaps
description: Apply Handoff Chain Gaps lens to plugin skills — traces .dev/ file handoff chains to find established chains with obvious next steps or orphaned outputs. Returns findings for Extend suggestions.
model: haiku
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |
| handoff_chains | Traced chains of .dev/ file handoffs between skills (provided in dispatch prompt) |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Handoff Chain Gaps (→ Extend)

Read every file path provided in the dispatch prompt. Use `handoff_chains` for
chain analysis.

**Look for:**

1. A well-established chain that has an obvious next step not yet covered:
   e.g., a chain ending at `commit` where a natural `release` or `deploy` step
   would complete the workflow.
2. Outputs produced by one skill (listed in body as "writes X.md") that are
   never referenced as inputs by any other skill — orphaned outputs that could
   be useful if consumed. To decide "never referenced": grep each output's
   `.dev/` filename across all other `SKILL.md` bodies; zero matches = orphaned.

**Established chain criteria:**

- 3+ skills connected via .dev/ file handoffs
- The final output of the chain is commonly useful for a task not yet in the plugin

**Severity rules:**

- Medium: well-established chain with an obvious gap that would serve a frequent use case
- Low: orphaned output or possible extension that serves an infrequent use case

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Handoff Chain Gaps Findings

- **[chain-endpoint or orphaned-output]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Handoff Chain Gaps Findings

_No issues found._
