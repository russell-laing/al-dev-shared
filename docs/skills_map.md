# AL Dev Plugin Map

> A reference tool for understanding skill relationships, agent patterns, and file handoffs in profile-al-dev-shared. This document is for personal gap analysis and extension planning, not onboarding.
>
> **Generated sections** are refreshed by `scripts/generate_map_doc_sections.py`. Layer 2 drill-downs include Phase<N> nodes extracted from each skill's SKILL.md file. Do not hand-edit inside `<!-- BEGIN/END GENERATED -->` markers.

**Last updated:** 2026-06-28

<!-- BEGIN GENERATED: skill-coverage -->
**Coverage:** 23 active skills in `profile-al-dev-shared/skills/` (count derived from disk at generation time).
<!-- END GENERATED: skill-coverage -->

**Scope:** Active skill directories only. Archived items (`al-dev-test`, test-engineer agents, `al-dev-test-coverage-reviewer`, `al-dev-align`) excluded. Layer 1 contains 21 primary lifecycle skills. Layer 2 includes 1 additional distributed utility (`/al-dev-help`). Maintainer-surface skills (e.g. `al-dev-consolidate`, relocated to `.claude/skills/`) and tools are documented in separate tracking systems.

---

## Layer 1: Lifecycle Overview

This diagram shows pre-planning tributaries (dashed, optional), the three main entry points, and the development spine through to post-commit output.

<!-- BEGIN GENERATED: skill-lifecycle-mermaid -->
```mermaid
flowchart TD
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    skill_commit[commit]
    skill_commit_recover[commit-recover]
    skill_develop_orchestrate[develop-orchestrate]
    skill_document[document]
    skill_explore[explore]
    skill_fix[fix]
    skill_handoff[handoff]
    skill_interview[interview]
    skill_investigate[investigate]
    skill_lint[lint]
    skill_perf[perf]
    skill_plan[plan]
    skill_plan_preflight[plan-preflight]
    skill_release_notes[release-notes]
    skill_review_develop[review-develop]
    skill_support_reply[support-reply]
    skill_ticket[ticket]

    skill_commit -.-> skill_document
    skill_commit -.-> skill_handoff
    skill_commit -.-> skill_release_notes
    skill_commit_recover --> skill_commit
    skill_develop_orchestrate --> skill_review_develop
    skill_develop_orchestrate -.-> skill_lint
    skill_explore -.-> |explore-findings.md| skill_plan
    skill_fix --> skill_commit
    skill_interview -.-> |interview-requirements.md| skill_plan
    skill_investigate -.-> skill_plan
    skill_perf -.-> |perf-analysis.md| skill_plan
    skill_plan --> skill_develop_orchestrate
    skill_plan_preflight -.-> |preflight-context.md| skill_plan
    skill_review_develop --> skill_commit
    skill_ticket --> skill_support_reply

    class skill_commit skillNode
    class skill_commit_recover skillNode
    class skill_develop_orchestrate skillNode
    class skill_document skillNode
    class skill_explore skillNode
    class skill_fix skillNode
    class skill_handoff skillNode
    class skill_interview skillNode
    class skill_investigate skillNode
    class skill_lint skillNode
    class skill_perf skillNode
    class skill_plan skillNode
    class skill_plan_preflight skillNode
    class skill_release_notes skillNode
    class skill_review_develop skillNode
    class skill_support_reply skillNode
    class skill_ticket skillNode
```
<!-- END GENERATED: skill-lifecycle-mermaid -->

---

## Layer 2: Per-Skill Drill-Downs

Each skill is shown with its internal phases, spawned agents, and key outputs. Agents are referenced by their full type name (for example, `al-dev-shared:developer-tdd`).

### Notation

- **Phase**: Numbered step inside the skill
- **Agent**: Which agent (or skill itself) executes the phase
- **Pattern**: ×1 (serial), ×2-3 (parallel), ×N (variable count)
- **Output**: File written to `.dev/` or code generated

### /al-dev-ticket

**Two modes:** `--mode=context-only` (default fetch/context only) and `--mode=full` (fetch context then chains to `/al-dev-support-reply`). Research and reply drafting are handled by `/al-dev-support-reply`. Phases: 0, 0.5, 5.

<!-- BEGIN GENERATED: skill-drilldown-ticket -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_ticket[ticket]
    Phase0["Phase 0"]
    Phase0_5["Phase 0.5"]
    Phase1["Phase 1"]
    Phase1_5["Phase 1.5"]
    Phase2["Phase 2"]
    Phase3["Phase 3"]
    Phase4["Phase 4"]
    Phase5["Phase 5"]
    skill_interview[interview]
    skill_plan[plan]
    skill_support_reply[support-reply]
    agent_ticket_context_writer[ticket-context-writer]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_ticket_agent_invocation_pattern_md[ticket-agent-invocation-pattern]

    skill_ticket --> Phase0
    skill_ticket --> Phase0_5
    skill_ticket --> Phase1
    skill_ticket --> Phase1_5
    skill_ticket --> Phase2
    skill_ticket --> Phase3
    skill_ticket --> Phase4
    skill_ticket --> Phase5
    skill_ticket -.-> skill_interview
    skill_ticket -.-> skill_plan
    skill_ticket -.-> skill_support_reply
    skill_ticket --> agent_ticket_context_writer
    skill_ticket --> knowledge_artifact_contracts_md
    skill_ticket --> knowledge_ticket_agent_invocation_pattern_md

    class skill_ticket skillNode
    class Phase0 phaseNode
    class Phase0_5 phaseNode
    class Phase1 phaseNode
    class Phase1_5 phaseNode
    class Phase2 phaseNode
    class Phase3 phaseNode
    class Phase4 phaseNode
    class Phase5 phaseNode
    class skill_interview skillNode
    class skill_plan skillNode
    class skill_support_reply skillNode
    class agent_ticket_context_writer agentNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_ticket_agent_invocation_pattern_md knowledgeNode
