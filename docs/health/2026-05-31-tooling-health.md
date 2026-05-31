# Tooling Health — 2026-05-31

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 3      | 18      | 0      | 21    |
| Medium   | 9      | 34      | 0      | 43    |
| Low      | 8      | 25      | 0      | 33    |
| **Total**| **20** | **77**  | **0**  | **97** |

**Failed lenses:** None

**Top 5 ranked actions:**

1. **Merge review-agent-map + review-skill-map** (Design/Near-Duplicates+Complexity, High+Medium) — Both skills use identical 7-phase audit-update-verify structure with `--no-update` and optional object filtering; they differ only in target type (agent vs. skill) and vocabulary. Currently maintained as two separate 250-line files with duplicated scoring matrices and markdown templates. Fix: consolidate into `/review-maps --type agent|skill` with a type-specific vocabulary configuration block.

2. **Fix High clarity issues in discover-agent-design and discover-skill-design** (Quality/Clarity, High) — Both have missing error handling for invalid `--focus` argument values; discover-skill-design additionally doesn't define which focus values are valid. These are called on every analyze-*-design run. Fix: add error handling for unrecognized focus names; enumerate valid values per skill.

3. **Fix analyze-agent-design + analyze-skill-design forward reference error** (Quality/Clarity, High) — Both Phase 4 bodies say "After Phase 5 invocation completes" but Phase 5 doesn't exist in either skill — a daily maintenance trap. Fix: correct phase count; either add the missing Phase 5 documentation or renumber.

4. **Fix argument-hint mismatches across 11 tooling skills** (Quality/Structure, Medium) — Most tooling skills have argument-hint fields that misrepresent actual argument parsing: wrong bracket conventions, missing flags (e.g., `--resume` absent from plugin-health-discover), incorrect required/optional markers. Low effort, high discoverability value. Fix: audit all 11 affected skills; update hints to accurately reflect parsing logic.

