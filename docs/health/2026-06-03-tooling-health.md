# Tooling Health — 2026-06-03

Source findings: `docs/health/2026-06-03-tooling-findings.md` (21/21 lenses returned; evening re-run of the 2026-06-03 morning sweep against the current tooling surface — 25 agents, 18 active skills).

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 5      | 14      | 0      | 19    |
| Medium   | 16     | 31      | 0      | 47    |
| Low      | 5      | 8       | 0      | 13    |
| **Total**| **26** | **53**  | **0**  | **79**|

Failed lenses: none.

Top 5 ranked actions:

1. **Archive `/sync-documentation-maps-finalize`** — flagged independently by six lenses (complexity, bloat, clarity, description drift, name fit, structure). It is marked deprecated yet remains fully implemented alongside its replacement pair (`-wait` + `-write`), creating conflicting guidance. Move to `archived/` and update workflow references.
2. **Resolve the model assignment for the four sync-documentation-maps agents** — the model-fit lens now rates the two audit agents High for an upgrade to a mid-tier model, but this morning's sweep recommended (and the repo applied) the opposite downgrade to a small model. The lens recommendation has oscillated within one day; this needs a human decision plus a recorded rationale to stop the flip-flop, not a mechanical re-application.
3. **Split `design-skill-lens-complexity` into two agents** (scope isolation, High) — its body carries two unrelated lenses (Complexity Outliers → Atomise/Absorb, and Surface Placement → Move) with separate output formats. Split into `design-skill-lens-complexity` and `design-skill-lens-surface-placement`, and update the dispatcher.
4. **Deduplicate the four sync-documentation-maps agent bodies** (bloat, 4× High) — the audit pair and update pair mirror each other step-for-step (50–90 line procedures). Extract shared audit/update procedures to referenced knowledge documents, parameterized by object type (agent vs skill).
5. **Fix the three High clarity blockers in skills** — `al-dev-map-suggestions-verify` (captures `FILTER_TYPE` but never defines the filtering action), `plugin-health-discover` (contradictory Phase 2→3 sequencing for incomplete background agents), and `sync-documentation-maps-skill-audit` (undefined "minus" set operation blocks runnable execution).

## Design suggestions

### High

- **sync-documentation-maps-agent-audit / -skill-audit** | Model Fit (Remodel) | Lens rates the cross-file audit work as needing a mid-tier model; both currently use a small model. | ⚠ See top action 2: the same lens recommended the opposite direction this morning and that downgrade was applied. Decide once, record the rationale alongside the model assignment.
- **design-skill-lens-complexity** | Scope Isolation (Split) | Two unrelated lenses (Complexity Outliers, Surface Placement) in one body with separate findings blocks and severity rules; separable by deleting one contiguous ~40-line block. | Split into `design-skill-lens-complexity` and `design-skill-lens-surface-placement`; update the dispatcher to invoke both for skill analysis.
- **sync-documentation-maps-finalize** | Complexity (Atomise/Archive) | 9 phases across 3 concerns; explicitly deprecated and superseded by the two-step flow. | Archive the skill; confirm references point to `-wait` + `-write`.
- **plugin-health-discover** | Caller Alignment (Align) | Lens reports the per-lens context contract file as missing. | ⚠ **Verification note:** `profile-al-dev-shared/knowledge/lens-invocation-patterns.md` exists and was read during this sweep; this finding (and the nine Medium findings premised on it below) appears to be a false positive — likely the lens agent failed to resolve the path. Verify before acting; if confirmed false, consider adding an explicit existence-check step to the caller-alignment lens.

### Medium

- **9 lens agents** | Caller Alignment (Align) | Inputs tables (model-fit, tool-hygiene, usage-patterns, complexity, handoff-gaps, near-duplicates, preplanning, shared-backbone, naming-convention) document context fields whose delivery contract allegedly lives in a missing knowledge file. | Same ⚠ verification note as above — the contract file exists; confirm/dismiss these as one batch.
- **design-skill-lens-complexity / -near-duplicates / -handoff-gaps / -shared-backbone** | Model Fit (Remodel) | Multi-file comparative synthesis is borderline for a small model. | Consider a mid-tier model for the four comparative skill lenses (subject to the same oscillation caution as top action 2).
- **align-harness-repos** | Complexity | Detect (steps 1–3) and fix (steps 4–6) phases coupled behind a user gate. | Defensible as-is; split only if detect-only/fix-only usage emerges.
- **al-dev-map-suggestions-verify → plan execution** | Handoff Gaps (Extend) | The vetted implementation plan has no downstream executor; the improvement cycle ends at planning. | Consider a `/plugin-map-execute` skill that reads the latest plan, dispatches fix agents per task, and reports completion.
- **review-documentation-map + review-documentation-map-audit** | Near-Duplicates (Merge) | Parent's `--no-update` flag makes the audit-only skill functionally redundant (6 vs 8 phases, same scan/compare). | Consolidate on the flag, or document the audit skill's distinct use case.

### Low

