# Tooling Health — 2026-06-07

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 0      | 6       | 0      | 6     |
| Medium   | 0      | 15      | 0      | 15    |
| Low      | 0      | 23      | 4      | 27    |

New this sweep: 47 · Recurring from prior sweeps: 1 (annotated inline) ·
Stale (dropped): 9 · Suppressed (declined/grandfathered): 15

**Failed lenses:** None

### Stale (dropped)

The following findings were dropped after confirming the subject changed after the
findings were generated and the claim no longer holds:

- **sync-documentation-maps-write** | High | Bloat: four regeneration blocks — fixed `c1d55ca`
- **plugin-health-report** | High | Bloat: Phase 1b/1c/1d oversized — fixed `2d9d82f`
- **projection-sync** | Medium | Clarity: no timeout for non-response — fixed `7cebb69` (2026-06-04)
- **review-documentation-map** | Medium | Clarity: "normalize the map edit" ambiguous — fixed `73d0684`
- **sync-documentation-maps-apply** | Medium | Clarity: "missed or duplicated" undefined — verified fixed 2026-06-06
- **audit-knowledge-quality** | Medium | Description drift: "targeted fixes" scope — fixed `d3faeac`
- **sync-documentation-maps** | Low | Clarity: `${RUN_ID}` undeclared — fixed `bda1383`
- **sync-documentation-maps** | Low | Description: four-skill sequence omitted — fixed `0de2bf8`
- **sync-documentation-maps-agent-update, -skill-update** | Low | Description: staging-dir target — fixed `d999e38`

### Dispositioned (suppressed)

- **sync-documentation-maps-agent-audit** | High | Bloat: Instructions >30 lines — declined 2026-06-06 (no viable shared extraction)
- **sync-documentation-maps-skill-audit** | High | Bloat: Instructions >52 lines — declined 2026-06-06 (same reason)
- **sync-documentation-maps-collect** | High | Bloat: Phase 1/2 >50 lines — declined 2026-06-06 (already addressed)
- **sync-documentation-maps-apply** | Medium | Bloat: dead Phase 2 branch — declined 2026-06-06 (claim does not hold)
- **sync-documentation-maps** | Medium | Bloat: checkpoint field tables duplicate — declined 2026-06-06 (claim does not hold)
- **sync-documentation-maps-collect** | Medium | Bloat: Phase 4 dispatch duplication — declined 2026-06-06 (already addressed)
- **audit-knowledge-quality** | Medium | Clarity: "Explore subagent" undefined — declined 2026-06-06 (canonical term)
- **plugin-health-discover** | Medium | Clarity: `single_use_agents` zero-use + Mermaid ambiguity — declined 2026-06-06 (claim does not hold)
- **plugin-health-report** | Medium | Clarity: "repeats" vs "match on substance" — declined 2026-06-06 (canonical)
- **sync-documentation-maps-apply** | Medium | Clarity: "Exit 1" undefined — fixed/verified 2026-06-06
- **sync-documentation-maps-agent-audit, -skill-audit** | Low | Structure: code-block language tags — declined 2026-06-06 (fences already tagged)
- **align-harness-repos** | Medium | Name-fit: name implies alignment not validation — grandfathered 2026-06-05
- **analyze-architectural-design, plugin-health-discover, plugin-health-report** | Low | Naming: not verb-first — grandfathered 2026-06-05
- **plan-health-findings** | Low | Naming: name settled after three renames — grandfathered 2026-06-05
- **quality-agent/skill-lens-clarity** | Low | Clarity: placeholder meta-notation self-flagging — declined 2026-06-06

### Top 5 ranked actions

1. **record-health-dispositions** — Clarity: no rule for contradictory batch input; incorrect ledger state is unrecoverable without manual edits. Add: "If any decision contradicts an earlier one in the same batch, ask for clarification before recording."

2. **plugin-health-discover** — Clarity: Phase 1 cadence guard has no else branch — happy path (proceed when dispositions ARE recorded) is undocumented, creating ambiguity every sweep. Add explicit "rows found dated on/after dossier → proceed" branch.

