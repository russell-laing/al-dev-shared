# Plugin Health — 2026-05-29

> Surface: `profile-al-dev-shared/` — 21 skills, 20 agents  
> Lenses: 10 design + 10 quality + 1 naming = 21 dispatched, 21 returned  
> No auto-edits made. Review and run `/plan-map-changes` on accepted items.

---

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 7      | 33      | 0      | 40    |
| Medium   | 12     | 22      | 0      | 34    |
| Low      | 4      | 14      | 0      | 18    |

**Top 5 ranked actions:**

1. **Remodel (Agents)** — 5 agents show the wrong model in their actual files despite the map claiming a haiku downgrade on 2026-05-27: `al-dev-code-review`, `al-dev-expert-reviewer`, `al-dev-performance-reviewer`, `al-dev-security-reviewer` all read `model: claude-sonnet-4-6`; `al-dev-commit-preflight` reads `model: sonnet`. Map-to-file mismatch; downgrade to `claude-haiku-4-5-20251001`.
2. **Bloat + Connect (Skills)** — `al-dev-develop` and `al-dev-review-develop` each inline the three-reviewer dispatch template (the latter 3× verbatim). Six skills total (commit, consolidate, develop, plan, review-develop, ticket) have High bloat. Extract reviewer template to `knowledge/review-panel-invocation-pattern.md` as first move.
3. **Structure (Agents)** — 4 agents have a spurious `name:` frontmatter field (`commit-preflight`, `commit-recover-verifier`, `support-reply-drafter`, `support-researcher`); most agents use short model aliases instead of canonical IDs; `al-dev-interview` uses `USER_GATE` (non-canonical; should be `AskUserQuestion`); several use `mcp:` prefix (non-canonical; should be `mcp__`).
4. **Clarity (Agents)** — `al-dev-commit-preflight` has 3 High operational gaps (incomplete baseline-capture code block, undeclared `perl` dependency, misplaced regex caution note). `al-dev-solution-architect` has 3 High issues (`$AL_DEV_SHARED_PLUGIN_ROOT` undefined at agent runtime, missing SIMPLE-tier gate, undefined "Pattern reference" term).
5. **Align (Maps)** — `al-dev-commit-preflight` agent file exists and is dispatched at `/al-dev-commit` Step 9.5 but is **absent from the agent catalog table** in `docs/al-dev-agent-map.md`; `al-dev-diagram-generator` skill exists but has **no section** in `docs/al-dev-plugin-map.md`. Both maps are stale for these additions.

*Lenses with no findings: `naming-convention-lens`, `design-skill-lens-near-duplicates`, `design-skill-lens-preplanning`, `design-agent-lens-usage-patterns`.*

---

## Design suggestions

### Remodel

- **al-dev-code-review** | High | File reads `model: claude-sonnet-4-6` (line 7); single-pass parallel read-only review — no multi-file synthesis required. Map claims haiku downgrade applied 2026-05-27 but file was never updated. | Set `model: claude-haiku-4-5-20251001`
- **al-dev-expert-reviewer** | High | File reads `model: claude-sonnet-4-6` (line 7); parallel single-file AL pattern checklist. Same map-vs-file mismatch. | Set `model: claude-haiku-4-5-20251001`
- **al-dev-performance-reviewer** | High | File reads `model: claude-sonnet-4-6` (line 6); parallel single-file N+1 and query-efficiency pattern matching. Same map-vs-file mismatch. | Set `model: claude-haiku-4-5-20251001`
- **al-dev-security-reviewer** | High | File reads `model: claude-sonnet-4-6` (line 6); parallel single-file security vulnerability checklist. Same map-vs-file mismatch. | Set `model: claude-haiku-4-5-20251001`
- **al-dev-commit-preflight** | High | File reads `model: sonnet`; task is mechanical lint/validation (ruff, whitespace, ZIP integrity check) — no multi-file reasoning required. | Set `model: claude-haiku-4-5-20251001`

### Split

- **al-dev-commit-preflight** | Medium | Two separable validation concerns with independent failure modes: (1) Python lint and trailing-whitespace fixing; (2) OOXML ZIP validation. These could fail independently and have different recovery paths. | Consider splitting into `al-dev-commit-lint-fixer` and `al-dev-commit-ooxml-validator`; lower-priority given the agent is still new

