# Plugin Health — 2026-06-05

Surface: `profile-al-dev-shared/` (23 agents, 23 skills). 22 lenses dispatched.
Source findings: `docs/health/2026-06-05-plugin-findings.md`.

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 0      | 10      | 0      | 10    |
| Medium   | 6      | 31      | 0      | 37    |
| Low      | 3      | 17      | 0      | 20    |

New this sweep: ~22 (notably the 5 agent-bloat High findings — the agent-bloat
lens reported "no issues" on 2026-06-04 against unchanged files, so this is lens
variance, not regression) · Recurring from prior sweeps: ~45 (annotated inline) ·
Stale (dropped): 3 · Suppressed (dispositioned): 1

Failed lenses: none — all 22 returned.

Top 5 ranked actions:

1. **Trim shared developer-agent bloat (Connect + Trim).** `al-dev-developer-tdd`
   and `al-dev-developer-traditional` (both High bloat) duplicate their AL coding
   standards / code-pattern sections nearly verbatim. Extract the shared standards to
   `knowledge/al-developer-patterns.md` and reference from both. Pairs with the
   shared-backbone finding to canonicalize the dispatch template in `knowledge/`.
2. **Trim `al-dev-solution-architect` (High bloat).** 130-line workflow section, 7
   top-level sections, repeated MCP-tool guidance. Move MCP guidance + pattern-evidence
   hierarchy to a knowledge reference; reduce to ~5 sections.
3. **Trim `al-dev-interview` and `al-dev-commit-hook-fixer` (High bloat).** Extract the
   interview question categories to `knowledge/interview-question-bank.md`; move the
   hook-fixer Failure Classification table + Approved Fixes to
   `knowledge/commit-hook-recovery-patterns.md`.
4. **Close High skill-clarity incomplete conditionals.** `al-dev-lint` (no fallback if
   neither `al-compile` nor `al compile` is present), `al-dev-fix` (ambiguous
   `MEDIUM or COMPLEX` branch), `al-dev-interview` (no else clause on the INTERVIEW
   COMPLETE gate). All three change observable behavior. *(open since 2026-06-04 for
   interview)*
5. **Close High skill-clarity undefined placeholders.** `al-dev-develop` (undefined
   `<src-file>` and unexplained `-nt`), `al-dev-plan-preflight` ("substantive answer"
   undefined). *(both open since 2026-06-04)*

## Design suggestions

**Medium**

- **Split — `al-dev-support-reply-drafter`** (scope-isolation) | Agent owns two
  concerns: drafting the customer-facing reply *and* writing the internal technical
  findings to the same `.dev/` file. | Optionally separate internal findings
  documentation from customer reply drafting (new `al-dev-support-findings-documenter`).
  *Note: a model-fit downgrade on this same agent is `declined` — see Dispositioned.*
- **Connect — `al-dev-developer-tdd`** (shared-backbone) | `/al-dev-develop` and
  `/al-dev-fix` both spawn it with the same test-plan-routing structure. | Extract the
  routing decision + TDD spawn template to `knowledge/developer-test-plan-dispatch-pattern.md`.
  *(open since 2026-06-04)*
- **Connect — `al-dev-developer-traditional`** (shared-backbone) | Same duplicated
  dispatch structure across the two skills. | Expand
  `knowledge/developer-invocation-patterns.md` to document both context variations under
  one canonical dispatch. *(open since 2026-06-04)*
- **Align — `al-dev-commit-agent-analysis`** (caller-alignment) | Inputs table marks
  `REPO` required, but `knowledge/commit-dispatch-template.md` never passes it; agent
  uses `git -C "$REPO"`. | Document REPO as "inferred from working directory", or add it
  to the dispatch preamble.
- **Extend — post-commit orchestration** (handoff-gaps) | The dev chain ends at
  `al-dev-commit`; `commits.json` / `hook-failures.json` have no downstream consumer. |
  Consider an `al-dev-deploy`/release-readiness skill consuming commit outputs.
  *(open since 2026-06-04)*
- **Move — `al-dev-consolidate`** (surface-placement) | No spawned agents; references
  internal `.dev/sessions/` and `profile-al-dev-shared/` paths that only resolve inside
  this repo's plugin ecosystem. | Candidate to move to `.claude/skills/`.

**Low**

- **Align — `al-dev-developer-tdd` / `-traditional`** | Inputs tables under-specify the
  inline context fields. | Add a "Context Fields" row referencing
  `knowledge/al-dev-develop-spawn-prompt.md`. *(open since 2026-06-04)*
- **Extend — `al-dev-fix` test-plan** | `.dev/test-plan.md` is produced but never read. |
  Have `/al-dev-develop` consume it to route to the TDD developer.
- **Extend — `al-dev-consolidate` session index** | `.dev/sessions/sessions-index.md`
  has no downstream consumer. | Optional vault-integration / publishing chain.

*Tool-hygiene, usage-patterns, complexity, near-duplicates, and preplanning lenses:
no issues found.*

## Quality findings

**High — Bloat (agents)**

