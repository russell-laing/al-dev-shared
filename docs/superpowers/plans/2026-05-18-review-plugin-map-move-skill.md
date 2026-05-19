# Review Plugin Map — Move Candidate Detection (Phase 7) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Phase 7 to the `review-plugin-map` skill so it detects skills that belong in `.claude/skills/` rather than the distributed plugin and reports them as `Move:` suggestions in `docs/al-dev-plugin-map.md`.

**Architecture:** Single skill file edit — append a `## Phase 7: Detect Move Candidates` section to `.claude/skills/review-plugin-map/SKILL.md`. Phase 7 runs after Phase 6, scores each active skill against three detection signals, appends `Move:` entries to the plugin map's Architectural suggestions section, and commits separately. If $ARGUMENTS names a skill, Phase 7 is skipped.

**Tech Stack:** Markdown skill file, bash commands in skill body, `docs/al-dev-plugin-map.md` as output target.

---

## Files

- Modify: `.claude/skills/review-plugin-map/SKILL.md` — append Phase 7 section (after line 151, the current end of the file)

No other files change. Phase 7 writes to `docs/al-dev-plugin-map.md` at runtime, but the plan task is only editing the skill itself.

---

### Task 1: Verify acceptance criteria checklist before editing

Read the current skill end and confirm where Phase 7 must be inserted.

- [ ] **Step 1: Record the current line count**

```bash
wc -l .claude/skills/review-plugin-map/SKILL.md
```

Expected: 151 lines. Note this — post-edit count must be 151 + the Phase 7 block.

- [ ] **Step 2: Confirm the last line of the current skill**

Read lines 140–151 of `.claude/skills/review-plugin-map/SKILL.md` and confirm the file ends with:

```
Report what changed and what was verified as already correct.
```

(No trailing content after that line.) Phase 7 appends after this line.

- [ ] **Step 3: State the acceptance criteria as a checklist**

Before editing, confirm the following are the acceptance criteria you will verify after editing:

```
AC1: Phase 7 section appears at end of SKILL.md with detection table and output format template
AC2: Detection checks all three signals; a skill scoring 2+ is flagged
AC3: Output follows **Move: /skill-name → .claude/skills/** with Observation/Signals/Suggestion/Trade-off
AC4: Phase 7 commits separately from Phase 6 (or skips if no candidates found)
AC5: When $ARGUMENTS names a skill, Phase 7 is skipped with the stated note
AC6: al-dev-align would be flagged if the skill were run (manual: confirm signal scoring)
```

---

### Task 2: Insert Phase 7 into SKILL.md

- [ ] **Step 1: Append Phase 7 content**

Open `.claude/skills/review-plugin-map/SKILL.md` and append the following block after the last line (`Report what changed and what was verified as already correct.`):

````markdown

---

## Phase 7: Detect Move Candidates

> **Skip if** `$ARGUMENTS` names a specific skill — this is a scoped accuracy-check run. Note: *"Move candidate scan skipped — run without arguments for full analysis."* and stop.

Scan every active skill identified in Phase 1 for signals that it belongs in the project-local `.claude/skills/` directory rather than the distributed plugin. Report findings only — do not move any files.

### Detection signals

Score each active skill against these three signals:

| Signal | What to check |
|--------|---------------|
| **Internal path references** | Skill body contains paths like `profile-al-dev-shared/`, `.claude/`, or repo-root filenames (e.g. `marketplace.json`) that only resolve inside this repo |
| **Self-audit purpose** | Skill's stated purpose is maintaining or auditing the plugin itself — alignment checks, map reviews, design analysis — not serving AL developers |
| **No spawned agents** | No `al-dev-shared:` agent type appears in the skill body |

A skill scoring **2 or more signals** is a Move candidate.

Agents are not scanned separately. If a flagged skill is the sole caller of an agent, note the agent as a side-effect consideration in the Suggestion field.

### Output

For each Move candidate, append to the `### Architectural suggestions` section of `docs/al-dev-plugin-map.md`:

```markdown
**Move: /skill-name → .claude/skills/**
Observation: [Why this skill has no value to plugin consumers.]
Signals: internal path refs (✓/✗), self-audit purpose (✓/✗), no spawned agents (✓/✗).
Suggestion: Move `profile-al-dev-shared/skills/<skill-name>/` to `.claude/skills/<skill-name>/` and update the plugin map scope line to exclude it.
Trade-off: Skill remains available in this project; removed from the distributed plugin.
```

If no candidates are found, append a `### Move candidates` subheading with a single line:

```markdown
### Move candidates

None detected.
```

### Commit

If one or more candidates were found:

