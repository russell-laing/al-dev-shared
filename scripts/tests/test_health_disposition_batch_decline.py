"""Tests for the batch_decline helper and CLI in health_disposition_store.py."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
STORE_PATH = REPO_ROOT / "scripts" / "health_disposition_store.py"
SPEC = importlib.util.spec_from_file_location("health_disposition_store", STORE_PATH)
assert SPEC is not None and SPEC.loader is not None
STORE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = STORE
SPEC.loader.exec_module(STORE)


def _seed_accepted(events_root: Path, event_id: str, obj: str) -> None:
    """Write one accepted event so a declined event has something to close."""
    STORE.append_event(events_root, {
        "event_id": event_id,
        "legacy_id": "",
        "surface": "plugin",
        "dimension": "quality",
        "object": obj,
        "finding": f"Structure: {obj} issue",
        "disposition": "accepted",
        "date": "2026-06-26",
        "closes_event_ids": [],
        "evidence": "accepted",
        "source": "record-plugin-dispositions",
    })


class BatchDeclineHelperTest(unittest.TestCase):
    def test_appends_one_declined_event_per_row_with_closes_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "events"
            _seed_accepted(root, "disp_20260626_000001", "al-dev-foo")
            _seed_accepted(root, "disp_20260626_000002", "al-dev-bar")
            rows = [
                {"surface": "plugin", "dimension": "quality", "object": "al-dev-foo",
                 "finding": "Structure: al-dev-foo issue", "reason": "already covered",
                 "closes_event_id": "disp_20260626_000001"},
                {"surface": "plugin", "dimension": "quality", "object": "al-dev-bar",
                 "finding": "Structure: al-dev-bar issue", "reason": "refuted on read",
                 "closes_event_id": "disp_20260626_000002"},
            ]
            written = STORE.batch_decline(root, rows, "2026-06-26")
            self.assertEqual(2, len(written))
            declined = [e for e in STORE.iter_event_rows(root)
                        if e["disposition"] == "declined"]
            self.assertEqual(2, len(declined))
            by_obj = {e["object"]: e for e in declined}
            self.assertEqual(["disp_20260626_000001"],
                             by_obj["al-dev-foo"]["closes_event_ids"])
            self.assertTrue(by_obj["al-dev-foo"]["evidence"].startswith(
                "declined: rubber-duck refuted — "))
            self.assertIn("already covered", by_obj["al-dev-foo"]["evidence"])
            # fresh sequential ids — never reuse a closed accepted id
            self.assertNotIn(by_obj["al-dev-foo"]["event_id"],
                             {"disp_20260626_000001", "disp_20260626_000002"})
            self.assertNotEqual(by_obj["al-dev-foo"]["event_id"],
                                by_obj["al-dev-bar"]["event_id"])

    def test_missing_required_field_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "events"
            rows = [{"surface": "plugin", "dimension": "quality", "object": "x",
                     "finding": "f", "reason": "r"}]  # no closes_event_id
            with self.assertRaises(ValueError):
                STORE.batch_decline(root, rows, "2026-06-26")

    def test_empty_input_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "events"
            self.assertEqual([], STORE.batch_decline(root, [], "2026-06-26"))


class BatchDeclineCliTest(unittest.TestCase):
    def test_cli_writes_declined_events_from_json_input(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "events"
            _seed_accepted(root, "disp_20260626_000001", "al-dev-foo")
            input_path = Path(d) / "declines.json"
            input_path.write_text(json.dumps([
                {"surface": "plugin", "dimension": "quality", "object": "al-dev-foo",
                 "finding": "Structure: al-dev-foo issue", "reason": "already covered",
                 "closes_event_id": "disp_20260626_000001"},
            ]), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(STORE_PATH), "batch_decline",
                 "--input", str(input_path), "--date", "2026-06-26",
                 "--events-root", str(root)],
                capture_output=True, text=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("wrote 1 declined event", result.stdout)
            declined = [e for e in STORE.iter_event_rows(root)
                        if e["disposition"] == "declined"]
            self.assertEqual(1, len(declined))


if __name__ == "__main__":
    unittest.main()
