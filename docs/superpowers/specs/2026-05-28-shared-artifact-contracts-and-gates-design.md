# Design: Shared Artifact Contracts and Final Gates for `profile-al-dev-shared`

**Date:** 2026-05-28
**Goal:** Lift the most portable, high-value ideas from `coleam00/harness-engineering-demo` into the shared plugin surface without introducing harness-specific runtime wiring
**Scope:** Three bounded shared-profile improvements
**Priority:** Shared-profile user impact first

---

## Source Review

This design reviewed the external repository `coleam00/harness-engineering-demo` and compared it against current `al-dev-shared` plans and specs.

Useful patterns from the demo:

- explicit phase artifacts with clear handoff files
- separation between intermediate checks and blocking final validation
- a compact worked example of a successful end-to-end run

Important non-portable patterns from the demo:

- Claude-specific hook wiring under `.claude/`
- session orchestration via the Ralph loop
- runtime enforcement mechanisms that depend on harness-specific hook APIs

This design keeps the portable workflow ideas and rejects the harness-specific mechanics.

---

## Existing Coverage Reviewed

The following recent local design work was reviewed to avoid duplication:

- `docs/superpowers/specs/2026-05-28-profile-al-dev-shared-hybrid-improvements.md`
- `docs/superpowers/specs/2026-05-28-harness-coverage-model-design.md`
- `docs/superpowers/specs/2026-05-26-plugin-improvement-review-design.md`

Those designs already cover:

- compile-gate tightening
- investigation-guidance tightening
- intent-preflight completion
- maintainer-facing harness coverage mapping
- repo-local report-driven plugin assessment

This design therefore does **not** propose:

- another intent-preflight expansion
- another compile-only gate design
- another maintainer-only review workflow
- hook-based runtime enforcement in the shared profile

---

## Problem Statement

`profile-al-dev-shared` already has durable workflow artifacts, resume guidance, and review/compile expectations. The gaps are narrower:

1. Artifact expectations are real but not yet centralized as a first-class contract across the main shared skills.
2. Verification expectations exist, but completion claims are not consistently governed by a shared rule that ties the claim to current-run evidence.
3. Users and maintainers do not have one compact canonical example showing what a healthy core AL workflow artifact bundle should look like.

These are high-leverage gaps because they affect day-to-day shared-profile usage across harnesses without requiring new runtime infrastructure.

---

## Recommended Design

Implement three bounded improvements:

| Improvement | Type | Shared-profile fit | Effort | Expected benefit |
|---|---|---|---|---|
| Shared artifact contract matrix | New knowledge document | Strong | Low to medium | Clearer handoffs, resume behavior, and skill expectations |
| Final-gate claim discipline | Small skill wording updates | Strong | Low | Fewer premature success or validation claims |
| Canonical example run | Docs example bundle | Strong | Low | Faster adoption and more consistent artifact usage |

These three changes deliberately avoid new orchestration layers and avoid coupling the shared authored surface to Claude-, Copilot-, or Codex-specific runtime features.

---

## Change 1: Shared Artifact Contract Matrix

### Intent

Make artifact behavior explicit instead of leaving it distributed across multiple skill files and knowledge docs.

### File

- `profile-al-dev-shared/knowledge/artifact-contracts.md`

### Contract Schema

For each covered skill, declare:

- `Skill`
- `Required inputs`
- `Durable outputs`
- `Resume read order`
- `Handoff artifact`
- `Success evidence`

### Initial Coverage

Seed entries should cover:

- `al-dev-plan`
- `al-dev-develop`
- `al-dev-review-develop`
- `al-dev-fix`
- `al-dev-commit`
- `al-dev-lint`

### Rules

The document should define these constraints:

- A skill may not describe a durable output unless the current workflow actually writes or expects it.
- Resume order must be explicit when multiple artifacts can exist.
- Handoff artifacts must be named so downstream skills can fail clearly when they are missing.
- Success evidence must name the concrete artifact, log, or review result that supports completion messaging.

### Why This Belongs in the Shared Profile

This is a harness-neutral workflow contract. It describes durable behavior that should remain true whether the consumer is Claude, Copilot, or Codex.

### Deliberate Non-Goals

Do not:

- define hook APIs
- describe harness-local settings files
- move repo-local maintainer artifacts into the distributed plugin
- invent new artifact classes beyond the workflows that already exist

---

## Change 2: Final-Gate Claim Discipline

### Intent

Separate intermediate progress reporting from completion claims, and require current-run evidence before the workflow is allowed to claim success.

### Target Files

- `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-lint/SKILL.md`

### Required Wording Shape

Each skill should receive:

1. a brief cross-reference to `knowledge/artifact-contracts.md`
2. a bounded rule that distinguishes:
   - intermediate progress statements
   - final completion or validation claims

Recommended rule shape:

```markdown
Do not claim the work is complete, validated, clean, or ready for the next workflow step until the success evidence named in `knowledge/artifact-contracts.md` for this skill has been produced and read for the current run.
```

