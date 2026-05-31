# Plugin Health — 2026-05-31

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 5      | 24      | 0      | 29    |
| Medium   | 9      | 63      | 1      | 73    |
| Low      | 9      | 32      | 0      | 41    |
| **Total**| **23** | **119** | **1**  | **143** |

**Failed lenses:** None

**Top 5 ranked actions:**

1. **Renumber al-dev-review-develop phases 1–6** (Quality/Bloat+Clarity, High) — Phases currently run in non-sequential order (5→8→8.5→6-7→9→10); the skill itself must include an execution-order note to explain it. This is the single highest-frequency confusing pattern — used on every develop run. Fix: renumber phases 1–6 in execution order, retaining parent-workflow reference in parentheses.

2. **Split al-dev-developer into TDD and traditional paths** (Design/Scope-Isolation, High) — Agent body contains two distinct workflows (TDD with RED-GREEN-REFACTOR gates vs. traditional with BUILD_VERIFY_GATE). The conditional dispatch logic spans 40+ lines and runs on every invocation. Fix: create al-dev-developer-tdd and al-dev-developer-traditional; route from al-dev-develop and al-dev-fix based on test-plan presence.

3. **Add `knowledge/developer-invocation-patterns.md`** (Design/Shared-Backbone, Medium) — al-dev-developer is spawned by 3 skills (al-dev-develop, al-dev-fix, al-dev-review-develop) with materially different dispatch prompts. When SYMBOL_PREFLIGHT_GATE requirements change, al-dev-fix and al-dev-review-develop won't get the update. Fix: document 3-4 named dispatch contexts (Full Scope Preflight, Trivial Direct Fix, Architect-Guided Fix, Error Correction); add explicit knowledge-file references in al-dev-fix and al-dev-review-develop.

4. **Upgrade al-dev-code-review and al-dev-diagnostics-fixer to sonnet** (Design/Model-Fit, Medium) — Both require multi-file synthesis and judgment (severity matrix construction, rule classification, iterative compile loops). Haiku introduces truncation risk on complex inputs. Fix: change `model: haiku` → `model: sonnet` in each agent's frontmatter.

5. **Consolidate al-dev-develop and al-dev-plan phase structure** (Quality/Bloat+Clarity, High) — al-dev-develop has 11 phases (0, 0.5, 1–1.5, 1.6, 2–4.5, 6, 8–8.5) with invisible dead branches for `--autonomous` mode and a 73-line inline spawn prompt. al-dev-plan has 9 phases with a "Phase Numbering Rationale" comment block that belongs in git history. These are entry-point skills on every feature task. Fix: label optional phases explicitly "(Autonomous Mode Only)"; extract spawn prompt to knowledge file; remove Rationale section.

---

## Design suggestions

### Scope Isolation

- **al-dev-developer** | High | System prompt contains two distinct implementation workflows (TDD with RED-GREEN-REFACTOR cycle gates vs. traditional with BUILD_VERIFY_GATE), separate success evidence, and different intermediate artifacts. Callers cannot reliably predict which path runs. | Split into `al-dev-developer-tdd` and `al-dev-developer-traditional`; route from al-dev-develop based on test-plan file presence.

### Model Fit

- **al-dev-code-review** | Medium | Haiku assigned for multi-file code review requiring Logic + Security + Error Handling + Maintainability synthesis across a severity matrix. | Upgrade to sonnet.
- **al-dev-diagnostics-fixer** | Medium | Haiku assigned for lint grouping by rule ID, judgment-required classification, delegation to script-engineer, iterative compile loops, and detailed report writing. | Upgrade to sonnet.

### Caller Alignment