3. **align-harness-repos** — Bloat: Phase 5 token-replacement block (~20 lines) inline in the skill body. Extract token-mapping logic to a reference; reduce to 5-line shell-out with a link.

4. **plugin-health-discover** — Bloat: 9 top-level phases with nested 3.1/3.1b/3.2/3.3 (accepted 2026-06-05 — awaiting implementation). Fold cadence guard into Phase 0; merge resume+dispatch sub-sections.

5. **review-documentation-map** — Bloat: Phase 2 (profile extraction + caller sets, 76 lines) and Phase 2b still inline. Extract to `knowledge/documentation-map-profile-schema.md`.

---

## Design suggestions

_No design lenses dispatched (quality dimension only)._

---

## Quality findings

### Agent quality

#### Bloat (agents)

_No active findings (both High findings suppressed — declined 2026-06-06)._

#### Clarity (agents)

- **design-agent-lens-caller-alignment** | Medium | Line 32-33: "passed context with no dispatch line is also a finding" — severity unstated; dispatch-with-no-context is High but the converse state carries no severity label. Verified against live file post-fix `abe7cf6` — this state is still unspecified. | Add severity label: e.g., "passed context with no dispatch line is a Medium finding (documented contract implies a dispatch was intended)."

- **design-skill-lens-near-duplicates** | Medium | Line 28: "If within 2 of each other" — ambiguous whether this means ±2 difference or a range of size 2. | Define operationally: "phase counts differ by at most 2 (e.g., counts of 5 and 7 qualify)."

#### Description (agents)

_All findings stale (subjects fixed `d999e38` today)._

#### Name Fit (agents)

_No issues found._

#### Structure (agents)

- **design-agent-lens-caller-alignment** | Low | Code blocks at lines 35, 76 lack language tags. | Add language specifiers (bash, regex, or text as appropriate).

- **quality-agent-lens-clarity** | Low | Pseudo-code block (lines 29-32) lacks language tag. | Add `text` tag to clarify intent.

- **quality-skill-lens-clarity** | Low | Pseudo-code block (lines 30-33) lacks language tag. | Add `text` tag.

---

### Skill quality

#### Bloat (skills)

- **align-harness-repos** | High | Phase 5 fix flow exceeds 30 lines (lines 115-132); step 3 contains ~20-line token-replacement block inline. | Extract token-replacement mapping to a reference document; reduce Phase 5 to a ~5-line shell-out with a knowledge link.

- **plugin-health-discover** | High | 9 top-level phases; Phase 3 nested 3.1/3.1b/3.2/3.3. (open since 2026-06-05 — accepted row 95) | Fold cadence guard into Phase 0; merge resume+dispatch into one Phase 3.

- **review-documentation-map** | High | Phase 2 (lines 73-148, ~76 lines) with nested Phase 2a/2b spans profile extraction, caller sets, and deduplication inline. (Phase 4 bloat closed by `95b173a`; Phase 2 is a new finding.) | Extract profile extraction logic to `knowledge/documentation-map-profile-schema.md`; extract caller-set rules to `knowledge/documentation-map-comparison-rules.md`.

- **audit-knowledge-quality** | Medium | Phase 2a (lines 51-68) and Phase 2b (lines 64-84) contain near-identical parallel/sequential decision trees differing only in file count thresholds. | Unify into one decision section with a threshold condition; extract to `knowledge/skill-dispatch-routing.md`.

- **plan-health-findings** | Medium | ⚠ possibly stale — subject changed `c9a34b3` today. Repetitive rubber-duck vocabulary (lines 227-229) and verification pattern table (lines 250-259) duplicate content already in knowledge/ references. | If still present: replace inline vocabulary with a cross-reference to `knowledge/rubber-duck.md`; replace verification table with reference to `knowledge/artifact-contracts.md`.

