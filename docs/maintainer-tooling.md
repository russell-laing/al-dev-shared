# Maintainer Tooling Reference

Repo-local maintainer tooling lives under `.claude/` and `.codex/`. This page
summarizes the current workflow for map sync, health sweeps, disposition
tracking, planning, projections, and validation.

Use this guide to:

- pick the right entry point for the task
- see which artifacts each skill reads and writes
- understand the current sequence of the maintainer loop
- spot gaps and extension opportunities in the loop

Most diagrams and tables on this page are generated from the `workflow:`
frontmatter contracts in `.claude/skills/*/SKILL.md` by
`scripts/generate-maintainer-guide.py`. Do not hand-edit content between
`BEGIN GENERATED` and `END GENERATED` markers; edit the contracts and re-run
the generator instead. A skill with no `workflow:` block is not an error — it
is reported as a missing-contract gap below.

**Diagram color key:**

- **Blue nodes** — user-invoked skills
- **Grey dashed nodes** — internal skills dispatched by other skills
- **Violet nodes** — artifacts
- **Violet nodes with red dashed border** — orphaned artifacts
- **Amber nodes** — manual steps
- **Indigo nodes** — checkpoints (async detail diagram only)
- **Green nodes** — background agents spawned by a skill (async detail diagram only)

**Diagram conventions:**

- Dotted self-loops marked _repeat_ are steps commonly re-run within one loop pass
- Edge labels in the overview name the artifacts that flow between stages

## Health Filter Contract

The self-healing loop uses one canonical filter contract:
`.claude/knowledge/health-filter-contract.md`.

- `--surface plugin|tooling|both` selects which surface the audit,
  disposition, and planning stages may read.
- `--dimension design|quality|naming|all` selects concrete finding
  dimensions; `all` expands to the three concrete values.
- `--resume` is audit-only. It reuses the stored concrete filters from the
  interrupted discovery run and fails on mismatch.
- `/plugin-health-report` preserves the upstream filter metadata from the
  findings artifact; it does not re-select dimensions via a public flag.

## Workflow Overview

<!-- BEGIN GENERATED: maintainer-workflow-overview -->
```mermaid
flowchart LR
    classDef userSkill fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef manualStep fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold

    subgraph stage_map_sync["Map sync"]
        skill_sync_documentation_maps["/sync-documentation-maps"]
        skill_sync_documentation_maps_apply["/sync-documentation-maps-apply"]
        skill_sync_documentation_maps_collect["/sync-documentation-maps-collect"]
        skill_sync_documentation_maps_write["/sync-documentation-maps-write"]
    end
    subgraph stage_discover["Discover"]
        skill_plugin_health_audit["/plugin-health-audit"]
        skill_plugin_health_discover["/plugin-health-discover"]
        skill_plugin_health_report["/plugin-health-report"]
    end
    subgraph stage_decide["Decide"]
        skill_plan_health_findings["/plan-health-findings"]
        skill_record_health_dispositions["/record-health-dispositions"]
        skill_revise_health_plan["/revise-health-plan"]
    end
    subgraph stage_implement["Implement"]
        skill_implement_health_plan["/implement-health-plan"]
    end
    subgraph stage_derive["Derive"]
        skill_align_harness_repos["/align-harness-repos"]
        skill_audit_knowledge_quality["/audit-knowledge-quality"]
        skill_fix_knowledge_quality["/fix-knowledge-quality"]
        skill_projection_sync["/projection-sync"]
    end
    stage_map_sync ~~~ stage_discover
    stage_discover ~~~ stage_decide
    stage_decide ~~~ stage_implement
    stage_implement ~~~ stage_derive

    skill_align_harness_repos --> skill_audit_knowledge_quality
    skill_audit_knowledge_quality -- "docs/al-dev-knowledge-quality.md" --> skill_fix_knowledge_quality
    skill_fix_knowledge_quality -- "profile-al-dev-shared/knowledge/" --> skill_align_harness_repos
    skill_implement_health_plan --> skill_align_harness_repos
    skill_implement_health_plan --> skill_audit_knowledge_quality
    skill_implement_health_plan --> skill_projection_sync
    skill_plan_health_findings -- "docs/superpowers/plans/*-*.md" --> skill_implement_health_plan
    skill_plugin_health_audit --> skill_plugin_health_discover
    skill_plugin_health_discover -- "docs/health/*-*-findings.md" --> skill_plugin_health_report
    skill_plugin_health_report -- "docs/health/*-*-health.md" --> skill_record_health_dispositions
    skill_projection_sync --> skill_align_harness_repos
    skill_record_health_dispositions -- "docs/health/dispositions.md" --> skill_plan_health_findings
    skill_revise_health_plan -- "docs/health/dispositions.md + docs/superpowers/plans/*-*.md" --> skill_implement_health_plan
    skill_sync_documentation_maps -- ".dev/sync-documentation-maps-checkpoint.json + .dev/sync-documentation-maps-runs/*/audit/*-audit.json" --> skill_sync_documentation_maps_collect
    skill_sync_documentation_maps_apply -- "docs/al-dev-agent-map.md + docs/al-dev-skills-map.md" --> skill_sync_documentation_maps_write
    skill_sync_documentation_maps_collect -- ".dev/sync-documentation-maps-runs/*/updates/*-map.md" --> skill_sync_documentation_maps_apply
    skill_sync_documentation_maps_write --> skill_plugin_health_audit

    class skill_align_harness_repos userSkill
    class skill_audit_knowledge_quality userSkill
    class skill_fix_knowledge_quality userSkill
    class skill_implement_health_plan userSkill
    class skill_plan_health_findings userSkill
    class skill_plugin_health_audit userSkill
    class skill_plugin_health_discover userSkill
    class skill_plugin_health_report userSkill
    class skill_projection_sync userSkill
    class skill_record_health_dispositions userSkill
    class skill_revise_health_plan userSkill
    class skill_sync_documentation_maps userSkill
    class skill_sync_documentation_maps_apply userSkill
    class skill_sync_documentation_maps_collect userSkill
    class skill_sync_documentation_maps_write userSkill
```
<!-- END GENERATED: maintainer-workflow-overview -->

