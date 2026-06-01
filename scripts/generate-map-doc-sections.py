#!/usr/bin/env python3
"""Thin CLI wrapper for generated map-document sections."""

from __future__ import annotations

from pathlib import Path
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from map_doc_sections import apply_document_updates, generate_document_updates


def main() -> int:
    repo = SCRIPT_DIR.parent
    updates = generate_document_updates(repo)
    apply_document_updates(updates)
    print(f"Updated {len(updates)} map documents")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"generate-map-doc-sections: {exc}\n")
        raise SystemExit(1) from exc