- **al-dev-commit-agent-analysis** | High | Inputs table documents `REPO` as required, but /al-dev-commit Step 6 dispatch prompt does not pass REPO. Agent assumes implicit working directory. | Update Inputs table: mark REPO as "inferred from current working directory; not passed by caller".
- **al-dev-commit-message-drafter** | Medium | Inputs lack structure details for MANIFESTS, PROJECT_CONTEXT, and FD_TICKET formats. | Document structured format for each dispatch field.
- **al-dev-commit-lint-fixer** | Medium | GROUP_N structured blocks described in Inputs but no example structure. | Add example APPROVED_PLAN structure showing GROUP_N blocks, files array, and message field.
- **al-dev-commit-ooxml-validator** | Medium | Same as al-dev-commit-lint-fixer. | Same fix.
- **al-dev-commit-agent-execute** | Medium | APPROVED_PLAN Inputs table lacks GROUP_N field structure. | Document GROUP_N structure; reference message-drafting output format.
- **al-dev-developer** | Low | Inputs table implies code-review file is a dispatch parameter; developer actually reads it directly from `.dev/`. | Clarify: "reads directly from `.dev/` rather than receiving as dispatch parameter".
- **al-dev-solution-architect** | Low | Inputs table says "glob pattern match" without specifying `*-al-dev-interview-requirements.md`. | Specify exact glob pattern.

### Tool Hygiene

- **al-dev-support-reply-drafter** | Low | `Write` tool declared but agent constructs content passed back in return block to be written by the caller. Usage is implicit. | Remove `Write` from tools list or add explicit file-write step.
- **al-dev-interview** | Low | `USER_GATE` referenced in Step 1 governance but not integrated into process steps 2–6. | Add explicit USER_GATE invocation steps or clarify single-gate-at-opening behavior.

### Shared Execution Backbone

- **al-dev-developer (3 callers)** | Medium | Three skills spawn this agent with materially different dispatch prompts; no shared knowledge doc governs the contexts. Drift risk when preflight gates change. | Add `knowledge/developer-invocation-patterns.md` with 3-4 named contexts; update al-dev-fix and al-dev-review-develop to reference it.
- **al-dev-solution-architect / Explore subagent** | Low | Both have documented invocation patterns (`knowledge/architect-invocation-patterns.md`, `knowledge/explore-subagent-pattern.md`). Pattern variation is intentional. | No action required.

### Complexity Outliers

- **al-dev-review-develop** | High | 6 phases, non-sequential numbering (5→8→8.5→6-7→9→10), two separable concern clusters (Preparation & Validation vs. Review Panel & Synthesis). Skill includes a required execution-order note to explain its own phase ordering. | Renumber phases 1–6 in execution order; consider extracting Phases 6-7 + 9-10 into `/al-dev-review-synthesis` if the split is validated against al-dev-develop's handoff contract.
- **al-dev-commit** | High | 5 phases; Step 9.5 introduced a new validation pipeline (lint-fixer + ooxml-validator) that adds conditional overhead on every invocation regardless of staged file types. | Invoke preflight agents conditionally based on whether staged files include Python/markdown (lint) or OOXML (validator).
- **al-dev-develop** | High | 11 phases when sub-phases counted; Phases 1.5 and 4.5 are autonomous-only but invisible without reading the flag handling; Phase 3 inline spawn prompt spans 73 lines. | Label optional phases "(Autonomous Mode Only)" at Phase 1; extract spawn prompt to knowledge file; remove Glossary section.
- **al-dev-handoff** | Medium | 3 phases, no agent, bash-only — overlaps with al-dev-explore's cross-repo discovery. Candidates for folding into al-dev-explore as a conditional Phase 4. | Absorb: fold into al-dev-explore as conditional Phase 4, triggered when Affected Repositories table is non-empty.
- **verify-commits** | Low | 4 phases, no agent, inline validation. Could integrate as optional Step 11.5 in al-dev-commit (post-execution verification via --verify flag). | Absorb into al-dev-commit as optional post-execution step.

### Handoff Chain Gaps

