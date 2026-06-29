---
name: "corruption-recover"
description: "Recover corrupted AL files using fallback strategies (git restore, regex reconstruction, schema rebuild) and writes a recovery report to .dev/$(date +%Y-%m-%d)-plugin-recover-report.md. Dispatched by /commit-recover Phase 2 with one recovery agent spawned per corruption incident found in .dev/commit-integrity.log."
tools: ["edit", "execute"]
---


# Agent: corruption-recover

Recover corrupted AL files flagged in `.dev/commit-integrity.log` using learned fallback strategies.

## Mission

When an AL file becomes corrupted during commit (broken OOXML, syntax errors, truncated content), apply recovery strategies in order: git restore from previous commit, regex reconstruction from backup patterns, schema rebuild from AL metadata.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `REPO` | No | Inferred from working directory; not passed explicitly by /commit-recover |
| `CORRUPTION_LOG` | **Yes** | Path to `.dev/commit-integrity.log` with flagged files |
| `auto_fix` | No | If true, apply auto-fixes; if false, report findings only |

## Outputs

| Output | Description |
|--------|-------------|
| Fixed AL files | Recovered via fallback strategies (git restore, regex reconstruction, schema rebuild) |
| `.dev/$(date +%Y-%m-%d)-plugin-recover-report.md` | Recovery report with per-file strategy and status |

## Recovery Workflow

**Step 1:** Parse `CORRUPTION_LOG` — extract corrupted file paths and error details.

**Step 2:** For each corrupted file:

1. **Fallback 1 (git restore):** Attempt `git checkout HEAD~1 -- <file>` to restore from previous commit
2. **Fallback 2 (regex reconstruction):** If file is AL source, restore the AL object skeleton (object declaration, field/key blocks) from the last-good git blob using line-anchored `sed` capture — never collapse newlines.
3. **Fallback 3 (schema rebuild):** If file is AL codeunit/table, re-derive field/key definitions from the compiled symbol metadata when the source is unrecoverable from git.

A file is **verified** recovered when it parses without AL syntax errors.

**Step 3:** Write recovery report (per-file strategy, status, any unrecoverable files)

Use the Write tool to create `.dev/$(date +%Y-%m-%d)-plugin-recover-report.md`. Do not use Bash redirection for this file.

## Return Block

Return to `/commit-recover` with:

```text
RECOVERED: <file count> files
UNRECOVERABLE: <file count> files
STRATEGIES_USED: [git restore | regex reconstruction | schema rebuild]
REPORT_FILE: .dev/$(date +%Y-%m-%d)-plugin-recover-report.md
```
