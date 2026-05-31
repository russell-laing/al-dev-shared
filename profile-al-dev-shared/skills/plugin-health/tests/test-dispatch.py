import sys
import json
import tempfile
from pathlib import Path
sys.path.insert(0, '/Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/plugin-health')

from dispatch import (
    validate_arguments,
    build_file_lists,
    determine_lenses_for_scope,
    save_checkpoint,
    load_checkpoint,
)
from schemas import CheckpointState

def test_validate_arguments_valid():
    """Valid argument combinations should pass."""
    valid, msg = validate_arguments("plugin", "design")
    assert valid, msg

    valid, msg = validate_arguments("both", "all")
    assert valid, msg
    print("✓ test_validate_arguments_valid PASSED")

def test_validate_arguments_invalid():
    """Invalid arguments should fail with error message."""
    valid, msg = validate_arguments("invalid", "design")
    assert not valid
    assert "Invalid surface" in msg

    valid, msg = validate_arguments("plugin", "invalid")
    assert not valid
    assert "Invalid dimension" in msg
    print("✓ test_validate_arguments_invalid PASSED")

def test_determine_lenses_design_plugin():
    """Should return only design lenses for plugin surface."""
    lenses = determine_lenses_for_scope("plugin", "design")

    # Should include design lenses
    design_lens_names = {l.name for l in lenses}
    assert "design-agent-lens-tool-hygiene" in design_lens_names
    assert "design-skill-lens-complexity" in design_lens_names

    # Should not include quality lenses
    assert not any("quality" in l.name for l in lenses)
    print("✓ test_determine_lenses_design_plugin PASSED")

def test_determine_lenses_all():
    """Should return all lenses for 'all' dimension."""
    lenses = determine_lenses_for_scope("both", "all")
    lens_names = {l.name for l in lenses}

    # Should include both design and quality
    assert any("design" in n for n in lens_names)
    assert any("quality" in n for n in lens_names)
    print("✓ test_determine_lenses_all PASSED")

def test_checkpoint_roundtrip_file():
    """Checkpoint should persist and restore from file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        checkpoint_path = str(Path(tmpdir) / "checkpoint.json")

        original = CheckpointState(
            run_id="2026-05-31-001",
            team_id="team-uuid-123",
            surface="plugin",
            dimension="design",
            spawned_at="2026-05-31T14:30:00Z",
            status="dispatched",
            pending_lenses=["lens1", "lens2"]
        )

        # Save
        success = save_checkpoint(original, checkpoint_path)
        assert success
        assert Path(checkpoint_path).exists()

        # Load
        restored = load_checkpoint(checkpoint_path)
        assert restored is not None
        assert restored.run_id == original.run_id
        assert restored.team_id == original.team_id
        assert restored.pending_lenses == original.pending_lenses
        print("✓ test_checkpoint_roundtrip_file PASSED")

if __name__ == "__main__":
    test_validate_arguments_valid()
    test_validate_arguments_invalid()
    test_determine_lenses_design_plugin()
    test_determine_lenses_all()
    test_checkpoint_roundtrip_file()
    print("\nAll dispatch tests passed!")
