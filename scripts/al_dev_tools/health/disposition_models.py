"""Shared models and pure helpers for health disposition tooling."""

from __future__ import annotations

import re

TABLE_HEADER = (
    "| ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence / note |"
)
TABLE_DIVIDER = (
    "|----|---------|-----------|--------|---------|-------------|------|------------------|"
)

EVENT_REQUIRED_FIELDS = (
    "event_id",
    "surface",
    "dimension",
    "object",
    "finding",
    "disposition",
    "date",
    "closes_event_ids",
    "evidence",
    "source",
)
VALID_DISPOSITIONS = {"accepted", "declined", "fixed", "grandfathered"}
EVENT_ID_RE = re.compile(r"^disp_(\d{8})_(\d{6})$")


def normalize_finding(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _escape_cell(text: object) -> str:
    """Escape bare pipe characters in a Markdown table cell value."""
    return str(text).replace("|", r"\|")


def _unescape_cell(text: str) -> str:
    """Unescape \\| back to | when reading a Markdown table cell."""
    return text.replace(r"\|", "|")


def disposition_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        row["surface"].strip(),
        row["dimension"].strip(),
        row["object"].strip(),
        normalize_finding(row["finding"]),
    )
