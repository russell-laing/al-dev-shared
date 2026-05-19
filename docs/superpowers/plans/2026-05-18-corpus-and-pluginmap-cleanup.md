# Corpus Cleanup, analyze-plugin-design Update, and Plugin Map Housekeeping

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 3 stale test cases in `skill-test-trigger-corpus.yaml`; add pre-planning tributary analysis to `analyze-plugin-design`; and clean up implemented suggestions in `docs/al-dev-plugin-map.md`.

**Architecture:** Three independent tasks touching three different files. Task 1 and Task 2 have no shared files. Task 3 touches `docs/al-dev-plugin-map.md` — the same file `analyze-plugin-design` rewrites when it runs, but cleanup happens in a static commit so there is no conflict.

> **Note on al-dev-interview in Layer 1:** al-dev-interview is **already** in the Layer 1 lifecycle overview diagram (added 2026-05-18): `Interview("al-dev-interview") -.->|interview-requirements.md| Plan`. No diagram change is needed. Task 2 adds it to `analyze-plugin-design`'s analytical vocabulary; Task 3 updates the description text around the diagram.

**Tech Stack:** YAML (corpus), Markdown (skill files, plugin map). No code compilation. Verification is grep + wc -l.

---

## File Map

| Task | Files Modified |
|------|---------------|
| 1 | `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml` |
| 2 | `.claude/skills/analyze-plugin-design/SKILL.md` |
| 3 | `docs/al-dev-plugin-map.md` |

All paths relative to `/Users/russelllaing/al-dev-shared/`.

---

## Task 1: Fix skill-test-trigger-corpus.yaml — 3 stale al-dev-autonomous entries

**Files:**
- Modify: `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml`

**Context:** When `al-dev-autonomous` was archived and merged into `al-dev-develop --autonomous`, the skill-test corpus was not updated. Three test cases still expect `al-dev-autonomous`, which is no longer an active skill. The skill-test harness will report false failures when it next runs.

The 3 stale entries are in the `# --- al-dev-autonomous ---` section (lines 32–38):
```yaml
  # --- al-dev-autonomous -------------------------------------------------
  - prompt: "implement the plan automatically and keep compiling until it builds"
    expected: al-dev-autonomous
  - prompt: "autonomous mode: build the feature and self-correct compile errors"
    expected: al-dev-autonomous
  - prompt: "just keep iterating on the code until al-compile is clean"
    expected: al-dev-autonomous
```

These prompts describe behavior now provided by `al-dev-develop --autonomous`. The prompts are still good; only the `expected` and the section comment need changing.

- [ ] **Step 1: Read the corpus file**

  ```bash
  cat profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml
  ```

  Confirm the 3 stale entries are present exactly as shown above.

- [ ] **Step 2: Replace the al-dev-autonomous section**

  Use the Edit tool. Find this exact block:

  ```
    # --- al-dev-autonomous -------------------------------------------------
    - prompt: "implement the plan automatically and keep compiling until it builds"
      expected: al-dev-autonomous
    - prompt: "autonomous mode: build the feature and self-correct compile errors"
      expected: al-dev-autonomous
    - prompt: "just keep iterating on the code until al-compile is clean"
      expected: al-dev-autonomous
  ```

  Replace with:

  ```
    # --- al-dev-develop (--autonomous mode) --------------------------------
    - prompt: "implement the plan automatically and keep compiling until it builds"
      expected: al-dev-develop
    - prompt: "autonomous mode: build the feature and self-correct compile errors"
      expected: al-dev-develop
    - prompt: "just keep iterating on the code until al-compile is clean"
      expected: al-dev-develop
  ```

- [ ] **Step 3: Verify no al-dev-autonomous entries remain**

  ```bash
  grep -n "al-dev-autonomous" profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml
  ```

  Expected: no output.

- [ ] **Step 4: Verify the 3 prompts are still present with correct expected**

  ```bash
  grep -A1 "keep compiling\|self-correct compile\|al-compile is clean" \
    profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml
  ```

  Expected: each prompt followed by `expected: al-dev-develop`.