### Align (Caller alignment)

- **al-dev-ticket-agent** | High | Inputs table omits the required `Phase` parameter that `/al-dev-ticket` passes in every dispatch (`fetch` or `download-attachments`); agent workflow branches on this value but Inputs never documents it | Add `Phase | string | Required | "fetch" or "download-attachments" — determines workflow branch` to Inputs table
- **al-dev-commit-agent-execute** | Medium | Inputs table documents `APPROVED_PLAN` as required but omits schema; caller passes structured `GROUP_N` blocks with `files` and `message` subfields | Document APPROVED_PLAN block schema in Inputs table
- **al-dev-commit-message-drafter** | Medium | Inputs table shows `MANIFESTS` as required but omits schema (per-file structure: `object_id`, `change_type`, `fields_added/removed`, `procs_added/modified/removed`) | Document MANIFESTS block schema in Inputs table
- **al-dev-commit-preflight** | Medium | Same APPROVED_PLAN schema gap as commit-agent-execute; dispatched at Step 9.5 with the same structured plan block | Add APPROVED_PLAN schema to Inputs table
- **al-dev-support-researcher** | Medium | Outputs section says return block goes "to /al-dev-support" but the dispatching skill is `/al-dev-ticket`; `/al-dev-support` is a deprecated alias | Update caller reference to `/al-dev-ticket (--mode=full, Phase 6)`
- **Three reviewer agents** (expert, security, performance) | Low | Inputs table documents `AL files to review` but not the format (one file path per line) or the implementation-context block structure passed from Phase 4 handoff | Add format note and context-block structure to each reviewer's Inputs table

### Connect / Promote (Shared backbone)

- **Three-reviewer dispatch template** | Medium | Both `/al-dev-develop` (Phase 6–7) and `/al-dev-review-develop` (Phase 6–7) inline the same reviewer dispatch prompt template; `/al-dev-review-develop` repeats it 3× with only the specialist label changing. `knowledge/review-panel-pattern.md` exists but skills do not reference it for the dispatch template itself. | Canonicalise reviewer spawn template in `knowledge/review-panel-invocation-pattern.md` (create or expand the existing pattern file); both skills reference instead of inlining
- **Developer invocation shapes** | Medium | `/al-dev-fix` spawns `al-dev-developer` with a terse directive (minimal context); `/al-dev-develop` spawns it with full onboarding including symbol-preflight gate and scope rules. Same agent, two structurally different invocation shapes with no canonical distinction documented. | Add both shapes to `knowledge/developer-invocation-patterns.md` (analogous to existing `architect-invocation-patterns.md`)
- **Solution architect quick-analysis pattern** | Low | Two invocation shapes (competitive debate in `/al-dev-plan`, quick-analysis in `/al-dev-fix`) are partially in `knowledge/architect-invocation-patterns.md` but the quick-analysis shape lacks model-selection rules | Add model-selection table: SIMPLE → sonnet override, MEDIUM/COMPLEX → opus default

### Atomise (Complexity)

- **al-dev-review-develop** | Medium | 6 phases with two separable concern clusters: compile/staging (Phases 5, 8, 8.5) and review dispatch/synthesis (Phases 6–7, 9–10). Different failure modes; staging could be a gate independent of review. | Consider extracting review/synthesis phases into a separate invocation; the compile/staging phases become a self-contained pre-review gate
- **al-dev-consolidate** | Medium | 5 phases: discovery/grouping (Phases 0–1) and extraction/writing/indexing (Phases 2–4). First cluster is classifying; second is producing. | Consider whether Phase 0–1 output could serve as standalone inventory; if not, accept as reasonable utility skill structure

### Absorb (Complexity outliers)

- **verify-commits** | Low | Zero-agent, 4 steps; overlaps substantially with `/al-dev-commit` Step 8 scope verification; the entire workflow (count + compare + optional re-split) could become an optional `--verify` post-commit flag | Consider absorbing into al-dev-commit Phase 11 as optional verification step
- **plan-with-critic-swarm** | Low | 4-phase skill that wraps plan generation + 6-critic red-team; overlaps with `/al-dev-plan` Phase 2 competitive debate. More value as `--critics` mode than standalone skill. | Consider as optional mode of `/al-dev-plan`; reduces user decision fatigue

### Extend (Handoff gaps)