## User Journey

<!-- BEGIN GENERATED: maintainer-user-journey -->
### Map sync steps

1. `/sync-documentation-maps` — Use when plugin documentation maps are out of sync with the current codebase, or to verify accuracy after adding/removing skills or agents. Repeat as needed.
   - reads: `docs/al-dev-skills-map.md`, `docs/al-dev-agent-map.md`
   - writes: `.dev/sync-documentation-maps-checkpoint.json`, `.dev/sync-documentation-maps-runs/RUN_ID/audit/<surface>-audit.json`
2. `/sync-documentation-maps-collect` — Collect results from /sync-documentation-maps audit agents.
   - reads: `.dev/sync-documentation-maps-checkpoint.json`, `.dev/sync-documentation-maps-runs/RUN_ID/audit/<surface>-audit.json`
   - writes: `.dev/sync-documentation-maps-runs/RUN_ID/updates/<surface>-map.md`
3. `/sync-documentation-maps-apply` — Applies validated update artifacts to docs/.
   - reads: `.dev/sync-documentation-maps-checkpoint.json`, `.dev/sync-documentation-maps-runs/RUN_ID/updates/<surface>-map.md`
   - writes: `docs/al-dev-skills-map.md`, `docs/al-dev-agent-map.md`
4. `/sync-documentation-maps-write` — Final regeneration step after /sync-documentation-maps-apply; fourth step of the async sync flow.
   - reads: `.dev/sync-documentation-maps-checkpoint.json`, `docs/al-dev-skills-map.md`, `docs/al-dev-agent-map.md`
   - writes: `docs/al-dev-workflow-diagrams.md`, `docs/al-dev-plugin-graph.md`, `docs/maintainer-tooling.md`, `profile-al-dev-shared/generated/agents/`

### Discover steps

1. `/plugin-health-audit` — Standing suggestions-only entry point for the al-dev-shared plugin surfaces. Repeat as needed.
   - reads: `docs/al-dev-skills-map.md`, `docs/al-dev-agent-map.md`
2. `/plugin-health-discover` — Discovery phase of the plugin health sweep. Repeat as needed.
   - reads: `docs/al-dev-skills-map.md`, `docs/al-dev-agent-map.md`, `profile-al-dev-shared/knowledge/lens-invocation-patterns.md`
   - writes: `docs/health/<date>-<surface>-findings.md`
3. `/plugin-health-report` — Report phase of the plugin health sweep. Repeat as needed.
   - reads: `docs/health/<date>-<surface>-findings.md`, `docs/health/dispositions.md`
   - writes: `docs/health/<date>-<surface>-health.md`

### Decide steps

1. `/record-health-dispositions` — Disposition phase of the health-audit loop. Repeat as needed.
   - reads: `docs/health/<date>-<surface>-health.md`, `docs/health/dispositions.md`
   - writes: `docs/health/dispositions.md`
2. `/plan-health-findings` — Verify and plan accepted health-audit findings (formerly verify-map-suggestions). Repeat as needed.
   - reads: `docs/health/dispositions.md`, `docs/health/<date>-<surface>-health.md`, `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`
   - writes: `docs/superpowers/plans/<date>-<topic>.md`
3. `/revise-health-plan` — Reconciles a health-loop implementation plan against a review document and re-dispositions out-of-scope findings to the ledger. Repeat as needed.
   - reads: `docs/superpowers/plans/<date>-<topic>-commentary.md`, `docs/superpowers/plans/<date>-<topic>.md`, `docs/health/dispositions.md`
   - writes: `docs/superpowers/plans/<date>-<topic>.md`, `docs/health/dispositions.md`

### Implement steps

1. `/implement-health-plan` — Closes the health-audit loop: executes an accepted implementation plan, verifies each change, and appends `fixed` rows to docs/health/dispositions.md for every `closes_rows:` entry (the distinguishing ledger close-back). Repeat as needed.
   - reads: `docs/superpowers/plans/<date>-<topic>.md`, `docs/health/dispositions.md`
   - writes: `docs/health/dispositions.md`, `.dev/implement-health-plan-progress.md`

