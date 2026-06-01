# Generated Map Sections Design

## Context

The plugin surface map documents contain Mermaid diagrams and catalog tables
that describe skills, agents, knowledge files, and their relationships. Those
sections drift when the canonical source changes because many of them are
maintained by hand.

The source of truth remains the shared plugin surface:

- `profile-al-dev-shared/skills/*/SKILL.md`
- `profile-al-dev-shared/agents/*.md`
- `profile-al-dev-shared/knowledge/*.md`
- projection policy documents only where labels or metadata require them

The goal is to generate the drift-prone Mermaid diagrams and catalog tables
from source while preserving manually authored interpretation and commentary.

## Scope

Generate marked Mermaid and table sections in these documents:

- `docs/al-dev-skills-map.md`
- `docs/al-dev-agent-map.md`
- `docs/al-dev-plugin-graph.md`
- `docs/al-dev-workflow-diagrams.md`

Do not include `docs/projection-layer-readme.md` in this first pass.

The generator is manually run. Generated sections are checked in, but stale
output detection is not added to hooks or blocking validation yet.

## Architecture

Create a deterministic map-section generator at
`scripts/generate-map-doc-sections.py`, backed by reusable extraction logic.
The extraction logic should replace duplicated structured-grep behavior in the
new generator and remain compatible with `scripts/generate-plugin-graph.py`.

Each generated section is bounded by explicit markers:

```markdown
<!-- BEGIN GENERATED: skill-lifecycle-mermaid -->
...
<!-- END GENERATED: skill-lifecycle-mermaid -->
```

The generator replaces only content inside known generated markers. It must not
rewrite surrounding prose, headings, recommendations, or explanatory text.

## Components

### Inventory And Extraction

The inventory layer reads canonical source files and produces structured data:

- skill names from `profile-al-dev-shared/skills/*/SKILL.md`
- agent names and frontmatter from `profile-al-dev-shared/agents/*.md`
- knowledge filenames from `profile-al-dev-shared/knowledge/*.md`
- skill-to-agent references
- skill-to-skill references
- skill-to-knowledge references
- agent-to-knowledge references
- artifact references where a map section needs them

Parsing should use frontmatter parsing for agent metadata and deterministic
regular-expression extraction for existing textual references. It should
deduplicate relationships and produce stable ordering.

### Renderers

Renderers consume the inventory and produce source-derived outputs:

- Mermaid relationship diagrams
- Mermaid lifecycle or workflow diagrams where relationships are inferable or
  backed by a small explicit workflow-order config
- agent catalog tables from frontmatter and discovered spawn relationships
- skill and knowledge reference tables or callouts

When workflow ordering cannot be inferred safely from source references, the
ordering should live in a small explicit config owned by the generator rather
than remaining embedded only in doc prose.

### Document Updater

The updater replaces generated blocks by marker key. It should render all
sections successfully before writing any target document so failures do not
leave partially updated docs.

Missing or duplicate markers are errors. The updater must not append generated
content to a guessed location.

## Error Handling

The generator exits non-zero and leaves documents unchanged when it cannot
safely update sections. Error cases include:

- missing begin or end marker
- duplicate marker key
- unparseable YAML frontmatter in an agent
- generated Mermaid with unsafe or duplicate node IDs
- referenced skill, agent, or knowledge file missing on disk
- renderer requested for an unknown section key

Unlike the current full plugin graph script, this generator should not emit a
partial map section after parse failure. Partial generated blocks inside
authored docs are harder to reason about than a failed refresh.

## Source Boundaries

Generate only relationships, inventories, and source-derived facts. Do not
generate judgement-heavy claims such as recommended improvements, quality
concerns, or architectural conclusions.

Keep authored commentary in the docs. The generator updates diagrams and
tables; maintainers continue to write interpretation.

## Testing

Add focused tests for the new generator:

- fixture-based extraction tests for skills, agents, knowledge files, and
  references
- renderer tests for stable Mermaid node IDs and expected table rows
- updater tests for marker replacement, missing markers, duplicate markers,
  and unchanged output when rendering fails
- a smoke test that runs the generator against the real repo and verifies
  deterministic output for the target docs

If `scripts/generate-plugin-graph.py` is refactored to share extraction logic,
keep `scripts/tests/test_generate_plugin_graph.py` passing as a compatibility
check.

## Verification Commands

Implementation should verify the design with:

```bash
python3 scripts/generate-map-doc-sections.py
python3 scripts/tests/test_generate_map_doc_sections.py
python3 scripts/tests/test_generate_plugin_graph.py
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

The generator is manual-only in this design, so no pre-commit freshness gate is
required.
