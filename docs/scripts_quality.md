# Scripts Quality Review

**Generated:** 2026-07-03  
**Files reviewed:** 22 | **Clusters:** 5 | **Skipped (compat shims):** 13

## Summary

- **Critical:** 1 | **High:** 3 | **Medium:** 7 | **Low:** 0
- **Watch-list matches:** 11 (100% of findings map to recurring bug classes)

## Findings (ranked by severity)

### Critical — Ledger fork vulnerability

**File:** `scripts/al_dev_tools/health/health_disposition_store.py:113`

**Defect:** `dispositions_events_root()` called without explicit `root` parameter, violating contract in `paths.py` that requires explicit root to prevent cwd-relative resolution.

**Failure scenario:** If `_cli_match(findings, ledger, None)` is called directly (not via CLI where argparse defaults root), line 113 raises `TypeError`. This represents a broken contract and opens path-resolution vulnerability.

**Watch-list class:** #1 (Ledger fork from stale/relative paths)

---

### High — Sequence gap in batch operations

**File:** `scripts/al_dev_tools/health/disposition_events.py:128–135`

**Defect:** `batch_decline` increments sequence number returned by `next_event_id()`, creating ID gaps. When last event is `000010`, `next_event_id` correctly returns `000011`, but the loop increments to `000012`, leaving `000011` unused.

**Failure scenario:** Running `batch_decline([row1, row2], "2026-07-03")` with last event `000010` creates events `000012, 000013` (gap at `000011`). Re-running the same batch produces `000015, 000016` with different IDs but identical `closes_event_ids`, violating idempotency and leaving the ledger partially applied.

**Watch-list class:** #2 (Non-atomic/non-idempotent writes)

---

### High — Case-sensitive header match

**File:** `scripts/al_dev_tools/health/precision_gate_fixture.py:24`

**Defect:** Condition `stripped == "## Quality findings"` performs exact-case match on section header. If dossier generation changes casing (e.g., "## Quality Findings"), the section detection fails.

**Failure scenario:** Dossier header capitalized to "## Quality Findings" → section detection fails → `retained_section` is empty → all expected IDs marked missing → test incorrectly reports FAIL.

**Watch-list class:** #3 (Disposition/findings parse fragility — normalize casing on read AND write)

---

### Medium — cwd-relative default root

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

## Clean Clusters & Files

**Shared-utils cluster (7 files):** `_compat_entrypoint.py`, `companion_surface_contract.py`, `io_utils.py`, `markdown_frontmatter.py`, `reference_contracts.py`, `runtime_artifacts.py`, `shared_surface_names.py`

**Generators cluster (7 files):** `check_health_loop_handoffs.py`, `derive_agent_callers.py`, `derive_skill_spawned_agents.py`, `generate_maintainer_guide.py`, `generate_map_doc_sections.py`, `generate_plugin_graph.py`, `summarize_superpowers_history.py`

**Additional clean files:**

- `scripts/al_dev_tools/health/paths.py`
- `scripts/validate_artifact_contracts.py`
- `scripts/validate_artifact_leaks.py`
- `scripts/validate_knowledge_quality.py`
- `scripts/validate_reference_integrity.py`
- `scripts/validate_shared_surface.py`