### Derive steps

1. `/projection-sync` — Validates shared agent source and unidirectionally regenerates harness-native agent projections from the canonical agent source, summarizes changes, and asks before committing. Repeat as needed.
   - reads: `profile-al-dev-shared/agents/`
   - writes: `profile-al-dev-shared/generated/agents/`
2. `/align-harness-repos` — Validate harness neutrality in the al-dev-shared single shared plugin surface. Repeat as needed.
   - reads: `profile-al-dev-shared/skills/`, `profile-al-dev-shared/agents/`, `profile-al-dev-shared/knowledge/`
3. `/audit-knowledge-quality` — Audit knowledge files for stub sections and structural issues. Repeat as needed.
   - reads: `profile-al-dev-shared/knowledge/`
   - writes: `docs/al-dev-knowledge-quality.md`
4. `/fix-knowledge-quality` — Reads HIGH-severity knowledge quality tasks from the fix-task block produced by /audit-knowledge-quality, presents the HIGH-only task list, and conditionally dispatches one `al-dev-docs-writer` agent per issue when the user approves (or when --auto-fix is passed). Repeat as needed.
   - reads: `docs/al-dev-knowledge-quality.md`
   - writes: `profile-al-dev-shared/knowledge/`
<!-- END GENERATED: maintainer-user-journey -->

## Stage Details

### Map sync stage

<!-- BEGIN GENERATED: maintainer-stage-map-sync -->
```mermaid
flowchart LR
    classDef userSkill fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef internalSkill fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-dasharray:5 5,font-weight:bold
    classDef artifact fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef orphanArtifact fill:#ede9fe,stroke:#dc2626,color:#4c1d95,stroke-dasharray:4 4,font-weight:bold
    classDef manualStep fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold

    skill_sync_documentation_maps["/sync-documentation-maps"]
    skill_sync_documentation_maps_apply["/sync-documentation-maps-apply"]
    skill_sync_documentation_maps_collect["/sync-documentation-maps-collect"]
    skill_sync_documentation_maps_write["/sync-documentation-maps-write"]
    art__dev_sync_documentation_maps_checkpoint_json[".../sync-documentation-maps-checkpoint.json"]
    art__dev_sync_documentation_maps_runs___audit___audit_json[".../*-audit.json"]
    art__dev_sync_documentation_maps_runs___updates___map_md[".../*-map.md"]
    art_docs_al_dev_agent_map_md["docs/al-dev-agent-map.md"]
    art_docs_al_dev_plugin_graph_md["docs/al-dev-plugin-graph.md"]
    art_docs_al_dev_skills_map_md["docs/al-dev-skills-map.md"]
    art_docs_al_dev_workflow_diagrams_md[".../al-dev-workflow-diagrams.md"]
    art_docs_maintainer_tooling_md["docs/maintainer-tooling.md"]
    art_profile_al_dev_shared_generated_agents_["generated/agents/"]

    art_docs_al_dev_agent_map_md --> skill_sync_documentation_maps
    art_docs_al_dev_skills_map_md --> skill_sync_documentation_maps
    skill_sync_documentation_maps --> art__dev_sync_documentation_maps_checkpoint_json
    skill_sync_documentation_maps --> art__dev_sync_documentation_maps_runs___audit___audit_json
    skill_sync_documentation_maps --> skill_sync_documentation_maps_collect
    skill_sync_documentation_maps -. "repeat" .-> skill_sync_documentation_maps
    art__dev_sync_documentation_maps_checkpoint_json --> skill_sync_documentation_maps_apply
    art__dev_sync_documentation_maps_runs___updates___map_md --> skill_sync_documentation_maps_apply
    skill_sync_documentation_maps_apply --> art_docs_al_dev_agent_map_md
    skill_sync_documentation_maps_apply --> art_docs_al_dev_skills_map_md
    skill_sync_documentation_maps_apply --> skill_sync_documentation_maps_write
    art__dev_sync_documentation_maps_checkpoint_json --> skill_sync_documentation_maps_collect
    art__dev_sync_documentation_maps_runs___audit___audit_json --> skill_sync_documentation_maps_collect
    skill_sync_documentation_maps_collect --> art__dev_sync_documentation_maps_runs___updates___map_md
    skill_sync_documentation_maps_collect --> skill_sync_documentation_maps_apply
    art__dev_sync_documentation_maps_checkpoint_json --> skill_sync_documentation_maps_write
    art_docs_al_dev_agent_map_md --> skill_sync_documentation_maps_write
    art_docs_al_dev_skills_map_md --> skill_sync_documentation_maps_write
    skill_sync_documentation_maps_write --> art_docs_al_dev_plugin_graph_md
    skill_sync_documentation_maps_write --> art_docs_al_dev_workflow_diagrams_md
    skill_sync_documentation_maps_write --> art_docs_maintainer_tooling_md
    skill_sync_documentation_maps_write --> art_profile_al_dev_shared_generated_agents_

    class skill_sync_documentation_maps userSkill
    class skill_sync_documentation_maps_apply userSkill
    class skill_sync_documentation_maps_collect userSkill
    class skill_sync_documentation_maps_write userSkill
    class art__dev_sync_documentation_maps_checkpoint_json artifact
    class art__dev_sync_documentation_maps_runs___audit___audit_json artifact
    class art__dev_sync_documentation_maps_runs___updates___map_md artifact
    class art_docs_al_dev_agent_map_md artifact
    class art_docs_al_dev_plugin_graph_md orphanArtifact
    class art_docs_al_dev_skills_map_md artifact
    class art_docs_al_dev_workflow_diagrams_md orphanArtifact
    class art_docs_maintainer_tooling_md orphanArtifact
    class art_profile_al_dev_shared_generated_agents_ orphanArtifact
```
<!-- END GENERATED: maintainer-stage-map-sync -->

