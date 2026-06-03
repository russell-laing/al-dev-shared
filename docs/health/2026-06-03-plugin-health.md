# Plugin Health — 2026-06-03

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 3      | 19      | 0      | 22    |
| Medium   | 14     | 18      | 5      | 37    |
| Low      | 12     | 8       | 0      | 20    |

Failed lenses: none — all 21 plugin lenses returned results.

Top 5 ranked actions:

1. **[Design / Shared Backbone — High]** Extract the 6-agent `al-dev-commit` chain dispatch into `knowledge/commit-agent-invocation-patterns.md`. Six sequential agents have inline, tightly-coupled dispatch prompts; any architecture change requires editing all six in-place.
2. **[Design / Complexity — High]** Atomise `al-dev-plan` (7 phases). Context-gathering (0–1.6) is already delegated to preflight; the architect debate + synthesis + validation + presentation (phases 2–7) is cognitively heavy every invocation. Extract Phase 6 validation / Phase 7 presentation into a final-review skill.
3. **[Design / Model Fit — High]** `al-dev-solution-architect` runs opus on every invocation, but SIMPLE features (2–3 files, "skip research") draft 50–100 line plans that don't justify opus tokens. Route SIMPLE to sonnet; reserve opus for MEDIUM/COMPLEX.
4. **[Quality / Clarity — High]** Resolve 10 high-severity undefined-term / incomplete-conditional issues: `al-dev-commit` (`$AL_DEV_SHARED_PLUGIN_ROOT` unvalidated), `al-dev-develop` ("external procedure" undefined), `al-dev-fix` ("errors caused by the small change"), `al-dev-interview` (category "coverage"), `al-dev-investigate` (hypothesis criteria), plus map-suggestions-verify, plan-preflight, plan-swarm-validate, ticket, verify-commits.
5. **[Quality / Bloat — High]** Reduce `al-dev-commit` (611 lines, Phase 0 spans 44–262 with 5-level nesting) and `al-dev-develop` (464 lines, repeated developer-spawn blocks) by extracting patterns to knowledge files.

---

## Design suggestions

### High

- **al-dev-commit (6-agent chain)** | Shared Backbone | Six sequential commit agents (analysis, execute, hook-fixer, lint-fixer, message-drafter, ooxml-validator) with tightly coupled inline dispatch prompts and no shared invocation-pattern document. Architecture changes require updating all six prompts manually. | Create `knowledge/commit-agent-invocation-patterns.md` documenting phase sequence, inter-phase artifact contracts, and canonical dispatch templates.
- **al-dev-plan** | Complexity (Atomise) | 7-phase skill with two separable concerns: context gathering (0–1.6, delegated to preflight) and architect debate/synthesis (2–7). Debate phases are heavy every invocation. | Extract Phase 6 validation and Phase 7 presentation into a separate final-review skill.
- **al-dev-solution-architect** | Model Fit (Remodel) | Assigned opus for all invocations; SIMPLE features explicitly route here with "skip research" and draft 50–100 line plans. | Route SIMPLE to sonnet-level planning; reserve opus for MEDIUM/COMPLEX.

### Medium

- **al-dev-support-researcher** | Tool Hygiene | MCP tools declared but body is descriptive, not prescriptive — no concrete invocation examples. | Add concrete MCP call examples or remove MCP tools if reasoning-only.
- **al-dev-commit-message-drafter** | Model Fit (Remodel) | Sonnet for a purely mechanical template-fill task. | Downgrade to haiku.
- **al-dev-commit-agent-analysis** | Caller Alignment | Inputs table doesn't clarify staged git index arrives via bash, not structured blocks. | Clarify two-source input pattern.
- **al-dev-interview** | Caller Alignment | Inputs table lists "File path argument" as an agent input, but it's a skill-level argument processed before dispatch. | Correct Inputs table.
- **al-dev-support-researcher** | Caller Alignment | Outputs don't state output is return-block only (no file writes). | Add "Return block only (no file output)".
- **al-dev-ticket-agent** | Caller Alignment | Inputs don't clarify FRESHDESK credentials are harness-injected env vars, not dispatch-prompt fields. | Clarify credential injection.
- **al-dev-review-develop** | Complexity (Atomise) | 6 phases: pre-review prep + compile (1–3) vs reviewer dispatch + output (4–6). | Split after Phase 3.
- **verify-commits** | Complexity (Absorb) | 0-phase zero-agent skill overlapping al-dev-commit Phase 2. | Absorb as optional al-dev-commit Phase 2.4.
- **al-dev-review-develop → al-dev-commit** | Handoff Gaps | Code-review output is a well-established chain endpoint with no solid handoff arrow to commit. | Formalize handoff + dispatch pattern in Phase 6.
- **al-dev-plan-preflight** | Pre-planning | `preflight-context.md` is a primary Phase 0 output but is absent from al-dev-plan's artifact contract. | Add preflight I/O to `knowledge/artifact-contracts.md`.
- **al-dev-developer-tdd** | Shared Backbone | Identical TDD spawn pattern in al-dev-develop and al-dev-fix without shared canonical template. | Document canonical TDD spawn template in `knowledge/developer-invocation-patterns.md`.
- **al-dev-developer-traditional** | Shared Backbone | Spawn pattern across develop/fix/review-develop without single canonical template. | Extract canonical template; reference by section.
- **al-dev-solution-architect** | Shared Backbone | Two spawn patterns (debate vs quick analysis) reference architect-invocation-patterns.md but it lacks prompt templates. | Add "Pattern 1/2 Dispatch Template" sections.
- **3-reviewer panel (security/expert/performance)** | Shared Backbone | Three parallel reviewers with identical dispatch structure but no shared pattern doc; adding a 4th requires editing all three. | Create `knowledge/code-review-panel-invocation-pattern.md`.