```

Agents spawned: `al-dev-shared:ticket-context-writer`
<!-- END GENERATED: skill-drilldown-ticket -->

### /al-dev-support-reply

Follow-on support workflow used after `/al-dev-ticket --mode=full`. Researches the issue and drafts the customer-facing reply using the ticket context prepared upstream. Phases: 0, 1, 2, 3, 4.

<!-- BEGIN GENERATED: skill-drilldown-support-reply -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_support_reply[support-reply]
    Phase0["Phase 0"]
    Phase1["Phase 1"]
    Phase2["Phase 2"]
    Phase3["Phase 3"]
    Phase4["Phase 4"]
    skill_ticket[ticket]
    agent_support_reply_drafter[support-reply-drafter]
    agent_support_researcher[support-researcher]
    artifact_2026_06_01_ticket_ticket_context_md[.dev/2026-06-01-ticket-ticket-context.md]
    artifact_YYYY_MM_DD_ticket_reply_md[.dev/YYYY-MM-DD-ticket-reply.md]

    skill_support_reply --> Phase0
    skill_support_reply --> Phase1
    skill_support_reply --> Phase2
    skill_support_reply --> Phase3
    skill_support_reply --> Phase4
    skill_support_reply -.-> skill_ticket
    skill_support_reply --> agent_support_reply_drafter
    skill_support_reply --> agent_support_researcher
    skill_support_reply --> artifact_2026_06_01_ticket_ticket_context_md
    skill_support_reply --> artifact_YYYY_MM_DD_ticket_reply_md

    class skill_support_reply skillNode
    class Phase0 phaseNode
    class Phase1 phaseNode
    class Phase2 phaseNode
    class Phase3 phaseNode
    class Phase4 phaseNode
    class skill_ticket skillNode
    class agent_support_reply_drafter agentNode
    class agent_support_researcher agentNode
    class artifact_2026_06_01_ticket_ticket_context_md artifactNode
    class artifact_YYYY_MM_DD_ticket_reply_md artifactNode
```

Agents spawned: `al-dev-shared:support-reply-drafter`, `al-dev-shared:support-researcher`
<!-- END GENERATED: skill-drilldown-support-reply -->

### /al-dev-investigate

<!-- BEGIN GENERATED: skill-drilldown-investigate -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_investigate[investigate]
    skill_fix[fix]
    skill_handoff[handoff]
    skill_plan[plan]
    agent_explore[explore]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_explore_subagent_pattern_md[explore-subagent-pattern]
    knowledge_investigate_findings_template_md[investigate-findings-template]
    knowledge_workflow_resilience_md[workflow-resilience]
    artifact_YYYY_MM_DD_investigate_findings_md[.dev/YYYY-MM-DD-investigate-findings.md]
    artifact_investigate_errors_log[.dev/investigate-errors.log]
    artifact_project_context_md[.dev/project-context.md]

    skill_investigate -.-> skill_fix
    skill_investigate -.-> skill_handoff
    skill_investigate -.-> skill_plan
    skill_investigate --> agent_explore
    skill_investigate --> knowledge_artifact_contracts_md
    skill_investigate --> knowledge_explore_subagent_pattern_md
    skill_investigate --> knowledge_investigate_findings_template_md
    skill_investigate --> knowledge_workflow_resilience_md
    skill_investigate --> artifact_YYYY_MM_DD_investigate_findings_md
    skill_investigate --> artifact_investigate_errors_log
    skill_investigate --> artifact_project_context_md

    class skill_investigate skillNode
    class skill_fix skillNode
    class skill_handoff skillNode
    class skill_plan skillNode
    class agent_explore agentNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_explore_subagent_pattern_md knowledgeNode
    class knowledge_investigate_findings_template_md knowledgeNode
    class knowledge_workflow_resilience_md knowledgeNode
    class artifact_YYYY_MM_DD_investigate_findings_md artifactNode
    class artifact_investigate_errors_log artifactNode
    class artifact_project_context_md artifactNode
```

Agents spawned: `al-dev-shared:explore`
<!-- END GENERATED: skill-drilldown-investigate -->

### /al-dev-fix

**Complexity routing:** Trivial fixes skip the analysis phase; complex fixes route through `solution-architect`.

<!-- BEGIN GENERATED: skill-drilldown-fix -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_fix[fix]
    skill_develop_orchestrate[develop-orchestrate]
    skill_plan[plan]
    agent_developer_traditional[developer-traditional]
    agent_solution_architect[solution-architect]
    knowledge_architect_invocation_patterns_md[architect-invocation-patterns]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_compile_lint_procedure_md[compile-lint-procedure]
    knowledge_developer_invocation_patterns_md[developer-invocation-patterns]
    knowledge_fix_examples_md[fix-examples]
    knowledge_intent_preflight_md[intent-preflight]
    knowledge_scope_expansion_gate_md[scope-expansion-gate]
    artifact_test_plan_md[.dev/test-plan.md]

    skill_fix -.-> skill_develop_orchestrate
    skill_fix -.-> skill_plan
    skill_fix --> agent_developer_traditional
    skill_fix --> agent_solution_architect
    skill_fix --> knowledge_architect_invocation_patterns_md
    skill_fix --> knowledge_artifact_contracts_md
    skill_fix --> knowledge_compile_lint_procedure_md
    skill_fix --> knowledge_developer_invocation_patterns_md
    skill_fix --> knowledge_fix_examples_md
    skill_fix --> knowledge_intent_preflight_md
    skill_fix --> knowledge_scope_expansion_gate_md
    skill_fix --> artifact_test_plan_md

    class skill_fix skillNode
    class skill_develop_orchestrate skillNode
    class skill_plan skillNode
    class agent_developer_traditional agentNode
    class agent_solution_architect agentNode
    class knowledge_architect_invocation_patterns_md knowledgeNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_compile_lint_procedure_md knowledgeNode
    class knowledge_developer_invocation_patterns_md knowledgeNode
    class knowledge_fix_examples_md knowledgeNode
    class knowledge_intent_preflight_md knowledgeNode
    class knowledge_scope_expansion_gate_md knowledgeNode
    class artifact_test_plan_md artifactNode
```

