# Health Finding Dispositions

<!-- generated from docs/health/dispositions_events/; do not edit directly -->

| ID | Surface | Dimension | Object | Finding | Disposition | Date | Note |
|----|---------|-----------|--------|---------|-------------|------|------|
| disp_20260701_000005 | plugin | design | commit-preflight-staged-diff-crosscheck | Phase 2.1 presents PROPOSED_GROUPS with no cross-check against git diff --cached --name-only | fixed | 2026-07-01 | d12e85af — Add staged-file cross-check in Phase 2.1; verified live; closes disp_20260701_000001 |
| disp_20260701_000006 | plugin | quality | compile-lint-procedure | Documented plain-text diagnostic format contradicts actual SARIF/JSON output | fixed | 2026-07-01 | c1003861 — Update diagnostic format to SARIF JSON; verified live; closes disp_20260701_000002 |
| disp_20260701_000007 | plugin | design | commit-preflight-manifest-grep-permissionset | Inline manifest grep doesn't cover permission-set lines | fixed | 2026-07-01 | 7678dd02 — Extend manifest grep to permission-set lines; verified live; closes disp_20260701_000003 |
| disp_20260701_000008 | plugin | design | commit-compile-gate-fixed-cost | Compile gate always triggers full-project compile regardless of diff size | fixed | 2026-07-01 | a68e0130 — Document scoped compile future enhancement; verified live; closes disp_20260701_000004 |
