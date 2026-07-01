---
name: design-agent-lens-caller-alignment
description: Apply Caller Alignment lens to agent files — evaluates documented Inputs/Outputs against how spawning skills actually invoke each agent by looking up dispatch patterns in the provided caller_map (distributed-surface agents only). Returns a findings block for Align suggestions. Skips tooling-surface agents (.claude/agents/) — their callers live in .claude/skills/ and are out of scope.
model: haiku
tools: ["Read"]
---

# Caller Alignment Lens

## Inputs

| Field | Description |
| --- | --- |
| file_list | Newline-separated absolute paths to agent `.md` files |
| caller_map | Mapping of agent-name → list of skill names that spawn it (provided in dispatch prompt) |
| (scope guard) | Tooling-surface agents (those in `.claude/agents/` with primary use in maintainer tooling) are **out of scope** — return an empty findings block with the heading `### <Lens Name> Findings` followed by `_No issues found._` for these agents; do not skip the entire output. |

**Implicit dependency:** For distributed-surface agents, the lens looks up
callers from the `caller_map` provided in the dispatch context. For
tooling-surface agents, caller-alignment analysis is skipped — their callers
live in `.claude/skills/`, which is out of scope for this lens.

## Outputs

Returns a findings block. See Output Format.

> **Model fit note:** This lens performs contract extraction and pattern-matching against provided caller maps (haiku-appropriate). Architectural judgment about whether contract deviations are design violations vs. harmless differences (sonnet-appropriate) is secondary. Future enhancements for autonomous architectural reasoning may benefit from sonnet upgrade.

---

## Lens: Caller Alignment (→ Align)

For each agent file: derive the agent name (strip path + `.md` extension), extract
its `## Inputs` / `## Outputs` sections.

**Detect agent surface from file path:**

- **Distributed-surface agent** (path contains `profile-al-dev-shared/agents/`):
  Look up the agent name in `caller_map` to get the list of skills that spawn it.
  If the agent is absent from `caller_map` or its caller list is empty, treat it
  as unreferenced in the distributed surface.

- **Tooling-surface agent** (path contains `.claude/agents/`):
  Callers live in `.claude/skills/`, which is out of scope for this lens. Skip
  caller-alignment analysis for this agent and emit no finding.

For distributed-surface agents, classify into three states:

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
