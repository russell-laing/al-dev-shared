---
name: quality-agent-lens-name-fit
description: Apply Name Fit lens to agent files — compares agent name against primary verb and scope in description and body to detect naming drift and conflicts. Returns a findings block.
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

## Lens: Name Fit

Read every file path provided in the dispatch prompt. For each file, derive the
agent name from the filename (strip directory path and `.md` extension).

**Compare agent name against the primary verb and scope in description and body.
Check for:**
- Name implies X but body primarily does Y (scope has shifted since naming)
- Name is too generic relative to a narrower actual scope
- Another agent file in the provided list has a name so similar a user would
  struggle to choose between them
- Name uses a noun or adjective that conflicts with the agent's actual action verb

**Severity rules:**
- High: name actively misleads a caller about what the agent does
- Medium: moderate drift between name and actual scope
- Low: minor verb mismatch with no behavioral consequence

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Name Fit Findings
- **[agent-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Name Fit Findings
_No issues found._