- **Post-commit deployment gap** | Medium | The chain `investigate → plan → develop → review-develop → commit` is well-established and ends at commit. No skill orchestrates deploy/tag/promote workflows. `al-dev-release-notes` exists but is manually triggered. Previously identified as `/al-dev-publish` opportunity. | See `knowledge/publish-workflow-opportunity.md`; deferred pending standardized publishing targets
- **Documentation handoff** | Low | `al-dev-document` produces `docs/*` artifacts but no downstream skill formally consumes them; treated as parallel output | Mark explicitly as parallel-only in Layer 1 diagram or add an optional post-commit step
- **Performance analysis gate** | Low | `al-dev-perf` output is advisory only; `al-dev-review-develop` does not check for perf findings or gate on CRITICAL items | Optionally add perf-analysis check to Phase 5 pre-review loading step

### Align (Map staleness)

- **al-dev-commit-preflight missing from agent map** | High | Agent file `profile-al-dev-shared/agents/al-dev-commit-preflight.md` exists and is dispatched at `/al-dev-commit` Step 9.5; absent from `docs/al-dev-agent-map.md` catalog table (only mentioned in Observations) | Add catalog row; run `/review-agent-map`
- **al-dev-diagram-generator missing from plugin map** | Medium | Skill file `profile-al-dev-shared/skills/al-dev-diagram-generator/SKILL.md` exists but has no section in `docs/al-dev-plugin-map.md`; plugin map header still says 19 distributed skills | Add `/al-dev-diagram-generator` section; update count; run `/review-skill-map`

---

## Quality findings

### Agent quality

**Clarity — High**

- **al-dev-commit-preflight** | High | Three operational issues: (1) Step 1 baseline-capture uses `wc -l < "$f"` without surrounding pipeline — not runnable as shown; (2) `perl -pi -e 's/[ \t]+$//'` used but `perl` undeclared as dependency — replace with `sed`; (3) regex safety note appears *after* the code block it applies to — restructure as a constraint *before* the block | Fix all three; agents/al-dev-commit-preflight.md lines 31–55
- **al-dev-solution-architect** | High | Three issues: (1) Bash block references `$AL_DEV_SHARED_PLUGIN_ROOT` undefined at agent runtime — replace with `find ~ -name md-mermaid-helper.md -type f | head -1`; (2) "SIMPLE features: Skip research" gate has no active classification verification before skipping; (3) "Pattern reference" term used in Step 4 without cross-reference definition | Fix all three
- **al-dev-developer** | High | TDD vs traditional workflow selection has no active gate — workflow branches on `.dev/*-al-dev-test-test-plan.md` existence but no pre-implementation confirmation step | Add explicit pre-implementation workflow-selection gate
- **al-dev-interview** | High | "If no file specified, creates new interview notes" — default filename and location unspecified in the body | Specify: `.dev/YYYY-MM-DD-al-dev-interview-requirements.md`
- **al-dev-commit-agent-execute** | High | "message from approved plan" referenced in Step 1 but APPROVED_PLAN structure never documented in agent body; agent cannot reliably parse what it receives | Document expected block structure in Inputs table and body
- **al-dev-diagnostics-fixer** | High | Step 3a "mark unresolved" — output format and location completely unspecified (report file? separate issue file?) | Specify: append to dated lint-report file under `## Unresolved` section
- **al-dev-support-reply-drafter** | High | Step 1.5 subjective-opinion handling has prose guidance but no if/else structure — unclear when it applies vs normal reply flow | Restructure as: "IF subjective opinion found THEN [steps 1–4] ELSE proceed to Step 2"
- **al-dev-ticket-agent** | High | Step 1.5 detects both `src=` and `cid:` inline images but output format does not specify whether these are combined or listed separately | Clarify: combined list with source-type labels (`src=` URL vs `cid:` reference)

**Clarity — Medium (selected)**

- **al-dev-commit-agent-analysis** | Medium | Non-AL file handling: "emit a simple one-liner" — format and output location unspecified
- **al-dev-commit-agent-execute** | Medium | "if scripted fix available" in hook retry — no enumeration of which hook failures are auto-fixable
- **al-dev-commit-message-drafter** | Medium | "Mechanical changes" (WHY omission trigger) subjectively defined — boundary unclear
- **al-dev-commit-recover-verifier** | Medium | Fallback trigger conditions undefined: when should Fallback 2 trigger vs Fallback 3?
- **al-dev-release-notes-writer** | Medium | "short hash if VERSION omitted" — hash length unspecified (7 chars?)
- **al-dev-script-engineer** | Medium | "Default to Python" conflicts with "use language best suited to stack" — no tie-breaker for ambiguous stack

