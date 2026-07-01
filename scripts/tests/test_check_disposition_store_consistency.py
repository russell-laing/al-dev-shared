"""Behavioral tests for scripts/check_disposition_store_consistency.py (read-only).

Verifies:
- consistent store -> exit 0
- event with dangling closes_event_ids -> exit 1
- script never writes to dispositions-history
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check_disposition_store_consistency.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("check_disposition_store_consistency", SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _write_jsonl(events_dir: Path, lines: list[str]) -> None:
    events_dir.mkdir(parents=True, exist_ok=True)
    (events_dir / "2026-06.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")


_ACCEPTED_EVENT = (
    '{"event_id":"disp_20260619_000001","surface":"tooling","dimension":"quality",'
    '"object":"obj","finding":"issue","disposition":"accepted","date":"2026-06-19",'
    '"closes_event_ids":[],"evidence":"queued","source":"test"}'
)
_FIXED_EVENT = (
    '{"event_id":"disp_20260619_000002","surface":"tooling","dimension":"quality",'
    '"object":"obj","finding":"issue","disposition":"fixed","date":"2026-06-19",'
    '"closes_event_ids":["disp_20260619_000001"],"evidence":"fixed","source":"test"}'
)


class ConsistentStoreTest(unittest.TestCase):
    def test_consistent_store_exits_zero(self) -> None:
        mod = _load_script()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            events_dir = root / "2026"
            _write_jsonl(events_dir, [_ACCEPTED_EVENT, _FIXED_EVENT])
            rc = mod.run(root)
        self.assertEqual(0, rc)

    def test_empty_store_dir_exits_zero(self) -> None:
        """An events_root that exists but has no shards is consistent."""
        mod = _load_script()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rc = mod.run(root)
        self.assertEqual(0, rc)

    def test_absent_store_exits_zero(self) -> None:
        """No events directory is treated as nothing to check."""
        mod = _load_script()
        with tempfile.TemporaryDirectory() as d:
            rc = mod.run(Path(d) / "nonexistent")
        self.assertEqual(0, rc)

    def test_subprocess_root_override_uses_temporary_repo(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            events_dir = root / "docs" / "health" / "dispositions_events" / "2026"
            _write_jsonl(events_dir, [_ACCEPTED_EVENT, _FIXED_EVENT])
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("consistent", result.stdout)
            self.assertNotIn("RuntimeWarning", result.stderr, result.stderr)


class DanglingReferenceTest(unittest.TestCase):
    def test_dangling_closes_event_ids_exits_one(self) -> None:
        mod = _load_script()
        dangling = (
            '{"event_id":"disp_20260619_000002","surface":"tooling","dimension":"quality",'
            '"object":"obj","finding":"issue","disposition":"fixed","date":"2026-06-19",'
            '"closes_event_ids":["disp_20260619_NONEXISTENT"],"evidence":"fixed","source":"test"}'
        )
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            events_dir = root / "2026"
            _write_jsonl(events_dir, [_ACCEPTED_EVENT, dangling])
            rc = mod.run(root)
        self.assertEqual(1, rc)


class NoWriteTest(unittest.TestCase):
    def test_does_not_write_dispositions_history(self) -> None:
        """run() must never create files under dispositions-history."""
        mod = _load_script()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            events_dir = root / "2026"
            _write_jsonl(events_dir, [_ACCEPTED_EVENT, _FIXED_EVENT])
            history = root / "dispositions-history"
            mod.run(root)
            self.assertFalse(
                history.exists(),
                f"check_disposition_store_consistency.py wrote to {history} — must be read-only",
            )


class NoImportAppendRowTest(unittest.TestCase):
    def test_script_does_not_import_append_row(self) -> None:
        """The rewritten script must not import or call append_row."""
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn(
            "append_row",
            source,
            "check_disposition_store_consistency.py references append_row — it must be read-only",
        )


class PathsAbsoluteTest(unittest.TestCase):
    def test_events_root_is_absolute(self) -> None:
        mod = _load_script()
        self.assertTrue(
            mod.EVENTS_ROOT.is_absolute(),
            "EVENTS_ROOT must be an absolute path",
        )

    def test_events_root_cwd_independent(self) -> None:
        mod = _load_script()
        expected = REPO_ROOT / "docs" / "health" / "dispositions_events"
        cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                os.chdir(tmp)
                self.assertEqual(expected, mod.EVENTS_ROOT)
        finally:
            os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
