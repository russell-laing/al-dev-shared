# Plugin Health — 2026-05-29

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 0      | 16      | 0      | 16    |
| Medium   | 0      | 36      | 0      | 36    |
| Low      | 0      | 26      | 0      | 26    |

Design lenses not dispatched in this run (`--dimension quality` used for first sweep).
Naming: `lens naming-convention-lens: no result` — agent not yet registered in harness (pending plugin install after merge).

Top 5 ranked actions:
1. **al-dev-commit-agent-execute** (agent/quality/clarity/High) — vague "scripted fix" criteria in hook failure handling; define which failures can be auto-fixed vs. escalated
2. **al-dev-commit-preflight** (agent/quality/clarity/High) — baseline file path written to `.git/.commit-baselines` but never referenced in restoration logic; clarify read-back path
3. **al-dev-developer** (agent/quality/clarity/High) — "hard stop" gate semantics undefined; clarify that agent must wait for explicit user approval before proceeding
4. **al-dev-solution-architect** (agent/quality/clarity/High) — acceptance criteria types (structural/gate/pattern/manual) listed but not defined with examples
5. **al-dev-commit-recover-verifier** (agent/quality/structure/High) — missing required `description` field in frontmatter

## Design suggestions

_No design lenses dispatched in this run. Re-run with `--dimension design` or `--dimension all` to generate Atomise / Merge / Trim / Split / Align suggestions._

## Quality findings

### Agents — Clarity (quality-lens-clarity)

- **al-dev-commit-agent-execute** | High | "Attempt to fix issues if scripted fix available" — no criteria for what constitutes a scripted fix or when to auto-apply | Define: lint/trailing-whitespace fixes are auto-applicable; permission errors and merge conflicts must be escalated
- **al-dev-commit-preflight** | High | Baseline capture writes to `.git/.commit-baselines` but restoration step (Step 4) never references this path | Clarify file path and show read-back command in Step 4
- **al-dev-developer** | High | "Hard stop for user review" gate semantics not defined — unclear whether agent must wait or can proceed | Clarify: hard stop requires explicit user approval via the harness before next phase begins
- **al-dev-solution-architect** | High | Acceptance criteria types (structural, gate, pattern, [manual]) listed but never defined with examples | Add: structural = "file exists"; gate = USER_APPROVAL_GATE; pattern = "follows al-developer-patterns.md"; [manual] = human judgment required
- **al-dev-commit-agent-analysis** | Medium | "Pair" undefined when describing modified procedures across `-`/`+` diff lines | Clarify: a procedure is modified if it appears on both a `-` and a `+` line in the diff
- **al-dev-commit-message-drafter** | Medium | "Deployable atomic commit unit" used but never formally defined | Add: a deployable unit is one that can be applied to a BC environment in isolation without breaking system consistency
- **al-dev-commit-recover-verifier** | Medium | Fallback 1/2/3 ordering conditions vague — when to use fallback 2 vs. 1 is undefined | Specify order: try git restore first; if fail and file is .al, try regex reconstruction; if fail, try schema rebuild
- **al-dev-developer** | Medium | (additional) "Completion" of TDD workflow undefined — whether "hard stop" gates block transition is unclear (duplicate High finding; applies to gate semantics throughout)
- **al-dev-diagnostics-fixer** | Medium | "Mark unresolved" has no operational definition for judgment-required checks | Define: document in lint report under "Unresolved Issues" with "requires human judgment" label; fixer does not attempt fix
- **al-dev-docs-writer** | Medium | RTM handling rules referenced but not included inline; agent should state the guide file is authoritative | Add explicit statement referencing `knowledge/documentation-rtm-guide.md` as source of truth
- **al-dev-explore** | Medium | "Never let compiler output flow to session stdout" — no threshold defined for acceptable output volume | Add: limit unredirected output to <100 lines; use file redirection for longer output
- **al-dev-interview** | Medium | "Group 2-4 related questions per call" — "related" not defined | Clarify: group by category (data model, security, etc.) or by logical dependency
- **al-dev-release-notes-writer** | Medium | "Get object definitions" action lacks concrete MCP function name | Specify: use `al_get_object_definition` from the AL MCP Server
- **al-dev-script-engineer** | Medium | Dynamic discovery using `find ~ -name...` has no timeout or depth limit | Add: use `-maxdepth 5`; skip if discovery exceeds 5 seconds
- **al-dev-support-reply-drafter** | Medium | "Subjective opinion" vs. "legitimate issue" distinction not defined | Add examples: subjective = "not suitable"; legitimate = "Feature X returns error Y"; when in doubt, treat as legitimate
- **al-dev-support-researcher** | Medium | No conflict-resolution rule when 3 MCP sources disagree | Add: note both findings, label which is authoritative, document uncertainty
- **al-dev-ticket-agent** | Medium | `cid:` inline image pattern assumed from Freshdesk docs but not verified | Add fallback: if `cid:` pattern fails, list all `src=` URLs from HTML
- **al-dev-code-review** | Low | Output Format section shows markdown block but provides no concrete example entry | Add a sample finding entry to the Output Format section
- **al-dev-expert-reviewer** | Low | Dispatch format for other reviewers' findings not specified | Clarify: findings arrive as text blocks in the dispatch prompt, each labeled with reviewer name
- **al-dev-performance-reviewer** | Low | "Measurable regression" and "blocks scaling" are vague severity labels | Add quantifiers: CRITICAL = timeout on >100K rows; HIGH = >20% query time increase
- **al-dev-security-reviewer** | Low | Format of other reviewers' findings in dispatch prompt not specified | Clarify: see al-dev-expert-reviewer dispatch format

