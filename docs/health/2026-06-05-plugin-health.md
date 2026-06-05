# Plugin Health — 2026-06-05

Surface: `profile-al-dev-shared/` (23 agents, 22 skills). 22 lenses dispatched.
Source findings: `docs/health/2026-06-05-plugin-findings.md`.

Re-sweep note: this dossier replaces the earlier 2026-06-05 dossier. It was
generated **after** today's fix wave (dispositions rows dated 2026-06-05), so
every High finding and top-5 candidate was spot-checked against the live file;
stale lens re-flags of already-fixed text were dropped, not ranked.

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 0      | 8       | 0      | 8     |
| Medium   | 7      | 39      | 0      | 46    |
| Low      | 5      | 31      | 1      | 37    |

New this sweep: 87 · Recurring from prior sweeps: 4 (annotated inline) ·
Stale (dropped): 22 · Dispositioned (suppressed): 8

Failed lenses: none (22/22 returned).

Top 5 ranked actions:

1. **al-dev-commit-lint-fixer — implement the `.git/` baseline fallback before the write loop** (Quality/Clarity, High; verified against live file 2026-06-05). The Step 1 bash writes to `.git/.commit-baselines` unconditionally; the `.dev/commit-baselines` fallback is stated after the block but never implemented. Compute `BASELINE_FILE` first, then write.
2. **al-dev-plan-swarm-validate — resolve name vs behavior** (Quality/Name-fit, High; verified against live file 2026-06-05). The description (post-76b0c5b) says "Generate a draft implementation plan … then red-team it"; the name says only "validate". Rename (e.g. `al-dev-plan-critic-review`) or re-scope.
3. **al-dev-commit — structural consolidation** (Quality/Bloat, High; recurring, open since 2026-06-04). 18 top-level Step/Phase headers. The dispatch-frame aspect was fixed (e0ea5eb); the header/verbosity aspect remains.
4. **al-dev-plan-preflight — consolidate the three resume modes** (Quality/Bloat, High). Modes A/B/C repeat near-identical file-loading; one decision tree + shared loading step.
5. **al-dev-commit-executor — fix internal heading** (Quality/Description+Name-fit, Medium; verified against live file 2026-06-05, line 14). Heading still reads `# Agent: al-dev-commit-agent (Execute Phase)` after today's rename (319e4c7). One-line fix; corroborated by two lenses.

## Design suggestions

Medium:

- **al-dev-support-researcher** (Tool Hygiene) | MCP tools declared but invocation patterns not documented in body | Document MCP call usage or cross-reference a knowledge file.
- **al-dev-release-notes-writer** (Tool Hygiene) | `MCP: al-mcp-server` declared; usage described only as "using AL MCP Server" | Document invocation or cross-reference knowledge. *(Pairs naturally with the researcher fix — one knowledge doc could serve both.)*
- **al-dev-commit-hook-fixer** (Scope Isolation → Split) | Diagnosis/classification vs recovery execution are separable | Optional split into diagnostics + recovery agents.
- **al-dev-release-notes-writer** (Scope Isolation → Split) | Diff extraction/analysis vs notes composition | Optional analyzer/composer split.
- **al-dev-support-reply-drafter** (Caller Alignment) | RESEARCHER_FINDINGS could be clearer as a required inline structured block | Clarify Inputs wording.
- **al-dev-docs-writer** (Caller Alignment) | Required inputs are glob-located by the agent, not passed explicitly — not stated | Clarify auto-location in Inputs.
- **Post-develop documentation chain** (Handoff Gaps → Extend) | Code-review artifact from /al-dev-review-develop is consumed by no skill; /al-dev-document never suggested downstream | Suggest /al-dev-document at Phase 6, or have /al-dev-document read the latest code-review artifact.

Low:

