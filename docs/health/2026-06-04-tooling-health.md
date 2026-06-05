# Tooling Health — 2026-06-04

Source findings: `docs/health/2026-06-04-tooling-findings.md` (22/22 lenses returned; no failed lenses)
Surface: `.claude/` — 26 agents, 16 active skills (`archived/` excluded)
Suggestions only — no source files were edited. This dossier supersedes the earlier 2026-06-04 tooling run.

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 2      | 12      | 0      | 14    |
| Medium   | 19     | 15      | 0      | 34    |
| Low      | 9      | 2       | 3      | 14    |
| **Total**| **30** | **29**  | **3**  | **62** |

Counts exclude informational "no action required / acceptable" entries returned by lenses.

Failed lenses: none — all 22 dispatched lenses returned results.

> **Read this first — two large blocks are lens-calibration noise, not work:**
>
> 1. **Surface-placement (9 Medium "Move to .claude/skills/").** Every one of these
>    files is *already* in `.claude/skills/`. The surface-placement lens is built to
>    find files in the *distributed* surface that should move *into* the maintainer
>    surface; pointed at the maintainer surface it recommends each file move to where
>    it already lives. Treat all nine as false positives.
> 2. **Design-complexity (2 High).** `review-documentation-map` and
>    `sync-documentation-maps` were flagged on phase count, but the lens's own verdict
>    is "Not an Atomise candidate" for both — monitor-only, not action.
>
> Good news vs last sweep: the `quality-agent-lens-structure` lens that emitted 26
> tooling-agent false positives on 2026-06-03 returned **no issues** this run, and the
> `sync-documentation-maps-wait` skill flagged then has since been renamed to
> `-apply` / `-write`. The genuine new signal is the skill-clarity cluster below.

Top 5 ranked actions:

1. **sync-documentation-maps-write — possibly inverted status guard (Quality/Clarity, High).** Phase 0 reads "Confirm `status` is not `'awaiting-write'`" and then stops when that is true — the logic looks reversed, which would make the skill refuse to run exactly when it should. Verify against the SKILL.md and correct to "confirm status **is** `awaiting-write`; otherwise stop." The only suspected live bug in this surface — do this first.
2. **Sync-doc audit-agent grep/dedup ambiguity (Quality/Clarity, High; repeat from 2026-06-03, still open).** `sync-documentation-maps-agent-audit` and `-skill-audit` Step 3 sequence a grep union + `sort -u` without explicit sub-steps, and mix `<SKILL.md>` placeholders with runnable bash. A correctness risk in script-driven agents. Restructure into 3a/3b/3c with one final dedup and concrete example paths.
3. **Skill control-flow / undefined-placeholder cluster (Quality/Clarity, remaining 8 High).** `al-dev-diagram-generator` (Phase 3 diagram routing), `align-harness-repos` (discretionary "or similar neutral path"), `plugin-health-discover` (`agentType` mapping), `projection-sync` (no Resume/Restart default), `review-documentation-map` (union-grep idiom), `sync-documentation-maps` (parallel-dispatch blocking), `sync-documentation-maps-collect` (Restart-with-absent-artifacts), `verify-map-suggestions` (DOSSIER_DATE + per-task verification map). One-line fix each in the findings file.
4. **align-harness-repos — name no longer matches behavior (Quality/Name-fit, Medium).** The skill validates harness-neutrality via `validate_harness_neutrality.py`; it performs no "alignment." Rename to `validate-harness-neutrality` or make the description state that "align" means "validate alignment to neutrality constraints." Consistent with the earlier `al-dev-align` retirement.
5. **Oversized phases (Quality/Bloat, 2 High + Medium tail).** `plugin-health-discover` Phase 3 (~145 lines, 3 nested sub-steps) and `review-documentation-map` Phase 5 (two-surface edit logic) pack independent steps into one phase; `audit-knowledge-quality` Phase 2 and `verify-map-suggestions` Phases 1–3 are Medium variants. Split into numbered single-responsibility phases.

