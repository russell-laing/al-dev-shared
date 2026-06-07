# AL Dev Plugin Map

> A reference tool for understanding skill relationships, agent patterns, and file handoffs in profile-al-dev-shared. This document is for personal gap analysis and extension planning, not onboarding.
>
> **Generated sections** are refreshed by `scripts/generate-map-doc-sections.py`. Layer 2 drill-downs include Phase<N> nodes extracted from each skill's SKILL.md file. Do not hand-edit inside `<!-- BEGIN/END GENERATED -->` markers.

**Last updated:** 2026-06-04

<!-- BEGIN GENERATED: skill-coverage -->
**Coverage:** 22 active skills in `profile-al-dev-shared/skills/` (count derived from disk at generation time).
<!-- END GENERATED: skill-coverage -->

**Scope:** Active skill directories only. Archived items (`al-dev-test`, test-engineer agents, `al-dev-test-coverage-reviewer`, `al-dev-align`) excluded. Layer 1 contains 21 primary lifecycle skills. Layer 2 includes 1 additional distributed utility (`/al-dev-help`). Maintainer-surface skills (e.g. `al-dev-consolidate`, relocated to `.claude/skills/`) and tools are documented in separate tracking systems.

---

## Layer 1: Lifecycle Overview

This diagram shows pre-planning tributaries (dashed, optional), the three main entry points, and the development spine through to post-commit output.

<!-- BEGIN GENERATED: skill-lifecycle-mermaid -->
```mermaid
flowchart TD
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    skill_al_dev_commit[al-dev-commit]
    skill_al_dev_develop[al-dev-develop]
    skill_al_dev_document[al-dev-document]
    skill_al_dev_explore[al-dev-explore]
    skill_al_dev_fix[al-dev-fix]
    skill_al_dev_handoff[al-dev-handoff]
    skill_al_dev_interview[al-dev-interview]
    skill_al_dev_investigate[al-dev-investigate]
    skill_al_dev_lint[al-dev-lint]
    skill_al_dev_perf[al-dev-perf]
    skill_al_dev_plan[al-dev-plan]
    skill_al_dev_plan_preflight[al-dev-plan-preflight]
    skill_al_dev_release_notes[al-dev-release-notes]
    skill_al_dev_review_develop[al-dev-review-develop]
    skill_al_dev_support_reply[al-dev-support-reply]
    skill_al_dev_ticket[al-dev-ticket]
    skill_commit_recover[commit-recover]
    skill_verify_commits[verify-commits]

    skill_al_dev_commit --> skill_verify_commits
    skill_al_dev_commit -.-> skill_al_dev_document
    skill_al_dev_commit -.-> skill_al_dev_handoff
    skill_al_dev_commit -.-> skill_al_dev_release_notes
    skill_al_dev_develop --> skill_al_dev_review_develop
    skill_al_dev_develop -.-> skill_al_dev_lint
    skill_al_dev_explore -.-> skill_al_dev_plan
    skill_al_dev_fix --> skill_al_dev_commit
    skill_al_dev_interview -.-> skill_al_dev_plan
    skill_al_dev_investigate --> skill_al_dev_plan
    skill_al_dev_perf -.-> skill_al_dev_plan
    skill_al_dev_plan --> skill_al_dev_develop
    skill_al_dev_plan_preflight -.-> skill_al_dev_plan
    skill_al_dev_review_develop --> skill_al_dev_commit
    skill_al_dev_ticket --> skill_al_dev_support_reply
    skill_commit_recover --> skill_al_dev_commit

    class skill_al_dev_commit skillNode
    class skill_al_dev_develop skillNode
    class skill_al_dev_document skillNode
    class skill_al_dev_explore skillNode
    class skill_al_dev_fix skillNode
    class skill_al_dev_handoff skillNode
    class skill_al_dev_interview skillNode
    class skill_al_dev_investigate skillNode
    class skill_al_dev_lint skillNode
    class skill_al_dev_perf skillNode
    class skill_al_dev_plan skillNode
    class skill_al_dev_plan_preflight skillNode
    class skill_al_dev_release_notes skillNode
    class skill_al_dev_review_develop skillNode
    class skill_al_dev_support_reply skillNode
    class skill_al_dev_ticket skillNode
    class skill_commit_recover skillNode
    class skill_verify_commits skillNode
```
<!-- END GENERATED: skill-lifecycle-mermaid -->

---

## Layer 2: Per-Skill Drill-Downs

Each skill is shown with its internal phases, spawned agents, and key outputs. Agents are referenced by their full type name (for example, `al-dev-shared:al-dev-developer-tdd`).

### Notation

- **Phase**: Numbered step inside the skill
- **Agent**: Which agent (or skill itself) executes the phase
- **Pattern**: ×1 (serial), ×2-3 (parallel), ×N (variable count)
- **Output**: File written to `.dev/` or code generated

### /al-dev-ticket

**Two modes:** `--mode=context-only` (default fetch/context only) and `--mode=full` (fetch context then chains to `/al-dev-support-reply`). Research and reply drafting are handled by `/al-dev-support-reply`. Phases: 0, 0.5, 5.

