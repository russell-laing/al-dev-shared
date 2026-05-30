# Tooling Health — 2026-05-30

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 4      | 13      | 0      | 17    |
| Medium   | 6      | 32      | 0      | 38    |
| Low      | 7      | 30      | 12     | 49    |

Lenses: 21 run · 0 failed.

**Top 5 ranked actions:**

1. **Map management skills have severe duplication (High, Bloat)** — `review-agent-map` phases 2-3 duplicate `audit-agents-against-map` phases 1-2 verbatim; `update-agent-map` phase 5 duplicates `review-agent-map` phase 7. Same pattern on the skill side. Merging these 6 skills into 2 unified review skills (each with `--no-update` flag) eliminates all cross-skill duplication and is the single highest-leverage structural change.

2. **All 21 lens agents are missing the `model` field in frontmatter (High, Structure)** — If the harness requires this field for dispatch, all lens agents are incorrectly configured. Add `model: haiku` to all 21 files.

3. **`analyze-skill-design` and `analyze-agent-design` have separable discovery/synthesis phases (High, Complexity)** — Phases 1-2 (build lists, dispatch lenses) are cleanly separable from phases 3-6 (aggregate, draft suggestions, write map). Making this separation explicit enables the health sweep to reuse just the discovery phases.

4. **Clarity blockers in `plan-map-changes` and `audit-knowledge-quality` (High, Clarity)** — `plan-map-changes` Phase 2 is described as "a blocker, not a suggestion" but has no action defined when rubber-ducking reveals infeasibility. `audit-knowledge-quality` Phase 2 references an undefined tool and unspecified parallel-agent return format. Both have undefined failure paths that block correct execution.

5. **`draft-map-suggestions`, `audit-quality`, `plan-map-changes` contain bloated template prose (High, Bloat)** — `draft-map-suggestions` (232 lines) has 84 lines of copy-paste template examples in Phase 3; `audit-quality` (277 lines) copy-pastes agent/skill variants; `plan-map-changes` (174 lines) contains a 60-line rubber-duck checklist already referenced in a knowledge file. All three should extract templates to `knowledge/`.

---

## Design suggestions

### Skill design

**Merge — review-agent-map + update-agent-map** | Both follow identical audit-then-update pattern with 6-7 phases. `update-agent-map` is a subset of `review-agent-map` with duplicate logic in multiple phases. | Add `--no-update` flag to `review-agent-map`; archive `update-agent-map` as an internal sub-skill invoked conditionally.

**Merge — review-skill-map + update-skill-map** | Same pattern as above for the skill surface. | Add `--no-update` flag to `review-skill-map`; archive `update-skill-map` as an internal sub-skill.

**Atomise — analyze-skill-design** | 6 phases with two separable concerns: phases 1-2 (discovery: read map, build lists, dispatch lenses) vs. phases 3-6 (synthesis: aggregate findings, draft suggestions, write map). | Extract phases 1-2 into a standalone discovery entry point to enable reuse by the health sweep; keep phases 3-6 as the synthesis core.

**Atomise — analyze-agent-design** | Same structure as `analyze-skill-design`. | Same approach.

**Atomise — review-agent-map** | 7 phases with two independent workflows: phases 1-5 (audit) vs. phases 6-7 (update and inline-candidate detection). The audit portion duplicates `audit-agents-against-map`. | After the Merge above, extract the pure audit logic; keep phases 6-7 for update and detection.

**Atomise — review-skill-map** | 7 phases with same structure as `review-agent-map`. Dead branch at line 157 also present. | Same approach; remove or document the dead branch.

**Connect — design-skill-lens-* dispatch context** | Both `analyze-skill-design` and `plugin-health-discover` spawn the five design-skill lens agents with identical dispatch templates but derive context from different sources. If context field names change, both callers must be updated independently. | Extract a canonical dispatch contract document in `knowledge/` specifying the five lens types, required context fields, and how each caller builds the fields.

**Extend — health dossier → plan extraction** | Health sweep produces ranked dossiers in `docs/health/YYYY-MM-DD-<surface>-health.md` but this output is never consumed by any downstream skill. Users must manually re-enter context to `/plan-map-changes`. | Consider extending `/plan-map-changes` with `--from-health <dossier-path>` to pre-stage findings.