- `al-dev-solution-architect` — 130-line workflow, 7 sections, repeated MCP guidance.
- `al-dev-interview` — 90-line interview-process section with nested categories.
- `al-dev-developer-tdd` — 144 lines; AL code patterns duplicate `-traditional` verbatim.
- `al-dev-developer-traditional` — 126 lines; Standards section 56 lines; duplicates `-tdd`.
- `al-dev-commit-hook-fixer` — 74-line procedure section, nested Steps 1–5.

  *Fixes converge on `knowledge/al-developer-patterns.md` (shared AL standards),
  `knowledge/interview-question-bank.md`, and `knowledge/commit-hook-recovery-patterns.md`.*

**High — Prompt clarity (skills)** *(incomplete conditionals / undefined placeholders
that change observable behavior)*

- `al-dev-develop` — undefined `<src-file>` placeholder; `-nt` operator unexplained.
- `al-dev-fix` — `IF complexity == 'medium' or 'complex'` ambiguous; split into branches.
- `al-dev-interview` — INTERVIEW COMPLETE gate has no else clause. *(open since 2026-06-04)*
- `al-dev-lint` — no fallback if neither `al-compile` nor `al compile` is available.
- `al-dev-plan-preflight` — "substantive answer" undefined. *(open since 2026-06-04)*

**Medium (by class — see findings file for full lines)**

- *Agent bloat (6):* `al-dev-commit-lint-fixer`, `al-dev-release-notes-writer`
  (also has an unclosed code fence), `al-dev-commit-agent-analysis`, `al-dev-script-engineer`,
  `al-dev-support-researcher`, `al-dev-diagnostics-fixer`.
- *Agent clarity (8):* `al-dev-solution-architect` ⚠ *"best existing analogue" partially
  addressed by `6de8bfd` — residual: add yes/no verdict examples*; `al-dev-solution-architect`
  (TESTABILITY_COMPLETE criteria); `al-dev-commit-lint-fixer` (move sed warning before block);
  `al-dev-developer-tdd` / `-traditional` ("latest" glob tie-break undefined);
  `al-dev-explore` ("largest file count" undefined); `al-dev-support-reply-drafter`
  (link-marker placement); `al-dev-commit-recover-fixer` (fallback strategies undefined).
- *Agent name-fit (2):* `al-dev-code-review` (too generic vs specialist reviewers →
  `al-dev-general-code-reviewer`); `al-dev-ticket-agent` (→ `al-dev-ticket-context-writer`).
- *Skill clarity (9):* `al-dev-consolidate`, `al-dev-document`, `al-dev-help`, `al-dev-perf`,
  `al-dev-plan`, `al-dev-release-notes`, `al-dev-review-develop`, `al-dev-ticket`
  (URL-encoding example), `commit-recover` ("verified" undefined). *(several open since 2026-06-04)*
- *Skill description (5):* `al-dev-consolidate`, `al-dev-develop` (Phase 4 handoff content),
  `al-dev-explore` ("delegates" misleading), `al-dev-plan-final-review` (validator-fail path),
  `al-dev-support-reply` (REPLY block vs `.dev/ticket-reply.md`). *(open since 2026-06-04)*
- *Skill structure (1):* `al-dev-support-reply` `argument-hint` contradicts the two usage modes.

**Low (counts — see findings file)**

- Agent name-fit: 2 (`al-dev-commit-agent-analysis` → `-analyzer`,
  `al-dev-commit-agent-execute` → `-executor`).
- Agent structure: 3 (`al-dev-explore`, `al-dev-commit-agent-analysis`,
  `al-dev-release-notes-writer` — code-fence / step-numbering).
- Skill bloat: 1 (`al-dev-develop` partition-table preamble).
- Skill clarity: 4 (`al-dev-commit`, `al-dev-handoff`, `al-dev-plan-swarm-validate`,
  `verify-commits`).
- Skill structure: 7 (missing `bash` language tags — `al-dev-lint`, `al-dev-perf`,
  `al-dev-plan-swarm-validate`, `al-dev-review-develop-preflight`, `al-dev-ticket`,
  `commit-recover`, `verify-commits`). *(language-tag class open since 2026-06-04)*

*Agent description-drift and skill name-fit lenses: no issues found.*

## Naming violations

*No issues found.* (The 2026-06-04 `al-dev-commit-recover-fixer` literal-date finding
did not recur — lens reported clean against the live file.)

## Graph deltas

See refreshed `docs/al-dev-plugin-graph.md` (regenerated this sweep).

## Stale (dropped — fixed items re-flagged; verified against live files 2026-06-05)

- `al-dev-ticket` clarity "first token decides" (was High) — live file has explicit
  `^(FD-?)?[0-9]+$` regex + IF/THEN (fixed `966d81b`); claim no longer holds.
- `al-dev-commit` skill-bloat "repetitive dispatch blocks" (was Medium) — live file cites
  `knowledge/commit-dispatch-template.md` per phase rather than inlining (fixed `e0ea5eb`).
- `al-dev-plan-swarm-validate` description "6 critics not shown" (was Medium) — live body
  enumerates all 6 parallel Agent dispatches + Dispatch Pattern section (fixed `76b0c5b`).

## Dispositioned (suppressed)

- `al-dev-support-reply-drafter` — model-fit downgrade sonnet → haiku — **declined**
  2026-06-05 (`3bed965`: reply quality outranks the token saving). Counted out of the
  table above.
