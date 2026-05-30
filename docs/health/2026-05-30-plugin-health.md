# Plugin Health — 2026-05-30

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 1      | 23      | 0      | 24    |
| Medium   | 14     | 35      | 9      | 58    |
| Low      | 9      | 35      | 0      | 44    |

Lenses: 21 run · 0 failed.

**Top 5 ranked actions:**

1. **Skill bloat (High)** — Six major skills exceed the 8-step complexity threshold: `al-dev-commit` (11 steps), `al-dev-develop` (9 checkpoints), `al-dev-review-develop` (10 non-sequential phases), `al-dev-fix` (dual-path with nested steps), `al-dev-plan` (6 validation gates pre-dispatch), `al-dev-consolidate` (5 phases with 7 extraction patterns). Reducing bloat reduces per-invocation context overhead. Suggested moves are already individually described in Design and Quality sections below.

2. **Clarity blockers in core skills (High)** — `al-dev-develop` has 3 High-severity clarity gaps affecting every invocation: symbol preflight precedence undefined, "5-attempt loop" ambiguity, and "bounded scope" undefined. `al-dev-solution-architect` has 3: no research source hierarchy, missing mandatory testability return-block gate, no decision rule for unverified fields. Fix these to prevent divergent developer behavior on every plan/develop cycle.

3. **Downgrade `al-dev-commit-agent-execute` (High, Design)** — Currently sonnet; its task is sequential bash calls with simple pass/fail retry logic. No multi-step reasoning required. Downgrading to haiku is a direct cost reduction with no capability loss.

4. **Split `al-dev-commit-preflight` (Medium, Design)** — Two separable concerns: AL/Python source lint + trailing whitespace fixes vs. OOXML ZIP validation. Different domains, different outputs (`LINT_FIXES` vs `OOXML_FAILURES`), different expertise. The split also resolves 2 High-severity clarity issues that stem from the dual-concern design.

5. **Upgrade three review specialists (Medium, Design)** — `al-dev-expert-reviewer`, `al-dev-performance-reviewer`, `al-dev-security-reviewer` are all assigned haiku but perform cross-file reasoning, design-level judgment, and vulnerability pattern matching. All three warrant sonnet.

---

## Design suggestions

### Agent design

**Remodel — al-dev-commit-agent-execute: haiku** | sonnet assigned for commit execution, but the task is sequential bash calls (git commit, retry on hook failure, parse hook output). No multi-step reasoning or cross-system synthesis required. | Downgrade to haiku.

**Remodel — al-dev-code-review: sonnet** | haiku assigned for general code review spanning logic errors, security issues, and pattern analysis across multiple files. Requires cross-file synthesis and design-level judgment. | Upgrade to sonnet.

**Remodel — al-dev-commit-preflight: haiku** | sonnet assigned for pre-flight validation. Task is mechanical: run linters, check line counts, validate ZIP files. Sequential steps with simple pass/fail gates. | Downgrade to haiku.

**Remodel — al-dev-commit-message-drafter: sonnet** | haiku assigned for drafting commit messages. Task requires grouping files into deployable units, understanding compile-time dependencies, and synthesizing atomic commit rationale. Multi-file reasoning needed. | Upgrade to sonnet.

**Remodel — al-dev-expert-reviewer, al-dev-performance-reviewer, al-dev-security-reviewer: sonnet** | All three assigned haiku. All perform cross-file pattern analysis requiring design-level judgment (BC patterns, query execution semantics, vulnerability reasoning). | Upgrade all three to sonnet.

**Split — al-dev-commit-preflight** | Two separable concerns: (1) AL/Python source lint and trailing whitespace fixes; (2) OOXML ZIP validation. Different domains (source quality vs. binary file integrity), different outputs, different failure modes. | Split into `al-dev-commit-lint-fixer` and `al-dev-commit-ooxml-validator`.

**Align — al-dev-commit-agent-analysis** | Inputs table documents `PROJECT_CONTEXT` and `FD_TICKET` but does not specify the structured fields passed by the spawning skill (Valid scopes, Object ID prefix, AL naming pattern, Gitmoji style). | Expand Inputs table to document all structured fields.

