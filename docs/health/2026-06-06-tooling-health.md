# Tooling Health — 2026-06-06

Surface: `.claude/` (26 agents, 19 active skills; `archived/` excluded).
Source findings: `docs/health/2026-06-06-tooling-findings.md` (21 lenses, none
failed; `design-skill-lens-surface-placement` excluded per discover §3.1b).

All High findings and top-5 candidates were spot-checked against live files
(2026-06-06). Three lens claims were false or already-addressed against current
text and are dropped, not ranked. Two findings are suppressed as settled
dispositions.

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 1      | 7       | 0      | 8     |
| Medium   | 9      | 28      | 0      | 37    |
| Low      | 3      | 20      | 0      | 23    |

New this sweep: ~62 · Recurring from prior sweeps: 6 (annotated inline) ·
Stale (dropped): 3 · Dispositioned (suppressed): 2

Failed lenses: none (21/21 returned).

Top 5 ranked actions:

1. **plugin-health-report — Atomise the 8-phase skill** (Design/Complexity, High). Two separable concerns: findings processing (phases 0–1d: locate, parse, annotate, gate) and dossier generation + presentation (phases 2–4: rank, write, refresh, present), each 4–5 phases and independently runnable. Split into a process step and a finalize step, or pull the optional Phase 3 (graph refresh) out as a post-write utility.
2. **review-docs — split the ~94-line Phase 2** (Quality/Bloat, High; verified against live file 2026-06-06: Phase 2 spans :61–:156 with 2a Technical Accuracy :66 + 2b Readability :122). Elevate 2a and 2b to top-level Phase 3 / Phase 4 and template the script/skill/path verification blocks.
3. **plugin-health-discover — structural consolidation** (Quality/Bloat, High; accepted 2026-06-05 row 95 — awaiting implementation; recurring, open since 2026-06-04; subject changed via `a9ef0b3` but the nested-Phase-3 structure persists — verified against live file 2026-06-06). 9 top-level sections with Phase 3 nested as 3.1/3.1b/3.2/3.3; fold the cadence guard into Phase 0 and merge resume + dispatch.
4. **sync-documentation-maps-{agent,skill}-{audit,update} — extract oversized Instructions blocks** (Quality/Bloat, High ×4; count-based — re-verify line counts before executing). Each agent's Instructions section runs 43–52 lines. Pair this with the Shared-Backbone Medium suggestion: move the shared procedure into one knowledge doc and reference it from all four agents.
5. **review-documentation-map — split audit from remediation** (Design/Complexity Medium + Quality/Bloat High converge). 7 phases; Phase 4 spans ~70 lines across 4a/4b/4c. `--no-update` already supports audit-only runs — split into an audit step (0–4c) and an apply step (5–6).

## Design suggestions

High:

- **plugin-health-report** (Complexity → Atomise) | 8 phases, two independently-runnable concerns (0–1d processing; 2–4 generation+presentation) | Split process vs finalize, or extract Phase 3 graph-refresh as a utility. *(See top action 1.)*

Medium:

- **review-documentation-map** (Complexity → Atomise) | 7 phases; audit (0–4c) vs remediation (5–6) cleanly separable; `--no-update` already exists | Split into audit + apply skills. *(Converges with the Quality/Bloat High; see top action 5.)*
- **design-skill-lens-near-duplicates** (Model Fit → Remodel) | Multi-file comparative synthesis on haiku | Consider haiku → sonnet. *(Prior sweep judged this lens "clean" for model-fit — severity churn; weigh before acting.)*
- **design-skill-lens-preplanning** (Model Fit → Remodel) | Reads skills + diagram, cross-references downstream, on haiku | Consider haiku → sonnet. *(Same prior-clean churn note.)*
- **design-skill-lens-shared-backbone** (Model Fit → Remodel) | Multi-file pattern synthesis on haiku | Consider haiku → sonnet. *(Same prior-clean churn note.)*
- **sync-documentation-maps-agent-audit** (Model Fit → Remodel) | bash + Python + multi-file JSON aggregation on haiku | Consider haiku → sonnet. *(Not covered by the row-47 decline, which named only the update pair.)*
- **sync-documentation-maps-skill-audit** (Model Fit → Remodel) | Same as agent-audit | Consider haiku → sonnet.
- **docs/al-dev-plugin-synthesis.md** (Handoff Gaps → Extend) | Produced by analyze-architectural-design; consumed by no skill (open since 2026-06-05) | Add a consumer that folds synthesis findings into the dispositions/plan workflow, or accept as a terminal human-read artifact.
- **docs/superpowers/plans/<date>-<topic>.md** (Handoff Gaps → Extend) | Produced by plan-health-findings; chain ends at manual implement | Add a skill that reads accepted plan tasks, dispatches implementation agents, and tracks completion. *(Overlaps prior decline rows 79–80 — post-commit orchestration deferred to a dedicated design pass; revisit there, not by re-sweep.)*
- **sync-documentation-maps audit/update agents** (Shared Backbone → Connect) | Structurally identical background-dispatch pattern across `/sync-documentation-maps` and `/sync-documentation-maps-collect`; not canonicalized in one doc (open since 2026-06-05) | Document the unified dispatch skeleton once and cross-link both skills. *(Check whether checkpoint-patterns.md / collect-dispatch-patterns.md already cover this before adding a third doc.)*

Low:

- **naming-convention-lens** (Tool Hygiene → Trim) | `Glob` declared, unused in body (open since 2026-06-04) | Trim `Glob` or add the intended glob usage.
- **profile-al-dev-shared/generated/agents/** (Handoff Gaps → Extend) | Produced by projection-sync; no downstream skill validates the projections | Add a lightweight projection-vs-source validation skill.
- **docs/al-dev-workflow-diagrams.md** (Handoff Gaps → Extend) | Produced by diagram-generator / sync-write; consumed by no skill | Optional diagram-consistency check against upstream maps.

Monitor-only (excluded from counts): scope-isolation, caller-alignment, usage-patterns, near-duplicates, preplanning lenses all clean for their own dimension this sweep.

## Quality findings

High:

- **sync-documentation-maps-agent-audit** (Bloat) | Instructions (Steps 1–6) > 30 lines | Extract procedure to a knowledge doc. *(Count-based — re-verify.)*
- **sync-documentation-maps-agent-update** (Bloat) | Instructions ~43 lines | Extract procedure to a knowledge doc. *(Count-based.)*
- **sync-documentation-maps-skill-audit** (Bloat) | Instructions ~52 lines | Extract procedure to a knowledge doc. *(Count-based.)*
- **sync-documentation-maps-skill-update** (Bloat) | Instructions ~43 lines | Extract procedure to a knowledge doc. *(Count-based.)* *(All four pair with the Shared-Backbone Connect suggestion — see top action 4.)*
- **plugin-health-discover** (Bloat) | 9 sections; nested Phase 3 (accepted row 95, recurring open since 2026-06-04) | Consolidate. *(See top action 3.)*
- **review-documentation-map** (Bloat) | Phase 4 ~70 lines across 4a/4b/4c | Elevate sub-phases. *(See top action 5.)*
- **review-docs** (Bloat) | Phase 2 ~94 lines (2a + 2b) | Split sub-sections. *(Verified; see top action 2.)*

Medium:

- Bloat (skills): **sync-documentation-maps-apply** (Phase 3 repeats file-validation 3×), **sync-documentation-maps-collect** (Phase 4 parallels /sync Phase 4), **sync-documentation-maps** (checkpoint JSON field tables enumerated twice), **sync-documentation-maps-write** (four near-identical regeneration blocks), **plan-health-findings** (downgraded from lens-High: 7 top-level sections — lens claimed "10+"; Phase 2 ~35 lines — extract Phase 2b).
- Clarity (agents): **design-agent-lens-caller-alignment** ("dispatch line **and** context block" co-occurrence ambiguous), **naming-convention-lens** (`plugin` \| `tooling` pipe set-notation), **quality-agent-lens-clarity** (own `<placeholder>` meta-notation risks self-flagging), **quality-skill-lens-clarity** (same), **sync-documentation-maps-agent-audit** (`(none)` literal normalization, type-mismatch risk), **sync-documentation-maps-skill-audit** (`sed … <SKILL.md> | grep` pipe-before-filename).
- Clarity (skills): **al-dev-consolidate** ×2 (inconsistent dir-name backticks; "same session date" matching undefined), **audit-knowledge-quality** ("Explore subagent" not a named agent type here), **plugin-health-discover** ×2 (`single_use_agents` zero-use inclusion; "right of an edge" Mermaid ambiguity), **plugin-health-report** ("repeats" vs "match on substance" terminology), **record-health-dispositions** (`← implemented`/`← completed` markers undefined), **review-documentation-map** (node-ID grep doesn't state quoted IDs unsupported), **sync-documentation-maps-apply** ("Exit 1 or other: runtime error" undefined), **sync-documentation-maps** ("Abandoned runs" cites history without a defined rule).
- Description (skills): **audit-knowledge-quality** ("targeted fixes" scope), **fix-knowledge-quality** ("converts findings into a task list" — task block originates in audit), **plan-health-findings** (omits `--skills`/`--agents` routing), **plugin-health-discover** (does not say it writes RAW findings, not the dossier), **review-docs** ("archived path references" check absent from description), **sync-documentation-maps-collect** (omits Resume/Restart + `--wait`), **sync-documentation-maps** (omits Phase 0 cadence guard + `--force`).

Low:

- Bloat: **analyze-architectural-design** (inline synthesis protocol overlaps /plan-health-findings rubber-duck).
- Clarity (agents): **design-agent-lens-caller-alignment** ("potential High" — drop "potential"), **design-skill-lens-preplanning** (substring-match else clause), **sync-documentation-maps-agent-audit** ×2 ("not a failure" double negative; relative `ls` path).
- Clarity (skills): **al-dev-diagram-generator** ("partial edge" undefined).
- Description (agents): **design-agent-lens-caller-alignment** (description omits skills-dir grep), **sync-documentation-maps-agent-update** + **-skill-update** (description says writes `docs/al-dev-*-map.md`; body writes to `<result_dir>/updates/` staging — open since 2026-06-05; verify the agents' own description fields).
- Description (skills): **sync-documentation-maps-write** (omits "maintainer guide" from regenerated list), **sync-documentation-maps-apply** ("applies" omits Phase 3 validation).
- Name-fit (skills): **sync-documentation-maps** (name implies single sync; it dispatches audit agents + writes checkpoint — front-load in description, don't rename family), **review-maps** (name suggests inspection; it is a mode-selection router — clarify in description).
- Structure (agents): code-block language tags (MD040) on **design-skill-lens-surface-placement**, **sync-documentation-maps-agent-audit**, **-agent-update**, **-skill-audit** — batch fix.
- Structure (skills): pervasive MD040 missing code-block language tags across ~19 files (batch — verify against markdownlint config first; prior row 75 found some fences already tagged); **al-dev-diagram-generator** Phase/Sub-step numbering inconsistency; **align-harness-repos** uses "Step N" instead of "Phase N".

## Naming violations

*No issues found.* (Grandfathered suppressions honored: align-harness-repos name, workflow-phase family names, sync family, plan-health-findings.)

---

### Stale (dropped) — verified against live files 2026-06-06

- **plugin-health-discover** Phase 2 verb-overlap / "circular Phase 1 forward-reference" (clarity-skill High) — not reproduced: `plan-health-findings` Phase 1 (`:82`) and the design/agent verb vocabularies (`:63`, `:69`, `:96`) are clearly delineated.
- **plan-health-findings** `FILTER_TYPE` one-vs-many ambiguity (clarity-skill High) — already specified at `:121–122` ("set `FILTER_TYPE=all` and process all").
- **quality-agent-lens-bloat** self-finding "6 top-level sections at the >6 threshold" (bloat-agent High) — false: 6 is not greater than 6.

### Dispositioned (suppressed)

- **sync-documentation-maps-agent-update / -skill-update** model upgrade haiku → sonnet — declined, row 47 (the hardest synthesis was moved into generator scripts by `3da3c72`/`a365db9`). The two *audit* agents are not covered by this row and remain ranked.