### Low

- **al-dev-commit-recover-fixer** | Tool Hygiene | `Write` declared; unclear if report uses Write or Bash redirection. | Clarify or remove Write.
- **reviewers (security/expert/performance)** | Model Fit | Sonnet for single-file checklist review; haiku could execute. Defensible. | Borderline; no remodel required.
- **al-dev-diagnostics-fixer** | Model Fit | Sonnet for mechanical classification pipeline. Defensible for judgment rules. | Borderline.
- **al-dev-developer-tdd / -traditional** | Caller Alignment | Inputs imply glob-only; dispatcher may also pass inline context. | Clarify two-source pattern.
- **al-dev-solution-architect** | Caller Alignment | Inputs precedence backwards (primary is inline text, not globbed file). | Reorder Inputs table.
- **al-dev-commit-lint-fixer / -ooxml-validator** | Caller Alignment | APPROVED_PLAN not marked as inline text block. | Add clarification.
- **al-dev-map-suggestions-verify** | Surface Placement (Move) | Scores 2 signals (internal refs, self-audit). Already in `.claude/skills/`. | Confirm placement; likely no action.
- **plugin-health-audit** | Surface Placement (Move) | Scores 2 signals. Already in `.claude/skills/`. | Confirm placement; likely no action.
- **al-dev-document** | Handoff Gaps | Feature docs never consumed downstream. | Optional handoff to al-dev-consolidate.
- **al-dev-release-notes** | Handoff Gaps | Release notes never referenced downstream. | Optional publish skill.
- **al-dev-consolidate** | Handoff Gaps | Output could feed vault-promotion but lacks completion handoff. | Document soft handoff.
- **al-dev-lint** | Handoff Gaps | al-dev-commit uses internal lint-fixer rather than chaining to /al-dev-lint — dual orchestration. | Document which skill owns pre-commit lint.
- **al-dev-explore / -interview / -perf / -investigate** | Pre-planning | Dashed arrows to al-dev-plan without labeled handoffs or artifact-contract entries. | Add labeled handoffs or document optional inputs.
- **support agents (researcher + reply-drafter)** | Shared Backbone | Two sequential agents without canonical pattern doc. | Document "Support Reply Pattern" section.

---

## Quality findings

### High

**Agent bloat (sections >30 lines):** al-dev-commit-agent-analysis (43-line Manifest Extraction), al-dev-developer-tdd (63-line Standards), al-dev-developer-traditional (61-line Standards), al-dev-docs-writer (65-line Documentation Guidelines), al-dev-solution-architect (114 lines across 4 subsections), al-dev-interview (74 lines across 3 subsections). → Split oversized sections into focused subsections.

**Skill bloat (>30-line steps):** al-dev-commit (611 lines, Phase 0 5-level nesting), al-dev-develop (464 lines, repeated spawn blocks), al-dev-plan (335 lines, Phase 2 repeats knowledge-file content). → Extract patterns to knowledge files; reduce nesting.

