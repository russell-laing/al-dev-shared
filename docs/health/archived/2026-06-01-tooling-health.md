# Tooling Health — 2026-06-01

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 0      | 19      | 0      | 19    |
| Medium   | 0      | 42      | 1      | 43    |
| Low      | 0      | 64      | 0      | 64    |

**Top 5 ranked actions:**

1. **[High / Clarity]** Remove harness-specific `AskUserQuestion` tool reference from `sync-documentation-maps-collect/SKILL.md` Phase 5 — shared surface must use generic `USER_GATE` concept; this token leaks Claude Code harness vocabulary into a distributed skill
2. **[High / Bloat]** Reduce `sync-documentation-maps-collect` from 8 phases to 4 — Phases 5–7 make overlapping UI/file decisions with repeated checkpoint writes; restructure as: (1) Load, (2) Poll, (3) Read artifacts, (4) Ask user & dispatch
3. **[High / Bloat]** Remove `audit-quality` Phase 2 pseudo-code Python block labeled "Reference only — do not execute" — 50 lines of dead code; replace with single pointer to parsing implementation
4. **[High / Description]** Verify `al-dev-diagram-generator` agent exists before `draft-map-suggestions` dispatches it — body references this agent without confirming its existence; missing agent causes silent failure
5. **[High / Name-fit]** Rename `plugin-health` → `plugin-health-audit` — name does not signal read-only suggestions-only scope; users may invoke it expecting auto-fix behavior

Failed lenses: None.

---

## Design suggestions

_No design lenses were run against the tooling surface in this sweep._

---

## Quality findings

### Bloat

**Agents:**

- **sync-documentation-maps-agent-audit** | Medium | Repetitive instruction blocks duplicated across all four audit/update agents (Step structure, verification patterns, file-write procedures) | Extract common patterns to `knowledge/sync-documentation-maps-common.md`; reference from each agent
- **sync-documentation-maps-skill-audit** | Medium | Same repetitive structure as agent-audit; Step numbering and validation patterns nearly identical | Same fix — extract to shared knowledge document
- **sync-documentation-maps-agent-update** | Medium | Identical Step structure, verification patterns, and file-write error handling with agent-audit | Consolidate audit-common patterns (Steps 1–6 template, verification gate, JSON output contract)
- **sync-documentation-maps-skill-update** | Medium | Near-identical "Read metadata, update map, return" structure across four type-specific fix categories | Extract sync-common patterns; consider templated instruction base

**Skills:**

- **sync-documentation-maps-collect** | High | 8 phases with Phases 5–7 making overlapping UI/file decisions with repeated checkpoint writes (145–240 lines) | Reduce to 4 phases: (1) Load checkpoint, (2) Poll if --wait, (3) Read artifacts, (4) Ask user & spawn updates
- **sync-documentation-maps-finalize** | High | 8 phases with overlapping checkpoint/summary writes in Phases 1, 6, 8 (3 checkpoint operations) | Consolidate to 5 phases: (1) Load, (2) Check status, (3) Read artifacts, (4) Write maps, (5) Commit & finalize
- **review-agent-map** | High | Phase 7 is 30+ lines for inline-candidate scoring and only runs on non-scoped invocations; adds 13% to total skill length | Split Phase 7 into separate skill or move scoring logic to helper note
- **review-skill-map** | High | Phase 7 is 57+ lines (30% of skill) and only executes when no `$TARGET_SKILL` argument is passed | Extract Phase 7 move-candidate detection into separate `/discover-move-candidates` skill
- **plugin-health-discover** | High | Phase 3a is 65+ lines with nested token-budget, wave-logging, and per-lens context tables | Extract token-budget logic inline (3 lines); move per-lens context tables to `knowledge/lens-invocation-patterns.md`
- **audit-knowledge-quality** | High | 6 named phases plus nested "Parallel Exploration" and "Sequential Analysis" subsections | Flatten nested hierarchy; move Parallel/Sequential routing into Phase 2 as brief rule
- **audit-quality** | High | Phase 2 contains 50-line Python block labeled "Reference only — do not execute" | Remove Python block; replace with one-line pointer to parsing implementation
- **plan-map-changes** | High | Phase 2 rubber-duck section is 35+ lines with nested subsections; references two knowledge files that may not exist | Verify knowledge files exist; split into "Rubber-Duck Protocol" (1 rule) + "Progressive Exploration"
- **discover-agent-design** | Medium | Phase 1 builds 7 working lists; Phase 2 repeats same 7 list names in lens context fields with overlapping definitions | Merge list-building and lens-dispatch into single phase; define each list once
- **discover-skill-design** | Medium | Same pattern as discover-agent-design | Merge phases
- **projection-sync** | Medium | Progress-checkpoint write described twice (workflow section + "Progress Checkpoint Format" section); all 4 phases update same file | Consolidate checkpoint spec into one section
- **sync-documentation-maps** | Medium | Phase 4 JSON field list is 14 fields that should live in a shared reference file | Replace with pointer to `knowledge/sync-maps-checkpoint-format.md`
- **draft-map-suggestions** | Medium | Phase 2 repeats same input-context structure 4 times across agent/skill variants | Create single "Input Context Contract" section; remove inline repetition
- **plugin-health-report** | Low | Phase 2–3 boundary between ranking and writing is unclear; writing section (Phase 3) is 43 lines | Merge Phase 2 and 3 into "Rank and Write Dossier"
- **analyze-agent-design / analyze-skill-design** | Low | Phase 4 reiterates highest-leverage marking criteria already described in Phase 2–3 | Consolidate highest-leverage rule into one section