## Design suggestions

### Remodel (model fit)

- **sync-documentation-maps-agent-update** | Medium | Multi-step synthesis (read audit JSON → read map → apply conditional fixes → write) on haiku. | Assign `sonnet`.
- **sync-documentation-maps-skill-update** | Medium | Same multi-document synthesis profile on haiku. | Assign `sonnet`.
- **sync-documentation-maps-agent-audit / skill-audit** | Low | Grep-based cross-referencing on haiku; lens calls the assignment "acceptable." | Monitor; escalate to `sonnet` only if discrepancy logic grows.
- **Model pinning inconsistency** | Low (carried from 2026-06-03) | The 4 sync-doc agents pin the full id `claude-haiku-4-5-20251001` while the 22 lens agents use the `haiku` alias. | Standardize to the alias.

### Connect / Promote (shared backbone)

- **sync audit-agent pair** | Medium | Identical background-agent dispatch + checkpoint schema copy-pasted between `sync-documentation-maps` and `sync-documentation-maps-collect`. | Document `knowledge/background-agent-dispatch.md` (field names, checkpoint schema, artifact paths); reference from both.
- **sync update-agent pair** | Medium | Parallel update-agent dispatch documented in one external `.md` referenced only once per skill. | Create a canonical dispatch spec both audit and update inherit from; add inline pointers so baseline changes surface at each site.

### Align (caller alignment)

- **naming-convention-lens** | Medium | Documents required input `convention_doc` but is referenced (not dispatched) in `plugin-health-report`; the real dispatcher is `plugin-health-discover`. | Confirm `plugin-health-discover` builds and passes `convention_doc` (this sweep did); reconcile the agent's Inputs table with that single dispatcher.
- **sync audit / update agents** | Low | Inputs tables list `run_id` / `result_dir` as if tool parameters. | Add note: "passed as context in the dispatch prompt, not as separate parameters."

### Atomise / Absorb (complexity)

- **projection-sync** | Medium | Two independently valuable concerns — validate+regenerate (phases 1–2) vs review+commit (phases 3–4). | Atomise candidate: split into `projection-sync-generate` / `projection-sync-commit`, or keep the wrapper auto-invoking both.
- **audit-knowledge-quality** | Medium | Report/offer-fixes phases (3–4) could run on an existing findings file without re-discovery. | Absorb candidate: make the reporting phase a utility callable by both audit and fix skills.
- **plugin-health-audit** | Low | Thin 2-phase pass-through over discover + report. | An optional `--report-after-discovery` flag on `plugin-health-discover` could retire the wrapper. *Low confidence — the wrapper is the documented standing entry point.*
- **review-documentation-map / sync-documentation-maps** | High (monitor only) | Flagged on phase count (12 and 6) but lens verdict is "Not an Atomise candidate" (tightly coupled / single concern). | No split; monitor. **Caveat:** the review-documentation-map family was recently consolidated — weigh any re-split against that merge.

### Extend (handoff gaps)

- **Plan → execution gap** | Medium | `verify-map-suggestions` writes a verified plan, but no skill reads it to execute the changes. | Either add an `execute-plugin-changes` skill, **or** confirm execution is intentionally delegated to generic `superpowers:executing-plans` / `subagent-driven-development` before building one.
- **align-harness-repos orphaned output** | Low | The validator exits with only a console message; no durable pass/fail artifact for downstream gating. | Write `.dev/<date>-harness-neutrality-validation.json` so `projection-sync` / `sync-documentation-maps-write` can gate on it.
- **fix-knowledge-quality** | Low | The show-task-list-only path prints tasks but doesn't persist them to `.dev/`. | Optionally persist as an artifact.
- **al-dev-diagram-generator** | Low | `docs/al-dev-workflow-diagrams.md` has no downstream consumer. | Confirm it is an intended leaf/reference output.

### Document (pre-planning / diagram coverage)

