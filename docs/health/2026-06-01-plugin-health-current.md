# Plugin Health — 2026-06-01 (Current Session)

**Audit Date:** 2026-06-01  
**Surface:** Plugin (`profile-al-dev-shared/`)  
**Lenses Run:** 20 of 21 completed  
**Failed Lenses:** 1 (quality-agent-lens-structure — requires explicit file paths)

---

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 2      | 8+      | 0      | 10+   |
| Medium   | 8      | 12+     | 1      | 21+   |
| Low      | 7      | 0       | 0      | 7     |
| **Total**| **17** | **20+** | **1**  | **38+**|

### Top 5 Ranked Actions

1. **[High/Design]** Atomise `/al-dev-plan` (9 phases) — split into preflight (phases 0–1.6) + architect debate (phases 2–7). Pre-planning is independent and could be reused by other workflows.

2. **[High/Quality]** Fix systematic markdown code fence errors (16+ agents have ` ```text` on closing backticks instead of ```; 13+ skills have language tags on closing fences). These break tool invocation.

3. **[High/Quality]** Clarify vague skill phase conditionals (20+ instances of "as needed", "if appropriate" without operative definitions). Replace with explicit decision logic for agent routing.

4. **[Medium/Design]** Atomise `/al-dev-ticket` (8 phases) — extract phases 6–8 (research + reply) into `/al-dev-support-reply`. Context-fetch (phases 0.5–4) is fully independent and the default mode.

5. **[Medium/Design]** Split `/al-dev-commit-agent-execute` — separate hook-failure retry recovery from commit execution. Success path and error recovery are independent concerns with separate outputs.

---

## Design Findings

### Atomise Candidates (High Priority)

**al-dev-plan** | High | 9 phases split cleanly into two independent concerns: (1) Phases 0–1.6 preflight (context gathering, requirements triage, verification), (2) Phases 2–7 architect debate (design, debate, evaluation, synthesis). The skill's own checkpoint schema acknowledges this separation (`--resume-from=phase2` design implies independence). Every invocation reloads both phases even when preflight is cached. | **Fix:** Extract preflight into `/al-dev-plan-preflight` (phases 0–1.6). Allow `/al-dev-plan` to call it automatically or skip if `--resume-from=phase2` passed. This unblocks reuse by other workflows and reduces token waste.

**al-dev-ticket** | Medium | 8 phases with hard mode gate at phase 5. Phases 0.5–4 (context fetch) form a complete, independent unit used by default (`mode=context-only`). Phases 6–8 (research + reply) are optional extension. Current design forces cognitive load of all 8 phases even when only 4 are used. | **Fix:** Extract phases 6–8 into `/al-dev-support-reply` (research + draft). Preserve backward compatibility with `--mode=full` as convenience alias that chains `/al-dev-ticket` → `/al-dev-support-reply`. Reduces primary ticket workflow from 8 phases to 4.

### Split Candidates (Medium Priority)

**al-dev-commit-agent-execute** | Medium | Combines (1) executing commits with hook retry logic (success path) and (2) handling hook failures and recovery fallback (error path). Both produce unrelated outputs (`COMMITS` block vs `HOOK_FAILURES` block) and could be diagnosed independently. Current monolithic design masks which concern failed. | **Fix:** Extract hook-failure retry into dedicated `al-dev-commit-hook-fixer` agent. Keep execute agent focused on success path only.

**al-dev-support-researcher** | Medium | Combines (1) multi-source research (AL symbols, MS Docs, BC history) and (2) synthesis of findings into structured output block. Research and synthesis serve different cognitive purposes and could have independent checkpoints for debugging. | **Fix:** Extract synthesis step into separate agent or fold into reply drafter to decouple research from presentation logic.

**al-dev-support-reply-drafter** | Medium | Combines (1) validation of researcher findings (tone/framing constraints) and (2) drafting customer reply. Validation/gatekeeping is logically separate from draft-writing. | **Fix:** Separate into validator + drafter agents, or collapse validation into researcher's synthesis step.

**al-dev-release-notes-writer** | Medium | System prompt describes two separable concerns: (1) Git diff analysis and change extraction (Phase 1) and (2) Release notes composition and formatting (Phase 2). Currently owns both git operations and narrative authoring with no intermediate handoff. | **Fix:** Extract Phase 1 into new agent `al-dev-release-notes-analyzer` that returns `CHANGES_EXTRACTED` block; have composer consume independently.

### Scope Isolation Findings (Low Priority)

_No critical issues._ Other agents are properly focused or already split appropriately.

### Trim / Remodel / Align Findings

