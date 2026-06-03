# Sync Documentation Maps — Edit Cases

Reference document for discrepancy-fix logic used by the
sync-documentation-maps audit and update agents. Four sections cover two
surfaces × two roles (audit / update).

---

## Agent surface — discrepancy types (audit)

Used by `sync-documentation-maps-agent-audit` Step 5.

- **`missing_from_map`** — an active agent has no entry in the Layer 1 Catalog
  table OR no `### <agent-name>` section in Layer 2. Flag if either layer is
  absent.
- **`stale_in_map`** — an archived agent still has a Layer 1 row OR a Layer 2
  section. Flag if either artifact remains.
- **`model_mismatch`** — the `model:` value in the agent frontmatter does not
  match the model recorded in the Layer 2 section.
- **`tools_mismatch`** — normalize first: if the map records `(none)` and
  frontmatter `tools:` is `[]`, treat as matching. Only flag when normalized
  values differ.
- **`caller_mismatch`** — the `Spawned by:` field in the Layer 2 section does
  not match the caller list from grep. Count only `al-dev-shared:<agent-name>`
  functional invocations; document prose-only mentions in `detail` instead.

---

## Agent surface — edit cases (update)

Used by `sync-documentation-maps-agent-update` Step 3.

**Common to all cases:**

- (a) Locate the target section in the map file before editing.
- (b) After each edit, verify: `wc -l <map-file>` did not decrease unexpectedly.

**`missing_from_map`** — active agent has no Layer 1 row or Layer 2 section.

1. Read `profile-al-dev-shared/agents/<agent-name>.md` to extract `model:`,
   `tools:` list, and `description:` frontmatter fields.
2. If the agent has no row in the Layer 1 Catalog table, add one
   (`Agent | Model | Tools | Spawned by`); use the caller list from the
   discrepancy `detail` field, or `(none found)`.
3. If the agent has no `### <agent-name>` Layer 2 section, insert one (before
   Observations if present) with `**Description:**`, `**Model:**`, `**Tools:**`,
   `**Spawned by:**` lines.

**`stale_in_map`** — archived agent still has Layer 1 row or Layer 2 section.

1. If the agent has a row in the Layer 1 Catalog table, remove it.
2. If the agent has a `### <agent-name>` Layer 2 section, remove it (heading
   through the next `###` or `##` heading, exclusive).

**`model_mismatch`** — frontmatter model does not match Layer 2 section.

1. Read `profile-al-dev-shared/agents/<agent-name>.md` to confirm the
   authoritative model value.
2. Update the `Model` column in the Layer 1 table row and the `**Model:**` line
   in the Layer 2 section.

**`tools_mismatch`** — frontmatter tools list does not match Layer 2 section.

1. Read `profile-al-dev-shared/agents/<agent-name>.md` to confirm the
   authoritative tools list (use `(none)` if the list is `[]`).
2. Update the `Tools` column in the Layer 1 table row and the `**Tools:**` line
   in the Layer 2 section.

**`caller_mismatch`** — `Spawned by:` does not match grep-derived callers.

1. Use the grep-derived caller list from the discrepancy `detail` field
   (or `(none found)` if empty).
2. Update the `Spawned by` column in the Layer 1 table row and the
   `**Spawned by:**` line in the Layer 2 section.

---

## Skill surface — discrepancy types (audit)

Used by `sync-documentation-maps-skill-audit` Step 4.

- **`missing_from_map`** — an active skill has no `### /skill-name` section in
  Layer 2 of `docs/al-dev-skills-map.md`.
- **`stale_in_map`** — a `### /skill-name` Layer 2 section exists for an
  archived skill (not in the active list).
- **`phase_count_mismatch`** — the phase count in `SKILL.md` (count of
  `## Phase N` headings) does not match the highest `Phase<N>` node ID in the
  Layer 2 Mermaid diagram. If the diagram is absent or ambiguous, record in
  `detail` (e.g. `"map shows phases 0–3, skill file has phases 0–5"`).
- **`agent_name_mismatch`** — an agent name extracted from `SKILL.md`
  (`al-dev-shared:<name>`) does not appear in the map's Layer 2 section for
  that skill.

---

## Skill surface — edit cases (update)

Used by `sync-documentation-maps-skill-update` Step 3.

**Common to all cases:**

- (a) Locate the target section in the map file before editing.
- (b) After each edit, verify: `wc -l <map-file>` did not decrease unexpectedly.
- (c) After every Layer 1 Mermaid edit, confirm every `style X` line refers to
  a node ID that exists in the diagram; delete any orphaned `style` lines.

**`missing_from_map`** — active skill has no Layer 2 `### /skill-name` section.

1. Read `profile-al-dev-shared/skills/<skill>/SKILL.md` to extract the skill
   description, phase count (count `## Phase N` headings), and all
   `al-dev-shared:<name>` agent references.
2. Insert a new Layer 2 `### /skill-name` section following the template
   pattern used by adjacent sections: description sentence, `flowchart LR`
   Mermaid diagram with phase nodes matching the SKILL.md phase count, and an
   `Agents spawned:` list.
3. If this skill belongs in the Layer 1 lifecycle diagram, add a node ID,
   edges, and `style` line in the Layer 1 Mermaid block.

**`stale_in_map`** — Layer 2 section exists for an archived skill.

1. Remove the entire `### /skill-name` Layer 2 section (heading through the
   next `###` or `##` heading, exclusive).
2. Remove any node, edge, and `style` line for this skill from the Layer 1
   Mermaid diagram.

**`phase_count_mismatch`** — Layer 2 diagram phase count does not match SKILL.md.

1. Read `profile-al-dev-shared/skills/<skill>/SKILL.md` and count `## Phase N`
   headings to determine the authoritative phase count.
2. Rewrite the `flowchart LR` Mermaid block in the Layer 2 section to use the
   correct phase nodes (Phase0 through PhaseN); preserve existing labels.

**`agent_name_mismatch`** — Layer 2 agent list does not match SKILL.md.

1. Read `profile-al-dev-shared/skills/<skill>/SKILL.md` to extract the current
   `al-dev-shared:<name>` agent references.
2. Update the `Agents spawned:` list in the Layer 2 section to match exactly.
