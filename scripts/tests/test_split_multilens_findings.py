import importlib.util
import json
import os
import tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "split_multilens_findings",
    str(Path(__file__).resolve().parents[1] / "split_multilens_findings.py"),
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

COMBINED = """<!-- lens: quality-agent-lens-bloat -->
### Bloat Findings

- **al-dev-foo** | Medium | repetitive block | consolidate

<!-- lens: quality-agent-lens-clarity -->
### Prompt Clarity Findings

_No issues found._

<!-- lens: quality-agent-lens-description -->
### Description Drift Findings

- **al-dev-bar** | Medium | desc drift | align
- **al-dev-baz** | Low | minor | tweak

<!-- lens: quality-agent-lens-name-fit -->
### Name Fit Findings

_No issues found._
"""


def test_splits_four_blocks():
    with tempfile.TemporaryDirectory() as d:
        written = mod.split_combined(COMBINED, "2026-06-25", d, completed_at="2026-06-25T00:00:00Z")
        assert len(written) == 4, written
        names = sorted(os.path.basename(p) for p in written)
        assert names == [
            "2026-06-25-plugin-health-lens-quality-agent-lens-bloat.json",
            "2026-06-25-plugin-health-lens-quality-agent-lens-clarity.json",
            "2026-06-25-plugin-health-lens-quality-agent-lens-description.json",
            "2026-06-25-plugin-health-lens-quality-agent-lens-name-fit.json",
        ], names


def test_suggestion_counts_and_schema():
    with tempfile.TemporaryDirectory() as d:
        mod.split_combined(COMBINED, "2026-06-25", d, completed_at="2026-06-25T00:00:00Z")
        bloat = json.load(open(os.path.join(d, "2026-06-25-plugin-health-lens-quality-agent-lens-bloat.json")))
        assert set(bloat) == {"lens", "findings", "suggestion_count", "completed_at"}, bloat
        assert bloat["lens"] == "quality-agent-lens-bloat"
        assert bloat["suggestion_count"] == 1, bloat
        desc = json.load(open(os.path.join(d, "2026-06-25-plugin-health-lens-quality-agent-lens-description.json")))
        assert desc["suggestion_count"] == 2, desc
        clarity = json.load(open(os.path.join(d, "2026-06-25-plugin-health-lens-quality-agent-lens-clarity.json")))
        assert clarity["suggestion_count"] == 0, clarity


def test_no_markers_raises():
    try:
        mod.split_combined("### Bloat Findings\n\n_No issues found._", "2026-06-25", "/tmp")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError when no lens markers present")


if __name__ == "__main__":
    test_splits_four_blocks()
    test_suggestion_counts_and_schema()
    test_no_markers_raises()
    print("PASS")
