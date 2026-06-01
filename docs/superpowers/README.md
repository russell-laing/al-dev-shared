# Superpowers Planning Artifacts

This directory keeps durable summaries of historical Superpowers-generated planning work.

Raw generated plans and specs are not current implementation guidance. They are useful mainly as provenance for how this repository's reports, validators, and shared plugin contracts evolved over time.

## Current Source of Truth

- `profile-al-dev-shared/knowledge/` for workflow guidance
- `profile-al-dev-shared/skills/` for skill behavior
- `profile-al-dev-shared/agents/` for agent behavior
- `docs/architectural-decisions.md` for accepted architectural decisions
- `scripts/` for validators and generated-artifact tooling

## Tracking Policy

- Track `docs/superpowers/README.md`.
- Track `docs/superpowers/history.md`.
- Do not track new raw files under `docs/superpowers/plans/`.
- Do not track new raw files under `docs/superpowers/specs/` unless a maintainer explicitly promotes the spec to durable design documentation.
- When promoting a spec, move or copy the durable content into a named document outside the raw historical folder.