**Align — al-dev-developer** | Inputs table does not clarify which files are required vs optional for TDD vs traditional workflows. | Split Inputs section into TDD Workflow and Traditional Workflow with clear Required/Optional per path.

**Align — al-dev-ticket-agent** | Inputs table says credentials are "available as shell environment variable" (implying automatic injection) but the spawning skill verifies presence and may error if missing. | Change Inputs description to: "Must be configured in harness environment settings; skill verifies presence before dispatch."

### Skill design

**Connect — al-dev-developer invocation pattern** | Both `al-dev-develop` and `al-dev-fix` spawn the developer agent with nearly identical prompt structures but subtle differences in context field names and optional parameters that create drift risk. | Document canonical invocation pattern in `knowledge/developer-invocation-pattern.md` with unified field names; both skills reference it.

**Connect — commit workflow handoff contract** | Four commit pipeline agents (`al-dev-commit-agent-analysis`, `al-dev-commit-message-drafter`, `al-dev-commit-preflight`, `al-dev-commit-agent-execute`) are spawned sequentially with tightly coupled prompts but no external pattern document codifies the cross-agent handoff contract. | Create `knowledge/commit-workflow-agent-invocation-pattern.md` documenting the 4-phase handoff contract with exact field names and output format expectations per phase.

**Atomise — al-dev-review-develop** | 6 phases with two separable concerns: pre-review validation (phases 5, 8, 8.5 — compile/staging checks) vs. post-review execution (phases 6-7, 9, 10 — review dispatch/synthesis/output). Review panel spawn cannot happen until compile passes, creating a hard sequential gate between the two concerns. | Extract pre-flight validation into a separate `/al-dev-review-preflight` skill; reduce main skill to review-synthesis phases only.

**Atomise — al-dev-develop** | 9 checkpoints (phases 0-4.5 with fractional subdivisions) spanning pre-implementation verification (0-1.5) and implementation/delivery (2-4.5). Autonomous-mode-only checkpoints (1.5, 4.5) distract from the core workflow when not in autonomous mode. | Extract Phase 1.5 (signature verification) and Phase 4.5 (static validation) into optional autonomous-mode-only sub-skills; reduce main skill to 6 core checkpoints.

**Extend — al-dev-release-notes (orphaned output)** | `al-dev-release-notes` produces a dated artifact but no downstream skill consumes it. Natural next step is changelog aggregation, release tagging, or external distribution. | Add a post-release orchestration skill (deferred pending scope clarification per existing `knowledge/publish-workflow-opportunity.md`).

---

## Quality findings

### Agent quality

**al-dev-docs-writer** | High | Bloat: "Documentation Guidelines" section (lines 56-89, 34 lines) exceeds 30-line section limit with 6 nested subsections. | Refactor as reference-only bullets; move style guide to `knowledge/documentation-writing-style.md`.

**al-dev-solution-architect** | High | Clarity: Three gaps affecting every /al-dev-plan invocation — (1) no research source hierarchy rule ("AL LSP > AL MCP > text search" stated elsewhere but not as a decision gate), (2) "Design testability architecture (MANDATORY)" has no return-block gate verifying inclusion, (3) `unverified` field in Schema Mapping table has no decision rule (block or proceed?). | Add decision gates for all three; add `TESTABILITY_COMPLETE: yes|no` to return block.

**al-dev-commit-agent-execute** | High | Clarity: "Attempt to fix issues if scripted fix available" — which fixes are "scripted" is undefined. No decision rule. | Add: "Scripted fixes limited to: trailing whitespace (perl), lint fixes (al-compile --fix). All other hook failures recorded as HOOK_FAILURE."

**al-dev-commit-preflight** | High | Clarity (×2): (1) `.git/.commit-baselines` path hardcoded — monorepo `.git/` may be in parent directory; (2) bash script context unclear — does it run in repo context or project root. | Replace with: "Write baseline to `$REPO/.git/.commit-baselines`; use `git -C <REPO> diff --cached --name-only`."

