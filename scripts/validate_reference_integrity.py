#!/usr/bin/env python3
"""Validate markdown path and command references against canonical contracts."""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from _entrypoint_bootstrap import bootstrap_repo
except ModuleNotFoundError:  # pragma: no cover - exercised in package imports
    from scripts._entrypoint_bootstrap import bootstrap_repo

try:
    from scripts.al_dev_tools.reference_contracts import (
        allowed_template_patterns,
        canonical_artifact_patterns,
        canonical_script_entrypoints,
        generated_output_surfaces,
        legacy_reference_aliases,
    )
except ModuleNotFoundError:  # pragma: no cover - exercised in direct script execution
    from al_dev_tools.reference_contracts import (
        allowed_template_patterns,
        canonical_artifact_patterns,
        canonical_script_entrypoints,
        generated_output_surfaces,
        legacy_reference_aliases,
    )

REPO_ROOT = bootstrap_repo(__file__)

_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
_MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_BARE_REFERENCE_RE = re.compile(
    r"(?<![`<])(?<!python3 )(?P<ref>(?:python3\s+)?(?:\.{1,2}/|\.claude/|profile-al-dev-shared/|docs/|scripts/|knowledge/)[^\s`<>\")]*)"
)
_PATH_PREFIXES = (
    ".claude/",
    "profile-al-dev-shared/",
    "docs/",
    "scripts/",
    ".dev/",
    "knowledge/",
    "../",
    "./",
    "/",
)
_EXPLANATORY_ROOTS = (
    Path("docs/reviews"),
    Path("docs/superpowers/plans"),
    Path("docs/health"),
)
_GENERATED_OUTPUT_HINTS = ("docs/maintainer_tooling", "profile-al-dev-shared/generated/agents/")


@dataclass(frozen=True)
class ReferenceIssue:
    path: str
    rule: str
    issue: str
    fix: str


def _format_issue(issue: ReferenceIssue) -> str:
    return (
        f"{issue.path}\n"
        f"  rule: {issue.rule}\n"
        f"  issue: {issue.issue}\n"
        f"  fix: {issue.fix}"
    )


def _repo_relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _iter_markdown_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(root.rglob("*.md"))


def _iter_reference_candidates(content: str) -> Iterable[str]:
    for match in _MARKDOWN_LINK_RE.finditer(content):
        yield match.group(1).strip()
    for match in _INLINE_CODE_RE.finditer(content):
        yield match.group(1).strip()
    for match in _BARE_REFERENCE_RE.finditer(content):
        token = match.group("ref").rstrip(").,;:!?\"'`")
        if token:
            yield token


def _is_candidate_reference(token: str) -> bool:
    if not token or " " in token and not token.startswith("python3 "):
        return False
    if token.startswith("/") and "." not in token:
        return False
    if token.startswith("http://") or token.startswith("https://"):
        return False
    if token in {"SKILL.md", ".md", ".toml", "*.md"}:
        return False
    if token.endswith(".md") and "/" not in token:
        return False
    if token.endswith(".py") and "/" not in token and not any(
        token in values
        for values in legacy_reference_aliases().values()
    ) and token not in {
        Path(command.removeprefix("python3 ")).name
        for command in canonical_script_entrypoints().values()
    }:
        return False
    if token.endswith(".md") or token.endswith(".py") or token.endswith(".toml"):
        return True
    if token.startswith("python3 scripts/"):
        return True
    if token.startswith(_PATH_PREFIXES):
        return True
    return False


def _canonical_artifact_tokens() -> set[str]:
    return {f".dev/{pattern}" for pattern in canonical_artifact_patterns().values()}


def _matches_generated_output(token: str) -> bool:
    for values in generated_output_surfaces().values():
        for pattern in values:
            if fnmatch.fnmatch(token, pattern):
                return True
    if token.startswith("profile-al-dev-shared/generated/") and token.endswith("/"):
        return True
    return False


def _matches_allowed_template(token: str) -> bool:
    for pattern in allowed_template_patterns():
        if fnmatch.fnmatch(token, pattern):
            return True
    return False


def _flatten_legacy_aliases() -> dict[str, str]:
    flattened: dict[str, str] = {}
    for family, values in legacy_reference_aliases().items():
        for value in values:
            flattened[value] = family
    return flattened


def _is_explanatory_surface(path: Path) -> bool:
    rel = path.relative_to(REPO_ROOT)
    if "archived" in rel.parts:
        return True
    return any(rel == root or root in rel.parents for root in _EXPLANATORY_ROOTS)


