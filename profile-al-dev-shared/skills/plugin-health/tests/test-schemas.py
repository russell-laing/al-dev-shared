import sys
import json
sys.path.insert(0, '/Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/plugin-health')

from schemas import CheckpointState, WorkQueue, WorkQueueLens

def test_checkpoint_roundtrip():
    """Checkpoint must serialize/deserialize without loss."""
    original = CheckpointState(
        run_id="2026-05-31-001",
        team_id="team-uuid-123",
        surface="both",
        dimension="all",
        spawned_at="2026-05-31T14:30:00Z",
        completed_lenses=["design-agent-lens-tool-hygiene"],
        status="dispatched"
    )

    # Serialize to dict
    data = original.to_dict()

    # Serialize to JSON and back
    json_str = json.dumps(data)
    loaded_data = json.loads(json_str)

    # Deserialize
    restored = CheckpointState.from_dict(loaded_data)

    assert restored.run_id == original.run_id
    assert restored.team_id == original.team_id
    assert restored.completed_lenses == original.completed_lenses
    assert restored.status == original.status
    print("✓ test_checkpoint_roundtrip PASSED")

def test_work_queue_roundtrip():
    """WorkQueue must serialize/deserialize without loss."""
    lens = WorkQueueLens(
        name="design-agent-lens-tool-hygiene",
        agent_name="design-agent-lens-tool-hygiene",
        files=["agent1.md", "agent2.md"],
        context_fields=["tool_inventory"]
    )
    queue = WorkQueue(
        surface="plugin",
        dimension="design",
        agent_files=["agent1.md", "agent2.md"],
        skill_files=[],
        context={"tool_inventory": {"Agent1": ["Tool1", "Tool2"]}},
        lenses=[lens]
    )

    # Roundtrip
    data = queue.to_dict()
    json_str = json.dumps(data)
    loaded_data = json.loads(json_str)
    restored = WorkQueue.from_dict(loaded_data)

    assert restored.surface == queue.surface
    assert len(restored.lenses) == 1
    assert restored.lenses[0].name == lens.name
    print("✓ test_work_queue_roundtrip PASSED")

if __name__ == "__main__":
    test_checkpoint_roundtrip()
    test_work_queue_roundtrip()
    print("\nAll schema tests passed!")
