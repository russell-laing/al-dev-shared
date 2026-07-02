# Plugin Workflow Diagrams

> Generated sections refreshed by `scripts/generate_map_doc_sections.py` on 2026-06-01.
> Re-run the script to refresh bounded generated blocks. Do not hand-edit inside markers.

## Skills → Agents

<!-- BEGIN GENERATED: workflow-skills-agents-mermaid -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold

    subgraph Skills[Skills]
        skill_commit[commit]
        skill_commit_execute[commit-execute]
        skill_commit_preflight[commit-preflight]
        skill_commit_recover[commit-recover]
        skill_develop_orchestrate[develop-orchestrate]
        skill_document[document]
        skill_explore[explore]
        skill_fix[fix]
        skill_generic_preflight[generic-preflight]
        skill_handoff[handoff]
        skill_help[help]
        skill_interview[interview]
        skill_investigate[investigate]
        skill_lint[lint]
        skill_perf[perf]
        skill_plan[plan]
        skill_plan_final_review[plan-final-review]
        skill_plan_with_critics[plan-with-critics]
        skill_release_notes[release-notes]
        skill_research[research]
        skill_review_develop[review-develop]
        skill_support_reply[support-reply]
        skill_ticket[ticket]
    end
    subgraph Agents[Agents]
        agent_al_pattern_reviewer[al-pattern-reviewer]
        agent_commit_analyzer[commit-analyzer]
        agent_commit_executor[commit-executor]
        agent_commit_group_drafter[commit-group-drafter]
        agent_commit_hook_classifier[commit-hook-classifier]
        agent_commit_hook_fixer[commit-hook-fixer]
        agent_commit_lint_fixer[commit-lint-fixer]
        agent_corruption_recover[corruption-recover]
        agent_developer_tdd[developer-tdd]
        agent_developer_traditional[developer-traditional]
        agent_diagnostics_resolver[diagnostics-resolver]
        agent_docs_writer[docs-writer]
        agent_ecosystem_researcher[ecosystem-researcher]
        agent_explore[explore]
        agent_interview[interview]
        agent_performance_reviewer[performance-reviewer]
        agent_release_notes_writer[release-notes-writer]
        agent_repo_researcher[repo-researcher]
        agent_security_reviewer[security-reviewer]
        agent_solution_architect[solution-architect]
        agent_support_reply_drafter[support-reply-drafter]
        agent_support_researcher[support-researcher]
        agent_ticket_context_writer[ticket-context-writer]
    end

    skill_commit --> skill_commit_execute
    skill_commit --> skill_commit_preflight
    skill_commit_execute --> skill_commit
    skill_commit_preflight --> skill_commit_execute
    skill_develop_orchestrate --> skill_review_develop
    skill_explore --> skill_plan
    skill_fix --> skill_develop_orchestrate
    skill_fix --> skill_investigate
    skill_fix --> skill_plan
    skill_help --> skill_develop_orchestrate
    skill_help --> skill_plan
    skill_interview --> skill_plan
    skill_investigate --> skill_fix
    skill_investigate --> skill_handoff
    skill_investigate --> skill_plan
    skill_plan --> skill_generic_preflight
    skill_plan --> skill_plan_final_review
    skill_plan_final_review --> skill_plan
    skill_plan_final_review --> skill_plan_with_critics
    skill_review_develop --> skill_commit
    skill_review_develop --> skill_generic_preflight
    skill_support_reply --> skill_ticket
    skill_ticket --> skill_interview
    skill_ticket --> skill_plan
    skill_commit_execute --> agent_commit_executor
    skill_commit_execute --> agent_commit_hook_classifier
    skill_commit_execute --> agent_commit_hook_fixer
    skill_commit_execute --> agent_commit_lint_fixer
    skill_commit_preflight --> agent_commit_analyzer
    skill_commit_preflight --> agent_commit_group_drafter
    skill_commit_recover --> agent_corruption_recover
    skill_develop_orchestrate --> agent_developer_tdd
    skill_develop_orchestrate --> agent_developer_traditional
    skill_document --> agent_docs_writer
    skill_explore --> agent_explore
    skill_fix --> agent_developer_traditional
    skill_fix --> agent_solution_architect
    skill_interview --> agent_interview
    skill_investigate --> agent_explore
    skill_lint --> agent_diagnostics_resolver
    skill_perf --> agent_explore
    skill_plan --> agent_solution_architect
    skill_release_notes --> agent_release_notes_writer
    skill_research --> agent_ecosystem_researcher
    skill_research --> agent_repo_researcher
    skill_review_develop --> agent_al_pattern_reviewer
    skill_review_develop --> agent_performance_reviewer
    skill_review_develop --> agent_security_reviewer
    skill_support_reply --> agent_support_reply_drafter
    skill_support_reply --> agent_support_researcher
    skill_ticket --> agent_ticket_context_writer

    class skill_commit skillNode
    class skill_commit_execute skillNode
    class skill_commit_preflight skillNode
    class skill_commit_recover skillNode
    class skill_develop_orchestrate skillNode
    class skill_document skillNode
    class skill_explore skillNode
    class skill_fix skillNode
    class skill_generic_preflight skillNode
    class skill_handoff skillNode
    class skill_help skillNode
    class skill_interview skillNode
    class skill_investigate skillNode
    class skill_lint skillNode
    class skill_perf skillNode
    class skill_plan skillNode
    class skill_plan_final_review skillNode
    class skill_plan_with_critics skillNode
    class skill_release_notes skillNode
    class skill_research skillNode
    class skill_review_develop skillNode
    class skill_support_reply skillNode
    class skill_ticket skillNode
    class agent_al_pattern_reviewer agentNode
    class agent_commit_analyzer agentNode
    class agent_commit_executor agentNode
    class agent_commit_group_drafter agentNode
    class agent_commit_hook_classifier agentNode
    class agent_commit_hook_fixer agentNode
    class agent_commit_lint_fixer agentNode
    class agent_corruption_recover agentNode
    class agent_developer_tdd agentNode
    class agent_developer_traditional agentNode
    class agent_diagnostics_resolver agentNode
    class agent_docs_writer agentNode
    class agent_ecosystem_researcher agentNode
    class agent_explore agentNode
    class agent_interview agentNode
    class agent_performance_reviewer agentNode
    class agent_release_notes_writer agentNode
    class agent_repo_researcher agentNode
    class agent_security_reviewer agentNode
    class agent_solution_architect agentNode
    class agent_support_reply_drafter agentNode
    class agent_support_researcher agentNode
    class agent_ticket_context_writer agentNode
