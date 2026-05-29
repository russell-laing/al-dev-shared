# Tooling Health — 2026-05-29

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 0      | 8       | 0      | 8     |
| Medium   | 0      | 22      | 0      | 22    |
| Low      | 0      | 52      | 0      | 52    |

Design lenses not dispatched in this run (`--dimension quality` used for first sweep).
Naming: `lens naming-convention-lens: no result` — agent not yet registered in harness (pending plugin install after merge).

Top 5 ranked actions:
1. **analyze-agent-design** (skill/quality/clarity/High) — incomplete conditional: no instruction for when grep returns no extractable names
2. **analyze-skill-design** (skill/quality/clarity/High) — incomplete conditional: filtered lens dispatch leaves aggregation phase without guidance for missing blocks
3. **audit-knowledge-quality** (skill/quality/clarity/High) — incomplete conditional: no branch when validator script is missing and Phase 2 cannot run
4. **plan-map-changes** (skill/quality/clarity/High) — incomplete conditional: no error path for unrecognized `--argument` values
5. **review-agent-map** (skill/quality/clarity/High) — pseudo-code without fallback: Phase 7 inline-candidate scoring has no "none found" branch

## Design suggestions

_No design lenses dispatched in this run. Re-run with `--dimension design` or `--dimension all` to generate Atomise / Merge / Trim / Split / Align suggestions._

## Quality findings

### Agents — Clarity (quality-agent-lens-clarity)

- **quality-agent-lens-bloat** | Medium | "always evaluate the same way in all realistic invocations based on the agent's documented contract" — "realistic invocations" remains contextual; fixed in Task 4 (wording tightened) | Monitored; no further action needed this cycle
- **quality-skill-lens-bloat** | Medium | Same Medium finding as above; fixed in Task 4 | Monitored

### Agents — Structure (quality-agent-lens-structure)

_No issues found._

### Agents — Bloat (quality-agent-lens-bloat)

All 21 agents share repetitive "Severity rules" and "Output Format" structural sections — cross-file pattern, Low severity. Systemic fix: extract shared lens-methodology header to `knowledge/lens-methodology.md` and reference it; apply when any lens body is next edited.

- **All 21 agents** | Low | Repetitive "Severity rules" + "Output Format" block pattern across all lens agents | Extract shared template to knowledge file; reference by section name

### Agents — Description Drift (quality-agent-lens-description)

- **design-agent-lens-caller-alignment** | Low | Description phrase "compares documented Inputs/Outputs against how spawning skills actually invoke" slightly imprecise | Rephrase: "checks documented Inputs/Outputs against actual caller invocations"
- **design-agent-lens-model-fit** | Low | "task complexity" in description is vague relative to body's concrete model-tier criteria | Rephrase: "evaluates whether assigned model tier matches the task's reasoning requirements"
- **design-agent-lens-usage-patterns** | Low | "no documented contract" in description vaguer than body check ("No Inputs/Outputs tables") | Rephrase: "identifies single-use agents with small bodies lacking documented Inputs/Outputs tables"
- **design-skill-lens-shared-backbone** | Low | Description mentions only "Connect" outcome; body also describes "Promote" | Add: "or variant patterns warranting explicit documentation (Promote candidates)"

### Skills — Clarity (quality-skill-lens-clarity)

