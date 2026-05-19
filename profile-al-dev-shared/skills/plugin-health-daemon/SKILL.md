---
name: plugin-health-daemon
description: Autonomous audit sweep with auto-fix and PR generation for plugin drift
argument-hint: "[optional: --dry-run]"
---

# Plugin Health Daemon

## Overview

Run all plugin audit/review skills in parallel, detect drift (orphaned nodes, stale references, move-candidates, quality issues), auto-fix safe issues, open PRs for manual review items, and generate a weekly digest.

## Execution

1. **Dispatch parallel audits** via Agent tool on `.../profile-al-dev-shared/`:
   - audit-skill-quality → skills/SKILL.md quality report
   - audit-agent-quality → agents quality report
   - review-plugin-map → map accuracy report
   - analyze-plugin-design → design suggestions report
2. **Aggregate findings** into unified report:
   - Classify each finding as autofixable | needs-review | informational
3. **Auto-fix safe issues:**
   - Stale validator references → remove
   - Orphaned diagram nodes → delete
   - Duplicated content → deduplicate
   - Commit atomically to `chore/health-sweep-YYYYMMDD` branch
4. **Generate PR for needs-review items:**
   - Title: "chore: plugin health sweep YYYYMMDD"
   - Body includes all findings + recommended fixes + reproduction steps
   - Push to branch, create PR
5. **Write weekly digest:**
   - findings-per-week trend
   - fix latency (how long items stay open)
   - drift hotspots (which components drift most)
   - Write to `docs/health/digest-YYYY-W<week>.md`
6. **Exit** with non-zero only on daemon errors, not on findings

## Schedule

Intended to run via cron/launchd nightly, e.g. `0 2 * * * /path/to/plugin-health-daemon.sh`