### Skill-Specific Interpretation

Examples of the evidence each skill is likely to name:

- `al-dev-fix` — current compile/lint evidence or bounded verification output
- `al-dev-develop` — current phase handoff plus any required verification artifact before claiming implementation complete
- `al-dev-review-develop` — current code-review artifact and compile/review result
- `al-dev-commit` — current compile evidence when AL-affecting, plus commit-readiness result
- `al-dev-lint` — current lint/compile output or explicit no-error summary

The artifact contract document is the source of truth; the skills should not each redefine the full evidence model.

### Why This Belongs in the Shared Profile

This is not a harness hook. It is shared instruction quality. It improves user-facing reliability across all consumers by tightening when success language is permitted.

### Deliberate Non-Goals

Do not:

- add harness-specific stop hooks
- create a universal validator in this pass
- require a single verification toolchain for all project types

---

## Change 3: Canonical Example Run

### Intent

Show what a correct artifact bundle looks like for the core AL workflow, without forcing users to infer the shape from historical `.dev/` output.

### Location

Prefer a documentation location rather than a spec folder because this is reference material, not planning output.

Recommended path:

- `docs/example-runs/al-dev-core/`

### Files

- `README.md`
- `sample-solution-plan.md`
- `sample-progress.md`
- `sample-checklist.md`
- `sample-scope.md`
- `sample-code-review.md`

### Content Rules

The example should be:

- compact
- current with the artifact contract matrix
- synthetic or normalized, not a raw captured session dump
- specific enough to teach naming, sequencing, and handoff expectations

### Why This Belongs in the Shared Profile

The shared profile already depends heavily on durable artifacts. A worked example is portable documentation that helps every harness consumer use the profile correctly.

### Deliberate Non-Goals

Do not:

- publish large real session transcripts
- add harness-specific UI screenshots
- create example runs for every skill in the first pass

One high-quality core example is enough to establish the pattern.

---

## Architecture Summary

This design adds:

- one new shared knowledge document
- small wording changes in a limited set of high-traffic skills
- one documentation example bundle

This design does **not** add:

- new runtime daemons
- hooks
- worktree orchestration
- cross-session loop drivers

That keeps the effort low while preserving the main value extracted from the demo repository.

---

## Data Flow

### Normal Path

1. Skill reads its required inputs.
2. Skill writes its declared durable artifacts at the phase boundaries it already owns.
3. Downstream skills consume the declared handoff artifact instead of reconstructing context ad hoc.
4. Final completion claims are allowed only after the named success evidence has been produced and read for the current run.

### Resume Path

1. Skill reads artifacts in the contract document’s declared precedence order.
2. Skill resumes from the highest-confidence artifact bundle.
3. If artifacts conflict or required resume data is missing, the workflow stops or asks instead of silently guessing.

---

## Error Handling

Expected failure handling:

- Missing required input artifact:
  stop and report the exact missing file or artifact class.
- Missing handoff artifact:
  downstream skill refuses to continue and reports the missing handoff artifact explicitly.
- Missing or stale success evidence:
  regenerate it when appropriate, or refuse the final success claim.
- Contradictory resume artifacts:
  prefer the declared precedence only when the conflict is superficial; otherwise stop and escalate.

---

## Testing Strategy

Use existing test surfaces only.

### Trigger Corpus

Add small cases that verify:

- prompts that ask for a summary after partial work do not allow a false `validated` or `done` claim
- prompts that mention success-state language still require current evidence

### Scenario Coverage

Where per-skill scenario harnesses already exist, add checks for:

- expected artifact creation
- blocked completion claims when success evidence is absent

### Documentation Review

Review that:

- every artifact named in `artifact-contracts.md` exists in the current workflow surface or is already written by the skill
- the example-run bundle matches the contract doc
- no harness-specific runtime terms leak into the shared authored files

---

## Implementation Order

1. Create `profile-al-dev-shared/knowledge/artifact-contracts.md`
2. Patch the target skills with small cross-references and final-gate wording
3. Add `docs/example-runs/al-dev-core/`
4. Add focused trigger/scenario coverage on existing test surfaces

### Reason for This Order

- The contract doc must exist before skills can reference it.
- The example run should follow the contract, not invent it.
- Test additions should lock the chosen contract and wording, not define them implicitly.

---

## Success Criteria

This design is successful when:

- the shared profile has one central artifact contract reference for the main execution skills
- targeted skills explicitly prevent unsupported final success claims
- the example run is compact and aligned with the declared contract
- the authored shared surface remains harness-neutral

---

## Rejected Alternatives

### Hook-Based Enforcement

Rejected because it belongs in harness-specific runtime layers, not the shared authored plugin surface.

### Ralph-Style Orchestration Loop

Rejected because it is higher effort, more runtime-coupled, and less portable than the workflow-contract improvements above.

### Another Coverage-Model Pass

Rejected because the recent harness coverage model already covers maintainer-facing behavior mapping. The current gap is user-facing workflow contract clarity.

