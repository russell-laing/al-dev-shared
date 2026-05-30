# Plugin Findings — 2026-05-30

## Raw lens output

### Design Agent Lens Tool Hygiene Findings

_No issues found._

All 20 plugin agents declare only tools they actually use. No declared-but-unused tools detected.

---

### Design Agent Lens Model Fit Findings

- **al-dev-code-review** | Medium | Haiku assigned for comprehensive code review spanning logic errors, security issues, and pattern analysis. The task requires reading multiple files and synthesizing cross-file issues; this exceeds haiku's single-step retrieval scope. | Upgrade to sonnet
- **al-dev-commit-message-drafter** | Medium | Haiku assigned for message drafting. Task requires grouping files into deployable units, understanding dependencies, and synthesizing atomic commit rationale. Multi-file reasoning needed. | Upgrade to sonnet
- **al-dev-commit-preflight** | Medium | Sonnet assigned for pre-flight validation. Task is mechanical: run linters, check line counts, validate ZIP files. Sequential steps with simple pass/fail gates; no reasoning across multiple concerns required. | Downgrade to haiku
- **al-dev-commit-agent-execute** | High | Sonnet assigned for commit execution, but the actual work is orchestration of sequential bash calls (git commit, retry logic, parsing hook output). Each retry is a simple conditional; no multi-step reasoning required. | Downgrade to haiku
- **al-dev-expert-reviewer** | Medium | Haiku assigned for AL pattern review. Task requires reading AL files and synthesizing across naming conventions, event subscribers, error handling, and BC design patterns. Pattern analysis requires cross-file reasoning and design-level judgment. | Upgrade to sonnet
- **al-dev-performance-reviewer** | Medium | Haiku assigned for performance analysis. Task requires reading AL code and identifying N+1 patterns, inefficient queries, resource leaks — complex pattern matching requiring understanding of query execution semantics. Cross-file performance reasoning needed. | Upgrade to sonnet
- **al-dev-security-reviewer** | Medium | Haiku assigned for security review. Task requires reading AL files and identifying permission issues, data exposure, input validation flaws — complex vulnerability pattern matching requiring cross-file reasoning. | Upgrade to sonnet
- **al-dev-developer** | High | Sonnet appropriately assigned for complex multi-file implementation. Keep sonnet.
- **al-dev-solution-architect** | High | Opus appropriately assigned for multi-source research and competitive design. Keep opus.
- **al-dev-docs-writer, al-dev-script-engineer, al-dev-release-notes-writer, al-dev-support-researcher** | Low | Sonnet appropriately assigned. Keep sonnet.
- **All remaining haiku agents** | Low | Haiku appropriately assigned for mechanical/single-step tasks. Keep haiku.

---

### Design Agent Lens Scope Isolation Findings

- **al-dev-commit-preflight** | Medium | Two separable concerns: (1) AL/Python source lint + trailing whitespace fixes, (2) OOXML file ZIP validation. Different domains (source quality vs. binary file integrity), different outputs (LINT_FIXES vs. OOXML_FAILURES), different expertise. | Split into `al-dev-commit-lint-fixer` (handles lint) and `al-dev-commit-ooxml-validator` (handles OOXML gate), each with single responsibility and focused error reporting.

_All other agents have single well-defined concerns._

---

### Design Agent Lens Caller Alignment Findings

