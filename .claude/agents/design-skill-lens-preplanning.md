---
name: design-skill-lens-preplanning
description: Apply Pre-planning Skills lens to plugin skills — checks whether pre-planning/brainstorming skills appear correctly in the Layer 1 diagram as dashed tributary arrows and have named outputs referenced downstream. Returns findings.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |
| preplanning_skills | List of skills identified as pre-planning tributaries (provided in dispatch prompt) |
| layer1_diagram_content | Content of the Layer 1 diagram from docs/al-dev-plugin-map.md (provided in dispatch prompt) |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Pre-planning and Brainstorming Skills

Canonical pre-planning skills in this plugin:
- `/al-dev-interview` — produces `interview-requirements.md`
- `/al-dev-explore` — produces `explore-findings.md`

For each skill in `preplanning_skills` and any additional pre-planning skills
found in the file list:

1. Check whether it appears in `layer1_diagram_content` as a dashed tributary
   arrow (`-.->`) rather than a main-spine node.
2. Check whether its output filename is referenced in Layer 1 handoff labels.
3. Check whether a downstream skill explicitly names it as an input in its body.

**Flag as Extend candidate:**
- Pre-planning skill is active (has a SKILL.md) but absent from the Layer 1 diagram entirely
- Pre-planning skill feeds a downstream step but its output is unnamed in the diagram

**Severity rules:**
- Medium: active pre-planning skill entirely absent from Layer 1 diagram
- Low: skill present in diagram but output filename not referenced in handoff labels

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Pre-planning Skills Findings
- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Pre-planning Skills Findings
_No issues found._
