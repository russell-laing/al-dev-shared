#!/usr/bin/env python3
"""Thin CLI wrapper for generated map-document sections."""

from __future__ import annotations

from _entrypoint_bootstrap import bootstrap_repo

REPO_ROOT = bootstrap_repo(__file__)
from scripts.al_dev_tools.docs.map_doc_sections import (
    apply_document_updates,
    generate_document_updates,
)


def main() -> int:
    updates = generate_document_updates(REPO_ROOT)
    apply_document_updates(updates)
    print(f"Updated {len(updates)} map documents")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
