# Plugin Findings — 2026-06-01

## Raw lens output

### Design Agent Lens Tool Hygiene Findings

- **al-dev-developer-tdd** | Low | `Grep` declared in frontmatter but no grep usage described in system prompt body; workflow covers plan reading, TDD cycles, and compilation via Read/Write/Bash | Remove Grep from tools list or add explicit grep usage (e.g., symbol verification pattern matching)
- **al-dev-developer-traditional** | Low | `Grep` declared in frontmatter but no grep usage described in system prompt body; workflow covers plan reading, implementation, and compilation via Read/Write/Bash | Remove Grep from tools list or add explicit grep usage

---

### Design Agent Lens Model Fit Findings

- **al-dev-support-reply-drafter** | Medium | `sonnet` assigned for what is effectively a mechanical format transformation (parse findings block, write reply, two sections, no novel reasoning). Single-step document generation. | Downgrade to `haiku` — task is a structured rewrite with tight constraints, not synthesis or judgment
- **al-dev-code-review** | Low | `haiku` assigned for multi-file code review requiring synthesis of findings across multiple files and complex severity judgment. | Consider upgrading to `sonnet` for more accurate severity calibration; current haiku assignment was intentional (2026-06-01 remodel) so verify if finding is outdated

---

### Design Agent Lens Scope Isolation Findings

- **al-dev-commit-agent-execute** | Medium | Combines two separable concerns: (1) executing git commits with hook retry logic, and (2) handling hook failures and repair fallback. These produce different outputs (COMMITS block vs HOOK_FAILURES block) and could be diagnosed independently. | Consider extracting hook-failure retry into a dedicated `al-dev-commit-hook-fixer` agent to separate success path from error recovery path
- **al-dev-support-researcher** | Medium | Combines (1) internal technical research across AL symbols, MS Docs, and BC history, and (2) synthesis of findings into a structured block. Research and synthesis serve different cognitive purposes. | Extract synthesis into a separate `al-dev-support-findings-synthesizer` or fold synthesis logic into the reply drafter
- **al-dev-support-reply-drafter** | Medium | Combines (1) validation of researcher findings (step 1.5 tone/framing constraints) and (2) drafting the customer reply. The validation/gatekeeping layer is logically separate from draft-writing. | Separate into validator + drafter agents, or collapse validation into the researcher's synthesis step

---

### Design Agent Lens Caller Alignment Findings

- **al-dev-support-reply-drafter** | Medium | `RESEARCHER_FINDINGS` must be passed as an inline text block in the dispatch prompt — if `/al-dev-ticket` Phase 7 does not pass the full structured output from `al-dev-support-researcher`, this agent will fail to parse silently | Verify `/al-dev-ticket` Phase 7 explicitly passes the full `RESEARCHER_FINDINGS` block from the researcher as a text block in the dispatch prompt
- **al-dev-developer-tdd / al-dev-developer-traditional** | Low | Inputs table documents specific `.dev/` file paths but callers don't pass them explicitly — agents locate files via glob. Inputs table implies explicit passing. | Clarify Inputs table: "Files are auto-located via glob pattern in `.dev/`; callers do not pass explicit file paths"
- **al-dev-solution-architect** | Low | Inputs table documents "Dated requirements file via glob pattern match" but caller invocation (al-dev-plan Phase 2) does not pass file paths explicitly. Agent is responsible for file location. | Clarify Inputs: "Agent locates dated requirements via glob; caller does not pass explicit paths"

---

### Design Agent Lens Usage Patterns Findings

_No issues found._ All single-use agents have documented Inputs/Outputs sections and bodies >10 lines; none meet the 2-signal threshold for inlining.

---

### Design Skill Lens Shared Backbone Findings

- **al-dev-plan** | Low | `/al-dev-plan` Phase 2 spawns `al-dev-solution-architect` competitively but only `/al-dev-fix` Step 3 references `knowledge/architect-invocation-patterns.md`; the plan skill doesn't reference this canonical pattern doc. | Add reference to `knowledge/architect-invocation-patterns.md` in `/al-dev-plan` Phase 2 to prevent invocation drift between the two callers

---

### Design Skill Lens Complexity Findings