**Structure — High**

- **Non-canonical model IDs** | High | Many agents use short aliases (`model: haiku`, `model: sonnet`, `model: opus`) instead of full canonical IDs; aliases may cause projection failures across harnesses | Normalize to: `claude-haiku-4-5-20251001`, `claude-sonnet-4-6`, `claude-opus-4-8`
- **Spurious `name:` field in 4 agents** | High | `al-dev-commit-preflight`, `al-dev-commit-recover-verifier`, `al-dev-support-reply-drafter`, `al-dev-support-researcher` all have `name:` in frontmatter — this is a skill-only field; agents use filename for identity | Remove `name:` from all four agent frontmatters
- **Non-canonical tool names** | High | `al-dev-interview` declares `USER_GATE` (should be `AskUserQuestion`); `al-dev-release-notes-writer`, `al-dev-solution-architect`, `al-dev-support-researcher` use `mcp:` prefix (should be `mcp__`) | Normalize all tool declarations

**Bloat — High**

- **al-dev-solution-architect** | High | "Workflow" section spans 65 lines with 10+ substeps — severely oversized | Split into Pre-research, Research Phase, Design Phase, Implementation Planning, Output Generation sections
- **al-dev-developer** | High | "Standards" section spans 65 lines; compilation guidance appears 3× (lines ~87, ~90–105, error-handling section) | Extract compilation guidance as `## Governance Gates`; reference once
- **Three reviewer agents (expert, security, performance)** | Medium | Each inlines verbatim severity classification blocks and output-format templates — same content repeated across three files | Extract to `knowledge/review-severity-framework.md`; replace with single-line reference in each agent

**Description drift — Medium**

- **al-dev-commit-message-drafter** | Medium | Description says "drafts commit messages" but primary output is `PROPOSED_GROUPS` block (group proposals with messages) and `DELETIONS` block — neither mentioned | Update: "proposes atomic commit groups, drafts commit messages, outputs PROPOSED_GROUPS and DELETIONS blocks"
- **al-dev-commit-preflight** | Medium | Description omits line-count corruption detection (Step 1 explicitly detects post-lint line-count changes as a corruption indicator) | Add corruption-detection to description
- **al-dev-ticket-agent** | Low | Description says "download attachments" but body states "Attachments are referenced by URL only (not downloaded by default)" — contradiction | Fix: "detect and list inline image attachments; attachments referenced by URL only"

**Name fit — Medium**

- **al-dev-commit-recover-verifier** | Medium | Name foregrounds "verifier" but primary mission is multi-strategy recovery execution; verification is incidental | Rename to `al-dev-commit-recover`
- **al-dev-ticket-agent** | Medium | "agent" suffix is generic and redundant — specific action is Freshdesk ticket fetching | Rename to `al-dev-ticket-fetcher`

---

### Skill quality

**Clarity — High**

