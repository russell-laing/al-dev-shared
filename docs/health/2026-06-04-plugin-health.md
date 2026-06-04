# Plugin Health — 2026-06-04

Surface: distributed plugin (`profile-al-dev-shared/`) — 23 agents, 23 skills.
Dimensions: design + quality + naming. 22 lenses dispatched, 22 returned, 0 failed.
Suggestions only — no source files were edited.

> **Read this first.** Two large High blocks are lens-calibration noise, not work:
> the 23 "non-canonical model identifier" agent-structure hits flag the project's
> own `model: sonnet|haiku|opus` alias convention (the 2026-06-03 tooling sweep
> already confirmed the alias is the standard), and most of the 16 agent-bloat
> "section count > 6" hits are borderline. The genuine new signal this run is the
> **skill** quality coverage: the five skill quality lenses that hit the session
> limit on 2026-06-03 completed this time, surfacing skill clarity/bloat/structure
> findings for the first time.

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 0      | 44      | 0      | 44    |
| Medium   | 5      | 37      | 0      | 42    |
| Low      | 17     | 30      | 2      | 49    |

Counts above are raw lens output. The 44 Quality/High split as: 23 agent-structure
(model-alias false positives — see note), 16 agent-bloat (section-count, mostly
borderline), 1 agent-clarity (genuine), 4 skill-clarity (genuine, new coverage).

Top 5 ranked actions:

