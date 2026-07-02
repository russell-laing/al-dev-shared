"""Small reusable I/O helpers for repo-local generator scripts."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile


def write_text_atomic(path: Path, text: str) -> None:
    """Write text to ``path`` via a temp file in the same directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        temp_path.replace(path)
    except Exception:
        if temp_path and temp_path.exists():
            temp_path.unlink()
        raise
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def write_json_atomic(path: Path, payload: object) -> None:
    write_text_atomic(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


__all__ = ["write_json_atomic", "write_text_atomic"]
