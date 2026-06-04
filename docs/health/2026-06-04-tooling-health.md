# Tooling Health — 2026-06-04

Surface: maintainer tooling (`.claude/`) — 26 agents, 16 active skills. Dimensions: design + quality + naming. 22 lenses dispatched, 22 returned, 0 failed. Suggestions only — no source files were edited.

> Findings are ordered High → Medium → Low. Counts below exclude the 26 false-positive structure-lens hits (see note). Many Low/Medium "clarity" and "description" items are wording nits inside the lens agents' own instruction bodies; treat them as polish, not priorities.

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 2      | 17      | 0      | 19    |
| Medium   | 4      | 33      | 0      | 37    |
| Low      | 8      | 21      | 2      | 31    |

Top 5 ranked actions:

1. **Fix the grep/dedup ambiguity in the sync-doc audit agents** (Quality/clarity, High) — `sync-documentation-maps-agent-audit` and `-skill-audit` Step 3 has two deduplication points and a backtick-vs-literal grep pattern in Step 4. This is a genuine correctness risk in a script-driven agent. Specify a single `sort -u` at end + exact executable bash.
2. **Trim unused `Bash` from the two sync-doc update agents** (Design/tool-hygiene, Medium — but the cleanest win) — `sync-documentation-maps-agent-update` and `-skill-update` declare `Bash` yet only Read/Write. Remove it.
3. **Decompose the overloaded skill phases** (Quality/bloat, High) — `audit-knowledge-quality` (Phase 2), `review-documentation-map` (Phases 2 & 4), `verify-map-suggestions` (Phase 1/1b), `sync-documentation-maps-collect` (Phase 4) each pack >30 lines / mixed concerns into one phase. Split into sub-phases.
4. **Rename the misleading `sync-documentation-maps-wait`** (Quality/name-fit, High) — it does not wait; it validates artifacts and writes maps to disk. Rename to reflect the write action.
5. **Repair the structure lens's tooling-surface blind spot** (Quality/structure, Medium) — `quality-agent-lens-structure` flagged all 26 tooling agents for lacking an `al-dev-` filename prefix, which is the *distributed*-surface rule. Teach it the maintainer-tooling convention so it stops emitting 26 false positives every sweep.

## Design suggestions

### High

- **review-documentation-map** — Atomise | 8 phases split cleanly into audit/analysis (0–4b) vs. map modification (5–6). | Consider splitting into a read-only audit skill + an apply-changes skill with a structured handoff. **Caveat:** this trio was *just* consolidated (commit 7087b8a); weigh re-splitting against that recent merge before acting.
- **plugin-health-discover** — Atomise | 6 phases mix context aggregation (0–2), lens dispatch (3–3b), and findings assembly (4). | Consolidate Phases 3+3b, or split prep / dispatch / assemble. Overlaps the Quality/bloat finding on the same skill.

### Medium

- **sync-documentation-maps-agent-update** — Trim | `Bash` declared but only Read/Write used. | Remove `Bash`.
- **sync-documentation-maps-skill-update** — Trim | `Bash` declared but only Read/Write used. | Remove `Bash`.
- **sync-documentation-maps** — Monitor | 6 phases; setup (0–2) entangled with finalization (4–5). | If background-dispatch is reused elsewhere, extract a reusable orchestration module; otherwise leave.
- **plugin-health-audit → plan execution** — Handoff gap | The audit→discover→report→verify-map-suggestions chain produces a plan no skill executes. | Optionally add an execute-plugin-plan skill — **but** plan execution is intentionally delegated to generic `superpowers:executing-plans` / `subagent-driven-development`; confirm a dedicated skill is actually wanted before building one.

### Low