1. **Skill control-flow clarity — 4 genuine High (new coverage).** `al-dev-commit`
   (0.2.1 has no explicit proceed-without-ticket fallback), `al-dev-develop`
   (Phase 2 doesn't state whether file→partition mapping is 1:1), `al-dev-plan-preflight`
   (Phase 1 "sufficient context" has no minimum-specificity threshold), `al-dev-ticket`
   (Step 1 doesn't define precedence when both a numeric ID and search terms are
   supplied). These are the highest-value items — they were never surfaced before
   because the skill quality lenses failed last run. Fix the four conditionals.
2. **al-dev-solution-architect** — Highest-impact single agent (repeat from
   2026-06-03, still unfixed). High clarity (ambiguous "best existing analogue"
   disjunction) + High bloat (11 top-level sections, ~55-line Output Format).
   Add a matching rubric; move the Output Format schema guide to a knowledge file.
3. **al-dev-developer-tdd / -traditional + al-dev-diagnostics-fixer** — High agent
   bloat (9, 9 sections; an 84-line Fix Process block). Repeat from 2026-06-03.
   Consolidate sections and split the oversized block into named phases.
4. **Fix the agent-structure lens, not 23 agents** (Quality/structure, High ×23).
   The lens flags every agent's `model: sonnet|haiku|opus` and demands the full
   `claude-sonnet-4-6` form, but the alias IS the established convention. Teach the
   lens the alias is canonical so it stops emitting 23 false positives per sweep.
5. **Surface placement + shared-backbone drift** (Design/Medium). `al-dev-consolidate`
   scores all three misplacement signals (repeat from 2026-06-03 — Move to `.claude/skills/`);
   `al-dev-developer-traditional` and `al-dev-solution-architect` have divergent
   dispatch patterns across their callers (document canonical invocation in
   `knowledge/` to lock them).

## Design suggestions

### Medium

- **al-dev-consolidate** — Move (surface placement) | Scores all three misplacement
  signals: internal `.dev/` path references, self-audit/maintenance purpose, no
  spawned agents. Repeat from 2026-06-03. | Move to `.claude/skills/`.
- **al-dev-developer-traditional** — Connect (shared backbone) | Inconsistent dispatch
  across `/al-dev-develop` (detailed build-verify + compilation expectations),
  `/al-dev-fix` (minimal issue+fix, defers compile), and `/al-dev-review-develop`.
  Drift risk. | Document a canonical developer-traditional invocation in
  `knowledge/developer-invocation-patterns.md` with Full-Scope / Trivial-Fix /
  Code-Review variants; reference from all three sites.
- **al-dev-solution-architect** — Connect (shared backbone) | `/al-dev-plan` spawns
  2–3 architects in parallel for competitive debate; `/al-dev-fix` spawns one for a
  bounded 5-min analysis. Same agent, fundamentally different contracts. | Formalize
  both patterns in `knowledge/architect-invocation-patterns.md` (Competitive Debate
  vs Quick Analysis); make the pattern choice explicit at each dispatch site.
- **al-dev-interview** — Align | Agent Inputs table marks inline context "optional"
  but `/al-dev-interview` requires the dispatcher to pre-read a description or file
  path from `$ARGUMENTS` before spawning. | Document the dispatcher's pre-read
  responsibility in the agent Inputs table.
- **al-dev-support-researcher** — Align | Inputs table lists `TICKET_FILE` as
  conditional ("when available") but `/al-dev-support-reply` always provides it. |
  Mark `TICKET_FILE` required and document the always-provided contract + fallback.

### Low

- **Caller alignment — documentation clarity (6 Low):** `al-dev-release-notes-writer`
  (Outputs table omits the 7th `AMBIGUOUS` return field), `al-dev-developer-tdd` /
  `-traditional` (Inputs don't enumerate the inline module-scope/object-ID-range/prefix/
  symbol-evidence fields callers pass), `al-dev-al-pattern-reviewer` /
  `-security-reviewer` / `-performance-reviewer` (file list embedded in dispatch
  prompt not documented in Inputs). | Enumerate the inline dispatch fields in each
  Inputs/Outputs table. No blocking issues.
- **Surface placement (6 Low):** `al-dev-help`, `al-dev-plan-final-review`,
  `al-dev-plan-preflight`, `al-dev-plan-swarm-validate`, `al-dev-review-develop-preflight`,
  `verify-commits` each score two of three misplacement signals (internal paths +
  no agents). | Lower-confidence than `al-dev-consolidate`; several are deliberate
  preflight utilities consumed by distributed skills, so weigh against their role
  before moving.
- **al-dev-developer-tdd** — Connect | Minimal spec in `/al-dev-fix` vs full TDD-cycle
  structure in `/al-dev-develop`. | Add a TDD developer pattern to
  `knowledge/developer-invocation-patterns.md`.
- **al-dev-release-notes-writer** — Trim (tool hygiene) | `MCP: al-mcp-server`
  declared but used only aspirationally in the body. | Add a concrete MCP invocation
  example in the research phase, or remove the tool from frontmatter.
- **Handoff gaps (3 Low):** `al-dev-release-notes` output, `al-dev-consolidate`
  output, and the `al-dev-commit → al-dev-release-notes` step are terminal/implicit
  with no documented downstream consumer. | Optionally document each as a terminal
  step or add an explicit handoff note (low priority).

_Scope-isolation, model-fit, usage-patterns, complexity, near-duplicates, and
pre-planning lenses found no issues._

## Quality findings

### High — genuine

- **al-dev-solution-architect** (clarity) | "Best existing analogue" uses subjective
  language ("structural similarity", "similar pattern") with no objective match
  criteria. Repeat from 2026-06-03. | Add a rubric: (1) same business function,
  (2) same pattern type, (3) file:line evidence.
- **al-dev-commit** (skill clarity) | 0.2.1 "IF caller does not supply --ticket-id"
  has no explicit fallback after a Freshdesk-unreachable check. | State: proceed to
  Phase 1 without ticket context when unreachable.
- **al-dev-develop** (skill clarity) | Phase 2 lists four partition categories but
  never says whether files map 1:1 to partitions or may overlap. | Add: each
  developer owns exactly one partition; no shared files.
- **al-dev-plan-preflight** (skill clarity) | Phase 1 "sufficient context" gate has
  no minimum length/specificity threshold. | Define a concrete minimum (e.g. feature
  name ≥5 words AND one concrete workflow or BC object reference).
- **al-dev-ticket** (skill clarity) | Step 1 branches on numeric-ID vs search-terms
  but doesn't define precedence when both are supplied. | Add a precedence rule
  (first arg numeric / `FD\d+` ⇒ ticket ID, else search terms).

### High — agent bloat (mostly borderline; standouts first)

- **al-dev-solution-architect** | 11 top-level sections + ~10-step workflow. | Group
  into Research / Design / Implementation phases; move the schema guide to knowledge.
- **al-dev-diagnostics-fixer** | 84-line Fix Process block (lines 34–117). | Split
  into Parse / Classify / Fix / Delegate / Report phases.
- **al-dev-commit-agent-analysis** | 108-line Phase block (lines 41–149). | Split
  into discrete `##` phases.
- **al-dev-developer-tdd / -traditional** | 9 top-level sections each. | Merge
  Governance Tokens into Workflow or Standards.
- **al-dev-commit-hook-fixer** (74-line Procedure), **-lint-fixer** (49-line),
  **-execute** (44-line), **-ooxml-validator** (37-line), **-message-drafter**
  (32-line), **al-dev-docs-writer** (8 sections), **al-dev-release-notes-writer**
  (8 sections), **al-dev-script-engineer** (7), **al-dev-interview** (7),
  **al-dev-al-pattern-reviewer** (7), **al-dev-explore** (heading hierarchy). |
  Consolidate sections / split oversized blocks. Many are at-threshold; batch-fix
  during the next agent edit rather than as standalone work.

### High — agent structure (lens false positives, do not action as-is)

- **All 23 agents** (structure) | Lens flags `model: sonnet|haiku|opus` and wants
  `model: claude-sonnet-4-6` etc. The short alias is the established project
  convention (confirmed by the 2026-06-03 tooling sweep, which recommended
  standardizing _to_ the alias). | Fix the `quality-agent-lens-structure` lens to
  treat the alias as canonical. Do not rewrite 23 agent frontmatters.

### Medium

- **Skill clarity (25 Medium)** spanning `al-dev-commit` (advisory-mode definition),
  `al-dev-consolidate` (glob dialect), `al-dev-develop` (conflicting symbol providers;
  object-name char count), `al-dev-document` (audience boundaries; section spot-check
  criteria), `al-dev-fix` (TRIVIAL/NON-TRIVIAL vs four-tier mismatch; tdd/traditional
  routing undocumented), `al-dev-handoff` (overwrite behavior), `al-dev-interview`
  (missing-signal fallback), `al-dev-investigate` (target-mismatch decision; hypothesis
  agent count), `al-dev-lint` (al compile arg specifics), `al-dev-perf` (provider
  tie-break; full-content vs summary), `al-dev-plan-final-review` (validator success
  criteria), `al-dev-plan-preflight` (verified threshold definition), `al-dev-plan`
  ("meaningfully different" undefined), `al-dev-release-notes` (arg ordering),
  `al-dev-review-develop-preflight` (grep count semantics), `al-dev-review-develop`
  ("reading" the artifact defined), `al-dev-support-reply` (same-date tiebreak),
  `al-dev-ticket` (result limit), `commit-recover` (git log form), `verify-commits`
  (reset N calculation). | Each is a one-line specificity fix; address opportunistically.
- **Agent clarity (5 Medium):** `al-dev-developer-tdd` / `-traditional` ("logical
  group" boundary), `al-dev-commit-lint-fixer` (10% threshold rationale),
  `al-dev-interview` (USER_GATE syntax), `al-dev-release-notes-writer` ("architecture
  updates" criteria). | Tighten each qualifier.
- **Skill bloat (3 Medium):** `al-dev-fix` (duplicated Compilation Verification),
  `al-dev-plan-preflight` & `al-dev-plan` (duplicated PREFLIGHT_CONTEXT schema —
  extract to `knowledge/preflight-context-schema.md`), `al-dev-ticket` (dead
  "mode not set" branch in Phase 5). | Consolidate / remove dead branch.
- **Skill name-fit (2 Medium):** `al-dev-consolidate` (name implies merge; does
  session summarization), `al-dev-plan-swarm-validate` (name says "plan"; primarily
  validates). | Clarify descriptions or rename.
- **Skill description (1 Medium):** `al-dev-plan-swarm-validate` description verb
  "Generate plan" but the skill validates an existing plan. | Reconcile description.
- **Skill structure (1 Medium):** `al-dev-plan-final-review` missing `argument-hint`
  frontmatter field. | Add the field.

### Low

- **Skill structure (21 Low):** missing code-block language tags across most skills
  (`al-dev-consolidate`, `-develop`, `-document`, `-explore`, `-handoff`, `-interview`,
  `-investigate`, `-lint`, `-perf`, `-plan*`, `-release-notes`, `-review-develop*`,
  `-support-reply`, `-ticket`, `commit-recover`) plus two empty `argument-hint`
  values. | Batch-add language tags; a markdownlint pass covers most.
- **Agent clarity (3 Low):** `al-dev-support-reply-drafter` (findings parsing),
  `al-dev-commit-hook-fixer` (manual-review boundary), `al-dev-explore` (out-of-scope
  else-clause). | Polish.
- **Skill bloat (2 Low):** `al-dev-commit` (historical lint-ownership commentary),
  `al-dev-interview` (misleading "Phase 1" label for optional pre-work). | Trim.
- **Skill clarity (3 Low):** `al-dev-explore` (external Steps A–D not inlined),
  `al-dev-help` (glob root unspecified), `al-dev-plan-swarm-validate` (description
  vs validation-only). | Polish.

_Agent description-drift and agent name-fit lenses found no issues._

## Naming violations

- **commit-recover** | Low | Skill name doesn't follow `{verb}-{object}-{aspect}`
  and isn't in the grandfathered list. | Rename (e.g. `recover-commits-integrity`)
  or add to the grandfathered exceptions.
- **verify-commits** | Low | Same — doesn't follow the pattern and isn't grandfathered. |
  Rename (e.g. `verify-commits-atomicity`) or grandfather.

No High or Medium naming findings. All agent filenames follow `al-dev-{role}`. No
output-path violations.

## Graph deltas

_Refreshed via `scripts/generate-plugin-graph.py` (see below). Four agents remain
orphaned in the catalog (`al-dev-code-review`, `al-dev-docs-writer`, `al-dev-explore`,
`al-dev-script-engineer` — no spawning skill); these are documented standalone/utility
agents, not broken links. `al-dev-consolidate` flagged for surface-placement Move
(see Design) — misplaced content, not a dead link._