- **Post-commit release pipeline** | Medium | Commit chain terminates at 5 independent post-commit branches (release-notes, handoff, document, recover, consolidate) with no unified coordination step. Release notes are generated but readiness is never validated before deployment. | Add optional `al-dev-release-coordinate` skill that reads release-notes, consolidation summary, and code-review artifact to confirm release readiness. (Note: /al-dev-publish was previously assessed as deferred pending scope clarification in docs/al-dev-skills-map.md.)
- **Performance findings not re-validated after fix** | Low | al-dev-perf findings inform al-dev-plan and al-dev-fix, but post-fix re-validation against original findings never occurs. | Optional: add re-scan capability to /al-dev-fix for CRITICAL/HIGH perf issues post-fix.
- **Interview notes orphaned** | Low | al-dev-interview writes both `*-interview-notes.md` and `*-interview-requirements.md`; only requirements are consumed downstream. Architects lose original user reasoning. | Optional: reference interview notes in the solution plan artifact.

### Near-Duplicate Shapes

_No issues found._ No pairs met all three merge criteria.

### Pre-planning Skills

_No issues found._ al-dev-explore, al-dev-interview, and al-dev-perf are correctly represented as dashed tributary arrows in the Layer 1 diagram with named outputs referenced by downstream consumers.

---

## Quality findings

### Agent Bloat

- **al-dev-developer** | High | 8 top-level sections; 56-line Workflow with deeply nested TDD/traditional conditional. Compilation guidance restated in multiple subsections. | Extract TDD vs. Traditional decision tree to knowledge doc; consolidate Standards + Governance; remove redundant compilation warnings.
- **al-dev-solution-architect** | High | Schema Mapping Decisions (27 lines, repetitive table/field rules) and MCP Tools guidance belong in knowledge files. | Move to `knowledge/schema-mapping-decisions.md` and `knowledge/mcp-tool-selection.md`.
- **al-dev-commit-agent-analysis** | Medium | Manifest Extraction Steps 1–6 read as expanded pseudocode; extraction patterns repeat across steps. | Extract bash command patterns to `knowledge/commit-analysis-procedures.md`.
- **al-dev-commit-lint-fixer** | Medium | Regex corruption warning appears twice; `.git/` fallback branch always evaluates identically. | Single regex safety callout at top; remove `.git/` fallback branch.
- **al-dev-release-notes-writer, al-dev-docs-writer, al-dev-script-engineer** | Medium | Standalone reference sections (6–10 lines each) for content that should be one-sentence knowledge-file pointers. | Extract to knowledge files; replace with single-sentence references.
- **al-dev-expert-reviewer, al-dev-performance-reviewer, al-dev-security-reviewer** | Low | "Review Focus" sections list categories that duplicate knowledge file references; Step 3 single-branch conditionals could each be one sentence. | Consolidate to knowledge reference; merge single-branch conditionals.
- **al-dev-interview, al-dev-support-reply-drafter, al-dev-ticket-agent** | Low | Inline pseudocode/regex blocks (7–17 lines) belong in knowledge files. | Extract to knowledge file; reduce inline content to 3–4 lines.

### Agent Prompt Clarity

- **al-dev-commit-lint-fixer** | High | "Re-stage fixed files" in Step 2 — no command specified. | Add: "After each ruff invocation, run `git add <file>` to stage the modified file."
- **al-dev-interview** | High | References `knowledge/interview-question-bank.md` but provides no schema for adapting questions to project scope. | Add: "For each question in the bank, check if it applies to the stated scope; skip and note out-of-scope categories."
- **al-dev-solution-architect** | High | "Best existing analogue in the project" — "best" undefined with no tiebreaker. | Add ranking: (1) Exact structural match; (2) same object type; (3) similar module scope; (4) none — record with rationale.
- **al-dev-ticket-agent** | High | `cid:` inline attachment format described but no guidance when cid: references appear without attachment metadata. | Add: "If cid: present but attachment array empty, note: 'INLINE_IMAGES: Detected cid: references but no attachment metadata; may be lost in API response'."
- **al-dev-code-review** | Medium | "Trivial matters" undefined — no operative criteria. | Define with examples or reference criteria.
- **al-dev-commit-agent-execute** | Medium | Boundary between "scripted fix" and "all other" hook failures not enumerated. | Enumerate fix types in order: trailing whitespace → Python lint → (stop).
- **al-dev-diagnostics-fixer** | Medium | Blocking behavior after judgment-required issue found is unstated. | Clarify: "Complete all scripted fixes first, then stop and wait for user input."
- **al-dev-explore** | Medium | "Trivial questions" undefined for the context check. | Replace with: "If question can be answered with <10 grep patterns or <5 files, answer inline."
- **al-dev-support-researcher** | Medium | "Related" BC history boundary is vague. | Add: "Search BC history only for exact symbol matches and tables modified in last 3 major versions; report 'no matches' if none found."

