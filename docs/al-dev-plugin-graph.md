# Plugin Dependency Graph

> Generated sections refreshed by `scripts/generate-map-doc-sections.py` on 2026-06-01.
> Re-run the script to refresh bounded generated blocks. Do not hand-edit inside markers.

## Dependency graph

<!-- BEGIN GENERATED: plugin-dependency-mermaid -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold

    subgraph Skills[Skills]
        skill_al_dev_commit[al-dev-commit]
        skill_al_dev_consolidate[al-dev-consolidate]
        skill_al_dev_develop[al-dev-develop]
        skill_al_dev_diagram_generator[al-dev-diagram-generator]
        skill_al_dev_document[al-dev-document]
        skill_al_dev_explore[al-dev-explore]
        skill_al_dev_fix[al-dev-fix]
        skill_al_dev_handoff[al-dev-handoff]
        skill_al_dev_help[al-dev-help]
        skill_al_dev_interview[al-dev-interview]
        skill_al_dev_investigate[al-dev-investigate]
        skill_al_dev_lint[al-dev-lint]
        skill_al_dev_map_suggestions_verify[al-dev-map-suggestions-verify]
        skill_al_dev_perf[al-dev-perf]
        skill_al_dev_plan[al-dev-plan]
        skill_al_dev_plan_preflight[al-dev-plan-preflight]
        skill_al_dev_plan_swarm_validate[al-dev-plan-swarm-validate]
        skill_al_dev_release_notes[al-dev-release-notes]
        skill_al_dev_review_develop[al-dev-review-develop]
        skill_al_dev_support_reply[al-dev-support-reply]
        skill_al_dev_ticket[al-dev-ticket]
        skill_commit_recover[commit-recover]
        skill_plugin_health_audit[plugin-health-audit]
        skill_verify_commits[verify-commits]
    end
    subgraph Agents[Agents]
        agent_al_dev_code_review[al-dev-code-review]
        agent_al_dev_commit_agent_analysis[al-dev-commit-agent-analysis]
        agent_al_dev_commit_agent_execute[al-dev-commit-agent-execute]
        agent_al_dev_commit_hook_fixer[al-dev-commit-hook-fixer]
        agent_al_dev_commit_lint_fixer[al-dev-commit-lint-fixer]
        agent_al_dev_commit_message_drafter[al-dev-commit-message-drafter]
        agent_al_dev_commit_ooxml_validator[al-dev-commit-ooxml-validator]
        agent_al_dev_commit_recover_fixer[al-dev-commit-recover-fixer]
        agent_al_dev_developer_tdd[al-dev-developer-tdd]
        agent_al_dev_developer_traditional[al-dev-developer-traditional]
        agent_al_dev_diagnostics_fixer[al-dev-diagnostics-fixer]
        agent_al_dev_docs_writer[al-dev-docs-writer]
        agent_al_dev_expert_reviewer[al-dev-expert-reviewer]
        agent_al_dev_explore[al-dev-explore]
        agent_al_dev_interview[al-dev-interview]
        agent_al_dev_performance_reviewer[al-dev-performance-reviewer]
        agent_al_dev_release_notes_writer[al-dev-release-notes-writer]
        agent_al_dev_script_engineer[al-dev-script-engineer]
        agent_al_dev_security_reviewer[al-dev-security-reviewer]
        agent_al_dev_solution_architect[al-dev-solution-architect]
        agent_al_dev_support_reply_drafter[al-dev-support-reply-drafter]
        agent_al_dev_support_researcher[al-dev-support-researcher]
        agent_al_dev_ticket_agent[al-dev-ticket-agent]
    end
    subgraph Knowledge[Knowledge Files]
        knowledge_al_dev_develop_spawn_prompt_md[al-dev-develop-spawn-prompt]
        knowledge_al_dev_fix_examples_md[al-dev-fix-examples]
        knowledge_al_dev_plan_phase_routing_md[al-dev-plan-phase-routing]
        knowledge_al_developer_patterns_md[al-developer-patterns]
        knowledge_al_linting_rules_md[al-linting-rules]
        knowledge_al_symbol_pre_flight_md[al-symbol-pre-flight]
        knowledge_architect_invocation_patterns_md[architect-invocation-patterns]
        knowledge_artifact_contracts_md[artifact-contracts]
        knowledge_code_review_patterns_md[code-review-patterns]
        knowledge_compile_lint_procedure_md[compile-lint-procedure]
        knowledge_compile_output_safeguard_md[compile-output-safeguard]
        knowledge_consolidate_extraction_patterns_md[consolidate-extraction-patterns]
        knowledge_developer_invocation_patterns_md[developer-invocation-patterns]
        knowledge_documentation_rtm_guide_md[documentation-rtm-guide]
        knowledge_explore_subagent_pattern_md[explore-subagent-pattern]
        knowledge_intent_preflight_md[intent-preflight]
        knowledge_interview_question_bank_md[interview-question-bank]
        knowledge_map_change_rubber_duck_checks_md[map-change-rubber-duck-checks]
        knowledge_perf_anti_patterns_prompt_md[perf-anti-patterns-prompt]
        knowledge_performance_review_examples_md[performance-review-examples]
        knowledge_release_notes_template_md[release-notes-template]
        knowledge_scope_expansion_gate_md[scope-expansion-gate]
        knowledge_script_engineer_conventions_md[script-engineer-conventions]
        knowledge_security_review_examples_md[security-review-examples]
        knowledge_solution_plan_template_md[solution-plan-template]
        knowledge_tdd_workflow_md[tdd-workflow]
        knowledge_ticket_agent_invocation_pattern_md[ticket-agent-invocation-pattern]
        knowledge_workflow_resilience_md[workflow-resilience]
    end
    subgraph Artifacts[Artifacts]
        artifact_2026_05_19_al_dev_develop_code_review_md[.dev/2026-05-19-al-dev-develop-code-review.md]
        artifact_2026_05_19_al_dev_explore_findings_md[.dev/2026-05-19-al-dev-explore-findings.md]
        artifact_2026_05_19_al_dev_interview_requirements_md[.dev/2026-05-19-al-dev-interview-requirements.md]
        artifact_2026_05_19_al_dev_plan_solution_plan_md[.dev/2026-05-19-al-dev-plan-solution-plan.md]
        artifact_2026_06_01_al_dev_ticket_ticket_context_md[.dev/2026-06-01-al-dev-ticket-ticket-context.md]
        artifact_YYYY_MM_DD_al_dev_investigate_findings_md[.dev/YYYY-MM-DD-al-dev-investigate-findings.md]
        artifact_YYYY_MM_DD_al_dev_plan_plan_md[.dev/YYYY-MM-DD-al-dev-plan-plan.md]
        artifact_commit_integrity_log[.dev/commit-integrity.log]
        artifact_commits_json[.dev/commits.json]
        artifact_compile_errors_log[.dev/compile-errors.log]
        artifact_explore_findings_md[.dev/explore-findings.md]
        artifact_file_sizes_json[.dev/file-sizes.json]
        artifact_findings_file_md[.dev/findings-file.md]
        artifact_hook_failures_json[.dev/hook-failures.json]
        artifact_investigate_errors_log[.dev/investigate-errors.log]
        artifact_learnings_md[.dev/learnings.md]
        artifact_plan_critique_YYYYMMDD_md[.dev/plan-critique-YYYYMMDD.md]
        artifact_plugin_health_team_checkpoint_json[.dev/plugin-health-team-checkpoint.json]
        artifact_preflight_context_md[.dev/preflight-context.md]
        artifact_progress_md[.dev/progress.md]
        artifact_project_context_md[.dev/project-context.md]
        artifact_source_explore_findings_md[.dev/source-explore-findings.md]
        artifact_source_project_context_md[.dev/source-project-context.md]
        artifact_source_requirements_md[.dev/source-requirements.md]
        artifact_source_solution_plan_md[.dev/source-solution-plan.md]
        artifact_source_ticket_context_md[.dev/source-ticket-context.md]
        artifact_test_plan_md[.dev/test-plan.md]
        artifact_ticket_context_md[.dev/ticket-context.md]
        artifact_ticket_reply_md[.dev/ticket-reply.md]
    end

    skill_al_dev_develop --> skill_al_dev_review_develop
    skill_al_dev_fix --> skill_al_dev_develop
    skill_al_dev_fix --> skill_al_dev_plan
    skill_al_dev_help --> skill_al_dev_develop
    skill_al_dev_help --> skill_al_dev_plan
    skill_al_dev_investigate --> skill_al_dev_handoff
    skill_al_dev_investigate --> skill_al_dev_plan
    skill_al_dev_plan --> skill_al_dev_plan_preflight
    skill_al_dev_review_develop --> skill_al_dev_commit
    skill_al_dev_review_develop --> skill_al_dev_develop
    skill_al_dev_support_reply --> skill_al_dev_ticket
    skill_al_dev_ticket --> skill_al_dev_interview
    skill_al_dev_ticket --> skill_al_dev_plan
    skill_al_dev_ticket --> skill_al_dev_support_reply
    skill_al_dev_commit --> agent_al_dev_commit_agent_analysis
    skill_al_dev_commit --> agent_al_dev_commit_agent_execute
    skill_al_dev_commit --> agent_al_dev_commit_hook_fixer
    skill_al_dev_commit --> agent_al_dev_commit_lint_fixer
    skill_al_dev_commit --> agent_al_dev_commit_message_drafter
    skill_al_dev_commit --> agent_al_dev_commit_ooxml_validator
    skill_al_dev_develop --> agent_al_dev_developer_tdd
    skill_al_dev_develop --> agent_al_dev_developer_traditional
    skill_al_dev_fix --> agent_al_dev_developer_tdd
    skill_al_dev_fix --> agent_al_dev_developer_traditional
    skill_al_dev_fix --> agent_al_dev_solution_architect
    skill_al_dev_interview --> agent_al_dev_interview
    skill_al_dev_lint --> agent_al_dev_diagnostics_fixer
    skill_al_dev_plan --> agent_al_dev_solution_architect
    skill_al_dev_release_notes --> agent_al_dev_release_notes_writer
    skill_al_dev_review_develop --> agent_al_dev_developer_traditional
    skill_al_dev_review_develop --> agent_al_dev_expert_reviewer
    skill_al_dev_review_develop --> agent_al_dev_performance_reviewer
    skill_al_dev_review_develop --> agent_al_dev_security_reviewer
    skill_al_dev_support_reply --> agent_al_dev_support_reply_drafter
    skill_al_dev_support_reply --> agent_al_dev_support_researcher
    skill_al_dev_ticket --> agent_al_dev_ticket_agent
    skill_commit_recover --> agent_al_dev_commit_recover_fixer
    skill_al_dev_commit --> knowledge_artifact_contracts_md
    skill_al_dev_commit --> knowledge_compile_lint_procedure_md
    skill_al_dev_commit --> knowledge_intent_preflight_md
    skill_al_dev_consolidate --> knowledge_consolidate_extraction_patterns_md
    skill_al_dev_develop --> knowledge_al_dev_develop_spawn_prompt_md
    skill_al_dev_develop --> knowledge_artifact_contracts_md
    skill_al_dev_develop --> knowledge_developer_invocation_patterns_md
    skill_al_dev_develop --> knowledge_intent_preflight_md
    skill_al_dev_develop --> knowledge_scope_expansion_gate_md
    skill_al_dev_develop --> knowledge_workflow_resilience_md
    skill_al_dev_explore --> knowledge_explore_subagent_pattern_md
    skill_al_dev_fix --> knowledge_al_dev_fix_examples_md
    skill_al_dev_fix --> knowledge_artifact_contracts_md
    skill_al_dev_fix --> knowledge_compile_lint_procedure_md
    skill_al_dev_fix --> knowledge_developer_invocation_patterns_md
    skill_al_dev_fix --> knowledge_intent_preflight_md
    skill_al_dev_investigate --> knowledge_explore_subagent_pattern_md
    skill_al_dev_lint --> knowledge_al_linting_rules_md
    skill_al_dev_lint --> knowledge_artifact_contracts_md
    skill_al_dev_lint --> knowledge_intent_preflight_md
    skill_al_dev_map_suggestions_verify --> knowledge_map_change_rubber_duck_checks_md
    skill_al_dev_perf --> knowledge_explore_subagent_pattern_md
    skill_al_dev_perf --> knowledge_perf_anti_patterns_prompt_md
    skill_al_dev_plan --> knowledge_architect_invocation_patterns_md
    skill_al_dev_plan --> knowledge_artifact_contracts_md
    skill_al_dev_plan --> knowledge_intent_preflight_md
    skill_al_dev_plan --> knowledge_solution_plan_template_md
    skill_al_dev_plan --> knowledge_workflow_resilience_md
    skill_al_dev_plan_preflight --> knowledge_al_dev_plan_phase_routing_md
    skill_al_dev_plan_preflight --> knowledge_intent_preflight_md
    skill_al_dev_plan_preflight --> knowledge_workflow_resilience_md
    skill_al_dev_review_develop --> knowledge_artifact_contracts_md
    skill_al_dev_review_develop --> knowledge_developer_invocation_patterns_md
    skill_al_dev_ticket --> knowledge_ticket_agent_invocation_pattern_md
    agent_al_dev_developer_tdd --> knowledge_al_developer_patterns_md
    agent_al_dev_developer_tdd --> knowledge_al_symbol_pre_flight_md
    agent_al_dev_developer_tdd --> knowledge_compile_output_safeguard_md
    agent_al_dev_developer_tdd --> knowledge_developer_invocation_patterns_md
    agent_al_dev_developer_tdd --> knowledge_tdd_workflow_md
    agent_al_dev_developer_traditional --> knowledge_al_developer_patterns_md
    agent_al_dev_developer_traditional --> knowledge_al_symbol_pre_flight_md
    agent_al_dev_developer_traditional --> knowledge_compile_output_safeguard_md
    agent_al_dev_developer_traditional --> knowledge_developer_invocation_patterns_md
    agent_al_dev_docs_writer --> knowledge_documentation_rtm_guide_md
    agent_al_dev_expert_reviewer --> knowledge_code_review_patterns_md
    agent_al_dev_interview --> knowledge_interview_question_bank_md
    agent_al_dev_performance_reviewer --> knowledge_perf_anti_patterns_prompt_md
    agent_al_dev_performance_reviewer --> knowledge_performance_review_examples_md
    agent_al_dev_release_notes_writer --> knowledge_release_notes_template_md
    agent_al_dev_script_engineer --> knowledge_script_engineer_conventions_md
    agent_al_dev_security_reviewer --> knowledge_security_review_examples_md
    agent_al_dev_solution_architect --> knowledge_al_developer_patterns_md
    agent_al_dev_solution_architect --> knowledge_solution_plan_template_md
    agent_al_dev_ticket_agent --> knowledge_ticket_agent_invocation_pattern_md
    skill_al_dev_commit --> artifact_commits_json
    skill_al_dev_commit --> artifact_compile_errors_log
    skill_al_dev_commit --> artifact_file_sizes_json
    skill_al_dev_commit --> artifact_hook_failures_json
    skill_al_dev_develop --> artifact_progress_md
    skill_al_dev_develop --> artifact_project_context_md
    skill_al_dev_explore --> artifact_2026_05_19_al_dev_explore_findings_md
    skill_al_dev_explore --> artifact_project_context_md
    skill_al_dev_fix --> artifact_test_plan_md
    skill_al_dev_handoff --> artifact_explore_findings_md
    skill_al_dev_handoff --> artifact_project_context_md
    skill_al_dev_handoff --> artifact_source_explore_findings_md
    skill_al_dev_handoff --> artifact_source_project_context_md
    skill_al_dev_handoff --> artifact_source_requirements_md
    skill_al_dev_handoff --> artifact_source_solution_plan_md
    skill_al_dev_handoff --> artifact_source_ticket_context_md
    skill_al_dev_help --> artifact_2026_05_19_al_dev_develop_code_review_md
    skill_al_dev_help --> artifact_2026_05_19_al_dev_interview_requirements_md
    skill_al_dev_help --> artifact_2026_05_19_al_dev_plan_solution_plan_md
    skill_al_dev_help --> artifact_project_context_md
    skill_al_dev_investigate --> artifact_YYYY_MM_DD_al_dev_investigate_findings_md
    skill_al_dev_investigate --> artifact_investigate_errors_log
    skill_al_dev_investigate --> artifact_project_context_md
    skill_al_dev_lint --> artifact_compile_errors_log
    skill_al_dev_map_suggestions_verify --> artifact_YYYY_MM_DD_al_dev_plan_plan_md
    skill_al_dev_map_suggestions_verify --> artifact_progress_md
    skill_al_dev_perf --> artifact_project_context_md
    skill_al_dev_plan --> artifact_preflight_context_md
    skill_al_dev_plan --> artifact_progress_md
    skill_al_dev_plan_preflight --> artifact_findings_file_md
    skill_al_dev_plan_preflight --> artifact_preflight_context_md
    skill_al_dev_plan_preflight --> artifact_progress_md
    skill_al_dev_plan_preflight --> artifact_project_context_md
    skill_al_dev_plan_swarm_validate --> artifact_plan_critique_YYYYMMDD_md
    skill_al_dev_release_notes --> artifact_project_context_md
    skill_al_dev_review_develop --> artifact_compile_errors_log
    skill_al_dev_review_develop --> artifact_progress_md
    skill_al_dev_support_reply --> artifact_2026_06_01_al_dev_ticket_ticket_context_md
    skill_al_dev_support_reply --> artifact_ticket_reply_md
    skill_al_dev_ticket --> artifact_ticket_context_md
    skill_al_dev_ticket --> artifact_ticket_reply_md
    skill_commit_recover --> artifact_commit_integrity_log
    skill_commit_recover --> artifact_learnings_md
    skill_plugin_health_audit --> artifact_plugin_health_team_checkpoint_json

    class skill_al_dev_commit skillNode
    class skill_al_dev_consolidate skillNode
    class skill_al_dev_develop skillNode
    class skill_al_dev_diagram_generator skillNode
    class skill_al_dev_document skillNode
    class skill_al_dev_explore skillNode
    class skill_al_dev_fix skillNode
    class skill_al_dev_handoff skillNode
    class skill_al_dev_help skillNode
    class skill_al_dev_interview skillNode
    class skill_al_dev_investigate skillNode
    class skill_al_dev_lint skillNode
    class skill_al_dev_map_suggestions_verify skillNode
    class skill_al_dev_perf skillNode
    class skill_al_dev_plan skillNode
    class skill_al_dev_plan_preflight skillNode
    class skill_al_dev_plan_swarm_validate skillNode
    class skill_al_dev_release_notes skillNode
    class skill_al_dev_review_develop skillNode
    class skill_al_dev_support_reply skillNode
    class skill_al_dev_ticket skillNode
    class skill_commit_recover skillNode
    class skill_plugin_health_audit skillNode
    class skill_verify_commits skillNode
    class agent_al_dev_code_review agentNode
    class agent_al_dev_commit_agent_analysis agentNode
    class agent_al_dev_commit_agent_execute agentNode
    class agent_al_dev_commit_hook_fixer agentNode
    class agent_al_dev_commit_lint_fixer agentNode
    class agent_al_dev_commit_message_drafter agentNode
    class agent_al_dev_commit_ooxml_validator agentNode
    class agent_al_dev_commit_recover_fixer agentNode
    class agent_al_dev_developer_tdd agentNode
    class agent_al_dev_developer_traditional agentNode
    class agent_al_dev_diagnostics_fixer agentNode
    class agent_al_dev_docs_writer agentNode
    class agent_al_dev_expert_reviewer agentNode
    class agent_al_dev_explore agentNode
    class agent_al_dev_interview agentNode
    class agent_al_dev_performance_reviewer agentNode
    class agent_al_dev_release_notes_writer agentNode
    class agent_al_dev_script_engineer agentNode
    class agent_al_dev_security_reviewer agentNode
    class agent_al_dev_solution_architect agentNode
    class agent_al_dev_support_reply_drafter agentNode
    class agent_al_dev_support_researcher agentNode
    class agent_al_dev_ticket_agent agentNode
    class knowledge_al_dev_develop_spawn_prompt_md knowledgeNode
    class knowledge_al_dev_fix_examples_md knowledgeNode
    class knowledge_al_dev_plan_phase_routing_md knowledgeNode
    class knowledge_al_developer_patterns_md knowledgeNode
    class knowledge_al_linting_rules_md knowledgeNode
    class knowledge_al_symbol_pre_flight_md knowledgeNode
    class knowledge_architect_invocation_patterns_md knowledgeNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_code_review_patterns_md knowledgeNode
    class knowledge_compile_lint_procedure_md knowledgeNode
    class knowledge_compile_output_safeguard_md knowledgeNode
    class knowledge_consolidate_extraction_patterns_md knowledgeNode
    class knowledge_developer_invocation_patterns_md knowledgeNode
    class knowledge_documentation_rtm_guide_md knowledgeNode
    class knowledge_explore_subagent_pattern_md knowledgeNode
    class knowledge_intent_preflight_md knowledgeNode
    class knowledge_interview_question_bank_md knowledgeNode
    class knowledge_map_change_rubber_duck_checks_md knowledgeNode
    class knowledge_perf_anti_patterns_prompt_md knowledgeNode
    class knowledge_performance_review_examples_md knowledgeNode
    class knowledge_release_notes_template_md knowledgeNode
    class knowledge_scope_expansion_gate_md knowledgeNode
    class knowledge_script_engineer_conventions_md knowledgeNode
    class knowledge_security_review_examples_md knowledgeNode
    class knowledge_solution_plan_template_md knowledgeNode
    class knowledge_tdd_workflow_md knowledgeNode
    class knowledge_ticket_agent_invocation_pattern_md knowledgeNode
    class knowledge_workflow_resilience_md knowledgeNode
    class artifact_2026_05_19_al_dev_develop_code_review_md artifactNode
    class artifact_2026_05_19_al_dev_explore_findings_md artifactNode
    class artifact_2026_05_19_al_dev_interview_requirements_md artifactNode
    class artifact_2026_05_19_al_dev_plan_solution_plan_md artifactNode
    class artifact_2026_06_01_al_dev_ticket_ticket_context_md artifactNode
    class artifact_YYYY_MM_DD_al_dev_investigate_findings_md artifactNode
    class artifact_YYYY_MM_DD_al_dev_plan_plan_md artifactNode
    class artifact_commit_integrity_log artifactNode
    class artifact_commits_json artifactNode
    class artifact_compile_errors_log artifactNode
    class artifact_explore_findings_md artifactNode
    class artifact_file_sizes_json artifactNode
    class artifact_findings_file_md artifactNode
    class artifact_hook_failures_json artifactNode
    class artifact_investigate_errors_log artifactNode
    class artifact_learnings_md artifactNode
    class artifact_plan_critique_YYYYMMDD_md artifactNode
    class artifact_plugin_health_team_checkpoint_json artifactNode
    class artifact_preflight_context_md artifactNode
    class artifact_progress_md artifactNode
    class artifact_project_context_md artifactNode
    class artifact_source_explore_findings_md artifactNode
    class artifact_source_project_context_md artifactNode
    class artifact_source_requirements_md artifactNode
    class artifact_source_solution_plan_md artifactNode
    class artifact_source_ticket_context_md artifactNode
    class artifact_test_plan_md artifactNode
    class artifact_ticket_context_md artifactNode
    class artifact_ticket_reply_md artifactNode
