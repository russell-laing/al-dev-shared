"""Tests for JSONL-backed health disposition store behavior."""

from __future__ import annotations

import importlib.util
import json
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


class EventIdTest(unittest.TestCase):
    def test_next_event_id_uses_existing_max_sequence_for_date(self) -> None:
        rows = [
            {"event_id": "disp_20260619_000001", "date": "2026-06-19"},
            {"event_id": "disp_20260619_000003", "date": "2026-06-19"},
            {"event_id": "disp_20260618_000099", "date": "2026-06-18"},
        ]

        self.assertEqual(
            "disp_20260619_000004",
            STORE.next_event_id(rows, "2026-06-19"),
        )


class JsonlPathTest(unittest.TestCase):
    def test_event_shard_path_uses_year_and_month(self) -> None:
        self.assertEqual(
            Path("2026") / "2026-06.jsonl",
            STORE.event_shard_path_for_date("2026-06-19"),
        )


class JsonlAppendTest(unittest.TestCase):
    def test_append_event_writes_one_json_object_per_line(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "docs" / "health" / "dispositions-events"
            event = {
                "event_id": "disp_20260619_000001",
                "legacy_id": "#976",
                "surface": "tooling",
                "dimension": "quality",
                "object": "validate_health_loop_state.py",
                "finding": "Validator stage enum omits revise-plugin-plan.",
                "disposition": "accepted",
                "date": "2026-06-19",
                "closes_event_ids": [],
                "evidence": "queued",
                "source": "test",
            }

            shard = STORE.append_event(root, event)

            self.assertEqual(root / "2026" / "2026-06.jsonl", shard)
            loaded = [json.loads(line) for line in shard.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([event], loaded)

    def test_append_event_rejects_duplicate_event_id(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "events"
            event = {
                "event_id": "disp_20260619_000001",
                "surface": "tooling",
                "dimension": "quality",
                "object": "obj",
                "finding": "finding",
                "disposition": "accepted",
                "date": "2026-06-19",
                "closes_event_ids": [],
                "evidence": "queued",
                "source": "test",
            }

            STORE.append_event(root, event)
            with self.assertRaisesRegex(ValueError, "duplicate event_id"):
                STORE.append_event(root, event)


class JsonlValidationTest(unittest.TestCase):
    def test_validate_event_requires_event_id_and_known_disposition(self) -> None:
        event = {
            "event_id": "",
            "surface": "tooling",
            "dimension": "quality",
            "object": "obj",
            "finding": "finding",
            "disposition": "maybe",
            "date": "2026-06-19",
            "closes_event_ids": [],
            "evidence": "evidence",
            "source": "test",
        }

        errors = STORE.validate_event(event)

        self.assertIn("event_id is required", errors)
        self.assertIn("disposition must be one of accepted, declined, fixed, grandfathered", errors)


class JsonlCurrentStateTest(unittest.TestCase):
    def test_materialize_current_events_closes_accepted_event_by_event_id(self) -> None:
        events = [
            {
                "event_id": "disp_20260619_000001",
                "legacy_id": "#976",
                "surface": "tooling",
                "dimension": "quality",
                "object": "validate_health_loop_state.py",
                "finding": "Validator stage enum omits revise-plugin-plan.",
                "disposition": "accepted",
                "date": "2026-06-19",
                "closes_event_ids": [],
                "evidence": "queued",
                "source": "test",
            },
            {
                "event_id": "disp_20260619_000002",
                "legacy_id": "#976",
                "surface": "tooling",
                "dimension": "quality",
                "object": "validate_health_loop_state.py",
                "finding": "Validator stage enum omits revise-plugin-plan.",
                "disposition": "fixed",
                "date": "2026-06-19",
                "closes_event_ids": ["disp_20260619_000001"],
                "evidence": "8f3c205 verified live",
                "source": "test",
            },
        ]

        current = STORE.materialize_current_events(events)

        self.assertEqual(1, len(current))
        self.assertEqual("disp_20260619_000002", current[0]["event_id"])
        self.assertEqual("fixed", current[0]["disposition"])

    def test_declined_same_legacy_id_closes_accepted_event_without_explicit_closes(self) -> None:
        events = [
            {
                "event_id": "disp_20260619_000001",
                "legacy_id": "#596",
                "surface": "tooling",
                "dimension": "quality",
                "object": "fix-knowledge-quality",
                "finding": "Original accepted finding.",
                "disposition": "accepted",
                "date": "2026-06-19",
                "closes_event_ids": [],
                "evidence": "queued",
                "source": "test",
            },
            {
                "event_id": "disp_20260619_000002",
                "legacy_id": "#596",
                "surface": "tooling",
                "dimension": "quality",
                "object": "fix-knowledge-quality",
                "finding": "Later declined wording.",
                "disposition": "declined",
                "date": "2026-06-19",
                "closes_event_ids": [],
                "evidence": "superseded",
                "source": "test",
            },
        ]

        current = STORE.materialize_current_events(events)

        self.assertEqual(["disp_20260619_000002"], [e["event_id"] for e in current])

    def test_grandfathered_same_object_closes_earliest_open_accepted_event(self) -> None:
        events = [
            {
                "event_id": "disp_20260619_000001",
                "surface": "tooling",
                "dimension": "quality",
                "object": "report-plugin-health",
                "finding": "Original accepted finding.",
                "disposition": "accepted",
                "date": "2026-06-19",
                "closes_event_ids": [],
                "evidence": "queued",
                "source": "test",
            },
            {
                "event_id": "disp_20260619_000002",
                "surface": "tooling",
                "dimension": "quality",
                "object": "report-plugin-health",
                "finding": "Different grandfathered wording.",
                "disposition": "grandfathered",
                "date": "2026-06-19",
                "closes_event_ids": [],
                "evidence": "accepted risk",
                "source": "test",
            },
        ]

        current = STORE.materialize_current_events(events)

        self.assertEqual(["disp_20260619_000002"], [e["event_id"] for e in current])


class JsonlIndexTest(unittest.TestCase):
    def test_build_disposition_index_counts_open_and_by_surface(self) -> None:
        events = [
            {
                "event_id": "disp_20260619_000001",
                "surface": "tooling",
                "dimension": "quality",
                "object": "a",
                "finding": "one",
                "disposition": "accepted",
                "date": "2026-06-19",
                "closes_event_ids": [],
                "evidence": "queued",
                "source": "test",
            },
            {
                "event_id": "disp_20260619_000002",
                "surface": "plugin",
                "dimension": "design",
                "object": "b",
                "finding": "two",
                "disposition": "declined",
                "date": "2026-06-19",
                "closes_event_ids": [],
                "evidence": "not worth doing",
                "source": "test",
            },
        ]

        index = STORE.build_disposition_index(events, source_hash="abc123")

        self.assertEqual(2, index["total_events"])
        self.assertEqual(2, index["current_rows"])
        self.assertEqual(1, index["open_accepted"])
        self.assertEqual(0, index["integrity_warnings"])
        self.assertEqual(1, index["by_surface"]["tooling"]["open_accepted"])
        self.assertEqual("abc123", index["source_hash"])


class JsonlFreshnessTest(unittest.TestCase):
    def test_validate_index_freshness_detects_stale_source_hash(self) -> None:
        events = [
            {
                "event_id": "disp_20260619_000001",
                "surface": "tooling",
                "dimension": "quality",
                "object": "a",
                "finding": "one",
                "disposition": "accepted",
                "date": "2026-06-19",
                "closes_event_ids": [],
                "evidence": "queued",
                "source": "test",
            }
        ]
        index = STORE.build_disposition_index(events, source_hash="stale")

        errors = STORE.validate_index_freshness(index, events)

        self.assertEqual(["source_hash is stale"], errors)


class JsonlRenderTest(unittest.TestCase):
    def test_render_open_view_writes_only_open_accepted_events(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "docs" / "health" / "dispositions-open.md"
            events = [
                {
                    "event_id": "disp_20260619_000001",
                    "surface": "tooling",
                    "dimension": "quality",
                    "object": "a",
                    "finding": "one",
                    "disposition": "accepted",
                    "date": "2026-06-19",
                    "closes_event_ids": [],
                    "evidence": "queued",
                    "source": "test",
                },
                {
                    "event_id": "disp_20260619_000002",
                    "surface": "plugin",
                    "dimension": "design",
                    "object": "b",
                    "finding": "two",
                    "disposition": "declined",
                    "date": "2026-06-19",
                    "closes_event_ids": [],
                    "evidence": "not worth doing",
                    "source": "test",
                },
            ]

            STORE.render_open_view(output, events)

            text = output.read_text(encoding="utf-8")
            self.assertIn("disp_20260619_000001", text)
            self.assertNotIn("disp_20260619_000002", text)

    def test_legacy_compatibility_view_uses_existing_eight_column_schema(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "docs" / "health" / "dispositions.md"
            events = [
                {
                    "event_id": "disp_20260619_000001",
                    "legacy_id": "#976",
                    "surface": "tooling",
                    "dimension": "quality",
                    "object": "obj",
                    "finding": "issue",
                    "disposition": "accepted",
                    "date": "2026-06-19",
                    "closes_event_ids": [],
                    "evidence": "queued",
                    "source": "test",
                }
            ]

            STORE.render_legacy_compatibility_view(output, events)

            text = output.read_text(encoding="utf-8")
            self.assertIn("| ID | Surface | Dimension | Object | Finding | Disposition | Date | Note |", text)
            self.assertNotIn("| Event ID |", text)
            parsed = STORE.parse_ledger_file(output)
            self.assertEqual("#976", parsed[0]["id"])
            self.assertEqual("tooling", parsed[0]["surface"])


class JsonlCliTest(unittest.TestCase):
    def test_cli_append_event_and_regenerate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            events_root = root / "docs" / "health" / "dispositions-events"
            open_view = root / "docs" / "health" / "dispositions-open.md"
            current_view = root / "docs" / "health" / "dispositions-current.md"
            index = root / "docs" / "health" / "dispositions-index.json"

            event = {
                "event_id": "disp_20260619_000001",
                "surface": "tooling",
                "dimension": "quality",
                "object": "obj",
                "finding": "issue",
                "disposition": "accepted",
                "date": "2026-06-19",
                "closes_event_ids": [],
                "evidence": "queued",
                "source": "test",
            }
            STORE.append_event(events_root, event)
            events = list(STORE.iter_event_rows(events_root))
            STORE.render_open_view(open_view, events)
            STORE.render_current_events_view(current_view, events)
            STORE.render_index(index, events)

            self.assertTrue(open_view.exists())
            self.assertTrue(current_view.exists())
            self.assertTrue(index.exists())


if __name__ == "__main__":
    unittest.main()
