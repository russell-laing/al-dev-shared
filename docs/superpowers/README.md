# Superpowers Planning Artifacts

This directory keeps durable summaries of historical Superpowers-generated planning work.

Raw generated plans and specs are not current implementation guidance. They are useful mainly as provenance for how this repository's reports, validators, and shared plugin contracts evolved over time.

## Current Source of Truth

- `profile-al-dev-shared/knowledge/` for workflow guidance
- `profile-al-dev-shared/skills/` for skill behavior
- `profile-al-dev-shared/agents/` for agent behavior
- `scripts/` for validators and generated-artifact tooling

## Tracking Policy

- Track `docs/superpowers/README.md`.
- Track `docs/superpowers/history.md`.
- Do not track new raw files under `docs/superpowers/plans/`.
- Do not track new raw files under `docs/superpowers/specs/` unless a maintainer explicitly promotes the spec to durable design documentation.
- When promoting a spec, move or copy the durable content into a named document outside the raw historical folder.

## `.dev` Policy

The `.dev/` directory mixes two kinds of artifacts and they should not be
treated the same way.

- Keep live resumable workflow state files tracked when current skills depend on
  them as stable paths, for example:
  - `.dev/progress.md`
  - `.dev/sync-map-documentation-checkpoint.json`
  - `.dev/plugin-health-team-checkpoint.json`
- Do not keep historical reports, one-off analyses, completed run manifests, or
  dated scratch notes tracked once their provenance has been summarized in a
  durable doc such as `docs/superpowers/history.md`.
- Before deleting a tracked `.dev` artifact, verify whether it is:
  - a live checkpoint path referenced by shared knowledge, skill docs, or map docs
  - a completed historical artifact that can be summarized and removed safely

When in doubt, prefer preserving the durable summary and keeping only the small
set of stable live-state files that current workflows read by exact path.
