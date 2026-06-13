"""Tests for the deterministic ledger-suppression matcher in health_disposition_store.

Run with unittest (pytest may hit the macOS libexpat conflict; see CLAUDE.md):

    python3 scripts/tests/test_health_disposition_store_match.py
"""
from __future__ import annotations

import importlib.util
import inspect
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "health_disposition_store.py"

_spec = importlib.util.spec_from_file_location("health_disposition_store", MODULE_PATH)
hds = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hds)


def _row(surface, dimension, obj, finding, disposition, id_="#999", date="2026-06-13"):
    return {
        "id": id_,
        "surface": surface,
        "dimension": dimension,
        "object": obj,
        "finding": finding,
        "disposition": disposition,
        "date": date,
        "note": "",
    }


def _finding(obj, surface, dimension, text):
    return {"object": obj, "surface": surface, "dimension": dimension, "finding": text}


def test_object_members_comma_list() -> None:
    members = hds.object_members(
        "sync-documentation-maps-agent-update, sync-documentation-maps-skill-update"
    )
    assert "sync-documentation-maps-agent-update" in members
    assert "sync-documentation-maps-skill-update" in members


def test_object_members_parenthetical_list() -> None:
    members = hds.object_members(
        "11 design-lens agents (caller-alignment, model-fit, scope-isolation)"
    )
    assert {"caller-alignment", "model-fit", "scope-isolation"} <= members


def test_object_members_single() -> None:
    assert "plugin-health-discover" in hds.object_members("plugin-health-discover")


def test_suppress_grandfathered_member_match() -> None:
    rows = [
        _row(
            "tooling",
            "naming",
            "analyze-architectural-design, plugin-health-discover, plugin-health-report",
            "Naming: not verb-first {verb}-{object}-{aspect}",
            "grandfathered",
        )
    ]
    findings = [
        _finding(
            "plugin-health-discover",
            "tooling",
            "naming",
            "Skill name is not the recommended verb-first {verb}-{object}-{aspect} pattern",
        )
    ]
    result = hds.match_against_ledger(findings, rows)
    assert result[0]["classification"] == "suppress", result[0]


def test_verify_fixed_match() -> None:
    rows = [
        _row(
            "tooling",
            "quality",
            "implement-health-plan",
            "clarity: Phase 0 before acting on it ambiguous guard wording",
            "fixed",
        )
    ]
    findings = [
        _finding(
            "implement-health-plan",
            "tooling",
            "quality",
            "Phase 0 acting on it guard wording is ambiguous before deciding",
        )
    ]
    result = hds.match_against_ledger(findings, rows)
    assert result[0]["classification"] == "verify", result[0]


def test_keep_when_object_not_in_ledger() -> None:
    rows = [_row("tooling", "quality", "some-other-skill", "Bloat: long phase", "fixed")]
    findings = [_finding("brand-new-skill", "tooling", "quality", "Bloat: long phase")]
    result = hds.match_against_ledger(findings, rows)
    assert result[0]["classification"] == "keep", result[0]


def test_no_false_suppress_same_object_different_issue() -> None:
    # Object matches a grandfathered row, but the finding is a different issue
    # (clarity vs bloat) with little text overlap → must NOT be suppressed.
    rows = [
        _row(
            "tooling",
            "quality",
            "implement-health-plan",
            "Bloat: Phase 2 verify-per-task fifty-two lines inherent procedure",
            "grandfathered",
        )
    ]
    findings = [
        _finding(
            "implement-health-plan",
            "tooling",
            "quality",
            "Clarity: depends on the edited text undefined self-edit ordering",
        )
    ]
    result = hds.match_against_ledger(findings, rows)
    assert result[0]["classification"] == "keep", result[0]


def test_suppress_beats_verify_precedence() -> None:
    rows = [
        _row("tooling", "quality", "obj-x", "clarity: vague term foo bar baz qux", "fixed"),
        _row(
            "tooling",
            "quality",
            "obj-x",
            "clarity: vague term foo bar baz qux",
            "grandfathered",
            id_="#1000",
        ),
    ]
    findings = [
        _finding("obj-x", "tooling", "quality", "clarity: vague term foo bar baz qux")
    ]
    result = hds.match_against_ledger(findings, rows)
    assert result[0]["classification"] == "suppress", result[0]


def test_naming_matches_on_object_without_text_overlap() -> None:
    # Naming has one verdict per object; a grandfathered naming row must suppress
    # a new naming finding on the same object even when the wording is disjoint.
    rows = [
        _row(
            "tooling",
            "naming",
            "analyze-architectural-design, plugin-health-discover, plugin-health-report",
            "Naming: not verb-first {verb}-{object}-{aspect}",
            "grandfathered",
        )
    ]
    findings = [
        {
            "object": "plugin-health-discover",
            "surface": "tooling",
            "dimension": "naming",
            "type": "naming",
            "finding": "Same pattern deviation; not grandfathered",
        }
    ]
    result = hds.match_against_ledger(findings, rows)
    assert result[0]["classification"] == "suppress", result[0]


def test_bloat_different_phase_same_object_kept() -> None:
    # Bloat can have many verdicts per object; a Phase 0 finding must NOT be
    # suppressed by a grandfathered Phase 2 bloat row (disjoint text).
    rows = [
        _row(
            "tooling",
            "quality",
            "implement-health-plan",
            "Bloat: Phase 2 verify per task fifty-two lines inherent procedure",
            "grandfathered",
        )
    ]
    findings = [
        {
            "object": "implement-health-plan",
            "surface": "tooling",
            "dimension": "quality",
            "type": "bloat",
            "finding": "Bloat: Phase 0 seventy lines location scan resume checkpoint write block",
        }
    ]
    result = hds.match_against_ledger(findings, rows)
    assert result[0]["classification"] == "keep", result[0]


def test_legacy_unknown_surface_row_still_matches() -> None:
    rows = [
        _row(
            "unknown",
            "unknown",
            "align-harness-repos",
            "Name implies alignment behavior is validation only",
            "grandfathered",
        )
    ]
    findings = [
        _finding(
            "align-harness-repos",
            "tooling",
            "quality",
            "Name implies alignment but behavior is validation only with optional fixes",
        )
    ]
    result = hds.match_against_ledger(findings, rows)
    assert result[0]["classification"] == "suppress", result[0]


def _run(func):
    sig = inspect.signature(func)
    if sig.parameters:
        raise TypeError(f"Unsupported signature: {func.__name__}{sig}")
    func()


def load_tests(loader, tests, pattern):  # noqa: ARG001
    suite = unittest.TestSuite()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            suite.addTest(unittest.FunctionTestCase(lambda fn=fn: _run(fn)))
    return suite


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                _run(fn)
                print(f"PASS {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL {name}: {exc}")
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f"ERROR {name}: {exc!r}")
    print(f"\n{failures} failure(s)")
    raise SystemExit(1 if failures else 0)