### Clarity

**Agents — High severity:**

- **naming-convention-lens** | High | "The single allowed exception is `naming-convention-lens`" — no explanation for why; rule boundary is opaque | Add rationale: "Meta-lenses that audit the naming convention they enforce are exempt to prevent circular self-violation"
- **design-agent-lens-model-fit** | High | "Marginally better output" (Low severity trigger) is subjective and context-dependent | Replace with concrete threshold or remove Low severity tier from this lens
- **sync-documentation-maps-agent-audit** | High | Incomplete conditional: tools matching check has no `else` clause after normalization | Add: "After normalization, flag as `tools_mismatch` only if normalized values differ as strings"
- **sync-documentation-maps-skill-update** | High | Incomplete conditional: "confirm every `style` line has a matching node ID" but no action specified on mismatch | Add: "If orphaned `style` line found, delete it immediately before proceeding to next step"

**Agents — Medium severity:**

- **design-skill-lens-complexity** | Medium | "Cluster into two distinct concerns" — no decision rule for "distinct" | Add: "Distinct = two groups where deleting one leaves the other comprehensible without modification"
- **design-skill-lens-handoff-gaps** | Medium | "Obvious next step" is subjective | Define: "Obvious = completes a common downstream workflow already present in the plugin"
- **design-skill-lens-near-duplicates** | Medium | "Could be merged" and "plausibly confuse" are subjective | Add: "Flag as Merge candidate only if a user invoking the simpler skill would reasonably expect the same behavior as the complex skill"
- **design-skill-lens-shared-backbone** | Medium | "Identical or significantly different" is bipolar with no middle ground | Add three tiers: "Identical = same template; Substantially different = >50% fields diverge; Partially similar = otherwise"
- **quality-skill-lens-bloat** | Medium | Skills use >8 step threshold but agents use >6; no explanation for the difference | Unify thresholds or document rationale
- **quality-skill-lens-name-fit** | Medium | "Trigger-phrase conflicts" undefined | Add rule: "Conflict exists if trigger phrases describe action X but name implies action Y"
- **quality-skill-lens-structure** | Medium | "References an optional argument" has no operative definition | Add examples: "body contains 'If an argument was passed', `[arg]`, or `{{arg}}`"
- **sync-documentation-maps-agent-update** | Medium | Vague: "present = list in `detail` field" — malformed content handling undefined | Clarify: "Present = non-empty comma-separated list; otherwise use `(none found)`"
- **sync-documentation-maps-skill-audit** | Medium | "Derive phase count from Mermaid diagram" — no rule for non-contiguous phase IDs | Add: "Take highest numeric suffix N in any `Phase<N>` node ID as phase count, regardless of gaps"

