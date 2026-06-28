from __future__ import annotations

import importlib.util
import inspect
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "check_health_loop_handoffs",
    REPO_ROOT / "scripts" / "check_health_loop_handoffs.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

_PHF_BODY = """# plan-plugin-findings

Read .dev/health-loop-state.md before starting.
Reference .dev/health-loop-state.md again before ending.

Use superpowers:writing-plans before proposing changes.

## Phase 3
Suppress the Execution Handoff here.

## Phase 4
Hand off to implement-plugin-health after the planning step.
Execution Handoff
implement-plugin-health
"""

_GENERIC_BODY = """# skill

Read .dev/health-loop-state.md before starting.
Write .dev/health-loop-state.md before ending.
"""


def _make_fixture_repo(tmp_path: Path, plan_body: str = _PHF_BODY) -> Path:
    skills_root = tmp_path / ".claude" / "skills"
    contract = tmp_path / ".claude" / "knowledge" / "health-loop-state-contract.md"
    contract.parent.mkdir(parents=True)
    contract.write_text("# Contract\n", encoding="utf-8")

    for name in _mod.LOOP:
        skill_dir = skills_root / name
        skill_dir.mkdir(parents=True)
        body = plan_body if name == "plan-plugin-findings" else _GENERIC_BODY
        (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")

    return tmp_path


def test_main_returns_zero_when_required_references_exist(tmp_path: Path) -> None:
    repo_root = _make_fixture_repo(tmp_path)
    assert _mod.main(repo_root=repo_root) == 0


def test_main_returns_one_when_plan_override_reference_is_missing(tmp_path: Path) -> None:
    broken_body = _PHF_BODY.replace("implement-plugin-health", "report-plugin-health")
    repo_root = _make_fixture_repo(tmp_path, plan_body=broken_body)
    assert _mod.main(repo_root=repo_root) == 1


def _run(func):
    sig = inspect.signature(func)
    if not sig.parameters:
        func()
    elif list(sig.parameters) == ["tmp_path"]:
        with tempfile.TemporaryDirectory() as td:
            func(Path(td))
    else:
        raise TypeError(f"Unsupported signature: {func.__name__}{sig}")


def load_tests(loader, tests, pattern):  # noqa: ARG001
    suite = unittest.TestSuite()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            suite.addTest(unittest.FunctionTestCase(lambda fn=fn: _run(fn)))
    return suite


if __name__ == "__main__":
    unittest.main()