**al-dev-developer-tdd & al-dev-developer-traditional** | Low | `Grep` declared in frontmatter but no grep usage in body workflows (use Read/Write/Bash only). | Remove `Grep` from tools list or add explicit symbol search step.

**al-dev-support-reply-drafter** | Medium | `sonnet` assigned for mechanical format transformation (parse findings → write two-section reply, no novel reasoning). Task is structured rewrite with tight constraints. | Downgrade to `haiku` for cost reduction without signal loss.

**al-dev-plan & shared architect invocation** | Low | `/al-dev-plan` Phase 2 spawns architect competitively but doesn't reference `knowledge/architect-invocation-patterns.md` (only `/al-dev-fix` does). Pattern documentation exists but is inconsistently referenced. | Add reference to architect-invocation-patterns.md in `/al-dev-plan` Phase 2 to prevent invocation drift.

**Developer agent Inputs tables** | Low | Tables document specific `.dev/` file paths, but callers locate files via glob pattern. Documentation implies explicit passing. | Clarify Inputs: "Files are auto-located via glob in `.dev/`; callers do not pass explicit paths."

### Connection Findings

**No action needed.** Shared agents (`al-dev-solution-architect`, `al-dev-developer-tdd/traditional`) are already documented in `knowledge/` files preventing drift.

### Handoff Chain Findings

**Release notes output orphaned** | Medium | `/al-dev-commit` → `/al-dev-release-notes` → `.dev/release-notes-*.md` produced but never consumed by downstream skill. Natural continuation would be `/al-dev-publish` skill (deferred scope). | Create `/al-dev-publish` skill to consume release-notes for publication orchestration, or document as terminal output.

**Code review artifact terminal** | Low | `/al-dev-review-develop` writes `.dev/*-al-dev-develop-code-review.md` but no downstream skill reads it. Output is user-facing terminal only. | Optional: document as terminal or create consumer if cross-session audit trails needed.

---

## Quality Findings

### Critical Issues (High Priority)

**Systematic markdown formatting errors (21+ agents, 13+ skills)**

Malformed code fence closures affect rendering and tool invocation:
- **21+ agents** have ` ```text` instead of ``` on closing backticks
- **13+ skills** have language tags on closing backticks instead of opening only
- Examples: `al-dev-developer-tdd`, `al-dev-expert-reviewer`, `al-dev-commit-agent-analysis`, `al-dev-lint`, `al-dev-plan`, `al-dev-develop`, `al-dev-fix`, `al-dev-commit`, `al-dev-interview`, `al-dev-ticket-agent`

**Fix:** Standardize all code blocks:
- Opening backticks have language specifiers: ` ```bash `, ` ```yaml `, ` ```text `
- Closing backticks are plain: ` ``` ` (no language tag)
- Apply systematically across all 34 files

---

### High-Severity Clarity Issues (20+ instances)

**Vague phase conditionals in skills** — Undefined qualifiers affecting agent routing:
- "as needed" (al-dev-develop Phase 3, al-dev-fix Step 3)
- "if appropriate" (multiple skills)
- "handle edge cases" (pseudo-code blocks)
- Incomplete conditionals: "if X then Y" without else case or fallback

Examples:
- `al-dev-develop` Phase 3: "scope expansion as needed" — when is it needed? No decision logic provided.
- `al-dev-fix` Step 3: "test-plan routing as needed" — unclear whether to check for file existence or parse content.
- `al-dev-commit` Phase 0.2: "check for Freshdesk ticket" — fallback if not found not specified.

**Fix:** Replace all vague qualifiers with explicit decision logic:
- "as needed" → "if [specific condition], then [action]"
- "if appropriate" → "if [concrete test] is true, then [action]"
- Add fallback for every conditional: "if not X, then [default behavior]"

---

### Medium-Severity Clarity Issues (5+ instances)

**Pseudo-code notation inconsistency** — Workflow diagrams use mismatched fence markers:
- YAML fence markers on plaintext flowcharts (should be `text`)
- Bash fence markers on structured output (should be `yaml`)
- Inconsistent throughout al-dev-plan, al-dev-fix, al-dev-develop

