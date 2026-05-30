# Tooling Findings — 2026-05-30

## Raw lens output

### Design Agent Lens Tool Hygiene Findings

_No issues found._

All 21 tooling lens agents declare only tools they actually use. All are read-only analysis tools (Read, Grep, or Glob only). No declared-but-unused tools detected.

---

### Design Agent Lens Model Fit Findings

_No issues found._

All 21 tooling lens agents are assigned `haiku`. All tasks are mechanical: file reads, frontmatter extraction, pattern matching, structured output generation. Haiku is appropriately assigned for each. No upgrade or downgrade warranted.

---

### Design Agent Lens Scope Isolation Findings

_No issues found._

Each agent targets a single evaluation lens (one architectural or quality dimension). The 21-agent family is intentionally separated so each lens is independently invocable. Combining agents would violate single-concern principle and prevent selective dispatch.

---

### Design Agent Lens Caller Alignment Findings

_No issues found._

All lens agents have documented Inputs/Outputs sections, and all calling skills (plugin-health-discover, analyze-agent-design, analyze-skill-design, audit-quality) pass exactly the documented inputs. Caller contracts are clean across the tooling surface.

---

### Design Agent Lens Usage Patterns Findings

_No issues found._

All 21 tooling lens agents have Inputs/Outputs tables documented in their bodies. Criterion 3 (no documented contract) fails for all agents, meaning no agent qualifies as an inline candidate regardless of spawn frequency.

---

### Design Skill Lens Shared Backbone Findings

- **design-skill-lens-* family (5 agents: shared-backbone, complexity, near-duplicates, handoff-gaps, preplanning)** | Medium | Both `analyze-skill-design` (Phase 2) and `plugin-health-discover` (Phase 3) spawn these lenses with identical dispatch templates (file list + context fields) but derive the context from different sources — analyze-skill-design uses pre-built working lists from Phase 1, while plugin-health-discover builds its own by parsing documentation maps. This creates two divergent code paths that construct nominally identical context field values. If context structure or field names change, both callers must be updated independently. | Extract a canonical helper document in `knowledge/` specifying: (1) the five lens agent types, (2) required context fields per lens, (3) contract for building each field, and (4) reference URLs for how each caller should populate the fields. Both skills reference this doc to reduce drift when the pattern evolves.

---

### Design Skill Lens Complexity Findings

- **analyze-skill-design** | High | 6 phases with two separable concerns: Phases 1-2 (discovery: read map, build lists, dispatch lenses) vs. Phases 3-6 (synthesis: aggregate findings, draft suggestions, write map). | Extract phases 1-2 into a separate discovery sub-phase; keep phases 3-6 as the core synthesis logic.
- **analyze-agent-design** | High | 6 phases with identical structure to analyze-skill-design — phases 1-2 (discovery) vs. phases 3-6 (synthesis). | Same as above.
- **review-agent-map** | High | 7 phases with two independent workflows: phases 1-5 (audit: scan, extract, cross-ref, compare, report) vs. phases 6-7 (update map and detect candidates). | Extract phases 1-5 into `/audit-agent-map` (pure audit); keep phases 6-7 in `/review-agent-map` for update workflow.
- **review-skill-map** | High | 7 phases with two independent workflows: phases 1-5 (audit) vs. phases 6-7 (verify/commit and move-candidate detection). | Extract phases 1-5 into `/audit-skill-map`; keep phases 6-7 in `/review-skill-map`.
- **draft-map-suggestions** | Medium | 7 phases with separable concerns: phases 1-3 (parse input, receive findings, draft suggestions) vs. phases 4-7 (complete inventory tables, dispatch diagram, write map, present). | Consider splitting draft+present from inventory+diagram+write.

---

### Design Skill Lens Near Duplicates Findings