- **al-dev-commit-agent-analysis** | Medium | Inputs table documents `PROJECT_CONTEXT` and `FD_TICKET` but does not specify the structured fields passed by the spawning skill (Valid scopes, Object ID prefix, AL naming pattern, Gitmoji style). | Expand Inputs table to document all structured fields.
- **al-dev-commit-message-drafter** | Medium | Inputs table does not specify the structured format for PROJECT_CONTEXT and MANIFESTS blocks. | Clarify Inputs table showing PROJECT_CONTEXT arrives as a structured block with named fields.
- **al-dev-commit-preflight** | Medium | Inputs table states `APPROVED_PLAN` arrives in dispatch prompt but does not document its GROUP_N block structure. | Add to Inputs table: "APPROVED_PLAN (structured block format: GROUP_N with files and message fields)."
- **al-dev-commit-agent-execute** | Medium | Inputs table documents APPROVED_PLAN but structure under-specified; spawning skill constructs it as GROUP_N with "files:" and "message:" fields. | Clarify Inputs: "APPROVED_PLAN arrives as inline structured blocks (GROUP_N format); no file reads required."
- **al-dev-developer** | Medium | Inputs table does not clarify which files are required vs optional for TDD vs traditional workflows. | Split Inputs section into TDD Workflow and Traditional Workflow with clear Required/Optional per path.
- **al-dev-diagnostics-fixer** | Low | Inputs table lists "AL source files (flagged paths)" as required but does not specify these are identified by parsing compile-errors.log, not passed explicitly. | Add clarification: "AL source files are identified by parsing .dev/compile-errors.log (no explicit file list passed)."
- **al-dev-solution-architect** | Low | Inputs table says requirements file found via "glob pattern match" but does not state agent uses Glob tool to locate it. | Clarify: "Agent uses Glob tool to locate requirements file if path not provided explicitly."
- **al-dev-ticket-agent** | Medium | Inputs table says credentials are "available as shell environment variable" (implying automatic injection) but the spawning skill verifies their presence and may error if missing. | Change Inputs description to: "Must be configured in harness environment settings; skill verifies presence before dispatch."
- **al-dev-support-reply-drafter** | Low | Inputs table does not clarify RESEARCHER_FINDINGS arrives as embedded text in dispatch prompt (no file read required). | Add: "RESEARCHER_FINDINGS arrives as embedded structured text block in dispatch prompt (no file read required)."
- **al-dev-interview** | Low | Inputs table does not clarify what agent does with optional file path argument vs. fresh start. | Clarify: "Optional file path for refining existing requirements; if omitted, agent creates new interview from feature description in dispatch prompt."

---

### Design Agent Lens Usage Patterns Findings

_No issues found._

All single-use agents fail the inline criteria: all have system prompt bodies exceeding 15 lines (66–152 lines) and all document Inputs/Outputs tables. No agents meet all three inline criteria.

---

### Design Skill Lens Shared Backbone Findings

- **al-dev-developer** | Medium | Both al-dev-develop and al-dev-fix spawn this agent with nearly identical prompt structures, but subtle differences in context field names and optional parameters create drift risk. | Document canonical invocation pattern in `knowledge/developer-invocation-pattern.md` with unified field names; update both skills to reference it.
- **al-dev-solution-architect** | Medium | Both al-dev-plan and al-dev-fix spawn this agent with overlapping but diverging prompt sections. Dispatch templates differ in preamble wording and field organization. | Extract canonical architect invocation template; both skills must reference single template.
- **al-dev-ticket-agent** | Low | Referenced in al-dev-ticket and al-dev-support (deprecated) via slightly different prompt structures. Verify `knowledge/ticket-agent-invocation-pattern.md` documents authoritative field order. | No new file needed; existing pattern reference may need detail verification.
- **al-dev-commit-agent-analysis, al-dev-commit-message-drafter, al-dev-commit-preflight, al-dev-commit-agent-execute** | Medium | Four agents spawned sequentially by al-dev-commit with tightly coupled prompts. No external pattern document codifies the cross-agent handoff contract. | Create `knowledge/commit-workflow-agent-invocation-pattern.md` documenting the 4-phase handoff contract with exact field names and output format expectations per phase.
- **Three-reviewer panel (expert, performance, security)** | Low | Spawned in parallel by al-dev-review-develop. Pattern is well-encapsulated within the review skill. No cross-skill reuse. | No action required.

---

### Design Skill Lens Complexity Findings

- **al-dev-review-develop** | Medium | 6 phases with two separable concerns: pre-review validation (phases 5, 8, 8.5) clusters compile/staging checks; post-review execution (phases 6-7, 9, 10) clusters review dispatch/synthesis/output. Review panel spawn cannot happen until compile passes, creating a hard barrier. | Extract pre-flight validation (phases 5, 8, 8.5) into a separate `/al-dev-review-preflight` skill; reduce main skill to review-synthesis phases only.
- **al-dev-consolidate** | Medium | 5 phases with separable concerns: discovery/extraction (phases 0-2) vs. assembly/indexing (phases 3-4). Phase 2 contains 7 distinct extraction patterns with heavy cognitive load. | Extract Phase 2 group-specific extraction logic into a reusable library or sub-skill to reduce complexity-per-read.
- **al-dev-develop** | Medium | 9 checkpoints (0–4.5 with fractional subdivisions) spanning two concerns: pre-implementation verification (0–1.5) and implementation/delivery (2–4.5). Autonomous-mode-only checkpoints (1.5, 4.5) add 2 conditional phases that distract from core workflow. | Extract Phase 1.5 (signature verification) and Phase 4.5 (static validation) into optional autonomous-mode-only sub-skills; reduce main skill to 6 core checkpoints.

