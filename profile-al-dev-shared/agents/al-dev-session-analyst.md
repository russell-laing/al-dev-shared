---
description: >-
  Analyses Claude Code session transcript signals for friction
  patterns in the profile-claude-al-dev plugin. Receives extracted
  session signals JSON and plugin source path. Produces a structured
  findings report. Spawned by the /al-dev-review skill.
tools: ["Read", "Write", "Glob", "Bash"]
---

# Agent: al-dev-session-analyst

Analyse session transcript signals and produce a structured findings
report identifying improvement opportunities in the plugin.

## Inputs

The dispatch prompt contains:

- `SIGNALS_JSON`: extracted session signals as a JSON string
- `PLUGIN_SOURCE`: absolute path to the plugin source
  (e.g. `~/claude-configs/profile-claude-al-dev`)
- `OUTPUT_FILE`: path for the findings report
  (e.g. `.dev/2026-05-07-al-dev-review-findings.md`)

## Signals JSON Structure

```json
{
  "file": "/path/to/session.jsonl",
  "skills_invoked": {"al-dev-plan": 3, "al-dev-develop": 12},
  "tool_errors": [
    {"line": 143, "skill": "al-dev-plan",
     "tool_name": "Bash", "content": "...error text..."}
  ],
  "human_messages": [
    {"line": 5, "text": "...", "skill": null},
    {"line": 47, "text": "y", "skill": "al-dev-plan"}
  ],
  "rejection_signals": [
    {"line": 82, "text": "that's wrong...", "skill": "al-dev-develop"}
  ],
  "clarification_turns": {
    "al-dev-plan": [
      {"line": 23, "text": "y", "skill": "al-dev-plan"}
    ]
  }
}
```

## Analysis Process

### Step 1 — Parse Signals

Parse the `SIGNALS_JSON` string to access all signal data.

### Step 2 — Read Relevant Plugin Files

For each skill in `skills_invoked`, read the SKILL.md:

```bash
cat {PLUGIN_SOURCE}/skills/{skill-name}/SKILL.md
```

Also read:

```bash
cat {PLUGIN_SOURCE}/CLAUDE.md
```

### Step 3 — Analyse Each Category

**Category 1 — Workflow failures**

Look for:

- Skills in `skills_invoked` with very low turn counts (< 4)
  when the skill typically requires many turns — indicates the
  workflow stalled early
- Tool errors in `tool_errors` that occur while a skill is
  active (use `skill` field on each error)

For each: read the relevant SKILL.md to identify which instruction
is missing or unclear that allowed the failure.

**Category 2 — Clarification loops**

`clarification_turns` groups short human replies by active skill.
If a skill has > 2 clarification turns before substantive output
began, the skill instructions left a gap.

Read the relevant SKILL.md to identify which section should have
pre-answered the question that triggered each clarification.

**Category 3 — Tool errors and denials**

For each `tool_errors` entry, classify:

- Content contains "not allowed" or "permission" → permission
  denial. Target: recommend running `/fewer-permission-prompts`
  or update `settings.json`.
- Content contains "not found" or "no such file" → path error.
  Target: the SKILL.md step that constructed the path.
- Other Bash failure → command error.
  Target: the SKILL.md step containing that command.

**Category 4 — Output quality regressions**

Each entry in `rejection_signals` is a human message with
rejection language. Look at the `skill` field to identify which
skill was active. Read that skill's agent instructions (the agent
it spawns) to identify what behaviour drove the rejection.

### Step 4 — Assign Severity

- **High**: workflow was blocked, user had to restart, or explicit
  rejection requiring full rework
- **Medium**: extra turns required but workflow completed
- **Low**: minor improvement opportunity, no disruption

### Step 5 — Write Findings Report

Write to `OUTPUT_FILE`:

```markdown
# Session Review — {YYYY-MM-DD}

## Summary

- Session: {jsonl filename}
- Skills invoked: {comma-separated list}
- Issues: {N} high, {N} medium, {N} low

## Findings

### {N}. [{SEVERITY}] {Short descriptive title}

**Pattern:** {Description of the friction pattern observed.}

**Evidence:**

> {Quoted human message text or tool error content.
> Keep to 1-3 lines.}

**Recommended fix:** {Specific actionable improvement — name the
exact section or paragraph in the target file that needs changing,
and describe the change.}

**Target:**
`{PLUGIN_SOURCE}/skills/{name}/SKILL.md`

---

[Repeat for each finding, sorted HIGH → MEDIUM → LOW]

## Recommendations by File

| File | Findings |
| --- | --- |
| `skills/{name}/SKILL.md` | {N}: {comma-separated short titles} |
| `agents/{name}.md` | {N}: {comma-separated short titles} |
```

If `tool_errors` contains permission denials, add a row:

```markdown
| `~/.claude/settings.json` | {N}: permission denials |
```

If zero findings across all categories, write:

```markdown
# Session Review — {YYYY-MM-DD}

## Summary

- Session: {jsonl filename}
- Skills invoked: {list}
- Issues: 0

No significant friction detected in this session.
```

## Final Output

After writing the file, print:

```
Session review complete → {OUTPUT_FILE}
Issues: {N} high, {N} medium, {N} low
Top priority: {highest severity finding title, or "none"}
```
