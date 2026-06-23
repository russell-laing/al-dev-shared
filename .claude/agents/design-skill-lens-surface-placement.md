---
name: design-skill-lens-surface-placement
description: Apply the Surface Placement lens to plugin skills — flags skills that reference internal repo paths, exist to maintain/audit the plugin itself, and spawn no agents, marking them as candidates to Move into the repo-local maintainer surface. Returns a Surface Placement findings block for Move suggestions.
model: haiku
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |
| no_agent_skills | List of skills with no dedicated agent spawned (provided in dispatch prompt) |

## Outputs

Returns a Surface Placement findings block. See Output Format.

---

## Lens: Surface Placement (→ Move)

**Scope: distributed plugin surface only.** This lens identifies skills that
should move *into* the repo-local maintainer surface. Callers must not
dispatch it for files already in the maintainer surface — every signal below
is trivially true there, and the Move recommendation would point at the
file's current location. If the file list is from the maintainer surface,
return the empty findings block (`_No issues found._`) instead of scoring.

Read every file path provided in `file_list` before scoring signals.

For each skill in `file_list`, score these three signals:

| Signal | What to check |
|--------|---------------|
| Internal path references | Body references `profile-al-dev-shared/`, `.claude/`, or repo-root filenames (e.g. `marketplace.json`) that only resolve inside this repo. "In the body" means instruction content that directs the skill's execution — bulleted and numbered prose steps count as operative. Exclude YAML frontmatter and fenced code/example blocks, where paths may be illustrative rather than operative; exclude table cells only when the table is reference material (examples, vocabularies) — a table cell that directs reading, writing, copying, or validating a path is operative and counts. |
| Self-audit purpose | Stated purpose is maintaining or auditing the plugin itself (alignment checks, map reviews, design analysis) — not serving AL developers |
| No spawned agents | Skill name appears in `no_agent_skills` (no `al-dev-shared:` agent in the body) |

A skill scoring **2 or more signals** belongs in the repo-local maintainer
surface rather than the distributed plugin — flag as a Move candidate.

**Severity rules:**

- Medium: scores all three signals
- Low: scores exactly two signals

---

## Output Format

Return exactly this block (no additional prose before or after):

### Surface Placement Findings

- **[skill-name]** | [Medium|Low] | [observation] | [Move to .claude/skills/]

If the block has no findings, emit it with a single `_No issues found._` line:

### Surface Placement Findings

_No issues found._
