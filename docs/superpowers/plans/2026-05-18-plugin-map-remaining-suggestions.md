# Plugin Map Remaining Suggestions — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the 4 remaining unimplemented suggestions from the Observations section of `docs/al-dev-plugin-map.md` — one new knowledge doc with architect invocation patterns, two SKILL.md reference additions, three Layer 1 diagram extensions, and closing out one already-implemented observation.

**Architecture:** Purely additive across all tasks. Task 1 creates the knowledge doc; Task 2 adds references in two SKILL.md files; Task 3 makes three diagram additions in one file; Task 4 marks all suggestions as resolved. No code changes, no AL compilation.

**Tech Stack:** Markdown files (SKILL.md, knowledge docs, plugin map). Verification is text-based (`grep`, `wc -l`, `git status`).

---

## File Map

| Task | Files Created | Files Modified |
|------|--------------|----------------|
| 1 | `profile-al-dev-shared/knowledge/architect-invocation-patterns.md` | — |
| 2 | — | `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`, `profile-al-dev-shared/skills/al-dev-fix/SKILL.md` |
| 3 | — | `docs/al-dev-plugin-map.md` (Layer 1 diagram only) |
| 4 | — | `docs/al-dev-plugin-map.md` (Observations section only) |

All paths are relative to `/Users/russelllaing/al-dev-shared/` unless otherwise specified.

---

## Rubber Duck Summary (pre-plan verification)

| Suggestion | Verdict |
|-----------|---------|
| Connect: al-dev-solution-architect invocation patterns | proceed — `knowledge/architect-invocation-patterns.md` does not exist; both patterns confirmed in SKILL.md files |
| Extend: /al-dev-support integrated ticket lookup | skip — **already implemented**; al-dev-support Step 1 already handles `FD-NNNN`/numeric input inline |
| Extend Layer 1: /al-dev-perf as pre-plan tributary | proceed — Perf absent from Layer 1; produces `perf-analysis.md` (confirmed Layer 2) |
| Extend Layer 1: /al-dev-handoff as post-commit node | proceed — Handoff absent from Layer 1; produces `handoff-prompt.md` (confirmed Layer 2) |
| Extend Layer 1: lint → fix feedback loop | proceed with modification — Lint absent from Layer 1 entirely; plan must add both the Lint node and the feedback arrow (the suggestion implies only the arrow but the node is prerequisite) |

---

## Task 1: Create `knowledge/architect-invocation-patterns.md`

**Files:**
- Create: `profile-al-dev-shared/knowledge/architect-invocation-patterns.md`

Precedent: mirrors the structure of `knowledge/review-panel-pattern.md` (structural mechanics only; domain-specific prompt content stays local to each calling skill).

- [ ] **Step 1: Create the knowledge doc**

Write the following content verbatim to `profile-al-dev-shared/knowledge/architect-invocation-patterns.md`:

```markdown
# Architect Invocation Patterns

`al-dev-solution-architect` is spawned by two skills using structurally
different patterns. The domain-specific prompt content (what to analyse,
what to produce) stays local to each skill; only the structural mechanics
are documented here.

## Pattern 1: Competitive Debate (×2-3 parallel)

Used by /al-dev-plan.

Spawn 2-3 `al-dev-solution-architect` agents in parallel, each assigned a
**meaningfully different starting approach** to prevent convergence. The goal
is genuine diversity of design, not minor variations on the same idea.

Before spawning, derive 2-3 distinct approaches from the requirement itself
(data-centric: table extension vs. separate table; process: event-driven vs.
direct integration; reporting: query object vs. API page, etc.).

After agents complete:
1. Collect all outputs (proposal, critique, falsification from each).
2. Facilitate cross-architect debate — challenge weak points, ask architects
   to respond to each other's critiques.
3. Synthesise the winner or create a hybrid from the best elements.

Spawn count guidance: 2 for SIMPLE/MEDIUM; 3 for COMPLEX. Omit if
TRIVIAL — route directly to a developer.

## Pattern 2: Quick Analysis (×1 serial)

Used by /al-dev-fix (non-trivial path).

Spawn **one** `al-dev-solution-architect` with a time-bounded prompt (5 min
max). Ask for:
1. Root cause hypothesis (2-3 sentences)
2. Recommended fix approach (bullet points)
3. Files that need changes
4. Risks/side effects to watch for

After the agent returns, review the analysis yourself:
- Does the root cause make sense?
- Is the fix approach sound?
- Are there risks?

If the approach needs refinement, engage the architect directly (one
revision pass). After confirming, spawn a developer with the approved
approach.

## Adding a New Caller

Add the new calling skill here with its pattern type, then document any
structural variation (e.g. different model tier, different output format).
```