**Extend — quality audit outputs** | `/audit-quality` writes quality reports to `docs/al-dev-agent-quality.md` and `docs/al-dev-skill-quality.md` but no skill consumes these findings. | Create a `/plan-quality-fixes` skill that reads quality audit reports and writes a targeted fix plan.

---

## Quality findings

### Agent quality

**All 21 lens agents** | High | Structure: Missing `model` field in frontmatter. Haiku is the appropriate model for all mechanical single-file analysis tasks. | Add `model: haiku` to frontmatter of all 21 agents in `.claude/agents/`.

**design-agent-lens-caller-alignment** | Medium | Clarity: "check how each spawning skill actually invokes the agent. Search the skills directory" — ambiguous whether agent names should be matched against filenames or frontmatter names. | Clarify: "Pattern matching uses the `name` field from agent frontmatter."

**design-skill-lens-near-duplicates** | Medium | Clarity: "For each pair sharing the same agent types: Compare phase counts. If within 2 of each other, read both files" — no instruction for pairs NOT within 2 of each other. | Add explicit else: "Skip pairs where phase counts differ by > 2 or agent types are different."

**design-skill-lens-shared-backbone** | Medium | Clarity: "Are the spawn patterns identical or significantly different?" — "significantly different" is unmeasurable. | Define measurable criteria: "different if dispatch prompt template varies by > 20% token count or context fields differ."

**naming-convention-lens** | Medium | Clarity: Statement repeats the same condition twice with contradictory severity assignments. | Clarify which deviation is High vs Low.

**quality-agent-lens-bloat** | Medium | Clarity: "dead branches" — "always evaluate the same way in all realistic invocations" is not operationally defined. | Add: "dead if the condition's outcome is predetermined by the agent's frontmatter Inputs table or description."

**design-skill-lens-complexity** | Low | Name fit: Name omits "Outliers" from the full lens concept "Complexity Outliers." | Rename to `design-skill-lens-complexity-outliers` or document as accepted abbreviation.

**quality-agent-lens-description, quality-skill-lens-description** | Low | Name fit: Names say "description" but lenses focus on "Description Drift" — caller may expect description extraction rather than drift detection. | Rename to `quality-*-lens-description-drift` for clarity.

### Skill quality

**audit-agents-against-map, audit-skills-against-map, review-agent-map, review-skill-map, update-agent-map, update-skill-map** | High | Bloat: These 6 map management skills contain verbatim duplication across phases — `review-*-map` phases 2-3 copy `audit-*-against-map` phases 1-2; `update-*-map` phase 5 copies `review-*-map` phase 7. | Merge per Design suggestions above; duplicate phases disappear in the merged structure.

**draft-map-suggestions, audit-quality, plan-map-changes** | High | Bloat: `draft-map-suggestions` (232 lines) has 84 lines of copy-paste template examples; `audit-quality` (277 lines) copy-pastes agent/skill dispatch variants; `plan-map-changes` (174 lines) contains redundant rubber-duck checklist prose. | Extract templates to `knowledge/map-suggestion-templates.md` and `knowledge/quality-report-template.md`; reference from skills.

**audit-knowledge-quality** | High | Clarity: Phase 2 references undefined tool for progress tracking and invokes parallel-agent dispatch without specifying the subagent return format. | Specify: "Each subagent returns YAML: `{file, issue_type, gap_description, severity}`." Remove undefined tool references.

**plan-map-changes** | High | Clarity: "The rubber duck is a blocker, not a suggestion" but no action defined when rubber-ducking reveals infeasibility. | Add: "If rubber-ducking finds a suggestion is not feasible, mark verdict as `skip [reason]` and do not include in Phase 3 plan."

**audit-quality** | High | Clarity: "Derive skill names from parent directory name" — no guidance for hyphens vs. underscores mismatch between directory name and artifact. | Clarify: "Use directory name as-is; do not transform hyphens or underscores."

**align-harness-repos** | Medium | Name fit: Name implies bidirectional alignment across multiple harness repositories, but skill only validates `profile-al-dev-shared/` for harness-specific token leakage. The harness repos are consumers, not targets. | Rename to `validate-harness-neutrality` or `check-shared-surface-neutrality`.

**align-harness-repos** | Medium | Description: Description mentions "validator scans skills, agents, knowledge documents" but Phase 5 fix flow describes replacing tokens — fix capability not mentioned. | Expand description to note "and applies fixes for harness-specific tokens."

