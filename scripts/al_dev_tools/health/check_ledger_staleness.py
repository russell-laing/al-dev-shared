#!/usr/bin/env python3
"""Compatibility facade for the ledger staleness checker."""

from __future__ import annotations

from .ledger_cli import main
from .ledger_models import LEDGER, Row, dict_to_row, parse_ledger, parse_ledger_text
from .ledger_queries import (
    candidate_paths,
    commits_since,
    integrity_warnings,
    load_rows_from_store,
    norm_object,
    resolve_closures,
    staged_files,
)

__all__ = [
    "LEDGER",
    "Row",
    "candidate_paths",
    "commits_since",
    "dict_to_row",
    "integrity_warnings",
    "load_rows_from_store",
    "main",
    "norm_object",
    "parse_ledger",
    "parse_ledger_text",
    "resolve_closures",
    "staged_files",
]


if __name__ == "__main__":
    raise SystemExit(main())