- **analyze-agent-design** | High | No instruction for the case where grep returns no extractable names — aggregation step has no empty-set path | Add: "If a grep pass returns no results, record as empty set; preserve relationship sets even if empty"
- **analyze-skill-design** | High | Filtered lens dispatch (e.g., `atomise` only) leaves Phase 3 aggregation with missing blocks from other lenses | Clarify: "Phase 3 aggregates only returned blocks; candidate lists for filtered-out lenses remain empty"
- **audit-knowledge-quality** | High | Phase 1 exits if validator missing (`exit 1`) but Phase 2 parallel dispatch still proceeds with undefined behavior | Clarify: "If validator script is missing, exit before Phase 2; do not attempt parallel dispatch"
- **plan-map-changes** | High | No error path for unrecognized argument values | Add: "If unrecognized argument, reject with error listing valid values and re-prompt"
- **review-agent-map** | High | Phase 7 inline-candidate scoring has no fallback when no agents score 2+ signals | Add: "If no agents score ≥2 signals, append 'None detected.' instead of suggestion template"
- **review-skill-map** | High | Phase 6 sanity check has no else branch when archived skill names are found in the map | Add: "If grep finds archived names, do not commit; report matches and ask user to fix before re-running Phase 6"
- **align-harness-repos** | Medium | No operative definition of which code blocks are eligible for token flagging vs. auto-replacement | Add: "Code blocks = sections wrapped in triple backticks. Illustrative tokens inside backticks = flag only"
- **analyze-agent-design** | Medium | "as a system" in diagram generation sub-step does not define scope boundary | Add: "Include all direct relationships; exclude transitive relationships not explicit in codebase"
- **analyze-agent-design** | Medium | Diagram extraction algorithm pseudo-code underspecified for suffix extraction | Clarify: "Split on ':' and take second part to extract agent suffix from `al-dev-shared:al-dev-X`"
- **analyze-skill-design** | Medium | "real improvement" has no operative definition | Add: "Real = reduces coupling, shrinks scope, or eliminates dead code; cosmetic only = skip"
- **audit-agent-quality** | Medium | Agent name normalization undefined when lens returns short names | Clarify: "All findings reference agents by filename without `.md`"
- **audit-agent-quality** | Medium | Budget edge case: no guidance when budget rounds to 0 or exactly 1 | Clarify: "Budget 0 = apply only zero-line-reduction fixes; budget 1 = apply single-line fix only"
- **audit-skill-quality** | Medium | "highest-severity finding descending" sort order ambiguous | Clarify: "Sort by worst-finding severity: High first, then Medium, Low, then clean; alphabetical within tier"
- **plan-map-changes** | Medium | "unique to it" in Merge check ambiguous (absent in A vs. domain-specific to B) | Clarify: "Unique = present in skill B but not in skill A SKILL.md"
- **plan-map-changes** | Medium | Inline check pseudo-code: "does any other skill or script reference" — search path undefined | Clarify: "Search via `grep -r '<agent-type-name>' profile-al-dev-shared/ .claude/`; only .md and .py files count"
- **review-agent-map** | Medium | Union of two grep passes has no deduplication rule for overlapping results | Clarify: "If same skill appears in both passes, include it once"
- **review-skill-map** | Medium | "same threshold" for Move candidate justification lacks rationale | Clarify: "≥2 threshold ensures high confidence; adjust only if producing false positives in practice"
- **projection-sync** | Low | "managed outputs" not defined | Clarify: "Managed outputs = files under `profile-al-dev-shared/generated/agents/` only"

### Skills — Structure (quality-skill-lens-structure)

- **analyze-agent-design** | Medium | `argument-hint` does not document the default `all` behaviour for omitted argument | Update: `[focus: trim|remodel|split|inline|align|all, or omit for all]`
- **analyze-skill-design** | Medium | Same argument-hint omission issue | Update: `[focus: atomise|connect|merge|all, or omit for all]`
- **align-harness-repos** | Low | Bash blocks at lines 25–29 missing language tags | Add bash tags
- **analyze-agent-design** | Low | Phase 7 Mermaid block missing `mermaid` tag (fixed in Task 4) | Resolved
- **analyze-agent-design** | Low | Phase numbering mixes sequential and sub-step labeling | Standardize to sequential or `Phase N.A` notation
- **analyze-skill-design** | Low | Bash blocks at lines 49–50 and 193–202 missing tags | Add bash tags
- **audit-agent-quality** | Low | Code block at line 27 missing bash tag | Add bash tag
- **audit-knowledge-quality** | Low | Code blocks at lines 27 and 45 missing bash tags | Add bash tags
- **audit-skill-quality** | Low | Code block at line 27 missing bash tag | Add bash tag
- **plan-map-changes** | Low | Code blocks at lines 119 and 184 missing bash tags | Add bash tags
- **projection-sync** | Low | Code blocks at lines 35, 66, 90 missing bash tags; line 162 missing yaml tag | Add appropriate tags
- **review-agent-map** | Low | Code blocks at lines 25–31 and 69–75 missing bash tags | Add bash tags
- **review-skill-map** | Low | Code blocks at lines 25–34, 49–62, 136–142 missing bash tags | Add bash tags

### Skills — Description Drift (quality-skill-lens-description)

