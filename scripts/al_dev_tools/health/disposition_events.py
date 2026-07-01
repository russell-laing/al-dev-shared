"""JSONL event-store helpers for health finding dispositions."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict, OrderedDict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Iterator

from .disposition_models import (
    EVENT_ID_RE,
    EVENT_REQUIRED_FIELDS,
    VALID_DISPOSITIONS,
    disposition_key,
    normalize_finding,
)


def event_shard_path_for_date(iso_date: str) -> Path:
    year, month, _ = iso_date.split("-")
    return Path(year) / f"{year}-{month}.jsonl"


def next_event_id(events: list[dict[str, object]], iso_date: str) -> str:
    date_token = iso_date.replace("-", "")
    max_seq = 0
    for event in events:
        raw = str(event.get("event_id", ""))
        match = EVENT_ID_RE.match(raw)
        if not match or match.group(1) != date_token:
            continue
        max_seq = max(max_seq, int(match.group(2)))
    return f"disp_{date_token}_{max_seq + 1:06d}"


def validate_event(event: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for field in EVENT_REQUIRED_FIELDS:
        if field not in event:
            errors.append(f"{field} is required")
    if not str(event.get("event_id", "")).strip():
        errors.append("event_id is required")
    if str(event.get("disposition", "")).strip().lower() not in VALID_DISPOSITIONS:
        errors.append("disposition must be one of accepted, declined, fixed, grandfathered")
    closes = event.get("closes_event_ids", [])
    if not isinstance(closes, list) or not all(isinstance(v, str) for v in closes):
        errors.append("closes_event_ids must be a list of strings")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(event.get("date", ""))):
        errors.append("date must be YYYY-MM-DD")
    return errors


def parse_event_file(path: Path) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    if not path.exists():
        return events
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno}: invalid JSONL: {exc}") from exc
        if not isinstance(event, dict):
            raise ValueError(f"{path}:{lineno}: event must be a JSON object")
        errors = validate_event(event)
        if errors:
            raise ValueError(f"{path}:{lineno}: " + "; ".join(errors))
        event["disposition"] = str(event["disposition"]).lower()
        events.append(event)
    return events


def iter_event_rows(events_root: Path) -> Iterator[dict[str, object]]:
    for shard in sorted(events_root.rglob("*.jsonl")):
        yield from parse_event_file(shard)


def append_event(events_root: Path, event: dict[str, object]) -> Path:
    errors = validate_event(event)
    if errors:
        raise ValueError("; ".join(errors))
    event_id = str(event["event_id"])
    existing_ids = {
        str(existing["event_id"])
        for existing in iter_event_rows(events_root)
        if existing.get("event_id")
    }
    if event_id in existing_ids:
        raise ValueError(f"duplicate event_id: {event_id}")
    shard = events_root / event_shard_path_for_date(str(event["date"]))
    shard.parent.mkdir(parents=True, exist_ok=True)
    with shard.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return shard


def batch_decline(
    events_root: Path,
    rows: list[dict[str, str]],
    date: str,
    source: str = "plan-plugin-findings",
) -> list[tuple[str, Path]]:
    required = ("surface", "dimension", "object", "finding", "reason", "closes_event_id")
    written: list[tuple[str, Path]] = []
    for i, row in enumerate(rows):
        missing = [k for k in required if not str(row.get(k, "")).strip()]
        if missing:
            raise ValueError(f"row {i}: missing required field(s): {', '.join(missing)}")
        event_id = next_event_id(list(iter_event_rows(events_root)), date)
        event = {
            "event_id": event_id,
            "legacy_id": "",
            "surface": row["surface"],
            "dimension": row["dimension"],
            "object": row["object"],
            "finding": row["finding"],
            "disposition": "declined",
            "date": date,
            "closes_event_ids": [row["closes_event_id"]],
            "evidence": f"declined: rubber-duck refuted — {row['reason']}",
            "source": source,
        }
        shard = append_event(events_root, event)
        written.append((event_id, shard))
    return written


def _event_key(event: dict[str, object]) -> tuple[str, str, str, str]:
    return (
        str(event["surface"]).strip(),
        str(event["dimension"]).strip(),
        str(event["object"]).strip(),
        normalize_finding(str(event["finding"])),
    )


def materialize_current_events(events: list[dict[str, object]]) -> list[dict[str, object]]:
    by_id = {str(event["event_id"]): event for event in events}
    closed_ids: set[str] = set()
    for event in events:
        for closed_id in event.get("closes_event_ids", []):
            if closed_id not in by_id:
                raise ValueError(f"unknown closes_event_ids value: {closed_id}")
            closed_ids.add(str(closed_id))

    open_accepted: list[dict[str, object]] = []
    by_legacy_id: dict[str, dict[str, object]] = {}
    for event in events:
        event_id = str(event["event_id"])
        if event_id in closed_ids:
            continue
        legacy_id = str(event.get("legacy_id", "")).strip()
        if str(event["disposition"]) == "accepted":
            open_accepted.append(event)
            if legacy_id:
                by_legacy_id[legacy_id] = event
            continue
        if str(event["disposition"]) in ("declined", "grandfathered") and legacy_id:
            target = by_legacy_id.get(legacy_id)
            if target:
                closed_ids.add(str(target["event_id"]))
                open_accepted = [
                    e for e in open_accepted if str(e["event_id"]) != str(target["event_id"])
                ]
                by_legacy_id.pop(legacy_id, None)
                continue
        if str(event["disposition"]) in ("declined", "grandfathered") and not event.get(
            "closes_event_ids"
        ):
            for accepted in list(open_accepted):
                if str(accepted["object"]).strip() == str(event["object"]).strip():
                    closed_ids.add(str(accepted["event_id"]))
                    open_accepted.remove(accepted)
                    break

    latest: OrderedDict[tuple[str, str, str, str], dict[str, object]] = OrderedDict()
    for event in events:
        if str(event["event_id"]) not in closed_ids:
            latest[_event_key(event)] = event
    return list(latest.values())


def _source_hash(events: list[dict[str, object]]) -> str:
    payload = "\n".join(json.dumps(e, ensure_ascii=False, sort_keys=True) for e in events)
    return sha256(payload.encode("utf-8")).hexdigest()


def build_disposition_index(
    events: list[dict[str, object]], *, source_hash: str | None = None
) -> dict[str, object]:
    current = materialize_current_events(events)
    by_disposition = Counter(str(e["disposition"]) for e in current)
    by_surface: dict[str, dict[str, int]] = defaultdict(
        lambda: {"current_rows": 0, "open_accepted": 0}
    )
    by_dimension: dict[str, dict[str, int]] = defaultdict(
        lambda: {"current_rows": 0, "open_accepted": 0}
    )
    for event in current:
        surface = str(event["surface"])
        dimension = str(event["dimension"])
        by_surface[surface]["current_rows"] += 1
        by_dimension[dimension]["current_rows"] += 1
        if event["disposition"] == "accepted":
            by_surface[surface]["open_accepted"] += 1
            by_dimension[dimension]["open_accepted"] += 1
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_hash": source_hash or _source_hash(events),
        "total_events": len(events),
        "current_rows": len(current),
        "open_accepted": by_disposition.get("accepted", 0),
        "integrity_warnings": 0,
        "by_disposition": dict(sorted(by_disposition.items())),
        "by_surface": dict(sorted(by_surface.items())),
        "by_dimension": dict(sorted(by_dimension.items())),
    }


def validate_index_freshness(index: dict[str, object], events: list[dict[str, object]]) -> list[str]:
    errors: list[str] = []
    if index.get("source_hash") != _source_hash(events):
        errors.append("source_hash is stale")
    if index.get("total_events") != len(events):
        errors.append("total_events is stale")
    if index.get("open_accepted") != build_disposition_index(events)["open_accepted"]:
        errors.append("open_accepted is stale")
    return errors
