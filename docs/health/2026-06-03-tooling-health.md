# Tooling Health — 2026-06-03

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 4      | 10      | 0      | 14    |
| Medium   | 5      | 12      | 0      | 12    |
| Low      | 1      | 6       | 5      | 12    |

Failed lenses: none — all 21 tooling lenses returned results (2 re-run after a session-limit interruption).

Top 5 ranked actions:

1. **[Design / Model Fit — High]** Reassign all 4 `sync-documentation-maps-*` agents from sonnet to haiku. They do mechanical file reading, JSON parsing, grep-based list building, and templated map edits — no synthesis or design reasoning.
2. **[Design / Complexity — High]** Split the three high-phase map skills along their natural validation/commit gates: `review-agent-map` (7→audit+update), `review-skill-map` (7→audit+update), `sync-documentation-maps-finalize` (9→wait+write).
3. **[Design / Near-Duplicates — High]** Merge `review-skill-map` + `review-agent-map` into one `--surface [skills|agents]` skill — identical 7-phase structure, only the target surface differs.
4. **[Quality / Bloat — High]** Deduplicate the 6 high-bloat skills (plugin-health-discover Phase 3b, review-agent-map Phases 3/4/5b, review-skill-map Phases 5–6, sync-documentation-maps-collect Phases 2–3, sync-documentation-maps-finalize, audit-knowledge-quality) and the 4 high-bloat sync agents.
5. **[Quality / Clarity — High]** Fix the incomplete missing-lens conditional in `plugin-health-discover` ("note the lens name" with no concrete action) — specify recording in a "Failed lenses" section.

---

## Design suggestions

### High

- **sync-documentation-maps-agent-audit / -agent-update / -skill-audit / -skill-update** | Model Fit (Remodel) | All four assigned sonnet for mechanical tasks: file reading, JSON parsing, grep list-building, templated Mermaid/map edits — no multi-file synthesis or design decisions. | Reassign all four to haiku.
- **review-agent-map** | Complexity (Atomise) | 7 phases: discovery/audit (1–4) + editorial/commit (5–6). | Split into `/review-agent-map-audit` and `/review-agent-map-update`.
- **review-skill-map** | Complexity (Atomise) | 7 phases, identical structure to review-agent-map. | Split into audit + update.
- **sync-documentation-maps-finalize** | Complexity (Atomise) | 9 phases: validation/read (0–4) + write/regenerate/commit (5–8); natural gate at Phase 4. | Split into `-wait` and `-write`.

### Medium

- **sync-documentation-maps-agent-audit** | Scope Isolation (Split) | Two concerns: build agent list + metadata (audit) vs cross-reference and compare (validation). | Consider splitting into audit + compare agents.
- **sync-documentation-maps-skill-audit** | Scope Isolation (Split) | Same audit-vs-compare split. | Consider splitting.
- **review-skill-map + review-agent-map** | Near-Duplicates (Merge) | Identical 7-phase structure, identical `--no-update` flag, parallel surfaces; only target differs. | Refactor into unified `/review-documentation-map --surface [skills|agents]`.
- **docs/al-dev-plugin-synthesis.md** | Handoff Gaps (Extend) | `analyze-architectural-design` writes synthesis but no skill consumes it. | Fold synthesis context into `al-dev-map-suggestions-verify` Phase 2 rubber-duck checks.
- **docs/al-dev-knowledge-quality.md** | Handoff Gaps (Extend) | `audit-knowledge-quality` reports issues but no skill systematizes fixes. | Create a skill that converts HIGH issues into tasks + optionally dispatches a knowledge-fixer agent.

### Low

- **Lens-agent Workflow dispatch + RemoteTrigger fallback** | Shared Backbone | 21 lens agents dispatched via Workflow with no cross-reference doc; sync-documentation-maps-collect lacks the audit-phase fallback clause. | Document canonical Workflow pattern in `knowledge/`; add fallback clause to collect Phase 4.

_Surface Placement: all 14 tooling skills are correctly placed in `.claude/skills/` — no Move suggestions._

---

