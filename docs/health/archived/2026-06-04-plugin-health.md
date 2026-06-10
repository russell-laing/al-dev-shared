# Plugin Health — 2026-06-04

Source findings: `docs/health/2026-06-04-plugin-findings.md` (22/22 lenses returned; no failed lenses)
Surface: `profile-al-dev-shared/` — 23 agents, 23 skills
Suggestions only — no source files were edited. This dossier supersedes the earlier 2026-06-04 sweep run.

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 0      | 13      | 0      | 13    |
| Medium   | 7      | 28      | 1      | 36    |
| Low      | 17     | 40      | 0      | 57    |
| **Total**| **24** | **81**  | **1**  | **106** |

Counts exclude informational "no action required" entries returned by lenses.

Failed lenses: none — all 22 dispatched lenses returned results.

Top 5 ranked actions:

1. **al-dev-solution-architect — incomplete `TESTABILITY_COMPLETE: no` conditional (Quality/Clarity, High).** The agent returns the flag without any caller procedure; callers can proceed to implementation on an unresolved plan. Add explicit caller guidance: halt and do not dispatch the developer agent until testability is resolved.
2. **Seven-skill bloat cluster (Quality/Bloat, High).** `al-dev-commit`, `al-dev-develop`, `al-dev-investigate`, `al-dev-perf`, `al-dev-plan-preflight`, `al-dev-plan`, `al-dev-ticket` all exceed step-size thresholds with inlined templates and repeated procedural blocks. Extract inline templates (architect prompt, findings template, perf report, doc structure) to `knowledge/` and consolidate repeated rules into per-skill Critical Rules sections.
3. **Five-skill clarity cluster (Quality/Clarity, High).** Undefined operational terms gate behavior: "block progress" (`al-dev-develop`), circular "success evidence" (`al-dev-interview`, `al-dev-plan`), vague fallback (`al-dev-plan-preflight`), trailing-otherwise precedence rule (`al-dev-ticket`). Define each term inline at first use.
4. **Caller-alignment trio (Design/Align, Medium).** `/al-dev-explore`, `/al-dev-help`, and `/al-dev-document` reference their agents generically but never dispatch them by explicit agent type name; `al-dev-code-review` has no caller at all and should be documented as standalone-only.
5. **al-dev-plan-swarm-validate body is pseudo-code only (Quality/Description, Medium).** The description promises six parallel critics, synthesis, auto-fixes, and an approval gate, but the body contains no actionable implementation steps. Expand to concrete phases or descope the description.

## Design suggestions

### Remodel (model fit)

- **al-dev-support-reply-drafter** | Medium | Single-input/single-output translation task (findings block → customer reply) needing only Write; mechanical formatting work. | Assign `haiku` instead of `sonnet`.

### Align (caller alignment)

- **al-dev-code-review** | Medium | No spawning caller anywhere; documented for standalone use but never invoked. | Document explicitly as standalone manual dispatch only; not auto-spawned by any skill.
- **al-dev-explore** | Medium | `/al-dev-explore` says "Spawn an explore agent" without naming the agent type; `/al-dev-handoff` never dispatches it. | Add explicit agent-type dispatch line to `/al-dev-explore` Step 2.
- **al-dev-script-engineer** | Medium | `/al-dev-help` lists the agent in a reference table but has no dispatch step. | Either add a dispatch step for script requests or mark the agent "available for external dispatch only".
- **al-dev-docs-writer** | Low | `/al-dev-document` mentions "docs-writer specialist" but never names the agent type in a dispatch line. | Add explicit dispatch line passing AUDIENCE and artifact paths.
- **al-dev-developer-tdd / al-dev-developer-traditional** | Low | Inputs tables ambiguous about whether callers pass file paths or the agent auto-locates them. | Add note: agent auto-locates from `.dev/` via glob; dispatch prompt carries inline context only.

### Inline (usage patterns)

