# Scripts Quality Review

Generated: 2026-07-03  
Files reviewed: 60 | Clusters: 6 | Skipped (compat shims): 13

## Summary

- **Critical:** 7 | **High:** 8 | **Medium:** 8 | **Low:** 3
- **Watch-list matches:** 15

## Findings (ranked by severity)

### CRITICAL — CWD-relative path resolution in CLI defaults

- **File:** `scripts/al_dev_tools/health/health_disposition_store.py:163`
- **Defect:** `parse_args()` calls path helpers with no repo-root argument, resolving to `Path(".") / docs/health/dispositions_events`, causing all CLI subcommands to inherit cwd-relative defaults.
- **Failure scenario:** User runs `python -m al_dev_tools.health.health_disposition_store match findings.md ledger.md` from a subdirectory → tool loads store from `subdir/docs/health/dispositions_events/` instead of repo root → syncs against non-existent/stale event store → ledger diverges from canonical.
- **Watch-list class:** #1 (ledger fork from stale/relative paths)

---

### CRITICAL — Unhandled JSON parse crash in assembly

- **File:** `scripts/al_dev_tools/health/assemble_health_findings.py:85`
- **Defect:** `json.loads(Path(p).read_text(encoding="utf-8"))` has no try/except block; malformed lens JSON (truncated file, invalid syntax) raises `JSONDecodeError` → function crashes.
- **Failure scenario:** Corrupted lens JSON during lens dispatch → `assemble_findings()` crashes silently → dossier never written → discovery phase fails with no diagnostic about which file is bad → discovery loop stalls.
- **Watch-list class:** #3 (disposition/findings parse fragility)

---

### CRITICAL — Orphan cleanup skipped on empty agents list

- **File:** `scripts/generate_agent_projections.py:199-210`
- **Defect:** Glob on `agents_root` silently succeeds with empty list if directory doesn't exist; `write_all_projections()` then skips orphan cleanup because `desired_*` sets are empty (line 174 guard fails).
- **Failure scenario:** Run with `--agents-root=/nonexistent` → `agents=[]` → `desired_claude={}` → `if desired_claude or ...` is False → orphaned projection files untouched → README.md written, other projections left stale → partial writes corrupt projection state; re-runs don't clean up.
- **Watch-list class:** #2 (non-atomic/non-idempotent writes) + #4 (fail-open validators)

---

### CRITICAL — ValueError swallowed on malformed policy file

- **File:** `scripts/validate_harness_neutrality.py:137-139`
- **Defect:** `ValueError` swallowed when parsing agent-tool-projection-policy.md frontmatter; `parse_required_frontmatter()` raises ValueError → caught and silently returns empty set → `scan_models()` early-returns with no findings → validator reports "PASS: no harness-specific leakage" despite incomplete validation.
- **Failure scenario:** Policy file with malformed YAML (unclosed quote in `shared_model_aliases`) → validator accepts it silently → model-canonicality check never performed → harness-specific tokens leak undetected.
- **Watch-list class:** #4 (fail-open validators)

---

### CRITICAL — Missing policy file silently accepted

- **File:** `scripts/validate_harness_neutrality.py:146-149`
- **Defect:** Missing agent-tool-projection-policy.md silently accepted; `load_model_aliases()` returns empty set (line 135) → `scan_models()` early-returns because `if not aliases` is true → no findings generated → validator reports "PASS" even though model-canonicality check was never performed.
- **Failure scenario:** Repo without profile-al-dev-shared/knowledge/agent-tool-projection-policy.md → validator skips entire model validation → canonical tool-name check never runs → harness projection mismatches pass undetected.
- **Watch-list class:** #4 (fail-open validators)

---

### CRITICAL — SKILLS_ROOT not validated, all checks skipped

- **File:** `scripts/validate_maintainer_contracts.py:85`
- **Defect:** SKILLS_ROOT directory is never asserted to exist; missing directory causes silent skip of all skill checks.
- **Failure scenario:** If .claude/skills/ doesn't exist, `check_coverage()` iterates over MULTI_PHASE_SKILLS set, each `skill_md.exists()` returns False, all skills skipped with `continue`, violations list remains empty → main() reports "all required references present ✓" despite no skills being validated.
- **Watch-list class:** #4 (fail-open validators)