**Fix:** Use consistent fence language:
- ASCII flowcharts/diagrams: ` ```text `
- Shell commands: ` ```bash `
- Structured output (JSON, YAML): ` ```yaml `

---

### Bloat Issues (7 skills identified)

**al-dev-plan** (465 lines) | High | Phases 0–1.6 alone contain 150+ lines of repetitive context assembly instructions. Historical commentary ("as of v3.0") mixed with current instructions. Resume modes section repeats checkpoint logic. | Extract context assembly to `knowledge/plan-context-assembly.md`; remove historical commentary.

**al-dev-develop** (420 lines) | High | Phase 1 signature verification spans 92 lines with redundant decision-tree steps. Phase 3 developer-spawn logic repeats `knowledge/developer-invocation-patterns.md`. | Extract signature verification to knowledge file; reference invocation patterns instead of inlining.

**al-dev-fix** (444 lines) | High | Step 2 (trivial fixes, 107–168 lines) and Step 3 (non-trivial fixes, 172–302 lines) near-duplicate the overall workflow with different complexity signals. "Fast Iteration Philosophy" block duplicates intent already stated in description. | Create single parameterized flow branching on complexity flag; remove duplication.

**al-dev-commit** (550+ lines) | High | Phase 0 alone runs 208 lines with 7 overlapping sub-steps. Phases 1–2 repeat context assembly instructions. Compile-gate logic appears in multiple sections. | Extract compile-gate to `knowledge/compile-lint-procedure.md`; consolidate Phase 0 sub-steps.

**al-dev-consolidate** | High | Phase 2 (74 lines) has repetitive bash patterns for groups A–D. | Extract to `knowledge/consolidate-extraction-patterns.md`.

**al-dev-review-develop** | Medium | Phases 1–3 (145 lines) contain verbose explanations and repeated reviewer-dispatch template headers. | Condense and extract dispatch templates to knowledge file.

**al-dev-ticket** | Medium | Steps 1–2 overlap in auto-detection and credential verification; could consolidate into "Resolve & Load" step. | Merge overlapping detection blocks.

---

### Description Drift Issues (11 skills identified)

- **al-dev-ticket** | Medium | Description doesn't clarify two modes (context-only vs. full) with different agent spawning behavior.
- **al-dev-fix** | Low | Description says "lightweight" but non-trivial path includes architect analysis (not lightweight).
- **al-dev-review-develop** | Medium | Description omits autonomous developer error-fixing in Phase 2.
- **al-dev-commit** | Medium | Description doesn't mention alignment advisory and knowledge validators.
- **al-dev-investigate** | Medium | Description oversimplifies to "parallel agents" without cardinality or branching logic.
- **al-dev-interview** | Medium | Description doesn't mention mandatory `INTERVIEW COMPLETE` gate with 11-category coverage requirement.
- **al-dev-lint** | Low | Description says "lint checking" but body implements automated fixing.
- **al-dev-perf** | Medium | Description omits semantic symbol verification and severity escalation for hot-path findings.
- **al-dev-handoff**, **al-dev-explore**, **al-dev-consolidate** | Low | Minor output artifact description omissions.

**Fix:** Update descriptions to match body behavior; document gates, branching, and key behaviors upfront.

---

## Naming Findings

**al-dev-map-suggestions-verify** | Low | Hybrid naming mixes maintainer skill prefix `al-dev-` with maintainer convention pattern `{verb}-{object}-{aspect}`. Appears in `.claude/skills/` as maintainer skill but named like application skill. | Rename to `verify-map-suggestions` to align with other maintainer skills (`audit-quality`, `analyze-skill-design`, etc.).

---

## Pre-Planning Skills (Verified as Correct)

All three pre-planning skills (al-dev-explore, al-dev-interview, al-dev-perf) correctly appear as dashed tributaries in Layer 1 diagram and are properly integrated into downstream consumers. **No issues found.**

---

## Next Steps

1. **Critical (Fix immediately):**
   - Fix systematic markdown code fence errors (21+ agents, 13+ skills)
   - Clarify vague skill phase conditionals (20+ instances)

2. **High Priority (Plan in next cycle):**
   - Atomise `/al-dev-plan` (preflight + architect debate)
   - Atomise `/al-dev-ticket` (context-fetch + reply-draft)
   - Reduce bloat in al-dev-plan, al-dev-develop, al-dev-fix, al-dev-commit

3. **Medium Priority (Queue for review):**
   - Split agent concerns (execute, researcher, reply-drafter)
   - Update 11 skill descriptions to match body behavior
   - Extract repetitive knowledge blocks to `knowledge/` files

4. **To rubber-duck findings before implementation:**
   ```bash
   /al-dev-map-suggestions-verify
   ```

---

## Failed Lenses & Resume Path

**quality-agent-lens-structure** — Did not complete. Requires explicit file path list. To collect this finding:

```bash
/plugin-health-discover --surface plugin --dimension quality --resume
```

Then re-run this report phase to include structure findings.

---

**Generated:** 2026-06-01 (current session)  
**Lenses Completed:** 20/21 (95%)  
**Findings:** 38+ actionable suggestions across design, quality, and naming dimensions
