# Audit Friction Analysis — 2026-06-05

Plan: `docs/health/2026-06-05-audit-friction-analysis-plan.md`
Status: **Complete (Phases 1–5).** Final prioritized backlog in §21–23;
everything above it is the evidence trail.

Inputs: `2026-06-04-plugin-findings.md` / `-tooling-findings.md` (and the
2026-06-03 pair for duplicate detection), all dossiers 2026-05-31 →
2026-06-04, git history. All commit hashes and key classifications below
were spot-verified against the live repo (10+ checks; corrections from
spot-checks are listed in §6).

## 1. Timeline of 2026-06-04 (reconstructed)

| Time | Event |
| --- | --- |
| 14:18–14:41 | Afternoon fix batch — 7 commits (`c065363`…`c0e6c77`), incl. ticket precedence (`966d81b`), plan-swarm-validate description (`76b0c5b`), and the structure-lens alias fix (`c0e6c77`) that eliminated the prior day's 26 false positives |
| 15:21–19:19 | Docs/maps sync (`2114ad3`, `2ab2811`) |
| 19:43–19:54 | **Health sweep ran** — findings + dossiers written (currently uncommitted) |
| 20:11–20:38 | Evening fix batch — 9 commits (`d8146e0`…`e0ea5eb`) fixing 6 of the sweep's 10 top-ranked actions within an hour of the dossiers |

Two structural consequences:

1. The 19:43 sweep **re-flagged at least one item fixed at 14:32** —
   `al-dev-plan-swarm-validate` "body is pseudo-code only" was ranked
   plugin top-5 action #5, but the body had six concrete numbered steps
   five hours before the sweep (verified live). Intra-day stale input.
2. The dossiers were never annotated after the 20:11–20:38 fixes, so they
   now **overstate open work**: 6 of 10 top-ranked actions are already
   resolved, invisible to any reader of the dossier.

## 2. Noise floor — tooling surface (62 findings)

| Classification | Count | % | Notes |
| --- | --- | --- | --- |
| actionable | 48 | 77% | includes sync-write status guard — real bug at sweep time, fixed 20:11 (`d8146e0`) |
| false-positive | 9 | 15% | all surface-placement "Move to `.claude/skills/`" for files already there |
| monitor-only | 2 | 3% | complexity Highs whose own verdict is "Not an Atomise candidate" |
| duplicate-of-prior-sweep | 2 | 3% | sync audit-agent grep/dedup pair, open since 06-03 |
| stale-input | 1 | 2% | naming-convention-lens caller-alignment — `convention_doc` wiring updated 19:03, sweep claim predates it |

Outright noise (FP + monitor + stale): **12/62 = 19%**. Both
dossier-disclaimed noise blocks confirmed against live paths.

## 3. Noise floor — plugin surface (127 object×lens findings; dossier rolls up to 106)

| Classification | Count | % | Notes |
| --- | --- | --- | --- |
| actionable (new this sweep) | 78 | 61% | concentrated in Bloat and Structural Conventions |
| duplicate-of-prior-sweep | 49 | 39% | re-discovered from 06-03, mostly identical severity |
| false-positive / stale-input | ≥1 (undercounted) | — | `al-dev-plan-swarm-validate` top-5 item verified wrong against live file; classifier did not deep-verify plugin claims — full adjudication deferred to Phase 2 |

Caveats: granularity delta (127 vs 106) is rollup of paired objects and
clustered structural fixes, reconciles within ~2%. Duplicate matching was
by (object, lens) presence in the 06-03 findings; severity-churn cases
(below) confirm these are the same findings re-scored.

## 4. Per-lens precision (actionable ÷ total, 2026-06-04)

Worst offenders, both surfaces combined:

| Lens | Surface | Total | Actionable | Precision |
| --- | --- | --- | --- | --- |
| design-skill-surface-placement | tooling | 9 | 0 | **0%** |
| quality-agent-structure (agents) | plugin | 5 | 0 | 0% (all 06-03 re-discoveries) |
| design-agent-caller-alignment | plugin | 5 | 0 | 0% (all re-discoveries) |
| naming-convention-lens | tooling | 4 | 0 | 0% (informational/grandfather) |
| design-skill-preplanning | tooling | 4 | 1 | 25% |
| design-skill-complexity | tooling | 7 | 3 | 43% (2 monitor-only Highs) |
| quality-skill-clarity | tooling | 22 | 14 | 64% |
| quality-skill-bloat | plugin | 23 | 18 | 78% |