- [ ] **Step 5: Scan for forbidden patterns**

  ```bash
  grep -n '\[date\]\|YYYY-MM-DD\|TODO\|TBD\|Co-Authored-By\|claude:\|copilot:' \
    profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml --color=never || true
  ```

  Expected: no output.

- [ ] **Step 6: Commit**

  ```bash
  git add profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml
  git commit -m "$(cat <<'EOF'
  fix(corpus): update 3 al-dev-autonomous test cases to al-dev-develop

  al-dev-autonomous was archived and merged into al-dev-develop --autonomous.
  The skill-test corpus still expected the archived skill name, which would
  cause false failures on the next /skill-test run.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  EOF
  )"
  ```

---

## Task 2: Update analyze-plugin-design SKILL.md — add pre-planning tributary lens

**Files:**
- Modify: `.claude/skills/analyze-plugin-design/SKILL.md`

**Context:** The `analyze-plugin-design` skill applies four analytical lenses to the plugin map but has no lens for the pre-planning tributary skills — skills like `/al-dev-interview` and `/al-dev-explore` that produce structured outputs feeding into the planning phase before implementation begins.

`/al-dev-interview` is the AL-development equivalent of `superpowers:brainstorming`: it pre-researches base app objects via the AL symbols MCP and conducts a structured BC/AL interview, producing a formal requirements document (`interview-requirements.md`) consumed by `/al-dev-plan`. Without an explicit lens for this category, future analysis runs may miss whether new pre-planning skills are represented in the lifecycle diagram.

Two additions are needed:
1. A 5th inventory item in **Step 1** (build working list of pre-planning tributaries)
2. A new **Lens E** in **Step 2** (analyze pre-planning skills for diagram inclusion and handoff coverage)
3. A note in **Step 3** to avoid re-suggesting already-implemented patterns

- [ ] **Step 1: Read the current SKILL.md**

  Read `.claude/skills/analyze-plugin-design/SKILL.md` in full. Note the exact text of Step 1 item 4 and the Lens D section ending.

- [ ] **Step 2: Add item 5 to the Step 1 working lists**

  Find this exact text:
  ```
  4. **No-agent skills** — list skills whose drill-down contains only `(skill itself)`
     nodes (no dedicated agent spawned).
  
  If an argument was passed, restrict analysis to that category
  ```

  Replace with:
  ```
  4. **No-agent skills** — list skills whose drill-down contains only `(skill itself)`
     nodes (no dedicated agent spawned).

  5. **Pre-planning tributaries** — list skills that produce output files consumed
     by `/al-dev-plan` or `/al-dev-investigate` before implementation begins (e.g.
     `interview-requirements.md`, `explore-findings.md`). For each, note whether it
     appears in the Layer 1 diagram as a dashed tributary arrow (`-.->`) rather than
     a main-spine node.

  If an argument was passed, restrict analysis to that category
  ```

  Verify:
  ```bash
  grep -n "Pre-planning tributaries" .claude/skills/analyze-plugin-design/SKILL.md
  ```
  Expected: 1 match.

- [ ] **Step 3: Add Lens E before Step 3**

  Find this exact text (the separator and heading before Step 3):
  ```
  ---
  
  ## Step 3 — Draft Suggestions
  ```

  Replace with:
  ```
  ### Lens E — Pre-planning and Brainstorming Skills

  Pre-planning skills produce structured outputs that feed into the planning phase.
  They are optional but high-value tributaries to the main development spine.

  **Canonical pre-planning skills in this plugin:**

  - `/al-dev-interview` — requirements-gathering for AL/BC features. Analogous to
    `superpowers:brainstorming` in the general superpowers skill set, but domain-
    specific: conducts a structured BC/AL interview, pre-researches base app objects
    via the AL symbols MCP, and produces a formal requirements document with
    acceptance-criteria tokens (`interview-requirements.md`).
  - `/al-dev-explore` — fast codebase investigation producing `explore-findings.md`,
    consumed by `/al-dev-investigate` and `/al-dev-plan`.

  For each pre-planning skill found in the inventory, ask:
  - Does it appear in the Layer 1 diagram as a dashed tributary (`-.->`) rather
    than a main-spine node?
  - Is its output filename referenced in the Layer 1 handoff labels?
  - Is there a downstream skill that explicitly names it as an input?

  Flag any pre-planning skill that is active but absent from the Layer 1 diagram as
  an **Extend** candidate. Flag any skill that feeds a downstream step but whose
  output is unnamed in the diagram as a labelling gap.

  ---

  ## Step 3 — Draft Suggestions
  ```

  Verify:
  ```bash
  grep -n "Lens E\|Pre-planning and Brainstorming" .claude/skills/analyze-plugin-design/SKILL.md
  ```
  Expected: at least 1 match for each.