```bash
git -C . add docs/al-dev-plugin-map.md
git -C . commit -m "docs: add Move candidates to plugin map architectural suggestions"
```

If no candidates were found, skip the commit entirely.
````

- [ ] **Step 2: Verify line count increased correctly**

```bash
wc -l .claude/skills/review-plugin-map/SKILL.md
```

Expected: greater than 151 (the Phase 7 block adds ~55 lines, so expect ~206). If the count is still 151, the append failed — retry Step 1.

- [ ] **Step 3: Confirm Phase 7 header appears at end of file**

```bash
grep -n "Phase 7" .claude/skills/review-plugin-map/SKILL.md
```

Expected output (one line):

```
<line-number>:## Phase 7: Detect Move Candidates
```

- [ ] **Step 4: Confirm all three signal rows are present**

```bash
grep -c "Internal path references\|Self-audit purpose\|No spawned agents" .claude/skills/review-plugin-map/SKILL.md
```

Expected: `3`

- [ ] **Step 5: Confirm the Move output template is present**

```bash
grep -n "Move: /skill-name" .claude/skills/review-plugin-map/SKILL.md
```

Expected: one match showing the template line `**Move: /skill-name → .claude/skills/**`

- [ ] **Step 6: Confirm the scoped invocation guard is present**

```bash
grep -n "Move candidate scan skipped" .claude/skills/review-plugin-map/SKILL.md
```

Expected: one match.

- [ ] **Step 7: Manual AC6 verification — confirm al-dev-align would score 2+**

Read `profile-al-dev-shared/skills/al-dev-align/SKILL.md` and score it:

- Signal 1 (internal path refs): Does body contain `profile-al-dev-shared/` or `$AL_DEV_SHARED_PLUGIN_ROOT`? → Check for `yes`
- Signal 2 (self-audit purpose): Is the stated purpose auditing the plugin? → Check for `yes`
- Signal 3 (no spawned agents): Does body contain `al-dev-shared:` agent spawn? → Check for `no`

Expected: 2 or 3 signals score `yes/yes` — al-dev-align is a valid candidate. If it scores fewer than 2, the detection criteria are not calibrated correctly and you must revisit the signal definitions.

```bash
grep -c "profile-al-dev-shared/\|AL_DEV_SHARED_PLUGIN_ROOT\|marketplace.json" profile-al-dev-shared/skills/al-dev-align/SKILL.md
grep -c "al-dev-shared:" profile-al-dev-shared/skills/al-dev-align/SKILL.md
```

Expected: first command ≥ 1 (internal path refs present); second command = 0 (no spawned agents).

---

### Task 3: Commit the skill change

- [ ] **Step 1: Check git status — only the skill file should be modified**

```bash
git status
```

Expected:
```
modified:   .claude/skills/review-plugin-map/SKILL.md
```

No other files modified. If unexpected files appear, do not commit — investigate before proceeding.

- [ ] **Step 2: Scan for forbidden patterns in changed content**

```bash
git diff .claude/skills/review-plugin-map/SKILL.md | grep -E "\[date\]|YYYY-MM-DD|Co-Authored-By|claude:|copilot:"
```

Expected: no output. If any match is found, fix the pattern in the skill file before committing.

- [ ] **Step 3: Commit**

```bash
git -C . add .claude/skills/review-plugin-map/SKILL.md
git -C . commit -m "$(cat <<'EOF'
feat(review-plugin-map): add Phase 7 Move candidate detection

Extends the skill with a post-commit phase that scores active skills
against three signals (internal path refs, self-audit purpose, no spawned
agents). Skills scoring 2+ are reported as Move: suggestions in the
plugin map's Architectural suggestions section, committed separately.
Scoped runs ($ARGUMENTS set) skip Phase 7 with an explanatory note.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 4: Verify commit succeeded**

```bash
git log --oneline -3
```

Expected: the new commit appears at the top with the `feat(review-plugin-map):` subject.

---

## Self-Review Against Acceptance Criteria

| AC | Covered by |
|----|-----------|
| AC1: Phase 7 at end of SKILL.md with detection table and output template | Task 2 Step 3, 4, 5 |
| AC2: All three signals checked; 2+ → flagged | Task 2 Step 4; detection table in skill body |
| AC3: Output format `**Move: /skill-name → .claude/skills/**` with 4 fields | Task 2 Step 5 |
| AC4: Phase 7 commits separately from Phase 6 | Phase 7 Commit section in skill body |
| AC5: Skip Phase 7 when $ARGUMENTS names a skill | Task 2 Step 6 |
| AC6: al-dev-align would be flagged | Task 2 Step 7 |
