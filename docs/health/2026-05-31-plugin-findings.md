# Plugin Findings — 2026-05-31

## Raw lens output

### Tool Hygiene Findings

- **al-dev-support-reply-drafter** | Low | `Write` tool declared but agent only constructs draft content passed back in return block to be written by the caller. `Write` tool usage is implicit in the specification but not explicitly exercised in the system prompt. | Remove `Write` from tools list, or add explicit file-write step in the workflow.

- **al-dev-interview** | Low | `USER_GATE` tool declared and referenced once in Step 1 ("CRITICAL: Use **USER_GATE** for every question group"), but the remainder of the workflow (Steps 2-6) makes no explicit mention of `USER_GATE` invocation. | Clarify whether USER_GATE is invoked once at opening or per question group; add explicit invocation steps to the workflow section.

---

### Model Fit Findings

- **al-dev-code-review** | Medium | Haiku assigned for comprehensive code review (Logic, Security, Error Handling, Maintainability). Requires analyzing multiple code sections and synthesizing findings across a severity matrix — sonnet-appropriate. | Upgrade to sonnet.

- **al-dev-diagnostics-fixer** | Medium | Haiku assigned for lint issue grouping and fixing. Task spans grouping by rule ID, judgment-required classification, delegating to script-engineer, iterative compile+fix loops, and detailed lint reports. Multi-file analysis with structured decision-making suggests sonnet. | Upgrade to sonnet.

---

### Scope Isolation Findings

- **al-dev-developer** | Medium | System prompt describes two distinct implementation workflows (TDD vs. traditional) with separate gates, control flow, and success evidence. Both workflows accept the same plan but produce different intermediate artifacts and require different user approval patterns. | Split into `al-dev-developer-tdd` and `al-dev-developer-traditional`, with `al-dev-develop` skill routing based on test-plan presence. Eliminates 40+ lines of conditional workflow selection.

---

### Caller Alignment Findings

- **al-dev-commit-agent-analysis** | High | Agent Inputs table documents `REPO` as required, but /al-dev-commit Step 6 dispatch prompt does not pass REPO. Agent assumes implicit current directory. | Update Inputs table to mark REPO as "inferred from current working directory; not passed by caller" or add REPO to the dispatch prompt.

- **al-dev-commit-message-drafter** | Medium | Inputs section lacks structure details for MANIFESTS, PROJECT_CONTEXT, and FD_TICKET format. Future callers may misunderstand expected format. | Document structured format: valid scopes, object ID prefix, AL naming pattern, gitmoji style; document MANIFESTS format from prior agent output.

- **al-dev-commit-lint-fixer** | Medium | Inputs table describes GROUP_N structured blocks but provides no example structure. | Update Inputs table with example APPROVED_PLAN structure showing GROUP_N blocks, files array, and message field.

- **al-dev-commit-ooxml-validator** | Medium | Same as al-dev-commit-lint-fixer: GROUP_N structure undocumented. | Same fix.

- **al-dev-commit-agent-execute** | Medium | Inputs table says "APPROVED_PLAN" but doesn't document GROUP_N structure or required fields. | Update Inputs table with GROUP_N structure and reference to message-drafting output format.

- **al-dev-developer** | Low | Inputs table marks code-review file as optional but implies it's passed as dispatch parameter when it's actually read directly by the developer. | Clarify: "reads directly from `.dev/` rather than receiving as dispatch parameter".

- **al-dev-solution-architect** | Low | Inputs table uses "glob pattern match" without specifying the exact pattern. | Update: "From latest `*-al-dev-interview-requirements.md` (use most recent dated variant)".

---

### Usage Patterns Findings

_No Inline candidates found._

All single-use agents have documented Inputs/Outputs tables and substantive body content (≥44 lines). Three zero-use agents noted: al-dev-code-review, al-dev-explore, al-dev-script-engineer — all documented as available for standalone use, not candidates for inlining.

---

### Shared Execution Backbone Findings