- **al-dev-plan** | High | 9 phases split across two separable concerns: pre-planning/context gathering (phases 0–1.6) and architect debate/synthesis (phases 2–7). Full skill re-runs all preflight even when context is cached. | Atomise: add `--resume-from=phase2` flag to skip to architect phases, or split into `al-dev-plan-preflight` + `al-dev-plan-architect`
- **al-dev-ticket** | Medium | 8 phases with a hard gate at phase 5 (mode branch). Phases 0.5–4 form a complete context-fetch workflow; phases 6–8 are optional research+reply extension. Mode=context-only is default and fully self-contained. | Consider splitting: `al-dev-ticket` (phases 0.5–4) + `al-dev-support-reply` (phases 6–8). Or add `--resume-from=phase5` flag.
- **verify-commits** | Medium | 2–3 steps, no agents spawned; logic is thin (count expected commits, compare git log, reset if mismatch). Overlaps with `/al-dev-commit` post-execution responsibilities. | Absorb into `/al-dev-commit` as a post-commit verification phase, or make it an optional `--verify` flag

---

### Design Skill Lens Near-Duplicate Shapes Findings

_No merge-worthy pairs found._ Skills with similar structure (explore-type, review-type, post-commit utilities) serve distinct enough purposes to justify separate skills.

---

### Design Skill Lens Handoff Chain Gaps Findings

- **Commit → release/deploy chain gap** | Medium | Well-established chain (`al-dev-commit` → `verify-commits` → git) has four optional post-commit outputs but none serve as a staging point for deployment or environment promotion. Release notes are a complete deliverable with no downstream skill. | Add optional `/al-dev-deploy` or `/al-dev-release-promote` skill that reads `*-al-dev-release-notes-*.md` and orchestrates deployment. Deferred pending scope clarification (see Observations in plugin map).
- **al-dev-consolidate output orphaned** | Low | `.dev/sessions/` output (sessions-index + summaries) has no downstream consumer; consolidation is a terminal utility. | Document as intentionally terminal or add note in Layer 1 diagram that consolidate is a standalone archival utility

---

### Design Skill Lens Pre-planning Findings

_No issues found._ All four pre-planning skills (al-dev-explore, al-dev-interview, al-dev-perf, plan-with-critic-swarm) appear correctly in Layer 1 as dashed tributary arrows with named outputs referenced downstream.

---

### Quality Agent Lens Bloat Findings

- **al-dev-ticket-agent** | High | "Workflow" section is 87 lines, significantly exceeds 30-line threshold | Extract inline-image detection (lines 55–68) into separate subsection; move context file template to knowledge reference
- **al-dev-commit-message-drafter** | High | "Phase: message-drafting" section is 110 lines | Extract gitmoji table and message guidelines to a knowledge reference; keep only grouping logic in agent
- **al-dev-developer-tdd** | High | "Standards" section is 51 lines | Extract "Compile Output — Critical Safeguard" block to `knowledge/compile-output-safeguard.md`; reference from both developer agents
- **al-dev-developer-traditional** | High | "Standards" section is 51 lines (identical Compile Output block to TDD agent) | Same — consolidate to `knowledge/compile-output-safeguard.md`
- **al-dev-commit-lint-fixer** | High | "Phase: lint-preflight" section is 47 lines | Split into "Line Count Capture" and "Lint & Whitespace Fixing" subsections
- **al-dev-security-reviewer** | High | "Review Focus" section is 47 lines | Extract vulnerability taxonomy to knowledge reference; keep only focus area names in agent
- **al-dev-solution-architect** | High | "Workflow" section is 40 lines | Extract Symbol Evidence hierarchy and MCP Tools table to knowledge reference
- **al-dev-diagnostics-fixer** | High | "Process" section is 39 lines | Extract judgment-required rules reference table to separate reference section
- **al-dev-commit-agent-analysis** | High | "Manifest Extraction (Steps 1–3)" is 31 lines | Extract extraction patterns into reference table; condense procedural steps
- **al-dev-interview** | High | "Interview Process" section is 38 lines | Extract question categories to knowledge reference
- **al-dev-script-engineer** | High | "Standards" section is 32 lines | Extract language-specific patterns to knowledge reference
- **al-dev-developer-tdd + al-dev-developer-traditional** | Medium | "Compile Output — Critical Safeguard" block is identical in both agents | Consolidate to single `knowledge/compile-output-safeguard.md` and reference from both

---

### Quality Agent Lens Clarity Findings

