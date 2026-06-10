# Tooling Health — 2026-06-05

Surface: `.claude/` (26 agents, 17 active skills; `archived/` excluded).
Source findings: `docs/health/2026-06-05-tooling-findings.md` (21 lenses, none
failed; `design-skill-lens-surface-placement` excluded per discover §3.1b).

Re-sweep note: this dossier replaces the earlier 2026-06-05 dossier. All High
findings were spot-checked against live files; four lens claims were false
against current text and are dropped, not ranked.

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 0      | 4       | 0      | 4     |
| Medium   | 6      | 31      | 0      | 37    |
| Low      | 4      | 24      | 0      | 28    |

New this sweep: 68 · Recurring from prior sweeps: 1 (annotated inline) ·
Stale (dropped): 4 · Dispositioned (suppressed at dispatch): 6 rows honored

Failed lenses: none (21/21 returned).

Top 5 ranked actions:

1. **sync-documentation-maps family — align workflow numbering** (Quality/Description, Medium; verified against live files 2026-06-05). `sync-documentation-maps:19` and `-collect:12,16` say "Three-skill workflow"; `-apply:17` and `-write:16` say "Four-skill workflow"; the apply/write descriptions say "First/Second step of two-step sync finalization". Pick one frame (four-skill, with apply+write as the two-step finalization) and align all four files.
2. **plugin-health-discover — the documented Python dispatch path is a stub** (Quality/Description, Medium; observed during this run). `workflow_utils.py` returns mock findings; the skill's §3.2 invocation cannot work as written. Either implement the utilities or document in-session parallel lens dispatch as the canonical mechanism.
3. **sync-documentation-maps-\* agents — normalize `model:` to the `haiku` alias** (Quality/Structure, Medium). Four files carry `claude-haiku-4-5-20251001` where every other agent uses the alias. One mechanical change.
4. **plugin-health-discover — structural consolidation** (Quality/Bloat, High, count-based). 9 top-level sections with Phase 3 as a nested 3.1–3.3 workflow; fold the cadence guard into Phase 0 and merge resume+dispatch.
5. **al-dev-consolidate — replace Phase 2 inline patterns with cross-references** (Quality/Bloat, High). Phase 2 ~73 lines duplicating patterns now canonical in `consolidate-extraction-patterns.md` (moved to the maintainer surface today, 6cf7e81).

## Design suggestions

Medium:

- **sync-documentation-maps-agent-update / -skill-update** (Tool Hygiene → Trim) | `Bash` declared; no bash steps in body, only an external patterns-file reference | Trim `Bash` or add concrete steps — *check the referenced patterns file first; it may direct bash usage.*
- **sync-documentation-maps-{agent,skill}-{audit,update}** (Caller Alignment) | Inputs tables intermix dispatched inputs (run_id, result_dir) with internal knowledge references callers never pass | Separate the two in all four files (one pattern).
- **Knowledge-quality loop termination** (Handoff Gaps → Extend) | audit → fix dispatches fixes; nothing validates HIGH issues were resolved | Optional re-audit/compare phase in fix-knowledge-quality.
- **Background-audit dispatch pattern** (Shared Backbone) | The two audit agents share an undocumented run_id/result_dir/JSON-artifact contract | Document the canonical pattern (e.g. checkpoint-patterns.md).
- **Background-update dispatch pattern** (Shared Backbone) | Same for the update pair, with distinct schema | Document alongside, keeping audit/update schemas distinct.

Low:

- **naming-convention-lens** (Tool Hygiene) | `Glob` declared, unused (open since 2026-06-04) | Trim or add the intended glob usage.
- **Lens-agent dispatch-protocol wording** (Caller Alignment) | 12 context-taking lens agents say inputs are "provided in dispatch prompt" while context arrives as formatted text in one prompt field | Low-confidence bulk flag — ONE convention decision (standard sentence describing the protocol), not 12 fixes.
- **docs/al-dev-plugin-synthesis.md** (Handoff Gaps) | Written by analyze-architectural-design; no skill consumes it | Reference from plan-health-findings as optional context, or accept as terminal human-read artifact.
- **Vault promotion terminal** (Handoff Gaps) | al-dev-consolidate's sessions index has no automated consumer | Document manual import as canonical closure; check copilot-vault plugin overlap before adding anything.

Monitor-only (excluded from counts): naming-convention-lens dual-caller pattern (already canonical in lens-invocation-patterns.md); model-fit, scope-isolation, usage-patterns, complexity, near-duplicates, preplanning lenses all clean.

## Quality findings

High (all count-based bloat — re-verify counts before executing):

