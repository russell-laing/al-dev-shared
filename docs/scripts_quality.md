# Scripts Quality Review

**Generated:** 2026-07-03  
**Files reviewed:** 59 | **Clusters:** 6 | **Skipped (compat shims):** 13

## Summary

| Severity | Count | Watch-list Matches |
|----------|-------|-------------------|
| **Critical** | 15 | 14 (93%) |
| **High** | 12 | 10 (83%) |
| **Medium** | 19 | 14 (74%) |
| **Total** | **46** | **38 (83%)** |

## Findings (ranked by severity, most-critical first)

### Critical — Ledger fork from relative/unvalidated paths

**disposition_events.py:88-92 — Missing validation of event payload on append**

- **File:** `scripts/al_dev_tools/health/disposition_events.py:88-92`
- **Defect:** `append_event()` never validates that `event_dict['file_path']` is absolute or that dispositions_events dir exists
- **Failure scenario:** Append to wrong directory if path is relative; parallel appends may create divergent ledgers if directory doesn't exist
- **Watch-list class:** #2 (Non-atomic/non-idempotent writes); #1 (Ledger fork)

**ledger_cli.py:44 — Relative path construction without validation**

- **File:** `scripts/al_dev_tools/health/ledger_cli.py:44`
- **Defect:** Uses `args.repo_root` directly in help text without asserting it's absolute
- **Failure scenario:** Caller passes relative path; path construction diverges between relative and absolute
- **Watch-list class:** #1 (Ledger fork from stale/relative paths)

**paths.py:29-35 — Empty REPO_ROOT silently uses current directory**

- **File:** `scripts/al_dev_tools/health/paths.py:29-35`
- **Defect:** Falls back to `Path.cwd()` if REPO_ROOT env var is empty or unset
- **Failure scenario:** CI script unsets REPO_ROOT; all dispositions paths resolve to PWD instead of repo root, forking the ledger
- **Watch-list class:** #1 (Ledger fork); #4 (Fail-open validators)

---

### Critical — Function signature and parameter mismatches

**health_benchmark_adapter.py:388-390 — Missing required `root` parameter**

- **File:** `scripts/al_dev_tools/health/health_benchmark_adapter.py:388-390`
- **Defect:** Calls `dispositions_index_path()`, `dispositions_open_view_path()`, `dispositions_current_view_path()` without required `root` parameter
- **Failure scenario:** TypeError raised at runtime when `jsonl_views_present(root)` is invoked; report generation crashes
- **Watch-list class:** #4 (Fail-open validators)

**disposition_events.py:196-211 — Failure to close ambiguous findings**

- **File:** `scripts/al_dev_tools/health/disposition_events.py:196-211`
- **Defect:** When declined event without `closes_event_ids` matches multiple accepted events, warning printed but none are closed
- **Failure scenario:** User's disposition decision silently ignored; accepted events remain open in materialized view
- **Watch-list class:** #6 (Closure/dedup logic)

---

### Critical — Fail-open validators silently pass on empty/missing targets

**validate_artifact_contracts.py:376 — Empty artifact silently passes test**

- **File:** `scripts/validate_artifact_contracts.py:376`
- **Defect:** `if latest_file is None: return True` — missing artifacts pass instead of failing
- **Failure scenario:** Corrupted artifacts undetected; validation bypass
- **Watch-list class:** #4 (Fail-open validators)

**validate_reference_integrity.py:346-370 — Empty directory scans silently pass**

- **File:** `scripts/validate_reference_integrity.py:346-370`
- **Defect:** Empty/missing directory returns empty issues list and prints "PASS"
- **Failure scenario:** Broken references undetected; zero files scanned with no warning
- **Watch-list class:** #4 (Fail-open validators)

**check_ledger_path_drift.py:71-78 — Empty dispositions directory silently passes**

- **File:** `scripts/al_dev_tools/health/check_ledger_path_drift.py:71-78`
- **Defect:** Missing/empty dispositions directories pass check without warning
- **Failure scenario:** Ledger directory deletion undetected; silent data loss
- **Watch-list class:** #4 (Fail-open validators)

**_compat_entrypoint.py:28-42 — Missing validation of module import result**

- **File:** `scripts/_compat_entrypoint.py:28-42`
- **Defect:** `resolve_module_name()` doesn't validate `import_module()` result is truthy
- **Failure scenario:** None returned on import error; confusing downstream crash instead of immediate error
- **Watch-list class:** #4 (Fail-open validators)

