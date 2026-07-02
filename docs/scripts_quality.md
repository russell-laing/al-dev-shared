# Scripts Quality Review

Generated: 2026-07-03  
Files reviewed: 53 | Clusters: 6 | Skipped (compat shims): 2

## Summary

- **Critical:** 6 | **High:** 8 | **Medium:** 5 | **Low:** 2
- **Watch-list matches:** All 7 bug classes represented

---

## Findings (Ranked by Severity)

### CRITICAL — Race condition in append_event allows duplicate event_ids

- **File:** `scripts/al_dev_tools/health/disposition_events.py:86–115`
- **Defect:** Two concurrent `append_event()` calls can both pass the uniqueness check and write duplicate event_ids to the ledger, corrupting the JSONL store.
- **Failure scenario:** Processes A and B load existing_ids concurrently, both check their event_id against a stale snapshot (Process A's pending write invisible to Process B), both pass, both append to file. Ledger now has duplicate event_ids.
- **Watch-list class:** 2 (Non-atomic / non-idempotent writes)

---

### CRITICAL — Relative path default in health_benchmark_adapter breaks artifact lookup

- **File:** `scripts/al_dev_tools/health/health_benchmark_adapter.py:546`
- **Defect:** `--root` defaults to `Path(".")` (cwd-relative) instead of `bootstrap_repo(__file__)`. Tool silently reads from wrong directory, reports stale results.
- **Failure scenario:** Run from subdirectory; tool resolves paths relative to cwd instead of repo root; silently returns empty or stale results without error.
- **Watch-list class:** 1 (Ledger fork from stale or relative paths)

---

### CRITICAL — Fail-open in validate_lens_agents when .claude/agents/ missing

- **File:** `scripts/validate_lens_agents.py:44–50`
- **Defect:** If `.claude/agents/` directory doesn't exist, `_get_lens_agents()` silently returns empty list. Main loop doesn't iterate. Validator reports `PASS` instead of failing.
- **Failure scenario:** Developer accidentally deletes `.claude/agents/`; commit passes validation without running any lens agent checks.
- **Watch-list class:** 4 (Fail-open validators)

---

### CRITICAL — Fail-open in validate_shared_surface with empty skills/agents dirs

- **File:** `scripts/validate_shared_surface.py:85–100`
- **Defect:** Checks directory existence but not content. Empty `profile-al-dev-shared/agents/` and `profile-al-dev-shared/skills/` pass validation with "all clean" message.
- **Failure scenario:** All `.md` files deleted from skills/agents dirs; validator passes with OK status.
- **Watch-list class:** 4 (Fail-open validators)

---

### CRITICAL — Fail-open in validate_harness_neutrality when scan directories missing

- **File:** `scripts/validate_harness_neutrality.py:115–123`
- **Defect:** `iter_markdown_files()` silently skips missing directories. If all `SCAN_DIRS` are missing, yields 0 files and validator reports PASS.
- **Failure scenario:** `profile-al-dev-shared/skills/` deleted or renamed; validator passes without scanning skills.
- **Watch-list class:** 4 (Fail-open validators)

---

### HIGH — Missing agent/knowledge reference validation in map rendering

- **File:** `scripts/al_dev_tools/docs/map_rendering.py:587–589`
- **Defect:** Validates skill-to-skill edges only. Broken agent and knowledge references silently pass validation and get rendered into docs.
- **Failure scenario:** Skill references non-existent agent (`al-dev-shared:fake-agent`); validation succeeds; stale link rendered into docs.
- **Watch-list class:** 5 (Stale skill/agent name references in generators)

---

### HIGH — Orphaned tempfile on backup copy failure in map rendering

- **File:** `scripts/al_dev_tools/docs/map_rendering.py:601–612`
- **Defect:** If `shutil.copy2()` fails, `backup_path` is never added to tracking dict. Tempfile persists on disk and is never cleaned up.
- **Failure scenario:** Disk I/O error during backup; tempfile left orphaned in doc directories, accumulating over multiple failed runs.
- **Watch-list class:** 2 (Non-atomic / non-idempotent writes)

---

### HIGH — Conflicting path derivations in health_static_lenses create fork risk

- **File:** `scripts/health_static_lenses.py:69–87`
- **Defect:** Line 69 uses `REPO_ROOT = bootstrap_repo(__file__)` but line 83 redefines `REPO = Path(__file__).resolve().parents[1]`, then uses problematic REPO for paths. If derivations diverge, ledger artifacts fork.
- **Failure scenario:** Script invoked from different context; `bootstrap_repo()` and manual derivation disagree; paths diverge; ledger shard written to wrong location.
- **Watch-list class:** 1 (Ledger fork from stale or relative paths)

---

### HIGH — Default policy path inconsistency in generate_agent_projections

- **File:** `scripts/generate_agent_projections.py:39–44`
- **Defect:** `default_projection_policy()` uses `Path(__file__).resolve().parents[1]` instead of `bootstrap_repo()`, inconsistent with line 11. If called from CI with symlinked paths, policy lookup may fail.
- **Failure scenario:** Test suite invoked from CI; **file** resolves to symlink; policy_path diverges; policy lookup fails or reads stale policy.
- **Watch-list class:** 1 (Ledger fork from stale or relative paths)

---

### HIGH — Race condition in batch_decline allows duplicate event_ids

- **File:** `scripts/al_dev_tools/health/disposition_events.py:132–137`
- **Defect:** `seq_counter` initialized once, not per iteration. Comment says "Reload max sequence for each event" but doesn't. Concurrent calls can allocate same event_id.
- **Failure scenario:** Processes A and B both load max_seq = 10, init seq_counter = 9 once, both increment to 10, both append "disp_20260701_000010" → duplicate.
- **Watch-list class:** 2 (Non-atomic / non-idempotent writes)

---

### HIGH — Race condition in sync_shard deduplication allows duplicate rows

- **File:** `scripts/health_disposition_store.py:328–337`
- **Defect:** Builds static snapshot of existing row_ids at start, then checks against stale set. Concurrent calls can both decide to write same row_id.
- **Failure scenario:** Processes A and B start sync_shard, load history (identical snapshot), both find event not in snapshot, both append same row_id to history.
- **Watch-list class:** 2 (Non-atomic / non-idempotent writes)

---

### HIGH — Hardcoded dossier format regex fragile to changes

- **File:** `scripts/al_dev_tools/health/precision_gate_fixture.py:33`
- **Defect:** Pattern assumes `**[id]**:` format. If report-plugin-health changes ID formatting, fixture silently passes with wrong format.
- **Failure scenario:** report-plugin-health emits `**id**:` instead of `**[id]**:`; fixture verification passes despite format change.
- **Watch-list class:** 3 (Disposition/findings parse fragility)

---

### HIGH — Hard-coded skill name sets never reconciled against filesystem

- **File:** `scripts/validate_maintainer_contracts.py:31–55`
- **Defect:** `MULTI_PHASE_SKILLS`, `DISPATCHING_SKILLS` etc. are hard-coded. When a skill is renamed, old name remains in sets indefinitely. No reconciliation mechanism.
- **Failure scenario:** Skill renamed from `discover-plugin-health` to `discover-health-plugin`; old name stays in set; new skill isn't validated; mismatch escapes detection.
- **Watch-list class:** 5 (Stale skill/agent name references in generators)

---

### MEDIUM — Parse fragility in companion_surface_contract

- **File:** `scripts/al_dev_tools/companion_surface_contract.py:52`
- **Defect:** No type validation of `"packages"` field before iteration. If YAML has `packages: "string"`, loop iterates over characters instead of dicts.
- **Failure scenario:** Malformed `companions/companion-packages.yaml` with `packages: "string"` silently corrupts replacements; downstream gets unexpanded `${AL_DEV_HARNESS_HOME}` placeholders.
- **Watch-list class:** 3 (Disposition/findings parse fragility)

---

### MEDIUM — Duplicated path normalization logic in health_static_lenses

- **File:** `scripts/health_static_lenses.py:171–188`
- **Defect:** `changed_paths()` duplicates normalization logic from discover SKILL. If discover updates its normalization for edge cases, health_static_lenses continues using pre-fix version.
- **Failure scenario:** Discover SKILL fixes normalization for symlinks; health_static_lenses continues using stale logic; --since filtering misses modified files.
- **Watch-list class:** 7 (Duplication / copied-contract drift)

---

### MEDIUM — Default directory is cwd-relative in select_health_artifacts

- **File:** `scripts/al_dev_tools/health/select_health_artifacts.py:90`
- **Defect:** `Path("docs/health")` is relative to cwd, not REPO_ROOT. Breaks if called from subdirectories.
- **Failure scenario:** Invoked from `.dev/` subdirectory; looks for artifacts in `.dev/docs/health/` instead of repo root; silently returns empty.
- **Watch-list class:** 1 (Ledger fork from stale or relative paths)

---

### MEDIUM — Misleading comment-code mismatch in batch_decline

- **File:** `scripts/al_dev_tools/health/disposition_events.py:126`
- **Defect:** Comment claims "Reload max sequence for each event" but code only initializes seq_counter once. Suggests unintended behavior per High-4 above.
- **Failure scenario:** Maintainer refactors code assuming comment is accurate; race condition persists or new variant introduced.
- **Watch-list class:** 7 (Duplication / copied-contract drift)

---

### MEDIUM — Asymmetric re-export pattern in shared_surface_names

- **File:** `scripts/al_dev_tools/shared_surface_names.py:108–149`
- **Defect:** Reference contract functions wrapped in pass-through functions; companion functions imported directly. No logic difference, inconsistent surface.
- **Failure scenario:** Callers must remember which functions are wrapped vs. aliased; code maintenance burden.
- **Watch-list class:** 7 (Duplication / copied-contract drift)

---

### MEDIUM — Unhandled subprocess errors in validate_artifact_leaks

- **File:** `scripts/validate_artifact_leaks.py:35–42`
- **Defect:** `subprocess.run(..., check=True)` raises unhandled exceptions. Pre-commit hook gets Python stack trace instead of clear error message.
- **Failure scenario:** Developer outside git repo; sees `CalledProcessError` traceback; unclear if validation passed or failed.
- **Watch-list class:** 4 (Fail-open validators)

---

### LOW — Unused dead-code function in maintainer_mermaid

- **File:** `scripts/al_dev_tools/docs/maintainer_mermaid.py:268–269`
- **Defect:** `_normalize_skill_alias()` defined but never called. Appears to be incomplete infrastructure.
- **Failure scenario:** None functionally; clutters module.
- **Watch-list class:** 7 (Duplication / copied-contract drift)

---

### LOW — Import style violation in companion_surface_contract

- **File:** `scripts/al_dev_tools/companion_surface_contract.py:38`
- **Defect:** `import os` inside function body; PEP 8 requires module-level imports.
- **Failure scenario:** None functionally; minor style violation.
- **Watch-list class:** 7 (Duplication / copied-contract drift)

---

## Watch-list Coverage

| Class | Count | Findings |
|-------|-------|----------|
| 1 — Ledger fork from paths | 3 | health_static_lenses, generate_agent_projections, select_health_artifacts |
| 2 — Non-atomic writes | 5 | append_event, batch_decline, sync_shard, backup orphan, comment/code mismatch |
| 3 — Parse fragility | 2 | companion_surface_contract, precision_gate_fixture |
| 4 — Fail-open validators | 6 | validate_lens_agents, validate_shared_surface, validate_harness_neutrality, subprocess errors, map_rendering, select_health_artifacts |
| 5 — Stale references | 2 | map_rendering (agent refs), validate_maintainer_contracts (skill sets) |
| 7 — Duplication/drift | 3 | health_static_lenses (normalization), shared_surface_names (re-exports), disposition_events (comment/code) |

**All seven watch-list classes represented in findings.**