---

### Design Skill Lens Near Duplicates Findings

- **al-dev-fix + al-dev-plan** | Low | Both invoke `al-dev-solution-architect` and phase counts within 2 (2-3 vs 3 phases), but they serve distinct purposes: /fix is for quick bug fixes while /plan is for full architectural design. Merging would blur the fast-track vs. thorough-design intent distinction. | No merge recommended; intentional design separation justified by user workflow expectations.

_No other near-duplicate pairs detected._

---

### Design Skill Lens Handoff Gaps Findings

- **al-dev-release-notes output (orphaned)** | Medium | `.dev/*-al-dev-release-notes-*.md` is produced by a well-established 4-skill chain but is never consumed by any downstream skill. Natural next step would be changelog aggregation, tagging, or external distribution. | Add an `al-dev-publish-release` skill that consumes release-notes artifacts and orchestrates release publishing. Currently deferred pending scope clarification.
- **al-dev-lint findings not integrated into commit workflow** | Low | `al-dev-lint` writes `.dev/*-al-dev-lint-lint-report.md` consumed by `al-dev-fix` but NOT consulted by `al-dev-commit` during pre-commit validation. | Modify `al-dev-commit` Step 5 to read the latest lint-report.md if present, surfacing unresolved items as advisory warnings before user confirms commit groups.
- **al-dev-document lacks formal upstream handoff artifact** | Low | `al-dev-document` is positioned as the post-commit docs step but has no required input from `al-dev-review-develop`. | Add a light handoff artifact from `al-dev-review-develop` that lists code-reviewed files and their documentation status; require `al-dev-document` to read it as a resume checkpoint.

---

### Design Skill Lens Preplanning Findings

- **al-dev-explore** | Low | Skill is present in diagram with dashed tributaries. However, the SKILL.md Step 3 output section does not use the exact output filename pattern `.dev/$(date +%Y-%m-%d)-al-dev-explore-findings.md` explicitly, matching the diagram handoff label. | Ensure SKILL.md Step 3 uses exact output filename pattern, matching the diagram handoff label.

_al-dev-interview and al-dev-perf are correctly documented and aligned with diagram._

---

### Quality Agent Lens Bloat Findings

- **al-dev-commit-agent-analysis** | Low | "Do not modify" instruction repeated verbatim (lines 15 and 44). | Consolidate to single warning at top; remove line 44 repetition.
- **al-dev-developer** | Medium | "Compile Output — Critical Safeguard" section (lines 90-105) is 16 lines with repetitive DO/DO NOT examples listing same command twice with pipes. | Reduce to 2-3 bullet points.
- **al-dev-docs-writer** | High | "Documentation Guidelines" section (lines 56-89) spans 34 lines with nested subsections exceeding 30-line limit for single sections. | Refactor as reference-only bullets; move detailed style guide to `knowledge/documentation-writing-style.md`.
- **al-dev-explore** | Medium | "Tool: Bash Output Capture" section (lines 47-67, 21 lines) lists 5 repetitive examples with same redirection pattern shown 3 times. | Reduce to 1-2 representative patterns; move verbose capture guidance to `knowledge/bash-output-capture.md`.
- **al-dev-solution-architect** | Medium | Lines 43-85 contain two overlapping sections on MCP tool selection. "Prefer AL LSP" statement repeated verbatim 3 times. | Consolidate MCP selection guidance into single subsection; eliminate duplicate statements.
- **al-dev-support-reply-drafter** | Low | Step 1.5 and "Tone and Framing Constraints" section both address customer perspective handling with overlapping intent. | Merge into single "Customer Reply Constraints" section.
- **al-dev-ticket-agent** | Low | Step 1.5 includes 4 regex pattern examples with patterns 1 and 4 similar enough to combine. | Reduce to 2 representative patterns.