```
<!-- END GENERATED: plugin-dependency-mermaid -->

## Workflow-path overlays

<!-- BEGIN GENERATED: plugin-workflow-overlays -->
### Development Spine

```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    skill_al_dev_investigate[al-dev-investigate]
    skill_al_dev_plan[al-dev-plan]
    skill_al_dev_develop[al-dev-develop]
    skill_al_dev_review_develop[al-dev-review-develop]
    skill_al_dev_commit[al-dev-commit]

    skill_al_dev_investigate --> skill_al_dev_plan
    skill_al_dev_plan --> skill_al_dev_develop
    skill_al_dev_develop --> skill_al_dev_review_develop
    skill_al_dev_review_develop --> skill_al_dev_commit

    class skill_al_dev_investigate skillNode
    class skill_al_dev_plan skillNode
    class skill_al_dev_develop skillNode
    class skill_al_dev_review_develop skillNode
    class skill_al_dev_commit skillNode
```

### Ticket Support

```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    skill_al_dev_ticket[al-dev-ticket]
    skill_al_dev_support_reply[al-dev-support-reply]

    skill_al_dev_ticket --> skill_al_dev_support_reply

    class skill_al_dev_ticket skillNode
    class skill_al_dev_support_reply skillNode
```

### Direct Fix

```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    skill_al_dev_fix[al-dev-fix]
    skill_al_dev_commit[al-dev-commit]

    skill_al_dev_fix --> skill_al_dev_commit

    class skill_al_dev_fix skillNode
    class skill_al_dev_commit skillNode
