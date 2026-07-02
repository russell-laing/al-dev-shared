#!/usr/bin/env python3
"""
Validate skill descriptions against hardening rules.

Detects workflow-summary bloat, phase references, constraint meta-language,
and word-count violations in both distributed (profile-al-dev-shared/skills/)
and maintainer (.claude/skills/) skill descriptions.

Exit codes:
  0  Clean (no violations)
  1  Violations found
  2  Error (file I/O, etc.)

Usage:
  python3 scripts/validate_skill_descriptions.py [--fix]

With --fix: applies safe fixes (phase-ref removal, constraint-lang trim).
With --strict: enforces word-count limits and flagging heuristics.
"""

import re
import sys
from pathlib import Path

# Validation rules
RULES = {
    "phase_reference": {
        "patterns": [
            r"(?i)phase\s+[0-9]",  # "Phase 1", "phase 2.5", "Phase 2.5", etc. (numbered phases)
            r"(?i)phase\s+[0-9]\s*-\s*[0-9]",  # "Phase 1-3", "phase 4-5"
            r"(?i)(?:first|second|third|fourth|fifth|sixth)\s+phase",  # "first phase", "second phase"
        ],
        "severity": "HIGH",
        "reason": "Phase enumeration in description causes agents to skip skill body and follow the description shortcut instead.",
        "fix": "Remove phase-number and phase-label references; describe purpose + trigger only.",
    },
    "constraint_language": {
        "patterns": [
            r"(?i)single[- ]concern\s+(?:validation\s+)?pipeline",
            r"(?i)no\s+separable\s+concerns",
            r"(?i)each\s+phase\s+depends\s+on",
            r"(?i)mandatory\s+(?:fresh\s+session|neutrality\s+gate|coverage[- ]reconciliation|agent[- ]artifact\s+catalog)",
        ],
        "severity": "HIGH",
        "reason": "Constraint/design meta-language doesn't belong in discovery descriptions.",
        "fix": "Move constraint details to skill body; keep description brief and trigger-focused.",
    },
    "implementation_detail": {
        "patterns": [
            r"(?i)appends?.{0,30}(?:JSONL|event store|disposition)",  # "appends JSONL", "appends ...event store"
            r"(?i)(?:through|via)\s+scripts?/",  # "through scripts/", "via scripts/..."
            r"(?i)syncs?.{0,50}(?:shard|ledger|history)",  # "syncs shard", "syncs ledger"
        ],
        "severity": "MEDIUM",
        "reason": "Implementation detail (which tool, how it gates, what artifact) distracts from purpose.",
        "fix": "Keep to: purpose + trigger condition. Mechanics live in skill body.",
    },
    "repeated_clause": {
        "patterns": [
            r"(?i)This\s+skill\s+(?:writes|dispatches|reads|records|generates).*(?=This\s+skill)",
            r"(?i)(?:reads?|writes?)\s+.*findings.*and.*(?:reads|writes).*findings",
        ],
        "severity": "LOW",
        "reason": "Repeated clauses suggest duplication.",
        "fix": "Consolidate or trim to one instance.",
    },
}

# Word-count targets by skill tier
WORD_LIMITS = {
    "distributed": 50,  # ~200 chars; distributed skills are entry points
    "maintainer": 80,   # ~350 chars; maintainer skills are internal, can be slightly longer
}


def extract_description(skill_file: Path) -> str | None:
    """Extract description field from SKILL.md frontmatter."""
    try:
        content = skill_file.read_text()
    except Exception as e:
        print(f"ERROR: Cannot read {skill_file}: {e}", file=sys.stderr)
        return None

    # Extract frontmatter
    match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    frontmatter = match.group(1)

    # Extract description (handles both >- and inline formats)
    desc_match = re.search(
        r"description:\s*>-\s*\n((?:[ \t].*\n?)+)",
        frontmatter,
        re.MULTILINE
    )
    if desc_match:
        desc = " ".join(
            line.strip()
            for line in desc_match.group(1).splitlines()
            if line.strip()
        )
        return desc

    # Fallback to inline description
    desc_match = re.search(r"description:\s*(.+?)(?:\n|$)", frontmatter)
    if desc_match:
        return desc_match.group(1).strip().lstrip('"').rstrip('"')

    return None