---

### Quality Agent Lens Clarity Findings

- **al-dev-commit-agent-execute** | High | "Attempt to fix issues if scripted fix available" — undefined: which fixes are "scripted." No decision rule. | Add: "Scripted fixes are limited to: trailing whitespace (via perl), lint fixes (via al-compile --fix). All other hook failures are recorded as HOOK_FAILURE."
- **al-dev-commit-preflight** | High | Step 1 baseline procedure path `.git/.commit-baselines` is hardcoded but `.git/` may not exist or may be in a parent directory (monorepo). | Replace with explicit path: "Write baseline to `$REPO/.git/.commit-baselines`; if `.git/` does not exist, use `.dev/commit-baselines`."
- **al-dev-commit-preflight** | High | Step 1 bash script redirects from a process substitution without a proper git command wrapper — unclear if this runs in repo context or project root. | Clarify: "Baseline is captured in project root. Use `git -C <REPO> diff --cached --name-only` if running outside repo directory."
- **al-dev-commit-preflight** | Medium | Step 2 OOXML validation "Require human review before re-staging" — undefined escalation mechanism when OOXML_FAILURES occur. | Add: "If OOXML_FAILURES occur, record in return block and stop. User must resolve before re-running preflight."
- **al-dev-commit-recover-verifier** | Medium | "Fallback 2 (regex reconstruction): reconstruct from backup patterns (e.g., stored in `.dev/` analysis files)" — no specification of which backup files exist or what "patterns" means. | Clarify: "Backup patterns are extracted from `.dev/*-al-dev-plan-solution-plan.md` or `.dev/compile-errors.log`."
- **al-dev-developer** | Medium | TDD Workflow Step 3: "hard stop for user review" appears 3 times but no USER_GATE token or mechanism specified. | Replace with: "Stop and use USER_GATE to ask user."
- **al-dev-developer** | Medium | "Compile after each file or logical group" — "logical group" is vague. | Define: "Logical group = tables and their extensions, or a codeunit and its subscribers."
- **al-dev-interview** | High | "CRITICAL: Use USER_GATE for every question group. Group 2-4 related questions per call" — conflicts with "expect 40+ questions." 40+ questions = 10-20 USER_GATE calls, which is not acknowledged. | Clarify: "For complex features, expect 40+ questions across 10-15 USER_GATE calls."
- **al-dev-solution-architect** | High | Research phase has no decision rule if multiple equally-strong sources exist for analogue lookup. "Strongest available" is subjective. | Add: "Hierarchy: AL LSP (semantic correctness) > AL MCP (library knowledge) > text search (pattern matching)."
- **al-dev-solution-architect** | High | "Design testability architecture (MANDATORY)" has no gate or return-block requirement verifying inclusion. | Add return-block requirement: "TESTABILITY_COMPLETE: yes|no — if no, agent must loop back to design."
- **al-dev-solution-architect** | High | Schema Mapping Decisions table shows "unverified" as an evidence source but has no decision rule for what to do when a field is unverified. | Clarify: "If any CRITICAL field is unverified, the plan cannot proceed. Mark as blocker and escalate."
- **al-dev-support-researcher** | Medium | Step 2 Research instructions list 3 sources but no decision rule for when research is "complete enough." | Add: "Research is complete when root cause is identified in at least one source, OR when all 3 sources return no results."
- _(Multiple other medium/low clarity findings across remaining agents — see full results above)_

---

### Quality Agent Lens Description Findings

- **al-dev-commit-agent-execute** | Medium | Description does not mention "Never writes or edits source files directly — all fixes go through Bash" which is a critical capability constraint. | Add to description: "Never modifies source files directly; all fixes via Bash only."
- **al-dev-commit-preflight** | Medium | Description does not explain that the agent applies fixes via Bash; critical constraint at line 29 is absent from description. | Add to description: "Applies auto-fixes via Bash for lint issues; never uses Write or Edit on source files."
- **al-dev-ticket-agent** | Low | Description says "optionally download attachments" but body explicitly states "Attachments are referenced by URL only (not downloaded by default)." | Correct description to: "write .dev/context file with attachment references (URLs only, not downloaded)."
- **al-dev-commit-agent-analysis** | Low | Description uses "change signatures" but body uses "per-file change summary." Minor terminology variance. | Standardize terminology.

