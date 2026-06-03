---
name: design-agent-lens-caller-alignment
description: Apply Caller Alignment lens to agent files — compares documented Inputs/Outputs against how spawning skills actually invoke each agent. Returns a findings block for Align suggestions.
model: haiku
tools: ["Read", "Grep"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` files |
| caller_map | Mapping of agent-name → list of skill names that spawn it (provided in dispatch prompt) |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Caller Alignment (→ Align)

Read every file path provided in the dispatch prompt. For each file, derive the
agent name from the filename (strip directory path and `.md` extension).

Extract the `## Inputs` and `## Outputs` sections. Then use the Grep tool to
check how each spawning skill actually invokes the agent. "Actually invoke"
means: the skill body contains an `al-dev-shared:<agent>` dispatch line **and**
the context block passed alongside it (the prompt fields the skill hands the
agent). Check both: a dispatch line with no passed context block is not evidence
of a working contract — treat it as a potential High alignment finding (the
agent's documented Inputs are not being supplied), not as out-of-scope.
Likewise, passed context with no dispatch line is a finding. Search the skills
directory:

- Pattern: `al-dev-<agent-name>` in `/Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/`

**Red flags:**

- Spawning skill passes a structured context block (file paths, data) that the
  agent's Inputs table does not document
- Agent's Outputs table names a file the spawning skill never reads or references
- Agent Inputs table says "Not documented" but the spawning skill passes a
  structured prompt with specific fields

A mismatch between caller behaviour and agent documentation is an Align candidate.

**Severity rules:**

- High: caller passes structured data the agent's Inputs table explicitly contradicts
- Medium: Inputs/Outputs table is "Not documented" but caller clearly passes
  structured context
- Low: minor label mismatch that doesn't affect behavior but confuses future callers

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Caller Alignment Findings

- **[agent-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Caller Alignment Findings

_No issues found._
