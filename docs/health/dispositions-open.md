# Open Health Dispositions

<!-- generated from docs/health/dispositions-events/; do not edit directly -->

| Event ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence | Closes |
|----------|---------|-----------|--------|---------|-------------|------|----------|--------|
| disp_20260621_000059 | tooling | quality | plan-health-findings | closes_event_ids: block location ambiguous (~line 418) — 'inside each task verification block' vs task header | accepted | 2026-06-21 | Accepted for implementation: state exact location (after task title line, before body steps). |  |
| disp_20260621_000060 | tooling | quality | revise-health-plan | AskUserQuestion harness-specific token at SKILL.md:99 | accepted | 2026-06-21 | Accepted for implementation: replace with generic user-gate language. |  |
| disp_20260621_000061 | tooling | quality | projection-sync | name 'sync' implies bidirectional but skill unidirectionally regenerates agent projections | accepted | 2026-06-21 | Accepted for implementation: rename toward projection-regenerate / regenerate-agent-projections. |  |
| disp_20260621_000062 | tooling | quality | sync-documentation-maps-apply | 'the other surface validates independently' undefined for accept/reject at SKILL.md:118 | accepted | 2026-06-21 | Accepted for implementation: clarify a failed artifact skips only its own surface; the other is still written. |  |
| disp_20260621_000063 | tooling | quality | ingest-friction-log | 'recurring across >=2 distinct sessions' undefined at SKILL.md:122 | accepted | 2026-06-21 | Accepted for implementation: define a distinct session (e.g. separate calendar day). |  |
| disp_20260621_000064 | tooling | quality | sync-documentation-maps | abandoned run_id note form undefined at SKILL.md:94; no Phase 4 checkpoint field | accepted | 2026-06-21 | Accepted for implementation: specify note form (.dev/progress.md line with abandoned RUN_ID, new RUN_ID, reason). |  |
| disp_20260621_000065 | tooling | quality | health-rubber-duck | technique-noun name 'rubber-duck' obscures the verify action | accepted | 2026-06-21 | Accepted for implementation: verb-forward name (e.g. verify-health-finding) or clarifying suffix. |  |
