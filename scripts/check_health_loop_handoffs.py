#!/usr/bin/env python3
"""Regression guard for the health-audit loop handoff chain.

Fails (exit 1) unless every loop skill both reads and writes the
.dev/health-loop-state.md breadcrumb, and plan-health-findings overrides the
writing-plans Execution Handoff by naming /implement-health-plan after the
writing-plans invocation. Run from the repo root.

This is a STATIC TEXT guard: it verifies the handoff instructions are present
and positioned, not that the override fires at runtime. A PASS means the wiring
text is in place; confirm actual loop closure in a live run.
"""
import pathlib
import sys

SKILLS = pathlib.Path(".claude/skills")
STATE = ".dev/health-loop-state.md"
CONTRACT = pathlib.Path(".claude/knowledge/health-loop-state-contract.md")

LOOP = [
    "plugin-health-report",
    "record-health-dispositions",
    "plan-health-findings",
    "implement-health-plan",
]

errors = []

if not CONTRACT.exists():
    errors.append(f"missing contract doc {CONTRACT}")

for name in LOOP:
    path = SKILLS / name / "SKILL.md"
    if not path.exists():
        errors.append(f"{name}: SKILL.md not found at {path}")
        continue
    body = path.read_text()
    refs = body.count(STATE)
    if refs < 2:
        errors.append(
            f"{name}: must both read (Phase 0) and write {STATE} "
            f"(found {refs} reference(s), need >= 2)"
        )

phf_path = SKILLS / "plan-health-findings" / "SKILL.md"
if phf_path.exists():
    phf = phf_path.read_text()
    wp = phf.find("superpowers:writing-plans")
    ihp = phf.rfind("implement-health-plan")
    if wp == -1:
        errors.append("plan-health-findings: writing-plans invocation not found")
    elif ihp == -1 or ihp < wp:
        errors.append(
            "plan-health-findings: must reference /implement-health-plan AFTER "
            "the writing-plans invocation (the override handoff)"
        )
    if phf.count("Execution Handoff") < 2:
        errors.append(
            "plan-health-findings: must reference 'Execution Handoff' at least "
            "twice — once to suppress it in Phase 3, once as the authoritative "
            f"ending in Phase 4 (found {phf.count('Execution Handoff')})"
        )

if errors:
    print("HEALTH LOOP HANDOFF CHECK: FAIL")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("HEALTH LOOP HANDOFF CHECK: PASS")
sys.exit(0)