Agents spawned: `al-dev-shared:developer-traditional`, `al-dev-shared:solution-architect`
<!-- END GENERATED: skill-drilldown-fix -->

### /al-dev-plan

**Competitive design phase:** Dispatches `/al-dev-plan-preflight` first (context assembly + complexity triage), then multiple architects propose approaches in parallel; the skill synthesises the winner into a solution plan. Dispatches `/al-dev-plan-final-review` for validation and user approval gate before handing off to `/al-dev-develop-orchestrate`. Phases: 0, 2, 3, 4, 5.

<!-- BEGIN GENERATED: skill-drilldown-plan -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_plan[plan]
    Phase0["Phase 0"]
    Phase2["Phase 2"]
    Phase3["Phase 3"]
    Phase4["Phase 4"]
    Phase5["Phase 5"]
    skill_plan_preflight[plan-preflight]
    agent_solution_architect[solution-architect]
    knowledge_architect_evaluation_criteria_md[architect-evaluation-criteria]
    knowledge_architect_invocation_patterns_md[architect-invocation-patterns]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_intent_preflight_md[intent-preflight]
    knowledge_preflight_context_schema_md[preflight-context-schema]
    knowledge_solution_plan_template_md[solution-plan-template]
    knowledge_workflow_resilience_md[workflow-resilience]
    artifact_preflight_context_md[.dev/preflight-context.md]
    artifact_progress_md[.dev/progress.md]

    skill_plan --> Phase0
    skill_plan --> Phase2
    skill_plan --> Phase3
    skill_plan --> Phase4
    skill_plan --> Phase5
    skill_plan -.-> skill_plan_preflight
    skill_plan --> agent_solution_architect
    skill_plan --> knowledge_architect_evaluation_criteria_md
    skill_plan --> knowledge_architect_invocation_patterns_md
    skill_plan --> knowledge_artifact_contracts_md
    skill_plan --> knowledge_intent_preflight_md
    skill_plan --> knowledge_preflight_context_schema_md
    skill_plan --> knowledge_solution_plan_template_md
    skill_plan --> knowledge_workflow_resilience_md
    skill_plan --> artifact_preflight_context_md
    skill_plan --> artifact_progress_md

    class skill_plan skillNode
    class Phase0 phaseNode
    class Phase2 phaseNode
    class Phase3 phaseNode
    class Phase4 phaseNode
    class Phase5 phaseNode
    class skill_plan_preflight skillNode
    class agent_solution_architect agentNode
    class knowledge_architect_evaluation_criteria_md knowledgeNode
    class knowledge_architect_invocation_patterns_md knowledgeNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_intent_preflight_md knowledgeNode
    class knowledge_preflight_context_schema_md knowledgeNode
    class knowledge_solution_plan_template_md knowledgeNode
    class knowledge_workflow_resilience_md knowledgeNode
    class artifact_preflight_context_md artifactNode
    class artifact_progress_md artifactNode
```

Agents spawned: `al-dev-shared:solution-architect`
<!-- END GENERATED: skill-drilldown-plan -->

### /al-dev-plan-final-review

User approval gate for the solution plan written by `/al-dev-plan`. Runs validation and gates approval before implementation begins. Called by `/al-dev-plan` after Phase 5; can also be run standalone. Phases: 0–3.

<!-- BEGIN GENERATED: skill-drilldown-plan-final-review -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_plan_final_review[plan-final-review]
    Phase1["Phase 1"]
    Phase2["Phase 2"]
    Phase2_5["Phase 2.5"]
    Phase3["Phase 3"]
    skill_plan[plan]
    skill_plan_with_critics[plan-with-critics]

    skill_plan_final_review --> Phase1
    skill_plan_final_review --> Phase2
    skill_plan_final_review --> Phase2_5
    skill_plan_final_review --> Phase3
    skill_plan_final_review -.-> skill_plan
    skill_plan_final_review -.-> skill_plan_with_critics

    class skill_plan_final_review skillNode
    class Phase1 phaseNode
    class Phase2 phaseNode
    class Phase2_5 phaseNode
    class Phase3 phaseNode
    class skill_plan skillNode
    class skill_plan_with_critics skillNode
```
<!-- END GENERATED: skill-drilldown-plan-final-review -->

### /al-dev-plan-preflight

Preflight context-assembly workflow that `/al-dev-plan` dispatches before the architect debate. Gathers scope, prior findings, and verified context into `.dev/preflight-context.md`. Phases: 0–4.

