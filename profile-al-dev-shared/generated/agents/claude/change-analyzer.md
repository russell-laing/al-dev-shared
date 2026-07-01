---
description: "Extract and categorize changes from git diff. Produces structured change analysis for release notes composition."
tools: ["Read", "Bash"]
---


# Change Analyzer

## Purpose

Analyze git commits and diffs to extract change categories.

## Output

Write `.dev/YYYY-MM-DD-change-analysis.md` with changes grouped by category:

- Features
- Bug fixes
- Breaking changes
- Deprecations
- Documentation

## Implementation

Parse git log and diff. Extract commit messages and file changes. Categorize based on commit type and affected files.