- **sync-documentation-maps** | Low | Phase 0 comment "Abandoned runs spawn audit agents whose results are never read" is explanatory context. | Remove historical context comment and replace with the operative rule only.

- **record-health-dispositions** | Low | Closure write-back rule (lines 133-156) has dated procedural tone. | Condense to the three-item must-do checklist; move narrative to `knowledge/ledger-closure-protocol.md`.

#### Clarity (skills)

- **record-health-dispositions** | High | Phase 2 has no rule for contradictory batch input (e.g., "accept 1, decline 1" in one message). Incorrect decisions written to the ledger require manual correction. | Add: "If any decision in a batch contradicts an earlier one in the same batch, ask for clarification before recording any row."

- **plugin-health-discover** | High | Phase 1 cadence guard: "If it does not (or the ledger is absent), warn..." — no else branch for when rows ARE found. The happy path (proceed normally) is implicit, creating ambiguity. | Add explicit branch: "If dispositioned rows exist dated on or after the dossier date, proceed to Phase 1 — the prior sweep's work is recorded."

- **plan-health-findings** | High | ⚠ possibly stale — subject changed `c9a34b3`, `2396672` today. Phase 1 defines `--skills`/`--agents` and `FILTER_TYPE` separately but does not state their interaction order (e.g., "apply object-type flag first, then verb filter"). | Verify against live file; if still implicit: add explicit interaction rule with an example (e.g., "`/plan-health-findings --skills connect` keeps only skill-design findings of type 'connect'").

- **align-harness-repos** | Medium | Phase 5: "Flag it for manual review rather than auto-replacing, as the example may be illustrative" — "as the example may be illustrative" is vague; the actual trigger condition (token appears inside a fenced code block) is not stated. | Rewrite: "If the token appears inside a fenced code block (``` delimiters), flag for manual review only — do not auto-replace."

- **audit-knowledge-quality** | Medium | Phase 2a step 2 has no else branch for when no referencing agent or skill exists (orphaned knowledge file). | Add: "If no referencing agent or skill is found, note the file as orphaned with severity LOW."

- **plan-health-findings** | Medium | Phase 1b: "rubber-duck it by reading the live subject file in full first" — "in full" is imprecise (entire file vs relevant section). | Rewrite: "Read the entire subject file from start to finish; check whether the current text still matches the claim in the finding."

- **plugin-health-discover** | Medium | Phase 3.1b: "aimed at files already in the maintainer surface it can only emit false 'Move' findings" — "false" is undefined operationally. | Replace with: "Any 'Move' suggestion against a tooling-surface file is a non-actionable false positive — the file is already in its intended home."

- **review-documentation-map** | Medium | ⚠ possibly stale — subject changed `95b173a` today. Phase 6 (formerly Phase 5 post-restructure): "If everything is accurate, say so and stop" — no explicit else branch for "not accurate AND NO_UPDATE=false". | Verify; if still present: add "Otherwise, proceed to the next phase."

- **sync-documentation-maps-collect** | Medium | Phase 2 has no guard against infinite retry: if re-running collect finds the same surface still pending, the skill gives no recovery instruction. | Add: "If the same surface is still pending on re-run, check for agent failures (exit non-zero) and stop with a failure report."

- **sync-documentation-maps-collect** | Medium | Phase 3: "sort its discrepancies by object name and deduplicate by (object, type)" — sort order and deduplication winner (first vs last) not specified. | Clarify: "Sort alphabetically by object name. For (object, type) duplicates, keep the first occurrence."

- **sync-documentation-maps-write** | Medium | Incomplete conditional: "If the three values differ, stop before Phase 3 and report" — no recovery action specified. | Add: "To recover: re-run `/sync-documentation-maps` from scratch, or manually verify and correct the map if the audit result is a known false positive."

- **align-harness-repos** | Low | Phase 5: `<placeholder>` used as meta-notation without definition. | Add a note: "`<placeholder>` indicates a substitution point — replace with the actual token found."

#### Description (skills)