- **naming-convention-lens** | Tool Hygiene (Trim) | Declares a glob/pattern-matching tool never exercised in the body. | Remove it or add an explicit pattern-matching step.
- **docs/al-dev-plugin-synthesis.md** | Handoff Gaps | Synthesis doc is never consumed downstream as structured input. | Have `/al-dev-map-suggestions-verify` read it when present, or drop the synthesis step.
- **sync-documentation-maps-write → health audit** | Handoff Gaps | Next-step handoff is prose-only. | Write a `Next:` marker into the progress checkpoint.
- **review-documentation-map ± -update** | Near-Duplicates | Audit/update pairing duplicates the parent's purpose but supports preview-before-commit. | Keep; document the pairing order.
- **sync-documentation-maps-finalize + (-wait + -write)** | Near-Duplicates | Deliberate supersession, already documented. | Covered by top action 1.

## Quality findings

### High

- **sync-documentation-maps-agent-audit** (body ~49–138) | Bloat | 89-line step procedure in one agent body. | Extract to a shared sync-maps audit procedure doc, parameterized by object type.
- **sync-documentation-maps-skill-audit** (body ~49–102) | Bloat | 53-line procedure duplicating agent-audit step-for-step. | Same extraction.
- **sync-documentation-maps-agent-update** (body ~28–85) | Bloat | 57-line procedure with verification boilerplate repeated across sync agents. | Extract shared update procedure doc.
- **sync-documentation-maps-skill-update** (body ~28–85) | Bloat | Mirrors agent-update verbatim. | Same extraction.
- **naming-convention-lens** (body ~21–52) | Bloat | 32-line severity/examples block inline. | Move severity rules and examples to the convention doc; keep only the check procedure.
- **sync-documentation-maps-skill-audit** (line 59) | Clarity | "skills/ list minus archived/" — undefined set operation blocks runnable execution. | Specify the exact command (e.g. `comm -23` on sorted lists).
- **plugin-health-discover** (Phase 3b, ~80 lines) | Bloat | Repetitive dispatch boilerplate inline. | Extract invocation boilerplate to the existing reference doc; keep only the contract summary in the skill.
- **sync-documentation-maps-collect** (Phase 4, ~72 lines) | Bloat | Repetitive per-agent dispatch prose. | Reference the shared dispatch pattern + a per-agent variation table.
- **review-documentation-map-update** (Phases 2–5) | Bloat | 60+ lines duplicated from the audit skill. | Consolidate shared extract/compare phases into a referenced knowledge doc.
- **sync-documentation-maps-finalize** | Bloat + Clarity + Description Drift (3 findings) | Deprecated-but-implemented; conflicting guidance. | Covered by top action 1 — archive.
- **al-dev-map-suggestions-verify** | Clarity | `FILTER_TYPE` captured but the filtering action is never defined. | Add: "…and filter findings to that type before proceeding."
- **plugin-health-discover** (line ~128) | Clarity | Contradictory guidance on proceeding vs blocking when background agents are incomplete. | Pick one: poll-until-complete, or proceed and report absent artifacts as invalid.

### Medium

- **Agent clarity (6)** — vague qualifiers and undefined terms: design-agent-lens-scope-isolation ("cleanly identified"), design-skill-lens-complexity ("cognitive load"), design-skill-lens-shared-backbone ("significantly different"), quality-agent-lens-bloat and quality-skill-lens-bloat ("dead branches", "historical commentary"), sync-documentation-maps-skill-audit (count-vs-max phase ambiguity). | Add operative definitions/thresholds per the findings file.
- **Agent structure (4)** — all four sync-documentation-maps agents have multi-sentence `description` fields. | Convert each to a single sentence (suggested wordings in the findings file).
- **Skill bloat (4)** — sync-documentation-maps-write (three repeated regeneration blocks), review-documentation-map (surface-branch duplication), review-documentation-map-audit (same), align-harness-repos (verbose rule list). | Extract/tabulate per findings file.
- **Skill clarity (3)** — sync-documentation-maps (raw dispatch-token examples in body; genericise per the output-boundary rule), sync-documentation-maps-collect (missing else-branch for unexpected checkpoint status), sync-documentation-maps-wait (decoupled positive-case instruction). | Apply the stated rewrites.
- **Skill description drift (9)** — al-dev-map-suggestions-verify, analyze-architectural-design, fix-knowledge-quality, plugin-health-discover, projection-sync, review-maps, sync-documentation-maps, sync-documentation-maps-collect, sync-documentation-maps-wait: descriptions omit workflow position, resume support, or dispatched-agent specifics. | Apply the per-skill clarifications in the findings file.
- **Skill name fit (3)** — align-harness-repos (validates rather than aligns; self-acknowledged grandfathered name), sync-documentation-maps-wait ("wait" but the primary action is writing maps), sync-documentation-maps-finalize (name hides deprecation). | Rename or archive per findings file.
- **Skill structure (2)** — projection-sync (missing `argument-hint` frontmatter), sync-documentation-maps-finalize (deprecation as prose, not frontmatter). | Add the frontmatter fields.

### Low

- **naming-convention-lens** | Clarity | "Grandfathered" exceptions informal/undefined. | Name them explicitly (`projection-sync`, `align-harness-repos`).
- **sync-documentation-maps-finalize** | Bloat | Deprecation commentary in body. | Moot once archived.
- **review-documentation-map / -audit / -update** | Clarity | Unquoted bash variable placeholders. | Quote `"${VAR}"` throughout the bash blocks.
- **Skill description drift (5)** — align-harness-repos, audit-knowledge-quality, plugin-health-report ("optionally" → "plugin surface only"), review-documentation-map (historical context in description), sync-documentation-maps-write (final-step position). | Minor wording tightening.

## Naming violations

_No issues found._
