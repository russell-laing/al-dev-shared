# al-dev-align — Design Spec

**Date:** 2026-05-11  
**Status:** Approved for implementation

---

## Problem

After the harness-agnostic migration, `al-dev-shared` skill and agent bodies must not contain harness-specific tokens, and both harness profile repos (`claude-configs`, `copilot-configs`) must maintain complete mapping tables that cover every concept in `harness-concepts.md`. Without tooling, this alignment can silently drift as new skills, agents, or concepts are added.

## Goal

A skill (`/al-dev-align`) that audits alignment between `al-dev-shared` and the two harness repos, reports issues clearly, and offers to fix them — usable both interactively and as a programmatic check called by other skills.

---

## Files

```
profile-al-dev-shared/skills/al-dev-align/
  SKILL.md              ← skill definition (frontmatter + instructions)
  check-alignment.py    ← Python script that performs all checks
```

---

## Script: check-alignment.py

### Invocation

```bash
python3 check-alignment.py [options]

Options:
  --mode advisory|enforce   advisory = warn and exit 0; enforce = exit 1 on issues (default: enforce)
  --claude-profile <path>   override default ~/claude-configs/profile-claude-al-dev
  --copilot-profile <path>  override default ~/copilot-configs/profile-copilot-al-dev
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | Alignment issues found |
| 2 | Configuration / parse / runtime error |

In `--mode advisory`, exit code is always 0 (issues reported on stdout but not blocking).

### Output Format

JSON to stdout:

```json
{
  "forbidden_tokens": [
    {
      "file": "relative/path/to/file.md",
      "line": 42,
      "token": "CLAUDE.md",
      "context": "...surrounding text...",
      "context_type": "prose|code_block|prohibition_rule",
      "severity": "error|warning|manual_review",
      "autofixable": true
    }
  ],
  "missing_mappings": [
    {
      "concept": "USER_GATE",
      "missing_in": ["claude", "copilot"]
    }
  ],
  "orphaned_mappings": [
    {
      "concept": "some old concept",
      "present_in": ["claude"]
    }
  ]
}
```

---

## Check 1: Forbidden Token Audit

### What is scanned

Every file under `profile-al-dev-shared/` matching:
- `skills/*/SKILL.md`
- `agents/*.md`
- `knowledge/*.md`

`knowledge/harness-concepts.md` is excluded — it intentionally contains concrete harness names in its mapping table.

### Frontmatter handling

A file has frontmatter only if its first line is exactly `---`. The parser reads until the closing `---`. Frontmatter lines are replaced with blank lines (line numbers preserved). The body is what remains.

### Forbidden token derivation

The forbidden token list is derived dynamically from `harness-concepts.md`. The script reads all columns that are NOT the generic concept column (columns 3 and 4 in the vocabulary table) and extracts the concrete values. It also includes these hardcoded path/config tokens that are not in the table:

```
~/.claude
~/claude-configs
~/.copilot
~/copilot-configs
CLAUDE_CODE
```

This means any new harness-specific tokens added to `harness-concepts.md` are automatically forbidden in shared files.

### Context classification

Each hit is classified before reporting:

| `context_type` | How detected | `autofixable` | `severity` |
|---|---|---|---|
| `prose` | Not in a fenced code block, not in a "never"/"do not" rule | `true` | `error` |
| `code_block` | Inside ` ``` ` fences or indented code | `false` | `warning` |
| `prohibition_rule` | Line contains "never", "do not", "must not", "don't" | `false` | `manual_review` |

---

## Check 2: Harness Coverage Audit

### Source of truth

`harness-concepts.md` vocabulary table — column 1 (concept names). Strip `**` bold markers and trim whitespace.

### Parsing the mapping tables

In `CLAUDE.md` and `AGENTS.md`, locate the section starting with `## Harness Mapping`. Read the table rows until the next `## ` heading or end of file. For each row:
- Ignore separator rows (lines starting with `|---`)
- Trim outer pipes, normalize whitespace, strip `**` and backticks

### What is reported

- **Missing:** concept exists in `harness-concepts.md` but has no row in a mapping table
- **Orphaned:** row exists in a mapping table but the concept is not in `harness-concepts.md`

Orphaned rows are `severity: warning` (they may be intentional extensions). Missing rows are `severity: error`.

---

## Skill: SKILL.md

### Frontmatter

```yaml
---
name: al-dev-align
description: >-
  Check alignment between al-dev-shared and harness repos. Audits for forbidden
  harness-specific tokens in shared skill/agent bodies and verifies harness
  mapping tables are complete. Run after changes to al-dev-shared or harness profiles.
argument-hint: ""
---
```

### Skill instructions (summary)

1. Locate script: `$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-align/check-alignment.py`
2. Run script with `--mode enforce`
3. **Exit 0:** print "✅ All checks passed" and stop
4. **Exit 2:** report the error and stop
5. **Exit 1:** present findings as two sections:
   - **Forbidden tokens** — grouped by file, showing line + context + severity
   - **Coverage gaps** — missing/orphaned mapping rows, grouped by concept
6. USER_GATE: "Found N issue(s). Want me to attempt fixes? I'll auto-fix prose hits and flag anything that needs manual attention."
7. **Fix flow (if user consents):**
   - `autofixable: true` hits: substitute generic equivalent using `harness-concepts.md` vocabulary as reference
   - `code_block` / `prohibition_rule` hits: flag as "needs manual review", skip
   - Missing mapping rows: add to the appropriate Harness Mapping table in the harness repo
   - Orphaned rows: flag for manual review (don't auto-delete)
8. Re-run script to confirm exit 0. Report any remaining issues.

---

## Integration with Other Skills

Other skills invoke the script in advisory mode:

```bash
SCRIPT="$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-align/check-alignment.py"
if [ -f "$SCRIPT" ]; then
  python3 "$SCRIPT" --mode advisory
  # advisory mode always exits 0; issues are printed to stdout for the AI to surface
fi
```

For commit/release enforcement, use `--mode enforce` and let exit 1 block the workflow.

**Suggested integration points:**
- `al-dev-commit` — advisory check before committing
- `al-dev-handoff` — advisory check before packaging context

---

## Path Assumptions

| Path | Default | Override |
|---|---|---|
| al-dev-shared plugin root | `$AL_DEV_SHARED_PLUGIN_ROOT` | — |
| Claude profile | `~/claude-configs/profile-claude-al-dev` | `--claude-profile` |
| Copilot profile | `~/copilot-configs/profile-copilot-al-dev` | `--copilot-profile` |

The script resolves `~` to the current user's home directory.

---

## Out of Scope (v1)

- Mapping **value** correctness (checking that a mapping row maps to the right concrete value, not just that it exists) — future enhancement
- Scanning `docs/`, `README.md`, or other non-skill/agent/knowledge surfaces
- CI integration (the `--mode enforce` flag makes this easy to add later)