<!-- BEGIN GENERATED: skill-drilldown-al-dev-ticket -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_ticket[al-dev-ticket]
    Phase0["Phase 0"]
    Phase0_5["Phase 0.5"]
    Phase5["Phase 5"]
    skill_al_dev_interview[al-dev-interview]
    skill_al_dev_plan[al-dev-plan]
    skill_al_dev_support_reply[al-dev-support-reply]
    agent_al_dev_ticket_context_writer[al-dev-ticket-context-writer]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_ticket_agent_invocation_pattern_md[ticket-agent-invocation-pattern]

    skill_al_dev_ticket --> Phase0
    skill_al_dev_ticket --> Phase0_5
    skill_al_dev_ticket --> Phase5
    skill_al_dev_ticket -.-> skill_al_dev_interview
    skill_al_dev_ticket -.-> skill_al_dev_plan
    skill_al_dev_ticket -.-> skill_al_dev_support_reply
    skill_al_dev_ticket --> agent_al_dev_ticket_context_writer
    skill_al_dev_ticket --> knowledge_artifact_contracts_md
    skill_al_dev_ticket --> knowledge_ticket_agent_invocation_pattern_md

    class skill_al_dev_ticket skillNode
    class Phase0 phaseNode
    class Phase0_5 phaseNode
    class Phase5 phaseNode
    class skill_al_dev_interview skillNode
    class skill_al_dev_plan skillNode
    class skill_al_dev_support_reply skillNode
    class agent_al_dev_ticket_context_writer agentNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_ticket_agent_invocation_pattern_md knowledgeNode
```

Agents spawned: `al-dev-shared:al-dev-ticket-context-writer`
<!-- END GENERATED: skill-drilldown-al-dev-ticket -->

### /al-dev-support-reply

Follow-on support workflow used after `/al-dev-ticket --mode=full`. Researches the issue and drafts the customer-facing reply using the ticket context prepared upstream. Phases: 0–3.

<!-- BEGIN GENERATED: skill-drilldown-al-dev-support-reply -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_support_reply[al-dev-support-reply]
    Phase0["Phase 0"]
    Phase1["Phase 1"]
    Phase2["Phase 2"]
    Phase3["Phase 3"]
    skill_al_dev_ticket[al-dev-ticket]
    agent_al_dev_support_reply_drafter[al-dev-support-reply-drafter]
    agent_al_dev_support_researcher[al-dev-support-researcher]
    artifact_2026_06_01_al_dev_ticket_ticket_context_md[.dev/2026-06-01-al-dev-ticket-ticket-context.md]
    artifact_ticket_reply_md[.dev/ticket-reply.md]

    skill_al_dev_support_reply --> Phase0
    skill_al_dev_support_reply --> Phase1
    skill_al_dev_support_reply --> Phase2
    skill_al_dev_support_reply --> Phase3
    skill_al_dev_support_reply -.-> skill_al_dev_ticket
    skill_al_dev_support_reply --> agent_al_dev_support_reply_drafter
    skill_al_dev_support_reply --> agent_al_dev_support_researcher
    skill_al_dev_support_reply --> artifact_2026_06_01_al_dev_ticket_ticket_context_md
    skill_al_dev_support_reply --> artifact_ticket_reply_md

    class skill_al_dev_support_reply skillNode
    class Phase0 phaseNode
    class Phase1 phaseNode
    class Phase2 phaseNode
    class Phase3 phaseNode
    class skill_al_dev_ticket skillNode
    class agent_al_dev_support_reply_drafter agentNode
    class agent_al_dev_support_researcher agentNode
    class artifact_2026_06_01_al_dev_ticket_ticket_context_md artifactNode
    class artifact_ticket_reply_md artifactNode
```

Agents spawned: `al-dev-shared:al-dev-support-reply-drafter`, `al-dev-shared:al-dev-support-researcher`
<!-- END GENERATED: skill-drilldown-al-dev-support-reply -->

### /al-dev-investigate

<!-- BEGIN GENERATED: skill-drilldown-al-dev-investigate -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_investigate[al-dev-investigate]
    skill_al_dev_handoff[al-dev-handoff]
    skill_al_dev_plan[al-dev-plan]
    knowledge_explore_subagent_pattern_md[explore-subagent-pattern]
    knowledge_investigate_findings_template_md[investigate-findings-template]
    artifact_YYYY_MM_DD_al_dev_investigate_findings_md[.dev/YYYY-MM-DD-al-dev-investigate-findings.md]
    artifact_investigate_errors_log[.dev/investigate-errors.log]
    artifact_project_context_md[.dev/project-context.md]

    skill_al_dev_investigate -.-> skill_al_dev_handoff
    skill_al_dev_investigate -.-> skill_al_dev_plan
    skill_al_dev_investigate --> knowledge_explore_subagent_pattern_md
    skill_al_dev_investigate --> knowledge_investigate_findings_template_md
    skill_al_dev_investigate --> artifact_YYYY_MM_DD_al_dev_investigate_findings_md
    skill_al_dev_investigate --> artifact_investigate_errors_log
    skill_al_dev_investigate --> artifact_project_context_md

    class skill_al_dev_investigate skillNode
    class skill_al_dev_handoff skillNode
    class skill_al_dev_plan skillNode
    class knowledge_explore_subagent_pattern_md knowledgeNode
    class knowledge_investigate_findings_template_md knowledgeNode
    class artifact_YYYY_MM_DD_al_dev_investigate_findings_md artifactNode
    class artifact_investigate_errors_log artifactNode
    class artifact_project_context_md artifactNode