### Agents — Structure (quality-lens-structure)

- **al-dev-commit-recover-verifier** | High | Missing required `description` field in frontmatter | Add description as single sentence
- **al-dev-commit-preflight** | High | Model field present as `sonnet` (non-canonical shorthand) | Update to canonical full model ID
- **al-dev-code-review** | Medium | Missing `name` field in frontmatter | Add `name: al-dev-code-review`
- **al-dev-commit-agent-analysis** | Medium | Missing `name` field in frontmatter | Add `name: al-dev-commit-agent-analysis`
- **al-dev-commit-agent-execute** | Medium | Missing `name` field; model shorthand `sonnet` | Add name field; update model to canonical ID
- **al-dev-commit-message-drafter** | Medium | Missing `name` field | Add `name: al-dev-commit-message-drafter`
- **al-dev-developer** | Medium | Missing `name` field | Add `name: al-dev-developer`
- **al-dev-diagnostics-fixer** | Medium | Missing `name` field | Add `name: al-dev-diagnostics-fixer`
- **al-dev-docs-writer** | Medium | Missing `name` field | Add `name: al-dev-docs-writer`
- **al-dev-expert-reviewer** | Medium | Missing `name` field | Add `name: al-dev-expert-reviewer`
- **al-dev-solution-architect** | Medium | Missing `name` field; model shorthand `opus` | Add name field; update model to canonical ID
- **al-dev-support-reply-drafter** | Medium | Missing `description` field | Add description
- **al-dev-support-researcher** | Medium | Missing `name` field | Add `name: al-dev-support-researcher`
- **al-dev-ticket-agent** | Medium | Missing `name` field | Add `name: al-dev-ticket-agent`

### Agents — Bloat (quality-lens-bloat)

