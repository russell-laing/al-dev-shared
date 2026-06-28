# Scripts Quality Sweep

Date: 2026-06-28
Scope: `scripts/` follow-up work after the second quality sweep

## Implemented Changes

1. Repaired the `health_disposition_store.py match` CLI contract by defining the missing parser arguments and adding subprocess-level regression coverage.
2. Removed the wrapper double-load execution path for the health CLIs so direct script execution no longer relies on pre-import plus `runpy`.
3. Centralized `docs/health` path defaults into `scripts/al_dev_tools/health/paths.py`.
4. Replaced repeated runtime artifact validation branches in `scripts/validate_artifact_contracts.py` with a declarative rule registry.
5. Moved maintainer-guide page keys into a shared registry to reduce stage/page drift.

## Validation

- `python3 -m unittest scripts.tests.test_health_disposition_store_match scripts.tests.test_check_disposition_store_consistency scripts.tests.test_compat_entrypoints -v`
- `python3 -m unittest scripts.tests.test_runtime_artifacts scripts.tests.test_health_paths scripts.tests.test_validate_artifact_contracts scripts.tests.test_generate_maintainer_guide -v`
- `python3 -m unittest discover -s scripts/tests -p 'test_*.py'`
- `python3 -m py_compile scripts/*.py scripts/al_dev_tools/*.py scripts/al_dev_tools/docs/*.py scripts/al_dev_tools/health/*.py`

## Remaining Follow-Ups

1. Consider pushing the `docs/health` path helper into the remaining migration/reporting scripts that still compute paths inline.
2. Consider a separate plan for larger module decomposition in `scripts/al_dev_tools/docs/maintainer_rendering.py` and `scripts/migrate_health_dispositions.py`.
3. Keep any future `scripts/` review-only sweeps appending new evidence instead of rewriting this artifact.
