# Tooling Low Priority Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve the live low-priority tooling findings from `docs/health/2026-06-01-tooling-health.md` without implementing medium/high findings.

**Architecture:** Verify each reported low-priority issue against current repo-local maintainer tooling before editing. Apply narrow markdown contract fixes in `.claude/skills/` and `.claude/agents/`, then add regression tests that prevent the same low-priority drift from returning.

**Tech Stack:** Markdown skill/agent definitions, Python `unittest`, shell validation scripts.

---

## File Structure

- Create `scripts/tests/test_tooling_low_priority_contracts.py`
  - Regression tests for the low-priority tooling contracts.
- Modify `.claude/skills/plugin-health-report/SKILL.md`
  - Merge the ranking and dossier-writing phases into one "Rank and Write Dossier" phase.
- Modify `.claude/skills/analyze-agent-design/SKILL.md`
  - Clarify that `/draft-map-suggestions` owns highest-leverage selection and fix the stale Phase 5 reference.
- Modify `.claude/skills/analyze-skill-design/SKILL.md`
  - Same highest-leverage delegation and stale phase reference fix.
- Modify `.claude/skills/review-agent-map/SKILL.md` and `.claude/skills/review-skill-map/SKILL.md`
  - Clarify that `--no-update` is the audit-only mode.
- Modify `.claude/skills/align-harness-repos/SKILL.md`
  - Clarify that the skill validates the single shared plugin surface.
- Modify `.claude/skills/audit-quality/SKILL.md` and `.claude/skills/audit-knowledge-quality/SKILL.md`
  - Clarify that these audits can offer or apply fixes, so they are not purely read-only.
- Modify `.claude/skills/projection-sync/SKILL.md`
  - Clarify that projection sync is unidirectional validation and regeneration.
- Modify `.claude/skills/discover-agent-design/SKILL.md` and `.claude/skills/discover-skill-design/SKILL.md`
  - Clarify that these are internal discovery phases for the analyze skills.
- Modify `.claude/agents/naming-convention-lens.md`
  - Ensure bash examples use language-tagged code fences if present.
- Modify `.claude/agents/sync-documentation-maps-agent-audit.md`, `.claude/agents/sync-documentation-maps-skill-audit.md`, `.claude/agents/sync-documentation-maps-agent-update.md`, and `.claude/agents/sync-documentation-maps-skill-update.md`
  - Ensure bash command examples use `bash` fences.
- Modify all active `.claude/skills/*/SKILL.md`
  - Ensure every fenced code block has an explicit language tag.

## Stale Low Findings

These reported low findings no longer exist as stated and must not drive edits:

- Distributed `profile-al-dev-shared/skills/analyze-agent-design` and `profile-al-dev-shared/skills/analyze-skill-design` do not exist; the live targets are repo-local `.claude/skills/`.
- Several old distributed tooling skill paths named in the report have moved to `.claude/skills/`; fixes must stay repo-local.

### Task 1: Add Regression Tests

**Files:**
- Create: `scripts/tests/test_tooling_low_priority_contracts.py`

- [ ] **Step 1: Write the tests**

Create `scripts/tests/test_tooling_low_priority_contracts.py` with tests that:
- Assert active `.claude/skills/*/SKILL.md` code fences are language-tagged.
- Assert the four `sync-documentation-maps-*` agents have language-tagged fences.
- Assert `.claude/skills/plugin-health-report/SKILL.md` has "Phase 2 - Rank and Write Dossier" and no separate "Phase 3 - Write Dossier".
- Assert analyze-agent/skill skills say `/draft-map-suggestions` owns highest-leverage selection and do not mention a Phase 5 invocation.
- Assert the low-priority name-fit descriptions mention audit-only, single shared surface, fix offering/application, unidirectional regeneration, and internal discovery phase as appropriate.

- [ ] **Step 2: Run tests to confirm failures before edits**

Run:

```bash
python3 -m unittest scripts.tests.test_tooling_low_priority_contracts -v
```

Expected before edits: FAIL on the live low-priority issues.

### Task 2: Patch Low-Priority Tooling Docs

**Files:**
- Modify: `.claude/skills/plugin-health-report/SKILL.md`
- Modify: `.claude/skills/analyze-agent-design/SKILL.md`
- Modify: `.claude/skills/analyze-skill-design/SKILL.md`
- Modify: `.claude/skills/review-agent-map/SKILL.md`
- Modify: `.claude/skills/review-skill-map/SKILL.md`
- Modify: `.claude/skills/align-harness-repos/SKILL.md`
- Modify: `.claude/skills/audit-quality/SKILL.md`
- Modify: `.claude/skills/audit-knowledge-quality/SKILL.md`
- Modify: `.claude/skills/projection-sync/SKILL.md`
- Modify: `.claude/skills/discover-agent-design/SKILL.md`
- Modify: `.claude/skills/discover-skill-design/SKILL.md`
- Modify: active `.claude/skills/*/SKILL.md` files with unlabeled fences
- Modify: `.claude/agents/naming-convention-lens.md`
- Modify: `.claude/agents/sync-documentation-maps-*.md`

- [ ] **Step 1: Apply narrow markdown edits**

Update only wording and fence language tags. Do not rename skills or move files in this low-priority pass.

- [ ] **Step 2: Run regression tests**

Run:

```bash
python3 -m unittest scripts.tests.test_tooling_low_priority_contracts -v
```

Expected: PASS.

### Task 3: Validate and Commit

**Files:**
- All files modified in Tasks 1 and 2.

- [ ] **Step 1: Run repository validation**

Run:

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
```

Expected: both commands pass.

- [ ] **Step 2: Review intended diff**

Run:

```bash
git diff -- .claude/skills .claude/agents scripts/tests/test_tooling_low_priority_contracts.py docs/superpowers/plans/2026-06-01-tooling-low-priority-fixes.md
git status --short
```

Expected: only the new plan, new regression test, and low-priority tooling markdown edits are included in this commit scope.

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/superpowers/plans/2026-06-01-tooling-low-priority-fixes.md scripts/tests/test_tooling_low_priority_contracts.py .claude/skills .claude/agents
git commit -m "docs: fix low-priority tooling health issues"
```

Expected: commit succeeds without staging unrelated existing worktree changes.