- **al-dev-developer** | Medium | Spawned by 3 skills with significantly different dispatch prompts: al-dev-develop includes SYMBOL_PREFLIGHT_GATE + SCOPE EXPANSION GATE; al-dev-fix trivial path uses minimal prompt; al-dev-review-develop focuses on compile-error fixing. No two skills have identical spawn patterns, creating drift risk when preflight or scope-gate requirements change. | **Connect candidate**: document canonical developer invocation pattern in `knowledge/developer-invocation-patterns.md` with 3-4 distinct contexts (full-scope implementation, trivial fix, architect-informed fix, error correction). Update al-dev-fix and al-dev-review-develop to reference the knowledge file.

- **al-dev-solution-architect** | Low | Two meaningfully different invocation patterns (competitive debate vs. quick analysis) documented in `knowledge/architect-invocation-patterns.md`. Pattern variation is intentional. | No action required.

- **Explore subagent** | Low | Three skills consistently use `knowledge/explore-subagent-pattern.md`. No drift detected. | No action required.

---

### Complexity Outliers Findings

**High phase count (Atomise candidates):**

- **al-dev-review-develop** | High | 6 phases with non-sequential numbering (5→8→8.5→6-7→9→10) and two separable concern clusters: Preparation & Validation (5, 8, 8.5) vs. Review Panel & Synthesis (6-7, 9, 10). | Atomise: extract Phases 6-7 and 9-10 into a dedicated `/al-dev-review-synthesis` skill; or renumber phases 1–6 in execution order.

- **al-dev-commit** | High | 5 phases; Step 9.5 adds a new validation pipeline (lint-fixer + ooxml-validator) creating cognitive overhead. | Conditionally invoke preflight agents based on staged file types; agents already split, skill orchestration is the remaining concern.

- **al-dev-develop** | High | 11 phases when sub-phases counted. Optional phases 1.5 and 4.5 (autonomous-only) create invisible dead branches. Phase 3 inline spawn prompt spans 73 lines. | Consolidate --autonomous activation at Phase 1; label optional phases "(Autonomous Mode Only)"; extract developer spawn prompt to knowledge file; remove Glossary section.

**Zero-agent 2-phase skills (Absorb candidates):**

- **al-dev-handoff** | Medium | 3 phases, no agent, bash-only. Overlaps with al-dev-explore's cross-repo discovery. | Absorb: fold into al-dev-explore as conditional Phase 4 triggered when Affected Repositories table is non-empty.

- **verify-commits** | Low | 4 phases, no agent. Could integrate as optional Step 11.5 in al-dev-commit. | Absorb: integrate as optional post-execution verification triggered by --verify flag.

---

### Near-Duplicate Shapes Findings

_No issues found._ No pairs met all three merge criteria.

---

### Handoff Chain Gaps Findings

- **Post-commit release pipeline gap** | Medium | The commit chain terminates at 5 post-commit branches with no unified next step. Release notes are generated but there is no skill to validate release readiness or coordinate release artifacts. | Add optional `al-dev-release-coordinate` skill that reads the latest release-notes, consolidation summary, and code-review artifact to confirm release readiness. (Note: /al-dev-publish previously assessed as deferred pending scope clarification.)

- **Performance findings tracking** | Low | al-dev-perf findings inform al-dev-plan and al-dev-fix but fixes applied via al-dev-fix don't re-validate against original findings. | Optional: add re-scan capability to /al-dev-fix for CRITICAL/HIGH perf issues post-fix.

- **Interview notes orphaned** | Low | al-dev-interview writes both interview-notes.md and interview-requirements.md but only requirements are consumed downstream. | Optional: reference interview notes in the solution plan so architects can see original user reasoning.

---

### Pre-planning Skills Findings

_No issues found._ All three pre-planning skills (al-dev-explore, al-dev-interview, al-dev-perf) are correctly represented in Layer 1 as dashed tributaries with properly named output files referenced downstream.

Minor documentation opportunity: al-dev-interview SKILL.md could clarify that interview-requirements.md (not interview-notes.md) is the canonical handoff output to al-dev-plan.

---

### Agent Bloat Findings

- **al-dev-developer** | High | 8 top-level sections; Workflow spans 56 lines with deeply nested TDD vs. traditional conditional logic. Multiple subsections restate compilation guidance. | Consolidate Standards and Governance sections; extract TDD vs. Traditional to a knowledge document; remove redundant compilation warnings.

