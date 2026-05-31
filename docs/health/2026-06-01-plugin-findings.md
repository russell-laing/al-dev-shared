# Plugin Health Findings — 2026-06-01

## Raw Lens Output

### Design Agent Lens: Model Fit
No issues found. All agents have appropriate model assignments relative to their task complexity.

### Design Agent Lens: Scope Isolation
- **al-dev-commit-lint-fixer** | Low | Trailing whitespace fixes and lint corrections are distinct concerns from corruption detection. Both grouped in one agent unnecessarily.
- **al-dev-support-reply-drafter** | Medium | Agent conflates two distinct concerns: (1) parsing internal research findings + extracting structured data, and (2) drafting customer-facing reply text.
- **al-dev-commit-recover-verifier** | Medium | Agent combines two separable concerns: (1) recovery strategy execution and (2) report writing and completion judgment.

### Design Agent Lens: Usage Patterns
No issues found. All single-use agents properly document their Inputs and Outputs in dedicated tables.

### Quality Agent Lens: Description Drift
- **al-dev-code-review** | Medium | Model assignment (sonnet) conflicts with agent-map suggestion to downgrade to haiku.
- **al-dev-commit-recover-verifier** | Medium | Model assignment (haiku) conflicts with agent-map suggestion to upgrade to sonnet.
- **al-dev-ticket-agent** | Medium | Description promises "download attachments" but body only implements attachment detection and context file writing.

### Quality Agent Lens: Structure
- **al-dev-code-review** | Low | Model mismatch between agent file (haiku) and agent-map documentation (sonnet).
- **al-dev-commit-agent-analysis** | Low | Missing language tags on code blocks.
- **al-dev-commit-message-drafter** | Medium | Tools field contains empty array without documented reason.
- Multiple agents | Low | Missing bash language tags on code blocks (7 agents affected).
- Multiple agents | Medium | Inconsistent use of explicit `name:` field in frontmatter.

### Quality Agent Lens: Clarity
- **al-dev-solution-architect** | High | Ambiguous interpretation of "pattern references" research task — "best existing analogue" is undefined operationally.
- **al-dev-developer-traditional** | Medium | Vague qualifier "if necessary" in governance gate enforcement.
- **al-dev-developer-tdd** | Medium | Vague qualifier "if necessary" in gate description.
- **al-dev-commit-agent-execute** | High | Incomplete conditional: missing success path definition.
- **al-dev-interview** | Medium | Ambiguous instruction: "Group 2-4 related questions per call" lacks pacing guidance.
- **al-dev-release-notes-writer** | Medium | Vague qualifier "if available" with no operative definition.
- **al-dev-commit-message-drafter** | Medium | Vague reference to "CHANGED COMPONENTS marker" — placeholder undefined.
- **al-dev-diagnostics-fixer** | Medium | Ambiguous step in "Judgment-required check" — no procedure for determining judgment requirement.
- **plan-map-changes-duck-worker** | High | Incomplete conditional branches in type-specific checks.
- **al-dev-support-reply-drafter** | Medium | Vague instruction regarding opinion validation.

### Design Skill Lens: Shared Backbone
- **al-dev-developer-tdd** | Medium | Identical spawn pattern across 2 skills without canonical reference documentation.
- **al-dev-developer-traditional** | Medium | Identical spawn pattern across 3 skills without reference to shared template.
- **al-dev-solution-architect** | Medium | Two distinct patterns (competitive debate vs. quick analysis) masked by same agent name.

### Design Skill Lens: Complexity Outliers
- **al-dev-commit** | High | 10+ numbered steps spanning 5 distinct concern phases with significant cognitive load.
- **al-dev-plan** | Medium | 7 core phases with internal subdivisions; phases cluster naturally but complexity remains high.
- **plan-with-critic-swarm** | Medium | Zero-agent, 6-step skill functionally a variant of `/al-dev-plan` that could be absorbed.

### Design Skill Lens: Handoff Gaps
- **commit → release/deploy workflow** | Medium | Well-established chain has obvious next step; gap between code commit and release documentation.
- **`.dev/commit-integrity.log` source orphaned** | Low | File read by commit-recover but no skill writes this file.

### Design Skill Lens: Near-Duplicates
- **al-dev-plan + plan-with-critic-swarm** | Medium | Both spawn 2-3 solution architect agents; phase counts within threshold; could be merged via `--with-critics` flag.

### Design Skill Lens: Pre-Planning
No issues found. All three pre-planning skills are properly documented in Layer 1 diagram.

### Quality Skill Lens: Bloat
- **al-dev-commit** | High | 11 steps exceed reasonable threshold; Step 9 contains 3 repetitive confirmation blocks.
- **al-dev-develop** | High | 9 phases exceed 8 threshold; autonomous-mode branches duplicate non-autonomous logic.
- **plan-map-changes** | High | 1800+ lines of pseudocode in Step 2B.
- **al-dev-fix** | Medium | Step 3 (non-trivial fix) spans 160+ lines with duplicate patterns.
- **al-dev-ticket** | Medium | 8 phases can be consolidated; sequential context-gathering could be single phase.
- **al-dev-plan** | Medium | Phase 2 architect dispatch repeats identical context blocks three times.