<!-- BEGIN GENERATED: skill-drilldown-plan-preflight -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_plan_preflight[plan-preflight]
    Phase0["Phase 0"]
    Phase0_5["Phase 0.5"]
    Phase1["Phase 1"]
    Phase1_5["Phase 1.5"]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_companion_context_ownership_md[companion-context-ownership]
    knowledge_intent_preflight_md[intent-preflight]
    knowledge_plan_phase_routing_md[plan-phase-routing]
    knowledge_preflight_context_schema_md[preflight-context-schema]
    knowledge_workflow_resilience_md[workflow-resilience]
    artifact_findings_file_md[.dev/findings-file.md]
    artifact_preflight_context_md[.dev/preflight-context.md]
    artifact_progress_md[.dev/progress.md]
    artifact_project_context_md[.dev/project-context.md]

    skill_plan_preflight --> Phase0
    skill_plan_preflight --> Phase0_5
    skill_plan_preflight --> Phase1
    skill_plan_preflight --> Phase1_5
    skill_plan_preflight --> knowledge_artifact_contracts_md
    skill_plan_preflight --> knowledge_companion_context_ownership_md
    skill_plan_preflight --> knowledge_intent_preflight_md
    skill_plan_preflight --> knowledge_plan_phase_routing_md
    skill_plan_preflight --> knowledge_preflight_context_schema_md
    skill_plan_preflight --> knowledge_workflow_resilience_md
    skill_plan_preflight --> artifact_findings_file_md
    skill_plan_preflight --> artifact_preflight_context_md
    skill_plan_preflight --> artifact_progress_md
    skill_plan_preflight --> artifact_project_context_md

    class skill_plan_preflight skillNode
    class Phase0 phaseNode
    class Phase0_5 phaseNode
    class Phase1 phaseNode
    class Phase1_5 phaseNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_companion_context_ownership_md knowledgeNode
    class knowledge_intent_preflight_md knowledgeNode
    class knowledge_plan_phase_routing_md knowledgeNode
    class knowledge_preflight_context_schema_md knowledgeNode
    class knowledge_workflow_resilience_md knowledgeNode
    class artifact_findings_file_md artifactNode
    class artifact_preflight_context_md artifactNode
    class artifact_progress_md artifactNode
    class artifact_project_context_md artifactNode
```
<!-- END GENERATED: skill-drilldown-plan-preflight -->

### /al-dev-plan-with-critics

Generate an implementation plan then dispatch 6 parallel critic agents to red-team it. Synthesizes findings, applies auto-fixes, and gates user approval before execution.

<!-- BEGIN GENERATED: skill-drilldown-plan-with-critics -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_plan_with_critics[plan-with-critics]
    artifact_plan_critique_YYYY_MM_DD_md[.dev/plan-critique-YYYY-MM-DD.md]

    skill_plan_with_critics --> artifact_plan_critique_YYYY_MM_DD_md

    class skill_plan_with_critics skillNode
    class artifact_plan_critique_YYYY_MM_DD_md artifactNode
```
<!-- END GENERATED: skill-drilldown-plan-with-critics -->

### /al-dev-develop-orchestrate

**Pre-implementation orchestration:** Reads solution plan, validates scope, partitions work across developers, and dispatches parallel developers. Passes Phase 4 handoff to `/al-dev-review-develop` for compilation, review, and code-review output. Phases: 0, 1, 2, 3, 4.

<!-- BEGIN GENERATED: skill-drilldown-develop-orchestrate -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_develop_orchestrate[develop-orchestrate]
    Phase0["Phase 0"]
    Phase1["Phase 1"]
    Phase2["Phase 2"]
    Phase3["Phase 3"]
    Phase4["Phase 4"]
    skill_review_develop[review-develop]
    agent_developer_tdd[developer-tdd]
    agent_developer_traditional[developer-traditional]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_companion_context_ownership_md[companion-context-ownership]
    knowledge_developer_invocation_patterns_md[developer-invocation-patterns]
    knowledge_intent_preflight_md[intent-preflight]
    knowledge_scope_expansion_gate_md[scope-expansion-gate]
    knowledge_workflow_resilience_md[workflow-resilience]
    artifact_progress_md[.dev/progress.md]
    artifact_project_context_md[.dev/project-context.md]

    skill_develop_orchestrate --> Phase0
    skill_develop_orchestrate --> Phase1
    skill_develop_orchestrate --> Phase2
    skill_develop_orchestrate --> Phase3
    skill_develop_orchestrate --> Phase4
    skill_develop_orchestrate -.-> skill_review_develop
    skill_develop_orchestrate --> agent_developer_tdd
    skill_develop_orchestrate --> agent_developer_traditional
    skill_develop_orchestrate --> knowledge_artifact_contracts_md
    skill_develop_orchestrate --> knowledge_companion_context_ownership_md
    skill_develop_orchestrate --> knowledge_developer_invocation_patterns_md
    skill_develop_orchestrate --> knowledge_intent_preflight_md
    skill_develop_orchestrate --> knowledge_scope_expansion_gate_md
    skill_develop_orchestrate --> knowledge_workflow_resilience_md
    skill_develop_orchestrate --> artifact_progress_md
    skill_develop_orchestrate --> artifact_project_context_md

    class skill_develop_orchestrate skillNode
    class Phase0 phaseNode
    class Phase1 phaseNode
    class Phase2 phaseNode
    class Phase3 phaseNode
    class Phase4 phaseNode
    class skill_review_develop skillNode
    class agent_developer_tdd agentNode
    class agent_developer_traditional agentNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_companion_context_ownership_md knowledgeNode
    class knowledge_developer_invocation_patterns_md knowledgeNode
    class knowledge_intent_preflight_md knowledgeNode
    class knowledge_scope_expansion_gate_md knowledgeNode
    class knowledge_workflow_resilience_md knowledgeNode
    class artifact_progress_md artifactNode
    class artifact_project_context_md artifactNode