```
<!-- END GENERATED: skill-drilldown-al-dev-investigate -->

### /al-dev-fix

**Complexity routing:** Trivial fixes skip the analysis phase; complex fixes route through al-dev-solution-architect.

<!-- BEGIN GENERATED: skill-drilldown-al-dev-fix -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_fix[al-dev-fix]
    skill_al_dev_develop[al-dev-develop]
    skill_al_dev_plan[al-dev-plan]
    agent_al_dev_developer_traditional[al-dev-developer-traditional]
    agent_al_dev_solution_architect[al-dev-solution-architect]
    knowledge_al_dev_fix_examples_md[al-dev-fix-examples]
    knowledge_architect_invocation_patterns_md[architect-invocation-patterns]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_compile_lint_procedure_md[compile-lint-procedure]
    knowledge_developer_invocation_patterns_md[developer-invocation-patterns]
    knowledge_intent_preflight_md[intent-preflight]
    artifact_test_plan_md[.dev/test-plan.md]

    skill_al_dev_fix -.-> skill_al_dev_develop
    skill_al_dev_fix -.-> skill_al_dev_plan
    skill_al_dev_fix --> agent_al_dev_developer_traditional
    skill_al_dev_fix --> agent_al_dev_solution_architect
    skill_al_dev_fix --> knowledge_al_dev_fix_examples_md
    skill_al_dev_fix --> knowledge_architect_invocation_patterns_md
    skill_al_dev_fix --> knowledge_artifact_contracts_md
    skill_al_dev_fix --> knowledge_compile_lint_procedure_md
    skill_al_dev_fix --> knowledge_developer_invocation_patterns_md
    skill_al_dev_fix --> knowledge_intent_preflight_md
    skill_al_dev_fix --> artifact_test_plan_md

    class skill_al_dev_fix skillNode
    class skill_al_dev_develop skillNode
    class skill_al_dev_plan skillNode
    class agent_al_dev_developer_traditional agentNode
    class agent_al_dev_solution_architect agentNode
    class knowledge_al_dev_fix_examples_md knowledgeNode
    class knowledge_architect_invocation_patterns_md knowledgeNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_compile_lint_procedure_md knowledgeNode
    class knowledge_developer_invocation_patterns_md knowledgeNode
    class knowledge_intent_preflight_md knowledgeNode
    class artifact_test_plan_md artifactNode
```

Agents spawned: `al-dev-shared:al-dev-developer-traditional`, `al-dev-shared:al-dev-solution-architect`
<!-- END GENERATED: skill-drilldown-al-dev-fix -->

### /al-dev-plan

**Competitive design phase:** Dispatches `/al-dev-plan-preflight` first (context assembly + complexity triage), then multiple architects propose approaches in parallel; the skill synthesises the winner into a solution plan. Dispatches `/al-dev-plan-final-review` for validation and user approval gate before handing off to `/al-dev-develop`. Phases: 0, 2–4.

<!-- BEGIN GENERATED: skill-drilldown-al-dev-plan -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_plan[al-dev-plan]
    Phase0["Phase 0"]
    Phase2["Phase 2"]
    Phase3["Phase 3"]
    Phase4["Phase 4"]
    Phase5["Phase 5"]
    skill_al_dev_plan_preflight[al-dev-plan-preflight]
    agent_al_dev_solution_architect[al-dev-solution-architect]
    knowledge_architect_invocation_patterns_md[architect-invocation-patterns]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_intent_preflight_md[intent-preflight]
    knowledge_preflight_context_schema_md[preflight-context-schema]
    knowledge_solution_plan_template_md[solution-plan-template]
    knowledge_workflow_resilience_md[workflow-resilience]
    artifact_preflight_context_md[.dev/preflight-context.md]
    artifact_progress_md[.dev/progress.md]

    skill_al_dev_plan --> Phase0
    skill_al_dev_plan --> Phase2
    skill_al_dev_plan --> Phase3
    skill_al_dev_plan --> Phase4
    skill_al_dev_plan --> Phase5
    skill_al_dev_plan -.-> skill_al_dev_plan_preflight
    skill_al_dev_plan --> agent_al_dev_solution_architect
    skill_al_dev_plan --> knowledge_architect_invocation_patterns_md
    skill_al_dev_plan --> knowledge_artifact_contracts_md
    skill_al_dev_plan --> knowledge_intent_preflight_md
    skill_al_dev_plan --> knowledge_preflight_context_schema_md
    skill_al_dev_plan --> knowledge_solution_plan_template_md
    skill_al_dev_plan --> knowledge_workflow_resilience_md
    skill_al_dev_plan --> artifact_preflight_context_md
    skill_al_dev_plan --> artifact_progress_md

    class skill_al_dev_plan skillNode
    class Phase0 phaseNode
    class Phase2 phaseNode
    class Phase3 phaseNode
    class Phase4 phaseNode
    class Phase5 phaseNode
    class skill_al_dev_plan_preflight skillNode
    class agent_al_dev_solution_architect agentNode
    class knowledge_architect_invocation_patterns_md knowledgeNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_intent_preflight_md knowledgeNode
    class knowledge_preflight_context_schema_md knowledgeNode
    class knowledge_solution_plan_template_md knowledgeNode
    class knowledge_workflow_resilience_md knowledgeNode
    class artifact_preflight_context_md artifactNode
    class artifact_progress_md artifactNode
```

Agents spawned: `al-dev-shared:al-dev-solution-architect`
<!-- END GENERATED: skill-drilldown-al-dev-plan -->

### /al-dev-plan-final-review

User approval gate for the solution plan written by `/al-dev-plan`. Runs validation and gates approval before implementation begins. Called by `/al-dev-plan` after Phase 5; can also be run standalone. Phases: 1–3.

<!-- BEGIN GENERATED: skill-drilldown-al-dev-plan-final-review -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_plan_final_review[al-dev-plan-final-review]
    Phase1["Phase 1"]
    Phase2["Phase 2"]
    Phase3["Phase 3"]
    skill_al_dev_plan[al-dev-plan]

    skill_al_dev_plan_final_review --> Phase1
    skill_al_dev_plan_final_review --> Phase2
    skill_al_dev_plan_final_review --> Phase3
    skill_al_dev_plan_final_review -.-> skill_al_dev_plan

    class skill_al_dev_plan_final_review skillNode
    class Phase1 phaseNode
    class Phase2 phaseNode
    class Phase3 phaseNode
    class skill_al_dev_plan skillNode
```
<!-- END GENERATED: skill-drilldown-al-dev-plan-final-review -->