_All other agents show no description drift._

---

### Quality Agent Lens Name Fit Findings

- **al-dev-ticket-agent** | High | Name uses "agent" as a suffix for a simple API wrapper and context writer — not an autonomous agent with multi-step reasoning. Creates confusion when discussing agents as a category. | Rename to `al-dev-ticket-fetcher` or `al-dev-freshdesk-context-writer`.
- **al-dev-commit-message-drafter** | Medium | Name implies primary action is drafting messages, but agent also performs complex grouping logic (scope-based, type separation, deployable units). Grouping is arguably primary. | Rename to `al-dev-commit-grouper` or `al-dev-commit-planner` to reflect orchestration of both grouping and messaging.
- **al-dev-commit-recover-verifier** | Medium | Name uses "verifier" as the primary noun, implying verification is the main action. Body shows the agent's primary action is RECOVERY (git restore, regex reconstruction, schema rebuild). | Rename to `al-dev-commit-recover` and adjust description to emphasize recovery as primary action.
- **al-dev-diagnostics-fixer** | Medium | Name implies equal emphasis on diagnosis and fixing. Body shows primary action is applying fixes. Diagnosis is preparation. | Rename to `al-dev-lint-fixer` to clarify the specific problem domain and primary action.
- **al-dev-commit-agent-analysis** | Low | Name uses "agent" as a suffix. Performs manifest extraction from staged diffs. | Rename to `al-dev-commit-analyzer`.
- **al-dev-commit-agent-execute** | Low | Name uses "agent" as a suffix. Role is commit execution. | Rename to `al-dev-commit-executor`.
- **al-dev-code-review** | Low | Generic name not distinguishing it from specialist reviewers. Currently unavailable for automated dispatch. | Consider renaming to `al-dev-code-review-general`.
- _(Multiple other low-severity name fit findings for various agents — see full results above)_

---

### Quality Agent Lens Structure Findings

- **al-dev-commit-agent-execute, al-dev-commit-preflight, al-dev-release-notes-writer, al-dev-script-engineer, al-dev-solution-architect** | Medium | `model` field uses non-canonical short names (`sonnet`, `opus`) instead of model-version-specific identifiers. | Standardize model field to canonical convention (e.g., `claude-sonnet-4-6`, `claude-opus-4-8`).
- **al-dev-commit-message-drafter, al-dev-commit-preflight** | Medium | Contains redundant `name` field in frontmatter (filename already provides agent name). | Remove redundant `name` field.
- **al-dev-commit-recover-verifier, al-dev-support-reply-drafter, al-dev-support-researcher** | Medium | Missing `description` field in frontmatter. | Add single-sentence `description` field.
- **al-dev-code-review, al-dev-commit-agent-analysis, al-dev-commit-agent-execute, al-dev-developer, al-dev-diagnostics-fixer, al-dev-docs-writer, al-dev-expert-reviewer, al-dev-explore, al-dev-interview, al-dev-performance-reviewer, al-dev-release-notes-writer, al-dev-script-engineer, al-dev-security-reviewer, al-dev-solution-architect, al-dev-ticket-agent** | Medium | Missing `name` field in YAML frontmatter. | Add `name: <agent-name>` to frontmatter.

_Note: The agent map documents `name` as present on some agents but not others — structural inconsistency across the surface._

---

### Quality Skill Lens Bloat Findings