- **al-dev-commit-message-drafter** (Caller Alignment) | MANIFESTS not marked required | Add marker.
- **al-dev-support-researcher** (Caller Alignment) | TICKET_FILE availability inconsistent between Inputs and role text | Reconcile.
- **al-dev-general-code-reviewer** (Caller Alignment) | No skill dispatches it (open since 2026-06-04, was Medium) | Standalone-use is documented in the agent map; either mirror that note in the agent file or wire it in.
- **al-dev-explore** (Shared Backbone) | Agent map lists /al-dev-handoff as spawner but handoff only consumes findings (open since 2026-06-04, was Medium) | Verify and correct the map's Spawned-by field.
- **Perf → fix handoff** (Handoff Gaps) | Standalone /al-dev-perf ends with a soft next-step prompt | Make the /al-dev-fix vs /al-dev-plan suggestion explicit in the presentation step.

Monitor-only / low-confidence (excluded from counts): surface-placement Move flags on al-dev-plan-final-review, al-dev-plan-preflight, al-dev-review-develop-preflight, verify-commits — deliberate distributed lifecycle phase-family members; this lens's known false-positive class (also flagged 2026-06-03/04). Model-fit and usage-patterns lenses: no candidates. Complexity, near-duplicates, preplanning: clean.

## Quality findings

High:

- **al-dev-commit-lint-fixer** (Clarity) | `agents/al-dev-commit-lint-fixer.md:38-44` — baseline write precedes the `.git/` existence fallback; fallback never implemented in code | Compute `BASELINE_FILE` conditionally before the loop. *(verified against live file 2026-06-05)*
- **al-dev-plan-swarm-validate** (Name-fit) | Name implies validation; description+body generate a draft plan then red-team it | Rename or re-scope. *(verified against live file 2026-06-05)*
- **al-dev-commit** (Bloat) | 18 top-level Step/Phase headers (open since 2026-06-04; dispatch-frame aspect fixed in e0ea5eb) | Consolidate into 5 phase groups. *(count-based; re-verify counts before executing)*
- **al-dev-develop** (Bloat) | 9 top-level phases; Phase 4 Output section redundant with Phase 4 completion | Consolidate Phase 4. *(count-based)*
- **al-dev-fix** (Bloat) | Decision Tree section duplicates Implementation Steps routing | Fold Decision Tree + How-This-Works into Implementation Steps. *(count-based)*
- **al-dev-plan-preflight** (Bloat) | Resume Modes A/B/C near-identical file-loading | One decision tree + shared loader. *(count-based)*
- **al-dev-plan** (Bloat) | Phases 2–4 restate the architect contract and evidence rules | Extract shared architect-contract block; merge Phases 2+3. *(count-based)*
- **al-dev-ticket** (Bloat) | Steps 1/1.5 both resolve ticket input; Phase 5 repeats Phase 0.5 mode branching | Consolidate resolution + centralize mode logic. *(count-based)*

Medium (agents):

- Bloat: **al-dev-developer-tdd**, **al-dev-developer-traditional** (residual SYMBOL_PREFLIGHT_GATE phrasing duplicated at ~:54/:82/:117 after 804b0e1 dedup), **al-dev-commit-message-drafter** (externalize gitmoji table), **al-dev-commit-recover-fixer** (report format undefined inline), **al-dev-docs-writer** (guidelines externalize), **al-dev-support-reply-drafter** (Step 1.5 tangent), **al-dev-ticket-context-writer** (Step 1.5 placement).
- Clarity: **al-dev-commit-executor** (success/else sequencing), **al-dev-commit-hook-fixer** (approved-fixes file fallback), **al-dev-commit-recover-fixer** (report format), **al-dev-diagnostics-fixer** (default rule for rules outside the judgment table), **al-dev-docs-writer** (RTM-guide-missing fallback), **al-dev-support-researcher** (verified/unverified markers vs opaque MCP output), **al-dev-ticket-context-writer** (env-var expansion not explicit in curl examples).
- Description: **al-dev-commit-executor** (internal heading `al-dev-commit-agent` + no upstream-completion precheck — heading verified live :14), **al-dev-commit-recover-fixer** (date-format inconsistency %Y-%m-%d vs YYYY-MM-DD), **al-dev-ticket-context-writer** (Inputs table omits FRESHDESK_API_KEY/FRESHDESK_DOMAIN env-vars).

Medium (skills):