- **analyze-agent-design** | Medium | Description omits workflow diagram as an output (Phase 7 generates it) | Update description to include diagram generation
- **analyze-skill-design** | Medium | Description understates output scope (omits inventory tables and workflow diagram) | Update description to reflect all outputs
- **audit-knowledge-quality** | Medium | Description implies automated write; body makes write conditional on user approval | Clarify: "Identifies and proposes fixes; writes on approval"
- **plan-map-changes** | Medium | Description omits that skill invokes `superpowers:writing-plans` to generate the plan | Add external tool dependency to description
- **projection-sync** | Medium | Description underdocuments resume capability (Phase 0 checkpoint recovery) | Add: "Supports resuming from checkpoints after interruptions"
- **review-skill-map** | Medium | Description does not mention that Move candidate commit is conditional | Clarify: "Move candidates appended only if found"
- **align-harness-repos** | Low | Description overstates "validate" as encompassing fixes; fixes are user-gated | Clarify: "validation identifies findings; fix step requires user approval"
- **audit-agent-quality** | Low | "Reads each SKILL.md directly" — body dispatches agents, not the skill itself | Update: "Dispatches lens agents to audit each agent .md"
- **audit-skill-quality** | Low | Same as audit-agent-quality | Same fix
- **review-agent-map** | Low | "update" understates the conditional create-or-update path | Use "create or update" for precision

### Skills — Bloat (quality-skill-lens-bloat)

- **analyze-agent-design** | High | 9 phases; Phase 7 (workflow diagram, 96 lines) is effectively a mini-skill | Extract Phase 7 to `/generate-workflow-diagram` or `knowledge/`
- **analyze-skill-design** | High | 8 phases; Phase 7 (46 lines) contains schema generation sub-steps | Extract Phase 7 to shared knowledge
- **audit-agent-quality** | High | Phase 4 (50+ lines) has duplicated full-run vs. scoped-run instruction blocks | Consolidate into single conditional; extract Scoped Run protocol to knowledge
- **audit-skill-quality** | High | Same as audit-agent-quality | Same fix
- **plan-map-changes** | High | 8 phases; Phase 2 (105 lines) has 9 type-specific check subsections | Extract Universal Checks and type-specific cards to knowledge files
- **align-harness-repos** | Medium | Steps 2–5 repeat identical if/then gate pattern | Consolidate into single decision gate with parameter variation
- **audit-knowledge-quality** | Medium | Phase 2 (56 lines) has repetitive sequential-analysis steps; accumulated background commentary | Remove commentary; extract Sequential Analysis template to knowledge
- **review-agent-map** | Medium | Phase 6 template (34 lines) could be extracted; Phase 7 duplicates Phase 1 scoring signal definitions | Extract template to `knowledge/agent-map-template.md`; reference Phase 1 in Phase 7
- **projection-sync** | Low | "Narrow scope:" editorial note removed in Task 4 | Resolved

### Skills — Name Fit (quality-skill-lens-name-fit)

- **align-harness-repos** | Medium | "align" implies bidirectional update; body is validation-only, fixes are user-gated | Rename to `validate-harness-neutrality` or update description to clarify validation-only role
- **plan-map-changes** | Medium | Trigger phrases promise "implement" but skill only produces a plan | Remove "implement" from triggers; update description to "rubber-duck and plan"
- **analyze-agent-design** | Low | "analyze" less precise than "design/recommend" | Consider renaming to `design-agent-improvement`; current name acceptable
- **analyze-skill-design** | Low | Same pattern | Consider renaming to `design-skill-improvement`; current name acceptable
- **audit-agent-quality** | Low | "audit" does not surface optional fix capability | Clarify: "Audit agent quality with optional targeted fixes"
- **audit-knowledge-quality** | Low | Same pattern | Clarify description
- **audit-skill-quality** | Low | Same pattern | Clarify description
- **projection-sync** | Low | "sync" implies bidirectional; body is unidirectional validation + regeneration | Clarify description: "Validate, regenerate, and commit harness-native projections"
- **review-agent-map** | Low | "review" might suggest read-only; body writes the map | Update description: "Audit agents and sync docs/al-dev-agent-map.md"
- **review-skill-map** | Low | Same pattern | Update description: "Audit skills and sync docs/al-dev-plugin-map.md"

## Naming violations

_No issues found._ (lens `naming-convention-lens` returned no result — not yet in harness registry; all 21 lens agents now follow the enforced `{design|quality}-{agent|skill}-lens-{aspect}` pattern with the single allowed exception `naming-convention-lens`.)