- **plugin-health-audit** | Medium | Description says it dispatches lenses as a single unit; body reveals it delegates to two sub-skills (`/plugin-health-discover` and `/plugin-health-report`). Users would not expect this internal split. | Revise to: "Dispatches quality + naming lenses via a two-phase internal workflow (discover → report). User invokes `/plugin-health-audit`; sub-phases run transparently."

#### Name Fit (skills)

- **sync-documentation-maps-apply** | Medium | "apply" implies writing; the step also performs validation before writing. The validation gate is invisible to users choosing which skill to run next. | Consider `validate-and-apply` or add a note to trigger phrases that validation occurs here.

#### Structure (skills)

- **sync-documentation-maps-apply** | Medium | `argument-hint` references `RUN_ID` but the body describes `--team-ids` parameter (lines 8, 49). | Update `argument-hint` to match the parameters actually described in the body.

- **align-harness-repos** | Low | Code blocks in Phase 2-4 lack language tags. | Add `bash` for command blocks, `text` for output-only blocks.

- **analyze-architectural-design** | Low | Code block at line 40 lacks language tag (bash command). | Add `bash` tag.

- **audit-knowledge-quality** | Low | Phase headers mix "Phase N" and "Step N" patterns (lines 38, 63-64). | Standardize to "Phase N" throughout.

- **fix-knowledge-quality** | Low | Code blocks in Phase 1 and Phase 3 lack language tags. | Add `bash` and `text` tags.

- **plan-health-findings** | Low | Mixed phase header formats: "## Phase" and nested "### Phase" (lines 84, 128). | Standardize to flat "## Phase N" with no sub-phase headers.

- **plugin-health-discover** | Low | Code blocks at lines 94-101 lack language tags (bash commands). | Add `bash` tags.

- **plugin-health-report** | Low | Code blocks at lines 40 and 65 lack language tags; phase header punctuation inconsistent ("—" vs ":"). | Add `bash` tags; standardize header punctuation to "## Phase N —".

- **projection-sync** | Low | Code blocks at lines 44, 80 lack language tags. | Add `bash` tags.

- **record-health-dispositions** | Low | Code blocks at lines 45-46 lack language tags. | Add `bash` tags.

- **review-documentation-map** | Low | Code blocks at lines 62, 100 lack language tags; nested "### Phase 2b" under "## Phase 2" breaks header hierarchy. | Add `bash` tags; restructure as "## Phase 2a" / "## Phase 2b" or fold into Phase 2 narrative.

- **review-maps** | Low | Code blocks at line 50 lack language tags. | Add `bash` tags.

- **sync-documentation-maps-apply** | Low | Code blocks at lines 125, 169 lack language tags. | Add `bash` tags.

- **sync-documentation-maps-collect** | Low | Code blocks at lines 113-114 lack language tags. | Add `bash` tags.

- **sync-documentation-maps-write** | Low | Code blocks at lines 52, 97, 179 lack language tags. | Add `bash` tags.

- **sync-documentation-maps** | Low | Code blocks at lines 59, 82, 100 lack language tags. | Add `bash` tags.

---

## Naming violations

The following tooling skill names deviate from the `{verb}-{object}-{aspect}` advisory
pattern and are not listed in the grandfathered exceptions. All are Low severity; the
`plugin-health-*` family is the most actionable cluster.

- **plugin-health-audit** | Low | Structure inverted (object-verb-aspect vs verb-object-aspect). | Grandfather the `plugin-health-*` prefix family in `docs/al-dev-naming-convention.md`, or rename to `audit-plugin-health`.

- **record-health-dispositions** | Low | Verb "record" and object "health-dispositions" both outside documented sets. | Add to grandfathered exceptions if the name is intentional.

- **review-documentation-map** | Low | Object "documentation-map" is a compound; pattern uses singular "map". | Rename to `review-map` or add to grandfathered exceptions.

- **review-maps** | Low | Object "maps" is plural; pattern uses singular. | Rename to `review-map` or add to grandfathered exceptions.

---

## Graph deltas

_(Omitted — tooling surface.)_
