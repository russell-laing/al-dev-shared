"""Behavioral tests for scripts/sync_history_shard.py.

Loads the script as a module and drives its run() core with temporary paths.
"""

import importlib.util
import os
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "sync_history_shard.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("sync_history_shard", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_dispositions(module, path: Path, rows: list) -> None:
    # The script puts scripts/ on sys.path when loaded, so the table constants
    # are importable from the source module here (the script itself does not
    # re-export them).
    from health_disposition_store import TABLE_HEADER, TABLE_DIVIDER
    path.write_text(
        TABLE_HEADER + "\n" + TABLE_DIVIDER + "\n"
        + "\n".join(rows) + "\n",
        encoding="utf-8",
    )


def test_report_mode_flags_missing_row():
    module = _load_script()
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        dispositions = tmpdir / "dispositions.md"
        _write_dispositions(module, dispositions, [
            "| #001 | tooling | quality | my-skill | Some finding | fixed | 2026-06-10 | note |",
        ])
        history_root = tmpdir / "history"
        history_root.mkdir()
        rc = module.run(dispositions, history_root, fix=False)
        assert rc == 1, f"Expected exit 1 for missing row, got {rc}"
    print("PASS test_report_mode_flags_missing_row")


def test_report_mode_passes_when_present():
    module = _load_script()
    from health_disposition_store import parse_ledger_file, append_row
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        dispositions = tmpdir / "dispositions.md"
        _write_dispositions(module, dispositions, [
            "| #001 | tooling | quality | my-skill | Some finding | fixed | 2026-06-10 | note |",
        ])
        history_root = tmpdir / "history"
        append_row(history_root, parse_ledger_file(dispositions)[0])
        rc = module.run(dispositions, history_root, fix=False)
        assert rc == 0, f"Expected exit 0 when present, got {rc}"
    print("PASS test_report_mode_passes_when_present")


def test_fix_mode_syncs_and_passes():
    module = _load_script()
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        dispositions = tmpdir / "dispositions.md"
        _write_dispositions(module, dispositions, [
            "| #001 | tooling | quality | my-skill | Some finding | fixed | 2026-06-10 | note |",
        ])
        history_root = tmpdir / "history"
        history_root.mkdir()
        rc = module.run(dispositions, history_root, fix=True)
        assert rc == 0, f"Expected exit 0 after --fix, got {rc}"
        # Second report run now passes — row was synced.
        rc2 = module.run(dispositions, history_root, fix=False)
        assert rc2 == 0, f"Expected exit 0 on re-verify, got {rc2}"
    print("PASS test_fix_mode_syncs_and_passes")


def test_non_fixed_rows_ignored():
    module = _load_script()
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        dispositions = tmpdir / "dispositions.md"
        _write_dispositions(module, dispositions, [
            "| #001 | tooling | quality | my-skill | Finding | accepted | 2026-06-10 | note |",
            "| #002 | tooling | quality | my-skill | Finding | declined | 2026-06-10 | note |",
        ])
        history_root = tmpdir / "history"  # absent dir is fine: no fixed rows
        rc = module.run(dispositions, history_root, fix=False)
        assert rc == 0, f"Expected exit 0 with no fixed rows, got {rc}"
    print("PASS test_non_fixed_rows_ignored")


def test_missing_history_dir_fails():
    module = _load_script()
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        dispositions = tmpdir / "dispositions.md"
        _write_dispositions(module, dispositions, [
            "| #001 | tooling | quality | my-skill | Some finding | fixed | 2026-06-10 | note |",
        ])
        rc = module.run(dispositions, tmpdir / "absent-history", fix=False)
        assert rc == 1, f"Expected exit 1 when history dir missing, got {rc}"
    print("PASS test_missing_history_dir_fails")


def test_paths_are_cwd_independent():
    module = _load_script()
    expected = (Path(module.__file__).resolve().parent.parent
                / "docs/health/dispositions.md")
    with tempfile.TemporaryDirectory() as tmp:
        cwd = os.getcwd()
        try:
            os.chdir(tmp)  # run from a non-repo directory
            assert module.DISPOSITIONS.is_absolute(), "DISPOSITIONS must be absolute"
            assert module.DISPOSITIONS == expected, (
                f"DISPOSITIONS resolved to {module.DISPOSITIONS}, expected {expected}"
            )
        finally:
            os.chdir(cwd)
    print("PASS test_paths_are_cwd_independent")


if __name__ == "__main__":
    test_report_mode_flags_missing_row()
    test_report_mode_passes_when_present()
    test_fix_mode_syncs_and_passes()
    test_non_fixed_rows_ignored()
    test_missing_history_dir_fails()
    test_paths_are_cwd_independent()
    print("\nAll tests passed")
