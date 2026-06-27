"""Generated-section marker scanning and replacement helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Match, Optional
import re

from .map_inventory import MarkerSpan


BEGIN_RE = re.compile(r"<!-- BEGIN GENERATED: ([a-z0-9-]+) -->")
END_RE = re.compile(r"<!-- END GENERATED: ([a-z0-9-]+) -->")


@dataclass(frozen=True)
class _OpenMarker:
    key: str
    begin_start: int
    begin_end: int


def find_marker_spans(text: str) -> dict[str, MarkerSpan]:
    """Find validated generated-section spans in document text."""
    events: list[tuple[int, str, str, Match[str]]] = []
    for match in BEGIN_RE.finditer(text):
        events.append((match.start(), "begin", match.group(1), match))
    for match in END_RE.finditer(text):
        events.append((match.start(), "end", match.group(1), match))
    events.sort(key=lambda item: (item[0], 0 if item[1] == "begin" else 1))

    spans: dict[str, MarkerSpan] = {}
    open_marker: Optional[_OpenMarker] = None

    for _pos, kind, key, match in events:
        if kind == "begin":
            if key in spans or (open_marker is not None and open_marker.key == key):
                raise ValueError(f"duplicate marker key: {key}")
            if open_marker is not None:
                raise ValueError(f"overlapping marker spans: {open_marker.key} and {key}")
            open_marker = _OpenMarker(key=key, begin_start=match.start(), begin_end=match.end())
            continue

        if open_marker is None:
            raise ValueError(f"end marker without matching begin marker: {key}")
        if open_marker.key != key:
            raise ValueError(f"mismatched marker keys: begin {open_marker.key}, end {key}")

        spans[key] = MarkerSpan(
            key=key,
            start=open_marker.begin_start,
            end=match.end(),
            begin_start=open_marker.begin_start,
            begin_end=open_marker.begin_end,
            end_start=match.start(),
            end_end=match.end(),
        )
        open_marker = None

    if open_marker is not None:
        raise ValueError(f"begin marker without matching end marker: {open_marker.key}")

    return spans


def replace_marked_sections(text: str, replacements: dict[str, str]) -> str:
    spans = find_marker_spans(text)
    unknown = set(replacements) - set(spans)
    if unknown:
        raise KeyError(f"unknown section keys: {sorted(unknown)}")

    output = text
    for key, span in reversed(sorted(spans.items(), key=lambda item: item[1].start)):
        if key not in replacements:
            continue
        output = output[:span.start] + replacements[key] + output[span.end:]
    return output


__all__ = ["MarkerSpan", "find_marker_spans", "replace_marked_sections"]