### /al-dev-plan-preflight

Preflight context-assembly workflow that `/al-dev-plan` dispatches before the architect debate. Gathers scope, prior findings, and verified context into `.dev/preflight-context.md`. Phases: 0, 0.5, 1, 1.5, 1.6.

<!-- BEGIN GENERATED: skill-drilldown-al-dev-plan-preflight -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_plan_preflight[al-dev-plan-preflight]
    Phase0["Phase 0"]
    Phase0_5["Phase 0.5"]
    Phase1["Phase 1"]
    Phase1_5["Phase 1.5"]
    Phase1_6["Phase 1.6"]
    knowledge_al_dev_plan_phase_routing_md[al-dev-plan-phase-routing]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_intent_preflight_md[intent-preflight]
    knowledge_preflight_context_schema_md[preflight-context-schema]
    knowledge_workflow_resilience_md[workflow-resilience]
    artifact_findings_file_md[.dev/findings-file.md]
    artifact_preflight_context_md[.dev/preflight-context.md]
    artifact_progress_md[.dev/progress.md]
    artifact_project_context_md[.dev/project-context.md]

    skill_al_dev_plan_preflight --> Phase0
    skill_al_dev_plan_preflight --> Phase0_5
    skill_al_dev_plan_preflight --> Phase1
    skill_al_dev_plan_preflight --> Phase1_5
    skill_al_dev_plan_preflight --> Phase1_6
    skill_al_dev_plan_preflight --> knowledge_al_dev_plan_phase_routing_md
    skill_al_dev_plan_preflight --> knowledge_artifact_contracts_md
    skill_al_dev_plan_preflight --> knowledge_intent_preflight_md
    skill_al_dev_plan_preflight --> knowledge_preflight_context_schema_md
    skill_al_dev_plan_preflight --> knowledge_workflow_resilience_md
    skill_al_dev_plan_preflight --> artifact_findings_file_md
    skill_al_dev_plan_preflight --> artifact_preflight_context_md
    skill_al_dev_plan_preflight --> artifact_progress_md
    skill_al_dev_plan_preflight --> artifact_project_context_md

    class skill_al_dev_plan_preflight skillNode
    class Phase0 phaseNode
    class Phase0_5 phaseNode
    class Phase1 phaseNode
    class Phase1_5 phaseNode
    class Phase1_6 phaseNode
    class knowledge_al_dev_plan_phase_routing_md knowledgeNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_intent_preflight_md knowledgeNode
    class knowledge_preflight_context_schema_md knowledgeNode
    class knowledge_workflow_resilience_md knowledgeNode
    class artifact_findings_file_md artifactNode
    class artifact_preflight_context_md artifactNode
    class artifact_progress_md artifactNode
    class artifact_project_context_md artifactNode
```
<!-- END GENERATED: skill-drilldown-al-dev-plan-preflight -->

### /al-dev-develop

**Pre-implementation orchestration:** Reads solution plan, validates scope, partitions work across developers, and dispatches parallel developers. Passes Phase 4 handoff to `/al-dev-review-develop` for compilation, review, and code-review output. Phases: 0–5.

<!-- BEGIN GENERATED: skill-drilldown-al-dev-develop -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_develop[al-dev-develop]
    Phase0["Phase 0"]
    Phase1["Phase 1"]
    Phase2["Phase 2"]
    Phase3["Phase 3"]
    Phase4["Phase 4"]
    skill_al_dev_review_develop[al-dev-review-develop]
    agent_al_dev_developer_tdd[al-dev-developer-tdd]
    agent_al_dev_developer_traditional[al-dev-developer-traditional]
    knowledge_al_dev_develop_spawn_prompt_md[al-dev-develop-spawn-prompt]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_developer_invocation_patterns_md[developer-invocation-patterns]
    knowledge_intent_preflight_md[intent-preflight]
    knowledge_scope_expansion_gate_md[scope-expansion-gate]
    knowledge_workflow_resilience_md[workflow-resilience]
    artifact_progress_md[.dev/progress.md]
    artifact_project_context_md[.dev/project-context.md]

    skill_al_dev_develop --> Phase0
    skill_al_dev_develop --> Phase1
    skill_al_dev_develop --> Phase2
    skill_al_dev_develop --> Phase3
    skill_al_dev_develop --> Phase4
    skill_al_dev_develop -.-> skill_al_dev_review_develop
    skill_al_dev_develop --> agent_al_dev_developer_tdd
    skill_al_dev_develop --> agent_al_dev_developer_traditional
    skill_al_dev_develop --> knowledge_al_dev_develop_spawn_prompt_md
    skill_al_dev_develop --> knowledge_artifact_contracts_md
    skill_al_dev_develop --> knowledge_developer_invocation_patterns_md
    skill_al_dev_develop --> knowledge_intent_preflight_md
    skill_al_dev_develop --> knowledge_scope_expansion_gate_md
    skill_al_dev_develop --> knowledge_workflow_resilience_md
    skill_al_dev_develop --> artifact_progress_md
    skill_al_dev_develop --> artifact_project_context_md

    class skill_al_dev_develop skillNode
    class Phase0 phaseNode
    class Phase1 phaseNode
    class Phase2 phaseNode
    class Phase3 phaseNode
    class Phase4 phaseNode
    class skill_al_dev_review_develop skillNode
    class agent_al_dev_developer_tdd agentNode
    class agent_al_dev_developer_traditional agentNode
    class knowledge_al_dev_develop_spawn_prompt_md knowledgeNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_developer_invocation_patterns_md knowledgeNode
    class knowledge_intent_preflight_md knowledgeNode
    class knowledge_scope_expansion_gate_md knowledgeNode
    class knowledge_workflow_resilience_md knowledgeNode
    class artifact_progress_md artifactNode
    class artifact_project_context_md artifactNode
```

