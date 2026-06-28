"""Markdown table rendering helpers for maintainer tooling docs."""

from __future__ import annotations

from .maintainer_contracts import STAGES, WorkflowContract
from .maintainer_journey import _first_sentence


def _md_cell(text: str) -> str:
    """Escape a pipe so free text is safe inside a GFM table cell."""
    return text.replace("|", "\\|")


def render_skills_tables(contracts: list[WorkflowContract]) -> str:
    ordered = sorted(contracts, key=lambda c: (STAGES.index(c.stage), c.skill))
    glance = [
        "### Skills at a glance",
        "",
        "| Skill | Stage | Invoked by | Role |",
        "| --- | --- | --- | --- |",
    ]
    for contract in ordered:
        glance.append(
            f"| `/{contract.skill}` | {contract.stage} | {contract.invoked_by} "
            f"| {_md_cell(_first_sentence(contract.description))} |"
        )

    def cell(values: tuple[str, ...]) -> str:
        return ", ".join(f"`{v}`" for v in values) if values else "—"

    io = [
        "### Inputs and outputs",
        "",
        "| Skill | Reads | Writes | Next |",
        "| --- | --- | --- | --- |",
    ]
    for contract in ordered:
        next_cell = (
            ", ".join(f"`/{t}`" for t in contract.next_skills) if contract.next_skills else "—"
        )
        io.append(
            f"| `/{contract.skill}` | {cell(contract.inputs)} | {cell(contract.outputs)} "
            f"| {next_cell} |"
        )
    return "\n".join(glance) + "\n\n" + "\n".join(io)


STAGE_ARTIFACTS: dict[str, tuple[tuple[str, str], ...]] = {
    "map-sync": (
        (
            "docs/al-dev-skills-map.md` and `docs/al-dev-agent-map.md",
            "Canonical inventory maps audited and updated by the stage.",
        ),
        (
            ".dev/sync-map-documentation-checkpoint.json",
            "Records the active run, team identifiers, and current async phase.",
        ),
        (
            ".dev/sync-map-documentation-runs/RUN_ID/",
            "Keeps raw audit results and validated update artifacts separate from the canonical maps.",
        ),
        (
            "docs/al-dev-workflow-diagrams.md`, `docs/al-dev-plugin-graph.md`, `docs/maintainer-tooling.md`, and `docs/maintainer-tooling/",
            "Derived documentation regenerated only after the canonical maps are applied.",
        ),
        (
            "profile-al-dev-shared/generated/agents/",
            "Harness-native projections regenerated from canonical shared agent source.",
        ),
    ),
    "discover": (
        (
            "docs/al-dev-skills-map.md` and `docs/al-dev-agent-map.md",
            "Provide current inventory and relationship context to the audit-driven path.",
        ),
        (
            "docs/health/<date>-<surface>-findings.md",
            "Stores raw lens findings before report-time evidence checks and ranking.",
        ),
        (
            "docs/health/<date>-<surface>-friction-findings.md",
            "Carries friction-derived findings into report through an explicit `--findings` path.",
        ),
        (
            ".dev/health-loop-state.md",
            "Persists the exact report handoff across sessions.",
        ),
        (
            "docs/health/dispositions-open.md",
            "Lets report suppress or re-verify findings that already have durable decisions.",
        ),
        (
            "docs/health/<date>-<surface>-health.md",
            "The ranked dossier handed to the Decide stage.",
        ),
    ),
    "decide": (
        (
            "docs/health/<date>-<surface>-health.md",
            "Presents the verified findings that require a maintainer decision.",
        ),
        (
            "docs/health/dispositions-events/YYYY/YYYY-MM.jsonl` (canonical) + `docs/health/dispositions-open.md",
            "Canonical event store for decisions; dispositions-open.md is the generated open-items read view.",
        ),
        (
            "profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md",
            "Defines the live verification checks used before accepted findings become plan tasks.",
        ),
        (
            "docs/superpowers/plans/<date>-<topic>.md",
            "Carries the verified implementation tasks and required `closes_event_ids:` identifiers.",
        ),
        (
            "docs/superpowers/plans/<date>-<topic>-commentary.md",
            "Optional review evidence used only when the plan must be revised.",
        ),
    ),
    "implement": (
        (
            "docs/superpowers/plans/<date>-<topic>.md",
            "The approved execution contract; each task must name the event IDs it closes via `closes_event_ids:`.",
        ),
        (
            ".dev/implement-plugin-health-progress.md",
            "Supports recovery by recording completed tasks and their commits.",
        ),
        (
            "docs/health/dispositions-events/YYYY/YYYY-MM.jsonl",
            "Receives the fixed close-back events that prove accepted work was completed; generated views regenerate from the event store.",
        ),
        (
            ".dev/health-loop-state.md",
            "Closes the core loop with `next_command: none` in the ledger-close commit.",
        ),
        (
            "docs/health/archived/` and `docs/superpowers/plans/archived/",
            "Retain consumed findings, dossiers, plans, and review evidence outside live selectors.",
        ),
    ),
    "derive": (
        (
            "profile-al-dev-shared/agents/",
            "Canonical authored agent source.",
        ),
        (
            "profile-al-dev-shared/generated/agents/",
            "Generated harness-native projections; never edit these files directly.",
        ),
        (
            "profile-al-dev-shared/knowledge/",
            "Canonical shared guidance audited for structural and semantic quality.",
        ),
        (
            "docs/al-dev-knowledge-quality.md",
            "Records knowledge findings and the structured HIGH-severity fix task block.",
        ),
        (
            "scripts/validate_harness_neutrality.py",
            "Checks shared skills, agents, and knowledge for harness-specific leakage.",
        ),
    ),
}


def render_stage_artifacts(contracts: list[WorkflowContract], stage: str) -> str:
    if not any(contract.stage == stage for contract in contracts):
        return "No key artifacts are declared for this stage."
    lines = ["| Artifact | Role |", "| --- | --- |"]
    for artifact, role in STAGE_ARTIFACTS[stage]:
        lines.append(f"| `{artifact}` | {role} |")
    return "\n".join(lines)


SIGNAL_ORDER = (
    ("orphaned-artifact", "Orphaned artifact"),
    ("sourceless-input", "Sourceless input"),
    ("manual-step", "Manual step"),
    ("missing-contract", "Missing contract"),
    ("stale-artifact", "Artifact freshness"),
    ("internal-only", "Internal-only skill"),
)


def render_gaps_table(gaps: dict[str, list[tuple[str, str]]]) -> str:
    lines = [
        "| Signal | Item | Detail |",
        "| --- | --- | --- |",
    ]
    for key, title in SIGNAL_ORDER:
        rows = gaps[key]
        if not rows:
            lines.append(f"| {title} | none | — |")
            continue
        for item, detail in rows:
            lines.append(f"| {title} | `{item}` | {detail} |")
    return "\n".join(lines)

__all__ = [
    "SIGNAL_ORDER",
    "STAGE_ARTIFACTS",
    "_md_cell",
    "render_gaps_table",
    "render_skills_tables",
    "render_stage_artifacts",
]
