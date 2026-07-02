#!/usr/bin/env python3
"""Regression guard for the health-audit loop handoff chain.

Fails (exit 1) unless every loop skill both reads and writes the
.dev/health-loop-state.md breadcrumb, and plan-plugin-findings overrides the
writing-plans Execution Handoff by naming /implement-plugin-health after the
writing-plans invocation. Run from the repo root.

This is a STATIC TEXT guard: it verifies the handoff instructions are present
and positioned, not that the override fires at runtime. A PASS means the wiring
text is in place; confirm actual loop closure in a live run.
"""
import pathlib
import sys

STATE = ".dev/health-loop-state.md"

LOOP = [
    "discover-plugin-health",
    "report-plugin-health",
    "record-plugin-dispositions",
    "plan-plugin-findings-verify",
    "plan-plugin-findings",
    "implement-plugin-health",
]

def main(repo_root: pathlib.Path | None = None) -> int:
    root = pathlib.Path.cwd() if repo_root is None else pathlib.Path(repo_root)
    skills_root = root / ".claude" / "skills"
    contract = root / ".claude" / "knowledge" / "health-loop-state-contract.md"
    errors = []

    if not contract.exists():
        errors.append(f"missing contract doc {contract}")

    for name in LOOP:
        path = skills_root / name / "SKILL.md"
        if not path.exists():
            errors.append(f"{name}: SKILL.md not found at {path}")
            continue
        body = path.read_text(encoding="utf-8")
        refs = body.count(STATE)
        if refs < 2:
            errors.append(
                f"{name}: must both read (Phase 0) and write {STATE} "
                f"(found {refs} reference(s), need >= 2)"
            )

    phf_path = skills_root / "plan-plugin-findings" / "SKILL.md"
    if phf_path.exists():
        phf = phf_path.read_text(encoding="utf-8")
        wp = phf.find("superpowers:writing-plans")
        ihp = phf.rfind("implement-plugin-health")
        if wp == -1:
            errors.append("plan-plugin-findings: writing-plans invocation not found")
        elif ihp == -1 or ihp < wp:
            errors.append(
                "plan-plugin-findings: must reference /implement-plugin-health AFTER "
                "the writing-plans invocation (the override handoff)"
            )
        if phf.count("Execution Handoff") < 2:
            errors.append(
                "plan-plugin-findings: must reference 'Execution Handoff' at least "
                "twice — once to suppress it in Phase 3, once as the authoritative "
                f"ending in Phase 4 (found {phf.count('Execution Handoff')})"
            )

    if errors:
        print("HEALTH LOOP HANDOFF CHECK: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("HEALTH LOOP HANDOFF CHECK: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