Agents spawned: `al-dev-shared:al-dev-developer-tdd`, `al-dev-shared:al-dev-developer-traditional`
<!-- END GENERATED: skill-drilldown-al-dev-develop -->

### /al-dev-review-develop-preflight

Pre-review qualification workflow dispatched by `/al-dev-develop` before the reviewer panel. Locates the develop handoff, identifies changed AL files, verifies compile, and writes the preflight context file. Phases: 0–3.

<!-- BEGIN GENERATED: skill-drilldown-al-dev-review-develop-preflight -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_review_develop_preflight[al-dev-review-develop-preflight]
    Phase0["Phase 0"]
    Phase1["Phase 1"]
    Phase2["Phase 2"]
    Phase3["Phase 3"]
    skill_al_dev_develop[al-dev-develop]
    skill_al_dev_review_develop[al-dev-review-develop]
    artifact_compile_errors_log[.dev/compile-errors.log]
    artifact_progress_md[.dev/progress.md]

    skill_al_dev_review_develop_preflight --> Phase0
    skill_al_dev_review_develop_preflight --> Phase1
    skill_al_dev_review_develop_preflight --> Phase2
    skill_al_dev_review_develop_preflight --> Phase3
    skill_al_dev_review_develop_preflight -.-> skill_al_dev_develop
    skill_al_dev_review_develop_preflight -.-> skill_al_dev_review_develop
    skill_al_dev_review_develop_preflight --> artifact_compile_errors_log
    skill_al_dev_review_develop_preflight --> artifact_progress_md

    class skill_al_dev_review_develop_preflight skillNode
    class Phase0 phaseNode
    class Phase1 phaseNode
    class Phase2 phaseNode
    class Phase3 phaseNode
    class skill_al_dev_develop skillNode
    class skill_al_dev_review_develop skillNode
    class artifact_compile_errors_log artifactNode
    class artifact_progress_md artifactNode
```
<!-- END GENERATED: skill-drilldown-al-dev-review-develop-preflight -->

### /al-dev-review-develop

**Reviewer dispatch and synthesis:** Reads preflight context from `/al-dev-review-develop-preflight`, then dispatches the three-specialist panel in parallel and synthesises findings. Run `/al-dev-review-develop-preflight` first. Phases: 0, 4–6.

<!-- BEGIN GENERATED: skill-drilldown-al-dev-review-develop -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_review_develop[al-dev-review-develop]
    Phase0["Phase 0"]
    Phase4["Phase 4"]
    Phase5["Phase 5"]
    Phase6["Phase 6"]
    skill_al_dev_commit[al-dev-commit]
    skill_al_dev_review_develop_preflight[al-dev-review-develop-preflight]
    agent_al_dev_al_pattern_reviewer[al-dev-al-pattern-reviewer]
    agent_al_dev_performance_reviewer[al-dev-performance-reviewer]
    agent_al_dev_security_reviewer[al-dev-security-reviewer]
    knowledge_artifact_contracts_md[artifact-contracts]
    artifact_progress_md[.dev/progress.md]

    skill_al_dev_review_develop --> Phase0
    skill_al_dev_review_develop --> Phase4
    skill_al_dev_review_develop --> Phase5
    skill_al_dev_review_develop --> Phase6
    skill_al_dev_review_develop -.-> skill_al_dev_commit
    skill_al_dev_review_develop -.-> skill_al_dev_review_develop_preflight
    skill_al_dev_review_develop --> agent_al_dev_al_pattern_reviewer
    skill_al_dev_review_develop --> agent_al_dev_performance_reviewer
    skill_al_dev_review_develop --> agent_al_dev_security_reviewer
    skill_al_dev_review_develop --> knowledge_artifact_contracts_md
    skill_al_dev_review_develop --> artifact_progress_md

    class skill_al_dev_review_develop skillNode
    class Phase0 phaseNode
    class Phase4 phaseNode
    class Phase5 phaseNode
    class Phase6 phaseNode
    class skill_al_dev_commit skillNode
    class skill_al_dev_review_develop_preflight skillNode
    class agent_al_dev_al_pattern_reviewer agentNode
    class agent_al_dev_performance_reviewer agentNode
    class agent_al_dev_security_reviewer agentNode
    class knowledge_artifact_contracts_md knowledgeNode
    class artifact_progress_md artifactNode
```

Agents spawned: `al-dev-shared:al-dev-al-pattern-reviewer`, `al-dev-shared:al-dev-performance-reviewer`, `al-dev-shared:al-dev-security-reviewer`
<!-- END GENERATED: skill-drilldown-al-dev-review-develop -->

### /al-dev-commit

