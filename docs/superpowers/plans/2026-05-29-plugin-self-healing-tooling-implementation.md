# Self-Healing Maintainer Tooling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modernize and consolidate the `al-dev-shared` maintainer tooling into a documented naming convention, symmetric lens agents, and a standing suggestions-only self-healing loop (`/plugin-health`) backed by a deterministic dependency-graph generator.

**Architecture:** Two sequenced phases. Phase 1 (cleanup) writes the naming-convention doc, renames the 10 agent lenses to a symmetric pattern, dogfoods the quality lenses against `.claude/`, and removes the unused `plugin-health-daemon`. Phase 2 (standing system) adds a `naming-convention-lens` agent, a `scripts/generate-plugin-graph.py` visualization generator, and the `/plugin-health` orchestrator skill that dispatches lenses with per-surface file lists and writes one ranked dossier per surface. Nothing is auto-edited — the loop only produces reviewable artifacts.

**Tech Stack:** Python 3.13 (stdlib only — `re`, `pathlib`, `unittest`, `importlib`), Markdown skill/agent definitions, Mermaid diagrams. Tests use the repo's `importlib.util.spec_from_file_location` + `unittest` pattern; fall back to the libexpat inline-test workaround (per `CLAUDE.md`) if `pytest` misbehaves.

**Source spec:** `docs/superpowers/specs/2026-05-29-plugin-self-healing-tooling-design.md`

---

## File Structure

**Created:**
- `docs/al-dev-naming-convention.md` — living reference doc; the enforced + advisory naming rules (Task 1)
- `.claude/agents/naming-convention-lens.md` — new haiku read-only lens (Task 5)
- `scripts/generate-plugin-graph.py` — deterministic dependency-graph generator (Task 6)
- `scripts/tests/test_generate_plugin_graph.py` — fixture-based unit tests for the generator (Task 6)
- `.claude/skills/plugin-health/SKILL.md` — suggestions-only orchestrator skill (Task 7)
- `scripts/tests/test_naming_convention.py` — convention-checker: asserts `.claude/` names match the doc (Task 8)
- `docs/al-dev-plugin-graph.md` — generated graph output (first written when the generator runs, Task 6)
- `docs/health/.gitkeep` — anchors the dossier output directory (Task 7)

**Renamed (Task 2):**
- `.claude/agents/design-lens-*.md` (5) → `.claude/agents/design-agent-lens-*.md`
- `.claude/agents/quality-lens-*.md` (5) → `.claude/agents/quality-agent-lens-*.md`

**Modified:**
- `scripts/validate-lens-agents.py` — `EXPECTED_AGENTS` updated for renames (Task 2) + `naming-convention-lens` added (Task 5)
- `.claude/skills/analyze-agent-design/SKILL.md` — dispatch list uses new `design-agent-lens-*` names (Task 2)
- `.claude/skills/audit-agent-quality/SKILL.md` — dispatch list uses new `quality-agent-lens-*` names (Task 2)
- `scripts/tests/test_validate_lens_agents.py` — example path string uses a renamed lens (Task 2)
- `.claude/agents/*` and `.claude/skills/*` — atomic quality fixes from the dogfood pass (Task 4)
- `CLAUDE.md`, `docs/al-dev-plugin-map.md`, `.claude/settings.local.json`, `.github/copilot-instructions.md` — remove `plugin-health-daemon` references (Task 3)

**Deleted (Task 3):**
- `.claude/skills/plugin-health-daemon/` (skill dir)
- `scripts/plugin-health-daemon.sh`

---

## Phase 1 — Cleanup

### Task 1: Naming-convention reference doc

**Files:**
- Create: `docs/al-dev-naming-convention.md`

This doc is the single source the `naming-convention-lens` (Task 5) and the convention-checker test (Task 8) read. It must stay harness-neutral (per `CLAUDE.md` output-boundary rule) — no harness-specific tokens.

- [ ] **Step 1: Write the convention doc**

Write `docs/al-dev-naming-convention.md` with exactly this content:

````markdown
# Maintainer Tooling Naming Convention

**Last updated:** 2026-05-29

This document defines how maintainer tools and their outputs are named. The
`naming-convention-lens` agent flags drift against it on every `/plugin-health`
run; `scripts/tests/test_naming_convention.py` enforces the **lens-agent** rule
mechanically. Keep this doc and those two checkers in sync.

## Tools

### Lens agents — ENFORCED

Pattern: `{dimension}-{object}-lens-{aspect}`

- `dimension` ∈ `design` | `quality`
- `object` ∈ `agent` | `skill`
- `aspect` — a short kebab-case noun for the specific lens (e.g. `tool-hygiene`,
  `bloat`, `name-fit`)

Examples: `design-agent-lens-tool-hygiene`, `quality-skill-lens-bloat`.

**Exception:** `naming-convention-lens` is a cross-object lens (it judges both
agents and skills) and intentionally omits the `{dimension}` and `{object}`
words. It is the only allowed deviation from the pattern.

### Maintainer skills — ADVISORY

Pattern: `{verb}-{object}-{aspect}`

- `verb` ∈ `review` | `analyze` | `audit` | `plan` | `sync` | …
- `object` ∈ `skill` | `agent` | `knowledge` | `map` | `plugin`

Examples: `audit-skill-quality`, `review-agent-map`, `plan-map-changes`.

This rule is advisory: pre-existing skills that predate the convention
(`projection-sync`, `align-harness-repos`) are grandfathered. New skills SHOULD
conform; the `naming-convention-lens` flags non-conforming names as Low-severity
suggestions rather than hard failures.

## Outputs

### Living docs — overwritten in place, no date

Pattern: `al-dev-{object}-{kind}.md`

Examples: `al-dev-plugin-map.md`, `al-dev-agent-map.md`, `al-dev-skill-quality.md`,
`al-dev-agent-quality.md`, `al-dev-knowledge-quality.md`, `al-dev-plugin-graph.md`.

### Point-in-time artifacts — dated

Pattern: `{dir}/YYYY-MM-DD-{surface}-{kind}.md`

- `surface` ∈ `plugin` (the distributed `profile-al-dev-shared/` surface)
  | `tooling` (the maintainer `.claude/` surface)

Examples: `docs/health/2026-05-29-plugin-health.md`,
`docs/health/2026-05-29-tooling-health.md`.

## Harness neutrality

Every output named above must use generic vocabulary (no harness-specific
tokens such as tool names or settings paths). The maintainer tooling itself may
remain harness-specific, but its produced documents must not.
````

- [ ] **Step 2: Verify the file persisted and is non-empty**

Run: `wc -l docs/al-dev-naming-convention.md`
Expected: a non-zero line count (~80 lines).

- [ ] **Step 3: Harness-neutrality check (grep for forbidden tokens)**

Run:
```bash
grep -nE "AskUserQuestion|ask_user|subagent_type|mcp__plugin_profile-claude|~/\.claude|~/\.copilot|Open Claude Code|Restart Claude Code" docs/al-dev-naming-convention.md
```
Expected: no output (exit 1 from grep = no matches = pass).

- [ ] **Step 4: Forbidden-pattern scan**

