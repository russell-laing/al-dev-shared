# Tooling Findings — 2026-05-31

## Raw lens output

### Tool Hygiene Findings

- **naming-convention-lens** | Low | `Glob` tool declared in frontmatter but never referenced in system prompt body. Agent only reads and analyzes files; it does not perform path globbing operations. | Remove `Glob` from tools list; keep only `Read`.

_All other 20 lens agents: declared tools match body usage._

---

### Model Fit Findings

_No issues found._ All 21 tooling lens agents are correctly assigned to haiku. Each executes a focused, mechanical evaluation of specific criteria — single-pass structured analysis within defined output formats, well within haiku capabilities.

---

### Scope Isolation Findings

- **design-skill-lens-complexity** | Medium | Addresses two distinct concerns: identifying high-phase skills with separable concerns (Atomise candidates) and zero-agent 2-phase skills (Absorb candidates). These represent opposite refactoring directions. | Split into (1) `design-skill-lens-complexity-atomise` (high-phase skills with separable concerns) and (2) `design-skill-lens-absorb` (zero-agent 2-phase skills). Each would have its own Inputs/Outputs contract.

_All other 20 lens agents have single, clearly bounded concerns._

---

### Caller Alignment Findings

_No issues found._ All 21 tooling lens agents are fully aligned with their spawning skills. All Inputs table definitions match what dispatching skills (discover-agent-design, discover-skill-design, audit-quality, plugin-health-discover) actually pass.

---

### Usage Patterns Findings

_No issues found._ All 21 tooling lens agents have documented Inputs/Outputs tables and substantive body content. Lens agents are intentionally separated to allow independent invocation by both discovery skills and the health sweep — inlining any of them would reduce reusability.

---

### Shared Execution Backbone Findings

- **All design lens agents (10 total)** | Medium | All 5 design-agent-lens-* and all 5 design-skill-lens-* agents follow identical context-passing patterns across their two callers each (discover-*-design and plugin-health-discover). 10 identical spawn sites total create drift risk when prompt template or context format changes. | Verify both callers reference `knowledge/lens-invocation-patterns.md` explicitly rather than duplicating spawn prompt templates inline.

- **All quality lens agents (10 total)** | Medium | Ten quality lens agents spawned identically by `audit-quality` and `plugin-health-discover` (both pass file list only). | Add explicit "quality lens standard context" entry to `knowledge/lens-invocation-patterns.md` noting "file list only, no additional context".

---

### Complexity Outliers Findings

**High phase count (Atomise candidates):**

- **draft-map-suggestions** | High | 7 phases with two separable concerns: suggestion drafting + inventory (Phases 1-4) vs. diagram generation + map writing + user presentation (Phases 5-7). | Atomise: extract Phases 5-7 into `/apply-map-suggestions` skill.

- **review-agent-map** | High | 7 phases with two separable concerns: audit discovery (Phases 1-5) vs. map update + inline detection (Phases 6-7). `--no-update` flag already gates Phase 6-7 — natural split exists. | Atomise: move Phase 6-7 into `/apply-agent-map-updates`.

- **review-skill-map** | High | 7 phases with two separable concerns: audit discovery (Phases 1-4) vs. map update + move-candidate detection (Phases 5-7). `--no-update` flag already separates paths. | Atomise: split into `/audit-skill-map` and `/apply-skill-map-updates`.

**Zero-agent 2-phase skills (Absorb candidates):**

- **plugin-health** | Medium | 2 phases, no agents — pure orchestration glue calling `/plugin-health-discover` then `/plugin-health-report`. Sub-skills can be invoked independently. | Absorb candidate: document as "convenience wrapper" if retained, or remove and document the two-step pattern.

---

### Near-Duplicate Shapes Findings

- **review-agent-map + review-skill-map** | Medium | Both use identical 7-phase audit-update-verify structure with `--no-update` and optional object filtering; differ only in target type (agent vs skill). | Consolidate into `/review-maps --type agent|skill` with unified phase logic.

- **analyze-agent-design + analyze-skill-design** | Medium | Both use identical 4-phase discovery-aggregation-draft-present flow; differ only in lens vocabularies. | Consolidate into `/analyze-design --type agent|skill`.

- **discover-agent-design + discover-skill-design** | Low | Both use identical 2-phase discovery flow. Separation by type is defensible for clarity; low priority. | Could consolidate as `/discover-design --type agent|skill`; deferred.

---

### Handoff Chain Gaps Findings

- **audit-quality → no remediation skill** | Medium | `audit-quality` writes findings to docs/al-dev-agent-quality.md or docs/al-dev-skill-quality.md but no downstream skill consumes these for remediation. | Create a `/fix-quality-findings` skill that reads the quality report and produces a structured improvement plan — completing the audit→fix→verify loop.