### Skill Bloat

- **al-dev-develop** | High | 11 phases with invisible dead branches (Phases 1.5, 4.5 autonomous-only), 73-line inline spawn prompt, Glossary section belonging in git history. | Label optional phases "(Autonomous Mode Only)"; extract spawn prompt to knowledge file; remove Glossary.
- **al-dev-fix** | High | 12 steps with nested numbering 0–9 within Step 3, confusing two-branch structure. | Consolidate into two clear paths: "Trivial Path (3 steps)" and "Non-Trivial Path (5 steps)"; remove nested numbering.
- **al-dev-investigate** | High | 12 steps (Steps 0–6); 64 lines of pre-hypothesis context gathering before formulation. | Consolidate Steps 0–2 into single "Pre-flight: Load context and extract timeline" phase.
- **al-dev-plan** | High | 9 phases; Phase 1 has 6 sub-steps (57 lines); Phase Numbering Rationale section is historical commentary; Phases 1.5/1.6 have implicit activation. | Remove Rationale section; consolidate Phase 1 sub-steps; add explicit gate for 1.5/1.6.
- **al-dev-interview** | High | Phase 2 lists 11 question categories inline (39 lines). | Extract to `knowledge/interview-question-categories.md`; replace inline list with reference.
- **al-dev-commit** | Medium | Step count 11 including 4b substep; Step 4 creates two distinct concerns across 37 combined lines. | Split Step 4 into file-verification and optional acceptance-criteria check.
- **al-dev-consolidate** | Medium | Phase 2 repeats bash-command structure across 6 subsections despite referencing an external patterns file. | Extract reusable templates to consolidate-extraction-patterns.md; replace inline detail with name references.
- **al-dev-review-develop** | Medium | Non-sequential phase labels (5, 8, 8.5, 6-7, 9, 10) require a dedicated execution-order note. | Rename phases to execution order (1–6); remove execution-order note.
- **al-dev-ticket** | Medium | Steps 1 and 1.5 create an implicit dead branch (only one executes) with no upfront decision tree. | Add decision tree at top of Steps 1–1.5.

### Skill Prompt Clarity

- **al-dev-consolidate** | High | Update mode staleness check has no explicit else clause — incomplete conditional. | Add: "If no source file is newer, skip writing this session and proceed to next date group."
- **al-dev-develop** | High | Phase execution order never explicitly stated; "explicitly named" files undefined. | Add execution sequence statement; define: "Explicitly named = listed by full path or object type in solution plan."
- **al-dev-fix** | High | TRIVIAL/NON-TRIVIAL borderline undefined; "in scope" vs. "out of scope" undefined for scope check. | Add decision rules for both.
- **al-dev-interview** | High | Phase 2 GATE has no enforcement mechanism if agent doesn't output 'INTERVIEW COMPLETE'. | Add: "Do not proceed to Phase 3 until agent outputs 'INTERVIEW COMPLETE' with explicit 11-category confirmation."
- **al-dev-investigate** | High | Reconciliation Gate (pre-existing/environmental root cause) — not stated whether it blocks progression or warns. | Specify: "STOP and rewrite root cause section; do not proceed to Step 6 without reconciliation."
- **al-dev-plan** | High | Input Validation Gate has no re-ask limit if user's answer remains vague. | Add: "Ask once. If still vague, ask once more. If unclear after 2 attempts, request a written spec."
- **al-dev-review-develop** | High | Non-sequential execution order unexplained; Phase 8 following Phase 5 is surprising. | Add explanation: "Execution is non-sequential because Phase 5 prepares inputs for compile verify (Phase 8), which gates the reviewer panel (6-7)."
- **al-dev-ticket** | High | Phase 5 "If MODE is context-only: Skip / Exit" — what the skill outputs before exiting is undefined. | Specify: "Output ticket context summary to user and stop. Do not continue to Phase 6."
- **plan-with-critic-swarm** | High | Contradictory or zero-finding critics have no defined handling. | Define: "Zero findings = 'NONE (clean)'. Contradictions = flag as 'conflicting feedback' and present both viewpoints."
- **verify-commits** | High | Step 3 instructs `git reset --soft HEAD~<N>` with N undefined and no validation before reset. | Add: "Determine N by counting commits to split; verify with `git log --oneline -n <N>` before resetting."
- **al-dev-lint** | Medium | Case-sensitive `Warning`/`Error` matching; AL compile output may use lowercase. | Change to case-insensitive: `grep -iE 'error\|warning'`.
- **al-dev-plan** | Medium | "When in doubt, default to opus" — "doubt" has no operative definition. | Replace with: "If file count unknown, requirements ambiguous, or cannot confidently classify as SIMPLE, default to opus."

