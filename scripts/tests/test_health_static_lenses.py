"""Fixture tests for scripts/health_static_lenses.py.

Each of the four converted checks must FIRE on a known-bad fixture and stay
SILENT on a known-good one. Written to run either under pytest or via the
CLAUDE.md libexpat workaround (importlib spec_from_file_location).
"""

from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path


_SCRIPT = Path(__file__).resolve().parents[1] / "health_static_lenses.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("health_static_lenses", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = _load_module()


def _write(dirpath: Path, rel: str, content: str) -> Path:
    p = dirpath / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


# --- naming-convention-lens -------------------------------------------------

def test_naming_fires_on_bad_lens_name():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        bad = _write(root, "bad-lens-name.md", "---\nname: bad-lens-name\n---\nx\n")
        rows = M.check_naming([bad], [])
        assert any("High" in r and "bad-lens-name" in r for r in rows), rows


def test_naming_silent_on_good_lens_name():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        good = _write(root, "design-agent-lens-foo.md", "---\nname: x\n---\nx\n")
        also = _write(root, "naming-convention-lens.md", "---\nname: x\n---\nx\n")
        assert M.check_naming([good, also], []) == []


# --- quality-agent-lens-structure -------------------------------------------

_GOOD_AGENT = (
    "---\n"
    "name: al-dev-thing\n"
    "description: Does a thing.\n"
    "model: haiku\n"
    'tools: ["Read"]\n'
    "---\n"
    "## Inputs\n\nfoo\n\n## Outputs\n\nbar\n"
)


def test_agent_structure_fires_on_missing_model_and_inputs():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        bad = _write(
            root, "al-dev-thing.md",
            "---\nname: al-dev-thing\ndescription: x\n"
            'tools: ["Read"]\n---\n## Outputs\n\nbar\n',
        )
        rows = M.check_agent_structure([bad], "plugin")
        assert any("missing `model`" in r for r in rows), rows
        assert any("missing `## Inputs`" in r for r in rows), rows


def test_agent_structure_fires_on_noncanonical_tool():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        bad = _write(
            root, "al-dev-thing.md",
            "---\nname: al-dev-thing\ndescription: x\nmodel: haiku\n"
            'tools: ["Frobnicate"]\n---\n## Inputs\n\nfoo\n\n## Outputs\n\nbar\n',
        )
        rows = M.check_agent_structure([bad], "plugin")
        assert any("non-canonical tool `Frobnicate`" in r for r in rows), rows


def test_agent_structure_fires_on_empty_tools_array():
    """An empty `tools: []` array is present (so the missing-tools High check
    stays silent) but non-canonical, and must be flagged Medium."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        bad = _write(
            root, "al-dev-thing.md",
            "---\nname: al-dev-thing\ndescription: x\nmodel: haiku\n"
            "tools: []\n---\n## Inputs\n\nfoo\n\n## Outputs\n\nbar\n",
        )
        rows = M.check_agent_structure([bad], "plugin")
        assert any("empty `tools: []`" in r and "Medium" in r for r in rows), rows
        # The missing-tools High finding must NOT fire (the field is present).
        assert not any("missing `tools`" in r for r in rows), rows


def test_agent_structure_silent_on_populated_tools():
    """A populated tools list (canonical entries) must NOT trigger the empty-array
    finding."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        good = _write(root, "al-dev-thing.md", _GOOD_AGENT)
        rows = M.check_agent_structure([good], "plugin")
        assert not any("empty `tools: []`" in r for r in rows), rows


def test_agent_structure_silent_on_good_agent():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        good = _write(root, "al-dev-thing.md", _GOOD_AGENT)
        assert M.check_agent_structure([good], "plugin") == []


# --- quality-skill-lens-structure -------------------------------------------

def test_skill_structure_fires_on_missing_argument_hint():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        # body references an argument via the literal phrase, no argument-hint.
        bad = _write(
            root, "myskill/SKILL.md",
            "---\nname: myskill\ndescription: x\n---\n"
            "# Skill\n\nIf an argument was passed, use it.\n",
        )
        rows = M.check_skill_structure([bad])
        assert any("argument-hint" in r for r in rows), rows


def test_skill_structure_fires_on_name_mismatch():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        bad = _write(
            root, "myskill/SKILL.md",
            "---\nname: wrongname\ndescription: x\n---\n# Skill\n\nbody\n",
        )
        rows = M.check_skill_structure([bad])
        assert any("does not match parent directory" in r for r in rows), rows