def _resolve_reference(file_path: Path, token: str) -> Path | None:
    if token.startswith("/"):
        candidate = Path(token)
        return candidate if candidate.exists() else None

    if token.startswith("knowledge/"):
        relative = Path(token[len("knowledge/") :])
        local_root = file_path.parent
        # A bare `knowledge/X` token is usually the tail of a longer path
        # (e.g. `.claude/knowledge/X`). Resolve it against the local dir and
        # both canonical knowledge roots so a valid citation is not mistaken
        # for a dead path when the referencing file lives outside a knowledge
        # directory (e.g. a skill under .claude/skills/).
        candidates = [
            local_root / relative,
            REPO_ROOT / ".claude" / "knowledge" / relative,
            REPO_ROOT / "profile-al-dev-shared" / "knowledge" / relative,
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    if token.startswith((".claude/", "profile-al-dev-shared/", "docs/", "scripts/", ".dev/")):
        candidate = REPO_ROOT / token
        return candidate if candidate.exists() else None

    if token.startswith(("./", "../")):
        candidate = (file_path.parent / token).resolve()
        return candidate if candidate.exists() else None

    candidates = [file_path.parent / token]
    if token.endswith("/SKILL.md"):
        candidates.append(REPO_ROOT / ".claude" / "skills" / token)
        candidates.append(REPO_ROOT / "profile-al-dev-shared" / "skills" / token)
    if file_path.parent.parts[-2:] in {(".claude", "knowledge"), ("profile-al-dev-shared", "knowledge")}:
        candidates.append(REPO_ROOT / "profile-al-dev-shared" / "knowledge" / token)
        candidates.append(REPO_ROOT / ".claude" / "knowledge" / token)
    candidates.append(REPO_ROOT / "docs" / token)
    candidates.append(REPO_ROOT / token)

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _generated_output_issue(path: str, token: str) -> ReferenceIssue | None:
    if any(token.startswith(prefix) for prefix in _GENERATED_OUTPUT_HINTS):
        if not _matches_generated_output(token):
            return ReferenceIssue(
                path=path,
                rule="reference-unknown-generated-output",
                issue=f"generated output reference '{token}' is not declared in the canonical registry",
                fix="use a generated output declared in scripts/al_dev_tools/reference_contracts.py",
            )
    return None


def _script_entrypoint_issue(path: str, token: str) -> ReferenceIssue | None:
    entrypoints = canonical_script_entrypoints()
    if token in entrypoints.values():
        return None

    for name, command in entrypoints.items():
        script_path = command.removeprefix("python3 ")
        script_name = Path(script_path).name
        legacy_name = script_name.replace("_", "-")
        if token in {script_path, script_name, legacy_name}:
            return ReferenceIssue(
                path=path,
                rule="reference-stale-command",
                issue=f"script entrypoint '{token}' does not use canonical runnable form '{command}'",
                fix=f"replace the stale entrypoint with '{command}'",
            )
    return None


def _reference_issue_for_token(file_path: Path, token: str) -> ReferenceIssue | None:
    path = _repo_relative(file_path)

    if (
        _matches_allowed_template(token)
        or "<" in token
        or "YYYY-MM-DD" in token
        or "YYYY" in token
        or "*" in token
        or "${" in token
    ):
        return None

    legacy_family = _flatten_legacy_aliases().get(token)
    if legacy_family:
        if _is_explanatory_surface(file_path):
            return None
        return ReferenceIssue(
            path=path,
            rule="reference-legacy-alias",
            issue=f"legacy reference alias '{token}' appears on an active surface ({legacy_family})",
            fix="replace it with the canonical reference family from scripts/al_dev_tools/reference_contracts.py",
        )

    if token.startswith(".dev/"):
        return None
    if _matches_generated_output(token):
        return None

    if token in canonical_script_entrypoints().values():
        return None
    if token.startswith("python3 scripts/"):
        command_path = token.removeprefix("python3 ").split(" ", 1)[0]
        resolved_command = _resolve_reference(file_path, command_path)
        if resolved_command is not None:
            return None

    command_issue = _script_entrypoint_issue(path, token)
    if command_issue is not None:
        return command_issue

    if token in _canonical_artifact_tokens() or _matches_generated_output(token):
        return None

    generated_issue = _generated_output_issue(path, token)
    if generated_issue is not None:
        return generated_issue

    resolved = _resolve_reference(file_path, token)
    if resolved is not None:
        return None

    return ReferenceIssue(
        path=path,
        rule="reference-dead-path",
        issue=f"reference '{token}' does not resolve to a live path or canonical contract token",
        fix="replace it with a valid path, canonical artifact pattern, or allowed template pattern",
    )


def validate_reference_path(root: Path, match: str | None = None) -> list[str]:
    """Validate markdown reference integrity for a file or directory.

    When ``match`` is given, only issues whose formatted text contains that
    substring are returned. This lets callers scope the scan to one concern
    (e.g. ``dispositions`` for the disposition-ledger references) instead of
    the whole documentation surface.
    """

    issues: list[str] = []
    for file_path in _iter_markdown_files(root):
        content = file_path.read_text(encoding="utf-8")
        seen: set[tuple[str, str]] = set()
        for token in _iter_reference_candidates(content):
            if not _is_candidate_reference(token):
                continue
            issue = _reference_issue_for_token(file_path, token)
            if issue is None:
                continue
            key = (issue.rule, issue.issue)
            if key in seen:
                continue
            seen.add(key)
            # Match against the issue text (which embeds the offending token),
            # NOT the formatted block — the file path can contain the substring
            # incidentally (e.g. a skill named *-dispositions) and would leak
            # unrelated findings through the filter.
            if match is not None and match not in issue.issue:
                continue
            issues.append(_format_issue(issue))
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate markdown reference integrity")
    parser.add_argument("--path", required=True, help="Markdown file or directory to validate")
    parser.add_argument(
        "--match",
        default=None,
        help="Only report issues whose text contains this substring (e.g. 'dispositions').",
    )
    args = parser.parse_args(argv)

    target = Path(args.path)
    if not target.is_absolute():
        target = REPO_ROOT / target

    if not target.exists():
        print(f"Error: path not found: {target}")
        return 1

    issues = validate_reference_path(target, match=args.match)
    if issues:
        print(f"FAIL ({len(issues)} issues)\n")
        print("\n\n".join(issues))
        return 1

    print(f"PASS ({target})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
