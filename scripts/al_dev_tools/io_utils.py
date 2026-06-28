"""Small reusable I/O helpers for repo-local generator scripts."""

from __future__ import annotations

from pathlib import Path
import tempfile


def write_text_atomic(path: Path, text: str) -> None:
    """Write text to ``path`` via a temp file in the same directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    try:
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


__all__ = ["write_text_atomic"]