- **al-dev-commit-agent-analysis** | High | "Manifest Extraction" section (42 lines, lines 46–87) exceeds 30-line threshold | Extract bash snippets to reference file; keep agent body to high-level workflow
- **al-dev-commit-message-drafter** | High | "Phase: message-drafting" (111 lines, lines 39–149) dominates body; emoji table and format examples bloat the section | Move emoji table and examples to `knowledge/commit-message-template.md`
- **al-dev-docs-writer** | High | "Documentation Guidelines" (35 lines, lines 56–90) exceeds threshold; ASCII folder diagram and "When to Create" rules | Extract to `knowledge/documentation-structure.md`
- **al-dev-expert-reviewer** | High | "Review Focus" (38 lines, lines 33–70); four repetitive subsections restate same rules across angles | Consolidate to single "Patterns to Check" list with reference links
- **al-dev-support-reply-drafter** | High | "Process" (37 lines, lines 35–71) exceeds threshold; "Step 1.5" is a dead branch (subjective opinion handling) | Move Step 1.5 to "Edge Cases" section; reduce Process to core 3 steps
- **al-dev-support-researcher** | High | "Research Process" (34 lines, lines 39–72) exceeds threshold; MCP tool descriptions duplicated inline | Consolidate MCP mapping into single reference table
- **al-dev-developer** | Medium | Repetitive error-handling blocks across lines 73–79, 90–105, 107–115 | Consolidate into single "Code Quality Standards" section
- **al-dev-solution-architect** | Medium | "Workflow" (32 lines) near threshold; repeated LSP/MCP evidence-source guidance across steps | Extract to `knowledge/al-symbol-evidence-hierarchy.md`
- **al-dev-ticket-agent** | Medium | "Step 1.5: Detect Inline Image Attachments" inserted mid-flow; dead branch not always triggered | Move to explicit conditional "Edge Cases: Inline Images" section

### Skills — Structure (quality-skill-lens-structure)

- **al-dev-investigate** | Medium | Phase 5 appears twice (duplicate phase numbers); output filename referenced inconsistently | Renumber phases to avoid duplicates
- **al-dev-support** | Medium | Deprecated skill; argument-hint indicates deprecation but skill body still full | Mark clearly as deprecated alias or remove
- **plan-with-critic-swarm** | Medium | argument-hint uses angle-bracket syntax `<spec>` inconsistent with square-bracket convention | Standardize to `[spec-file-or-description]`
- **al-dev-consolidate** | Medium | argument-hint set to empty string; should reflect actual argument support or be absent | Populate or remove field
- **al-dev-explore** | Medium | argument-hint present but no conditional argument handling in body | Add conditional handling or remove field
- **al-dev-develop** | Low | Phase numbering mixes sequential and fractional (Phase 1.5, Phase 0.5) | Standardize numbering convention
- **al-dev-document** | Low | Code block at line 189 missing language tag | Add tag
- **al-dev-fix** | Low | Multiple code blocks missing language tags (lines 47, 136, 141, 244, 250) | Add bash tags
- **al-dev-handoff** | Low | Code blocks at lines 59, 101–133 missing language tags | Add bash tags
- **al-dev-help** | Low | Code block at line 51 missing language tag | Add text/markdown tag
- **al-dev-interview** | Low | Code blocks at lines 87–88 missing language tags | Add tags
- **al-dev-lint** | Low | Code blocks at lines 41, 48, 56 missing bash tags | Add bash tags
- **al-dev-perf** | Low | Code blocks at lines 36, 60 missing bash tags | Add bash tags
- **al-dev-plan** | Low | Code blocks at lines 88–90 missing bash tags | Add bash tags
- **al-dev-release-notes** | Low | Code blocks at lines 15, 74 missing tags | Add bash/markdown tags
- **al-dev-review-develop** | Low | Code blocks at lines 66, 86, 94, 222 missing bash tags | Add bash tags
- **al-dev-ticket** | Low | Code blocks at lines 48–60, 85, 113, 145 missing tags | Add bash/text tags
- **commit-recover** | Low | Code blocks at lines 31, 91 missing bash tags | Add bash tags
- **verify-commits** | Low | Code blocks at lines 23, 28 missing bash tags | Add bash tags
- **al-dev-commit** | Low | argument-hint present; body does not reference optional arguments | Remove or add handling