- **review-agent-map + update-agent-map** | Medium | Both follow identical audit-then-update pattern with 6-7 phases. The simpler update skill could become an option flag on review-agent-map (e.g., `--no-update`). | Merge by adding `--no-update` flag to review-agent-map; archive update-agent-map as a callable sub-skill invoked conditionally.
- **review-skill-map + update-skill-map** | Medium | Same pattern as above for the skill surface. | Merge by adding `--no-update` flag to review-skill-map; archive update-skill-map as a callable sub-skill.
- **analyze-agent-design + analyze-skill-design** | Low | Both have identical phase structure and invoke dispatch in parallel Phase 2. However, they operate on fundamentally different object types (agents vs. skills) with distinct lens vocabularies and output maps. Boundary is intentional. | No merge recommended.
- **audit-agents-against-map + audit-skills-against-map** | Low | Both are audit-only with nearly identical workflows. However, they audit different object types with different structure. | Justifiably two separate audit entry points.

---

### Design Skill Lens Handoff Gaps Findings

- **plugin-health → plan extraction (orphaned)** | Medium | Well-established health sweep produces ranked dossiers in `docs/health/YYYY-MM-DD-<surface>-health.md` with "Top 5 ranked actions" but dossier output is never consumed by any skill. Users must manually review and re-invoke `/plan-map-changes`. | Create a new `/extract-health-plan` skill (or extend `/plan-map-changes` with `--from-health <dossier-path>`) that reads the dossier, identifies High/Medium findings by lens type, and writes a pre-staged context block for planning.
- **Quality audit outputs (orphaned)** | Medium | `/audit-quality` writes comprehensive quality audit reports to `docs/al-dev-agent-quality.md` and `docs/al-dev-skill-quality.md` but these findings are never routed to any remediation skill. | Create a `/plan-quality-fixes` skill that reads quality audit reports and writes a plan to fix clarity, structure, and bloat issues.
- **Knowledge quality audit (orphaned)** | Low | `/audit-knowledge-quality` writes findings to `docs/al-dev-knowledge-quality.md` with HIGH/MEDIUM severity but no skill consumes this output. | Create a `/plan-knowledge-fixes` skill that reads the knowledge quality report and writes a targeted fix plan for stub sections and dead references.

---

### Design Skill Lens Preplanning Findings

- **review-skill-map** | Low | Pre-planning skill explicitly required by analyze-skill-design ("Run /review-skill-map first") but output filename not documented in skill frontmatter description. Skill writes `docs/al-dev-skills-map.md` but this contract is implicit. | Add explicit output reference to skill description: "outputs: docs/al-dev-skills-map.md."
- **review-agent-map** | Low | Same pattern — explicitly required by analyze-agent-design but output contract (`docs/al-dev-agent-map.md`) not stated in description. | Add explicit output reference to skill description.
- **plugin-health-discover** | Low | Downstream `plugin-health-report` depends on findings file at `docs/health/YYYY-MM-DD-<surface>-findings.md` but this filename pattern is only in the body, not in the frontmatter description or argument-hint. | Extend argument-hint or add findings filename pattern to description for explicit output contract.

---

### Quality Agent Lens Bloat Findings

_No issues found._

All 21 tooling lens agents are tightly scoped: 50–62 lines each, 3 sections (Inputs, Outputs, Lens body) all under 30 lines per section. No redundancy, dead branches, or historical commentary. Each maintains strict focus on a single lens aspect.

---

### Quality Agent Lens Clarity Findings