**Skills — High severity:**

- **sync-documentation-maps-collect** | High | Uses harness-specific `AskUserQuestion` tool name in Phase 5 — violates harness-neutrality requirement for shared surface content | Replace with generic `USER_GATE` concept throughout
- **plan-map-changes** | High | Phase 2 says "rubber duck is a blocker" but "resolve" is undefined: does skill author the fix or escalate to user? | Clarify: "If mismatch: update suggestion wording, OR mark 'Verdict: skip [reason]' and exclude from plan"
- **audit-quality** | High | Phase 2 docstring says "substitute `{file_list}`" but also labels a code block "Reference only — do not execute" — contradictory instructions | Remove pseudo-code block entirely or explicitly label as documentation only with no execution path

**Skills — Medium severity:**

- **plugin-health** | Medium | `--resume` flag described in a separate section but not in argument-hint or Phase 0 parsing | Add `--resume` to argument-hint; add Phase 0 parsing step
- **projection-sync** | Medium | Phase 0 "Offer Resume or Restart" — mechanism unspecified (is this a USER_GATE prompt?) | Clarify: "Use USER_GATE prompt. On Restart: delete checkpoint, proceed to Phase 1. On Resume: skip to next incomplete phase"
- **review-agent-map** | Medium | Phase 3 "union the results from both passes" — set or list union? | Clarify: "Set union — deduplicate by file path"
- **review-skill-map** | Medium | Phase 5 "corresponding node" for Mermaid style guard is ambiguous | Clarify: "Node corresponds if it appears in a node declaration `X[label]` or as source/target in an edge"
- **sync-documentation-maps-finalize** | Medium | Phase 5 references `generate-agent-projections.py` but Phase 4 calls it "Refresh Dependency Graph" — inconsistent naming | Clarify: "Run `generate-agent-projections.py` — this IS the dependency graph refresh"
- **sync-documentation-maps-collect** | Medium | Phase 7 uses `jq` for JSON merge with no fallback if `jq` fails | Add: "On jq failure: use Python read-mutate-write fallback"
- **plugin-health-discover** | Medium | Token budget constant `per_lens_token_budget = 5000` has no adjustment rule when actual costs exceed it | Add: "If lens historically costs >5000 tokens, reduce `lenses_per_wave` by 1"
- **draft-map-suggestions** | Medium | "Skip patterns that don't yield a real improvement" — no operative definition | Add: "Skip if: duplicates an implemented suggestion, affects <2 files, or <5% complexity reduction"

### Description drift

**High severity:**

- **draft-map-suggestions** | High | Body dispatches `al-dev-diagram-generator` agent but existence of this agent is unverified | Verify agent exists in `profile-al-dev-shared/agents/`; if missing, remove Phase 5 or replace with concrete implementation
- **plan-map-changes** | High | Body references `knowledge/map-change-rubber-duck-checks.md` and `knowledge/rubber-duck.md` without confirming files exist | Verify both knowledge files exist; inline the checks or remove references if missing
- **sync-documentation-maps-finalize** | High | Description says "refreshes the dependency graph" but body runs `generate-agent-projections.py` (projections generator, not a graph refresh tool) | Clarify: "Regenerates harness-native projection artifacts; this serves as the dependency graph refresh step"

**Medium severity:**