```

Agents spawned: `al-dev-shared:developer-tdd`, `al-dev-shared:developer-traditional`
<!-- END GENERATED: skill-drilldown-develop-orchestrate -->

### /al-dev-review-develop-preflight

Pre-review qualification workflow dispatched by `/al-dev-develop-orchestrate` before the reviewer panel. Locates the develop handoff, identifies changed AL files, verifies compile, and writes the preflight context file. Phases: 0, 1, 2, 3.

<!-- BEGIN GENERATED: skill-drilldown-review-develop-preflight -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_review_develop_preflight[review-develop-preflight]
    Phase0["Phase 0"]
    Phase1["Phase 1"]
    Phase2["Phase 2"]
    Phase3["Phase 3"]
    skill_develop_orchestrate[develop-orchestrate]
    skill_review_develop[review-develop]
    artifact_compile_errors_log[.dev/compile-errors.log]
    artifact_progress_md[.dev/progress.md]

    skill_review_develop_preflight --> Phase0
    skill_review_develop_preflight --> Phase1
    skill_review_develop_preflight --> Phase2
    skill_review_develop_preflight --> Phase3
    skill_review_develop_preflight -.-> skill_develop_orchestrate
    skill_review_develop_preflight -.-> skill_review_develop
    skill_review_develop_preflight --> artifact_compile_errors_log
    skill_review_develop_preflight --> artifact_progress_md

    class skill_review_develop_preflight skillNode
    class Phase0 phaseNode
    class Phase1 phaseNode
    class Phase2 phaseNode
    class Phase3 phaseNode
    class skill_develop_orchestrate skillNode
    class skill_review_develop skillNode
    class artifact_compile_errors_log artifactNode
    class artifact_progress_md artifactNode
```
<!-- END GENERATED: skill-drilldown-review-develop-preflight -->

### /al-dev-review-develop

**Reviewer dispatch and synthesis:** Reads preflight context from `/al-dev-review-develop-preflight`, then dispatches the three-specialist panel in parallel and synthesises findings. Run `/al-dev-review-develop-preflight` first. Phases: 0, 4, 5, 6.

<!-- BEGIN GENERATED: skill-drilldown-review-develop -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_review_develop[review-develop]
    Phase0["Phase 0"]
    Phase4["Phase 4"]
    Phase5["Phase 5"]
    Phase6["Phase 6"]
    skill_commit[commit]
    skill_review_develop_preflight[review-develop-preflight]
    agent_al_pattern_reviewer[al-pattern-reviewer]
    agent_performance_reviewer[performance-reviewer]
    agent_security_reviewer[security-reviewer]
    knowledge_artifact_contracts_md[artifact-contracts]
    artifact_progress_md[.dev/progress.md]

    skill_review_develop --> Phase0
    skill_review_develop --> Phase4
    skill_review_develop --> Phase5
    skill_review_develop --> Phase6
    skill_review_develop -.-> skill_commit
    skill_review_develop -.-> skill_review_develop_preflight
    skill_review_develop --> agent_al_pattern_reviewer
    skill_review_develop --> agent_performance_reviewer
    skill_review_develop --> agent_security_reviewer
    skill_review_develop --> knowledge_artifact_contracts_md
    skill_review_develop --> artifact_progress_md

    class skill_review_develop skillNode
    class Phase0 phaseNode
    class Phase4 phaseNode
    class Phase5 phaseNode
    class Phase6 phaseNode
    class skill_commit skillNode
    class skill_review_develop_preflight skillNode
    class agent_al_pattern_reviewer agentNode
    class agent_performance_reviewer agentNode
    class agent_security_reviewer agentNode
    class knowledge_artifact_contracts_md knowledgeNode
    class artifact_progress_md artifactNode
```

Agents spawned: `al-dev-shared:al-pattern-reviewer`, `al-dev-shared:performance-reviewer`, `al-dev-shared:security-reviewer`
<!-- END GENERATED: skill-drilldown-review-develop -->

### /al-dev-commit

**Multi-pass execution:** Setup and validation (Phase 0) checks project context, file integrity, staged files, acceptance criteria, and advisory alignment; analysis pass (Phase 1) builds manifests and proposes commit groups with message drafting; confirmation pass (Phase 2) gates user approval; preflight pass (Phase 3) runs lint fixes and OOXML validation; execution pass (Phase 4) runs the commits with hook support and presents the final summary. Five agents with focused responsibilities. Phases: 0, 1, 2.

<!-- BEGIN GENERATED: skill-drilldown-commit -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_commit[commit]
    skill_commit_execute[commit-execute]
    skill_commit_preflight[commit-preflight]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_commit_intent_preflight_md[commit-intent-preflight]
    artifact_commit_preflight_md[.dev/commit-preflight.md]

    skill_commit -.-> skill_commit_execute
    skill_commit -.-> skill_commit_preflight
    skill_commit --> knowledge_artifact_contracts_md
    skill_commit --> knowledge_commit_intent_preflight_md
    skill_commit --> artifact_commit_preflight_md

    class skill_commit skillNode
    class skill_commit_execute skillNode
    class skill_commit_preflight skillNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_commit_intent_preflight_md knowledgeNode
    class artifact_commit_preflight_md artifactNode
```
<!-- END GENERATED: skill-drilldown-commit -->

### /al-dev-commit-execute

