# Design: Harness Coverage Model for `profile-al-dev-shared`

**Date:** 2026-05-28
**Goal:** Convert useful harness-engineering ideas into a bounded, repo-specific design for improving the harness-agnostic `profile-al-dev-shared` plugin
**Primary deliverable:** A maintainer-facing coverage model that maps shared-profile guidance to sensors, enforcement points, and known gaps
**Secondary deliverable:** A small failure-to-rule ratchet pattern for promoting repeated agent failures into durable shared-profile improvements

---

## Source Review

This design is based on two external harness-engineering articles and the current `al-dev-shared` repository shape.

- Addy Osmani, ["Agent Harness Engineering"](https://addyosmani.com/blog/agent-harness-engineering/), argues that agent failures should be treated as signals for harness improvement, and that each harness component should be justified by the behavior it helps produce.
- Birgitta Bockeler, ["Harness engineering for coding agent users"](https://martinfowler.com/articles/harness-engineering.html), frames user-owned harnesses as a combination of feedforward guides and feedback sensors, split across computational and inferential controls.

The useful idea for this repository is not a new agent runtime. `profile-al-dev-shared` already acts as a shared outer harness through skills, agents, knowledge files, projection generation, and validation scripts. The missing piece is an explicit coverage model that shows which desired behaviors are only documented, which are tested, and which are enforced.

---

## Rubber-Duck Review

Before accepting the approach, I checked it against the local `profile-al-dev-shared/knowledge/rubber-duck.md` suggestion-of-merit gate.

| Gate | Answer |
|---|---|
| Source evidence | Both articles identify a recurring harness problem: guides and sensors drift unless they are designed as a system. Osmani emphasizes ratcheting observed failures into rules. Bockeler emphasizes feedforward and feedback controls, keeping checks early, and evaluating harness coverage. |
| Existing shared-profile coverage | `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md`, `workflow-resilience.md`, `intent-preflight.md`, `compile-lint-procedure.md`, and `skill-test-trigger-corpus.yaml` already cover parts of the behavior. The gap is that there is no compact map from behavior to guide, sensor, enforcement strength, and owner. |
| Shared plugin fit | The coverage model belongs partly in repo-local maintainer docs and partly in shared-profile knowledge. It is harness-neutral because it describes behavior, evidence, and ownership boundaries rather than Claude, Copilot, or Codex mechanics. |
| Risk reduced | Reduces policy drift, overstated guarantees, missing sensor coverage, repeated workflow failures, and confusion between shared-profile intent and harness-specific runtime wiring. |
| Test or review path | Review by checking the model against projection tests, neutrality validation, lens-agent validation, trigger-corpus cases, and existing workflow-resilience expectations. |

The main correction from this rubber-duck pass is scope. A coverage model should start as a maintainer-facing design and review artifact. Only specific, proven rules should be promoted into distributed `profile-al-dev-shared` skill or knowledge instructions.

---

## Problem Statement

The shared profile has several strong pieces already:

- canonical shared skills and agents under `profile-al-dev-shared`
- generated agent projections for Claude, Copilot, and Codex
- neutrality and lens-agent validation scripts
- intent-preflight, compile/lint, workflow-resilience, and rubber-duck guidance
- trigger-corpus and scenario coverage for important workflow boundaries

The weakness is visibility and traceability. A future maintainer can see individual guides and individual tests, but not the full relationship between:

- the behavior the profile wants agents to exhibit
- the guide that tries to shape the behavior
- the sensor or test that detects failure
- the enforcement point that blocks or corrects failure
- the owner of that control: shared profile, repo-local maintainer tooling, generated projection, or harness runtime

That gap makes it easy to add guidance without a sensor, add a sensor without shared doctrine, or describe guarantees that the current scripts do not actually enforce.

---

## Recommended Design

Create a harness coverage model for `profile-al-dev-shared`. The model should be small enough to maintain manually, but structured enough to expose gaps.

Recommended location:

- `docs/superpowers/specs/2026-05-28-harness-coverage-model-design.md` for this design
- a later implementation can add `docs/harness-coverage-model.md` or `profile-al-dev-shared/knowledge/harness-coverage-model.md`

Use this schema for each covered behavior:

| Field | Purpose |
|---|---|
| Behavior | The agent behavior or repo guarantee being regulated |
| Category | Maintainability, architecture/projection fitness, workflow behavior, or ownership boundary |
| Guide | The feedforward source that tells the agent what to do |
| Sensor | The feedback source that detects drift or failure |
| Enforcement strength | `guide only`, `guide + test`, or `guide + blocking enforcement` |
| Owner | Shared profile, generated projection, repo-local maintainer tooling, or harness runtime |
| Gap | The next missing control, if any |

Seed coverage rows should include:

| Behavior | Guide | Sensor | Enforcement strength | Owner | Initial gap |
|---|---|---|---|---|---|
| Shared agent tool intent projects correctly to each harness | `agent-tool-projection-policy.md` | `scripts/tests/test_generate_agent_projections.py`, generated projection diff review | Guide + test | Shared profile plus projection generator | Add coverage row that names generator as runtime source of truth |
| Harness-specific terms do not leak into shared authored files | `harness-concepts.md`, `agent-tool-projection-policy.md` | `scripts/validate_harness_neutrality.py` | Guide + blocking validation | Shared profile plus repo script | Make allowlisted exceptions visible in the model |
| Long-running workflows resume from compact durable state | `workflow-resilience.md` | Manual resume review, future scenario coverage | Guide only today, partial workflow enforcement | Shared profile | Add scenario coverage for resume-pack expectations |
| Review-only, plan-only, edit, and commit intents are not conflated | `intent-preflight.md` | `skill-test-trigger-corpus.yaml`, skill scenario tests | Guide + test | Shared profile | Add explicit coverage row for each high-risk entry skill |
| Compile and lint claims are evidence-backed | `compile-lint-procedure.md` | compile log review, future commit gate scenario | Guide only today, stronger where skill-specific gates exist | Shared profile | Mark where no blocking gate exists |
| Repo-local maintainer tooling is not treated as distributed plugin surface | `AGENTS.md`, projection docs | neutrality validation, manual generated-output review | Guide + partial validation | Repo-local maintainer tooling | Add ownership-boundary rows for `.claude`, `.codex`, generated projections |

---

## Failure-to-Rule Ratchet

Add a small maintainer practice for future profile changes:

1. Capture the failure mode.
2. Identify the behavior the shared profile should regulate.
3. Check the coverage model for existing guide and sensor coverage.
4. Choose the smallest durable control:
   - wording clarification
   - trigger-corpus case
   - scenario test
   - validator or structural test
   - workflow gate
   - projection generator change
5. Update the coverage row so future maintainers can see what changed.

This keeps the profile from accumulating untested advice. It also avoids turning every interesting article recommendation into shared runtime policy.

---

## Implementation Shape

This design should be implemented in three small steps:

1. Add the coverage model artifact with the seed rows above.
2. Add a short reference from `profile-al-dev-shared/knowledge/rubber-duck.md` or a maintainer-facing doc explaining that report-driven suggestions should update the coverage model when accepted.
3. Add focused tests or scenario rows only for gaps that already have existing test surfaces, starting with intent-preflight and projection behavior.

Avoid these non-goals:

- Do not introduce a new universal shared tool schema.
- Do not move harness runtime wiring into the shared profile.
- Do not turn repo-local `.claude` or `.codex` maintainer tooling into distributed plugin output.
- Do not add a broad new validator until the manual coverage model has shown which checks are stable enough to automate.

---

## Validation Plan

For a first implementation, validation should include:

- `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared`
- `python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents`
- `python3 scripts/tests/test_generate_agent_projections.py`
- targeted review that each coverage row names a real guide and a real sensor, or explicitly marks the sensor as missing

If implementation edits authored agents, regenerate projections with:

```bash
python3 scripts/generate-agent-projections.py
```

If implementation only adds maintainer docs and shared knowledge, projection regeneration is not required unless the agent source changes.

---

## Open Questions for Implementation

- Should the durable coverage artifact live under `docs/` as maintainer guidance, or under `profile-al-dev-shared/knowledge/` as distributed shared-profile knowledge?
- Should enforcement strength be free text, or restricted to the three labels in this design?
- Should future scenario coverage be added immediately, or only after the first manual coverage review identifies the highest-value gaps?

Recommended defaults:

- Put the first durable artifact under `docs/` to keep it maintainer-facing.
- Use the three fixed enforcement labels.
- Add scenario coverage only for rows where there is already an existing test surface.