- [ ] **Step 4: Add a "check for already-implemented patterns" note to Step 3**

  In Step 3 — Draft Suggestions, find:
  ```
  Write 3–6 high-quality suggestions. Skip patterns that don't yield a real
  improvement. Use these templates:
  ```

  Replace with:
  ```
  Write 3–6 high-quality suggestions. Skip patterns that don't yield a real
  improvement. Before writing a suggestion, check the current `## Observations`
  section — if a suggestion identical or equivalent to yours is already marked
  `← implemented`, skip it. Use these templates:
  ```

  Verify:
  ```bash
  grep -n "already marked" .claude/skills/analyze-plugin-design/SKILL.md
  ```
  Expected: 1 match.

- [ ] **Step 5: Verify line count increased (no content lost)**

  ```bash
  wc -l .claude/skills/analyze-plugin-design/SKILL.md
  ```

  Expected: 215+ lines (was 196 before Task 2; added ~25 lines).

- [ ] **Step 6: Scan for forbidden patterns**

  ```bash
  grep -n '\[date\]\|YYYY-MM-DD\|TODO\|TBD\|Co-Authored-By\|claude:\|copilot:' \
    .claude/skills/analyze-plugin-design/SKILL.md --color=never || true
  ```

  Expected: no output.

- [ ] **Step 7: Commit**

  ```bash
  git add .claude/skills/analyze-plugin-design/SKILL.md
  git commit -m "$(cat <<'EOF'
  feat(analyze-plugin-design): add Lens E for pre-planning tributary skills

  Adds a fifth Step 1 inventory item and a new Lens E covering pre-planning
  and brainstorming skills (al-dev-interview, al-dev-explore). Lens E checks
  whether each pre-planning skill appears in the Layer 1 diagram as a dashed
  tributary. Also adds a guard in Step 3 to skip re-suggesting patterns
  already marked as implemented in the Observations section.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  EOF
  )"
  ```

---

## Task 3: Clean up implemented suggestions in docs/al-dev-plugin-map.md

**Files:**
- Modify: `docs/al-dev-plugin-map.md`

**Context:** Five suggestions in the `## Observations` section are still showing as active even though all were implemented in the 2026-05-18 architectural suggestions plan:

| Suggestion | Implemented via |
|---|---|
| Connect: /al-dev-explore and /al-dev-perf — shared exploration backbone | `knowledge/explore-subagent-pattern.md` created |
| Promote: Explore subagent spawn pattern | same file; all 3 callers reference it |
| Move: /al-dev-align → .claude/skills/ | SKILL.md moved; Python script stays in plugin |
| Extend: Layer 1 — explore and interview missing | Both now in Layer 1 as dashed tributaries |
| Extend: Layer 1 — release-notes missing | al-dev-release-notes now in Layer 1 |

Also: the Layer 1 description text says "three entry paths" but the diagram now has pre-planning tributaries (explore, interview) and a post-commit output (release-notes), so the description is outdated.

Read the file fully before starting edits. Make each edit with the Edit tool using exact strings.

- [ ] **Step 1: Read docs/al-dev-plugin-map.md**

  Read the full file. Note current line count with:
  ```bash
  wc -l docs/al-dev-plugin-map.md
  ```