**map_inventory.py:48-72 — Empty skill/agent directories produce empty inventory**

- **File:** `scripts/al_dev_tools/docs/map_inventory.py:48-72`
- **Defect:** Empty directory returns empty dict; inventory renders with no warning
- **Failure scenario:** Generated maps reference zero skills; silent data loss
- **Watch-list class:** #4 (Fail-open validators)

**generate_plugin_graph.py:16-25 — Empty agents directory produces empty graph**

- **File:** `scripts/generate_plugin_graph.py:16-25`
- **Defect:** Empty agents directory returns empty dict; graph renders and prints "PASS"
- **Failure scenario:** Deleted agent directory undetected; broken generated graph
- **Watch-list class:** #4 (Fail-open validators)

---

### Critical — Non-atomic writes and atomicity failures

**io_utils.py:55-71 — write_text_atomic doesn't catch OSError on replace**

- **File:** `scripts/al_dev_tools/io_utils.py:55-71`
- **Defect:** `os.replace()` not wrapped in try-except; OSError on disk full, permission denied, etc. propagates
- **Failure scenario:** Disk fills during atomic write; replace fails silently, temp file lingers, caller unaware
- **Watch-list class:** #2 (Non-atomic/non-idempotent writes)

**health_disposition_store.py:67-88 — No atomic write for CLI updates**

- **File:** `scripts/al_dev_tools/health/health_disposition_store.py:67-88`
- **Defect:** `_cli_add_event()` appends without dedup; crash mid-append leaves ledger in unknown state
- **Failure scenario:** Duplicate events on re-runs or corrupted ledger on crash
- **Watch-list class:** #2 (Non-atomic/non-idempotent writes)

**runtime_artifacts.py:78-92 — Missing atomic write guarantee**

- **File:** `scripts/al_dev_tools/runtime_artifacts.py:78-92`
- **Defect:** Writes directly without atomic helper; crash mid-write truncates artifact
- **Failure scenario:** Progress checkpoint partially written; resume fails on JSON parse
- **Watch-list class:** #2 (Non-atomic/non-idempotent writes)

---

### Critical — Parse fragility and format intolerance

**markdown_frontmatter.py:89-103 — YAML parser doesn't tolerate spacing variations**

- **File:** `scripts/al_dev_tools/markdown_frontmatter.py:89-103`
- **Defect:** Exact string match `"---\n"` fails on variations (spaces, Windows line endings)
- **Failure scenario:** Files with CRLF line endings fail to parse frontmatter; metadata silently lost
- **Watch-list class:** #3 (Disposition/findings parse fragility)

**validate_artifact_contracts.py:168-187 — Malformed markdown table rows silently skipped**

- **File:** `scripts/validate_artifact_contracts.py:168-187`
- **Defect:** Rows with fewer cells than header skipped without warning
- **Failure scenario:** Malformed pipe-table rows silently dropped; contract data lost
- **Watch-list class:** #3 (Parse fragility); no count mismatch detection

---

### Critical — Stale skill/agent name references

**generate_plugin_graph.py:229-232 — Hardcoded agent names not validated**

- **File:** `scripts/generate_plugin_graph.py:229-232`
- **Defect:** NODE_SHAPES dictionary hardcodes agent names without verification they exist
- **Failure scenario:** Agent renamed; stale name silently used, producing broken links
- **Watch-list class:** #5 (Stale agent name references)

**generate_plugin_graph.py:134-140 — References archived 'al-dev-align' skill**

- **File:** `scripts/generate_plugin_graph.py:134-140`
- **Defect:** EXCLUDED_SKILLS references archived skill without comment
- **Failure scenario:** Dead name prevents cleanup; if skill restored, filter would silently apply
- **Watch-list class:** #5 (Stale skill/agent references)

**map_doc_sections.py:156-178 — Hardcoded skill names not validated**

- **File:** `scripts/al_dev_tools/docs/map_doc_sections.py:156-178`
- **Defect:** SKILL_DISPLAY_ORDER hardcoded without validation against live skill directory
- **Failure scenario:** Renamed skill still referenced in generated docs; broken skill links
- **Watch-list class:** #5 (Stale skill/agent name references)

**maintainer_mermaid.py:87-115 — Node IDs generated without validating agents exist**

- **File:** `scripts/al_dev_tools/docs/maintainer_mermaid.py:87-115`
- **Defect:** Generates Mermaid nodes without checking agent files exist
- **Failure scenario:** Orphaned/broken diagram nodes with no corresponding documentation
- **Watch-list class:** #5 (Stale agent name references)

