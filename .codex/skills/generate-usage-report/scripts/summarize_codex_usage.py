#!/usr/bin/env python3
import argparse
import json
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def load_history(history_path: Path) -> tuple[int, int, str | None, str | None]:
    session_ids: set[str] = set()
    message_count = 0
    first_ts = None
    last_ts = None

    if not history_path.exists():
        return 0, 0, None, None

    with history_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            message_count += 1
            session_id = record.get("session_id")
            if session_id:
                session_ids.add(session_id)
            ts = record.get("ts")
            if isinstance(ts, int):
                if first_ts is None or ts < first_ts:
                    first_ts = ts
                if last_ts is None or ts > last_ts:
                    last_ts = ts

    return len(session_ids), message_count, format_ts(first_ts), format_ts(last_ts)


def load_thread_summary(state_path: Path) -> tuple[int, Counter, Counter, Counter]:
    if not state_path.exists():
        raise FileNotFoundError(f"Codex state database not found: {state_path}")

    connection = sqlite3.connect(state_path)
    try:
        required_columns = {"source", "model_provider", "cwd", "archived"}
        table_columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(threads)").fetchall()
        }
        missing_columns = sorted(required_columns - table_columns)
        if missing_columns:
            missing_list = ", ".join(missing_columns)
            raise RuntimeError(
                "Codex state database is missing required threads columns: "
                f"{missing_list}"
            )
        rows = connection.execute(
            """
            SELECT source, model_provider, COALESCE(cwd, '')
            FROM threads
            WHERE archived = 0 OR archived IS NULL
            """
        ).fetchall()
    finally:
        connection.close()

    source_counts: Counter[str] = Counter()
    provider_counts: Counter[str] = Counter()
    cwd_counts: Counter[str] = Counter()

    for source, provider, cwd in rows:
        source_counts[source or "unknown"] += 1
        provider_counts[provider or "unknown"] += 1
        cwd_counts[cwd or "(none)"] += 1

    return len(rows), source_counts, provider_counts, cwd_counts


def format_ts(ts: int | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def format_source(source: str | None) -> str:
    if not source:
        return "unknown"

    stripped = source.strip()
    if stripped.startswith("{"):
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            pass
        else:
            subagent = parsed.get("subagent", {})
            if isinstance(subagent, str):
                return f"subagent:{subagent}"
            if not isinstance(subagent, dict):
                return stripped

            thread_spawn = subagent.get("thread_spawn", {})
            if not isinstance(thread_spawn, dict):
                return "subagent"

            nickname = thread_spawn.get("agent_nickname")
            role = thread_spawn.get("agent_role")
            if nickname and role:
                return f"subagent:{nickname}/{role}"
            if nickname:
                return f"subagent:{nickname}"
            if role:
                return f"subagent:{role}"
            if thread_spawn:
                return "subagent"

    if len(stripped) <= 80:
        return stripped
    return f"{stripped[:77]}..."


def top_items(counter: Counter, limit: int = 3) -> list[str]:
    return [f"{name} ({count})" for name, count in counter.most_common(limit)]


def render_markdown(
    history_sessions: int,
    history_messages: int,
    first_seen: str | None,
    last_seen: str | None,
    thread_count: int,
    source_counts: Counter,
    provider_counts: Counter,
    cwd_counts: Counter,
) -> str:
    lines: list[str] = []
    lines.append("## Codex Observations")
    lines.append("")
    lines.append("These observations are derived from local Codex history/state data rather than a built-in Codex Insights report.")
    lines.append("")
    lines.append("### Available Local Data")
    lines.append("")
    lines.append(f"- History sessions seen: `{history_sessions}`")
    lines.append(f"- History messages seen: `{history_messages}`")
    lines.append(f"- Active thread rows seen: `{thread_count}`")
    if first_seen:
        lines.append(f"- First history timestamp seen: `{first_seen}`")
    if last_seen:
        lines.append(f"- Last history timestamp seen: `{last_seen}`")
    lines.append("")
    lines.append("### Pattern Hints")
    lines.append("")
    if source_counts:
        normalized_sources = Counter()
        for source, count in source_counts.items():
            normalized_sources[format_source(source)] += count
        lines.append(f"- Top thread sources: {', '.join(top_items(normalized_sources))}")
    if provider_counts:
        lines.append(f"- Top model providers: {', '.join(top_items(provider_counts))}")
    if cwd_counts:
        lines.append(f"- Top working directories: {', '.join(top_items(cwd_counts))}")
    if not source_counts and not provider_counts and not cwd_counts:
        lines.append("- Local state data was too sparse to identify stable usage patterns.")
    lines.append("")
    lines.append("### Interpretation Limits")
    lines.append("")
    lines.append("- This section is inferential and based only on locally readable Codex history/state artifacts.")
    lines.append("- It does not include a built-in Codex sentiment, friction, or recommendation engine.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize local Codex usage artifacts as markdown.")
    parser.add_argument("--history", type=Path, required=True, help="Path to Codex history.jsonl")
    parser.add_argument("--state", type=Path, required=True, help="Path to Codex state_5.sqlite")
    args = parser.parse_args()

    try:
        history_sessions, history_messages, first_seen, last_seen = load_history(args.history)
        thread_count, source_counts, provider_counts, cwd_counts = load_thread_summary(args.state)
    except (FileNotFoundError, RuntimeError, sqlite3.Error, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(
        render_markdown(
            history_sessions,
            history_messages,
            first_seen,
            last_seen,
            thread_count,
            source_counts,
            provider_counts,
            cwd_counts,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
