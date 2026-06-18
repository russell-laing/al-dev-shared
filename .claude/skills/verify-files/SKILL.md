---
name: verify-files
description: >-
  Verify claimed files exist on disk before reporting completion or committing.
  Use before commits, after subagent execution, or any time a file write
  may not have persisted.
argument-hint: "[path ...] [--from-git-status]"
---

# Verify Files

## Purpose

Confirms that files Claude claimed to write or that subagents produced actually
exist on disk and are non-empty. Surfaces missing files before they cause
silent failures downstream.

**Read-only.** This skill does not write, edit, or fix anything.

## Phase 0: Parse Arguments

Read `$ARGUMENTS`:

- `--from-git-status` → set `MODE=git-status`
- One or more paths provided → set `MODE=explicit`, collect paths
- No arguments → set `MODE=session`

## Phase 1: Build File List

**`MODE=git-status`:**

```bash
git status --short
```

Extract all file paths from the output. Include new (`??`) and modified (`M`) paths.
Skip deleted (`D`) paths — they should not exist.

**`MODE=explicit`:**

Use the paths provided as arguments directly.

**`MODE=session`:**

Collect all paths from `Write` and `Edit` tool calls made in the current session.
If no tool calls are identifiable, ask the user to provide paths explicitly.

## Phase 2: Verify Each File

For each path in the file list, run:

```bash
ls -la <path>
```

Record:

- **exists**: yes or no
- **size**: file size in bytes (0 = empty)
- **note**: `ok`, `missing`, or `empty`

## Phase 3: Report

Produce a table:

| Path | Exists | Size | Note |
| --- | --- | --- | --- |
| path/to/file.md | yes | 1234 | ok |
| path/to/missing.py | no | — | missing |

Print summary line: `N verified, M missing`

**If any files are missing or empty:**

- List them explicitly
- Stop — do not report the work as done
- Do not attempt to recreate or fix the files

**If all files verified:**

Print: `All N files verified ✓`