- **plan-map-changes → no validation feedback loop** | Medium | Rubber-duck records are not persisted; no mechanism to validate that the produced plan matches verified rubber-duck records. | Extend to write rubber-duck records to `.dev/YYYY-MM-DD-plan-map-rubber-duck-audit.md`.

- **discover-agent-design / discover-skill-design → no durable output** | Low | Both discovery skills return context to callers but write no `.dev/` artifacts. If caller crashes during synthesis, results are lost. | Create resume mode: optionally write working_lists and candidate_lists to `.dev/YYYY-MM-DD-design-discovery-cache.json`.

- **plugin-health-discover → tooling findings co-mingled** | Low | Tooling surface findings are co-mingled with plugin findings in a single dossier; tooling-specific debt harder to action. | Consider writing separate findings files per surface.

---

### Pre-planning Skills Findings

- **discover-agent-design** | Low | Produces unnamed context output (returned to caller, not written to named file); not independently discoverable. | Standardize: write working_lists and candidate_lists to `.dev/YYYY-MM-DD-discover-agent-design-context.md`.

- **discover-skill-design** | Low | Same as discover-agent-design. | Same fix.

- **plugin-health-discover** | Low | Output `docs/health/YYYY-MM-DD-<surface>-findings.md` is written to disk but not referenced by handoff label in /plugin-health skill body. | Add explicit handoff label in /plugin-health Phase 1.

Note: Maintainer tooling has no equivalent Layer 1 lifecycle diagram. Consider adding a maintainer workflow diagram to docs/ for visibility.

---

### Agent Bloat Findings (tooling agents)

_No issues found._ All 21 tooling lens agents are intentionally compact (3-5 sections, under 30 lines per section). No dead branches, repetitive blocks, or historical commentary detected.

---

### Agent Prompt Clarity Findings (tooling agents)

**Medium severity:**
- **design-skill-lens-complexity**: "phase" vs "step" distinction undefined. → Define: "A phase is a top-level `## Phase` or `## Step` header in the SKILL.md body."
- **design-skill-lens-handoff-gaps**: "commonly useful" criterion has no operative definition. → Replace with concrete criteria.
- **design-skill-lens-preplanning**: method to identify additional pre-planning skills beyond the provided list is undefined. → Clarify detection method.
- **design-agent-lens-usage-patterns**: line count rule (15 lines) doesn't specify whether headers/tables count. → Clarify: "include all headers and tables, exclude blank lines."
- **quality-agent-lens-bloat**: "realistic invocations" is subjective for dead branch detection. → Define as: "condition references a frontmatter field whose value never changes."
- **quality-agent-lens-structure**: canonical tool names dependency on mutable comment block is brittle. → Move to stable knowledge document.

**Low severity:** quality-skill-lens-clarity (missing pseudo-code example), quality-agent-lens-bloat ("contract" reference vague), naming-convention-lens (surface set could reference knowledge doc), design-agent-lens-model-fit ("marginally better" subjective).

---

### Agent Description Drift Findings (tooling agents)

_No issues found._ All 21 tooling lens agents have descriptions that accurately reflect their bodies.

---

### Agent Name Fit Findings (tooling agents)

_No issues found._ All 21 tooling lens agents follow consistent naming pattern `{quality|design}-{agent|skill}-lens-{aspect}` with no naming drift.

---

### Agent Structural Conventions Findings (tooling agents)

**Low severity:**
- **design-agent-lens-caller-alignment**: code block at line 30 missing language tag (use `text`).

_All other 20 lens agents: no structural issues. No missing `name` fields, no tool canonicality violations._

---

### Skill Bloat Findings (tooling skills)

**High severity:**

- **review-agent-map** | High | Phases 1–7 span 258 lines. Phase 7 scoring logic repeated 3 times. Mermaid table templates hardcoded in English prose. | Extract scoring algorithm and markdown templates to knowledge document; compress Phase 7 to 10 lines.

- **review-skill-map** | High | Phases 1–7 span 247 lines. Phase 2 duplicates parsing logic. Phase 7 scoring matrix (27 lines) and template identical to review-agent-map. | Share scoring/template logic via knowledge document; compress Phases 2 and 7.

- **audit-knowledge-quality** | High | Phase 2 has 30+ lines of instruction blocks duplicated across parallel and sequential code paths. | Extract parallel/sequential conditional into reusable decision block.

- **audit-quality** | High | 24-line Python pseudo-code block with "do not execute" disclaimer. Agent/skill paths repeat identical structure. | Replace with 3-line prose; unify agent/skill paths into template with substitution variables.

- **plugin-health-discover** | High | Phase 3a (38 lines) mixes Python pseudocode with two identical matrix tables. Resume phase is a dead branch when not invoked with `--resume`. | Extract token-budget math to helper reference; collapse matrix tables; inline filter in Phase 3a.