- [ ] **Step 2: Verify the file was created and is non-empty**

Run:
```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/architect-invocation-patterns.md
```
Expected: `46` (or within ±2 of that — exact line count depends on trailing newline). Must be non-zero.

- [ ] **Step 3: Confirm no forbidden patterns**

Run:
```bash
grep -nE '\[date\]|TODO|TBD' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/architect-invocation-patterns.md
```
Expected: no output (exit code 1).

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/architect-invocation-patterns.md
git -C /Users/russelllaing/al-dev-shared status
```

Confirm only `profile-al-dev-shared/knowledge/architect-invocation-patterns.md` is staged. Then:

```bash
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
docs(knowledge): add architect-invocation-patterns knowledge doc

Documents the two structural patterns for spawning al-dev-solution-architect:
competitive debate (×2-3 parallel, used by /al-dev-plan) and quick analysis
(×1, used by /al-dev-fix). Mirrors the precedent set by review-panel-pattern.md.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Reference the new knowledge doc from al-dev-plan and al-dev-fix

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-plan/SKILL.md` (Phase 2 header block)
- Modify: `profile-al-dev-shared/skills/al-dev-fix/SKILL.md` (Step 2b header block)

Read both files before editing. Do NOT use Write to overwrite them — use Edit with exact string matches.

- [ ] **Step 1: Add reference to al-dev-plan SKILL.md**

In `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`, find the Phase 2 block that begins:

```
## Phase 2: Spawn Architect Team (2-3 agents)

Before spawning, derive 2-3 meaningfully different starting
```

Replace with:

```
## Phase 2: Spawn Architect Team (2-3 agents)

Follow the **Competitive Debate** pattern in
`knowledge/architect-invocation-patterns.md`.

Before spawning, derive 2-3 meaningfully different starting
```

- [ ] **Step 2: Add reference to al-dev-fix SKILL.md**

In `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`, find the Step 2b block that begins:

```
### Step 2b: Non-Trivial Fix (10-20 min)

```text
For non-trivial fixes:
```

Replace with:

```
### Step 2b: Non-Trivial Fix (10-20 min)

Follow the **Quick Analysis** pattern in
`knowledge/architect-invocation-patterns.md`.

```text
For non-trivial fixes:
```

- [ ] **Step 3: Verify both references exist**

Run:
```bash
grep -n "architect-invocation-patterns" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-plan/SKILL.md \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-fix/SKILL.md
```
Expected: two lines, one from each file.

- [ ] **Step 4: Verify line counts are preserved (not collapsed)**

Run:
```bash
wc -l \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-plan/SKILL.md \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-fix/SKILL.md
```
Expected: al-dev-plan ≥ 370 lines (was 370); al-dev-fix ≥ 400 lines (was 400). If either drops significantly, the Edit collapsed lines — abort and re-read the file.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/skills/al-dev-plan/SKILL.md \
  profile-al-dev-shared/skills/al-dev-fix/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
feat(skills): reference architect-invocation-patterns from plan and fix

Both /al-dev-plan (Phase 2) and /al-dev-fix (Step 2b) now point to the
canonical knowledge doc for their respective architect spawn patterns,
mirroring the review-panel-pattern.md precedent.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Update Layer 1 diagram — add Perf, Lint, and Handoff nodes

**Files:**
- Modify: `docs/al-dev-plugin-map.md` (the Layer 1 mermaid diagram block only — lines ~14–58)

Three additions in one edit:
1. `/al-dev-perf` as a dashed tributary feeding Plan and FixDirect
2. `/al-dev-lint` node off Develop with a dashed feedback arrow to FixDirect
3. `/al-dev-handoff` as a dashed post-commit node alongside ReleaseNotes

Read `docs/al-dev-plugin-map.md` before editing. Use Edit with exact string matches — do NOT Write the whole file.

- [ ] **Step 1: Add Perf tributary lines**

Find the pre-planning tributary block:
```
    Interview("al-dev-interview") -.->|interview-requirements.md| Plan

    %% Entry points
