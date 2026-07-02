from __future__ import annotations

from pathlib import Path

import yaml


_CANONICAL = (
    "companion-codex-al-dev",
    "companion-claude-al-dev",
    "companion-copilot-al-dev",
)


def canonical_companion_surfaces() -> tuple[str, ...]:
    return _CANONICAL


def legacy_surface_aliases() -> dict[str, tuple[str, ...]]:
    return {
        "both": ("plugin", "tooling"),
        "companions": _CANONICAL,
        "everything": ("plugin", "tooling", *_CANONICAL),
    }


def surface_root_map(repo_root: Path) -> dict[str, Path]:
    return {
        "plugin": repo_root / "profile-al-dev-shared",
        "tooling": repo_root / ".claude",
        "companion-codex-al-dev": repo_root / "companions/codex/al-dev",
        "companion-claude-al-dev": repo_root / "companions/claude/al-dev",
        "companion-copilot-al-dev": repo_root / "companions/copilot/al-dev",
    }


def load_companion_inventory(repo_root: Path) -> dict:
    import os

    inventory_path = repo_root / "companions/companion-packages.yaml"
    data = yaml.safe_load(inventory_path.read_text(encoding="utf-8"))
    harness_home = os.environ.get("AL_DEV_HARNESS_HOME", str(Path.home()))
    for entry in data.get("packages", []):
        for key in ("current_root", "current_registry"):
            if key in entry:
                entry[key] = entry[key].replace("${AL_DEV_HARNESS_HOME}", harness_home)
    return data