### Quality Skill Lens: Clarity
- **al-dev-commit** | High | Double-negative instruction contradicts preceding steps; condition underspecified.
- **al-dev-consolidate** | Medium | Vague: "contains a directory component" is ambiguous.
- **al-dev-develop** | High | Incomplete conditional: missing else-case action.
- **al-dev-diagram-generator** | Low | Pseudo-code uses undefined placeholder syntax.
- **al-dev-document** | Medium | Vague outcome for missing template.
- **al-dev-fix** | High | Ambiguous reference to another skill without inline explanation.
- **al-dev-handoff** | Medium | Incomplete rule: fixed filenames vs. glob patterns.
- **al-dev-help** | Low | Pseudo-code: `Glob` is not recognized binary name.
- **al-dev-interview** | High | Incomplete conditional: missing fallback if INTERVIEW COMPLETE not stated.
- **al-dev-investigate** | Medium | Vague: "2 new hypotheses" not bounded; no termination condition.
- **al-dev-lint** | Medium | Vague and contradictory: "Current-run success evidence read from" incomplete.
- **al-dev-perf** | Medium | Vague: "equal-weight analysis" undefined.
- **al-dev-plan** | High | Incomplete conditional: if user provides vague description, only one retry.
- **al-dev-release-notes** | Low | Vague qualifier "before considering the notes final".
- **al-dev-review-develop** | High | Orphaned sentence fragment duplicating routing logic.
- **al-dev-support** | Low | Vague deprecation message with no clear migration path.
- **al-dev-ticket** | High | Incomplete conditional: missing "if no" branch when user declines downloads.
- **commit-recover** | Medium | Ambiguous: unclear if skill batches incidents or spawns multiple agents.
- **plan-map-changes** | High | Incomplete conditional: no fallback for timeout or dispatch failure.
- **plan-with-critic-swarm** | Medium | Vague: no definition of "ranked", "auto-fixes", or approval gates.
- **plugin-health** | Medium | Vague: "fetches results" does not specify data source.
- **verify-commits** | Low | Vague: "match the plan" undefined.

### Quality Skill Lens: Description Drift
- **al-dev-consolidate** | Medium | Description says "Consolidates" but body lacks this verb; promises "vault-ready" but doesn't emphasize vault features.
- **al-dev-document** | Medium | Description omits mention of "RTM" (requirements traceability matrix) extensively documented in body.
- **al-dev-plan** | Medium | Description does not mention model-based complexity routing (sonnet vs opus).
- **al-dev-review-develop** | Medium | Description does not mention "compile verification" gate or autonomous error-fixing mode.
- **al-dev-support** | Medium | Body does not clearly state deprecation is complete; lacks migration guide.
- **commit-recover** | Medium | Description does not mention `.dev/learnings.md` as input file.

### Quality Skill Lens: Name Fit
- **al-dev-consolidate** | Medium | Name implies "merging/combining" but skill actually "archives and summarizes"; scope narrower than name.
- **al-dev-diagram-generator** | Medium | Name implies general diagram generation but skill only generates workflow diagrams.
- **al-dev-support** | High | Name is deprecated alias but still listed as active; actively misleads users.
- **plan-map-changes** | Medium | Verb "plan" implies design but skill actually verifies and collects suggestions.

### Quality Skill Lens: Structure
- **al-dev-commit** | Medium | Frontmatter `argument-hint` documented but body doesn't reference optional arguments.
- Multiple skills | Low | Missing bash/python language tags on code blocks (18 skills affected).
- **al-dev-develop** | Low | Inconsistent phase numbering (0, 0.5, 1, 1.5, 2, etc.).
- **al-dev-diagram-generator** | Low | Phase headings mix "Phase N" and "Sub-step".
- **al-dev-document** | Medium | Missing frontmatter `description` or truncated; references template files without documenting.
- **al-dev-interview** | Medium | Body references optional interview categories but `argument-hint` doesn't document filtering.
- **al-dev-release-notes** | Low | Output file naming uses variable placeholder inconsistent with convention.
- **al-dev-support** | Medium | Deprecated skill with outdated argument-hint; should be removed or consolidated.
- **plan-with-critic-swarm** | Medium | Body content is minimal (stub/outline); missing full Phase 1–6 steps.

---

## Failed Lenses

The following lenses hit session limits and did not return results:
- quality-agent-lens-bloat
- design-agent-lens-caller-alignment
- quality-agent-lens-name-fit
- naming-convention-lens
- design-agent-lens-tool-hygiene (partial — awaiting results)

## Resume Information

- Total lenses in scope: 21
- Completed this session: 17
- Failed/partial: 4
- Status: **INCOMPLETE** — call with `--resume` flag to complete missing lenses