```

Replace with:
```
    Interview("al-dev-interview") -.->|interview-requirements.md| Plan
    Perf("al-dev-perf") -.->|perf-analysis.md| Plan
    Perf -.->|perf-analysis.md| FixDirect

    %% Entry points
```

- [ ] **Step 2: Add Lint feedback loop section**

Find the main development spine block:
```
    %% Complexity gate within plan
    Note["Trivial requests<br/>route to /fix"] -.-> Plan
```

Replace with:
```
    %% Lint feedback loop
    Develop -.-> Lint("al-dev-lint")
    Lint -.->|lint-report.md| FixDirect

    %% Complexity gate within plan
    Note["Trivial requests<br/>route to /fix"] -.-> Plan
```

- [ ] **Step 3: Add Handoff post-commit node**

Find the outputs block:
```
    Git -.-> ReleaseNotes("al-dev-release-notes")
    ReleaseNotes --> Notes(["✓ release notes"])
    Support --> Reply(["✓ customer reply"])
```

Replace with:
```
    Git -.-> ReleaseNotes("al-dev-release-notes")
    ReleaseNotes --> Notes(["✓ release notes"])
    Git -.-> Handoff("al-dev-handoff")
    Handoff --> HandoffOut(["✓ handoff-prompt.md"])
    Support --> Reply(["✓ customer reply"])
```

- [ ] **Step 4: Add style entries for new nodes**

Find the style block that ends with:
```
    style Decision1 fill:#ffe0b2
```

Replace with:
```
    style Perf fill:#fce4ec
    style Lint fill:#e0f2f1
    style Handoff fill:#fff3e0
    style HandoffOut fill:#c8e6c9
    style Decision1 fill:#ffe0b2
