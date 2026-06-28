from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


def load_module():
    module_path = Path(__file__).resolve().parents[1] / "al_dev_tools" / "markdown_frontmatter.py"
    spec = importlib.util.spec_from_file_location("markdown_frontmatter", module_path)
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


def test_parse_required_frontmatter_returns_data_and_body():
    mod = load_module()

    data, body = mod.parse_required_frontmatter(
        "---\n"
        "title: Example\n"
        "tags:\n"
        "  - one\n"
        "  - two\n"
        "---\n"
        "\n"
        "# Body\n"
    )

    assert data == {"title": "Example", "tags": ["one", "two"]}
    assert body == "\n# Body\n"


def test_parse_optional_frontmatter_returns_original_text_when_missing():
    mod = load_module()
    text = "# Heading\n\nBody\n"

    data, body = mod.parse_optional_frontmatter(text)

    assert data == {}
    assert body == text


def test_parse_required_frontmatter_rejects_non_mapping_yaml():
    mod = load_module()

    with unittest.TestCase().assertRaises(ValueError):
        mod.parse_required_frontmatter("---\n- one\n- two\n---\nBody\n")


def test_find_markdown_heading_ignores_fences_and_quotes():
    mod = load_module()
    text = (
        "```markdown\n"
        "# Hidden heading\n"
        "```\n"
        "> # Also hidden\n"
        "\n"
        "## Visible heading\n"
    )

    assert mod.find_markdown_heading(text, "Hidden heading") is False
    assert mod.find_markdown_heading(text, "Also hidden") is False
    assert mod.find_markdown_heading(text, "Visible heading") is True


def _run(func):
    func()


def load_tests(loader, tests, pattern):  # noqa: ARG001
    suite = unittest.TestSuite()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            suite.addTest(unittest.FunctionTestCase(lambda fn=fn: _run(fn)))
    return suite


if __name__ == "__main__":
    unittest.main()
