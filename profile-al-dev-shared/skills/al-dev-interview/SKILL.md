---
name: al-dev-interview
description: Gather requirements through structured interview questions.
argument-hint: "[feature description or file path]"
---

# Interview Skill

Conduct a deep requirements interview for a Business Central
AL development feature.

## Artifact Contract

This skill is governed by `knowledge/artifact-contracts.md`.

Do not claim the work is complete or ready for handoff until the success evidence named in `knowledge/artifact-contracts.md` for this skill has been produced and read in the current run.

## Interview First, Write Last

The entire value of this skill is extracting information only
the user has. Writing requirements before asking questions means
generating assumptions — the output will look complete but will
be wrong in the ways that matter most. Ask first, write after.

## Phase 1: Pre-research Base App Context

Before spawning the interview agent, use the AL Symbols MCP
(`al-mcp-server`) to look up any base app objects mentioned
or implied by the user's feature description in $ARGUMENTS.

- `al_search_objects` — find tables, pages, or codeunits
  related to the feature area (e.g. "Sales Header" if the
  user mentions sales orders)
- `al_get_object_definition` — inspect key fields and
  available events on those objects

Include a brief summary of relevant base objects in the
interview agent's starting prompt so the interviewer asks
informed questions about BC integration points rather than
generic ones.

## Phase 2: Interview (mandatory, do this SECOND)

Spawn a single **al-dev-interview** agent to conduct the interview:

> Interview the user to gather comprehensive requirements
> for: $ARGUMENTS
>
> Base app context pre-researched:
> [paste relevant objects/events found in Phase 1]

The interview agent MUST:

1. Start by asking the user about their business context
   and goals. Do not assume — ask.

2. Ask questions directly in text output. Group 2-4 related
   questions per message. Wait for the user to respond before
   continuing.

3. Work through these categories, asking about each one:
   - Business logic and requirements
   - BC base app integration
   - Data model and state
   - User interface
   - Error handling and validation
   - Integration points
   - Performance and scale
   - Testing strategy
   - Security and compliance
   - Deployment and migration
   - Edge cases and unknowns

4. Expect 20-40+ questions depending on complexity. Do NOT
   rush through categories. Each user answer should inform
   your next questions.

5. **GATE: The interview agent must explicitly state "INTERVIEW COMPLETE" and
   confirm questions were asked in all 11 categories listed above. Upon this
   explicit signal, proceed to Phase 3.**

   **Completion check:** Verify agent output contains `INTERVIEW COMPLETE` and a
   category list. If missing:
   1. Re-dispatch with: "Please end your response with INTERVIEW COMPLETE and list
      the question groups covered."
   2. If still missing after re-dispatch, note the stopping point and proceed to
      plan with partial findings.

## Phase 3: Write Requirements (only after interview)

Only after the interview conversation is complete:

1. Write `.dev/$(date +%Y-%m-%d)-al-dev-interview-notes.md` with raw
   interview notes and key decisions captured during Q&A.

2. Write `.dev/$(date +%Y-%m-%d)-al-dev-interview-requirements.md` as a
   formal requirements
   document using governance tokens:

   ```text
   REQ:REQ-001|FUNCTIONAL|HIGH|DEFINED|[Requirement text]
   ACC:ACC-001|REQ-001|Given [state]|When [action]|Then [outcome]
   RISK:DataIntegrity|[Risk description]|[Mitigation]
   DEP:DEP-001|BCBaseApp|[Dependency description]
   ```

   Include sections: Business Context, Functional Requirements,
   Validation Rules, User Workflows, Data Requirements,
   BC Integration, UI/UX Requirements, Constraints,
   Success Criteria, Out of Scope, Open Questions.

3. Validate the output:

   ```bash
   # AL_DEV_SHARED_PLUGIN_ROOT is set by the harness to the plugin root directory.
   VALIDATOR="$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-interview/validate-requirements.py"
   REQFILE=$(ls -t .dev/*-al-dev-interview-requirements.md 2>/dev/null \
     | head -1)
   [ -f "$VALIDATOR" ] && [ -n "$REQFILE" ] && \
     python3 "$VALIDATOR" "$REQFILE" || \
     echo "Validator not found — skipping"
   ```

## Phase 4: Summary

Present a completion summary:

```text
INTERVIEW COMPLETE

Output: .dev/$(date +%Y-%m-%d)-al-dev-interview-requirements.md
Questions asked: [N]
Key decisions: [N]
Edge cases identified: [N]
Acceptance criteria: [N]

Business goal: [1 sentence]
Core functionality:
- [bullet 1]
- [bullet 2]
- [bullet 3]
BC integration: [tables/events/pages touched]
Key constraints: [notable limitations]
Open questions: [any remaining, or "None"]

Next step: /plan to generate solution design
```