- [ ] **Step 2: Update the Layer 1 description text**

  Find:
  ```
  This diagram shows the three entry paths and how they connect through the main development spine.
  ```

  Replace with:
  ```
  This diagram shows pre-planning tributaries (dashed, optional), the three main entry points, and the development spine through to post-commit output.
  ```

  Verify:
  ```bash
  grep -n "three entry paths\|pre-planning tributaries.*dashed" docs/al-dev-plugin-map.md
  ```
  Expected: 0 matches for "three entry paths"; 1 match for the new text.

- [ ] **Step 3: Mark "Connect: /al-dev-explore and /al-dev-perf" as implemented**

  Find this exact block:
  ```
  **Connect: /al-dev-explore and /al-dev-perf — shared exploration backbone**  
  Observation: Both follow an identical structure — skill reads context → spawn Explore subagent ×1 → write `.dev/` analysis file. The only difference is the analytical lens (general vs. performance).  
  Suggestion: Document a shared "focused exploration" pattern in `knowledge/explore-subagent-pattern.md` covering the canonical spawn template, context-loading steps, and output format. Both skills reference it; the domain focus is the only local customisation.  
  Trade-off: Slightly more indirection; eliminates drift if the Explore subagent API changes.
  ```

  Replace with:
  ```
  **Connect: /al-dev-explore and /al-dev-perf — shared exploration backbone** ← implemented  
  Observation: Both skills share an identical spawn structure.  
  Status: Done — `knowledge/explore-subagent-pattern.md` created; al-dev-explore, al-dev-perf, and al-dev-investigate all reference it.
  ```

- [ ] **Step 4: Mark "Promote: Explore subagent spawn pattern" as implemented**

  Find this exact block:
  ```
  **Promote: Explore subagent spawn pattern**  
  Observation: Three skills (investigate, explore, perf) each independently author their Explore subagent invocation. A fourth skill using Explore would have no canonical template to follow.  
  Suggestion: `knowledge/explore-subagent-pattern.md` (from the Connect suggestion above) doubles as this canonical template. All three callers update their spawn directives to reference it.  
  Trade-off: One extra file in knowledge/; invocations stay locally readable with a pointer for updates.
  ```

  Replace with:
  ```
  **Promote: Explore subagent spawn pattern** ← implemented  
  Observation: Three skills independently authored their Explore subagent invocation.  
  Status: Done — `knowledge/explore-subagent-pattern.md` is the canonical template; all three callers reference it.
  ```

- [ ] **Step 5: Mark "Move: /al-dev-align" as implemented**

  Find this exact block:
  ```
  ### Move candidates
  
  **Move: /al-dev-align → .claude/skills/**
  Observation: This skill's sole purpose is maintaining the plugin's own alignment with harness repos — it has no value to AL developers consuming the distributed plugin. It audits the plugin's internal consistency, not the user's AL code.
  Signals: internal path refs (✗), self-audit purpose (✓), no spawned agents (✓).
  Suggestion: Move `profile-al-dev-shared/skills/al-dev-align/` to `.claude/skills/al-dev-align/` and update the plugin map scope line to exclude it.
  Trade-off: Skill remains available in this project; removed from the distributed plugin so consumers don't see a maintenance-only skill that does nothing useful for them.
  ```

  Replace with:
  ```
  ### Move candidates
  
  **Move: /al-dev-align → .claude/skills/** ← implemented  
  Observation: Maintenance-only skill with no value to distributed plugin consumers.  
  Status: Done — SKILL.md moved to `.claude/skills/al-dev-align/`; Python script stays in plugin for path resolution.
  ```