- **al-dev-develop** | High | Developer spawn prompt (Phase 3) references `knowledge/scope-expansion-gate.md` without inline summary; developer agent cannot execute the gate without reading a separate file mid-dispatch | Include gate decision-tree summary in spawn prompt or add explicit read-first instruction
- **al-dev-develop** | High | Phase 1.5 (`--autonomous`) is described but no explicit standard-mode path is stated from Phase 1 → Phase 2 | Add: "In standard mode, Phase 1 proceeds directly to Phase 2; Phase 1.5 is skipped entirely"
- **al-dev-investigate** | High | Step 4 agent-count rule conflicts: section header says "spawn 2–3 agents" but prose says "spawn ×2 in parallel" for 3–4 hypotheses | Fix: "For 3–4 hypotheses: 2 agents (split evenly). For 5+ hypotheses: 3 agents"
- **al-dev-plan** | High | Phase 1 Input Validation Gate requires "at least one functional requirement" but no operationalization for detecting requirements from free-form text | Add: "Sufficient context = ≥2 independent sentences: one names what to build, one describes a user-facing behavior or constraint"
- **al-dev-review-develop** | High | Phase 6–7 dispatch prompt template applies to all three reviewers identically — no differentiation per specialty | Add per-reviewer focus sentence: security ("Review for permissions/data-exposure"), expert ("Review for AL conventions/naming"), performance ("Review for N+1/query-efficiency")
- **al-dev-ticket** | High | Step 1.5 search uses `curl -f` but no error handling specified for HTTP failure | Add: "If curl fails, tell user 'Search unavailable' and ask for explicit ticket number"
- **al-dev-document** | High | VERIFICATION block required before presenting to user; if any row shows `no`, escalation path completely unspecified | Add: "If any verification row is `no`, return to docs-writer; iterate until all rows show `yes`; do not present incomplete output"
- **al-dev-fix** | High | Step 2 and Step 3 both perform scope check via `git status` but decision trees differ subtly (Step 3 adds "confirmed root-cause scope" qualifier); subtle divergence creates confusion | Unify into a single scope-check rule; state explicitly that Step 3's boundary is the architect-approved scope
- **al-dev-commit** | High | Step 5 references `$AL_DEV_SHARED_PLUGIN_ROOT` without prior definition or harness-context statement | Add environment variable definitions at skill start
- **al-dev-interview** | High | Phase 2 gate requires explicit "INTERVIEW COMPLETE" signal but "explicit" is undefined | Clarify: literal string "INTERVIEW COMPLETE" as a standalone line before Phase 3

**Clarity — Medium (selected)**

- **al-dev-fix** | Medium | "TRIVIAL (90% of fixes)" classification threshold vague | Add: "TRIVIAL = visible in ≤1 file, fix ≤5 lines, no conditional logic, obvious root cause from symptom"
- **al-dev-consolidate** | Medium | "Group files sharing the same session date" — operationalization incomplete when variant suffixes (option-a, option-b) exist on same base date
- **al-dev-plan** | Medium | Phase 3 "Push architects to think deeper" — no timeout or stop condition for the debate | Add: "Debate until each architect responds to ≥1 critique, or 5 min elapsed; then proceed to Phase 4"
- **al-dev-release-notes** | Medium | `version` parameter "short form of `end_hash`" — hash length unspecified | Add: "Short form = first 7 characters (standard git convention)"
- **al-dev-review-develop** | Medium | Phase 9 "read the file back" — ambiguous: parse content or just confirm existence? | Clarify: "Read via Read tool; parse Verdict section for BLOCKING/READY status"
- **verify-commits** | Medium | "Verify commits match plan's approved groups" — plan file path/section not specified | Add: "Read `.dev/*-al-dev-plan-solution-plan.md` (latest) and extract PROPOSED_GROUPS section"

**Structure — High**

- **al-dev-diagram-generator** | High | `argument-hint` brackets `--caller-name <skill-name>` as optional but body (Phase 4) cannot proceed without it — required parameter must not be bracketed | Remove brackets: `argument-hint: "--caller-name <skill-name>"`

**Structure — Medium**

- **al-dev-support** | Medium | Deprecated alias skill has an active `argument-hint` referencing deprecated syntax; frontmatter should make legacy-only status unambiguous | Update or remove argument-hint from deprecated skill frontmatter

**Structure — Low** (many)

- Missing `bash` / `text` language tags on code blocks across: al-dev-explore, al-dev-fix, al-dev-handoff, al-dev-help, al-dev-interview, al-dev-investigate, al-dev-lint, al-dev-perf, al-dev-plan, al-dev-release-notes, al-dev-review-develop, commit-recover, plan-with-critic-swarm, verify-commits

**Bloat — High**

- **al-dev-develop** | High | 480+ lines total; symbol-preflight gate appears twice in near-identical form (Phase 1.5 and Phase 3 spawn prompt) | Extract to canonical reference; Phase 3 spawn prompt references Phase 1.5 gate by name rather than reinlining it
- **al-dev-review-develop** | High | Phase 6–7 inlines reviewer dispatch template 3× (once per reviewer specialist) with only the focus label changing; 260+ lines total | Extract single template with specialist-label substitution; reduce to 3 short parametrized invocations
- **al-dev-commit** | High | 11 top-level steps; context-assembly and dispatch patterns repeated across Steps 6–7a and 10 | Extract shared dispatch template once; reference in each phase that uses it
- **al-dev-plan** | High | Phase 1 repeats the "load optional artifact" pattern 5× (requirements, explore findings, perf analysis, project context, session log) with near-identical structure each time | Extract a single canonical artifact-loading block; reference per artifact type
- **al-dev-consolidate** | High | Phases 2–4 span 170+ lines with bash extraction patterns repeated and re-explained per group (A, B, C, D) | `knowledge/consolidate-extraction-patterns.md` already exists — confirm skills reference it instead of inlining
- **al-dev-ticket** | High | Steps 1–1.5 span 30+ lines with 4 nested conditional branches; Phases 5–8 repeat agent dispatch patterns from the support flow | Consolidate branching into sequential flow; extract dispatch patterns to reusable reference

