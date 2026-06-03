import re
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def extract_sed_expression(text: str) -> str:
    match = re.search(r"sed (?:-E )?-i '' '([^']+)'", text)
    assert match, "expected sed expression in agent instructions"
    return match.group(1)


def run_sed_expression(expression: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "sample.txt"
        path.write_text("cat\ncar \ncap\t\n", encoding="utf-8")
        subprocess.run(
            ["sed", "-E", "-i", "", expression, str(path)],
            check=True,
        )
        return path.read_text(encoding="utf-8")


def test_lint_fixer_trailing_whitespace_command_preserves_terminal_t() -> None:
    text = read("profile-al-dev-shared/agents/al-dev-commit-lint-fixer.md")
    expression = extract_sed_expression(text)
    result = run_sed_expression(expression)
    assert result == "cat\ncar\ncap\n"


def test_commit_agents_use_bsd_safe_blank_class() -> None:
    paths = [
        "profile-al-dev-shared/agents/al-dev-commit-lint-fixer.md",
        "profile-al-dev-shared/agents/al-dev-commit-hook-fixer.md",
        "profile-al-dev-shared/generated/agents/claude/al-dev-commit-lint-fixer.md",
        "profile-al-dev-shared/generated/agents/claude/al-dev-commit-hook-fixer.md",
        "profile-al-dev-shared/generated/agents/copilot/al-dev-commit-lint-fixer.md",
        "profile-al-dev-shared/generated/agents/copilot/al-dev-commit-hook-fixer.md",
        "profile-al-dev-shared/generated/agents/codex/al-dev-commit-lint-fixer.toml",
        "profile-al-dev-shared/generated/agents/codex/al-dev-commit-hook-fixer.toml",
    ]
    for path in paths:
        text = read(path)
        assert "[[:blank:]]+" in text, path
        assert "sed -i '' 's/[ \\t]*$//'" not in text, path
        assert "sed -i '' 's/[ \\t]+$//'" not in text, path


if __name__ == "__main__":
    test_lint_fixer_trailing_whitespace_command_preserves_terminal_t()
    test_commit_agents_use_bsd_safe_blank_class()
    print("2 tests passed")