### Skill Description Drift

- **al-dev-develop** | Medium | Description states "Produces Phase 4 handoff artifact" but no explicit step writes this artifact. | Add explicit Phase 4 conclusion step.
- **al-dev-commit** | Medium | Description promises detecting scope creep but body lacks pre-staging scope validation. | Add Step 2.5 or clarify description.
- **al-dev-interview** | Medium | "Gather requirements" undersells output — body produces formal governance-token requirements document. | Update description verb to "Gather and formalise".
- **al-dev-plan** | Medium | Competitive design debate described as guaranteed but is facilitated (not mandatory in all cases). | Clarify: "debate may be abbreviated for SIMPLE tier".
- **al-dev-release-notes** | Medium | "Ambiguous changes" classification workflow not mentioned in description. | Add to description.
- **commit-recover** | Medium | How incidents are added to `commit-integrity.log` is not documented in body. | Add note about what populates the log.
- **plan-with-critic-swarm** | Medium | "Apply auto-fixes" is listed as a step example but not as a guaranteed algorithmic step. | Add explicit Step 4 with auto-fix decision criteria.
- **al-dev-handoff** | Low | Description says "copies context" but body also generates a new handoff prompt artifact. | Add "generates handoff prompt" to description.

### Skill Name Fit

- **al-dev-handoff** | Medium | Name implies work transfer to a person/team; primary purpose is cross-repository context migration. | Rename to `al-dev-migrate-context` or update description explicitly.
- **al-dev-review-develop** | Medium | Name suggests standalone review command; this is Phase 5+ of /al-dev-develop dispatched automatically after Phase 4 handoff. | Rename to `al-dev-develop-review` or add prominent "not a standalone entry point" note.
- **al-dev-support** | Medium | Deprecated alias creates discovery confusion in the skill registry. | Remove from published skill list or archive.

### Agent Name Fit

- **al-dev-commit-recover-verifier** | High | Name uses "verifier" (inspection-only implied) but agent applies fixes (git restore, regex reconstruction, schema rebuild). | Rename to `al-dev-commit-recovery-fixer` or `al-dev-commit-file-recoverer`.
- **al-dev-commit-agent-analysis** | Medium | Compound "commit-agent-analysis" makes phase sequencing ambiguous; doesn't signal read-only role. | Rename to `al-dev-commit-analyzer`.
- **al-dev-commit-agent-execute** | Medium | Same compound-name ambiguity. | Rename to `al-dev-commit-executor`.
- **al-dev-ticket-agent** | Medium | Generic "ticket-agent" implies broader scope than actual (Freshdesk API fetch only). | Rename to `al-dev-ticket-fetcher` or `al-dev-ticket-context-loader`.

### Agent Structural Conventions