- **al-dev-support-researcher** | Low | Single-use agent with 108-line body and minimal contract documentation. | Consider consolidating the body to a structured format, or inlining research logic into the calling skill.

### Connect / Promote (shared backbone)

- **al-dev-developer-tdd & al-dev-developer-traditional** | Medium | Identical test-plan routing pattern copy-pasted in `al-dev-develop` (Phase 3) and `al-dev-fix` (Step 2). | Canonicalize the developer dispatch template in `knowledge/` and cross-reference from both skills.

### Atomise / Absorb (complexity)

- **al-dev-plan** | Medium | 7 phases, already partially atomized via preflight delegation; context-gathering and debate blocks are independently runnable. | No immediate split; document the preflight phase as a required dependency.
- **al-dev-plan-final-review** | Low | 3 phases, zero agents, pure approval gate for the plan output. | Absorb candidate: integrate validation + approval gate into `al-dev-plan`'s final phase; retire the standalone skill if validation always follows plan writing.
- **al-dev-consolidate** | Low | 5 phases, zero agents, two weakly coupled concerns (discovery/grouping vs extraction/output). | Absorb candidate: offer consolidation as an optional final phase of `/al-dev-document`.

### Extend (handoff gaps)

- **Post-commit chain gap** | Medium | The spine (plan → develop → review → commit) terminates at commit; release-notes/document are standalone entry points, not chained continuations. | Design a release-readiness skill that consumes commit metadata, updates changelog, optionally generates release notes, and gates deployment readiness.
- **Orphaned commit metadata** | Low | `.dev/commits.json`, `.dev/hook-failures.json`, `.dev/file-sizes.json` have no downstream reader. | Either give them a post-commit consumer or document as manual-inspection references.
- **Orphaned learnings artifact** | Low | `commit-recover` writes `.dev/learnings.md`; nothing reads it. | Extend `al-dev-commit` preflight to read learnings and warn on known corruption patterns.
- **Lint-before-commit gap** | Low | `al-dev-commit` optionally reads a prior lint report but never requires a fresh pass. | Add a staleness check in commit Phase 0 suggesting `/al-dev-lint` when staged AL files postdate the last report.

### Move (surface placement)

Nine skills flagged Low as maintainer-surface candidates (no spawned agents, developer-utility scope): `al-dev-help`, `al-dev-handoff`, `al-dev-investigate`, `al-dev-perf`, `al-dev-plan-final-review`, `al-dev-plan-preflight`, `al-dev-plan-swarm-validate`, `al-dev-review-develop-preflight`, `verify-commits`. **Caution:** several of these are integral to the distributed lifecycle (preflight skills are dispatched by `al-dev-plan`/`al-dev-develop`; `verify-commits` is chained from `al-dev-commit`) — treat the Move suggestions as low-confidence and verify each against the lifecycle diagram before accepting.

## Quality findings

### High