Run:
```bash
grep -nE "\[20[0-9]{2}-[0-9]{2}-[0-9]{2}\]|YYYY-MM-DD|TODO|TBD" docs/al-dev-naming-convention.md
```
Expected: one allowed match only — the `{dir}/YYYY-MM-DD-{surface}-{kind}.md` pattern line (it documents the placeholder, it is not an unrendered date). No `TODO`/`TBD`/bracketed-date matches.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add docs/al-dev-naming-convention.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: add maintainer tooling naming convention"
```

---

### Task 2: Rename the 10 agent lenses + update references

**Files:**
- Rename: `.claude/agents/design-lens-{tool-hygiene,model-fit,scope-isolation,caller-alignment,usage-patterns}.md` → `design-agent-lens-*.md`
- Rename: `.claude/agents/quality-lens-{clarity,structure,description,bloat,name-fit}.md` → `quality-agent-lens-*.md`
- Modify: `scripts/validate-lens-agents.py:19-40` (EXPECTED_AGENTS list)
- Modify: `.claude/skills/analyze-agent-design/SKILL.md:84-93` (dispatch list)
- Modify: `.claude/skills/audit-agent-quality/SKILL.md:55-60` (dispatch list)
- Modify: `scripts/tests/test_validate_lens_agents.py` (example path strings)

This is a TDD-flavored loop: update the validator's expectations first (it goes RED because the files still have old names), then rename to make it GREEN.

- [ ] **Step 1: Update the validator's EXPECTED_AGENTS to the new names**

In `scripts/validate-lens-agents.py`, replace the existing `EXPECTED_AGENTS` list (lines 19-40) so the first ten entries use the renamed pattern. Replace this block:

```python
EXPECTED_AGENTS = [
    "quality-lens-clarity",
    "quality-lens-structure",
    "quality-lens-description",
    "quality-lens-bloat",
    "quality-lens-name-fit",
    "design-lens-tool-hygiene",
    "design-lens-model-fit",
    "design-lens-scope-isolation",
    "design-lens-caller-alignment",
    "design-lens-usage-patterns",
    "quality-skill-lens-clarity",
    "quality-skill-lens-structure",
    "quality-skill-lens-description",
    "quality-skill-lens-bloat",
    "quality-skill-lens-name-fit",
    "design-skill-lens-shared-backbone",
    "design-skill-lens-complexity",
    "design-skill-lens-near-duplicates",
    "design-skill-lens-handoff-gaps",
    "design-skill-lens-preplanning",
]
```

with:

```python
EXPECTED_AGENTS = [
    "quality-agent-lens-clarity",
    "quality-agent-lens-structure",
    "quality-agent-lens-description",
    "quality-agent-lens-bloat",
    "quality-agent-lens-name-fit",
    "design-agent-lens-tool-hygiene",
    "design-agent-lens-model-fit",
    "design-agent-lens-scope-isolation",
    "design-agent-lens-caller-alignment",
    "design-agent-lens-usage-patterns",
    "quality-skill-lens-clarity",
    "quality-skill-lens-structure",
    "quality-skill-lens-description",
    "quality-skill-lens-bloat",
    "quality-skill-lens-name-fit",
    "design-skill-lens-shared-backbone",
    "design-skill-lens-complexity",
    "design-skill-lens-near-duplicates",
    "design-skill-lens-handoff-gaps",
    "design-skill-lens-preplanning",
]
```

- [ ] **Step 2: Run the validator to verify it now FAILS**

Run: `python3 scripts/validate-lens-agents.py`
Expected: FAIL — 10 issues, each "agent file not found" for the new `design-agent-lens-*` / `quality-agent-lens-*` paths (files still have old names).

- [ ] **Step 3: Rename the 10 agent files with git mv**

```bash
cd /Users/russelllaing/al-dev-shared/.claude/agents
git mv design-lens-tool-hygiene.md     design-agent-lens-tool-hygiene.md
git mv design-lens-model-fit.md        design-agent-lens-model-fit.md
git mv design-lens-scope-isolation.md  design-agent-lens-scope-isolation.md
git mv design-lens-caller-alignment.md design-agent-lens-caller-alignment.md
git mv design-lens-usage-patterns.md   design-agent-lens-usage-patterns.md
git mv quality-lens-clarity.md         quality-agent-lens-clarity.md
git mv quality-lens-structure.md       quality-agent-lens-structure.md
git mv quality-lens-description.md     quality-agent-lens-description.md
git mv quality-lens-bloat.md           quality-agent-lens-bloat.md
git mv quality-lens-name-fit.md        quality-agent-lens-name-fit.md
```

- [ ] **Step 4: Update the `name:` frontmatter inside each renamed file**

`git mv` renames the file but not the `name:` field in its frontmatter. For each of the 10 renamed files, update the frontmatter `name:` to match the new filename. Example for one file — apply the analogous edit to all 10:

In `.claude/agents/design-agent-lens-tool-hygiene.md`, replace:
```yaml
name: design-lens-tool-hygiene
```
with:
```yaml
name: design-agent-lens-tool-hygiene
```

Verify all 10 updated:
```bash
cd /Users/russelllaing/al-dev-shared/.claude/agents
grep -l "name: design-lens-\|name: quality-lens-" design-agent-lens-*.md quality-agent-lens-*.md
```
Expected: no output (no file still carries an old `name:`).

- [ ] **Step 5: Run the validator to verify it now PASSES**

Run: `python3 scripts/validate-lens-agents.py`
Expected: `PASS — 20 agents valid, 4 skills refactored.`

- [ ] **Step 6: Update the `analyze-agent-design` dispatch list**

In `.claude/skills/analyze-agent-design/SKILL.md`, replace the dispatch block (lines 84-93). Replace:

```
- `all` or no argument: dispatch all five simultaneously
  - `design-lens-tool-hygiene`
  - `design-lens-model-fit`
  - `design-lens-scope-isolation`
  - `design-lens-caller-alignment`
  - `design-lens-usage-patterns`
- `trim`: dispatch only `design-lens-tool-hygiene`
- `remodel`: dispatch only `design-lens-model-fit`
- `split`: dispatch only `design-lens-scope-isolation`
- `align`: dispatch only `design-lens-caller-alignment`
- `inline`: dispatch only `design-lens-usage-patterns`
```

with:

```
- `all` or no argument: dispatch all five simultaneously
  - `design-agent-lens-tool-hygiene`
  - `design-agent-lens-model-fit`
  - `design-agent-lens-scope-isolation`
  - `design-agent-lens-caller-alignment`
  - `design-agent-lens-usage-patterns`
- `trim`: dispatch only `design-agent-lens-tool-hygiene`
- `remodel`: dispatch only `design-agent-lens-model-fit`
- `split`: dispatch only `design-agent-lens-scope-isolation`
- `align`: dispatch only `design-agent-lens-caller-alignment`
- `inline`: dispatch only `design-agent-lens-usage-patterns`
```

- [ ] **Step 7: Update the `audit-agent-quality` dispatch list**

In `.claude/skills/audit-agent-quality/SKILL.md`, replace the dispatch list (lines 55-60). Replace:

```
- `quality-lens-clarity`
- `quality-lens-structure`
- `quality-lens-description`
- `quality-lens-bloat`
- `quality-lens-name-fit`
```

with:

```
- `quality-agent-lens-clarity`
- `quality-agent-lens-structure`
- `quality-agent-lens-description`
- `quality-agent-lens-bloat`
- `quality-agent-lens-name-fit`
```

- [ ] **Step 8: Update the example path in the validator test**

In `scripts/tests/test_validate_lens_agents.py`, the two test functions use `quality-lens-clarity.md` and `foo.md` as sample path strings. Update the real-lens example so it points at a renamed file. Replace:

```python
        path=".claude/agents/quality-lens-clarity.md",