- **audit-quality** | Medium | Description says skill "reads each agent .md or SKILL.md directly" but body dispatches five parallel lens agents | Correct: "Dispatches parallel lens agents; does not read files directly"
- **discover-agent-design / discover-skill-design** | Medium | Description says "Returns candidate_lists and working_lists for synthesis" but output format is undocumented with no example structure | Add example structure to clarify output format
- **plugin-health-discover** | Medium | Description says "dispatches all design and quality lenses" but body may halt early on token budget | Clarify: "Lenses dispatched in waves; use --resume to complete in subsequent sessions"
- **plugin-health-report** | Medium | Description says "ranks findings" without defining ranking criteria | Clarify: "Ranked: severity-first (High → Medium → Low), then dimension, then object type"
- **align-harness-repos** | Medium | Description implies fixes are applied automatically; body requires user approval gate before any edit | Clarify: "Fixes proposed and applied only after user approval via USER_GATE"
- **projection-sync** | Medium | Description says "validate shared agent source" but validation checks all shared source (agents, skills, knowledge) | Clarify: "Validates harness neutrality across all shared source — agents, skills, and knowledge files"
- **review-agent-map / review-skill-map** | Medium | Description says "update docs/al-dev-[agent|skills]-map.md" but body creates file if absent | Clarify: "Creates map if absent; updates existing map with targeted edits"
- **sync-documentation-maps-collect** | Medium | Description says "conditionally spawns remote update teams" but body uses harness-specific tool (`AskUserQuestion`) | Document harness requirement or add fallback
- **sync-documentation-maps** | Medium | Description says "dispatches parallel remote audit teams via RemoteTrigger" without confirming tool exists | Verify RemoteTrigger availability; document error handling if absent

### Name fit

**High severity:**

- **plugin-health** | High | Name doesn't signal read-only suggestions-only scope; "audit the plugin" trigger implies broader capability than suggestions; users may expect auto-fix | Rename to `plugin-health-audit` or prefix description with "Suggestions-only:"

**Medium severity:**

- **plan-map-changes (tooling)** | Medium | Primary behavior is rubber-duck verification of existing suggestions, not plan creation; name implies creating new plans | Rename to `verify-map-suggestions`
- **sync-documentation-maps-collect** | Medium | "Collect" understates user-gate and update-team dispatch roles | Rename to `collect-and-dispatch-map-updates`
- **draft-map-suggestions** | Medium | "Draft" is accurate but skill is not user-facing; triggers could lead users to invoke it directly | Add note: "Internal orchestration skill — do not invoke directly; use /analyze-agent-design or /analyze-skill-design instead"

**Low severity:**

- **review-agent-map / review-skill-map** | Low | "Review" implies read-only but skill modifies files by default unless `--no-update` is passed | Rename to `review-and-update-agent-map` / `review-and-update-skill-map` or clarify `--no-update` enables audit-only mode
- **align-harness-repos** | Low | Name implies multi-repo sync but skill validates a single repo surface | Rename to `validate-harness-neutrality`
- **audit-quality / audit-knowledge-quality** | Low | "Audit" implies read-only but both skills offer to apply fixes | Rename to `audit-and-fix-*` or separate audit from fix phases
- **projection-sync** | Low | "Sync" implies bidirectional; skill validates + regenerates + commits (unidirectional) | Rename to `validate-and-regenerate-projections`
- **discover-agent-design / discover-skill-design** | Low | "Discover" implies standalone exploration; both are mandatory sub-components of analyze-\* skills | Document as internal phases; add note in descriptions

### Structure

**Medium severity:**

- **plan-map-changes (tooling)** | Medium | `argument-hint` mixes required `--type` option with optional filter arguments without clear separation | Separate required from optional in argument-hint

**Low severity:**

- **naming-convention-lens** | Low | Missing code block language tags on bash examples | Add `bash` language tags
- **sync-documentation-maps agents (×4)** | Low | Missing code block language tags on bash commands in multiple steps | Add `bash` language tags
- All 19 tooling skills | Low | Widespread missing code block language tags (`text` instead of `bash`, `python`, `json`, `yaml`) | Apply correct language specifiers throughout

---

## Naming violations

- **plugin-health-discover (SKILL.md) intermediate output path** | Medium | `.dev/YYYY-MM-DD-plugin-health-lens-{name}.json` uses `-lens-` separator, `.json` extension, and `plugin-health` as surface identifier — violates `{dir}/YYYY-MM-DD-{surface}-{kind}.md` pattern | Change to `.dev/YYYY-MM-DD-plugin-{name}-findings.json` or consolidate into single findings file per surface
- All other agent and skill names | ✓ No violations | All names follow established conventions (`{design|quality}-{agent|skill}-lens-{aspect}`, `sync-documentation-maps-{object}-{verb}`, `{verb}-{object}[-aspect]`)

---

*Graph delta section omitted — tooling surface only.*