Plugin-surface "precision" here measures novelty (new vs re-discovered):
the dominant plugin noise mode is **re-discovery without closure
tracking**, while the dominant tooling noise mode is **lens
miscalibration** (hardcoded recommendation, severity/verdict decoupling).

## 5. Recurrence matrix and closure stats (2026-05-31 → 2026-06-04)

25 distinct findings recurred across 2+ sweeps or were resolved post-sweep.
Full matrix retained in the Phase 1 working notes; summary:

| Status | Count | Mechanism |
| --- | --- | --- |
| Resolved | 14 (56%) | 9 commit-backed fixes (evening 20:11–20:38 batch + afternoon batch), 3 renames/archives, 1 description reconciliation, 1 partial-counted |
| Still open | 11 (44%) | 4 bloat extractions, 4 clarity definitions, caller-alignment trio, model-fit decision, grandfathered name |

Longest-lived open items: sync audit-agent grep/dedup ambiguity (3 sweeps),
al-dev-develop Signature/Static bloat (06-01 → 06-04), al-dev-commit
Phase 0 gate (06-01 → 06-04), sync-documentation-maps-collect clarity
cluster (06-01, 06-02, 06-04).

Severity churn (same finding, different severity, no intervening change):
`al-dev-solution-architect` clarity Low→High, `al-dev-perf` bloat
Low→High, `al-dev-plan-preflight` bloat Low→High, plus ~10
Low→Medium upgrades on the plugin surface and 2 downgrades on tooling.
Severity is not stable run-to-run, so sweep-over-sweep severity diffs are
unreliable as a progress signal.