def test_skill_structure_fires_on_empty_argument_hint():
    """An empty-string `argument-hint: ""` must be flagged Low, independent of
    whether the body references an argument."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        bad = _write(
            root, "myskill/SKILL.md",
            '---\nname: myskill\ndescription: x\nargument-hint: ""\n---\n'
            "# Skill\n\nbody with no argument reference\n",
        )
        rows = M.check_skill_structure([bad])
        assert any("empty " in r and "Low" in r and "argument-hint" in r
                   for r in rows), rows


def test_skill_structure_silent_on_absent_argument_hint():
    """No argument-hint field at all (and no argument reference) must NOT trigger
    the empty-string finding."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        skill = _write(
            root, "myskill/SKILL.md",
            "---\nname: myskill\ndescription: x\n---\n# Skill\n\nbody\n",
        )
        rows = M.check_skill_structure([skill])
        assert not any("empty " in r and "argument-hint" in r for r in rows), rows


def test_skill_structure_silent_on_nonempty_argument_hint():
    """A populated argument-hint must NOT trigger the empty-string finding."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        skill = _write(
            root, "myskill/SKILL.md",
            '---\nname: myskill\ndescription: x\nargument-hint: "[--flag]"\n---\n'
            "# Skill\n\nbody\n",
        )
        rows = M.check_skill_structure([skill])
        assert not any("empty " in r and "argument-hint" in r for r in rows), rows


def test_skill_structure_silent_on_good_skill():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        good = _write(
            root, "myskill/SKILL.md",
            "---\nname: myskill\ndescription: x\nargument-hint: \"[arg]\"\n---\n"
            "# Skill\n\nIf an argument was passed, use it.\n",
        )
        assert M.check_skill_structure([good]) == []


def test_skill_structure_no_argument_inference_false_positive():
    """A skill that vaguely 'implies' an arg in prose (no [arg] / literal phrase)
    must NOT be flagged — the conditional check is concrete-pattern only."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        skill = _write(
            root, "myskill/SKILL.md",
            "---\nname: myskill\ndescription: x\n---\n"
            "# Skill\n\nThe user may optionally provide a value to refine output.\n",
        )
        assert M.check_skill_structure([skill]) == []


# --- design-agent-lens-tool-hygiene -----------------------------------------

def test_tool_hygiene_fires_on_write_on_readonly():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        bad = _write(
            root, "al-dev-reader.md",
            "---\nname: al-dev-reader\nmodel: haiku\n"
            'tools: ["Read", "Write"]\n---\n'
            "## Inputs\n\nRead the files and return a findings block.\n",
        )
        rows = M.check_tool_hygiene([bad])
        assert any("High" in r and "`Write`" in r for r in rows), rows


def test_tool_hygiene_fires_on_unused_mcp():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        bad = _write(
            root, "al-dev-writer.md",
            "---\nname: al-dev-writer\nmodel: haiku\n"
            'tools: ["Read", "Write", "MCP: al-mcp-server"]\n---\n'
            "## Inputs\n\nRead and then write the output file.\n",
        )
        rows = M.check_tool_hygiene([bad])
        assert any("al-mcp-server" in r for r in rows), rows


def test_tool_hygiene_silent_when_write_used():
    """Write/Edit on an agent whose body uses write verbs is NOT flagged."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        good = _write(
            root, "al-dev-writer.md",
            "---\nname: al-dev-writer\nmodel: haiku\n"
            'tools: ["Read", "Write"]\n---\n'
            "## Inputs\n\nRead the input, then write the report to disk.\n",
        )
        assert M.check_tool_hygiene([good]) == []


def test_tool_hygiene_no_generic_zero_mention_false_positive():
    """A read-only agent declaring Read/Glob/Grep/Bash without naming the literal
    word must NOT be flagged — generic zero-mention is intentionally out of scope."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        agent = _write(
            root, "al-dev-scanner.md",
            "---\nname: al-dev-scanner\nmodel: haiku\n"
            'tools: ["Read", "Glob", "Grep", "Bash"]\n---\n'
            "## Inputs\n\nScan the corpus and return a findings block.\n",
        )
        assert M.check_tool_hygiene([agent]) == []


def _run_all():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print(f"\nAll {len(tests)} fixture tests passed.")


if __name__ == "__main__":
    _run_all()