- **naming-convention-lens** — Trim | `Glob` declared, no globbing in body. | Remove `Glob` (also surfaced by description-drift).
- **Model fit — 4 sync-doc agents** | Multi-step orchestration sits at the high end of haiku's range. | Acceptable on haiku; escalate to sonnet only if reliability issues appear.
- **Model pinning inconsistency** | 4 sync-doc agents pin full id `claude-haiku-4-5-20251001`; 22 lens agents use alias `haiku`. | Standardize to the alias.
- **fix-knowledge-quality** — Handoff | show-task-list-only path prints tasks but doesn't persist them to `.dev/`. | Optionally persist as an artifact.
- **al-dev-diagram-generator** — Handoff | `docs/al-dev-workflow-diagrams.md` has no downstream consumer. | Confirm it's intended as a leaf/reference output.

*Scope-isolation, caller-alignment, usage-patterns, near-duplicates, pre-planning, shared-backbone, and surface-placement lenses found no issues.*

## Quality findings

### High

- **sync-documentation-maps-agent-audit** (clarity) | Step 3 double-deduplication + Step 4 ambiguous grep pattern (literal vs meta-notation). | Single `sort -u` at end; provide exact bash.
- **sync-documentation-maps-skill-audit** (clarity) | Same grep union/dedup ambiguity; Step 2 `.dev/` extraction pattern undefined. | Specify dedup + extraction regex.
- **design-skill-lens-complexity** (clarity) | "cluster into two distinct concerns... if identifiable" has no threshold. | Flag only if each concern ≥2 phases and standalone.
- **design-skill-lens-handoff-gaps** (clarity) | "never referenced" not operationalized. | Specify grep of `.dev/` filenames in downstream bodies.
- **audit-knowledge-quality** (bloat) | Phase 2 >30 lines, parallel branch + sequential fallback in one block. | Split into 2a (threshold) / 2b (execute).
- **plugin-health-discover** (bloat) | 9 effective sections; Phase 3b ~56 lines with nested Workflow + polling. | Consolidate 3+3b with marked sub-steps.
- **review-documentation-map** (bloat) | Phases 2 and 4 both >30 lines, nested extraction+decision logic. | Split 2→2a/2b, 4→4a/4b.
- **verify-map-suggestions** (bloat) | Phase 1 (~70 lines incl. 1b) and Phase 2 (~59 lines) overloaded. | Renumber into single-responsibility phases.
- **sync-documentation-maps-collect** (bloat) | Phase 4 (~70 lines) mixes dispatch, checkpoint-merge, verification. | Extract dispatch + merge patterns to a reference doc.
- **al-dev-diagram-generator** (clarity) | Grep parse-failure handling unspecified; "deduplicate" undefined. | Define skip/error recovery + dedup by (source,target).
- **plugin-health-discover** (clarity) | "compare returned lens ids with remaining_lenses" is prose, no code; `${today}` undefined. | Provide runnable snippet; define `today`.
- **review-documentation-map** (clarity) | Caller-set union/dedup ordering unclear; Mermaid style-guard not operationalized. | Specify dedup-after-union + grep/regex for style lines.
- **sync-documentation-maps-collect** (clarity) | `WAIT_MODE=false` absent-artifact behavior undefined. | Specify the harness-notify path.
- **verify-map-suggestions** (clarity) | "independent" suggestions ambiguous for chains. | Define via dependency graph + topological dispatch.
- **align-harness-repos** (name-fit) | Name implies bidirectional sync; body is validate-with-optional-fix. | Rename `validate-harness-neutrality`, or accept as grandfathered (see naming convention).
- **sync-documentation-maps-wait** (name-fit) | Name implies polling; body writes maps to disk. | Rename to a write/finalize name.

### Medium