### Discover stage

<!-- BEGIN GENERATED: maintainer-stage-discover -->
```mermaid
flowchart LR
    classDef userSkill fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef internalSkill fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-dasharray:5 5,font-weight:bold
    classDef artifact fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef orphanArtifact fill:#ede9fe,stroke:#dc2626,color:#4c1d95,stroke-dasharray:4 4,font-weight:bold
    classDef manualStep fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold

    skill_plugin_health_audit["/plugin-health-audit"]
    skill_plugin_health_discover["/plugin-health-discover"]
    skill_plugin_health_report["/plugin-health-report"]
    art_docs_al_dev_agent_map_md["docs/al-dev-agent-map.md"]
    art_docs_al_dev_skills_map_md["docs/al-dev-skills-map.md"]
    art_docs_health_____findings_md["docs/health/*-*-findings.md"]
    art_docs_health_____health_md["docs/health/*-*-health.md"]
    art_docs_health_dispositions_md["docs/health/dispositions.md"]
    art_profile_al_dev_shared_knowledge_lens_invocation_patterns_md[".../lens-invocation-patterns.md"]

    art_docs_al_dev_agent_map_md --> skill_plugin_health_audit
    art_docs_al_dev_skills_map_md --> skill_plugin_health_audit
    skill_plugin_health_audit --> skill_plugin_health_discover
    skill_plugin_health_audit -. "repeat" .-> skill_plugin_health_audit
    art_docs_al_dev_agent_map_md --> skill_plugin_health_discover
    art_docs_al_dev_skills_map_md --> skill_plugin_health_discover
    art_profile_al_dev_shared_knowledge_lens_invocation_patterns_md --> skill_plugin_health_discover
    skill_plugin_health_discover --> art_docs_health_____findings_md
    skill_plugin_health_discover --> skill_plugin_health_report
    skill_plugin_health_discover -. "repeat" .-> skill_plugin_health_discover
    art_docs_health_____findings_md --> skill_plugin_health_report
    art_docs_health_dispositions_md --> skill_plugin_health_report
    skill_plugin_health_report --> art_docs_health_____health_md
    skill_plugin_health_report -. "repeat" .-> skill_plugin_health_report

    class skill_plugin_health_audit userSkill
    class skill_plugin_health_discover userSkill
    class skill_plugin_health_report userSkill
    class art_docs_al_dev_agent_map_md artifact
    class art_docs_al_dev_skills_map_md artifact
    class art_docs_health_____findings_md artifact
    class art_docs_health_____health_md artifact
    class art_docs_health_dispositions_md artifact
    class art_profile_al_dev_shared_knowledge_lens_invocation_patterns_md artifact
```
<!-- END GENERATED: maintainer-stage-discover -->

### Decide stage

<!-- BEGIN GENERATED: maintainer-stage-decide -->
```mermaid
flowchart LR
    classDef userSkill fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef internalSkill fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-dasharray:5 5,font-weight:bold
    classDef artifact fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef orphanArtifact fill:#ede9fe,stroke:#dc2626,color:#4c1d95,stroke-dasharray:4 4,font-weight:bold
    classDef manualStep fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold

    skill_plan_health_findings["/plan-health-findings"]
    skill_record_health_dispositions["/record-health-dispositions"]
    skill_revise_health_plan["/revise-health-plan"]
    art_docs_health_____health_md["docs/health/*-*-health.md"]
    art_docs_health_dispositions_md["docs/health/dispositions.md"]
    art_docs_superpowers_plans_____commentary_md[".../*-*-commentary.md"]
    art_docs_superpowers_plans_____md["docs/superpowers/plans/*-*.md"]
    art_profile_al_dev_shared_knowledge_map_change_rubber_duck_checks_md[".../map-change-rubber-duck-checks.md"]

    art_docs_health_____health_md --> skill_plan_health_findings
    art_docs_health_dispositions_md --> skill_plan_health_findings
    art_profile_al_dev_shared_knowledge_map_change_rubber_duck_checks_md --> skill_plan_health_findings
    skill_plan_health_findings --> art_docs_superpowers_plans_____md
    skill_plan_health_findings -. "repeat" .-> skill_plan_health_findings
    art_docs_health_____health_md --> skill_record_health_dispositions
    art_docs_health_dispositions_md --> skill_record_health_dispositions
    skill_record_health_dispositions --> art_docs_health_dispositions_md
    skill_record_health_dispositions --> skill_plan_health_findings
    skill_record_health_dispositions -. "repeat" .-> skill_record_health_dispositions
    art_docs_health_dispositions_md --> skill_revise_health_plan
    art_docs_superpowers_plans_____commentary_md --> skill_revise_health_plan
    art_docs_superpowers_plans_____md --> skill_revise_health_plan
    skill_revise_health_plan --> art_docs_health_dispositions_md
    skill_revise_health_plan --> art_docs_superpowers_plans_____md
    skill_revise_health_plan -. "repeat" .-> skill_revise_health_plan

    class skill_plan_health_findings userSkill
    class skill_record_health_dispositions userSkill
    class skill_revise_health_plan userSkill
    class art_docs_health_____health_md artifact
    class art_docs_health_dispositions_md artifact
    class art_docs_superpowers_plans_____commentary_md artifact
    class art_docs_superpowers_plans_____md artifact
    class art_profile_al_dev_shared_knowledge_map_change_rubber_duck_checks_md artifact
```
<!-- END GENERATED: maintainer-stage-decide -->

