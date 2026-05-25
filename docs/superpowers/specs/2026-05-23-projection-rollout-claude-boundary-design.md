# Next Phase Spec: Projection Rollout Boundary for `.claude`

## Summary

The next phase should spec the rollout of the projection layer as a
shared-plugin integration boundary, not as a broader maintainer-tooling
migration. `profile-al-dev-shared/` remains the only canonical shared plugin
surface and the only valid projection source. `.claude/` remains repo-local
Claude Code maintainer tooling used to audit, document, and iteratively
improve the plugin source repo. It is explicitly out of scope for projection,
distribution, and downstream harness consumption.

The phase should define and enforce a hard split between:
- Shared projection layer: shared agents, skills, knowledge, projection
  policy, generator, generated artifacts, and alignment validation.
- Repo-local maintainer layer: `.claude/skills/*`, `.claude/agents/*`, and
  Claude-only repo settings/workflows.

## Key Requirements

### Boundary contract

- Treat `profile-al-dev-shared/` as the only shared authored surface for
  downstream harnesses.
- Treat `.claude/` as non-distributed, non-projected, and repo-local.
- Downstream harness repos may consume:
  - canonical shared plugin content where appropriate
  - generated harness-specific projection artifacts
- Downstream harness repos must not consume:
  - `.claude/skills/*`
  - `.claude/agents/*`
  - `.claude/settings.json`
  - any repo-local Claude maintenance documentation unless explicitly copied
    into a shared-plugin location first

### Documentation requirements

- Add an explicit repository boundary statement to the relevant maintainer docs
  so contributors can distinguish:
  - shared plugin content
  - generated projection artifacts
  - repo-local Claude maintenance tooling
- Document that `.claude` is allowed to inspect shared plugin content as a
  local maintainer tool, but is not itself part of the plugin contract.
- Document the allowed consumer surfaces for later harness adoption:
  - shared canonical source for authoring truth
  - generated `profile-al-dev-shared/generated/agents/...` artifacts for
    harness-native consumption
  - never `.claude`

### Validation and enforcement requirements

- Extend boundary enforcement so projection workflows fail if `.claude` is
  treated as:
  - a projection input
  - an expected generated output
  - part of the distributed plugin artifact set
- Keep enforcement at the shared-plugin boundary, not inside harness-specific
  consumer repos for this phase.
- Require any future exception to be represented as explicit documented policy,
  not as an ad hoc path special-case.

### `.claude` maintainer-tooling requirements

- Audit `.claude` skills and agents only for projection awareness, not for
  projection generation.
- Update local Claude maintainer tooling only where it reads shared agents,
  maps, or validation outputs and still assumes the pre-projection world.
- Do not require `.claude` to gain Copilot or Codex equivalents in this phase.
- Do not generalize `.claude` into a cross-harness maintainer framework in
  this phase.

## Interfaces and Behavior

- No new public runtime interface is required for downstream harness repos in
  this phase.
- The effective contract remains:
  - canonical shared source under `profile-al-dev-shared/`
  - generated projections under `profile-al-dev-shared/generated/agents/`
  - repo-local maintainer tooling under `.claude/`, excluded from shared
    projection semantics
- If a tool or validator needs a file classification model, it should use a
  three-way distinction:
  - `shared_source`
  - `generated_projection`
  - `repo_local_maintainer_tooling`

## Test Plan

- Validation passes when `.claude` is absent from all projection-input and
  projection-output expectations.
- Validation fails if a rule, script, or adoption doc starts treating
  `.claude` as part of the distributable plugin surface.
- Existing projection generation and alignment checks continue to pass for
  `profile-al-dev-shared/` and generated artifacts.
- `.claude` maintainer tools that inspect shared content still function after
  the boundary is documented, with any needed local updates for projection
  awareness.
- Contributor-facing docs are sufficient for a new maintainer to classify:
  - a shared plugin file
  - a generated projection file
  - a repo-local Claude maintenance file

## Assumptions and Defaults

- `.claude` remains permanently repo-local for now.
- Cross-harness maintainer-tool parity is explicitly deferred to a later,
  separate design.
- The next phase is a requirements and enforcement phase, not a downstream
  harness-consumer wiring phase.
- No named exceptions are allowed for `.claude` in the shared projection
  contract unless a later spec adds them explicitly.