- **quality-agent-lens-structure** (structure) | Emits 26 false positives by applying the distributed `al-dev-` filename rule to tooling agents; the dedicated naming lens correctly does not. | Teach the lens the maintainer-tooling convention or scope its filename check to the distributed surface. **This is the fix for the 26 excluded hits.**
- **Agent clarity (Medium ×8):** caller-alignment ("actually invoke" — no method), tool-hygiene ("described as read-only" — where to check), near-duplicates (exact vs subset agent-set), preplanning (substring vs exact label match), shared-backbone ("identical" threshold), surface-placement ("in the body" scope), naming-convention ("deviates" severity), bloat agent>6/skill>8 threshold mismatch. | Tighten each qualifier.
- **Skill bloat (Medium ×5):** fix-knowledge-quality (restated branch), projection-sync (repeated phase pattern), sync-documentation-maps-wait (repeated validation), sync-documentation-maps-write (repeated error-check), sync-documentation-maps (duplicated checkpoint/manifest write). | Extract shared patterns / consolidate.
- **Skill clarity (Medium ×7):** align-harness-repos ("flag for manual review"), audit-knowledge-quality (no parallel-dispatch fallback / all-stale action), fix-knowledge-quality ("genuine gaps"), plugin-health-report (no sort tie-breaker), projection-sync ("preserve as-is on failure"), sync-documentation-maps-collect (object-name sort/dedup), sync-documentation-maps (RUN_ID substitution). | Specify each.
- **Skill description drift (Medium ×9):** al-dev-diagram-generator (output structure + `--caller-name`), analyze-architectural-design (no-plan vs handoff wording), audit-knowledge-quality (dispatch mechanism), plugin-health-discover (filename + possible harness-specific token), projection-sync (omits resume/4-phase), review-maps (omits `--no-update`), sync-documentation-maps-collect (conditional read + token), sync-documentation-maps-wait (wrong "first of two" phase numbering), sync-documentation-maps-write (lists only some regen scripts). | Reconcile description with body.
- **Skill name-fit (Medium ×3):** fix-knowledge-quality (implies auto-fix; user-gated), sync-documentation-maps-collect ("collect" reads as read-only; also dispatches), sync-documentation-maps-write (undersells write+regen+commit). | Clarify descriptions or rename.

### Low

- **Agent clarity (Low ×5):** model-fit ("marginally"), scope-isolation ("cleanly"), clarity-lens (meta-notation note), sync-doc agent-update ("Stop if absent"), sync-doc skill-update (Step 3 skip logic). | Polish.
- **Agent description drift (Low ×7):** complexity ("ranks" not instructed), handoff-gaps ("traces" vs consumes), preplanning (dynamic vs hardcoded), surface-placement (omits Move target), naming-convention (`Glob`), sync-doc update agents (omit date-stamp edit), assorted verb/label styling. | Polish.
- **Skill bloat (Low ×5):** al-dev-diagram-generator (historical comment line 18), analyze-architectural-design (`head -2` vs single dossier), plugin-health-audit (long resume section), plugin-health-report (wordy line 81), review-maps (repeated `--no-update`). | Trim.
- **Skill clarity (Low ×1):** sync-documentation-maps-write ("otherwise" implied) — no fix needed.
- **Skill description drift (Low ×1):** align-harness-repos (validation vs repair). | Clarify.
- **Skill name-fit (Low ×2):** al-dev-diagram-generator ("generator"), analyze-architectural-design ("analyze" vs synthesis). | Accept or rename.

*Agent bloat and agent name-fit lenses found no issues.*

## Naming violations

- **al-dev-diagram-generator** | Low | `al-dev-` prefix + noun `generator` deviate from `{verb}-{object}-{aspect}`. | Rename (e.g. `generate-workflow-diagrams`) or grandfather.
- **sync-documentation-maps[-collect|-wait|-write]** | Low (advisory) | Workflow-phase naming parses awkwardly under the convention. | Grandfather the family or document a workflow-phase exception.

No High naming findings. All 22 lens-agent filenames conform to `{design|quality}-{agent|skill}-lens-{aspect}` (with `naming-convention-lens` the allowed exception). No output-path violations.

## Failed lenses

None — all 22 lenses returned results.