- **No tooling lifecycle diagram** | Medium | The maintainer surface has two real chains (detect → review → verify → plan; audit → fix) but no Layer 1 diagram — `docs/al-dev-skills-map.md` scopes Layer 1 to distributed skills only. | Add `docs/al-dev-tooling-skills-map.md`, or document in CLAUDE.md why tooling is excluded and where to look.
- **plugin-health-discover** | Medium | Active discovery skill, well-named output, absent from any diagram. | Cover it in the tooling diagram if added.
- **plugin-health-audit / audit-knowledge-quality** | Low | Handoff artifacts (`findings.md`, `## High-Priority Fix Tasks` block) not named in the skill descriptions. | Name the produced artifact in each description.

### Trim (tool hygiene)

- **naming-convention-lens** | Low | `Glob` declared in frontmatter but no globbing in the body. | Remove `Glob`, or add the operation if intended. (Also surfaced by description-drift last run.)

### Move (surface placement) — FALSE POSITIVES

Nine skills (`analyze-architectural-design`, `plugin-health-audit`, `plugin-health-report`, `projection-sync`, `review-documentation-map`, `review-maps`, `sync-documentation-maps-apply`, `sync-documentation-maps-write`, `verify-map-suggestions`) were each flagged Medium "Move to .claude/skills/". They are **already** in `.claude/skills/`. Lens misfire when aimed at the maintainer surface — no action. (Consider scoping the surface-placement lens to the distributed surface so it stops emitting these every sweep.)

## Quality findings

### High

- **sync-documentation-maps-write** (skill, clarity) | Phase 0 status guard appears inverted ("not `awaiting-write`" → stop) | Reword to "confirm status **is** `awaiting-write`; else stop." **Likely live bug — verify first.**
- **sync-documentation-maps-agent-audit** (agent, clarity) | Step 3 grep union + dedup not sequenced; pipeline mixes template + concrete paths | Restructure into 3a/3b/3c with one final `sort -u`.
- **sync-documentation-maps-skill-audit** (agent, clarity) | Same union/dedup ambiguity; `<SKILL.md>` placeholder mixed with runnable bash | Use a concrete example path or mark as a per-skill `[name]` template.
- **al-dev-diagram-generator** (skill, clarity) | Phase 2 picks one-vs-two diagrams but Phase 3 has no if/else routing to the matching template | Add explicit routing before the diagram blocks.
- **align-harness-repos** (skill, clarity) | Step 5 permits "~/.harness-config or similar neutral path" (discretionary) | Define exact canonical replacement paths, no discretion.
- **plugin-health-discover** (skill, clarity) | Phase 3.2 references `agentType` without showing the lens-name → agentType mapping | Show a concrete `{agentType, prompt}` example and the mapping.
- **projection-sync** (skill, clarity) | Phase 0 Resume/Restart has no timeout / non-response default | Add a default (e.g. Restart after no response).
- **review-documentation-map** (skill, clarity) | Phase 2b "union all grep results then sort -u" without the bash idiom | Specify `{ grep…; grep…; } | sort -u`.
- **sync-documentation-maps** (skill, clarity) | Phase 3 "dispatch both audit agents simultaneously" — block vs proceed unspecified | Specify `run_in_background: true`, then proceed to Phase 4.
- **sync-documentation-maps-collect** (skill, clarity) | Restart path when audit artifacts are still absent is undefined | Define non-blocking restart + `--wait` retry.
- **verify-map-suggestions** (skill, clarity) | `DOSSIER_DATE` format / `git log --since` acceptance unstated | Specify `YYYY-MM-DD` and the exact `--since` construction.
- **verify-map-suggestions** (skill, clarity) | Phase 3 lists verification commands without mapping pattern → task type | Add a table (Merge → `wc -l`; Move → `ls`; Promote → `grep`; …).

(Skill-bloat Highs — `plugin-health-discover` Phase 3 and `review-documentation-map` Phase 5 — are tracked under action 5 and the Medium bloat list below to avoid double-counting; both are oversized-phase splits.)