**al-dev-interview** | High | Clarity: "CRITICAL: Use USER_GATE for every question group" conflicts with "expect 40+ questions." 40+ questions across 2-4 per call = 10-20 USER_GATE calls — but this is unacknowledged. | Clarify: "For complex features, expect 40+ questions across 10-15 USER_GATE calls."

**al-dev-ticket-agent** | High | Name fit: Name uses "agent" as a suffix for a simple API wrapper and context writer. Creates confusion when discussing agents as a category. | Rename to `al-dev-ticket-fetcher` or `al-dev-freshdesk-context-writer`.

**al-dev-explore** | Medium | Bloat: "Tool: Bash Output Capture" section (lines 47-67, 21 lines) shows the same redirection pattern 3 times across 5 examples. | Reduce to 1-2 representative patterns; move verbose guidance to `knowledge/bash-output-capture.md`.

**al-dev-developer** | Medium | Bloat: "Compile Output — Critical Safeguard" section (lines 90-105, 16 lines) has repetitive DO/DO NOT examples listing same command twice. | Reduce to 2-3 bullet points.

**al-dev-solution-architect** | Medium | Bloat: Lines 43-85 contain two overlapping sections on MCP tool selection. "Prefer AL LSP" statement repeated verbatim 3 times. | Consolidate MCP selection guidance into single subsection.

**al-dev-commit-agent-execute** | Medium | Description: Does not mention "Never writes or edits source files directly — all fixes go through Bash" — a critical capability constraint. | Add to description.

**al-dev-commit-preflight** | Medium | Description: Does not explain that the agent applies fixes via Bash (not Write/Edit on source files). | Add to description.

**al-dev-commit-message-drafter** | Medium | Name fit: Name implies drafting messages, but the grouping logic (scope-based, type separation, deployable units) is complex and arguably the primary concern. | Consider renaming to `al-dev-commit-grouper` or `al-dev-commit-planner`.

**al-dev-commit-recover-verifier** | Medium | Name fit: Name uses "verifier" as primary noun, but the primary action is recovery (git restore, regex reconstruction, schema rebuild). | Rename to `al-dev-commit-recover`.

**al-dev-diagnostics-fixer** | Medium | Name fit: Name implies equal emphasis on diagnosis and fixing; body shows primary action is applying fixes. Diagnosis is preparation. | Rename to `al-dev-lint-fixer`.

**al-dev-* (multiple)** | Medium | Structure: 15 agents missing `name` field in frontmatter; 5 agents using non-canonical model short names (`sonnet`, `opus`); 3 agents with missing `description` field. | Add missing frontmatter fields across all affected agents; standardize model identifiers.

### Skill quality

**al-dev-commit, al-dev-consolidate, al-dev-develop, al-dev-fix, al-dev-plan, al-dev-review-develop** | High | Bloat: All six skills exceed the 8-step complexity threshold. `al-dev-commit` has 11 top-level steps, `al-dev-develop` has 9 checkpoints, `al-dev-review-develop` runs 10 non-sequential phases with a compile-fix loop. | See Design section for specific Atomise/Split suggestions per skill.

**al-dev-review-develop** | High | Clarity: Phase execution order (5 → 8 → 8.5 → 6-7 → 9 → 10) contradicts header numbers. Very confusing for any skill reader or agent. | Renumber all headers sequentially as "Step 1, Step 2, ..." matching execution order.

**al-dev-develop** | High | Clarity: SYMBOL_PREFLIGHT_GATE section references knowledge file for full checklist AND provides inline list — precedence unspecified if they diverge. | Clarify: "Use `knowledge/al-symbol-pre-flight.md` as the authoritative source. Inline list is a summary only."

**al-dev-plan** | High | Clarity: Input Validation Gate says "Do not proceed to steps 1-4 below" — unclear if ALL steps 1-4 are skipped or only some. | Clarify: "STOP immediately at the Input Validation Gate. Do NOT proceed to Phase 1 Steps 1-4."