```
<!-- END GENERATED: workflow-skills-agents-mermaid -->

## Skills and Agents → Knowledge Files

<!-- BEGIN GENERATED: workflow-knowledge-mermaid -->
```mermaid
flowchart LR
    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold
    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold
    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold

    subgraph Skills[Skills]
        skill_commit_preflight[commit-preflight]
        skill_develop_orchestrate[develop-orchestrate]
        skill_explore[explore]
        skill_fix[fix]
        skill_handoff[handoff]
        skill_help[help]
        skill_interview[interview]
        skill_investigate[investigate]
        skill_lint[lint]
        skill_perf[perf]
        skill_plan[plan]
        skill_plan_with_critics[plan-with-critics]
        skill_research[research]
        skill_review_develop[review-develop]
        skill_ticket[ticket]
    end
    subgraph Agents[Agents]
        agent_al_pattern_reviewer[al-pattern-reviewer]
        agent_commit_analyzer[commit-analyzer]
        agent_commit_hook_classifier[commit-hook-classifier]
        agent_commit_hook_fixer[commit-hook-fixer]
        agent_commit_lint_fixer[commit-lint-fixer]
        agent_developer_tdd[developer-tdd]
        agent_developer_traditional[developer-traditional]
        agent_diagnostics_resolver[diagnostics-resolver]
        agent_docs_writer[docs-writer]
        agent_ecosystem_researcher[ecosystem-researcher]
        agent_explore[explore]
        agent_general_code_reviewer[general-code-reviewer]
        agent_performance_reviewer[performance-reviewer]
        agent_release_notes_writer[release-notes-writer]
        agent_repo_researcher[repo-researcher]
        agent_script_engineer[script-engineer]
        agent_security_reviewer[security-reviewer]
        agent_solution_architect[solution-architect]
        agent_support_reply_drafter[support-reply-drafter]
        agent_ticket_context_writer[ticket-context-writer]
    end
    subgraph Knowledge[Knowledge Files]
        knowledge_agent_tool_projection_policy_md[agent-tool-projection-policy]
        knowledge_al_developer_patterns_md[al-developer-patterns]
        knowledge_al_developer_shared_standards_md[al-developer-shared-standards]
        knowledge_al_linting_rules_md[al-linting-rules]
        knowledge_al_symbol_pre_flight_md[al-symbol-pre-flight]
        knowledge_architect_evaluation_criteria_md[architect-evaluation-criteria]
        knowledge_architect_invocation_patterns_md[architect-invocation-patterns]
        knowledge_artifact_contracts_md[artifact-contracts]
        knowledge_bash_safe_patterns_md[bash-safe-patterns]
        knowledge_code_review_patterns_md[code-review-patterns]
        knowledge_commit_analysis_patterns_md[commit-analysis-patterns]
        knowledge_commit_compile_gate_md[commit-compile-gate]
        knowledge_commit_hook_recovery_patterns_md[commit-hook-recovery-patterns]
        knowledge_commit_intent_preflight_md[commit-intent-preflight]
        knowledge_commit_workflow_orchestration_md[commit-workflow-orchestration]
        knowledge_companion_context_ownership_md[companion-context-ownership]
        knowledge_compile_lint_procedure_md[compile-lint-procedure]
        knowledge_critic_dispatch_template_md[critic-dispatch-template]
        knowledge_develop_orchestrate_signature_decision_tree_md[develop-orchestrate-signature-decision-tree]
        knowledge_develop_spawn_prompt_md[develop-spawn-prompt]
        knowledge_developer_invocation_patterns_md[developer-invocation-patterns]
        knowledge_diagnostics_report_format_md[diagnostics-report-format]
        knowledge_documentation_rtm_guide_md[documentation-rtm-guide]
        knowledge_explore_findings_format_md[explore-findings-format]
        knowledge_explore_subagent_pattern_md[explore-subagent-pattern]
        knowledge_fix_examples_md[fix-examples]
        knowledge_intent_preflight_md[intent-preflight]
        knowledge_investigate_findings_template_md[investigate-findings-template]
        knowledge_perf_anti_patterns_prompt_md[perf-anti-patterns-prompt]
        knowledge_perf_report_template_md[perf-report-template]
        knowledge_performance_review_examples_md[performance-review-examples]
        knowledge_preflight_context_schema_md[preflight-context-schema]
        knowledge_release_notes_template_md[release-notes-template]
        knowledge_research_output_format_md[research-output-format]
        knowledge_research_source_policy_md[research-source-policy]
        knowledge_reviewer_findings_template_md[reviewer-findings-template]
        knowledge_scope_expansion_gate_md[scope-expansion-gate]
        knowledge_script_engineer_conventions_md[script-engineer-conventions]
        knowledge_security_review_examples_md[security-review-examples]
        knowledge_solution_architect_research_patterns_md[solution-architect-research-patterns]
        knowledge_solution_architect_schema_mapping_md[solution-architect-schema-mapping]
        knowledge_solution_plan_template_md[solution-plan-template]
        knowledge_support_reply_output_format_md[support-reply-output-format]
        knowledge_tdd_workflow_md[tdd-workflow]
        knowledge_ticket_agent_invocation_pattern_md[ticket-agent-invocation-pattern]
        knowledge_ticket_context_output_format_md[ticket-context-output-format]
        knowledge_ticket_image_patterns_md[ticket-image-patterns]
        knowledge_verification_and_planning_md[verification-and-planning]
        knowledge_workflow_resilience_md[workflow-resilience]
        knowledge_workflow_routing_md[workflow-routing]
    end

    skill_commit_preflight --> knowledge_artifact_contracts_md
    skill_commit_preflight --> knowledge_commit_compile_gate_md
    skill_commit_preflight --> knowledge_commit_intent_preflight_md
    skill_commit_preflight --> knowledge_commit_workflow_orchestration_md
    skill_commit_preflight --> knowledge_companion_context_ownership_md
    skill_commit_preflight --> knowledge_workflow_resilience_md
    skill_develop_orchestrate --> knowledge_artifact_contracts_md
    skill_develop_orchestrate --> knowledge_companion_context_ownership_md
    skill_develop_orchestrate --> knowledge_develop_orchestrate_signature_decision_tree_md
    skill_develop_orchestrate --> knowledge_develop_spawn_prompt_md
    skill_develop_orchestrate --> knowledge_developer_invocation_patterns_md
    skill_develop_orchestrate --> knowledge_intent_preflight_md
    skill_develop_orchestrate --> knowledge_scope_expansion_gate_md
    skill_develop_orchestrate --> knowledge_workflow_resilience_md
    skill_explore --> knowledge_artifact_contracts_md
    skill_explore --> knowledge_bash_safe_patterns_md
    skill_explore --> knowledge_companion_context_ownership_md
    skill_explore --> knowledge_explore_subagent_pattern_md
    skill_fix --> knowledge_architect_invocation_patterns_md
    skill_fix --> knowledge_artifact_contracts_md
    skill_fix --> knowledge_compile_lint_procedure_md
    skill_fix --> knowledge_developer_invocation_patterns_md
    skill_fix --> knowledge_fix_examples_md
    skill_fix --> knowledge_intent_preflight_md
    skill_fix --> knowledge_scope_expansion_gate_md
    skill_handoff --> knowledge_artifact_contracts_md
    skill_help --> knowledge_workflow_routing_md
    skill_interview --> knowledge_artifact_contracts_md
    skill_investigate --> knowledge_artifact_contracts_md
    skill_investigate --> knowledge_explore_subagent_pattern_md
    skill_investigate --> knowledge_investigate_findings_template_md
    skill_investigate --> knowledge_verification_and_planning_md
    skill_investigate --> knowledge_workflow_resilience_md
    skill_lint --> knowledge_al_linting_rules_md
    skill_lint --> knowledge_artifact_contracts_md
    skill_lint --> knowledge_compile_lint_procedure_md
    skill_lint --> knowledge_intent_preflight_md
    skill_perf --> knowledge_explore_subagent_pattern_md
    skill_perf --> knowledge_perf_anti_patterns_prompt_md
    skill_perf --> knowledge_perf_report_template_md
    skill_plan --> knowledge_architect_evaluation_criteria_md
    skill_plan --> knowledge_architect_invocation_patterns_md
    skill_plan --> knowledge_artifact_contracts_md
    skill_plan --> knowledge_intent_preflight_md
    skill_plan --> knowledge_preflight_context_schema_md
    skill_plan --> knowledge_solution_plan_template_md
    skill_plan --> knowledge_workflow_resilience_md
    skill_plan_with_critics --> knowledge_critic_dispatch_template_md
    skill_research --> knowledge_research_output_format_md
    skill_research --> knowledge_research_source_policy_md
    skill_review_develop --> knowledge_artifact_contracts_md
    skill_review_develop --> knowledge_critic_dispatch_template_md
    skill_ticket --> knowledge_artifact_contracts_md
    skill_ticket --> knowledge_ticket_agent_invocation_pattern_md
    agent_al_pattern_reviewer --> knowledge_code_review_patterns_md
    agent_al_pattern_reviewer --> knowledge_reviewer_findings_template_md
    agent_commit_analyzer --> knowledge_commit_analysis_patterns_md
    agent_commit_hook_classifier --> knowledge_commit_hook_recovery_patterns_md
    agent_commit_hook_fixer --> knowledge_commit_hook_recovery_patterns_md
    agent_commit_lint_fixer --> knowledge_bash_safe_patterns_md
    agent_developer_tdd --> knowledge_al_developer_shared_standards_md
    agent_developer_tdd --> knowledge_al_symbol_pre_flight_md
    agent_developer_tdd --> knowledge_develop_spawn_prompt_md
    agent_developer_tdd --> knowledge_developer_invocation_patterns_md
    agent_developer_tdd --> knowledge_tdd_workflow_md
    agent_developer_traditional --> knowledge_al_developer_shared_standards_md
    agent_developer_traditional --> knowledge_al_symbol_pre_flight_md
    agent_developer_traditional --> knowledge_develop_spawn_prompt_md
    agent_developer_traditional --> knowledge_developer_invocation_patterns_md
    agent_diagnostics_resolver --> knowledge_bash_safe_patterns_md
    agent_diagnostics_resolver --> knowledge_diagnostics_report_format_md
    agent_docs_writer --> knowledge_documentation_rtm_guide_md
    agent_ecosystem_researcher --> knowledge_research_output_format_md
    agent_ecosystem_researcher --> knowledge_research_source_policy_md
    agent_explore --> knowledge_explore_findings_format_md
    agent_general_code_reviewer --> knowledge_reviewer_findings_template_md
    agent_performance_reviewer --> knowledge_perf_anti_patterns_prompt_md
    agent_performance_reviewer --> knowledge_performance_review_examples_md
    agent_performance_reviewer --> knowledge_reviewer_findings_template_md
    agent_release_notes_writer --> knowledge_release_notes_template_md
    agent_repo_researcher --> knowledge_research_output_format_md
    agent_repo_researcher --> knowledge_research_source_policy_md
    agent_script_engineer --> knowledge_script_engineer_conventions_md
    agent_security_reviewer --> knowledge_reviewer_findings_template_md
    agent_security_reviewer --> knowledge_security_review_examples_md
    agent_solution_architect --> knowledge_agent_tool_projection_policy_md
    agent_solution_architect --> knowledge_al_developer_patterns_md
    agent_solution_architect --> knowledge_solution_architect_research_patterns_md
    agent_solution_architect --> knowledge_solution_architect_schema_mapping_md
    agent_solution_architect --> knowledge_solution_plan_template_md
    agent_support_reply_drafter --> knowledge_support_reply_output_format_md
    agent_ticket_context_writer --> knowledge_ticket_agent_invocation_pattern_md
    agent_ticket_context_writer --> knowledge_ticket_context_output_format_md
    agent_ticket_context_writer --> knowledge_ticket_image_patterns_md

    class skill_commit_preflight skillNode
    class skill_develop_orchestrate skillNode
    class skill_explore skillNode
    class skill_fix skillNode
    class skill_handoff skillNode
    class skill_help skillNode
    class skill_interview skillNode
    class skill_investigate skillNode
    class skill_lint skillNode
    class skill_perf skillNode
    class skill_plan skillNode
    class skill_plan_with_critics skillNode
    class skill_research skillNode
    class skill_review_develop skillNode
    class skill_ticket skillNode
    class agent_al_pattern_reviewer agentNode
    class agent_commit_analyzer agentNode
    class agent_commit_hook_classifier agentNode
    class agent_commit_hook_fixer agentNode
    class agent_commit_lint_fixer agentNode
    class agent_developer_tdd agentNode
    class agent_developer_traditional agentNode
    class agent_diagnostics_resolver agentNode
    class agent_docs_writer agentNode
    class agent_ecosystem_researcher agentNode
    class agent_explore agentNode
    class agent_general_code_reviewer agentNode
    class agent_performance_reviewer agentNode
    class agent_release_notes_writer agentNode
    class agent_repo_researcher agentNode
    class agent_script_engineer agentNode
    class agent_security_reviewer agentNode
    class agent_solution_architect agentNode
    class agent_support_reply_drafter agentNode
    class agent_ticket_context_writer agentNode
    class knowledge_agent_tool_projection_policy_md knowledgeNode
    class knowledge_al_developer_patterns_md knowledgeNode
    class knowledge_al_developer_shared_standards_md knowledgeNode
    class knowledge_al_linting_rules_md knowledgeNode
    class knowledge_al_symbol_pre_flight_md knowledgeNode
    class knowledge_architect_evaluation_criteria_md knowledgeNode
    class knowledge_architect_invocation_patterns_md knowledgeNode
    class knowledge_artifact_contracts_md knowledgeNode
    class knowledge_bash_safe_patterns_md knowledgeNode
    class knowledge_code_review_patterns_md knowledgeNode
    class knowledge_commit_analysis_patterns_md knowledgeNode
    class knowledge_commit_compile_gate_md knowledgeNode
    class knowledge_commit_hook_recovery_patterns_md knowledgeNode
    class knowledge_commit_intent_preflight_md knowledgeNode
    class knowledge_commit_workflow_orchestration_md knowledgeNode
    class knowledge_companion_context_ownership_md knowledgeNode
    class knowledge_compile_lint_procedure_md knowledgeNode
    class knowledge_critic_dispatch_template_md knowledgeNode
    class knowledge_develop_orchestrate_signature_decision_tree_md knowledgeNode
    class knowledge_develop_spawn_prompt_md knowledgeNode
    class knowledge_developer_invocation_patterns_md knowledgeNode
    class knowledge_diagnostics_report_format_md knowledgeNode
    class knowledge_documentation_rtm_guide_md knowledgeNode
    class knowledge_explore_findings_format_md knowledgeNode
    class knowledge_explore_subagent_pattern_md knowledgeNode
    class knowledge_fix_examples_md knowledgeNode
    class knowledge_intent_preflight_md knowledgeNode
    class knowledge_investigate_findings_template_md knowledgeNode
    class knowledge_perf_anti_patterns_prompt_md knowledgeNode
    class knowledge_perf_report_template_md knowledgeNode
    class knowledge_performance_review_examples_md knowledgeNode
    class knowledge_preflight_context_schema_md knowledgeNode
    class knowledge_release_notes_template_md knowledgeNode
    class knowledge_research_output_format_md knowledgeNode
    class knowledge_research_source_policy_md knowledgeNode
    class knowledge_reviewer_findings_template_md knowledgeNode
    class knowledge_scope_expansion_gate_md knowledgeNode
    class knowledge_script_engineer_conventions_md knowledgeNode
    class knowledge_security_review_examples_md knowledgeNode
    class knowledge_solution_architect_research_patterns_md knowledgeNode
    class knowledge_solution_architect_schema_mapping_md knowledgeNode
    class knowledge_solution_plan_template_md knowledgeNode
    class knowledge_support_reply_output_format_md knowledgeNode
    class knowledge_tdd_workflow_md knowledgeNode
    class knowledge_ticket_agent_invocation_pattern_md knowledgeNode
    class knowledge_ticket_context_output_format_md knowledgeNode
    class knowledge_ticket_image_patterns_md knowledgeNode
    class knowledge_verification_and_planning_md knowledgeNode
    class knowledge_workflow_resilience_md knowledgeNode
    class knowledge_workflow_routing_md knowledgeNode
```
<!-- END GENERATED: workflow-knowledge-mermaid -->