- **al-dev-commit** | High | Single skill contains 11 top-level steps (Step 1–11), exceeding the 8-step threshold. | Partition into "pre-flight" (Steps 1–7a) and "execute" (Steps 9–11) coordinated skills with handoff via manifest artifact.
- **al-dev-consolidate** | High | Phase 2 contains 5 major extraction sub-steps with complex orchestration bloat. | Extract extraction patterns to reusable library module; partition Phase 3 writing into focused sub-skills.
- **al-dev-develop** | High | 10 semantic phases with 5 autonomous-mode branches resulting in 8+ total step paths. Compound decision trees require factoring. | Extract autonomous validation (Phase 1.5 + 4.5) to optional sub-skill; decouple 5-attempt compile loop to utility skill.
- **al-dev-fix** | High | 9 top-level steps plus dual execution paths with Step 3 containing 9 sub-steps — nested complexity for a "lightweight" skill. | Partition trivial path into fast `al-dev-fix-trivial`; keep non-trivial path in separate `al-dev-fix-complex` routed by Step 1 classifier.
- **al-dev-plan** | High | 7 phases with Phase 1.5 introducing 3-level symbol verification gauntlet and Phase 1.6 adding target confirmation — 6 validation loops before architect dispatch. | Extract Phase 1.5 symbol verification and Phase 1.6 target confirmation to `al-dev-plan-preflight`.
- **al-dev-review-develop** | High | 10 phases in non-sequential order with Phase 8 spawning compile-fix loops up to 5 cycles. Non-linear execution makes testing and re-entry difficult. | Partition compile verification (Phase 8) to separate `al-dev-compile-verify` utility.
- **al-dev-commit** | Medium | Dead branch: Step 9's `MIXED_AL_DOCX` warning will only trigger if a specific WARNINGS block entry is present; analysis agent output format does not guarantee this entry. | Clarify contract or consolidate into a pre-commit lint rule.
- **al-dev-ticket** | Medium | Phases 5–8 form sequential branch-on-mode (context-only vs full) yet Phase 5 is labeled a decision point but includes no actual conditional logic — control flow is ambiguous. | Retitle Phase 5 as "Check Mode Flag" with explicit if/else pseudocode.
- **plan-with-critic-swarm** | Low | Lines 43–51 show pseudo-code framed as "reference" — architectural commentary belongs in a design document, not the skill body. | Remove the pseudo-code block; rely on step-by-step implementation as specification.

---

### Quality Skill Lens Clarity Findings

- **al-dev-commit** | High | Line 204: References a script path that contradicts stated plugin structure; no handling specified if script is not in expected location. | Clarify error handling: "If script is not found or returns error, continue with advisory skipped."
- **al-dev-develop** | High | SYMBOL_PREFLIGHT_GATE section references knowledge file for full checklist but also provides inline list. Precedence unspecified if they diverge. | Clarify: "Use knowledge/al-symbol-pre-flight.md as the authoritative source."
- **al-dev-document** | High | Line 79: Template path uses literal tilde `~/al-dev-shared/` — ambiguous $HOME expansion context; path does not match stated plugin root. | Use `$AL_DEV_SHARED_PLUGIN_ROOT` instead of `~`.
- **al-dev-review-develop** | High | Execution Order: "Phases run in this order: 5 → 8 → 8.5 → 6-7 → 9 → 10" — contradicts the header numbers. Very confusing. | Use consistent numbering: renumber all headers as "Step 1, Step 2, ..., Step 8" matching execution order, OR prepend "(RUN 1st)" labels to headers.
- **al-dev-fix** | High | Lines 185–187: No handling if optional .dev files exist but are incomplete or missing required sections. | Clarify: "If file exists but required section is absent, treat as 'no constraints' and proceed."
- **al-dev-plan** | High | Input Validation Gate: "Do not proceed to steps 1-4 below" — unclear if ALL steps 1-4 are skipped or only some. | Clarify: "STOP immediately at the Input Validation Gate. Do NOT proceed to Phase 1 Steps 1-4."
- **al-dev-ticket** | High | Bash command to parse --mode argument uses `${BASH_REMATCH[1]}` but context does not confirm this shell is Bash. | Add: "This skill requires Bash."
- **al-dev-verify-commits** | High | Lines 17–20: "Run `git reset --soft HEAD~<N>`" does not specify how to know which lines in the combined commit belong to which group. | Clarify: "Use the approved commit plan from prior /al-dev-commit to determine group boundaries."
- _(Multiple other medium/low clarity findings across skills — see full results above)_

---

### Quality Skill Lens Description Findings

- **al-dev-review-develop** | Medium | Description states skill "Produces Phase 4 handoff artifact" but Phase 4 handoff is an INPUT from /al-dev-develop, not an output. Actual output is the code-review artifact in Phase 9. | Correct description to: "Orchestrate multi-reviewer code review, compilation verification, and code-review output for implemented AL solutions. Consumes Phase 4 handoff from /al-dev-develop and produces synthesized code-review artifact."

