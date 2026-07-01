"""User-journey rendering helpers for maintainer tooling docs."""

from __future__ import annotations

from bisect import insort

from .maintainer_analysis import is_user_invocable
from .maintainer_contracts import CORE_STAGES, STAGE_TITLES, WorkflowContract


def _first_sentence(description: str) -> str:
    text = " ".join(description.split())
    if not text:
        return "(no description)"
    if ". " in text:
        return text.split(". ", 1)[0] + "."
    return text if text.endswith(".") else text + "."


def _topo_order(stage_contracts: list[WorkflowContract]) -> list[WorkflowContract]:
    """Kahn's algorithm over same-stage next edges, alphabetical tie-break, cycle fallback."""
    by_name = {c.skill: c for c in stage_contracts}
    names = set(by_name)
    indegree = {name: 0 for name in names}
    for contract in stage_contracts:
        for target in sorted(set(contract.next_skills)):
            if target in names and target != contract.skill:
                indegree[target] += 1
    ready = sorted(name for name, degree in indegree.items() if degree == 0)
    order: list[WorkflowContract] = []
    placed: set[str] = set()
    while ready:
        current = ready.pop(0)
        order.append(by_name[current])
        placed.add(current)
        for target in sorted(set(by_name[current].next_skills)):
            if target in indegree and target not in placed and target != current:
                indegree[target] -= 1
                if indegree[target] == 0:
                    insort(ready, target)
    for name in sorted(names - placed):
        order.append(by_name[name])
    return order


def render_user_journey(contracts: list[WorkflowContract]) -> str:
    """Numbered per-stage step list of user-invoked skills in next-chain order."""
    sections: list[str] = []
    for stage in CORE_STAGES:
        stage_user = [c for c in contracts if c.stage == stage and is_user_invocable(c)]
        if not stage_user:
            continue
        lines = [f"### {STAGE_TITLES[stage]} steps", ""]
        step = 0
        for contract in _topo_order(stage_user):
            step += 1
            repeat = " Repeat as needed." if contract.repeatable else ""
            lines.append(f"{step}. `/{contract.skill}` — {_first_sentence(contract.description)}{repeat}")
            if contract.inputs:
                lines.append("   - reads: " + ", ".join(f"`{t}`" for t in contract.inputs))
            if contract.outputs:
                lines.append("   - writes: " + ", ".join(f"`{t}`" for t in contract.outputs))
            if contract.manual_followup:
                step += 1
                lines.append(f"{step}. Manual step: {contract.manual_followup}.")
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def render_stage_journey(contracts: list[WorkflowContract], stage: str) -> str:
    stage_user = [c for c in contracts if c.stage == stage and is_user_invocable(c)]
    if not stage_user:
        return "No user-invoked skills in this stage declare a `workflow:` contract yet."
    by_name = {contract.skill: contract for contract in stage_user}

    def command(name: str, suffix: str = "") -> str:
        contract = by_name[name]
        return f"`/{name}{suffix}` — {_first_sentence(contract.description)}"

    if stage == "map-sync" and {"sync-map-documentation", "sync-map-documentation-collect", "sync-map-documentation-apply", "sync-map-documentation-write"} <= set(by_name):
        return "\n".join(
            [
                "### Primary path",
                "",
                "1. " + command("sync-map-documentation"),
                "2. " + command("sync-map-documentation-collect"),
                "3. " + command("sync-map-documentation-apply"),
                "4. " + command("sync-map-documentation-write"),
            ]
        )
    if stage == "discover" and {
        "ingest-plugin-friction",
        "audit-plugin-health",
        "discover-plugin-health",
        "report-plugin-health",
    } <= set(by_name):
        return "\n".join(
            [
                "### Audit-driven path",
                "",
                "1. " + command("audit-plugin-health"),
                "2. `/discover-plugin-health` dispatches the lenses and writes standard findings.",
                "3. `/report-plugin-health --findings <path>` verifies and ranks those findings into a dossier.",
                "",
                "### Friction-driven path",
                "",
                "1. " + command("ingest-plugin-friction"),
                "2. `/report-plugin-health --findings <path>` consumes the explicit friction findings path; automatic findings selection intentionally does not match this artifact family.",
            ]
        )
    if stage == "decide" and {
        "record-plugin-dispositions",
        "plan-plugin-findings",
        "revise-plugin-plan",
    } <= set(by_name):
        return "\n".join(
            [
                "### Primary path",
                "",
                "1. " + command("record-plugin-dispositions"),
                "2. " + command("plan-plugin-findings"),
                "",
                "### Optional revision path",
                "",
                "Run `/revise-plugin-plan` only when a separate review or commentary artifact requires the plan and ledger decisions to be reconciled before implementation.",
            ]
        )
    if stage == "implement" and "implement-plugin-health" in by_name:
        return "\n".join(
            [
                "### Primary path",
                "",
                "1. Run `/implement-plugin-health --plan <path>` in the fresh session named by the breadcrumb.",
                "2. Execute and verify each plan task, preserving the progress checkpoint for recovery.",
                "3. Append `fixed` disposition events to the JSONL event store, archive consumed health artifacts, and commit `next_command: none` with the close-back.",
            ]
        )
    if stage == "derive":
        if {
            "regenerate-agent-projections",
            "audit-knowledge-quality",
            "fix-knowledge-quality",
            "audit-plugin-neutrality",
        } <= set(by_name):
            return "\n".join(
                [
                    "### Agent source changed",
                    "",
                    "1. Run `/regenerate-agent-projections` to validate authored agents and regenerate harness-native projections.",
                    "2. Run `/audit-plugin-neutrality` to verify the shared source remains harness-neutral.",
                    "",
                    "### Knowledge source changed",
                    "",
                    "1. Run `/audit-knowledge-quality`.",
                    "2. If HIGH findings exist and are approved, run `/fix-knowledge-quality`.",
                    "3. Re-run the applicable quality and neutrality checks after fixes.",
                    "",
                    "### Any shared source changed",
                    "",
                    "Run `/audit-plugin-neutrality` after edits to shared skills, agents, or knowledge. In a health-plan run, Implement handles its supported projection and neutrality checks before loop closure; Derive is not another breadcrumb-controlled step.",
                ]
            )

    lines = ["### Primary path", ""]
    for step, contract in enumerate(_topo_order(stage_user), start=1):
        lines.append(f"{step}. `/{contract.skill}` — {_first_sentence(contract.description)}")
        if contract.manual_followup:
            lines.append(f"{step + 1}. Manual step: {contract.manual_followup}.")
    return "\n".join(lines)


__all__ = [
    "_first_sentence",
    "_topo_order",
    "render_stage_journey",
    "render_user_journey",
]