### Implement stage

<!-- BEGIN GENERATED: maintainer-stage-implement -->
```mermaid
flowchart LR
    classDef userSkill fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef internalSkill fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-dasharray:5 5,font-weight:bold
    classDef artifact fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef orphanArtifact fill:#ede9fe,stroke:#dc2626,color:#4c1d95,stroke-dasharray:4 4,font-weight:bold
    classDef manualStep fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold

    skill_implement_health_plan["/implement-health-plan"]
    art__dev_implement_health_plan_progress_md[".../implement-health-plan-progress.md"]
    art_docs_health_dispositions_md["docs/health/dispositions.md"]
    art_docs_superpowers_plans_____md["docs/superpowers/plans/*-*.md"]

    art_docs_health_dispositions_md --> skill_implement_health_plan
    art_docs_superpowers_plans_____md --> skill_implement_health_plan
    skill_implement_health_plan --> art__dev_implement_health_plan_progress_md
    skill_implement_health_plan --> art_docs_health_dispositions_md
    skill_implement_health_plan -. "repeat" .-> skill_implement_health_plan

    class skill_implement_health_plan userSkill
    class art__dev_implement_health_plan_progress_md orphanArtifact
    class art_docs_health_dispositions_md artifact
    class art_docs_superpowers_plans_____md artifact
```
<!-- END GENERATED: maintainer-stage-implement -->

### Derive stage

<!-- BEGIN GENERATED: maintainer-stage-derive -->
```mermaid
flowchart LR
    classDef userSkill fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef internalSkill fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-dasharray:5 5,font-weight:bold
    classDef artifact fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef orphanArtifact fill:#ede9fe,stroke:#dc2626,color:#4c1d95,stroke-dasharray:4 4,font-weight:bold
    classDef manualStep fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold

    subgraph agent_lane["Agent source changed"]
        art_agent_source["agents/"]
        skill_projection_sync["/projection-sync"]
        art_generated_agents["generated/agents/"]
    end
    subgraph knowledge_lane["Knowledge source changed"]
        art_knowledge_source["knowledge/"]
        skill_audit_knowledge_quality["/audit-knowledge-quality"]
        art_knowledge_quality_report[".../knowledge-quality.md"]
        skill_fix_knowledge_quality["/fix-knowledge-quality"]
    end
    art_shared_surface["shared authored surface"]
    skill_align_harness_repos["/align-harness-repos"]

    art_agent_source --> skill_projection_sync
    skill_projection_sync --> art_generated_agents
    skill_projection_sync --> skill_align_harness_repos
    art_knowledge_source --> skill_audit_knowledge_quality
    skill_audit_knowledge_quality --> art_knowledge_quality_report
    art_knowledge_quality_report -- "if HIGH" --> skill_fix_knowledge_quality
    skill_audit_knowledge_quality -. "if clean" .-> skill_align_harness_repos
    skill_fix_knowledge_quality --> art_knowledge_source
    skill_fix_knowledge_quality --> skill_align_harness_repos
    art_shared_surface --> skill_align_harness_repos

    class skill_projection_sync userSkill
    class skill_audit_knowledge_quality userSkill
    class skill_fix_knowledge_quality userSkill
    class skill_align_harness_repos userSkill
    class art_agent_source artifact
    class art_generated_agents orphanArtifact
    class art_knowledge_source artifact
    class art_knowledge_quality_report artifact
    class art_shared_surface artifact
```
<!-- END GENERATED: maintainer-stage-derive -->

### Adjacent tooling stage

<!-- BEGIN GENERATED: maintainer-stage-support -->
No skills in this stage declare a `workflow:` contract yet. Uncontracted skills appear under Missing contract in the gaps table.
<!-- END GENERATED: maintainer-stage-support -->

The adjacent tooling stage is intentionally light until those skills receive
workflow contracts. Current nearby tools are `/review-docs` for first-level
human-authored docs review and `/al-dev-consolidate` for `.dev/` session
artifact consolidation.