- Bloat: **al-dev-document** (spawn/wait/refine repetition), **al-dev-help** (mode logic triplication), **al-dev-investigate** (regression-timeline restated).
- Clarity (12 surviving verification/suppression): **al-dev-commit** (define "explicitly approved"), **al-dev-develop** (partition-ownership rule; autonomous-mode marker at Phase 4), **al-dev-explore** + **al-dev-lint** (spawned agent not named — verify, some skills name agents via knowledge refs), **al-dev-fix** (three complexity vocabularies un-reconciled), **al-dev-handoff** (incomplete glob pattern), **al-dev-interview** (token-validation step), **al-dev-investigate** (unknown regression-window guidance), **al-dev-plan** ("meaningfully different" lacks operational test — downgraded from High, partial definition exists at :140-143; TESTABILITY_COMPLETE cross-ref), **al-dev-review-develop-preflight** (dedup rule; eval order), **al-dev-review-develop** (empty severity tiers), **al-dev-support-reply** (latest-file tiebreak).
- Description: **al-dev-review-develop** (preflight prerequisite absent from description), **al-dev-commit** (atomic-grouping confirmation), **al-dev-document** (optional ancillary outputs unlisted).
- Structure (argument-hints): **al-dev-commit** `[--ticket-id=<id>]`, **al-dev-develop** add scope-override, **al-dev-plan-preflight** normalize, **al-dev-plan** confirm `--resume-from=phase2` is the only value.

Low (31): 10 agent-clarity qualifier/fallback items (incl. `$AL_DEV_SHARED_PLUGIN_ROOT` in al-dev-release-notes-writer — open since 2026-06-04, was Medium); al-dev-developer-tdd gate-timing description; al-dev-al-pattern-reviewer + al-dev-commit-hook-fixer name-fit notes; agent structure convention question (semantic headers vs numbered phases — ONE decision, not 22 fixes; lens flagged ~22 agents); 13 skill-bloat minor items; al-dev-plan-swarm-validate emoji; al-dev-investigate name note; skill structure (residual language-tag batch — verify a sample first, this lens previously re-flagged MD040-clean files — plus al-dev-help numbering).

## Naming violations

- **commit-recover** | Low | Skill name is `{object}-{verb}`; convention's verb-first rule and grandfather list don't mention it | Add to grandfathered exceptions (likely) or rename to `recover-commits`. *(Note: the convention doc primarily governs maintainer tooling — confirm scope applies to distributed skills before acting.)*

Dropped as false positives: six dated-artifact output paths (`…-al-dev-plan-solution-plan.md` etc.) flagged against the maintainer naming convention — they match the established distributed-artifact convention documented in project instructions.

## Graph deltas

See `docs/al-dev-plugin-graph.md` (regenerated this run). Known map deltas surfaced by lenses: al-dev-explore "Spawned by /al-dev-handoff" likely overcounts (consumer, not spawner).

---

### Stale (dropped) — verified against live files 2026-06-05

al-dev-plan-preflight substantive-answer (05e4dc3); al-dev-solution-architect TESTABILITY clarity (2d83dab/630d91f) and research-phase bloat (5fff2c7); al-dev-fix simple-branch else (:189 present); al-dev-commit 0.2.1 else-branch (:96 present); al-dev-develop "required external procedure" (single use at :184); al-dev-investigate "testable" (defined :142); al-dev-perf modifier stacking (single classification :111); al-dev-interview five-categories clarity (4a81c4b, recovery logic live :87-91) and bloat (row 54 adjudicated); al-dev-commit-hook-fixer bloat (0200d9e; CRITICAL ×1); al-dev-commit-lint-fixer bloat (99c4d95; CRITICAL ×1); al-dev-commit-analyzer $REPO (row 67); al-dev-explore narrowing thresholds (row 58); 6 naming output-path flags (convention misapplied); 7 language-tag flags on row-66 skills (previously verified MD040-clean).

### Dispositioned (suppressed)

al-dev-support-reply-drafter Split (declined, row 72); developer routing shared-backbone (row 52 — already canonical in developer-invocation-patterns.md); post-commit release handoff (declined, row 70); al-dev-ticket FD precedence (rows 26/43 — third lens re-flag); al-dev-support-reply-drafter model downgrade (declined, row 36); commit-recover/help/document/release-notes clarity items (row 63); al-dev-plan-final-review description drift (row 64, e9622f2).
