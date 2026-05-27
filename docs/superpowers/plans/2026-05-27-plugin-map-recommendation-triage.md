# Plugin Map Recommendation Triage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconcile `docs/al-dev-plugin-map.md` with the current repo state, keep only recommendations that still survive the suggestion-of-merit gate, and align related `/al-dev-fix` routing guidance.

**Architecture:** This is a documentation-reconciliation change, not a new shared-plugin feature build. First replace stale “remaining recommendation” entries that are already implemented. Then narrow the only partially-live `/al-dev-fix` recommendation to the actual open issue: routing/documentation consistency. Keep `/al-dev-publish` deferred until its scope questions are answered.

**Tech Stack:** Markdown docs in `docs/` and `profile-al-dev-shared/knowledge/`, plus text-based verification with `sed`, `rg`, and `git diff`.

---

## File Map

| Task | Files Modified | Purpose |
|---|---|---|
| 1 | `docs/al-dev-plugin-map.md` | Remove stale “remaining” items that are already implemented and refresh the summary blocks |
| 2 | `docs/al-dev-plugin-map.md`, `profile-al-dev-shared/knowledge/workflow-routing.md` | Reframe the `/al-dev-fix` symbol-rigor item around the real remaining gap: routing/documentation consistency |
| 3 | `docs/al-dev-plugin-map.md`, `profile-al-dev-shared/knowledge/publish-workflow-opportunity.md` | Keep `/al-dev-publish` explicitly deferred and out of immediate implementation scope |

All paths are relative to `/Users/russelllaing/al-dev-shared/`.

---

## Rubber Duck Verdicts

Apply `profile-al-dev-shared/knowledge/rubber-duck.md` before treating any “recommendation” as implementation scope.