## Async Map Sync Detail

Use this view when the maps are stale. The checkpoint and run directory are the
handoff surfaces between each async step.

```mermaid
flowchart TD
    classDef skill fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agent fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef artifact fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef checkpoint fill:#e0e7ff,stroke:#4f46e5,color:#312e81,font-weight:bold

    START["/sync-documentation-maps"]
    CHECKPOINT[".dev/sync-documentation-maps-checkpoint.json"]
    RUNDIR[".dev/sync-documentation-maps-runs/RUN_ID/"]

    subgraph AUDIT["Audit phase"]
        direction LR
        SKILLAUDIT["skill-audit agent"]
        AGENTAUDIT["agent-audit agent"]
        AUDITJSON["audit/*.json"]
    end

    COLLECT["/sync-documentation-maps-collect"]

    subgraph UPDATE["Update phase"]
        direction LR
        SKILLUPDATE["skill-update agent"]
        AGENTUPDATE["agent-update agent"]
        UPDATEFILES["updates/*.md"]
    end

    APPLY["/sync-documentation-maps-apply"]
    SKILLMAP["docs/al-dev-skills-map.md"]
    AGENTMAP["docs/al-dev-agent-map.md"]
    WRITE["/sync-documentation-maps-write"]
    GENERATED["diagrams, projections, graph"]
    DONE["checkpoint status: done"]

    START --> CHECKPOINT
    START --> RUNDIR
    START --> SKILLAUDIT
    START --> AGENTAUDIT
    SKILLAUDIT --> AUDITJSON
    AGENTAUDIT --> AUDITJSON
    AUDITJSON --> COLLECT
    CHECKPOINT --> COLLECT
    COLLECT --> SKILLUPDATE
    COLLECT --> AGENTUPDATE
    SKILLUPDATE --> UPDATEFILES
    AGENTUPDATE --> UPDATEFILES
    UPDATEFILES --> APPLY
    APPLY --> SKILLMAP
    APPLY --> AGENTMAP
    APPLY --> WRITE
    WRITE --> GENERATED
    WRITE --> DONE

    class START,COLLECT,APPLY,WRITE skill
    class SKILLAUDIT,AGENTAUDIT,SKILLUPDATE,AGENTUPDATE agent
    class RUNDIR,AUDITJSON,UPDATEFILES,SKILLMAP,AGENTMAP,GENERATED artifact
    class CHECKPOINT,DONE checkpoint
```

## Current Workflow

### 1. Keep the maps current

- `/sync-documentation-maps` is the maintained entry point. Pass `--no-update`
  to print the async sequence without dispatching; omit the flag to start the
  full audit workflow.
- `/sync-documentation-maps` dispatches background audit agents and writes the
  checkpoint.
- `/sync-documentation-maps-collect` gathers the audit results and launches the
  update phase.
- `/sync-documentation-maps-apply` writes the refreshed map files.
- `/sync-documentation-maps-write` regenerates downstream artifacts and can
  finish the sync loop.

### 2. Find improvements

- `/plugin-health-audit` is the single suggestions-only entry point.
- It chains `/plugin-health-discover` and `/plugin-health-report`.
- `/plugin-health-discover` runs the design, quality, and naming lenses and
  writes the raw findings file.
- `/plugin-health-report` ranks the findings into a dossier and presents the
  results to the user.
- `/plan-health-findings` conditionally verifies cross-layer handoffs, model
  assignments, and coupled changes when accepted findings span skills and
  agents.
- **Re-sweep provenance rule:** a re-sweep may overwrite a same-day dossier
  only when the new dossier carries a "supersedes the earlier … run" note.
  Dossiers from prior dates are history — normalizing one retroactively must
  keep the supersedes note so the report phase's recurrence diff against
  prior findings stays interpretable. Prefer a new dated dossier over
  cross-day rewrites.

### 3. Record decisions and plan accepted work

- `/record-health-dispositions` records accept, decline, grandfather, and fixed
  decisions in `docs/health/dispositions.md`.
- `/plan-health-findings` turns accepted ledger rows into a verified
  implementation plan.
- The plan step is a planning output, not the implementation itself.
- **Closure write-back:** a session that lands a commit resolving an
  `accepted` ledger row must flip that row to `fixed` (or append a `fixed`
  row if the accepted row is already committed) before the session ends,
  citing the commit. See the binding rule in `/record-health-dispositions`;
  `/plugin-health-discover` Phase 0 flags violations as stale-open rows.

### 4. Refresh derived artifacts

- `/projection-sync` regenerates harness-native agent projections from the
  canonical agent source.
- `/audit-knowledge-quality` audits the knowledge files and writes
  `docs/al-dev-knowledge-quality.md`.
- `/fix-knowledge-quality` reads HIGH-severity rows from the knowledge-quality
  report and can dispatch targeted fixes before the final neutrality pass.
- `/align-harness-repos` validates harness neutrality in the shared plugin
  surface after agent, skill, or knowledge changes.

## Skills Reference