- **al-dev-solution-architect** (agent, clarity) | `TESTABILITY_COMPLETE: no` return path has no caller procedure | Add caller guidance: halt, do not dispatch developer until resolved.
- **al-dev-commit** (skill, bloat) | 589 lines; repeated dispatch patterns and procedural footnotes across phases | Consolidate into a reusable dispatch template + single Critical Rules section.
- **al-dev-develop** (skill, bloat) | Signature Verification (~60 lines) and Static Validation (~70 lines) inlined; dead `--autonomous` branches | Extract both blocks to standalone sub-skills or knowledge refs.
- **al-dev-investigate** (skill, bloat) | Step 5 spans ~98 lines incl. inline findings template | Extract template to `knowledge/investigate-findings-template.md`.
- **al-dev-perf** (skill, bloat) | Inline classification logic, agent prompt, and 60-line report template | Extract classification + report template to `knowledge/`.
- **al-dev-plan-preflight** (skill, bloat) | Optional phases 1.5/1.6 carry 30+ line decision trees; validation gate logic repeated | Consolidate optional phases into one verification block; externalize the input-validation gate.
- **al-dev-plan** (skill, bloat) | 40+ line inline architect prompt; Phase 0 resume modes sprawl | Extract architect prompt template to `knowledge/`; consolidate resume modes into one decision tree.
- **al-dev-ticket** (skill, bloat) | 8 named sections; mode detection logic repeated in Phases 0, 0.5 and 5 | Consolidate mode resolution into one block at the top.
- **al-dev-develop** (skill, clarity) | "block progress" escalation trigger undefined | Define specific blocking conditions.
- **al-dev-interview** (skill, clarity) | "success evidence" referenced circularly, never defined inline | Define success evidence upfront (INTERVIEW COMPLETE signal + category list).
- **al-dev-plan** (skill, clarity) | Artifact-contract success evidence not inlined | Inline summary: plan file written AND read AND validator passes.
- **al-dev-plan-preflight** (skill, clarity) | "fall back to re-running the specific preflight step" — which step is unidentified | Map each required field to the phase that produces it.
- **al-dev-ticket** (skill, clarity) | Mixed-input precedence rule states the fallback after the rule, inviting misreads | Restate as explicit IF/THEN/ELSE.

### Medium

- **al-dev-commit-lint-fixer** (agent, clarity) | Regex mandate lacks failure-mode explanation | Document why only `[[:blank:]]+$` is safe on BSD sed.
- **al-dev-developer-tdd** (agent, clarity) | Gate tokens used ~70 lines before they're defined | Define at first use or move the governance table up.
- **al-dev-interview** (agent, clarity) | USER_GATE failure path documented; success path missing | Add explicit success-path clause.
- **al-dev-release-notes-writer** (agent, clarity) | Pseudo-code references undefined env var `AL_DEV_SHARED_PLUGIN_ROOT` | Define it or replace the snippet with the real invocation pattern.
- **al-dev-commit-recover-fixer** (agent, name-fit) | "commit" in name over-emphasizes trigger; actual scope is corrupted-file restoration | Rename (e.g. file-corruption-fixer) or sharpen the leading description sentence.
- **al-dev-commit** (skill, description) | Promised scope-creep detection has no corresponding body step | Add a Phase 0 scope-creep detection step comparing staged diff to approved plan.
- **al-dev-develop** (skill, description) | Phase 4 handoff artifact promised but its write step is implicit | Make the handoff-file write explicit in Phase 4 Step 1.
- **al-dev-document** (skill, description) | RTM outputs promised in spawn prompt but absent from success criteria | Add RTM acceptance criterion or descope.
- **al-dev-fix** (skill, description) | "without approval gates" contradicted by scope-confirmation gate in body | Qualify the description or restructure scope filtering.
- **al-dev-interview** (skill, description) | Mandatory INTERVIEW COMPLETE gate absent from description | Mention the completion gate in the description.
- **al-dev-plan-swarm-validate** (skill, description) | Body is pseudo-code; promised critics/synthesis/auto-fix/gate not implemented | Expand into concrete phases or descope the description.
- **al-dev-support-reply** (skill, description) | Auto-detect input mode and file-based output not reflected in description | Update description: input path or auto-detect; output written to reply file.
- **al-dev-consolidate** (skill, bloat) | Extraction patterns re-stated inline despite knowledge reference | Reference patterns by name only.
- **al-dev-document** (skill, bloat) | 80-line doc-structure template inlined | Externalize to a knowledge template per audience.
- **al-dev-fix** (skill, bloat) | Classification logic and trivial-fix rule repeated ×3 | Consolidate into one Complexity Classification section + Critical Rules footnote.
- **al-dev-interview** (skill, bloat) | Long inline dispatch prompt; governance patterns restated | Consolidate via artifact-contracts reference.
- **al-dev-review-develop-preflight** (skill, bloat) | Same git/checkpoint bash patterns stated 3× | Define each pattern once in a Critical Rules block.
- **al-dev-review-develop** (skill, bloat) | Three reviewer dispatch blocks verbatim-identical except name | Replace with a single parameterized dispatch template.
- **al-dev-commit** (skill, clarity) | Two bare "Stop." branches without else clauses | Add explicit else paths.
- **al-dev-explore** (skill, clarity) | Malformed sentence "Holdclassify the user's question type" | Fix the sentence.
- **al-dev-fix** (skill, clarity) | Trivial-fix recompile loop lacks exit condition | Cap at one rerun, then escalate.
- **al-dev-help** (skill, clarity) | Two routing branches missing else clauses | Complete the branch logic.
- **al-dev-investigate** (skill, clarity) | "best-supported hypothesis" threshold undefined | Define evidence thresholds.
- **al-dev-perf** (skill, clarity) | "evidence source" used before being defined | Define evidence sources upfront.
- **al-dev-plan-swarm-validate** (skill, clarity) | "gates user approval" passive and ambiguous | State who gates and what triggers approval.
- **al-dev-review-develop-preflight** (skill, clarity) | PREREQUISITES_MET conditional incomplete | State both branches explicitly.
- **commit-recover** (skill, clarity) | "verified" recovery status undefined | Define: compiles post-recovery AND line count matches baseline.
- **al-dev-develop** (skill, structure) | Body references developer agents without existence check note | Confirm agent references against the agents directory.