_All other skills show no description drift._

---

### Quality Skill Lens Name Fit Findings

- **commit-recover** | Medium | Name suggests "recover commits" (git-level recovery), but body describes "recover corrupted AL files from commit integrity failures" — the scope is file recovery, not commit recovery. | Rename to `al-dev-file-recover` or `commit-file-recover` to match the actual file-level corruption recovery scope.

_All other skills show clear alignment between name, primary verb, and actual scope._

---

### Quality Skill Lens Structure Findings

- **al-dev-commit** | Medium | Missing concrete argument-hint examples — `argument-hint: "[optional args]"` but body does not clarify what optional arguments are accepted or how they modify behavior. | Add concrete argument examples (e.g., `--force`, `--no-verify`) and describe effects.
- **al-dev-document** | Medium | Output file naming convention unclear — references `docs/Features/[FeatureName]-[AUDIENCE].md` but skill instructions do not clarify the `docs/` vs `.dev/` boundary for persistent vs dated outputs. | Clarify whether `docs/Features/` is a persistent report output (outside `.dev/`) or should be date-prefixed.
- **al-dev-develop, al-dev-explore, al-dev-fix, al-dev-handoff, al-dev-help, al-dev-interview, al-dev-investigate, al-dev-lint, al-dev-perf, al-dev-plan, al-dev-release-notes, al-dev-review-develop, al-dev-ticket, commit-recover, verify-commits, al-dev-diagram-generator** | Low | Missing code block language tags on bash/text code fence blocks throughout these skill files. | Add `bash` or `text` language tags to all code fence blocks.
- **plan-with-critic-swarm** | Low | No numbered phases defined — uses "Steps" section but lacks Phase headers with checkpoint/resume support. | Consider adding explicit Phase numbering with checkpoint definitions.

---

### Naming Convention Lens Findings (Plugin Surface)

_Note: The naming convention lens applied .dev/ output path conventions from `docs/al-dev-naming-convention.md`. Results indicate the convention doc uses `{surface}` in dated artifact patterns, but the plugin uses `al-dev-` skill prefixes instead._

- **al-dev-developer output path** | Medium | `.dev/$(date +%Y-%m-%d)-al-dev-developer-tdd-log.md` — output path uses skill-name prefix rather than `{surface}` convention. | Verify against actual convention doc whether `al-dev-*` prefixed output paths are the intended convention for plugin surface artifacts.
- **al-dev-diagnostics-fixer output path** | Medium | `.dev/$(date +%Y-%m-%d)-al-dev-lint-lint-report.md` — uses skill-name prefix. | Verify against convention doc.
- **al-dev-explore output path** | Medium | `.dev/$(date +%Y-%m-%d)-al-dev-explore.md` — uses skill-name prefix. | Verify against convention doc.
- **al-dev-interview output path** | Medium | `.dev/$(date +%Y-%m-%d)-al-dev-interview-requirements.md` — uses skill-name prefix. | Verify against convention doc.
- **al-dev-release-notes-writer output path** | Medium | `.dev/$(date +%Y-%m-%d)-al-dev-release-notes-<VERSION>.md` — uses skill-name prefix. | Verify against convention doc.
- **al-dev-commit-recover-verifier output path** | Medium | `.dev/$(date +%Y-%m-%d)-al-dev-commit-recover-report.md` — uses skill-name prefix. | Verify against convention doc.
- **al-dev-develop skill output paths** | Medium | `.dev/$(date +%Y-%m-%d)-al-dev-develop-progress.md` and related — use skill-name prefix. | Verify against convention doc.
- **al-dev-support-reply-drafter output path** | Medium | `.dev/<date>-support-<slug>.md` — uses `<date>` instead of `YYYY-MM-DD` format. | Standardize to `YYYY-MM-DD` format.
- **al-dev-ticket-agent output path** | Medium | `.dev/<date>-al-dev-ticket-ticket-context.md` — uses `<date>` instead of `YYYY-MM-DD` format. | Standardize to `YYYY-MM-DD` format.

---

## Failed lenses

None — all 21 plugin surface lenses returned results.