Phases 0, 3, 4 of the atomic commit workflow. Loads the approved plan from `.dev/commit-preflight.md`, runs lint preflight and OOXML validation, dispatches the execution agent, handles hook failures via the classifier+fixer recovery pipeline, and summarises results.

<!-- BEGIN GENERATED: skill-drilldown-commit-execute -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_commit_execute[commit-execute]
    Phase0["Phase 0"]
    Phase3["Phase 3"]
    Phase4["Phase 4"]
    skill_commit[commit]
    agent_commit_executor[commit-executor]
    agent_commit_hook_classifier[commit-hook-classifier]
    agent_commit_hook_fixer[commit-hook-fixer]
    agent_commit_lint_fixer[commit-lint-fixer]
    artifact_commit_preflight_md[.dev/commit-preflight.md]
    artifact_commits_json[.dev/commits.json]
    artifact_hook_failures_json[.dev/hook-failures.json]

    skill_commit_execute --> Phase0
    skill_commit_execute --> Phase3
    skill_commit_execute --> Phase4
    skill_commit_execute -.-> skill_commit
    skill_commit_execute --> agent_commit_executor
    skill_commit_execute --> agent_commit_hook_classifier
    skill_commit_execute --> agent_commit_hook_fixer
    skill_commit_execute --> agent_commit_lint_fixer
    skill_commit_execute --> artifact_commit_preflight_md
    skill_commit_execute --> artifact_commits_json
    skill_commit_execute --> artifact_hook_failures_json

    class skill_commit_execute skillNode
    class Phase0 phaseNode
    class Phase3 phaseNode
    class Phase4 phaseNode
    class skill_commit skillNode
    class agent_commit_executor agentNode
    class agent_commit_hook_classifier agentNode
    class agent_commit_hook_fixer agentNode
    class agent_commit_lint_fixer agentNode
    class artifact_commit_preflight_md artifactNode
    class artifact_commits_json artifactNode
    class artifact_hook_failures_json artifactNode
```

Agents spawned: `al-dev-shared:commit-executor`, `al-dev-shared:commit-hook-classifier`, `al-dev-shared:commit-hook-fixer`, `al-dev-shared:commit-lint-fixer`
<!-- END GENERATED: skill-drilldown-commit-execute -->

### /al-dev-commit-preflight

Phases 0, 1, 2 of the atomic commit workflow. Validates staged files, dispatches the analysis and message-drafting agents, handles user confirmation gates, and persists the approved plan to `.dev/commit-preflight.md`.

<!-- BEGIN GENERATED: skill-drilldown-commit-preflight -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_commit_preflight[commit-preflight]
    Phase0["Phase 0"]
    Phase1["Phase 1"]
    Phase2["Phase 2"]
    skill_commit_execute[commit-execute]
    agent_commit_analyzer[commit-analyzer]
    agent_commit_group_drafter[commit-group-drafter]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_commit_compile_gate_md[commit-compile-gate]
    knowledge_commit_intent_preflight_md[commit-intent-preflight]
    knowledge_commit_workflow_orchestration_md[commit-workflow-orchestration]
    knowledge_companion_context_ownership_md[companion-context-ownership]
    knowledge_workflow_resilience_md[workflow-resilience]
    artifact_commit_preflight_md[.dev/commit-preflight.md]
    artifact_file_sizes_json[.dev/file-sizes.json]

    skill_commit_preflight --> Phase0
    skill_commit_preflight --> Phase1
    skill_commit_preflight --> Phase2
    skill_commit_preflight -.-> skill_commit_execute
    skill_commit_preflight --> agent_commit_analyzer
    skill_commit_preflight --> agent_commit_group_drafter
    skill_commit_preflight --> knowledge_artifact_contracts_md
    skill_commit_preflight --> knowledge_commit_compile_gate_md
    skill_commit_preflight --> knowledge_commit_intent_preflight_md
    skill_commit_preflight --> knowledge_commit_workflow_orchestration_md
    skill_commit_preflight --> knowledge_companion_context_ownership_md
    skill_commit_preflight --> knowledge_workflow_resilience_md
    skill_commit_preflight --> artifact_commit_preflight_md
    skill_commit_preflight --> artifact_file_sizes_json

    class skill_commit_preflight skillNode
    class Phase0 phaseNode
    class Phase1 phaseNode
    class Phase2 phaseNode
    class skill_commit_execute skillNode
    class agent_commit_analyzer agentNode
    class agent_commit_group_drafter agentNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_commit_compile_gate_md knowledgeNode
    class knowledge_commit_intent_preflight_md knowledgeNode
    class knowledge_commit_workflow_orchestration_md knowledgeNode
    class knowledge_companion_context_ownership_md knowledgeNode
    class knowledge_workflow_resilience_md knowledgeNode
    class artifact_commit_preflight_md artifactNode
    class artifact_file_sizes_json artifactNode
```

Agents spawned: `al-dev-shared:commit-analyzer`, `al-dev-shared:commit-group-drafter`
<!-- END GENERATED: skill-drilldown-commit-preflight -->

### /explore

