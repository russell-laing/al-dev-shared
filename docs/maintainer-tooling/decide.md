# Stage 3: Decide

[Previous: Discover](./discover.md) | [Back to summary](../maintainer-tooling.md) | [Next: Implement](./implement.md)

Decide converts a ranked dossier into durable maintainer choices and an executable plan. This
stage answers: "Which findings do we accept? Which do we decline? What work will we do?"

**The process has two parts:**

1. **Record dispositions** — For each finding in the dossier, you decide:
   - **Accept** — This is real work we'll fix now.
   - **Decline** — We're not addressing this; it's out of scope, intentional, or already handled
     elsewhere.
   - **Grandfather** — This is a pre-existing state we're acknowledging but not fixing now.
   - **Fixed** — We realized this was already fixed in a prior session (since the last dossier)
     or by a different maintainer.

   These decisions are recorded as events in the JSONL event store (`docs/health/dispositions-events/`). Later audits filter out
   already-decided findings using the generated `docs/health/dispositions-open.md` view, so you don't re-triage the same issue twice.

2. **Plan accepted findings** — For findings you've accepted, `/plan-plugin-findings` verifies
   each one against the live codebase (using rubber-duck checks), then writes an implementation
   plan with explicit task steps. Crucially, each plan task names the event IDs it will close
   (via `closes_event_ids:`), creating the linkage that lets Implement prove work was completed.

**Plan revision (optional):** If someone reviews the plan and finds that scope or decisions need
to change before execution, run `/revise-plugin-plan` to reconcile the plan and ledger in one
step. This is a side path, not a required step.

## How Decide Works

Dispositions are the key to this stage. By recording durable decisions as JSONL events, you create a durable
audit trail: "We looked at this finding, made a decision, and here's what we did." Later audits
can read the generated `docs/health/dispositions-open.md` view and skip re-triaging findings you've already decided on, making the loop
more efficient over time.

The plan that emerges from accepted findings is not a generic task list—it's a **verified
contract**. Each task in the plan explicitly names which event IDs it will close, creating
an audit trail. When Implement runs the plan, it appends `fixed` events to the JSONL event store for each
`closes_event_ids:` identifier, proving that the work was completed and not just attempted.

If a review stage finds issues with the plan (scope creep, wrong decision, etc.), `/revise-plugin-plan`
lets you reconcile without re-planning from scratch. It reads the review commentary, reconciles
the plan and ledger, and prepares for Implement.

## Workflow

<!-- BEGIN GENERATED: maintainer-stage-decide-diagram -->
```mermaid
flowchart TD
    classDef userSkill fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef artifact fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef orphanArtifact fill:#ede9fe,stroke:#dc2626,color:#4c1d95,stroke-dasharray:4 4,font-weight:bold

    art_dossier["ranked health dossier"]
    skill_record_health_dispositions["/record-plugin-dispositions"]
    art_ledger["accepted rows in disposition ledger"]
    skill_plan_health_findings["/plan-plugin-findings"]
    art_plan["verified plan with closes_event_ids"]
    art_commentary["optional review commentary"]
    skill_revise_health_plan["/revise-plugin-plan"]

    art_dossier --> skill_record_health_dispositions
    skill_record_health_dispositions --> art_ledger
    art_ledger --> skill_plan_health_findings
    skill_plan_health_findings --> art_plan
    art_commentary -.-> skill_revise_health_plan
    art_plan -.-> skill_revise_health_plan
    skill_revise_health_plan -. "reconciled plan + ledger" .-> art_plan

    class skill_record_health_dispositions userSkill
    class skill_plan_health_findings userSkill
    class skill_revise_health_plan userSkill
    class art_dossier artifact
    class art_ledger orphanArtifact
    class art_plan artifact
    class art_commentary artifact
```
<!-- END GENERATED: maintainer-stage-decide-diagram -->

## How This Stage Works

<!-- BEGIN GENERATED: maintainer-stage-decide-journey -->
### Primary path

1. `/record-plugin-dispositions` — Disposition phase of the health-audit loop.
2. `/plan-plugin-findings` — Verify and plan accepted health-audit findings.

### Optional revision path

Run `/revise-plugin-plan` only when a separate review or commentary artifact requires the plan and ledger decisions to be reconciled before implementation.
<!-- END GENERATED: maintainer-stage-decide-journey -->

## Key Artifacts

<!-- BEGIN GENERATED: maintainer-stage-decide-artifacts -->
| Artifact | Role |
| --- | --- |
| `docs/health/<date>-<surface>-health.md` | Presents the verified findings that require a maintainer decision. |
| `docs/health/dispositions-events/YYYY/YYYY-MM.jsonl` (canonical) + `docs/health/dispositions-open.md` | Canonical event store for decisions; dispositions-open.md is the generated open-items read view. |
| `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md` | Defines the live verification checks used before accepted findings become plan tasks. |
| `docs/superpowers/plans/<date>-<topic>.md` | Carries the verified implementation tasks and required `closes_event_ids:` identifiers. |
| `docs/superpowers/plans/<date>-<topic>-commentary.md` | Optional review evidence used only when the plan must be revised. |
<!-- END GENERATED: maintainer-stage-decide-artifacts -->

Exact per-skill reads, writes, and `next` declarations are in
[Appendix B of the summary](../maintainer-tooling.md#appendix-b-contracted-skills).

---

**Next:** Once you have an approved plan with `closes_event_ids:` identifiers, open [Stage 4: Implement](./implement.md)
to execute the plan tasks, verify results, and close the health loop by appending fixed events to the JSONL event store.