**Medium severity:**
- plan-map-changes: Phase 2 Rubber Duck (30+ lines) with nested subsections; no fallback for dispatch failure
- projection-sync: error handling logic duplicated across phases; missing recovery step for script failure

**Low severity:**
- align-harness-repos: 6 steps could be 4 phases
- analyze-agent-design / analyze-skill-design: non-existent Phase 5 referenced (off-by-one)
- discover-agent-design / discover-skill-design: 5 identical-structure dispatch prompts could be templated
- draft-map-suggestions: Phases 6–7 nearly identical; Phase 2 restates caller context
- plugin-health-report: Phases 3–5 could merge into single "Finalize and Report" phase
- plugin-health: 2-phase wrapper adds no value beyond sub-skill invocation
- sync-documentation-maps: Phase 3–4 repeat same conditional structure

---

### Skill Prompt Clarity Findings (tooling skills)

**High severity:**
- align-harness-repos: no handling if ALIGN_EXIT output doesn't match expected format
- analyze-agent-design: "Phase 4 — Present to User" says "After Phase 5 invocation completes" but Phase 5 doesn't exist
- analyze-skill-design: same forward reference error as analyze-agent-design
- audit-quality: Phase 3 sort rule has no tiebreaker within severity level
- discover-agent-design: no error handling for invalid lens name argument
- discover-skill-design: validity of `--focus handoff-gaps`/`--focus preplanning` undefined
- draft-map-suggestions: "report the error and stop" has no format specified
- plan-map-changes: independence rule defined but never used to make ordering decision
- plugin-health-discover: `budget.remaining()` pseudo-code with no Budget object defined
- plugin-health: `--resume` flag documented in body but absent from argument-hint
- projection-sync: inline phases + orchestration script coexist with no explanation of relationship
- review-skill-map: Phase 7 skip condition creates ambiguous commit behavior

**Medium severity (representative):**
- audit-knowledge-quality: "4+ files" threshold ambiguous
- audit-quality: Python pseudo-code in bash fence with "do not execute" is confusing
- draft-map-suggestions: skip condition matching method (exact string vs. pattern) undefined
- plan-map-changes: "sequential as fallback" unclear
- plugin-health-discover: "Failed lens" record format undefined
- plugin-health-report: top-5 ranking has no tiebreaker
- projection-sync: progress checkpoint format (YAML frontmatter vs. pure YAML) ambiguous
- review-agent-map / review-skill-map: `$ARGUMENTS` variable syntax and population undefined
- sync-documentation-maps: projection sync condition in Phase 5 undefined

---

### Skill Description Drift Findings (tooling skills)

- **analyze-agent-design** | Medium | Description promises "write concrete Trim/Remodel/Split/Inline/Align suggestions to the Observations section" but actual file write is delegated to `/draft-map-suggestions`. | Clarify that synthesis is dispatched via `/draft-map-suggestions`, or add explicit verification step.

- **analyze-skill-design** | Medium | Same issue: file write delegated to `/draft-map-suggestions`. | Same fix.

_No drift detected in other 14 skills._

---

### Skill Name Fit Findings (tooling skills)

- **align-harness-repos** | High | Name uses imperative verb "align" but primary action is validation; fixes are optional and user-gated. | Rename to `validate-harness-repos` or update description.

- **audit-knowledge-quality** | Medium | Name implies broad quality audit; scope is narrower (stub sections and structural issues). | Rename to `audit-knowledge-completeness` or narrow description.

- **audit-quality** | Medium | Name is too generic; body implements five specific quality lenses. | Rename to `multi-lens-quality-audit`.

- **plan-map-changes** | Medium | Name implies planning; primary mission is rubber-ducking (validation before planning). | Rename to `rubber-duck-map-changes` or add rubber-duck emphasis to description.

---

### Skill Structural Conventions Findings (tooling skills)

**Medium severity — argument-hint mismatches:**
analyze-agent-design, analyze-skill-design, audit-knowledge-quality, audit-quality, draft-map-suggestions, plan-map-changes, plugin-health-discover, plugin-health, review-agent-map, review-skill-map, sync-documentation-maps — all have argument-hint fields that don't accurately reflect body argument parsing logic.

**Low severity:**
- align-harness-repos: `argument-hint: ""` (empty string) should be omitted
- discover-agent-design: line 39 missing `bash` tag
- discover-skill-design: line 42 missing `bash` tag
- plugin-health-report: line 22 missing `bash` tag
- projection-sync: lines 31, 43, 51, 66, 88 missing `bash` tags

---

### Naming Convention Findings (tooling)

_No issues found._ All 21 tooling lens agent names follow the enforced pattern. All 16 active tooling skill names follow the advisory pattern. Output paths follow documented conventions.

---

## Failed lenses

None

## Resume information

- Total lenses in scope: 21
- Completed this session: 21
- Completed in prior sessions: 0
- Status: COMPLETE
