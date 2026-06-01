import contextlib
import io
import tempfile
import sys
import unittest
from pathlib import Path

import importlib.util


def load_module():
    module_path = Path(__file__).resolve().parents[1] / "summarize_superpowers_history.py"
    spec = importlib.util.spec_from_file_location("summarize_superpowers_history", module_path)
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(spec.name)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        if previous is None:
            sys.modules.pop(spec.name, None)
        else:
            sys.modules[spec.name] = previous
        raise
    return module


def test_extract_title_prefers_first_heading(tmp_path):
    module = load_module()
    artifact = tmp_path / "2026-05-31-example.md"
    artifact.write_text("# Example Plan\n\nBody\n", encoding="utf-8")

    item = module.inspect_artifact(artifact, tmp_path)

    assert item.title == "Example Plan"
    assert item.date == "2026-05-31"
    assert item.kind == "unknown"


def test_classify_status_from_keywords(tmp_path):
    module = load_module()
    artifact = tmp_path / "2026-05-30-cleanup.md"
    artifact.write_text(
        "# Cleanup\n\nStatus: implemented / superseded\n\nOlder plan text.\n",
        encoding="utf-8",
    )

    item = module.inspect_artifact(artifact, tmp_path)

    assert item.status == "superseded"


def test_explicit_approved_status_is_historical_not_implemented(tmp_path):
    module = load_module()
    artifact = tmp_path / "2026-05-31-approved.md"
    artifact.write_text(
        "# Approved Idea\n\n**Status:** Approved (brainstorming complete; pending implementation plan)\n",
        encoding="utf-8",
    )

    item = module.inspect_artifact(artifact, tmp_path)

    assert item.status == "historical"


def test_explicit_draft_status_is_historical(tmp_path):
    module = load_module()
    artifact = tmp_path / "2026-05-31-draft.md"
    artifact.write_text("# Draft Idea\n\nStatus: Draft\n", encoding="utf-8")

    item = module.inspect_artifact(artifact, tmp_path)

    assert item.status == "historical"


def test_body_status_after_heading_does_not_override_fallback(tmp_path):
    module = load_module()
    artifact = tmp_path / "2026-05-31-implemented.md"
    artifact.write_text(
        "# Implemented Plan\n\nImplemented cleanup.\n\n## Notes\n\nStatus: Draft\n",
        encoding="utf-8",
    )

    item = module.inspect_artifact(artifact, tmp_path)

    assert item.status == "implemented"


def test_unknown_preamble_status_falls_back_to_body_inference(tmp_path):
    module = load_module()
    artifact = tmp_path / "2026-05-31-unclear.md"
    artifact.write_text(
        "# Unclear Plan\n\nStatus: Needs triage\n\nImplemented cleanup.\n",
        encoding="utf-8",
    )

    item = module.inspect_artifact(artifact, tmp_path)

    assert item.status == "implemented"


def test_ready_revised_and_parked_status_phrases_are_bucketed(tmp_path):
    module = load_module()

    assert module.classify_status("Status: Ready for implementation") == "ready"
    assert module.classify_status("Status: Ready for plan authoring") == "ready"
    assert module.classify_status("Status: Revised for implementation planning") == "ready"
    assert module.classify_status("Status: Revised after claim verification") == "historical"
    assert module.classify_status("Status: Parked") == "deferred"


def test_main_prints_absolute_output_outside_root(tmp_path):
    module = load_module()
    root = tmp_path / "repo"
    artifact = root / "docs" / "superpowers" / "plans" / "2026-05-31-example.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("# Example\n\nImplemented cleanup.\n", encoding="utf-8")
    output = tmp_path / "outside" / "history.md"
    stdout = io.StringIO()

    with contextlib.redirect_stdout(stdout):
        result = module.main(["--root", str(root), "--output", str(output)])

    assert result == 0
    assert output.exists()
    assert f"Wrote {output}" in stdout.getvalue()
    assert "with 1 artifacts" in stdout.getvalue()


def test_reference_detection_excludes_superpowers_tree(tmp_path):
    module = load_module()
    root = tmp_path
    spec = root / "docs" / "superpowers" / "specs" / "2026-05-16-archive-test-skills-design.md"
    spec.parent.mkdir(parents=True)
    spec.write_text("# Archive Test Skills\n", encoding="utf-8")
    outside = root / "profile-al-dev-shared" / "archived" / "README.md"
    outside.parent.mkdir(parents=True)
    outside.write_text(
        "See `docs/superpowers/specs/2026-05-16-archive-test-skills-design.md`.\n",
        encoding="utf-8",
    )

    references = module.find_external_references(root, [spec])

    assert references[spec.as_posix()] == ["profile-al-dev-shared/archived/README.md"]


def test_reference_detection_excludes_nested_worktree_docs(tmp_path):
    module = load_module()
    root = tmp_path
    spec = root / "docs" / "superpowers" / "specs" / "2026-05-16-archive-test-skills-design.md"
    spec.parent.mkdir(parents=True)
    spec.write_text("# Archive Test Skills\n", encoding="utf-8")
    nested_worktree_doc = (
        root
        / ".worktrees"
        / "other"
        / "docs"
        / "superpowers"
        / "history.md"
    )
    nested_worktree_doc.parent.mkdir(parents=True)
    nested_worktree_doc.write_text(
        "See `docs/superpowers/specs/2026-05-16-archive-test-skills-design.md`.\n",
        encoding="utf-8",
    )

    references = module.find_external_references(root, [spec])

    assert references[spec.as_posix()] == []


def test_reference_detection_scans_repo_root_under_worktrees(tmp_path):
    module = load_module()
    root = tmp_path / ".worktrees" / "repo"
    spec = root / "docs" / "superpowers" / "specs" / "2026-05-16-archive-test-skills-design.md"
    spec.parent.mkdir(parents=True)
    spec.write_text("# Archive Test Skills\n", encoding="utf-8")
    outside = root / "profile-al-dev-shared" / "archived" / "README.md"
    outside.parent.mkdir(parents=True)
    outside.write_text(
        "See `docs/superpowers/specs/2026-05-16-archive-test-skills-design.md`.\n",
        encoding="utf-8",
    )

    references = module.find_external_references(root, [spec])

    assert references[spec.as_posix()] == ["profile-al-dev-shared/archived/README.md"]


def test_render_history_groups_by_date(tmp_path):
    module = load_module()
    artifact = tmp_path / "docs" / "superpowers" / "plans" / "2026-05-31-plugin-health-top-5.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("# Plugin Health Top 5\n\nImplemented cleanup.\n", encoding="utf-8")
    item = module.inspect_artifact(artifact, tmp_path)

    markdown = module.render_history([item], {})

    assert "# Superpowers Planning History" in markdown
    assert "## 2026-05-31" in markdown
    assert "Plugin Health Top 5" in markdown
    assert "Current source of truth" in markdown


def _run(func):
    if func.__code__.co_argcount == 0:
        func()
        return
    with tempfile.TemporaryDirectory() as td:
        func(Path(td))


def load_tests(loader, tests, pattern):  # noqa: ARG001
    suite = unittest.TestSuite()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            suite.addTest(unittest.FunctionTestCase(lambda fn=fn: _run(fn)))
    return suite


if __name__ == "__main__":
    unittest.main()
