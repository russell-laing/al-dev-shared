import os
import json
from datetime import datetime
from pathlib import Path
import uuid
import sys
sys.path.insert(0, '/Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/plugin-health')

from schemas import CheckpointState, WorkQueue, WorkQueueLens

def validate_arguments(surface: str, dimension: str) -> tuple[bool, str]:
    """Validate surface and dimension flags."""
    valid_surfaces = {"plugin", "tooling", "both"}
    valid_dimensions = {"design", "quality", "all"}

    if surface not in valid_surfaces:
        return False, f"Invalid surface '{surface}'. Must be one of {valid_surfaces}"
    if dimension not in valid_dimensions:
        return False, f"Invalid dimension '{dimension}'. Must be one of {valid_dimensions}"

    return True, ""

def load_checkpoint(checkpoint_path: str) -> CheckpointState | None:
    """Load existing checkpoint if it exists and is valid."""
    path = Path(checkpoint_path)
    if not path.exists():
        return None

    try:
        with open(path, "r") as f:
            data = json.load(f)
        return CheckpointState.from_dict(data)
    except Exception as e:
        print(f"Warning: Failed to load checkpoint: {e}")
        return None

def save_checkpoint(checkpoint: CheckpointState, checkpoint_path: str) -> bool:
    """Save checkpoint to disk."""
    try:
        path = Path(checkpoint_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(checkpoint.to_dict(), f, indent=2)
        return True
    except Exception as e:
        print(f"Error: Failed to save checkpoint: {e}")
        return False

def build_file_lists(surface: str) -> tuple[list[str], list[str]]:
    """Build lists of agent and skill files based on surface."""
    repo_root = Path("/Users/russelllaing/al-dev-shared")

    agent_files = []
    skill_files = []

    if surface in {"plugin", "both"}:
        # Shared plugin surface agents
        agents_dir = repo_root / "profile-al-dev-shared" / "agents"
        if agents_dir.exists():
            agent_files.extend([str(f.relative_to(repo_root)) for f in agents_dir.glob("*.md")])

        # Shared plugin surface skills
        skills_dir = repo_root / "profile-al-dev-shared" / "skills"
        if skills_dir.exists():
            skill_files.extend([str(f.relative_to(repo_root)) for f in skills_dir.glob("*/SKILL.md")])

    if surface in {"tooling", "both"}:
        # Maintainer tooling agents
        tooling_agents_dir = repo_root / ".claude" / "agents"
        if tooling_agents_dir.exists():
            agent_files.extend([str(f.relative_to(repo_root)) for f in tooling_agents_dir.glob("*.md")])

        # Maintainer tooling skills
        tooling_skills_dir = repo_root / ".claude" / "skills"
        if tooling_skills_dir.exists():
            skill_files.extend([str(f.relative_to(repo_root)) for f in tooling_skills_dir.glob("*/SKILL.md")])

    return sorted(agent_files), sorted(skill_files)

def build_context_aggregation(agent_files: list[str], skill_files: list[str]) -> dict:
    """Pre-aggregate context from documentation maps and codebase.

    This would normally read:
    - docs/al-dev-agent-map.md to extract tool inventory, model assignments, caller map
    - docs/al-dev-plugin-map.md to extract layer 1 diagram, phase counts, handoff chains

    For now, return a stub that lenses can populate as needed.
    """
    return {
        "tool_inventory": {},
        "model_assignments": {},
        "caller_map": {},
        "agent_usage_counts": {},
        "phase_counts": {},
        "handoff_chains": {},
        "preplanning_skills": [],
        "layer1_diagram_content": "",
        "agent_files": agent_files,
        "skill_files": skill_files,
    }

def determine_lenses_for_scope(surface: str, dimension: str) -> list[WorkQueueLens]:
    """Determine which lenses to run based on surface and dimension."""
    lenses = []

    # Design lenses
    if dimension in {"design", "all"}:
        if surface in {"plugin", "both"}:
            # Agent design lenses
            lenses.extend([
                WorkQueueLens(
                    name="design-agent-lens-tool-hygiene",
                    agent_name="design-agent-lens-tool-hygiene",
                    files=[],  # Will be populated
                    context_fields=["tool_inventory"]
                ),
                WorkQueueLens(
                    name="design-agent-lens-model-fit",
                    agent_name="design-agent-lens-model-fit",
                    files=[],
                    context_fields=["model_assignments"]
                ),
                WorkQueueLens(
                    name="design-agent-lens-scope-isolation",
                    agent_name="design-agent-lens-scope-isolation",
                    files=[],
                    context_fields=[]
                ),
                WorkQueueLens(
                    name="design-agent-lens-caller-alignment",
                    agent_name="design-agent-lens-caller-alignment",
                    files=[],
                    context_fields=["caller_map"]
                ),
                WorkQueueLens(
                    name="design-agent-lens-usage-patterns",
                    agent_name="design-agent-lens-usage-patterns",
                    files=[],
                    context_fields=["agent_usage_counts"]
                ),
            ])

            # Skill design lenses
            lenses.extend([
                WorkQueueLens(
                    name="design-skill-lens-complexity",
                    agent_name="design-skill-lens-complexity",
                    files=[],
                    context_fields=["phase_counts"]
                ),
                WorkQueueLens(
                    name="design-skill-lens-handoff-gaps",
                    agent_name="design-skill-lens-handoff-gaps",
                    files=[],
                    context_fields=["handoff_chains"]
                ),
                WorkQueueLens(
                    name="design-skill-lens-near-duplicates",
                    agent_name="design-skill-lens-near-duplicates",
                    files=[],
                    context_fields=[]
                ),
                WorkQueueLens(
                    name="design-skill-lens-preplanning",
                    agent_name="design-skill-lens-preplanning",
                    files=[],
                    context_fields=["preplanning_skills"]
                ),
                WorkQueueLens(
                    name="design-skill-lens-shared-backbone",
                    agent_name="design-skill-lens-shared-backbone",
                    files=[],
                    context_fields=[]
                ),
            ])

    # Quality lenses
    if dimension in {"quality", "all"}:
        if surface in {"plugin", "both"}:
            # Agent quality lenses
            lenses.extend([
                WorkQueueLens(
                    name="quality-agent-lens-bloat",
                    agent_name="quality-agent-lens-bloat",
                    files=[],
                    context_fields=[]
                ),
                WorkQueueLens(
                    name="quality-agent-lens-clarity",
                    agent_name="quality-agent-lens-clarity",
                    files=[],
                    context_fields=[]
                ),
                WorkQueueLens(
                    name="quality-agent-lens-description",
                    agent_name="quality-agent-lens-description",
                    files=[],
                    context_fields=[]
                ),
                WorkQueueLens(
                    name="quality-agent-lens-name-fit",
                    agent_name="quality-agent-lens-name-fit",
                    files=[],
                    context_fields=[]
                ),
                WorkQueueLens(
                    name="quality-agent-lens-structure",
                    agent_name="quality-agent-lens-structure",
                    files=[],
                    context_fields=[]
                ),
            ])

            # Skill quality lenses
            lenses.extend([
                WorkQueueLens(
                    name="quality-skill-lens-bloat",
                    agent_name="quality-skill-lens-bloat",
                    files=[],
                    context_fields=[]
                ),
                WorkQueueLens(
                    name="quality-skill-lens-clarity",
                    agent_name="quality-skill-lens-clarity",
                    files=[],
                    context_fields=[]
                ),
                WorkQueueLens(
                    name="quality-skill-lens-description",
                    agent_name="quality-skill-lens-description",
                    files=[],
                    context_fields=[]
                ),
                WorkQueueLens(
                    name="quality-skill-lens-name-fit",
                    agent_name="quality-skill-lens-name-fit",
                    files=[],
                    context_fields=[]
                ),
                WorkQueueLens(
                    name="quality-skill-lens-structure",
                    agent_name="quality-skill-lens-structure",
                    files=[],
                    context_fields=[]
                ),
            ])

    return lenses

def build_work_queue(surface: str, dimension: str, agent_files: list[str], skill_files: list[str]) -> WorkQueue:
    """Build the complete work queue for remote team execution."""
    context = build_context_aggregation(agent_files, skill_files)
    lenses = determine_lenses_for_scope(surface, dimension)

    # Populate file lists in lenses
    for lens in lenses:
        if "agent" in lens.name.lower():
            lens.files = agent_files
        elif "skill" in lens.name.lower():
            lens.files = skill_files

    return WorkQueue(
        surface=surface,
        dimension=dimension,
        agent_files=agent_files,
        skill_files=skill_files,
        context=context,
        lenses=lenses
    )

def generate_run_id() -> str:
    """Generate a unique run ID."""
    timestamp = datetime.now().isoformat().replace(":", "").replace("-", "")[:14]
    unique_suffix = str(uuid.uuid4())[:8]
    return f"{timestamp}-{unique_suffix}"

def write_run_artifacts(run_id: str, work_queue: WorkQueue) -> str:
    """Write work queue and manifest scaffold to repo-owned run directory."""
    repo_root = Path("/Users/russelllaing/al-dev-shared")
    run_dir = repo_root / ".dev" / "plugin-health-runs" / run_id

    try:
        run_dir.mkdir(parents=True, exist_ok=True)

        # Write work queue
        work_queue_path = run_dir / "work-queue.json"
        with open(work_queue_path, "w") as f:
            json.dump(work_queue.to_dict(), f, indent=2)

        # Write manifest scaffold
        manifest = {
            "run_id": run_id,
            "team_id": "",  # Will be filled by remote team
            "status": "dispatched",
            "total_lenses": len(work_queue.lenses),
            "completed": [],
            "pending": [lens.name for lens in work_queue.lenses],
            "failed": []
        }
        manifest_path = run_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        return str(run_dir)
    except Exception as e:
        print(f"Error: Failed to write run artifacts: {e}")
        raise

def dispatch_work(surface: str, dimension: str, resume: bool) -> tuple[bool, str]:
    """Main dispatch orchestration.

    Returns: (success: bool, message: str)
    """
    # Validate arguments
    valid, error = validate_arguments(surface, dimension)
    if not valid:
        return False, error

    repo_root = Path("/Users/russelllaing/al-dev-shared")
    checkpoint_path = repo_root / ".dev" / "plugin-health-team-checkpoint.json"

    # Check for prior checkpoint if resuming
    if resume:
        prior_checkpoint = load_checkpoint(str(checkpoint_path))
        if prior_checkpoint is None:
            return False, "No resumable plugin-health run found. Start a new sweep with /plugin-health."
        print(f"Resuming prior run: team_id={prior_checkpoint.team_id}, run_id={prior_checkpoint.run_id}")
        # TODO: Collection phase would use this checkpoint
        return True, f"Resume detection working. Would fetch results for {prior_checkpoint.run_id}."

    # Build file lists
    agent_files, skill_files = build_file_lists(surface)
    print(f"Found {len(agent_files)} agents, {len(skill_files)} skills")

    # Build work queue
    work_queue = build_work_queue(surface, dimension, agent_files, skill_files)
    print(f"Work queue: {len(work_queue.lenses)} lenses to execute")

    # Write run artifacts
    run_id = generate_run_id()
    run_dir = write_run_artifacts(run_id, work_queue)
    print(f"Run artifacts written to {run_dir}")

    # Create checkpoint
    team_id = str(uuid.uuid4())  # Would be assigned by remote team manager
    checkpoint = CheckpointState(
        run_id=run_id,
        team_id=team_id,
        surface=surface,
        dimension=dimension,
        spawned_at=datetime.now().isoformat(),
        status="dispatched",
        result_dir=run_dir,
        manifest_path=str(Path(run_dir) / "manifest.json"),
        pending_lenses=[lens.name for lens in work_queue.lenses]
    )

    # Save checkpoint
    if not save_checkpoint(checkpoint, str(checkpoint_path)):
        return False, "Failed to save checkpoint"

    print(f"Checkpoint saved: {checkpoint_path}")
    print(f"Team ID: {team_id}")

    return True, f"Dispatched health sweep team {team_id}. Lenses running in background. Re-run /plugin-health --resume when you want to collect results."