```
with:
```python
        path=".claude/agents/quality-agent-lens-clarity.md",
```
And replace the assertion on the next lines:
```python
    assert lines[0] == ".claude/agents/quality-lens-clarity.md", (
```
with:
```python
    assert lines[0] == ".claude/agents/quality-agent-lens-clarity.md", (
```

- [ ] **Step 9: Run the validator test to verify it passes**

Run:
```bash
python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('t', 'scripts/tests/test_validate_lens_agents.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.test_format_failure_has_canonical_shape()
m.test_format_failure_embeds_path_in_fix_when_provided()
print('PASS')
"
```
Expected: `PASS`

- [ ] **Step 10: Confirm no stale old-name references remain (repo-wide guard)**

Scan the WHOLE repo (not just `.claude`/`scripts`) so a stray reference in
`docs/`, `.github/`, or a root file cannot slip through. Exclude `.git` and
`docs/superpowers/` — the latter holds historical plans/specs that the source
spec explicitly says must NOT be rewritten.

```bash
cd /Users/russelllaing/al-dev-shared
grep -rn "design-lens-\|quality-lens-" --exclude-dir=.git . \
  | grep -v "docs/superpowers/" \
  | grep -v "design-agent-lens\|quality-agent-lens\|design-skill-lens\|quality-skill-lens"
```
Expected: no output. Any line printed is a live caller still pointing at an old
name — fix it before committing. (The only intentionally-untouched references
live under `docs/superpowers/`, which is filtered out above.)

The earlier validator run (Step 5) already proved every renamed agent file
*resolves* by name; this step proves no *caller* still asks for an old name —
together they confirm dispatch is intact end-to-end.

- [ ] **Step 11: Verify and commit**

```bash
git -C /Users/russelllaing/al-dev-shared status
git -C /Users/russelllaing/al-dev-shared add -A .claude/agents scripts/validate-lens-agents.py scripts/tests/test_validate_lens_agents.py .claude/skills/analyze-agent-design/SKILL.md .claude/skills/audit-agent-quality/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "refactor(lenses): rename agent lenses to symmetric {dimension}-agent-lens-{aspect}"
```
Expected: `git status` shows the 10 renames (R) plus the 4 modified reference files; no unexpected extras.

---

### Task 3: Remove the unused `plugin-health-daemon`

**Files:**
- Delete: `.claude/skills/plugin-health-daemon/` (and its `SKILL.md`)
- Delete: `scripts/plugin-health-daemon.sh`
- Modify: `CLAUDE.md:177-180`
- Modify: `docs/al-dev-plugin-map.md:6,749`
- Modify: `.claude/settings.local.json:99`
- Modify: `.github/copilot-instructions.md:125,128,250`

- [ ] **Step 1: Delete the skill directory and the script**

```bash
cd /Users/russelllaing/al-dev-shared
git rm -r .claude/skills/plugin-health-daemon
git rm scripts/plugin-health-daemon.sh
```

- [ ] **Step 2: Remove the daemon block from `CLAUDE.md`**

In `CLAUDE.md`, delete the "Plugin Health and Documentation" example block. Replace:

```markdown
### Plugin Health and Documentation

```bash
# Run plugin health daemon (audit sweep with auto-fix)
bash scripts/plugin-health-daemon.sh --dry-run    # preview changes
bash scripts/plugin-health-daemon.sh --execute    # apply changes and create PR
```

```

with:

```markdown
### Plugin Health and Documentation

```bash
# Run the suggestions-only health sweep (writes per-surface dossiers; never auto-edits)
/plugin-health --surface both
```

```

- [ ] **Step 3: Remove the daemon mentions from `docs/al-dev-plugin-map.md`**

In `docs/al-dev-plugin-map.md` line 6, replace:

```
**Scope:** Active skills only. Archived items (al-dev-test, test-engineer agents, al-dev-test-coverage-reviewer, al-dev-align, plugin-health-daemon) excluded. `/align-harness-repos` and `/plugin-health-daemon` are project-local maintenance tools in `.claude/skills/`, not distributed in the plugin.
```

with:

```
**Scope:** Active skills only. Archived items (al-dev-test, test-engineer agents, al-dev-test-coverage-reviewer, al-dev-align) excluded. `/align-harness-repos` and `/plugin-health` are project-local maintenance tools in `.claude/skills/`, not distributed in the plugin.
```

Then delete the status line at line 749:

```
**✅ Status: /plugin-health-daemon** — Moved to `.claude/skills/` as project-local maintenance infrastructure.
```
(Remove the entire line.)

- [ ] **Step 4: Remove the stale permission from `.claude/settings.local.json`**

In `.claude/settings.local.json`, delete the array entry at line 99:

```
      "Bash(chmod +x /Users/russelllaing/al-dev-shared/scripts/plugin-health-daemon.sh)",
```
(Remove the entire line, including its trailing comma — ensure the resulting JSON array stays valid: the preceding entry must still end with a comma only if another entry follows it.)

- [ ] **Step 5: Remove the daemon command refs from `.github/copilot-instructions.md`**

In `.github/copilot-instructions.md`, remove the two `bash scripts/plugin-health-daemon.sh ...` invocation lines (lines 125 and 128) and the "Run health sweep" bullet (line 250). Replace the bullet at line 250:

```
- **Run health sweep**: `bash scripts/plugin-health-daemon.sh --execute` to create PR with auto-fixes
```
with:
```
- **Run health sweep**: invoke the `/plugin-health` skill (suggestions-only; writes per-surface dossiers, no auto-fixes)
```
For lines 125 and 128, read the surrounding block first and remove the two daemon command lines so the block no longer references the deleted script.

- [ ] **Step 6: Validate `settings.local.json` is still valid JSON**

Run: `python3 -c "import json; json.load(open('.claude/settings.local.json')); print('valid JSON')"`
Expected: `valid JSON`

- [ ] **Step 7: Confirm no daemon references remain**

Run:
```bash
cd /Users/russelllaing/al-dev-shared
grep -rn "plugin-health-daemon\|plugin_health_daemon" CLAUDE.md docs/al-dev-plugin-map.md .claude/settings.local.json .github/copilot-instructions.md scripts .claude/skills
```
Expected: no output.

- [ ] **Step 8: Verify and commit**

```bash
git -C /Users/russelllaing/al-dev-shared status
git -C /Users/russelllaing/al-dev-shared add -A
git -C /Users/russelllaing/al-dev-shared commit -m "chore: remove unused plugin-health-daemon (skill, script, doc mentions)"
```
Expected: `git status` shows the deleted skill dir + script and the 4 modified docs/config files.

---

### Task 4: Dogfood the quality lenses against `.claude/` and apply atomic fixes

**Files:**
- Modify (discovery-driven): files under `.claude/agents/` and `.claude/skills/` that the lenses flag

This is Phase 2's loop pointed at the maintainer surface, run manually before the orchestrator exists. The lenses already take a file list (no internal change needed), so dispatch them directly against `.claude/` paths. Apply only safe, atomic, within-budget fixes — this is a cleanup, not a rewrite.

- [ ] **Step 1: Build the maintainer file lists**

```bash
cd /Users/russelllaing/al-dev-shared
find .claude/agents -name "*.md" | sort        # agent file list
find .claude/skills -name "SKILL.md" | sort     # skill file list
```
Record both lists (absolute paths) for the dispatch prompts.

- [ ] **Step 2: Dispatch the 5 agent quality lenses in parallel against the agent file list**

In a single response, dispatch these five via the Agent tool (`subagent_type` = each lens name), passing the agent file list in the prompt body (one absolute path per line):
- `quality-agent-lens-clarity`
- `quality-agent-lens-structure`
- `quality-agent-lens-description`
- `quality-agent-lens-bloat`
- `quality-agent-lens-name-fit`

Dispatch prompt template (substitute the real paths):
```
Analyze the following agent files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line from Step 1]
```

- [ ] **Step 3: Dispatch the 5 skill quality lenses in parallel against the skill file list**

In a single response, dispatch these five against the skill (`SKILL.md`) file list:
- `quality-skill-lens-clarity`
- `quality-skill-lens-structure`
- `quality-skill-lens-description`
- `quality-skill-lens-bloat`
- `quality-skill-lens-name-fit`

- [ ] **Step 4: Aggregate findings and apply atomic fixes within budget**

Collect all findings blocks. For each file with findings, apply the **Fix Application Protocol** from `.claude/skills/audit-agent-quality/SKILL.md` (Phase 6, "Fix Application Protocol"):
1. Read the file; record `original_lines`.
2. `budget = floor(original_lines × 0.05)`. If `0`, skip non-atomic edits for that file.
3. Apply only atomic fixes, High → Medium → Low.
4. Skip any fix that would exceed the budget or requires rewriting a structural block.
5. After each edit: `wc -l <file>` — confirm net reduction ≤ budget and required structural sections (`## Output Format`, frontmatter) survive.

Note: `.claude/` files are maintainer-specific and need **no** harness-neutrality check (only shared-surface outputs do).

- [ ] **Step 5: Re-run the lens validator to confirm nothing structural broke**

Run: `python3 scripts/validate-lens-agents.py`
Expected: `PASS — 20 agents valid, 4 skills refactored.`

- [ ] **Step 6: Verify and commit**

```bash
git -C /Users/russelllaing/al-dev-shared status
git -C /Users/russelllaing/al-dev-shared diff --stat
git -C /Users/russelllaing/al-dev-shared add -A .claude
git -C /Users/russelllaing/al-dev-shared commit -m "refactor(.claude): apply dogfooded quality-lens fixes to maintainer tooling"
```
Expected: `git status` shows only `.claude/` edits. If the lenses found nothing actionable, record "no atomic fixes within budget" and skip the commit.

---

## Phase 2 — Self-healing system

### Task 5: `naming-convention-lens` agent + validator extension

**Files:**
- Create: `.claude/agents/naming-convention-lens.md`
- Modify: `scripts/validate-lens-agents.py` (append `naming-convention-lens` to `EXPECTED_AGENTS`)

- [ ] **Step 1: Add `naming-convention-lens` to the validator's EXPECTED_AGENTS**

In `scripts/validate-lens-agents.py`, append a new final entry to the `EXPECTED_AGENTS` list (after `"design-skill-lens-preplanning",`):

```python
    "design-skill-lens-preplanning",
    "naming-convention-lens",
]
```

- [ ] **Step 2: Run the validator to verify it now FAILS**

Run: `python3 scripts/validate-lens-agents.py`
Expected: FAIL — 1 issue: "agent file not found" for `.claude/agents/naming-convention-lens.md`.

- [ ] **Step 3: Write the `naming-convention-lens` agent**

Write `.claude/agents/naming-convention-lens.md`:

````markdown
---
name: naming-convention-lens
description: Apply the Naming Convention lens to maintainer tool files and output paths — flags any tool name or output filename that violates docs/al-dev-naming-convention.md. Returns a findings block.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` and/or skill `SKILL.md` files |
| convention_doc | Absolute path to `docs/al-dev-naming-convention.md` (read it before judging) |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Naming Convention

Read `docs/al-dev-naming-convention.md` first — it is the source of truth. Then
read every file path in the dispatch prompt and derive each tool's name:
- Agent name = filename without directory and `.md`.
- Skill name = parent directory name of `SKILL.md`.

**Check tool names:**
- Lens agents (filename matches `*-lens-*`) MUST match
  `{design|quality}-{agent|skill}-lens-{aspect}`. The single allowed exception
  is `naming-convention-lens`. Any other lens-agent name that deviates is a
  **High** finding.
- Maintainer skills SHOULD match `{verb}-{object}-{aspect}` with the documented
  verb/object sets. A non-conforming skill name that is not a grandfathered
  pre-existing skill (`projection-sync`, `align-harness-repos`) is a **Low**
  finding (advisory).

**Check output paths** mentioned in the body (Write/output targets):
- Living docs must match `al-dev-{object}-{kind}.md`.
- Dated artifacts must match `{dir}/YYYY-MM-DD-{surface}-{kind}.md` with
  `surface` ∈ `plugin` | `tooling`.
- A documented output path that violates either pattern is a **Medium** finding.

**Severity summary:**
- High: a lens-agent filename that breaks the enforced lens pattern
- Medium: an output path that breaks a documented output pattern
- Low: an advisory skill-name deviation

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Naming Convention Findings
- **[tool-or-path-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Naming Convention Findings
_No issues found._
````

- [ ] **Step 4: Run the validator to verify it now PASSES**

Run: `python3 scripts/validate-lens-agents.py`
Expected: `PASS — 21 agents valid, 4 skills refactored.`

- [ ] **Step 5: Verify and commit**

```bash
git -C /Users/russelllaing/al-dev-shared status
git -C /Users/russelllaing/al-dev-shared add .claude/agents/naming-convention-lens.md scripts/validate-lens-agents.py
git -C /Users/russelllaing/al-dev-shared commit -m "feat(lenses): add naming-convention-lens for naming-drift detection"
```

---

### Task 6: Dependency-graph generator + tests

**Files:**
- Create: `scripts/generate-plugin-graph.py`
- Create: `scripts/tests/test_generate_plugin_graph.py`
- Create (generated output): `docs/al-dev-plugin-graph.md`

Deterministic structured-grep extraction over `profile-al-dev-shared/`. Reusable extraction functions take a `plugin_dir` argument so tests can point at a fixture. The generator is suggestions-only: on parse error it writes a partial graph with an "incomplete" banner and exits 0.

- [ ] **Step 1: Write the failing test**

Write `scripts/tests/test_generate_plugin_graph.py`:

```python
"""Fixture-based tests for scripts/generate-plugin-graph.py."""
from __future__ import annotations

import importlib.util
import inspect
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "generate_plugin_graph",
    REPO_ROOT / "scripts" / "generate-plugin-graph.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def _build_fixture(root: Path) -> Path:
    """Create a tiny fake plugin dir with a known orphan, dead link, and missing ref."""
    plugin = root / "profile-al-dev-shared"
    (plugin / "skills" / "s-main").mkdir(parents=True)
    (plugin / "skills" / "s-other").mkdir(parents=True)
    (plugin / "agents").mkdir(parents=True)
    (plugin / "knowledge").mkdir(parents=True)

    (plugin / "skills" / "s-main" / "SKILL.md").write_text(
        "Spawn al-dev-shared:al-dev-worker.\n"
        "See ../../knowledge/good.md and ../../knowledge/missing.md.\n"
        "Writes .dev/output.md.\n"
        "Then run /s-other to continue.\n",
        encoding="utf-8",
    )
    (plugin / "skills" / "s-other" / "SKILL.md").write_text(
        "A second skill with no agent or knowledge refs.\n",
        encoding="utf-8",
    )
    (plugin / "agents" / "al-dev-worker.md").write_text(
        "Worker agent. Reads ../../knowledge/good.md.\n", encoding="utf-8"
    )
    (plugin / "agents" / "al-dev-orphan.md").write_text(
        "Orphan agent spawned by no skill.\n", encoding="utf-8"
    )
    (plugin / "knowledge" / "good.md").write_text("good\n", encoding="utf-8")
    (plugin / "knowledge" / "dead.md").write_text("referenced by nobody\n", encoding="utf-8")
    return plugin


def test_discover_finds_skills_agents_knowledge() -> None:
    with tempfile.TemporaryDirectory() as td:
        plugin = _build_fixture(Path(td))
        skills, agents, knowledge = _mod.discover(plugin)
        assert skills == ["s-main", "s-other"], skills
        assert agents == ["al-dev-orphan", "al-dev-worker"], agents
        assert knowledge == ["dead.md", "good.md"], knowledge


def test_extract_edges_finds_all_edge_types() -> None:
    with tempfile.TemporaryDirectory() as td:
        plugin = _build_fixture(Path(td))
        skills, _, _ = _mod.discover(plugin)
        edges = _mod.extract_edges(plugin, skills)
        assert ("s-main", "al-dev-worker") in edges["skill_agent"]
        assert ("s-main", "s-other") in edges["skill_skill"]
        assert ("s-main", "good.md") in edges["skill_knowledge"]
        assert ("s-main", "missing.md") in edges["skill_knowledge"]
        assert ("al-dev-worker", "good.md") in edges["agent_knowledge"]
        assert ("s-main", "output.md") in edges["skill_artifact"]


def test_find_health_detects_orphan_dead_and_missing() -> None:
    with tempfile.TemporaryDirectory() as td:
        plugin = _build_fixture(Path(td))
        skills, agents, knowledge = _mod.discover(plugin)
        edges = _mod.extract_edges(plugin, skills)
        health = _mod.find_health(skills, agents, knowledge, edges)
        assert health["orphan_agents"] == ["al-dev-orphan"], health["orphan_agents"]
        assert "dead.md" in health["dead_knowledge"]
        assert ("knowledge", "missing.md") in health["missing_refs"]


def test_node_id_sanitizes_hyphens() -> None:
    assert _mod.node_id("al-dev-worker") == "al_dev_worker"


def _run(func):
    sig = inspect.signature(func)
    if not sig.parameters:
        func()
    else:
        raise TypeError(f"Unsupported signature: {func.__name__}{sig}")


def load_tests(loader, tests, pattern):  # noqa: ARG001
    suite = unittest.TestSuite()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            suite.addTest(unittest.FunctionTestCase(lambda fn=fn: _run(fn)))
    return suite


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:
```bash
python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('t', 'scripts/tests/test_generate_plugin_graph.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
"
```
Expected: FAIL — `FileNotFoundError` / module load error because `scripts/generate-plugin-graph.py` does not exist yet.

- [ ] **Step 3: Write the generator**

Write `scripts/generate-plugin-graph.py`:

```python
#!/usr/bin/env python3
"""Generate docs/al-dev-plugin-graph.md.

Deterministic structured-grep extraction over profile-al-dev-shared/. Renders a
dependency graph, the three workflow-path overlays, and health callouts (orphans,
dead links, off-path skills, missing refs). Suggestions-only: never edits source.
On a parse error it writes a partial graph with an 'incomplete' banner and exits 0.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path("/Users/russelllaing/al-dev-shared")
PLUGIN = REPO / "profile-al-dev-shared"
OUTPUT = REPO / "docs" / "al-dev-plugin-graph.md"

# The three canonical workflow paths (from CLAUDE.md "Plugin Architecture").
WORKFLOW_PATHS = {
    "Ticket / Support": ["al-dev-ticket", "al-dev-support-reply-drafter"],
    "Development spine": [
        "al-dev-investigate",
        "al-dev-plan",
        "al-dev-develop",
        "al-dev-commit",
    ],
    "Direct fix": ["al-dev-fix"],
}

AGENT_REF = re.compile(r"al-dev-shared:(al-dev-[a-z0-9-]+)")
SKILL_REF = re.compile(r"/(al-dev-[a-z0-9-]+)")
KNOWLEDGE_REF = re.compile(r"knowledge/([a-z0-9-]+\.md)")
ARTIFACT_REF = re.compile(r"\.dev/([A-Za-z0-9._-]+\.md)")


def node_id(name: str) -> str:
    """Mermaid-safe node id: letters, numbers, underscores only."""
    return re.sub(r"[^A-Za-z0-9_]", "_", name)


def discover(plugin_dir: Path) -> tuple[list[str], list[str], list[str]]:
    skills = sorted(p.parent.name for p in (plugin_dir / "skills").glob("*/SKILL.md"))
    agents = sorted(p.stem for p in (plugin_dir / "agents").glob("*.md"))
    knowledge = sorted(p.name for p in (plugin_dir / "knowledge").glob("*.md"))
    return skills, agents, knowledge


def extract_edges(plugin_dir: Path, skills: list[str]) -> dict[str, set[tuple[str, str]]]:
    edges: dict[str, set[tuple[str, str]]] = {
        "skill_agent": set(),
        "skill_skill": set(),
        "skill_knowledge": set(),
        "agent_knowledge": set(),
        "skill_artifact": set(),
    }
    skill_set = set(skills)
    for skill_md in (plugin_dir / "skills").glob("*/SKILL.md"):
        src = skill_md.parent.name
        text = skill_md.read_text(encoding="utf-8")
        for dst in AGENT_REF.findall(text):
            edges["skill_agent"].add((src, dst))
        for dst in SKILL_REF.findall(text):
            if dst != src and dst in skill_set:
                edges["skill_skill"].add((src, dst))
        for dst in KNOWLEDGE_REF.findall(text):
            edges["skill_knowledge"].add((src, dst))
        for dst in ARTIFACT_REF.findall(text):
            edges["skill_artifact"].add((src, dst))
    for agent_md in (plugin_dir / "agents").glob("*.md"):
        src = agent_md.stem
        text = agent_md.read_text(encoding="utf-8")
        for dst in KNOWLEDGE_REF.findall(text):
            edges["agent_knowledge"].add((src, dst))
    return edges


def find_health(
    skills: list[str],
    agents: list[str],
    knowledge_on_disk: list[str],
    edges: dict[str, set[tuple[str, str]]],
) -> dict[str, list]:
    spawned = {dst for _, dst in edges["skill_agent"]}
    orphan_agents = sorted(a for a in agents if a not in spawned)

    referenced_knowledge = {dst for _, dst in edges["skill_knowledge"]} | {
        dst for _, dst in edges["agent_knowledge"]
    }
    dead_knowledge = sorted(k for k in knowledge_on_disk if k not in referenced_knowledge)

    on_path = {s for path in WORKFLOW_PATHS.values() for s in path}
    offpath_skills = sorted(s for s in skills if s not in on_path)

    agent_set, skill_set, knowledge_set = set(agents), set(skills), set(knowledge_on_disk)
    missing: set[tuple[str, str]] = set()
    for _, dst in edges["skill_agent"]:
        if dst not in agent_set:
            missing.add(("agent", dst))
    for _, dst in edges["skill_skill"]:
        if dst not in skill_set:
            missing.add(("skill", dst))
    for _, dst in edges["skill_knowledge"] | edges["agent_knowledge"]:
        if dst not in knowledge_set:
            missing.add(("knowledge", dst))

    return {
        "orphan_agents": orphan_agents,
        "dead_knowledge": dead_knowledge,
        "offpath_skills": offpath_skills,
        "missing_refs": sorted(missing),
    }


def render_dependency_graph(
    skills: list[str],
    agents: list[str],
    edges: dict[str, set[tuple[str, str]]],
) -> str:
    referenced_knowledge = sorted(
        {dst for _, dst in edges["skill_knowledge"]}
        | {dst for _, dst in edges["agent_knowledge"]}
    )
    lines = [
        "```mermaid",
        "flowchart LR",
        "    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold",
        "    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold",
        "    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold",
        "",
        "    subgraph Skills[Skills]",
    ]
    for s in skills:
        lines.append(f"        {node_id(s)}[{s}]")
    lines.append("    end")
    lines.append("    subgraph Agents[Agents]")
    for a in agents:
        lines.append(f"        {node_id(a)}[{a}]")
    lines.append("    end")
    lines.append("    subgraph Knowledge[Knowledge Files]")
    for k in referenced_knowledge:
        lines.append(f"        {node_id(k)}[{k[:-3]}]")
    lines.append("    end")
    lines.append("")
    for src, dst in sorted(edges["skill_skill"]):
        lines.append(f"    {node_id(src)} --> {node_id(dst)}")
    for src, dst in sorted(edges["skill_agent"]):
        lines.append(f"    {node_id(src)} --> {node_id(dst)}")
    for src, dst in sorted(edges["skill_knowledge"] | edges["agent_knowledge"]):
        if dst in referenced_knowledge:
            lines.append(f"    {node_id(src)} --> {node_id(dst)}")
    lines.append("")
    for s in skills:
        lines.append(f"    class {node_id(s)} skillNode")
    for a in agents:
        lines.append(f"    class {node_id(a)} agentNode")
    for k in referenced_knowledge:
        lines.append(f"    class {node_id(k)} knowledgeNode")
    lines.append("```")
    return "\n".join(lines)


def render_workflow_overlays() -> str:
    blocks = []
    for title, path in WORKFLOW_PATHS.items():
        lines = ["```mermaid", "flowchart LR"]
        for i in range(len(path) - 1):
            lines.append(f"    {node_id(path[i])}[{path[i]}] --> {node_id(path[i + 1])}[{path[i + 1]}]")
        if len(path) == 1:
            lines.append(f"    {node_id(path[0])}[{path[0]}]")
        lines.append("```")
        blocks.append(f"### {title}\n\n" + "\n".join(lines))
    return "\n\n".join(blocks)


def render_health(health: dict[str, list]) -> str:
    def section(title: str, items: list[str]) -> str:
        if not items:
            return f"**{title}:** none\n"
        body = "\n".join(f"- `{i}`" for i in items)
        return f"**{title}:**\n\n{body}\n"

    missing = [f"{kind}: {name}" for kind, name in health["missing_refs"]]
    parts = [
        section("Orphan agents (spawned by no skill)", health["orphan_agents"]),
        section("Dead knowledge (referenced by nothing)", health["dead_knowledge"]),
        section("Off-path skills (not on any workflow path)", health["offpath_skills"]),
        section("Missing refs (referenced but not on disk)", missing),
    ]
    return "\n".join(parts)


def build_document(skills, agents, knowledge, edges, health, incomplete: bool, today: str) -> str:
    banner = ""
    if incomplete:
        banner = (
            "> ⚠️ **Incomplete** — the generator hit a parse error and emitted a "
            "partial graph. Re-run after fixing the offending file.\n\n"
        )
    return (
        f"# Plugin Dependency Graph\n\n"
        f"> Generated by `scripts/generate-plugin-graph.py` on {today}.\n"
        f"> Re-run the script (or `/plugin-health`) to refresh. Do not hand-edit.\n\n"
        f"{banner}"
        f"## Dependency graph\n\n"
        f"{render_dependency_graph(skills, agents, edges)}\n\n"
        f"## Workflow-path overlays\n\n"
        f"{render_workflow_overlays()}\n\n"
        f"## Health callouts\n\n"
        f"{render_health(health)}\n"
    )


def main() -> int:
    from datetime import date

    today = date.today().isoformat()
    incomplete = False
    try:
        skills, agents, knowledge = discover(PLUGIN)
        edges = extract_edges(PLUGIN, skills)
        health = find_health(skills, agents, knowledge, edges)
    except Exception as exc:  # noqa: BLE001 — partial graph is the documented fallback
        sys.stderr.write(f"generate-plugin-graph: parse error: {exc}\n")
        skills, agents, knowledge = [], [], []
        edges = {k: set() for k in (
            "skill_agent", "skill_skill", "skill_knowledge", "agent_knowledge", "skill_artifact",
        )}
        health = {"orphan_agents": [], "dead_knowledge": [], "offpath_skills": [], "missing_refs": []}
        incomplete = True

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        build_document(skills, agents, knowledge, edges, health, incomplete, today),
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the test to verify it passes**

Run:
```bash
python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('t', 'scripts/tests/test_generate_plugin_graph.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.test_discover_finds_skills_agents_knowledge()
m.test_extract_edges_finds_all_edge_types()
m.test_find_health_detects_orphan_dead_and_missing()
m.test_node_id_sanitizes_hyphens()
print('PASS')
"
```
Expected: `PASS`

- [ ] **Step 5: Run the generator against the real plugin and inspect output**

```bash
cd /Users/russelllaing/al-dev-shared
python3 scripts/generate-plugin-graph.py
wc -l docs/al-dev-plugin-graph.md
grep -c "mermaid" docs/al-dev-plugin-graph.md
```
Expected: `Wrote .../docs/al-dev-plugin-graph.md`; non-zero line count; at least 4 mermaid blocks (1 dependency + 3 overlays).

- [ ] **Step 6: Harness-neutrality + forbidden-pattern check on the generated doc**

```bash
grep -nE "AskUserQuestion|ask_user|subagent_type|mcp__plugin_profile-claude|~/\.claude|~/\.copilot|Open Claude Code|Restart Claude Code" docs/al-dev-plugin-graph.md
grep -nE "\bTODO\b|\bTBD\b|YYYY-MM-DD" docs/al-dev-plugin-graph.md
```
Expected: no output from either grep.

- [ ] **Step 7: Verify and commit**

```bash
git -C /Users/russelllaing/al-dev-shared status
git -C /Users/russelllaing/al-dev-shared add scripts/generate-plugin-graph.py scripts/tests/test_generate_plugin_graph.py docs/al-dev-plugin-graph.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(scripts): add plugin dependency-graph generator + tests"
```

---

### Task 7: `/plugin-health` orchestrator skill

**Files:**
- Create: `.claude/skills/plugin-health/SKILL.md`
- Create: `docs/health/.gitkeep`

The orchestrator dispatches lenses with a per-surface file list and writes one ranked dossier per surface. Suggestions-only — it never edits source. It always runs the graph generator for the profile surface.

- [ ] **Step 1: Create the dossier output directory anchor**

```bash
mkdir -p /Users/russelllaing/al-dev-shared/docs/health
touch /Users/russelllaing/al-dev-shared/docs/health/.gitkeep
```

- [ ] **Step 2: Write the orchestrator skill**

Write `.claude/skills/plugin-health/SKILL.md`:

````markdown
---
name: plugin-health
description: >-
  Suggestions-only health sweep of the al-dev-shared plugin surfaces. Dispatches
  design + quality + naming lenses with a per-surface file list, ranks findings,
  and writes one dossier per surface to docs/health/. Always refreshes the
  dependency graph for the plugin surface. Never auto-edits source. Triggers on:
  "plugin health", "health sweep", "audit the plugin", "check plugin health".
argument-hint: "[--surface plugin|tooling|both] [--dimension design|quality|all]"
---

# Skill: /plugin-health

Standing self-healing entry point. Detects drift across both plugin surfaces and
consolidates suggestions into one ranked dossier per surface. Nothing is
auto-edited — the loop is: `/plugin-health` (detect) → dossier (review) →
`/plan-map-changes` (rubber-duck accepted items) → plan → execute.

## Phase 0 — Parse arguments

- `--surface` ∈ `plugin` | `tooling` | `both` (default `both`)
- `--dimension` ∈ `design` | `quality` | `all` (default `all`)

Surface → directory mapping:
- `plugin` → `profile-al-dev-shared/` → dossier `docs/health/YYYY-MM-DD-plugin-health.md`
- `tooling` → `.claude/` → dossier `docs/health/YYYY-MM-DD-tooling-health.md`

## Phase 1 — Build file lists (per requested surface)

For each requested surface, glob both object types:

```bash
# plugin surface
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents -name "*.md" | sort
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills -name "SKILL.md" | sort
# tooling surface
find /Users/russelllaing/al-dev-shared/.claude/agents -name "*.md" | sort
find /Users/russelllaing/al-dev-shared/.claude/skills -name "SKILL.md" | sort
```

Keep the agent list and the skill list separate — different lenses target each.

## Phase 2 — Parallel lens dispatch (per surface)

Dispatch in a single response (parallel Agent tool calls). Choose lenses by the
object type and the `--dimension` argument:

**Agent file list** receives:
- `design`/`all`: `design-agent-lens-tool-hygiene`, `design-agent-lens-model-fit`,
  `design-agent-lens-scope-isolation`, `design-agent-lens-caller-alignment`,
  `design-agent-lens-usage-patterns`
- `quality`/`all`: `quality-agent-lens-clarity`, `quality-agent-lens-structure`,
  `quality-agent-lens-description`, `quality-agent-lens-bloat`,
  `quality-agent-lens-name-fit`

**Skill file list** receives:
- `design`/`all`: `design-skill-lens-shared-backbone`, `design-skill-lens-complexity`,
  `design-skill-lens-near-duplicates`, `design-skill-lens-handoff-gaps`,
  `design-skill-lens-preplanning`
- `quality`/`all`: `quality-skill-lens-clarity`, `quality-skill-lens-structure`,
  `quality-skill-lens-description`, `quality-skill-lens-bloat`,
  `quality-skill-lens-name-fit`

**Both object lists** additionally receive `naming-convention-lens`, with
`docs/al-dev-naming-convention.md` passed as the convention doc.

Dispatch prompt template (substitute real paths):

```
Analyze the following files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]

Convention doc (naming-convention-lens only):
/Users/russelllaing/al-dev-shared/docs/al-dev-naming-convention.md
```

## Phase 3 — Collect findings (fault-tolerant)

Collect each lens's findings block. A lens that returns a malformed or empty
block is recorded as `lens <name>: no result` and the run continues — a failed
lens NEVER aborts the sweep.

Parse each finding line: `- **[name]** | [Severity] | [observation] | [fix]`.

## Phase 4 — Rank

Order findings High → Medium → Low, grouped by dimension (design before quality
before naming), then by object (agent before skill). Pick the top 5 ranked
actions for the summary.

## Phase 5 — Write ONE dossier per surface

Write `docs/health/YYYY-MM-DD-<surface>-health.md` (substitute today's date and
`plugin`/`tooling`). The dossier MUST use generic vocabulary (no harness-specific
tokens). Structure:

```markdown
# <Surface> Health — YYYY-MM-DD

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | <n>    | <n>     | <n>    | <n>   |
| Medium   | <n>    | <n>     | <n>    | <n>   |
| Low      | <n>    | <n>     | <n>    | <n>   |

Top 5 ranked actions:
1. ...

## Design suggestions

[Atomise / Merge / Trim / Split / Align findings — each: finding | rationale | fix]
_No issues found._  ← if empty

## Quality findings

[Bloat / Clarity / Structure / Name-fit / Description — with file:line]
_No issues found._  ← if empty

## Naming violations

[actual name/path vs convention-expected — from naming-convention-lens]
_No issues found._  ← if empty

## Graph deltas

[orphans, dead links, off-path skills, missing refs — plugin surface only;
 omit this section for the tooling surface]
_No issues found._  ← if empty
```

Record any `lens <name>: no result` notes at the foot of the Summary section.

## Phase 6 — Refresh the dependency graph (plugin surface only)

If the plugin surface was swept, run the generator and source the "Graph deltas"
section from its health callouts (single source of truth for both the picture and
those findings):

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/generate-plugin-graph.py
```

The generator writes `docs/al-dev-plugin-graph.md` and exits 0 even on a parse
error (partial graph + "incomplete" banner).

## Phase 7 — Present to user

Print, per surface: dossier path + severity counts + the top action. List any
`no result` lenses. Ask: "Review the dossier and run `/plan-map-changes` on the
items you accept?" Do not edit any source file.
````

- [ ] **Step 3: Harness-neutrality + forbidden-pattern check on the SKILL.md**

Note: the SKILL.md itself is maintainer-specific (`.claude/`), so it MAY contain harness tokens — but it should not, since its design avoids them. Confirm no unrendered placeholders leaked:
```bash
grep -nE "\bTODO\b|\bTBD\b|\[20[0-9]{2}-[0-9]{2}-[0-9]{2}\]" .claude/skills/plugin-health/SKILL.md
```
Expected: no output. (`YYYY-MM-DD` appears intentionally as the dossier filename pattern — that is documentation, not an unrendered date.)

- [ ] **Step 4: Verify and commit**

```bash
git -C /Users/russelllaing/al-dev-shared status
git -C /Users/russelllaing/al-dev-shared add .claude/skills/plugin-health/SKILL.md docs/health/.gitkeep
git -C /Users/russelllaing/al-dev-shared commit -m "feat(skills): add /plugin-health suggestions-only orchestrator"
```

---

### Task 8: Convention-checker test + first real `/plugin-health` run

**Files:**
- Create: `scripts/tests/test_naming_convention.py`
- Generated (run output): `docs/health/YYYY-MM-DD-tooling-health.md`, `docs/health/YYYY-MM-DD-plugin-health.md`

- [ ] **Step 1: Write the failing convention-checker test**

Write `scripts/tests/test_naming_convention.py`:

```python
"""Assert every .claude/ lens-agent name matches docs/al-dev-naming-convention.md."""
from __future__ import annotations

import inspect
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"
CONVENTION_DOC = REPO_ROOT / "docs" / "al-dev-naming-convention.md"

LENS_PATTERN = re.compile(r"^(design|quality)-(agent|skill)-lens-[a-z0-9-]+$")
LENS_EXCEPTIONS = {"naming-convention-lens"}


def test_convention_doc_exists() -> None:
    assert CONVENTION_DOC.is_file(), f"missing {CONVENTION_DOC}"


def test_all_lens_agents_match_enforced_pattern() -> None:
    offenders = []
    for path in sorted(AGENTS_DIR.glob("*.md")):
        name = path.stem
        if name in LENS_EXCEPTIONS:
            continue
        if "-lens-" in name and not LENS_PATTERN.match(name):
            offenders.append(name)
    assert not offenders, f"lens agents break the enforced pattern: {offenders}"


def test_no_legacy_lens_names_remain() -> None:
    legacy = re.compile(r"^(design|quality)-lens-")
    offenders = [p.stem for p in AGENTS_DIR.glob("*.md") if legacy.match(p.stem)]
    assert not offenders, f"legacy lens names still present: {offenders}"


def test_skill_dirs_are_kebab_case() -> None:
    kebab = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
    offenders = [
        p.name for p in SKILLS_DIR.iterdir() if p.is_dir() and not kebab.match(p.name)
    ]
    assert not offenders, f"non-kebab skill dirs: {offenders}"


def _run(func):
    sig = inspect.signature(func)
    if not sig.parameters:
        func()
    else:
        raise TypeError(f"Unsupported signature: {func.__name__}{sig}")


def load_tests(loader, tests, pattern):  # noqa: ARG001
    suite = unittest.TestSuite()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            suite.addTest(unittest.FunctionTestCase(lambda fn=fn: _run(fn)))
    return suite


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the convention-checker test to verify it passes**

Because Tasks 2 and 5 already renamed the lenses and the convention doc exists, this test should pass on first run (it asserts the end state). Run:
```bash
python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('t', 'scripts/tests/test_naming_convention.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.test_convention_doc_exists()
m.test_all_lens_agents_match_enforced_pattern()
m.test_no_legacy_lens_names_remain()
m.test_skill_dirs_are_kebab_case()
print('PASS')
"
```
Expected: `PASS`. (If it fails, a rename was missed in Task 2 — fix the offending file before continuing.)

- [ ] **Step 3: Commit the convention-checker test**

```bash
git -C /Users/russelllaing/al-dev-shared add scripts/tests/test_naming_convention.py
git -C /Users/russelllaing/al-dev-shared commit -m "test: assert .claude lens names match the naming convention"
```

- [ ] **Step 4: First real `/plugin-health` run — confirm two-surface separation**

Invoke `/plugin-health --surface both`. Confirm the run:
1. Writes two dossiers: `docs/health/<today>-plugin-health.md` and `docs/health/<today>-tooling-health.md`.
2. Each dossier contains the `## Summary`, `## Design suggestions`, `## Quality findings`, `## Naming violations` sections; the plugin dossier additionally contains `## Graph deltas`; the tooling dossier omits it.
3. Refreshes `docs/al-dev-plugin-graph.md`.

Verify section presence and surface separation:
```bash
cd /Users/russelllaing/al-dev-shared
TODAY=$(date +%F)
ls docs/health/${TODAY}-plugin-health.md docs/health/${TODAY}-tooling-health.md
grep -c "^## " docs/health/${TODAY}-plugin-health.md      # expect 5 sections
grep -c "^## " docs/health/${TODAY}-tooling-health.md      # expect 4 sections (no Graph deltas)
grep -L "Graph deltas" docs/health/${TODAY}-tooling-health.md   # tooling dossier should match (no Graph deltas)
```
Expected: both files exist; plugin dossier has 5 `##` sections, tooling has 4; the tooling dossier does NOT contain "Graph deltas".

- [ ] **Step 5: Harness-neutrality check on the dossiers**

The dossiers are maintainer outputs that must stay harness-agnostic:
```bash
cd /Users/russelllaing/al-dev-shared
grep -nE "AskUserQuestion|ask_user|subagent_type|mcp__plugin_profile-claude|~/\.claude|~/\.copilot|Open Claude Code|Restart Claude Code" docs/health/*-health.md
```
Expected: no output. If a token leaked, edit the dossier to use generic vocabulary before committing.

- [ ] **Step 6: Commit the first-run artifacts**

```bash
git -C /Users/russelllaing/al-dev-shared status
git -C /Users/russelllaing/al-dev-shared add docs/health docs/al-dev-plugin-graph.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(health): first /plugin-health sweep — per-surface dossiers + refreshed graph"
```

---

## Self-Review

**Spec coverage** (against the 7 Deliverables):
1. Naming-convention doc + 10 lens renames & reference updates → Tasks 1, 2 ✓
2. `plugin-health-daemon` removed (skill + script + doc mentions incl. `CLAUDE.md`, `al-dev-plugin-map.md`) → Task 3 ✓ (also covers `settings.local.json` + `copilot-instructions.md` for dead-command correctness)
3. Maintainer tooling modernized via dogfooded quality lenses → Task 4 ✓
4. `/plugin-health` orchestrator → two per-surface dossiers → Task 7 + first run in Task 8 ✓
5. `scripts/generate-plugin-graph.py` → `docs/al-dev-plugin-graph.md` → Task 6 ✓
6. `naming-convention-lens` agent → Task 5 ✓
7. Tests + validator extensions → Task 2 (validator renames + test), Task 5 (validator + naming lens), Task 6 (graph generator tests), Task 8 (convention-checker) ✓

Spec **Testing** section items: validate-lens-agents extended for renamed + new lens (Tasks 2, 5) ✓; graph generator fixture asserts orphan/dead-link detection (Task 6) ✓; convention-checker over `.claude/agents` + `.claude/skills` (Task 8) ✓; `/plugin-health` run confirms two-surface separation & dossier sections (Task 8) ✓; libexpat inline-test fallback used throughout (all test steps use the inline `importlib` runner) ✓.

Spec **Error handling**: malformed lens → "no result", run continues (Phase 3 of Task 7) ✓; graph parse error → partial + "incomplete" banner, exit 0 (Task 6 `main()`) ✓; no findings → dossier still written with "No issues found" per section (Task 7 Phase 5) ✓; nothing auto-edited (suggestions-only throughout) ✓.

**Type/name consistency:** Generator function names (`discover`, `extract_edges`, `find_health`, `node_id`, `render_dependency_graph`, `render_workflow_overlays`, `render_health`, `build_document`) are identical between Task 6's implementation and its test. Renamed lens names are identical across Task 2's `git mv` targets, validator `EXPECTED_AGENTS`, and the two skill dispatch lists. Dossier filename pattern (`docs/health/YYYY-MM-DD-{plugin|tooling}-health.md`) is consistent between the convention doc (Task 1), the orchestrator (Task 7), and the verification (Task 8).

**Placeholder scan:** `YYYY-MM-DD` appears only where it documents a filename *pattern* (convention doc, dossier template, verification globs use `$(date +%F)` for the real value) — not as an unrendered date. No `TODO`/`TBD`/"implement later" in any task. All code steps contain complete, runnable content.

**Harness-neutrality self-check (per `CLAUDE.md` Plan Self-Review):** The plan's neutral outputs (convention doc, graph doc, dossiers) are each verified by a grep for harness tokens before commit (Tasks 1, 6, 8). The `.claude/` files (lens agents, `/plugin-health` SKILL.md) are maintainer-specific and explicitly exempt — no task directs writing harness tokens into a shared-surface or `docs/` output.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-29-plugin-self-healing-tooling-implementation.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Note: Task 4 (dogfood) and Task 8 Step 4 (first `/plugin-health` run) require Agent-tool lens dispatch, so they run in the main session rather than a sandboxed subagent.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints for review.

**Which approach?**