**Description drift — Medium**

- **al-dev-document** | Medium | RTM generation (parse REQ: tokens, add inline references, append traceability table) is a mandatory deliverable per the body but is absent from the description | Add: "Generates requirement traceability (RTM) table mapping implementation to source requirements"

**Name fit — High**

- **al-dev-support** | High | Name implies active skill but body states "DEPRECATED ALIAS — use /al-dev-ticket --mode=full instead"; invoking the skill redirects users to a different skill | Remove from active registry or retitle `al-dev-support-deprecated`; current name actively misleads

**Name fit — Medium**

- **al-dev-diagram-generator** | Medium | Name implies general-purpose diagram generation; body is plugin-architecture-only (generates skill/agent/knowledge relationship diagrams for maintainer tools, not domain diagrams) | Rename to `al-dev-plugin-diagram` or add explicit scope restriction to description
- **plan-with-critic-swarm** | Medium | Name implies standalone planner; body is a post-plan refinement step (requires existing plan draft, runs 6-critic red-team) | Clarify in description: "Refinement step for an existing plan draft — not a standalone planner. Use `/al-dev-plan` to produce the initial plan first."

---

## Naming violations

_No issues found._

---

## Graph deltas

Graph refreshed: `docs/al-dev-plugin-graph.md` updated 2026-05-29.

**Orphan agents** (no incoming spawn edge in graph):

| Agent | Status |
|-------|--------|
| `al-dev-code-review` | Confirmed unspawned — no caller in any skill |
| `al-dev-script-engineer` | Confirmed unspawned — no caller in any skill |
| `al-dev-docs-writer` | Prose reference only in al-dev-document; no formal Agent() spawn call |
| `al-dev-diagnostics-fixer` | Graph parser miss — IS dispatched by `/al-dev-lint` Step 2; not a true orphan |
| `al-dev-explore` (agent) | Confirmed — `/al-dev-explore` skill uses built-in Explore subagent type, not this file |
| `al-dev-interview` (agent) | Graph parser miss — IS dispatched by `/al-dev-interview` skill; not a true orphan |

**Dead knowledge** (16 files referenced by nothing in graph):

Notable unlinked files:
- `review-panel-pattern.md` — documented in agent map Observations as the canonical reviewer pattern; no skill currently references it despite this being the intended single source of truth
- `commit-conventions.md` — referenced in CLAUDE.md and the map header but not in any distributed skill
- `harness-concepts.md` — referenced in CLAUDE.md only; no skill uses it
- `anti-patterns.md`, `quality-checklist.md`, `rubber-duck.md` — documentation artifacts; no skill references

Maintainer-tooling knowledge files (expected unlinked; not distributed to consuming harnesses):
`agent-tool-projection-policy.md`, `lens-invocation-patterns.md`, `map-change-rubber-duck-checks.md`, `publish-workflow-opportunity.md`, `proportional-planning.md`, `session-analysis-report-format.md`, `skill-test-format.md`, `verification-and-planning.md`, `feedback-resolution.md`

**Off-path skills** (not on any named workflow path — 15 total):

All are expected. These are utility/optional/post-commit skills not part of the main development spine: `al-dev-consolidate`, `al-dev-diagram-generator`, `al-dev-document`, `al-dev-explore`, `al-dev-handoff`, `al-dev-help`, `al-dev-interview`, `al-dev-lint`, `al-dev-perf`, `al-dev-release-notes`, `al-dev-review-develop`, `al-dev-support`, `commit-recover`, `plan-with-critic-swarm`, `verify-commits`.

**Missing refs:** None — all referenced knowledge files exist on disk.