5. **Extract shared review-map scoring matrix to knowledge/** (Quality/Bloat, High) — Phase 7 of both review-agent-map and review-skill-map contains a 27–40 line scoring matrix repeated identically in each skill, plus inline markdown templates. Fix: extract to `knowledge/review-map-scoring.md` and `knowledge/review-map-templates.md`; both skills reference by name.

---

## Design suggestions

### Scope Isolation

- **design-skill-lens-complexity** | Medium | Addresses two distinct concerns: Atomise candidates (high-phase skills with separable concerns) and Absorb candidates (zero-agent 2-phase skills). These represent opposite refactoring directions. | Split into `design-skill-lens-complexity-atomise` (6+ phase skills with separable concern groups) and `design-skill-lens-absorb` (zero-agent 2-phase skills overlapping adjacent skills).

### Tool Hygiene

- **naming-convention-lens** | Low | `Glob` tool declared in frontmatter but never referenced in system prompt body. Agent only reads and analyzes files. | Remove `Glob` from tools list; keep only `Read`.

### Shared Execution Backbone

- **All design lens agents (10 total, 2 callers each)** | Medium | All 5 design-agent-lens-* agents follow identical context-passing patterns across discover-agent-design and plugin-health-discover. All 5 design-skill-lens-* agents follow identical patterns across discover-skill-design and plugin-health-discover. 10 identical spawn sites create drift risk when context format changes. | Verify both callers explicitly reference `knowledge/lens-invocation-patterns.md` rather than duplicating spawn prompt templates inline.
- **All quality lens agents (10 total, 2 callers each)** | Medium | Ten quality lens agents spawned identically by audit-quality and plugin-health-discover (file list only). | Add "quality lens standard context" entry to `knowledge/lens-invocation-patterns.md` noting "file list only, no additional context"; have both skills cross-reference it.

### Complexity Outliers

- **draft-map-suggestions** | High | 7 phases with two separable concerns: suggestion drafting + inventory (Phases 1-4) vs. diagram generation + map writing + user presentation (Phases 5-7). | Atomise: extract Phases 5-7 into `/apply-map-suggestions` (diagram + write + present); retain `/draft-map-suggestions` as suggestion synthesis only.
- **review-agent-map** | High | 7 phases; `--no-update` flag already gates Phase 6-7 (map update + inline detection) separately from Phases 1-5 (audit discovery). Natural split exists. | Atomise: move Phase 6-7 into `/apply-agent-map-updates`; leave audit discovery in this skill.
- **review-skill-map** | High | 7 phases; `--no-update` flag gates Phases 5-7 separately from Phases 1-4. Same pattern as review-agent-map. | Atomise: split into `/audit-skill-map` (Phases 1-4) and `/apply-skill-map-updates` (Phases 5-7).
- **plugin-health** | Medium | 2-phase orchestration wrapper — pure glue calling `/plugin-health-discover` then `/plugin-health-report`. Both sub-skills can be invoked independently with the same outcome. | Absorb: document as "convenience wrapper" if retained; otherwise remove and document the two-step pattern in CLAUDE.md.

### Near-Duplicate Shapes

- **review-agent-map + review-skill-map** | Medium | Identical 7-phase audit-update-verify structure with `--no-update` and optional object filtering; differ only in target type (agent vs. skill) and output vocabulary. Currently two separate 250-line files. | Consolidate into `/review-maps --type agent|skill` with unified phase logic; use type-specific configuration for vocabulary and path handling.
- **analyze-agent-design + analyze-skill-design** | Medium | Identical 4-phase discovery-aggregation-draft-present flow; differ only in lens vocabularies (Trim/Remodel/Split/Align/Inline for agents vs. Atomise/Connect/Merge/Promote/Extend for skills). | Consolidate into `/analyze-design --type agent|skill` with a type-specific vocabulary block.
- **discover-agent-design + discover-skill-design** | Low | Identical 2-phase discovery flow; separation by type is defensible for clarity when invoked by health sweeps. | Could consolidate as `/discover-design --type agent|skill`; low priority; deferred unless review-maps + analyze-design consolidation proceeds.

### Handoff Chain Gaps

- **audit-quality → no remediation skill** | Medium | Writes findings to docs/al-dev-agent-quality.md or docs/al-dev-skill-quality.md; no downstream skill consumes these for remediation. | Create `/fix-quality-findings` skill that reads the quality report, rubber-ducks High/Medium findings, and produces a structured improvement plan — completing the audit→fix→verify loop.
- **plan-map-changes → no validation feedback loop** | Medium | Rubber-duck records not persisted; no mechanism to validate that the produced plan matches verified rubber-duck records. | Extend plan-map-changes to write rubber-duck records to `.dev/YYYY-MM-DD-plan-map-rubber-duck-audit.md`.
- **discover-*-design → no durable output** | Low | Both discovery skills return context to callers only; if the caller crashes during synthesis, results are lost. | Create resume mode: optionally write working_lists and candidate_lists to `.dev/YYYY-MM-DD-design-discovery-cache.json`.
- **plugin-health-discover → tooling findings co-mingled** | Low | Tooling surface findings are co-mingled with plugin findings in one dossier; tooling-specific debt is harder to action when mixed. | Consider writing separate findings files per surface (already the case in this run) and ensure the dossier report maintains per-surface separation.

### Pre-planning Skills

- **discover-agent-design** | Low | Produces unnamed context output returned to caller (no named file); discoverable only from /analyze-agent-design, not independently. No maintainer workflow diagram equivalent. | Write working_lists and candidate_lists to `.dev/YYYY-MM-DD-discover-agent-design-context.md`; reference output filename in /analyze-agent-design handoff labels.
- **discover-skill-design** | Low | Same as discover-agent-design. | Same fix.
- **plugin-health-discover** | Low | Output `docs/health/YYYY-MM-DD-<surface>-findings.md` is written to disk but not referenced by handoff label in /plugin-health skill body. | Add explicit handoff label in /plugin-health Phase 1.

---

## Quality findings

### Skill Bloat

- **review-agent-map** | High | Phases 1–7 span 258 lines. Phase 7 scoring logic repeated 3 times (once per signal); Mermaid table templates hardcoded in English prose (lines 164–207). | Extract scoring algorithm and markdown templates to knowledge document (`knowledge/review-map-scoring.md`); compress Phase 7 to 10 lines referencing the shared pattern.
- **review-skill-map** | High | Phases 1–7 span 247 lines. Phase 7 scoring matrix (27 lines) and markdown template identical to review-agent-map. Phase 2 duplicates parsing logic described generically. | Share scoring and template logic with review-agent-map via knowledge document; compress Phase 2 and Phase 7.
- **audit-knowledge-quality** | High | Phase 2 "Analyze Flagged Files" has 30+ lines of instruction blocks duplicated across parallel and sequential code paths. | Extract parallel/sequential conditional into reusable decision block; reference common instruction set rather than inlining.
- **audit-quality** | High | 24-line Python pseudo-code block labeled "do not execute" in a bash code fence. Agent/skill audit paths repeat identical structure across 6 phases. | Replace pseudo-code with 3-line prose description; unify agent/skill paths with substitution variables.
- **plugin-health-discover** | High | Phase 3a (38 lines) mixes Python token-budget pseudocode with two identical matrix tables. Resume-detection phase (18 lines) is a dead branch when not invoked with `--resume`. | Extract token-budget math to a helper reference; collapse matrix tables; inline completed-lens filter directly in Phase 3a.
- **plan-map-changes** | Medium | Phase 2 "Rubber Duck" (30+ lines) has nested subsections; conditional (≤2 suggestions inline, 3+ parallel) is stated but not enforced; no fallback on dispatch failure. | Extract parallel/sequential decision to a reusable block; add explicit sequential fallback.
- **projection-sync** | Medium | Error-handling and progress-checkpointing logic duplicated across Phases 1-4; no recovery procedure if orchestration script returns non-zero. | Reference error handling as a single design pattern; add explicit recovery step.
- **align-harness-repos, analyze-agent-design, analyze-skill-design, discover-agent-design, discover-skill-design, draft-map-suggestions, plugin-health-report, plugin-health, sync-documentation-maps** | Low | Various minor redundancies: off-by-one phase labels, identical dispatch prompts that could be templated, near-duplicate phases that could merge. | Address during next routine edit of each file.

### Skill Prompt Clarity

- **align-harness-repos** | High | Incomplete conditional: no handling if ALIGN_EXIT output format doesn't match expected pattern. | Add else clause: "If output does not match expected format, report parsing failure and stop."
- **analyze-agent-design** | High | Phase 4 says "After Phase 5 invocation completes" — Phase 5 doesn't exist. Forward reference error. | Correct phase count; add missing Phase 5 documentation or renumber.
- **analyze-skill-design** | High | Same forward reference error as analyze-agent-design. | Same fix.
- **audit-quality** | High | Phase 3 sort rule "High first, then Medium, then Low, then clean" has no tiebreaker within a severity level. | Add: "Within each tier, sort by object name alphabetically."
- **discover-agent-design** | High | No error handling if an invalid lens name is passed as `--focus` argument. | Add: "If argument does not match a recognized lens name, report error and default to `all`."
- **discover-skill-design** | High | Valid `--focus` values not enumerated; unclear if `handoff-gaps` or `preplanning` are valid. | Clarify valid focus values and what each triggers.
- **draft-map-suggestions** | High | Phase 1 says "report the error and stop" for missing/invalid `--type` but provides no error message format. | Specify: "Print 'Error: --type must be agent or skill' and exit."
- **plan-map-changes** | High | Independence rule defined (non-overlapping files, no dependency chain) but never used to make an ordering decision. | Add: "Order dependent suggestions so the producing suggestion runs before the consuming one."
- **plugin-health-discover** | High | Token budget calculation pseudocode uses `budget.remaining()` but no Budget object is defined or passed. | Replace with concrete commands or remove budget calculation if not implementable.
- **plugin-health** | High | `--resume` flag documented in body instructions but absent from `argument-hint` line. | Add `[--resume]` to argument-hint.
- **projection-sync** | High | Inline phases (0-4) and orchestration script `run.sh` coexist without explaining the relationship. Ambiguous which is authoritative. | Clarify: "An optional orchestration script automates all phases; if present, invoke it instead of executing phases manually."
- **review-skill-map** | High | Phase 7 skip condition: "Skip if `$ARGUMENTS` names a specific skill" — but Phase 7 also contains a commit step. If Phase 7 skipped, is the commit from Phase 6 also skipped? Unspecified. | Clarify: "If Phase 7 is skipped, commit from Phase 6 still executes."
- **audit-knowledge-quality** | Medium | "4+ files flagged" threshold is ambiguous (4+ distinct files or 4+ flags across files?). | Specify: "When 4 or more distinct files are flagged by the validator."
- **audit-quality** | Medium | Python pseudo-code block in a bash code fence with "do not execute" disclaimer is confusing. | Replace with 3-line prose argument-parsing description.
- **draft-map-suggestions** | Medium | Skip condition for suggestions (← implemented, ← completed, ← done, ← deferred) — unclear if exact string match or pattern match; case-sensitivity undefined. | Clarify: "Case-sensitive exact substring match anywhere in the line."
- **plan-map-changes** | Medium | "Sequential inline path as fallback" — vague about what it falls back from. | Clarify: "For ≤2 suggestions, proceed sequentially. For suggestions with dependencies, order them before parallel dispatch."
- **plugin-health-discover** | Medium | "Failed lens" record format undefined (printed to stdout, written to file, or stored in memory?). | Add: "Write 'Failed lens: <name>' to findings file in Failed lenses section."
- **plugin-health-report** | Medium | "Pick the top 5 ranked actions" has no tiebreaker. | Add: "Within each severity level, rank alphabetically by object name; pick first 5."
- **projection-sync** | Medium | Progress checkpoint format ambiguous — YAML frontmatter in markdown or pure YAML? | Clarify with a full file structure example.
- **review-agent-map** | Medium | `$ARGUMENTS` variable syntax and population method are undefined. | Add: "Arguments are passed via the dispatch prompt; reference as `$ARGUMENTS` or parse from invocation context."
- **sync-documentation-maps** | Medium | Phase 5 projection sync condition undefined — runs for all paths or only when skills map was updated? | Clarify: "Run projection sync only if skills map was updated in Phase 4."

### Skill Description Drift

- **analyze-agent-design** | Medium | Description promises "write concrete Trim/Remodel/Split/Inline/Align suggestions to the Observations section" but actual file write is delegated to `/draft-map-suggestions` (Phase 3). | Clarify that synthesis is dispatched via `/draft-map-suggestions`, or add explicit verification step in Phase 4.
- **analyze-skill-design** | Medium | Same issue: description promises "write concrete Atomise/Connect/Merge/Promote suggestions" but file write is delegated. | Same fix.

### Skill Name Fit

- **align-harness-repos** | High | Name uses imperative verb "align" but primary action is validation; fixes are optional and user-gated. | Rename to `validate-harness-repos` or update description to "Validate and optionally fix harness-specific tokens."
- **audit-knowledge-quality** | Medium | Name implies broad quality audit; actual scope is narrower (stub sections and structural issues only). | Rename to `audit-knowledge-completeness` or narrow description to match.
- **audit-quality** | Medium | Name is too generic; body implements five specific quality lenses. | Rename to `multi-lens-quality-audit` to signal the lens-dispatch pattern.
- **plan-map-changes** | Medium | Name implies planning as primary task; primary mission is rubber-ducking suggestions before planning is invoked. | Rename to `rubber-duck-map-changes` or add rubber-duck emphasis to description.
- **analyze-agent-design, analyze-skill-design, draft-map-suggestions** | Low | "analyze" undersells the synthesis/orchestration role; "draft" undersells the full scope (writes tables, dispatches diagram, writes output files). | Consider `synthesize-*-design` and `generate-map-observations`; low urgency.

### Skill Structural Conventions

- **11 skills with argument-hint mismatches** | Medium | analyze-agent-design, analyze-skill-design, audit-knowledge-quality, audit-quality, draft-map-suggestions, plan-map-changes, plugin-health-discover, plugin-health, review-agent-map, review-skill-map, sync-documentation-maps all have argument-hint fields that misrepresent actual argument parsing (wrong brackets, missing flags, incorrect required/optional markers). | Audit and correct all 11. Priority: plugin-health-discover (missing `--resume`), review-agent-map/review-skill-map (ambiguous "optional" phrasing), audit-quality (mandatory `--type` not marked required), draft-map-suggestions (brackets imply optional when required).
- **align-harness-repos** | Low | `argument-hint: ""` (empty string) should be omitted when the skill takes no arguments. | Remove the `argument-hint` line.
- **discover-agent-design, discover-skill-design, plugin-health-report, projection-sync** | Low | Code blocks missing `bash` language tags (discover-*-design line 39/42; plugin-health-report line 22; projection-sync lines 31, 43, 51, 66, 88). | Add `bash` tag to each.

### Agent Prompt Clarity

- **design-skill-lens-complexity** | Medium | "Phase" vs "step" distinction undefined — "high-phase" uses "phase" but SKILL.md files use both terms. | Define: "A phase is a top-level `## Phase` or `## Step` header in SKILL.md body; 6+ phases = high-phase."
- **design-skill-lens-handoff-gaps** | Medium | "Commonly useful for a task not yet in the plugin" has no operative definition. | Replace with concrete criteria: "Appears referenced in 2+ existing skill bodies or serves 3+ distinct workflows."
- **design-skill-lens-preplanning** | Medium | Method to identify pre-planning skills beyond the provided `preplanning_skills` list is undefined. | Clarify: "Only flag skills explicitly in `preplanning_skills`; or detect by scanning for `*-findings.md` or `*-requirements.md` output patterns."
- **design-agent-lens-usage-patterns** | Medium | "Fewer than 15 lines" body count doesn't specify whether headers and tables count. | Clarify: "Count lines from closing `---` to EOF, including headers and tables, excluding blank lines."
- **quality-agent-lens-bloat** | Medium | "Always evaluate the same way in all realistic invocations" for dead branch detection is subjective. | Clarify: "A dead branch is one where the condition references a frontmatter field whose value never changes for this agent."
- **quality-agent-lens-structure** | Medium | Canonical tool names stored in a mutable comment block — brittle as a dependency. | Move canonical tool names to a stable section or reference `knowledge/harness-concepts.md`.
- **design-agent-lens-model-fit** | Low | "Marginally better" is a subjective severity criterion. | Replace with: "where task involves light synthesis across 2-3 files, where a higher-capability model may reduce truncation risk."
- **quality-agent-lens-bloat** | Low | "Agent's documented contract" is vague — doesn't specify where the contract lives. | Clarify: "based on the Inputs table or body description governing how the agent is invoked."
- **naming-convention-lens** | Low | Validation relies on dispatch-provided surface list; canonical set is in knowledge. | Clarify: "Surface set is always `plugin` or `tooling` per `knowledge/artifact-contracts.md`; no dispatch input needed for validation."

### Agent Structural Conventions

- **design-agent-lens-caller-alignment** | Low | Code block at line 30 missing language tag for URL pattern example. | Add `text` language tag.

---

## Naming violations

_No issues found._

---

*(Graph deltas section omitted — tooling surface only)*
