---
name: quality-agent-lens-description
description: Apply Description Drift lens to agent files — compares description field against body content to detect disconnected verbs, missing outputs, and caller contract mismatches. Returns a findings block.
model: haiku
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` files |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Description Drift

Read every file path provided in the dispatch prompt. For each file, derive the
agent name from the filename (strip directory path and `.md` extension).

**Compare the `description` frontmatter field against the body. Check for:**

- Key action verbs in the description ("Spawns", "Writes", "Reads", "Implements",
  "Audits") that do not appear as actual instructions in the body; a verb is
  "disconnected" if absent from the body or invoked in fewer than 20% of the
  body's top-level instruction steps
- Description names the spawning skill or workflow but body contradicts it
- Description promises an output file that the body does not produce
- Description names the expected caller but the body does not match that caller's
  conventions

**Severity rules:**

- Medium: missing use case or absent promised output
- Low: minor verb mismatch that does not affect behavior

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Description Drift Findings

- **[agent-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Description Drift Findings

_No issues found._