- **design-agent-lens-caller-alignment** | Medium | "check how each spawning skill actually invokes the agent. Search the skills directory" — ambiguous whether agent names should be matched against filenames or frontmatter names. | Clarify: "Pattern matching uses the `name` field from agent frontmatter, not filenames."
- **design-agent-lens-model-fit** | Low | "Evaluate against the task described in the body" — vague without specifying what constitutes sufficient evidence of complexity. | Add explicit signals (e.g., "count file dependencies", "check for multi-step reasoning blocks", "scan for agent spawning").
- **design-agent-lens-scope-isolation** | Low | "Ask: does it describe two clearly separable concerns" — criteria for "clearly separable" is not operationally defined. | Define thresholds: "separable if deleting a contiguous 10+ line block removes one entire phase without breaking the other."
- **design-skill-lens-complexity** | Low | "could this skill be absorbed into an adjacent skill" — "adjacent" is undefined. | Define "adjacent" as "shares at least one spawned agent" or "reads the same .dev/ input files."
- **design-skill-lens-handoff-gaps** | Low | "a well-established chain that has an obvious next step not yet covered" — "obvious" is a vague qualifier. | Replace with: "flagged if 3+ existing skills in a handoff chain converge to a common output and no downstream skill consumes that output."
- **design-skill-lens-near-duplicates** | Medium | "For each pair sharing the same agent types: Compare phase counts. If within 2 of each other, read both files" — no instruction for pairs NOT within 2 of each other. | Add explicit else: "Skip pairs where phase counts differ by > 2 or agent types are different."
- **design-skill-lens-preplanning** | Low | "Check whether its output filename is referenced in Layer 1 handoff labels" — undefined how "referenced" is determined. | Specify: "output filename must appear verbatim in a handoff label or downstream skill's documented inputs."
- **design-skill-lens-shared-backbone** | Medium | "Are the spawn patterns identical or significantly different?" — "significantly different" is vague and unmeasurable. | Define measurable criteria: e.g., "different if dispatch prompt template varies by > 20% token count or context fields differ."
- **naming-convention-lens** | Medium | Statement repeats the same condition twice with contradictory severity assignments. | Clarify: first sentence should specify which deviation is High vs Low.
- **quality-agent-lens-bloat** | Medium | "dead branches" — `skip if...` or `only if...` conditions that "always evaluate the same way in all realistic invocations" — "always evaluate the same way" and "realistic invocations" are not operationally defined. | Add: "dead if the condition's outcome is predetermined by the agent's frontmatter Inputs table or description."
- **quality-skill-lens-bloat** | Low | Threshold inconsistency: agents use >6 sections, skills use >8 steps — different thresholds for similar constructs. | Standardize or explicitly document the rationale for the difference.
- **quality-skill-lens-structure** | Low | Two detection patterns for argument-hint provided but no guidance on which takes precedence if both appear. | Add: "flag if argument-hint is missing AND any of these patterns appear in body."

---

### Quality Agent Lens Description Findings

_No issues found._

All 21 tooling lens agents have accurate descriptions that match their body content. Description verbs, output types, and scope are correctly stated in every case.

---

### Quality Agent Lens Name Fit Findings

- **design-skill-lens-complexity** | Low | Name omits "Outliers" from the full lens concept — description and body both accurately describe "Complexity Outliers" detection, but filename shortens to just "complexity." | Rename to `design-skill-lens-complexity-outliers` or accept as a minor abbreviation.
- **quality-agent-lens-description** | Low | Name says "description" but lens focuses on "Description Drift" — caller may expect description extraction rather than drift detection. | Rename to `quality-agent-lens-description-drift` for clarity.
- **quality-skill-lens-description** | Low | Same pattern as above. | Rename to `quality-skill-lens-description-drift` for clarity.

_All other agents show good name-to-scope alignment._

---

### Quality Agent Lens Structure Findings

- **All 21 tooling lens agents** | High | Missing `model` field in frontmatter — the harness needs this to select the appropriate model for dispatch. All 21 agents should declare `model: haiku` given their mechanical single-file analysis tasks. | Add `model: haiku` to frontmatter of all 21 lens agents in `.claude/agents/`.

_Note: This may be intentional if the harness inherits model from the calling skill's context. Verify whether the model field is required for this agent surface before applying the fix._

---

### Quality Skill Lens Bloat Findings

