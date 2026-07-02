---
name: generate-duplicate-text-report
description: Use when reviewing .claude or profile-al-dev-shared for repeated text, copy-paste drift, exact duplicate blocks, or consecutive duplication of eight or more lines.
---

# Generate Duplicate Text Report

## Overview

Generate a deterministic Markdown inventory of exact duplicate text blocks for
maintainer review. Treat the output as evidence, not an automatic refactoring
list: templates, examples, and self-contained contracts can be intentionally
duplicated.

## Quick Start

From the repository root:

```bash
python3 .codex/skills/generate-duplicate-text-report/scripts/generate_duplicate_text_report.py
```

The default scan covers `.claude` and `profile-al-dev-shared`, excludes copied
checkout snapshots under `.claude/worktrees`, requires at least eight matching
lines, and writes:

```text
docs/reviews/2026-07-02-duplicate-text-report.md
```

Run `--help` for threshold, path, output, archive, and generated-content
options.

## Workflow

1. Run the script with the user-supplied paths, or use the default active
   authored surfaces.
2. Read the report summary and inspect each location in the live files.
3. Classify matches as:
   - drift risk: duplicated rules or commands that can diverge
   - reusable template candidate: repeated operational structure
   - intentional: examples, projections, fixtures, or self-contained contracts
4. Rank drift risks by behavioral impact and current divergence.
5. Report the output path and the highest-signal findings. Do not edit matched
   files unless the user separately requests remediation.

## Defaults and Guardrails

- Normalize line endings and trailing whitespace only.
- Exclude `archived`, `generated`, `.claude/worktrees`, `__pycache__`,
  `.DS_Store`, binary, and non-UTF-8 files by default.
- Use `--include-archived` or `--include-generated` only when the user wants
  intentional historical or projection duplication included.
- Collapse overlapping windows into maximal blocks and group all occurrences.
- Keep durable reports under `docs/reviews/`; use an explicit temporary
  `--output` path for exploratory scans.
- Do not claim semantic or near-duplicate detection. The scanner reports exact
  normalized text only.

## Validation

After changing the scanner or skill:

```bash
python3 -m unittest discover \
  -s .codex/skills/generate-duplicate-text-report/tests \
  -p 'test_*.py'
python3 /Users/russelllaing/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .codex/skills/generate-duplicate-text-report
```
