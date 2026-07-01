"""Behavioral tests for scripts/check_ledger_path_drift.py (read-only).

Verifies:
- healthy ledger layout -> exit 0
- missing generated view -> exit 1 (paths.py/on-disk drift)
- event store present but no .jsonl shard -> exit 1 (fork signature)
- no dispositions_events directory at all -> exit 0 (uninitialised, skip)
- the checker never writes any file
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check_ledger_path_drift.py"

_EVENT = (
    '{"event_id":"disp_20260619_000001","surface":"tooling","dimension":"quality",'
    '"object":"obj","finding":"issue","disposition":"accepted","date":"2026-06-19",'
    '"closes_event_ids":[],"evidence":"queued","source":"test"}'
)


def _load_script():
    spec = importlib.util.spec_from_file_location("check_ledger_path_drift", SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _healthy_root(base: Path) -> Path:
    """Build a minimal, healthy docs/health layout under ``base``."""
    health = base / "docs" / "health"
    events = health / "dispositions_events" / "2026"
    events.mkdir(parents=True, exist_ok=True)
    (events / "2026-06.jsonl").write_text(_EVENT + "\n", encoding="utf-8")
    (health / "dispositions_history").mkdir(parents=True, exist_ok=True)
    (health / "dispositions_open.md").write_text("open\n", encoding="utf-8")
    (health / "dispositions_current.md").write_text("current\n", encoding="utf-8")
    (health / "dispositions_index.json").write_text("{}\n", encoding="utf-8")
    (health / "dispositions.md").write_text("ledger\n", encoding="utf-8")
    return base


class CheckLedgerPathDriftTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load_script()

    def test_healthy_layout_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _healthy_root(Path(tmp))
            self.assertEqual(self.mod.run(root), 0)

    def test_missing_view_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _healthy_root(Path(tmp))
            (root / "docs" / "health" / "dispositions_open.md").unlink()
            self.assertEqual(self.mod.run(root), 1)

    def test_forked_empty_event_store_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _healthy_root(Path(tmp))
            # Simulate a fork: the events dir exists but the shard is gone.
            (root / "docs" / "health" / "dispositions_events" / "2026" / "2026-06.jsonl").unlink()
            self.assertEqual(self.mod.run(root), 1)

    def test_uninitialised_ledger_skips(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # No docs/health/dispositions_events at all.
            self.assertEqual(self.mod.run(Path(tmp)), 0)

    def test_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _healthy_root(Path(tmp))
            before = {p for p in (root / "docs" / "health").rglob("*")}
            self.mod.run(root)
            after = {p for p in (root / "docs" / "health").rglob("*")}
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
