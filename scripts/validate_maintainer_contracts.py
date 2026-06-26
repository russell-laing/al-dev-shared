#!/usr/bin/env python3
"""Assert that maintainer skills reference the repo-local contract docs.

Coverage gate for the phase-proof, dispatch-fallback, and delegated-scope-pack
contracts. Report mode only; exits 1 when any required reference is missing.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / ".claude" / "skills"

PHASE_PROOF_DOC = "phase-proof-contract.md"
DISPATCH_DOC = "dispatch-fallback-contract.md"
SCOPE_PACK_DOC = "delegated-scope-pack.md"
MAINTAINER_CONTRACTS_HEADING = "## Maintainer Contracts"

# Authoritative scope sets. Update deliberately when a skill changes shape.
MULTI_PHASE_SKILLS = {
    "audit-plugin-health", "discover-plugin-health", "report-plugin-health",
    "plan-plugin-findings", "record-plugin-dispositions", "implement-plugin-health",
    "revise-plugin-plan", "sync-map-documentation", "sync-map-documentation-collect",
    "sync-map-documentation-apply", "sync-map-documentation-write",
    "audit-knowledge-quality", "fix-knowledge-quality", "ingest-plugin-friction",
    "al-dev-consolidate", "review-docs", "validate-plugin-neutrality", "regenerate-agent-projections",
}
# 18 of the 19 live phase-bearing skills. `verify-files` is excluded as a pure
# read-only verifier (no mutating phase deliverable). `audit-plugin-health` is
# included: it advances discover→report across a session boundary and writes the
# health-loop breadcrumb, the exact phantom-phase-progress surface this contract guards.
DISPATCHING_SKILLS = {
    "discover-plugin-health", "report-plugin-health", "plan-plugin-findings",
    "sync-map-documentation", "audit-knowledge-quality", "fix-knowledge-quality",
}
# `report-plugin-health` dispatches `verify-health-finding` agents in evidence mode
# via superpowers:dispatching-parallel-agents — a real dispatch lane.
DELEGATING_EXECUTION_SKILLS = {
    "sync-map-documentation-collect",
}
# `implement-plugin-health` is intentionally absent: it executes inline, one task at
# a time, and explicitly rejects subagent dispatch — wiring a delegated-scope-pack
# contract into it would contradict its own execution mode.

REQUIREMENTS = [
    (MULTI_PHASE_SKILLS, PHASE_PROOF_DOC),
    (DISPATCHING_SKILLS, DISPATCH_DOC),
    (DELEGATING_EXECUTION_SKILLS, SCOPE_PACK_DOC),
]


def has_markdown_heading(text: str, heading: str) -> bool:
    heading_re = re.compile(rf"^{re.escape(heading)}\s*$")
    in_fence = False
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or stripped.startswith(">"):
            continue
        if heading_re.match(line):
            return True
    return False


def check_coverage(skills_root: Path) -> list[str]:
    violations: list[str] = []
    for skill_set, doc in REQUIREMENTS:
        for name in sorted(skill_set):
            skill_md = skills_root / name / "SKILL.md"
            if not skill_md.exists():
                continue  # skill not present in this tree; not this gate's job
            text = skill_md.read_text(encoding="utf-8")
            # Enforce the relative-path link shape, not a bare-filename substring:
            # a contract is only "referenced" when linked as ../../knowledge/<doc>.
            ref = f"../../knowledge/{doc}"
            if ref not in text:
                violations.append(f"{name}: missing reference to {ref}")
    for name in sorted(DISPATCHING_SKILLS):
        skill_md = skills_root / name / "SKILL.md"
        if not skill_md.exists():
            continue
        text = skill_md.read_text(encoding="utf-8")
        if not has_markdown_heading(text, MAINTAINER_CONTRACTS_HEADING):
            violations.append(
                f"{name}: missing heading {MAINTAINER_CONTRACTS_HEADING}"
            )
    return violations


def main() -> int:
    violations = check_coverage(SKILLS_ROOT)
    if violations:
        print("Maintainer contract coverage: FAIL")
        for v in violations:
            print(f"  {v}")
        return 1
    print("Maintainer contract coverage: all required references present ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
