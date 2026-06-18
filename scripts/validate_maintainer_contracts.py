#!/usr/bin/env python3
"""Assert that maintainer skills reference the repo-local contract docs.

Coverage gate for the phase-proof, dispatch-fallback, and delegated-scope-pack
contracts. Report mode only; exits 1 when any required reference is missing.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / ".claude" / "skills"

PHASE_PROOF_DOC = "phase-proof-contract.md"
DISPATCH_DOC = "dispatch-fallback-contract.md"
SCOPE_PACK_DOC = "delegated-scope-pack.md"

# Authoritative scope sets. Update deliberately when a skill changes shape.
MULTI_PHASE_SKILLS = {
    "plugin-health-audit", "plugin-health-discover", "plugin-health-report",
    "plan-health-findings", "record-health-dispositions", "implement-health-plan",
    "revise-health-plan", "sync-documentation-maps", "sync-documentation-maps-collect",
    "sync-documentation-maps-apply", "sync-documentation-maps-write",
    "audit-knowledge-quality", "fix-knowledge-quality", "ingest-friction-log",
    "al-dev-consolidate", "review-docs", "align-harness-repos", "projection-sync",
}
# 18 of the 19 live phase-bearing skills. `verify-files` is excluded as a pure
# read-only verifier (no mutating phase deliverable). `plugin-health-audit` is
# included: it advances discover→report across a session boundary and writes the
# health-loop breadcrumb, the exact phantom-phase-progress surface this contract guards.
DISPATCHING_SKILLS = {
    "plugin-health-discover", "plugin-health-report", "plan-health-findings",
    "sync-documentation-maps", "audit-knowledge-quality", "fix-knowledge-quality",
}
# `plugin-health-report` dispatches `health-rubber-duck` agents in evidence mode
# via superpowers:dispatching-parallel-agents — a real dispatch lane.
DELEGATING_EXECUTION_SKILLS = {
    "sync-documentation-maps-collect",
}
# `implement-health-plan` is intentionally absent: it executes inline, one task at
# a time, and explicitly rejects subagent dispatch — wiring a delegated-scope-pack
# contract into it would contradict its own execution mode.

REQUIREMENTS = [
    (MULTI_PHASE_SKILLS, PHASE_PROOF_DOC),
    (DISPATCHING_SKILLS, DISPATCH_DOC),
    (DELEGATING_EXECUTION_SKILLS, SCOPE_PACK_DOC),
]


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