---

### CRITICAL — Missing directories reported as clean

- **File:** `scripts/validate_shared_surface.py:88, 123-125`
- **Defect:** AGENTS_DIR and SKILLS_DIR are not asserted to exist; missing directories cause `glob()` to return empty, resulting in zero-count reported as "all clean".
- **Failure scenario:** If profile-al-dev-shared/agents/ doesn't exist, line 88 `AGENTS_DIR.glob("*.md")` returns empty → `validate_all()` returns {} (all clean) → line 123 counts 0 agents, line 125 prints "OK: 0 agents, 0 skills — all clean." and returns 0, masking missing directory as success.
- **Watch-list class:** #4 (fail-open validators)

---

### HIGH — Non-atomic append in markdown history shard

- **File:** `scripts/al_dev_tools/health/disposition_views.py:57-67`
- **Defect:** `write_shard()` appends to markdown shards via buffered `f.write()` without `fsync()` or atomic-write guards. If process crashes mid-write, shard file is corrupted with partial table rows.
- **Failure scenario:** `sync_shard` command syncs 100 events. After writing 50 rows, process receives SIGKILL → shard file left with truncated final row and malformed markdown → next run of `iter_history_rows()` raises `ValueError` on unparseable line → blocks all ledger operations until manual repair.
- **Watch-list class:** #2 (non-atomic/non-idempotent writes)

---

### HIGH — Closure lookup dedup collision risk

- **File:** `scripts/al_dev_tools/health/ledger_queries.py:93`
- **Defect:** Pattern `by_id.get(f"#{target_id}") or by_id.get(target_id)` tries both variants. If ID format is inconsistent (e.g., legacy `foo` vs newer `foo-legacy`), collision is possible.
- **Failure scenario:** Legacy ID `milestone-fix` exists. Later fixed row's note says "closes #milestone-fix". Regex captures `milestone-fix`. Code tries `by_id.get("#milestone-fix")` (fails), then `by_id.get("milestone-fix")` (matches). If another row has ID `milestone-fix-v2` mapping to same `norm_object()`, closure could match wrong row due to order-dependency in dict → wrong finding marked closed.
- **Watch-list class:** #6 (closure/dedup logic)

---

### HIGH — Silent empty corpus in health lenses

- **File:** `scripts/health_static_lenses.py:141-166`
- **Defect:** `agent_files()` and `skill_files()` silently return `[]` if their roots don't exist; lenses then run on empty corpus, producing "No issues found." instead of erroring.
- **Failure scenario:** `surface_root /agents` missing → `agent_files()` returns `[]` → `run_lens()` produces empty findings → output claims "no issues" when corpus is actually absent → false negatives in health sweep for plugin/tooling surfaces → incorrect findings written to ledger.
- **Watch-list class:** #4 (fail-open validators)

---

### HIGH — Missing POLICY_PATH not validated before use

- **File:** `scripts/health_static_lenses.py:132-138`
- **Defect:** `canonical_tools()` calls `POLICY_PATH.read_text()` without validating path exists; callers may not expect FileNotFoundError.
- **Failure scenario:** POLICY_PATH not found → `FileNotFoundError` at first `check_agent_structure()` call (line 620) → error swallowed by lens runner → incorrect findings written to ledger.
- **Watch-list class:** #4 (fail-open validators)

---

### HIGH — Missing opening backtick in map-sync artifacts

- **File:** `scripts/al_dev_tools/docs/maintainer_tables.py:51`
- **Defect:** Artifact description missing opening backtick for inline code formatting. Current: `"docs/skills_map.md` and `docs/agent_map.md"`. Renders as unformatted text followed by two separate code blocks, not a code pair.
- **Failure scenario:** When `render_stage_artifacts()` (line 171) wraps this in backticks, output is `| \`docs/skills_map.md\` and \`docs/agent_map.md |`, rendering malformed → maintainers reading generated docs see inconsistent formatting.
- **Watch-list class:** —

---

### HIGH — Missing opening backtick in discover artifacts