<!-- BEGIN GENERATED: skill-drilldown-explore -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_explore[explore]
    skill_plan[plan]
    agent_explore[explore]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_bash_safe_patterns_md[bash-safe-patterns]
    knowledge_companion_context_ownership_md[companion-context-ownership]
    knowledge_explore_subagent_pattern_md[explore-subagent-pattern]
    artifact_2026_05_19_explore_findings_md[.dev/2026-05-19-explore-findings.md]
    artifact_project_context_md[.dev/project-context.md]

    skill_explore -.-> skill_plan
    skill_explore --> agent_explore
    skill_explore --> knowledge_artifact_contracts_md
    skill_explore --> knowledge_bash_safe_patterns_md
    skill_explore --> knowledge_companion_context_ownership_md
    skill_explore --> knowledge_explore_subagent_pattern_md
    skill_explore --> artifact_2026_05_19_explore_findings_md
    skill_explore --> artifact_project_context_md

    class skill_explore skillNode
    class skill_plan skillNode
    class agent_explore agentNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_bash_safe_patterns_md knowledgeNode
    class knowledge_companion_context_ownership_md knowledgeNode
    class knowledge_explore_subagent_pattern_md knowledgeNode
    class artifact_2026_05_19_explore_findings_md artifactNode
    class artifact_project_context_md artifactNode
```

Agents spawned: `al-dev-shared:explore`
<!-- END GENERATED: skill-drilldown-explore -->

### /interview

Phases: 1, 2, 3, 4.

<!-- BEGIN GENERATED: skill-drilldown-interview -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_interview[interview]
    Phase1["Phase 1"]
    Phase2["Phase 2"]
    Phase3["Phase 3"]
    Phase4["Phase 4"]
    skill_plan[plan]
    agent_interview[interview]
    knowledge_artifact_contracts_md[artifact-contracts]
    artifact_session_log_md[.dev/session-log.md]

    skill_interview --> Phase1
    skill_interview --> Phase2
    skill_interview --> Phase3
    skill_interview --> Phase4
    skill_interview -.-> skill_plan
    skill_interview --> agent_interview
    skill_interview --> knowledge_artifact_contracts_md
    skill_interview --> artifact_session_log_md

    class skill_interview skillNode
    class Phase1 phaseNode
    class Phase2 phaseNode
    class Phase3 phaseNode
    class Phase4 phaseNode
    class skill_plan skillNode
    class agent_interview agentNode
    class knowledge_artifact_contracts_md knowledgeNode
    class artifact_session_log_md artifactNode
```

Agents spawned: `al-dev-shared:interview`
<!-- END GENERATED: skill-drilldown-interview -->

### /al-dev-lint

<!-- BEGIN GENERATED: skill-drilldown-lint -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_lint[lint]
    agent_diagnostics_resolver[diagnostics-resolver]
    knowledge_al_linting_rules_md[al-linting-rules]
    knowledge_artifact_contracts_md[artifact-contracts]
    knowledge_compile_lint_procedure_md[compile-lint-procedure]
    knowledge_intent_preflight_md[intent-preflight]
    artifact_compile_errors_log[.dev/compile-errors.log]

    skill_lint --> agent_diagnostics_resolver
    skill_lint --> knowledge_al_linting_rules_md
    skill_lint --> knowledge_artifact_contracts_md
    skill_lint --> knowledge_compile_lint_procedure_md
    skill_lint --> knowledge_intent_preflight_md
    skill_lint --> artifact_compile_errors_log

    class skill_lint skillNode
    class agent_diagnostics_resolver agentNode
    class knowledge_al_linting_rules_md knowledgeNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_compile_lint_procedure_md knowledgeNode
    class knowledge_intent_preflight_md knowledgeNode
    class artifact_compile_errors_log artifactNode
```

Agents spawned: `al-dev-shared:diagnostics-resolver`
<!-- END GENERATED: skill-drilldown-lint -->

### /al-dev-document

<!-- BEGIN GENERATED: skill-drilldown-document -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_document[document]
    agent_docs_writer[docs-writer]
    artifact_format_sweep_progress_md[.dev/format-sweep-progress.md]

    skill_document --> agent_docs_writer
    skill_document --> artifact_format_sweep_progress_md

    class skill_document skillNode
    class agent_docs_writer agentNode
    class artifact_format_sweep_progress_md artifactNode
```

Agents spawned: `al-dev-shared:docs-writer`
<!-- END GENERATED: skill-drilldown-document -->

### /al-dev-release-notes

Phases: 0–3.

<!-- BEGIN GENERATED: skill-drilldown-release-notes -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_release_notes[release-notes]
    Phase1["Phase 1"]
    Phase1_5["Phase 1.5"]
    Phase2["Phase 2"]
    Phase3["Phase 3"]
    agent_release_notes_writer[release-notes-writer]
    artifact_YYYY_MM_DD_plugin_release_notes_md[.dev/YYYY-MM-DD-plugin-release-notes.md]
    artifact_project_context_md[.dev/project-context.md]

    skill_release_notes --> Phase1
    skill_release_notes --> Phase1_5
    skill_release_notes --> Phase2
    skill_release_notes --> Phase3
    skill_release_notes --> agent_release_notes_writer
    skill_release_notes --> artifact_YYYY_MM_DD_plugin_release_notes_md
    skill_release_notes --> artifact_project_context_md

    class skill_release_notes skillNode
    class Phase1 phaseNode
    class Phase1_5 phaseNode
    class Phase2 phaseNode
    class Phase3 phaseNode
    class agent_release_notes_writer agentNode
    class artifact_YYYY_MM_DD_plugin_release_notes_md artifactNode
    class artifact_project_context_md artifactNode