**Multi-pass execution:** Setup and validation (Phase 0) checks project context, file integrity, staged files, acceptance criteria, and advisory alignment; analysis pass (Phase 1) builds manifests and proposes commit groups with message drafting; confirmation pass (Phase 2) gates user approval; preflight pass (Phase 3) runs lint fixes and OOXML validation; execution pass (Phase 4) runs the commits with hook support and presents the final summary. Five agents with focused responsibilities. Phases: 0–4.

<!-- BEGIN GENERATED: skill-drilldown-al-dev-commit -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_commit[al-dev-commit]
    Phase0["Phase 0"]
    Phase1["Phase 1"]
    Phase2["Phase 2"]
    Phase3["Phase 3"]
    Phase4["Phase 4"]
    agent_al_dev_commit_analyzer[al-dev-commit-analyzer]
    agent_al_dev_commit_executor[al-dev-commit-executor]
    agent_al_dev_commit_hook_fixer[al-dev-commit-hook-fixer]
    agent_al_dev_commit_lint_fixer[al-dev-commit-lint-fixer]
    agent_al_dev_commit_message_drafter[al-dev-commit-message-drafter]
    agent_al_dev_commit_ooxml_validator[al-dev-commit-ooxml-validator]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_commit_dispatch_template_md[commit-dispatch-template]
    knowledge_commit_workflow_orchestration_md[commit-workflow-orchestration]
    knowledge_compile_lint_procedure_md[compile-lint-procedure]
    knowledge_intent_preflight_md[intent-preflight]
    artifact_commits_json[.dev/commits.json]
    artifact_compile_errors_log[.dev/compile-errors.log]
    artifact_file_sizes_json[.dev/file-sizes.json]
    artifact_hook_failures_json[.dev/hook-failures.json]

    skill_al_dev_commit --> Phase0
    skill_al_dev_commit --> Phase1
    skill_al_dev_commit --> Phase2
    skill_al_dev_commit --> Phase3
    skill_al_dev_commit --> Phase4
    skill_al_dev_commit --> agent_al_dev_commit_analyzer
    skill_al_dev_commit --> agent_al_dev_commit_executor
    skill_al_dev_commit --> agent_al_dev_commit_hook_fixer
    skill_al_dev_commit --> agent_al_dev_commit_lint_fixer
    skill_al_dev_commit --> agent_al_dev_commit_message_drafter
    skill_al_dev_commit --> agent_al_dev_commit_ooxml_validator
    skill_al_dev_commit --> knowledge_artifact_contracts_md
    skill_al_dev_commit --> knowledge_commit_dispatch_template_md
    skill_al_dev_commit --> knowledge_commit_workflow_orchestration_md
    skill_al_dev_commit --> knowledge_compile_lint_procedure_md
    skill_al_dev_commit --> knowledge_intent_preflight_md
    skill_al_dev_commit --> artifact_commits_json
    skill_al_dev_commit --> artifact_compile_errors_log
    skill_al_dev_commit --> artifact_file_sizes_json
    skill_al_dev_commit --> artifact_hook_failures_json

    class skill_al_dev_commit skillNode
    class Phase0 phaseNode
    class Phase1 phaseNode
    class Phase2 phaseNode
    class Phase3 phaseNode
    class Phase4 phaseNode
    class agent_al_dev_commit_analyzer agentNode
    class agent_al_dev_commit_executor agentNode
    class agent_al_dev_commit_hook_fixer agentNode
    class agent_al_dev_commit_lint_fixer agentNode
    class agent_al_dev_commit_message_drafter agentNode
    class agent_al_dev_commit_ooxml_validator agentNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_commit_dispatch_template_md knowledgeNode
    class knowledge_commit_workflow_orchestration_md knowledgeNode
    class knowledge_compile_lint_procedure_md knowledgeNode
    class knowledge_intent_preflight_md knowledgeNode
    class artifact_commits_json artifactNode
    class artifact_compile_errors_log artifactNode
    class artifact_file_sizes_json artifactNode
    class artifact_hook_failures_json artifactNode
```

Agents spawned: `al-dev-shared:al-dev-commit-analyzer`, `al-dev-shared:al-dev-commit-executor`, `al-dev-shared:al-dev-commit-hook-fixer`, `al-dev-shared:al-dev-commit-lint-fixer`, `al-dev-shared:al-dev-commit-message-drafter`, `al-dev-shared:al-dev-commit-ooxml-validator`
<!-- END GENERATED: skill-drilldown-al-dev-commit -->

### /al-dev-explore

<!-- BEGIN GENERATED: skill-drilldown-al-dev-explore -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_explore[al-dev-explore]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_explore_subagent_pattern_md[explore-subagent-pattern]
    artifact_2026_05_19_al_dev_explore_findings_md[.dev/2026-05-19-al-dev-explore-findings.md]
    artifact_project_context_md[.dev/project-context.md]

    skill_al_dev_explore --> knowledge_artifact_contracts_md
    skill_al_dev_explore --> knowledge_explore_subagent_pattern_md
    skill_al_dev_explore --> artifact_2026_05_19_al_dev_explore_findings_md
    skill_al_dev_explore --> artifact_project_context_md

    class skill_al_dev_explore skillNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_explore_subagent_pattern_md knowledgeNode
    class artifact_2026_05_19_al_dev_explore_findings_md artifactNode
    class artifact_project_context_md artifactNode
```
<!-- END GENERATED: skill-drilldown-al-dev-explore -->

### /al-dev-interview

Phases: 1–4.

