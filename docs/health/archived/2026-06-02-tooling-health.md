# Tooling Health — 2026-06-02

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 1      | 6       | 0      | 7     |
| Medium   | 2      | 21      | 0      | 23    |
| Low      | 0      | 0       | 0      | 0     |

**Total suggestions: 30 retained suggestions from a 21-lens sweep**

### Top 5 ranked actions

1. **Command mismatch: sync-documentation-maps-finalize (High)** — Phase 5 is described as dependency-graph refresh but runs `generate-agent-projections.py`. This is a real workflow-correctness issue, not a naming or style problem. Fix the command or the phase description so the finalize step does what it claims.

2. **Name-fit drift: align-harness-repos (High)** — The skill is a harness-neutrality validator, not a general repo-alignment workflow. The current name makes the intent harder to infer than the body warrants.

3. **Remote dispatch contract gap: sync-documentation-maps-collect (High)** — Phase 4 depends on `RemoteTrigger` semantics but does not explain the runtime assumption or fallback behavior if that mechanism is unavailable. That is a real workflow-execution risk.

4. **Lens invocation contract adoption gap (Medium)** — `knowledge/lens-invocation-patterns.md` already defines the minimal per-lens context, but discovery callers still duplicate large prompt/context scaffolding inline. The next step is to converge those callers on the existing contract and reduce duplicated prompt templates.

5. **Description and name-fit drift in maintainer workflows (Medium)** — Several maintainer skills understate what they do or use names that no longer match their operational scope. These are secondary to the correctness issues above, but still worth cleaning up.

---

## Design suggestions

### Atomisation (Split complex skills)

- **sync-documentation-maps-finalize** | High | Phase 5 is labelled as dependency-graph refresh, but the command shown runs `generate-agent-projections.py`. That is a workflow contract mismatch, not just a complexity concern. | Make the command match the documented graph-refresh behavior, or change the phase wording so it accurately describes projection generation.

### Connection/Consolidation (Align invocation patterns)

- **Lens invocation contract adoption** | Medium | design-skill-lens-* and design-agent-lens-* callers still duplicate prompt/context scaffolding even though `knowledge/lens-invocation-patterns.md` already defines the canonical minimal context per lens. | Converge discovery callers on the existing contract and reduce duplicated prompt/context tables inline.

- **Checkpoint passing** | Medium | sync-documentation-maps-collect and sync-documentation-maps-finalize both manage same checkpoint; high coupling. | Factor out shared checkpoint read/write helpers; keep skills separate but reduce duplication.

_Quality/naming extensions documented in respective sections below._

---

## Quality findings

### Bloat (Agent Lenses)

_No issues found._ All 10 lens agents follow compact structure (Inputs, Outputs, Lens definition, Severity rules, Output Format). Cross-file repetition is architectural consistency, not bloat.

### Bloat (Skills)

- **plugin-health-discover** | High | Phase 3b still carries a large inline workflow block. Move the workflow template to a knowledge/helper surface and keep the skill focused on orchestration. | Reduce the in-skill pseudo-code and leave one canonical workflow template or helper reference.

- **audit-quality** | High | Phase 2 dispatch spans 26 lines of boilerplate repeated across discover-agent-design, discover-skill-design. Combined redundancy exceeds 100 lines. Extract to knowledge/audit-parallel-dispatch.md; reference with one line. Reduces bloat by ~80 lines.

- **discover-skill-design** | Medium | Phase 2 lens-invocation context table spans 52 lines nearly identical to discover-agent-design. Extract to knowledge/lens-invocation-patterns.md; replace with table lookup. Reduces from 52 to ~5 lines.

- **discover-agent-design** | Medium | Phase 2 spans 55 lines with same redundancy as discover-skill-design. Same fix: reference knowledge/; reduces to ~5 lines.

### Prompt Clarity (Agent Lenses)

- **quality-agent-lens-clarity** | High | Self-referential bash criterion: agent flags `<placeholder>` syntax but example uses `<placeholder>`. Separate into: (1) unrecognized binaries, (2) undefined variables, (3) allow comment placeholders.

- **quality-agent-lens-clarity** | Medium | "Ambiguous instructions" criterion lacks objective decision rule. Provide examples or behavioral criteria.

- **quality-agent-lens-clarity** | Medium | Output format `[observation]` and `[fix]` fields undefined. Specify field contents (exact text vs. reworded fix).

- **quality-agent-lens-clarity** | Medium | Return condition underspecified: when to stop reading and return? After all files? After first issue? Add explicit trigger.

### Prompt Clarity (Skills)