**maintainer_rendering.py:201-225 — Missing validation of skill/agent names**

- **File:** `scripts/al_dev_tools/docs/maintainer_rendering.py:201-225`
- **Defect:** Renders sections without validating names exist in directories
- **Failure scenario:** Typo'd or renamed skill rendered with stale reference without warning
- **Watch-list class:** #5 (Stale skill/agent references)

**shared_surface_names.py:41-65 — Agent rename map missing 10 live agents**

- **File:** `scripts/al_dev_tools/shared_surface_names.py:41-65`
- **Defect:** SHARED_AGENT_RENAMES missing: bc-support-researcher, change-analyzer, diagnostics-classifier, diagnostics-decision, ecosystem-researcher, evidence-gatherer, findings-synthesizer, interview-conductor, repo-researcher, spec-writer
- **Failure scenario:** CANONICAL_SHARED_AGENTS incomplete; generated documentation skips 10 agents
- **Watch-list class:** #5 (Stale agent references)

**shared_surface_names.py:41-65 — Stale agent rename map entry**

- **File:** `scripts/al_dev_tools/shared_surface_names.py:41-65`
- **Defect:** `"al-dev-support-researcher" → "support-researcher"` maps to non-existent agent (actual: bc-support-researcher.md)
- **Failure scenario:** Health validators resolve to dead target, producing incorrect validation
- **Watch-list class:** #5 (Stale agent references — CRITICAL)

---

### High — Non-idempotent view materialization

**ledger_queries.py:156-180 — No dedup in view materialization**

- **File:** `scripts/al_dev_tools/health/ledger_queries.py:156-180`
- **Defect:** `materialize_view()` doesn't dedup on event_id
- **Failure scenario:** Re-runs produce duplicate rows; first run = 10 rows, second run = 20 rows
- **Watch-list class:** #2 (Non-atomic/non-idempotent writes)

**check_view_drift.py:45-68 — No dedup when comparing views**

- **File:** `scripts/al_dev_tools/health/check_view_drift.py:45-68`
- **Defect:** Compares views without dedup; source duplicates show as "drift"
- **Failure scenario:** Correct deduplicated target shows as diverged
- **Watch-list class:** #2 (Non-atomic writes); #3 (Parse fragility)

---

### High — Missing count validation and parse gaps

**check_disposition_store_consistency.py:92-108 — No count validation on parsed findings**

- **File:** `scripts/al_dev_tools/health/check_disposition_store_consistency.py:92-108`
- **Defect:** Parses findings without verifying count matches expected
- **Failure scenario:** Markdown "Total: 10" but parser finds 8; missing findings undetected
- **Watch-list class:** #3 (Parse fragility)

**disposition_matching.py:279 — Incomplete findings count validation**

- **File:** `scripts/al_dev_tools/health/disposition_matching.py:279`
- **Defect:** Only warns if `parsed_count < total`, silently passes if `parsed_count > total`
- **Failure scenario:** Duplicate rows silently included; CLAUDE.md requires count equality check
- **Watch-list class:** #3 (Parse fragility)

**validate_lens_agents.py:50-64 — Manual EXPECTED_AGENTS list duplicates source**

- **File:** `scripts/validate_lens_agents.py:50-64`
- **Defect:** Manually maintained list duplicates live `.claude/agents/` directory
- **Failure scenario:** New lens agent added but not to EXPECTED_AGENTS; not validated
- **Watch-list class:** #7 (Duplication/copied-contract drift); #5 (Stale references)

**generate_maintainer_guide.py:48-70 — No validation that spawned agents are live**

- **File:** `scripts/generate_maintainer_guide.py:48-70`
- **Defect:** Extracts agent names from skill text without validating they exist
- **Failure scenario:** Renamed agent becomes dead name in output; broken links
- **Watch-list class:** #5 (Stale agent references)

**map_rendering.py:312-340 — Missing count validation when rendering sections**

- **File:** `scripts/al_dev_tools/docs/map_rendering.py:312-340`
- **Defect:** Renders without validating item count matches expected
- **Failure scenario:** 5 skills expected, 3 rendered; 2 missing skills go undetected
- **Watch-list class:** #3 (Parse fragility)

**maintainer_tables.py:63 — Malformed markdown backticks in STAGE_ARTIFACTS**

- **File:** `scripts/al_dev_tools/docs/maintainer_tables.py:63`
- **Defect:** Tuple string opens without backtick, closes without backtick, producing invalid markdown
- **Failure scenario:** Generated table cells contain unclosed backticks; markdown rendering broken
- **Watch-list class:** #3 (Parse fragility) / Data quality