<!-- BEGIN GENERATED: skill-drilldown-al-dev-interview -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_interview[al-dev-interview]
    Phase1["Phase 1"]
    Phase2["Phase 2"]
    Phase3["Phase 3"]
    Phase4["Phase 4"]
    agent_al_dev_interview[al-dev-interview]
    knowledge_artifact_contracts_md[artifact-contracts]

    skill_al_dev_interview --> Phase1
    skill_al_dev_interview --> Phase2
    skill_al_dev_interview --> Phase3
    skill_al_dev_interview --> Phase4
    skill_al_dev_interview --> agent_al_dev_interview
    skill_al_dev_interview --> knowledge_artifact_contracts_md

    class skill_al_dev_interview skillNode
    class Phase1 phaseNode
    class Phase2 phaseNode
    class Phase3 phaseNode
    class Phase4 phaseNode
    class agent_al_dev_interview agentNode
    class knowledge_artifact_contracts_md knowledgeNode
```

Agents spawned: `al-dev-shared:al-dev-interview`
<!-- END GENERATED: skill-drilldown-al-dev-interview -->

### /al-dev-lint

<!-- BEGIN GENERATED: skill-drilldown-al-dev-lint -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_lint[al-dev-lint]
    agent_al_dev_diagnostics_fixer[al-dev-diagnostics-fixer]
    knowledge_al_linting_rules_md[al-linting-rules]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_intent_preflight_md[intent-preflight]
    artifact_compile_errors_log[.dev/compile-errors.log]

    skill_al_dev_lint --> agent_al_dev_diagnostics_fixer
    skill_al_dev_lint --> knowledge_al_linting_rules_md
    skill_al_dev_lint --> knowledge_artifact_contracts_md
    skill_al_dev_lint --> knowledge_intent_preflight_md
    skill_al_dev_lint --> artifact_compile_errors_log

    class skill_al_dev_lint skillNode
    class agent_al_dev_diagnostics_fixer agentNode
    class knowledge_al_linting_rules_md knowledgeNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_intent_preflight_md knowledgeNode
    class artifact_compile_errors_log artifactNode
```

Agents spawned: `al-dev-shared:al-dev-diagnostics-fixer`
<!-- END GENERATED: skill-drilldown-al-dev-lint -->

### /al-dev-document

<!-- BEGIN GENERATED: skill-drilldown-al-dev-document -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_document[al-dev-document]


    class skill_al_dev_document skillNode
```
<!-- END GENERATED: skill-drilldown-al-dev-document -->

### /al-dev-release-notes

Phases: 1, 1.5, 2, 3.

<!-- BEGIN GENERATED: skill-drilldown-al-dev-release-notes -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_release_notes[al-dev-release-notes]
    Phase1["Phase 1"]
    Phase1_5["Phase 1.5"]
    Phase2["Phase 2"]
    Phase3["Phase 3"]
    agent_al_dev_release_notes_writer[al-dev-release-notes-writer]
    artifact_YYYY_MM_DD_plugin_release_notes_md[.dev/YYYY-MM-DD-plugin-release-notes.md]
    artifact_project_context_md[.dev/project-context.md]

    skill_al_dev_release_notes --> Phase1
    skill_al_dev_release_notes --> Phase1_5
    skill_al_dev_release_notes --> Phase2
    skill_al_dev_release_notes --> Phase3
    skill_al_dev_release_notes --> agent_al_dev_release_notes_writer
    skill_al_dev_release_notes --> artifact_YYYY_MM_DD_plugin_release_notes_md
    skill_al_dev_release_notes --> artifact_project_context_md

    class skill_al_dev_release_notes skillNode
    class Phase1 phaseNode
    class Phase1_5 phaseNode
    class Phase2 phaseNode
    class Phase3 phaseNode
    class agent_al_dev_release_notes_writer agentNode
    class artifact_YYYY_MM_DD_plugin_release_notes_md artifactNode
    class artifact_project_context_md artifactNode
```

Agents spawned: `al-dev-shared:al-dev-release-notes-writer`
<!-- END GENERATED: skill-drilldown-al-dev-release-notes -->

### /al-dev-perf

<!-- BEGIN GENERATED: skill-drilldown-al-dev-perf -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_perf[al-dev-perf]
    knowledge_explore_subagent_pattern_md[explore-subagent-pattern]
    knowledge_perf_anti_patterns_prompt_md[perf-anti-patterns-prompt]
    knowledge_perf_report_template_md[perf-report-template]
    artifact_project_context_md[.dev/project-context.md]

    skill_al_dev_perf --> knowledge_explore_subagent_pattern_md
    skill_al_dev_perf --> knowledge_perf_anti_patterns_prompt_md
    skill_al_dev_perf --> knowledge_perf_report_template_md
    skill_al_dev_perf --> artifact_project_context_md

    class skill_al_dev_perf skillNode
    class knowledge_explore_subagent_pattern_md knowledgeNode
    class knowledge_perf_anti_patterns_prompt_md knowledgeNode
    class knowledge_perf_report_template_md knowledgeNode
    class artifact_project_context_md artifactNode
