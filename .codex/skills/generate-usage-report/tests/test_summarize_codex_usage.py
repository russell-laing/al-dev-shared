from __future__ import annotations

import importlib.util
import sqlite3
import tempfile
import unittest
from collections import Counter
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "summarize_codex_usage.py"
)
MODULE_SPEC = importlib.util.spec_from_file_location(
    "summarize_codex_usage", MODULE_PATH
)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
summarize_codex_usage = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(summarize_codex_usage)


class FormatSourceTest(unittest.TestCase):
    def test_collapses_thread_spawn_subagent_json(self) -> None:
        raw = (
            '{"subagent":{"thread_spawn":{'
            '"agent_nickname":"Feynman","agent_role":"worker"}}}'
        )
        self.assertEqual(summarize_codex_usage.format_source(raw), "subagent:Feynman/worker")

    def test_truncates_long_plain_sources(self) -> None:
        self.assertEqual(
            summarize_codex_usage.format_source("x" * 81),
            f"{'x' * 77}...",
        )


class LoadThreadSummaryTest(unittest.TestCase):
    def test_rejects_missing_state_database(self) -> None:
        with self.assertRaises(FileNotFoundError):
            summarize_codex_usage.load_thread_summary(Path("/tmp/does-not-exist.sqlite"))

    def test_rejects_missing_threads_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.sqlite"
            connection = sqlite3.connect(state_path)
            try:
                connection.execute(
                    "CREATE TABLE threads (source TEXT, model_provider TEXT, cwd TEXT)"
                )
                connection.commit()
            finally:
                connection.close()

            with self.assertRaisesRegex(RuntimeError, "missing required threads columns"):
                summarize_codex_usage.load_thread_summary(state_path)

    def test_reads_active_threads(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.sqlite"
            connection = sqlite3.connect(state_path)
            try:
                connection.execute(
                    """
                    CREATE TABLE threads (
                        source TEXT,
                        model_provider TEXT,
                        cwd TEXT,
                        archived INTEGER
                    )
                    """
                )
                connection.executemany(
                    "INSERT INTO threads VALUES (?, ?, ?, ?)",
                    [
                        (
                            '{"subagent":{"thread_spawn":{'
                            '"agent_nickname":"Feynman","agent_role":"worker"}}}',
                            "openai",
                            "/tmp/work",
                            0,
                        ),
                        ("cli", "openai", "/tmp/work", None),
                        ("archived", "openai", "/tmp/skip", 1),
                    ],
                )
                connection.commit()
            finally:
                connection.close()

            thread_count, source_counts, provider_counts, cwd_counts = (
                summarize_codex_usage.load_thread_summary(state_path)
            )

            self.assertEqual(thread_count, 2)
            self.assertEqual(source_counts["cli"], 1)
            self.assertEqual(
                source_counts[
                    '{"subagent":{"thread_spawn":{"agent_nickname":"Feynman","agent_role":"worker"}}}'
                ],
                1,
            )
            self.assertEqual(provider_counts["openai"], 2)
            self.assertEqual(cwd_counts["/tmp/work"], 2)


class LoadHistoryTest(unittest.TestCase):
    def test_reads_sample_history_fixture(self) -> None:
        fixture_path = Path(__file__).resolve().parent / "fixtures" / "codex-history-sample.jsonl"

        session_count, message_count, first_seen, last_seen = summarize_codex_usage.load_history(
            fixture_path
        )

        self.assertEqual(session_count, 2)
        self.assertEqual(message_count, 3)
        self.assertEqual(first_seen, "2026-05-15 09:08:17Z")
        self.assertEqual(last_seen, "2026-05-15 10:13:20Z")


class RenderMarkdownTest(unittest.TestCase):
    def test_normalizes_and_aggregates_source_labels(self) -> None:
        raw_sources = Counter(
            {
                '{"subagent":{"thread_spawn":{'
                '"agent_nickname":"Feynman","agent_role":"worker","depth":1}}}': 1,
                '{"subagent":{"thread_spawn":{'
                '"agent_nickname":"Feynman","agent_role":"worker","depth":2}}}': 2,
                "cli": 3,
            }
        )

        rendered = summarize_codex_usage.render_markdown(
            history_sessions=1,
            history_messages=1,
            first_seen=None,
            last_seen=None,
            thread_count=3,
            source_counts=raw_sources,
            provider_counts=Counter(),
            cwd_counts=Counter(),
        )

        self.assertIn("cli (3)", rendered)
        self.assertIn("subagent:Feynman/worker (3)", rendered)
        self.assertEqual(rendered.count("subagent:Feynman/worker (3)"), 1)


if __name__ == "__main__":
    unittest.main()
