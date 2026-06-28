"""Validates agents and skills in profile-al-dev-shared/ for surface quality."""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AGENTS_DIR = REPO / "profile-al-dev-shared" / "agents"
SKILLS_DIR = REPO / "profile-al-dev-shared" / "skills"

REQUIRED_AGENT_FIELDS = ("name:", "description:", "model:", "tools:")
UNLABELED_FENCE = re.compile(r"(?m)^```[ \t]*$")


def _check_agent(path: Path) -> list[str]:
    issues = []
    content = path.read_text(encoding="utf-8")
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


def _check_skill(path: Path) -> list[str]:
    issues = []
    content = path.read_text(encoding="utf-8")
    unlabeled = len(UNLABELED_FENCE.findall(content))
    if unlabeled:
        issues.append(f"{unlabeled} unlabeled code block(s) — add language specifier after ```")
    return issues


def validate_file(path: str | Path) -> list[str]:
    """Validate a single file. Returns list of issue strings (empty = clean)."""
    abs_path = Path(path).resolve()
    if AGENTS_DIR.resolve() in abs_path.parents and abs_path.suffix == ".md":
        return _check_agent(abs_path)
    for skill_path in SKILLS_DIR.rglob("SKILL.md"):
        if abs_path == skill_path.resolve():
            return _check_skill(abs_path)
    return []


def validate_all() -> dict[str, list[str]]:
    """Validate all agents and skills. Returns {path: [issues]} for files with issues."""
    results = {}
    for path in sorted(AGENTS_DIR.glob("*.md")):
        if path.name.endswith(".md"):
            issues = _check_agent(path)
            if issues:
                results[str(path)] = issues
    for path in sorted(SKILLS_DIR.rglob("SKILL.md")):
        issues = _check_skill(path)
        if issues:
            results[str(path)] = issues
    return results


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args:
        target = Path(args[0])
        issues = validate_file(target)
        if issues:
            print(f"ISSUES in {target.name}:")
            for issue in issues:
                print(f"  - {issue}")
            return 1
        print(f"OK: {target.name}")
        return 0

    results = validate_all()
    if results:
        for path, issues in results.items():
            rel = Path(path).relative_to(REPO)
            print(f"ISSUES in {rel}:")
            for issue in issues:
                print(f"  - {issue}")
        print(f"\n{len(results)} file(s) with issues.")
        return 1

    agent_count = len(list(AGENTS_DIR.glob("*.md")))
    skill_count = len(list(SKILLS_DIR.rglob("SKILL.md")))
    print(f"OK: {agent_count} agents, {skill_count} skills — all clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