## Quality findings

### High

**Agent bloat (sync-documentation-maps agents, steps >30 lines):** agent-audit (Step 5, 32 lines), agent-update (Step 3, 44 lines / 5 case types), skill-audit (Step 4, 28 lines), skill-update (Step 3, 52 lines). → Extract fix-case logic to helpers; the four agents form a duplicative pair that could share generic parametric agents.

**Skill bloat (>30-line steps / dead branches):** plugin-health-discover (Phase 3b, 53 lines), review-agent-map (Phases 3/4 duplicate scanning; Phase 5b near-duplicate of 5), review-skill-map (Phases 5–6 identical Mermaid ops), sync-documentation-maps-collect (Phases 2–3 unreachable zero-discrepancy exit), sync-documentation-maps-finalize (duplicate checkpoint reads, 3 identical try-run blocks), al-dev-map-suggestions-verify (all validation deferred to external docs), audit-knowledge-quality (repeated gap-assessment across 3 categories).

**Skill clarity:** plugin-health-discover — incomplete missing-lens conditional ("note the lens name" with no concrete action). → Specify recording in a "Failed lenses" section.

### Medium

**Agent bloat:** design-skill-lens-complexity (shared file-reading across 2 output blocks), naming-convention-lens (redundant severity sections), quality-agent-lens-structure (canonical tools list maintained in two places).

**Agent clarity:** design-agent-lens-caller-alignment (grep pattern diverges from bash commands), design-skill-lens-complexity ("adjacent skill" undefined), design-skill-lens-handoff-gaps ("obvious" undefined), design-skill-lens-preplanning (provided vs hardcoded list conflict), naming-convention-lens (out-of-band exception), quality-agent-lens-bloat ("realistic invocations" undefined), quality-skill-lens-bloat (threshold 6 vs 8 conflict), sync agents (grep distinction, control-flow contradiction, "belongs" undefined).

**Agent name fit:** design-skill-lens-complexity (applies two lenses; name reflects only "complexity").

**Skill bloat:** align-harness-repos (Step 4 duplicates Step 3 replacements), plugin-health-report (35-line inline template), projection-sync (split checkpoint logic), sync-documentation-maps (duplicate JSON payloads).

**Skill clarity (Medium cluster):** ~18 items across map-suggestions-verify, align-harness-repos, audit-knowledge-quality, plugin-health-discover/report, projection-sync, review-agent-map, review-skill-map, sync-documentation-maps-collect/finalize/dispatch, review-maps — undefined terms, ambiguous conditionals, missing schemas.

### Low

- **design-skill-lens-complexity** | Name Fit | Consider rename to `-complexity-placement` (applies two lenses).
- **quality-agent-lens-description / quality-skill-lens-description** | Name Fit | Generic "description" name; consider `-description-drift`.
- **al-dev-map-suggestions-verify** | Structure | YAML `description` field appears empty/malformed.
- **plugin-health-audit** | Structure | `docs/health/` output path not clarified as accepted exception to `.dev/` convention.
- **Most tooling skills + 4 sync agents** | Structure | Missing language tags on code blocks; inconsistent phase/step heading depth.
- **Various lens agents** | Bloat | Minor repetitive patterns within small agent bodies.

---

## Naming violations

- **al-dev-map-suggestions-verify** | Low | Skill in maintainer `.claude/skills/` uses `al-dev-` prefix (plugin-distributed convention); maintainer skills should follow `{verb}-{object}-{aspect}`. | Rename to `verify-map-suggestions` or `verify-health-findings`.
- **sync-documentation-maps-agent-audit / -agent-update / -skill-audit / -skill-update** | Low | Agent names don't follow lens pattern and aren't documented exceptions; utility agents that may be better structured as maintainer skills. | Consider renaming (`audit-documentation-maps-agent`, etc.) or restructuring as skills.

_Note: the structure lens separately flagged all 21 lens agents for missing the `al-dev-` prefix. This is a false positive — lens agents intentionally follow the `{dimension}-{object}-lens-{aspect}` maintainer convention. Not counted as violations here._