### Low

- **Agent clarity (2):** `al-dev-commit-ooxml-validator` missing success-path clause; `al-dev-support-reply-drafter` unlabelled/unverified-URL handling undefined.
- **Agent structure (5):** missing code-fence language tag (`al-dev-commit-agent-analysis`); malformed fence (`al-dev-release-notes-writer`); step-numbering gaps or `.5` steps (`al-dev-support-researcher`, `al-dev-support-reply-drafter`, `al-dev-ticket-agent`).
- **Agent name-fit (1):** `al-dev-diagnostics-fixer` name broader than its compile/lint scope.
- **Skill bloat (1):** `al-dev-explore` restates the subagent pattern it already references.
- **Skill clarity (9):** vague qualifiers or implicit success conditions in `al-dev-consolidate`, `al-dev-document`, `al-dev-handoff`, `al-dev-lint`, `al-dev-plan-final-review`, `al-dev-release-notes`, `al-dev-review-develop`, `al-dev-support-reply`, `verify-commits` — each with a one-line definition fix in the findings file.
- **Skill structure (22):** missing code-fence language tags across nearly all skills; placeholder `argument-hint` values in `al-dev-commit` and `al-dev-consolidate`; same-day output-collision note for `al-dev-support-reply`. Mechanical batch fix.

## Naming violations

- **al-dev-commit-recover-fixer** | Medium | Output path documented with literal `YYYY-MM-DD` placeholder (lines 6, 34, 58) instead of date expansion or a rendered example | Use `$(date +%Y-%m-%d)` expansion or show a rendered example date.

## Graph deltas

- **Orphan agent:** `al-dev-code-review` has no spawning skill (standalone-only; catalog confirms "(none found)").
- **Catalog vs profile drift:** the agent catalog table lists "(none found)" for `al-dev-docs-writer`, `al-dev-explore`, and `al-dev-script-engineer`, while their Layer 2 profiles name callers (`/al-dev-document`, `/al-dev-explore` + `/al-dev-handoff`, `/al-dev-help`). One of the two layers is wrong in each case.
- **Count drift:** the agent map header states 22 agents; 23 agent files exist on disk and 23 rows are in the catalog.
- **Missing diagram edge:** the skills-map drilldown for `/al-dev-document` shows no agent, but the agent map records `al-dev-docs-writer` as spawned by it.

---

Next step: review this dossier, then run `/verify-map-suggestions` on accepted items to rubber-duck them against the live codebase before planning changes.
