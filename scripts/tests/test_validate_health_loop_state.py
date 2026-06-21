from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_health_loop_state import validate_text, SUCCESSOR  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_BREADCRUMB = """\
stage_completed: implement-plugin-health
completed_at: 2026-06-14
next_command: none
next_inputs: []
fresh_session_recommended: false
note: loop closed; no further steps required
"""

VALID_MID_LOOP = """\
stage_completed: plan-plugin-findings
completed_at: 2026-06-14
next_command: /implement-plugin-health --plan .dev/my-plan.md
next_inputs:
- .dev/my-plan.md
fresh_session_recommended: true
note: heavy context transition — run in a fresh session
"""


def _drop(text: str, field: str) -> str:
    """Return text with the line for `field` removed."""
    return "\n".join(
        ln for ln in text.splitlines() if not ln.startswith(f"{field}:")
    )


def _replace(text: str, field: str, value: str) -> str:
    """Replace a single-line field value."""
    return "\n".join(
        f"{field}: {value}" if ln.startswith(f"{field}:") else ln
        for ln in text.splitlines()
    )


# ---------------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------------

def test_valid_closed_loop():
    assert validate_text(VALID_BREADCRUMB) == []


def test_valid_mid_loop():
    assert validate_text(VALID_MID_LOOP) == []


def test_absent_equivalent_empty_string():
    # An empty file should fail (missing fields) but not crash
    errors = validate_text("")
    assert any("missing required field" in e for e in errors)


# ---------------------------------------------------------------------------
# Missing required fields
# ---------------------------------------------------------------------------

def test_missing_stage_completed():
    errors = validate_text(_drop(VALID_BREADCRUMB, "stage_completed"))
    assert any("stage_completed" in e for e in errors)


def test_missing_completed_at():
    errors = validate_text(_drop(VALID_BREADCRUMB, "completed_at"))
    assert any("completed_at" in e for e in errors)


def test_missing_next_command():
    errors = validate_text(_drop(VALID_BREADCRUMB, "next_command"))
    assert any("next_command" in e for e in errors)


def test_missing_fresh_session_recommended():
    errors = validate_text(_drop(VALID_BREADCRUMB, "fresh_session_recommended"))
    assert any("fresh_session_recommended" in e for e in errors)


def test_missing_note():
    errors = validate_text(_drop(VALID_BREADCRUMB, "note"))
    assert any("note" in e for e in errors)


# ---------------------------------------------------------------------------
# Field format violations
# ---------------------------------------------------------------------------

def test_bad_date_format():
    errors = validate_text(_replace(VALID_BREADCRUMB, "completed_at", "14-06-2026"))
    assert any("completed_at" in e for e in errors)


def test_bad_date_slash():
    errors = validate_text(_replace(VALID_BREADCRUMB, "completed_at", "2026/06/14"))
    assert any("completed_at" in e for e in errors)


def test_bad_fresh_session_yes():
    errors = validate_text(_replace(VALID_BREADCRUMB, "fresh_session_recommended", "yes"))
    assert any("fresh_session_recommended" in e for e in errors)


def test_bad_fresh_session_1():
    errors = validate_text(_replace(VALID_BREADCRUMB, "fresh_session_recommended", "1"))
    assert any("fresh_session_recommended" in e for e in errors)


def test_next_inputs_non_list():
    errors = validate_text(_replace(VALID_BREADCRUMB, "next_inputs", "some-path.md"))
    assert any("next_inputs" in e for e in errors)


# ---------------------------------------------------------------------------
# next_command validation
# ---------------------------------------------------------------------------

def test_unknown_next_command():
    errors = validate_text(_replace(VALID_BREADCRUMB, "next_command", "/unknown-skill"))
    assert any("not a known loop command" in e for e in errors)


def test_next_command_no_slash():
    errors = validate_text(_replace(VALID_BREADCRUMB, "next_command", "record-plugin-dispositions"))
    assert any("not a known loop command" in e for e in errors)


# ---------------------------------------------------------------------------
# Lifecycle consistency
# ---------------------------------------------------------------------------

def test_lifecycle_wrong_successor():
    # implement-plugin-health must write next_command=none, not plan-plugin-findings
    text = _replace(VALID_BREADCRUMB, "next_command", "/plan-plugin-findings")
    errors = validate_text(text)
    assert any("requires next_command" in e for e in errors)


def test_lifecycle_all_successors():
    # Each stage should pass with its correct successor from SUCCESSOR
    for stage, successor in SUCCESSOR.items():
        nc = "none" if successor is None else f"{successor} --plan x"
        ni = "[]" if successor is None else ""
        if ni == "":
            text = (
                f"stage_completed: {stage}\n"
                f"completed_at: 2026-06-14\n"
                f"next_command: {nc}\n"
                f"next_inputs:\n"
                f"- some-artifact.md\n"
                f"fresh_session_recommended: false\n"
                f"note: test\n"
            )
        else:
            text = (
                f"stage_completed: {stage}\n"
                f"completed_at: 2026-06-14\n"
                f"next_command: {nc}\n"
                f"next_inputs: {ni}\n"
                f"fresh_session_recommended: false\n"
                f"note: test\n"
            )
        errors = validate_text(text)
        assert errors == [], f"stage={stage!r} nc={nc!r} errors={errors}"


def test_lifecycle_unknown_stage():
    text = _replace(VALID_BREADCRUMB, "stage_completed", "some-other-skill")
    errors = validate_text(text)
    assert any("not a known loop stage" in e for e in errors)


# ---------------------------------------------------------------------------
# Coherence: next_command=none with non-empty next_inputs
# ---------------------------------------------------------------------------

def test_closed_loop_with_nonempty_inputs():
    text = (
        "stage_completed: implement-plugin-health\n"
        "completed_at: 2026-06-14\n"
        "next_command: none\n"
        "next_inputs:\n"
        "- .dev/some-plan.md\n"
        "fresh_session_recommended: false\n"
        "note: loop closed\n"
    )
    errors = validate_text(text)
    assert any("next_inputs is non-empty" in e for e in errors)


# ---------------------------------------------------------------------------
# Block-list next_inputs (mid-loop)
# ---------------------------------------------------------------------------

def test_block_list_next_inputs_valid():
    assert validate_text(VALID_MID_LOOP) == []


if __name__ == "__main__":
    # Collect and run all test_ functions as a simple test runner
    # (fallback for Python 3.13 / libexpat pytest conflicts).
    current_module = sys.modules[__name__]
    tests = [
        (name, obj)
        for name, obj in vars(current_module).items()
        if name.startswith("test_") and callable(obj)
    ]
    failures: list[str] = []
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
        except AssertionError as exc:
            failures.append(name)
            print(f"FAIL  {name}: {exc}")
        except Exception as exc:
            failures.append(name)
            print(f"ERROR {name}: {exc}")
    if failures:
        print(f"\n{len(failures)} test(s) failed: {', '.join(failures)}")
        sys.exit(1)
    print(f"\n{len(tests)} test(s) passed")