- **File:** `scripts/al_dev_tools/docs/maintainer_tables.py:73`
- **Defect:** Same issue as line 51. Current: `"docs/skills_map.md` and `docs/agent_map.md"`. Identical rendering failure.
- **Watch-list class:** —

---

### HIGH — Missing opening backtick in decide artifacts

- **File:** `scripts/al_dev_tools/docs/maintainer_tables.py:103`
- **Defect:** Artifact description string has inconsistent backtick pairing. Current: `"docs/health/dispositions_events/YYYY/YYYY-MM.jsonl` (canonical) + `docs/health/dispositions_open.md"`. First path renders unformatted; second renders as code → readers cannot reliably identify actual artifact paths.
- **Watch-list class:** —

---

### HIGH — Missing opening backtick in implement artifacts

- **File:** `scripts/al_dev_tools/docs/maintainer_tables.py:137`
- **Defect:** Same pattern as lines 51, 73. Current: `"docs/health/archived/` and `docs/superpowers/plans/archived/"`. Identical rendering failure.
- **Watch-list class:** —

---

### MEDIUM — API design invites ledger fork via relative paths

- **File:** `scripts/al_dev_tools/health/paths.py:19-51`
- **Defect:** All `docs_health_root()`, `dispositions_events_root()`, etc. functions default to `root: Path = Path(".")` instead of requiring explicit root. Current callers (check_* scripts) pass explicit `REPO_ROOT`, so latent.
- **Failure scenario:** Future code calls `dispositions_events_root()` without root from non-root directory → resolves to cwd-relative path → subsequent writes fork ledger to wrong location.
- **Watch-list class:** #1 (ledger fork from relative paths)

---

### MEDIUM — Hardcoded overlapping names become stale

- **File:** `scripts/health_static_lenses.py:206-211`
- **Defect:** `OVERLAPPING_NAMES = {"explore", "interview"}` is hardcoded; not derived from filesystem. If skill is renamed or new overlapping agent/skill pair added, deduplication logic becomes stale.
- **Failure scenario:** Skill renamed from `explore` to `explore-plugin`, or new overlapping pair added → dedup logic stale → incorrect object tags in findings rows → ledger accuracy degraded.
- **Watch-list class:** #5 (stale skill/agent name references)

---

### MEDIUM — SKILLS_DIR hardcoded without validation

- **File:** `scripts/generate_maintainer_guide.py:31-36`
- **Defect:** `SKILLS_DIR` hardcoded without validation; `load_contracts()` called without checking directory exists.
- **Failure scenario:** `.claude/skills` removed or symlink broken → `load_contracts()` fails (behavior depends on helper; no guard in this script) → silent or opaque failure during maintainer guide regeneration.
- **Watch-list class:** #4 (fail-open validators)

---

### MEDIUM — Empty glob on missing directory

- **File:** `scripts/summarize_superpowers_history.py:192-196`
- **Defect:** `full_directory.glob("*.md")` returns empty if directory doesn't exist; no validation. Script produces empty history file silently.
- **Failure scenario:** `docs/superpowers/plans` or `docs/superpowers/specs` deleted → script produces empty history file silently → no signal that source directories are missing → false-empty historical summary.
- **Watch-list class:** #4 (fail-open validators)

---

### MEDIUM — O(N²) event-store load in batch_decline

- **File:** `scripts/al_dev_tools/health/disposition_events.py:130`
- **Defect:** `batch_decline()` function calls `list(iter_event_rows(events_root))` once per input row, forcing complete re-parse of JSONL event store for every declined event.
- **Failure scenario:** User declines 500 findings via `batch_decline`. With 2000 existing events, tool issues 500 full-store re-reads and parses → blocks disposition pipeline for minutes on slow I/O or large stores.
- **Watch-list class:** #2 (non-atomic/non-idempotent writes)

---

### MEDIUM — Warning message conflates parse formats