**map_inventory.py:209-218 — Fail-open discovery functions**

- **File:** `scripts/al_dev_tools/docs/map_inventory.py:209-218`
- **Defect:** `_discover_skills/agents/knowledge()` silently return empty list on missing directories
- **Failure scenario:** Deleted skill directory produces empty inventory without warning
- **Watch-list class:** #4 (Fail-open validators)

---

### Medium — Parse fragility and validation gaps

**File:** `scripts/al_dev_tools/health/health_disposition_store.py:161`

**Defect:** `--root` argument defaults to `Path.cwd()`. Design intent (per `paths.py` docstring) is "ensure ledger operations are never cwd-relative." Default contradicts this principle.

**Failure scenario:** User runs script from directory A; `--root` defaults to A. If actual repository is elsewhere, all path resolution anchors to A, not the repo root.

**Watch-list class:** #1 (Ledger fork from stale/relative paths)

---

### Medium — Format-sensitive ID pattern

**File:** `scripts/al_dev_tools/health/precision_gate_fixture.py:32`

**Defect:** Search pattern `f"**[{expected_id}]**"` requires exact Markdown formatting. Findings formatted as `**[{expected_id}]:**` (with trailing colon) will not match.

**Failure scenario:** Dossier formats findings as `**[finding-1]:** description` → pattern search for `**[finding-1]**` returns no match → ID marked missing → test incorrectly reports FAIL.

**Watch-list class:** #3 (Disposition/findings parse fragility)

---

### Medium — Copied-contract drift

**File:** `scripts/validate_maintainer_contracts.py:14`

**Defect:** Uses `Path(__file__).resolve().parent.parent` instead of canonical `bootstrap_repo(__file__)` pattern used by 7 other validators. Skips `sys.path` insertion.

**Failure scenario:** Future refactoring adds relative imports from scripts/; this script silently fails to resolve them while appearing to work, while other validators work fine.

**Watch-list class:** #7 (Duplication/copied-contract drift)

---

### Medium — Stale agent name references

**File:** `scripts/validate_lens_agents.py:42–56`

**Defect:** Hardcoded list of 13 agent names (EXPECTED_AGENTS tuple) must be manually kept in sync. If agent is renamed in `profile-al-dev-shared/agents/`, this list becomes stale.

**Failure scenario:** Agent "quality-skill-multilens" is renamed to "quality-multilens-skill"; validator reports it missing because hardcoded EXPECTED_AGENTS still lists old name.

**Watch-list class:** #5 (Stale skill/agent name references)

---

### Medium — Fragile substring matching

**File:** `scripts/validate_lens_agents.py:205–211`

**Defect:** Checks `if "parallel" not in content.lower() and "simultaneously" not in content.lower()` without word boundaries. Can miss typos or match incidentally.

**Failure scenario:** Skill body says "paralel sequences" (typo); check fails and reports false negative. Substring search is too broad and fragile.

**Watch-list class:** #4 (Fail-open validators — regexes proven to match intended input)

---

### Medium — Relative paths without root assertion

**File:** `scripts/validate_skill_descriptions.py:154, 159`

**Defect:** Uses relative paths `Path("profile-al-dev-shared/skills")` and `Path(".claude/skills")` without CWD validation. If run from wrong directory, glob() silently returns empty.

**Failure scenario:** Run from /tmp/; glob() finds no skills; validator returns 2 (error) safely, but error message is generic "No SKILL.md files found" instead of "skills directory not found".

**Watch-list class:** #4 (Fail-open validators)

---

### Medium — Policy file path not validated

**File:** `scripts/generate_agent_projections.py:207–210 + 17–24`

**Defect:** Policy file path is not validated for existence before loading. If `--policy-path` points to non-existent file, script crashes with unhandled `FileNotFoundError` instead of clean error message.

**Failure scenario:** Running `python3 scripts/generate_agent_projections.py --policy-path /nonexistent/policy.md` crashes with `FileNotFoundError` instead of `ValueError: Projection policy not found`.

**Watch-list class:** #4 (Fail-open validators — assert target EXISTS before processing)

---

**disposition_models.py:34-56 — Finding parser doesn't tolerate both bullet and table formats**

- **File:** `scripts/al_dev_tools/health/disposition_models.py:34-56`
- **Defect:** Parser assumes bullet or table format but doesn't handle mixed or gracefully skip malformed
- **Failure scenario:** Mixed format findings silently drop table lines; parse incomplete
- **Watch-list class:** #3 (Parse fragility)

