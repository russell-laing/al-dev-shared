---
name: design-skill-lens-preplanning
description: Apply Pre-planning Skills lens to plugin skills — checks whether pre-planning/brainstorming skills appear correctly in the Layer 1 diagram as dashed tributary arrows and have named outputs referenced downstream. Returns findings.
model: haiku
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |
| preplanning_skills | Starting list of pre-planning tributary skills (provided in dispatch prompt). Agent also searches `file_list` autonomously for additional pre-planning skills not already in this list. |
| layer1_diagram_content | Content of the Layer 1 diagram from docs/al-dev-skills-map.md (provided in dispatch prompt) |

## Outputs

Returns a findings block. See Output Format.

---

## Reference: Canonical pre-planning skills

- `/al-dev-interview` — produces `interview-requirements.md`
- `/al-dev-explore` — produces `explore-findings.md`

---

## Lens: Pre-planning and Brainstorming Skills

For each skill in `preplanning_skills` and any additional pre-planning skills
found in the file list:

1. Check whether it appears in `layer1_diagram_content` as a dashed tributary
   arrow (`-.->`) rather than a main-spine node. Require an **exact**
   tributary-label match (the node label text — not the node ID — equals the
   skill name), not a substring match — `al-dev-explore` must not be counted as present merely because
   `al-dev-explore-deep` appears in the diagram.
2. Check whether its output filename is referenced in Layer 1 handoff labels.
3. Check whether a downstream skill explicitly names it as an input in its body.

**Flag as Extend candidate:**

- Pre-planning skill is active (has a SKILL.md) but missing its exact dashed
  tributary representation in the Layer 1 diagram
- Pre-planning skill feeds a downstream step but its output is unnamed in the diagram

---

## Severity Rules

Treat occurrence states explicitly:

- Exact dashed-tributary match: the skill is correctly represented in Layer 1.
- Substring-only match: a different node name contains the skill name, but the
  exact tributary node is missing.
- Main-spine-only match: the skill appears only as a main-spine node, not as a
  dashed tributary.
- Entirely absent: no relevant Layer 1 node exists for the skill.

**Severity rules:**

- Medium: active pre-planning skill entirely absent from Layer 1 diagram
- Medium: active pre-planning skill appears only as a main-spine node
- Low: active pre-planning skill appears only as a substring match in another
  node label
- Low: skill present in diagram but output filename not referenced in handoff labels

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Pre-planning Skills Findings

- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Pre-planning Skills Findings

_No issues found._