**Skill clarity (undefined terms / incomplete conditionals):** al-dev-commit (`$AL_DEV_SHARED_PLUGIN_ROOT` unvalidated), al-dev-develop ("external procedure" undefined), al-dev-fix ("errors caused by the small change"), al-dev-interview (category "coverage"), al-dev-investigate (hypothesis "testable"/"bounded"), al-dev-map-suggestions-verify (dependent-suggestion procedure for count ≥3), al-dev-plan-preflight (50–74% verified-claims guidance), al-dev-plan-swarm-validate (critic timeout/failure handling), al-dev-ticket (mode-flag fallback), verify-commits (`<N>` computation for `git reset`). → Add explicit definitions and fallback rules.

### Medium

**Agent bloat (repetitive blocks / dead branches):** al-dev-commit-agent-execute, al-dev-commit-hook-fixer (unreachable fallback branch), al-dev-commit-lint-fixer, al-dev-commit-recover-fixer (malformed return block), al-dev-diagnostics-fixer, al-dev-explore, al-dev-release-notes-writer, al-dev-script-engineer, al-dev-support-reply-drafter (constraint in 3 places), al-dev-ticket-agent.

**Agent clarity:** al-dev-commit-agent-analysis (mismatched backtick), al-dev-commit-recover-fixer (mismatched backtick), al-dev-docs-writer (3 mismatched closers), al-dev-explore, al-dev-interview, al-dev-release-notes-writer, al-dev-solution-architect (vague conditional, no else), al-dev-support-reply-drafter ("as needed"), al-dev-ticket-agent (undefined download trigger).

**Agent description drift:** al-dev-commit-hook-fixer (description promises "optionally reruns commits" but body forbids it — direct contradiction).

**Agent name fit:** al-dev-commit-agent-analysis/execute (inconsistent commit-family naming), al-dev-expert-reviewer (vague — actually an AL pattern reviewer).

**Agent structure:** al-dev-commit-agent-analysis (malformed duplicate bash tags).

**Skill bloat:** al-dev-map-suggestions-verify (134-line Troubleshooting), al-dev-consolidate (inline patterns duplicated), al-dev-perf (hierarchy stated twice), al-dev-plan-preflight (overlapping Resume/schema sections), al-dev-commit (advisory block belongs in separate skill).

**Skill clarity (Medium cluster):** ~20 medium items across consolidate, document, explore, fix, handoff, help, lint, perf, plan, release-notes, review-develop, support-reply, ticket, commit-recover — undefined terms, missing fallback rules, ambiguous conditionals.

### Low

- **al-dev-script-engineer** | Clarity | TOOLKIT_PATH lacks empty-result fallback.
- **al-dev-commit-recover-fixer** | Description | Recovery report output not advertised in description.
- **al-dev-code-review** | Name Fit | Generic name; consider al-dev-general-code-reviewer.
- **al-dev-ticket-agent** | Name Fit | Broad name; consider al-dev-ticket-fetcher.
- **al-dev-code-review** | Bloat | Duplicated historical commentary.
- **al-dev-commit-message-drafter** | Structure | Empty tools array — document why none.
- **21 agents + ~22 skills** | Structure | Missing language tags on code blocks; al-dev-consolidate mixes Phase/Step naming.

---

## Naming violations

All 5 are agent output-path findings flagged against the `YYYY-MM-DD-{surface}-{kind}.md` convention. **Rubber-duck caveat:** the convention was designed for maintainer-tooling outputs; these are AL workflow artifacts written to project `.dev/` directories, so the convention may not apply. Verify before acting.

- **al-dev-commit-recover-fixer** | Medium | `.dev/YYYY-MM-DD-al-dev-commit-recover-report.md` uses skill name where `{surface}` expected.
- **al-dev-developer-tdd** | Medium | `.dev/YYYY-MM-DD-al-dev-developer-tdd-log.md` uses skill name as surface.
- **al-dev-explore** | Medium | `.dev/YYYY-MM-DD-al-dev-explore.md` uses skill name as surface; missing kind.
- **al-dev-release-notes-writer** | Medium | `.dev/YYYY-MM-DD-al-dev-release-notes-<VERSION>.md` embeds skill name where surface should be.
- **al-dev-docs-writer** | Medium | `docs/Features/[name].md` doesn't match `al-dev-{object}-{kind}.md` living-doc pattern.

---

## Graph deltas

Refreshed via `scripts/generate-plugin-graph.py` — see `docs/al-dev-plugin-graph.md`. Notable structural observations surfaced by the design lenses:

- **al-dev-document, al-dev-release-notes** — orphaned outputs (produced, never consumed downstream).
- **al-dev-explore / -interview / -perf / -investigate** — dashed tributaries to al-dev-plan with no labeled handoff or artifact-contract entry.
- **al-dev-review-develop → al-dev-commit** — established endpoint missing a solid handoff arrow.
