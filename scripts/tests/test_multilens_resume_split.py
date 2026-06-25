"""Regression tests for the bundled-quality resume/split state machine.

Exercises the discover-plugin-health bundled-reader branch directly, without
dispatching real agents: the resume-collapse completeness rule (`reader_complete`),
the raw classifier (`classify_raw`), the Phase 4 all-clean fallback
(`write_allclean_children`), and the splitter fan-out (`split_combined`).
"""
import importlib.util
import json
import os
import tempfile
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "multilens"

spec = importlib.util.spec_from_file_location(
    "split_multilens_findings",
    str(Path(__file__).resolve().parents[1] / "split_multilens_findings.py"),
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

AGENT_VALID = (FIXTURES / "agent-valid.raw.md").read_text()
SKILL_VALID = (FIXTURES / "skill-valid.raw.md").read_text()

# Marker-less all-clean return (a reader that reported no issues without markers).
ALL_CLEAN_AGENT = "### Bloat Findings\n\n_No issues found._\n"

# Truncated mid-stream — only two of the four expected markers present.
TRUNCATED_AGENT = """<!-- lens: quality-agent-lens-bloat -->
### Bloat Findings

- **foo** | Medium | x | y

<!-- lens: quality-agent-lens-clarity -->
### Prompt Clarity Findings
"""


def test_valid_four_marker_raw_is_complete():
    # valid four-marker .raw.md => resume collapse treats the reader as completed
    assert mod.classify_raw(AGENT_VALID, "agent") == "complete"
    assert mod.classify_raw(SKILL_VALID, "skill") == "complete"
    assert mod.reader_complete("agent", [], AGENT_VALID) is True
    assert mod.reader_complete("skill", [], SKILL_VALID) is True


def test_malformed_raw_is_incomplete():
    # malformed/truncated .raw.md => resume collapse treats the reader as incomplete
    assert mod.classify_raw(TRUNCATED_AGENT, "agent") == "malformed"
    assert mod.reader_complete("agent", [], TRUNCATED_AGENT) is False
    # partial child JSON set (2 of 4) => reader re-dispatched
    partial = ["quality-agent-lens-bloat", "quality-agent-lens-clarity"]
    assert mod.reader_complete("agent", partial, None) is False


def test_complete_child_set_is_complete():
    # all four child JSONs present => reader complete even with no raw on disk
    assert mod.reader_complete("agent", mod.OBJECT_LENSES["agent"], None) is True


def test_allclean_fallback_writes_four_children():
    # marker-less explicit all-clean .raw.md => Phase 4 fallback writes four child JSONs
    assert mod.classify_raw(ALL_CLEAN_AGENT, "agent") == "all-clean"
    with tempfile.TemporaryDirectory() as d:
        written = mod.write_allclean_children(
            "agent", "2026-06-25", d, completed_at="2026-06-25T00:00:00Z"
        )
        assert len(written) == 4, written
        for p in written:
            obj = json.load(open(p))
            # synthesized child JSONs include all four schema keys
            assert set(obj) == {"lens", "findings", "suggestion_count", "completed_at"}, obj
            assert obj["suggestion_count"] == 0, obj
            assert "_No issues found._" in obj["findings"], obj
        names = sorted(os.path.basename(p) for p in written)
        assert names == [
            "2026-06-25-plugin-health-lens-quality-agent-lens-bloat.json",
            "2026-06-25-plugin-health-lens-quality-agent-lens-clarity.json",
            "2026-06-25-plugin-health-lens-quality-agent-lens-description.json",
            "2026-06-25-plugin-health-lens-quality-agent-lens-name-fit.json",
        ], names


def test_valid_raw_splits_to_four_children():
    # a validated four-marker raw fans out into the same four child JSONs
    # the rest of Phase 4 assembly consumes
    with tempfile.TemporaryDirectory() as d:
        written = mod.split_combined(
            SKILL_VALID, "2026-06-25", d, completed_at="2026-06-25T00:00:00Z"
        )
        names = sorted(os.path.basename(p) for p in written)
        assert names == [
            "2026-06-25-plugin-health-lens-quality-skill-lens-bloat.json",
            "2026-06-25-plugin-health-lens-quality-skill-lens-clarity.json",
            "2026-06-25-plugin-health-lens-quality-skill-lens-description.json",
            "2026-06-25-plugin-health-lens-quality-skill-lens-name-fit.json",
        ], names
        clarity = json.load(
            open(os.path.join(d, "2026-06-25-plugin-health-lens-quality-skill-lens-clarity.json"))
        )
        assert clarity["suggestion_count"] == 1, clarity


if __name__ == "__main__":
    test_valid_four_marker_raw_is_complete()
    test_malformed_raw_is_incomplete()
    test_complete_child_set_is_complete()
    test_allclean_fallback_writes_four_children()
    test_valid_raw_splits_to_four_children()
    print("PASS")
