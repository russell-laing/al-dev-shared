# Lens-Agent Parallelization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure four project-level analysis skills into a three-phase architecture that dispatches one lightweight Haiku lens agent per analytical lens in parallel, replacing sequential in-context analysis.

**Architecture:** Each skill gains: Phase 1 (filesystem discovery inline), Phase 2 (parallel dispatch — all lens agents launched in one response), Phase 3 (inline aggregation of findings blocks into the existing report format). Five lens specifications are extracted from each skill body into dedicated agent files in `.claude/agents/`.

**Tech Stack:** Claude Code skill files (Markdown + YAML frontmatter), project-level agent files (`.claude/agents/`), Python validation script.

---

## File Structure

### New directory
```
.claude/agents/                          # Project-level agents (new)
```

### New agent files (20 total)
```
.claude/agents/quality-lens-clarity.md          # audit-agent-quality: Lens 1
.claude/agents/quality-lens-structure.md         # audit-agent-quality: Lens 2
.claude/agents/quality-lens-description.md       # audit-agent-quality: Lens 3
.claude/agents/quality-lens-bloat.md             # audit-agent-quality: Lens 4
.claude/agents/quality-lens-name-fit.md          # audit-agent-quality: Lens 5
.claude/agents/design-lens-tool-hygiene.md       # analyze-agent-design: Lens 1
.claude/agents/design-lens-model-fit.md          # analyze-agent-design: Lens 2
.claude/agents/design-lens-scope-isolation.md    # analyze-agent-design: Lens 3
.claude/agents/design-lens-caller-alignment.md   # analyze-agent-design: Lens 4
.claude/agents/design-lens-usage-patterns.md     # analyze-agent-design: Lens 5
.claude/agents/quality-skill-lens-clarity.md     # audit-skill-quality: Lens 1
.claude/agents/quality-skill-lens-structure.md   # audit-skill-quality: Lens 2
.claude/agents/quality-skill-lens-description.md # audit-skill-quality: Lens 3
.claude/agents/quality-skill-lens-bloat.md       # audit-skill-quality: Lens 4
.claude/agents/quality-skill-lens-name-fit.md    # audit-skill-quality: Lens 5
.claude/agents/design-skill-lens-shared-backbone.md  # analyze-skill-design: Lens A
.claude/agents/design-skill-lens-complexity.md       # analyze-skill-design: Lens B
.claude/agents/design-skill-lens-near-duplicates.md  # analyze-skill-design: Lens C
.claude/agents/design-skill-lens-handoff-gaps.md     # analyze-skill-design: Lens D
.claude/agents/design-skill-lens-preplanning.md      # analyze-skill-design: Lens E
```

### New validation file
```
scripts/validate-lens-agents.py
```

### Modified files (4 skills)
```
.claude/skills/audit-agent-quality/SKILL.md
.claude/skills/analyze-agent-design/SKILL.md
.claude/skills/audit-skill-quality/SKILL.md
.claude/skills/analyze-skill-design/SKILL.md
```

---

## Task 1: Create `.claude/agents/` Directory and Validation Script

**Files:**
- Create: `.claude/agents/` (directory)
- Create: `scripts/validate-lens-agents.py`

- [ ] **Step 1: Create the agents directory**

```bash
mkdir -p /Users/russelllaing/al-dev-shared/.claude/agents
```

- [ ] **Step 2: Verify the directory exists**

```bash
ls -la /Users/russelllaing/al-dev-shared/.claude/
```

Expected: `agents/` directory is listed.

- [ ] **Step 3: Write the validation script**

Create `scripts/validate-lens-agents.py`:

```python
"""Validates all lens agent files and refactored skills meet the spec."""
import os
import re
import sys

REPO = "/Users/russelllaing/al-dev-shared"
AGENTS_DIR = os.path.join(REPO, ".claude/agents")

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

SKILLS_TO_CHECK = [
    os.path.join(REPO, ".claude/skills/audit-agent-quality/SKILL.md"),
    os.path.join(REPO, ".claude/skills/audit-skill-quality/SKILL.md"),
    os.path.join(REPO, ".claude/skills/analyze-agent-design/SKILL.md"),
    os.path.join(REPO, ".claude/skills/analyze-skill-design/SKILL.md"),
]

FORBIDDEN_TOOLS = ["Bash", "Write", "Edit"]

failures = []

for name in EXPECTED_AGENTS:
    path = os.path.join(AGENTS_DIR, f"{name}.md")
    if not os.path.exists(path):
        failures.append(f"MISSING: {path}")
        continue

    content = open(path).read()

    if "model: haiku" not in content:
        failures.append(f"NOT HAIKU model: {path}")

    tools_match = re.search(r'tools:\s*\[([^\]]*)\]', content)
    if tools_match:
        tools_str = tools_match.group(1)
        for tool in FORBIDDEN_TOOLS:
            if tool in tools_str:
                failures.append(f"FORBIDDEN TOOL '{tool}' in tools list: {path}")

    if "## Output Format" not in content:
        failures.append(f"MISSING '## Output Format' section: {path}")

    if "_No issues found._" not in content:
        failures.append(f"MISSING no-issues pattern: {path}")

for skill_path in SKILLS_TO_CHECK:
    if not os.path.exists(skill_path):
        failures.append(f"MISSING SKILL: {skill_path}")
        continue
    content = open(skill_path).read()
    if "Phase 2" not in content:
        failures.append(f"MISSING 'Phase 2' (parallel dispatch not added): {skill_path}")
    if "parallel" not in content.lower() and "simultaneously" not in content.lower():
        failures.append(f"MISSING parallel dispatch language: {skill_path}")

if failures:
    print(f"FAIL — {len(failures)} issue(s):")
    for f in failures:
        print(f"  {f}")
    sys.exit(1)
else:
    print(f"PASS — {len(EXPECTED_AGENTS)} agents valid, 4 skills refactored.")
```

- [ ] **Step 4: Verify the script was written**

```bash
ls -la /Users/russelllaing/al-dev-shared/scripts/validate-lens-agents.py
wc -l /Users/russelllaing/al-dev-shared/scripts/validate-lens-agents.py
```

Expected: file exists, ~60+ lines.

- [ ] **Step 5: Run the validation script (expect failures — agents not created yet)**

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/validate-lens-agents.py
```

Expected: `FAIL — 20 issue(s)` (all agents missing). This confirms the script runs and will pass once agents are created.

- [ ] **Step 6: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add scripts/validate-lens-agents.py
git -C /Users/russelllaing/al-dev-shared commit -m "feat(lens-agents): add validation script and agents directory"
```

---

## Task 2: Create Five Quality Lens Agents for `/audit-agent-quality`

**Files:**
- Create: `.claude/agents/quality-lens-clarity.md`
- Create: `.claude/agents/quality-lens-structure.md`
- Create: `.claude/agents/quality-lens-description.md`
- Create: `.claude/agents/quality-lens-bloat.md`
- Create: `.claude/agents/quality-lens-name-fit.md`

- [ ] **Step 1: Write `quality-lens-clarity.md`**

```markdown
---
name: quality-lens-clarity
description: Apply Prompt Clarity lens to agent files — identifies ambiguous instructions, vague qualifiers, incomplete conditionals, and pseudo-code blocks. Returns a findings block.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` files |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Prompt Clarity

Read every file path provided in the dispatch prompt. For each file, derive the
agent name from the filename (strip directory path and `.md` extension).

**Check for — flag every occurrence:**
- Instructions interpretable in more than one way — record the ambiguous sentence verbatim
- Vague qualifiers with no operative definition: "as needed", "appropriate", "reasonable", "if necessary"
- `if X` branches with no `else` / `otherwise` clause (incomplete conditional)
- Bash code blocks that are pseudo-code rather than runnable commands: unrecognised
  binary names, unexplained `<placeholder>` syntax, variables defined nowhere