Top-10 ranked actions, post-evening status: **6 resolved** (TESTABILITY
halt `2d83dab`, investigate template `86576bf`, perf template `b02b332`,
sync-write guard `d8146e0`, diagram-gen routing `45f7480`, projection-sync
default `7cebb69`), 3 partial (commit/plan/ticket bloat cluster — dispatch
frame extracted in `e0ea5eb`), 1 was noise (plugin #5, see §1).

## 6. Corrections from spot-checks

1. **sync-write status guard:** classifier called it false-positive after
   reading the post-fix file; git shows `d8146e0` (20:11) fixed a real
   inverted guard. Reclassified actionable-already-fixed. Tooling FP count
   is 9, not 10.
2. **Commit transposition:** the recurrence pass swapped `d8067cc`
   (align-harness-repos path pin) and `d8146e0` (sync-write guard). Both
   exist; attributions corrected above.
3. **Plugin FP undercount:** the plugin classifier reported 0 false
   positives but did not verify claims against live files; the
   plan-swarm-validate top-5 item is verified noise. Plugin FP rate is >0
   and unquantified — Phase 2 must adjudicate the 78 "actionable" plugin
   findings against the post-fix codebase.

## 7. Headline metrics

- **Tooling sweep noise: 19%** outright (FP/monitor/stale), worst lens at
  0% precision for the second consecutive sweep family.
- **Plugin sweep redundancy: 39%** of findings are re-discoveries of the
  prior day's findings, re-ranked as if new.
- **2 of 10 top-ranked actions were noise or near-noise** (plugin #5
  stale/false; tooling #4 grandfathered-name re-litigated).
- **Closure is happening but invisible:** 16 fix commits landed on
  2026-06-04 alone, yet no dossier, findings file, or ledger records which
  findings they closed — so the next sweep will re-discover the remainder
  and re-rank survivors, repeating the cycle.
- **Same-day sweeps consume stale context:** a sweep run 5 hours after a
  fix batch re-flagged fixed items; the freshness gap is hours, not days.
- **Lens-fix precedent holds:** `c0e6c77` (structure-lens alias fix)
  drove 26 FPs → 0 in one sweep — per-lens calibration fixes are cheap
  and verifiably effective.

## 8. Feed-forward to Phases 2–5 (as written at Phase 1; refined in §13)

- Phase 2 (FP root-cause) should add a fourth chain: **ranking promotes
  noise** — both noise top-5 entries passed through ranking with no
  verdict/freshness check.
- Phase 3 (stale data) gains a new instance class: dossiers go stale
  within hours of fix sessions; staleness is bidirectional (sweep reads
  stale code state; readers read stale dossiers).
- Phase 4 (closure) has its measurement: 56% eventual closure but 0%
  recorded closure; 11 findings surviving 2–4 sweeps.
- Phase 5 backlog candidates confirmed by data: surface-placement scoping
  (kills 9 FP/sweep), complexity verdict gating (kills 2 High FP/sweep),
  recurrence ledger (de-noises 39% of plugin volume), post-fix dossier
  annotation or sweep-after-fix freshness gate.

---

## Phase 2 — Root-cause chains and plugin adjudication

All chains below were verified by direct reads of the cited lines (not
agent reports). Plugin adjudication ran as two independent passes
(design+naming, quality) with corrections from spot-checks itemized in §11.

## 9. Root-cause chains (verified)

### Chain 1 — Surface-placement false positives (9/sweep on tooling)

| Step | Mechanism | Evidence |
| --- | --- | --- |
| Lens premise | The lens is defined as plugin-surface-only: its purpose is to find distributed skills to *move into* the maintainer surface | `design-skill-lens-surface-placement.md:3` |
| Signal design | Signal 1 ("references `.claude/`") is inherently true of every maintainer skill — pointed at the maintainer surface the lens converges on flag-everything | lens lines 24–33 |
| Hardcoded output | Recommendation is fixed text `[Move to .claude/skills/]` regardless of input location | lens line 48 |
| Dispatch gap | Dispatch context for this lens is `no_agent_skills` only; no surface field exists anywhere in the chain | `lens-invocation-patterns.md:62`; `plugin-health-discover` Phase 1 (lines 31–40) builds per-surface lists but Phase 3.2 (line 99) passes only the lens's required fields |

Root cause: **the dispatcher applies a surface-specific lens to both
surfaces.** Cheapest fix is in the dispatcher (skip this lens for the
tooling surface), not the lens.

### Chain 2 — Complexity severity/verdict decoupling (2 High/sweep)

| Step | Mechanism | Evidence |
| --- | --- | --- |
| Severity rule violated | High requires "8+ phases **with two clearly separable concerns**" — a skill the lens itself judges "Not an Atomise candidate" fails that conjunction, so the lens broke its own rule | `design-skill-lens-complexity.md:41-42` |
| No structured verdict | Output format is severity, then observation, then fix — no verdict column; the Atomise/Absorb/Not-a-candidate verdict exists only inside observation prose | lens line 55 |
| Aggregator blind | Report parses only the severity token; counts and ranks without reading verdicts | `plugin-health-report/SKILL.md:29-38` |

Root cause: dual — a haiku lens misapplying its own conditional severity
rule, and an output schema with no machine-checkable verdict field for the
aggregator to gate on.

### Chain 3 — No suppression/dedup layer anywhere

- `plugin-health-discover` Phase 4 (lines 158–211): concatenates raw lens
  JSON blocks into the findings file — no filtering, no validation.
- `plugin-health-report` Phase 1–2 (lines 27–38): parse → rank → count.
  No verdict filter, no dedup against prior findings files, no git/freshness
  check, no comparison with the previous sweep.
- Noise detection does happen — but manually, by the dossier author, as
  prose ("Read this first — two large blocks are lens-calibration noise"),
  downstream of the summary counts and invisible to machines.

### Chain 4 — Ranking promotes noise into top-5 actions

- `plugin-health-report/SKILL.md:36-38`: "Pick the top 5 ranked actions" —
  ordering is severity → dimension → object only; nothing verifies a
  finding's truth before promotion.
- Verification is deferred to `/verify-map-suggestions`
  (`plugin-health-report/SKILL.md:96`) — which has never been run (§7).

### Chain 5 — "Intra-day staleness" is actually lens misjudgment (re-interpretation of §1/§6)

Quality lenses receive only file lists and read live files
(`lens-invocation-patterns.md:84-89`). The 19:43 sweep therefore read the
**already-fixed** text of `al-dev-ticket` precedence (fixed 14:22,
`966d81b` — live file has explicit IF/THEN/ELSE at lines 99–103) and
still issued the old complaint, ranked High. The same applies to the
plan-swarm-validate top-5 item (description reconciled 14:32, `76b0c5b`).
These are not stale inputs; they are **judgment failures by haiku lens
agents re-issuing prior complaints against current text**. The freshness
problem from Phase 1 stands for dossier *readers*; the re-flagging
mechanism is lens misjudgment, not stale context.

### Chain 6 — Settled decisions get re-litigated (no decision ledger)

`al-dev-support-reply-drafter` model-fit (Medium, recommend haiku)
contradicts a deliberate sonnet assignment from 2026-06-01 (`3bed965`,
model reassignment commit). Same class: `align-harness-repos` rename
re-flagged after being grandfathered. No lens or report phase consumes any
record of accepted/declined decisions, so every settled judgment re-enters
the dossier as a fresh finding.

## 10. Plugin findings adjudication (recount from source)

Two passes at line-item granularity (design+naming: 32 items; quality: 87
items). Raw tallies, before §11 corrections:

| Pass | valid-open | already-fixed | duplicate | false-positive | monitor-only |
| --- | --- | --- | --- | --- | --- |
| Design + naming (32) | 19 | 0 | 0 | 1 | 12 |
| Quality (87) | 54 | 0 | 7 | 1 | 0 |

## 11. Corrections from spot-checks (Phase 2)

1. **`al-dev-investigate` bloat High → already-fixed.** Adjudicator wrote
   "still inlined in live file"; `86576bf` removed 74 lines, live file
   references `knowledge/investigate-findings-template.md` at line 248.
2. **`al-dev-perf` bloat High → already-fixed.** Same error; `b02b332`
   removed 63 lines, live reference at `al-dev-perf/SKILL.md:135`.
3. **`al-dev-commit` bloat High → partially-fixed.** `e0ea5eb` extracted
   the dispatch frame (589 → 565 lines); Phase 0 gate still inline.
4. **`al-dev-plan` bloat High → partially-fixed.** Architect prompt
   externalized to `knowledge/architect-invocation-patterns.md`
   (referenced at `al-dev-plan/SKILL.md:138`; short checklist remains
   inline at 161–171); Phase 0 resume-mode sprawl unadjudicated.
5. **9 plugin surface-placement findings → contested, not valid-open.**
   The adjudicator accepted all 9 "Move" suggestions at face value; the
   06-04 dossier itself flags them low-confidence because several targets
   (preflights, `verify-commits`) are integral to the distributed
   lifecycle. Substantive accept/decline belongs to the user.
6. **`al-dev-plan-swarm-validate` → contested.** Phase 1 called the top-5
   "body is pseudo-code" claim verified-false (body has six numbered
   steps); the quality adjudicator judges those steps thin enough to count
   as pseudo-code. Genuinely a judgment call — the description-level claim
   was fixed by `76b0c5b`; body depth is a real but separate question.
7. **Model-fit FP reclassified as decision-conflict** (Chain 6) — the
   finding is not factually wrong; it re-litigates a settled choice.

## 12. Revised remaining workload (plugin surface, post-adjudication)

- **High, valid-open: ~8** — `al-dev-solution-architect` symbol-clarity,
  `al-dev-develop` bloat (Signature/Static blocks), `al-dev-plan-preflight`
  bloat + clarity, `al-dev-develop` "block progress" clarity,
  `al-dev-interview` success-evidence clarity, `al-dev-plan`
  success-evidence clarity, `al-dev-ticket` mode-consolidation bloat
  (partial after `966d81b`).
- **Medium, valid-open: ~40** — concentrated in skill clarity and
  description drift; plus the caller-alignment quartet and handoff-gap
  quartet from the design pass.
- **Low: dominated by mechanical structure nits** (code-fence language
  tags across ~22 skills) — one batch fix, not 45 findings.
- **Confirmed noise on the plugin sweep: 2 false positives (both
  lens-misjudgment of already-fixed text), 1 decision-conflict, 12
  monitor-only, 9 contested surface-placement, ~8 duplicates (strict
  essence-matching).**

## 13. Corrections to Phase 1 conclusions

1. **§2 tooling stale-input (1) reinterpreted:** with Chain 5 established,
   the same mechanism question applies — at minimum the class boundary
   between stale-input and lens-misjudgment needs the git timestamp test
   applied per finding.
2. **§3/§7 plugin duplicate rate (39%) is method-dependent and likely
   overstated as stated, but understated by essence-matching:** Phase 1
   matched on (object, lens) presence in the 06-03 file (over-counts:
   different issues on the same object collapse); Phase 2 matched on
   strict issue essence (under-counts: rephrased same-issue findings
   escape). True redundancy lies between 8 and 95 of ~120 line items —
   establishing it precisely requires a per-finding diff, which is only
   worth doing if the recurrence-ledger fix (§14) is declined.
3. **§1/§6 "intra-day stale input" reinterpreted as lens misjudgment**
   (Chain 5). The headline stands — sweeps within hours of fix batches
   re-flag fixed items — but the fix is lens-side QA, not input freshness.

## 14. Refined Phase 5 backlog candidates (evidence-complete)

1. **Dispatcher scoping:** skip `design-skill-lens-surface-placement` for
   the tooling surface (`plugin-health-discover` Phase 3.2). Kills 9
   FP/sweep. One-line change.
2. **Structured verdict field:** add a `verdict` column to complexity-lens
   output (`Atomise|Absorb|None`); report phase drops or downgrades
   `None`-verdict findings. Kills the 2 High FPs and makes Chain 2
   machine-checkable.
3. **Recurrence ledger:** report phase diffs findings against the prior
   findings file and annotates repeats with "open since YYYY-MM-DD"
   instead of re-ranking as new. Addresses the 8–95 duplicate band and
   severity churn (§5).
4. **Decision ledger:** a small accepted/declined/grandfathered list
   (object + decision + date) consumed by the report phase to suppress
   re-litigation (Chain 6 class, includes align-harness-repos rename).
5. **Lens judgment QA:** the two confirmed plugin FPs were haiku lenses
   re-issuing stale complaints against fixed text. Options: spot-check N
   High findings against live files before ranking (report phase), or
   escalate clarity/description lenses to sonnet. Data so far: 2 FP /
   ~50 clarity+description findings ≈ 4% — cheap spot-check beats model
   escalation.
6. **Dossier post-fix annotation:** when fix commits land same-day, append
   a resolution block to the dossier (finding → commit) so readers don't
   work from overstated dossiers (§1 consequence 2).

---

## Phase 3 — Stale-data provenance (verified by direct reads)

### 15. The header count is ownerless

| Actor | Behaviour | Evidence |
| --- | --- | --- |
| Update agent | Explicitly **forbidden** to touch the count: "Replace the `**Last updated:**` value with today's date. Do not change any other part of the preamble line." | `sync-documentation-maps-agent-update.md:57-58` |
| Generator | Refreshes only content inside `<!-- BEGIN/END GENERATED -->` markers; the header sits outside all markers | `docs/al-dev-agent-map.md:5,9,35`; `map_doc_sections.py` (no header logic) |
| Apply gate | Validates artifact existence, ≥100/≥50 line minimums, and the `# AL Dev` header string — no content checks | `sync-documentation-maps-apply/SKILL.md:120-158` |

No component in the pipeline owns the "(N agents)" prose. It can only ever
be fixed by hand, and the update agent's instruction actively preserves the
stale value on every run. Fix: move the count inside a generated marker (a
one-line `len(inv.agents)` for the generator) or amend update-agent Step 4.

### 16. Dual caller-derivation — the oscillation engine

Two independent implementations of "which skills spawn this agent"
disagree by design:

| | Generator | Audit agents |
| --- | --- | --- |
| Scope | `profile-al-dev-shared/` **only** (`map_doc_sections.py:1061`) | Both surfaces, incl. `.claude/skills/` (`sync-documentation-maps-agent-audit.md:72-89`) |
| Matching | Strict: `al-dev-shared:<name>` regex + line-filtered bare refs (`map_doc_sections.py:13-14,330-348`) | Loose: 4 grep patterns incl. bare name anywhere in the file |
| Writes to | Layer 1 catalog table (generated section) | Layer 2 sections, via the update agent |

The cycle that has run 13 times since May 31: audit greps loosely → finds
"callers" → reports `caller_mismatch` → update agent writes them into the
map → **write phase reruns the generator, which regenerates the Layer 1
catalog from its stricter, narrower parse — reverting to "(none found)"** →
next audit re-detects the same 3 mismatches. The three "eternal" agents
each sit exactly in the disagreement zone:

- `al-dev-docs-writer` — real caller is `.claude/skills/fix-knowledge-quality`,
  outside the generator's scan scope.
- `al-dev-explore` — the audit's bare-name grep matches the **same-named
  skill's own frontmatter** (a self-reference, not a dispatch); the
  generator's line filter rejects it.
- `al-dev-script-engineer` — appears in `/al-dev-help`'s reference table; the
  audit grep matches it, the generator's dispatch-context filter does not.

Downstream blast radius: `plugin-health-discover` Phase 2 builds
`caller_map` **from the catalog table** (`SKILL.md:48-53`), so the
catalog's "(none found)" entries feed the caller-alignment lens, which
re-emits the same three findings every sweep, and the dossier's "Graph
deltas" section reports catalog-vs-profile drift — three symptom classes,
one root cause. The fix is a single source of truth for caller derivation
(have the audit call the generator's parser, or have the generator widen
its scope), not more sync runs.

### 17. Field ownership inventory (agent map)

| Field | Written by | Recomputable by | State |
| --- | --- | --- | --- |
| Header date | update agent (Step 4) | trivially | maintained |
| Header count prose | nobody (update agent forbidden) | generator (`len(inv.agents)`) | **ownerless — permanently stale** |
| Layer 1 catalog: model, tools, spawned-by | generator (regenerated each write) | — | generator-owned; **silently reverts update-agent fixes** |
| Layer 2 model/tools/Spawned-by | update agent (from audit JSON) | audit grep | dual-writer conflict with Layer 1 |
| Mermaid diagrams | generator | — | maintained |

The skills map has the same shape (generated diagram + maintained prose
sections); the same ownership audit applies before trusting any field.

---

## Phase 4 — Closure loop and cadence

### 18. How closure actually happens

- **Inter-sweep closure ≈ 0.** Of the recurring High findings first flagged
  2026-06-01, none were resolved before the 06-02 sweep and at most two
  (renames/archives) before 06-04. Sweeps re-ranked the same items three
  times.
- **Closure is burst-mode, post-review.** 16 fix commits on 2026-06-04
  alone (14:18–14:41 and 20:11–20:38), resolving 6 of 10 top-ranked
  actions within hours of the dossier. The working loop is: read dossier →
  fix directly in-session — not the documented loop.
- **The documented loop's verification step has never run** — yet
  `/verify-map-suggestions` contains the best freshness machinery in the
  entire pipeline: its mandatory Phase 1b staleness gate
  (`SKILL.md:101-135`) git-checks every finding's subject file against the
  dossier date and labels `⚠ possibly stale` — exactly the gate whose
  absence caused the Chain 5 noise and the over-stated dossiers. The
  pipeline's only git-aware component lives in its least-used skill.
- **Why it's bypassed:** (a) it fronts a heavy three-skill chain
  (verify → `writing-plans` → execute) for what are often one-line fixes;
  (b) its precondition — "accepted findings" — has no mechanism: nothing
  marks a finding accepted, so the entry state is undefined; (c) the
  direct-fix path is faster and demonstrably works (§18, burst closure).

### 19. Cadence economics

- **Sync pipeline:** 13 dispatches in 5 days (progress.md), 9 completed,
  **4 abandoned (31%)** — audit agents spawned whose results were never
  collected. Each abandoned run is pure cost, and frequency cannot fix the
  §16 oscillation no matter how often it runs.
- **Health sweeps:** ~1 per 1.5 days. The 06-04 plugin findings file
  doubled in size (24KB → 52KB) while its top-5 included one noise item
  and its High/Medium set was 39–75% re-discovery (method-dependent, §13).
  Marginal new signal per sweep is shrinking while per-sweep cost (22
  lenses + dossier) is constant.
- **Sweep-before-execute inversion:** every dossier ends "run
  `/verify-map-suggestions` next", but the next event in practice was
  either a direct fix session (good, §18) or **another sweep** (06-03 had
  two, 06-04 had two counting the superseded run). Sweeps that re-run
  before the prior dossier is dispositioned mostly re-measure known state.

### 20. Phase 3/4 additions to the backlog

- **Item 7 — Single caller-derivation source:** expose the generator's
  edge parser (`map_doc_sections.py`) as the audit's cross-reference tool,
  or widen the generator's scan scope and matching to the agreed
  semantics — then delete the 4-pattern grep from the audit agents. Ends
  the §16 oscillation; supersedes per-run caller fixes.
- **Item 8 — Generator owns the counts:** move the header count into a
  generated marker. One line of Python; permanently retires the 22-vs-23
  class.
- **Item 9 — Content-aware apply gate:** apply phase asserts header count
  == catalog row count == files on disk before copying to docs/.
- **Item 10 — Lightweight disposition step:** after a dossier is read,
  record accept/decline/fixed per finding (one checklist file; doubles as
  the §14.4 decision ledger). Gives `/verify-map-suggestions` its missing
  "accepted" input and gives sweeps a re-rank suppression list.
- **Item 11 — Promote the Phase 1b staleness gate** from
  `/verify-map-suggestions` into `plugin-health-report` (label findings
  whose subject changed since the prior sweep) — reuse the existing bash
  pattern verbatim.
- **Item 12 — Cadence rule:** no new sweep for a surface until the prior
  dossier is dispositioned (Item 10); no new sync dispatch while a prior
  run's artifacts are uncollected (would have prevented all 4 abandoned
  runs).

---

## Phase 5 — Final prioritized backlog

The 12 candidates from §14 and §20 consolidate to 9 (the disposition
ledger absorbs the decision ledger and dossier annotation — one mechanism
serves all three). Ranked by eliminated-noise-per-effort, sequenced in
three waves.

### 21. The backlog

#### Wave 1 — calibration fixes (each ≤30 min; verifiable on the very next sweep)

| # | Fix | Change | Eliminates | Effort |
| --- | --- | --- | --- | --- |
| B1 | Scope surface-placement lens to the plugin surface | `plugin-health-discover` Phase 3.2: skip this lens when surface=tooling | 9 FP/sweep — 15% of all tooling findings (§2, Chain 1) | one line |
| B2 | Structured verdict on complexity lens | `design-skill-lens-complexity.md` output format: add `verdict` column (`Atomise\|Absorb\|None`); `plugin-health-report` Phase 1 drops/downgrades `None` | 2 High FP/sweep (§2, Chain 2); makes severity-rule violations machine-visible | two small edits |
| B3 | Generator owns the header counts | Move the "(N agents)" prose inside a generated marker; emit `len(inv.agents)` in `map_doc_sections.py`; relax update-agent Step 4 wording | The ownerless-count class — 22-vs-23 and all successors (§15) | ~5 lines |
| B4 | Content-aware apply gate | `sync-documentation-maps-apply` Phase 3: assert header count == catalog rows == files on disk | Silent propagation of count drift through a green pipeline (§15) | small |

#### Wave 2 — structural fixes (kill the recurring classes)

| # | Fix | Change | Eliminates | Effort |
| --- | --- | --- | --- | --- |
| B5 | Single caller-derivation source | Expose the generator's edge parser as a CLI the audit agents call (or widen generator scope to both surfaces first, then converge); delete the 4-pattern grep from both audit agents | The §16 oscillation: 3 eternal caller mismatches, the recurring caller-alignment lens findings, the Graph-deltas drift — across BOTH pipelines | medium; highest single payoff |
| B6 | Recurrence annotation in report | `plugin-health-report` Phase 1: diff findings against the prior findings file; annotate repeats "open since YYYY-MM-DD" and exclude them from the new-findings count | The 39–75% plugin re-discovery band (§3, §13); severity churn becomes visible as churn (§5) | medium |
| B7 | Staleness gate in report | Port `/verify-map-suggestions` Phase 1b verbatim (`SKILL.md:101-135`): label findings whose subject file changed since the prior sweep; spot-check labelled Highs before top-5 promotion | Chain 5-class FPs reaching ranked actions (2 of 10 top-5 on 06-04); doubles as the Chain 4 ranking gate | small — the bash already exists in-repo |

#### Wave 3 — process loop (needs B6/B7 in place to pay off)

| # | Fix | Change | Eliminates | Effort |
| --- | --- | --- | --- | --- |
| B8 | Disposition ledger | One file (e.g. `docs/health/dispositions.md`): finding → accepted / declined / grandfathered / fixed (commit). Report phase suppresses declined+grandfathered; dossier readers see fixed; `/verify-map-suggestions` gets its "accepted" input | Decision re-litigation (Chain 6: model-fit, align-harness-repos rename); overstated dossiers (§1); 0%-recorded closure (§18) | small format + consumption hooks |
| B9 | Cadence rules | Two guards: `plugin-health-discover` Phase 0 warns if the prior dossier has no dispositions; `sync-documentation-maps` Phase 0 refuses dispatch while a prior run is uncollected | Re-measurement sweeps (§19); the 31% abandoned sync runs (§19) | small |

### 22. Dependencies and explicit non-actions

- B9 depends on B8 (disposition is what "dispositioned" means); B7's
  spot-check leans on B6's prior-findings diff. Everything in Wave 1 is
  independent and parallel.
- **Not proposed:** escalating lens models (2 FP / ~50 judgment findings ≈
  4% — B7's spot-check is cheaper, §14.5); re-splitting
  review-documentation-map (its High was a Chain 2 artifact); acting on
  the 9 contested plugin surface-placement "Move" items (user disposition
  required — B8 is where that decision gets recorded); a precise
  duplicate-rate count (§13 — B6 makes the question moot).
- The ~8 High + ~40 Medium valid-open *content* findings (§12) are
  deliberately out of scope here — they flow through the normal
  fix path once the measurement system stops lying about them.

### 23. Empirical verification

Precedent: `c0e6c77` drove the structure lens from 26 FPs to 0 in one
sweep — calibration fixes are verifiable this way.

1. After Wave 1: run `/plugin-health-audit --surface tooling`. Acceptance:
   0 surface-placement findings; 0 High complexity findings carrying a
   `None` verdict; summary counts exclude both classes.
2. After B3+B4: run one full sync cycle. Acceptance: agent-map header
   reads "(23 agents)" (or current disk truth) and apply fails loudly if
   forced out of sync.
3. After B5: two consecutive sync audits report **0** caller_mismatch
   discrepancies for docs-writer / explore / script-engineer, and the next
   plugin sweep's caller-alignment lens no longer emits the trio.
4. After B6+B7: next plugin dossier separates "new" from "open since" in
   its summary; no top-5 action whose subject file post-dates the finding
   without a spot-check note.
5. After B8+B9: `align-harness-repos` rename and the support-reply-drafter
   model-fit item appear in dispositions, not in the next dossier; zero
   uncollected sync runs over the following week.

### 24. Closing note

The original framing — "false positives and stale data" — resolves into
three precise defects: two miscalibrated lenses dispatched out of scope
(Chains 1–2), two pipelines deriving the same fact with different logic
and overwriting each other (§16), and a measurement system with no memory
of its own prior output or of decisions taken (Chains 3–6, §18). None of
the heavy options (more sweeps, more sync runs, bigger models) addresses
any of them; all nine backlog items are calibration, ownership, and ledger
fixes. The plugin surface itself is healthier than its dossiers suggest:
after adjudication, the real open workload is ~8 High and ~40 Medium
items, several of which were fixed within hours of being reported.