- **al-dev-consolidate** (Bloat) | Phase 2 ~73 lines duplicating extraction patterns canonical in `consolidate-extraction-patterns.md` | Cross-reference instead of restating.
- **sync-documentation-maps** (Bloat) | Phase 3 spans ~42 lines with nested 3.1/3.1b/3.2/3.3 | Condense dispatch; move invocation prose to companion reference.
- **sync-documentation-maps-collect** (Bloat) | Phase 4 defers all dispatch logic to collect-dispatch-patterns.md, reading as a forward reference | Inline minimal executable steps or tighten the reference contract.
- **plugin-health-discover** (Bloat) | 9 top-level sections; Phase 3 nested workflow | Consolidate resume+dispatch; cadence guard into Phase 0.

Medium (agents):

- Clarity: **design-agent-lens-caller-alignment** ("potential High" undefined), **design-agent-lens-usage-patterns** (skip-list rule lacks else), **design-skill-lens-complexity** ("independently runnable" undefined), **design-skill-lens-handoff-gaps** ("obvious next step"), **design-skill-lens-near-duplicates** ("plausibly confuse"), **naming-convention-lens** (no rule stated for non-lens maintainer agents), **sync-documentation-maps-agent-audit** ("(none found)" mapping lacks counterpart; skipped-caller-check reporting under-specified).
- Description: **sync-documentation-maps-agent-update / -skill-update** (description says writes the map; body writes to `<result_dir>/updates/` staging — verify the agent files' own description fields; the registry wording already mentions the updates directory).
- Structure: **sync agents ×4** | `model: claude-haiku-4-5-20251001` → alias `haiku`.

Medium (skills):

- Bloat: **plugin-health-audit** (thin-coordinator doc overlap with discover — valid pattern, trim only), **audit-knowledge-quality** (2a/2b describe both paths in full), **plan-health-findings** (historical "formerly verify-map-suggestions" commentary; staleness gate mirrors plugin-health-report's), **review-documentation-map** (surface conditionals duplicated across phases).
- Clarity: **al-dev-consolidate** (excerpt-holding definition; same-date grouping order), **al-dev-diagram-generator** (node-ID casing), **audit-knowledge-quality** (2b sequential labeling), **plan-health-findings** (`## Skipped` placement), **plugin-health-discover** (edge-extraction: one edge per target when a line matches multiple), **plugin-health-report** (monitor-only output placement), **projection-sync** (checkpoint create-vs-resume), **review-documentation-map** (union/dedup wording), **sync-documentation-maps-apply** ("continue" target phase), **sync-documentation-maps-write** (enumerate the "three numbers").
- Description: **sync family workflow numbering** (verified — see top action 1; covers sync/collect/apply/write), **fix-knowledge-quality** ("optionally dispatches fix agents" → conditionally dispatches al-dev-docs-writer), **plan-health-findings** (rubber-duck protocol delegated to knowledge file — say so), **analyze-architectural-design** (state it consumes completed lens output; name the output file), **plugin-health-discover** (stub workflow_utils — see top action 2).
- Structure: **al-dev-consolidate** (`argument-hint` present but empty).

Low (24): 10 agent-clarity qualifier items; preplanning-lens description wording; lens-agent code-block tags (batch — verify a sample); review-documentation-map "working table" storage note (downgraded from High — tables at :82/:102 are conventional working state); projection-sync Phase 0 prose→decision-tree; 8 skill-description minor items (al-dev-consolidate excerpt promise, diagram-generator write-verify, audit-knowledge-quality TaskCreate vocabulary, plugin-health-audit delegation note, plugin-health-report graph-error tolerance, projection-sync two-phase wording, review-documentation-map trigger clarity, review-maps dispatcher note); al-dev-diagram-generator mixed numbering; skill code-block tags (batch).

## Naming violations

*No issues found.* (Grandfathered suppressions honored: align-harness-repos, workflow-phase family names, sync family, plan-health-findings.)

---

### Stale (dropped) — verified against live files 2026-06-05

align-harness-repos code-block token branch (specified at :122-123); fix-knowledge-quality --auto-fix else (both branches at :65-67); sync-documentation-maps-collect audit-status else (present at :81); sync-documentation-maps notification/collect path (collect step named in description and :16-17).

### Dispositioned (suppressed at dispatch)

sync-update model upgrade (declined, row 38); align-harness-repos name (grandfathered, row 35); workflow-phase family names (grandfathered, row 37); sync family names (grandfathered); tooling lifecycle diagram (accepted row 39 — not re-flagged); agent-audit grep sequencing (fixed, row 33 — not re-flagged).