<!-- BEGIN GENERATED: maintainer-skills-tables -->
### Skills at a glance

| Skill | Stage | Invoked by | Role |
| --- | --- | --- | --- |
| `/sync-documentation-maps` | map-sync | both | Use when plugin documentation maps are out of sync with the current codebase, or to verify accuracy after adding/removing skills or agents. |
| `/sync-documentation-maps-apply` | map-sync | user | Applies validated update artifacts to docs/. |
| `/sync-documentation-maps-collect` | map-sync | user | Collect results from /sync-documentation-maps audit agents. |
| `/sync-documentation-maps-write` | map-sync | user | Final regeneration step after /sync-documentation-maps-apply; fourth step of the async sync flow. |
| `/plugin-health-audit` | discover | user | Standing suggestions-only entry point for the al-dev-shared plugin surfaces. |
| `/plugin-health-discover` | discover | both | Discovery phase of the plugin health sweep. |
| `/plugin-health-report` | discover | both | Report phase of the plugin health sweep. |
| `/plan-health-findings` | decide | user | Verify and plan accepted health-audit findings (formerly verify-map-suggestions). |
| `/record-health-dispositions` | decide | user | Disposition phase of the health-audit loop. |
| `/revise-health-plan` | decide | user | Reconciles a health-loop implementation plan against a review document and re-dispositions out-of-scope findings to the ledger. |
| `/implement-health-plan` | implement | user | Closes the health-audit loop: executes an accepted implementation plan, verifies each change, and appends `fixed` rows to docs/health/dispositions.md for every `closes_rows:` entry (the distinguishing ledger close-back). |
| `/align-harness-repos` | derive | user | Validate harness neutrality in the al-dev-shared single shared plugin surface. |
| `/audit-knowledge-quality` | derive | user | Audit knowledge files for stub sections and structural issues. |
| `/fix-knowledge-quality` | derive | user | Reads HIGH-severity knowledge quality tasks from the fix-task block produced by /audit-knowledge-quality, presents the HIGH-only task list, and conditionally dispatches one `al-dev-docs-writer` agent per issue when the user approves (or when --auto-fix is passed). |
| `/projection-sync` | derive | user | Validates shared agent source and unidirectionally regenerates harness-native agent projections from the canonical agent source, summarizes changes, and asks before committing. |

### Inputs and outputs

| Skill | Reads | Writes | Next |
| --- | --- | --- | --- |
| `/sync-documentation-maps` | `docs/al-dev-skills-map.md`, `docs/al-dev-agent-map.md` | `.dev/sync-documentation-maps-checkpoint.json`, `.dev/sync-documentation-maps-runs/RUN_ID/audit/<surface>-audit.json` | `/sync-documentation-maps-collect` |
| `/sync-documentation-maps-apply` | `.dev/sync-documentation-maps-checkpoint.json`, `.dev/sync-documentation-maps-runs/RUN_ID/updates/<surface>-map.md` | `docs/al-dev-skills-map.md`, `docs/al-dev-agent-map.md` | `/sync-documentation-maps-write` |
| `/sync-documentation-maps-collect` | `.dev/sync-documentation-maps-checkpoint.json`, `.dev/sync-documentation-maps-runs/RUN_ID/audit/<surface>-audit.json` | `.dev/sync-documentation-maps-runs/RUN_ID/updates/<surface>-map.md` | `/sync-documentation-maps-apply` |
| `/sync-documentation-maps-write` | `.dev/sync-documentation-maps-checkpoint.json`, `docs/al-dev-skills-map.md`, `docs/al-dev-agent-map.md` | `docs/al-dev-workflow-diagrams.md`, `docs/al-dev-plugin-graph.md`, `docs/maintainer-tooling.md`, `profile-al-dev-shared/generated/agents/` | `/plugin-health-audit` |
| `/plugin-health-audit` | `docs/al-dev-skills-map.md`, `docs/al-dev-agent-map.md` | — | `/plugin-health-discover` |
| `/plugin-health-discover` | `docs/al-dev-skills-map.md`, `docs/al-dev-agent-map.md`, `profile-al-dev-shared/knowledge/lens-invocation-patterns.md` | `docs/health/<date>-<surface>-findings.md` | `/plugin-health-report` |
| `/plugin-health-report` | `docs/health/<date>-<surface>-findings.md`, `docs/health/dispositions.md` | `docs/health/<date>-<surface>-health.md` | `/record-health-dispositions` |
| `/plan-health-findings` | `docs/health/dispositions.md`, `docs/health/<date>-<surface>-health.md`, `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md` | `docs/superpowers/plans/<date>-<topic>.md` | `/implement-health-plan` |
| `/record-health-dispositions` | `docs/health/<date>-<surface>-health.md`, `docs/health/dispositions.md` | `docs/health/dispositions.md` | `/plan-health-findings` |
| `/revise-health-plan` | `docs/superpowers/plans/<date>-<topic>-commentary.md`, `docs/superpowers/plans/<date>-<topic>.md`, `docs/health/dispositions.md` | `docs/superpowers/plans/<date>-<topic>.md`, `docs/health/dispositions.md` | `/implement-health-plan` |
| `/implement-health-plan` | `docs/superpowers/plans/<date>-<topic>.md`, `docs/health/dispositions.md` | `docs/health/dispositions.md`, `.dev/implement-health-plan-progress.md` | `/projection-sync`, `/align-harness-repos`, `/audit-knowledge-quality` |
| `/align-harness-repos` | `profile-al-dev-shared/skills/`, `profile-al-dev-shared/agents/`, `profile-al-dev-shared/knowledge/` | — | `/audit-knowledge-quality` |
| `/audit-knowledge-quality` | `profile-al-dev-shared/knowledge/` | `docs/al-dev-knowledge-quality.md` | `/fix-knowledge-quality` |
| `/fix-knowledge-quality` | `docs/al-dev-knowledge-quality.md` | `profile-al-dev-shared/knowledge/` | `/align-harness-repos` |
| `/projection-sync` | `profile-al-dev-shared/agents/` | `profile-al-dev-shared/generated/agents/` | `/align-harness-repos` |
<!-- END GENERATED: maintainer-skills-tables -->

