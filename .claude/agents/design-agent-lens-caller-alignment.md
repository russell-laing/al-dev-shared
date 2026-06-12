---
name: design-agent-lens-caller-alignment
description: Apply Caller Alignment lens to agent files — evaluates documented Inputs/Outputs against how spawning skills actually invoke each agent by autonomously grepping profile-al-dev-shared/skills/ for dispatch patterns and context blocks. Returns a findings block for Align suggestions.
model: haiku
tools: ["Read", "Grep"]
---

# Caller Alignment Lens

## Inputs

| Field | Description |
| --- | --- |
| file_list | Newline-separated absolute paths to agent `.md` files |
| caller_map | Mapping of agent-name → list of skill names that spawn it (provided in dispatch prompt) |

**Implicit dependency:** The agent searches the hardcoded path
`profile-al-dev-shared/skills/` for dispatch patterns (see the "Lens: Caller
Alignment" section). This path is embedded in the agent body — callers do not
supply it.

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Caller Alignment (→ Align)

For each agent file: derive the agent name (strip path + `.md` extension), extract
its `## Inputs` / `## Outputs` sections, then Grep `profile-al-dev-shared/skills/`
for `al-dev-shared:<agent-name>` to check how spawning skills invoke it.

Classify into three states:

- **Both present, fields match** — working contract; no finding
- **Dispatch line, no context block** — High; documented Inputs are not supplied
- **Context block, no dispatch line** — High; unreferenced invocation

**Red flags:**

- Spawning skill passes structured context the agent's Inputs table does not document
- Agent Outputs table names a file the spawning skill never reads or references
- Inputs table says "Not documented" but caller passes structured fields

**Severity rules:**

- High: caller passes structured data the Inputs table explicitly contradicts
- High: caller dispatches with no context block
- High: context block passed with no dispatch line
- Medium: Inputs/Outputs table is "Not documented" but caller passes structured context
- Low: minor label mismatch that doesn't affect behavior but confuses future callers

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Caller Alignment Findings

- **[agent-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

_No issues found._