- **File:** `scripts/al_dev_tools/health/disposition_matching.py:279-283`
- **Defect:** Warning `"parsed {parsed_count} / {total_data_lines} table rows"` is misleading. `parsed_count` includes bullets, em-dashes, AND table rows. `total_data_lines` counts only table rows. Message implies table-parsing failure when it may just mean non-table findings were parsed.
- **Failure scenario:** Findings file with 3 bullets and 10 tables where only 3 bullets parsed → prints "parsed 3 / 10 table rows" → misread as "3 out of 10 tables were parsed" rather than "3 items parsed, 10 table rows found" → diagnostic ambiguity.
- **Watch-list class:** #3 (disposition/findings parse fragility)

---

### MEDIUM — Inconsistent atomicity in view rendering

- **File:** `scripts/al_dev_tools/health/disposition_views.py:57-93`
- **Defect:** `write_shard()` (used by `sync_shard` and `append_row` commands) lacks atomic guards, while `render_*()` functions (used by `regenerate` command) all call `write_text_atomic()`. No consistency check prevents stale/corrupt shards mixed with atomic views.
- **Failure scenario:** Legacy workflow appends rows via `append_row` (non-atomic write). New workflow calls `regenerate` to sync JSONL to markdown (atomic write). If `append_row` crashes, shard is corrupted, and `regenerate` may fail to overwrite it or trust stale data → views become inconsistent with JSONL store.
- **Watch-list class:** #2 (non-atomic/non-idempotent writes)

---

### MEDIUM — Render function assumes string artifacts, causes double-wrap

- **File:** `scripts/al_dev_tools/docs/maintainer_tables.py:171`
- **Defect:** `render_stage_artifacts()` unconditionally wraps `artifact` in backticks (`` f"`{artifact}`" ``), but STAGE_ARTIFACTS tuples contain pre-formatted markdown with embedded backticks and prose. This causes double-wrapping and malformed output.
- **Failure scenario:** STAGE_ARTIFACTS["X"][Y] contains `` `path1` and `path2` `` → rendering produces `` `\`path1\` and \`path2\`` `` → breaks markdown parsing → malformed rendered output.
- **Watch-list class:** —

---

### LOW — Hardcoded LOOP list becomes stale

- **File:** `scripts/check_health_loop_handoffs.py:18-25`
- **Defect:** `LOOP` list hardcodes skill names; no filesystem validation. If skill is renamed, validator silently passes despite missing skill.
- **Failure scenario:** Skill in `LOOP` is renamed → validator silently passes despite skill missing → regression detector becomes stale → handoff chain could break without detection.
- **Watch-list class:** #5 (stale skill/agent name references)

---

### LOW — Stage equality check is strict (possible regression)

- **File:** `scripts/al_dev_tools/docs/maintainer_mermaid.py:662`
- **Defect:** Line 662 uses strict equality (`==`) instead of superset check (`>=`) like "decide" (line 653), though currently this matches the design. Worth documenting as intentional.
- **Current:** `if stage == "implement" and {contract.skill for contract in stage_contracts} == {"implement-plugin-health"}:`
- **Risk:** If new sub-skills are added to implement stage (e.g., "implement-plugin-health-preflight"), focused view silently falls back to generic rendering. Lower priority than other findings.
- **Watch-list class:** —

---

### LOW — Glob validation doesn't verify directory content

- **File:** `scripts/al_dev_tools/health/ledger_queries.py:62-76`
- **Defect:** `candidate_paths()` matches object names to directories via glob (e.g., `profile-al-dev-shared/skills/{name}`). Verifies path glob matches something but doesn't confirm matched directory contains valid SKILL.md or agent markdown file.
- **Failure scenario:** Skill `foo` deleted (SKILL.md removed), but directory `profile-al-dev-shared/skills/foo/` remains (stale cache) → ledger row mapped to stale directory → `commits_since()` called on stale path → misleading staleness results.
- **Watch-list class:** #5 (stale skill/agent name references)

---

## Clusters Reviewed

- ✅ **ledger-core** (9 files) — 1 Critical, 2 High, 3 Medium, 1 Low
- ✅ **health-checks** (10 files) — 1 Critical, 1 Medium
- ✅ **docs-render** (14 files) — 4 High, 1 Medium, 1 Low
- ✅ **shared-utils** (8 files) — Clean (no verified bugs)
- ✅ **validators** (10 files) — 4 Critical
- ✅ **generators** (9 files) — 1 Critical, 2 High, 3 Medium, 1 Low