- [ ] **Step 6: Mark both Extension opportunities as implemented**

  Find this exact block:
  ```
  ### Extension opportunities
  
  **Extend: Layer 1 — /al-dev-explore and /al-dev-interview missing as pre-plan tributaries**  
  Observation: Both skills produce files consumed directly by the planning phase (explore-findings.md → investigate/plan, interview-requirements.md → plan), but neither appears in the Layer 1 lifecycle overview. The pre-planning phase is invisible in the diagram.  
  Suggestion: Add /al-dev-explore and /al-dev-interview as optional input nodes in Layer 1 — tributary arrows feeding into /al-dev-investigate and /al-dev-plan respectively, not on the main spine.
  
  **Extend: Layer 1 — /al-dev-release-notes missing as post-commit output**  
  Observation: The lifecycle ends at `al-dev-commit → ✓ git commit`. /al-dev-release-notes is a natural post-commit step (consumes git hashes, produces release notes) but is not connected to the lifecycle overview.  
  Suggestion: Add /al-dev-release-notes as an output node from the `✓ git commit` terminal in Layer 1.
  ```

  Replace with:
  ```
  ### Extension opportunities
  
  **Extend: Layer 1 — /al-dev-explore and /al-dev-interview as pre-plan tributaries** ← implemented  
  Status: Done — both appear in Layer 1 as dashed tributary arrows feeding Investigate and Plan.
  
  **Extend: Layer 1 — /al-dev-release-notes as post-commit output** ← implemented  
  Status: Done — /al-dev-release-notes appears in Layer 1 as a dashed post-commit node after `✓ git commit`.
  ```

- [ ] **Step 7: Update the Last Updated line**

  Find:
  ```
  **Last updated:** 2026-05-18 (al-dev-autonomous merged into al-dev-develop --autonomous; al-dev-align moved to .claude/skills/)  
  ```

  Note: the `old_string` must include the two trailing spaces (markdown hard break) at the end of the line — they exist in the file between the `)` and the newline.

  Replace with:
  ```
  **Last updated:** 2026-05-18 (all 2026-05-18 architectural suggestions implemented; observations cleaned up)  
  ```

  Note: preserve the two trailing spaces in `new_string` — they are a markdown hard break keeping Last Updated and Scope on separate rendered lines.

- [ ] **Step 8: Verify implemented markers appear for all 5 suggestions**

  ```bash
  grep -n "← implemented" docs/al-dev-plugin-map.md
  ```

  Expected: 7 matches total (2 existing from the previous plan + 5 new from this task).

- [ ] **Step 9: Verify file line count decreased (entries shortened)**

  ```bash
  wc -l docs/al-dev-plugin-map.md
  ```

  Expected: approximately 15–25 lines FEWER than the pre-task count (long suggestion blocks replaced with short status lines).

- [ ] **Step 10: Scan for forbidden patterns**

  ```bash
  grep -n '\[date\]\|TODO\|TBD\|Co-Authored-By\|claude:\|copilot:' \
    docs/al-dev-plugin-map.md --color=never || true
  ```

  Expected: no output. (`YYYY-MM-DD` may appear in the Last updated date — acceptable as a date value, not a template placeholder.)

- [ ] **Step 11: Commit**

  ```bash
  git add docs/al-dev-plugin-map.md
  git commit -m "$(cat <<'EOF'
  docs(plugin-map): mark all 2026-05-18 suggestions implemented; update Layer 1 desc

  Marks Connect (explore-perf backbone), Promote (explore spawn pattern),
  Move (al-dev-align), and both Extend (Layer 1 tributaries + release-notes)
  suggestions as implemented. Updates Layer 1 description text to mention
  pre-planning tributaries and post-commit output.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  EOF
  )"
  ```

---

## Acceptance Criteria (full plan)

Before marking complete, verify:

- [ ] `grep -n "al-dev-autonomous" profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml` returns no output
- [ ] `grep -n "Pre-planning tributaries" .claude/skills/analyze-plugin-design/SKILL.md` returns 1 match
- [ ] `grep -n "Lens E" .claude/skills/analyze-plugin-design/SKILL.md` returns 1 match
- [ ] `grep -c "← implemented" docs/al-dev-plugin-map.md` returns 7
- [ ] Layer 1 description no longer says "three entry paths"
- [ ] `git log --oneline -3` shows 3 commits (one per task)