### Skills — Bloat (quality-skill-lens-bloat)

- **al-dev-commit** | High | 11 steps (exceeds 8); advisory checks duplicate governance from other skills | Consolidate advisory checks into single "Advisory Gate" step; extract manifest template to knowledge
- **al-dev-develop** | High | 9 phases (exceeds 8); historical commentary in Phase 1.5; dead-branch reconciliation spans 4 lines | Split into base workflow and autonomous variant; move commentary to knowledge
- **al-dev-fix** | High | 9 steps; identical "Out of scope" decision tree repeated in Steps 2 and 3 | Consolidate scope-check into reusable template; remove dead-branch explanation
- **al-dev-plan** | High | 7 phases with fractional sub-phases; Phase 1.5/1.6 duplicate validation logic; accumulated triage guidance repeats knowledge/workflow-routing.md | Deduplicate validation phases; reference triage table once
- **al-dev-review-develop** | High | 10 phases non-sequentially numbered; Phase 8.5 only 3 bullets | Renumber sequentially; merge Phase 8.5 into Phase 8
- **al-dev-consolidate** | Medium | Extraction pattern definitions repeated inline despite referencing external knowledge file | Move all patterns to knowledge file; reference by name only
- **al-dev-document** | Medium | Steps 1 and 2 repeat scope discovery commands; Step 3 repeats file-path checks from Step 2 | Extract scope-determination as reusable fragment
- **al-dev-interview** | Medium | 11-category checklist in Phase 2 repeated; philosophical note at line 12 is design commentary | Extract checklist to knowledge; move commentary to design rationale
- **al-dev-investigate** | Medium | Steps 0 and 1 perform similar validation; Step 2 includes accumulated "why this matters" commentary | Merge Steps 0/1; move rationale to design doc
- **al-dev-perf** | Medium | 4-line methodology rationale embedded in Step 1a; severity escalation rule repeated twice | Move rationale to knowledge; state escalation once with cross-reference
- **al-dev-ticket** | Medium | Step 1.5 inserted mid-flow; agent dispatch includes full prompt inline | Extract prompt to knowledge template; move inline images to edge-cases section
- **al-dev-explore** | Low | Historical commentary on YYYY-MM-DD dating convention | Move to commit message or reduce to one line
- **al-dev-help** | Low | Step 2B and 2C similar structure; minor duplication | Combine into single mode selector

## Naming violations

_No issues found._ (lens `naming-convention-lens` returned no result — not yet in harness registry; plugin surface agents use `al-dev-*` naming not subject to the lens-agent or maintainer-skill conventions.)

## Graph deltas

**Orphan agents (spawned by no skill):**
- `al-dev-code-review`
- `al-dev-diagnostics-fixer`
- `al-dev-docs-writer`
- `al-dev-explore`
- `al-dev-interview`
- `al-dev-script-engineer`

**Dead knowledge (referenced by nothing):**
- `agent-tool-projection-policy.md`, `anti-patterns.md`, `code-review-template.md`, `commit-conventions.md`, `feedback-resolution.md`, `harness-concepts.md`, `proportional-planning.md`, `publish-workflow-opportunity.md`, `quality-checklist.md`, `review-panel-pattern.md`, `rubber-duck.md`, `session-analysis-report-format.md`, `skill-test-format.md`, `verification-and-planning.md`

**Off-path skills (not on any workflow path):**
- `al-dev-consolidate`, `al-dev-document`, `al-dev-explore`, `al-dev-handoff`, `al-dev-help`, `al-dev-interview`, `al-dev-lint`, `al-dev-perf`, `al-dev-release-notes`, `al-dev-review-develop`, `al-dev-support`, `commit-recover`, `plan-with-critic-swarm`, `verify-commits`

**Missing refs (referenced but not on disk):** none

> Source: `docs/al-dev-plugin-graph.md` (generated 2026-05-29). Re-run `scripts/generate-plugin-graph.py` to refresh.
