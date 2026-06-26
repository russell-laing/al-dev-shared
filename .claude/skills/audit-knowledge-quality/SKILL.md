---
name: audit-knowledge-quality
description: >-
  Audit knowledge files for stub sections and structural issues. Dispatches
  parallel agents for large audit scopes (4+ files). It always writes
  HIGH-severity fix-guidance blocks to the report and optionally re-presents
  the HIGH-severity fix guidance interactively when the user opts in after reporting.
argument-hint: "[--surface plugin|tooling] [--path <directory>] [--verbose]"
workflow:
  stage: derive
  invoked-by: user
  repeatable: true
  inputs:
    - profile-al-dev-shared/knowledge/
    - .claude/knowledge/
  outputs:
    - docs/al-dev-knowledge-quality.md
    - docs/al-dev-knowledge-quality-tooling.md
  next: [fix-knowledge-quality]
---

# Audit Knowledge Quality

Review knowledge files for stub sections, thin content, and structural issues. Use `--surface plugin` (default) to audit
`profile-al-dev-shared/knowledge/`, or `--surface tooling` to audit `.claude/knowledge/`.
After reporting, this audit optionally provides fix guidance for HIGH-severity findings when the user opts in; it does not edit files autonomously.

## Purpose

Detects knowledge files that are referenced by agents for operational guidance but contain incomplete or thin section bodies. Complements the automated validator run at commit time by providing semantic context for why sections are stubs and what content should be added.

Its mission:

1. Run the structural validator to identify potential stubs
2. For each flagged file, read it and the agent/skill that references it
3. Understand what content is missing or incomplete
4. Write findings to the surface-derived report path with recommendations
5. Offer the user targeted fixes

## Maintainer Contracts

Apply `../../knowledge/phase-proof-contract.md` at every phase boundary before
reporting completion or updating `.dev/health-loop-state.md`.

Apply `../../knowledge/dispatch-fallback-contract.md` before every agent
dispatch. Declare the preferred path, run preflight, fall back
deterministically, and log `preferred → outcome → fallback → reason`.

## Arguments

| Argument | Values | Default | Effect |
|----------|--------|---------|--------|
| `--surface` | `plugin` \| `tooling` | `plugin` | Selects the knowledge directory and referencing-agent search paths |
| `--path` | directory | _(derived from `--surface`)_ | Overrides the knowledge directory directly; `--surface` still governs report path and search paths |
| `--verbose` | — | off | Passes `--verbose` to the validator |

**Surface routing:**

| Surface | Knowledge path | Agent/skill search paths | Report output |
|---------|----------------|--------------------------|---------------|
| `plugin` | `profile-al-dev-shared/knowledge/` | `profile-al-dev-shared/agents/`, `profile-al-dev-shared/skills/` | `docs/al-dev-knowledge-quality.md` |
| `tooling` | `.claude/knowledge/` | `.claude/agents/`, `.claude/skills/` | `docs/al-dev-knowledge-quality-tooling.md` |

## Implementation

### Phase 1: Discover Issues

```bash
# Resolve surface argument (default: plugin)
SURFACE="${SURFACE:-plugin}"  # set from --surface arg; default is plugin
case "$SURFACE" in
  plugin)  KNOWLEDGE_PATH="profile-al-dev-shared/knowledge" ;;
  tooling) KNOWLEDGE_PATH=".claude/knowledge" ;;
  *)       echo "Error: --surface must be 'plugin' or 'tooling'"; exit 1 ;;
esac

# Canonical location: in-repo scripts/; global plugin is the fallback.
VALIDATOR="scripts/validate-knowledge-quality.py"
if [ ! -f "$VALIDATOR" ]; then
  VALIDATOR="$(find ~/.claude/plugins -name "validate-knowledge-quality.py" 2>/dev/null | head -1)"
fi
if [ -z "$VALIDATOR" ] || [ ! -f "$VALIDATOR" ]; then
  echo "Error: validate-knowledge-quality.py not found in scripts/ or ~/.claude/plugins"
  exit 1
fi
python3 "$VALIDATOR" --path "$KNOWLEDGE_PATH" --verbose
```

`validate-knowledge-quality.py` emits one multiline record per finding:

```text
<path>
  rule: <rule>
  issue: <detail>
  fix: <action>
```

Parse each record and map its `rule` value to an issue group:
`knowledge-stub → THIN`, `knowledge-no-code → NO-CODE`,
`knowledge-dead-ref → DEAD-REF`. Group findings by the mapped issue type.

### Phase 2: Analyze