- **analyze-agent-design** | Medium | Phase 2 contains 92 lines describing five parallel dispatch patterns with nearly identical structure; all five lens invocation templates are copy-pasted with only field names changing. | Extract dispatch template to shared knowledge document; reference it once with field substitution table per lens.
- **analyze-skill-design** | Medium | Phase 2 spans 56 lines with five parallel lens patterns, all structured identically. Repetitive across both analyze-* skills. | Same fix as analyze-agent-design.
- **audit-agents-against-map** | High | 152 lines across 6 phases; Phase 3 (26 lines) has grep commands repeated twice with explanation; Phase 6 (18 lines) has suggestion templates. | Consolidate Phase 3 to 8 lines; move suggestion templates to `knowledge/map-update-templates.md`.
- **audit-knowledge-quality** | High | 142 lines with Phase 2 containing 40 lines of conditional branching logic (parallel vs sequential) that should be in a helper knowledge doc. | Extract parallel-agent dispatch logic to `knowledge/dispatching-strategy.md`.
- **audit-quality** | High | 277 lines; Phase 2 lens-dispatch section (48 lines) copy-pastes agent vs skill variants; Phase 4 template rules (42 lines) include redundant substitution tables. | Consolidate agent/skill dispatch variants; extract Phase 4 logic to `knowledge/quality-report-template.md`.
- **audit-skills-against-map** | High | 135 lines across 5 phases; Phase 1 and Phase 2 mirror `audit-agents-against-map` almost exactly; Phase 5 output format duplicates findings presentation. | Merge audit-skills and audit-agents into a unified skill with `--type skills|agents` parameter.
- **draft-map-suggestions** | High | 232 lines; Phase 3 contains 84 lines of template examples; Phase 4 repeats inventory table descriptions already stated in Phase 2. | Extract suggestion templates to `knowledge/map-suggestion-templates.md`.
- **plan-map-changes** | High | 174 lines; Phase 2 contains 60 lines of rubber-duck checklist; Phase 1 has 20 lines describing argument routing that could be a table. | Condense argument routing to a 5-line table; rubber-duck checklist already referenced in knowledge file — remove redundant prose.
- **plugin-health-discover** | Medium | 120 lines; Phase 2 (37 lines) extracting map context; Phase 3 lens-dispatch table (28 lines) mirrors both analyze-* skills' dispatch tables exactly. | Extract pre-dispatch map-context extraction to `knowledge/map-context-extraction.md`.
- **plugin-health-report** | Medium | 100 lines; Phase 3 template (35 lines) with conditional `_No issues found._` blocks repeated in five sections. | Extract dossier template structure to knowledge.
- **review-agent-map** | High | 224 lines; Phase 2 and Phase 3 mirror respective phases in `/audit-agents-against-map` verbatim; Phase 6 template (44 lines) and Phase 7 inline candidates (35 lines) duplicate logic in `/update-agent-map`. | Consolidate review-agent-map and audit-agents-against-map; absorb Phase 7 into `/update-agent-map`.
- **review-skill-map** | High | 211 lines; Phases 1-4 duplicate `/audit-skills-against-map` nearly exactly; **Dead branch at line 157**: condition "Skip if `$ARGUMENTS` names a specific skill" contradicts the skill's description — both use cases (specific or all-skills) are the same scope. | Consolidate with audit-skills-against-map; remove or document dead branch.
- **projection-sync** | Medium | 177 lines with Phases 0-4 each containing detailed explanatory prose (18-25 lines per phase). | Condense prose to 2-3 core instruction lines per phase; move example YAML to knowledge.
- **update-agent-map** | High | 161 lines; Phases 2-3 mirror respective phases in `/review-agent-map`; Phase 5 inline candidate detection (32 lines) duplicates logic in `/review-agent-map` Phase 7. | Merge update-agent-map with review-agent-map; eliminate Phase 5 duplication.
- **update-skill-map** | High | 128 lines; Phases 2-3 mirror `/review-skill-map` Phases 5-6; Phase 5 move-candidate detection identical to `/review-skill-map` Phase 7. | Merge update-skill-map with review-skill-map; run move-candidate detection once.

---

### Quality Skill Lens Clarity Findings