```

- [ ] **Step 5: Verify all three new node names appear in the diagram**

Run:
```bash
grep -n "Perf\|Lint\|Handoff" /Users/russelllaing/al-dev-shared/docs/al-dev-plugin-map.md | head -20
```
Expected: at least 2 lines for `Perf` (declaration + second arrow), 2 for `Lint`, 2 for `Handoff` (declaration + `HandoffOut`), and style entries for each.

- [ ] **Step 6: Verify diagram line count is preserved (not collapsed)**

Run:
```bash
wc -l /Users/russelllaing/al-dev-shared/docs/al-dev-plugin-map.md
```
Expected: original line count + ~9 new lines (3 for Perf, 3 for Lint, 2 for Handoff node+output, 4 style lines minus 0 removed = net +10 or so). Must be greater than the original count.

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add docs/al-dev-plugin-map.md
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
docs(plugin-map): add Perf, Lint, Handoff to Layer 1 lifecycle diagram

Three additive changes to the Layer 1 diagram:
- /al-dev-perf added as dashed pre-plan tributary (feeds Plan + Fix)
- /al-dev-lint added with dashed feedback loop to /al-dev-fix
- /al-dev-handoff added as dashed post-commit node alongside release-notes

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Mark all resolved suggestions as implemented in Observations

**Files:**
- Modify: `docs/al-dev-plugin-map.md` (Observations section only)

Read `docs/al-dev-plugin-map.md` before editing. Use Edit for each change individually.

- [ ] **Step 1: Mark the architect-invocation-patterns suggestion as implemented**

Find:
```
**Connect: al-dev-solution-architect invocation patterns**  
Observation: al-dev-solution-architect is spawned by two skills using structurally different patterns — /al-dev-plan uses it ×2-3 in parallel (competitive debate) and /al-dev-fix uses it ×1 (quick analysis). Both patterns live in-skill with no shared reference, unlike the three-reviewer panel which already has `knowledge/review-panel-pattern.md`.  
Suggestion: Document both patterns in `knowledge/architect-invocation-patterns.md`; reference from /al-dev-plan and /al-dev-fix. Mirrors the precedent set by review-panel-pattern.md.  
Trade-off: Small authoring cost; prevents drift when the architect agent definition changes and makes it easier to add a third skill that needs architect analysis.
```

Replace the first line of that block (just the header line) with:
```
**Connect: al-dev-solution-architect invocation patterns** ← implemented  
Status: Done — `knowledge/architect-invocation-patterns.md` created; referenced from /al-dev-plan Phase 2 and /al-dev-fix Step 2b.
```

And delete the Observation/Suggestion/Trade-off lines that follow, replacing the full block with:

```
**Connect: al-dev-solution-architect invocation patterns** ← implemented  
Status: Done — `knowledge/architect-invocation-patterns.md` created; referenced from /al-dev-plan Phase 2 and /al-dev-fix Step 2b.
```

- [ ] **Step 2: Mark the support ticket suggestion as already-implemented**

Find:
```
**Extend: /al-dev-support — integrated ticket lookup**  
Observation: Support queries almost always begin by fetching a ticket. Users must manually invoke /al-dev-ticket then /al-dev-support. If a ticket ID is passed directly to /al-dev-support, the ticket-fetch phase could be folded in, reducing a two-step workflow to one.  
Suggestion: Extend /al-dev-support to accept an optional `[ticket-id]` argument; if present, run the ticket-fetch phase inline before research. /al-dev-ticket remains useful for standalone ticket inspection.  
Trade-off: Requires editing /al-dev-support SKILL.md; the two-step flow still works for users who prefer it.
```

Replace with:
```
**Extend: /al-dev-support — integrated ticket lookup** ← already implemented  
Status: Done (pre-existing) — /al-dev-support Step 1 already handles `FD-NNNN`/numeric ticket IDs inline; dispatches al-dev-ticket-agent before research. No change required.
```

- [ ] **Step 3: Mark the Perf tributary suggestion as implemented**

Find:
```
**Extend: Layer 1 — /al-dev-perf as a pre-plan tributary**  
Observation: /al-dev-perf produces `perf-analysis.md` but does not appear anywhere in the Layer 1 diagram. Like /al-dev-explore and /al-dev-interview, its output can inform /al-dev-plan (scope decisions around optimisation) or /al-dev-fix (targeted fix targets). It is a missing optional tributary.  
Suggestion: Add /al-dev-perf as a dashed tributary in Layer 1, with `perf-analysis.md` feeding /al-dev-plan and /al-dev-fix alongside the existing explore-findings.md arrows.  
Trade-off: Diagram-only change; closes a real gap in lifecycle documentation with zero code disruption.
```

Replace with:
```
**Extend: Layer 1 — /al-dev-perf as a pre-plan tributary** ← implemented  
Status: Done — /al-dev-perf added as dashed tributary in Layer 1, feeding /al-dev-plan and /al-dev-fix via `perf-analysis.md`.
```

- [ ] **Step 4: Mark the Handoff post-commit suggestion as implemented**

Find:
```
**Extend: Layer 1 — /al-dev-handoff as a post-commit exit path**  
Observation: /al-dev-handoff packages context for cross-repo session migration and logically belongs at the end of the development spine (after /al-dev-commit), alongside /al-dev-release-notes. It does not appear in Layer 1 at all, making it invisible to users scanning the lifecycle diagram.  
Suggestion: Add /al-dev-handoff as a dashed post-commit node in Layer 1, labelled `handoff-prompt.md`, alongside the /al-dev-release-notes branch.  
Trade-off: Diagram-only update; improves discoverability with no code change.
```

Replace with:
```
**Extend: Layer 1 — /al-dev-handoff as a post-commit exit path** ← implemented  
Status: Done — /al-dev-handoff added as dashed post-commit node in Layer 1 alongside /al-dev-release-notes.
```

- [ ] **Step 5: Mark the lint feedback loop suggestion as implemented**

Find:
```
**Extend: Layer 1 — lint → fix feedback loop**  
Observation: /al-dev-lint produces `lint-report.md` but its output has no downstream connection in Layer 1. When lint surfaces violations the natural next step is /al-dev-fix; that path is implied but undocumented.  
Suggestion: Add a dashed arrow from /al-dev-lint to /al-dev-fix in Layer 1, labelled `lint-report.md → fix violations`, to make the remediation path explicit.  
Trade-off: Diagram-only change; guides new users to the correct next step after a lint run.
```

Replace with:
```
**Extend: Layer 1 — lint → fix feedback loop** ← implemented  
Status: Done — /al-dev-lint node added in Layer 1 (dashed off Develop), with dashed `lint-report.md` feedback arrow to /al-dev-fix.
```

- [ ] **Step 6: Update the Last updated line**

Find:
```
**Last updated:** 2026-05-18 (second-pass analysis; 5 new suggestions added)  
```

Replace with:
```
**Last updated:** 2026-05-18 (third-pass implementation; all suggestions resolved)  
```

- [ ] **Step 7: Verify all suggestion headers have a status marker**

Run:
```bash
grep -n "^\*\*Connect:\|^\*\*Merge:\|^\*\*Promote:\|^\*\*Extend:\|^\*\*Move:" \
  /Users/russelllaing/al-dev-shared/docs/al-dev-plugin-map.md
