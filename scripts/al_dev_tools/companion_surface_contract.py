from __future__ import annotations

import os
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
    inventory_path = repo_root / "companions/companion-packages.yaml"
    try:
        content = inventory_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise ValueError(f"Cannot read companion inventory at {inventory_path}: {type(e).__name__}: {e}") from e
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise ValueError(f"Malformed YAML in {inventory_path}: {e}") from e
    if not isinstance(data, dict):
        raise ValueError(f"Companion inventory must be a YAML dict, got {type(data).__name__}")
    harness_home = os.environ.get("AL_DEV_HARNESS_HOME", str(Path.home()))
    packages = data.get("packages", [])
    if not isinstance(packages, list):
        raise ValueError(f"Companion inventory 'packages' must be a list, got {type(packages).__name__}")
    for entry in packages:
        if not isinstance(entry, dict):
            raise ValueError(f"Each package entry must be a dict, got {type(entry).__name__}")
        for key in ("current_root", "current_registry"):
            if key in entry:
                value = entry[key]
                if isinstance(value, str):
                    entry[key] = value.replace("${AL_DEV_HARNESS_HOME}", harness_home)
    return data