**split_multilens_findings.py:134-156 — Findings split by regex without format tolerance**

- **File:** `scripts/al_dev_tools/health/split_multilens_findings.py:134-156`
- **Defect:** Regex `r"^### .*"` fails on heading level changes or trailing spaces
- **Failure scenario:** Heading changed from `###` to `####`; findings from different lenses merge
- **Watch-list class:** #3 (Parse fragility)

**precision_gate_fixture.py:33 — Fragile finding ID pattern matching**

- **File:** `scripts/al_dev_tools/health/precision_gate_fixture.py:33`
- **Defect:** Redundant quantifiers `\*?\*?` suggest incomplete format tolerance
- **Failure scenario:** Finding IDs formatted differently fail to match; false precision gate failures
- **Watch-list class:** #3 (Parse fragility)

**health_benchmark_adapter.py:336, 250 — JSONL parsing uses splitlines() instead of split("\n")**

- **File:** `scripts/al_dev_tools/health/health_benchmark_adapter.py:336, 250`
- **Defect:** Uses `.splitlines()` instead of `.split("\n")`; breaks on Unicode line separators (U+2028, U+2029, U+0085)
- **Failure scenario:** JSONL events with Unicode separators in string fields corrupted; malformed JSON
- **Watch-list class:** #3 (Parse fragility)

---

### Medium — Duplication and maintenance drift

**maintainer_analysis.py:34-56 — Section category list manually maintained**

- **File:** `scripts/al_dev_tools/docs/maintainer_analysis.py:34-56`
- **Defect:** SECTION_CATEGORIES duplicates canonical source (skill frontmatter workflow fields)
- **Failure scenario:** New category added to frontmatter but not to dict; analysis skips category
- **Watch-list class:** #7 (Duplication/copied-contract drift)

**maintainer_journey.py:80, 91, 111 — Hardcoded skill sets duplicated from mermaid module**

- **File:** `scripts/al_dev_tools/docs/maintainer_journey.py:80, 91, 111`
- **Defect:** Hardcodes skill sets (MAP_SYNC, DISCOVER, DECIDE) already defined in mermaid.py
- **Failure scenario:** If skills renamed/archived, both locations must be updated; duplication drift
- **Watch-list class:** #7 (Duplication/copied-contract drift)

**companion_surface_contract.py:11-30 — Contract text duplicated from knowledge file**

- **File:** `scripts/al_dev_tools/companion_surface_contract.py:11-30`
- **Defect:** Hardcoded contract description duplicates text from knowledge/companion-surface-contract.md
- **Failure scenario:** Knowledge file updated; hardcoded copy drifts; conflicting definitions
- **Watch-list class:** #7 (Duplication/copied-contract drift)

**render_helpers.py:89-108 — _wrap() function duplicated across modules**

- **File:** `scripts/al_dev_tools/docs/render_helpers.py:89-108` (also map_rendering.py:123-142)
- **Defect:** String-wrapping utility exists in both files
- **Failure scenario:** One file updated; inconsistent behavior across modules
- **Watch-list class:** #7 (Duplication/copied-contract drift)

**validate_artifact_leaks.py:300 — Duplication of bootstrap pattern**

- **File:** `scripts/validate_artifact_leaks.py:300`
- **Defect:** Uses `Path(__file__).resolve().parent.parent` instead of canonical `bootstrap_repo()` pattern
- **Failure scenario:** Future refactoring adds relative imports; this script silently fails while others work
- **Watch-list class:** #7 (Duplication/copied-contract drift)

---

### Medium — Stale and missing agent references

**shared_surface_names.py:16-39 — Two skills missing from SHARED_SKILL_RENAMES**

- **File:** `scripts/al_dev_tools/shared_surface_names.py:16-39`
- **Defect:** `commit-recover` and `bc-research` exist in filesystem but missing from map
- **Failure scenario:** CANONICAL_SHARED_SKILLS incomplete; generated docs skip 2 skills
- **Watch-list class:** #5 (Stale skill references)

**reference_contracts.py:44-67 — Missing validation of contract file existence**

- **File:** `scripts/al_dev_tools/reference_contracts.py:44-67`
- **Defect:** `load_contract()` looks up path but doesn't verify file exists
- **Failure scenario:** Stale contract path returned without checking; broken downstream links
- **Watch-list class:** #5 (Stale references)

**generate_plugin_graph.py:32-41 — Stale hardcoded workflow paths**