- **al-dev-solution-architect** | High | 8+ major sections; Schema Mapping Decisions (27 lines) and MCP Tools guidance belong in knowledge files. | Move schema mapping to `knowledge/schema-mapping-decisions.md`; extract MCP guidance to `knowledge/mcp-tool-selection.md`.

- **al-dev-commit-agent-analysis** | Medium | Manifest Extraction section (Steps 1–6) reads like expanded pseudocode with repetitive patterns. | Extract bash command patterns to `knowledge/commit-analysis-procedures.md`.

- **al-dev-commit-lint-fixer** | Medium | Regex corruption warning appears twice; `.git/` fallback branch is redundant. | Single regex safety callout; remove `.git/` fallback.

- **al-dev-release-notes-writer** | Medium | 15-line Workflow section; standalone "Handling Diagrams" section (6 lines) and Mermaid reference (6 lines) add padding. | Consolidate to 5-bullet workflow; fold Diagrams section into workflow.

- **al-dev-docs-writer** | Medium | RTM callout repeats guidance from Step 4; Documentation Guidelines (34 lines) mostly references external knowledge files. | Remove RTM callout; compress Guidelines to 1-sentence pointers.

- **al-dev-script-engineer** | Medium | Standalone Conventions, Toolkit Integration (10-line snippet), and Token Generation sections all belong in knowledge files. | Extract to knowledge file; reduce to one-sentence references.

- **al-dev-interview** | Medium | "Your Mission" (3 lines) is redundant; Steps 3 and 5 both address clarification. Question categories repeated from question bank. | Remove "Your Mission"; merge Steps 3 & 5; replace question categories with knowledge file reference.

- **al-dev-support-reply-drafter** | Medium | Step 1.5 (9 lines) is one rule that could be 2 lines. Tone constraints have repetitive explanatory asides. | Compress Step 1.5 to 2 lines; compress constraints to 1-sentence bullets.

- **al-dev-expert-reviewer, al-dev-performance-reviewer, al-dev-security-reviewer** | Low | "Review Focus" sections list categories that duplicate knowledge file references. Single-branch Step 3 conditions could be one sentence each. | Consolidate to knowledge reference only; merge single-branch conditionals.

- **al-dev-ticket-agent** | Low | Step 1.5 inline regex pseudocode (17 lines) should be a knowledge file reference. | Extract patterns to knowledge file.

---

### Agent Prompt Clarity Findings

**High severity:**

- **al-dev-commit-lint-fixer**: Undefined placeholder "Re-stage fixed files" — no command specified. → Add: "After each ruff invocation, run `git add <file>` to stage the modified file".
- **al-dev-interview**: References `knowledge/interview-question-bank.md` but no schema for adapting questions to project scope. → Add explicit adaptation rule.
- **al-dev-solution-architect**: "Best existing analogue" undefined with no tiebreaker. → Add explicit ranking: exact structural match → same object type → similar scope → none.
- **al-dev-ticket-agent**: `cid:` format described but no guidance for when cid: references appear without attachment metadata. → Add: "If cid: present but attachment array empty, note 'INLINE_IMAGES: Detected cid: references but no attachment metadata'".

**Medium severity (representative):**
- al-dev-code-review: "trivial" undefined for comment exclusion
- al-dev-commit-agent-analysis: incomplete conditional for missing fallback path
- al-dev-commit-agent-execute: boundary between "scripted fix" and "all other" undefined
- al-dev-commit-message-drafter: "mechanical changes" undefined
- al-dev-commit-recover-verifier: commit-integrity.log format undefined
- al-dev-developer: "logical group" for compile batching ambiguous
- al-dev-diagnostics-fixer: blocking behavior for judgment-required rules unclear
- al-dev-explore: "trivial questions" undefined
- al-dev-performance-reviewer: "8 patterns" is non-binding claim
- al-dev-release-notes-writer: no instruction if Mermaid helper file unavailable
- al-dev-script-engineer: no decision criteria for language selection with multiple stacks
- al-dev-support-reply-drafter: escalation format for inconclusive findings undefined
- al-dev-support-researcher: "related" BC history boundary vague