## Gaps & Extension Candidates

Improvement-spotting surface, generated from the same contracts as the
diagrams. Each row is a candidate to extend or tighten the loop; this is the
only place cross-stage gaps are guaranteed to appear in full.

<!-- BEGIN GENERATED: maintainer-gaps -->
| Signal | Item | Detail |
| --- | --- | --- |
| Orphaned artifact | `.dev/implement-health-plan-progress.md` | produced by /implement-health-plan; consumed by no skill |
| Orphaned artifact | `docs/al-dev-plugin-graph.md` | produced by /sync-documentation-maps-write; consumed by no skill |
| Orphaned artifact | `docs/al-dev-workflow-diagrams.md` | produced by /sync-documentation-maps-write; consumed by no skill |
| Orphaned artifact | `docs/maintainer-tooling.md` | produced by /sync-documentation-maps-write; consumed by no skill |
| Orphaned artifact | `profile-al-dev-shared/generated/agents/` | produced by /projection-sync, /sync-documentation-maps-write; consumed by no skill |
| Sourceless input | `docs/superpowers/plans/*-*-commentary.md` | consumed by /revise-health-plan; produced by no skill |
| Manual step | none | — |
| Missing contract | `al-dev-consolidate` | active skill with no workflow contract |
| Missing contract | `review-docs` | active skill with no workflow contract |
| Artifact freshness | `.dev/implement-health-plan-progress.md` | latest 2026-06-14 |
| Artifact freshness | `.dev/sync-documentation-maps-checkpoint.json` | latest 2026-06-14 |
| Artifact freshness | `.dev/sync-documentation-maps-runs/*/audit/*-audit.json` | latest 2026-06-14 |
| Artifact freshness | `.dev/sync-documentation-maps-runs/*/updates/*-map.md` | latest 2026-06-14 |
| Artifact freshness | `docs/al-dev-agent-map.md` | latest 2026-06-14 |
| Artifact freshness | `docs/al-dev-knowledge-quality.md` | latest 2026-06-13 |
| Artifact freshness | `docs/al-dev-plugin-graph.md` | latest 2026-06-14 |
| Artifact freshness | `docs/al-dev-skills-map.md` | latest 2026-06-14 |
| Artifact freshness | `docs/al-dev-workflow-diagrams.md` | latest 2026-06-14 |
| Artifact freshness | `docs/health/*-*-findings.md` | latest 2026-06-13 |
| Artifact freshness | `docs/health/*-*-health.md` | latest 2026-06-13 |
| Artifact freshness | `docs/health/dispositions.md` | latest 2026-06-14 |
| Artifact freshness | `docs/superpowers/plans/*-*.md` | latest 2026-06-13 |
| Artifact freshness | `profile-al-dev-shared/generated/agents/` | present |
| Artifact freshness | `profile-al-dev-shared/knowledge/` | present |
| Internal-only skill | none | — |
<!-- END GENERATED: maintainer-gaps -->

## Quick Reference

| Situation | Run |
| --- | --- |
| Added or removed a skill or agent | `/sync-documentation-maps` |
| Want to audit the async sequence without updating docs | `/sync-documentation-maps --no-update` |
| Maps are out of sync | `/sync-documentation-maps` |
| Edited an agent `.md` file | `/projection-sync`, then `/align-harness-repos` |
| Edited a knowledge file | `/audit-knowledge-quality`; if HIGH findings exist, `/fix-knowledge-quality`; then `/align-harness-repos` |
| Want to find improvement candidates | `/plugin-health-audit` |
| Want design-only or quality-only findings | `/plugin-health-audit --dimension design` or `--dimension quality` |
| Ready to plan accepted skill and agent findings together | `/plan-health-findings` |
| Ready to record disposition decisions | `/record-health-dispositions` |
| Ready to plan accepted findings | `/plan-health-findings` |
| Need the live map refresh flow | `/sync-documentation-maps` |

If a step feels blocked, check whether its input artifact exists and was
produced by the preceding step — the gaps table above shows each artifact's
freshness.