```
<!-- END GENERATED: plugin-workflow-overlays -->

## Health callouts

<!-- BEGIN GENERATED: plugin-health-callouts -->
**Orphan agents (spawned by no skill):**

- `al-dev-code-review`
- `al-dev-docs-writer`
- `al-dev-explore`
- `al-dev-script-engineer`

**Dead knowledge (referenced by nothing):**

- `agent-tool-projection-policy.md`
- `anti-patterns.md`
- `code-review-template.md`
- `commit-conventions.md`
- `feedback-resolution.md`
- `handoff-chain-map.md`
- `harness-concepts.md`
- `lens-invocation-patterns.md`
- `map-suggestion-templates.md`
- `proportional-planning.md`
- `publish-workflow-opportunity.md`
- `quality-checklist.md`
- `review-panel-pattern.md`
- `rubber-duck.md`
- `session-analysis-report-format.md`
- `skill-test-format.md`
- `verification-and-planning.md`
- `workflow-routing.md`

**Off-path skills (not on any configured workflow path):**

- `al-dev-consolidate`
- `al-dev-diagram-generator`
- `al-dev-document`
- `al-dev-explore`
- `al-dev-handoff`
- `al-dev-help`
- `al-dev-interview`
- `al-dev-lint`
- `al-dev-map-suggestions-verify`
- `al-dev-perf`
- `al-dev-plan-preflight`
- `al-dev-plan-swarm-validate`
- `al-dev-release-notes`
- `commit-recover`
- `plugin-health-audit`
- `verify-commits`

**Missing refs (referenced but not on disk):**

- `knowledge: plugin-health-lenses.md`
- `knowledge: remote-trigger-duck-team-dispatch.md`
<!-- END GENERATED: plugin-health-callouts -->