---

### Agent Description Drift Findings

- **al-dev-commit-recover-verifier** | Low | Description promises "Fixed AL files" as output but Return Block only documents report file path and recovery counts. | Clarify that fixed files are written in-place to original paths, or adjust description.

- **al-dev-ticket-agent** | Low | Description says "optionally download attachments" but body only extracts URLs and inline image references. | Remove "download attachments" from description or add Step describing attachment retrieval.

---

### Agent Name Fit Findings

- **al-dev-commit-recover-verifier** | High | Name uses "verifier" but agent actually applies fixes (git restore, regex reconstruction, schema rebuild). Name actively misleads about the action verb. | Rename to `al-dev-commit-recovery-fixer` or `al-dev-commit-file-recoverer`.

- **al-dev-commit-agent-analysis** | Medium | Compound name "commit-agent-analysis" — "agent" part is ambiguous, doesn't clarify read-only role. | Rename to `al-dev-commit-analyzer`.

- **al-dev-commit-agent-execute** | Medium | Same compound-name issue. | Rename to `al-dev-commit-executor`.

- **al-dev-ticket-agent** | Medium | Generic "ticket-agent" implies broader scope than actual (Freshdesk API fetch only). | Rename to `al-dev-ticket-fetcher` or `al-dev-ticket-context-loader`.

---

### Agent Structural Conventions Findings

**Medium severity — missing `name` field in frontmatter:**
al-dev-code-review, al-dev-commit-agent-analysis, al-dev-commit-agent-execute, al-dev-commit-lint-fixer, al-dev-commit-message-drafter, al-dev-commit-ooxml-validator, al-dev-support-reply-drafter — all missing `name` field.

**Low severity — pervasive missing code block language tags:**
al-dev-developer (line 95), al-dev-diagnostics-fixer (line 39), al-dev-docs-writer (lines 35–37, 70–78), al-dev-expert-reviewer (lines 89–101), al-dev-explore (lines 59, 74), al-dev-interview (lines 71–77), al-dev-performance-reviewer (lines 77–91), al-dev-release-notes-writer (lines 78–93), al-dev-script-engineer (lines 69–76), al-dev-security-reviewer (lines 87–103), al-dev-support-researcher (lines 45–62), al-dev-ticket-agent (lines 39–42, 63–67).

**Low severity:** al-dev-commit-recover-verifier: header numbering inconsistency ("Step N" vs "Fallback N").

**Medium severity:** al-dev-solution-architect: verify MCP tool names match canonical vocabulary in agent-tool-projection-policy.

---

### Skill Bloat Findings

**High severity:**

- **al-dev-develop**: 11 phases, invisible dead branches for --autonomous mode, inline spawn prompt (73 lines), Glossary section belongs in git history.
- **al-dev-fix**: 12 steps, nested numbering (0–9 within Step 3), confusing dual-branch structure.
- **al-dev-investigate**: 12 steps (Steps 0–6), 64-line pre-hypothesis preamble.
- **al-dev-plan**: 9 phases, Phase 1 has 6 sub-steps (57 lines), Phase Numbering Rationale comment, implicit Phase 1.5/1.6 activation.
- **al-dev-interview**: Phase 2 lists 11 question categories inline (39 lines).

**Medium severity:**
- al-dev-commit: Step 4 creates two distinct concerns across 37 lines
- al-dev-consolidate: Phase 2 repeats bash-command structure across 6 subsections
- al-dev-document: Steps 2–3 repeat docs-writer dispatch and review
- al-dev-perf: Step 1a symbol-classification logic (32 lines) belongs in knowledge file
- al-dev-review-develop: non-sequential phase labels create cognitive load
- al-dev-ticket: dead branch between Steps 1 and 1.5 with implicit activation

---

### Skill Prompt Clarity Findings