- **audit-knowledge-quality** | High | "Progress Tracking" section references "one TodoWrite todo per flagged file" but TodoWrite is never defined or available in this context. | Remove TodoWrite references or simplify to "Track progress manually by marking each file analyzed."
- **audit-knowledge-quality** | High | Phase 2 "Parallel Exploration" invokes `superpowers:dispatching-parallel-agents` but does not define what context should be passed to each subagent or what the return format should be. | Specify: "Each subagent returns a YAML structure: {file, issue_type, gap_description, severity}."
- **audit-quality** | High | Phase 1 "Derive skill names from parent directory name" does not address cases where directory name contains hyphens and the artifact uses underscores. | Clarify: "Use directory name as-is; do not transform hyphens or underscores."
- **plan-map-changes** | High | Phase 2: "The rubber duck is a blocker, not a suggestion" but does not define action if rubber-ducking reveals infeasibility. | Specify: "If rubber-ducking finds a suggestion is not feasible, mark verdict as `skip [reason]` and do not include in Phase 3 plan."
- **plugin-health-discover** | Medium | `already_inline_candidates` described as "filter of `single_use_agents`" but filtering criteria not specified. | Define: "Filter single-use agents to those scoring 2+ signals from inline-candidate detection rules."
- **plugin-health-report** | Medium | "Pick the top 5 ranked actions" but no tiebreaker rules specified. | Add: "In case of ties, prefer findings that block other work; then alphabetical order."
- **review-agent-map** | Medium | Phase 7 inline candidate threshold uses "2 or more signals" but does not address agents scoring exactly 1 signal. | Clarify: "Record only agents scoring 2 or more signals. Agents with 1 signal are not candidates and are not recorded."
- **review-skill-map** | Medium | Phase 7 same ambiguity for move candidates with 1 signal. | Same clarification as review-agent-map.
- **align-harness-repos** | Medium | Step 5 contains vague instruction "flag it for manual review rather than auto-replacing, as the example may be illustrative" — criteria for what constitutes an "illustrative" example are undefined. | Define explicit criteria: "Flag for manual review only if the token appears in a code example marked with `...` or a comment explaining it is pseudo-code."
- **audit-agents-against-map** | Medium | Phase 3 "two-pass grep" union resolution not specified when skill directory name differs from invocation name. | Clarify: "If a skill directory name and its qualified reference yield different results, include both in the union and verify manually."
- **draft-map-suggestions** | Medium | Phase 3 "skip anything already marked `← implemented`" but other completed-marker suffixes not defined. | Add: "Skip suggestions marked with `← implemented`, `← completed`, `← done`, or `← deferred`."
- **audit-skills-against-map** | Medium | "parallel markers (`×2`, `×2-3`)" but `×` is ambiguous — does it mean literal `×` or `*2`? | Change to: "parallel markers (`in parallel`, `at once`, or notation like `*2` or `*2-3`)."
- **projection-sync** | Medium | Phase 3 `git diff --name-only` does not specify staging area vs working tree. | Clarify: "Run against the working tree (no arguments); if files are staged, show what has changed since the last commit."
- **sync-documentation-maps** | Low | Phase 5 references "Refresh the dependency graph" by running `generate-agent-projections.py` but skill description says it updates maps, not projections. | Clarify: "This refreshes `docs/al-dev-plugin-graph.md`; it does not regenerate harness-native projections."

---

### Quality Skill Lens Description Findings

- **align-harness-repos** | Medium | Description mentions "validator scans skills, agents, knowledge documents, and markdown guides" but Phase 5 (fix flow) describes replacing specific token types — fix capability not mentioned in description. | Expand description to note "and applies fixes for harness-specific tokens."
- **audit-knowledge-quality** | Medium | Description states "Audit knowledge files for stub sections and structural issues" but does not mention parallel dispatch of Explore subagents when 4+ files are flagged. | Add: "Dispatches parallel agents for large audit scopes (4+ files)."
- **draft-map-suggestions** | Medium | Description says "Writes concrete suggestions" but Phase 5 invokes `al-dev-diagram-generator` — diagram generation not mentioned in description. | Add to description: "Dispatches diagram generation and writes workflow diagrams to docs/al-dev-workflow-diagrams.md."
- **plugin-health-discover** | Low | Description mentions "writes structured findings" but does not specify the directory or filename pattern. | Clarify path pattern: "writes findings to docs/health/YYYY-MM-DD-<surface>-findings.md."
- **plugin-health-report** | Low | Description says "optionally refreshes the dependency graph" but Phase 4 unconditionally runs graph generator for plugin surface. | Correct: "refreshes the dependency graph (plugin surface only; unconditional)."
- **review-skill-map** | Low | Description mentions "verify the map reflects the current state" but Phase 7 detects Move candidates — this output not mentioned in description. | Add: "Detects Move candidates (skills that should migrate to .claude/skills/)."
- **sync-documentation-maps** | Low | Phase 5 runs `generate-agent-projections.py` which is not mentioned in description. | Add: "Refreshes the harness projection layer after successful map updates."
- **review-agent-map** | Low | Description says "Update docs/al-dev-agent-map.md" without noting the conditional nature (only if discrepancies found). | Clarify: "Updates docs/al-dev-agent-map.md if discrepancies are found; audit-only if accurate."

