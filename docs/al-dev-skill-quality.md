# AL Dev Skill Quality Audit

**Last run:** 2026-05-28
**Skills audited:** 20

## Summary

| Severity | Count |
|----------|-------|
| High     | 16    |
| Medium   | 28    |
| Low      | 21    |

## Findings

### /al-dev-develop

**[High] Prompt Clarity**
Observation: Glossary defines "Scope Expansion Gate" but Phase body doesn't specify whether developer waits in blocking state for user input or continues after presenting changes.
Fix: Add "Stop development (blocking). Present proposed changes in numbered-item format and wait for explicit per-item approval. Do NOT continue writing code until user confirms each item."

**[High] Prompt Clarity**
Observation: Phase 1.5 says "If any required external procedure is NOT VERIFIED, do not spawn developers" — "required" is undefined (referenced in plan vs. in developer's module).
Fix: Clarify: "A procedure is 'required' if it is explicitly referenced in the approved solution plan and the assigned developer task must call it."

**[High] Prompt Clarity**
Observation: Phase 8 references "up to 5 sequential compile-fix-compile cycles" but does not define when the loop stops.
Fix: State: "Stop when: (1) compilation succeeds with zero errors, OR (2) 5 attempts exhausted. If exhausted, escalate to the user with the final compile error log."

**[High] Prompt Clarity**
Observation: The Scope Expansion Gate rule contains an `if X` branch (before editing out-of-scope files) with no `else` clause defining what to do when all edits are in-scope.
Fix: Add: "If no out-of-scope changes are proposed, proceed with the edits."

**[High] Bloat**
Observation: The Scope Expansion Gate is stated twice verbatim — in the skill body and in the developer spawn prompt (lines 335–398), duplicating 60+ lines of gate rules.
Fix: Extract Scope Expansion Gate to `knowledge/` and reference it from both locations.

**[High] Bloat**
Observation: Dead-branch conditions — "Skip this phase if `--autonomous` is not in `$ARGUMENTS`" appear in Phases 1.5 and 4.5, creating always-skipped code paths in normal mode.
Fix: Refactor into a single pre-phase gate that branches to `autonomous_workflow()` vs `standard_workflow()` tracks.

**[Medium] Prompt Clarity**
Observation: Phase 4 says "Escalate to user only for...ambiguity that block progress" — "block progress" is undefined.
Fix: Define: "A blocker is a contradiction that prevents compilation, violates a named constraint, or requires a decision outside the developer's scope."

**[Medium] Prompt Clarity**
Observation: Autonomous-conditional glossary entries appear before the flag is introduced in Phase 1, creating a temporal mismatch.
Fix: Move all autonomous-conditional glossary entries into a single "Optional: Autonomous Mode" section after the main glossary.

**[Medium] Structure**
Observation: `argument-hint: "[--autonomous] [module or scope override]"` present but no dispatch instructions clarify the scope override format for users.
Fix: Expand argument-hint to clarify optional scope override usage or add an examples block in Phase 1.

**[Medium] Bloat**
Observation: Context-loading instructions appear in Phase 1 (lines 87–134), Phase 2 architect prompt (lines 236–252), and Phase 3 synthesis (lines 282–293) — three repetitions.
Fix: Extract to `knowledge/architect-invocation-patterns.md`; reference from each phase dispatch.

---

### /al-dev-commit

**[High] Prompt Clarity**
Observation: Step 4a references "AL-affecting staged set" but does not define what files constitute "AL-affecting" vs "docs-only" staged changes.
Fix: Define: "Run this gate when staged changes include any `.al`, `.app.json`, or `.al.json` files. Skip for pure documentation (`.md`, `.txt`), changelog, or manifest-only edits."

**[High] Bloat**
Observation: 11 top-level steps exceeds the 6-step threshold. Steps 4 and 4a cover overlapping concerns (staged files check + compile verification) with dead-branch complexity.
Fix: Consolidate steps 4/4a into a unified staged-file verification phase; move compile gating into a prerequisite check.

**[Medium] Prompt Clarity**
Observation: Step 5 uses "advisory mode (non-blocking)" without defining what "non-blocking" means operationally.
Fix: State: "Advisory mode: surface warnings but do not stop the commit workflow. Warnings are informational only."

**[Medium] Structure**
Observation: `argument-hint` is empty string but body references optional arguments (staging files, unstaging, committing).
Fix: Add a proper argument-hint or remove optional argument references from the body.

---

### /al-dev-plan

**[High] Prompt Clarity**
Observation: Phase 1 Input Validation Gate says stop for "vague word...with no feature context" but does not define "vague word" or "sufficient feature context."
Fix: State: "Sufficient context requires: (1) a feature name or description, AND (2) at least one functional requirement. Examples: 'Add a credit limit check during posting.'"

**[High] Prompt Clarity**
Observation: Phase 2 lists "Default fallback: table extension / separate table / event-driven" as flat list with no guidance on when to use each as a fallback.
Fix: Clarify: "Use fallback debate angles in order: (1) table extension (conservative); (2) separate table (isolated scope); (3) event-driven (flexible, extensible)."

**[Medium] Prompt Clarity**
Observation: "Architects without all three outputs are excluded from Phase 3 synthesis" — "excluded" not defined operationally.
Fix: Clarify: "If an architect fails all three outputs, their output is not considered in Phase 3 debate. Remark on the incomplete submission when presenting to the user."

**[Medium] Bloat**
Observation: Context-loading instructions appear in Phase 1, Phase 2 architect prompt, and Phase 3 synthesis — three repetitions of identical content.
Fix: Extract to `knowledge/architect-invocation-patterns.md` and reference from each phase dispatch.

**[Low] Structure**
Observation: Several code blocks throughout (Phase 1 markdown blocks, Phase 2 architect prompt blocks) lack language tags.
Fix: Tag all code blocks with `markdown` or `text` as appropriate.

---

### /al-dev-consolidate

**[High] Bloat**
Observation: Phase 2 spans 120+ lines with 5 extraction command groups (A–E) each repeating the same 30-line bash pattern (headings, verdict lines, first-N-lines-per-section).
Fix: Extract common bash patterns to `knowledge/consolidate-extraction-patterns.md` and reference rather than repeating per group.

**[Medium] Prompt Clarity**
Observation: Phase 1, Step 3: the filtering rule "matches, or glob-matches" could be interpreted as substring match or regex match.
Fix: Clarify: "Exact match = basename string is identical character-for-character. Glob uses `*` as wildcard only; do not interpret `?` or character classes."

**[Medium] Prompt Clarity**
Observation: Phase 3 uses "if any source file is newer" without defining "newer."
Fix: State: "Check modification time (`mtime`) using the `-nt` test operator."

**[Low] Structure**
Observation: Phase/step headers mix "Phase" and "Step" nomenclature inconsistently (Phase 1–4, then Steps 1–4 within Phase 1).
Fix: Normalize to either "Phase" or "Step" numbering throughout.

---

### /al-dev-fix

**[High] Prompt Clarity**
Observation: The Decision Tree diagram (lines 278–299) uses arrows and indentation but nodes lack decision labels (e.g., "TRIVIAL?", "NON-TRIVIAL?").
Fix: Add decision labels to the diagram, e.g., "You: Analyze complexity [Is it TRIVIAL or NON-TRIVIAL?]"

**[Medium] Prompt Clarity**
Observation: Step 1 states "TRIVIAL (90% of fixes)" and "NON-TRIVIAL (10% of fixes)" — percentages are stated as facts but are heuristic estimates.
Fix: Remove percentages or reframe: "Most fixes are TRIVIAL; when in doubt, default to NON-TRIVIAL."

**[Medium] Prompt Clarity**
Observation: Step 2: "fix only errors caused by the small change" — ambiguous whether this means errors introduced by the fix or errors now exposed.
Fix: Clarify: "Errors caused by the small change = compile diagnostics referencing lines modified by this fix. Do not fix pre-existing errors in other lines."

**[Medium] Bloat**
Observation: Steps 2 and 3 both contain identical scope-check logic and identical "Ready to test?" summaries; Compilation Verification section repeats scope-correction a third time.
Fix: Extract scope-check and compile-verify logic to `knowledge/`; reference as single-source-of-truth in steps 2 and 3.

**[Low] Structure**
Observation: Several code blocks (Step 1, Step 2, decision tree) lack language tags.
Fix: Add language tags (`bash`, `text`, `markdown`) to all code blocks.

---

### /al-dev-interview

**[High] Prompt Clarity**
Observation: Phase 2 GATE says "before signalling completion" — "signalling completion" is undefined.
Fix: Define: "The interview agent must explicitly state 'INTERVIEW COMPLETE' and confirm questions were asked in all 11 categories. Upon this explicit signal, proceed to Phase 3."

**[Medium] Prompt Clarity**
Observation: Phase 2 instructs the agent to "Work through these categories" without defining whether categories are skipped if answered earlier.
Fix: Clarify: "Ask about each category. If a category's key question was answered earlier, skip follow-ups but confirm coverage before moving on."

**[Low] Structure**
Observation: Code blocks in Phase 3 and Phase 4 lack language tags.
Fix: Tag with `bash` or `markdown` as appropriate.

---

### /al-dev-investigate

**[High] Prompt Clarity**
Observation: Step 4 says "if ≤2 hypotheses, spawn 1 agent" but earlier says "Spawn 2 Explore agents in parallel" — contradictory without a complete decision tree.
Fix: Clarify: "If 1–2 hypotheses: spawn 1 agent. If 3–4: spawn 2 agents (H1+H2, H3+H4). If 5+: spawn 3 agents distributing evenly."

**[Low] Structure**
Observation: Multiple code blocks (Step 0, Step 4 bash commands, markdown templates) lack language tags.
Fix: Tag all code blocks with `bash` or `markdown`.

---

### /al-dev-perf

**[High] Prompt Clarity**
Observation: Step 2 includes "Paste the full content of that file here before dispatching" — this is a skill-author instruction embedded in agent dispatch text.
Fix: Remove from agent prompt; read the file in Step 2 before assembling the dispatch prompt and reference it as input context.

**[Medium] Prompt Clarity**
Observation: Step 1a lists three symbol evidence sources in preference order but does not specify the fallback when all three are unavailable.
Fix: State: "Preference order: AL LSP → AL MCP → text search → unverified (default classification with zero evidence)."

**[Low] Structure**
Observation: Step 1a and Step 2 code blocks lack language tags.
Fix: Tag with `bash` and `markdown`.

**[Low] Bloat**
Observation: Classification and severity escalation rules are stated in Step 1a narrative, repeated in the Step 2 dispatch prompt, and illustrated again in the Step 3 example output — three repetitions.
Fix: Extract classification and severity rules to a single template reference; cite it in Step 1a and Step 2 dispatch.

---

### /al-dev-ticket

**[High] Prompt Clarity**
Observation: Step 1 includes "skip to Step 1.5" for the keyword-search branch, but the Step 1.5 header position is unclear in the document flow.
Fix: Ensure Step 1.5 is clearly labeled and step numbers flow sequentially to remove ambiguity.

**[Medium] Prompt Clarity**
Observation: Phase 0.5 uses `$ARGUMENTS` without defining it as user input at the top of the skill.
Fix: Add at the top of Phase 0.5: "`$ARGUMENTS` = the text provided by the user after `/al-dev-ticket`, extracted by the harness."

**[Low] Structure**
Observation: Multiple code blocks (Phase 0.5 bash, Step 1 terminal examples, Step 3 prompt blocks) lack language tags.
Fix: Tag with `bash`, `text`, or `markdown`.

---

### /al-dev-document

**[Medium] Prompt Clarity**
Observation: Step 0 asks the user to select an audience but does not define what "audience" means operationally or how the docs-writer uses the selection.
Fix: State: "AUDIENCE determines depth and vocabulary: Technical = code references + AL syntax; Functional = business rules in plain language; User = step-by-step navigation; Executive = 1-page summary."

**[Medium] Prompt Clarity**
Observation: Step 2: "inline documentation structure defined in Step 2" refers to a suggested outline, not a schema — the fallback path is ambiguous.
Fix: Clarify: "If template is missing, the docs-writer uses the outline in the 'Documentation structure' subsection as a fallback template."

**[Low] Structure**
Observation: Code blocks in Step 0 and Step 2 lack language tags.
Fix: Add `bash` or `markdown` tags to all code blocks.

---

### /al-dev-explore

**[Medium] Prompt Clarity**
Observation: Step 2 Classify question type table entry "Directory scan + targeted reads" is a strategy label, not a runnable instruction.
Fix: Rephrase: "For Structural questions, use Glob to find candidate files, then Read selectively to answer the location-based query."

**[Low] Structure**
Observation: Phase 1 Step 2 bash command blocks are not tagged.
Fix: Tag all command blocks with `bash`.

---

### /al-dev-handoff

**[Medium] Name Fit**
Observation: Name implies active "handoff" (transfer task to another party); body describes packaging context and preparing for migration — a preparatory step, not the transfer itself.
Fix: Rename to `al-dev-migrate-context` or `al-dev-prepare-handoff` to reflect the preparatory role accurately.

**[Low] Structure**
Observation: Code block in Step 3 (`TARGET="[target-repo-path]"...`) lacks language tag.
Fix: Tag with `bash`.

---

### /al-dev-help

**[Medium] Prompt Clarity**
Observation: Step 2C says "Scan `.dev/` for existing workflow artifacts" without defining what constitutes a workflow artifact.
Fix: Rephrase: "Scan `.dev/` for: `project-context.md`, `*-al-dev-interview-requirements.md`, `*-al-dev-plan-solution-plan.md`, `*-al-dev-develop-code-review.md`."

**[Low] Structure**
Observation: Reference mode output examples in Step 2A lack language tags on table code blocks.
Fix: Add `markdown` tags to table blocks.

---

### /al-dev-lint

**[Medium] Prompt Clarity**
Observation: Step 1 says "contains no lines matching `Warning` or `Error`" — "matching" could mean literal word or diagnostic code prefix.
Fix: Clarify: "No lint issues found if the log contains zero lines matching the regex `^(Error|Warning)\b`."

**[Low] Structure**
Observation: Step 1 and Step 2 code blocks lack language tags.
Fix: Tag with `bash`.

**[Low] Bloat**
Observation: Step 3 preamble "If unresolved items exist, list them inline:" adds framing lines separated from the concrete list generation logic.
Fix: Move the condition inline with the list generation logic to remove preamble separation.

---

### /al-dev-release-notes

**[Medium] Prompt Clarity**
Observation: Phase 1 says "use the short form of `end_hash`" without defining "short form."
Fix: State: "Short form = first 7 characters of the full commit hash (Git's default abbreviation)."

**[Low] Structure**
Observation: Phase 1 and Phase 2 code blocks lack language tags.
Fix: Tag with `bash` and `text`.

---

### /al-dev-review-develop

**[Medium] Description Drift**
Observation: Body claims "full implementation of Phases 5–10" in Implementation Notes but only shows truncated outline headers; description promises "multi-reviewer code review" and synthesis but the phase implementations are absent.
Fix: Add full Phase 5–10 implementation details (review panel dispatch, compile verification, code-review artifact synthesis) or clarify this skill is a stub pending refactoring.

**[Medium] Structure**
Observation: `argument-hint: ""` is empty but skill requires Phase 4 handoff artifact as input and is orchestrator-dispatch-only with no user arguments.
Fix: Update hint to `"[no user args — dispatched by al-dev-develop]"` to clarify dispatch context.

---

---

### /commit-recover

**[Medium] Prompt Clarity**
Observation: Step 2 says "For each unresolved incident" — "unresolved" is not defined (not yet restored vs. restoration failed).
Fix: Clarify: "Unresolved incident = an incident marked 'CORRUPTION' or 'SYNTAX_ERROR' whose status is not 'RESTORED'."

**[Low] Structure**
Observation: Code blocks in Steps 2 and 4 lack language tags.
Fix: Tag with `bash` and `text`.

---

### /plan-with-critic-swarm

**[Medium] Prompt Clarity**
Observation: Step 2 lists six "Critic" roles but does not clarify whether these are distinct agents or specializations within a single agent.
Fix: Clarify: "Six critic agents are spawned in parallel, each configured for one specialization (security, testability, type-safety, rollback-safety, API-contracts, edge-cases)."

**[Low] Description Drift**
Observation: Body is a high-level overview/outline with pseudo-code dispatch, not detailed step-by-step procedures like peer skills; lacks concrete invocation detail and Artifact Contract reference.
Fix: Expand body with Phase 0 resume check, detailed Phase 1–7 steps, and Artifact Contract section per `knowledge/artifact-contracts.md`.

**[Low] Structure**
Observation: Step 1 "dispatch pattern" pseudo-code block lacks language tag.
Fix: Tag with `text`.

---

### /verify-commits

**[Low] Prompt Clarity**
Observation: Description says "auto-split if combined" but "combined" is not defined.
Fix: Rephrase: "If multiple plan groups were merged into a single commit, split them back into separate atomic commits."

**[Low] Structure**
Observation: Steps 1–4 and example code blocks lack language tags.
Fix: Tag with `bash` and `text`.

---
