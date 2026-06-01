from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from datetime import datetime
import json

@dataclass
class CheckpointState:
    """Durable checkpoint for plugin-health dispatch and resume."""
    run_id: str                          # Unique run identifier (timestamp or UUID)
    team_id: str                         # Remote agent team ID
    surface: str                         # "plugin" | "tooling" | "both"
    dimension: str                       # "design" | "quality" | "all"
    spawned_at: str                      # ISO 8601 timestamp
    collected_at: str = ""               # ISO 8601 timestamp, empty if not yet collected
    completed_lenses: List[str] = field(default_factory=list)  # Lens names completed
    pending_lenses: List[str] = field(default_factory=list)    # Lens names not yet run
    failed_lenses: List[Dict[str, str]] = field(default_factory=list)  # [{"name": "...", "error": "..."}]
    status: str = "dispatched"           # "dispatched" | "collecting" | "collected" | "partial"
    result_dir: str = ""                 # Path to .dev/plugin-health-runs/<run-id>
    manifest_path: str = ""              # Path to manifest.json
    findings_file: str = ""              # Path to findings markdown file
    dossier_file: str = ""               # Path to dossier markdown file

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for JSON storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CheckpointState":
        """Deserialize from dict loaded from JSON."""
        return cls(**data)

@dataclass
class WorkQueueLens:
    """Single lens entry in the work queue."""
    name: str                            # "design-agent-lens-tool-hygiene"
    agent_name: str                      # Agent to invoke (for team dispatcher)
    files: List[str]                     # Files to analyze
    context_fields: List[str]            # Context keys to pass (e.g., ["tool_inventory"])

@dataclass
class WorkQueue:
    """Distributed work queue for remote agent team."""
    surface: str                         # "plugin" | "tooling" | "both"
    dimension: str                       # "design" | "quality" | "all"
    agent_files: List[str]               # Paths to agents being analyzed
    skill_files: List[str]               # Paths to skills being analyzed
    context: Dict[str, Any]              # Pre-aggregated context (tool_inventory, model_assignments, etc.)
    lenses: List[WorkQueueLens]          # Lens definitions with file subsets

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface": self.surface,
            "dimension": self.dimension,
            "agent_files": self.agent_files,
            "skill_files": self.skill_files,
            "context": self.context,
            "lenses": [asdict(lens) for lens in self.lenses],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkQueue":
        lenses = [WorkQueueLens(**lens) for lens in data.pop("lenses", [])]
        return cls(lenses=lenses, **data)

@dataclass
class ManifestEntry:
    """Entry in the team progress manifest."""
    name: str                            # Lens name
    status: str                          # "pending" | "success" | "failed" | "timeout"
    timestamp: str = ""                  # ISO 8601 when status was set
    error: str = ""                      # Error message if failed

@dataclass
class ExecutionManifest:
    """Progress manifest maintained by remote team."""
    team_id: str
    run_id: str
    status: str                          # "dispatched" | "in_progress" | "completed" | "partial" | "failed"
    total_lenses: int
    completed: List[Dict[str, str]] = field(default_factory=list)  # [{"name": "...", "status": "...", "timestamp": "..."}]
    pending: List[str] = field(default_factory=list)               # Lens names not yet run
    failed: List[Dict[str, str]] = field(default_factory=list)     # [{"name": "...", "error": "..."}]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionManifest":
        return cls(**data)