---

### Quality Skill Lens Name Fit Findings

- **align-harness-repos** | Medium | Name "align-harness-repos" implies bidirectional alignment across multiple harness repositories, but skill validates only `profile-al-dev-shared/` shared surface for harness-specific token leakage. The harness repos are consumers, not targets. | Rename to `validate-harness-neutrality` or `check-shared-surface-neutrality` to reflect the actual scope (validation only, single surface).

_All other tooling skills show clear name-to-scope alignment._

---

### Quality Skill Lens Structure Findings

- **audit-knowledge-quality** | Medium | `argument-hint` field missing from frontmatter while body references optional `--verbose` and `--path` parameters. | Add `argument-hint: "[--path <directory>] [--verbose]"` to frontmatter.
- **align-harness-repos** | Medium | `argument-hint: ""` field present but empty — body suggests argument support exists. | Define the optional argument pattern or remove empty field.
- **audit-quality** | Medium | `argument-hint: "--type agent|skill [object-name]"` shown in frontmatter but description says `--type` is required, not optional. | Ensure description and argument-hint are consistent about whether `--type` is required or optional.
- **analyze-agent-design, analyze-skill-design, audit-agents-against-map, audit-skills-against-map, draft-map-suggestions, plan-map-changes, plugin-health-discover, plugin-health-report, plugin-health, projection-sync, review-agent-map, review-skill-map, sync-documentation-maps, update-agent-map, update-skill-map** | Low | Missing code block language tags on bash/markdown/python code fence blocks throughout. | Add `bash`, `markdown`, or `text` language tags to all code fence blocks.

---

### Naming Convention Lens Findings (Tooling Surface)

_Agent files:_
All 21 tooling agent files follow the established lens naming pattern correctly (`design-agent-lens-*`, `design-skill-lens-*`, `quality-agent-lens-*`, `quality-skill-lens-*`, `naming-convention-lens`). No violations.

_Skill files:_
- **audit-agents-against-map** | Low | Deviates from pattern `{verb}-{object}-{aspect}` with extra preposition "against". | Rename to `audit-agent-map` or grandfather as accepted deviation.
- **audit-skills-against-map** | Low | Same pattern — extra preposition "against". | Rename to `audit-skill-map` or grandfather.
- **plugin-health** | Low | Missing verb prefix — pattern requires `{verb}-{object}-{aspect}` but skill starts with object. | Rename to `audit-plugin-health` or establish as grandfathered compound.
- **plugin-health-discover** | Low | Puts verb at end — should be verb-first per convention. | Rename to `discover-plugin-health` or grandfather as compound object.
- **plugin-health-report** | Low | Same pattern — verb at end. | Rename to `report-plugin-health` or grandfather as compound object.
- **sync-documentation-maps** | Low | Uses "documentation" (not in documented object set) and plural "maps." | Rename to `sync-maps` or `sync-plugin-maps`.
- **review-agent-map, update-agent-map** | Low | Uses compound object `agent-map` — verify if this is intentional per convention. | Either document `agent-map` as accepted compound object or use `review-map`/`update-map` with `--type agent` argument.
- **review-skill-map, update-skill-map** | Low | Same pattern with `skill-map` compound. | Same guidance as above.
- **draft-map-suggestions, plan-map-changes** | Low | Verb-object-noun structure is present but "suggestions"/"changes" uses plural — convention prefers singular aspect nouns. | Verify against convention doc or grandfather as accepted.

---

## Failed lenses

None — all 21 tooling surface lenses returned results.