```

Agents spawned: `al-dev-shared:release-notes-writer`
<!-- END GENERATED: skill-drilldown-release-notes -->

### /al-dev-perf

<!-- BEGIN GENERATED: skill-drilldown-perf -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_perf[perf]
    agent_explore[explore]
    knowledge_explore_subagent_pattern_md[explore-subagent-pattern]
    knowledge_perf_anti_patterns_prompt_md[perf-anti-patterns-prompt]
    knowledge_perf_report_template_md[perf-report-template]
    artifact_project_context_md[.dev/project-context.md]

    skill_perf --> agent_explore
    skill_perf --> knowledge_explore_subagent_pattern_md
    skill_perf --> knowledge_perf_anti_patterns_prompt_md
    skill_perf --> knowledge_perf_report_template_md
    skill_perf --> artifact_project_context_md

    class skill_perf skillNode
    class agent_explore agentNode
    class knowledge_explore_subagent_pattern_md knowledgeNode
    class knowledge_perf_anti_patterns_prompt_md knowledgeNode
    class knowledge_perf_report_template_md knowledgeNode
    class artifact_project_context_md artifactNode
```

Agents spawned: `al-dev-shared:explore`
<!-- END GENERATED: skill-drilldown-perf -->

### /al-dev-handoff

<!-- BEGIN GENERATED: skill-drilldown-handoff -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_handoff[handoff]
    knowledge_artifact_contracts_md[artifact-contracts]
    artifact_explore_findings_md[.dev/explore-findings.md]
    artifact_project_context_md[.dev/project-context.md]
    artifact_source_explore_findings_md[.dev/source-explore-findings.md]
    artifact_source_project_context_md[.dev/source-project-context.md]
    artifact_source_release_notes_md[.dev/source-release-notes.md]
    artifact_source_requirements_md[.dev/source-requirements.md]
    artifact_source_solution_plan_md[.dev/source-solution-plan.md]
    artifact_source_ticket_context_md[.dev/source-ticket-context.md]

    skill_handoff --> knowledge_artifact_contracts_md
    skill_handoff --> artifact_explore_findings_md
    skill_handoff --> artifact_project_context_md
    skill_handoff --> artifact_source_explore_findings_md
    skill_handoff --> artifact_source_project_context_md
    skill_handoff --> artifact_source_release_notes_md
    skill_handoff --> artifact_source_requirements_md
    skill_handoff --> artifact_source_solution_plan_md
    skill_handoff --> artifact_source_ticket_context_md

    class skill_handoff skillNode
    class knowledge_artifact_contracts_md knowledgeNode
    class artifact_explore_findings_md artifactNode
    class artifact_project_context_md artifactNode
    class artifact_source_explore_findings_md artifactNode
    class artifact_source_project_context_md artifactNode
    class artifact_source_release_notes_md artifactNode
    class artifact_source_requirements_md artifactNode
    class artifact_source_solution_plan_md artifactNode
    class artifact_source_ticket_context_md artifactNode
```
<!-- END GENERATED: skill-drilldown-handoff -->

### /al-dev-help

No agents spawned; no `.dev/` output. The skill reads available context files and presents contextual guidance inline.

<!-- BEGIN GENERATED: skill-drilldown-help -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold
    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold

    skill_help[help]
    skill_develop_orchestrate[develop-orchestrate]
    skill_plan[plan]
    knowledge_workflow_routing_md[workflow-routing]
    artifact_2026_05_19_develop_code_review_md[.dev/2026-05-19-develop-code-review.md]
    artifact_2026_05_19_interview_requirements_md[.dev/2026-05-19-interview-requirements.md]
    artifact_2026_05_19_plan_solution_plan_md[.dev/2026-05-19-plan-solution-plan.md]
    artifact_project_context_md[.dev/project-context.md]

    skill_help -.-> skill_develop_orchestrate
    skill_help -.-> skill_plan
    skill_help --> knowledge_workflow_routing_md
    skill_help --> artifact_2026_05_19_develop_code_review_md
    skill_help --> artifact_2026_05_19_interview_requirements_md
    skill_help --> artifact_2026_05_19_plan_solution_plan_md
    skill_help --> artifact_project_context_md

    class skill_help skillNode
    class skill_develop_orchestrate skillNode
    class skill_plan skillNode
    class knowledge_workflow_routing_md knowledgeNode
    class artifact_2026_05_19_develop_code_review_md artifactNode
    class artifact_2026_05_19_interview_requirements_md artifactNode
    class artifact_2026_05_19_plan_solution_plan_md artifactNode
    class artifact_project_context_md artifactNode
```
<!-- END GENERATED: skill-drilldown-help -->

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
    agent_corruption_recover[corruption-recover]
    artifact_commit_integrity_log[.dev/commit-integrity.log]
    artifact_compile_errors_log[.dev/compile-errors.log]
    artifact_learnings_md[.dev/learnings.md]

    skill_commit_recover --> agent_corruption_recover
    skill_commit_recover --> artifact_commit_integrity_log
    skill_commit_recover --> artifact_compile_errors_log
    skill_commit_recover --> artifact_learnings_md

    class skill_commit_recover skillNode
    class agent_corruption_recover agentNode
    class artifact_commit_integrity_log artifactNode
    class artifact_compile_errors_log artifactNode
    class artifact_learnings_md artifactNode
```

Agents spawned: `al-dev-shared:corruption-recover`
<!-- END GENERATED: skill-drilldown-commit-recover -->

---

## Observations

> **Findings live in the health dossier, not in this map.** This map is
> documentation only — it describes the current skill structure. To find
> improvement suggestions (Atomise, Absorb, Connect, Merge, Promote, Move,
> Extend), run `/audit-plugin-health` and read the ranked dossier in
> `docs/health/`, then `/al-dev-map-suggestions-verify` to turn accepted
> findings into a plan.
>
> History: in-map suggestions through 2026-05-27 were retired when findings
> converged on the health dossier (2026-06-02).
>
