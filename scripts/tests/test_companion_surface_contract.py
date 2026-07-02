import unittest
from pathlib import Path

from scripts.al_dev_tools.companion_surface_contract import (
    canonical_companion_surfaces,
    legacy_surface_aliases,
    load_companion_inventory,
    surface_root_map,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_canonical_companion_surfaces_are_stable() -> None:
    assert canonical_companion_surfaces() == (
        "companion-codex-al-dev",
        "companion-claude-al-dev",
        "companion-copilot-al-dev",
    )


def test_legacy_aliases_preserve_both_semantics() -> None:
    aliases = legacy_surface_aliases()
    assert aliases["both"] == ("plugin", "tooling")
    assert aliases["companions"] == canonical_companion_surfaces()


def test_surface_axis_never_reuses_the_dimension_all_token() -> None:
    aliases = legacy_surface_aliases()
    assert "all" not in aliases, (
        "'all' is reserved for --dimension all; the surface-axis aggregate must be "
        "spelled 'everything'"
    )
    assert aliases["everything"] == ("plugin", "tooling", *canonical_companion_surfaces())


def test_surface_root_map_uses_repo_relative_targets() -> None:
    roots = surface_root_map(REPO_ROOT)
    assert roots["companion-codex-al-dev"] == REPO_ROOT / "companions/codex/al-dev"
    assert roots["companion-claude-al-dev"] == REPO_ROOT / "companions/claude/al-dev"
    assert roots["companion-copilot-al-dev"] == REPO_ROOT / "companions/copilot/al-dev"


def test_inventory_loader_reads_yaml_package_records() -> None:
    inventory = load_companion_inventory(REPO_ROOT)
    assert {entry["surface_id"] for entry in inventory["packages"]} >= {
        "companion-codex-al-dev",
        "companion-claude-al-dev",
        "companion-copilot-al-dev",
    }


def test_inventory_loader_expands_harness_home_placeholder() -> None:
    inventory = load_companion_inventory(REPO_ROOT)
    for entry in inventory["packages"]:
        for key in ("current_root", "current_registry"):
            if key in entry:
                assert "${AL_DEV_HARNESS_HOME}" not in entry[key], (
                    f"{entry['surface_id']}.{key} was not expanded"
                )


def load_tests(loader, tests, pattern):  # noqa: ARG001
    """Wire bare-function tests into unittest discovery."""
    suite = unittest.TestSuite()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            suite.addTest(unittest.FunctionTestCase(fn))
    return suite