**High severity:**
- al-dev-consolidate: incomplete conditional in Update mode staleness check
- al-dev-develop: non-linear phase execution order unstated; "explicitly named" undefined
- al-dev-fix: TRIVIAL/NON-TRIVIAL borderline undefined; "in scope" vs "out of scope" undefined
- al-dev-interview: Phase 2 GATE has no enforcement if agent doesn't output 'INTERVIEW COMPLETE'
- al-dev-investigate: Reconciliation Gate enforcement unstated
- al-dev-plan: Input Validation Gate has no re-ask limit
- al-dev-review-develop: non-sequential execution order unexplained
- al-dev-ticket: Phase 5 "exit" behavior undefined
- plan-with-critic-swarm: contradictory/zero critic findings undefined
- verify-commits: N for git reset --soft undefined

**Medium severity (representative):**
- al-dev-commit: success evidence references external file only
- al-dev-consolidate: "no files present" vague
- al-dev-diagram-generator: "stripped" path ambiguous
- al-dev-document: spot-check loop has no exit condition
- al-dev-explore: approach column in classification table uses vague terms
- al-dev-handoff: no guidance if source-project-context.md already exists in target
- al-dev-lint: case-sensitive matching for Error/Warning
- al-dev-perf: conflicting classification indicators undefined
- al-dev-plan: "when in doubt" undefined for model selection
- al-dev-release-notes: format for user's decision on ambiguous changes undefined
- al-dev-ticket: search result count boundaries missing
- commit-recover: output format for "prompt user to re-run" undefined

---

### Skill Description Drift Findings

- **al-dev-develop** | Medium | Description states "Produces Phase 4 handoff artifact" but no explicit step writes this artifact. | Add explicit Phase 4 conclusion step.
- **al-dev-commit** | Medium | Description promises detecting scope creep but body lacks pre-staging scope check. | Add Step 2.5 or clarify description.
- **al-dev-interview** | Medium | "Gather requirements" undersells output — body produces formal governance-token requirements document. | Update description verb.
- **al-dev-investigate** | Medium | Trigger phrases listed but body reads as manually invoked only. | Clarify whether triggers are automatic or manual.
- **al-dev-plan** | Medium | Competitive design debate described as guaranteed but is facilitated (not mandatory). | Clarify description.
- **al-dev-release-notes** | Medium | "Ambiguous changes" classification workflow not mentioned in description. | Add to description.
- **commit-recover** | Medium | How incidents are added to commit-integrity.log is not documented. | Add note about what populates the log.
- **plan-with-critic-swarm** | Medium | "Apply auto-fixes" listed but body only lists auto-fixes as an example, not a guaranteed step. | Add explicit Step 4 for auto-fix logic.

---

### Skill Name Fit Findings

- **al-dev-handoff** | Medium | Name implies work transfer to a person/team; actual purpose is cross-repository context migration. | Rename to `al-dev-migrate-context` or update description to state cross-repo migration explicitly.
- **al-dev-review-develop** | Medium | Name suggests standalone review but this is Phase 5+ of /al-dev-develop dispatched automatically. | Rename to `al-dev-develop-review` or clarify it's not a standalone entry point.
- **al-dev-support** | Medium | Deprecated alias creates discovery confusion. | Remove from published skill list or archive.

---

### Skill Structural Conventions Findings

**Medium severity:**
- al-dev-help: `argument-hint: ""` should be omitted

**Low severity — pervasive missing code block language tags:**
All 21 skills have at least one code block missing a language tag. Most affected: al-dev-commit, al-dev-fix, al-dev-develop, al-dev-handoff, al-dev-review-develop, al-dev-ticket, al-dev-investigate, al-dev-perf, al-dev-plan. Add `bash`, `python`, `markdown`, or `text` as appropriate.

---

### Naming Convention Findings

- **al-dev-release-notes output path** | Medium | Output path `.dev/$(date +%Y-%m-%d)-al-dev-release-notes-<VERSION>.md` adds undocumented placeholders (`<VERSION>`, `[app-id]`, `[short-hash]`) beyond the documented `YYYY-MM-DD-{skill}-{kind}.md` pattern. | Review against convention doc. Consider moving version/app-id/hash into file content rather than filename, or explicitly document as an approved exception.

---

## Failed lenses

None

## Resume information

- Total lenses in scope: 21
- Completed this session: 21
- Completed in prior sessions: 0
- Status: COMPLETE