Analyze each Phase 1 issue per `.claude/knowledge/knowledge-audit-analysis.md` — it
defines path selection (parallel for 4+ files: dispatch one analysis agent per file;
sequential for ≤3 files: analyze each in the current session), progress tracking,
the mandatory referencing-agent/skill reads (the agent or skill named in the
finding's `Reference:` field — the one that defers to the knowledge file),
the per-issue treatment (THIN: content is too sparse to guide an agent — add
missing substantive guidance; NO-CODE: code examples are absent from a section
that requires them — add working code; DEAD-REF: the file cross-references a
path that no longer exists — update or remove the reference), and the
structured return schema that Phase 3 consumes.

**Surface-specific referencing-search override:** `knowledge-audit-analysis.md` names
`profile-al-dev-shared/agents/` and `profile-al-dev-shared/skills/` as the referencing
search paths. For `--surface tooling`, replace those with `.claude/agents/` and
`.claude/skills/` respectively. All other analysis rules apply unchanged.

### Phase 3: Write Findings Report

Determine the output path from the surface argument: `plugin` → `docs/al-dev-knowledge-quality.md`; `tooling` → `docs/al-dev-knowledge-quality-tooling.md`. Write to that path. The report **always** contains the
`## Fix Recommendations` and `## High-Priority Fix Tasks` blocks — they are written
unconditionally. Whether they are re-presented interactively is governed by the
USER_GATE in Phase 4.

Structure:

```markdown
# Knowledge File Quality Report

Generated: [timestamp]
Issues: [count by severity]

## HIGH Severity (Blocks Agent Guidance)

- **File:** knowledge/X.md
  - **Reference:** `agents/Y.md:NN` — agent explicitly defers to this file
  - **Issue:** [THIN|NO-CODE|DEAD-REF] — specific detail
  - **Missing Content:** [What should be in the section]
  - **Fix:** [Concrete recommendation]

## MEDIUM Severity (Incomplete Guidance)

[Same structure as HIGH]

## LOW Severity (Minor/False Positives)

[Same structure]

---

## Fix Recommendations

### High Priority
[Actionable next steps for HIGH issues]

### Medium Priority
[Actionable next steps for MEDIUM issues]
```

After the HIGH findings narrative, append a machine-readable task block:

```yaml
## High-Priority Fix Tasks
<!-- auto-generated by /audit-knowledge-quality — consumed by /fix-knowledge-quality -->
tasks:
  - file: <exact-path-to-knowledge-file>
    issue_type: <THIN|NO-CODE|DEAD-REF>
    description: <one-line description of the issue>
    suggested_action: <concrete fix instruction>
```

One entry per HIGH issue. Use the exact file path from the finding. Do not include
MEDIUM or LOW issues in this block.

### Phase 4: Offer Fixes

After writing the report:

1. Print: `Knowledge quality report written to <report-path>` (where `<report-path>` is the surface-derived output path from Phase 3)
2. Present the audit summary (findings count by severity and top 3 HIGH issues).

**USER_GATE — fix-guidance presentation.** The `## Fix Recommendations` and
`## High-Priority Fix Tasks` blocks already exist in the report
(the surface-derived `<report-path>`): Phase 3 wrote these blocks unconditionally;
this phase gates only their interactive re-presentation. After presenting the
audit summary, ask:

> HIGH-severity stub findings were found. Walk through the fix guidance now?
> (yes / no)

On `yes`, present the recommendations inline; on `no` or no response, stop after
the summary — the guidance remains in the report file for later use.

## Output Format

```text
## Knowledge File Quality Audit

Scanning <knowledge-path> for structural issues...

FINDINGS SUMMARY:
- HIGH (blocks agent guidance): N
- MEDIUM (incomplete): N  
- LOW (minor/false positives): N

Report written to: <report-path>

[Top 3 HIGH issues listed]

Run `cat <report-path>` to see full report.
```

Where `<knowledge-path>` and `<report-path>` are derived from the surface argument (see Arguments table).

## Success Criteria

✅ All HIGH severity findings have concrete fix recommendations written to the surface-derived report path (`docs/al-dev-knowledge-quality.md` for `plugin`; `docs/al-dev-knowledge-quality-tooling.md` for `tooling`)
✅ The report always contains `## Fix Recommendations` and `## High-Priority Fix Tasks` (written unconditionally)
✅ The USER_GATE in Phase 4 gates interactive re-presentation only — not generation of the report sections
✅ False positives (LOW severity) are clearly marked and explained
✅ Report is actionable — user can immediately address MEDIUM/HIGH issues
✅ DEAD-REF issues are investigated (not every broken link is a real problem)

**When to run:**

- After `/audit-knowledge-quality` is invoked (user-triggered)
- Periodically (e.g., before major plugin releases)
- After significant knowledge file updates
- If the `/al-dev-commit` advisory surfaces knowledge warnings