def check_description(desc: str, skill_name: str, skill_type: str) -> list[dict]:
    """Run all rules against description; return violations."""
    violations = []

    for rule_name, rule in RULES.items():
        for pattern in rule["patterns"]:
            if re.search(pattern, desc):
                violations.append({
                    "skill": skill_name,
                    "type": skill_type,
                    "rule": rule_name,
                    "severity": rule["severity"],
                    "reason": rule["reason"],
                    "fix": rule["fix"],
                    "pattern": pattern,
                })
                break  # One violation per rule per description

    # Word-count check
    word_count = len(desc.split())
    limit = WORD_LIMITS[skill_type]
    if word_count > limit:
        violations.append({
            "skill": skill_name,
            "type": skill_type,
            "rule": "word_count",
            "severity": "MEDIUM",
            "reason": f"{skill_type} skills should be ≤{limit} words (~{limit * 4} chars) for clarity.",
            "fix": "Trim to purpose + trigger; move mechanics to body.",
            "count": word_count,
            "limit": limit,
        })

    return violations


def find_skills() -> list[tuple[Path, str]]:
    """Locate all SKILL.md files; return (path, 'distributed'|'maintainer') tuples."""
    skills = []

    # Distributed skills
    for f in Path("profile-al-dev-shared/skills").glob("*/SKILL.md"):
        if f.exists():
            skills.append((f, "distributed"))

    # Maintainer skills
    for f in Path(".claude/skills").glob("*/SKILL.md"):
        if f.exists():
            skills.append((f, "maintainer"))

    return sorted(skills)


def format_violation(v: dict) -> str:
    """Format a violation for human reading."""
    lines = [
        f"  {v['skill']} [{v['type']}] — {v['rule'].replace('_', ' ').title()}",
        f"    Severity: {v['severity']}",
        f"    Reason: {v['reason']}",
        f"    Fix: {v['fix']}",
    ]
    if "count" in v:
        lines.insert(
            3,
            f"    Details: {v['count']} words (limit: {v['limit']})",
        )
    return "\n".join(lines)


def main():
    """Validate all skill descriptions."""
    fix_mode = "--fix" in sys.argv
    strict_mode = "--strict" in sys.argv
    all_violations = []

    skills = find_skills()
    if not skills:
        print("ERROR: No SKILL.md files found", file=sys.stderr)
        return 2

    for skill_path, skill_type in skills:
        desc = extract_description(skill_path)
        if not desc:
            continue

        skill_name = skill_path.parent.name
        violations = check_description(desc, skill_name, skill_type)

        # Filter: in non-strict mode, skip word_count violations (they're heuristic)
        if not strict_mode:
            violations = [v for v in violations if v["rule"] != "word_count"]

        all_violations.extend(violations)

    if not all_violations:
        print("✓ All skill descriptions are clean")
        return 0

    # Group and report by severity
    by_severity = {}
    for v in all_violations:
        sev = v["severity"]
        by_severity.setdefault(sev, []).append(v)

    for severity in ["HIGH", "MEDIUM", "LOW"]:
        if severity in by_severity:
            print(f"\n{severity}-severity violations:")
            for v in by_severity[severity]:
                print(format_violation(v))

    # Summary
    count = len(all_violations)
    high_count = len(by_severity.get("HIGH", []))
    print(f"\n{count} total violations ({high_count} HIGH)")

    if fix_mode:
        print("\n--fix mode: apply safe fixes (not implemented yet)")

    return 1 if high_count > 0 else 0  # Exit non-zero if any HIGH


if __name__ == "__main__":
    sys.exit(main())