```
Expected: every line returned contains `← implemented` or `← already implemented`. If any line is missing the marker, that suggestion was not updated in Steps 1–5.

- [ ] **Step 8: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add docs/al-dev-plugin-map.md
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
docs(plugin-map): mark all remaining suggestions as implemented

All 5 suggestions resolved:
- Connect: architect-invocation-patterns (done)
- Extend: support ticket lookup (pre-existing, marked as already implemented)
- Extend: Layer 1 Perf tributary (done)
- Extend: Layer 1 Handoff post-commit (done)
- Extend: Layer 1 lint→fix feedback loop (done)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review

**Spec coverage check:**

| Suggestion | Task | Status |
|-----------|------|--------|
| Connect: architect-invocation-patterns | Task 1 (create doc) + Task 2 (add refs) | covered |
| Extend: support ticket lookup | Task 4 Step 2 (mark as pre-existing) | covered |
| Extend Layer 1 Perf | Task 3 Steps 1+4 (add node + style) | covered |
| Extend Layer 1 Handoff | Task 3 Steps 3+4 (add node + style) | covered |
| Extend Layer 1 lint→fix | Task 3 Steps 2+4 (add node+arrow + style) | covered |
| Update "Last updated" line | Task 4 Step 6 | covered |

**Placeholder scan:** No TBD, TODO, YYYY-MM-DD placeholders, or Co-Authored-By in code comments. The git trailer `Co-Authored-By` appears only in commit message heredocs (correct usage).

**Type consistency:**
- Node IDs in Task 3: `Perf`, `Lint`, `Handoff`, `HandoffOut`, `FixDirect` — all consistent with original diagram node IDs.
- `FixDirect` is already declared in the original diagram at `%% Entry points`. The Perf and Lint arrows reference it by ID after the diagram's `FixDirect("al-dev-fix")` declaration — consistent with how the original diagram references forward-declared nodes.
- Style entries in Step 4 use the same node IDs as the new diagram lines.

No gaps found.
