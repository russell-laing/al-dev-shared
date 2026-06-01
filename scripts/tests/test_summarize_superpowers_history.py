import tempfile
import unittest
from pathlib import Path

import importlib.util


def load_module():
    module_path = Path(__file__).resolve().parents[1] / "summarize_superpowers_history.py"
    spec = importlib.util.spec_from_file_location("summarize_superpowers_history", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
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