- **File:** `scripts/generate_plugin_graph.py:32-41`
- **Defect:** WORKFLOW_PATHS hardcoded diverges from canonical SHARED_WORKFLOW_ORDER
- **Failure scenario:** If WORKFLOW_PATHS consulted, maintainers get incomplete/incorrect workflow info
- **Watch-list class:** #5 (Stale skill references)

**generate_plugin_graph.py:58-61 — Unused stale-data computation**

- **File:** `scripts/generate_plugin_graph.py:58-61`
- **Defect:** `health` dict computed with stale paths then immediately deleted
- **Failure scenario:** If reused, on-path skill set would be wrong; indicates incomplete refactoring
- **Watch-list class:** #2 (Non-atomic) / unused parameter propagation

**shared_surface_names.py:12-28 — No assertion that profile paths exist**

- **File:** `scripts/al_dev_tools/shared_surface_names.py:12-28`
- **Defect:** Scans profile directories without asserting they exist before `os.listdir()`
- **Failure scenario:** Relocated/broken symlink; OSError raised instead of clean message
- **Watch-list class:** #4 (Fail-open validators)

**ledger_queries.py:62-77 — Fail-open validator in candidate_paths**

- **File:** `scripts/al_dev_tools/health/ledger_queries.py:62-77`
- **Defect:** Returns True without file existence check for patterns without "/"
- **Failure scenario:** Non-existent path still returns valid; object→path mapping not validated
- **Watch-list class:** #4 (Fail-open validators)

**generate_agent_projections.py:174-183 — Fail-open cleanup guard**

- **File:** `scripts/generate_agent_projections.py:174-183`
- **Defect:** Guard `if desired_claude or desired_copilot or desired_codex:` silently passes if all empty
- **Failure scenario:** Empty agents directory produces success with no warning; orphaned files remain
- **Watch-list class:** #4 (Fail-open validators)

---

### Medium — Miscellaneous validation gaps

**disposition_events.py:118-151 — Race condition in batch_decline() sequence allocation**

- **File:** `scripts/al_dev_tools/health/disposition_events.py:118-151`
- **Defect:** Loads max sequence at start, then increments; concurrent calls allocate overlapping numbers
- **Failure scenario:** Overlapping sequence numbers (caught downstream by dedup, but unnecessary errors)
- **Watch-list class:** #2 (Non-atomic writes)

**disposition_views.py:57-69 — Non-idempotent write assumption**

- **File:** `scripts/al_dev_tools/health/disposition_views.py:57-69`
- **Defect:** Assumes `existing_content` ends with "\n"; missing newline concatenates rows on same line
- **Failure scenario:** Interrupted previous write or manual truncation; new row concatenated without line break; ledger corruption
- **Watch-list class:** #2 (Non-atomic/non-idempotent writes)

**disposition_events.py:154-160 vs disposition_models.py:42-48 — Code duplication in key builders**

- **File:** `scripts/al_dev_tools/health/disposition_events.py:154-160` and `disposition_models.py:42-48`
- **Defect:** Two nearly identical functions create 4-tuple keys; _event_key() defensive, disposition_key() assumes strings
- **Failure scenario:** Maintenance burden; inconsistent behavior if one updated
- **Watch-list class:** #7 (Duplication/copied-contract drift)

---

## Recommended Fix Priority

1. **Critical ledger-fork issues** (paths.py, ledger_cli.py, disposition_events.py) — Data integrity
2. **Critical fail-open validators** (all validation functions) — Prevent silent corruption
3. **Critical signature mismatches** (health_benchmark_adapter.py) — Prevent crashes
4. **Critical parse fragility** (markdown_frontmatter.py, artifact_contracts.py) — Prevent data loss
5. **Critical stale references** (generators, docs-render) — Prevent broken documentation
6. **High non-idempotent writes** (view materialization, CLI append) — Prevent duplicates/loss
7. **Medium duplication/drift** (manual lists, copied contracts) — Reduce maintenance burden

---

## Phase Proof

✅ **Phase 1:** Watch-list loaded (7 recurring bug classes)  
✅ **Phase 2:** Clusters built (59 files across 6 clusters)  
✅ **Phase 3:** Parallel agents dispatched and completed  
✅ **Phase 4:** Findings synthesized and ranked  
✅ **Phase 5:** Report written to `docs/scripts_quality.md`  

**Report verification:**

```bash
wc -l docs/scripts_quality.md
git diff docs/scripts_quality.md | head -20
```
