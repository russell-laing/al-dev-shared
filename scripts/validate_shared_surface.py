"""Validates agents and skills in profile-al-dev-shared/ for surface quality."""
import re
import sys
from pathlib import Path

try:
    from _entrypoint_bootstrap import bootstrap_repo
except ModuleNotFoundError:  # pragma: no cover - direct-script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _entrypoint_bootstrap import bootstrap_repo

REPO = bootstrap_repo(__file__)

from scripts.al_dev_tools.markdown_frontmatter import parse_required_frontmatter

AGENTS_DIR = REPO / "profile-al-dev-shared" / "agents"
SKILLS_DIR = REPO / "profile-al-dev-shared" / "skills"

REQUIRED_AGENT_FIELDS = ("name", "description", "model", "tools")
FENCE_LINE = re.compile(r"^```([A-Za-z0-9_+-]+)?[ \t]*$")


def _count_unlabeled_opening_fences(content: str) -> int:
    unlabeled = 0
    in_fence = False
    for raw_line in content.splitlines():
        line = raw_line.strip()
        match = FENCE_LINE.match(line)
        if not match:
            continue
        if in_fence:
            in_fence = False
            continue
        if match.group(1) is None:
            unlabeled += 1
        in_fence = True
    return unlabeled


def _check_agent(path: Path) -> list[str]:
    issues = []
    content = path.read_text(encoding="utf-8")
    try:
        fm, _body = parse_required_frontmatter(content)
    except ValueError as exc:
        issues.append(str(exc))
        return issues
    for field in REQUIRED_AGENT_FIELDS:
        if field not in fm:
            issues.append(f"missing '{field}' in frontmatter")
    unlabeled = _count_unlabeled_opening_fences(content)
    if unlabeled:
        issues.append(f"{unlabeled} unlabeled code block(s) — add language specifier after ```")
    return issues


def _check_skill(path: Path) -> list[str]:
    issues = []
    content = path.read_text(encoding="utf-8")
    unlabeled = _count_unlabeled_opening_fences(content)
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
    args = [] if argv is None else list(argv)
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
    raise SystemExit(main(sys.argv[1:]))