**audit-knowledge-quality** | Medium | Description: Does not mention parallel dispatch of agents when 4+ files are flagged. | Add: "Dispatches parallel agents for large audit scopes (4+ files)."

**draft-map-suggestions** | Medium | Description: Phase 5 invokes the diagram-generator skill — not mentioned in description. | Add: "Dispatches diagram generation and writes workflow diagrams."

**review-agent-map, review-skill-map** | Medium | Clarity: Phase 7 threshold uses "2 or more signals" but agents/skills with exactly 1 signal have no defined outcome — silently ignored or recorded? | Clarify: "Record only those scoring 2 or more signals; 1-signal cases are not candidates and are not recorded."

**audit-agents-against-map** | Medium | Clarity: Phase 3 two-pass grep union resolution not specified when skill directory name differs from invocation name. | Clarify: "If directory name and qualified reference yield different results, include both and verify manually."

**draft-map-suggestions** | Medium | Clarity: Phase 3 "skip anything already marked `← implemented`" but other completed-marker suffixes not defined. | Add: "Skip suggestions marked with `← implemented`, `← completed`, `← done`, or `← deferred`."

**plugin-health-discover** | Medium | Clarity: `already_inline_candidates` described as "filter of `single_use_agents`" but filtering criteria unspecified. | Define: "Filter single-use agents to those scoring 2+ signals from inline-candidate detection rules."

**plugin-health-report** | Medium | Clarity: "Pick the top 5 ranked actions" — no tiebreaker rules. | Add: "In case of ties, prefer findings that block other work; then alphabetical order."

**audit-skills-against-map** | Medium | Clarity: "parallel markers (`×2`, `×2-3`)" — `×` character is ambiguous. | Change to: "parallel markers (`in parallel`, `at once`, or notation like `*2`)."

**projection-sync** | Medium | Clarity: `git diff --name-only` does not specify staging area vs. working tree. | Clarify: "Run against the working tree (no arguments)."

**audit-knowledge-quality** | Medium | Structure: `argument-hint` field missing from frontmatter while body references optional `--path` parameter. | Add `argument-hint: "[--path <directory>] [--verbose]"` to frontmatter.

**align-harness-repos** | Medium | Structure: `argument-hint: ""` field present but empty. | Define the optional argument pattern or remove empty field.

**plugin-health-discover** | Low | Preplanning: Downstream `plugin-health-report` depends on findings file at `docs/health/YYYY-MM-DD-<surface>-findings.md` but this filename pattern is only in the body, not in the description. | Extend description or argument-hint with the output filename pattern.

**review-skill-map, review-agent-map** | Low | Preplanning: Both are explicitly required as prerequisites but their output filenames are not stated in the frontmatter description. | Add explicit output file reference to each skill's description field.

**All tooling skills (most)** | Low | Structure: Missing code block language tags on bash/markdown/python code fence blocks throughout. | Add `bash`, `markdown`, or `text` language tags to all code fence blocks.

---

## Naming violations

**audit-agents-against-map, audit-skills-against-map** | Low | Skill names include extra preposition "against" — deviates from `{verb}-{object}-{aspect}` pattern. Convention-expected: `audit-agent-map`, `audit-skill-map`. | Rename to conform, or explicitly grandfather in the convention doc.

**plugin-health, plugin-health-discover, plugin-health-report** | Low | Skill names place the object before the verb (`plugin-health-*`) — pattern requires verb-first. Convention-expected: `audit-plugin-health`, `discover-plugin-health`, `report-plugin-health`. Alternatively, treat `plugin-health` as an accepted compound object. | Verify intent with convention doc; either grandfather or rename.

**sync-documentation-maps** | Low | Uses "documentation" (not in documented object set) and plural "maps." Convention-expected: `sync-maps` or `sync-plugin-maps`. | Rename or document "documentation-maps" as accepted compound object.

**review-agent-map, review-skill-map, update-agent-map, update-skill-map** | Low | Uses compound objects `agent-map` and `skill-map` — verify if intentional per convention. | Either document `{type}-map` as accepted compound objects, or use `{verb}-map --type {type}` argument pattern.

**draft-map-suggestions, plan-map-changes** | Low | "suggestions"/"changes" are plural aspect nouns — convention prefers singular. | Verify against convention doc or grandfather as accepted.