**al-dev-document** | High | Clarity: Line 79 uses literal tilde `~/al-dev-shared/` — ambiguous `$HOME` expansion context. | Use `$AL_DEV_SHARED_PLUGIN_ROOT` instead of `~`.

**al-dev-fix** | High | Clarity: Lines 185-187 — no handling specified if optional `.dev` files exist but are incomplete or missing required sections. | Clarify: "If file exists but required section is absent, treat as 'no constraints' and proceed."

**al-dev-ticket** | High | Clarity: `${BASH_REMATCH[1]}` usage assumes Bash shell but context does not confirm this. | Add: "This skill requires Bash."

**verify-commits** | High | Clarity: Lines 17-20 — "Run `git reset --soft HEAD~<N>` to unstage; Re-commit each group" does not specify how to know which lines in the combined commit belong to which group. | Clarify: "Use the approved commit plan from prior /al-dev-commit to determine group boundaries."

**al-dev-review-develop** | Medium | Description drift: Description states skill "Produces Phase 4 handoff artifact" but Phase 4 handoff is an INPUT from /al-dev-develop. Actual output is the code-review artifact written in Phase 9. | Correct description to: "Consumes Phase 4 handoff from /al-dev-develop and produces synthesized code-review artifact."

**commit-recover** | Medium | Name fit: Name suggests "recover commits" (git-level) but body describes "recover corrupted AL files from commit integrity failures" — file recovery, not commit recovery. | Rename to `commit-file-recover` or `al-dev-file-recover`.

**al-dev-commit** | Medium | Structure: `argument-hint: "[optional args]"` present but no concrete examples. Body does not clarify what optional arguments are accepted. | Add concrete argument examples and describe their effects.

**al-dev-commit** | Medium | Bloat dead branch: Step 9's `MIXED_AL_DOCX` warning only triggers if analysis agent produces a specific WARNINGS block entry — format not guaranteed. | Clarify contract or consolidate into a pre-commit lint rule.

**al-dev-* (most skills)** | Low | Structure: Missing code block language tags on bash/text code fence blocks throughout the skill surface. | Add `bash` or `text` language tags to all code fence blocks.

---

## Naming violations

**Output path format: `al-dev-support-reply-drafter`, `al-dev-ticket-agent`** | Medium | Output paths use `<date>` instead of `YYYY-MM-DD` format. All dated artifacts should use the literal `YYYY-MM-DD` pattern so harnesses can resolve them consistently. | Change: `.dev/<date>-support-<slug>.md` → `.dev/YYYY-MM-DD-al-dev-support-<slug>.md`; `.dev/<date>-al-dev-ticket-ticket-context.md` → `.dev/YYYY-MM-DD-al-dev-ticket-ticket-context.md`.

**Output path prefix pattern** | Medium | Multiple agents and skills use `al-dev-` as a skill-name prefix in dated output filenames (e.g., `.dev/$(date +%Y-%m-%d)-al-dev-developer-tdd-log.md`, `.dev/$(date +%Y-%m-%d)-al-dev-explore.md`, etc.). Verify against `docs/al-dev-naming-convention.md` whether this is the intended convention or whether the `{surface}` placeholder (`plugin`/`tooling`) should be used instead. | Cross-check all dated output paths against the naming convention doc. If `al-dev-*` prefix is the accepted convention for plugin surface artifacts, document it explicitly.

---

## Graph deltas

**Orphaned chain: `al-dev-release-notes`** | Established 4-skill chain (`al-dev-investigate/plan/develop/commit` → `al-dev-release-notes`) terminates without a downstream consumer. The `.dev/*-al-dev-release-notes-*.md` artifact is never read by any other skill. | Deferred to future `/al-dev-publish` skill per `knowledge/publish-workflow-opportunity.md`.

**Missing feedback arc: `al-dev-lint` → `al-dev-commit`** | The lint report artifact (`.dev/*-al-dev-lint-lint-report.md`) feeds `al-dev-fix` but is not consulted by `al-dev-commit` pre-commit validation. The graph shows a disconnection between the lint advisory output and the commit gate. | Modify `al-dev-commit` Step 5 to read the latest lint report and surface unresolved items as advisory warnings.