### Medium

- **design-skill-lens-surface-placement** (agent, clarity) | "operative" vs "illustrative" path distinction not operationally clear | Add a concrete example of each.
- **Other agent-clarity nits** (agent, clarity) | caller-alignment ("actually invoke"), tool-hygiene ("described as read-only"), near-duplicates (exact vs subset agent-set), preplanning (substring vs exact label), shared-backbone ("identical" threshold), naming-convention ("deviates" severity) | Tighten each qualifier in the lens bodies.
- **plugin-health-discover** (skill, bloat) | Phase 3 ~145 lines, 3 nested executable sub-steps | Split into top-level phases 3/4/5, renumber downstream.
- **review-documentation-map** (skill, bloat) | Phase 5 couples Layer 1 + Layer 2 edit logic plus a style guard | Split into separate Layer 1 / Layer 2 phases.
- **audit-knowledge-quality** (skill, bloat) | Phase 2 nests mutually-exclusive 2a/2b paths with overlap | Flatten into decision + sequential + parallel phases.
- **verify-map-suggestions** (skill, bloat) | Phases 1–3 fragmented; check logic deferred entirely to a knowledge file | Consolidate Phase 2; inline the critical check outline.
- **al-dev-diagram-generator** (skill, clarity) | "short display name" undefined | Define a char/word limit.
- **analyze-architectural-design** (skill, clarity) | "coupling gaps", "cross-surface" lack operative definitions | Define thresholds.
- **audit-knowledge-quality** (skill, clarity) | "thin content", "stub sections" not measurable | Define (e.g. `[THIN]` = ≤3 lines after heading).
- **fix-knowledge-quality** (skill, clarity) | Phase 3 doesn't bound permitted edits | Specify "fill bodies only; no new top-level headings."
- **plugin-health-discover** (skill, clarity) | "Spawned by" containing "(none found)" — handling unstated | Specify parse-as-empty-list.
- **plugin-health-report** (skill, clarity) | "top 5 ranked actions" without ranking criteria | Specify the severity/dimension/object ordering.
- **review-documentation-map** (skill, clarity) | Phase 2a doesn't separate mandatory vs optional fields | Mark phase headers + agent spawns mandatory.
- **sync-documentation-maps** (skill, clarity) | Phase 4 read-first rule unclear for manifest.json | Specify checkpoint + manifest precedence.
- **align-harness-repos** (skill, name-fit) | Name implies alignment; behavior is validation-only | Rename to `validate-harness-neutrality` or clarify the description.

### Low

- **sync-documentation-maps-collect** (skill, bloat) | Checkpoint-lifecycle commentary repeated across sync skills | Move to a shared `checkpoint-patterns.md` and point to it.
- **sync-documentation-maps** (skill, bloat) | `RUN_ID`/`RUN_DIR`/manifest structure repeated across 5 files | Externalize run-context to one document; cross-reference.

## Naming violations

- **analyze-architectural-design** | Low | Compound object-aspect rather than `{verb}-{object}-{aspect}` | Consider `analyze-plugin-architecture` / `synthesize-plugin-design`, or grandfather.
- **plugin-health-discover** | Low | Object-hyphenated-verb, not verb-first; not grandfathered | Consider `discover-plugin-health`, or add to grandfathered exceptions if the workflow-phase family name is intentional.
- **plugin-health-report** | Low | Same pattern deviation | Consider `report-plugin-health`, or grandfather the family name.

No High naming findings. All 22 lens-agent filenames conform to `{design|quality}-{agent|skill}-lens-{aspect}` (with `naming-convention-lens` the allowed exception). No output-path violations.

---

Next step: review this dossier, then run `/verify-map-suggestions` on accepted items to rubber-duck them against the live codebase before planning changes. Start with action 1 (the `sync-documentation-maps-write` status guard) — the only suspected live bug in this surface.