| Recommendation in `docs/al-dev-plugin-map.md` | Verdict | Why |
|---|---|---|
| **Atomise: /al-dev-develop** | reject as new implementation scope | Already implemented: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` now produces a Phase 4 handoff for `/al-dev-review-develop`, and `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md` exists as the extracted review workflow |
| **Connect: Reuse symbol pre-flight more broadly** | narrow and document | `/al-dev-fix` already loads lint findings and tells the architect to follow `knowledge/al-symbol-pre-flight.md` on the non-trivial path. The remaining gap is misleading routing prose elsewhere, not missing core infrastructure |
| **Extend: /al-dev-publish** | defer | `profile-al-dev-shared/knowledge/publish-workflow-opportunity.md` still shows unresolved scope questions about targets, tooling, frequency, and audience |
| **Improve: Close /al-dev-lint feedback loop** | reject as new implementation scope | Already implemented: `/al-dev-fix` Step 3 loads `.dev/*-al-dev-lint-lint-report.md` and passes unresolved items as “Known linting constraints” |

**Additional gap discovered during rubber ducking:** `profile-al-dev-shared/knowledge/workflow-routing.md` still says `/al-dev-fix` is “no planning, no testing” and “Always TRIVIAL path”, which conflicts with the live `/al-dev-fix` skill. That inconsistency must be fixed if Task 2 proceeds.

---

### Task 1: Refresh stale recommendation status in `docs/al-dev-plugin-map.md`

**Files:**
- Modify: `docs/al-dev-plugin-map.md`

**Intent:** Convert stale “remaining recommendation” text into current-state documentation. Do not add new skill scope in this task.

- [ ] **Step 1: Confirm the stale sections are still present**

Run:
```bash
sed -n '596,733p' /Users/russelllaing/al-dev-shared/docs/al-dev-plugin-map.md
```
Expected: the output still contains:
- `**Atomise: /al-dev-develop**`
- `**Improve: Close /al-dev-lint feedback loop in /al-dev-fix**`
- a status summary bullet list that still treats both items as future-facing suggestions

- [ ] **Step 2: Replace the Atomise section with implemented-state wording**

In `docs/al-dev-plugin-map.md`, replace the block that begins:

```markdown
**Atomise: /al-dev-develop** ← highest leverage
```

and ends just before the next `---` with:

```markdown
**✅ Implemented: /al-dev-review-develop extracted from /al-dev-develop**

Status: Confirmed in current sweep. The live workflow now splits implementation from review:
- `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` produces a Phase 4 handoff for `/al-dev-review-develop`
- `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md` owns the post-implementation review orchestration (Phase 5–10)

Impact: This is no longer remaining implementation scope. The map should treat review-workflow independence as current state, not future work.
```

- [ ] **Step 3: Replace the lint-feedback section with implemented-state wording**

In `docs/al-dev-plugin-map.md`, replace the block that begins:

```markdown
**Improve: Close /al-dev-lint feedback loop in /al-dev-fix**
```

and ends just before the next `---` with:

```markdown
**✅ Implemented: /al-dev-fix consumes prior lint findings**

Status: Confirmed in current sweep. `/al-dev-fix` Step 3 now:
- loads the latest `.dev/*-al-dev-lint-lint-report.md` when present
- extracts unresolved items
- passes them into the architect prompt as `Known linting constraints`

Impact: The Layer 1 lint → fix feedback loop is implemented in the live skill. No new behavior change is required here; only the map text needed reconciliation.
```

- [ ] **Step 4: Update the status summary and extension-opportunity bullets**

In `docs/al-dev-plugin-map.md`, replace the “Current analysis (2026-05-27)” bullet list under `### Status summary` with:

```markdown
**Current analysis (2026-05-27):** Five lenses re-applied across the same 18 skills. Current state is:
- **Implemented: /al-dev-review-develop extraction** (review workflow independence is now live)
- **Narrow follow-up: `/al-dev-fix` symbol-rigor wording** (non-trivial path already uses symbol pre-flight; routing docs still need alignment)
- **Deferred: /al-dev-publish** (blocked on scope clarification)
- **Implemented: lint feedback into `/al-dev-fix`** (unresolved lint items already surface to the architect)
- **Confirmed: /al-dev-plan interview guidance already present**
- **Confirmed: /al-dev-develop compile/staging gates already documented**
- **Confirmed: /al-dev-explore integration working** (outdated observation removed)
- **Confirmed: Patterns documented** (architect, explore, ticket-agent, review-panel)
```

Then replace the `### Extension opportunities` list with:

```markdown
1. **Post-release orchestration**: `/al-dev-publish` remains a deferred opportunity until publication targets, tooling, and audience are standardized.
2. **`/al-dev-fix` routing clarity**: Align the routing docs with the live skill so “fast fix” does not imply “always trivial” or “never uses an architect”.
3. **Lint quality gates**: Optional pre-commit lint gating remains separate future work; current lint integration is advisory by design.
```

- [ ] **Step 5: Verify stale phrases are gone and replacement phrases are present**

Run:
```bash
rg -n "Atomise: /al-dev-develop|Improve: Close /al-dev-lint feedback loop|Review workflow independence" /Users/russelllaing/al-dev-shared/docs/al-dev-plugin-map.md
```
Expected:
- no hit for the old `Atomise:` heading
- no hit for the old `Improve:` heading
- no hit for the old extension-opportunity bullet about extracting `/al-dev-review-develop`

Run:
```bash
rg -n "Implemented: /al-dev-review-develop extraction|Implemented: lint feedback into `/al-dev-fix`|✅ Implemented: /al-dev-fix consumes prior lint findings" /Users/russelllaing/al-dev-shared/docs/al-dev-plugin-map.md
```
Expected: one or more hits showing the new reconciled wording.

- [ ] **Step 6: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add docs/al-dev-plugin-map.md
git -C /Users/russelllaing/al-dev-shared diff --cached -- docs/al-dev-plugin-map.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(plugin-map): reconcile stale implemented recommendations"
```

---

### Task 2: Narrow the `/al-dev-fix` follow-up to the real open gap

**Files:**
- Modify: `docs/al-dev-plugin-map.md`
- Modify: `profile-al-dev-shared/knowledge/workflow-routing.md`

**Intent:** Do not invent a new shared-plugin behavior. Make the docs accurately describe the live behavior: `/al-dev-fix` is the fast-fix entrypoint, but it can still escalate to architect analysis when the issue is non-trivial.

- [ ] **Step 1: Replace the current “Connect” subsection in the plugin map**

In `docs/al-dev-plugin-map.md`, replace the block that begins:

```markdown
**Connect: Reuse the existing symbol pre-flight pattern more broadly**
```

and ends just before the next `---` with:

```markdown
**Connect: Clarify `/al-dev-fix` escalation boundaries**

Observation: The core propagation work is already present. `/al-dev-fix` now:
- loads prior lint findings on the non-trivial path
- dispatches an architect for non-trivial fixes
- explicitly tells that architect to follow `knowledge/al-symbol-pre-flight.md`

The remaining asymmetry is documentation: `profile-al-dev-shared/knowledge/workflow-routing.md` still describes `/al-dev-fix` as if it were always a direct trivial edit with no planning branch.

Suggestion: Treat symbol pre-flight reuse as implemented for the non-trivial `/al-dev-fix` path. The remaining follow-up is to align routing guidance so `/al-dev-fix` is documented as a fast-fix entrypoint that may escalate to quick architect analysis when the issue is ambiguous, multi-file, or integration-heavy.

Trade-off: Slightly more nuanced routing prose. Improvement: removes false expectations about `/al-dev-fix`, makes existing symbol-rigor behavior discoverable, and avoids adding prompt weight to truly trivial fixes without evidence.
```

- [ ] **Step 2: Update the TRIVIAL routing text in `workflow-routing.md`**

In `profile-al-dev-shared/knowledge/workflow-routing.md`, replace:

```markdown
**Route:** `/al-dev-fix` workflow (no planning, no testing)
```

with:

```markdown
**Route:** `/al-dev-fix` workflow (fast-fix entrypoint; may escalate to quick architect analysis if the issue proves non-trivial)
```

Then replace the current five-item TRIVIAL `Steps:` list with:

```markdown
**Steps:**
1. Read project-context.md
2. Locate the likely file with minimal search
3. If the fix stays obvious and single-scope, continue on the direct `/al-dev-fix` path
4. If ambiguity, multiple files, or integration risk appears, follow the `/al-dev-fix` non-trivial branch instead of forcing a trivial edit
5. Run compile/lint verification and present the bounded result
```

- [ ] **Step 3: Update the override-mechanism bullet that says `/al-dev-fix` is always trivial**

In `profile-al-dev-shared/knowledge/workflow-routing.md`, replace:

```markdown
- `/al-dev-fix` → Always TRIVIAL path
```

with:

```markdown
- `/al-dev-fix` → Explicit fast-fix entrypoint; still allows architect escalation for non-trivial bugs
```

- [ ] **Step 4: Verify the routing contradiction is removed**

Run:
```bash
rg -n "no planning, no testing|skip all agents|Always TRIVIAL path" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/workflow-routing.md
```
Expected:
- no hit for `no planning, no testing`
- no hit for `Always TRIVIAL path`

Run:
```bash
rg -n "architect escalation|non-trivial branch|fast-fix entrypoint" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/workflow-routing.md \
  /Users/russelllaing/al-dev-shared/docs/al-dev-plugin-map.md
```
Expected: hits in both files showing the aligned framing.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add docs/al-dev-plugin-map.md profile-al-dev-shared/knowledge/workflow-routing.md
git -C /Users/russelllaing/al-dev-shared diff --cached -- docs/al-dev-plugin-map.md profile-al-dev-shared/knowledge/workflow-routing.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(fix-routing): align plugin map with live /al-dev-fix behavior"
```

---

### Task 3: Keep `/al-dev-publish` deferred and explicitly out of immediate implementation scope

**Files:**
- Modify: `docs/al-dev-plugin-map.md`
- Modify: `profile-al-dev-shared/knowledge/publish-workflow-opportunity.md`

**Intent:** Preserve the opportunity without quietly upgrading it into shared-profile scope.

- [ ] **Step 1: Keep the plugin-map publish section explicitly deferred**

In `docs/al-dev-plugin-map.md`, keep the existing `/al-dev-publish` section, but ensure the closing recommendation text ends with this exact block:

```markdown
**Status:** Deferred to future work pending scope clarification.
See `knowledge/publish-workflow-opportunity.md` for detailed opportunity analysis.
Current recommendation: Do not implement in shared profile until:
1. Publishing is confirmed to be a frequent manual workflow
2. Publication targets are standardized enough to be harness-neutral
3. Required integrations are known and supportable across downstream repos
```

- [ ] **Step 2: Strengthen the deferral gate in `publish-workflow-opportunity.md`**

Append this section to `profile-al-dev-shared/knowledge/publish-workflow-opportunity.md` after `## Decision Required Before Implementation`:

```markdown
## Shared-Profile Gate

Do not convert this opportunity into a distributed skill until the four scope
questions above are answered for at least one real downstream workflow. If the
answers are repo-specific, keep the automation repo-local instead of adding it
to `profile-al-dev-shared`.
```

- [ ] **Step 3: Verify the defer language is explicit in both files**

Run:
```bash
rg -n "Do not implement in shared profile until|## Shared-Profile Gate|keep the automation repo-local" \
  /Users/russelllaing/al-dev-shared/docs/al-dev-plugin-map.md \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/publish-workflow-opportunity.md
```
Expected: hits in both files.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add docs/al-dev-plugin-map.md profile-al-dev-shared/knowledge/publish-workflow-opportunity.md
git -C /Users/russelllaing/al-dev-shared diff --cached -- docs/al-dev-plugin-map.md profile-al-dev-shared/knowledge/publish-workflow-opportunity.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(publish): keep publish workflow explicitly deferred"
```

---

## Self-Review

- [ ] **Spec coverage check:** Confirm the plan covers all four “remaining” items from `docs/al-dev-plugin-map.md` and that each ended in one of three buckets: implemented-state cleanup, narrowed follow-up, or deferred future work.
- [ ] **Placeholder scan:** Run:
```bash
rg -n "TODO|TBD|implement later|appropriate error handling|edge cases|similar to Task" /Users/russelllaing/al-dev-shared/docs/superpowers/plans/2026-05-27-plugin-map-recommendation-triage.md
```
Expected: no output.
- [ ] **Type and wording consistency check:** Ensure the plan uses the same names everywhere:
  - `/al-dev-review-develop`
  - `/al-dev-fix`
  - `knowledge/al-symbol-pre-flight.md`
  - `profile-al-dev-shared/knowledge/workflow-routing.md`
  - `profile-al-dev-shared/knowledge/publish-workflow-opportunity.md`

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-27-plugin-map-recommendation-triage.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