- Steps that reference undefined placeholders or variables

**Severity rules:**
- High: ambiguity that changes observable behavior
- Medium: vague qualifiers with no definition
- Low: minor style issues

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Prompt Clarity Findings
- **[agent-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Prompt Clarity Findings
_No issues found._
```

- [ ] **Step 2: Write `quality-lens-structure.md`**

```markdown
---
name: quality-lens-structure
description: Apply Structural Conventions lens to agent files — checks frontmatter completeness, tool canonicality, Inputs/Outputs tables, header numbering, and code block language tags. Returns a findings block.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` files |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Structural Conventions

Read every file path provided in the dispatch prompt. For each file, derive the
agent name from the filename (strip directory path and `.md` extension).

**Check each file for:**
- Agent filename (without `.md`) matches the `al-dev-<name>` prefix convention
- `description` field is present in YAML frontmatter and is a single sentence
- `model` field is present in YAML frontmatter
- `tools` field is present in YAML frontmatter and contains only canonical names:
  `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `Agent`, `AskUserQuestion`,
  `WebSearch`, `WebFetch`, or `mcp__`-prefixed tool names
- Frontmatter contains no skill-only fields (`argument-hint`, `triggers`) that
  are invalid in agents
- `## Inputs` and `## Outputs` sections are present, or a stated reason explains
  their absence
- Phase/step headers are numbered consistently — not mixing "Phase N" and "Step N"
  in the same file
- Every code block has a language tag (`bash`, `markdown`, `python`, etc.)

**Severity rules:**
- High: missing `model` or `tools` frontmatter fields
- Medium: missing Inputs/Outputs sections, non-canonical tool names, filename not
  matching `al-dev-<name>` convention, or skill-only fields in frontmatter
- Low: numbering inconsistency or missing code block language tags

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Structural Conventions Findings
- **[agent-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Structural Conventions Findings
_No issues found._
```

- [ ] **Step 3: Write `quality-lens-description.md`**

```markdown
---
name: quality-lens-description
description: Apply Description Drift lens to agent files — compares description field against body content to detect disconnected verbs, missing outputs, and caller contract mismatches. Returns a findings block.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` files |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Description Drift

Read every file path provided in the dispatch prompt. For each file, derive the
agent name from the filename (strip directory path and `.md` extension).

**Compare the `description` frontmatter field against the body. Check for:**
- Key action verbs in the description ("Spawns", "Writes", "Reads", "Implements",
  "Audits") that do not appear as actual instructions in the body
- Description names the spawning skill or workflow but body contradicts it
- Description promises an output file that the body does not produce
- Description names the expected caller but the body does not match that caller's
  conventions

**Severity rules:**
- Medium: missing use case or absent promised output
- Low: minor verb mismatch that does not affect behavior

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Description Drift Findings
- **[agent-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Description Drift Findings
_No issues found._
```

- [ ] **Step 4: Write `quality-lens-bloat.md`**

```markdown
---
name: quality-lens-bloat
description: Apply Bloat lens to agent files — detects oversized sections, dead conditional branches, repetitive instruction blocks, and historical commentary. Returns a findings block.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` files |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Bloat

Read every file path provided in the dispatch prompt. For each file, derive the
agent name from the filename (strip directory path and `.md` extension).

**Check for:**
- Section count in the system prompt body (after frontmatter) > 6 top-level sections
- Any single section > 30 lines
- `skip if...` or `only if...` conditions that are effectively always true given
  normal usage (dead branches with no realistic false path)
- Repetitive instruction blocks across sections that could be stated once
- Accumulated historical commentary ("as of v2", "previously this was", "now uses")
  that belongs in git history, not the agent body

**Severity rules:**
- High: any single section > 30 lines or > 6 total top-level sections
- Medium: dead branches or repetitive instruction blocks
- Low: minor historical commentary

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Bloat Findings
- **[agent-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Bloat Findings
_No issues found._
```

- [ ] **Step 5: Write `quality-lens-name-fit.md`**

```markdown
---
name: quality-lens-name-fit
description: Apply Name Fit lens to agent files — compares agent name against primary verb and scope in description and body to detect naming drift and conflicts. Returns a findings block.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` files |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Name Fit

Read every file path provided in the dispatch prompt. For each file, derive the
agent name from the filename (strip directory path and `.md` extension).

**Compare agent name against the primary verb and scope in description and body.
Check for:**
- Name implies X but body primarily does Y (scope has shifted since naming)
- Name is too generic relative to a narrower actual scope
- Another agent file in the provided list has a name so similar a user would
  struggle to choose between them
- Name uses a noun or adjective that conflicts with the agent's actual action verb

**Severity rules:**
- High: name actively misleads a caller about what the agent does
- Medium: moderate drift between name and actual scope
- Low: minor verb mismatch with no behavioral consequence

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Name Fit Findings
- **[agent-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Name Fit Findings
_No issues found._
```

- [ ] **Step 6: Verify all five files were written**

```bash
ls -la /Users/russelllaing/al-dev-shared/.claude/agents/
```

Expected: five files listed — `quality-lens-clarity.md`, `quality-lens-structure.md`, `quality-lens-description.md`, `quality-lens-bloat.md`, `quality-lens-name-fit.md`.

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/agents/quality-lens-clarity.md .claude/agents/quality-lens-structure.md .claude/agents/quality-lens-description.md .claude/agents/quality-lens-bloat.md .claude/agents/quality-lens-name-fit.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(lens-agents): add five quality lens agents for /audit-agent-quality"
```

---

## Task 3: Refactor `/audit-agent-quality` Skill

**Files:**
- Modify: `.claude/skills/audit-agent-quality/SKILL.md`

- [ ] **Step 1: Read the current skill**

Read `.claude/skills/audit-agent-quality/SKILL.md` in full. Note the current line count:

```bash
wc -l /Users/russelllaing/al-dev-shared/.claude/skills/audit-agent-quality/SKILL.md
```

- [ ] **Step 2: Rewrite the skill with Phase 1-2-3 structure**

Replace the full contents of `.claude/skills/audit-agent-quality/SKILL.md` with:

```markdown
---
name: audit-agent-quality
description: >-
  Audit profile-al-dev-shared agents for internal quality: prompt clarity,
  structural conventions, description drift, bloat, and name fit. Reads each
  agent .md directly and writes findings to docs/al-dev-agent-quality.md.
  Run after /analyze-agent-design for a complete picture. Triggers on:
  "audit agent quality", "check agent quality", "are agents well written",
  "agent quality report", "check for agent drift", "agent bloat".
argument-hint: "[agent-name]"
---

# Skill: /audit-agent-quality

Per-file quality audit of al-dev plugin agents. Dispatches five parallel lens
agents, aggregates their findings, and writes a structured report to
`docs/al-dev-agent-quality.md`.

If an argument is passed (e.g., `/audit-agent-quality al-dev-developer`), only
that agent is audited and only its section is updated in the report.

---

## Phase 1 — Discover Agent Files

```bash
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents -name "*.md" | sort
```

Build a list of absolute paths (`file_list`). Derive agent names from filenames
(strip directory path and `.md` extension).

If an argument was passed, filter `file_list` to the single matching path.
Normalize: strip `al-dev-` prefix if present when matching input; always use
`al-dev-<name>` for section headings in the report.

---

## Phase 2 — Parallel Lens Dispatch

Dispatch all five lens agents in a **single response** (five parallel Agent tool calls).

Pass this prompt to each agent, substituting the actual absolute paths:

```
Analyze the following agent files. Apply your lens to every file and return a findings block.

File list:
/absolute/path/to/agent1.md
/absolute/path/to/agent2.md
[one path per line — paste all paths from Phase 1 here]
```

Agents to dispatch simultaneously (use `subagent_type` for each):
- `quality-lens-clarity`
- `quality-lens-structure`
- `quality-lens-description`
- `quality-lens-bloat`
- `quality-lens-name-fit`

Each agent returns one block headed `### [Lens Name] Findings`.

---

## Phase 3 — Aggregate Findings

Collect all five findings blocks. Each block contains lines in this format:
`- **[agent-name]** | [Severity] | [observation] | [fix]`

Reorganize by agent name for the report:

1. Parse every findings line across all five blocks.
2. Group lines by agent name.
3. For each agent with at least one finding:
   - Sort findings by severity: High first, then Medium, then Low.
   - Format each finding with its lens name as the heading.
4. Sort agents: those with High findings first, then Medium, then Low, then clean.
5. Agents with no findings across all five lenses → `### al-dev-<name> — No findings.`

---

## Phase 4 — Write the Report

### Full run (no argument passed)

Fully replace `docs/al-dev-agent-quality.md`. Substitute actual values for all
angle-bracket placeholders before writing:

```markdown
# AL Dev Agent Quality Audit

**Last run:** <today's date>
**Agents audited:** <N>

## Summary

| Severity | Count |
|----------|-------|
| High     | <N>   |
| Medium   | <N>   |
| Low      | <N>   |

## Findings

### al-dev-<agent-name>

**[High] Prompt Clarity**
Observation: <offending text or pattern>
Fix: <one-line suggestion>

**[Medium] Bloat**
Observation: <what is bloated>
Fix: <one-line suggestion>

---

### al-dev-<other-agent> — No findings.

---
```

Ordering: agents with findings first (highest-severity finding descending), then
clean agents. Each agent section ends with `---`.

### Scoped run (argument passed)

1. Read `docs/al-dev-agent-quality.md` if it exists.
2. Locate the section for the named agent — from `### al-dev-<arg>` to just
   before the next `### al-dev-` heading or end of `## Findings`.
3. Build a replacement section with new findings (or `### al-dev-<arg> — No findings.`).
4. Replace in-place using the Edit tool, with the old section as `old_string`.
5. If the section doesn't exist yet: append at the end of `## Findings`.
6. Recalculate Summary counts by scanning all `**[High]`, `**[Medium]`, `**[Low]`
   occurrences in the updated file, then rewrite the Summary table.
7. If `docs/al-dev-agent-quality.md` doesn't exist: write a new full report
   containing only the named agent's section.

---

## Phase 5 — Commit

```bash
git -C /Users/russelllaing/al-dev-shared add docs/al-dev-agent-quality.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: update agent quality audit"
```

For scoped runs, name the target in the commit message:

```bash
git -C /Users/russelllaing/al-dev-shared commit -m "docs: update agent quality audit — al-dev-<agent-name>"
```

---

## Phase 6 — Present to User

Print one line per audited agent:
- With findings: `al-dev-<agent-name>: N High, N Medium, N Low`
- Without findings: `al-dev-<agent-name>: clean`

Ask: "Would you like to fix any of these now?"
```

- [ ] **Step 3: Verify the file was written**

```bash
wc -l /Users/russelllaing/al-dev-shared/.claude/skills/audit-agent-quality/SKILL.md
grep -n "Phase 2\|simultaneously\|parallel" /Users/russelllaing/al-dev-shared/.claude/skills/audit-agent-quality/SKILL.md
```

Expected: file has content, "Phase 2" and "simultaneously" appear in the output.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/skills/audit-agent-quality/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(audit-agent-quality): restructure to three-phase parallel lens dispatch"
```

---

## Task 4: Create Five Design Lens Agents for `/analyze-agent-design`

**Files:**
- Create: `.claude/agents/design-lens-tool-hygiene.md`
- Create: `.claude/agents/design-lens-model-fit.md`
- Create: `.claude/agents/design-lens-scope-isolation.md`
- Create: `.claude/agents/design-lens-caller-alignment.md`
- Create: `.claude/agents/design-lens-usage-patterns.md`

- [ ] **Step 1: Write `design-lens-tool-hygiene.md`**

```markdown
---
name: design-lens-tool-hygiene
description: Apply Tool Hygiene lens to agent files — identifies tools declared in frontmatter but unused in the system prompt body. Returns a findings block for Trim suggestions.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` files |
| tool_inventory | JSON mapping of agent-name → tools-list (provided in dispatch prompt) |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Tool Hygiene (→ Trim)

Read every file path provided in the dispatch prompt. For each file, derive the
agent name from the filename (strip directory path and `.md` extension).

Extract the `tools` field from YAML frontmatter. Read the system prompt body
(everything after the closing `---` of the frontmatter).

**Red flags — a tool present in frontmatter but unused in the body:**
- Agent described as "read-only" or analysis-only but has `Write` or `Edit` in tools
- Agent has `Bash` but no commands or shell operations are mentioned in the body
- Agent has `mcp__`-prefixed tools but no MCP usage is described in the body
- Any tool listed in frontmatter with no corresponding usage verb or code block in body

A tool present in frontmatter but unused in the system prompt body is a Trim candidate.

**Severity rules:**
- High: `Write` or `Edit` on an agent described as read-only or analysis-only
- Medium: `Bash` with no commands, or MCP tools with no MCP usage described
- Low: other declared tools with no evidence of use in the body

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Tool Hygiene Findings
- **[agent-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Tool Hygiene Findings
_No issues found._
```

- [ ] **Step 2: Write `design-lens-model-fit.md`**

```markdown
---
name: design-lens-model-fit
description: Apply Model Fit lens to agent files — evaluates whether haiku/sonnet/opus assignment matches task complexity. Returns a findings block for Remodel suggestions.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` files |
| model_assignments | Mapping of agent-name → current model (provided in dispatch prompt) |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Model Fit (→ Remodel)

Read every file path provided in the dispatch prompt. For each file, derive the
agent name from the filename (strip directory path and `.md` extension).

Check the `model` frontmatter field and evaluate against the task described in the body.

**Model appropriateness criteria:**
- **Haiku-appropriate:** Single-step retrieval, simple API calls, basic
  formatting, mechanical rule-checking — no multi-file reasoning or synthesis
- **Sonnet (default):** Multi-step implementation, code review, analysis tasks
  that require reading and connecting information from several files
- **Opus justified:** Competitive design tasks, multi-file synthesis,
  complex reasoning requiring broad codebase understanding

**Flag as Remodel candidate:**
- `opus` assigned for a task that is single-step, single-file, or purely mechanical
- `sonnet` assigned for a task that is clearly haiku-appropriate (e.g., simple
  grep + format, single API call, basic file read + structured output)

**Severity rules:**
- High: `opus` for a single-step or mechanical task (wasted tokens on every invocation)
- Medium: `sonnet` where `haiku` is clearly sufficient
- Low: `haiku` where `sonnet` might provide marginally better output

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Model Fit Findings
- **[agent-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Model Fit Findings
_No issues found._
```

- [ ] **Step 3: Write `design-lens-scope-isolation.md`**

```markdown
---
name: design-lens-scope-isolation
description: Apply Scope Isolation lens to agent files — identifies agents with two clearly separable concerns in their system prompt body. Returns a findings block for Split suggestions.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` files |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Scope Isolation (→ Split)

Read every file path provided in the dispatch prompt. For each file, derive the
agent name from the filename (strip directory path and `.md` extension).

Read the system prompt body. Ask: does it describe two clearly separable concerns
that could be individual agents?

**Signals of separable concerns:**
- System prompt contains two distinct `## Phase` or `## Mission` sections
  addressing unrelated outputs or different downstream consumers
- The Inputs and Outputs tables serve two different callers or produce two
  unrelated artifacts
- The `description` uses "and" to connect two distinct task categories
- Body length > 50 lines where two distinct tasks can be cleanly identified by
  deleting one contiguous block

A system prompt with two separable concerns is a Split candidate.

**Severity rules:**
- High: two completely unrelated concerns with separate output destinations
- Medium: two related concerns that could be cleanly separated with clear benefits
- Low: minor scope overlap that could be separated but may not be worth the
  maintenance overhead

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Scope Isolation Findings
- **[agent-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Scope Isolation Findings
_No issues found._
```

- [ ] **Step 4: Write `design-lens-caller-alignment.md`**

```markdown
---
name: design-lens-caller-alignment
description: Apply Caller Alignment lens to agent files — compares documented Inputs/Outputs against how spawning skills actually invoke each agent. Returns a findings block for Align suggestions.
model: haiku
tools: ["Read", "Glob", "Grep"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` files |
| caller_map | Mapping of agent-name → list of skill names that spawn it (provided in dispatch prompt) |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Caller Alignment (→ Align)

Read every file path provided in the dispatch prompt. For each file, derive the
agent name from the filename (strip directory path and `.md` extension).

Extract the `## Inputs` and `## Outputs` sections. Then use the Grep tool to
check how each spawning skill actually invokes the agent. Search the skills
directory:

- Pattern: `al-dev-<agent-name>` in `/Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/`

**Red flags:**
- Spawning skill passes a structured context block (file paths, data) that the
  agent's Inputs table does not document
- Agent's Outputs table names a file the spawning skill never reads or references
- Agent Inputs table says "Not documented" but the spawning skill passes a
  structured prompt with specific fields

A mismatch between caller behaviour and agent documentation is an Align candidate.

**Severity rules:**
- High: caller passes structured data the agent's Inputs table explicitly contradicts
- Medium: Inputs/Outputs table is "Not documented" but caller clearly passes
  structured context
- Low: minor label mismatch that doesn't affect behavior but confuses future callers

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Caller Alignment Findings
- **[agent-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Caller Alignment Findings
_No issues found._
```

- [ ] **Step 5: Write `design-lens-usage-patterns.md`**

```markdown
---
name: design-lens-usage-patterns
description: Apply Usage Patterns lens to agent files — identifies single-use agents with small bodies and no documented contract, which are candidates for inlining. Returns a findings block for Inline suggestions.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` files |
| single_use_agents | Comma-separated agent names spawned by exactly one skill (provided in dispatch prompt) |
| already_inline_candidates | Comma-separated agent names already listed in docs/al-dev-agent-map.md Inline candidates section (provided in dispatch prompt) |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Usage Patterns (→ Inline)

Read every file path provided in the dispatch prompt. For each file, derive the
agent name from the filename (strip directory path and `.md` extension).

**Inline criteria — all three must apply:**
1. Agent name appears in the `single_use_agents` list (spawned by exactly one skill)
2. System prompt body (everything after the closing `---` of frontmatter) is
   fewer than 15 lines
3. No `## Inputs` or `## Outputs` tables are documented in the body

Skip any agent whose name appears in `already_inline_candidates` — it has already
been flagged in a previous run.

An agent meeting all three criteria is an Inline candidate.

**Severity rules:**
- Medium: agent meets all three criteria
- Low: agent meets exactly two of three criteria

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Usage Patterns Findings
- **[agent-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Usage Patterns Findings
_No issues found._
```

- [ ] **Step 6: Verify all five files were written**

```bash
ls -la /Users/russelllaing/al-dev-shared/.claude/agents/design-lens-*.md
```

Expected: five files listed.

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/agents/design-lens-tool-hygiene.md .claude/agents/design-lens-model-fit.md .claude/agents/design-lens-scope-isolation.md .claude/agents/design-lens-caller-alignment.md .claude/agents/design-lens-usage-patterns.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(lens-agents): add five design lens agents for /analyze-agent-design"
```

---

## Task 5: Refactor `/analyze-agent-design` Skill

**Files:**
- Modify: `.claude/skills/analyze-agent-design/SKILL.md`

The current skill has 7 steps. Only Step 2 (the lens analysis) becomes parallel;
Steps 1 and 3–7 remain inline. The refactored skill gains a Phase 3 (aggregate)
between the dispatch and the existing suggestion-drafting step.

- [ ] **Step 1: Read the current skill**

Read `.claude/skills/analyze-agent-design/SKILL.md` in full.

- [ ] **Step 2: Replace Step 2 in the skill with Phase 1 / Phase 2 / Phase 3**

Using the Edit tool, replace the section from `## Step 1` through the end of
`## Step 2` (the five lenses) with the following content. Leave Steps 3–7
(Draft Suggestions, Inventory Tables, Workflow Diagram, Write, Present) unchanged
but renumber them as Phases 4–8.

Replace this block (from `## Step 1` to the end of `## Step 2 — Apply Five Analytical Lenses`):

```
## Step 1 — Read the Agent Map and Build Working Lists
```

With this replacement (Phase 1 through end of Phase 3):

```markdown
## Phase 1 — Read the Agent Map and Build Working Lists

Read `docs/al-dev-agent-map.md` in full. Build these working lists:

1. **Tool inventory** — for every agent, record its tools list from the map.
2. **Model assignments** — for every agent, record its model.
3. **Caller map** — for every agent, record which skills spawn it.
4. **Single-use agents** — agents spawned by exactly one skill.
5. **Shared agents** — agents spawned by 2+ skills.
6. **Undocumented agents** — agents with "Not documented" for both Inputs and Outputs.
7. **Existing inline candidates** — agents already listed in `### Inline candidates`
   in `docs/al-dev-agent-map.md`.

If an argument was passed, restrict analysis to that lens:
`trim`, `remodel`, `split`, `inline`, `align`, or `all` / no argument = `all`.

Also run this command to get agent file paths:

```bash
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents -name "*.md" | sort
```

---

## Phase 2 — Parallel Lens Dispatch

Dispatch the relevant lens agents in a **single response** (parallel Agent tool calls).

For each agent, pass this prompt (substituting actual data from Phase 1):

```
Analyze the following agent files. Apply your lens and return a findings block.

## File list
/absolute/path/to/agent1.md
/absolute/path/to/agent2.md
[one path per line]

## Context from map analysis
Tool inventory (agent → tools):
[paste tool_inventory here]

Model assignments (agent → model):
[paste model_assignments here]

Caller map (agent → spawning skills):
[paste caller_map here]

Single-use agents (spawned by exactly one skill):
[comma-separated list]

Already-listed inline candidates:
[comma-separated list from docs/al-dev-agent-map.md]
```

Agents to dispatch based on the focus argument:
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

Each agent returns one block headed `### [Lens Name] Findings`.

---

## Phase 3 — Aggregate Findings

Collect all returned findings blocks. Parse each line:
`- **[agent-name]** | [Severity] | [observation] | [fix]`

Group by lens type to produce candidate lists for Phase 4:
- **Trim candidates** — agents from Tool Hygiene findings
- **Remodel candidates** — agents from Model Fit findings
- **Split candidates** — agents from Scope Isolation findings
- **Align candidates** — agents from Caller Alignment findings
- **Inline candidates** — agents from Usage Patterns findings

Keep the raw findings lines — they form the basis of Phase 4 suggestions.

---
```

Then rename the remaining steps:
- `## Step 3 — Draft Suggestions` → `## Phase 4 — Draft Suggestions`
- `## Step 4 — Complete Inventory Tables` → `## Phase 5 — Complete Inventory Tables`
- `## Step 5 — Generate Workflow Diagram` → `## Phase 6 — Generate Workflow Diagram`
- `## Step 6 — Write to docs/al-dev-agent-map.md` → `## Phase 7 — Write to docs/al-dev-agent-map.md`
- `## Step 7 — Present to User` → `## Phase 8 — Present to User`

- [ ] **Step 3: Verify the refactored skill**

```bash
grep -n "Phase [0-9]\|simultaneously\|parallel" /Users/russelllaing/al-dev-shared/.claude/skills/analyze-agent-design/SKILL.md
```

Expected: Phase 1 through Phase 8 appear, plus "simultaneously".

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/skills/analyze-agent-design/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(analyze-agent-design): restructure Step 2 to parallel lens dispatch"
```

---

## Task 6: Create Five Quality-Skill Lens Agents for `/audit-skill-quality`

**Files:**
- Create: `.claude/agents/quality-skill-lens-clarity.md`
- Create: `.claude/agents/quality-skill-lens-structure.md`
- Create: `.claude/agents/quality-skill-lens-description.md`
- Create: `.claude/agents/quality-skill-lens-bloat.md`
- Create: `.claude/agents/quality-skill-lens-name-fit.md`

These are skill-focused variants of the quality lenses. Lenses 1 (Clarity), 3
(Description), and 5 (Name Fit) share the same rules but apply to SKILL.md files.
Lenses 2 (Structure) and 4 (Bloat) have skill-specific rules that differ from the
agent versions.

- [ ] **Step 1: Write `quality-skill-lens-clarity.md`**

```markdown
---
name: quality-skill-lens-clarity
description: Apply Prompt Clarity lens to SKILL.md files — identifies ambiguous instructions, vague qualifiers, incomplete conditionals, and pseudo-code blocks. Returns a findings block.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Prompt Clarity

Read every file path provided in the dispatch prompt. For each file, derive the
skill name from the parent directory name (e.g., `.../skills/al-dev-develop/SKILL.md`
→ skill name `al-dev-develop`).

**Check for — flag every occurrence:**
- Instructions interpretable in more than one way — record the ambiguous sentence verbatim
- Vague qualifiers with no operative definition: "as needed", "appropriate", "reasonable", "if necessary"
- `if X` branches with no `else` / `otherwise` clause (incomplete conditional)
- Bash code blocks that are pseudo-code rather than runnable commands: unrecognised
  binary names, unexplained `<placeholder>` syntax, variables defined nowhere
- Steps that reference undefined placeholders or variables

**Severity rules:**
- High: ambiguity that changes observable behavior
- Medium: vague qualifiers with no definition
- Low: minor style issues

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Prompt Clarity Findings
- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Prompt Clarity Findings
_No issues found._
```

- [ ] **Step 2: Write `quality-skill-lens-structure.md`**

```markdown
---
name: quality-skill-lens-structure
description: Apply Structural Conventions lens to SKILL.md files — checks frontmatter fields, argument-hint presence, output file naming, header numbering, and code block language tags. Returns a findings block.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Structural Conventions

Read every file path provided in the dispatch prompt. For each file, derive the
skill name from the parent directory name.

**Check each file for:**
- `name` field in YAML frontmatter matches the parent directory name exactly
- `description` field is present in frontmatter
- `argument-hint` is present in frontmatter when the body references an
  optional argument (look for `If an argument was passed` or `[arg]` patterns)
- Phase/step headers are numbered consistently — not mixing "Phase N" and
  "Step N" in the same file
- Output files referenced in the body follow the `.dev/YYYY-MM-DD-<skill>-*.md`
  naming convention (or `docs/` for persistent report-style outputs)
- Every code block has a language tag (`bash`, `markdown`, `python`, etc.)

**Severity rules:**
- Medium: missing or inconsistent frontmatter fields, `argument-hint` absent
  when body uses optional argument, output file naming doesn't follow convention
- Low: numbering inconsistency or missing code block language tags

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Structural Conventions Findings
- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Structural Conventions Findings
_No issues found._
```

- [ ] **Step 3: Write `quality-skill-lens-description.md`**

```markdown
---
name: quality-skill-lens-description
description: Apply Description Drift lens to SKILL.md files — compares description and trigger phrases against body content to detect disconnected verbs, missing outputs, and absent use cases. Returns a findings block.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Description Drift

Read every file path provided in the dispatch prompt. For each file, derive the
skill name from the parent directory name.

**Compare the `description` frontmatter and trigger phrases against the body.
Check for:**
- Key action verbs in the description ("Spawns", "Writes", "Reads", "Audits")
  that do not appear as actual instructions in the body
- Trigger phrases describing use cases that are absent from the body steps
- Related skills or agents mentioned in the description that do not appear in
  the body
- Description that promises an output file the body does not produce

**Severity rules:**
- Medium: missing use case, absent promised output, or related skill/agent
  mentioned in description but not used in body
- Low: minor verb mismatch that does not affect behavior

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Description Drift Findings
- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Description Drift Findings
_No issues found._
```

- [ ] **Step 4: Write `quality-skill-lens-bloat.md`**

```markdown
---
name: quality-skill-lens-bloat
description: Apply Bloat lens to SKILL.md files — detects oversized steps, dead conditional branches, repetitive instruction blocks, and historical commentary. Returns a findings block.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Bloat

Read every file path provided in the dispatch prompt. For each file, derive the
skill name from the parent directory name.

**Check for:**
- Step/phase count (top-level `## Step` or `## Phase` headers) > 6
- Any single step > 30 lines
- `skip if...` or `only if...` conditions that are effectively always true given
  normal usage (dead branches with no realistic false path)
- Repetitive instruction blocks across steps that could be stated once
- Accumulated historical commentary ("as of v2", "previously this was", "now uses")
  that belongs in git history, not the skill body

**Severity rules:**
- High: any single step > 30 lines or > 8 total top-level steps
- Medium: dead branches or repetitive instruction blocks
- Low: minor historical commentary

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Bloat Findings
- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Bloat Findings
_No issues found._
```

- [ ] **Step 5: Write `quality-skill-lens-name-fit.md`**

```markdown
---
name: quality-skill-lens-name-fit
description: Apply Name Fit lens to SKILL.md files — compares skill name against primary verb and scope in description and body to detect naming drift and trigger-phrase conflicts. Returns a findings block.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Name Fit

Read every file path provided in the dispatch prompt. For each file, derive the
skill name from the parent directory name.

**Compare skill name against the primary verb and scope in description and body.
Check for:**
- Name implies X but body primarily does Y (scope has shifted since naming)
- Name is too generic relative to a narrower actual scope
- Another skill in the file list has a name so similar a user would struggle
  to choose between them
- Name uses an action verb inconsistent with how the skill is triggered
  (e.g., trigger phrases describe a different action than the name suggests)

**Severity rules:**
- High: name actively misleads a user about what the skill does when invoked
- Medium: moderate drift between name and actual scope or trigger phrases
- Low: minor verb mismatch with no behavioral consequence

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Name Fit Findings
- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Name Fit Findings
_No issues found._
```

- [ ] **Step 6: Verify all five files were written**

```bash
ls -la /Users/russelllaing/al-dev-shared/.claude/agents/quality-skill-lens-*.md
```

Expected: five files listed.

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/agents/quality-skill-lens-clarity.md .claude/agents/quality-skill-lens-structure.md .claude/agents/quality-skill-lens-description.md .claude/agents/quality-skill-lens-bloat.md .claude/agents/quality-skill-lens-name-fit.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(lens-agents): add five quality-skill lens agents for /audit-skill-quality"
```

---

## Task 7: Refactor `/audit-skill-quality` Skill

**Files:**
- Modify: `.claude/skills/audit-skill-quality/SKILL.md`

Same structural change as Task 3 but referencing skill paths and the five
`quality-skill-lens-*` agents.

- [ ] **Step 1: Read the current skill**

Read `.claude/skills/audit-skill-quality/SKILL.md` in full.

- [ ] **Step 2: Rewrite the skill with Phase 1-2-3 structure**

Replace the full contents of `.claude/skills/audit-skill-quality/SKILL.md` with:

```markdown
---
name: audit-skill-quality
description: >-
  Audit profile-al-dev-shared skills for internal quality: prompt clarity,
  structural conventions, description drift, bloat, and name fit. Reads each
  SKILL.md directly and writes findings to docs/al-dev-skill-quality.md.
  Run after /analyze-skill-design for a complete picture. Triggers on:
  "audit skill quality", "check skill quality", "are skills well written",
  "skill quality report", "check for skill drift", "skill bloat".
argument-hint: "[skill-name]"
---

# Skill: /audit-skill-quality

Per-file quality audit of al-dev plugin skills. Dispatches five parallel lens
agents, aggregates their findings, and writes a structured report to
`docs/al-dev-skill-quality.md`.

If an argument is passed (e.g., `/audit-skill-quality al-dev-develop`), only
that skill is audited and only its section is updated in the report.

---

## Phase 1 — Discover Skill Files

```bash
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills -name "SKILL.md" | sort
```

Build a list of absolute paths (`file_list`). Derive skill names from the parent
directory name (e.g., `.../skills/al-dev-develop/SKILL.md` → `al-dev-develop`).

If an argument was passed, filter `file_list` to the single matching path.
Normalize: strip `/` prefix if present when matching input; always use `/<name>`
for section headings in the report.

---

## Phase 2 — Parallel Lens Dispatch

Dispatch all five lens agents in a **single response** (five parallel Agent tool calls).

Pass this prompt to each agent, substituting the actual absolute paths:

```
Analyze the following SKILL.md files. Apply your lens to every file and return a findings block.

File list:
/absolute/path/to/skills/skill-name/SKILL.md
/absolute/path/to/skills/other-skill/SKILL.md
[one path per line — paste all paths from Phase 1 here]
```

Agents to dispatch simultaneously (use `subagent_type` for each):
- `quality-skill-lens-clarity`
- `quality-skill-lens-structure`
- `quality-skill-lens-description`
- `quality-skill-lens-bloat`
- `quality-skill-lens-name-fit`

Each agent returns one block headed `### [Lens Name] Findings`.

---

## Phase 3 — Aggregate Findings

Collect all five findings blocks. Each block contains lines in this format:
`- **[skill-name]** | [Severity] | [observation] | [fix]`

Reorganize by skill name for the report:

1. Parse every findings line across all five blocks.
2. Group lines by skill name.
3. For each skill with at least one finding:
   - Sort findings by severity: High first, then Medium, then Low.
   - Format each finding with its lens name as the heading.
4. Sort skills: those with High findings first, then Medium, then Low, then clean.
5. Skills with no findings across all five lenses → `### /<name> — No findings.`

---

## Phase 4 — Write the Report

### Full run (no argument passed)

Fully replace `docs/al-dev-skill-quality.md`. Substitute actual values for all
angle-bracket placeholders before writing:

```markdown
# AL Dev Skill Quality Audit

**Last run:** <today's date>
**Skills audited:** <N>

## Summary

| Severity | Count |
|----------|-------|
| High     | <N>   |
| Medium   | <N>   |
| Low      | <N>   |

## Findings

### /<skill-name>

**[High] Prompt Clarity**
Observation: <offending text or pattern>
Fix: <one-line suggestion>

**[Medium] Bloat**
Observation: <what is bloated>
Fix: <one-line suggestion>

---

### /<other-skill> — No findings.

---
```

Ordering: skills with findings first (highest-severity finding descending), then
clean skills. Each skill section ends with `---`.

### Scoped run (argument passed)

1. Read `docs/al-dev-skill-quality.md` if it exists.
2. Locate the section for the named skill — from `### /<arg>` to just before
   the next `### /` heading or end of `## Findings`.
3. Build a replacement section with new findings (or `### /<arg> — No findings.`).
4. Replace in-place using the Edit tool, with the old section as `old_string`.
5. If the section doesn't exist yet: append at the end of `## Findings`.
6. Recalculate Summary counts by scanning all `**[High]`, `**[Medium]`, `**[Low]`
   occurrences in the updated file, then rewrite the Summary table.
7. If `docs/al-dev-skill-quality.md` doesn't exist: write a new full report
   containing only the named skill's section.

---

## Phase 5 — Commit

```bash
git -C /Users/russelllaing/al-dev-shared add docs/al-dev-skill-quality.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: update skill quality audit"
```

For scoped runs, name the target in the commit message:

```bash
git -C /Users/russelllaing/al-dev-shared commit -m "docs: update skill quality audit — /<skill-name>"
```

---

## Phase 6 — Present to User

Print one line per audited skill:
- With findings: `/<skill-name>: N High, N Medium, N Low`
- Without findings: `/<skill-name>: clean`

Ask: "Would you like to fix any of these now?"
```

- [ ] **Step 3: Verify the file was written**

```bash
grep -n "Phase 2\|simultaneously\|quality-skill-lens" /Users/russelllaing/al-dev-shared/.claude/skills/audit-skill-quality/SKILL.md
```

Expected: "Phase 2", "simultaneously", and all five `quality-skill-lens-*` names appear.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/skills/audit-skill-quality/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(audit-skill-quality): restructure to three-phase parallel lens dispatch"
```

---

## Task 8: Create Five Design-Skill Lens Agents for `/analyze-skill-design`

**Files:**
- Create: `.claude/agents/design-skill-lens-shared-backbone.md`
- Create: `.claude/agents/design-skill-lens-complexity.md`
- Create: `.claude/agents/design-skill-lens-near-duplicates.md`
- Create: `.claude/agents/design-skill-lens-handoff-gaps.md`
- Create: `.claude/agents/design-skill-lens-preplanning.md`

These agents apply architectural lenses to the plugin's skills, using the plugin
map data provided in their dispatch prompt.

- [ ] **Step 1: Write `design-skill-lens-shared-backbone.md`**

```markdown
---
name: design-skill-lens-shared-backbone
description: Apply Shared Execution Backbone lens to plugin skills — identifies agent types used by 2+ skills whose invocation patterns could be documented in knowledge/ to prevent drift. Returns findings for Connect/Promote suggestions.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |
| agent_usage_counts | Mapping of agent-type → list of skills that use it (provided in dispatch prompt) |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Shared Execution Backbone (→ Connect or Promote)

Read every file path provided in the dispatch prompt. Use `agent_usage_counts` to
identify agent types used by 2 or more skills.

For each such agent type:
1. Read the relevant SKILL.md files to compare how each skill spawns the agent.
2. Ask: are the spawn patterns identical or significantly different?
   - **Identical patterns** → Connect candidate: document a canonical invocation
     in `knowledge/` to prevent drift.
   - **Different patterns** → Promote candidate: make the variation explicit and
     decide if a shared base pattern is worth extracting.

**What constitutes an "identical" pattern:**
- Same dispatch prompt template
- Same context fields passed
- Same output expectation

**Severity rules:**
- Medium: identical pattern copy-pasted across 2+ skills (drift risk when pattern needs updating)
- Low: similar but not identical patterns (worth noting but lower urgency)

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Shared Execution Backbone Findings
- **[agent-type]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Shared Execution Backbone Findings
_No issues found._
```

- [ ] **Step 2: Write `design-skill-lens-complexity.md`**

```markdown
---
name: design-skill-lens-complexity
description: Apply Complexity Outliers lens to plugin skills — ranks skills by phase count to find high-phase skills with separable concerns (Atomise) and zero-agent 2-phase skills (Absorb candidates). Returns findings.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |
| phase_counts | Mapping of skill-name → phase/step count (provided in dispatch prompt) |
| no_agent_skills | List of skills with no dedicated agent spawned (provided in dispatch prompt) |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Complexity Outliers (→ Atomise or Absorb)

Read every file path provided in the dispatch prompt. Use `phase_counts` for ranking.

**High-phase skills (6+ phases):**
Read each. Ask: do the phases cluster into two distinct concerns (e.g., pre-flight +
execution, or discovery + analysis + output)? If two distinct concern groups are
identifiable by deleting a contiguous block of phases, flag as Atomise candidate.

**Zero-agent, 2-phase skills (from `no_agent_skills`):**
Ask: could this skill be absorbed into an adjacent skill as an option flag or
sub-step rather than a separate invocation? Flag as Absorb candidate if the
skill's entire body could fit as one extra phase in an existing adjacent skill.

**Severity rules:**
- High: skill has 8+ phases with two clearly separable concerns (significant
  cognitive load on every invocation)
- Medium: skill has 6-7 phases with separable concerns, or zero-agent 2-phase
  skill that overlaps heavily with an adjacent skill
- Low: minor complexity that warrants monitoring but not immediate action

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Complexity Outliers Findings
- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Complexity Outliers Findings
_No issues found._
```

- [ ] **Step 3: Write `design-skill-lens-near-duplicates.md`**

```markdown
---
name: design-skill-lens-near-duplicates
description: Apply Near-Duplicate Shapes lens to plugin skills — identifies pairs with similar structure (same agents, similar phase count, similar output patterns) that could be merged. Returns findings for Merge suggestions.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |
| agent_usage_counts | Mapping of agent-type → list of skills that use it (provided in dispatch prompt) |
| phase_counts | Mapping of skill-name → phase/step count (provided in dispatch prompt) |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Near-Duplicate Shapes (→ Merge)

Read the relevant file paths. Use `agent_usage_counts` to find pairs of skills
that use the same agent types.

For each pair sharing the same agent types:
1. Compare phase counts. If within 2 of each other, read both files.
2. Ask: is the difference between them a small delta (one extra phase, one extra
   output file, one additional reviewer)? 
3. If yes: could the simpler skill become an option or mode of the more complex one?

**Merge criteria (all should be true):**
- Both skills use the same agent types
- Phase counts within 2 of each other
- The unique elements of the simpler skill could be expressed as an option flag
  on the more complex skill (e.g., `--quick`, `--dry-run`, `--light`)

**Severity rules:**
- Medium: pair meets all merge criteria and users would plausibly confuse the two
- Low: pair is similar but serves clearly distinct purposes that justify two skills

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Near-Duplicate Shapes Findings
- **[skill-a + skill-b]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Near-Duplicate Shapes Findings
_No issues found._
```

- [ ] **Step 4: Write `design-skill-lens-handoff-gaps.md`**

```markdown
---
name: design-skill-lens-handoff-gaps
description: Apply Handoff Chain Gaps lens to plugin skills — traces .dev/ file handoff chains to find established chains with obvious next steps or orphaned outputs. Returns findings for Extend suggestions.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |
| handoff_chains | Traced chains of .dev/ file handoffs between skills (provided in dispatch prompt) |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Handoff Chain Gaps (→ Extend)

Read every file path provided in the dispatch prompt. Use `handoff_chains` for
chain analysis.

**Look for:**
1. A well-established chain that has an obvious next step not yet covered:
   e.g., a chain ending at `commit` where a natural `release` or `deploy` step
   would complete the workflow.
2. Outputs produced by one skill (listed in body as "writes X.md") that are
   never referenced as inputs by any other skill — orphaned outputs that could
   be useful if consumed.

**Established chain criteria:**
- 3+ skills connected via .dev/ file handoffs
- The final output of the chain is commonly useful for a task not yet in the plugin

**Severity rules:**
- Medium: well-established chain with an obvious gap that would serve a frequent use case
- Low: orphaned output or possible extension that serves an infrequent use case

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Handoff Chain Gaps Findings
- **[chain-endpoint or orphaned-output]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Handoff Chain Gaps Findings
_No issues found._
```

- [ ] **Step 5: Write `design-skill-lens-preplanning.md`**

```markdown
---
name: design-skill-lens-preplanning
description: Apply Pre-planning Skills lens to plugin skills — checks whether pre-planning/brainstorming skills appear correctly in the Layer 1 diagram as dashed tributary arrows and have named outputs referenced downstream. Returns findings.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |
| preplanning_skills | List of skills identified as pre-planning tributaries (provided in dispatch prompt) |
| layer1_diagram_content | Content of the Layer 1 diagram from docs/al-dev-plugin-map.md (provided in dispatch prompt) |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Pre-planning and Brainstorming Skills

Canonical pre-planning skills in this plugin:
- `/al-dev-interview` — produces `interview-requirements.md`
- `/al-dev-explore` — produces `explore-findings.md`

For each skill in `preplanning_skills` and any additional pre-planning skills
found in the file list:

1. Check whether it appears in `layer1_diagram_content` as a dashed tributary
   arrow (`-.->`) rather than a main-spine node.
2. Check whether its output filename is referenced in Layer 1 handoff labels.
3. Check whether a downstream skill explicitly names it as an input in its body.

**Flag as Extend candidate:**
- Pre-planning skill is active (has a SKILL.md) but absent from the Layer 1 diagram entirely
- Pre-planning skill feeds a downstream step but its output is unnamed in the diagram

**Severity rules:**
- Medium: active pre-planning skill entirely absent from Layer 1 diagram
- Low: skill present in diagram but output filename not referenced in handoff labels

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Pre-planning Skills Findings
- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Pre-planning Skills Findings
_No issues found._
```

- [ ] **Step 6: Verify all five files were written**

```bash
ls -la /Users/russelllaing/al-dev-shared/.claude/agents/design-skill-lens-*.md
```

Expected: five files listed.

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/agents/design-skill-lens-shared-backbone.md .claude/agents/design-skill-lens-complexity.md .claude/agents/design-skill-lens-near-duplicates.md .claude/agents/design-skill-lens-handoff-gaps.md .claude/agents/design-skill-lens-preplanning.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(lens-agents): add five design-skill lens agents for /analyze-skill-design"
```

---

## Task 9: Refactor `/analyze-skill-design` Skill

**Files:**
- Modify: `.claude/skills/analyze-skill-design/SKILL.md`

The current skill has 6 steps. Only Step 2 (the lens analysis) becomes parallel.
Steps 1 and 3–6 remain inline, renumbered as Phases.

- [ ] **Step 1: Read the current skill**

Read `.claude/skills/analyze-skill-design/SKILL.md` in full.

- [ ] **Step 2: Replace Steps 1-2 with Phase 1 / Phase 2 / Phase 3**

Using the Edit tool, replace the section from `## Step 1` through the end of
`## Step 2 — Apply Four Analytical Lenses` with:

```markdown
## Phase 1 — Read the Plugin Map and Build Working Lists

Read `docs/al-dev-plugin-map.md` in full. Build these working lists:

1. **Agent usage counts** — for every `al-dev-shared:` agent type mentioned in
   drill-downs, record which skills use it and how many times.
2. **Phase counts** — record the number of named phases per skill.
3. **File handoff chains** — trace `.dev/` output files. Note when one skill's
   output is consumed by another.
4. **No-agent skills** — list skills whose drill-down contains only `(skill itself)`
   nodes.
5. **Pre-planning tributaries** — list skills that produce output files consumed
   by `/al-dev-plan` or `/al-dev-investigate`. Note whether each appears in the
   Layer 1 diagram as a dashed tributary arrow (`-.->`).

Also read the Layer 1 diagram content from `docs/al-dev-plugin-map.md` for use
in the pre-planning lens.

Get SKILL.md file paths:

```bash
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills -name "SKILL.md" | sort
```

If an argument was passed, restrict analysis to that category
(`atomise`, `connect`, `merge`, or `all` / no argument = `all`).

---

## Phase 2 — Parallel Lens Dispatch

Dispatch the relevant lens agents in a **single response** (parallel Agent tool calls).

For each agent, pass this prompt (substituting actual data from Phase 1):

```
Analyze the following skill files. Apply your lens and return a findings block.

## File list
/absolute/path/to/skills/skill-name/SKILL.md
[one path per line]

## Context from plugin map analysis
Agent usage counts (agent-type → skills that use it):
[paste agent_usage_counts here]

Phase counts (skill-name → count):
[paste phase_counts here]

No-agent skills:
[comma-separated list]

Handoff chains:
[paste handoff_chains here — skill → output-file → consuming-skill]

Pre-planning skills:
[comma-separated list]

Layer 1 diagram content:
[paste the Layer 1 diagram block from docs/al-dev-plugin-map.md]
```

Agents to dispatch based on the focus argument:
- `all` or no argument: dispatch all five simultaneously
  - `design-skill-lens-shared-backbone`
  - `design-skill-lens-complexity`
  - `design-skill-lens-near-duplicates`
  - `design-skill-lens-handoff-gaps`
  - `design-skill-lens-preplanning`
- `connect`: dispatch only `design-skill-lens-shared-backbone`
- `atomise`: dispatch only `design-skill-lens-complexity`
- `merge`: dispatch only `design-skill-lens-near-duplicates`

Each agent returns one block headed `### [Lens Name] Findings`.

---

## Phase 3 — Aggregate Findings

Collect all returned findings blocks. Parse each line:
`- **[subject]** | [Severity] | [observation] | [fix]`

Group by lens type to produce candidate lists for Phase 4:
- **Connect/Promote candidates** — from Shared Execution Backbone findings
- **Atomise/Absorb candidates** — from Complexity Outliers findings
- **Merge candidates** — from Near-Duplicate Shapes findings
- **Extend candidates** — from Handoff Chain Gaps findings
- **Diagram/labelling gaps** — from Pre-planning Skills findings

Keep the raw findings lines — they form the basis of Phase 4 suggestions.

---
```

Then rename Steps 3–6 to Phases 4–7:
- `## Step 3 — Draft Suggestions` → `## Phase 4 — Draft Suggestions`
- `## Step 4 — Complete the Agent Inventory Tables` → `## Phase 5 — Complete the Agent Inventory Tables`
- `## Step 5 — Write to docs/al-dev-plugin-map.md` → `## Phase 6 — Write to docs/al-dev-plugin-map.md`
- `## Step 6 — Present to User` → `## Phase 7 — Present to User`

- [ ] **Step 3: Verify the refactored skill**

```bash
grep -n "Phase [0-9]\|simultaneously\|design-skill-lens" /Users/russelllaing/al-dev-shared/.claude/skills/analyze-skill-design/SKILL.md
```

Expected: Phase 1 through Phase 7 appear, "simultaneously" appears, and all five
`design-skill-lens-*` names appear.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/skills/analyze-skill-design/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(analyze-skill-design): restructure Step 2 to parallel lens dispatch"
```

---

## Task 10: Run Validation and Final Commit

**Files:**
- No new files — verification only.

- [ ] **Step 1: Run the validation script**

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/validate-lens-agents.py
```

Expected output:
```
PASS — 20 agents valid, 4 skills refactored.
```

- [ ] **Step 2: If validation fails, fix before proceeding**

For each failure line:
- `MISSING: ...` → the agent file was not written; re-run the corresponding task step.
- `NOT HAIKU model: ...` → the file has wrong model; edit the frontmatter.
- `FORBIDDEN TOOL '...' in tools list: ...` → edit the tools array in frontmatter.
- `MISSING '## Output Format': ...` → add the Output Format section.
- `MISSING no-issues pattern: ...` → add `_No issues found._` to the Output Format section.
- `MISSING 'Phase 2': ...` → the skill was not refactored; re-run the corresponding task.
- `MISSING parallel dispatch language: ...` → the skill lacks "simultaneously" or "parallel"; add it.

Re-run the script after each fix until output is `PASS`.

- [ ] **Step 3: Verify git status shows all expected changes**

```bash
git -C /Users/russelllaing/al-dev-shared status
```

Expected: working tree clean (all changes committed in Tasks 1–9).

- [ ] **Step 4: Confirm acceptance criteria**

Run these manual checks:

```bash
# 1. All 20 agents exist
ls /Users/russelllaing/al-dev-shared/.claude/agents/ | wc -l
```
Expected: 20

```bash
# 2. No lens agent uses Bash, Write, or Edit in tools
grep -l "Bash\|\"Write\"\|\"Edit\"" /Users/russelllaing/al-dev-shared/.claude/agents/*.md
```
Expected: no output (no files match).

```bash
# 3. All lens agents use haiku model
grep -L "model: haiku" /Users/russelllaing/al-dev-shared/.claude/agents/*.md
```
Expected: no output (all files have haiku).

```bash
# 4. All four skills have Phase 2
grep -l "Phase 2" /Users/russelllaing/al-dev-shared/.claude/skills/audit-agent-quality/SKILL.md /Users/russelllaing/al-dev-shared/.claude/skills/audit-skill-quality/SKILL.md /Users/russelllaing/al-dev-shared/.claude/skills/analyze-agent-design/SKILL.md /Users/russelllaing/al-dev-shared/.claude/skills/analyze-skill-design/SKILL.md | wc -l
```
Expected: 4

- [ ] **Step 5: If any acceptance check fails, fix and re-verify**

- [ ] **Step 6: Final commit (only if any fixes were needed in Step 2 or 5)**

```bash
git -C /Users/russelllaing/al-dev-shared add -p
git -C /Users/russelllaing/al-dev-shared commit -m "fix(lens-agents): address validation failures"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task that implements it |
|---|---|
| `/audit-agent-quality` spawns 5 parallel lens agents | Task 2 (agents) + Task 3 (skill) |
| `/analyze-agent-design` restructured with Phase 2 | Task 4 (agents) + Task 5 (skill) |
| `/audit-skill-quality` same pattern | Task 6 (agents) + Task 7 (skill) |
| `/analyze-skill-design` same pattern | Task 8 (agents) + Task 9 (skill) |
| Each lens agent uses `haiku` model | All agent tasks — verified in Task 10 Step 4 |
| No lens agent has Bash/Write/Edit | All agent tasks — verified in Task 10 Step 4 |
| Aggregation merges findings by file | Task 3 Phase 3, Task 5 Phase 3, Task 7 Phase 3, Task 9 Phase 3 |
| Scoped-run (argument) support preserved | Task 3 Phase 4, Task 7 Phase 4 |
| Focus-argument (trim/remodel/etc.) preserved | Task 5 Phase 2, Task 9 Phase 2 |

**No placeholders present:** All agent files contain complete lens rules and output format blocks.

**Type consistency:** All five quality lens agent names (`quality-lens-*`) are consistently referenced in the refactored `/audit-agent-quality` Phase 2. All five `quality-skill-lens-*` names are consistently referenced in `/audit-skill-quality`. Same for the design lens agents.