- **al-dev-ticket-agent** | High | "Detect Inline Image Attachments" specifies regex patterns but does not define what tool/language to use (bash grep, Python, or manual parsing) | Specify: "Use bash `grep -oE` to extract `src="[^"]+"` from HTML, filter for `cdn.freshdesk.com` or `cid:` patterns"
- **al-dev-interview** | High | "INTERVIEW COMPLETE" gate requires explicit statement but does not define a terminal failure condition if signal is never received | Add: "After 2 retry rounds, if agent has not covered all 11 categories explicitly, escalate to user with list of missing categories"
- **al-dev-solution-architect** | High | Schema mapping decision table requires UNVERIFIED symbols to be marked BLOCKED but does not define what constitutes "verification" | Clarify: "VERIFIED = found via AL LSP, AL MCP, or exact text search with file:line. UNVERIFIED = no evidence provided"
- **al-dev-commit-agent-analysis** | High | Extraction patterns use vague logic "procedure names on both `-` and `+` lines" without specifying how to distinguish added vs modified | Define: "procs_modified = names in both `-` and `+` hunks; procs_added = `+` only; procs_removed = `-` only"
- **al-dev-commit-lint-fixer** | High | "Regex MUST be `[ \t]+$`" warns against `\s+$` collapsing files but doesn't explain when this risk applies | Clarify: "Never use `\s` in sed regex; use only `[ \t]` for portable POSIX regex"
- **al-dev-commit-agent-analysis** | Medium | Multiple bash code blocks use unterminated fenced markers (`text` instead of `bash`) | Close all code blocks with correct language tags
- **al-dev-commit-recover-verifier** | Medium | "Fallback 2 (regex reconstruction)" and "Fallback 3 (schema rebuild)" described vaguely with no concrete patterns | Specify regex patterns to search for backup data; define schema metadata format
- **al-dev-developer-tdd / al-dev-developer-traditional** | Medium | Compilation safeguard references "4.7MB+ log" as a fixed size — context window overhead varies | Rephrase: "Piping forces buffering of entire output into session context. Use `--output` flag and read file afterward"
- **al-dev-diagnostics-fixer** | Medium | "Scripted fix" vs "direct edit" classification uses "3+ occurrences"/"1-2 occurrences" thresholds without defining what varies | Define: "Scripted = Edit tool with loop or regex for all instances; direct = Edit tool called once per instance"
- **al-dev-interview** | Medium | "Ask deep, probing questions (40+ typical)" uses vague qualifier "typical" with no scaling criteria | Clarify: "40+ for COMPLEX features, 25–35 for MEDIUM, 10–15 for SIMPLE"
- **al-dev-support-reply-drafter** | Medium | "Critical reading" step (line 41) instructs independent assessment but source for this is undefined | Clarify: "If findings don't directly address capability, flag as: 'Open question for escalation: [capability not confirmed in research]'"
- Unclosed code blocks in: al-dev-commit-agent-execute, al-dev-commit-lint-fixer, al-dev-commit-message-drafter, al-dev-commit-ooxml-validator, al-dev-expert-reviewer, al-dev-performance-reviewer, al-dev-security-reviewer, al-dev-support-researcher | Low | Multiple agents have unterminated fenced markers using `text` instead of `bash`/`markdown` | Use appropriate language tags on all code blocks

---

### Quality Agent Lens Description Findings

- **al-dev-diagnostics-fixer** | Medium | Description states "applies auto-fixes" but body explicitly documents judgment-required rules NOT auto-fixed as core output | Add: "...identifies judgment-required rules (AS0016, AS0013, etc.), auto-fixes others, documents both in lint report"
- **al-dev-interview** | Medium | Description omits the INTERVIEW_COMPLETE signal requirement and mandatory 7–11 category coverage gate | Add: "Agent enforces INTERVIEW_COMPLETE signal and must cover all 11 categories before output is accepted"
- **al-dev-solution-architect** | Medium | Description omits that testability architecture is mandatory and solution plan requires structured acceptance criteria | Add: "Testability architecture design is mandatory; plan must include structured RTM acceptance criteria"
- **al-dev-commit-recover-verifier** | Medium | Description names three fallback strategies but body only documents git restore in detail | Expand implementation section to detail all three fallback strategies
- **al-dev-support-reply-drafter** | Medium | Description omits independent assessment of customer claims and Microsoft source citation requirements | Clarify: "Agent independently validates customer claims against technical findings and cites authoritative Microsoft sources"
- **al-dev-ticket-agent** | Medium | Description omits inline image detection step (scanning for `src=` and `cid:` references in HTML) | Add: "Also detects and logs inline embedded images extracted from HTML src= and cid: references"
- **al-dev-commit-lint-fixer** | Medium | Description names "Python lint (ruff)" and "trailing whitespace" but omits critical line-count corruption detection | Add explicit mention of line-count baseline capture and corruption detection
- (10 low-severity description drift issues across remaining agents — minor verb mismatches, missing reference to knowledge files)

---

### Quality Agent Lens Name Fit Findings

- **al-dev-commit-recover-verifier** | High | Name says "verifier" but primary verb is recover/fix (applies recovery strategies, never passively verifies) | Rename to `al-dev-commit-recover-fixer` or `al-dev-commit-recover-agent` to reflect active recovery
- **al-dev-commit-agent-analysis** | Medium | Name says "agent-analysis" (generic) but actual scope is narrowly parsing staged git diffs into per-file manifests | Rename to `al-dev-commit-manifest-analyzer` to reflect true scope
- **al-dev-ticket-agent** | Medium | Name is overly generic ("agent" provides no scope information); actual scope is fetching Freshdesk tickets and writing context files | Rename to `al-dev-ticket-fetcher` or `al-dev-ticket-context-writer`
- (18 low-severity findings — all lens agents and other agents have appropriate names with no action needed)

---

### Quality Agent Lens Structure Findings

All 22 agents have correct frontmatter fields (name, description, model, tools) and Inputs/Outputs tables. All issues are low severity:
- Missing code block language tags (`text` instead of `bash`/`markdown`) in: al-dev-code-review, al-dev-commit-agent-analysis, al-dev-commit-agent-execute, al-dev-commit-lint-fixer, al-dev-commit-message-drafter, al-dev-commit-ooxml-validator, al-dev-commit-recover-verifier, al-dev-developer-tdd, al-dev-developer-traditional, al-dev-diagnostics-fixer, al-dev-docs-writer, al-dev-expert-reviewer, al-dev-explore, al-dev-interview, al-dev-performance-reviewer, al-dev-release-notes-writer, al-dev-script-engineer, al-dev-security-reviewer, al-dev-solution-architect, al-dev-support-reply-drafter, al-dev-support-researcher, al-dev-ticket-agent | Low | Use `bash` for shell commands and `markdown` for text examples throughout

---

### Quality Skill Lens Bloat Findings

- **al-dev-commit** | High | Phase 0 contains 7 numbered sub-steps totalling 160+ lines; repetitive compile-gate instructions appear in multiple sections | Consolidate Phase 0 sub-steps; extract compile-gate to reusable knowledge reference
- **al-dev-consolidate** | High | Phase 2 (Extract Per Session) is 74 lines with bash patterns repeated across groups A–D with minor parameter variations | Extract common patterns to `knowledge/consolidate-extraction-patterns.md`; use single parameterized step
- **al-dev-develop** | High | Phase 1 signature verification spans 58 lines; Phase 4 validation adds 70+ lines with repeated verification patterns | Extract signature verification and static validation checks to dedicated knowledge files
- **al-dev-fix** | High | Step 3 alone is 100+ lines; artifact-contract and compile-lint references duplicated across trivial and non-trivial paths | Extract complexity classification rules to `knowledge/fix-complexity-classifier.md`
- **al-dev-plan** | High | Phase 1 (Gather Context) is 50+ lines; Phase 1.5 (Verify External Claims) adds 38 lines repeating symbol verification already present in other skills | Extract input validation and external claims verification to reusable patterns in `knowledge/`
- **al-dev-review-develop** | Medium | Phase 2 and Phase 4 both include extensive agent dispatch templates with identical header structure; Phase 5 repeats artifact-contracts.md contract | Extract review-panel dispatch template to knowledge file
- **al-dev-ticket** | Medium | Steps 1–2 include 15-line auto-detection and 20-line search blocks that could be unified; credential verification repeated | Consolidate ticket resolution and context loading into single "Resolve & Load" step
- **al-dev-document** | Medium | Step 0 and Step 2 both include identical documentation structure outline (22 lines); RTM instructions appear twice | Extract documentation structure to external template file; reference once from both steps
- **al-dev-perf** | Medium | Step 1a (40+ lines) and Step 2 agent prompt both describe performance entry-point classification with overlap | Extract to `knowledge/perf-anti-patterns-prompt.md` reference; simplify agent prompt
- **plan-map-changes** | Medium | Phase 1, 2, 3 each define the same validation/check pattern (35+ lines); Phase 3 polling logic duplicates Phase 2 conditionals | Extract universal checks to knowledge file
- **plugin-health** | Medium | Phase 1 and Phase 3 (resume path) both include identical checkpoint loading and status-checking patterns (30+ lines) | Consolidate checkpoint logic to single knowledge file

---

### Quality Skill Lens Clarity Findings

- **al-dev-plan** | High | Phase 1 incomplete conditional: "STOP immediately" if vague input, with retry logic but no terminal condition | Add: "Terminal: After second vague response, escalate with decision: (1) provide specific context, (2) run /interview first, or (3) cancel"
- **al-dev-fix** | High | Incomplete conditional: Step 2 "spawn al-dev-developer-traditional (trivial fixes have no test plan)" contradicts Step 3 which says "check for a test plan" for non-trivial fixes | Clarify: "TRIVIAL: skip test plan check; always use traditional. NON-TRIVIAL: check test plan; dispatch TDD if present"
- **al-dev-interview** | High | "Fallback if INTERVIEW COMPLETE is NOT received" provides retry but no terminal failure condition | Add terminal condition after 2 retry rounds
- **al-dev-commit** | High | "If `$AL_STAGED` is non-empty, run compile gate" lacks `else` clause for non-AL staged changes | Add: "If `$AL_STAGED` is empty, skip compile gate and proceed to Phase 1"
- **plan-map-changes** | High | Phase 2 decision tree lacks failure handling for both inline and remote paths | Add: "If inline verification fails: write error record, offer user (skip / retry / abort). If remote dispatch fails: offer (inline verify / abort)"
- (15+ medium-severity issues: vague qualifiers like "representative diagnostics", "minimal", "multiple", "high-volume"; ambiguous mode case-sensitivity; missing else clauses across al-dev-consolidate, al-dev-develop, al-dev-perf, al-dev-ticket, al-dev-release-notes, verify-commits, commit-recover)

---

### Quality Skill Lens Description Findings

- **al-dev-fix** | Medium | Description promises "lightweight bug fix workflow without approval gates" but body describes complex multi-phase scope including architect dispatch for non-trivial fixes | Clarify dual-path nature: "trivial fixes are lightweight; non-trivial fixes escalate to quick architect analysis"
- **al-dev-ticket** | Medium | "optionally research" in description is misleading — attachment download is a conditional gate, not a true optional, and `--mode=full` controls research | Clarify that attachment download is conditional and `--mode=full` controls research
- (20 low-severity description drift issues — minor mismatches, missing reference to knowledge files, incomplete output descriptions)

---

### Quality Skill Lens Name Fit Findings

- **plan-map-changes** | High | Name implies "create a plan for map changes" but primary behavior is rubber-duck verification of existing suggestions; triggers include "implement" but skill only plans | Rename to `al-dev-map-suggestions-verify` or `al-dev-map-observation-verify` to match primary verb (verify)
- **plan-with-critic-swarm** | High | Name leads with "plan" but primary behavior is red-teaming an existing plan; skill critiques, not creates; triggers say "generate plan then defend it" | Rename to `al-dev-plan-critic-review` or `al-dev-plan-swarm-validate` to signal review as primary verb
- **al-dev-diagram-generator** | Medium | Name implies user-facing diagram creation but skill is dispatched exclusively by `/analyze-agent-design` and `/analyze-skill-design`; not a standalone entry point | Clarify as internal tool or rename to signal internal dispatch context
- **commit-recover** | Medium | Name suggests active recovery but execution is inspection-first; recovery only on `--auto-fix` flag | Rename to `al-dev-commit-integrity-verify` or clarify `--auto-fix` requirement in description
- **al-dev-fix** | Medium | Name implies lightweight fix but body has complex dual-path routing including architect dispatch | Clarify complexity routing in description prefix
- **al-dev-consolidate** | Low | "Consolidate" is incidental to primary purpose of building session summaries and vault-ready indexes | Consider "al-dev-session-summary" or update description to lead with "aggregate and summarize"

---

### Quality Skill Lens Structure Findings

- **al-dev-fix** | High | Two consecutive stray `# test` headers at end of file (lines 444–445) appear to be debugging artifacts | Remove lines 444–445 immediately
- **al-dev-explore** | Low | `argument-hint: ""` (empty string) but body references argument `[question or area to explore]` | Correct to `argument-hint: "[question or area to explore]"`
- All 22 skills have missing code block language tags (using `text`, `yaml`, `markdown` where `bash`, `al` would be appropriate) | Low | Widespread code block language tag inconsistency throughout all skill files | Audit all code blocks and apply correct language specifiers

---

## Failed lenses

None — all 20 lenses returned results.

## Resume information

- Total lenses in scope: 20 (plugin surface: 10 design + 10 quality)
- Completed this session: 20
- Status: COMPLETE
