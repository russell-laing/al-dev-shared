# /al-dev-publish Workflow Opportunity

**Status:** Identified as orphaned handoff point; deferred pending scope clarification.

## Context

- `/al-dev-commit` → `/al-dev-release-notes` → [END]
- Release-notes output (`.dev/*-al-dev-release-notes-*.md`) is not consumed by
  any downstream skill today. This is an observed workflow gap, not a current
  artifact contract.
- This is a natural continuation point for automation: plan → develop → commit → release-notes → **publish**

## Proposed /al-dev-publish Skill

Would consume `/al-dev-release-notes` output and orchestrate:

1. **Copy to changelog** — merge release notes into the project's changelog
   target (for example, `CHANGELOG.md`)
2. **Tag repository** — create git tag with version and notes
3. **Notify stakeholders** — post to the project's notification channel (for
   example, Slack, email, or Teams)
4. **Trigger CI/CD** — call deployment pipeline webhook

## Scope Questions (Pending Clarification)

1. **Publication targets:** Which of the above are in scope? (changelog only, or all?)
2. **Integration dependencies:** What external tools/APIs required?
3. **Frequency:** Is this frequently manual, or already automated in CI/CD?
4. **Audience:** Which projects need /al-dev-publish? (all AL projects, or subset?)

## Decision Required Before Implementation

- Confirm publishing is frequent manual task (not already automated)
- Confirm publication targets match project needs
- Estimate integration complexity (low if standardized; high if ad-hoc)

## Shared-Profile Gate

Do not convert this opportunity into a distributed skill until the four scope
questions above are answered for at least one real downstream workflow. If the
answers are repo-specific, keep the automation repo-local instead of adding it
to `profile-al-dev-shared`.

## Future Task

Once scope is approved, create either a repo-local publish workflow or, if the
answers generalize cleanly, a shared `/al-dev-publish` skill with:
- Phase 1: Load latest release-notes artifact
- Phase 2: Offer publication targets (changelog, GitHub, notify, CI/CD)
- Phase 3: Execute chosen target(s)