- **Seven agents missing `name` field in frontmatter** | Medium | al-dev-code-review, al-dev-commit-agent-analysis, al-dev-commit-agent-execute, al-dev-commit-lint-fixer, al-dev-commit-message-drafter, al-dev-commit-ooxml-validator, al-dev-support-reply-drafter. | Add `name: <agent-name>` to each frontmatter block.
- **al-dev-solution-architect** | Medium | Non-canonical MCP tool names — verify `MCP: bc-code-intelligence`, `MCP: microsoft-docs`, `MCP: al-mcp-server` match canonical vocabulary in agent-tool-projection-policy.
- **Pervasive missing code block language tags (12 agent files)** | Low | al-dev-developer, al-dev-diagnostics-fixer, al-dev-docs-writer, al-dev-expert-reviewer, al-dev-explore, al-dev-interview, al-dev-performance-reviewer, al-dev-release-notes-writer, al-dev-script-engineer, al-dev-security-reviewer, al-dev-support-researcher, al-dev-ticket-agent — each has at least one unlabelled code block. | Add `bash`, `python`, or `text` language tags as appropriate.
- **al-dev-commit-recover-verifier** | Low | Header numbering inconsistency — "Step N" and "Fallback N" mixed. | Standardize to one convention.

### Agent Description Drift

- **al-dev-commit-recover-verifier** | Low | Description promises "Fixed AL files" as output; Return Block only documents recovery counts and report path. | Clarify that fixed files are written in-place, or adjust Outputs section.
- **al-dev-ticket-agent** | Low | Description says "optionally download attachments" but body only extracts URLs and inline image references. | Remove "download" or add attachment retrieval step.

### Skill Structural Conventions

- **al-dev-help** | Medium | `argument-hint: ""` (empty string) should be omitted when the skill takes no arguments. | Remove the `argument-hint` line.
- **Pervasive missing code block language tags (all 21 skills affected)** | Low | Every skill file has at least one unlabelled code block. Most affected: al-dev-commit, al-dev-fix, al-dev-develop, al-dev-handoff, al-dev-review-develop, al-dev-ticket, al-dev-investigate, al-dev-perf, al-dev-plan. | Add `bash`, `python`, `markdown`, or `text` as appropriate to all bare code fences.

---

## Naming violations

- **al-dev-release-notes output path** | Medium | Output path `.dev/$(date +%Y-%m-%d)-al-dev-release-notes-<VERSION>.md` adds undocumented placeholders (`<VERSION>`, `[app-id]`, `[short-hash]`) beyond the documented `YYYY-MM-DD-{skill}-{kind}.md` pattern. Agent spec uses `.dev/YYYY-MM-DD-[app-id]-al-dev-release-notes-[short-hash].md` with additional undocumented placeholders. | Review against `docs/al-dev-naming-convention.md`. Consider moving version/app-id/hash into file content rather than the filename, or document as an approved exception with rationale.

---

## Graph deltas

**Dead knowledge files** (exist on disk, referenced by nothing in skill/agent bodies):
- `agent-tool-projection-policy.md`, `anti-patterns.md`, `code-review-template.md`, `commit-conventions.md`, `feedback-resolution.md`, `harness-concepts.md`, `lens-invocation-patterns.md`, `map-change-rubber-duck-checks.md`, `map-suggestion-templates.md`, `proportional-planning.md`, `publish-workflow-opportunity.md`, `quality-checklist.md`, `review-panel-pattern.md`, `rubber-duck.md`, `session-analysis-report-format.md`, `skill-test-format.md`, `verification-and-planning.md`

Note: knowledge files may be referenced in descriptions or prose without triggering graph edges. Verify before archiving.

**Off-path skills** (not connected via any primary workflow edge in the graph):
`al-dev-consolidate`, `al-dev-diagram-generator`, `al-dev-document`, `al-dev-explore`, `al-dev-handoff`, `al-dev-help`, `al-dev-interview`, `al-dev-lint`, `al-dev-perf`, `al-dev-release-notes`, `al-dev-review-develop`, `al-dev-support`, `commit-recover`, `plan-with-critic-swarm`, `verify-commits`

Note: many of these are intentionally optional (pre-planning tributaries, post-commit utilities, standalone tools). The graph only captures strict invocation edges; optional/dashed flows in the Layer 1 diagram are not represented. Treat this list as a visibility check, not a removal candidate list.

**Missing refs:** None — all referenced files exist on disk.