- **al-dev-map-suggestions-verify** | High | Independence criteria not defined operationally ("3+ independent suggestions"). Define: no file-read conflicts + no output dependency.

- **sync-documentation-maps-collect** | High | Phase 4 depends on `RemoteTrigger` semantics but does not explain the runtime assumption or fallback behavior if that mechanism is unavailable. | Clarify the required runtime capability and the expected argument-passing contract for `RUN_ID` and `RUN_DIR`.

- **sync-documentation-maps-finalize** | Medium | "Refresh dependency graph" vs. "Run generate-agent-projections.py" mismatch. These are different operations. Clarify which.

- **review-agent-map** | Medium | Missing field handling (malformed YAML) not specified. Add: "Record 'undefined' and flag for manual review."

- **projection-sync** | Medium | Corrupted checkpoint YAML handling not specified. Add: "Report parse error; offer Restart or Stop."

### Description Drift

- **al-dev-map-suggestions-verify** | Medium | Description promises "rubber-ducks each" but body shows skip pathway without mentioning in description. Add: "Suggestions failing validation are skipped and noted in ## Skipped."

- **analyze-agent-design** | Medium | Description mentions triggering but doesn't list lenses (tool-hygiene, model-fit, scope-isolation, caller-alignment, usage-patterns). Add specific lens names.

- **analyze-skill-design** | Medium | Description lists "Atomise / Connect / Merge / Promote" but body includes "Extend" and description is incomplete. Update to include Extend.

- **audit-knowledge-quality** | Medium | Description doesn't mention output file (docs/al-dev-knowledge-quality.md) or severity/fix recommendation structure. Add output details.

- **audit-quality** | Medium | Description doesn't list five quality lenses or mention fix-application budget. Clarify methodology and fix-budget protocol.

- **draft-map-suggestions** | Medium | Description says "draft" but skill also completes inventory tables, generates diagrams, writes finalized sections. Underspecifies scope. Rename or clarify as full write operation.

- **plugin-health-report** | Medium | Description says graph refresh is "optional" but the body makes it unconditional for the plugin surface. | Update the description to match the current body behavior.

- **review-agent-map** | Medium | Description says "update the map" but doesn't mention Phase 7's inline candidate detection. Add: "Also detects single-use, minimal-body agents as inline candidates."

- **review-skill-map** | Medium | Description says "update the map" but doesn't mention Phase 7's Move candidate detection. Add: "Also detects skills belonging in .claude/ (internal tooling) via three signals."

- **sync-documentation-maps-finalize** | Medium | Description doesn't mention validation gate (Phase 3) that checks file presence, line count, headers. Add: "Validates each artifact before writing; skips incomplete surfaces."

### Name Fit

- **align-harness-repos** | High | Name implies repository alignment or synchronization, but the body is a focused harness-neutrality validation and optional fix flow. | Rename to `validate-harness-neutrality`, or adjust the description to lead with validation instead of alignment.

- **al-dev-map-suggestions-verify** | Medium | Name suggests verification-only, but skill creates implementation plan in Phase 3. "Verify" undersells planning scope. | Rename to `al-dev-map-suggestions-plan` or clarify to lead with planning.

- **draft-map-suggestions** | Medium | Name "draft" undersells actual scope (completes tables, writes sections, dispatches diagram generation). "Draft" implies incomplete/review-stage. | Rename to `finalize-map-suggestions` or clarify full-scope writing.

- **sync-documentation-maps-collect** | Medium | Name says "collect" but Phase 4 dispatches updates. Term doesn't signal dispatch/gate behavior. | Rename to `sync-documentation-maps-collect-and-dispatch` or clarify dispatch in description.

---

## Naming violations

_No issues found._ All 21 lens names reviewed for this tooling run conform to the expected lens naming shape. Maintainer skill naming is mostly consistent; the concerns above are about name fit, not naming-convention violations.

---

## Graph deltas

_Not applicable for tooling surface._ (Graph refresh applies to plugin surface only.)

---

## Failed lenses

None. All 21 lenses completed successfully.

---

## Dossier metadata

- **Surface:** Tooling (.claude/ maintainer tools)
- **Lint scope:** 19 active skills + 25 active agents + 6 archived skills
- **Lenses run:** 21 (5 design-agent, 5 design-skill, 5 quality-agent, 5 quality-skill, 1 naming convention)
- **Total suggestions:** 30 (7 High, 23 Medium, 0 Low)
- **Dimension breakdown:** 3 Design, 27 Quality, 0 Naming
- **Generated:** 2026-06-02