```
<!-- END GENERATED: skill-drilldown-al-dev-perf -->

### /al-dev-handoff

<!-- BEGIN GENERATED: skill-drilldown-al-dev-handoff -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_handoff[al-dev-handoff]
    artifact_explore_findings_md[.dev/explore-findings.md]
    artifact_project_context_md[.dev/project-context.md]
    artifact_source_explore_findings_md[.dev/source-explore-findings.md]
    artifact_source_project_context_md[.dev/source-project-context.md]
    artifact_source_requirements_md[.dev/source-requirements.md]
    artifact_source_solution_plan_md[.dev/source-solution-plan.md]
    artifact_source_ticket_context_md[.dev/source-ticket-context.md]

    skill_al_dev_handoff --> artifact_explore_findings_md
    skill_al_dev_handoff --> artifact_project_context_md
    skill_al_dev_handoff --> artifact_source_explore_findings_md
    skill_al_dev_handoff --> artifact_source_project_context_md
    skill_al_dev_handoff --> artifact_source_requirements_md
    skill_al_dev_handoff --> artifact_source_solution_plan_md
    skill_al_dev_handoff --> artifact_source_ticket_context_md

    class skill_al_dev_handoff skillNode
    class artifact_explore_findings_md artifactNode
    class artifact_project_context_md artifactNode
    class artifact_source_explore_findings_md artifactNode
    class artifact_source_project_context_md artifactNode
    class artifact_source_requirements_md artifactNode
    class artifact_source_solution_plan_md artifactNode
    class artifact_source_ticket_context_md artifactNode
```
<!-- END GENERATED: skill-drilldown-al-dev-handoff -->

### /al-dev-help

No agents spawned; no `.dev/` output. The skill reads available context files and presents contextual guidance inline.

<!-- BEGIN GENERATED: skill-drilldown-al-dev-help -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_help[al-dev-help]
    skill_al_dev_develop[al-dev-develop]
    skill_al_dev_plan[al-dev-plan]
    knowledge_workflow_routing_md[workflow-routing]
    artifact_2026_05_19_al_dev_develop_code_review_md[.dev/2026-05-19-al-dev-develop-code-review.md]
    artifact_2026_05_19_al_dev_interview_requirements_md[.dev/2026-05-19-al-dev-interview-requirements.md]
    artifact_2026_05_19_al_dev_plan_solution_plan_md[.dev/2026-05-19-al-dev-plan-solution-plan.md]
    artifact_project_context_md[.dev/project-context.md]

    skill_al_dev_help -.-> skill_al_dev_develop
    skill_al_dev_help -.-> skill_al_dev_plan
    skill_al_dev_help --> knowledge_workflow_routing_md
    skill_al_dev_help --> artifact_2026_05_19_al_dev_develop_code_review_md
    skill_al_dev_help --> artifact_2026_05_19_al_dev_interview_requirements_md
    skill_al_dev_help --> artifact_2026_05_19_al_dev_plan_solution_plan_md
    skill_al_dev_help --> artifact_project_context_md

    class skill_al_dev_help skillNode
    class skill_al_dev_develop skillNode
    class skill_al_dev_plan skillNode
    class knowledge_workflow_routing_md knowledgeNode
    class artifact_2026_05_19_al_dev_develop_code_review_md artifactNode
    class artifact_2026_05_19_al_dev_interview_requirements_md artifactNode
    class artifact_2026_05_19_al_dev_plan_solution_plan_md artifactNode
    class artifact_project_context_md artifactNode
```
<!-- END GENERATED: skill-drilldown-al-dev-help -->

### /commit-recover

Spawns one fixer per corrupted-file incident found in `.dev/commit-integrity.log`.

<!-- BEGIN GENERATED: skill-drilldown-commit-recover -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_commit_recover[commit-recover]
    agent_al_dev_commit_recover_fixer[al-dev-commit-recover-fixer]
    artifact_commit_integrity_log[.dev/commit-integrity.log]
    artifact_compile_errors_log[.dev/compile-errors.log]
    artifact_learnings_md[.dev/learnings.md]

    skill_commit_recover --> agent_al_dev_commit_recover_fixer
    skill_commit_recover --> artifact_commit_integrity_log
    skill_commit_recover --> artifact_compile_errors_log
    skill_commit_recover --> artifact_learnings_md

    class skill_commit_recover skillNode
    class agent_al_dev_commit_recover_fixer agentNode
    class artifact_commit_integrity_log artifactNode
    class artifact_compile_errors_log artifactNode
    class artifact_learnings_md artifactNode
```

Agents spawned: `al-dev-shared:al-dev-commit-recover-fixer`
<!-- END GENERATED: skill-drilldown-commit-recover -->

### /al-dev-plan-critic-review

Spawns 6 parallel critic agents (generic Agent tool calls) to red-team a plan. Synthesizes findings into ranked recommendations.

<!-- BEGIN GENERATED: skill-drilldown-al-dev-plan-critic-review -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_al_dev_plan_critic_review[al-dev-plan-critic-review]
    artifact_plan_critique_YYYYMMDD_md[.dev/plan-critique-YYYYMMDD.md]

    skill_al_dev_plan_critic_review --> artifact_plan_critique_YYYYMMDD_md

    class skill_al_dev_plan_critic_review skillNode
    class artifact_plan_critique_YYYYMMDD_md artifactNode
```
<!-- END GENERATED: skill-drilldown-al-dev-plan-critic-review -->

### /verify-commits

No agents spawned; compares git commits against plan and optionally re-splits combined commits.

<!-- BEGIN GENERATED: skill-drilldown-verify-commits -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_verify_commits[verify-commits]


    class skill_verify_commits skillNode
```
<!-- END GENERATED: skill-drilldown-verify-commits -->

---

## Observations

> **Findings live in the health dossier, not in this map.** This map is
> documentation only — it describes the current skill structure. To find
> improvement suggestions (Atomise, Absorb, Connect, Merge, Promote, Move,
> Extend), run `/plugin-health-audit` and read the ranked dossier in
> `docs/health/`, then `/al-dev-map-suggestions-verify` to turn accepted
> findings into a plan.
>
> History: in-map suggestions through 2026-05-27 were retired when findings
> converged on the health dossier (2026-06-02).
>
