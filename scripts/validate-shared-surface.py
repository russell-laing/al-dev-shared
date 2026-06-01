"""Validates agents and skills in profile-al-dev-shared/ for surface quality."""
import os
import re
import sys
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
AGENTS_DIR = os.path.join(REPO, "profile-al-dev-shared", "agents")
SKILLS_DIR = os.path.join(REPO, "profile-al-dev-shared", "skills")

REQUIRED_AGENT_FIELDS = ("name:", "description:", "model:", "tools:")
UNLABELED_FENCE = re.compile(r"(?m)^```[ \t]*$")


def _check_agent(path: str) -> list[str]:
    issues = []
    content = open(path).read()
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        issues.append("missing YAML frontmatter")
        return issues
    fm = fm_match.group(1)
    for field in REQUIRED_AGENT_FIELDS:
        if field not in fm:
            issues.append(f"missing '{field.rstrip(':')}' in frontmatter")
    unlabeled = len(UNLABELED_FENCE.findall(content))
    if unlabeled:
        issues.append(f"{unlabeled} unlabeled code block(s) — add language specifier after ```")
    return issues


def _check_skill(path: str) -> list[str]:
    issues = []
    content = open(path).read()
    unlabeled = len(UNLABELED_FENCE.findall(content))
    if unlabeled:
        issues.append(f"{unlabeled} unlabeled code block(s) — add language specifier after ```")
    return issues


def validate_file(path: str) -> list[str]:
    """Validate a single file. Returns list of issue strings (empty = clean)."""
    abs_path = os.path.abspath(path)
    if abs_path.startswith(AGENTS_DIR) and abs_path.endswith(".md"):
        return _check_agent(abs_path)
    for root, dirs, files in os.walk(SKILLS_DIR):
        for f in files:
            if f == "SKILL.md" and abs_path == os.path.join(root, f):
                return _check_skill(abs_path)
    return []


def validate_all() -> dict[str, list[str]]:
    """Validate all agents and skills. Returns {path: [issues]} for files with issues."""
    results = {}
    for fname in sorted(os.listdir(AGENTS_DIR)):
        if fname.endswith(".md"):
            path = os.path.join(AGENTS_DIR, fname)
            issues = _check_agent(path)
            if issues:
                results[path] = issues
    for root, dirs, files in os.walk(SKILLS_DIR):
        for fname in sorted(files):
            if fname == "SKILL.md":
                path = os.path.join(root, fname)
                issues = _check_skill(path)
                if issues:
                    results[path] = issues
    return results


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Single file mode
        target = sys.argv[1]
        issues = validate_file(target)
        if issues:
            print(f"ISSUES in {os.path.basename(target)}:")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)
        else:
            print(f"OK: {os.path.basename(target)}")
    else:
        # Bulk mode
        results = validate_all()
        if results:
            for path, issues in results.items():
                rel = os.path.relpath(path, REPO)
                print(f"ISSUES in {rel}:")
                for issue in issues:
                    print(f"  - {issue}")
            print(f"\n{len(results)} file(s) with issues.")
            sys.exit(1)
        else:
            agent_count = len([f for f in os.listdir(AGENTS_DIR) if f.endswith(".md")])
            skill_count = sum(1 for r, d, fs in os.walk(SKILLS_DIR) for f in fs if f == "SKILL.md")
            print(f"OK: {agent_count} agents, {skill_count} skills — all clean.")
